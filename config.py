"""
MedSafe AI – Centralized Configuration
=======================================
All configurable settings for the project (database, Kafka, email, etc.).
Uses environment variables with sensible defaults for local development.
"""

import os

# ─────────────────────────── PostgreSQL ───────────────────────────
DB_HOST = os.getenv("MEDSAFE_DB_HOST", "localhost")
DB_PORT = os.getenv("MEDSAFE_DB_PORT", "5432")
DB_NAME = os.getenv("MEDSAFE_DB_NAME", "medsafe_ai")
DB_USER = os.getenv("MEDSAFE_DB_USER", "postgres")
DB_PASSWORD = os.getenv("MEDSAFE_DB_PASSWORD", "postgres")

# ──────────────────────────── Kafka ────────────────────────────
KAFKA_BROKER = os.getenv("MEDSAFE_KAFKA_BROKER", "localhost:9092")
KAFKA_TOPIC = os.getenv("MEDSAFE_KAFKA_TOPIC", "patient_vitals")

# ──────────────────────── Email Alerts ─────────────────────────
SMTP_SERVER = os.getenv("MEDSAFE_SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("MEDSAFE_SMTP_PORT", "587"))
EMAIL_SENDER = os.getenv("MEDSAFE_EMAIL_SENDER", "")
EMAIL_PASSWORD = os.getenv("MEDSAFE_EMAIL_PASSWORD", "")
EMAIL_RECEIVER = os.getenv("MEDSAFE_EMAIL_RECEIVER", "")

# ──────────────────────── Flask API ────────────────────────────
API_HOST = os.getenv("MEDSAFE_API_HOST", "0.0.0.0")
# Respect Render's PORT env var if it exists, otherwise use config
API_PORT = int(os.getenv("PORT", os.getenv("MEDSAFE_API_PORT", "5000")))

# ─────────────────── Anomaly Thresholds ────────────────────────
# Severity classification based on anomaly score (0-1 scale)
THRESHOLD_LOW = 0.3       # Below this → LOW severity
THRESHOLD_HIGH = 0.7      # Above this → HIGH severity
# Between LOW and HIGH → MEDIUM severity

# ──────────────── Data / Model Paths ───────────────────────────
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
MEDICINE_DB_PATH = os.path.join(DATA_DIR, "sample_medicine_database.csv")
DRUG_INTERACTIONS_PATH = os.path.join(DATA_DIR, "drug_interactions.csv")
SYMPTOM_DB_PATH = os.path.join(DATA_DIR, "symptom_database.json")
