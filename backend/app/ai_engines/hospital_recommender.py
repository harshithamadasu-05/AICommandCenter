from typing import List, Dict
from backend.app.ai_engines.route_optimizer import haversine_distance, calculate_eta

def recommend_hospitals(
    patient_lat: float,
    patient_lon: float,
    emergency_type: str,
    priority: str,
    hospitals: List[Dict]
) -> List[Dict]:
    """
    Multi-criteria AI recommendation system for matching patients to the most suitable hospital.
    
    Criteria considered:
    1. Distance & ETA from emergency location
    2. ICU Bed availability
    3. Ventilator availability (critical for severe respiratory or cardiac cases)
    4. Required specialist availability (Cardiologist, Neurologist, Trauma Surgeon)
    """
    scored_hospitals = []

    # Identify specialist requirement based on emergency type
    specialist_key = None
    if "Heart Attack" in emergency_type or "Cardiac" in emergency_type:
        specialist_key = "has_cardiologist"
    elif "Stroke" in emergency_type or "Neurological" in emergency_type:
        specialist_key = "has_neurologist"
    elif "Accident" in emergency_type or "Trauma" in emergency_type:
        specialist_key = "has_trauma_surgeon"

    for h in hospitals:
        # Distance & ETA
        dist_km = haversine_distance(patient_lat, patient_lon, h["latitude"], h["longitude"])
        eta_min = calculate_eta(dist_km, average_speed_kmh=45.0, traffic_factor=1.15)

        # 1. Proximity Score (0 to 40 pts)
        proximity_score = max(0, 40 - (dist_km * 2.5))

        # 2. ICU Bed Score (0 to 30 pts)
        icu_beds = h.get("icu_beds_available", 0)
        icu_score = min(30, icu_beds * 10)

        # 3. Ventilator Score (0 to 15 pts)
        vents = h.get("ventilators_available", 0)
        vent_score = min(15, vents * 7.5)

        # 4. Specialist Presence (0 or 15 pts)
        specialist_available = True
        specialist_score = 15
        if specialist_key:
            specialist_available = h.get(specialist_key, False)
            specialist_score = 15 if specialist_available else 0

        # Total Suitability Score (0 to 100)
        total_score = proximity_score + icu_score + vent_score + specialist_score

        # Penalty if no ICU beds available for critical patients
        if icu_beds == 0 and priority == "CRITICAL":
            total_score *= 0.3

        # Construct Explainable AI (XAI) rationale text
        reasons = []
        if specialist_key and specialist_available:
            spec_name = specialist_key.replace("has_", "").title()
            reasons.append(f"{spec_name} available on site")
        elif specialist_key and not specialist_available:
            spec_name = specialist_key.replace("has_", "").title()
            reasons.append(f"No {spec_name} currently available")

        if icu_beds > 0:
            reasons.append(f"{icu_beds} ICU beds open")
        else:
            reasons.append("NO ICU beds available")

        if vents > 0:
            reasons.append(f"{vents} ventilators ready")

        reasons.append(f"Est. Travel Time: {eta_min} mins ({round(dist_km, 1)} km)")

        rationale = " | ".join(reasons)

        scored_hospitals.append({
            "hospital_id": h["id"],
            "hospital_name": h["name"],
            "distance_km": round(dist_km, 2),
            "eta_minutes": eta_min,
            "icu_beds_available": icu_beds,
            "ventilators_available": vents,
            "specialist_available": specialist_available,
            "suitability_score": round(total_score, 1),
            "recommendation_reason": rationale
        })

    # Sort descending by suitability score
    scored_hospitals.sort(key=lambda x: x["suitability_score"], reverse=True)
    return scored_hospitals
