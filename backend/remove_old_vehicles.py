from app.database import SessionLocal
from app.models import Vehicle


def remove_old_vehicles():
    db = SessionLocal()

    try:
        old_codes = [
            "RESQ-V01",
            "RESQ-V02",
            "RESQ-V03",
            "RESQ-V04",
            "RESQ-V05",
        ]

        vehicles = (
            db.query(Vehicle)
            .filter(Vehicle.code.in_(old_codes))
            .all()
        )

        if not vehicles:
            print("No old RESQ-V0x vehicles found.")
            return

        for vehicle in vehicles:
            print(f"Removing: {vehicle.code} - {vehicle.vehicle_type}")
            db.delete(vehicle)

        db.commit()

        print()
        print(f"Removed {len(vehicles)} old vehicle records.")

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise

    finally:
        db.close()


if __name__ == "__main__":
    remove_old_vehicles()