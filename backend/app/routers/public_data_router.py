import asyncio
import json
import time
from pathlib import Path
from typing import Optional

import httpx
from fastapi import APIRouter, HTTPException, Query


router = APIRouter(
    prefix="/public-data",
    tags=["Public Data"],
)


# ============================================================
# OVERPASS SERVERS
# ============================================================

OVERPASS_URLS = [
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
    "https://overpass.osm.jp/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
    "https://overpass-api.de/api/interpreter",
]


# ============================================================
# CACHE
# ============================================================

# Freshness window for facility data.
# Cached data older than this is still usable, but will be
# refreshed in the background when possible.
CACHE_TTL_SECONDS = 300

# Maximum age of cached data that can still be served immediately.
# This prevents the first request after a Render restart from
# waiting for Overpass.
STALE_CACHE_MAX_AGE_SECONDS = 24 * 60 * 60  # 24 hours

FACILITY_CACHE = {}

# Prevent multiple requests from triggering the same Overpass refresh.
FACILITY_REFRESH_TASKS = {}

DISK_CACHE_FILE = (
    Path(__file__).resolve().parent.parent
    / "facility_cache.json"
)


def get_cache_key(
    facility_type: str,
    region: Optional[str],
    latitude: float,
    longitude: float,
    radius_m: int,
):
    """
    Generate a unique cache key for a facility request.
    """

    return (
        facility_type,
        region,
        round(latitude, 5),
        round(longitude, 5),
        radius_m,
    )


def cache_key_to_string(cache_key):
    """
    Convert tuple cache key into a JSON-safe string.
    """

    return "|".join(
        str(value)
        for value in cache_key
    )


def get_cached_facilities(cache_key):
    """
    Return a valid in-memory cached result.

    Returns None when:
    - cache entry does not exist
    - cache entry has expired
    """

    cached = FACILITY_CACHE.get(cache_key)

    if not cached:
        return None

    cached_time, cached_data = cached

    if (
        time.monotonic() - cached_time
        > CACHE_TTL_SECONDS
    ):
        FACILITY_CACHE.pop(
            cache_key,
            None,
        )

        return None

    return cached_data

def get_stale_memory_facilities(cache_key):
    """
    Return cached facility data even if it is older than the
    normal freshness TTL, provided it is not older than the
    maximum allowed stale-cache age.
    """

    cached = FACILITY_CACHE.get(cache_key)

    if not cached:
        return None

    cached_time, cached_data = cached

    age = time.monotonic() - cached_time

    if age > STALE_CACHE_MAX_AGE_SECONDS:
        return None

    return cached_data

def set_cached_facilities(
    cache_key,
    data,
):
    """
    Save facility result to:
    1. memory cache
    2. disk cache
    """

    # --------------------------------------------------------
    # MEMORY CACHE
    # --------------------------------------------------------

    FACILITY_CACHE[cache_key] = (
        time.monotonic(),
        data,
    )

    # --------------------------------------------------------
    # DISK CACHE
    # --------------------------------------------------------

    try:

        disk_cache = {}

        if DISK_CACHE_FILE.exists():

            with open(
                DISK_CACHE_FILE,
                "r",
                encoding="utf-8",
            ) as f:

                existing_cache = json.load(f)

                if isinstance(
                    existing_cache,
                    dict,
                ):
                    disk_cache = existing_cache

        cache_key_string = cache_key_to_string(
            cache_key
        )

        disk_cache[
            cache_key_string
        ] = {
            "cached_at": time.time(),
            "data": data,
        }

        with open(
            DISK_CACHE_FILE,
            "w",
            encoding="utf-8",
        ) as f:

            json.dump(
                disk_cache,
                f,
                indent=2,
            )

        print(
            "Saved facility result to disk cache."
        )

    except Exception as exc:

        print(
            "Failed to save facility cache: "
            f"{exc}"
        )


