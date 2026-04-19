<div align="center">
  <img src="https://img.shields.io/badge/Status-Complete-success.svg?style=for-the-badge" alt="Status" />
  <img src="https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" alt="React" />
  <img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask" />
  <img src="https://img.shields.io/badge/Kafka-231F20?style=for-the-badge&logo=apachekafka&logoColor=white" alt="Kafka" />
  <br/>
  
  <h1>🏥 MedSafe AI</h1>
  <p><b>An AI-driven Medical Safety Assistant designed for real-time patient monitoring, prescription analysis, and intelligent clinical alerts.</b></p>
  
  <p>
    > <b>Academic AI/ML Project</b> — Educational purposes only. Not a diagnostic tool.
  </p>
</div>

---

## 🌟 Features

MedSafe AI provides a comprehensive suite of healthcare safety features:
- **🫀 Real-Time Vitals Monitoring:** Streams patient telemetry data via Kafka.
- **🧠 Anomaly Detection:** Ensemble ML models (Isolation Forest + Autoencoder) monitor vitals continuously.
- **🚥 Intelligent Triaging:** Classifies anomaly severity into `LOW`, `MEDIUM`, or `HIGH` risk tiers.
- **✉️ Critical Alerts:** Automatically triggers SMTP email alerts to staff for severe anomalies.
- **📄 Prescription OCR Analyzer:** Extracts medicines directly from uploaded prescription images using Tesseract OCR and fuzzy matching.
- **💊 Drug Interaction Checker:** Prevents adverse events by flagging contraindications between prescribed medications.
- **🩺 Symptom Guidance Engine:** Maps patient symptoms to possible conditions and provides simulated clinical advice.
- **📋 Side-Effect Reporter:** Uses AI intelligence to process and categorize self-reported adverse drug reactions.

---
## 🎥 Project Demo

Watch the working demonstration of MedSafe AI:

https://drive.google.com/file/d/1yrFuXSmpwxVyO8dqQ6BscWw7h-FJOE6f/view

---

## 📄 Project Documentation

Full Project Report:

docs/MedSafe_AI_Project_Report.pdf

## 🏗 System Architecture

The ecosystem relies on an asynchronous event-driven backend paired with a dynamic React frontend.

```text
┌─────────────────────────────────────────────────────────────────┐
│                        REACT FRONTEND UI                        │
│  Vitals Monitor │ Prescription │ Drug Check │ Symptoms │ Side FX│
└────────┬────────────────────────────────────────────────────────-┘
         │ REST API (HTTP)
┌────────▼────────┐     ┌──────────────┐     ┌──────────────────┐
│   FLASK API     │────▶│  PostgreSQL  │◀────│  KAFKA CONSUMER  │
│  /latest_vitals │     │ patient_vitals│     │  anomaly_pipeline│
│  /history       │     └──────────────┘     │  email_alert     │
│  /high_alerts   │                          └────────▲─────────┘
│  /check_inter.  │                                   │ Kafka
│  /symptom_guide │                          ┌────────┴─────────┐
│  /side_effect   │                          │  KAFKA PRODUCER  │
│  /analyze_presc │                          │  (vitals simulator)│
└─────────────────┘                          └──────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                        ML MODELS                                │
│  Isolation Forest  │  Autoencoder  │  Anomaly Pipeline          │
└─────────────────────────────────────────────────────────────────┘
```

## 📁 Folder Structure

```text
MedSafe-AI/
├── api/                   # Flask REST API server & endpoints
├── dashboard/             # (Deprecated) Old Streamlit UI scripts
├── data/                  # CSV datasets (Medicines, Interactions, Symptoms)
├── database/              # SQLite/PostgreSQL schemas and CRUD operations
├── drug_checker/          # Fuzzy-matching drug interaction logic
├── kafka/                 # Kafka producer/consumer streaming logic
├── medsafe-insight-main/  # React + Tailwind Frontend (MedSafe AI UI)
├── models/                # ML Models (Isolation Forest, Autoencoder)
├── ocr/                   # Tesseract optical character recognition for prescriptions
├── symptom_engine/        # Symptom-to-condition mapping & advice simulation
├── config.py              # Centralized environment configurations
├── run_project.py         # Unified boot script for all services
├── simulator.py           # Standalone vital signs simulator & ML trigger
└── requirements.txt       # Python backend dependencies
```

