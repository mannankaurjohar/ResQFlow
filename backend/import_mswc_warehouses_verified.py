import csv
import datetime
import re
import time
import requests

from app.database import SessionLocal
from app.models import Organization, Warehouse


# ============================================================
# CONFIGURATION
# ============================================================

OVERPASS_URLS = [
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
    "https://overpass-api.de/api/interpreter",
]

USER_AGENT = (
    "ResQFlow-AI/1.0 "
    "(emergency-relief-platform)"
)

OFFICIAL_SOURCE = (
    "https://mswarehousing.com/MSwhs/all-districts-list/"
)

REPORT_FILE = "mswc_verified_warehouse_report.csv"


# ============================================================
# OFFICIAL MSWC NASHIK WAREHOUSES
# Source: Maharashtra State Warehousing Corporation
# ============================================================

MSWC_WAREHOUSES = [
    {
        "code": "1427",
        "name": "Ambad",
        "address": (
            "MSWC, MIDC Area, Ambad, "
            "A/P Ambad, Tal. Nashik, "
            "Dist. Nashik 431204"
        ),
        "capacity_mt": 2480,
    },
    {
        "code": "1416",
        "name": "Kalwan",
        "address": (
            "MSWC, Krushi Utpanna Bazar Samiti, "
            "Market Yard, Kalwan, "
            "A/P Kalwan, Tal. Kalwan, "
            "Dist. Nashik 423501"
        ),
        "capacity_mt": 3500,
    },
    {
        "code": "1417",
        "name": "Lasalgaon",
        "address": (
            "MSWC, Kotamgaon Road, "
            "Near Onion Market, Lasalgaon, "
            "A/P Lasalgaon, Tal. Niphad, "
            "Dist. Nashik 422306"
        ),
        "capacity_mt": 4000,
    },
    {
        "code": "1418",
        "name": "Malegaon (N)",
        "address": (
            "MSWC, Krushi Utpanna Bazar Samiti, "
            "Market Yard, Camp Road, Malegaon(N), "
            "A/P Malegaon (N), Tal. Malegaon, "
            "Dist. Nashik 423105"
        ),
        "capacity_mt": 7970,
    },
    {
        "code": "1419",
        "name": "Manmad",
        "address": (
            "MSWC, Krushi Utpanna Bazar Samiti, "
            "Market Yard, Chandwad Road, Manmad, "
            "A/P Manmad, Tal. Nandgaon, "
            "Dist. Nashik 423104"
        ),
        "capacity_mt": 11500,
    },
    {
        "code": "1430",
        "name": "Musalgaon",
        "address": (
            "MSWC, Survey No. 142/2, "
            "Musalgaon MIDC Area, Musalgaon, "
            "A/P Musalgaon, Tal. Sinnar, "
            "Dist. Nashik 422112"
        ),
        "capacity_mt": 3000,
    },
    {
        "code": "1420",
        "name": "Nampur",
        "address": (
            "MSWC, Market Yard, Nampur, "
            "A/P Nampur, Tal. Satana (Baglan), "
            "Dist. Nashik 423204"
        ),
        "capacity_mt": 2000,
    },
    {
        "code": "1426",
        "name": "Nandgaon",
        "address": (
            "MSWC, Krushi Utpanna Bazar Samiti, "
            "Market Yard, Nandgaon, "
            "A/P Nandgaon, Tal. Nandgaon, "
            "Dist. Nashik 423106"
        ),
        "capacity_mt": 1580,
    },
    {
        "code": "1421",
        "name": "Ozar",
        "address": (
            "MSWC, Mumbai-Agra National Highway, "
            "Dahawa Mail, Ozar, "
            "A/P Ozar, Tal. Niphad, "
            "Dist. Nashik 422206"
        ),
        "capacity_mt": 7615,
    },
    {
        "code": "1422",
        "name": "Satana",
        "address": (
            "MSWC, Krushi Utpanna Bazar Samiti, "
            "Market Yard, Satana, "
            "A/P Satana, Tal. Satana (Baglan), "
            "Dist. Nashik 423301"
        ),
        "capacity_mt": 5200,
    },
    {
        "code": "1425",
        "name": "Sinnar",
        "address": (
            "MSWC, MIDC Area, Plot No. E, "
            "Malegaon, Sinnar, "
            "A/P Sinnar, Tal. Sinnar, "
            "Dist. Nashik 422213"
        ),
        "capacity_mt": 7140,
    },
    {
        "code": "1423",
        "name": "Wani (N)",
        "address": (
            "MSWC, Mulane Road, Wani, "
            "A/P Wani (N), Tal. Dindori, "
            "Dist. Nashik 422215"
        ),
        "capacity_mt": 2000,
    },
]


# ============================================================
# HELPERS
# ============================================================

