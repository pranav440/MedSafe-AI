#!/bin/bash
# MedSafe AI – Cloud Startup Script

echo "[System] Starting Vitals Simulator..."
python simulator.py &

echo "[System] Starting Flask API with Gunicorn on port $PORT..."
# Bind to 0.0.0.0 and the port provided by Railway
gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 api.app:app
