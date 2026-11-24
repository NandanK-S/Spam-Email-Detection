"""
test_integration.py — Integration & End-to-End tests for the full application flow.

Tests the interaction between:
  - ML inference → blockchain logging → chain verification
  - Prediction API → blockchain log consistency
  - Error recovery and edge-case flows
  - Model comparison data contract

Uses FastAPI TestClient (same-process, no network needed).
"""

import sys
import os
import json
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend import app


@pytest.fixture(scope="module")
def client():
    """Create a shared TestClient for all integration tests."""
    with TestClient(app) as c:
        yield c


# =============================================================================
# E2E Flow: Predict → Blockchain Log → Chain Verify
# =============================================================================

class TestFullPredictionFlow:
    """End-to-end tests for the complete prediction-to-audit cycle."""

    def test_spam_prediction_creates_blockchain_entry(self, client):
        """Submit spam email → verify prediction + blockchain block created."""
        # Step 1: Get current blockchain length
        log_before = client.get("/api/blockchain/log").json()
        count_before = len(log_before)

        # Step 2: Submit a clearly spam email
        spam_payload = {
            "text": "CONGRATULATIONS!!! You have been SELECTED as our grand prize WINNER! "
                    "Click http://claim-prize-now.com immediately to collect $1,000,000! "
                    "Call NOW at 09061234567! This offer EXPIRES today!!!"
        }
        res = client.post("/api/predict", json=spam_payload)
        assert res.status_code == 200
        prediction = res.json()

        # Step 3: Verify prediction response structure
        assert prediction["prediction"] == "Spam"
        assert 0.70 <= prediction["confidence"] <= 1.0
        assert "emailHash" in prediction
        assert prediction["emailHash"].startswith("0x")
        assert "blockNumber" in prediction
        assert "blockHash" in prediction

        # Step 4: Verify features were extracted correctly
        features = prediction["features"]
        assert features["charCount"] > 0
        assert features["wordCount"] > 0
        assert features["exclamationCount"] >= 3  # Multiple !!! in text
        assert features["linkCount"] >= 1  # At least http://claim-prize-now.com
        assert features["urgencyWordCount"] >= 1  # "now", "expires", "today", etc.

        # Step 5: Verify a new block was appended to blockchain
        log_after = client.get("/api/blockchain/log").json()
        assert len(log_after) == count_before + 1

        # Step 6: Verify the newest block matches the prediction
        newest_block = log_after[0]  # Newest first (reversed order)
        assert newest_block["blockNumber"] == prediction["blockNumber"]
        assert newest_block["prediction"] == "Spam"
        assert newest_block["confidence"] == prediction["confidence"]

    def test_ham_prediction_creates_blockchain_entry(self, client):
        """Submit ham email → verify prediction + blockchain block created."""
        log_before = client.get("/api/blockchain/log").json()
        count_before = len(log_before)

        ham_payload = {
            "text": "Hi Professor, I have completed the assignment and attached the final report. "
                    "Please let me know if any revisions are needed. Thank you."
        }
        res = client.post("/api/predict", json=ham_payload)
        assert res.status_code == 200
        prediction = res.json()

        assert prediction["prediction"] == "Ham"
        assert 0.50 <= prediction["confidence"] <= 1.0
        assert prediction["features"]["linkCount"] == 0  # No URLs
        assert prediction["features"]["exclamationCount"] == 0

        log_after = client.get("/api/blockchain/log").json()
        assert len(log_after) == count_before + 1

        newest_block = log_after[0]
        assert newest_block["prediction"] == "Ham"

    def test_multiple_predictions_maintain_chain_integrity(self, client):
        """Submit multiple predictions → verify entire chain remains valid."""
        emails = [
            {"text": "Team meeting at 3 PM today in conference room B. Please bring your notes."},
            {"text": "URGENT! Your bank account has been compromised! Click here to verify NOW!"},
            {"text": "Hey, want to grab lunch tomorrow? That new Italian place looks good."},
        ]

        for email in emails:
            res = client.post("/api/predict", json=email)
            assert res.status_code == 200

        # Verify the full chain integrity after multiple writes
        verify_res = client.post(
            "/api/blockchain/verify",
            json={"simulate_tamper": False}
        )
        assert verify_res.status_code == 200
        assert verify_res.json()["valid"] is True


# =============================================================================
# Chain Verification & Tamper Detection
# =============================================================================

class TestChainIntegrity:
    """Tests for blockchain chain verification and tamper simulation."""

    def test_chain_valid_without_tampering(self, client):
        verify = client.post("/api/blockchain/verify", json={"simulate_tamper": False})
        assert verify.status_code == 200
        data = verify.json()
        assert data["valid"] is True
        assert "tampered_block" not in data or data.get("tampered_block") is None

    def test_simulate_tamper_detects_corruption(self, client):
        verify = client.post("/api/blockchain/verify", json={"simulate_tamper": True})
        assert verify.status_code == 200
        data = verify.json()
        assert data["valid"] is False
        # Check that tampered block is identified (either key format)
        tampered = data.get("tamperedBlock") or data.get("tampered_block")
        assert tampered is not None
        assert isinstance(tampered, int)
        assert tampered >= 1  # Never genesis block

    def test_chain_recovers_after_simulated_tamper(self, client):
        """After tamper simulation, chain should auto-restore and remain valid."""
        # First simulate tampering
        client.post("/api/blockchain/verify", json={"simulate_tamper": True})

        # Then verify it's valid again (restore happened automatically)
        verify = client.post("/api/blockchain/verify", json={"simulate_tamper": False})
        assert verify.status_code == 200
        assert verify.json()["valid"] is True


