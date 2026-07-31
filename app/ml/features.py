"""
Feature engineering for the fraud detection model.

Converts raw transaction rows into numeric features suitable
for XGBoost. Keeping this as a separate module means training
and inference (real-time scoring) both call the exact same
transformation logic, avoiding train/serve skew.
"""

import numpy as np
import pandas as pd

HIGH_RISK_COUNTRIES = {"NG", "RU", "KP", "IR", "PK"}
HIGH_RISK_CATEGORIES = {"gambling", "crypto_exchange", "jewelry", "electronics_high_value"}


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Takes a DataFrame of raw transactions and returns a DataFrame
    of numeric features ready for model training/inference.

    Expected input columns: amount, country, merchant_category, timestamp
    """
    features = pd.DataFrame(index=df.index)

    # --- Amount-based features ---
    features["amount"] = df["amount"]
    features["amount_log"] = np.log1p(df["amount"])

    # --- Time-based features ---
    ts = pd.to_datetime(df["timestamp"])
    features["hour"] = ts.dt.hour
    features["day_of_week"] = ts.dt.dayofweek
    features["is_weekend"] = (ts.dt.dayofweek >= 5).astype(int)
    features["is_night"] = ts.dt.hour.apply(lambda h: 1 if h < 6 else 0)

    # --- Risk flags ---
    features["is_high_risk_country"] = df["country"].apply(
        lambda c: 1 if c in HIGH_RISK_COUNTRIES else 0
    )
    features["is_high_risk_category"] = df["merchant_category"].apply(
        lambda c: 1 if c in HIGH_RISK_CATEGORIES else 0
    )

    # --- Categorical encoding (one-hot for merchant category) ---
    category_dummies = pd.get_dummies(df["merchant_category"], prefix="cat")
    features = pd.concat([features, category_dummies], axis=1)

    return features