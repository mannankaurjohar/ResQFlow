import math
from typing import List, Tuple, Optional

from app.models import CommunityRequest


def haversine_distance_km(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
) -> float:
    """Calculate distance between two coordinates in km."""

    R = 6371.0

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    return R * c


def token_jaccard_similarity(
    text1: str,
    text2: str
) -> float:
    """Simple word-overlap similarity."""

    words1 = set(
        text1.lower()
        .replace(",", " ")
        .replace(".", " ")
        .split()
    )

    words2 = set(
        text2.lower()
        .replace(",", " ")
        .replace(".", " ")
        .split()
    )

    if not words1 or not words2:
        return 0.0

    intersection = words1.intersection(words2)
    union = words1.union(words2)

    return len(intersection) / len(union)


def item_similarity(
    target_request: CommunityRequest,
    existing_request: CommunityRequest
) -> float:
    """Compare requested resource categories."""

    target_categories = {
        item.category.strip().lower()
        for item in target_request.items
        if item.category
    }

    existing_categories = {
        item.category.strip().lower()
        for item in existing_request.items
        if item.category
    }

    if not target_categories or not existing_categories:
        return 0.0

    intersection = (
        target_categories &
        existing_categories
    )

    union = (
        target_categories |
        existing_categories
    )

    return len(intersection) / len(union)


def detect_duplicates(
    target_request: CommunityRequest,
    existing_requests: List[CommunityRequest]
) -> Tuple[
    bool,
    Optional[CommunityRequest],
    float,
    str
]:

    best_similarity = 0.0
    duplicate_candidate = None
    reason = ""

    target_location = (
        target_request.location_name
        .strip()
        .lower()
    )

    target_text = (
        f"{target_request.raw_description} "
        f"{target_request.location_name}"
    )

    for req in existing_requests:

        # -----------------------------------------------------
        # Never compare the request against itself
        # -----------------------------------------------------

        if req.id == target_request.id:
            continue

        # -----------------------------------------------------
        # Ignore completed/rejected requests when searching
        # for an active duplicate.
        # -----------------------------------------------------

        req_status = str(
            req.status
        ).upper()

        if req_status in {
            "REJECTED",
            "DELIVERED",
            "CANCELLED",
            "CANCELED"
        }:
            continue

        # -----------------------------------------------------
        # Geographic distance
        # -----------------------------------------------------

        if (
            target_request.latitude is None
            or target_request.longitude is None
            or req.latitude is None
            or req.longitude is None
        ):
            dist_km = 999.0
        else:
            dist_km = haversine_distance_km(
                target_request.latitude,
                target_request.longitude,
                req.latitude,
                req.longitude
            )

        # -----------------------------------------------------
        # Text similarity
        # -----------------------------------------------------

        existing_text = (
            f"{req.raw_description} "
            f"{req.location_name}"
        )

        text_sim = token_jaccard_similarity(
            target_text,
            existing_text
        )

        # -----------------------------------------------------
        # Location similarity
        # -----------------------------------------------------

        existing_location = (
            req.location_name
            .strip()
            .lower()
        )

        exact_location_match = (
            target_location ==
            existing_location
        )

        # -----------------------------------------------------
        # Resource similarity
        # -----------------------------------------------------

        cat_sim = item_similarity(
            target_request,
            req
        )

        # =====================================================
        # IMPORTANT:
        #
        # Geographic closeness ALONE is NOT a duplicate.
        # Same location ALONE is NOT a duplicate.
        # Same resource categories ALONE are NOT a duplicate.
        #
        # We require multiple independent signals.
        # =====================================================

        is_candidate = False
        candidate_score = 0.0
        candidate_reason = ""

        # -----------------------------------------------------
        # CASE 1:
        # Same named location + strong textual similarity
        # + meaningful resource overlap
        # -----------------------------------------------------

        if (
            exact_location_match
            and text_sim >= 0.45
            and cat_sim >= 0.50
        ):
            is_candidate = True

            candidate_score = (
                0.45 * text_sim
                + 0.30 * cat_sim
                + 0.25
            )

            candidate_reason = (
                f"Same reported location '{req.location_name}', "
                f"similar description ({int(text_sim * 100)}%), "
                f"and overlapping requested resources "
                f"({int(cat_sim * 100)}%)."
            )

        # -----------------------------------------------------
        # CASE 2:
        # Very close geographically + strong text similarity
        # + resource overlap
        # -----------------------------------------------------

        elif (
            dist_km <= 0.50
            and text_sim >= 0.55
            and cat_sim >= 0.50
        ):
            is_candidate = True

            candidate_score = (
                0.40 * text_sim
                + 0.30 * cat_sim
                + 0.30
            )

            candidate_reason = (
                f"Reports are only {dist_km:.2f} km apart, "
                f"have similar descriptions "
                f"({int(text_sim * 100)}%), "
                f"and overlapping resources "
                f"({int(cat_sim * 100)}%)."
            )

        # -----------------------------------------------------
        # CASE 3:
        # Very strong textual match + very strong resource
        # match, even if location wording differs slightly.
        # -----------------------------------------------------

        elif (
            text_sim >= 0.72
            and cat_sim >= 0.67
            and dist_km <= 1.0
        ):
            is_candidate = True

            candidate_score = (
                0.50 * text_sim
                + 0.30 * cat_sim
                + 0.20
            )

            candidate_reason = (
                f"Highly similar emergency description "
                f"({int(text_sim * 100)}%) and requested "
                f"resources ({int(cat_sim * 100)}%), "
                f"within {dist_km:.2f} km."
            )

        if is_candidate and candidate_score > best_similarity:

            best_similarity = candidate_score
            duplicate_candidate = req

            reason = (
                f"Possible duplicate of "
                f"{req.tracking_code}: "
                f"{candidate_reason}"
            )

    # ---------------------------------------------------------
    # Final threshold
    # ---------------------------------------------------------

    is_duplicate = (
        duplicate_candidate is not None
        and best_similarity >= 0.70
    )

    if not is_duplicate:
        duplicate_candidate = None
        reason = ""

    return (
        is_duplicate,
        duplicate_candidate,
        round(best_similarity, 3),
        reason
    )