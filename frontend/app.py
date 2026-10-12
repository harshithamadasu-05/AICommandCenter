import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import pydeck as pdk
import time
import os
import base64
from datetime import datetime

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000/api")

st.set_page_config(
    page_title="AI Emergency Healthcare Command Centre",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

LOGO_PATH = os.path.join(os.path.dirname(__file__), "logo.png")

def get_logo_base64():
    if os.path.exists(LOGO_PATH):
        with open(LOGO_PATH, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    return ""

logo_b64 = get_logo_base64()

# Clean Cream Boxes & High-Contrast Typography
st.markdown("""
    <style>
    /* Global App Background */
    .stApp, [data-testid="stAppViewContainer"] {
        background-color: #F0F9FF !important;
        color: #0F172A !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    }

    /* Sidebar Background */
    [data-testid="stSidebar"] {
        background-color: #E0F2FE !important;
        border-right: 2px solid #0284C7 !important;
    }
    [data-testid="stSidebar"] * {
        color: #0F172A !important;
    }

    /* Headings & Text */
    h1, h2, h3, h4, h5, h6, p, span, label, div {
        color: #0F172A !important;
    }

    /* Input Containers & Typer Bars */
    div[data-baseweb="select"] > div, 
    div[data-baseweb="input"] > div,
    input, textarea, select {
        background-color: #FAF6EE !important;
        border: 1px solid #E2E8F0 !important;
        outline: none !important;
        box-shadow: none !important;
        border-radius: 8px !important;
        color: #0F172A !important;
        font-weight: 600 !important;
    }
    
    input:focus, textarea:focus, div[data-baseweb="select"] > div:focus-within {
        border: 1px solid #CBD5E1 !important;
        outline: none !important;
        box-shadow: none !important;
    }

    /* Keep Streamlit buttons readable if the deployed theme falls back to defaults. */
    [data-testid="stButton"] button,
    [data-testid="stFormSubmitButton"] button {
        background: #FFFFFF !important;
        border: 1px solid #0284C7 !important;
        color: #0F172A !important;
    }
    [data-testid="stButton"] button *,
    [data-testid="stFormSubmitButton"] button * {
        color: inherit !important;
    }
    [data-testid="stButton"] button[kind="primary"],
    [data-testid="stButton"] button[data-testid="baseButton-primary"],
    [data-testid="stFormSubmitButton"] button[kind="primary"],
    [data-testid="stFormSubmitButton"] button[data-testid="baseButton-primary"] {
        background: #0284C7 !important;
        border-color: #0284C7 !important;
        color: #FFFFFF !important;
    }

    div[data-baseweb="popover"], ul[role="listbox"] {
        background-color: #FAF6EE !important;
        border: 1px solid #CBD5E1 !important;
        box-shadow: 0 4px 12px rgba(2, 132, 199, 0.12) !important;
    }
    li[role="option"] {
        color: #0F172A !important;
        background-color: #FAF6EE !important;
    }

    /* Clean Expander Container */
    div[data-testid="stExpander"] {
        background-color: #FAF6EE !important;
        border: 2px solid #0284C7 !important;
        border-radius: 10px !important;
        overflow: hidden !important;
        margin-bottom: 12px !important;
        box-shadow: none !important;
    }
    div[data-testid="stExpander"] > details {
        border: none !important;
        background-color: transparent !important;
        box-shadow: none !important;
    }
    div[data-testid="stExpander"] summary {
        border: none !important;
        background-color: #FAF6EE !important;
        color: #0F172A !important;
        font-weight: 700 !important;
        padding: 10px 14px !important;
        box-shadow: none !important;
    }

    /* Read-Only Hospital Resource Card */
    .hospital-live-card {
        background-color: #FAF6EE !important;
        border: 2px solid #0284C7 !important;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 4px 12px rgba(2, 132, 199, 0.06);
    }
    .hospital-title {
        font-size: 1.35rem;
        font-weight: 800;
        color: #0F172A !important;
        margin: 0;
    }
    .hosp-metric-box {
        background-color: #FFFFFF;
        border: 1.5px solid #BAE6FD;
        border-radius: 8px;
        padding: 12px 16px;
        text-align: center;
    }
    .hosp-metric-val {
        font-size: 1.6rem;
        font-weight: 800;
        color: #0284C7;
    }
    .hosp-metric-lbl {
        font-size: 0.85rem;
        font-weight: 700;
        color: #475569;
    }

    /* Patient Banner */
    .patient-banner {
        background: #FFFFFF;
        border: 2px solid #0284C7;
        border-radius: 14px;
        padding: 18px 24px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(2, 132, 199, 0.06);
    }
    .patient-name {
        font-size: 1.5rem;
        font-weight: 800;
        color: #0F172A !important;
        margin: 0;
    }

    /* RPM Cards */
    .rpm-card-bp {
        background-color: #FFFDF0 !important;
        border: 2px solid #F59E0B !important;
        border-radius: 12px;
        padding: 16px;
    }
    .rpm-card-hr {
        background-color: #F0F4FF !important;
        border: 2px solid #3B82F6 !important;
        border-radius: 12px;
        padding: 16px;
    }
    .rpm-card-spo2 {
        background-color: #E6FFFA !important;
        border: 2px solid #10B981 !important;
        border-radius: 12px;
        padding: 16px;
    }
    .rpm-card-temp {
        background-color: #FFF5F5 !important;
        border: 2px solid #EC4899 !important;
        border-radius: 12px;
        padding: 16px;
    }

    /* Priority Badges */
    .badge-critical {
        background-color: #FEE2E2 !important;
        color: #991B1B !important;
        padding: 5px 14px;
        border-radius: 6px;
        font-weight: 800;
        font-size: 0.85rem;
        border: 1.5px solid #EF4444;
        display: inline-block;
    }
    .badge-high {
        background-color: #FEF3C7 !important;
        color: #92400E !important;
        padding: 5px 14px;
        border-radius: 6px;
        font-weight: 800;
        font-size: 0.85rem;
        border: 1.5px solid #F59E0B;
        display: inline-block;
    }
    .badge-moderate {
        background-color: #DBEAFE !important;
        color: #1E40AF !important;
        padding: 5px 14px;
        border-radius: 6px;
        font-weight: 800;
        font-size: 0.85rem;
        border: 1.5px solid #3B82F6;
        display: inline-block;
    }
    .badge-low {
        background-color: #D1FAE5 !important;
        color: #065F46 !important;
        padding: 5px 14px;
        border-radius: 6px;
        font-weight: 800;
        font-size: 0.85rem;
        border: 1.5px solid #10B981;
        display: inline-block;
    }
    .badge-severity-critical {
        background-color: #FEE2E2 !important;
        color: #991B1B !important;
        padding: 4px 12px;
        border-radius: 6px;
        font-weight: 800;
        font-size: 0.82rem;
        border: 1.5px solid #EF4444;
        display: inline-block;
    }
    .badge-severity-mild {
        background-color: #FEF3C7 !important;
        color: #92400E !important;
        padding: 4px 12px;
        border-radius: 6px;
        font-weight: 800;
        font-size: 0.82rem;
        border: 1.5px solid #F59E0B;
        display: inline-block;
    }
    .badge-severity-minor {
        background-color: #D1FAE5 !important;
        color: #065F46 !important;
        padding: 4px 12px;
        border-radius: 6px;
        font-weight: 800;
        font-size: 0.82rem;
        border: 1.5px solid #10B981;
        display: inline-block;
    }
    .badge-status-dispatched {
        background-color: #E0F2FE !important;
        color: #0369A1 !important;
        padding: 4px 12px;
        border-radius: 6px;
        font-weight: 800;
        font-size: 0.8rem;
        border: 1.5px solid #0284C7;
        display: inline-block;
    }
    .badge-status-intransit {
        background-color: #FEF3C7 !important;
        color: #B45309 !important;
        padding: 4px 12px;
        border-radius: 6px;
        font-weight: 800;
        font-size: 0.8rem;
        border: 1.5px solid #F59E0B;
        display: inline-block;
    }
    .badge-status-arrived {
        background-color: #EDE9FE !important;
        color: #5B21B6 !important;
        padding: 4px 12px;
        border-radius: 6px;
        font-weight: 800;
        font-size: 0.8rem;
        border: 1.5px solid #8B5CF6;
        display: inline-block;
    }
    .badge-status-resolved {
        background-color: #D1FAE5 !important;
        color: #065F46 !important;
        padding: 4px 12px;
        border-radius: 6px;
        font-weight: 800;
        font-size: 0.8rem;
        border: 1.5px solid #10B981;
        display: inline-block;
    }
    .badge-status-reported {
        background-color: #FEE2E2 !important;
        color: #B91C1C !important;
        padding: 4px 12px;
        border-radius: 6px;
        font-weight: 800;
        font-size: 0.8rem;
        border: 1.5px solid #EF4444;
        display: inline-block;
    }
    .history-card {
        background-color: #FAF6EE !important;
        border: 2px solid #0284C7 !important;
        border-radius: 12px;
        padding: 18px 22px;
        margin-bottom: 16px;
        box-shadow: 0 4px 12px rgba(2, 132, 199, 0.06);
    }
    .history-card:hover {
        box-shadow: 0 6px 16px rgba(2, 132, 199, 0.12);
    }

    /* Navigation Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background-color: #E0F2FE !important;
        padding: 6px;
        border-radius: 10px;
        border: 2px solid #0284C7;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #FFFFFF !important;
        border: 1px solid #0284C7 !important;
        border-radius: 8px !important;
        box-shadow: none !important;
        color: #0F172A !important;
        font-weight: 600 !important;
        padding: 8px 20px;
    }
    .stTabs [data-baseweb="tab"]:focus {
        outline: 2px solid #0284C7 !important;
        outline-offset: 2px !important;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #FAF6EE !important;
        color: #0284C7 !important;
        font-weight: 800 !important;
        border: 2px solid #0284C7 !important;
    }

    /* PyDeck Map Tooltip - Crisp White Box */
    .deck-tooltip, [data-deck-tooltip], div.deck-tooltip {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        border: 2px solid #0284C7 !important;
        border-radius: 8px !important;
        padding: 8px 14px !important;
        font-size: 0.85rem !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 14px rgba(2, 132, 199, 0.18) !important;
        z-index: 99999 !important;
    }
    .deck-tooltip * {
        color: #0F172A !important;
    }
    </style>
""", unsafe_allow_html=True)

# Main Header Banner (Title updated to "AI-Powered Emergency Healthcare Command Centre")
if logo_b64:
    st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 16px; background: linear-gradient(135deg, #FAF6EE 0%, #E0F2FE 100%); padding: 14px 22px; border-radius: 12px; border: 2px solid #0284C7; margin-bottom: 20px;">
            <img src="data:image/png;base64,{logo_b64}" style="width: 70px; height: 70px; border-radius: 50%; border: 3px solid #0284C7; object-fit: cover; flex-shrink: 0; box-shadow: 0 2px 8px rgba(2,132,199,0.15);">
            <div>
                <div style="font-size: 1.75rem; font-weight: 800; color: #1E3A8A !important;">🏥 AI-Powered Emergency Healthcare Command Centre</div>
                <div style="font-size: 0.95rem; color: #0284C7 !important; font-weight: 600;">AI Priority Triage • Smart Dispatch • IoT Multi-Param Patient Telemetry</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <div style="background: linear-gradient(135deg, #FAF6EE 0%, #E0F2FE 100%); padding: 14px 22px; border-radius: 12px; border: 2px solid #0284C7; margin-bottom: 20px;">
            <div style="font-size: 1.75rem; font-weight: 800; color: #1E3A8A !important;">🏥 AI-Powered Emergency Healthcare Command Centre</div>
            <div style="font-size: 0.95rem; color: #0284C7 !important; font-weight: 600;">AI Priority Triage • Smart Dispatch • IoT Multi-Param Patient Telemetry</div>
        </div>
    """, unsafe_allow_html=True)

# Helper API functions
@st.cache_data(ttl=2)
def fetch_emergencies():
    try:
        r = requests.get(f"{API_BASE_URL}/emergencies/")
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return []

@st.cache_data(ttl=2)
def fetch_hospitals():
    try:
        r = requests.get(f"{API_BASE_URL}/hospitals/")
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return []

def fetch_recommendations(emergency_id):
    try:
        r = requests.get(f"{API_BASE_URL}/dispatch/recommend_hospital/{emergency_id}")
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return []

def fetch_vitals_history(emergency_id):
    try:
        r = requests.get(f"{API_BASE_URL}/vitals/emergency/{emergency_id}")
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return []

@st.cache_data(ttl=2)
def fetch_ambulances():
    try:
        r = requests.get(f"{API_BASE_URL}/dispatch/ambulances")
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return []

def update_case_status(emergency_id, new_status):
    try:
        r = requests.patch(f"{API_BASE_URL}/emergencies/{emergency_id}/status", params={"status": new_status})
        return r.status_code == 200
    except Exception:
        return False

def format_timestamp(ts):
    if not ts:
        return "N/A"
    try:
        if isinstance(ts, str):
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        else:
            dt = ts
        return dt.strftime("%b %d, %Y • %H:%M")
    except Exception:
        return str(ts)[:16]

def get_status_badge(status):
    st_upper = str(status).upper()
    if "DISPATCH" in st_upper:
        return f'<span class="badge-status-dispatched">🚑 DISPATCHED</span>'
    elif "TRANSIT" in st_upper:
        return f'<span class="badge-status-intransit">⏱️ IN TRANSIT</span>'
    elif "ARRIVE" in st_upper:
        return f'<span class="badge-status-arrived">🏥 ARRIVED</span>'
    elif "RESOLV" in st_upper:
        return f'<span class="badge-status-resolved">✅ RESOLVED</span>'
    else:
        return f'<span class="badge-status-reported">⚠️ REPORTED</span>'

def get_priority_badge(priority):
    p = str(priority).upper()
    if p == "CRITICAL":
        return f'<span class="badge-critical">CRITICAL</span>'
    elif p == "HIGH":
        return f'<span class="badge-high">HIGH</span>'
    elif p == "MODERATE":
        return f'<span class="badge-moderate">MODERATE</span>'
    else:
        return f'<span class="badge-low">{p}</span>'

def get_accident_severity(case):
    sev = case.get("accident_severity")
    if sev in ["Critical", "Mild", "Minor"]:
        return sev
    p = str(case.get("priority", "")).upper()
    score = float(case.get("priority_score", 0))
    if p == "CRITICAL" or score >= 80:
        return "Critical"
    elif p in ["HIGH", "MODERATE"] or score >= 50:
        return "Mild"
    else:
        return "Minor"

def get_accident_severity_badge(severity):
    s = str(severity).capitalize()
    if s == "Critical":
        return '<span class="badge-severity-critical">🔴 CRITICAL</span>'
    elif s == "Mild":
        return '<span class="badge-severity-mild">🟡 MILD</span>'
    else:
        return '<span class="badge-severity-minor">🟢 MINOR</span>'

def get_incident_emoji(case):
    etype = str(case.get("emergency_type", "")).lower()
    if "accident" in etype or "crash" in etype or "collision" in etype:
        return "🚗"
    elif "trauma" in etype or "injury" in etype:
        return "🩹"
    elif "heart" in etype or "cardiac" in etype or "infarction" in etype:
        return "🫀"
    elif "stroke" in etype or "brain" in etype or "neuro" in etype:
        return "🧠"
    elif "respiratory" in etype or "asthma" in etype or "lung" in etype:
        return "🫁"
    elif "burn" in etype:
        return "🔥"
    return "🚨"

def render_incident_card_html(case, h_name, amb_call, v_hist=None):
    sev = get_accident_severity(case)

    # Visual theme per severity level
    if sev == "Critical":
        border_color = "#EF4444"
        card_gradient = "linear-gradient(180deg, #FFFFFF 0%, #FFF5F5 100%)"
        accent_bar = "linear-gradient(90deg, #DC2626 0%, #EF4444 50%, #F87171 100%)"
        sev_badge = '<span style="background: #FEE2E2; color: #991B1B; padding: 4px 12px; border-radius: 9999px; font-weight: 800; font-size: 0.8rem; border: 1.5px solid #EF4444; display: inline-flex; align-items: center; gap: 4px;">🚨 CRITICAL ACCIDENT</span>'
    elif sev == "Mild":
        border_color = "#F59E0B"
        card_gradient = "linear-gradient(180deg, #FFFFFF 0%, #FFFDF5 100%)"
        accent_bar = "linear-gradient(90deg, #D97706 0%, #F59E0B 50%, #FBBF24 100%)"
        sev_badge = '<span style="background: #FEF3C7; color: #92400E; padding: 4px 12px; border-radius: 9999px; font-weight: 800; font-size: 0.8rem; border: 1.5px solid #F59E0B; display: inline-flex; align-items: center; gap: 4px;">⚠️ MILD ACCIDENT</span>'
    else:
        border_color = "#10B981"
        card_gradient = "linear-gradient(180deg, #FFFFFF 0%, #F4FDF8 100%)"
        accent_bar = "linear-gradient(90deg, #059669 0%, #10B981 50%, #34D399 100%)"
        sev_badge = '<span style="background: #D1FAE5; color: #065F46; padding: 4px 12px; border-radius: 9999px; font-weight: 800; font-size: 0.8rem; border: 1.5px solid #10B981; display: inline-flex; align-items: center; gap: 4px;">🩹 MINOR ACCIDENT</span>'

    # Transit status pill
    status = str(case.get("status", "REPORTED")).upper()
    if "DISPATCH" in status:
        s_badge = '<span style="background: #E0F2FE; color: #0369A1; padding: 4px 12px; border-radius: 9999px; font-weight: 800; font-size: 0.8rem; border: 1.5px solid #0284C7;">🚑 DISPATCHED</span>'
    elif "TRANSIT" in status:
        s_badge = '<span style="background: #FEF3C7; color: #B45309; padding: 4px 12px; border-radius: 9999px; font-weight: 800; font-size: 0.8rem; border: 1.5px solid #F59E0B;">⏱️ IN TRANSIT</span>'
    elif "ARRIVE" in status:
        s_badge = '<span style="background: #EDE9FE; color: #5B21B6; padding: 4px 12px; border-radius: 9999px; font-weight: 800; font-size: 0.8rem; border: 1.5px solid #8B5CF6;">🏥 ARRIVED</span>'
    elif "RESOLV" in status:
        s_badge = '<span style="background: #D1FAE5; color: #065F46; padding: 4px 12px; border-radius: 9999px; font-weight: 800; font-size: 0.8rem; border: 1.5px solid #10B981;">✅ RESOLVED</span>'
    else:
        s_badge = '<span style="background: #FEE2E2; color: #B91C1C; padding: 4px 12px; border-radius: 9999px; font-weight: 800; font-size: 0.8rem; border: 1.5px solid #EF4444;">⚠️ REPORTED</span>'

    emoji_icon = get_incident_emoji(case)
    patient_name = case.get("patient_name", "Unknown")
    patient_age = case.get("patient_age", "N/A")
    case_id = case.get("id", 0)
    p_score = float(case.get("priority_score", 0))
    p_level = case.get("priority", "HIGH")
    etype = case.get("emergency_type", "Emergency")
    address = case.get("address", "Location Pending")
    notes = case.get("notes") or "Standard emergency protocol active. Real-time fleet and hospital telemetry linked."
    lat = float(case.get("location_lat", 0))
    lon = float(case.get("location_lon", 0))
    created_at_fmt = format_timestamp(case.get("created_at"))

    # Hospital & Ambulance confirmation tags
    h_confirmed = h_name and "pending" not in h_name.lower() and "unassigned" not in h_name.lower()
    h_pill = '<span style="margin-top: 10px; display: inline-flex; align-items: center; gap: 4px; font-size: 0.76rem; font-weight: 700; color: #065F46; background: #D1FAE5; padding: 2px 8px; border-radius: 6px; width: fit-content;">✅ Beds & Facility Allotted</span>' if h_confirmed else '<span style="margin-top: 10px; display: inline-flex; align-items: center; gap: 4px; font-size: 0.76rem; font-weight: 700; color: #92400E; background: #FEF3C7; padding: 2px 8px; border-radius: 6px; width: fit-content;">⏳ Allotment Pending</span>'

    amb_confirmed = amb_call and "pending" not in amb_call.lower() and "unassigned" not in amb_call.lower()
    amb_pill = '<span style="margin-top: 10px; display: inline-flex; align-items: center; gap: 4px; font-size: 0.76rem; font-weight: 700; color: #1E40AF; background: #DBEAFE; padding: 2px 8px; border-radius: 6px; width: fit-content;">📡 Live Fleet Unit</span>' if amb_confirmed else '<span style="margin-top: 10px; display: inline-flex; align-items: center; gap: 4px; font-size: 0.76rem; font-weight: 700; color: #991B1B; background: #FEE2E2; padding: 2px 8px; border-radius: 6px; width: fit-content;">⚠️ Fleet Unassigned</span>'

    # Telemetry or Informational strip
    if sev == "Critical":
        latest_v = v_hist[-1] if v_hist else None
        hr = f"{latest_v['heart_rate']} bpm" if latest_v else "128 bpm"
        bp = f"{latest_v['systolic_bp']}/{latest_v['diastolic_bp']} mmHg" if latest_v else "165/98 mmHg"
        spo2 = f"{latest_v['spo2']}%" if latest_v else "92%"
        ecg = latest_v['ecg_status'] if latest_v else "ST_ELEVATION"

        strip_html = (
            f'<div style="background: linear-gradient(135deg, #FEF2F2 0%, #FEE2E2 100%); border: 1.5px solid #F87171; border-radius: 10px; padding: 10px 14px; margin: 12px 0; display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 8px;">'
            f'<div style="display: flex; align-items: center; gap: 6px;">'
            f'<span style="font-size: 1.1rem;">🚨</span>'
            f'<span style="font-weight: 800; color: #991B1B; font-size: 0.85rem;">CRITICAL TRAUMA TELEMETRY ACTIVE</span>'
            f'<span style="color: #DC2626; font-size: 0.78rem; font-weight: 600;">— Immediate ICU & Resuscitation Bay Reserved</span>'
            f'</div>'
            f'<div style="display: flex; flex-wrap: wrap; gap: 10px; font-size: 0.82rem; font-weight: 800;">'
            f'<span style="background: #FFFFFF; border: 1px solid #FCA5A5; color: #B91C1C; padding: 3px 8px; border-radius: 6px;">❤️ HR: {hr}</span>'
            f'<span style="background: #FFFFFF; border: 1px solid #FCA5A5; color: #B91C1C; padding: 3px 8px; border-radius: 6px;">🩸 BP: {bp}</span>'
            f'<span style="background: #FFFFFF; border: 1px solid #FCA5A5; color: #B91C1C; padding: 3px 8px; border-radius: 6px;">🫁 SpO2: {spo2}</span>'
            f'<span style="background: #FFFFFF; border: 1px solid #FCA5A5; color: #B91C1C; padding: 3px 8px; border-radius: 6px;">⚡ ECG: {ecg}</span>'
            f'</div>'
            f'</div>'
        )
    elif sev == "Mild":
        strip_html = (
            f'<div style="background: linear-gradient(135deg, #FFFBEB 0%, #FEF3C7 100%); border: 1.5px solid #FCD34D; border-radius: 10px; padding: 9px 14px; margin: 12px 0; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">'
            f'<div style="display: flex; align-items: center; gap: 6px;">'
            f'<span style="font-size: 1.05rem;">ℹ️</span>'
            f'<span style="font-weight: 800; color: #92400E; font-size: 0.85rem;">MILD ACCIDENT PROTOCOL</span>'
            f'<span style="color: #B45309; font-size: 0.8rem; font-weight: 600;">— Patient conscious & hemodynamically stable</span>'
            f'</div>'
            f'<span style="background: #FDE68A; color: #78350F; font-size: 0.76rem; font-weight: 800; padding: 3px 8px; border-radius: 6px;">🟡 NON-ICU ROUTING</span>'
            f'</div>'
        )
    else:
        strip_html = (
            f'<div style="background: linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%); border: 1.5px solid #86EFAC; border-radius: 10px; padding: 9px 14px; margin: 12px 0; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">'
            f'<div style="display: flex; align-items: center; gap: 6px;">'
            f'<span style="font-size: 1.05rem;">🩹</span>'
            f'<span style="font-weight: 800; color: #166534; font-size: 0.85rem;">MINOR ACCIDENT PROTOCOL</span>'
            f'<span style="color: #15803D; font-size: 0.8rem; font-weight: 600;">— Superficial trauma / ambulatory outpatient</span>'
            f'</div>'
            f'<span style="background: #BBF7D0; color: #14532D; font-size: 0.76rem; font-weight: 800; padding: 3px 8px; border-radius: 6px;">🟢 OUTPATIENT</span>'
            f'</div>'
        )

    # 4 Bento Capsules
    capsules_html = (
        f'<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 12px; margin-bottom: 12px;">'
        f'<div style="background: #FFFFFF; border: 1.5px solid #BAE6FD; border-radius: 10px; padding: 12px 14px; display: flex; flex-direction: column; justify-content: space-between; box-shadow: 0 1px 3px rgba(0,0,0,0.02);">'
        f'<div>'
        f'<div style="display: flex; align-items: center; justify-content: space-between;">'
        f'<span style="font-size: 0.72rem; font-weight: 800; color: #0284C7; text-transform: uppercase; letter-spacing: 0.5px;">🏷️ Emergency Type</span>'
        f'<span style="font-size: 0.95rem;">🩺</span>'
        f'</div>'
        f'<div style="font-size: 0.98rem; font-weight: 800; color: #0F172A; margin-top: 4px; line-height: 1.3;">{etype}</div>'
        f'</div>'
        f'<div style="margin-top: 10px; display: inline-flex; align-items: center; gap: 4px; font-size: 0.76rem; font-weight: 700; color: #0369A1; background: #E0F2FE; padding: 2px 8px; border-radius: 6px; width: fit-content;">'
        f'⚡ Priority: {p_level}'
        f'</div>'
        f'</div>'
        f'<div style="background: #FFFFFF; border: 1.5px solid #BAE6FD; border-radius: 10px; padding: 12px 14px; display: flex; flex-direction: column; justify-content: space-between; box-shadow: 0 1px 3px rgba(0,0,0,0.02);">'
        f'<div>'
        f'<div style="display: flex; align-items: center; justify-content: space-between;">'
        f'<span style="font-size: 0.72rem; font-weight: 800; color: #0284C7; text-transform: uppercase; letter-spacing: 0.5px;">🏥 Allotted Hospital</span>'
        f'<span style="font-size: 0.95rem;">🎯</span>'
        f'</div>'
        f'<div style="font-size: 0.98rem; font-weight: 800; color: #0F172A; margin-top: 4px; line-height: 1.3;">{h_name}</div>'
        f'</div>'
        f'{h_pill}'
        f'</div>'
        f'<div style="background: #FFFFFF; border: 1.5px solid #BAE6FD; border-radius: 10px; padding: 12px 14px; display: flex; flex-direction: column; justify-content: space-between; box-shadow: 0 1px 3px rgba(0,0,0,0.02);">'
        f'<div>'
        f'<div style="display: flex; align-items: center; justify-content: space-between;">'
        f'<span style="font-size: 0.72rem; font-weight: 800; color: #0284C7; text-transform: uppercase; letter-spacing: 0.5px;">🚑 Dispatched Unit</span>'
        f'<span style="font-size: 0.95rem;">🚨</span>'
        f'</div>'
        f'<div style="font-size: 0.98rem; font-weight: 800; color: #0F172A; margin-top: 4px; line-height: 1.3;">{amb_call}</div>'
        f'</div>'
        f'{amb_pill}'
        f'</div>'
        f'<div style="background: #FFFFFF; border: 1.5px solid #BAE6FD; border-radius: 10px; padding: 12px 14px; display: flex; flex-direction: column; justify-content: space-between; box-shadow: 0 1px 3px rgba(0,0,0,0.02);">'
        f'<div>'
        f'<div style="display: flex; align-items: center; justify-content: space-between;">'
        f'<span style="font-size: 0.72rem; font-weight: 800; color: #0284C7; text-transform: uppercase; letter-spacing: 0.5px;">📍 Incident Location</span>'
        f'<span style="font-size: 0.95rem;">🌐</span>'
        f'</div>'
        f'<div style="font-size: 0.98rem; font-weight: 800; color: #0F172A; margin-top: 4px; line-height: 1.3;">{address}</div>'
        f'</div>'
        f'<div style="margin-top: 10px; display: inline-flex; align-items: center; gap: 4px; font-size: 0.76rem; font-weight: 700; color: #475569; background: #F1F5F9; padding: 2px 8px; border-radius: 6px; width: fit-content;">'
        f'📍 {lat:.4f}, {lon:.4f}'
        f'</div>'
        f'</div>'
        f'</div>'
    )

    # Dispatcher Log Box
    log_html = (
        f'<div style="background: #FFFFFF; border: 1px solid #BAE6FD; border-left: 4px solid #0284C7; border-radius: 8px; padding: 10px 14px; margin-top: 12px; display: flex; align-items: flex-start; gap: 10px;">'
        f'<span style="font-size: 1.1rem; line-height: 1.2;">📋</span>'
        f'<div style="font-size: 0.86rem; line-height: 1.4;">'
        f'<b style="color: #0F172A;">Dispatcher & Field Log:</b>'
        f'<span style="color: #334155; margin-left: 6px;">"{notes}"</span>'
        f'</div>'
        f'</div>'
    )

    # Full Card Wrapper
    card_html = (
        f'<div style="background: {card_gradient}; border: 2px solid {border_color}; border-radius: 14px; padding: 18px 20px; margin-bottom: 16px; box-shadow: 0 4px 16px rgba(2, 132, 199, 0.08); position: relative; overflow: hidden;">'
        f'<div style="position: absolute; top: 0; left: 0; right: 0; height: 5px; background: {accent_bar};"></div>'
        f'<div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 12px; margin-top: 4px; margin-bottom: 10px;">'
        f'<div style="display: flex; align-items: center; gap: 12px;">'
        f'<div style="width: 46px; height: 46px; border-radius: 12px; background: #E0F2FE; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; border: 2px solid #0284C7; flex-shrink: 0; box-shadow: 0 2px 6px rgba(2,132,199,0.15);">'
        f'{emoji_icon}'
        f'</div>'
        f'<div>'
        f'<div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">'
        f'<span style="background: #FFFFFF; color: #0284C7 !important; border: 1.5px solid #0284C7; font-size: 0.75rem; font-weight: 800; padding: 2px 8px; border-radius: 6px; letter-spacing: 0.5px; box-shadow: 0 1px 3px rgba(2,132,199,0.08);">🆔 CASE #{case_id}</span>'
        f'<span style="font-size: 1.25rem; font-weight: 800; color: #0F172A;">👤 {patient_name}</span>'
        f'<span style="background: #E2E8F0; color: #334155; font-size: 0.78rem; font-weight: 700; padding: 2px 7px; border-radius: 6px;">🎂 {patient_age} YRS</span>'
        f'</div>'
        f'<div style="font-size: 0.82rem; color: #64748B; font-weight: 600; margin-top: 3px;">🕒 Incident Logged: {created_at_fmt}</div>'
        f'</div>'
        f'</div>'
        f'<div style="display: flex; gap: 8px; align-items: center; flex-wrap: wrap;">'
        f'{sev_badge}'
        f'<span style="background: #EFF6FF; color: #1D4ED8; padding: 4px 10px; border-radius: 9999px; font-weight: 800; font-size: 0.8rem; border: 1.5px solid #3B82F6;">⚡ AI SCORE: {p_score:.1f}/100</span>'
        f'{s_badge}'
        f'</div>'
        f'</div>'
        f'{strip_html}'
        f'{capsules_html}'
        f'{log_html}'
        f'</div>'
    )

    return card_html

def update_patient_details(emergency_id, payload):
    try:
        r = requests.put(f"{API_BASE_URL}/emergencies/{emergency_id}", json=payload)
        return r.status_code == 200
    except Exception:
        return False

def record_patient_vital(emergency_id, hr, spo2, sbp, dbp, temp, ecg):
    try:
        payload = {
            "emergency_id": int(emergency_id),
            "heart_rate": int(hr),
            "spo2": int(spo2),
            "systolic_bp": int(sbp),
            "diastolic_bp": int(dbp),
            "temperature": float(temp),
            "ecg_status": str(ecg)
        }
        r = requests.post(f"{API_BASE_URL}/vitals/", json=payload)
        return r.status_code == 200
    except Exception:
        return False

# Sidebar Header - Circular Badge Format matching Image 2
if logo_b64:
    st.sidebar.markdown(f"""
        <div style="display: flex; align-items: center; gap: 12px; padding: 4px 0; margin-bottom: 8px;">
            <img src="data:image/png;base64,{logo_b64}" style="width: 52px; height: 52px; border-radius: 50%; border: 2.5px solid #0284C7; object-fit: cover; flex-shrink: 0; box-shadow: 0 2px 6px rgba(2,132,199,0.15);">
            <div>
                <h3 style="color: #0F172A !important; margin: 0; font-weight: 800; font-size: 1.25rem;">AI Command Centre</h3>
                <span style="background-color: #D1FAE5; color: #065F46 !important; padding: 2px 8px; border-radius: 6px; font-weight: 700; font-size: 0.75rem; display: inline-block; margin-top: 4px; border: 1px solid #10B981;">● SYSTEM ONLINE</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
else:
    st.sidebar.markdown("""
        <div style="padding: 2px 0;">
            <h3 style="color: #0F172A !important; margin: 0; font-weight: 800; font-size: 1.35rem;">AI Command Centre</h3>
            <span style="background-color: #D1FAE5; color: #065F46 !important; padding: 4px 10px; border-radius: 6px; font-weight: 700; font-size: 0.85rem; display: inline-block; margin-top: 6px; border: 1px solid #10B981;">● SYSTEM ONLINE</span>
        </div>
    """, unsafe_allow_html=True)

st.sidebar.divider()

emergencies = fetch_emergencies()
hospitals = fetch_hospitals()

active_cases = [e for e in emergencies if e.get("status") in ["REPORTED", "DISPATCHED", "IN_TRANSIT"]]
case_options = {f"Case #{e['id']}: {e['patient_name']} ({e['emergency_type']}) - Priority: {e['priority']}": e for e in active_cases}
total_icu = sum(h.get("icu_beds_available", 0) for h in hospitals)
total_vents = sum(h.get("ventilators_available", 0) for h in hospitals)

st.sidebar.metric("Active Emergencies", len(active_cases))
st.sidebar.metric("Available ICU Beds", total_icu)
st.sidebar.metric("Available Ventilators", total_vents)

st.sidebar.divider()
st.sidebar.markdown("""
    <div style="color: #0F172A !important; font-weight: 600;">
        <b>Target Operational Impact</b><br>
        • Response Time Reduction: <b>20-30%</b><br>
        • Golden Hour Delay Reduction: <b>30-40%</b>
    </div>
""", unsafe_allow_html=True)

# Navigation Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🚨 Live Command & GIS Map",
    "🩺 IoT Patient Telemetry",
    "📊 Resource Analytics & Hospital Board",
    "📝 Intake Emergency (AI Triage)",
    "📜 Incident & Allotment History"
])

# ==========================================
# TAB 1: Live Command Centre & GIS Map
# ==========================================
with tab1:
    ambulances = fetch_ambulances()
    amb_dict = {a["id"]: a for a in ambulances}
    hosp_dict = {h["id"]: h for h in hospitals}

    if active_cases:
        if "allotment_counter" not in st.session_state:
            st.session_state["allotment_counter"] = 0

        active_case_ids = [e["id"] for e in active_cases]

        if "selected_case_id" not in st.session_state or st.session_state["selected_case_id"] not in active_case_ids:
            pending_cases = [e for e in active_cases if not e.get("recommended_hospital_id") or e.get("status") == "REPORTED" or "pending" in str(e.get("recommended_hospital_name", "")).lower()]
            if pending_cases:
                st.session_state["selected_case_id"] = pending_cases[0]["id"]
            else:
                st.session_state["selected_case_id"] = active_cases[0]["id"]

        selected_case = next((e for e in active_cases if e["id"] == st.session_state["selected_case_id"]), active_cases[0])

    col_left, col_right = st.columns([1.3, 1])

    with col_left:
        st.markdown("### 🗺️ Real-Time Street Map Navigation & Vehicle Fleet Routes")
        
        map_data = []
        # 1. Hospital Markers
        for h in hospitals:
            map_data.append({
                "name": f"🏥 Hospital: {h['name']} ({h['icu_beds_available']} ICU Beds, {h['ventilators_available']} Vents)",
                "lat": h["latitude"],
                "lon": h["longitude"],
                "color": [2, 132, 199, 230] if h["icu_beds_available"] > 0 else [220, 38, 38, 230],
                "size": 190
            })
        
        # 2. Live Ambulances (Vehicle Fleet Markers)
        for a in ambulances:
            is_active_amb = a.get("status") in ["DISPATCHED", "IN_TRANSIT"]
            amb_color = [245, 158, 11, 255] if is_active_amb else [16, 185, 129, 240]
            map_data.append({
                "name": f"🚑 Vehicle: {a['call_sign']} | Status: {a['status']} | Paramedic: {a['driver_name']} | Lat: {a['latitude']:.4f}, Lon: {a['longitude']:.4f}",
                "lat": a["latitude"],
                "lon": a["longitude"],
                "color": amb_color,
                "size": 220
            })

        # 3. Patient Incident Markers (Classified: Critical, Mild, Minor)
        for e in active_cases:
            sev = get_accident_severity(e)
            if sev == "Critical":
                inc_color = [239, 68, 68, 255] # Red
            elif sev == "Mild":
                inc_color = [245, 158, 11, 255] # Amber
            else:
                inc_color = [16, 185, 129, 255] # Emerald Green

            map_data.append({
                "name": f"🚨 Patient Incident: {e['patient_name']} ({e['emergency_type']}) | Severity: {sev.upper()} ACCIDENT | Score: {e['priority_score']}/100",
                "lat": e["location_lat"],
                "lon": e["location_lon"],
                "color": inc_color,
                "size": 270
            })

        df_map = pd.DataFrame(map_data)

        # 4. Real-time Vehicle Fleet Routes (Ambulance ➔ Patient ➔ Hospital)
        routes_data = []
        for e in active_cases:
            amb_id = e.get("assigned_ambulance_id")
            hosp_id = e.get("recommended_hospital_id")
            amb = amb_dict.get(amb_id)
            hosp = hosp_dict.get(hosp_id)

            if amb:
                # Dispatch Route from Vehicle to Incident Location
                routes_data.append({
                    "name": f"🚑 Dispatch Route: {amb['call_sign']} ➔ {e['patient_name']} ({e['emergency_type']})",
                    "path": [
                        [amb["longitude"], amb["latitude"]],
                        [(amb["longitude"] * 0.55 + e["location_lon"] * 0.45) + 0.0015, (amb["latitude"] * 0.55 + e["location_lat"] * 0.45) - 0.001],
                        [e["location_lon"], e["location_lat"]]
                    ],
                    "color": [245, 158, 11, 240], # Amber
                    "width": 5
                })

            if hosp:
                # Emergency Transit Route from Incident to Hospital
                routes_data.append({
                    "name": f"🏥 Hospital Route: {e['patient_name']} ➔ {hosp['name']}",
                    "path": [
                        [e["location_lon"], e["location_lat"]],
                        [(e["location_lon"] * 0.45 + hosp["longitude"] * 0.55) - 0.0015, (e["location_lat"] * 0.45 + hosp["latitude"] * 0.55) + 0.001],
                        [hosp["longitude"], hosp["latitude"]]
                    ],
                    "color": [2, 132, 199, 240], # Blue
                    "width": 6
                })

        deck_layers = []

        if routes_data:
            df_routes = pd.DataFrame(routes_data)
            route_layer = pdk.Layer(
                "PathLayer",
                df_routes,
                get_path="path",
                get_color="color",
                get_width="width",
                width_min_pixels=3,
                pickable=True
            )
            deck_layers.append(route_layer)

        if not df_map.empty:
            marker_layer = pdk.Layer(
                "ScatterplotLayer",
                df_map,
                get_position=["lon", "lat"],
                get_color="color",
                get_radius="size",
                pickable=True
            )
            deck_layers.append(marker_layer)

            view_state = pdk.ViewState(
                latitude=df_map["lat"].mean(),
                longitude=df_map["lon"].mean(),
                zoom=12.7,
                pitch=20
            )

            map_tooltip = {
                "html": "<div style='background-color: #FFFFFF; color: #0F172A; font-weight: 700; font-size: 12px; padding: 6px 10px; border-radius: 6px; border: 1.5px solid #0284C7; box-shadow: 0 4px 12px rgba(2,132,199,0.15);'>{name}</div>",
                "style": {
                    "backgroundColor": "#FFFFFF",
                    "color": "#0F172A",
                    "border": "1.5px solid #0284C7",
                    "borderRadius": "6px",
                    "padding": "0px",
                    "zIndex": "1000"
                }
            }

            st.pydeck_chart(pdk.Deck(
                layers=deck_layers,
                initial_view_state=view_state,
                map_style="https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json",
                tooltip=map_tooltip
            ))

            # Visual Map Legend
            st.markdown("""
                <div style="background-color: #FAF6EE; border: 1.5px solid #BAE6FD; border-radius: 8px; padding: 10px 14px; margin-top: 6px; display: flex; flex-wrap: wrap; gap: 14px; font-size: 0.8rem; font-weight: 700; color: #0F172A;">
                    <span>🔴 Critical Accident / Incident</span>
                    <span>🟡 Mild Accident</span>
                    <span>🟢 Minor Accident</span>
                    <span>🚑 Live Ambulance</span>
                    <span>🏥 Receiving Hospital</span>
                    <span><b style="color: #F59E0B;">━━</b> Vehicle Dispatch Route</span>
                    <span><b style="color: #0284C7;">━━</b> Hospital Route</span>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.info("No active emergency markers to display on map.")

        # ========================================================
        # 🧠 AI Hospital Recommendations (Directly Below Map)
        # ========================================================
        if active_cases:
            st.markdown("<hr style='margin: 14px 0 10px 0; border: none; border-top: 1.5px solid #BAE6FD;' />", unsafe_allow_html=True)
            st.markdown("### 🧠 AI Hospital Recommendations")
            recs = fetch_recommendations(selected_case['id'])

            if recs:
                top_rec = recs[0]
                st.markdown(f"""
                    <div style="background-color:#FAF6EE; border: 2px solid #0284C7; padding: 14px 16px; border-radius: 10px; margin-bottom: 12px; box-shadow: 0 2px 6px rgba(2,132,199,0.08);">
                        <div style="font-size: 1.05rem; font-weight: 800; color: #0F172A !important;">⭐ Primary AI Pick: {top_rec['hospital_name']}</div>
                        <div style="color: #0284C7 !important; font-size: 0.88rem; margin-top: 4px; font-weight: 700;">Suitability Score: {top_rec['suitability_score']}/100 | Distance: {top_rec['distance_km']} km (ETA: {top_rec['eta_minutes']} mins)</div>
                    </div>
                """, unsafe_allow_html=True)

                for idx, r in enumerate(recs[:3]):
                    with st.expander(f"Option #{idx+1}: {r['hospital_name']} ({r['distance_km']} km | {r['eta_minutes']} min ETA)", expanded=(idx==0)):
                        st.markdown(f"""
                        - **Available ICU Beds**: {r['icu_beds_available']}
                        - **Ventilators Ready**: {r['ventilators_available']}
                        - **Required Specialist**: {'Available' if r['specialist_available'] else 'Not Available'}
                        - **Rationale**: {r['recommendation_reason']}
                        """)
            else:
                st.info("No hospital recommendations available for this incident.")

    with col_right:
        st.markdown("### 📋 Active Incident & Patient Profile")
        
        if active_cases:
            selected_idx = 0
            if st.session_state["selected_case_id"] in active_case_ids:
                selected_idx = active_case_ids.index(st.session_state["selected_case_id"])

            def format_case_dropdown(e):
                sev = get_accident_severity(e)
                badge_icon = "🔴" if sev == "Critical" else "🟡" if sev == "Mild" else "🟢"
                h_name = e.get("recommended_hospital_name") or hosp_dict.get(e.get("recommended_hospital_id"), {}).get("name")
                is_allotted = e.get("recommended_hospital_id") and h_name and "pending" not in str(h_name).lower()
                status_tag = f"✅ ALLOTTED: {h_name[:20]}" if is_allotted else "⏳ PENDING ALLOTMENT"
                return f"{badge_icon} Case #{e['id']}: {e['patient_name']} ({e['emergency_type'][:20]}) • {status_tag}"

            chosen_case = st.selectbox(
                "Select Incident for Allotment / Review:",
                active_cases,
                index=selected_idx,
                format_func=format_case_dropdown,
                key=f"dispatch_case_selector_{st.session_state['allotment_counter']}"
            )
            # Sync session state if changed
            if chosen_case["id"] != st.session_state["selected_case_id"]:
                st.session_state["selected_case_id"] = chosen_case["id"]
                st.rerun()

            selected_sev = get_accident_severity(selected_case)
            sev_badge = get_accident_severity_badge(selected_sev)

            # Details of patient rendered with attractive modern emoji card
            h_name = selected_case.get("recommended_hospital_name")
            if not h_name or h_name == "Pending Hospital Allotment":
                h_name = hosp_dict.get(selected_case.get("recommended_hospital_id"), {}).get("name", "⚠️ Pending Allotment")

            amb_call = selected_case.get("assigned_ambulance_call_sign")
            if not amb_call or amb_call == "Pending Ambulance":
                amb_call = amb_dict.get(selected_case.get("assigned_ambulance_id"), {}).get("call_sign", "⚠️ Unassigned")

            v_hist = fetch_vitals_history(selected_case['id']) if selected_sev == "Critical" else None
            st.markdown(render_incident_card_html(selected_case, h_name, amb_call, v_hist=v_hist), unsafe_allow_html=True)

            # ========================================================
            # 🏥 Confirm Patient Allotment (Below Case Card, Beside Recommendations)
            # ========================================================
            st.markdown("<hr style='margin: 14px 0 10px 0; border: none; border-top: 1.5px solid #BAE6FD;' />", unsafe_allow_html=True)
            st.markdown("### 🏥 Confirm Patient Allotment")
            
            st.markdown("""
                <div style="background-color: #FAF6EE; border: 1.5px solid #BAE6FD; border-radius: 10px; padding: 12px 16px; margin-bottom: 10px;">
                    <div style="font-weight: 800; color: #0F172A; font-size: 0.92rem;">🤖 Fast AI Auto-Allotment</div>
                    <div style="color: #475569; font-size: 0.82rem; margin-top: 2px;">
                        Immediately assigns top AI recommended hospital, reserves ICU bed & dispatches ambulance.
                    </div>
                </div>
            """, unsafe_allow_html=True)

            if st.button("🤖 Confirm AI Auto-Allotment", type="primary", use_container_width=True):
                try:
                    recs_allot = fetch_recommendations(selected_case['id'])
                    top_hosp_id = recs_allot[0]['hospital_id'] if recs_allot else None
                    res = requests.post(
                        f"{API_BASE_URL}/dispatch/auto_dispatch/{selected_case['id']}",
                        params={"hospital_id": top_hosp_id}
                    ).json()
                    
                    # Invalidate caches immediately so History and Command Centre refresh with latest DB state
                    fetch_emergencies.clear()
                    fetch_hospitals.clear()
                    fetch_ambulances.clear()

                    # Determine the NEXT patient in the queue
                    curr_pos = next((i for i, c in enumerate(active_cases) if c["id"] == selected_case["id"]), 0)
                    other_pending = [c for c in active_cases if c["id"] != selected_case["id"] and (not c.get("recommended_hospital_id") or c.get("status") == "REPORTED" or "pending" in str(c.get("recommended_hospital_name", "")).lower())]
                    if other_pending:
                        next_case = other_pending[0]
                    else:
                        next_pos = (curr_pos + 1) % len(active_cases)
                        next_case = active_cases[next_pos]

                    st.session_state["selected_case_id"] = next_case["id"]
                    st.session_state["allotment_counter"] += 1

                    st.success(f"✅ **AI Allotment Confirmed!** Patient **{selected_case['patient_name']}** allocated to `{res['assigned_hospital']}`.")
                    st.info(f"🚑 Ambulance `{res['dispatched_ambulance']}` dispatched! ETA: **{res['ambulance_eta_minutes']} mins**.")
                    st.info(f"➡️ **Advancing to Next Patient**: **{next_case['patient_name']}** (Case #{next_case['id']}). Check Tab 5 for updated record.")
                    time.sleep(1.2)
                    st.rerun()
                except Exception as ex:
                    st.error(f"AI Allotment error: {ex}")

            st.markdown("""
                <div style="background-color: #FAF6EE; border: 1.5px solid #BAE6FD; border-radius: 10px; padding: 12px 16px; margin-top: 12px; margin-bottom: 10px;">
                    <div style="font-weight: 800; color: #0F172A; font-size: 0.92rem;">🖐️ Manual Facility Override</div>
                    <div style="color: #475569; font-size: 0.82rem; margin-top: 2px;">
                        Select a specific hospital facility to manually allocate this patient.
                    </div>
                </div>
            """, unsafe_allow_html=True)

            hosp_options = {f"{h['name']} ({h['icu_beds_available']} ICU Beds)": h for h in hospitals}
            selected_hosp_label = st.selectbox("Select Hospital for Manual Allotment:", list(hosp_options.keys()), key="man_tab1_select")
            man_hosp = hosp_options[selected_hosp_label]

            if st.button("🖐️ Confirm Manual Allotment", type="secondary", use_container_width=True):
                try:
                    res = requests.post(
                        f"{API_BASE_URL}/dispatch/auto_dispatch/{selected_case['id']}",
                        params={"hospital_id": man_hosp['id']}
                    ).json()
                    
                    fetch_emergencies.clear()
                    fetch_hospitals.clear()
                    fetch_ambulances.clear()

                    curr_pos = next((i for i, c in enumerate(active_cases) if c["id"] == selected_case["id"]), 0)
                    other_pending = [c for c in active_cases if c["id"] != selected_case["id"] and (not c.get("recommended_hospital_id") or c.get("status") == "REPORTED" or "pending" in str(c.get("recommended_hospital_name", "")).lower())]
                    if other_pending:
                        next_case = other_pending[0]
                    else:
                        next_pos = (curr_pos + 1) % len(active_cases)
                        next_case = active_cases[next_pos]

                    st.session_state["selected_case_id"] = next_case["id"]
                    st.session_state["allotment_counter"] += 1

                    st.success(f"✅ **Manual Allotment Confirmed!** Patient **{selected_case['patient_name']}** allocated to `{man_hosp['name']}`.")
                    st.info(f"🚑 Ambulance `{res['dispatched_ambulance']}` dispatched! ETA: **{res['ambulance_eta_minutes']} mins**.")
                    st.info(f"➡️ **Advancing to Next Patient**: **{next_case['patient_name']}** (Case #{next_case['id']}). Check Tab 5 for updated record.")
                    time.sleep(1.2)
                    st.rerun()
                except Exception as ex:
                    st.error(f"Manual Allotment error: {ex}")
        else:
            st.info("No active emergency cases currently requiring hospital allotment.")

# ==========================================
# TAB 2: IoT Patient Telemetry
# ==========================================
with tab2:
    if active_cases:
        case_options = {f"Case #{e['id']}: {e['patient_name']} ({e['emergency_type']}) - Priority: {e['priority']}": e for e in active_cases}
        keys_list = list(case_options.keys())
        default_vitals_idx = 0
        if "selected_case_id" in st.session_state:
            for idx, e in enumerate(active_cases):
                if e["id"] == st.session_state["selected_case_id"]:
                    default_vitals_idx = idx
                    break
        selected_label = st.selectbox("Select Patient Telemetry Stream:", keys_list, index=default_vitals_idx, key="vitals_select")
        selected_case = case_options[selected_label]

        st.markdown(f"""
            <div class="patient-banner">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                    <div>
                        <div class="patient-name">👤 {selected_case['patient_name']}</div>
                        <div class="patient-sub">ID: #{selected_case['id']} | Male | {selected_case['patient_age']} Years | 📍 {selected_case['address']}</div>
                    </div>
                    <div>
                        <span style="background-color: #E0F2FE; color: #0284C7; padding: 6px 14px; border-radius: 8px; font-weight: 700;">Condition: {selected_case['emergency_type']}</span>
                        <span style="background-color: #FAF6EE; color: #0F172A; padding: 6px 14px; border-radius: 8px; font-weight: 700; border: 1.5px solid #0284C7; margin-left: 8px;">Device: IoT Multi-Param Monitor</span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        col_left_ctrl, col_right_ctrl = st.columns([3, 1])
        with col_right_ctrl:
            if st.button("🔄 Stream Next Vital Reading", type="secondary"):
                try:
                    requests.post(f"{API_BASE_URL}/vitals/simulate_next/{selected_case['id']}")
                    st.rerun()
                except Exception as ex:
                    st.error(f"Error streaming vitals: {ex}")

        vitals_data = fetch_vitals_history(selected_case['id'])
        if vitals_data:
            latest = vitals_data[-1]

            c1, c2, c3, c4 = st.columns(4)

            with c1:
                st.markdown(f"""
                    <div class="rpm-card-bp">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div class="rpm-label">Blood Pressure</div>
                            <span style="font-size:1.4rem;">⚠️</span>
                        </div>
                        <div class="rpm-val" style="color: #D97706;">{latest['systolic_bp']}/{latest['diastolic_bp']} <span style="font-size:0.9rem; font-weight:600;">mmHg</span></div>
                        <div class="rpm-trend" style="color: #D97706;">↗ 5% higher than normal</div>
                    </div>
                """, unsafe_allow_html=True)

            with c2:
                st.markdown(f"""
                    <div class="rpm-card-hr">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div class="rpm-label">Heart Rate</div>
                            <span style="font-size:1.4rem;">💓</span>
                        </div>
                        <div class="rpm-val" style="color: #2563EB;">{latest['heart_rate']} <span style="font-size:0.9rem; font-weight:600;">bpm</span></div>
                        <div class="rpm-trend" style="color: #2563EB;">↗ Elevated Rate</div>
                    </div>
                """, unsafe_allow_html=True)

            with c3:
                st.markdown(f"""
                    <div class="rpm-card-spo2">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div class="rpm-label">Oxygen Saturation</div>
                            <span style="font-size:1.4rem;">🫁</span>
                        </div>
                        <div class="rpm-val" style="color: #059669;">{latest['spo2']} <span style="font-size:0.9rem; font-weight:600;">SpO2 %</span></div>
                        <div class="rpm-trend" style="color: #059669;">✓ Stable O2 Level</div>
                    </div>
                """, unsafe_allow_html=True)

            with c4:
                st.markdown(f"""
                    <div class="rpm-card-temp">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div class="rpm-label">Body Temperature</div>
                            <span style="font-size:1.4rem;">🌡️</span>
                        </div>
                        <div class="rpm-val" style="color: #DB2777;">{latest['temperature']} <span style="font-size:0.9rem; font-weight:600;">°C</span></div>
                        <div class="rpm-trend" style="color: #DB2777;">ECG: {latest['ecg_status']}</div>
                    </div>
                """, unsafe_allow_html=True)

            st.divider()

            df_vitals = pd.DataFrame(vitals_data)

            st.markdown("#### 📈 Multi-Param Blood Pressure & Heart Rate Clinical Telemetry Graph")

            fig = go.Figure()

            fig.add_hrect(
                y0=90, y1=140,
                fillcolor="#D1FAE5", opacity=0.35,
                line_width=0,
                annotation_text="Normal BP Target Zone (90-140 mmHg)", annotation_position="top left"
            )

            fig.add_hrect(
                y0=140, y1=180,
                fillcolor="#FEF3C7", opacity=0.35,
                line_width=0,
                annotation_text="Elevated Warning Zone", annotation_position="top left"
            )

            fig.add_trace(go.Scatter(
                x=df_vitals["timestamp"],
                y=df_vitals["systolic_bp"],
                mode="lines+markers",
                name="Systolic BP (mmHg)",
                line=dict(color="#0284C7", width=3),
                marker=dict(size=8, color="#0284C7")
            ))

            fig.add_trace(go.Scatter(
                x=df_vitals["timestamp"],
                y=df_vitals["diastolic_bp"],
                mode="lines+markers",
                name="Diastolic BP (mmHg)",
                line=dict(color="#EC4899", width=2, dash="dash"),
                marker=dict(size=7, color="#EC4899")
            ))

            fig.add_trace(go.Scatter(
                x=df_vitals["timestamp"],
                y=df_vitals["heart_rate"],
                mode="lines+markers",
                name="Heart Rate (BPM)",
                line=dict(color="#10B981", width=3),
                marker=dict(size=8, color="#10B981")
            ))

            fig.update_layout(
                paper_bgcolor="#FFFFFF",
                plot_bgcolor="#FAF6EE",
                height=380,
                font=dict(color="#0F172A", family="Inter, sans-serif"),
                hovermode="x unified",
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                margin=dict(l=20, r=20, t=40, b=20),
                yaxis=dict(title="Vital Signs Scale (mmHg / BPM)", gridcolor="#E2E8F0"),
                xaxis=dict(title="Streaming Telemetry Timestamp", gridcolor="#E2E8F0")
            )

            st.plotly_chart(fig, use_container_width=True)

            # Time-to-Time Patient Details & Telemetry Updater
            st.divider()
            st.markdown("#### ⏱️ Real-Time Patient Details & Telemetry Updater (Time-to-Time)")
            st.markdown(
                "<div style='color: #475569; font-size: 0.9rem; font-weight: 600; margin-bottom: 12px;'>"
                "Paramedics and triage officers can update patient clinical conditions, accident severity, "
                "dispatcher observations, and vital signs dynamically over time."
                "</div>",
                unsafe_allow_html=True
            )

            with st.expander(f"📝 Edit & Update Details for {selected_case['patient_name']} (Case #{selected_case['id']})", expanded=False):
                with st.form(f"update_patient_form_{selected_case['id']}"):
                    u_col1, u_col2 = st.columns(2)
                    with u_col1:
                        u_name = st.text_input("Patient Name", value=selected_case["patient_name"])
                        u_age = st.number_input("Patient Age", min_value=1, max_value=120, value=int(selected_case["patient_age"]))
                        u_type = st.text_input("Emergency / Accident Type", value=selected_case["emergency_type"])
                        
                        sev_options = ["Critical", "Mild", "Minor"]
                        curr_sev = get_accident_severity(selected_case)
                        sev_idx = sev_options.index(curr_sev) if curr_sev in sev_options else 0
                        u_sev = st.selectbox("Accident Severity Classification:", sev_options, index=sev_idx)
                        status_opts = ["REPORTED", "DISPATCHED", "IN_TRANSIT", "ARRIVED", "RESOLVED"]
                        st_idx = status_opts.index(selected_case["status"]) if selected_case["status"] in status_opts else 1
                        u_status = st.selectbox("Transit Status:", status_opts, index=st_idx)

                    with u_col2:
                        st.markdown("##### 🩺 New Vital Signs Telemetry Reading:")
                        cur_hr = latest["heart_rate"] if vitals_data else 80
                        cur_sbp = latest["systolic_bp"] if vitals_data else 120
                        cur_dbp = latest["diastolic_bp"] if vitals_data else 80
                        cur_spo2 = latest["spo2"] if vitals_data else 98
                        cur_temp = latest["temperature"] if vitals_data else 37.0
                        cur_ecg = latest["ecg_status"] if vitals_data else "NORMAL"

                        v_c1, v_c2 = st.columns(2)
                        with v_c1:
                            new_hr = st.number_input("Heart Rate (bpm)", min_value=30, max_value=220, value=int(cur_hr))
                            new_sbp = st.number_input("Systolic BP (mmHg)", min_value=50, max_value=250, value=int(cur_sbp))
                            new_spo2 = st.number_input("Oxygen SpO2 (%)", min_value=50, max_value=100, value=int(cur_spo2))
                        with v_c2:
                            new_dbp = st.number_input("Diastolic BP (mmHg)", min_value=30, max_value=150, value=int(cur_dbp))
                            new_temp = st.number_input("Temperature (°C)", min_value=32.0, max_value=43.0, value=float(cur_temp), step=0.1)
                            ecg_opts = ["NORMAL", "ST_ELEVATION", "ARRHYTHMIA", "CRITICAL_ALERT"]
                            ecg_idx = ecg_opts.index(cur_ecg) if cur_ecg in ecg_opts else 0
                            new_ecg = st.selectbox("ECG Status", ecg_opts, index=ecg_idx)

                    u_notes = st.text_area("Updated Clinical Notes / Dispatcher Log", value=selected_case.get("notes") or "")

                    save_btn = st.form_submit_button("💾 Save & Broadcast Updated Patient Details", type="primary")

                    if save_btn:
                        update_payload = {
                            "patient_name": u_name,
                            "patient_age": u_age,
                            "emergency_type": u_type,
                            "accident_severity": u_sev,
                            "status": u_status,
                            "notes": u_notes
                        }
                        p_ok = update_patient_details(selected_case["id"], update_payload)
                        v_ok = record_patient_vital(selected_case["id"], new_hr, new_spo2, new_sbp, new_dbp, new_temp, new_ecg)

                        if p_ok or v_ok:
                            st.success(f"✅ Patient details and new telemetry logged for Case #{selected_case['id']} ({u_name})!")
                            time.sleep(0.8)
                            st.rerun()
                        else:
                            st.error("Failed to save patient update. Check server logs.")
        else:
            st.info("Click 'Stream Next Vital Reading' to record patient telemetry.")
    else:
        st.info("No active patient transports currently streaming vitals.")

# ==========================================
# TAB 3: Visual Analytics & Hospital Board
# ==========================================
with tab3:
    st.markdown("### 📊 Hospital Resource Analytics & Command Board")

    c_chart1, c_chart2 = st.columns(2)

    with c_chart1:
        st.markdown("#### ICU Bed Distribution Across Hospitals")
        h_names = [h["name"].replace("Hospital", "").replace("Emergency", "") for h in hospitals]
        h_icu = [h["icu_beds_available"] for h in hospitals]

        fig_pie = go.Figure(data=[go.Pie(labels=h_names, values=h_icu, hole=.3, marker_colors=['#0284C7', '#0EA5E9', '#38BDF8', '#7DD3FC'])])
        fig_pie.update_layout(height=270, margin=dict(l=10, r=10, t=30, b=10), paper_bgcolor="#FAF6EE", font_color="#0F172A")
        st.plotly_chart(fig_pie, use_container_width=True)

    with c_chart2:
        st.markdown("#### Available Ventilators by Hospital")
        h_vents = [h["ventilators_available"] for h in hospitals]

        fig_bar = px.bar(
            x=h_names,
            y=h_vents,
            labels={'x': 'Hospital', 'y': 'Ventilators Ready'},
            color_discrete_sequence=['#0284C7']
        )
        fig_bar.update_layout(height=270, paper_bgcolor="#FAF6EE", plot_bgcolor="#FFFFFF", font_color="#0F172A")
        st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()

    st.markdown("#### Live Hospital Database Monitor & Direct Allotment Controls")

    if active_cases:
        active_p = active_cases[0]
        recs_tab3 = fetch_recommendations(active_p['id'])
        top_hosp_name = recs_tab3[0]['hospital_name'] if recs_tab3 else "Apollo Emergency Healthcare Centre"
        top_hosp_id = recs_tab3[0]['hospital_id'] if recs_tab3 else 1

        st.markdown(f"""
            <div style="background-color:#E0F2FE; border: 2px solid #0284C7; border-radius: 12px; padding: 16px; margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                    <div>
                        <div style="font-size: 1.15rem; font-weight: 800; color: #1E3A8A;">🤖 AI Auto-Allotment Recommendation for Patient: {active_p['patient_name']}</div>
                        <div style="font-size: 0.95rem; color: #0284C7; font-weight: 600;">Recommended Hospital: <b>{top_hosp_name}</b></div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        if st.button(f"🤖 Confirm AI Auto-Allotment to {top_hosp_name}", type="primary", key="tab3_ai_allot"):
            try:
                res = requests.post(
                    f"{API_BASE_URL}/dispatch/auto_dispatch/{active_p['id']}",
                    params={"hospital_id": top_hosp_id}
                ).json()
                fetch_emergencies.clear()
                fetch_hospitals.clear()
                fetch_ambulances.clear()
                st.success(f"✅ **AI Allotment Confirmed!** Patient {active_p['patient_name']} allocated to `{res['assigned_hospital']}`.")
                st.info(f"🚑 Ambulance `{res['dispatched_ambulance']}` dispatched! ETA: **{res['ambulance_eta_minutes']} mins**.")
                time.sleep(1)
                st.rerun()
            except Exception as ex:
                st.error(f"Allotment error: {ex}")

        st.markdown("---")

    for h in hospitals:
        status_bg = "#D1FAE5" if h['status'] == "OPERATIONAL" else "#FEE2E2"
        status_color = "#065F46" if h['status'] == "OPERATIONAL" else "#991B1B"
        
        st.markdown(f"""
            <div class="hospital-live-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
                    <div class="hospital-title">🏥 {h['name']}</div>
                    <span style="background-color:{status_bg}; color:{status_color} !important; padding:5px 14px; border-radius:6px; font-weight:800; font-size:0.85rem; border: 1px solid {status_color};">Status: {h['status']}</span>
                </div>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 12px; margin-bottom: 14px;">
                    <div class="hosp-metric-box">
                        <div class="hosp-metric-val">{h['icu_beds_available']} / {h['icu_beds_total']}</div>
                        <div class="hosp-metric-lbl">Available ICU Beds</div>
                    </div>
                    <div class="hosp-metric-box">
                        <div class="hosp-metric-val">{h['ventilators_available']}</div>
                        <div class="hosp-metric-lbl">Ventilators Ready</div>
                    </div>
                    <div class="hosp-metric-box">
                        <div class="hosp-metric-val" style="font-size:1.1rem; color:#0F172A; font-weight:700; padding-top:4px;">
                            Cardiologist: {'✅' if h['has_cardiologist'] else '❌'}<br>Neurologist: {'✅' if h['has_neurologist'] else '❌'}
                        </div>
                        <div class="hosp-metric-lbl">Specialists On-Duty</div>
                    </div>
                    <div class="hosp-metric-box">
                        <div class="hosp-metric-val" style="font-size:1.0rem; color:#0284C7; font-weight:700; padding-top:8px;">{h['contact_number']}</div>
                        <div class="hosp-metric-lbl">ER Contact Line</div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        if active_cases:
            curr_p = active_cases[0]
            if st.button(f"🖐️ Manually Allot {curr_p['patient_name']} to {h['name']}", key=f"man_allot_hosp_{h['id']}"):
                try:
                    res = requests.post(
                        f"{API_BASE_URL}/dispatch/auto_dispatch/{curr_p['id']}",
                        params={"hospital_id": h['id']}
                    ).json()
                    fetch_emergencies.clear()
                    fetch_hospitals.clear()
                    fetch_ambulances.clear()
                    st.success(f"✅ **Manual Allotment Confirmed!** Patient {curr_p['patient_name']} allocated to `{h['name']}`.")
                    st.info(f"🚑 Ambulance `{res['dispatched_ambulance']}` dispatched! ETA: **{res['ambulance_eta_minutes']} mins**.")
                    time.sleep(1)
                    st.rerun()
                except Exception as ex:
                    st.error(f"Manual allotment error: {ex}")

# ==========================================
# TAB 4: Intake Emergency (AI Triage)
# ==========================================
with tab4:
    st.markdown("### 📝 Incident Reporting & AI Priority Triage")

    with st.form("pro_emergency_form"):
        col1, col2 = st.columns(2)
        with col1:
            p_name = st.text_input("Patient Name", value="Ravi Kumar")
            p_age = st.number_input("Patient Age", min_value=1, max_value=110, value=48)
            e_type = st.selectbox("Emergency Category", ["Heart Attack", "Stroke", "Road Accident / Trauma", "Severe Respiratory Distress", "Other Emergency"])
            address = st.text_input("Location Address", value="IT Expressway, Sector 4")

        with col2:
            st.markdown("##### Clinical Symptoms & Risk Factors")
            cp = st.checkbox("Chest Pain / Pressure", value=True)
            sob = st.checkbox("Shortness of Breath", value=True)
            loc = st.checkbox("Loss of Consciousness", value=False)
            bleeding = st.checkbox("Severe Bleeding", value=False)
            
            sev_selection = st.selectbox(
                "Accident / Emergency Severity:",
                ["Critical (Severe Trauma / Unconscious / High Alert)", "Mild (Moderate Collision / Stable)", "Minor (Low-Speed Skid / Surface Injury)"]
            )

            lat = st.number_input("Latitude", value=17.4400, format="%.4f")
            lon = st.number_input("Longitude", value=78.4450, format="%.4f")

        notes = st.text_area("Medical Dispatcher Notes", value="Patient collapsed while driving, chest pain radiating to left arm.")
        
        submitted = st.form_submit_button("Submit Emergency Case & Run AI Triage", type="primary")

        if submitted:
            if "Critical" in sev_selection:
                sev_tag = "Critical"
            elif "Mild" in sev_selection:
                sev_tag = "Mild"
            else:
                sev_tag = "Minor"

            payload = {
                "patient_name": p_name,
                "patient_age": p_age,
                "emergency_type": e_type,
                "accident_severity": sev_tag,
                "location_lat": lat,
                "location_lon": lon,
                "address": address,
                "chest_pain": cp,
                "shortness_of_breath": sob,
                "loss_of_consciousness": loc,
                "severe_bleeding": bleeding,
                "notes": notes
            }

            try:
                res = requests.post(f"{API_BASE_URL}/emergencies/", json=payload)
                if res.status_code == 200:
                    data = res.json()
                    fetch_emergencies.clear()
                    fetch_hospitals.clear()
                    fetch_ambulances.clear()
                    st.session_state["selected_case_id"] = data["id"]
                    if "allotment_counter" in st.session_state:
                        st.session_state["allotment_counter"] += 1
                    st.success(f"Emergency incident #{data['id']} ({data['patient_name']}) logged successfully.")
                    st.markdown(f"### AI Triage: **{data['priority']}** ({data['priority_score']}/100) | Severity: **{sev_tag.upper()}**")
                    st.info("Navigate to 'Live Command & GIS Map' tab to confirm hospital allotment & dispatch nearest ambulance.")
                else:
                    st.error(f"Error submitting intake: {res.text}")
            except Exception as ex:
                st.error(f"Submission error: {ex}")

# ==========================================
# TAB 5: Incident & Allotment History
# ==========================================
with tab5:
    st.markdown("### 📜 Incident & Hospital Allotment History")
    st.markdown(
        "<div style='color: #475569; font-weight: 600; margin-bottom: 18px;'>"
        "Comprehensive operational audit trail of emergency calls, accident severities (Critical, Mild, Minor), "
        "assigned receiving hospitals, dispatched emergency response vehicles, and active transit states."
        "</div>",
        unsafe_allow_html=True
    )

    ambulances = fetch_ambulances()
    amb_map = {a["id"]: a["call_sign"] for a in ambulances}
    hosp_map = {h["id"]: h["name"] for h in hospitals}

    # Summary KPI Cards (Classified: Critical, Mild, Minor)
    total_incidents = len(emergencies)
    crit_cases = [e for e in emergencies if get_accident_severity(e) == "Critical"]
    mild_cases = [e for e in emergencies if get_accident_severity(e) == "Mild"]
    minor_cases = [e for e in emergencies if get_accident_severity(e) == "Minor"]

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""
            <div style="background-color:#FAF6EE; border:2px solid #BAE6FD; border-radius:10px; padding:14px 18px; text-align:center;">
                <div style="font-size:1.8rem; font-weight:800; color:#0284C7;">{total_incidents}</div>
                <div style="font-size:0.85rem; font-weight:700; color:#475569;">Total Emergency Incidents</div>
            </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
            <div style="background-color:#FAF6EE; border:2px solid #FCA5A5; border-radius:10px; padding:14px 18px; text-align:center;">
                <div style="font-size:1.8rem; font-weight:800; color:#DC2626;">{len(crit_cases)}</div>
                <div style="font-size:0.85rem; font-weight:700; color:#475569;">🔴 Critical Accidents & Traumas</div>
            </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
            <div style="background-color:#FAF6EE; border:2px solid #FDE68A; border-radius:10px; padding:14px 18px; text-align:center;">
                <div style="font-size:1.8rem; font-weight:800; color:#D97706;">{len(mild_cases)}</div>
                <div style="font-size:0.85rem; font-weight:700; color:#475569;">🟡 Mild Accidents</div>
            </div>
        """, unsafe_allow_html=True)
    with m4:
        st.markdown(f"""
            <div style="background-color:#FAF6EE; border:2px solid #86EFAC; border-radius:10px; padding:14px 18px; text-align:center;">
                <div style="font-size:1.8rem; font-weight:800; color:#15803D;">{len(minor_cases)}</div>
                <div style="font-size:0.85rem; font-weight:700; color:#475569;">🟢 Minor Accidents</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    # Filter Controls Container
    st.markdown("""
        <div style="background-color:#FAF6EE; border:1.5px solid #BAE6FD; border-radius:10px; padding:14px 18px; margin-bottom:14px;">
            <div style="font-size:1.0rem; font-weight:800; color:#0F172A; margin-bottom:8px;">🔍 Search & Filter Incident Allotments</div>
        </div>
    """, unsafe_allow_html=True)

    fc1, fc2, fc3, fc4 = st.columns([2, 1, 1, 1])
    with fc1:
        search_query = st.text_input("Search by Patient Name, ID, or Location Address:", placeholder="e.g. Vikram, Accident, Banjara...", key="hist_search")
    with fc2:
        category_filter = st.selectbox("Filter Incident Category:", ["All Categories", "Road Accidents & Trauma", "Heart Attack", "Stroke", "Respiratory Distress"], key="hist_cat")
    with fc3:
        severity_filter = st.selectbox("Filter Severity:", ["All Severities", "Critical", "Mild", "Minor"], key="hist_sev")
    with fc4:
        status_filter = st.selectbox("Filter by Status:", ["All Statuses", "DISPATCHED", "IN_TRANSIT", "ARRIVED", "RESOLVED", "REPORTED"], key="hist_status")

    # Filter the emergencies
    filtered_cases = list(emergencies)

    if search_query.strip():
        q = search_query.strip().lower()
        filtered_cases = [
            e for e in filtered_cases
            if q in str(e.get("id")).lower()
            or q in e.get("patient_name", "").lower()
            or q in e.get("emergency_type", "").lower()
            or q in e.get("address", "").lower()
            or q in str(e.get("notes", "")).lower()
        ]

    if category_filter == "Road Accidents & Trauma":
        filtered_cases = [e for e in filtered_cases if "accident" in e.get("emergency_type", "").lower() or "trauma" in e.get("emergency_type", "").lower()]
    elif category_filter == "Heart Attack":
        filtered_cases = [e for e in filtered_cases if "heart" in e.get("emergency_type", "").lower() or "cardiac" in e.get("emergency_type", "").lower()]
    elif category_filter == "Stroke":
        filtered_cases = [e for e in filtered_cases if "stroke" in e.get("emergency_type", "").lower()]
    elif category_filter == "Respiratory Distress":
        filtered_cases = [e for e in filtered_cases if "respiratory" in e.get("emergency_type", "").lower() or "asthma" in e.get("emergency_type", "").lower()]

    if severity_filter != "All Severities":
        filtered_cases = [e for e in filtered_cases if get_accident_severity(e) == severity_filter]

    if status_filter != "All Statuses":
        filtered_cases = [e for e in filtered_cases if e.get("status") == status_filter]

    st.markdown(f"**Showing {len(filtered_cases)} of {total_incidents} incident allotment records**")

    # Sub-views: Rich Cards vs Audit Table
    hist_subtab1, hist_subtab2, hist_subtab3 = st.tabs([
        "🗂️ Detailed Case Cards",
        "📋 Allotment Audit Table & CSV",
        "📈 Allotment Distribution Analytics"
    ])

    with hist_subtab1:
        if not filtered_cases:
            st.info("No incident records match the selected filters.")
        else:
            for case in filtered_cases:
                # Lookup hospital and ambulance names
                h_name = case.get("recommended_hospital_name")
                if not h_name or h_name == "Pending Hospital Allotment":
                    h_name = hosp_map.get(case.get("recommended_hospital_id"), "⚠️ Pending Allotment")

                amb_call = case.get("assigned_ambulance_call_sign")
                if not amb_call or amb_call == "Pending Ambulance":
                    amb_call = amb_map.get(case.get("assigned_ambulance_id"), "⚠️ Unassigned")

                v_hist = fetch_vitals_history(case["id"]) if get_accident_severity(case) == "Critical" else None

                # Render attractive emoji template card (no raw code blocks, 100% clean HTML)
                st.markdown(render_incident_card_html(case, h_name, amb_call, v_hist=v_hist), unsafe_allow_html=True)

                # Quick Operational Status Controls
                col_up1, col_up2, col_up3 = st.columns([2, 1, 1.2])
                with col_up1:
                    status_choices = ["DISPATCHED", "IN_TRANSIT", "ARRIVED", "RESOLVED"]
                    current_idx = status_choices.index(case["status"]) if case["status"] in status_choices else 0
                    status_display = {
                        "DISPATCHED": "🚑 DISPATCHED",
                        "IN_TRANSIT": "⏱️ IN TRANSIT",
                        "ARRIVED": "🏥 ARRIVED",
                        "RESOLVED": "✅ RESOLVED"
                    }
                    new_st = st.selectbox(
                        f"Operational Transit Status (Case #{case['id']}):",
                        status_choices,
                        index=current_idx,
                        format_func=lambda x: status_display.get(x, x),
                        key=f"status_select_{case['id']}"
                    )
                with col_up2:
                    st.write("")
                    st.write("")
                    if st.button("🔄 Update Status", key=f"btn_up_{case['id']}", type="primary"):
                        if update_case_status(case["id"], new_st):
                            fetch_emergencies.clear()
                            fetch_hospitals.clear()
                            fetch_ambulances.clear()
                            st.success(f"Case #{case['id']} status updated to {new_st}")
                            time.sleep(0.5)
                            st.rerun()
                with col_up3:
                    st.write("")
                    st.write("")
                    if case.get("status") in ["DISPATCHED", "IN_TRANSIT"]:
                        st.caption("📡 Telemetry stream active in Tab 2")
                    else:
                        st.caption("🔒 Allotment cycle concluded")

                # If case is awaiting hospital allotment, provide quick allotment action directly in history card
                if not case.get("recommended_hospital_id") or "pending" in str(h_name).lower():
                    st.info(f"⏳ **Case #{case['id']} ({case['patient_name']}) is awaiting Hospital Allotment & Fleet Dispatch.**")
                    col_ha1, col_ha2 = st.columns([1, 1])
                    with col_ha1:
                        if st.button(f"🤖 Confirm AI Auto-Allotment (Case #{case['id']})", key=f"hist_auto_{case['id']}", type="primary"):
                            try:
                                res = requests.post(f"{API_BASE_URL}/dispatch/auto_dispatch/{case['id']}").json()
                                fetch_emergencies.clear()
                                fetch_hospitals.clear()
                                fetch_ambulances.clear()
                                st.success(f"✅ Patient {case['patient_name']} allocated to {res['assigned_hospital']}!")
                                time.sleep(0.8)
                                st.rerun()
                            except Exception as ex:
                                st.error(f"Allotment error: {ex}")
                    with col_ha2:
                        h_choices = {f"{h['name']} ({h['icu_beds_available']} ICU Beds)": h['id'] for h in hospitals}
                        chosen_h = st.selectbox("Select Hospital for Manual Allotment:", list(h_choices.keys()), key=f"hist_h_sel_{case['id']}")
                        if st.button(f"🖐️ Confirm Manual Allotment (Case #{case['id']})", key=f"hist_man_{case['id']}"):
                            try:
                                h_id = h_choices[chosen_h]
                                res = requests.post(f"{API_BASE_URL}/dispatch/auto_dispatch/{case['id']}", params={"hospital_id": h_id}).json()
                                fetch_emergencies.clear()
                                fetch_hospitals.clear()
                                fetch_ambulances.clear()
                                st.success(f"✅ Patient {case['patient_name']} allocated to {res['assigned_hospital']}!")
                                time.sleep(0.8)
                                st.rerun()
                            except Exception as ex:
                                st.error(f"Allotment error: {ex}")

                st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    with hist_subtab2:
        st.markdown("#### 📋 Official Allotment Audit Register")
        
        table_rows = []
        for case in filtered_cases:
            h_name = case.get("recommended_hospital_name")
            if not h_name or h_name == "Pending Hospital Allotment":
                h_name = hosp_map.get(case.get("recommended_hospital_id"), "Pending")

            amb_call = case.get("assigned_ambulance_call_sign")
            if not amb_call or amb_call == "Pending Ambulance":
                amb_call = amb_map.get(case.get("assigned_ambulance_id"), "Unassigned")

            table_rows.append({
                "Case ID": f"#{case['id']}",
                "Reported At": format_timestamp(case.get("created_at")),
                "Patient Name": case["patient_name"],
                "Age": case["patient_age"],
                "Emergency / Accident Type": case["emergency_type"],
                "Accident Severity": get_accident_severity(case).upper(),
                "Priority": case["priority"],
                "AI Score": f"{case['priority_score']:.1f}",
                "Allotted Hospital": h_name,
                "Dispatched Ambulance": amb_call,
                "Location Address": case["address"],
                "Status": case["status"]
            })

        if table_rows:
            df_hist = pd.DataFrame(table_rows)
            st.dataframe(df_hist, use_container_width=True, hide_index=True)

            csv_data = df_hist.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Export Allotment Audit Register (CSV)",
                data=csv_data,
                file_name=f"emergency_incident_allotments_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                type="primary"
            )
        else:
            st.info("No records to display.")

    with hist_subtab3:
        st.markdown("#### 📈 Incident & Allotment Analytics")
        ch_col1, ch_col2 = st.columns(2)

        with ch_col1:
            st.markdown("##### Allotments by Receiving Hospital")
            hosp_counts = {}
            for c in emergencies:
                h_name = c.get("recommended_hospital_name")
                if not h_name or h_name == "Pending Hospital Allotment":
                    h_name = hosp_map.get(c.get("recommended_hospital_id"), "Unallotted")
                hosp_counts[h_name] = hosp_counts.get(h_name, 0) + 1

            df_hosp_counts = pd.DataFrame(list(hosp_counts.items()), columns=["Hospital", "Allotted Cases"])
            fig_h_bar = px.bar(
                df_hosp_counts,
                x="Hospital",
                y="Allotted Cases",
                color="Allotted Cases",
                color_continuous_scale="Blues",
                labels={"Allotted Cases": "Incidents Allotted"}
            )
            fig_h_bar.update_layout(
                paper_bgcolor="#FAF6EE",
                plot_bgcolor="#FFFFFF",
                height=320,
                font_color="#0F172A",
                margin=dict(l=10, r=10, t=30, b=10)
            )
            st.plotly_chart(fig_h_bar, use_container_width=True)

        with ch_col2:
            st.markdown("##### Incident Categories Breakdown")
            cat_counts = {}
            for c in emergencies:
                etype = c.get("emergency_type", "Other")
                cat_counts[etype] = cat_counts.get(etype, 0) + 1

            df_cat_counts = pd.DataFrame(list(cat_counts.items()), columns=["Category", "Count"])
            fig_cat_pie = px.pie(
                df_cat_counts,
                names="Category",
                values="Count",
                hole=0.35,
                color_discrete_sequence=['#EF4444', '#0284C7', '#F59E0B', '#10B981', '#8B5CF6']
            )
            fig_cat_pie.update_layout(
                paper_bgcolor="#FAF6EE",
                height=320,
                font_color="#0F172A",
                margin=dict(l=10, r=10, t=30, b=10)
            )
            st.plotly_chart(fig_cat_pie, use_container_width=True)

