import os

AI_DIR = os.path.join(os.path.dirname(__file__), "backend", "app", "ai")

dup_code = """import math
from typing import List, Tuple, Optional
from app.models import CommunityRequest

def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    # Earth radius in kilometers
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def token_jaccard_similarity(text1: str, text2: str) -> float:
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    if not words1 or not words2:
        return 0.0
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    return len(intersection) / len(union)

def detect_duplicates(
    target_request: CommunityRequest,
    existing_requests: List[CommunityRequest]
) -> Tuple[bool, Optional[CommunityRequest], float, str]:
    best_similarity = 0.0
    duplicate_candidate = None
    reason = ""

    for req in existing_requests:
        if req.id == target_request.id:
            continue
            
        # 1. Geographic distance check
        dist_km = haversine_distance_km(
            target_request.latitude, target_request.longitude,
            req.latitude, req.longitude
        )
        
        # 2. Text similarity
        text_sim = token_jaccard_similarity(
            target_request.raw_description + " " + target_request.location_name,
            req.raw_description + " " + req.location_name
        )
        
        # 3. Location name exact or partial match
        loc_match = 1.0 if target_request.location_name.strip().lower() == req.location_name.strip().lower() else 0.0
        
        # 4. Item category overlap
        target_cats = set([it.category.lower() for it in target_request.items]) if target_request.items else set()
        req_cats = set([it.category.lower() for it in req.items]) if req.items else set()
        cat_sim = len(target_cats.intersection(req_cats)) / max(1, len(target_cats.union(req_cats))) if target_cats and req_cats else 0.5
        
        # Combined score calculation
        geo_score = max(0.0, 1.0 - (dist_km / 3.0)) # 1.0 at 0km, 0 at 3km
        
        sim_score = (geo_score * 0.40) + (text_sim * 0.30) + (loc_match * 0.15) + (cat_sim * 0.15)
        
        if sim_score > best_similarity:
            best_similarity = sim_score
            duplicate_candidate = req
            reason = (
                f"Potential duplicate detected — {int(sim_score * 100)}% similarity with {req.tracking_code}. "
                f"Proximity: {dist_km:.2f} km, Location: '{req.location_name}', Resource overlap: {int(cat_sim * 100)}%."
            )
            
    is_duplicate = best_similarity >= 0.70
    return is_duplicate, duplicate_candidate, round(best_similarity, 3), reason
"""

with open(os.path.join(AI_DIR, "duplicate_detector.py"), "w", encoding="utf-8") as f:
    f.write(dup_code)

print("duplicate_detector.py written successfully.")
