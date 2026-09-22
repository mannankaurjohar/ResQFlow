from app.database import SessionLocal
from app.models import Vehicle


def seed_vehicles():
    db = SessionLocal()

    try:
        resources = [
            {
                "code": "LOG-NK-001",
                "vehicle_type": "Relief Cargo Vehicle",
                "capacity_kg": 3500.0,
            },
            {
                "code": "LOG-NK-002",
                "vehicle_type": "Relief Cargo Vehicle",
                "capacity_kg": 3500.0,
            },
            {
                "code": "LOG-NK-003",
                "vehicle_type": "4x4 Utility Vehicle",
                "capacity_kg": 1200.0,
            },
            {
                "code": "LOG-NK-004",
                "vehicle_type": "Rescue Boat",
                "capacity_kg": 850.0,
            },
            {
                "code": "LOG-NK-005",
                "vehicle_type": "Rescue Boat",
                "capacity_kg": 850.0,
            },
            {
                "code": "LOG-NK-006",
                "vehicle_type": "Mini Fire Rescue Tender",
                "capacity_kg": 1500.0,
            },
        ]

        added = 0
        skipped = 0

        for resource in resources:

            existing = (
                db.query(Vehicle)
                .filter(Vehicle.code == resource["code"])
                .first()
            )

            if existing:
                print(
                    f"Already exists: "
                    f"{resource['code']} - "
                    f"{resource['vehicle_type']}"
                )
                skipped += 1
                continue

            vehicle = Vehicle(
                code=resource["code"],
                vehicle_type=resource["vehicle_type"],
                capacity_kg=resource["capacity_kg"],

                # Internal logistics state.
                # This is required by the dispatch workflow,
                # but should not be presented as public resource data.
                status="AVAILABLE",

                # No driver information.
                driver_name=None,
                driver_phone=None,

                # No fabricated live coordinates.
                current_lat=None,
                current_lon=None,
            )

            db.add(vehicle)

            print(
                f"Added: "
                f"{resource['code']} - "
                f"{resource['vehicle_type']}"
            )

            added += 1

        db.commit()

        print()
        print("========================================")
        print("RESOURCE SEEDING COMPLETE")
        print("========================================")
        print(f"Added  : {added}")
        print(f"Skipped: {skipped}")
        print(f"Total  : {added + skipped}")
        print("========================================")

    except Exception as e:
        db.rollback()
        print()
        print("ERROR while seeding resources:")
        print(e)
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_vehicles()