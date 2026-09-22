import datetime
from app.database import SessionLocal
from app.models import Warehouse, Inventory, InventoryBatch


DEMO_INVENTORY = [
    ("Clean Drinking Water", "Drinking Water", "Liters", 5000, 500),
    ("Ready-to-Eat Food Packets", "Food", "Packets", 1800, 200),
    ("Emergency Medicine Kits", "Medicines", "Kits", 90, 20),
]


def seed_inventory():
    db = SessionLocal()

    try:
        warehouses = (
            db.query(Warehouse)
            .filter(Warehouse.is_active == True)
            .all()
        )

        if not warehouses:
            print("No active warehouses found.")
            return

        print(f"Found {len(warehouses)} active warehouses.")

        for warehouse in warehouses:
            print(f"\nProcessing: {warehouse.name} (ID {warehouse.id})")

            for item_name, category, unit, quantity, threshold in DEMO_INVENTORY:

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
                    print(f"  Already exists: {item_name}")
                    continue

                inventory = Inventory(
                    warehouse_id=warehouse.id,
                    category=category,
                    item_name=item_name,
                    unit=unit,
                    total_quantity=quantity,
                    reserved_quantity=0,
                    allocated_quantity=0,
                    available_quantity=quantity,
                    min_threshold=threshold,
                    status="AVAILABLE",
                    verification_status="VERIFIED",
                    verification_source="PROTOTYPE_SEED_DATA",
                    verified_by_id=None,
                    verified_at=datetime.datetime.utcnow(),
                )

                db.add(inventory)
                db.flush()

                batch = InventoryBatch(
                    inventory_id=inventory.id,
                    batch_number=f"DEMO-{warehouse.id}-{inventory.id}",
                    quantity=quantity,
                    expiry_date=None,
                    donor_id=None,
                    received_date=datetime.datetime.utcnow(),
                )

                db.add(batch)

                print(
                    f"  Added: {item_name} = "
                    f"{quantity:g} {unit}"
                )

        db.commit()

        print("\n========================================")
        print("DEMO INVENTORY SEEDING COMPLETE")
        print("========================================")

    except Exception as e:
        db.rollback()
        print(f"\nERROR: {e}")
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_inventory()