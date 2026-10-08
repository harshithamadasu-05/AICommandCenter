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

API_BASE_URL = "http://127.0.0.1:8000/api"

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
        border-radius: 8px;
        color: #0F172A !important;
        font-weight: 600 !important;
        padding: 8px 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FAF6EE !important;
        color: #0284C7 !important;
        font-weight: 800 !important;
        border: 2px solid #0284C7 !important;
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
tab1, tab2, tab3, tab4 = st.tabs([
    "🚨 Live Command & GIS Map",
    "🩺 IoT Patient Telemetry",
    "📊 Resource Analytics & Hospital Board",
    "📝 Intake Emergency (AI Triage)"
])

# ==========================================
# TAB 1: Live Command Centre & GIS Map
# ==========================================
with tab1:
    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.markdown("### 🗺️ Real-Time Street Map Navigation")
        
        map_data = []
        for h in hospitals:
            map_data.append({
                "name": f"🏥 Hospital: {h['name']} ({h['icu_beds_available']} ICU Beds)",
                "lat": h["latitude"],
                "lon": h["longitude"],
                "color": [2, 132, 199, 230] if h["icu_beds_available"] > 0 else [220, 38, 38, 230],
                "size": 200
            })
        
        for e in active_cases:
            map_data.append({
                "name": f"🚨 Patient Incident: {e['patient_name']} ({e['emergency_type']})",
                "lat": e["location_lat"],
                "lon": e["location_lon"],
                "color": [220, 38, 38, 255],
                "size": 250
            })

        df_map = pd.DataFrame(map_data)

        if not df_map.empty:
            view_state = pdk.ViewState(
                latitude=df_map["lat"].mean(),
                longitude=df_map["lon"].mean(),
                zoom=13,
                pitch=0
            )

            layer = pdk.Layer(
                "ScatterplotLayer",
                df_map,
                get_position=["lon", "lat"],
                get_color="color",
                get_radius="size",
                pickable=True
            )

            st.pydeck_chart(pdk.Deck(
                layers=[layer],
                initial_view_state=view_state,
                map_style="https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json",
                tooltip={"text": "{name}"}
            ))
        else:
            st.info("No active emergency markers to display on map.")

    with col_right:
        st.markdown("### ⚡ Dispatch & Hospital Allocation")
        
        if active_cases:
            case_options = {f"Case #{e['id']}: {e['patient_name']} ({e['emergency_type']})": e for e in active_cases}
            selected_label = st.selectbox("Select Active Incident:", list(case_options.keys()))
            selected_case = case_options[selected_label]

            p_badge = f"badge-{selected_case['priority'].lower()}"
            st.markdown(f"""
                <div style="background-color:#FAF6EE; border:2px solid #0284C7; border-radius:10px; padding:18px; margin-bottom:16px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h4 style="margin:0; color:#0F172A !important; font-weight:800;">{selected_case['patient_name']} ({selected_case['patient_age']} yrs)</h4>
                        <span class="{p_badge}">{selected_case['priority']}</span>
                    </div>
                    <div style="margin-top: 10px; color:#0F172A !important; line-height: 1.6;">
                        <b>Emergency Category:</b> {selected_case['emergency_type']}<br>
                        <b>AI Severity Score:</b> {selected_case['priority_score']}/100<br>
                        <b>Location:</b> {selected_case['address']}
                    </div>
                </div>
            """, unsafe_allow_html=True)

            st.markdown("#### 🧠 Hospital Recommendations & Allotment Controls")
            recs = fetch_recommendations(selected_case['id'])

            if recs:
                top_rec = recs[0]
                st.markdown(f"""
                    <div style="background-color:#FAF6EE; border: 2px solid #0284C7; padding: 14px; border-radius: 10px; margin-bottom: 12px;">
                        <div style="font-size: 1.05rem; font-weight: 800; color: #0F172A !important;">⭐ Primary AI Pick: {top_rec['hospital_name']}</div>
                        <div style="color: #0284C7 !important; font-size: 0.9rem; margin-top: 4px; font-weight: 700;">Suitability Score: {top_rec['suitability_score']}/100 | Distance: {top_rec['distance_km']} km (ETA: {top_rec['eta_minutes']} mins)</div>
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

            st.divider()

            st.markdown("##### 🏥 Confirm Patient Hospital Allotment:")

            btn_col1, btn_col2 = st.columns(2)

            with btn_col1:
                if st.button("🤖 Confirm AI Auto-Allotment", type="primary"):
                    try:
                        top_hosp_id = recs[0]['hospital_id'] if recs else None
                        res = requests.post(
                            f"{API_BASE_URL}/dispatch/auto_dispatch/{selected_case['id']}",
                            params={"hospital_id": top_hosp_id}
                        ).json()
                        st.balloons()
                        st.success(f"✅ **AI Allotment Confirmed!** Patient {selected_case['patient_name']} allocated to `{res['assigned_hospital']}`.")
                        st.info(f"🚑 Ambulance `{res['dispatched_ambulance']}` dispatched! ETA: **{res['ambulance_eta_minutes']} mins**.")
                        time.sleep(1)
                        st.rerun()
                    except Exception as ex:
                        st.error(f"AI Allotment error: {ex}")

            with btn_col2:
                hosp_options = {f"{h['name']} ({h['icu_beds_available']} ICU Beds)": h for h in hospitals}
                selected_hosp_label = st.selectbox("Select Hospital for Manual Allotment:", list(hosp_options.keys()), key="man_tab1_select")
                man_hosp = hosp_options[selected_hosp_label]

                if st.button("🖐️ Confirm Manual Allotment", type="secondary"):
                    try:
                        res = requests.post(
                            f"{API_BASE_URL}/dispatch/auto_dispatch/{selected_case['id']}",
                            params={"hospital_id": man_hosp['id']}
                        ).json()
                        st.balloons()
                        st.success(f"✅ **Manual Allotment Confirmed!** Patient {selected_case['patient_name']} allocated to `{man_hosp['name']}`.")
                        st.info(f"🚑 Ambulance `{res['dispatched_ambulance']}` dispatched! ETA: **{res['ambulance_eta_minutes']} mins**.")
                        time.sleep(1)
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
        case_options = {f"Case #{e['id']}: {e['patient_name']} ({e['emergency_type']})": e for e in active_cases}
        selected_label = st.selectbox("Select Patient Telemetry Stream:", list(case_options.keys()), key="vitals_select")
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
                st.balloons()
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
                    st.balloons()
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
            
            lat = st.number_input("Latitude", value=17.4400, format="%.4f")
            lon = st.number_input("Longitude", value=78.4450, format="%.4f")

        notes = st.text_area("Medical Dispatcher Notes", value="Patient collapsed while driving, chest pain radiating to left arm.")
        
        submitted = st.form_submit_button("Submit Emergency Case & Run AI Triage", type="primary")

        if submitted:
            payload = {
                "patient_name": p_name,
                "patient_age": p_age,
                "emergency_type": e_type,
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
                    st.success("Emergency incident logged successfully.")
                    st.markdown(f"### AI Triage Priority: **{data['priority']}** ({data['priority_score']}/100)")
                    st.info("Navigate to 'Live Command & GIS Map' tab to dispatch nearest ambulance.")
                else:
                    st.error(f"Error submitting intake: {res.text}")
            except Exception as ex:
                st.error(f"Submission error: {ex}")
