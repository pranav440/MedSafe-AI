/**
 * MedSafe AI – API Service Layer
 * ================================
 * Connects the React frontend to the Flask backend (port 5000).
 * All endpoints, type definitions, and error handling live here.
 */

// Definitive API Detection:
// 1. If VITE_API_URL is set (build-time), use it.
// 2. If running on localhost, use the local Flask port (5000).
// 3. Otherwise (Production/Cloud), use relative paths to the same origin.
const getApiBase = () => {
  // 1. If we are in production (Render), always use relative paths
  if (import.meta.env.PROD) return "";

  // 2. If VITE_API_URL is set (local dev override), use it
  const envUrl = import.meta.env.VITE_API_URL;
  if (envUrl && envUrl.trim().length > 0) return envUrl;

  // 3. Default to local Flask in development
  return "http://localhost:5000";
};

const API_BASE = getApiBase();
console.log(`[MedSafe AI] Cloud Sync: Using backend at "${API_BASE || "(the same URL)"}"`);

// ─── Generic Fetch Wrapper ───────────────────────────
async function request<T>(endpoint: string, options?: RequestInit): Promise<T> {
  // Add a cache-buster in development and production to force fresh data
  const url = `${API_BASE}${endpoint}${endpoint.includes("?") ? "&" : "?"}t=${Date.now()}`;

  try {
    const res = await fetch(url, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });

    if (!res.ok) {
      const body = await res.json().catch(() => ({}));
      throw new Error(body.message || `API error ${res.status} at ${url}`);
    }

    return res.json();
  } catch (err: any) {
    if (err.message === "Failed to fetch") {
      console.error(`[MedSafe AI] Fatal Network Error: Could not reach ${url}`);
      throw new Error(`Connection Error: The dashboard cannot reach the data engine at ${url}. Please ensure the Flask backend is running.`);
    }
    throw err;
  }
}

// ─── TypeScript Interfaces (match Flask responses) ───

/** Single vitals record as returned by Flask */
export interface VitalRecord {
  id: number;
  heart_rate: number;
  oxygen: number;
  bp_systolic: number;
  bp_diastolic: number;
  anomaly_score: number;
  severity: "LOW" | "MEDIUM" | "HIGH";
  timestamp: string;
}

/** What the Dashboard/VitalsMonitor pages display */
export interface VitalsData {
  heart_rate: number;
  oxygen_level: number;
  blood_pressure: string;
  anomaly_score: number;
  severity: "LOW" | "MEDIUM" | "HIGH";
  timestamp?: string;
}

export interface HistoryEntry extends VitalsData {
  time: string;
  timestamp: string;
}

/** Flask /analyze_vitals response */
export interface AnalyzeVitalsResult {
  status: string;
  anomaly_score: number;
  if_score: number;
  ae_score: number;
  severity: "LOW" | "MEDIUM" | "HIGH";
}

/** Prescription medicine match */
export interface MedicineMatch {
  medicine: string;
  active_salt: string;
  confidence: number;
}

export interface PrescriptionResult {
  status: string;
  medicines_found: MedicineMatch[];
  raw_text?: string;
}

/** Drug interaction entry */
export interface InteractionEntry {
  drug_1: string;
  drug_2: string;
  severity: string;
  description: string;
}

export interface InteractionResult {
  status: string;
  medicines_checked: string[];
  interactions_found: InteractionEntry[];
  safe_message?: string;
}

/** Symptom guidance condition */
export interface MatchedCondition {
  condition: string;
  match_score: number;
  possible_causes: string[];
  home_remedies: string[];
  lifestyle_advice: string[];
  warning_signs: string[];
}

export interface SymptomResult {
  status: string;
  matched_conditions: MatchedCondition[];
  disclaimer: string;
}

/** Side-effect analysis */
export interface SideEffectResult {
  status: string;
  analysis: string;
  urgency: string;
  recommendations: string[];
  disclaimer: string;
}

// ─── Helper: Convert Flask vitals record → UI format ───

function toVitalsData(rec: VitalRecord): VitalsData {
  return {
    heart_rate: rec.heart_rate,
    oxygen_level: rec.oxygen,
    blood_pressure: `${Math.round(rec.bp_systolic)}/${Math.round(rec.bp_diastolic)}`,
    anomaly_score: rec.anomaly_score,
    severity: rec.severity,
    timestamp: rec.timestamp,
  };
}

function toHistoryEntry(rec: VitalRecord, index: number): HistoryEntry {
  return {
    ...toVitalsData(rec),
    time: `${index}m`,
    timestamp: rec.timestamp,
  };
}

// ─── API Methods ──────────────────────────────────────

export const api = {
  /** GET /latest_vitals → latest vitals records */
  getLatestVitals: async (): Promise<VitalsData> => {
    const res = await request<{ status: string; data: VitalRecord[] }>("/latest_vitals");
    if (!res.data.length) throw new Error("No vitals data available yet.");
    return toVitalsData(res.data[0]);
  },

  /** GET /history → paginated vitals history (for charts) */
  getHistory: async (limit = 50): Promise<HistoryEntry[]> => {
    const res = await request<{ status: string; data: VitalRecord[] }>(`/history?limit=${limit}&offset=0`);
    return res.data.reverse().map((rec, i) => toHistoryEntry(rec, i));
  },

  /** GET /high_alerts → HIGH severity records */
  getHighAlerts: async (): Promise<VitalRecord[]> => {
    const res = await request<{ status: string; data: VitalRecord[] }>("/high_alerts");
    return res.data;
  },

  /** POST /analyze_vitals → manual anomaly detection */
  analyzeVitals: async (heart_rate: number, oxygen: number, bp_systolic: number, bp_diastolic: number): Promise<AnalyzeVitalsResult> => {
    return request<AnalyzeVitalsResult>("/analyze_vitals", {
      method: "POST",
      body: JSON.stringify({ heart_rate, oxygen, bp_systolic, bp_diastolic }),
    });
  },

  /** POST /analyze_prescription → OCR or text-based medicine extraction */
  analyzePrescription: async (file?: File, text?: string): Promise<PrescriptionResult> => {
    if (file) {
      const formData = new FormData();
      formData.append("file", file);
      const res = await fetch(`${API_BASE}/analyze_prescription`, { method: "POST", body: formData });
      if (!res.ok) throw new Error(`Prescription analysis failed (${res.status})`);
      return res.json();
    }
    return request<PrescriptionResult>("/analyze_prescription", {
      method: "POST",
      body: JSON.stringify({ text: text || "" }),
    });
  },

  /** POST /check_interactions → drug interaction checker */
  checkInteractions: async (medicines: string[]): Promise<InteractionResult> => {
    return request<InteractionResult>("/check_interactions", {
      method: "POST",
      body: JSON.stringify({ medicines }),
    });
  },

  /** POST /symptom_guidance → symptom-based health guidance */
  getSymptomGuidance: async (symptoms: string[]): Promise<SymptomResult> => {
    return request<SymptomResult>("/symptom_guidance", {
      method: "POST",
      body: JSON.stringify({ symptoms }),
    });
  },

  /** POST /side_effect_report → side-effect analysis */
  reportSideEffect: async (data: {
    age: number;
    gender: string;
    medicine: string;
    dosage: string;
    symptoms: string[];
  }): Promise<SideEffectResult> => {
    return request<SideEffectResult>("/side_effect_report", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
};
