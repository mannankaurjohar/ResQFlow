import datetime

from app.database import SessionLocal, Base, engine
from app.models import OfficialWarehouse


OFFICIAL_SOURCE = (
    "https://mswarehousing.com/MSwhs/all-districts-list/"
)


MSWC_WAREHOUSES = [
    {
        "plant_code": "1427",
        "warehouse_name": "Ambad",
        "district": "Nashik",
        "taluka": "Nashik",
        "address": (
            "MSWC, MIDC Area, Ambad, "
            "A/P Ambad, Tal. Nashik, "
            "Dist. Nashik 431204"
        ),
        "godown_count": 2,
        "capacity_mt": 2480,
    },
    {
        "plant_code": "1416",
        "warehouse_name": "Kalwan",
        "district": "Nashik",
        "taluka": "Kalwan",
        "address": (
            "MSWC, Krushi Utpanna Bazar Samiti, "
            "Market Yard, Kalwan, "
            "A/P Kalwan, Tal. Kalwan, "
            "Dist. Nashik 423501"
        ),
        "godown_count": 3,
        "capacity_mt": 3500,
    },
    {
        "plant_code": "1417",
        "warehouse_name": "Lasalgaon",
        "district": "Nashik",
        "taluka": "Niphad",
        "address": (
            "MSWC, Kotamgaon Road, "
            "Near Onion Market, Lasalgaon, "
            "A/P Lasalgaon, Tal. Niphad, "
            "Dist. Nashik 422306"
        ),
        "godown_count": 4,
        "capacity_mt": 4000,
    },
    {
        "plant_code": "1418",
        "warehouse_name": "Malegaon (N)",
        "district": "Nashik",
        "taluka": "Malegaon",
        "address": (
            "MSWC, Krushi Utpanna Bazar Samiti, "
            "Market Yard, Camp Road, Malegaon(N), "
            "A/P Malegaon (N), Tal. Malegaon, "
            "Dist. Nashik 423105"
        ),
        "godown_count": 6,
        "capacity_mt": 8420,
    },
    {
        "plant_code": "1419",
        "warehouse_name": "Manmad",
        "district": "Nashik",
        "taluka": "Nandgaon",
        "address": (
            "MSWC, Krushi Utpanna Bazar Samiti, "
            "Market Yard, Chandwad Road, Manmad, "
            "A/P Manmad, Tal. Nandgaon, "
            "Dist. Nashik 423104"
        ),
        "godown_count": 6,
        "capacity_mt": 11500,
    },
    {
        "plant_code": "1430",
        "warehouse_name": "Musalgaon",
        "district": "Nashik",
        "taluka": "Sinnar",
        "address": (
            "MSWC, Survey No. 142/2, "
            "Musalgaon MIDC Area, Musalgaon, "
            "A/P Musalgaon, Tal. Sinnar, "
            "Dist. Nashik 422112"
        ),
        "godown_count": 1,
        "capacity_mt": 3000,
    },
    {
        "plant_code": "1420",
        "warehouse_name": "Nampur",
        "district": "Nashik",
        "taluka": "Satana (Baglan)",
        "address": (
            "MSWC, Market Yard, Nampur, "
            "A/P Nampur, Tal. Satana (Baglan), "
            "Dist. Nashik 423204"
        ),
        "godown_count": 2,
        "capacity_mt": 2000,
    },
    {
        "plant_code": "1426",
        "warehouse_name": "Nandgaon",
        "district": "Nashik",
        "taluka": "Nandgaon",
        "address": (
            "MSWC, Krushi Utpanna Bazar Samiti, "
            "Market Yard, Nandgaon, "
            "A/P Nandgaon, Tal. Nandgaon, "
            "Dist. Nashik 423106"
        ),
        "godown_count": 1,
        "capacity_mt": 1580,
    },
    {
        "plant_code": "1421",
        "warehouse_name": "Ozar",
        "district": "Nashik",
        "taluka": "Niphad",
        "address": (
            "MSWC, Mumbai-Agra National Highway, "
            "Dahawa Mail, Ozar, "
            "A/P Ozar, Tal. Niphad, "
            "Dist. Nashik 422206"
        ),
        "godown_count": 6,
        "capacity_mt": 7615,
    },
    {
        "plant_code": "1422",
        "warehouse_name": "Satana",
        "district": "Nashik",
        "taluka": "Satana (Baglan)",
        "address": (
            "MSWC, Krushi Utpanna Bazar Samiti, "
            "Market Yard, Satana, "
            "A/P Satana, Tal. Satana (Baglan), "
            "Dist. Nashik 423301"
        ),
        "godown_count": 3,
        "capacity_mt": 5200,
    },
    {
        "plant_code": "1425",
        "warehouse_name": "Sinner",
        "district": "Nashik",
        "taluka": "Sinnar",
        "address": (
            "MSWC, MIDC Area Plot No E, "
            "Malegaon, Sinner, "
            "A/P Sinner, Tal. Sinnar, "
            "Dist. Nashik 422213"
        ),
        "godown_count": 4,
        "capacity_mt": 7140,
    },
    {
        "plant_code": "1423",
        "warehouse_name": "Wani (N)",
        "district": "Nashik",
        "taluka": "Dindori",
        "address": (
            "MSWC, Mulane Road, Wani, "
            "A/P Wani (N), Tal. Dindori, "
            "Dist. Nashik 422215"
        ),
        "godown_count": 2,
        "capacity_mt": 2000,
    },
]


