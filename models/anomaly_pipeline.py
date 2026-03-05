"""
MedSafe AI – Anomaly Detection Pipeline
=========================================
Combines the Isolation Forest and Autoencoder models into a single
entry point. Returns a composite anomaly score and severity label.

Severity logic:
    score < 0.3  → LOW
    0.3 ≤ score < 0.7 → MEDIUM
    score ≥ 0.7 → HIGH
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config

from models.isolation_forest import VitalsIsolationForest
from models.autoencoder import VitalsAutoencoder

# ── Lazy-initialise singletons so models are loaded once ──
_if_model = None
_ae_model = None


def _get_models():
    """Return cached model instances (created on first call)."""
    global _if_model, _ae_model
    if _if_model is None:
        print("[PIPELINE] Loading Isolation Forest …")
        _if_model = VitalsIsolationForest()
    if _ae_model is None:
        print("[PIPELINE] Loading Autoencoder …")
        _ae_model = VitalsAutoencoder()
    return _if_model, _ae_model


def classify_severity(score):
    """Map anomaly score to severity label."""
    if score < config.THRESHOLD_LOW:
        return "LOW"
    elif score < config.THRESHOLD_HIGH:
        return "MEDIUM"
    else:
        return "HIGH"


def analyze_vitals(heart_rate, oxygen, bp_systolic, bp_diastolic):
    """
    Run both models and return a combined result dict.

    Returns:
        {
            "anomaly_score":    float,   # 0-1 composite
            "if_score":         float,   # Isolation Forest score
            "ae_score":         float,   # Autoencoder score
            "severity":         str,     # LOW / MEDIUM / HIGH
        }
    """
    if_model, ae_model = _get_models()

    if_score = if_model.predict(heart_rate, oxygen, bp_systolic, bp_diastolic)
    ae_score = ae_model.predict(heart_rate, oxygen, bp_systolic, bp_diastolic)

    # Weighted average: give equal weight to both models
    composite = round((if_score + ae_score) / 2, 4)
    severity = classify_severity(composite)

    return {
        "anomaly_score": composite,
        "if_score": if_score,
        "ae_score": ae_score,
        "severity": severity,
    }


# ─────── Quick Test ───────

if __name__ == "__main__":
    print("=== Normal Vitals ===")
    print(analyze_vitals(72, 98, 118, 76))

    print("\n=== Anomalous Vitals (Tachycardia + Hypoxia) ===")
    print(analyze_vitals(165, 85, 200, 120))

    print("\n=== Borderline Vitals ===")
    print(analyze_vitals(100, 94, 140, 90))
