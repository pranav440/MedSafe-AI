"""
MedSafe AI – Kafka Consumer
=============================
Consumes patient vitals from the Kafka topic, runs them through
the anomaly detection pipeline, stores results in PostgreSQL,
and triggers email alerts for HIGH-severity events.

Usage:
    python kafka/consumer.py
"""

import json
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config

try:
    from kafka import KafkaConsumer
    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False

from models.anomaly_pipeline import analyze_vitals
from database.db import insert_vital, init_db
from alerts.email_alert import send_alert


def run_consumer():
    """Main consumer loop – reads vitals, analyses, stores, alerts."""
    # Make sure the DB table exists
    init_db()

    if not KAFKA_AVAILABLE:
        print("[CONSUMER] kafka-python not installed. Cannot consume. "
              "Install it or use the API/dashboard in standalone mode.")
        return

    try:
        consumer = KafkaConsumer(
            config.KAFKA_TOPIC,
            bootstrap_servers=config.KAFKA_BROKER,
            auto_offset_reset="latest",
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        )
        print(f"[CONSUMER] Listening on topic '{config.KAFKA_TOPIC}' …")
    except Exception as e:
        print(f"[CONSUMER] Cannot connect to Kafka: {e}")
        return

    try:
        for message in consumer:
            vitals = message.value
            print(f"\n[CONSUMER] Received: {vitals}")

            # ── Run anomaly detection ──
            result = analyze_vitals(
                heart_rate=vitals["heart_rate"],
                oxygen=vitals["oxygen"],
                bp_systolic=vitals["bp_systolic"],
                bp_diastolic=vitals["bp_diastolic"],
            )

            anomaly_score = result["anomaly_score"]
            severity = result["severity"]

            print(f"[CONSUMER] Anomaly Score: {anomaly_score:.3f} | Severity: {severity}")

            # ── Store in database ──
            row_id = insert_vital(
                heart_rate=vitals["heart_rate"],
                oxygen=vitals["oxygen"],
                bp_systolic=vitals["bp_systolic"],
                bp_diastolic=vitals["bp_diastolic"],
                anomaly_score=anomaly_score,
                severity=severity,
            )
            print(f"[CONSUMER] Stored in DB (id={row_id})")

            # ── Email alert for HIGH severity ──
            if severity == "HIGH":
                print("[CONSUMER] 🚨 HIGH SEVERITY – Sending alert…")
                send_alert(
                    heart_rate=vitals["heart_rate"],
                    oxygen=vitals["oxygen"],
                    bp_systolic=vitals["bp_systolic"],
                    bp_diastolic=vitals["bp_diastolic"],
                    anomaly_score=anomaly_score,
                    timestamp=vitals.get("timestamp", datetime.now().isoformat()),
                )

    except KeyboardInterrupt:
        print("\n[CONSUMER] Stopped.")
    finally:
        consumer.close()


if __name__ == "__main__":
    run_consumer()
