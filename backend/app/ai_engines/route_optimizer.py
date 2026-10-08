import math
from typing import List, Dict, Tuple

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates the great-circle distance between two points on Earth in kilometers."""
    R = 6371.0 # Earth's radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def calculate_eta(distance_km: float, average_speed_kmh: float = 45.0, traffic_factor: float = 1.2) -> float:
    """Calculates estimated arrival time (ETA) in minutes considering average speed & live traffic factor."""
    if distance_km <= 0:
        return 1.0
    effective_speed = average_speed_kmh / traffic_factor
    time_hours = distance_km / effective_speed
    return round(time_hours * 60, 1)

def find_nearest_ambulance(patient_lat: float, patient_lon: float, ambulances: List[Dict]) -> Dict:
    """
    Scans list of available ambulances and selects the nearest available unit.
    """
    available_ambulances = [a for a in ambulances if a.get("status") == "AVAILABLE"]
    if not available_ambulances:
        # Fallback to any ambulance if all busy
        available_ambulances = ambulances

    if not available_ambulances:
        return None

    best_ambulance = None
    min_distance = float('inf')

    for amb in available_ambulances:
        dist = haversine_distance(patient_lat, patient_lon, amb["latitude"], amb["longitude"])
        if dist < min_distance:
            min_distance = dist
            best_ambulance = amb

    eta = calculate_eta(min_distance, average_speed_kmh=50.0, traffic_factor=1.1)

    return {
        "ambulance": best_ambulance,
        "distance_km": round(min_distance, 2),
        "eta_minutes": eta
    }

def get_route_waypoints(start_lat: float, start_lon: float, end_lat: float, end_lon: float, steps: int = 5) -> List[Tuple[float, float]]:
    """Generates linear route waypoints between start and destination for map visualization."""
    waypoints = []
    for i in range(steps + 1):
        fraction = i / steps
        lat = start_lat + fraction * (end_lat - start_lat)
        lon = start_lon + fraction * (end_lon - start_lon)
        waypoints.append((round(lat, 6), round(lon, 6)))
    return waypoints
