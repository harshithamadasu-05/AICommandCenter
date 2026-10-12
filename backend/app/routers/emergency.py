from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.app.db.database import get_db
from backend.app.db.models import EmergencyCase, Ambulance, Hospital
from backend.app.schemas.schemas import EmergencyCreate, EmergencyOut, EmergencyUpdate
from backend.app.ai_engines.priority_classifier import classifier_instance

router = APIRouter(prefix="/api/emergencies", tags=["Emergencies"])

@router.post("/", response_model=EmergencyOut)
def create_emergency(data: EmergencyCreate, db: Session = Depends(get_db)):
    """
    Intake new emergency case, run AI priority classification model, and log case.
    """
    ai_result = classifier_instance.classify_emergency(
        age=data.patient_age,
        emergency_type=data.emergency_type,
        chest_pain=data.chest_pain,
        shortness_of_breath=data.shortness_of_breath,
        loss_of_consciousness=data.loss_of_consciousness,
        severe_bleeding=data.severe_bleeding,
        heart_rate=data.heart_rate or 80,
        systolic_bp=data.systolic_bp or 120
    )

    severity = data.accident_severity
    if not severity or severity == "Critical":
        if ai_result["priority"] == "CRITICAL" or ai_result["priority_score"] >= 80:
            severity = "Critical"
        elif ai_result["priority"] in ["HIGH", "MODERATE"] or ai_result["priority_score"] >= 50:
            severity = "Mild"
        else:
            severity = "Minor"

    emergency = EmergencyCase(
        patient_name=data.patient_name,
        patient_age=data.patient_age,
        emergency_type=data.emergency_type,
        priority=ai_result["priority"],
        priority_score=ai_result["priority_score"],
        accident_severity=severity,
        location_lat=data.location_lat,
        location_lon=data.location_lon,
        address=data.address,
        status="REPORTED",
        notes=data.notes
    )

    db.add(emergency)
    db.commit()
    db.refresh(emergency)
    return emergency

@router.get("/", response_model=List[EmergencyOut])
def list_emergencies(status: str = None, db: Session = Depends(get_db)):
    query = db.query(EmergencyCase)
    if status:
        query = query.filter(EmergencyCase.status == status)
    return query.order_by(EmergencyCase.created_at.desc()).all()

@router.get("/{emergency_id}", response_model=EmergencyOut)
def get_emergency(emergency_id: int, db: Session = Depends(get_db)):
    emg = db.query(EmergencyCase).filter(EmergencyCase.id == emergency_id).first()
    if not emg:
        raise HTTPException(status_code=404, detail="Emergency case not found")
    return emg

@router.patch("/{emergency_id}/status", response_model=EmergencyOut)
def update_emergency_status(emergency_id: int, status: str, db: Session = Depends(get_db)):
    emg = db.query(EmergencyCase).filter(EmergencyCase.id == emergency_id).first()
    if not emg:
        raise HTTPException(status_code=404, detail="Emergency case not found")
    emg.status = status.upper()
    if emg.status in ["ARRIVED", "RESOLVED"] and emg.assigned_ambulance:
        emg.assigned_ambulance.status = "AVAILABLE"
    db.commit()
    db.refresh(emg)
    return emg

@router.put("/{emergency_id}", response_model=EmergencyOut)
def update_emergency_details(emergency_id: int, data: EmergencyUpdate, db: Session = Depends(get_db)):
    emg = db.query(EmergencyCase).filter(EmergencyCase.id == emergency_id).first()
    if not emg:
        raise HTTPException(status_code=404, detail="Emergency case not found")
    
    if data.patient_name is not None:
        emg.patient_name = data.patient_name
    if data.patient_age is not None:
        emg.patient_age = data.patient_age
    if data.emergency_type is not None:
        emg.emergency_type = data.emergency_type
    if data.priority is not None:
        emg.priority = data.priority
    if data.accident_severity is not None:
        emg.accident_severity = data.accident_severity
    if data.priority_score is not None:
        emg.priority_score = data.priority_score
    if data.address is not None:
        emg.address = data.address
    if data.notes is not None:
        emg.notes = data.notes
    if data.recommended_hospital_id is not None:
        emg.recommended_hospital_id = data.recommended_hospital_id
    if data.assigned_ambulance_id is not None:
        emg.assigned_ambulance_id = data.assigned_ambulance_id
    if data.status is not None:
        emg.status = data.status.upper()
        if emg.status in ["ARRIVED", "RESOLVED"] and emg.assigned_ambulance:
            emg.assigned_ambulance.status = "AVAILABLE"
            
    db.commit()
    db.refresh(emg)
    return emg
