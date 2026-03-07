"""
MedSafe AI – Database Helper Module
=====================================
Provides database connection management and CRUD operations
for the patient_vitals table.

Supports two backends:
  • SQLite   (default – zero setup, runs locally)
  • PostgreSQL (set MEDSAFE_DB_BACKEND=postgres in env)
"""

import os
import sys
import sqlite3
from datetime import datetime

# ── Add project root to path so we can import config ──
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config

# ── Determine backend ──
DB_BACKEND = os.getenv("MEDSAFE_DB_BACKEND", "sqlite")  # "sqlite" or "postgres"

SQLITE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "medsafe.db")


# ────────────────────── Connection ──────────────────────

def get_connection():
    """Return a new database connection."""
    if DB_BACKEND == "postgres":
        import psycopg2
        return psycopg2.connect(
            host=config.DB_HOST,
            port=config.DB_PORT,
            dbname=config.DB_NAME,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
        )
    else:
        # Enable timeout and multi-process support for SQLite
        conn = sqlite3.connect(SQLITE_PATH, timeout=30.0, check_same_thread=False)
        conn.row_factory = sqlite3.Row  # dict-like access
        return conn


# ───────────────── Schema Initialisation ─────────────────

def init_db():
    """Create the patient_vitals table if it does not exist."""
    conn = get_connection()
    cur = conn.cursor()

    if DB_BACKEND == "postgres":
        cur.execute("""
            CREATE TABLE IF NOT EXISTS patient_vitals (
                id              SERIAL PRIMARY KEY,
                heart_rate      FLOAT        NOT NULL,
                oxygen          FLOAT        NOT NULL,
                bp_systolic     FLOAT        NOT NULL,
                bp_diastolic    FLOAT        NOT NULL,
                anomaly_score   FLOAT        DEFAULT 0.0,
                severity        VARCHAR(10)  DEFAULT 'LOW',
                timestamp       TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
            );
        """)
    else:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS patient_vitals (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                heart_rate      REAL         NOT NULL,
                oxygen          REAL         NOT NULL,
                bp_systolic     REAL         NOT NULL,
                bp_diastolic    REAL         NOT NULL,
                anomaly_score   REAL         DEFAULT 0.0,
                severity        TEXT         DEFAULT 'LOW',
                timestamp       TEXT         DEFAULT CURRENT_TIMESTAMP
            );
        """)

    conn.commit()
    cur.close()
    conn.close()
    print(f"[DB] patient_vitals table ready (backend={DB_BACKEND}).")


# ────────────────────── INSERT ──────────────────────

def insert_vital(heart_rate, oxygen, bp_systolic, bp_diastolic,
                 anomaly_score, severity):
    """Insert a single vitals record and return the new row id."""
    conn = get_connection()
    cur = conn.cursor()

    if DB_BACKEND == "postgres":
        cur.execute(
            """
            INSERT INTO patient_vitals
                (heart_rate, oxygen, bp_systolic, bp_diastolic, anomaly_score, severity)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id;
            """,
            (heart_rate, oxygen, bp_systolic, bp_diastolic, anomaly_score, severity),
        )
        row_id = cur.fetchone()[0]
    else:
        cur.execute(
            """
            INSERT INTO patient_vitals
                (heart_rate, oxygen, bp_systolic, bp_diastolic, anomaly_score, severity)
            VALUES (?, ?, ?, ?, ?, ?);
            """,
            (heart_rate, oxygen, bp_systolic, bp_diastolic, anomaly_score, severity),
        )
        row_id = cur.lastrowid

    conn.commit()
    cur.close()
    conn.close()
    return row_id


# ────────────────────── QUERIES ──────────────────────

def _rows_to_dicts(cursor):
    """Convert cursor results to a list of dictionaries."""
    if DB_BACKEND == "postgres":
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    else:
        return [dict(row) for row in cursor.fetchall()]


def get_latest_vitals(limit=10):
    """Return the most recent `limit` vitals records."""
    conn = get_connection()
    cur = conn.cursor()
    placeholder = "%s" if DB_BACKEND == "postgres" else "?"
    cur.execute(
        f"SELECT * FROM patient_vitals ORDER BY id DESC LIMIT {placeholder};",
        (limit,),
    )
    results = _rows_to_dicts(cur)
    cur.close()
    conn.close()
    return results


def get_history(limit=100, offset=0):
    """Return paginated vitals history."""
    conn = get_connection()
    cur = conn.cursor()
    if DB_BACKEND == "postgres":
        cur.execute(
            "SELECT * FROM patient_vitals ORDER BY id DESC LIMIT %s OFFSET %s;",
            (limit, offset),
        )
    else:
        cur.execute(
            "SELECT * FROM patient_vitals ORDER BY id DESC LIMIT ? OFFSET ?;",
            (limit, offset),
        )
    results = _rows_to_dicts(cur)
    cur.close()
    conn.close()
    return results


def get_high_alerts(limit=50):
    """Return recent records where severity == 'HIGH'."""
    conn = get_connection()
    cur = conn.cursor()
    if DB_BACKEND == "postgres":
        cur.execute(
            "SELECT * FROM patient_vitals WHERE severity = 'HIGH' ORDER BY id DESC LIMIT %s;",
            (limit,),
        )
    else:
        cur.execute(
            "SELECT * FROM patient_vitals WHERE severity = 'HIGH' ORDER BY id DESC LIMIT ?;",
            (limit,),
        )
    results = _rows_to_dicts(cur)
    cur.close()
    conn.close()
    return results


# ─────────────── Quick Standalone Test ───────────────

if __name__ == "__main__":
    init_db()
    rid = insert_vital(72.0, 98.0, 120.0, 80.0, 0.1, "LOW")
    print(f"[DB] Inserted test record id={rid}")
    print("[DB] Latest vitals:", get_latest_vitals(3))
