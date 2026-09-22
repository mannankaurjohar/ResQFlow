import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.schemas import (
    InventoryResponse,
    WarehouseResponse,
    InventoryBatchResponse,
    InventoryReceiveRequest,
    InventoryVerifyRequest
)
from app.database import get_db
from app.models import Warehouse, Inventory, InventoryBatch, User
from app.schemas import InventoryResponse, WarehouseResponse, InventoryBatchResponse
from app.auth import get_current_user, log_audit_event

router = APIRouter(prefix="/inventory", tags=["Inventory Management"])

@router.get("", response_model=List[InventoryResponse])
def get_inventory(
    category: str = None,
    warehouse_id: int = None,
    db: Session = Depends(get_db)
):
    query = db.query(Inventory)

    if category:
        query = query.filter(
            Inventory.category.ilike(f"%{category}%")
        )

    if warehouse_id:
        query = query.filter(
            Inventory.warehouse_id == warehouse_id
        )

    items = query.all()

    result = []

    for it in items:

        if it.available_quantity <= 0:
            status_value = "CRITICAL_SHORTAGE"
        elif it.available_quantity <= it.min_threshold:
            status_value = "LOW_STOCK"
        else:
            status_value = "AVAILABLE"

        result.append({
            "id": it.id,
            "warehouse_id": it.warehouse_id,
            "warehouse_name": (
                it.warehouse.name
                if it.warehouse
                else "Main Depot"
            ),
            "category": it.category,
            "item_name": it.item_name,
            "unit": it.unit,
            "total_quantity": it.total_quantity,
            "reserved_quantity": it.reserved_quantity,
            "allocated_quantity": it.allocated_quantity,
            "available_quantity": it.available_quantity,
            "min_threshold": it.min_threshold,
            "status": status_value,
            "updated_at": it.updated_at,
            "batches": [
                {
                    "id": batch.id,
                    "batch_number": batch.batch_number,
                    "quantity": batch.quantity,
                    "expiry_date": batch.expiry_date,
                    
                }
                for batch in it.batches
            ]
        })

    return result
@router.post("/receive", response_model=InventoryResponse)
def receive_inventory(
    payload: InventoryReceiveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    warehouse = db.query(Warehouse).filter(
        Warehouse.id == payload.warehouse_id,
        Warehouse.is_active == True
    ).first()

    if not warehouse:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Warehouse not found or inactive."
        )

    if payload.quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quantity must be greater than zero."
        )

    inventory = db.query(Inventory).filter(
        Inventory.warehouse_id == payload.warehouse_id,
        Inventory.category == payload.category,
        Inventory.item_name == payload.item_name,
        Inventory.unit == payload.unit
    ).first()

    if not inventory:
        inventory = Inventory(
            warehouse_id=payload.warehouse_id,
            category=payload.category,
            item_name=payload.item_name,
            unit=payload.unit,
            total_quantity=0,
            reserved_quantity=0,
            allocated_quantity=0,
            available_quantity=0,
            min_threshold=payload.min_threshold,
            status="AVAILABLE",
            verification_status="UNKNOWN"
        )

        db.add(inventory)
        db.flush()

    inventory.total_quantity += payload.quantity
    inventory.available_quantity += payload.quantity

    batch = InventoryBatch(
        inventory_id=inventory.id,
        batch_number=payload.batch_number,
        quantity=payload.quantity,
        expiry_date=payload.expiry_date,
        donor_id=current_user.id if current_user else None,
        received_date=datetime.datetime.utcnow()
    )

    db.add(batch)

    inventory.verification_status = "UNKNOWN"
    inventory.verification_source = payload.verification_source
    inventory.verified_by_id = None
    inventory.verified_at = None

    db.commit()
    db.refresh(inventory)

    log_audit_event(
        db=db,
        user_id=current_user.id if current_user else None,
        action="INVENTORY_RECEIVED",
        entity_type="Inventory",
        entity_id=inventory.id,
        details={
            "item_name": inventory.item_name,
            "quantity": payload.quantity,
            "unit": inventory.unit,
            "warehouse_id": inventory.warehouse_id,
            "batch_number": payload.batch_number,
            "verification_status": "UNKNOWN"
        }
    )

    return inventory


@router.post("/{inventory_id}/verify", response_model=InventoryResponse)
def verify_inventory(
    inventory_id: int,
    payload: InventoryVerifyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    inventory = db.query(Inventory).filter(
        Inventory.id == inventory_id
    ).first()

    if not inventory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory record not found."
        )

    if inventory.available_quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot verify inventory with zero available quantity."
        )

    inventory.verification_status = "VERIFIED"
    inventory.verification_source = payload.verification_source
    inventory.verified_by_id = current_user.id if current_user else None
    inventory.verified_at = datetime.datetime.utcnow()

    db.commit()
    db.refresh(inventory)

    log_audit_event(
        db=db,
        user_id=current_user.id if current_user else None,
        action="INVENTORY_VERIFIED",
        entity_type="Inventory",
        entity_id=inventory.id,
        details={
            "item_name": inventory.item_name,
            "available_quantity": inventory.available_quantity,
            "unit": inventory.unit,
            "warehouse_id": inventory.warehouse_id,
            "verification_source": payload.verification_source
        }
    )

    return inventory

@router.get("/warehouses", response_model=List[WarehouseResponse])
def get_warehouses(db: Session = Depends(get_db)):
    warehouses = db.query(Warehouse).filter(Warehouse.is_active == True).all()
    for wh in warehouses:
        for it in wh.inventory:
            it.warehouse_name = wh.name
    return warehouses

@router.get("/alerts")
def get_inventory_alerts(db: Session = Depends(get_db)):
    # Low stock & critical shortages
    low_stock = db.query(Inventory).filter(Inventory.available_quantity <= Inventory.min_threshold).all()
    
    # Expiring batches (within 14 days)
    two_weeks_ahead = datetime.datetime.utcnow() + datetime.timedelta(days=14)
    expiring_batches = db.query(InventoryBatch).filter(
        InventoryBatch.expiry_date != None,
        InventoryBatch.expiry_date <= two_weeks_ahead
    ).all()
    
    alerts = []
    for it in low_stock:
        alerts.append({
            "type": "SHORTAGE" if it.available_quantity == 0 else "LOW_STOCK",
            "severity": "CRITICAL" if it.available_quantity == 0 else "HIGH",
            "warehouse": it.warehouse.name if it.warehouse else "Warehouse",
            "item": it.item_name,
            "category": it.category,
            "available": it.available_quantity,
            "threshold": it.min_threshold,
            "unit": it.unit,
            "message": f"{it.item_name} is critically low ({it.available_quantity:g} {it.unit} left) at {it.warehouse.name if it.warehouse else 'Depot'}."
        })
        
    for b in expiring_batches:
        inv = b.inventory
        alerts.append({
            "type": "EXPIRING",
            "severity": "HIGH",
            "warehouse": inv.warehouse.name if inv and inv.warehouse else "Depot",
            "item": inv.item_name if inv else "Batch Item",
            "batch_number": b.batch_number,
            "expiry_date": b.expiry_date.strftime("%Y-%m-%d") if b.expiry_date else "",
            "quantity": b.quantity,
            "unit": inv.unit if inv else "units",
            "message": f"Batch {b.batch_number} ({inv.item_name if inv else ''}) expires on {b.expiry_date.strftime('%Y-%m-%d')}."
        })
        
    return alerts
