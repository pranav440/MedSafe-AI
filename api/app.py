"""
MedSafe AI – Flask REST API
==============================
Provides HTTP endpoints for accessing patient vitals, history,
alerts, and healthcare AI features.

Endpoints:
    GET  /latest_vitals       → Last 10 vitals records
    GET  /history              → Paginated vitals history
    GET  /high_alerts          → Records with severity == HIGH
    POST /analyze_prescription → OCR prescription analysis
    POST /check_interactions   → Drug interaction check
    POST /symptom_guidance     → Symptom-based guidance
    POST /side_effect_report   → Side-effect analysis

Usage:
    python api/app.py
"""

import sys
import sys
import os
import json
import tempfile
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config

from flask import Flask, request, jsonify, Response

from database.db import (
    init_db, get_latest_vitals, get_history, get_high_alerts, insert_vital
)
from models.anomaly_pipeline import analyze_vitals
from ocr.prescription_reader import extract_medicines, extract_medicines_from_text
from drug_checker.interaction_checker import check_interactions
from symptom_engine.symptom_solver import get_symptom_guidance, analyze_side_effects

print("[API] Starting Flask app")
# Use absolute path for static folder to ensure gunicorn finds it
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
static_folder = os.path.join(BASE_DIR, "static")
app = Flask(__name__, static_folder=static_folder, static_url_path="/")

@app.route("/")
def index():
    """Serve the React frontend."""
    return app.send_static_file("index.html")

@app.errorhandler(404)
def not_found(e):
    """Fallback for React Router."""
    return app.send_static_file("index.html")


# ──────────── CORS Support ────────────

@app.route("/<path:path>", methods=["OPTIONS"])
@app.route("/", methods=["OPTIONS"])
def cors_preflight(path=""):
    """Handle CORS preflight requests (OPTIONS)."""
    resp = app.make_default_options_response()
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return resp


@app.after_request
def add_cors_headers(response):
    """Allow cross-origin requests from the frontend."""
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


# ──────────── JSON Serialisation Helper ────────────

