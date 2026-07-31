"""
Trains an XGBoost fraud detection model on transactions pulled from Postgres.

Usage:
    python -m app.ml.train
"""

import json
import os

import joblib
import pandas as pd
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

from app.db.database import SessionLocal
from app.ml.features import build_features
from app.models.transaction import Transaction

ARTIFACTS_DIR = "app/ml/artifacts"
MODEL_PATH = os.path.join(ARTIFACTS_DIR, "fraud_model.pkl")
FEATURE_COLUMNS_PATH = os.path.join(ARTIFACTS_DIR, "feature_columns.json")


def load_data() -> pd.DataFrame:
    """Pull all transactions from Postgres into a DataFrame."""
    db = SessionLocal()
    try:
        txns = db.query(Transaction).all()
        data = [
            {
                "amount": t.amount,
                "country": t.country,
                "merchant_category": t.merchant_category,
                "timestamp": t.timestamp,
                "is_fraud": t.is_fraud,
            }
            for t in txns
        ]
        return pd.DataFrame(data)
    finally:
        db.close()


def train():
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)

    print("Loading data from database...")
    df = load_data()
    print(f"Loaded {len(df)} transactions ({df['is_fraud'].sum()} fraudulent)")

    print("Building features...")
    X = build_features(df)
    y = df["is_fraud"].astype(int)

    feature_columns = X.columns.tolist()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Handle class imbalance: fraud is rare, so weight positive class higher
    scale_pos_weight = (y_train == 0).sum() / (y_train == 1).sum()

    print(f"Training XGBoost model (scale_pos_weight={scale_pos_weight:.2f})...")
    model = XGBClassifier(
        n_estimators=200,
        max_depth=5,
        learning_rate=0.1,
        scale_pos_weight=scale_pos_weight,
        eval_metric="logloss",
        random_state=42,
    )
    model.fit(X_train, y_train)

    print("\nEvaluating on test set...")
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=["Legit", "Fraud"]))

    print("Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

    auc = roc_auc_score(y_test, y_proba)
    print(f"\nROC-AUC Score: {auc:.4f}")

    # Save model and the exact feature column order (critical for inference later)
    joblib.dump(model, MODEL_PATH)
    with open(FEATURE_COLUMNS_PATH, "w") as f:
        json.dump(feature_columns, f)

    print(f"\nModel saved to {MODEL_PATH}")
    print(f"Feature columns saved to {FEATURE_COLUMNS_PATH}")


if __name__ == "__main__":
    train()