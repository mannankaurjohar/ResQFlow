import csv
import time
import requests

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Organization, Warehouse


# ============================================================
# SOURCE
# ============================================================

MSWC_SOURCE_URL = (
    "https://mswarehousing.com/MSwhs/all-districts-list/"
)

# OSM-based geocoding service.
# We use Photon instead of the public Nominatim endpoint.
PHOTON_URL = "https://photon.komoot.io/api/"

HEADERS = {
    "User-Agent": (
        "ResQFlow-AI/1.0 "
        "(emergency-relief-platform)"
    ),
    "Accept": "application/json",
}

# Be conservative with public geocoding infrastructure.
REQUEST_DELAY_SECONDS = 1.0


# ============================================================
# OFFICIAL MSWC NASHIK WAREHOUSES
# ============================================================

MSWC_NASHIK_WAREHOUSES = [
    {
        "plant_code": "1427",
        "name": "Ambad",
        "taluka": "Nashik",
        "address": (
            "MSWC, MIDC Area, Ambad, "
            "A/P Ambad, Tal. Nashik, Dist. Nashik 431204"
        ),
        "godowns": 2,
        "capacity_mt": 2480,
    },
    {
        "plant_code": "1416",
        "name": "Kalwan",
        "taluka": "Kalwan",
        "address": (
            "MSWC, Krushi Utpanna Bazar Samiti, "
            "Market Yard, Kalwan, A/P Kalwan, "
            "Tal. Kalwan, Dist. Nashik 423501"
        ),
        "godowns": 3,
        "capacity_mt": 3500,
    },
    {
        "plant_code": "1417",
        "name": "Lasalgaon",
        "taluka": "Niphad",
        "address": (
            "MSWC, Kotamgaon Road, Near Onion Market, "
            "Lasalgaon, A/P Lasalgaon, Tal. Niphad, "
            "Dist. Nashik 422306"
        ),
        "godowns": 4,
        "capacity_mt": 4000,
    },
    {
        "plant_code": "1418",
        "name": "Malegaon (N)",
        "taluka": "Malegaon",
        "address": (
            "MSWC, Krushi Utpanna Bazar Samiti, "
            "Market Yard, Camp Road, Malegaon (N), "
            "A/P Malegaon (N), Tal. Malegaon, "
            "Dist. Nashik 423105"
        ),
        "godowns": 6,
        "capacity_mt": 8420,
    },
    {
        "plant_code": "1419",
        "name": "Manmad",
        "taluka": "Nandgaon",
        "address": (
            "MSWC, Krushi Utpanna Bazar Samiti, "
            "Market Yard, Chandwad Road, Manmad, "
            "A/P Manmad, Tal. Nandgaon, "
            "Dist. Nashik 423104"
        ),
        "godowns": 6,
        "capacity_mt": 11500,
    },
    {
        "plant_code": "1430",
        "name": "Musalgaon",
        "taluka": "Sinnar",
        "address": (
            "MSWC, Survey No. 142/2, Musalgaon MIDC Area, "
            "Musalgaon, A/P Musalgaon, Tal. Sinnar, "
            "Dist. Nashik 422112"
        ),
        "godowns": 1,
        "capacity_mt": 3000,
    },
    {
        "plant_code": "1420",
        "name": "Nampur",
        "taluka": "Satana (Baglan)",
        "address": (
            "MSWC, Market Yard, Nampur, "
            "A/P Nampur, Tal. Satana (Baglan), "
            "Dist. Nashik 423204"
        ),
        "godowns": 2,
        "capacity_mt": 2000,
    },
    {
        "plant_code": "1426",
        "name": "Nandgaon",
        "taluka": "Nandgaon",
        "address": (
            "MSWC, Krushi Utpanna Bazar Samiti, "
            "Market Yard, Nandgaon, A/P Nandgaon, "
            "Tal. Nandgaon, Dist. Nashik 423106"
        ),
        "godowns": 1,
        "capacity_mt": 1580,
    },
    {
        "plant_code": "1421",
        "name": "Ozar",
        "taluka": "Niphad",
        "address": (
            "MSWC, Mumbai Agra National Highway, "
            "Dahawa Mail, Ozar, A/P Ozar, "
            "Tal. Niphad, Dist. Nashik 422206"
        ),
        "godowns": 6,
        "capacity_mt": 7615,
    },
    {
        "plant_code": "1422",
        "name": "Satana",
        "taluka": "Satana (Baglan)",
        "address": (
            "MSWC, Krushi Utpanna Bazar Samiti, "
            "Market Yard, Satana, A/P Satana, "
            "Tal. Satana (Baglan), Dist. Nashik 423301"
        ),
        "godowns": 3,
        "capacity_mt": 5200,
    },
    {
        "plant_code": "1425",
        "name": "Sinner",
        "taluka": "Sinnar",
        "address": (
            "MSWC, MIDC Area Plot No E Malegaon, "
            "Sinner, A/P Sinner, Tal. Sinnar, "
            "Dist. Nashik 422213"
        ),
        "godowns": 4,
        "capacity_mt": 7140,
    },
    {
        "plant_code": "1423",
        "name": "Wani (N)",
        "taluka": "Dindori",
        "address": (
            "MSWC, Mulane Road, Wani, "
            "A/P Wani (N), Tal. Dindori, "
            "Dist. Nashik 422215"
        ),
        "godowns": 2,
        "capacity_mt": 2000,
    },
]


