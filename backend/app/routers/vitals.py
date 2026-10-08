from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.app.db.database import get_db
from backend.app.db.models import PatientVital, EmergencyCase
from backend.app.schemas.schemas import PatientVitalOut, PatientVitalCreate
from backend.app.iot.vitals_stream import generate_live_vital

router = APIRouter(prefix="/api/vitals", tags=["IoT Vitals Telemetry"])

@router.post("/", response_model=PatientVitalOut)
def record_vital(data: PatientVitalCreate, db: Session = Depends(get_db)):
    vital = PatientVital(
        emergency_id=data.emergency_id,
        heart_rate=data.heart_rate,
        spo2=data.spo2,
        systolic_bp=data.systolic_bp,
        diastolic_bp=data.diastolic_bp,
        temperature=data.temperature,
        ecg_status=data.ecg_status
    )
    db.add(vital)
    db.commit()
    db.refresh(vital)
    return vital

@router.get("/emergency/{emergency_id}", response_model=List[PatientVitalOut])
def get_vitals_history(emergency_id: int, db: Session = Depends(get_db)):
    return db.query(PatientVital).filter(PatientVital.emergency_id == emergency_id).order_by(PatientVital.timestamp.asc()).all()

@router.post("/simulate_next/{emergency_id}", response_model=PatientVitalOut)
def simulate_next_vital(emergency_id: int, db: Session = Depends(get_db)):
    emg = db.query(EmergencyCase).filter(EmergencyCase.id == emergency_id).first()
    if not emg:
        raise HTTPException(status_code=404, detail="Emergency case not found")

    last_vital_record = db.query(PatientVital).filter(PatientVital.emergency_id == emergency_id).order_by(PatientVital.timestamp.desc()).first()
    prev_dict = None
    if last_vital_record:
        prev_dict = {
            "heart_rate": last_vital_record.heart_rate,
            "spo2": last_vital_record.spo2,
            "systolic_bp": last_vital_record.systolic_bp,
            "diastolic_bp": last_vital_record.diastolic_bp
        }

    simulated = generate_live_vital(emg.emergency_type, prev_dict)

    vital = PatientVital(
        emergency_id=emergency_id,
        heart_rate=simulated["heart_rate"],
        spo2=simulated["spo2"],
        systolic_bp=simulated["systolic_bp"],
        diastolic_bp=simulated["diastolic_bp"],
        temperature=simulated["temperature"],
        ecg_status=simulated["ecg_status"]
    )
    db.add(vital)
    db.commit()
    db.refresh(vital)
    return vital
