"""
MedSafe AI – Shared Utility Functions
=======================================
Common helpers used across multiple modules: severity classification,
timestamp formatting, data validation, and formatting utilities.
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config


# ──────────── Severity Classification ────────────

def classify_severity(score):
    """
    Map an anomaly score (0-1) to a severity label.

    Returns:
        'LOW'    if score < THRESHOLD_LOW   (default 0.3)
        'MEDIUM' if score < THRESHOLD_HIGH  (default 0.7)
        'HIGH'   if score >= THRESHOLD_HIGH
    """
    if score < config.THRESHOLD_LOW:
        return "LOW"
    elif score < config.THRESHOLD_HIGH:
        return "MEDIUM"
    else:
        return "HIGH"


# ──────────── Timestamp Helpers ────────────

def now_iso():
    """Return current timestamp in ISO 8601 format."""
    return datetime.now().isoformat()


def format_timestamp(ts):
    """
    Format a timestamp for display.
    Accepts datetime object or ISO string.
    """
    if isinstance(ts, str):
        ts = datetime.fromisoformat(ts)
    return ts.strftime("%Y-%m-%d %H:%M:%S")


# ──────────── Data Validation ────────────

def validate_vitals(heart_rate, oxygen, bp_systolic, bp_diastolic):
    """
    Validate that vital sign values are within physically plausible ranges.

    Returns:
        (is_valid: bool, error_message: str or None)
    """
    errors = []
    if not (20 <= heart_rate <= 300):
        errors.append(f"Heart rate {heart_rate} out of range (20-300 bpm)")
    if not (50 <= oxygen <= 100):
        errors.append(f"Oxygen {oxygen} out of range (50-100%)")
    if not (50 <= bp_systolic <= 300):
        errors.append(f"BP systolic {bp_systolic} out of range (50-300 mmHg)")
    if not (20 <= bp_diastolic <= 200):
        errors.append(f"BP diastolic {bp_diastolic} out of range (20-200 mmHg)")

    if errors:
        return False, "; ".join(errors)
    return True, None


# ──────────── Formatting ────────────

def vitals_to_dict(heart_rate, oxygen, bp_systolic, bp_diastolic,
                   anomaly_score=None, severity=None, timestamp=None):
    """Build a standardised vitals dictionary."""
    d = {
        "heart_rate":   heart_rate,
        "oxygen":       oxygen,
        "bp_systolic":  bp_systolic,
        "bp_diastolic": bp_diastolic,
        "timestamp":    timestamp or now_iso(),
    }
    if anomaly_score is not None:
        d["anomaly_score"] = anomaly_score
    if severity is not None:
        d["severity"] = severity
    return d


def severity_emoji(severity):
    """Return an emoji indicator for a severity level."""
    return {"LOW": "🟢", "MEDIUM": "🟠", "HIGH": "🔴"}.get(severity, "⚪")


# ─────── Quick Test ───────

if __name__ == "__main__":
    print("Severity  0.1 →", classify_severity(0.1))
    print("Severity  0.5 →", classify_severity(0.5))
    print("Severity  0.9 →", classify_severity(0.9))
    print("Now ISO       →", now_iso())
    print("Validate OK   →", validate_vitals(72, 98, 120, 80))
    print("Validate BAD  →", validate_vitals(5, 110, 120, 80))
