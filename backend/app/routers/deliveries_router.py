import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import Delivery, Allocation, CommunityRequest, Vehicle, Inventory, ReliefStatus, RequestStatus, User
from app.schemas import DeliveryResponse, DispatchDeliveryRequest, UpdateDeliveryStatusRequest
from app.auth import get_current_user, log_audit_event

router = APIRouter(prefix="/deliveries", tags=["Delivery & Logistics"])

@router.get("", response_model=List[DeliveryResponse])
def list_deliveries(db: Session = Depends(get_db)):
    return db.query(Delivery).order_by(Delivery.created_at.desc()).all()
@router.post("/dispatch/{delivery_id}", response_model=DeliveryResponse)
def dispatch_delivery(
    delivery_id: int,
    payload: DispatchDeliveryRequest = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    delivery = (
        db.query(Delivery)
        .filter(Delivery.id == delivery_id)
        .first()
    )

    if not delivery:
        raise HTTPException(
            status_code=404,
            detail="Delivery not found"
        )

    # Dispatch is allowed only after allocation approval
    if delivery.status != ReliefStatus.ALLOCATED:
        raise HTTPException(
            status_code=409,
            detail=(
                "Only an allocated delivery can be dispatched. "
                f"Current status: {delivery.status.value}"
            )
        )

    # Find or validate vehicle
    vehicle = None

    if payload and payload.vehicle_id:
        vehicle = (
            db.query(Vehicle)
            .filter(Vehicle.id == payload.vehicle_id)
            .first()
        )

        if not vehicle:
            raise HTTPException(
                status_code=404,
                detail="Selected vehicle not found"
            )

        if vehicle.status != "AVAILABLE":
            raise HTTPException(
                status_code=409,
                detail=(
                    "Selected vehicle is not available. "
                    f"Current status: {vehicle.status}"
                )
            )

    else:
        vehicle = (
            db.query(Vehicle)
            .filter(Vehicle.status == "AVAILABLE")
            .first()
        )

    if not vehicle:
        raise HTTPException(
            status_code=409,
            detail="No available vehicle is currently assigned to this delivery."
        )

    # Assign vehicle
    delivery.vehicle_id = vehicle.id

    if payload and payload.driver_name:
        delivery.driver_name = payload.driver_name

    if payload and payload.driver_phone:
        delivery.driver_phone = payload.driver_phone

    if payload and payload.notes:
        delivery.notes = payload.notes

    # Dispatch
    delivery.status = ReliefStatus.IN_TRANSIT
    delivery.dispatched_at = datetime.datetime.utcnow()

    # Mark vehicle as in transit
    vehicle.status = "IN_TRANSIT"

    # Update associated request
    if (
        delivery.allocation
        and delivery.allocation.request
    ):
        delivery.allocation.request.status = (
            RequestStatus.IN_TRANSIT
        )

    db.commit()
    db.refresh(delivery)

    # Audit trail
    log_audit_event(
        db=db,
        actor_id=(
            current_user.id
            if current_user
            else None
        ),
        actor_name=(
            current_user.full_name
            if current_user
            else "Logistics Dispatcher"
        ),
        actor_role="LOGISTICS",
        action="DISPATCH_DELIVERY",
        entity_type="DELIVERY",
        entity_id=delivery.relief_id,
        previous_state="ALLOCATED",
        new_state="IN_TRANSIT",
        reason=(
            "Convoy dispatched using vehicle "
            + str(vehicle.id)
            + " to "
            + delivery.destination_location_name
        )
    )

    return delivery

@router.patch("/{delivery_id}/status", response_model=DeliveryResponse)
def update_delivery_status(
    delivery_id: int,
    payload: UpdateDeliveryStatusRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    delivery = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")

    old_status = delivery.status
    delivery.status = payload.status
    
    if payload.notes:
        delivery.notes = payload.notes
    if payload.proof_photo_url:
        delivery.proof_photo_url = payload.proof_photo_url
    if payload.recipient_signature:
        delivery.recipient_signature = payload.recipient_signature

    if payload.status == ReliefStatus.DELIVERED:

    # Real proof-of-delivery is required.
        if not payload.proof_photo_url:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Proof-of-delivery photo is required "
                    "before marking the delivery as delivered."
                )
            )

        if not payload.recipient_signature:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Recipient signature is required "
                    "before marking the delivery as delivered."
                )
            )

        delivery.delivered_at = datetime.datetime.utcnow()

        delivery.proof_photo_url = (
             payload.proof_photo_url
    )

    delivery.recipient_signature = (
        payload.recipient_signature
    )

    # Update request to DELIVERED
    if (
        delivery.allocation
        and delivery.allocation.request
    ):
        req = delivery.allocation.request

        req.status = RequestStatus.DELIVERED

        # Mark requested quantities as fulfilled
        for item in req.items:
            item.fulfilled_quantity = (
                item.requested_quantity
            )

    # Release vehicle
    if delivery.vehicle:
        delivery.vehicle.status = "AVAILABLE"

    # Finalize physical inventory consumption
    if (
        delivery.allocation
        and delivery.allocation.items
    ):
        for allocation_item in delivery.allocation.items:

            inventory = (
                db.query(Inventory)
                .filter(
                    Inventory.warehouse_id
                    == delivery.origin_warehouse_id,
                    Inventory.category.ilike(
                        f"%{allocation_item.category}%"
                    )
                )
                .first()
            )

            if inventory:
                inventory.allocated_quantity = max(
                    0.0,
                    inventory.allocated_quantity
                    - allocation_item.allocated_quantity
                )

                inventory.total_quantity = max(
                    0.0,
                    inventory.total_quantity
                    - allocation_item.allocated_quantity
                )

        # Free vehicle
        if delivery.vehicle:
            delivery.vehicle.status = "AVAILABLE"

        # Deplete warehouse total inventory physically
        if delivery.allocation and delivery.allocation.items:
            for a_item in delivery.allocation.items:
                inv = db.query(Inventory).filter(
                    Inventory.warehouse_id == delivery.origin_warehouse_id,
                    Inventory.category.ilike(f"%{a_item.category}%")
                ).first()
                if inv:
                    inv.allocated_quantity = max(0.0, inv.allocated_quantity - a_item.allocated_quantity)
                    inv.total_quantity = max(0.0, inv.total_quantity - a_item.allocated_quantity)

    db.commit()
    db.refresh(delivery)

    log_audit_event(
        db=db,
        actor_id=current_user.id if current_user else None,
        actor_name=current_user.full_name if current_user else "Field Agent",
        actor_role="FIELD_OPERATIONS",
        action=f"UPDATE_DELIVERY_STATUS_{payload.status.value}",
        entity_type="DELIVERY",
        entity_id=delivery.relief_id,
        previous_state=old_status.value if hasattr(old_status, 'value') else str(old_status),
        new_state=payload.status.value if hasattr(payload.status, 'value') else str(payload.status),
        reason=payload.notes or f"Delivery transitioned to {payload.status.value}"
    )

    return delivery