def normalize(text):
    if not text:
        return ""

    text = text.lower()

    replacements = {
        "maharashtra state warehousing corporation": "mswc",
        "maharashtra state warehousing": "mswc",
        "m.s.w.c.": "mswc",
        "m.s.w.c": "mswc",
        "m s w c": "mswc",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(r"[^a-z0-9]+", " ", text)

    return " ".join(text.split())


def query_overpass(query):
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    last_error = None

    for url in OVERPASS_URLS:
        print(
            f"    Trying Overpass server: {url}"
        )

        try:
            response = requests.post(
                url,
                data=query,
                headers=headers,
                timeout=30,
            )

            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as exc:
            last_error = exc

            print(
                "    ⚠ Server unavailable:",
                type(exc).__name__
            )

            continue

    raise RuntimeError(
        "All Overpass servers failed. "
        f"Last error: {last_error}"
    )

def build_exact_name_query(warehouse):
    name = warehouse["name"]

    # Search ONLY for explicit MSWC / warehousing naming.
    return f"""
[out:json][timeout:60];

nwr[
    "name"~"MSWC|Maharashtra State Warehousing|Warehousing Corporation",
    i
](
    19.0,
    73.0,
    21.5,
    75.5
);

out center tags;
"""


def build_code_query(warehouse):
    code = warehouse["code"]

    return f"""
[out:json][timeout:60];

nwr[
    "ref"="{code}"
](
    19.0,
    73.0,
    21.5,
    75.5
);

out center tags;
"""


def get_coordinates(element):
    if "lat" in element and "lon" in element:
        return (
            float(element["lat"]),
            float(element["lon"])
        )

    center = element.get("center")

    if center:
        return (
            float(center["lat"]),
            float(center["lon"])
        )

    return None, None


def is_strict_mswc_match(element, warehouse):
    tags = element.get("tags", {})

    all_text = " ".join(
        [
            str(tags.get("name", "")),
            str(tags.get("operator", "")),
            str(tags.get("brand", "")),
            str(tags.get("description", "")),
            str(tags.get("official_name", "")),
            str(tags.get("ref", "")),
        ]
    )

    text = normalize(all_text)

    # Strongest condition:
    # actual MSWC identity appears in OSM.
    if "mswc" in text:
        return True

    if "maharashtra state warehousing" in text:
        return True

    if "warehousing corporation" in text:
        return True

    # A matching MSWC plant code is also acceptable.
    if tags.get("ref") == warehouse["code"]:
        return True

    return False


def find_verified_osm_match(warehouse):
    print("    Searching OSM for explicit MSWC identity...")

    # --------------------------------------------------------
    # Query 1: explicit MSWC name
    # --------------------------------------------------------

    try:
        data = query_overpass(
            build_exact_name_query(warehouse)
        )

        elements = data.get("elements", [])

        strict_matches = [
            element
            for element in elements
            if is_strict_mswc_match(
                element,
                warehouse
            )
        ]

        if strict_matches:
            element = strict_matches[0]

            lat, lon = get_coordinates(element)

            if lat is not None:
                tags = element.get("tags", {})

                return {
                    "latitude": lat,
                    "longitude": lon,
                    "osm_type": element.get(
                        "type",
                        ""
                    ),
                    "osm_id": element.get(
                        "id",
                        ""
                    ),
                    "osm_name": tags.get(
                        "name",
                        "Unnamed OSM object"
                    ),
                    "match_method":
                        "EXPLICIT_MSWC_NAME",
                }

    except Exception as exc:
        print(
            "    ⚠ OSM name query failed:",
            exc
        )

    # --------------------------------------------------------
    # Query 2: official plant code
    # --------------------------------------------------------

    try:
        data = query_overpass(
            build_code_query(warehouse)
        )

        elements = data.get("elements", [])

        for element in elements:
            if is_strict_mswc_match(
                element,
                warehouse
            ):
                lat, lon = get_coordinates(element)

                if lat is not None:
                    tags = element.get("tags", {})

                    return {
                        "latitude": lat,
                        "longitude": lon,
                        "osm_type": element.get(
                            "type",
                            ""
                        ),
                        "osm_id": element.get(
                            "id",
                            ""
                        ),
                        "osm_name": tags.get(
                            "name",
                            "Unnamed OSM object"
                        ),
                        "match_method":
                            "EXPLICIT_MSWC_CODE",
                    }

    except Exception as exc:
        print(
            "    ⚠ OSM code query failed:",
            exc
        )

    return None


# ============================================================
# DATABASE
# ============================================================

def get_or_create_organization(db):
    organization = (
        db.query(Organization)
        .filter(
            Organization.name
            == "Maharashtra State Warehousing Corporation"
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
        org_type="GOVERNMENT_WAREHOUSE",
        address="Maharashtra, India",
        created_at=datetime.datetime.utcnow(),
    )

    db.add(organization)
    db.commit()
    db.refresh(organization)

    return organization


# ============================================================
# MAIN IMPORT
# ============================================================

def main():
    print()
    print("=" * 70)
    print("RESQFLOW AI - VERIFIED MSWC WAREHOUSE IMPORT")
    print("=" * 70)
    print()
    print("Official source:")
    print(OFFICIAL_SOURCE)
    print()
    print("OSM sources:")
for url in OVERPASS_URLS:
    print(" -", url)
    print()
    print("Warehouse count:", len(MSWC_WAREHOUSES))
    print()

    db = SessionLocal()

    report_rows = []

    imported = 0
    needs_review = 0
    already_exists = 0

    try:
        organization = get_or_create_organization(db)

        for index, warehouse in enumerate(
            MSWC_WAREHOUSES,
            start=1
        ):
            code = warehouse["code"]
            name = warehouse["name"]

            print(
                f"[{index}/{len(MSWC_WAREHOUSES)}] "
                f"{name} (MSWC-{code})"
            )

            # ------------------------------------------------
            # Check existing record
            # ------------------------------------------------

            existing = (
                db.query(Warehouse)
                .filter(
                    Warehouse.code
                    == f"MSWC-{code}"
                )
                .first()
            )

            if existing:
                print(
                    "    ⚠ Warehouse already exists"
                )

                already_exists += 1

                report_rows.append({
                    "plant_code": code,
                    "warehouse_name": name,
                    "official_address":
                        warehouse["address"],
                    "capacity_mt":
                        warehouse["capacity_mt"],
                    "status": "ALREADY_EXISTS",
                    "latitude":
                        existing.latitude,
                    "longitude":
                        existing.longitude,
                    "osm_name": "",
                    "osm_type": "",
                    "osm_id": "",
                    "match_method": "",
                })

                print()
                continue

            # ------------------------------------------------
            # Search OSM
            # ------------------------------------------------

            match = find_verified_osm_match(
                warehouse
            )

            # ------------------------------------------------
            # VERIFIED MATCH
            # ------------------------------------------------

            if match:
                print(
                    "    ✓ VERIFIED OSM match"
                )

                print(
                    "      OSM name:",
                    match["osm_name"]
                )

                print(
                    "      Latitude:",
                    match["latitude"]
                )

                print(
                    "      Longitude:",
                    match["longitude"]
                )

                print(
                    "      Method:",
                    match["match_method"]
                )

                new_warehouse = Warehouse(
                    organization_id=organization.id,
                    name=(
                        "MSWC "
                        + name
                    ),
                    code=(
                        "MSWC-"
                        + code
                    ),
                    address=warehouse["address"],
                    latitude=match["latitude"],
                    longitude=match["longitude"],
                    capacity_sqm=None,
                    is_active=True,
                )

                db.add(new_warehouse)
                db.commit()

                imported += 1

                report_rows.append({
                    "plant_code": code,
                    "warehouse_name": name,
                    "official_address":
                        warehouse["address"],
                    "capacity_mt":
                        warehouse["capacity_mt"],
                    "status":
                        "IMPORTED_VERIFIED",
                    "latitude":
                        match["latitude"],
                    "longitude":
                        match["longitude"],
                    "osm_name":
                        match["osm_name"],
                    "osm_type":
                        match["osm_type"],
                    "osm_id":
                        match["osm_id"],
                    "match_method":
                        match["match_method"],
                })

            # ------------------------------------------------
            # NO VERIFIED MATCH
            # ------------------------------------------------

            else:
                print(
                    "    ⚠ No explicit MSWC OSM "
                    "match found"
                )

                print(
                    "    → NOT creating warehouse"
                )

                needs_review += 1

                report_rows.append({
                    "plant_code": code,
                    "warehouse_name": name,
                    "official_address":
                        warehouse["address"],
                    "capacity_mt":
                        warehouse["capacity_mt"],
                    "status":
                        "NEEDS_COORDINATE_REVIEW",
                    "latitude": "",
                    "longitude": "",
                    "osm_name": "",
                    "osm_type": "",
                    "osm_id": "",
                    "match_method": "",
                })

            print()

            # Be polite to public OSM infrastructure.
            time.sleep(2)

        # ----------------------------------------------------
        # REPORT
        # ----------------------------------------------------

        fieldnames = [
            "plant_code",
            "warehouse_name",
            "official_address",
            "capacity_mt",
            "status",
            "latitude",
            "longitude",
            "osm_name",
            "osm_type",
            "osm_id",
            "match_method",
        ]

        with open(
            REPORT_FILE,
            "w",
            newline="",
            encoding="utf-8"
        ) as csv_file:

            writer = csv.DictWriter(
                csv_file,
                fieldnames=fieldnames
            )

            writer.writeheader()

            writer.writerows(
                report_rows
            )

        print("=" * 70)
        print("IMPORT COMPLETE")
        print("=" * 70)
        print()
        print(
            "Verified imported:",
            imported
        )
        print(
            "Already existed:",
            already_exists
        )
        print(
            "Needs coordinate review:",
            needs_review
        )
        print(
            "Total processed:",
            len(MSWC_WAREHOUSES)
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
            REPORT_FILE
        )
        print()

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()