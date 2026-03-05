import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
import config
import importlib.util
from database.db import init_db, insert_vital
from models.anomaly_pipeline import analyze_vitals

# Load local generator properly avoiding installed 'kafka' namespace clash
spec = importlib.util.spec_from_file_location("local_producer", os.path.join(os.path.dirname(__file__), "kafka", "producer.py"))
local_producer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(local_producer)
generate_vitals = local_producer.generate_vitals

def run_simulator():
    print("[Simulator] Starting standalone fallback vitals simulator...")
    init_db()
    
    counter = 0
    while True:
        try:
            counter += 1
            # Inject anomaly roughly every 10th reading
            inject = (counter % 10 == 0)
            vitals = generate_vitals(inject_anomaly=inject)
            
            # Use real pipeline
            result = analyze_vitals(
                heart_rate=vitals["heart_rate"],
                oxygen=vitals["oxygen"],
                bp_systolic=vitals["bp_systolic"],
                bp_diastolic=vitals["bp_diastolic"],
            )
            
            insert_vital(
                heart_rate=vitals["heart_rate"],
                oxygen=vitals["oxygen"],
                bp_systolic=vitals["bp_systolic"],
                bp_diastolic=vitals["bp_diastolic"],
                anomaly_score=result["anomaly_score"],
                severity=result["severity"],
            )
            print(f"[Simulator] Inserted vitals (Severity: {result['severity']})")
        except Exception as e:
            print(f"[Simulator] Error: {e}")
            
        time.sleep(5)

if __name__ == "__main__":
    run_simulator()
