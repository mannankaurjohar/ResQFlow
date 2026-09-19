from typing import Optional

import httpx
from fastapi import APIRouter, HTTPException, Query

router = APIRouter(
    prefix="/public-data",
    tags=["Public Data"],
)
OVERPASS_URLS = [
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
    "https://overpass.osm.jp/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
    "https://overpass-api.de/api/interpreter",
]


FACILITY_FILTERS = {
    "hospital": [
        'nwr["amenity"="hospital"]',
    ],
    "clinic": [
        'nwr["amenity"="clinic"]',
    ],
    "pharmacy": [
        'nwr["amenity"="pharmacy"]',
    ],
   "shelter": [
    'nwr["amenity"="shelter"]',
],
    "school": [
        'nwr["amenity"="school"]',
    ],
    "police": [
        'nwr["amenity"="police"]',
    ],
    "fire_station": [
        'nwr["amenity"="fire_station"]',
    ],
    "all": [
        'nwr["amenity"="hospital"]',
        'nwr["amenity"="clinic"]',
        'nwr["amenity"="pharmacy"]',
        'nwr["amenity"="shelter"]',
        'nwr["amenity"="community_centre"]',
        'nwr["amenity"="school"]',
        'nwr["amenity"="police"]',
        'nwr["amenity"="fire_station"]',
    ],
}


TYPE_MAPPING = {
    "hospital": "Hospital",
    "clinic": "Clinic",
    "pharmacy": "Pharmacy",
    "shelter": "Shelter",
    "community_centre": "Community Centre",
    "school": "School",
    "police": "Police Station",
    "fire_station": "Fire Station",
}


def build_facility_query(
    facility_type: str,
    region: Optional[str],
    latitude: float,
    longitude: float,
    radius_m: int,
):
    """
    Build an Overpass query.

    region=nashik:
        Search the entire Nashik district.

    region omitted:
        Preserve the original radius-based search behaviour.
    """

    filters = FACILITY_FILTERS[facility_type]

    query_parts = []

    for element_filter in filters:
        if region == "nashik":
            query_parts.append(
                f"""
                {element_filter}(area.search_area);
                """
            )
        else:
            query_parts.append(
                f"""
                {element_filter}(
                    around:{radius_m},{latitude},{longitude}
                );
                """
            )

    if region == "nashik":
        return f"""
        [out:json][timeout:120];

        area["name"="Nashik"]
             ["boundary"="administrative"]
             ["admin_level"="5"]
             ->.search_area;

        (
            {"".join(query_parts)}
        );

        out center tags;
        """

    return f"""
    [out:json][timeout:60];

    (
        {"".join(query_parts)}
    );

    out center tags;
    """


