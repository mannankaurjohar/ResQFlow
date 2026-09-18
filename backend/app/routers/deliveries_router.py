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
    delivery = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")

    delivery.status = ReliefStatus.IN_TRANSIT
    delivery.dispatched_at = datetime.datetime.utcnow()
    
    if payload:
        if payload.vehicle_id:
            delivery.vehicle_id = payload.vehicle_id
        if payload.driver_name:
            delivery.driver_name = payload.driver_name
        if payload.driver_phone:
            delivery.driver_phone = payload.driver_phone
        if payload.notes:
            delivery.notes = payload.notes

    # Update associated request status
    if delivery.allocation and delivery.allocation.request:
        delivery.allocation.request.status = RequestStatus.IN_TRANSIT

    db.commit()
    db.refresh(delivery)

    log_audit_event(
        db=db,
        actor_id=current_user.id if current_user else None,
        actor_name=current_user.full_name if current_user else "Logistics Dispatcher",
        actor_role="LOGISTICS",
        action="DISPATCH_DELIVERY",
        entity_type="DELIVERY",
        entity_id=delivery.relief_id,
        previous_state="ALLOCATED",
        new_state="IN_TRANSIT",
        reason=f"Convoy dispatched to {delivery.destination_location_name}"
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
        delivery.delivered_at = datetime.datetime.utcnow()
        if not delivery.proof_photo_url:
            delivery.proof_photo_url = "https://images.unsplash.com/photo-1547841243-eacb14453cd9?auto=format&fit=crop&w=600&q=80"
        if not delivery.recipient_signature:
            delivery.recipient_signature = "Digital Signature - Ward 12 Community Council"

        # Update Request to DELIVERED
        if delivery.allocation and delivery.allocation.request:
            req = delivery.allocation.request
            req.status = RequestStatus.DELIVERED
            # Mark items fulfilled
            for it in req.items:
                it.fulfilled_quantity = it.requested_quantity

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
