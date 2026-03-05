"""
MedSafe AI – Streamlit Dashboard (v2.0 – Dark Theme)
======================================================
Modern, professional healthcare monitoring dashboard with a dark theme,
glassmorphism cards, animated metrics, and Plotly visualisations.

Launch:
    streamlit run dashboard/streamlit_app.py
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
from ocr.prescription_reader import extract_medicines_from_text

try:
    from ocr.prescription_reader import extract_medicines
    OCR_IMAGE_AVAILABLE = True
except Exception:
    OCR_IMAGE_AVAILABLE = False

from drug_checker.interaction_checker import check_interactions
from symptom_engine.symptom_solver import get_symptom_guidance, analyze_side_effects


# ══════════════════════════════════════════════════
#  PAGE CONFIG & THEME
# ══════════════════════════════════════════════════

st.set_page_config(
    page_title="MedSafe AI – Health Monitor",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Inject Dark Theme CSS ──
st.markdown("""
<style>
    /* ──── Google Font ──── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* ──── Root dark palette ──── */
    :root {
        --bg-primary:    #0e1117;
        --bg-secondary:  #161b22;
        --bg-card:       rgba(22, 27, 34, 0.85);
        --border-glow:   rgba(88, 166, 255, 0.15);
        --text-primary:  #e6edf3;
        --text-secondary:#8b949e;
        --accent-blue:   #58a6ff;
        --accent-purple: #bc8cff;
        --accent-green:  #3fb950;
        --accent-orange: #f0883e;
        --accent-red:    #f85149;
        --gradient-blue: linear-gradient(135deg, #1a73e8 0%, #6c63ff 100%);
        --gradient-green:linear-gradient(135deg, #1db954 0%, #3fb950 100%);
        --gradient-red:  linear-gradient(135deg, #d73a49 0%, #f85149 100%);
    }

    /* ──── Base app overrides ──── */
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* ──── Glass card ──── */
    .glass-card {
        background: var(--bg-card);
        backdrop-filter: blur(12px);
        border: 1px solid var(--border-glow);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 16px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .glass-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 32px rgba(88, 166, 255, 0.08);
    }

    /* ──── Metric cards ──── */
    .metric-card {
        border-radius: 16px;
        padding: 20px 16px;
        text-align: center;
        border: 1px solid var(--border-glow);
        transition: transform 0.2s ease;
    }
    .metric-card:hover { transform: translateY(-3px); }
    .metric-card .metric-value {
        font-size: 2rem;
        font-weight: 700;
        margin: 8px 0 4px;
        line-height: 1.1;
    }
    .metric-card .metric-label {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        opacity: 0.7;
    }
    .metric-card .metric-icon {
        font-size: 1.6rem;
    }

    .mc-heart   { background: linear-gradient(135deg, #1a1025 0%, #2d1f3d 100%); color: #f85149; }
    .mc-oxygen  { background: linear-gradient(135deg, #0d1b2a 0%, #1b2838 100%); color: #58a6ff; }
    .mc-bp      { background: linear-gradient(135deg, #1a1a0e 0%, #2d2d1f 100%); color: #f0883e; }
    .mc-anomaly { background: linear-gradient(135deg, #0e1a12 0%, #1f2d22 100%); color: #bc8cff; }

    /* ──── Severity badges ──── */
    .severity-badge {
        display: inline-block;
        padding: 6px 18px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.85rem;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    .sev-low    { background: rgba(63,185,80,0.15); color: #3fb950; border: 1px solid rgba(63,185,80,0.3); }
    .sev-medium { background: rgba(240,136,62,0.15); color: #f0883e; border: 1px solid rgba(240,136,62,0.3); }
    .sev-high   { background: rgba(248,81,73,0.15); color: #f85149; border: 1px solid rgba(248,81,73,0.3); animation: pulse-red 2s infinite; }

    @keyframes pulse-red {
        0%, 100% { box-shadow: 0 0 0 0 rgba(248,81,73,0.4); }
        50%      { box-shadow: 0 0 0 8px rgba(248,81,73,0); }
    }

    /* ──── Section headers ──── */
    .section-header {
        font-size: 1.3rem;
        font-weight: 600;
        color: var(--text-primary);
        margin: 24px 0 12px;
        padding-bottom: 8px;
        border-bottom: 2px solid var(--border-glow);
    }

    /* ──── Interaction warning cards ──── */
    .interaction-card {
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 12px;
        border-left: 4px solid;
    }
    .ic-high   { background: rgba(248,81,73,0.08); border-left-color: #f85149; }
    .ic-medium { background: rgba(240,136,62,0.08); border-left-color: #f0883e; }
    .ic-low    { background: rgba(63,185,80,0.08); border-left-color: #3fb950; }

    /* ──── Condition cards ──── */
    .condition-card {
        background: var(--bg-card);
        border: 1px solid var(--border-glow);
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 14px;
    }
    .condition-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--accent-blue);
        margin-bottom: 12px;
    }
    .condition-section-label {
        font-weight: 600;
        color: var(--accent-purple);
        margin-top: 10px;
        margin-bottom: 4px;
        font-size: 0.9rem;
    }

    /* ──── Sidebar styling ──── */
    section[data-testid="stSidebar"] > div {
        padding-top: 1rem;
    }

    /* ──── Footer ──── */
    .footer-text {
        text-align: center;
        font-size: 0.75rem;
        color: var(--text-secondary);
        padding: 20px;
        border-top: 1px solid var(--border-glow);
        margin-top: 40px;
    }

    /* ──── Hide streamlit branding ──── */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* ──── Better dataframe styling ──── */
    .stDataFrame { border-radius: 12px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════
#  SIDEBAR NAVIGATION
# ══════════════════════════════════════════════════

st.sidebar.markdown("""
<div style="text-align:center; padding: 10px 0 20px;">
    <div style="font-size: 2.5rem;">🏥</div>
    <div style="font-size: 1.4rem; font-weight: 700; color: #58a6ff; margin-top: 4px;">MedSafe AI</div>
    <div style="font-size: 0.8rem; color: #8b949e; margin-top: 2px;">AI-Driven Medical Safety</div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")

page = st.sidebar.radio(
    "🧭 Navigation",
    [
        "📊 Vitals Monitor",
        "🔬 Analyze Vitals",
        "💊 Prescription Analyzer",
        "⚠️ Drug Interactions",
        "🩺 Symptom Guidance",
        "📋 Side-Effect Reporter",
    ],
    label_visibility="collapsed",
)

st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style="padding: 12px; background: rgba(248,81,73,0.06); border: 1px solid rgba(248,81,73,0.2);
            border-radius: 10px; font-size: 0.78rem; color: #f0883e;">
    ⚕ <strong>Disclaimer</strong><br>
    This tool is for <em>educational purposes only</em>. It is NOT a substitute for professional medical advice.
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════
#  HELPER FUNCTIONS
# ══════════════════════════════════════════════════

def severity_badge(sev):
    """Return a styled HTML badge for severity level."""
    cls = f"sev-{sev.lower()}"
    return f'<span class="severity-badge {cls}">{sev}</span>'


def metric_card(icon, label, value, css_class):
    """Return HTML for a styled metric card."""
    return f"""
    <div class="metric-card {css_class}">
        <div class="metric-icon">{icon}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
    </div>
    """


def safe_df(data):
    """Convert list of dicts to DataFrame, coercing timestamps."""
    if data:
        df = pd.DataFrame(data)
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        return df
    return pd.DataFrame()


def dark_plotly_layout():
    """Return a dict of Plotly layout settings for the dark theme."""
    return dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#8b949e", family="Inter"),
        margin=dict(l=40, r=40, t=30, b=30),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
    )


def _render_medicines(result):
    """Display extracted medicines in styled cards."""
    st.markdown('<div class="section-header">💊 Medicines Identified</div>', unsafe_allow_html=True)
    if result.get("medicines_found"):
        for med in result["medicines_found"]:
            confidence_color = "#3fb950" if med["confidence"] >= 80 else "#f0883e"
            st.markdown(f"""
            <div class="glass-card" style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <div style="font-weight:600; font-size:1.05rem; color:#e6edf3;">
                        💊 {med['medicine']}
                    </div>
                    <div style="color:#8b949e; margin-top:4px;">
                        Active Salt: <code style="color:#bc8cff;">{med['active_salt']}</code>
                    </div>
                </div>
                <div style="text-align:right;">
                    <div style="color:{confidence_color}; font-weight:700; font-size:1.2rem;">
                        {med['confidence']}%
                    </div>
                    <div style="font-size:0.75rem; color:#8b949e;">confidence</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No medicines identified. Try a different text or clearer image.")


# ── Init DB once ──
try:
    init_db()
except Exception:
    pass


# ══════════════════════════════════════════════════
#  PAGE: VITALS MONITOR
# ══════════════════════════════════════════════════

if page == "📊 Vitals Monitor":
    # ── Header ──
    st.markdown("""
    <div style="display:flex; align-items:center; gap:14px; margin-bottom: 8px;">
        <span style="font-size:2.2rem;">📊</span>
        <div>
            <div style="font-size:1.8rem; font-weight:700; color:#e6edf3;">Real-Time Vitals Monitor</div>
            <div style="font-size:0.9rem; color:#8b949e;">Live patient vitals, severity status, and anomaly trends</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Refresh ──
    col_spacer, col_btn = st.columns([8, 1])
    with col_btn:
        if st.button("🔄", help="Refresh data"):
            st.rerun()

    # ── Fetch data ──
    try:
        latest = get_latest_vitals(limit=50)
    except Exception as e:
        st.error(f"⚠ Database error: `{e}`")
        st.info("Make sure the database is running. The system uses SQLite by default.")
        st.stop()

    if not latest:
        st.markdown("""
        <div class="glass-card" style="text-align:center; padding:40px;">
            <div style="font-size:3rem; margin-bottom:12px;">📡</div>
            <div style="font-size:1.1rem; font-weight:600; color:#e6edf3;">No Vitals Data Yet</div>
            <div style="color:#8b949e; margin-top:8px;">
                Use the <strong>🔬 Analyze Vitals</strong> page to add data manually,<br>
                or start the Kafka producer + consumer pipeline.
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.stop()

    df = safe_df(latest)
    last = latest[0]

    # ── Metric Cards ──
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown(metric_card("❤️", "Heart Rate",
                    f"{last['heart_rate']}<small style='font-size:0.9rem'> bpm</small>", "mc-heart"),
                    unsafe_allow_html=True)
    with c2:
        st.markdown(metric_card("🫁", "Oxygen",
                    f"{last['oxygen']}<small style='font-size:0.9rem'>%</small>", "mc-oxygen"),
                    unsafe_allow_html=True)
    with c3:
        st.markdown(metric_card("🩸", "Blood Pressure",
                    f"{last['bp_systolic']}/{last['bp_diastolic']}", "mc-bp"),
                    unsafe_allow_html=True)
    with c4:
        st.markdown(metric_card("📈", "Anomaly Score",
                    f"{last['anomaly_score']:.3f}", "mc-anomaly"),
                    unsafe_allow_html=True)
    with c5:
        sev = last["severity"]
        st.markdown(f"""
        <div class="metric-card" style="background: var(--bg-card); border: 1px solid var(--border-glow);">
            <div class="metric-icon">🛡️</div>
            <div style="margin: 12px 0 6px;">{severity_badge(sev)}</div>
            <div class="metric-label">Severity</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Charts ──
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-header">❤️ Heart Rate & Oxygen Trends</div>', unsafe_allow_html=True)
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(
            x=df["timestamp"], y=df["heart_rate"],
            name="Heart Rate (bpm)",
            line=dict(color="#f85149", width=2.5),
            fill="tozeroy", fillcolor="rgba(248,81,73,0.05)",
        ))
        fig1.add_trace(go.Scatter(
            x=df["timestamp"], y=df["oxygen"],
            name="Oxygen %",
            line=dict(color="#58a6ff", width=2.5),
            yaxis="y2",
        ))
        fig1.update_layout(
            **dark_plotly_layout(),
            yaxis=dict(title="Heart Rate (bpm)", gridcolor="rgba(88,166,255,0.06)"),
            yaxis2=dict(title="Oxygen %", overlaying="y", side="right",
                        gridcolor="rgba(88,166,255,0.06)"),
            height=380,
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.markdown('<div class="section-header">📈 Anomaly Score Trend</div>', unsafe_allow_html=True)
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=df["timestamp"], y=df["anomaly_score"],
            name="Anomaly Score",
            line=dict(color="#bc8cff", width=2.5),
            fill="tozeroy", fillcolor="rgba(188,140,255,0.08)",
        ))
        fig2.add_hline(y=config.THRESHOLD_HIGH, line_dash="dash",
                       line_color="#f85149", annotation_text="⚠ HIGH",
                       annotation_font_color="#f85149")
        fig2.add_hline(y=config.THRESHOLD_LOW, line_dash="dash",
                       line_color="#3fb950", annotation_text="✓ LOW",
                       annotation_font_color="#3fb950")
        fig2.update_layout(**dark_plotly_layout(), height=380)
        st.plotly_chart(fig2, use_container_width=True)

    # ── Blood Pressure Chart ──
    st.markdown('<div class="section-header">🩸 Blood Pressure Trends</div>', unsafe_allow_html=True)
    fig_bp = go.Figure()
    fig_bp.add_trace(go.Scatter(
        x=df["timestamp"], y=df["bp_systolic"],
        name="Systolic", line=dict(color="#f0883e", width=2),
        fill="tonexty" if "bp_diastolic" in df.columns else None,
    ))
    fig_bp.add_trace(go.Scatter(
        x=df["timestamp"], y=df["bp_diastolic"],
        name="Diastolic", line=dict(color="#58a6ff", width=2),
    ))
    fig_bp.update_layout(**dark_plotly_layout(), height=300)
    st.plotly_chart(fig_bp, use_container_width=True)

    # ── High Risk Alerts ──
    st.markdown('<div class="section-header">🚨 High Risk Alerts</div>', unsafe_allow_html=True)
    try:
        alerts = get_high_alerts(limit=20)
    except Exception:
        alerts = []

    if alerts:
        alerts_df = safe_df(alerts)
        st.dataframe(alerts_df, use_container_width=True, height=220)
    else:
        st.markdown("""
        <div class="glass-card" style="text-align:center; padding:20px;">
            <span style="font-size:1.5rem;">✅</span>
            <span style="color:#3fb950; font-weight:600; margin-left:8px;">
                No high-risk alerts — all readings within normal range
            </span>
        </div>
        """, unsafe_allow_html=True)

    # ── History Table ──
    st.markdown('<div class="section-header">📋 Recent Vitals History</div>', unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True, height=300)


# ══════════════════════════════════════════════════
#  PAGE: ANALYZE VITALS
# ══════════════════════════════════════════════════

elif page == "🔬 Analyze Vitals":
    st.markdown("""
    <div style="display:flex; align-items:center; gap:14px; margin-bottom: 20px;">
        <span style="font-size:2.2rem;">🔬</span>
        <div>
            <div style="font-size:1.8rem; font-weight:700; color:#e6edf3;">Manual Vitals Analysis</div>
            <div style="font-size:0.9rem; color:#8b949e;">Enter patient vitals for anomaly detection & severity classification</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.form("vitals_form"):
        c1, c2 = st.columns(2)
        with c1:
            hr = st.number_input("❤️ Heart Rate (bpm)", min_value=30.0, max_value=250.0, value=75.0, step=1.0)
            o2 = st.number_input("🫁 Oxygen Level (%)", min_value=50.0, max_value=100.0, value=97.0, step=0.5)
        with c2:
            bp_s = st.number_input("🩸 BP Systolic (mmHg)", min_value=60.0, max_value=300.0, value=120.0, step=1.0)
            bp_d = st.number_input("🩸 BP Diastolic (mmHg)", min_value=30.0, max_value=200.0, value=80.0, step=1.0)

        submitted = st.form_submit_button("🔍 Run Anomaly Detection", use_container_width=True)

    if submitted:
        with st.spinner("⏳ Running Isolation Forest + Autoencoder models…"):
            result = analyze_vitals(hr, o2, bp_s, bp_d)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Result Cards ──
        r1, r2, r3, r4 = st.columns(4)
        with r1:
            st.markdown(metric_card("📊", "Combined Score",
                        f"{result['anomaly_score']:.4f}", "mc-anomaly"), unsafe_allow_html=True)
        with r2:
            st.markdown(metric_card("🌲", "Isolation Forest",
                        f"{result['if_score']:.4f}", "mc-oxygen"), unsafe_allow_html=True)
        with r3:
            st.markdown(metric_card("🧠", "Autoencoder",
                        f"{result['ae_score']:.4f}", "mc-bp"), unsafe_allow_html=True)
        with r4:
            sev = result["severity"]
            st.markdown(f"""
            <div class="metric-card" style="background: var(--bg-card); border: 1px solid var(--border-glow);">
                <div class="metric-icon">🛡️</div>
                <div style="margin: 12px 0 6px;">{severity_badge(sev)}</div>
                <div class="metric-label">Severity</div>
            </div>
            """, unsafe_allow_html=True)

        # ── Store in DB ──
        try:
            row_id = insert_vital(hr, o2, bp_s, bp_d,
                                  result["anomaly_score"], result["severity"])
            st.success(f"✅ Stored in database (record #{row_id})")
        except Exception as e:
            st.warning(f"Could not save to database: {e}")

        # ── Critical warning ──
        if result["severity"] == "HIGH":
            st.markdown("""
            <div class="glass-card" style="border-left: 4px solid #f85149; margin-top: 16px;">
                <div style="font-size: 1.2rem; font-weight: 700; color: #f85149;">
                    🚨 CRITICAL ALERT
                </div>
                <div style="color: #e6edf3; margin-top: 8px;">
                    This reading is classified as <strong>HIGH severity</strong>.
                    Immediate medical attention may be required.
                </div>
            </div>
            """, unsafe_allow_html=True)
        elif result["severity"] == "MEDIUM":
            st.warning("🟠 Moderate anomaly detected. Monitor patient closely.")


# ══════════════════════════════════════════════════
#  PAGE: PRESCRIPTION ANALYZER
# ══════════════════════════════════════════════════

elif page == "💊 Prescription Analyzer":
    st.markdown("""
    <div style="display:flex; align-items:center; gap:14px; margin-bottom: 20px;">
        <span style="font-size:2.2rem;">💊</span>
        <div>
            <div style="font-size:1.8rem; font-weight:700; color:#e6edf3;">Prescription Analyzer</div>
            <div style="font-size:0.9rem; color:#8b949e;">Upload an image or paste text to identify medicines & active salts</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📷 Image Upload (OCR)", "📝 Text Input"])

    with tab1:
        uploaded = st.file_uploader("Upload prescription image",
                                    type=["png", "jpg", "jpeg", "bmp", "tiff"])
        if uploaded:
            st.image(uploaded, caption="Uploaded Prescription", width=400)
            if st.button("🔍 Extract Medicines from Image"):
                with st.spinner("⏳ Processing image with OCR…"):
                    temp_dir = os.path.join(os.path.dirname(__file__), "..", "data")
                    os.makedirs(temp_dir, exist_ok=True)
                    temp_path = os.path.join(temp_dir, "temp_prescription.png")
                    with open(temp_path, "wb") as f:
                        f.write(uploaded.getbuffer())
                    try:
                        result = extract_medicines(temp_path)
                        st.markdown('<div class="section-header">📄 Extracted Text</div>',
                                    unsafe_allow_html=True)
                        st.code(result["raw_text"], language=None)
                        _render_medicines(result)
                    except Exception as e:
                        st.error(f"OCR Error: `{e}`")
                        st.info("💡 Make sure Tesseract OCR is installed on your system.")

    with tab2:
        text_input = st.text_area(
            "Paste prescription text",
            placeholder="e.g. Take Paracetamol 500mg twice daily. Amoxicillin 250mg thrice.",
            height=150,
        )
        if st.button("🔍 Extract Medicines from Text"):
            if text_input.strip():
                with st.spinner("⏳ Matching against medicine database…"):
                    result = extract_medicines_from_text(text_input)
                    _render_medicines(result)
            else:
                st.warning("Please enter some text first.")




# ══════════════════════════════════════════════════
#  PAGE: DRUG INTERACTIONS
# ══════════════════════════════════════════════════

elif page == "⚠️ Drug Interactions":
    st.markdown("""
    <div style="display:flex; align-items:center; gap:14px; margin-bottom: 20px;">
        <span style="font-size:2.2rem;">⚠️</span>
        <div>
            <div style="font-size:1.8rem; font-weight:700; color:#e6edf3;">Drug Interaction Checker</div>
            <div style="font-size:0.9rem; color:#8b949e;">
                Enter two or more medicines to check for known interactions
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    medicine_input = st.text_input(
        "Enter medicine names (comma separated)",
        placeholder="e.g. Aspirin, Warfarin, Metformin",
        label_visibility="collapsed",
    )

    st.markdown("""
    <div style="font-size:0.8rem; color:#8b949e; margin: -8px 0 12px;">
        💡 Enter at least 2 medicine names separated by commas
    </div>
    """, unsafe_allow_html=True)

    if st.button("🔍 Check Interactions", use_container_width=True):
        if medicine_input.strip():
            meds = [m.strip() for m in medicine_input.split(",") if m.strip()]
            if len(meds) < 2:
                st.warning("Please enter at least 2 medicines.")
            else:
                with st.spinner("⏳ Checking drug interaction database…"):
                    result = check_interactions(meds)

                st.markdown(f"""
                <div class="glass-card" style="margin-top: 12px;">
                    <div style="font-weight:600; color:#58a6ff;">Medicines Checked</div>
                    <div style="color:#e6edf3; margin-top:6px; font-size:1.05rem;">
                        {' • '.join(result['medicines_checked'])}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if result["interactions_found"]:
                    st.markdown('<div class="section-header">⚠️ Interactions Found</div>',
                                unsafe_allow_html=True)
                    for ix in result["interactions_found"]:
                        sev = ix["severity"].lower()
                        emoji = {"high": "🔴", "medium": "🟠", "low": "🟢"}.get(sev, "⚪")
                        st.markdown(f"""
                        <div class="interaction-card ic-{sev}">
                            <div style="font-weight:700; font-size:1rem;">
                                {emoji} {ix['drug_1']}  ↔  {ix['drug_2']}
                                <span style="float:right;">{severity_badge(ix['severity'])}</span>
                            </div>
                            <div style="color:#8b949e; margin-top:8px;">{ix['description']}</div>
                        </div>
                        """, unsafe_allow_html=True)

                    st.error("⚠ Interactions found! Consult your pharmacist or doctor before combining.")
                else:
                    st.markdown("""
                    <div class="glass-card" style="text-align:center; padding:30px;">
                        <div style="font-size:2rem;">✅</div>
                        <div style="font-weight:600; color:#3fb950; margin-top:8px;">
                            No known interactions found
                        </div>
                        <div style="color:#8b949e; margin-top:4px;">
                            However, always consult a pharmacist or doctor.
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("Please enter medicine names.")


# ══════════════════════════════════════════════════
#  PAGE: SYMPTOM GUIDANCE
# ══════════════════════════════════════════════════

elif page == "🩺 Symptom Guidance":
    st.markdown("""
    <div style="display:flex; align-items:center; gap:14px; margin-bottom: 20px;">
        <span style="font-size:2.2rem;">🩺</span>
        <div>
            <div style="font-size:1.8rem; font-weight:700; color:#e6edf3;">Symptom Guidance System</div>
            <div style="font-size:0.9rem; color:#8b949e;">
                Enter symptoms for AI-powered educational health guidance
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    symptom_input = st.text_input(
        "Enter symptoms (comma separated)",
        placeholder="e.g. headache, fever, fatigue, body ache",
        label_visibility="collapsed",
    )

    st.markdown("""
    <div style="font-size:0.8rem; color:#8b949e; margin: -8px 0 12px;">
        💡 Enter one or more symptoms separated by commas
    </div>
    """, unsafe_allow_html=True)

    if st.button("🔍 Get Guidance", use_container_width=True):
        if symptom_input.strip():
            symptoms = [s.strip() for s in symptom_input.split(",") if s.strip()]
            with st.spinner("⏳ Analyzing symptoms…"):
                result = get_symptom_guidance(symptoms)

            if result["matched_conditions"]:
                for cond in result["matched_conditions"]:
                    score = cond["match_score"]
                    score_color = "#3fb950" if score >= 50 else "#f0883e" if score >= 30 else "#8b949e"

                    st.markdown(f"""
                    <div class="condition-card">
                        <div class="condition-title">
                            🏷 {cond['condition']}
                            <span style="float:right; color:{score_color}; font-size:0.9rem;">
                                Match: {score}%
                            </span>
                        </div>
                    """, unsafe_allow_html=True)

                    # Causes
                    with st.expander(f"🔍 Possible Causes – {cond['condition']}", expanded=False):
                        for c in cond["possible_causes"]:
                            st.markdown(f"• {c}")

                    # Remedies
                    with st.expander(f"🌿 Home Remedies – {cond['condition']}", expanded=False):
                        for r in cond["home_remedies"]:
                            st.markdown(f"• {r}")

                    # Lifestyle
                    with st.expander(f"💡 Lifestyle Advice – {cond['condition']}", expanded=False):
                        for a in cond["lifestyle_advice"]:
                            st.markdown(f"• {a}")

                    # Warning signs
                    with st.expander(f"🚨 Warning Signs – {cond['condition']}", expanded=False):
                        for w in cond["warning_signs"]:
                            st.markdown(f"🔴 {w}")

                    st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.info("No matching conditions found. Try different symptom descriptions.")

            # Disclaimer
            st.markdown(f"""
            <div class="glass-card" style="border-left: 4px solid #f0883e; margin-top: 16px;">
                <div style="color:#f0883e; font-weight:600;">⚕ Important</div>
                <div style="color:#8b949e; margin-top:6px;">{result['disclaimer']}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("Please enter at least one symptom.")


# ══════════════════════════════════════════════════
#  PAGE: SIDE-EFFECT REPORTER
# ══════════════════════════════════════════════════

elif page == "📋 Side-Effect Reporter":
    st.markdown("""
    <div style="display:flex; align-items:center; gap:14px; margin-bottom: 20px;">
        <span style="font-size:2.2rem;">📋</span>
        <div>
            <div style="font-size:1.8rem; font-weight:700; color:#e6edf3;">Side-Effect Reporter</div>
            <div style="font-size:0.9rem; color:#8b949e;">
                Report medication side effects for AI-powered analysis
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.form("side_effect_form"):
        c1, c2 = st.columns(2)
        with c1:
            age = st.number_input("👤 Age", min_value=1, max_value=120, value=30)
            gender = st.selectbox("⚥ Gender", ["Male", "Female", "Other"])
        with c2:
            medicine = st.text_input("💊 Medicine Name", placeholder="e.g. Metformin")
            dosage = st.text_input("📏 Dosage", placeholder="e.g. 500mg twice daily")

        symptoms_text = st.text_area(
            "🩺 Symptoms experienced (comma separated)",
            placeholder="e.g. nausea, dizziness, stomach upset",
        )
        submitted = st.form_submit_button("📤 Submit Report", use_container_width=True)

    if submitted:
        if medicine.strip() and symptoms_text.strip():
            symptoms = [s.strip() for s in symptoms_text.split(",") if s.strip()]
            with st.spinner("⏳ Analyzing side effects…"):
                result = analyze_side_effects(age, gender, medicine, dosage, symptoms)

            # ── Analysis Card ──
            urgency_high = "HIGH" in result["urgency"]
            urgency_cls = "ic-high" if urgency_high else "ic-low"
            urgency_emoji = "🔴" if urgency_high else "🟢"

            st.markdown(f"""
            <div class="glass-card" style="margin-top: 12px;">
                <div class="section-header" style="margin-top:0;">🧠 AI Analysis</div>
                <div style="color:#e6edf3; line-height:1.7;">{result['analysis']}</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="interaction-card {urgency_cls}">
                <div style="font-weight:700;">{urgency_emoji} Urgency Assessment</div>
                <div style="color:#8b949e; margin-top:4px;">{result['urgency']}</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown('<div class="section-header">📋 Recommendations</div>', unsafe_allow_html=True)
            for i, rec in enumerate(result["recommendations"], 1):
                st.markdown(f"""
                <div class="glass-card" style="padding:14px 20px; display:flex; align-items:center; gap:12px;">
                    <span style="background:#58a6ff; color:#0e1117; border-radius:50%; width:28px; height:28px;
                                 display:inline-flex; align-items:center; justify-content:center;
                                 font-weight:700; font-size:0.8rem; flex-shrink:0;">{i}</span>
                    <span style="color:#e6edf3;">{rec}</span>
                </div>
                """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="glass-card" style="border-left: 4px solid #f0883e; margin-top: 16px;">
                <div style="color:#f0883e; font-weight:600;">⚕ Disclaimer</div>
                <div style="color:#8b949e; margin-top:6px;">{result['disclaimer']}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("Please fill in both the medicine name and symptoms.")


# ══════════════════════════════════════════════════
#  FOOTER
# ══════════════════════════════════════════════════

st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style="text-align:center; font-size:0.72rem; color:#8b949e; padding: 10px 0;">
    <strong>MedSafe AI</strong> v2.0<br>
    Academic AI/ML Project<br>
    Python • Streamlit • Flask • Kafka
</div>
""", unsafe_allow_html=True)
