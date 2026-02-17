# app/model.py

import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report

# ─────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "artifacts", "aqi_model.pkl")

# ─────────────────────────────────────────────
# AQI Categories
# ─────────────────────────────────────────────
AQI_CATEGORIES = {
    0: "Good",
    1: "Moderate",
    2: "Unhealthy for Sensitive Groups",
    3: "Unhealthy",
    4: "Hazardous"
}

# ─────────────────────────────────────────────
# Generate Synthetic Training Data
# ─────────────────────────────────────────────
def generate_training_data(n_samples: int = 2000) -> pd.DataFrame:
    """
    Generates realistic synthetic AQI data.
    Features:
        - pm25       : Fine particulate matter (µg/m³), range 0–500
        - pm10       : Coarse particulate matter (µg/m³), range 0–600
        - co2        : Carbon dioxide (ppm), range 300–5000
        - no2        : Nitrogen dioxide (µg/m³), range 0–400
        - temperature: Ambient temperature (°C), range -10–50
        - humidity   : Relative humidity (%), range 10–100
    """
    np.random.seed(42)

    data = {
        "pm25":        np.random.uniform(0, 500, n_samples),
        "pm10":        np.random.uniform(0, 600, n_samples),
        "co2":         np.random.uniform(300, 5000, n_samples),
        "no2":         np.random.uniform(0, 400, n_samples),
        "temperature": np.random.uniform(-10, 50, n_samples),
        "humidity":    np.random.uniform(10, 100, n_samples),
    }

    df = pd.DataFrame(data)

    # Rule-based label generation (mimics real AQI logic)
    def assign_label(row):
        score = (
            (row["pm25"] / 500) * 40 +
            (row["pm10"] / 600) * 20 +
            (row["co2"] / 5000) * 20 +
            (row["no2"] / 400) * 20
        )
        # score ranges 0–100, fix thresholds accordingly:
        if score < 20:
            return 0  # Good
        elif score < 40:
            return 1  # Moderate
        elif score < 55:
            return 2  # Unhealthy for Sensitive Groups
        elif score < 75:
            return 3  # Unhealthy
        else:
            return 4  # Hazardous

    df["label"] = df.apply(assign_label, axis=1)
    return df


# ─────────────────────────────────────────────
# Train and Save Model
# ─────────────────────────────────────────────
def train_model() -> None:
    """Trains a RandomForest pipeline and saves it to disk."""
    print("🔧 Training AQI prediction model...")

    df = generate_training_data()
    X = df.drop("label", axis=1)
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Pipeline: scale → classify
    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("classifier", RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        ))
    ])

    pipeline.fit(X_train, y_train)

    # Evaluate
    y_pred = pipeline.predict(X_test)
    print("\n📊 Model Evaluation Report:")
    print(classification_report(
        y_test, y_pred,
        target_names=list(AQI_CATEGORIES.values())
    ))

    # Save model
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)
    print(f"✅ Model saved at: {MODEL_PATH}")


# ─────────────────────────────────────────────
# Load Model (lazy load singleton)
# ─────────────────────────────────────────────
_model = None

def load_model():
    """Loads model from disk. Trains if not found."""
    global _model
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            train_model()
        _model = joblib.load(MODEL_PATH)
        print("✅ Model loaded successfully.")
    return _model


# ─────────────────────────────────────────────
# Predict
# ─────────────────────────────────────────────
def predict_aqi(
    pm25: float,
    pm10: float,
    co2: float,
    no2: float,
    temperature: float,
    humidity: float
) -> dict:
    """Returns AQI category prediction with confidence scores."""
    model = load_model()

    features = np.array([[pm25, pm10, co2, no2, temperature, humidity]])
    prediction = int(model.predict(features)[0])
    probabilities = model.predict_proba(features)[0]

    confidence_scores = {
        AQI_CATEGORIES[i]: round(float(prob), 4)
        for i, prob in enumerate(probabilities)
    }

    return {
        "category_id": prediction,
        "category": AQI_CATEGORIES[prediction],
        "confidence": round(float(probabilities[prediction]), 4),
        "all_probabilities": confidence_scores
    }