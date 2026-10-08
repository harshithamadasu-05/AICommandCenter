from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.app.db.database import get_db
from backend.app.db.models import Hospital
from backend.app.schemas.schemas import HospitalOut, HospitalCreate

router = APIRouter(prefix="/api/hospitals", tags=["Hospitals"])

@router.get("/", response_model=List[HospitalOut])
def get_hospitals(db: Session = Depends(get_db)):
    return db.query(Hospital).all()

@router.put("/{hospital_id}/resources", response_model=HospitalOut)
def update_resources(
    hospital_id: int, 
    icu_beds_available: int, 
    ventilators_available: int,
    has_cardiologist: bool = True,
    has_neurologist: bool = True,
    has_trauma_surgeon: bool = True,
    db: Session = Depends(get_db)
):
    h = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    if not h:
        raise HTTPException(status_code=404, detail="Hospital not found")

    h.icu_beds_available = max(0, icu_beds_available)
    h.ventilators_available = max(0, ventilators_available)
    h.has_cardiologist = has_cardiologist
    h.has_neurologist = has_neurologist
    h.has_trauma_surgeon = has_trauma_surgeon

    db.commit()
    db.refresh(h)
    return h
