from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.app.db.database import Base

class Hospital(Base):
    __tablename__ = "hospitals"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    icu_beds_total = Column(Integer, default=10)
    icu_beds_available = Column(Integer, default=3)
    ventilators_available = Column(Integer, default=2)
    has_cardiologist = Column(Boolean, default=True)
    has_neurologist = Column(Boolean, default=True)
    has_trauma_surgeon = Column(Boolean, default=True)
    contact_number = Column(String, default="+1-800-EMERGENCY")
    status = Column(String, default="OPERATIONAL")

    emergencies = relationship("EmergencyCase", back_populates="recommended_hospital")

class Ambulance(Base):
    __tablename__ = "ambulances"

    id = Column(Integer, primary_key=True, index=True)
    call_sign = Column(String, unique=True, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    status = Column(String, default="AVAILABLE")  # AVAILABLE, DISPATCHED, IN_TRANSIT, BUSY
    driver_name = Column(String, default="Paramedic Unit")
    contact = Column(String, default="+1-555-0199")

    emergencies = relationship("EmergencyCase", back_populates="assigned_ambulance")

class EmergencyCase(Base):
    __tablename__ = "emergencies"

    id = Column(Integer, primary_key=True, index=True)
    patient_name = Column(String, nullable=False)
    patient_age = Column(Integer, nullable=False)
    emergency_type = Column(String, nullable=False)  # Heart Attack, Stroke, Road Accident, Trauma, Respiratory
    priority = Column(String, default="HIGH")        # CRITICAL, HIGH, MODERATE, LOW
    priority_score = Column(Float, default=85.0)     # 0-100 score from AI classifier
    location_lat = Column(Float, nullable=False)
    location_lon = Column(Float, nullable=False)
    address = Column(String, default="In Transit / GPS Location")
    status = Column(String, default="REPORTED")      # REPORTED, DISPATCHED, IN_TRANSIT, ARRIVED, RESOLVED
    created_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text, nullable=True)

    assigned_ambulance_id = Column(Integer, ForeignKey("ambulances.id"), nullable=True)
    recommended_hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=True)

    assigned_ambulance = relationship("Ambulance", back_populates="emergencies")
    recommended_hospital = relationship("Hospital", back_populates="emergencies")
    vitals = relationship("PatientVital", back_populates="emergency", cascade="all, delete-orphan")

class PatientVital(Base):
    __tablename__ = "patient_vitals"

    id = Column(Integer, primary_key=True, index=True)
    emergency_id = Column(Integer, ForeignKey("emergencies.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    heart_rate = Column(Integer, nullable=False)      # bpm
    spo2 = Column(Integer, nullable=False)            # % oxygen saturation
    systolic_bp = Column(Integer, nullable=False)     # mmHg
    diastolic_bp = Column(Integer, nullable=False)    # mmHg
    temperature = Column(Float, default=37.0)         # Celsius
    ecg_status = Column(String, default="NORMAL")     # NORMAL, ST_ELEVATION, ARRHYTHMIA, CRITICAL

    emergency = relationship("EmergencyCase", back_populates="vitals")
