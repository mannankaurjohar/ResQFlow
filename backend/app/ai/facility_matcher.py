from typing import List, Dict, Any

from app.ai.duplicate_detector import haversine_distance_km
from app.schemas import (
    AIFacilitySupportRecommendation,
    MatchedFacility,
)


FACILITY_ROLE_MAPPING = {
    "Hospital": "Medical Support",
    "Clinic": "Medical Support",
    "Pharmacy": "Medical Supplies",
    "Shelter": "Evacuation / Relief",
    "School": "Potential Relief Site",
    "Community Centre": "Relief / Community Coordination",
    "Police Station": "Security / Coordination",
    "Fire Station": "Rescue / Emergency Response",
}


def get_facility_role(facility_type: str) -> str:
    return FACILITY_ROLE_MAPPING.get(
        facility_type,
        "Emergency Support",
    )


def get_relevant_facility_types(
    request_items: List[Any],
) -> List[str]:
    """
    Determine which facility types are relevant to the
    community request.

    This does NOT assume that facilities have inventory.
    It only identifies potentially useful support locations.
    """

    categories = " ".join(
        (
            f"{item.category} "
            f"{item.item_name}"
        ).lower()
        for item in request_items
    )

    relevant_types = []

    # Medical requirements
    medical_keywords = [
        "medicine",
        "medical",
        "medicine",
        "first aid",
        "injury",
        "doctor",
        "health",
        "ambulance",
        "hospital",
    ]

    if any(keyword in categories for keyword in medical_keywords):
        relevant_types.extend([
            "Hospital",
            "Clinic",
            "Pharmacy",
        ])

    # Evacuation / shelter requirements
    shelter_keywords = [
        "shelter",
        "evacuation",
        "displaced",
        "homeless",
        "accommodation",
        "rescue",
    ]

    if any(keyword in categories for keyword in shelter_keywords):
        relevant_types.extend([
            "Shelter",
            "Community Centre",
            "School",
        ])

    # Security / rescue support
    emergency_keywords = [
        "rescue",
        "trapped",
        "missing",
        "security",
        "emergency",
    ]

    if any(keyword in categories for keyword in emergency_keywords):
        relevant_types.extend([
            "Police Station",
            "Fire Station",
        ])

    # If the request contains no clearly identifiable
    # support category, show general emergency facilities.
    if not relevant_types:
        relevant_types = [
            "Hospital",
            "Shelter",
            "Community Centre",
            "Fire Station",
        ]

    return list(dict.fromkeys(relevant_types))


def match_facilities_for_request(
    request: Any,
    facilities: List[Dict[str, Any]],
    max_results: int = 8,
) -> AIFacilitySupportRecommendation:

    relevant_types = get_relevant_facility_types(
        request.items
    )

    matched_facilities = []

    for facility in facilities:

        facility_type = facility.get(
            "facility_type",
            "Not reported",
        )

        if facility_type not in relevant_types:
            continue

        latitude = facility.get("latitude")
        longitude = facility.get("longitude")

        if latitude is None or longitude is None:
            continue

        distance_km = haversine_distance_km(
            request.latitude,
            request.longitude,
            latitude,
            longitude,
        )

        matched_facilities.append(
            (
                distance_km,
                MatchedFacility(
                    osm_id=facility["osm_id"],
                    osm_type=facility["osm_type"],
                    name=facility["name"],
                    facility_type=facility_type,
                    support_role=get_facility_role(
                        facility_type
                    ),
                    distance_km=round(
                        distance_km,
                        1,
                    ),
                    address=facility.get(
                        "address",
                        "Not reported",
                    ),
                    phone=facility.get(
                        "phone",
                        "Not reported",
                    ),
                    website=facility.get(
                        "website",
                        "Not reported",
                    ),
                    source=facility.get(
                        "source",
                        "OpenStreetMap",
                    ),
                    source_url=facility.get(
                        "source_url",
                        "Not reported",
                    ),
                    live_inventory=facility.get(
                        "live_inventory",
                        "Not reported",
                    ),
                    operational_status=facility.get(
                        "operational_status",
                        "Not reported",
                    ),
                ),
            )
        )

    # Nearest relevant facilities first
    matched_facilities.sort(
        key=lambda item: item[0]
    )

    selected_facilities = [
        item[1]
        for item in matched_facilities[:max_results]
    ]

    if selected_facilities:
        summary_rationale = (
            f"Identified {len(selected_facilities)} "
            f"nearby publicly mapped facilities relevant "
            f"to this request. Facilities are ranked by "
            f"geographical proximity. Live inventory, "
            f"capacity, and operational status are not "
            f"assumed unless reported by a verified source."
        )
    else:
        summary_rationale = (
            "No relevant publicly mapped facilities were "
            "identified near this request. This does not "
            "confirm that suitable facilities are unavailable."
        )

    return AIFacilitySupportRecommendation(
        request_id=request.id,
        request_tracking_code=request.tracking_code,
        location_name=request.location_name,
        summary_rationale=summary_rationale,
        facilities=selected_facilities,
    )