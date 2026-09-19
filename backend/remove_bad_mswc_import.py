from app.database import SessionLocal
from app.models import Warehouse


def remove_bad_mswc_imports():
    db = SessionLocal()

    try:
        warehouses = (
            db.query(Warehouse)
            .filter(
                Warehouse.code.like("MSWC-%")
            )
            .all()
        )

        print()
        print("=" * 60)
        print("MSWC IMPORT CLEANUP")
        print("=" * 60)
        print()

        if not warehouses:
            print("No MSWC warehouse records found.")
            return

        for warehouse in warehouses:
            print(
                f"Removing: "
                f"{warehouse.name} "
                f"({warehouse.code})"
            )

        print()
        print(
            f"Total MSWC records to remove: "
            f"{len(warehouses)}"
        )

        confirmation = input(
            "\nType DELETE to continue: "
        )

        if confirmation != "DELETE":
            print("Cleanup cancelled.")
            return

        for warehouse in warehouses:
            db.delete(warehouse)

        db.commit()

        print()
        print(
            f"Removed {len(warehouses)} "
            "incorrect MSWC import records."
        )
        print()

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    remove_bad_mswc_imports()