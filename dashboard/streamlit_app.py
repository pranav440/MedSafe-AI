"""
MedSafe AI – Streamlit Dashboard (v3.0 – React-Reconciled)
==========================================================
Unified UI that mimics the React frontend layout and styling.
"""

import sys
import os
import time

# ── Project root on path ──
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

import config
from database.db import init_db, get_latest_vitals, get_history, get_high_alerts, insert_vital
from models.anomaly_pipeline import analyze_vitals
from ocr.prescription_reader import extract_medicines_from_text, extract_medicines
from drug_checker.interaction_checker import check_interactions
from symptom_engine.symptom_solver import get_symptom_guidance, analyze_side_effects

# ══════════════════════════════════════════════════
#  PAGE CONFIG & THEME
# ══════════════════════════════════════════════════

st.set_page_config(
    page_title="MedSafe AI – Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Inject Modern Dark Theme CSS (Matching React App) ──
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    :root {
        --background: #09090b;
        --card: #09090b;
        --card-foreground: #fafafa;
        --primary: #58a6ff;
        --muted: #161b22;
        --muted-foreground: #a1a1aa;
        --border: #27272a;
        --severity-low: #3fb950;
        --severity-medium: #f0883e;
        --severity-high: #f85149;
    }

    .stApp {
        background-color: var(--background);
        font-family: 'Inter', sans-serif;
    }

    /* ──── Glass Card Style ──── */
    .glass-card {
        background: rgba(22, 27, 34, 0.5);
        backdrop-filter: blur(10px);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .glass-card:hover {
        border-color: rgba(88, 166, 255, 0.4);
    }

    /* ──── Metric Card Style ──── */
    .metric-container {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
    }
    .metric-title {
        font-size: 0.85rem;
        font-weight: 500;
        color: var(--muted-foreground);
    }
    .metric-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--card-foreground);
        margin-top: 4px;
    }
    .metric-icon-bg {
        padding: 10px;
        border-radius: 8px;
        background: rgba(88, 166, 255, 0.1);
        color: var(--primary);
    }

    /* ──── Severity Badges ──── */
    .badge {
        display: inline-flex;
        align-items: center;
        padding: 2px 8px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        border: 1px solid;
    }
    .badge-low { color: var(--severity-low); background: rgba(63, 185, 80, 0.1); border-color: rgba(63, 185, 80, 0.2); }
    .badge-medium { color: var(--severity-medium); background: rgba(240, 136, 62, 0.1); border-color: rgba(240, 136, 62, 0.2); }
    .badge-high { color: var(--severity-high); background: rgba(248, 81, 73, 0.1); border-color: rgba(248, 81, 73, 0.2); }

    /* ──── Custom Sidebar ──── */
    [data-testid="stSidebar"] {
        background-color: #0d1117;
        border-right: 1px solid var(--border);
    }

    /* ──── Headers ──── */
    h2, h3 { color: #fbfbfb; font-weight: 700; tracking-tight; }

    /* ──── Hide streamlit branding ──── */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════
#  SIDEBAR NAVIGATION
# ══════════════════════════════════════════════════

st.sidebar.markdown("""
<div style="display: flex; align-items: center; gap: 10px; padding: 10px 0 20px;">
    <div style="padding: 6px; border-radius: 8px; background: rgba(88,166,255,0.1); color: #58a6ff;">
        🛡️
    </div>
    <div>
        <div style="font-weight: 700; font-size: 1.1rem; color: #fbfbfb;">MedSafe AI</div>
        <div style="font-size: 0.7rem; color: #8b949e; line-height: 1;">Safety Assistant</div>
    </div>
</div>
""", unsafe_allow_html=True)

page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Vitals Monitor", "Prescription Analyzer", "Drug Interactions", "Symptom Guidance", "Side Effect Reporter"],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style="padding: 12px; background: rgba(248,81,73,0.05); border: 1px solid rgba(248,81,73,0.15); border-radius: 8px; font-size: 0.75rem;">
    ⚕ <b>Disclaimer</b><br>
    Educational purposes only. Not a substitute for medical advice.
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════
#  HELPER COMPONENTS
# ══════════════════════════════════════════════════

def render_metric_card(title, value, icon, severity=None, subtitle=None):
    badge_html = ""
    if severity:
        cls = f"badge-{severity.lower()}"
        badge_html = f'<div class="badge {cls}" style="margin-top: 8px;">{severity}</div>'
    
    subtitle_html = f'<div style="font-size:0.75rem; color:var(--muted-foreground); margin-top:2px;">{subtitle}</div>' if subtitle else ""

    st.markdown(f"""
    <div class="glass-card">
        <div class="metric-container">
            <div style="min-width:0;">
                <div class="metric-title">{title}</div>
                <div class="metric-value">{value}</div>
                {subtitle_html}
            </div>
            <div class="metric-icon-bg">{icon}</div>
        </div>
        {badge_html}
    </div>
    """, unsafe_allow_html=True)

def render_medicines(result):
    st.markdown("### 💊 Medicines Identified")
    if result.get("medicines_found"):
        for med in result["medicines_found"]:
            st.markdown(f"""
            <div class="glass-card" style="display:flex; justify-content:space-between; align-items:center; padding:15px;">
                <div>
                    <div style="font-weight:600; color:#fafafa;">{med['medicine']}</div>
                    <div style="font-size:0.8rem; color:#8b949e;">Salt: <code style="color:#bc8cff;">{med['active_salt']}</code></div>
                </div>
                <div style="text-align:right;">
                    <div style="font-weight:700; color:#58a6ff;">{med['confidence']}%</div>
                    <div style="font-size:0.7rem; color:#8b949e;">match</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No medicines identified.")

# ── Init DB ──
try: init_db()
except: pass

# ══════════════════════════════════════════════════
#  PAGE: DASHBOARD
# ══════════════════════════════════════════════════

if page == "Dashboard":
    st.markdown("## Dashboard")
    st.markdown("<p style='color:var(--muted-foreground); margin-top:-15px; margin-bottom:20px;'>Real-time patient monitoring overview</p>", unsafe_allow_html=True)

    data = get_latest_vitals(limit=30)
    if data:
        last = data[0]
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1: render_metric_card("Heart Rate", f"{last['heart_rate']} bpm", "❤️", subtitle="Range: 60-100")
        with c2: render_metric_card("Oxygen Level", f"{last['oxygen']}%", "🫁", subtitle="Normal: >95%")
        with c3: render_metric_card("Blood Pressure", f"{last['bp_systolic']}/{last['bp_diastolic']}", "🩸", subtitle="mmHg")
        with c4: render_metric_card("Anomaly Score", f"{last['anomaly_score']:.2f}", "🧠", severity=last['severity'])
        with c5: render_metric_card("Severity", last['severity'], "🛡️", severity=last['severity'])

        col_left, col_right = st.columns([2, 1])
        with col_left:
            st.markdown("### Vitals Trends")
            df = pd.DataFrame(data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df['timestamp'], y=df['heart_rate'], name="Heart Rate", line=dict(color='#f85149', width=2)))
            fig.add_trace(go.Scatter(x=df['timestamp'], y=df['oxygen'], name="Oxygen %", line=dict(color='#58a6ff', width=2)))
            fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                              margin=dict(l=0, r=0, t=10, b=0), height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        with col_right:
            st.markdown("### Risk Alerts")
            highs = [d for d in data if d['severity'] == 'HIGH']
            if highs:
                for h in highs[:3]:
                    st.error(f"🚨 {h['timestamp'].strftime('%H:%M')} - Critical Anomaly!")
            else:
                st.success("All systems operational. No critical risks detected.")
    else:
        st.info("System is waiting for vitals data. Use the simulator or manual input.")

# ══════════════════════════════════════════════════
#  PAGE: VITALS MONITOR
# ══════════════════════════════════════════════════

elif page == "Vitals Monitor":
    st.markdown("## Vitals Monitor")
    st.markdown("<p style='color:var(--muted-foreground); margin-top:-15px;'>Detailed patient history and analytics</p>", unsafe_allow_html=True)

    with st.expander("➕ Add Data Manually", expanded=False):
        with st.form("manual"):
            c1, c2 = st.columns(2)
            hr = c1.number_input("Heart Rate", 40, 200, 75)
            o2 = c1.number_input("Oxygen %", 50, 100, 98)
            bps = c2.number_input("Systolic", 80, 200, 120)
            bpd = c2.number_input("Diastolic", 40, 140, 80)
            if st.form_submit_button("Record Vital"):
                res = analyze_vitals(hr, o2, bps, bpd)
                insert_vital(hr, o2, bps, bpd, res['anomaly_score'], res['severity'])
                st.success("Reading saved.")
                st.rerun()

    data = get_latest_vitals(limit=50)
    if data:
        st.dataframe(pd.DataFrame(data), use_container_width=True, height=400)
    else:
        st.write("No historical data found.")

# ══════════════════════════════════════════════════
#  PAGE: PRESCRIPTION ANALYZER
# ══════════════════════════════════════════════════

elif page == "Prescription Analyzer":
    st.markdown("## Prescription Analyzer")
    t1, t2 = st.tabs(["📷 Upload Image", "📝 Paste Text"])
    with t1:
        img = st.file_uploader("Upload Image", type=['jpg', 'png', 'jpeg'])
        if img:
            st.image(img, width=400)
            if st.button("Extract Data"):
                with open("temp.png", "wb") as f: f.write(img.getbuffer())
                render_medicines(extract_medicines("temp.png"))
    with t2:
        txt = st.text_area("Prescription Text", height=150)
        if st.button("Identify Medicines"):
            render_medicines(extract_medicines_from_text(txt))

# ══════════════════════════════════════════════════
#  PAGE: DRUG INTERACTIONS
# ══════════════════════════════════════════════════

elif page == "Drug Interactions":
    st.markdown("## Drug Interaction Checker")
    meds_raw = st.text_input("Enter Medicines (comma separated)", placeholder="Aspirin, Warfarin")
    if st.button("Check Safety"):
        meds = [m.strip() for m in meds_raw.split(",") if m.strip()]
        if len(meds) > 1:
            res = check_interactions(meds)
            if res["interactions_found"]:
                for ix in res["interactions_found"]:
                    st.warning(f"⚠️ {ix['drug_1']} + {ix['drug_2']}: {ix['description']}")
            else:
                st.success("No known interactions found.")
        else:
            st.info("Please enter at least two medicines.")

# ══════════════════════════════════════════════════
#  PAGE: SYMPTOM GUIDANCE
# ══════════════════════════════════════════════════

elif page == "Symptom Guidance":
    st.markdown("## Symptom Guidance")
    sym = st.text_input("Describe Symptoms", placeholder="headache, fever")
    if st.button("Analyze"):
        res = get_symptom_guidance([s.strip() for s in sym.split(",")])
        for match in res["matched_conditions"]:
            with st.expander(f"📌 {match['condition']} ({match['match_score']}% match)"):
                st.write("**Causes:** " + ", ".join(match['possible_causes']))
                st.write("**Remedies:** " + ", ".join(match['home_remedies']))

# ══════════════════════════════════════════════════
#  PAGE: SIDE EFFECT REPORTER
# ══════════════════════════════════════════════════

elif page == "Side Effect Reporter":
    st.markdown("## Side-Effect Reporter")
    with st.form("se"):
        c1, c2 = st.columns(2)
        med = c1.text_input("Medicine")
        eff = c2.text_input("Side Effects Experienced")
        if st.form_submit_button("Report"):
            res = analyze_side_effects(30, "Male", med, "500mg", [eff])
            st.info(res["analysis"])

# ══════════════════════════════════════════════════
#  FOOTER
# ══════════════════════════════════════════════════

st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style="text-align:center; font-size:0.7rem; color:#8b949e;">
    MedSafe AI Unified UI v3.0<br>
    © 2026 MedSafe AI Labs
</div>
""", unsafe_allow_html=True)
