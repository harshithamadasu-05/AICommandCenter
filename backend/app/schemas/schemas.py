from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# --- Hospital Schemas ---
class HospitalBase(BaseModel):
    name: str
    latitude: float
    longitude: float
    icu_beds_total: int
    icu_beds_available: int
    ventilators_available: int
    has_cardiologist: bool
    has_neurologist: bool
    has_trauma_surgeon: bool
    contact_number: str
    status: str = "OPERATIONAL"

class HospitalCreate(HospitalBase):
    pass

class HospitalOut(HospitalBase):
    id: int

    class Config:
        from_attributes = True

# --- Ambulance Schemas ---
class AmbulanceBase(BaseModel):
    call_sign: str
    latitude: float
    longitude: float
    status: str = "AVAILABLE"
    driver_name: str
    contact: str

class AmbulanceOut(AmbulanceBase):
    id: int

    class Config:
        from_attributes = True

# --- Emergency Schemas ---
class EmergencyCreate(BaseModel):
    patient_name: str
    patient_age: int
    emergency_type: str
    location_lat: float
    location_lon: float
    address: str = "GPS Location"
    chest_pain: bool = False
    shortness_of_breath: bool = False
    loss_of_consciousness: bool = False
    severe_bleeding: bool = False
    systolic_bp: Optional[int] = 120
    heart_rate: Optional[int] = 80
    accident_severity: Optional[str] = "Critical"
    notes: Optional[str] = None

class EmergencyUpdate(BaseModel):
    patient_name: Optional[str] = None
    patient_age: Optional[int] = None
    emergency_type: Optional[str] = None
    priority: Optional[str] = None
    accident_severity: Optional[str] = None
    priority_score: Optional[float] = None
    address: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None
    recommended_hospital_id: Optional[int] = None
    assigned_ambulance_id: Optional[int] = None

class EmergencyOut(BaseModel):
    id: int
    patient_name: str
    patient_age: int
    emergency_type: str
    priority: str
    priority_score: float
    accident_severity: Optional[str] = "Critical"
    location_lat: float
    location_lon: float
    address: str
    status: str
    created_at: datetime
    notes: Optional[str] = None
    assigned_ambulance_id: Optional[int] = None
    recommended_hospital_id: Optional[int] = None
    assigned_ambulance_call_sign: Optional[str] = None
    recommended_hospital_name: Optional[str] = None

    class Config:
        from_attributes = True

# --- Recommendation Schemas ---
class HospitalRecommendation(BaseModel):
    hospital_id: int
    hospital_name: str
    distance_km: float
    eta_minutes: float
    icu_beds_available: int
    ventilators_available: int
    specialist_available: bool
    suitability_score: float
    recommendation_reason: str

# --- Vitals Schemas ---
class PatientVitalCreate(BaseModel):
    emergency_id: int
    heart_rate: int
    spo2: int
    systolic_bp: int
    diastolic_bp: int
    temperature: float = 37.0
    ecg_status: str = "NORMAL"

class PatientVitalOut(PatientVitalCreate):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True