def load_disk_cache(
    cache_key,
):
    """
    Load a specific facility result from disk cache.

    Disk cache is also subject to the same TTL.
    """

    if not DISK_CACHE_FILE.exists():
        return None

    try:

        with open(
            DISK_CACHE_FILE,
            "r",
            encoding="utf-8",
        ) as f:

            disk_cache = json.load(f)

        if not isinstance(
            disk_cache,
            dict,
        ):
            return None

        cache_key_string = cache_key_to_string(
            cache_key
        )

        cached_entry = disk_cache.get(
            cache_key_string
        )

        if not cached_entry:
            return None

        cached_at = cached_entry.get(
            "cached_at"
        )

        cached_data = cached_entry.get(
            "data"
        )

        if (
            cached_at is None
            or cached_data is None
        ):
            return None

                # ----------------------------------------------------
        # CHECK MAXIMUM DISK CACHE AGE
        # ----------------------------------------------------

        cache_age = time.time() - cached_at

        if cache_age > STALE_CACHE_MAX_AGE_SECONDS:
            return None

        return cached_data

    except Exception as exc:

        print(
            "Failed to load facility cache: "
            f"{exc}"
        )

        return None


# ============================================================
# FACILITY FILTERS
# ============================================================

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


# ============================================================
# TYPE MAPPING
# ============================================================

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


# ============================================================
# BUILD OVERPASS QUERY
# ============================================================

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
        Search within the specified radius.
    """

    filters = FACILITY_FILTERS[
        facility_type
    ]

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
                    around:{radius_m},
                    {latitude},
                    {longitude}
                );
                """
            )

    if region == "nashik":

        return f"""
        [out:json][timeout:45];

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
    [out:json][timeout:30];

    (
        {"".join(query_parts)}
    );

    out center tags;
    """


# ============================================================
# OVERPASS REQUEST
# ============================================================

async def fetch_from_overpass(
    client: httpx.AsyncClient,
    overpass_url: str,
    query: str,
):
    """
    Query one Overpass server.
    """

    try:

        print(
            "Trying Overpass endpoint: "
            f"{overpass_url}"
        )

        response = await client.post(
            overpass_url,
            data={
                "data": query
            },
        )

        response.raise_for_status()

        print(
            "Overpass request succeeded: "
            f"{overpass_url}"
        )

        return response

    except httpx.TimeoutException:

        print(
            "Overpass timeout: "
            f"{overpass_url}"
        )

        return None

    except httpx.HTTPError as exc:

        print(
            "Overpass failed: "
            f"{overpass_url} -> {exc}"
        )

        return None

    except Exception as exc:

        print(
            "Unexpected Overpass error: "
            f"{overpass_url} -> {exc}"
        )

        return None


async def fetch_overpass_parallel(
    query: str,
    headers: dict,
):
    """
    Query all Overpass servers simultaneously.

    The first successful response is used.
    """

    timeout = httpx.Timeout(
        connect=5.0,
        read=25.0,
        write=10.0,
        pool=5.0,
    )

    async with httpx.AsyncClient(
        timeout=timeout,
        headers=headers,
        follow_redirects=True,
    ) as client:

        tasks = [
            asyncio.create_task(
                fetch_from_overpass(
                    client,
                    url,
                    query,
                )
            )
            for url in OVERPASS_URLS
        ]

        pending = set(tasks)

        try:

            while pending:

                done, pending = await asyncio.wait(
                    pending,
                    return_when=asyncio.FIRST_COMPLETED,
                )

                for task in done:

                    try:

                        response = task.result()

                    except Exception:

                        response = None

                    if response is not None:

                        # Cancel slower requests.
                        for remaining in pending:

                            remaining.cancel()

                        await asyncio.gather(
                            *pending,
                            return_exceptions=True,
                        )

                        return response

            return None

        finally:

            for task in pending:

                if not task.done():

                    task.cancel()

