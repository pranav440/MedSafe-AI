/**
 * useVitalsData – Real-time data hook
 * =====================================
 * Calls the Flask API for vitals data.
 * Responds to the global Refresh button via RefreshContext.
 * Falls back gracefully if the backend is unavailable.
 */

import { useState, useCallback, useEffect } from "react";
import { api, type VitalsData, type HistoryEntry } from "@/services/api";
import { useRefresh } from "@/hooks/useRefresh";

const FALLBACK_VITALS: VitalsData = {
  heart_rate: 0,
  oxygen_level: 0,
  blood_pressure: "--/--",
  anomaly_score: 0,
  severity: "LOW",
};

export function useVitalsData() {
  const [vitals, setVitals] = useState<VitalsData>(FALLBACK_VITALS);
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { refreshKey } = useRefresh();

  const refresh = useCallback(async () => {
    try {
      const [latestVitals, historyData] = await Promise.all([
        api.getLatestVitals(),
        api.getHistory(30),
      ]);
      setVitals(latestVitals);
      setHistory(historyData);
      setError(null);
    } catch (err: any) {
      setError(err.message || "Failed to fetch vitals data");
    } finally {
      setLoading(false);
    }
  }, []);

  // Initial fetch and auto-refresh every 5 seconds
  useEffect(() => {
    refresh();
    const interval = setInterval(refresh, 5000);
    return () => clearInterval(interval); // cleanup to prevent memory leaks
  }, [refresh]);

  // Re-fetch when TopBar Refresh button is clicked
  useEffect(() => {
    if (refreshKey > 0) {
      refresh();
    }
  }, [refreshKey, refresh]);

  return { vitals, history, loading, error, refresh };
}

// Backward compat
export { useVitalsData as useMockData };