---

## 🚀 Quick Start

To make testing and deployment trivial, the entire application (Backend API, Data Simulator, Kafka consumers, and the React Frontend) can be launched simultaneously with a single command.

### 1. Clone & Install Dependencies
First, install the Python backend requirements:
```bash
git clone https://github.com/your-username/MedSafe-AI.git
cd MedSafe-AI

# Create virtual environment (optional but recommended)
python -m venv venv
# Windows: venv\\Scripts\\activate | Mac/Linux: source venv/bin/activate

# Install Python requirements
pip install -r requirements.txt
```

Next, install the Node.js frontend dependencies:
```bash
cd medsafe-insight-main
npm install
cd ..
```

### 2. Launch the Application
Start the entire stack automatically from the project root:
```bash
python run_project.py
```
> The script will automatically spin up the Flask API, start generating vitals telemetry, and open the React dashboard in your browser (`http://localhost:8080`).

---

## 🛠 Advanced Setup (Optional)

The application gracefully degrades to entirely local, single-node execution. However, if you wish to run the full distributed architecture, configure the external services below.

### Setup PostgreSQL Database
By default, MedSafe AI falls back to SQLite. If you want to use PostgreSQL:
```bash
psql -U postgres -c "CREATE DATABASE medsafe_ai;"
psql -U postgres -d medsafe_ai -f database/schema.sql
```

### Setup Apache Kafka Streaming
By default, the `simulator.py` handles direct DB injection. To test the async streaming architecture:
1. Start Zookeeper (`bin/zookeeper-server-start.sh`)
2. Start Kafka Broker (`bin/kafka-server-start.sh`)
3. Open `run_project.py` and ensure the Kafka Producer and Consumer are enabled.

### Setup Email Alerts
For `HIGH` severity anomalies, MedSafe AI can trigger emails. Set the following environment variables:
```bash
export MEDSAFE_EMAIL_SENDER="your_email@gmail.com"
export MEDSAFE_EMAIL_PASSWORD="your_app_password"
export MEDSAFE_EMAIL_RECEIVER="doctor@hospital.com"
```

---

## 🧪 REST API Reference
If you wish to test the backend directly, the Flask API exposes the following endpoints:

| Endpoint | Method | Payload | Purpose |
|----------|--------|---------|---------|
| `/latest_vitals` | `GET` | None | Poll the 10 most recent vitals records |
| `/history` | `GET` | Params: `limit`, `offset` | Paginated historical lookup |
| `/high_alerts` | `GET` | None | Returns severe anomalies |
| `/analyze_prescription` | `POST` | `{"text": "..."}` or Image File | Run OCR and extract medicines |
| `/check_interactions` | `POST` | `{"medicines": ["Aspirin", "Warfarin"]}` | Detect drug-drug contraindications |
| `/symptom_guidance` | `POST` | `{"symptoms": ["headache", "fever"]}` | AI condition mapping |
| `/side_effect_report` | `POST` | JSON demographics & symptoms | Classify drug adverse events |

---

## 🧠 Machine Learning Engine
MedSafe AI utilizes a hybrid ensemble approach for anomaly detection on physiological data:

| Model | Technique | Output Range | Use Case |
|-------|-----------|--------------|----------|
| **Isolation Forest** | Unsupervised Ensemble Tree (`scikit-learn`) | `0.0` - `1.0` | Ideal for identifying severe outliers in tabular vitals (Heart Rate / BP spikes) |
| **Autoencoder** | Deep Neural Network Reconstruction (`Keras/TensorFlow`) | `0.0` - `1.0` | Ideal for detecting subtle, non-linear anomalies in continuous oxygen decay |

**Scoring Thresholds:**
- `score < 0.30` → 🟢 **LOW** 
- `0.30 ≤ score < 0.70` → 🟠 **MEDIUM** 
- `score ≥ 0.70` → 🔴 **HIGH** (Triggers email alert)

---

## ⚠️ Academic Disclaimer
This software is an intricate **academic demonstration project** highlighting modern software engineering, data streaming, and applied machine learning practices. 

It generates simulated data and provides placeholder medical guidance. **It is not FDA approved, makes no diagnostic guarantees, and should never be used in a real clinical environment.**

---
<div align="center">
  <i>Developed as an advanced academic portfolio project.</i>
</div>
