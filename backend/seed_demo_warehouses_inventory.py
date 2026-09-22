import datetime

from app.database import SessionLocal
from app.models import OfficialWarehouse, Warehouse, Inventory, InventoryBatch


# ============================================================
# VARIED PROTOTYPE INVENTORY
# ============================================================

INVENTORY_DATA = {
    "Ambad": {
        "water": 8500,
        "food": 2400,
        "medicine": 125,
    },
    "Kalwan": {
        "water": 2800,
        "food": 750,
        "medicine": 32,
    },
    "Lasalgaon": {
        "water": 4600,
        "food": 1350,
        "medicine": 58,
    },
    "Malegaon (N)": {
        "water": 11500,
        "food": 3200,
        "medicine": 165,
    },
    "Manmad": {
        "water": 7800,
        "food": 2150,
        "medicine": 110,
    },
    "Musalgaon": {
        "water": 5200,
        "food": 1450,
        "medicine": 72,
    },
    "Nampur": {
        "water": 2100,
        "food": 620,
        "medicine": 28,
    },
    "Nandgaon": {
        "water": 3400,
        "food": 900,
        "medicine": 41,
    },
    "Ozar": {
        "water": 6700,
        "food": 1850,
        "medicine": 88,
    },
    "Satana": {
        "water": 4100,
        "food": 1100,
        "medicine": 53,
    },
    "Sinner": {
        "water": 7200,
        "food": 2000,
        "medicine": 96,
    },
    "Wani (N)": {
        "water": 2500,
        "food": 680,
        "medicine": 31,
    },
}


# ============================================================
# PROTOTYPE COORDINATES
# Used only by the operational matching/routing layer.
# ============================================================

WAREHOUSE_COORDINATES = {
    "Ambad": (19.9442, 73.7231),
    "Kalwan": (20.4923, 74.0260),
    "Lasalgaon": (20.1427, 74.2395),
    "Malegaon (N)": (20.5497, 74.5346),
    "Manmad": (20.2533, 74.4376),
    "Musalgaon": (19.8347, 74.0536),
    "Nampur": (20.5280, 74.2120),
    "Nandgaon": (20.3030, 74.6550),
    "Ozar": (20.0870, 73.9300),
    "Satana": (20.5940, 74.2050),
    "Sinner": (19.8450, 73.9980),
    "Wani (N)": (20.1860, 73.8280),
}


# ============================================================
# ADD INVENTORY
# ============================================================

def add_inventory(
    db,
    warehouse,
    item_name,
    category,
    unit,
    quantity,
    min_threshold,
):
    existing = (
        db.query(Inventory)
        .filter(
            Inventory.warehouse_id == warehouse.id,
            Inventory.item_name == item_name,
            Inventory.category == category,
            Inventory.unit == unit,
        )
        .first()
    )

    if existing:
        print(f"    Already exists: {item_name}")
        return

    inventory = Inventory(
        warehouse_id=warehouse.id,
        category=category,
        item_name=item_name,
        unit=unit,
        total_quantity=quantity,
        reserved_quantity=0,
        allocated_quantity=0,
        available_quantity=quantity,
        min_threshold=min_threshold,
        status="AVAILABLE",

        # Prototype stock is marked verified so
        # Match AI can use it.
        verification_status="VERIFIED",
        verification_source="PROTOTYPE_SEED_DATA",
        verified_by_id=None,
        verified_at=datetime.datetime.utcnow(),
    )

    db.add(inventory)
    db.flush()

    batch = InventoryBatch(
        inventory_id=inventory.id,
        batch_number=f"DEMO-{warehouse.code}-{inventory.id}",
        quantity=quantity,
        expiry_date=None,
        donor_id=None,
        received_date=datetime.datetime.utcnow(),
    )

    db.add(batch)

    print(
        f"    {item_name}: "
        f"{quantity:g} {unit} [VERIFIED]"
    )


# ============================================================
# MAIN SEED FUNCTION
# ============================================================

def seed():
    db = SessionLocal()

    try:
        official_warehouses = (
            db.query(OfficialWarehouse)
            .order_by(OfficialWarehouse.id)
            .all()
        )

        if not official_warehouses:
            print("No official warehouses found.")
            return

        print(
            f"Found {len(official_warehouses)} official warehouses."
        )

        for official in official_warehouses:

            name = official.warehouse_name

            if name not in INVENTORY_DATA:
                print(
                    f"Skipping unknown warehouse: {name}"
                )
                continue

            data = INVENTORY_DATA[name]

            print(f"\nProcessing: {name}")

            # ------------------------------------------------
            # GET COORDINATES
            # ------------------------------------------------

            latitude, longitude = WAREHOUSE_COORDINATES.get(
                name,
                (None, None)
            )

            if latitude is None or longitude is None:
                print(
                    f"  WARNING: No coordinates for {name}"
                )
                continue

            # ------------------------------------------------
            # FIND OPERATIONAL WAREHOUSE
            # ------------------------------------------------

            warehouse = (
                db.query(Warehouse)
                .filter(
                    Warehouse.code == official.plant_code
                )
                .first()
            )

            # ------------------------------------------------
            # CREATE OPERATIONAL WAREHOUSE IF NEEDED
            # ------------------------------------------------

            if not warehouse:

                warehouse = Warehouse(
                    organization_id=None,
                    name=official.warehouse_name,
                    code=official.plant_code,
                    address=official.address,
                    latitude=latitude,
                    longitude=longitude,
                    capacity_sqm=(
                        (official.capacity_mt or 1000) * 10
                    ),
                    is_active=True,
                )

                db.add(warehouse)
                db.flush()

                print(
                    f"  Created operational warehouse "
                    f"ID={warehouse.id}"
                )

            else:

                print(
                    f"  Existing operational warehouse "
                    f"ID={warehouse.id}"
                )

                # IMPORTANT:
                # Update coordinates even if the warehouse
                # already existed with 20.0 / 73.8.
                warehouse.latitude = latitude
                warehouse.longitude = longitude

            print(
                f"  Coordinates updated: "
                f"{latitude}, {longitude}"
            )

            # ------------------------------------------------
            # ADD WATER
            # ------------------------------------------------

            add_inventory(
                db,
                warehouse,
                "Clean Drinking Water",
                "Drinking Water",
                "Liters",
                data["water"],
                1000,
            )

            # ------------------------------------------------
            # ADD FOOD
            # ------------------------------------------------

            add_inventory(
                db,
                warehouse,
                "Ready-to-Eat Food Packets",
                "Food",
                "Packets",
                data["food"],
                300,
            )

            # ------------------------------------------------
            # ADD MEDICINE
            # ------------------------------------------------

            add_inventory(
                db,
                warehouse,
                "Emergency Medicine Kits",
                "Medicines",
                "Kits",
                data["medicine"],
                20,
            )

        # ----------------------------------------------------
        # SAVE EVERYTHING
        # ----------------------------------------------------

        db.commit()

        print("\n==============================================")
        print("DEMO WAREHOUSE + INVENTORY SEEDING COMPLETE")
        print("==============================================")

        print(
            "\nInventory is marked VERIFIED "
            "for prototype matching."
        )

        print(
            "Verification source: PROTOTYPE_SEED_DATA"
        )

    except Exception as e:

        db.rollback()

        print("\n==============================================")
        print("ERROR DURING SEEDING")
        print("==============================================")
        print(e)

        raise

    finally:
        db.close()


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    seed()