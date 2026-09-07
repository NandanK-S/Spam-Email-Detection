"""
inference.py — Step 6: Reusable Inference Module

The most important deliverable — the FastAPI backend will import this directly.

Provides a single function:
    predict_email(text: str) -> dict

Returns:
    {
        "prediction": "spam" | "ham",
        "confidence": float (0.0-1.0),
        "features": {
            "char_count": int,
            "word_count": int,
            "link_count": int,
            "capital_ratio": float,
            "punctuation_count": int
        }
    }

Artifacts are loaded ONCE at module level (lazy singleton) for performance.
Uses the SAME cleaning logic and feature extraction as training — imported
from features.py, not duplicated.
"""

import os
import numpy as np
import joblib
import scipy.sparse as sp

# Import the SAME functions used during training — no duplication
from features import clean_text, extract_structural_features


# =============================================================================
# Lazy Singleton Artifact Loader
# =============================================================================

_artifacts = {}


def _load_artifacts():
    """Load model, vectorizer, and scaler once (lazy singleton)."""
    if _artifacts:
        return  # Already loaded
    
    artifacts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "artifacts")
    
    # Load the best model
    model_path = os.path.join(artifacts_dir, "best_model.pkl")
    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"Best model not found at {model_path}. "
            f"Run the training pipeline first (python run_pipeline.py)."
        )
    _artifacts["model"] = joblib.load(model_path)
    
    # Load TF-IDF vectorizer
    vectorizer_path = os.path.join(artifacts_dir, "tfidf_vectorizer.pkl")
    if not os.path.exists(vectorizer_path):
        raise FileNotFoundError(f"TF-IDF vectorizer not found at {vectorizer_path}.")
    _artifacts["vectorizer"] = joblib.load(vectorizer_path)
    
    # Load StandardScaler
    scaler_path = os.path.join(artifacts_dir, "scaler.pkl")
    if not os.path.exists(scaler_path):
        raise FileNotFoundError(f"Scaler not found at {scaler_path}.")
    _artifacts["scaler"] = joblib.load(scaler_path)
    
    # Load model metadata to check if NB model (needs MaxAbsScaler)
    meta_path = os.path.join(artifacts_dir, "best_model_meta.pkl")
    if os.path.exists(meta_path):
        _artifacts["meta"] = joblib.load(meta_path)
    else:
        _artifacts["meta"] = {"uses_nb_data": False}
    
    # Load MaxAbsScaler if NB model was selected
    if _artifacts["meta"].get("uses_nb_data", False):
        max_abs_path = os.path.join(artifacts_dir, "max_abs_scaler.pkl")
        if os.path.exists(max_abs_path):
            _artifacts["max_abs_scaler"] = joblib.load(max_abs_path)


# =============================================================================
# Main Prediction Function
# =============================================================================

