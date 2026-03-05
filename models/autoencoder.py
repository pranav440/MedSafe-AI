"""
MedSafe AI – Autoencoder Anomaly Detector
==========================================
A Keras-based autoencoder trained on synthetic normal vitals.
Anomaly score = reconstruction error (MSE), normalised to [0, 1].

Architecture:
    Input(4) → Dense(8, relu) → Dense(4, relu) → Dense(2, relu)   [encoder]
             → Dense(4, relu) → Dense(8, relu) → Dense(4, sigmoid) [decoder]
"""

import os
import numpy as np

# Suppress TensorFlow info logs
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers


class VitalsAutoencoder:
    """Autoencoder for patient vitals anomaly detection."""

    def __init__(self):
        self.model = None
        self.scaler_min = None
        self.scaler_range = None
        self._build_and_train()

    # ──────────── Model Architecture ────────────

    def _build_model(self):
        """Build encoder–decoder network."""
        model = keras.Sequential([
            layers.Input(shape=(4,)),
            # Encoder
            layers.Dense(8, activation="relu"),
            layers.Dense(4, activation="relu"),
            layers.Dense(2, activation="relu"),   # bottleneck
            # Decoder
            layers.Dense(4, activation="relu"),
            layers.Dense(8, activation="relu"),
            layers.Dense(4, activation="sigmoid"),
        ])
        model.compile(optimizer="adam", loss="mse")
        return model

    # ──────────── Training ────────────

    def _build_and_train(self):
        """Generate synthetic normals, fit scaler, train autoencoder."""
        np.random.seed(42)
        n = 2000
        raw = np.column_stack([
            np.random.normal(75, 5, n),
            np.random.normal(97.5, 0.8, n),
            np.random.normal(120, 5, n),
            np.random.normal(78, 4, n),
        ])

        # Min-max normalisation to [0, 1]
        self.scaler_min = raw.min(axis=0)
        self.scaler_range = raw.max(axis=0) - self.scaler_min
        self.scaler_range[self.scaler_range == 0] = 1  # avoid div-by-zero
        normalised = (raw - self.scaler_min) / self.scaler_range

        self.model = self._build_model()
        self.model.fit(
            normalised, normalised,
            epochs=30,
            batch_size=32,
            verbose=0,
        )

    # ──────────── Prediction ────────────

    def predict(self, heart_rate, oxygen, bp_systolic, bp_diastolic):
        """
        Return an anomaly score between 0 (normal) and 1 (anomalous).
        Score = normalised reconstruction error (MSE).
        """
        sample = np.array([[heart_rate, oxygen, bp_systolic, bp_diastolic]])
        normalised = (sample - self.scaler_min) / self.scaler_range
        reconstructed = self.model.predict(normalised, verbose=0)
        mse = np.mean((normalised - reconstructed) ** 2)

        # Normalise – empirically, normal MSE < 0.01, anomalous > 0.05
        score = min(1.0, mse / 0.05)
        return round(float(score), 4)


# ─────── Quick Test ───────

if __name__ == "__main__":
    ae = VitalsAutoencoder()
    print("Normal  :", ae.predict(72, 98, 118, 76))
    print("Anomaly :", ae.predict(165, 85, 200, 120))
