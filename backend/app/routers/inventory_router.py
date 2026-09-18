import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.database import get_db
from app.models import Warehouse, Inventory, InventoryBatch, User
from app.schemas import InventoryResponse, WarehouseResponse, InventoryBatchResponse
from app.auth import get_current_user, log_audit_event

router = APIRouter(prefix="/inventory", tags=["Inventory Management"])

@router.get("", response_model=List[InventoryResponse])
def get_inventory(category: str = None, warehouse_id: int = None, db: Session = Depends(get_db)):
    query = db.query(Inventory)
    if category:
        query = query.filter(Inventory.category.ilike(f"%{category}%"))
    if warehouse_id:
        query = query.filter(Inventory.warehouse_id == warehouse_id)
        
    items = query.all()
    # Attach warehouse name
    for it in items:
        it.warehouse_name = it.warehouse.name if it.warehouse else "Main Depot"
        # Dynamic status check
        if it.available_quantity <= 0:
            it.status = "CRITICAL_SHORTAGE"
        elif it.available_quantity <= it.min_threshold:
            it.status = "LOW_STOCK"
        else:
            it.status = "AVAILABLE"
            
    return items

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