# =============================================================================
# Blockchain Log Format & Ordering
# =============================================================================

class TestBlockchainLogFormat:
    """Tests for blockchain log endpoint data format and ordering."""

    def test_log_entries_are_newest_first(self, client):
        log = client.get("/api/blockchain/log").json()
        if len(log) >= 2:
            # Block numbers should be in descending order (newest first)
            for i in range(len(log) - 1):
                assert log[i]["blockNumber"] > log[i + 1]["blockNumber"]

    def test_log_excludes_genesis_block(self, client):
        log = client.get("/api/blockchain/log").json()
        for block in log:
            assert block["prediction"].lower() != "genesis"
            assert block["blockNumber"] >= 1

    def test_log_entry_data_contract(self, client):
        log = client.get("/api/blockchain/log").json()
        assert isinstance(log, list)
        if len(log) > 0:
            entry = log[0]
            required_keys = [
                "blockNumber", "timestamp", "emailHash",
                "prediction", "confidence", "blockHash", "previousHash"
            ]
            for key in required_keys:
                assert key in entry, f"Missing key: {key}"

            assert isinstance(entry["blockNumber"], int)
            assert isinstance(entry["confidence"], (int, float))
            assert entry["emailHash"].startswith("0x")
            assert entry["prediction"] in ["Spam", "Ham"]
            assert 0.0 <= entry["confidence"] <= 1.0


# =============================================================================
# Model Comparison Data Contract
# =============================================================================

class TestModelComparisonIntegration:
    """Tests for model comparison endpoint data integrity."""

    def test_returns_top_three_models(self, client):
        res = client.get("/api/models/comparison")
        assert res.status_code == 200
        models = res.json()
        assert isinstance(models, list)
        assert 1 <= len(models) <= 3

    def test_exactly_one_selected_model(self, client):
        models = client.get("/api/models/comparison").json()
        selected = [m for m in models if m.get("selected")]
        assert len(selected) == 1
        assert selected[0]["name"] == "Random Forest"

    def test_models_sorted_by_f1_descending(self, client):
        models = client.get("/api/models/comparison").json()
        f1_scores = [m["f1Score"] for m in models]
        assert f1_scores == sorted(f1_scores, reverse=True)

    def test_model_metrics_within_valid_range(self, client):
        models = client.get("/api/models/comparison").json()
        for model in models:
            for metric in ["accuracy", "precision", "recall", "f1Score"]:
                value = model[metric]
                assert 0.0 <= value <= 1.0, (
                    f"{model['name']}.{metric} = {value} is out of range [0, 1]"
                )


# =============================================================================
# Input Validation & Error Handling
# =============================================================================

class TestInputValidationIntegration:
    """Tests for API input validation and error responses."""

    def test_empty_text_returns_400(self, client):
        res = client.post("/api/predict", json={"text": ""})
        assert res.status_code == 400
        assert "empty" in res.json()["detail"].lower()

    def test_whitespace_only_text_returns_400(self, client):
        res = client.post("/api/predict", json={"text": "    \t\n   "})
        assert res.status_code == 400

    def test_oversized_text_returns_400(self, client):
        oversized = "A" * 50_001
        res = client.post("/api/predict", json={"text": oversized})
        assert res.status_code == 400
        assert "exceeds maximum allowed length" in res.json()["detail"]

    def test_text_at_max_boundary_succeeds(self, client):
        boundary = "Hello world. " * 3846  # ~49998 chars (under 50K)
        boundary = boundary[:50_000]
        res = client.post("/api/predict", json=boundary[:50_000])
        # This sends malformed JSON (string instead of object), expect 422
        # Let's fix: send proper payload
        res = client.post("/api/predict", json={"text": boundary})
        assert res.status_code == 200

    def test_missing_text_field_returns_422(self, client):
        res = client.post("/api/predict", json={"email": "Hello"})
        assert res.status_code == 422  # Pydantic validation error

    def test_verify_missing_body_uses_default(self, client):
        # Empty body should default simulate_tamper=False
        res = client.post("/api/blockchain/verify", json={})
        assert res.status_code == 200
        assert res.json()["valid"] is True


# =============================================================================
# Health Check Integration
# =============================================================================

class TestHealthCheckIntegration:
    """Tests for health check endpoint integration."""

    def test_health_reports_blockchain_length(self, client):
        health = client.get("/api/health").json()
        log = client.get("/api/blockchain/log").json()

        # Blockchain length includes genesis block, log excludes it
        assert health["blockchain_length"] == len(log) + 1

    def test_health_confirms_model_loaded(self, client):
        health = client.get("/api/health").json()
        assert health["model_loaded"] is True
        assert health["status"] == "healthy"