# ============================================================
# PHOTON GEOCODING
# ============================================================

def photon_search(query: str):
    """
    Search Photon / OpenStreetMap for a location.

    Returns the first result or None.
    """

    try:
        response = requests.get(
            PHOTON_URL,
            params={
                "q": query,
                "limit": 5,
            },
            headers=HEADERS,
            timeout=30,
        )

        response.raise_for_status()

        data = response.json()

        features = data.get("features", [])

        if not features:
            return None

        return features

    except Exception as exc:
        print(
            f"    Photon error: {exc}"
        )
        return None


def extract_coordinates(features, warehouse):
    """
    Choose a sufficiently specific OSM result.

    We reject obvious city/town-only matches.
    """

    warehouse_name = (
        warehouse["name"]
        .lower()
        .replace("(n)", "")
        .strip()
    )

    for feature in features:

        geometry = feature.get("geometry", {})
        coordinates = geometry.get("coordinates")

        if (
            not coordinates
            or len(coordinates) < 2
        ):
            continue

        properties = feature.get(
            "properties",
            {}
        )

        name = str(
            properties.get("name", "")
        ).lower()

        street = str(
            properties.get("street", "")
        ).lower()

        city = str(
            properties.get("city", "")
        ).lower()

        district = str(
            properties.get("district", "")
        ).lower()

        osm_type = str(
            properties.get("osm_type", "")
        ).lower()

        # ----------------------------------------------------
        # We want a result related to the warehouse/place.
        # ----------------------------------------------------

        name_match = (
            warehouse_name in name
            or "mswc" in name
            or "warehouse" in name
            or "godown" in name
            or "market" in name
        )

        location_match = (
            warehouse_name in city
            or "nashik" in district
            or "nashik" in city
        )

        # Reject results that look like generic town/city
        # centres unless they contain stronger warehouse clues.
        generic_city = (
            osm_type == "N"
            and not name_match
        )

        if generic_city:
            continue

        if not (
            name_match
            or location_match
        ):
            continue

        return {
            "latitude": float(
                coordinates[1]
            ),
            "longitude": float(
                coordinates[0]
            ),
            "display_name": (
                properties.get(
                    "name"
                )
                or properties.get(
                    "street"
                )
                or warehouse["name"]
            ),
            "osm_type": osm_type,
            "osm_id": str(
                properties.get(
                    "osm_id",
                    ""
                )
            ),
        }

    return None


