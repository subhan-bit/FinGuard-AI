"""
Tests for feature engineering logic. These are pure unit tests --
no database or model needed, just checking that build_features()
transforms raw transaction data correctly and predictably.
"""

import pandas as pd

from app.ml.features import build_features


def make_sample_df(**overrides) -> pd.DataFrame:
    """Helper to build a one-row transaction DataFrame with sensible defaults."""
    row = {
        "amount": 100.0,
        "country": "US",
        "merchant_category": "grocery",
        "timestamp": pd.Timestamp("2026-01-15 14:30:00"),  # a Thursday, daytime
    }
    row.update(overrides)
    return pd.DataFrame([row])


def test_high_risk_country_flag_set_correctly():
    df = make_sample_df(country="RU")
    features = build_features(df)
    assert features["is_high_risk_country"].iloc[0] == 1

    df = make_sample_df(country="US")
    features = build_features(df)
    assert features["is_high_risk_country"].iloc[0] == 0


def test_high_risk_category_flag_set_correctly():
    df = make_sample_df(merchant_category="crypto_exchange")
    features = build_features(df)
    assert features["is_high_risk_category"].iloc[0] == 1

    df = make_sample_df(merchant_category="grocery")
    features = build_features(df)
    assert features["is_high_risk_category"].iloc[0] == 0


def test_night_flag_set_for_early_morning_hours():
    df = make_sample_df(timestamp=pd.Timestamp("2026-01-15 03:00:00"))
    features = build_features(df)
    assert features["is_night"].iloc[0] == 1

    df = make_sample_df(timestamp=pd.Timestamp("2026-01-15 14:00:00"))
    features = build_features(df)
    assert features["is_night"].iloc[0] == 0


def test_weekend_flag_set_correctly():
    # 2026-01-17 is a Saturday
    df = make_sample_df(timestamp=pd.Timestamp("2026-01-17 12:00:00"))
    features = build_features(df)
    assert features["is_weekend"].iloc[0] == 1

    # 2026-01-15 is a Thursday
    df = make_sample_df(timestamp=pd.Timestamp("2026-01-15 12:00:00"))
    features = build_features(df)
    assert features["is_weekend"].iloc[0] == 0


def test_amount_log_is_monotonic_with_amount():
    low = build_features(make_sample_df(amount=10.0))["amount_log"].iloc[0]
    high = build_features(make_sample_df(amount=1000.0))["amount_log"].iloc[0]
    assert high > low


def test_category_one_hot_encoding_creates_expected_column():
    df = make_sample_df(merchant_category="travel")
    features = build_features(df)
    assert "cat_travel" in features.columns
    assert features["cat_travel"].iloc[0] == 1