@router.get("/facilities")
async def get_public_facilities(
    region: Optional[str] = Query(
        None,
        description="Geographical region. Currently supported: nashik",
    ),
    latitude: float = Query(
        20.0059,
        description="Center latitude for radius-based search",
    ),
    longitude: float = Query(
        73.7897,
        description="Center longitude for radius-based search",
    ),
    radius_m: int = Query(
        15000,
        ge=1000,
        le=50000,
        description="Radius for radius-based search",
    ),
    facility_type: Optional[str] = Query(
        "all",
        description=(
            "hospital, clinic, pharmacy, shelter, school, "
            "police, fire_station, or all"
        ),
    ),
):
    """
    Retrieve publicly mapped emergency-relevant facilities.

    Supported geographical mode:
    - region=nashik -> entire Nashik district

    If region is omitted, the endpoint keeps the original
    coordinate + radius behaviour.

    This endpoint does NOT provide live inventory.
    Missing operational information is returned as 'Not reported'.
    """

    selected_type = (facility_type or "all").lower()
    selected_region = region.lower() if region else None

    if selected_type not in FACILITY_FILTERS:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid facility_type. Use: "
                "hospital, clinic, pharmacy, shelter, school, "
                "police, fire_station, or all."
            ),
        )

    if selected_region not in (None, "nashik"):
        raise HTTPException(
            status_code=400,
            detail="Invalid region. Currently supported region: nashik.",
        )

    query = build_facility_query(
        facility_type=selected_type,
        region=selected_region,
        latitude=latitude,
        longitude=longitude,
        radius_m=radius_m,
    )

    response = None
    last_error = None

    headers = {
        "User-Agent": (
            "ResQFlow-AI/1.0 "
            "(emergency-relief-platform)"
        ),
        "Referer": "http://localhost:8000/",
        "Accept": "application/json",
    }

    async with httpx.AsyncClient(
        timeout=140.0,
        headers=headers,
    ) as client:

        for overpass_url in OVERPASS_URLS:
            try:
                print(
                    f"Trying Overpass endpoint: "
                    f"{overpass_url}"
                )

                response = await client.post(
                    overpass_url,
                    data={"data": query},
                )

                response.raise_for_status()

                print(
                    f"Overpass request succeeded: "
                    f"{overpass_url}"
                )

                break

            except httpx.TimeoutException as exc:
                last_error = exc
                print(
                    f"Overpass timeout: "
                    f"{overpass_url}"
                )

            except httpx.HTTPError as exc:
                last_error = exc
                print(
                    f"Overpass failed: "
                    f"{overpass_url} -> {exc}"
                )

    if response is None:
        raise HTTPException(
            status_code=502,
            detail=(
                "All OpenStreetMap Overpass services "
                "are currently unavailable."
            ),
        )


    try:
        data = response.json()
    except ValueError:
        raise HTTPException(
            status_code=502,
            detail="OpenStreetMap returned an invalid response.",
        )

    facilities = []
    seen = set()

    for element in data.get("elements", []):

        osm_id = element.get("id")
        osm_type = element.get("type")

        unique_key = f"{osm_type}-{osm_id}"

        if unique_key in seen:
            continue

        seen.add(unique_key)

        tags = element.get("tags", {})

        element_lat = element.get("lat")
        element_lon = element.get("lon")

        if element_lat is None or element_lon is None:
            center = element.get("center", {})
            element_lat = center.get("lat")
            element_lon = center.get("lon")

        if element_lat is None or element_lon is None:
            continue

        amenity = tags.get(
            "amenity",
            "Not reported",
        )

        facility_name = tags.get(
            "name"
        ) or "Not reported"

        address_parts = [
            tags.get("addr:housenumber"),
            tags.get("addr:street"),
            tags.get("addr:suburb"),
            tags.get("addr:city"),
            tags.get("addr:district"),
            tags.get("addr:state"),
        ]

        address_parts = [
            part for part in address_parts
            if part
        ]

        address = (
            ", ".join(address_parts)
            if address_parts
            else "Not reported"
        )

        facilities.append(
            {
                "osm_id": osm_id,
                "osm_type": osm_type,
                "name": facility_name,
                "facility_type": TYPE_MAPPING.get(
                    amenity,
                    amenity.replace("_", " ").title()
                    if amenity != "Not reported"
                    else "Not reported",
                ),
                "latitude": element_lat,
                "longitude": element_lon,
                "address": address,
                "phone": tags.get(
                    "phone",
                    "Not reported",
                ),
                "website": tags.get(
                    "website",
                    "Not reported",
                ),
                "source": "OpenStreetMap",
                "source_url": (
                    "https://www.openstreetmap.org/"
                    f"{osm_type}/{osm_id}"
                ),
                "live_inventory": "Not reported",
                "operational_status": "Not reported",
            }
        )

    facilities.sort(
        key=lambda item: (
            item["facility_type"],
            item["name"],
        )
    )

    return {
        "source": "OpenStreetMap",
        "source_url": "https://www.openstreetmap.org/",
        "region": (
            "Nashik District"
            if selected_region == "nashik"
            else "Radius Search"
        ),
        "search_mode": (
            "district"
            if selected_region == "nashik"
            else "radius"
        ),
        "center": {
            "latitude": latitude,
            "longitude": longitude,
        },
        "radius_m": (
            None
            if selected_region == "nashik"
            else radius_m
        ),
        "facility_type": selected_type,
        "facility_count": len(facilities),
        "facilities": facilities,
    }