async def refresh_facilities_in_background(
    cache_key,
    selected_type,
    selected_region,
    latitude,
    longitude,
    radius_m,
):
    """
    Refresh facility data from Overpass without making the
    user wait when stale cached data is already available.
    """

    # Prevent duplicate refresh requests for the same cache key.
    existing_task = FACILITY_REFRESH_TASKS.get(cache_key)

    if existing_task is not None and not existing_task.done():
        return

    async def _refresh():
        try:
            print(
                "Background facility refresh started:",
                cache_key,
            )

            query = build_facility_query(
                facility_type=selected_type,
                region=selected_region,
                latitude=latitude,
                longitude=longitude,
                radius_m=radius_m,
            )

            headers = {
                "User-Agent": (
                    "ResQFlow-AI/1.0 "
                    "(emergency-relief-platform)"
                ),
                "Referer": "http://localhost:8000/",
                "Accept": "application/json",
            }

            response = await fetch_overpass_parallel(
                query=query,
                headers=headers,
            )

            if response is None:
                print(
                    "Background facility refresh failed: "
                    "all Overpass services unavailable."
                )
                return

            try:
                data = response.json()
            except ValueError:
                print(
                    "Background facility refresh failed: "
                    "invalid Overpass response."
                )
                return

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

                if (
                    element_lat is None
                    or element_lon is None
                ):
                    center = element.get("center", {})

                    element_lat = center.get("lat")
                    element_lon = center.get("lon")

                if (
                    element_lat is None
                    or element_lon is None
                ):
                    continue

                amenity = tags.get(
                    "amenity",
                    "Not reported",
                )

                facility_name = (
                    tags.get("name")
                    or "Not reported"
                )

                address_parts = [
                    tags.get("addr:housenumber"),
                    tags.get("addr:street"),
                    tags.get("addr:suburb"),
                    tags.get("addr:city"),
                    tags.get("addr:district"),
                    tags.get("addr:state"),
                ]

                address_parts = [
                    part
                    for part in address_parts
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
                            (
                                amenity
                                .replace("_", " ")
                                .title()
                                if amenity != "Not reported"
                                else "Not reported"
                            ),
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

            result = {
                "source": "OpenStreetMap",
                "source_url": (
                    "https://www.openstreetmap.org/"
                ),
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

            set_cached_facilities(
                cache_key,
                result,
            )

            print(
                "Background facility refresh completed: "
                f"{len(facilities)} facilities"
            )

        except Exception as exc:
            print(
                "Background facility refresh failed: "
                f"{exc}"
            )

        finally:
            FACILITY_REFRESH_TASKS.pop(
                cache_key,
                None,
            )

    task = asyncio.create_task(_refresh())

    FACILITY_REFRESH_TASKS[cache_key] = task
# ============================================================
# PUBLIC FACILITIES ENDPOINT
# ============================================================

@router.get("/facilities")
async def get_public_facilities(

    region: Optional[str] = Query(
        None,
        description=(
            "Geographical region. "
            "Currently supported: nashik"
        ),
    ),

    latitude: float = Query(
        20.0059,
        description=(
            "Center latitude for "
            "radius-based search"
        ),
    ),

    longitude: float = Query(
        73.7897,
        description=(
            "Center longitude for "
            "radius-based search"
        ),
    ),

    radius_m: int = Query(
        15000,
        ge=1000,
        le=50000,
        description=(
            "Radius for radius-based search"
        ),
    ),

    facility_type: Optional[str] = Query(
        "all",
        description=(
            "hospital, clinic, pharmacy, "
            "shelter, school, police, "
            "fire_station, or all"
        ),
    ),
):
    """
    Retrieve publicly mapped
    emergency-relevant facilities.

    region=nashik:
        Search entire Nashik district.

    region omitted:
        Use coordinate + radius search.

    Data source:
        OpenStreetMap through Overpass API.

    Results:
        Cached for 5 minutes.
    """

    # ========================================================
    # NORMALIZE INPUT
    # ========================================================

    selected_type = (
        facility_type or "all"
    ).strip().lower()

    selected_region = (
        region.strip().lower()
        if region
        else None
    )

    # ========================================================
    # VALIDATION
    # ========================================================

    if selected_type not in FACILITY_FILTERS:

        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid facility_type. "
                "Use: hospital, clinic, pharmacy, "
                "shelter, school, police, "
                "fire_station, or all."
            ),
        )

    if selected_region not in (
        None,
        "nashik",
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid region. "
                "Currently supported region: nashik."
            ),
        )

    # ========================================================
    # CACHE KEY
    # ========================================================

    cache_key = get_cache_key(
        facility_type=selected_type,
        region=selected_region,
        latitude=latitude,
        longitude=longitude,
        radius_m=radius_m,
    )

    print(
        "Facility request:",
        cache_key,
    )

        # ========================================================
    # MEMORY CACHE CHECK
    # ========================================================

    cached_result = get_cached_facilities(
        cache_key
    )

    if cached_result is not None:

        print(
            "Returning memory-cached public facilities: "
            f"{len(cached_result.get('facilities', []))} "
            "facilities"
        )

        return cached_result

    # ========================================================
    # STALE MEMORY CACHE CHECK
    # ========================================================

    stale_memory_result = get_stale_memory_facilities(
        cache_key
    )

    if stale_memory_result is not None:

        print(
            "Returning stale memory-cached public facilities "
            "and refreshing in background."
        )

        asyncio.create_task(
            refresh_facilities_in_background(
                cache_key=cache_key,
                selected_type=selected_type,
                selected_region=selected_region,
                latitude=latitude,
                longitude=longitude,
                radius_m=radius_m,
            )
        )

        return stale_memory_result

    # ========================================================
    # DISK CACHE CHECK
    # ========================================================

    disk_result = load_disk_cache(
        cache_key
    )

    if disk_result is not None:

        print(
            "Returning disk-cached public facilities: "
            f"{len(disk_result.get('facilities', []))} "
            "facilities"
        )

        # Restore disk result into memory cache.
        FACILITY_CACHE[cache_key] = (
            time.monotonic(),
            disk_result,
        )

        # If the disk cache is older than the normal
        # freshness window, refresh it in the background.
        disk_cache_age = 0

        try:
            with open(
                DISK_CACHE_FILE,
                "r",
                encoding="utf-8",
            ) as f:
                disk_cache_data = json.load(f)

            cache_key_string = cache_key_to_string(
                cache_key
            )

            cached_entry = disk_cache_data.get(
                cache_key_string
            )

            if cached_entry:
                cached_at = cached_entry.get(
                    "cached_at"
                )

                if cached_at:
                    disk_cache_age = (
                        time.time() - cached_at
                    )

        except Exception:
            disk_cache_age = 0

        if disk_cache_age > CACHE_TTL_SECONDS:

            print(
                "Disk cache is stale. "
                "Refreshing in background."
            )

            asyncio.create_task(
                refresh_facilities_in_background(
                    cache_key=cache_key,
                    selected_type=selected_type,
                    selected_region=selected_region,
                    latitude=latitude,
                    longitude=longitude,
                    radius_m=radius_m,
                )
            )

        return disk_result

    cached_result = get_cached_facilities(
        cache_key
    )

    if cached_result is not None:

        print(
            "Returning memory-cached public facilities: "
            f"{len(cached_result.get('facilities', []))} "
            "facilities"
        )

        return cached_result

    # ========================================================
    # DISK CACHE CHECK
    # ========================================================

    disk_result = load_disk_cache(
        cache_key
    )

    if disk_result is not None:

        print(
            "Returning disk-cached public facilities: "
            f"{len(disk_result.get('facilities', []))} "
            "facilities"
        )

        # Restore disk result into memory cache.
        FACILITY_CACHE[cache_key] = (
            time.monotonic(),
            disk_result,
        )

        return disk_result

    # ========================================================
    # BUILD QUERY
    # ========================================================

    query = build_facility_query(
        facility_type=selected_type,
        region=selected_region,
        latitude=latitude,
        longitude=longitude,
        radius_m=radius_m,
    )

    print(
        "Built Overpass query for "
        f"{selected_type} / "
        f"{selected_region or 'radius'}"
    )

    # ========================================================
    # OVERPASS HEADERS
    # ========================================================

    headers = {
        "User-Agent": (
            "ResQFlow-AI/1.0 "
            "(emergency-relief-platform)"
        ),
        "Referer": "http://localhost:8000/",
        "Accept": "application/json",
    }

    # ========================================================
    # PARALLEL OVERPASS REQUEST
    # ========================================================

    response = await fetch_overpass_parallel(
        query=query,
        headers=headers,
    )

    # ========================================================
    # ALL SERVERS FAILED
    # ========================================================

    if response is None:

        raise HTTPException(
            status_code=502,
            detail=(
                "All OpenStreetMap Overpass services "
                "are currently unavailable."
            ),
        )

    # ========================================================
    # PARSE RESPONSE
    # ========================================================

    try:

        data = response.json()

    except ValueError:

        raise HTTPException(
            status_code=502,
            detail=(
                "OpenStreetMap returned "
                "an invalid response."
            ),
        )

    # ========================================================
    # CONVERT OSM ELEMENTS
    # ========================================================

    facilities = []

    seen = set()

    for element in data.get(
        "elements",
        [],
    ):

        osm_id = element.get(
            "id"
        )

        osm_type = element.get(
            "type"
        )

        unique_key = (
            f"{osm_type}-{osm_id}"
        )

        if unique_key in seen:

            continue

        seen.add(
            unique_key
        )

        tags = element.get(
            "tags",
            {},
        )

        # ----------------------------------------------------
        # COORDINATES
        # ----------------------------------------------------

        element_lat = element.get(
            "lat"
        )

        element_lon = element.get(
            "lon"
        )

        if (
            element_lat is None
            or element_lon is None
        ):

            center = element.get(
                "center",
                {},
            )

            element_lat = center.get(
                "lat"
            )

            element_lon = center.get(
                "lon"
            )

        if (
            element_lat is None
            or element_lon is None
        ):

            continue

        # ----------------------------------------------------
        # FACILITY TYPE
        # ----------------------------------------------------

        amenity = tags.get(
            "amenity",
            "Not reported",
        )

        # ----------------------------------------------------
        # NAME
        # ----------------------------------------------------

        facility_name = (
            tags.get("name")
            or "Not reported"
        )

        # ----------------------------------------------------
        # ADDRESS
        # ----------------------------------------------------

        address_parts = [

            tags.get(
                "addr:housenumber"
            ),

            tags.get(
                "addr:street"
            ),

            tags.get(
                "addr:suburb"
            ),

            tags.get(
                "addr:city"
            ),

            tags.get(
                "addr:district"
            ),

            tags.get(
                "addr:state"
            ),
        ]

        address_parts = [
            part
            for part in address_parts
            if part
        ]

        address = (
            ", ".join(address_parts)
            if address_parts
            else "Not reported"
        )

        # ----------------------------------------------------
        # FINAL FACILITY OBJECT
        # ----------------------------------------------------

        facilities.append(
            {
                "osm_id": osm_id,

                "osm_type": osm_type,

                "name": facility_name,

                "facility_type": TYPE_MAPPING.get(
                    amenity,
                    (
                        amenity
                        .replace(
                            "_",
                            " ",
                        )
                        .title()
                        if amenity != "Not reported"
                        else "Not reported"
                    ),
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

                "live_inventory": (
                    "Not reported"
                ),

                "operational_status": (
                    "Not reported"
                ),
            }
        )

    # ========================================================
    # SORT
    # ========================================================

    facilities.sort(
        key=lambda item: (
            item["facility_type"],
            item["name"],
        )
    )

    # ========================================================
    # FINAL RESPONSE
    # ========================================================

    result = {

        "source": "OpenStreetMap",

        "source_url": (
            "https://www.openstreetmap.org/"
        ),

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

        "facility_count": len(
            facilities
        ),

        "facilities": facilities,
    }

    # ========================================================
    # SAVE TO CACHE
    # ========================================================

    set_cached_facilities(
        cache_key,
        result,
    )

    print(
        "Cached public facilities: "
        f"{len(facilities)} facilities "
        f"for {CACHE_TTL_SECONDS} seconds"
    )

    # ========================================================
    # RETURN RESPONSE
    # ========================================================

    return result