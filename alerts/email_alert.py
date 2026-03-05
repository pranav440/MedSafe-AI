"""
MedSafe AI – Email Alert System
=================================
Sends automated email alerts when patient vitals reach HIGH severity.
Falls back to console logging when SMTP credentials are not configured.

Configuration is read from config.py / environment variables:
    MEDSAFE_SMTP_SERVER, MEDSAFE_SMTP_PORT,
    MEDSAFE_EMAIL_SENDER, MEDSAFE_EMAIL_PASSWORD, MEDSAFE_EMAIL_RECEIVER
"""

import smtplib
import sys
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config


def send_alert(heart_rate, oxygen, bp_systolic, bp_diastolic,
               anomaly_score, timestamp):
    """
    Send a HIGH-severity email alert with patient vitals.

    If SMTP credentials are not configured, prints the alert to console
    instead (useful for local development/testing).
    """
    subject = "🚨 MedSafe AI – HIGH Severity Alert"
    body = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  MedSafe AI – CRITICAL ALERT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Severity   : HIGH
Timestamp  : {timestamp}

── Patient Vitals ──
Heart Rate : {heart_rate} bpm
Oxygen     : {oxygen} %
BP         : {bp_systolic}/{bp_diastolic} mmHg

── Analysis ──
Anomaly Score : {anomaly_score}

⚠ Immediate medical attention may be required.

This is an automated alert from MedSafe AI.
For educational purposes only.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

    # ── Check if SMTP is configured ──
    if not config.EMAIL_SENDER or not config.EMAIL_PASSWORD:
        print("[ALERT] SMTP not configured – printing alert to console:")
        print(body)
        return False

    # ── Build email ──
    msg = MIMEMultipart()
    msg["From"] = config.EMAIL_SENDER
    msg["To"] = config.EMAIL_RECEIVER
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    # ── Send via SMTP ──
    try:
        server = smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT)
        server.starttls()
        server.login(config.EMAIL_SENDER, config.EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"[ALERT] Email sent to {config.EMAIL_RECEIVER}")
        return True
    except Exception as e:
        print(f"[ALERT] Failed to send email: {e}")
        print("[ALERT] Falling back to console alert:")
        print(body)
        return False


# ─────── Quick Test ───────

if __name__ == "__main__":
    send_alert(
        heart_rate=170,
        oxygen=85,
        bp_systolic=200,
        bp_diastolic=120,
        anomaly_score=0.92,
        timestamp="2026-03-05T10:30:00",
    )
