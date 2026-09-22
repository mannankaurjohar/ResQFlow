from datetime import datetime
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import os
import uuid
from pathlib import Path
from fastapi import UploadFile, File
from app.database import get_db
from app.models import Delivery, Allocation, CommunityRequest, Vehicle, Inventory, ReliefStatus, RequestStatus, User
from app.schemas import DeliveryResponse, DispatchDeliveryRequest, UpdateDeliveryStatusRequest
from app.auth import get_current_user, log_audit_event

router = APIRouter(prefix="/deliveries", tags=["Delivery & Logistics"])

@router.get("", response_model=List[DeliveryResponse])
def list_deliveries(db: Session = Depends(get_db)):
    return db.query(Delivery).order_by(Delivery.created_at.desc()).all()
@router.get("/debug/vehicles")
def debug_vehicles(db: Session = Depends(get_db)):
    vehicles = db.query(Vehicle).all()

    return [
        {
            "id": v.id,
            "code": v.code,
            "status": v.status,
            "vehicle_type": v.vehicle_type,
            "driver_name": v.driver_name,
            "capacity_kg": v.capacity_kg
        }
        for v in vehicles
    ]
@router.post("/dispatch/{delivery_id}",response_model=DeliveryResponse)
def dispatch_delivery(
    delivery_id: int,
    payload: dict,
    db: Session = Depends(get_db)
):
    # --------------------------------------------------------
    # 1. FIND DELIVERY
    # --------------------------------------------------------

    delivery = (
        db.query(Delivery)
        .filter(Delivery.id == delivery_id)
        .first()
    )

    if not delivery:
        raise HTTPException(
            status_code=404,
            detail="Delivery not found."
        )

    # --------------------------------------------------------
    # 2. CHECK DELIVERY STATUS
    # --------------------------------------------------------

    if delivery.status != ReliefStatus.ALLOCATED:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Delivery cannot be dispatched "
                f"from status {delivery.status}."
            )
        )

    # --------------------------------------------------------
    # 3. IF VEHICLE IS ALREADY ASSIGNED, USE IT
    # --------------------------------------------------------

    vehicle = None

    if delivery.vehicle_id:
        vehicle = (
            db.query(Vehicle)
            .filter(Vehicle.id == delivery.vehicle_id)
            .first()
        )

        if not vehicle:
            raise HTTPException(
                status_code=400,
                detail="The assigned vehicle no longer exists."
            )

    # --------------------------------------------------------
    # 4. OTHERWISE AUTOMATICALLY ASSIGN AVAILABLE VEHICLE
    # --------------------------------------------------------

    if not vehicle:

        vehicle = (
            db.query(Vehicle)
            .filter(
                Vehicle.status == "AVAILABLE"
            )
            .order_by(
                Vehicle.id.asc()
            )
            .first()
        )

        if not vehicle:
            raise HTTPException(
                status_code=400,
                detail=(
                    "No available vehicle is currently assigned or available for dispatch."
                )
            )

        # Assign vehicle to delivery
        delivery.vehicle_id = vehicle.id

        # Copy driver information to delivery
        delivery.driver_name = vehicle.driver_name
        delivery.driver_phone = vehicle.driver_phone

    # --------------------------------------------------------
    # 5. MARK VEHICLE AS IN USE
    # --------------------------------------------------------

    vehicle.status = "IN_USE"

    # --------------------------------------------------------
    # 6. DISPATCH DELIVERY
    # --------------------------------------------------------

    delivery.status = ReliefStatus.DISPATCHED

    delivery.dispatched_at = datetime.now(IST)

    delivery.notes = (
        f"Delivery dispatched using vehicle "
        f"{vehicle.code}. "
        f"Driver: {vehicle.driver_name or 'Not assigned'}."
    )

    # --------------------------------------------------------
    # 7. SAVE
    # --------------------------------------------------------

    db.commit()

    db.refresh(delivery)

    return delivery

@router.patch("/{delivery_id}/status", response_model=DeliveryResponse)
def update_delivery_status(
    delivery_id: int,
    payload: UpdateDeliveryStatusRequest,
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

    old_status = delivery.status
    new_status = payload.status

    # --------------------------------------------------------
    # UPDATE BASIC DELIVERY INFORMATION
    # --------------------------------------------------------

    delivery.status = new_status

    if payload.notes:
        delivery.notes = payload.notes

    # --------------------------------------------------------
    # IN TRANSIT
    # --------------------------------------------------------

    # --------------------------------------------------------
# IN TRANSIT
# --------------------------------------------------------

    if new_status == ReliefStatus.IN_TRANSIT:

        if old_status != ReliefStatus.DISPATCHED:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Delivery must be DISPATCHED before "
                    f"marking it IN_TRANSIT. Current status: {old_status}"
                )
            )

        delivery.in_transit_at = datetime.now(IST)

    # --------------------------------------------------------
    # DELIVERED
    # --------------------------------------------------------

    if new_status == ReliefStatus.DELIVERED:

        # Proof of delivery is mandatory
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

        delivery.delivered_at = datetime.now(IST)

        delivery.proof_photo_url = (
            payload.proof_photo_url
        )

        delivery.recipient_signature = (
            payload.recipient_signature
        )

        # ----------------------------------------------------
        # UPDATE COMMUNITY REQUEST
        # ----------------------------------------------------

        if (
            delivery.allocation
            and delivery.allocation.request
        ):
            req = delivery.allocation.request

            req.status = RequestStatus.DELIVERED

            for item in req.items:
                item.fulfilled_quantity = (
                    item.requested_quantity
                )

        # ----------------------------------------------------
        # RELEASE VEHICLE
        # ----------------------------------------------------

        if delivery.vehicle:
            delivery.vehicle.status = "AVAILABLE"

        # ----------------------------------------------------
        # FINALIZE INVENTORY
        # ----------------------------------------------------

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

                    inventory.available_quantity = max(
                        0.0,
                        inventory.total_quantity
                        - inventory.reserved_quantity
                        - inventory.allocated_quantity
                    )

    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    db.commit()
    db.refresh(delivery)

    # --------------------------------------------------------
    # AUDIT LOG
    # --------------------------------------------------------

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
            else "Field Agent"
        ),
        actor_role="FIELD_OPERATIONS",
        action=(
            f"UPDATE_DELIVERY_STATUS_"
            f"{new_status.value}"
        ),
        entity_type="DELIVERY",
        entity_id=delivery.relief_id,
        previous_state=(
            old_status.value
            if hasattr(old_status, "value")
            else str(old_status)
        ),
        new_state=(
            new_status.value
            if hasattr(new_status, "value")
            else str(new_status)
        ),
        reason=(
            payload.notes
            or
            f"Delivery transitioned to "
            f"{new_status.value}"
        )
    )

    return delivery
@router.post("/upload-proof-photo")
async def upload_proof_photo(
    file: UploadFile = File(...)
):
    allowed_types = {
        "image/jpeg",
        "image/png",
        "image/webp"
    }

    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Only JPG, PNG, and WEBP images are allowed."
        )

    upload_dir = Path("uploads") / "proof"
    upload_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    extension = Path(
        file.filename or ""
    ).suffix.lower()

    if not extension:
        extension = ".jpg"

    filename = (
        f"{uuid.uuid4().hex}"
        f"{extension}"
    )

    file_path = upload_dir / filename

    contents = await file.read()

    with open(file_path, "wb") as buffer:
        buffer.write(contents)

    proof_url = (
        f"/uploads/proof/{filename}"
    )

    return {
        "message": "Proof photo uploaded successfully.",
        "filename": filename,
        "proof_photo_url": proof_url
    }