def geocode_warehouse(warehouse):
    """
    Try progressively simpler OSM queries.

    We NEVER fall back to town-centre coordinates.
    """

    name = warehouse["name"]
    taluka = warehouse["taluka"]
    address = warehouse["address"]

    queries = [
        # 1. Full official address
        (
            f"{address}, "
            f"Nashik District, Maharashtra, India"
        ),

        # 2. MSWC + warehouse town
        (
            f"MSWC {name}, "
            f"{taluka}, Nashik, Maharashtra, India"
        ),

        # 3. Warehouse + town
        (
            f"{name} warehouse, "
            f"{taluka}, Nashik, Maharashtra, India"
        ),

        # 4. Market-yard/MIDC context where applicable
        (
            f"{name}, "
            f"{taluka}, Nashik, Maharashtra, India"
        ),
    ]

    for attempt, query in enumerate(
        queries,
        start=1
    ):

        print(
            f"    OSM query {attempt}: "
            f"{query}"
        )

        features = photon_search(query)

        time.sleep(
            REQUEST_DELAY_SECONDS
        )

        if not features:
            continue

        result = extract_coordinates(
            features,
            warehouse
        )

        if result:

            result["query"] = query
            result["match_quality"] = (
                "ADDRESS_OR_FACILITY"
                if attempt <= 2
                else "LOCATION_CONTEXT"
            )

            return result

    return None


# ============================================================
# ORGANIZATION
# ============================================================

def get_or_create_mswc_organization(
    db: Session
):

    organization = (
        db.query(Organization)
        .filter(
            Organization.name
            == (
                "Maharashtra State "
                "Warehousing Corporation"
            )
        )
        .first()
    )

    if organization:
        return organization

    organization = Organization(
        name=(
            "Maharashtra State "
            "Warehousing Corporation"
        ),
        org_type=(
            "GOVERNMENT_WAREHOUSE_OPERATOR"
        ),
        address=(
            "Nashik Region, Maharashtra, India"
        ),
    )

    db.add(organization)
    db.commit()
    db.refresh(organization)

    return organization


# ============================================================
# MAIN IMPORT
# ============================================================

