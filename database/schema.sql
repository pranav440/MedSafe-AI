-- ================================================
-- MedSafe AI – PostgreSQL Schema
-- ================================================
-- Run this script to initialise the database:
--   psql -U postgres -d medsafe_ai -f database/schema.sql
-- ================================================

-- Create the database (run separately if needed)
-- CREATE DATABASE medsafe_ai;

-- Patient vitals table – stores every reading from the streaming pipeline
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

-- Index for quick severity lookups (used by /high_alerts endpoint)
CREATE INDEX IF NOT EXISTS idx_severity ON patient_vitals (severity);

-- Index for time-based queries (used by /history endpoint)
CREATE INDEX IF NOT EXISTS idx_timestamp ON patient_vitals (timestamp DESC);
