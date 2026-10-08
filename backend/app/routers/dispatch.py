from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict

from backend.app.db.database import get_db
from backend.app.db.models import EmergencyCase, Ambulance, Hospital
from backend.app.schemas.schemas import HospitalRecommendation, EmergencyOut
from backend.app.ai_engines.hospital_recommender import recommend_hospitals
from backend.app.ai_engines.route_optimizer import find_nearest_ambulance, haversine_distance, calculate_eta

router = APIRouter(prefix="/api/dispatch", tags=["Dispatch & Routing"])

@router.get("/recommend_hospital/{emergency_id}", response_model=List[HospitalRecommendation])
def get_hospital_recommendations(emergency_id: int, db: Session = Depends(get_db)):
    emg = db.query(EmergencyCase).filter(EmergencyCase.id == emergency_id).first()
    if not emg:
        raise HTTPException(status_code=404, detail="Emergency case not found")

    hospitals = db.query(Hospital).all()
    hospital_dicts = [
        {
            "id": h.id,
            "name": h.name,
            "latitude": h.latitude,
            "longitude": h.longitude,
            "icu_beds_available": h.icu_beds_available,
            "ventilators_available": h.ventilators_available,
            "has_cardiologist": h.has_cardiologist,
            "has_neurologist": h.has_neurologist,
            "has_trauma_surgeon": h.has_trauma_surgeon,
            "status": h.status
        }
        for h in hospitals
    ]

    recommendations = recommend_hospitals(
        patient_lat=emg.location_lat,
        patient_lon=emg.location_lon,
        emergency_type=emg.emergency_type,
        priority=emg.priority,
        hospitals=hospital_dicts
    )

    return recommendations

@router.post("/auto_dispatch/{emergency_id}")
def auto_dispatch(emergency_id: int, hospital_id: int = None, db: Session = Depends(get_db)):
    emg = db.query(EmergencyCase).filter(EmergencyCase.id == emergency_id).first()
    if not emg:
        raise HTTPException(status_code=404, detail="Emergency case not found")

    # 1. Find Nearest Ambulance
    ambulances = db.query(Ambulance).all()
    amb_dicts = [
        {
            "id": a.id,
            "call_sign": a.call_sign,
            "latitude": a.latitude,
            "longitude": a.longitude,
            "status": a.status
        }
        for a in ambulances
    ]

    nearest_res = find_nearest_ambulance(emg.location_lat, emg.location_lon, amb_dicts)
    if not nearest_res or not nearest_res["ambulance"]:
        raise HTTPException(status_code=400, detail="No ambulances available in system")

    selected_amb_id = nearest_res["ambulance"]["id"]
    assigned_ambulance = db.query(Ambulance).filter(Ambulance.id == selected_amb_id).first()

    # 2. Select Hospital (User specified or AI Top Recommendation)
    if not hospital_id:
        recs = get_hospital_recommendations(emergency_id, db)
        if recs:
            hospital_id = recs[0].hospital_id

    assigned_hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first() if hospital_id else None

    # Update Emergency Record
    emg.assigned_ambulance_id = assigned_ambulance.id
    emg.recommended_hospital_id = assigned_hospital.id if assigned_hospital else None
    emg.status = "DISPATCHED"

    # Update Ambulance Record
    assigned_ambulance.status = "DISPATCHED"

    db.commit()
    db.refresh(emg)

    # Route & ETA metrics
    h_dist = haversine_distance(emg.location_lat, emg.location_lon, assigned_hospital.latitude, assigned_hospital.longitude) if assigned_hospital else 0
    h_eta = calculate_eta(h_dist)

    return {
        "message": "Ambulance dispatched successfully",
        "emergency_id": emg.id,
        "dispatched_ambulance": assigned_ambulance.call_sign,
        "ambulance_eta_minutes": nearest_res["eta_minutes"],
        "assigned_hospital": assigned_hospital.name if assigned_hospital else "Unassigned",
        "hospital_eta_minutes": h_eta,
        "hospital_icu_beds": assigned_hospital.icu_beds_available if assigned_hospital else 0
    }