def import_warehouses():

    db = SessionLocal()

    report_rows = []

    try:

        organization = (
            get_or_create_mswc_organization(
                db
            )
        )

        print()
        print("=" * 70)
        print(
            "RESQFLOW AI - MSWC + OSM WAREHOUSE IMPORT"
        )
        print("=" * 70)
        print()

        print(
            "Official source:"
        )
        print(
            MSWC_SOURCE_URL
        )

        print()
        print(
            "Warehouse count:",
            len(MSWC_NASHIK_WAREHOUSES)
        )
        print()

        for index, item in enumerate(
            MSWC_NASHIK_WAREHOUSES,
            start=1
        ):

            code = (
                "MSWC-"
                + item["plant_code"]
            )

            print(
                f"[{index}/"
                f"{len(MSWC_NASHIK_WAREHOUSES)}] "
                f"{item['name']} "
                f"({code})"
            )

            # ------------------------------------------------
            # Existing warehouse?
            # ------------------------------------------------

            existing = (
                db.query(Warehouse)
                .filter(
                    Warehouse.code
                    == code
                )
                .first()
            )

            if existing:

                print(
                    "    Already exists -> skipping"
                )

                report_rows.append(
                    {
                        "plant_code": item[
                            "plant_code"
                        ],
                        "name": item[
                            "name"
                        ],
                        "status": (
                            "ALREADY_EXISTS"
                        ),
                        "latitude": (
                            existing.latitude
                        ),
                        "longitude": (
                            existing.longitude
                        ),
                    }
                )

                continue

            # ------------------------------------------------
            # OSM lookup
            # ------------------------------------------------

            print(
                "    Searching OpenStreetMap..."
            )

            geo = geocode_warehouse(
                item
            )

            # ------------------------------------------------
            # No sufficiently specific match
            # ------------------------------------------------

            if not geo:

                print(
                    "    ⚠ No sufficiently "
                    "specific OSM match found"
                )

                print(
                    "    → NOT creating warehouse"
                )

                report_rows.append(
                    {
                        "plant_code": item[
                            "plant_code"
                        ],
                        "name": item[
                            "name"
                        ],
                        "status": (
                            "NEEDS_COORDINATE_REVIEW"
                        ),
                        "latitude": "",
                        "longitude": "",
                        "capacity_mt": item[
                            "capacity_mt"
                        ],
                        "godowns": item[
                            "godowns"
                        ],
                    }
                )

                continue

            # ------------------------------------------------
            # Match found
            # ------------------------------------------------

            print(
                "    ✓ Coordinate found:"
            )

            print(
                "      Latitude:",
                geo["latitude"]
            )

            print(
                "      Longitude:",
                geo["longitude"]
            )

            print(
                "      Match:",
                geo["display_name"]
            )

            print(
                "      Quality:",
                geo["match_quality"]
            )

            # ------------------------------------------------
            # Create warehouse
            # ------------------------------------------------

            warehouse = Warehouse(

                organization_id=(
                    organization.id
                ),

                name=(
                    "MSWC "
                    + item["name"]
                ),

                code=code,

                address=item[
                    "address"
                ],

                latitude=geo[
                    "latitude"
                ],

                longitude=geo[
                    "longitude"
                ],

                # IMPORTANT:
                # MSWC capacity is MT, not sqm.
                #
                # Therefore DO NOT put the capacity
                # into capacity_sqm.
                capacity_sqm=None,

                is_active=True,
            )

            db.add(warehouse)
            db.flush()

            print(
                "    ✓ Warehouse record created"
            )

            print(
                "    Inventory: NOT REPORTED"
            )

            report_rows.append(
                {
                    "plant_code": item[
                        "plant_code"
                    ],
                    "name": item[
                        "name"
                    ],
                    "status": "IMPORTED",
                    "latitude": geo[
                        "latitude"
                    ],
                    "longitude": geo[
                        "longitude"
                    ],
                    "osm_type": geo[
                        "osm_type"
                    ],
                    "osm_id": geo[
                        "osm_id"
                    ],
                    "match_quality": geo[
                        "match_quality"
                    ],
                    "matched_query": geo[
                        "query"
                    ],
                    "capacity_mt": item[
                        "capacity_mt"
                    ],
                    "godowns": item[
                        "godowns"
                    ],
                }
            )

        db.commit()

        # ====================================================
        # REPORT
        # ====================================================

        report_path = (
            "mswc_warehouse_import_report.csv"
        )

        fieldnames = [
            "plant_code",
            "name",
            "status",
            "latitude",
            "longitude",
            "osm_type",
            "osm_id",
            "match_quality",
            "matched_query",
            "capacity_mt",
            "godowns",
        ]

        with open(
            report_path,
            "w",
            newline="",
            encoding="utf-8",
        ) as csv_file:

            writer = csv.DictWriter(
                csv_file,
                fieldnames=fieldnames,
                extrasaction="ignore",
            )

            writer.writeheader()

            writer.writerows(
                report_rows
            )

        # ====================================================
        # SUMMARY
        # ====================================================

        imported = sum(
            1
            for row in report_rows
            if row["status"]
            == "IMPORTED"
        )

        existing = sum(
            1
            for row in report_rows
            if row["status"]
            == "ALREADY_EXISTS"
        )

        review = sum(
            1
            for row in report_rows
            if row["status"]
            == "NEEDS_COORDINATE_REVIEW"
        )

        print()
        print("=" * 70)
        print("IMPORT COMPLETE")
        print("=" * 70)

        print(
            f"Imported:                {imported}"
        )

        print(
            f"Already existed:         {existing}"
        )

        print(
            f"Needs coordinate review: {review}"
        )

        print(
            f"Total processed:         "
            f"{len(report_rows)}"
        )

        print()
        print(
            "Inventory records created: 0"
        )

        print(
            "Inventory status: NOT REPORTED"
        )

        print()
        print(
            "Report:",
            report_path
        )

        print()

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    import_warehouses()