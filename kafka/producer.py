"""
MedSafe AI – Kafka Producer (Vitals Simulator)
================================================
Simulates real-time patient vitals and publishes them to a Kafka topic.

Normal ranges (used for simulation):
  • Heart rate : 60–100 bpm
  • Oxygen     : 95–100 %
  • BP systolic: 110–130 mmHg
  • BP diastol : 70–85  mmHg

Every ~10th reading injects an anomaly to test the detection pipeline.

Usage:
    python kafka/producer.py
"""

import json
import time
import random
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config

try:
    from kafka import KafkaProducer
    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False


# ──────────── Vitals Generation ────────────

def generate_normal_vitals():
    """Generate a single set of normal patient vitals."""
    return {
        "heart_rate":   round(random.gauss(75, 5), 1),
        "oxygen":       round(random.gauss(97.5, 0.8), 1),
        "bp_systolic":  round(random.gauss(120, 5), 1),
        "bp_diastolic": round(random.gauss(78, 4), 1),
        "timestamp":    datetime.now().isoformat(),
    }


def generate_anomalous_vitals():
    """Generate vitals that should trigger an anomaly alert."""
    anomaly_type = random.choice(["tachycardia", "hypoxia", "hypertension"])

    vitals = generate_normal_vitals()

    if anomaly_type == "tachycardia":
        vitals["heart_rate"] = round(random.uniform(140, 180), 1)
    elif anomaly_type == "hypoxia":
        vitals["oxygen"] = round(random.uniform(82, 89), 1)
    elif anomaly_type == "hypertension":
        vitals["bp_systolic"] = round(random.uniform(170, 210), 1)
        vitals["bp_diastolic"] = round(random.uniform(100, 130), 1)

    return vitals


def generate_vitals(inject_anomaly=False):
    """Return normal or anomalous vitals based on the flag."""
    if inject_anomaly:
        return generate_anomalous_vitals()
    return generate_normal_vitals()


# ──────────── Kafka Producer Loop ────────────

def run_producer():
    """Main producer loop – publishes vitals to Kafka every 2 seconds."""
    if not KAFKA_AVAILABLE:
        print("[PRODUCER] kafka-python not installed. Running in CONSOLE-ONLY mode.")
        _run_console_mode()
        return

    try:
        producer = KafkaProducer(
            bootstrap_servers=config.KAFKA_BROKER,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
        print(f"[PRODUCER] Connected to Kafka at {config.KAFKA_BROKER}")
    except Exception as e:
        print(f"[PRODUCER] Cannot connect to Kafka ({e}). Running in CONSOLE-ONLY mode.")
        _run_console_mode()
        return

    counter = 0
    print(f"[PRODUCER] Publishing to topic '{config.KAFKA_TOPIC}' every 2 seconds…")

    try:
        while True:
            counter += 1
            # Inject anomaly roughly every 10th reading
            inject = (counter % 10 == 0)
            vitals = generate_vitals(inject_anomaly=inject)

            producer.send(config.KAFKA_TOPIC, vitals)
            label = "⚠ ANOMALY" if inject else "  NORMAL "
            print(f"[PRODUCER] {label} | HR={vitals['heart_rate']} "
                  f"O2={vitals['oxygen']} BP={vitals['bp_systolic']}/{vitals['bp_diastolic']}")

            time.sleep(2)
    except KeyboardInterrupt:
        print("\n[PRODUCER] Stopped.")
    finally:
        producer.close()


def _run_console_mode():
    """Fallback: print vitals to console without Kafka."""
    counter = 0
    try:
        while True:
            counter += 1
            inject = (counter % 10 == 0)
            vitals = generate_vitals(inject_anomaly=inject)
            label = "⚠ ANOMALY" if inject else "  NORMAL "
            print(f"[CONSOLE] {label} | {json.dumps(vitals)}")
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n[CONSOLE] Stopped.")


# ──────────── Entry Point ────────────

if __name__ == "__main__":
    run_producer()
