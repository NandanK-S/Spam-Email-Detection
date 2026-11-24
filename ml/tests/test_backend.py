"""
test_backend.py — Unit tests for FastAPI REST API endpoints using TestClient.
"""

import sys
import os
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend import app, blockchain
import backend


@pytest.fixture(scope="module")
def client():
    """Create FastAPI TestClient."""
    with TestClient(app) as c:
        yield c


class TestBackendAPI:
    """Tests for FastAPI endpoints."""

    def test_health_check(self, client):
        res = client.get("/api/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "healthy"
        assert "blockchain_length" in data
        assert data["model_loaded"] is True

    def test_model_comparison_endpoint(self, client):
        res = client.get("/api/models/comparison")
        assert res.status_code == 200
        data = res.json()
        assert isinstance(data, list)
        assert len(data) <= 3
        if len(data) > 0:
            first = data[0]
            assert "name" in first
            assert "method" in first
            assert "accuracy" in first
            assert "precision" in first
            assert "recall" in first
            assert "f1Score" in first
            assert "selected" in first

    def test_blockchain_log_endpoint(self, client):
        res = client.get("/api/blockchain/log")
        assert res.status_code == 200
        data = res.json()
        assert isinstance(data, list)
        for block in data:
            assert "blockNumber" in block
            assert "timestamp" in block
            assert "emailHash" in block
            assert "prediction" in block
            assert "confidence" in block

    def test_predict_validation_empty_text(self, client):
        res = client.post("/api/predict", json={"text": ""})
        assert res.status_code == 400
        assert "empty" in res.json()["detail"].lower()

        res_ws = client.post("/api/predict", json={"text": "    "})
        assert res_ws.status_code == 400

    def test_predict_validation_max_length(self, client):
        oversized = "A" * 50_001
        res = client.post("/api/predict", json={"text": oversized})
        assert res.status_code == 400
        assert "exceeds maximum allowed length" in res.json()["detail"]

    def test_predict_success_and_chain_logging(self, client):
        initial_log = client.get("/api/blockchain/log").json()
        initial_count = len(initial_log)

        payload = {
            "text": "Project meeting scheduled for tomorrow at 10 AM. Please bring your slides."
        }
        res = client.post("/api/predict", json=payload)
        assert res.status_code == 200
        body = res.json()

        assert body["prediction"] in ["Spam", "Ham"]
        assert 0.0 <= body["confidence"] <= 1.0
        assert "features" in body
        assert "charCount" in body["features"]
        assert "urgencyWordCount" in body["features"]
        assert "emailHash" in body
        assert "blockNumber" in body

        # Verify a new block was added to the audit log
        updated_log = client.get("/api/blockchain/log").json()
        assert len(updated_log) == initial_count + 1

    def test_blockchain_verify_endpoint(self, client):
        # Verify valid chain
        res = client.post("/api/blockchain/verify", json={"simulate_tamper": False})
        assert res.status_code == 200
        assert res.json()["valid"] is True

        # Verify simulated tamper
        res_tamper = client.post("/api/blockchain/verify", json={"simulate_tamper": True})
        assert res_tamper.status_code == 200
        data_tamper = res_tamper.json()
        assert data_tamper["valid"] is False
        assert "tampered_block" in data_tamper or "tamperedBlock" in data_tamper