def _serialise(obj):
    """Make datetime objects JSON-serialisable."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


# ══════════════════════════════════════════════════
#  VITALS ENDPOINTS
# ══════════════════════════════════════════════════

@app.route("/latest_vitals", methods=["GET"])
def latest_vitals():
    """Return the most recent 10 vitals records."""
    try:
        data = get_latest_vitals(limit=10)
        return Response(json.dumps({"status": "ok", "data": data}, default=_serialise),
                        status=200, mimetype="application/json")
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/history", methods=["GET"])
def history():
    """Return paginated vitals history.

    Query params:
        limit  (int, default 100)
        offset (int, default 0)
    """
    try:
        limit = int(request.args.get("limit", 100))
        offset = int(request.args.get("offset", 0))
        data = get_history(limit=limit, offset=offset)
        return Response(json.dumps({"status": "ok", "count": len(data), "data": data},
                          default=_serialise), status=200, mimetype="application/json")
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/high_alerts", methods=["GET"])
def high_alerts():
    """Return recent HIGH-severity records."""
    try:
        data = get_high_alerts(limit=50)
        return Response(json.dumps({"status": "ok", "count": len(data), "data": data},
                          default=_serialise), status=200, mimetype="application/json")
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ══════════════════════════════════════════════════
#  ANOMALY ANALYSIS (manual trigger)
# ══════════════════════════════════════════════════

@app.route("/analyze_vitals", methods=["POST"])
def api_analyze_vitals():
    """
    Manually analyse a set of vitals.

    JSON body:
        {"heart_rate": 72, "oxygen": 98, "bp_systolic": 120, "bp_diastolic": 80}
    """
    try:
        body = request.get_json()
        result = analyze_vitals(
            heart_rate=float(body["heart_rate"]),
            oxygen=float(body["oxygen"]),
            bp_systolic=float(body["bp_systolic"]),
            bp_diastolic=float(body["bp_diastolic"]),
        )

        # Also store in DB
        insert_vital(
            heart_rate=body["heart_rate"],
            oxygen=body["oxygen"],
            bp_systolic=body["bp_systolic"],
            bp_diastolic=body["bp_diastolic"],
            anomaly_score=result["anomaly_score"],
            severity=result["severity"],
        )

        return jsonify({"status": "ok", **result}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


# ══════════════════════════════════════════════════
#  PRESCRIPTION / OCR
# ══════════════════════════════════════════════════

@app.route("/analyze_prescription", methods=["POST"])
def api_analyze_prescription():
    """
    Analyse an uploaded prescription image or raw text.

    Form data:
        file  → image file (optional)
        text  → raw text (if no file)
    """
    try:
        if "file" in request.files:
            file = request.files["file"]
            temp_path = os.path.join(tempfile.gettempdir(), file.filename)
            file.save(temp_path)
            result = extract_medicines(temp_path)
        elif request.is_json and "text" in request.get_json():
            text = request.get_json()["text"]
            result = extract_medicines_from_text(text)
        elif "text" in request.form:
            result = extract_medicines_from_text(request.form["text"])
        else:
            return jsonify({"status": "error",
                            "message": "Provide 'file' or 'text'"}), 400

        return jsonify({"status": "ok", **result}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


# ══════════════════════════════════════════════════
#  DRUG INTERACTIONS
# ══════════════════════════════════════════════════

@app.route("/check_interactions", methods=["POST"])
def api_check_interactions():
    """
    Check for drug–drug interactions.

    JSON body:
        {"medicines": ["Aspirin", "Warfarin", "Metformin"]}
    """
    try:
        body = request.get_json()
        medicines = body.get("medicines", [])
        if len(medicines) < 2:
            return jsonify({"status": "error",
                            "message": "Provide at least 2 medicines"}), 400
        result = check_interactions(medicines)
        return jsonify({"status": "ok", **result}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


# ══════════════════════════════════════════════════
#  SYMPTOM GUIDANCE
# ══════════════════════════════════════════════════

@app.route("/symptom_guidance", methods=["POST"])
def api_symptom_guidance():
    """
    Get symptom-based health guidance.

    JSON body:
        {"symptoms": ["headache", "fever", "fatigue"]}
    """
    try:
        body = request.get_json()
        symptoms = body.get("symptoms", [])
        if not symptoms:
            return jsonify({"status": "error",
                            "message": "Provide at least 1 symptom"}), 400
        result = get_symptom_guidance(symptoms)
        return jsonify({"status": "ok", **result}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


# ══════════════════════════════════════════════════
#  SIDE-EFFECT REPORT
# ══════════════════════════════════════════════════

@app.route("/side_effect_report", methods=["POST"])
def api_side_effect_report():
    """
    Report side effects and get AI analysis.

    JSON body:
        {
            "age": 35,
            "gender": "Male",
            "medicine": "Metformin",
            "dosage": "500mg twice daily",
            "symptoms": ["nausea", "dizziness"]
        }
    """
    try:
        body = request.get_json()
        result = analyze_side_effects(
            age=body["age"],
            gender=body["gender"],
            medicine=body["medicine"],
            dosage=body["dosage"],
            symptoms=body["symptoms"],
        )
        return jsonify({"status": "ok", **result}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


# ══════════════════════════════════════════════════
#  HEALTH CHECK
# ══════════════════════════════════════════════════

@app.route("/", methods=["GET"])
def health():
    """Simple health check."""
    return jsonify({
        "service": "MedSafe AI API",
        "status": "running",
        "endpoints": [
            "GET  /latest_vitals",
            "GET  /history?limit=100&offset=0",
            "GET  /high_alerts",
            "POST /analyze_vitals",
            "POST /analyze_prescription",
            "POST /check_interactions",
            "POST /symptom_guidance",
            "POST /side_effect_report",
        ],
    })


# ──────────── Initialisation ────────────
print("[API] Initialising database …")
init_db()

# ──────────── Entry Point ────────────
if __name__ == "__main__":
    print(f"[API] Starting Flask on {config.API_HOST}:{config.API_PORT}")
    app.run(host=config.API_HOST, port=config.API_PORT, debug=True)
