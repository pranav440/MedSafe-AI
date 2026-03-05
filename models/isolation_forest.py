"""
MedSafe AI – Isolation Forest Anomaly Detector
================================================
Uses scikit-learn IsolationForest trained on synthetic normal vitals
to score incoming readings.

Anomaly score: 0 (fully normal) → 1 (fully anomalous).
"""

import numpy as np
from sklearn.ensemble import IsolationForest


class VitalsIsolationForest:
    """Isolation Forest model for patient vitals anomaly detection."""

    def __init__(self, contamination=0.05, random_state=42):
        self.model = IsolationForest(
            n_estimators=100,
            contamination=contamination,
            random_state=random_state,
        )
        self._is_fitted = False
        self._fit_on_synthetic()

    # ──────────── Training ────────────

    def _fit_on_synthetic(self):
        """
        Pre-train on synthetic 'normal' vitals so the model is
        ready to use immediately without requiring a training step.
        """
        np.random.seed(42)
        n = 1000
        data = np.column_stack([
            np.random.normal(75, 5, n),     # heart_rate
            np.random.normal(97.5, 0.8, n), # oxygen
            np.random.normal(120, 5, n),    # bp_systolic
            np.random.normal(78, 4, n),     # bp_diastolic
        ])
        self.model.fit(data)
        self._is_fitted = True

    # ──────────── Prediction ────────────

    def predict(self, heart_rate, oxygen, bp_systolic, bp_diastolic):
        """
        Return an anomaly score between 0 (normal) and 1 (anomalous).

        IsolationForest.decision_function returns negative values for
        anomalies and positive for inliers. We normalise this to [0, 1].
        """
        if not self._is_fitted:
            self._fit_on_synthetic()

        sample = np.array([[heart_rate, oxygen, bp_systolic, bp_diastolic]])

        # decision_function: large positive → inlier, negative → outlier
        raw_score = self.model.decision_function(sample)[0]

        # Convert to 0-1 where 1 = most anomalous
        # Typical raw scores range roughly from -0.5 to 0.3
        anomaly_score = max(0.0, min(1.0, 0.5 - raw_score))
        return round(anomaly_score, 4)


# ─────── Quick Test ───────

if __name__ == "__main__":
    detector = VitalsIsolationForest()
    # Normal reading
    print("Normal  :", detector.predict(72, 98, 118, 76))
    # Anomalous reading (tachycardia)
    print("Anomaly :", detector.predict(165, 88, 190, 115))
