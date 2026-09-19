from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import OfficialWarehouse


router = APIRouter(
    prefix="/official-warehouses",
    tags=["Official Warehouses"]
)


@router.get("")
def get_official_warehouses(
    district: str = Query(
        "Nashik",
        description="District name"
    ),
    db: Session = Depends(get_db)
):
    warehouses = (
        db.query(OfficialWarehouse)
        .filter(
            OfficialWarehouse.district.ilike(
                f"%{district}%"
            )
        )
        .order_by(
            OfficialWarehouse.warehouse_name
        )
        .all()
    )

    return {
        "source": "Maharashtra State Warehousing Corporation",
        "source_url": (
            "https://mswarehousing.com/"
        ),
        "district": district,
        "warehouse_count": len(warehouses),
        "warehouses": [
            {
                "id": warehouse.id,
                "organization_name": warehouse.organization_name,
                "plant_code": warehouse.plant_code,
                "warehouse_name": warehouse.warehouse_name,
                "district": warehouse.district,
                "taluka": warehouse.taluka,
                "address": warehouse.address,
                "godown_count": warehouse.godown_count,
                "capacity_mt": warehouse.capacity_mt,
                "latitude": warehouse.latitude,
                "longitude": warehouse.longitude,
                "location_status": warehouse.location_status,
                "inventory_status": warehouse.inventory_status,
                "source": warehouse.source,
                "source_verified_at": (
                    warehouse.source_verified_at
                )
            }
            for warehouse in warehouses
        ]
    }