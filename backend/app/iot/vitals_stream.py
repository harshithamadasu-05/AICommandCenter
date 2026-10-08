import random
from datetime import datetime

def generate_live_vital(emergency_type: str, previous_vital: dict = None) -> dict:
    """
    Simulates real-time IoT patient sensor telemetry during ambulance transport.
    """
    if previous_vital:
        # Slight realistic drift from previous reading
        hr = max(40, min(190, previous_vital["heart_rate"] + random.randint(-4, 4)))
        spo2 = max(70, min(100, previous_vital["spo2"] + random.randint(-1, 1)))
        sys_bp = max(60, min(210, previous_vital["systolic_bp"] + random.randint(-5, 5)))
        dia_bp = max(40, min(130, previous_vital["diastolic_bp"] + random.randint(-3, 3)))
    else:
        # Initial baseline according to emergency type
        if "Heart Attack" in emergency_type:
            hr = random.randint(110, 145)
            spo2 = random.randint(90, 95)
            sys_bp = random.randint(145, 175)
            dia_bp = random.randint(90, 110)
        elif "Stroke" in emergency_type:
            hr = random.randint(85, 115)
            spo2 = random.randint(92, 97)
            sys_bp = random.randint(160, 195)
            dia_bp = random.randint(95, 115)
        elif "Trauma" in emergency_type or "Accident" in emergency_type:
            hr = random.randint(120, 155)
            spo2 = random.randint(88, 94)
            sys_bp = random.randint(85, 110) # Hypovolemic shock risk
            dia_bp = random.randint(55, 70)
        else:
            hr = random.randint(70, 95)
            spo2 = random.randint(95, 99)
            sys_bp = random.randint(115, 135)
            dia_bp = random.randint(75, 88)

    # Determine ECG Status & Alert Level
    ecg_status = "NORMAL"
    if "Heart Attack" in emergency_type or hr > 130:
        ecg_status = "ST_ELEVATION" if random.random() > 0.4 else "ARRHYTHMIA"
    elif spo2 < 88 or sys_bp < 85:
        ecg_status = "CRITICAL_ALERT"

    return {
        "timestamp": datetime.utcnow().strftime("%H:%M:%S"),
        "heart_rate": hr,
        "spo2": spo2,
        "systolic_bp": sys_bp,
        "diastolic_bp": dia_bp,
        "temperature": round(random.uniform(36.5, 37.8), 1),
        "ecg_status": ecg_status
    }
