"""
Loads the trained fraud model once and exposes a function to score
new transactions in real time.
"""

import json
import os

import joblib
import pandas as pd

from app.ml.features import build_features

ARTIFACTS_DIR = "app/ml/artifacts"
MODEL_PATH = os.path.join(ARTIFACTS_DIR, "fraud_model.pkl")
FEATURE_COLUMNS_PATH = os.path.join(ARTIFACTS_DIR, "feature_columns.json")

_model = None
_feature_columns = None


def _load_model():
    """Lazy-load the model and feature columns once, cache in memory."""
    global _model, _feature_columns
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"No trained model found at {MODEL_PATH}. Run `python -m app.ml.train` first."
            )
        _model = joblib.load(MODEL_PATH)
        with open(FEATURE_COLUMNS_PATH) as f:
            _feature_columns = json.load(f)
    return _model, _feature_columns


def score_transaction(transaction: dict, threshold: float = 0.5) -> dict:
    """
    Score a single transaction dict with keys:
    amount, country, merchant_category, timestamp

    Returns fraud_score (0-1 probability) and predicted_fraud (bool).
    """
    model, feature_columns = _load_model()

    df = pd.DataFrame([transaction])
    X = build_features(df)

    # Ensure columns match training exactly (missing categories -> 0, extras dropped)
    X = X.reindex(columns=feature_columns, fill_value=0)

    fraud_score = float(model.predict_proba(X)[0][1])
    predicted_fraud = fraud_score >= threshold

    return {
        "fraud_score": round(fraud_score, 4),
        "predicted_fraud": predicted_fraud,
        "flagged": predicted_fraud,
    }