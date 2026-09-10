import math
from typing import List, Tuple, Optional, Dict, Any

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points on the earth in kilometers.
    """
    R = 6371.0  # Earth radius in kilometers

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2.0) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c

def point_in_polygon(lat: float, lon: float, polygon: List[Tuple[float, float]]) -> bool:
    """
    Ray-casting algorithm to determine if a point (lat, lon) is inside a polygon.
    polygon is a list of (lat, lon) tuples.
    """
    if not polygon or len(polygon) < 3:
        return False

    n = len(polygon)
    inside = False

    p1_lat, p1_lon = polygon[0]
    for i in range(1, n + 1):
        p2_lat, p2_lon = polygon[i % n]
        if min(p1_lon, p2_lon) < lon <= max(p1_lon, p2_lon):
            if lat <= max(p1_lat, p2_lat):
                if p1_lon != p2_lon:
                    lat_inters = (lon - p1_lon) * (p2_lat - p1_lat) / (p2_lon - p1_lon) + p1_lat
                else:
                    lat_inters = p1_lat
                if p1_lat == p2_lat or lat <= lat_inters:
                    inside = not inside
        p1_lat, p1_lon = p2_lat, p2_lon

    return inside

def match_administrative_location(
    district: Optional[str],
    state: Optional[str],
    city: Optional[str],
    area_description: Optional[str]
) -> bool:
    """
    Checks if user's administrative location matches the alert's area description.
    """
    if not area_description:
        return False

    area_clean = area_description.lower()

    if district:
        d_clean = district.lower().replace("district", "").strip()
        if len(d_clean) >= 3 and d_clean in area_clean:
            return True

    if city:
        c_clean = city.lower().strip()
        if len(c_clean) >= 3 and c_clean in area_clean:
            return True

    # State matching alone can be too broad, but if area_description is specifically for the state
    if state and len(state) >= 4:
        s_clean = state.lower().strip()
        if s_clean in area_clean and ("entire" in area_clean or "all districts" in area_clean or "across" in area_clean):
            return True

    return False

def evaluate_alert_spatial_match(
    user_lat: float,
    user_lon: float,
    district: Optional[str],
    state: Optional[str],
    city: Optional[str],
    alert_centroid_lat: Optional[float],
    alert_centroid_lon: Optional[float],
    alert_radius_km: Optional[float],
    alert_polygon: Optional[List[Tuple[float, float]]],
    area_description: Optional[str],
    regional_threshold_km: float = 150.0
) -> Dict[str, Any]:
    """
    Determines if an alert directly affects the user or is a regional/nearby alert.
    Returns:
      {
        "is_direct": bool,
        "is_regional": bool,
        "distance_km": float,
        "match_type": str ("polygon", "radius", "admin", "proximity", "none")
      }
    """
    # 1. Point in polygon check (Highest precision)
    if alert_polygon and len(alert_polygon) >= 3:
        if point_in_polygon(user_lat, user_lon, alert_polygon):
            return {
                "is_direct": True,
                "is_regional": False,
                "distance_km": 0.0,
                "match_type": "polygon"
            }

    # 2. Administrative region text match
    admin_matched = match_administrative_location(district, state, city, area_description)

    # 3. Centroid distance calculation
    distance_km = None
    if alert_centroid_lat is not None and alert_centroid_lon is not None:
        distance_km = round(haversine_distance(user_lat, user_lon, alert_centroid_lat, alert_centroid_lon), 1)

    # Check alert radius coverage
    radius = alert_radius_km if alert_radius_km and alert_radius_km > 0 else 35.0  # Default ~35km average district/alert radius

    if admin_matched:
        return {
            "is_direct": True,
            "is_regional": False,
            "distance_km": distance_km if distance_km is not None else 0.0,
            "match_type": "admin"
        }

    if distance_km is not None:
        if distance_km <= radius:
            return {
                "is_direct": True,
                "is_regional": False,
                "distance_km": distance_km,
                "match_type": "radius"
            }
        elif distance_km <= regional_threshold_km:
            return {
                "is_direct": False,
                "is_regional": True,
                "distance_km": distance_km,
                "match_type": "proximity"
            }

    return {
        "is_direct": False,
        "is_regional": False,
        "distance_km": distance_km,
        "match_type": "none"
    }
