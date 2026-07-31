"""
Generates human-readable explanations for why a transaction was
flagged as fraud, using SHAP values from the trained XGBoost model.
"""

import shap

from app.services.fraud_scorer import _load_model

_explainer = None


def _get_explainer():
    """Lazy-load a SHAP TreeExplainer once, cache in memory."""
    global _explainer
    if _explainer is None:
        model, _ = _load_model()
        _explainer = shap.TreeExplainer(model)
    return _explainer


def explain_transaction(X, top_n: int = 5) -> list[dict]:
    """
    Takes a single-row feature DataFrame (already built via build_features
    and reindexed to match training columns) and returns the top N
    features that most influenced the fraud prediction, ranked by
    absolute impact.

    Positive shap_value = pushed toward fraud.
    Negative shap_value = pushed toward legitimate.
    """
    explainer = _get_explainer()
    shap_values = explainer.shap_values(X)

    # shap_values shape: (1, num_features) for a single transaction
    row_values = shap_values[0]
    feature_names = X.columns.tolist()

    explanations = [
        {"feature": feature_names[i], "impact": round(float(row_values[i]), 4)}
        for i in range(len(feature_names))
    ]

    # Sort by absolute impact, descending
    explanations.sort(key=lambda x: abs(x["impact"]), reverse=True)

    return explanations[:top_n]