def predict_email(text: str) -> dict:
    """
    Predict whether an email/SMS is spam or ham.
    
    Applies the SAME preprocessing pipeline as training:
        1. Extract structural features from raw text
        2. Clean text
        3. TF-IDF transform (using fitted vectorizer)
        4. Scale structural features (using fitted scaler)
        5. Combine features via hstack
        6. Predict with the best model
    
    Args:
        text: Raw email/SMS text.
    
    Returns:
        Dict with keys: prediction, confidence, features.
    """
    # Ensure artifacts are loaded
    _load_artifacts()
    
    model = _artifacts["model"]
    vectorizer = _artifacts["vectorizer"]
    scaler = _artifacts["scaler"]
    
    # Step 1: Extract structural features from RAW text (before cleaning)
    raw_features = extract_structural_features(text)
    
    # Step 2: Clean text for TF-IDF
    cleaned = clean_text(text)
    
    # Step 3: TF-IDF transform
    tfidf_vector = vectorizer.transform([cleaned])
    
    # Step 4: Scale structural features (supports both 9-feature and 11-feature scalers)
    if hasattr(scaler, "n_features_in_") and scaler.n_features_in_ == 9:
        struct_values = np.array([[
            raw_features["char_count"],
            raw_features["word_count"],
            raw_features["link_count"],
            raw_features["capital_ratio"],
            raw_features["punctuation_count"],
            raw_features["digit_count"],
            raw_features["special_char_count"],
            raw_features["avg_word_length"],
            raw_features["exclamation_count"],
        ]])
    else:
        struct_values = np.array([[
            raw_features["char_count"],
            raw_features["word_count"],
            raw_features["link_count"],
            raw_features["capital_ratio"],
            raw_features["punctuation_count"],
            raw_features["digit_count"],
            raw_features["special_char_count"],
            raw_features["avg_word_length"],
            raw_features["exclamation_count"],
            raw_features.get("urgency_word_count", 0),
            raw_features.get("sensitive_word_count", 0),
        ]])
    struct_scaled = scaler.transform(struct_values)
    
    # Step 5: Combine TF-IDF (sparse) + structural (dense)
    combined = sp.hstack([tfidf_vector, sp.csr_matrix(struct_scaled)])
    
    # Apply MaxAbsScaler if the best model is NB
    if _artifacts["meta"].get("uses_nb_data", False) and "max_abs_scaler" in _artifacts:
        combined = _artifacts["max_abs_scaler"].transform(combined)
    
    # Step 6: Predict base probabilities
    p_spam = 0.5
    p_ham = 0.5
    
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(combined)[0]
        classes = list(getattr(model, "classes_", [0, 1]))
        if 0 in classes and 1 in classes:
            p_spam = float(proba[classes.index(0)])
            p_ham = float(proba[classes.index(1)])
        else:
            p_spam = float(proba[0])
            p_ham = 1.0 - p_spam
    elif hasattr(model, "decision_function"):
        decision = float(model.decision_function(combined)[0])
        # Decision function: higher values indicate ham (class 1)
        prob_ham = float(1 / (1 + np.exp(-decision)))
        p_ham = prob_ham
        p_spam = 1.0 - prob_ham
    else:
        pred_raw = model.predict(combined)[0]
        p_spam = 1.0 if pred_raw == 0 else 0.0
        p_ham = 1.0 - p_spam
    
    # =========================================================================
    # Step 7: Hybrid Phishing & Security Threat Analysis
    # Real-world spam filters (SpamAssassin, Barracuda) combine ML with
    # heuristic rule-based weighting to detect credential harvesting / phishing.
    # =========================================================================
    text_lower = text.lower()
    urgency_cnt = raw_features.get("urgency_word_count", 0)
    sensitive_cnt = raw_features.get("sensitive_word_count", 0)
    
    credential_indicators = [
        'password', 'credit card', 'bank details', 'social security', 'ssn',
        'routing number', 'pin', 'login credential', 'wire transfer', 'cvv'
    ]
    urgency_threat_indicators = [
        'suspended', 'suspend', 'permanently suspended', 'verify your account',
        'account verification', 'unauthorized login', 'action required',
        'immediate deactivation', 'terminated', 'within 24 hours'
    ]
    
    has_credential_request = any(ci in text_lower for ci in credential_indicators)
    has_urgency_threat = any(ui in text_lower for ui in urgency_threat_indicators)
    
    threat_boost = 0.0
    if has_credential_request and has_urgency_threat:
        # High confidence credential theft / account suspension phishing attack
        threat_boost = 0.50
    elif has_credential_request:
        threat_boost = 0.25
    elif has_urgency_threat:
        threat_boost = 0.20
        
    if urgency_cnt >= 2 and sensitive_cnt >= 2:
        threat_boost = max(threat_boost, 0.35)
        
    adjusted_p_spam = min(0.9999, p_spam + threat_boost)
    adjusted_p_ham = 1.0 - adjusted_p_spam
    
    if adjusted_p_spam >= 0.50:
        prediction_label = "spam"
        confidence = adjusted_p_spam
    else:
        prediction_label = "ham"
        confidence = adjusted_p_ham
    
    return {
        "prediction": prediction_label,
        "confidence": round(confidence, 4),
        "features": raw_features,
    }


# =============================================================================
# Test / Demo
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("INFERENCE MODULE — predict_email() TEST")
    print("=" * 70)
    
    test_cases = [
        {
            "label": "OBVIOUS SPAM",
            "text": "CONGRATULATIONS!!! You've WON £1000 CASH! Call 09061234567 NOW to claim your prize! Visit http://free-prizes.com. Offer expires TODAY!!!"
        },
        {
            "label": "OBVIOUS HAM",
            "text": "Hey, are we still meeting for lunch tomorrow? I was thinking we could go to that new Italian place on Main Street."
        },
        {
            "label": "BORDERLINE",
            "text": "Your account has been updated. Please review your recent activity at http://mybank.com/activity"
        },
    ]
    
    for case in test_cases:
        print(f"\n{'─'*60}")
        print(f"📧 Test: {case['label']}")
        print(f"   Text: {case['text'][:80]}...")
        
        result = predict_email(case["text"])
        
        is_spam = result["prediction"] == "spam"
        icon = "🚫" if is_spam else "✅"
        
        print(f"\n   {icon} Prediction:  {result['prediction'].upper()}")
        print(f"   📊 Confidence:  {result['confidence']:.4f} ({result['confidence']*100:.1f}%)")
        print(f"   🔧 Features:")
        for key, value in result["features"].items():
            print(f"      {key}: {value}")
    
    print(f"\n{'='*70}")
    print("✅ All inference tests completed successfully!")
    print(f"{'='*70}")
