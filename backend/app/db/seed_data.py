from sqlalchemy.orm import Session
from backend.app.db.models import Hospital, Ambulance, EmergencyCase, PatientVital
from backend.app.db.database import SessionLocal, engine, Base
import random

def seed_database(db: Session = None):
    Base.metadata.create_all(bind=engine)
    
    close_session = False
    if db is None:
        db = SessionLocal()
        close_session = True

    try:
        # Check if already seeded with cases
        if db.query(EmergencyCase).count() >= 4:
            print("Database already contains multiple emergency cases. Skipping seed.")
            return

        print("Seeding database with default Hospitals, Ambulances, and 4 Emergency Cases...")

        # 1. Clear & Seed Hospitals
        db.query(PatientVital).delete()
        db.query(EmergencyCase).delete()
        db.query(Ambulance).delete()
        db.query(Hospital).delete()
        db.commit()

        hospitals_data = [
            {
                "name": "Apollo Emergency Healthcare Centre",
                "latitude": 17.4375,
                "longitude": 78.4482,
                "icu_beds_total": 12,
                "icu_beds_available": 4,
                "ventilators_available": 3,
                "has_cardiologist": True,
                "has_neurologist": True,
                "has_trauma_surgeon": True,
                "contact_number": "+1-800-APOLLO-EMG",
                "status": "OPERATIONAL"
            },
            {
                "name": "City General Trauma Hospital",
                "latitude": 17.4126,
                "longitude": 78.4501,
                "icu_beds_total": 15,
                "icu_beds_available": 1,
                "ventilators_available": 1,
                "has_cardiologist": False,
                "has_neurologist": True,
                "has_trauma_surgeon": True,
                "contact_number": "+1-800-CITY-GEN",
                "status": "OPERATIONAL"
            },
            {
                "name": "Sunshine Super Specialty Hospital",
                "latitude": 17.4510,
                "longitude": 78.4980,
                "icu_beds_total": 10,
                "icu_beds_available": 5,
                "ventilators_available": 4,
                "has_cardiologist": True,
                "has_neurologist": True,
                "has_trauma_surgeon": False,
                "contact_number": "+1-800-SUNSHINE",
                "status": "OPERATIONAL"
            },
            {
                "name": "KIMS Emergency & Heart Institute",
                "latitude": 17.4250,
                "longitude": 78.4820,
                "icu_beds_total": 20,
                "icu_beds_available": 6,
                "ventilators_available": 5,
                "has_cardiologist": True,
                "has_neurologist": False,
                "has_trauma_surgeon": True,
                "contact_number": "+1-800-KIMS-HEART",
                "status": "OPERATIONAL"
            }
        ]

        for h in hospitals_data:
            db.add(Hospital(**h))

        # 2. Seed Ambulances
        ambulances_data = [
            {"call_sign": "AMB-101 (ALS Cardiac Unit)", "latitude": 17.4420, "longitude": 78.4410, "status": "DISPATCHED", "driver_name": "Unit Alpha (Paramedic)", "contact": "+1-555-0101"},
            {"call_sign": "AMB-102 (Stroke Mobile Unit)", "latitude": 17.4180, "longitude": 78.4550, "status": "DISPATCHED", "driver_name": "Unit Bravo (Critical Care)", "contact": "+1-555-0102"},
            {"call_sign": "AMB-103 (Trauma Express Unit)", "latitude": 17.4580, "longitude": 78.4900, "status": "DISPATCHED", "driver_name": "Unit Charlie (Heart Care)", "contact": "+1-555-0103"},
            {"call_sign": "AMB-104 (Respiratory Rescue)", "latitude": 17.4300, "longitude": 78.4750, "status": "AVAILABLE", "driver_name": "Unit Delta (Trauma)", "contact": "+1-555-0104"}
        ]

        for a in ambulances_data:
            db.add(Ambulance(**a))

        db.commit()

        # 3. Seed 4 Emergency Cases
        c1 = EmergencyCase(
            patient_name="Ravi Kumar",
            patient_age=48,
            emergency_type="Heart Attack",
            priority="CRITICAL",
            priority_score=95.0,
            location_lat=17.4400,
            location_lon=78.4450,
            address="IT Corridor Expressway, Highway Km 14",
            status="DISPATCHED",
            notes="Patient collapsed with acute retrosternal chest pain and sweating.",
            assigned_ambulance_id=1,
            recommended_hospital_id=1
        )
        
        c2 = EmergencyCase(
            patient_name="Priya Sharma",
            patient_age=62,
            emergency_type="Stroke",
            priority="CRITICAL",
            priority_score=92.0,
            location_lat=17.4200,
            location_lon=78.4520,
            address="Jubilee Hills Road No. 36",
            status="DISPATCHED",
            notes="Sudden right-sided arm/leg weakness, facial drooping, and speech difficulty.",
            assigned_ambulance_id=2,
            recommended_hospital_id=1
        )

        c3 = EmergencyCase(
            patient_name="Vikram Singh",
            patient_age=34,
            emergency_type="Road Accident",
            priority="CRITICAL",
            priority_score=96.0,
            location_lat=17.4520,
            location_lon=78.4920,
            address="Outer Ring Road Interchange, Exit 4",
            status="DISPATCHED",
            notes="High-speed motorcycle collision. Multiple trauma lacerations, BP dropping.",
            assigned_ambulance_id=3,
            recommended_hospital_id=4
        )

        c4 = EmergencyCase(
            patient_name="Ananya Roy",
            patient_age=29,
            emergency_type="Severe Respiratory Distress",
            priority="HIGH",
            priority_score=84.0,
            location_lat=17.4310,
            location_lon=78.4700,
            address="Cyber Towers Metro Concourse",
            status="REPORTED",
            notes="Severe status asthmaticus attack. Shortness of breath, wheezing, SpO2 88%.",
            assigned_ambulance_id=4,
            recommended_hospital_id=3
        )

        db.add_all([c1, c2, c3, c4])
        db.commit()

        # Seed Initial Telemetry Vitals for Each Case
        v1 = PatientVital(emergency_id=c1.id, heart_rate=128, spo2=92, systolic_bp=165, diastolic_bp=98, temperature=37.1, ecg_status="ST_ELEVATION")
        v2 = PatientVital(emergency_id=c2.id, heart_rate=98, spo2=94, systolic_bp=185, diastolic_bp=110, temperature=36.8, ecg_status="NORMAL")
        v3 = PatientVital(emergency_id=c3.id, heart_rate=142, spo2=89, systolic_bp=88, diastolic_bp=56, temperature=36.4, ecg_status="CRITICAL_ALERT")
        v4 = PatientVital(emergency_id=c4.id, heart_rate=115, spo2=88, systolic_bp=132, diastolic_bp=84, temperature=37.2, ecg_status="NORMAL")

        db.add_all([v1, v2, v3, v4])
        db.commit()

        print("Database successfully seeded with 4 active emergency cases!")

    finally:
        if close_session:
            db.close()

if __name__ == "__main__":
    seed_database()
