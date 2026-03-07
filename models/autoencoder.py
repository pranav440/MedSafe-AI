"""
MedSafe AI – Autoencoder Anomaly Detector
==========================================
A Scikit-Learn based autoencoder (MLPRegressor) trained on synthetic normal vitals.
Anomaly score = reconstruction error (MSE), normalised to [0, 1].

Architecture:
    Uses an MLPRegressor with hidden layers [8, 4, 8] to mimic the 
    bottleneck structure of a traditional autoencoder.
"""

import numpy as np
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import MinMaxScaler


class VitalsAutoencoder:
    """Autoencoder for patient vitals anomaly detection using Scikit-Learn."""

    def __init__(self):
        self.model = MLPRegressor(
            hidden_layer_sizes=(8, 4, 8),
            activation="relu",
            solver="adam",
            max_iter=500,
            random_state=42,
            verbose=False
        )
        self.scaler = MinMaxScaler()
        self._is_fitted = False
        self._build_and_train()

    # ──────────── Training ────────────

    def _build_and_train(self):
        """Generate synthetic normals, fit scaler, train autoencoder."""
        np.random.seed(42)
        n = 1000  # Sufficient for a lightweight model
        raw = np.column_stack([
            np.random.normal(75, 5, n),      # heart_rate
            np.random.normal(97.5, 0.8, n),  # oxygen
            np.random.normal(120, 5, n),     # bp_systolic
            np.random.normal(78, 4, n),      # bp_diastolic
        ])

        # Fit scaler and transform data
        normalised = self.scaler.fit_transform(raw)

        # In an autoencoder pipeline using MLPRegressor, we predict the input itself
        self.model.fit(normalised, normalised)
        self._is_fitted = True

    # ──────────── Prediction ────────────

    def predict(self, heart_rate, oxygen, bp_systolic, bp_diastolic):
        """
        Return an anomaly score between 0 (normal) and 1 (anomalous).
        Score = normalised reconstruction error (MSE).
        """
        if not self._is_fitted:
            self._build_and_train()

        sample = np.array([[heart_rate, oxygen, bp_systolic, bp_diastolic]])
        
        # Scale input
        normalised = self.scaler.transform(sample)
        
        # Get reconstruction
        reconstructed = self.model.predict(normalised)
        
        # Calculate MSE
        mse = np.mean((normalised - reconstructed) ** 2)

        # Normalise – using similar heuristic as before
        # Standard normals have MSE < 0.005 usually, anomalies > 0.02
        score = min(1.0, mse / 0.02)
        return round(float(score), 4)


# ─────── Quick Test ───────

if __name__ == "__main__":
    ae = VitalsAutoencoder()
    # Normal reading
    print("Normal  :", ae.predict(72, 98, 118, 76))
    # Anomalous reading (extreme tachycardia + hypoxia)
    print("Anomaly :", ae.predict(165, 85, 200, 120))
