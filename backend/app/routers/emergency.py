from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.app.db.database import get_db
from backend.app.db.models import EmergencyCase, Ambulance, Hospital
from backend.app.schemas.schemas import EmergencyCreate, EmergencyOut
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

    emergency = EmergencyCase(
        patient_name=data.patient_name,
        patient_age=data.patient_age,
        emergency_type=data.emergency_type,
        priority=ai_result["priority"],
        priority_score=ai_result["priority_score"],
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
