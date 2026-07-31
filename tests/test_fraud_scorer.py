"""
Tests for the real-time fraud scoring service. These require a
trained model to exist at app/ml/artifacts/fraud_model.pkl --
run `python -m app.ml.train` first if this file is missing.
"""

from datetime import datetime

from app.services.fraud_scorer import score_transaction


def test_obviously_suspicious_transaction_scores_high():
    transaction = {
        "amount": 5000.0,
        "country": "RU",
        "merchant_category": "crypto_exchange",
        "timestamp": datetime(2026, 1, 15, 3, 0, 0),  # 3am
    }
    result, _ = score_transaction(transaction)
    assert result["fraud_score"] > 0.5
    assert result["predicted_fraud"] is True


def test_obviously_normal_transaction_scores_low():
    transaction = {
        "amount": 12.50,
        "country": "US",
        "merchant_category": "restaurant",
        "timestamp": datetime(2026, 1, 15, 13, 0, 0),  # 1pm
    }
    result, _ = score_transaction(transaction)
    assert result["fraud_score"] < 0.5
    assert result["predicted_fraud"] is False


def test_score_is_a_valid_probability():
    transaction = {
        "amount": 200.0,
        "country": "GB",
        "merchant_category": "electronics",
        "timestamp": datetime(2026, 1, 15, 10, 0, 0),
    }
    result, _ = score_transaction(transaction)
    assert 0.0 <= result["fraud_score"] <= 1.0