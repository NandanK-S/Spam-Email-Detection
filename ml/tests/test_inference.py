"""
test_inference.py — Unit tests for ML inference engine and hybrid security heuristic threat layer.
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from inference import predict_email


class TestInferenceEngine:
    """Tests for predict_email() function and hybrid heuristics."""

    def test_predict_email_response_contract(self):
        text = "Hello, are we still having the team sync today?"
        res = predict_email(text)

        assert isinstance(res, dict)
        assert "prediction" in res
        assert "confidence" in res
        assert "features" in res

        assert res["prediction"] in ["spam", "ham"]
        assert isinstance(res["confidence"], float)
        assert 0.0 <= res["confidence"] <= 1.0
        assert isinstance(res["features"], dict)
        assert len(res["features"]) == 11

    def test_obvious_spam_detection(self):
        spam_text = (
            "CONGRATULATIONS! You have won a $1,000,000 cash prize! "
            "Call NOW 09061234567 or click http://claim-rewards.com to receive your payout!"
        )
        res = predict_email(spam_text)
        assert res["prediction"] == "spam"
        assert res["confidence"] >= 0.70

    def test_obvious_ham_detection(self):
        ham_text = (
            "Hi Professor, I have completed the assigned reading for chapter 4 "
            "and submitted my draft report. Let me know if you would like any revisions."
        )
        res = predict_email(ham_text)
        assert res["prediction"] == "ham"
        assert res["confidence"] >= 0.70

    def test_phishing_credential_urgency_heuristics(self):
        phishing_text = (
            "Urgent Account Verification Required! Your account will be permanently suspended today. "
            "Verify your account now by entering your username, password, and credit card information."
        )
        res = predict_email(phishing_text)
        assert res["prediction"] == "spam"
        assert res["confidence"] >= 0.70

    def test_empty_string_graceful_handling(self):
        res = predict_email("")
        assert res["prediction"] in ["spam", "ham"]
        assert 0.0 <= res["confidence"] <= 1.0

    def test_large_input_text_boundary(self):
        # 10,000 character repeating string
        large_text = "This is a normal paragraph discussing project updates. " * 200
        res = predict_email(large_text)
        assert res["prediction"] in ["spam", "ham"]
        assert 0.0 <= res["confidence"] <= 1.0