def main():

    print()
    print("=" * 70)
    print("RESQFLOW AI - OFFICIAL MSWC WAREHOUSE IMPORT")
    print("=" * 70)
    print()

    print("Source:")
    print(OFFICIAL_SOURCE)
    print()

    # Create the new table if it does not exist.
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    inserted = 0
    updated = 0

    try:

        for index, item in enumerate(
            MSWC_WAREHOUSES,
            start=1
        ):

            print(
                f"[{index}/{len(MSWC_WAREHOUSES)}] "
                f"{item['warehouse_name']} "
                f"(MSWC-{item['plant_code']})"
            )

            existing = (
                db.query(OfficialWarehouse)
                .filter(
                    OfficialWarehouse.plant_code
                    == item["plant_code"]
                )
                .first()
            )

            if existing:

                existing.warehouse_name = (
                    item["warehouse_name"]
                )

                existing.district = (
                    item["district"]
                )

                existing.taluka = (
                    item["taluka"]
                )

                existing.address = (
                    item["address"]
                )

                existing.godown_count = (
                    item["godown_count"]
                )

                existing.capacity_mt = (
                    item["capacity_mt"]
                )

                existing.source = (
                    OFFICIAL_SOURCE
                )

                existing.source_verified_at = (
                    datetime.datetime.utcnow()
                )

                print(
                    "    ✓ Existing record updated"
                )

                updated += 1

            else:

                warehouse = OfficialWarehouse(
                    organization_name=(
                        "Maharashtra State "
                        "Warehousing Corporation"
                    ),

                    plant_code=(
                        item["plant_code"]
                    ),

                    warehouse_name=(
                        item["warehouse_name"]
                    ),

                    district=(
                        item["district"]
                    ),

                    taluka=(
                        item["taluka"]
                    ),

                    address=(
                        item["address"]
                    ),

                    godown_count=(
                        item["godown_count"]
                    ),

                    capacity_mt=(
                        item["capacity_mt"]
                    ),

                    # IMPORTANT:
                    # No coordinates are invented.
                    latitude=None,
                    longitude=None,

                    location_status=(
                        "PENDING_COORDINATE_VERIFICATION"
                    ),

                    inventory_status=(
                        "NOT_REPORTED"
                    ),

                    source=(
                        OFFICIAL_SOURCE
                    ),

                    source_verified_at=(
                        datetime.datetime.utcnow()
                    ),

                    created_at=(
                        datetime.datetime.utcnow()
                    ),
                )

                db.add(warehouse)

                print(
                    "    ✓ Official record created"
                )

                print(
                    "      Coordinates: NOT VERIFIED"
                )

                print(
                    "      Inventory: NOT REPORTED"
                )

                inserted += 1

            print()

        db.commit()

        print("=" * 70)
        print("IMPORT COMPLETE")
        print("=" * 70)
        print()

        print(
            "New official records:",
            inserted
        )

        print(
            "Updated records:",
            updated
        )

        print(
            "Total official warehouses:",
            len(MSWC_WAREHOUSES)
        )

        print()
        print(
            "Coordinates: "
            "PENDING VERIFICATION"
        )

        print(
            "Inventory: "
            "NOT REPORTED"
        )

        print()

    except Exception:

        db.rollback()
        raise

    finally:

        db.close()


if __name__ == "__main__":
    main()