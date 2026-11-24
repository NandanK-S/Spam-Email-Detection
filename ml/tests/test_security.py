"""
test_security.py — Security audit regression tests covering Phase 4 findings.
"""

import os
import sys
import threading
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend import app
import backend
from blockchain import Blockchain


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


class TestSecurityHardening:
    """Regression tests for Phase 4 security findings."""

    def test_oversized_payload_rejection(self, client):
        """SEC-01: Rejection of payloads exceeding MAX_EMAIL_LENGTH."""
        oversized = "Spam test content " * 3000  # > 50,000 characters
        res = client.post("/api/predict", json={"text": oversized})
        assert res.status_code == 400
        assert "exceeds maximum allowed length" in res.json()["detail"]

    def test_simulate_tamper_environment_gating(self, client, monkeypatch):
        """SEC-04: Verify simulate_tamper can be disabled in production via env var."""
        monkeypatch.setenv("ALLOW_TAMPER_SIMULATION", "false")
        res = client.post("/api/blockchain/verify", json={"simulate_tamper": True})
        assert res.status_code == 403
        assert "disabled" in res.json()["detail"].lower()

        # Re-enabled verification
        monkeypatch.setenv("ALLOW_TAMPER_SIMULATION", "true")
        res_allowed = client.post("/api/blockchain/verify", json={"simulate_tamper": True})
        assert res_allowed.status_code == 200

    def test_error_message_sanitization(self, client, monkeypatch):
        """SEC-05: Ensure internal exceptions do not leak stack traces or system paths."""
        def broken_predict(text):
            raise RuntimeError("Database connection string postgresql://user:secret@internal-db:5432/db")

        monkeypatch.setattr(backend, "predict_email", broken_predict)
        res = client.post("/api/predict", json={"text": "Normal email text"})
        assert res.status_code == 500
        # Check that secret details/file paths are NOT leaked in response
        assert "postgresql://" not in res.json()["detail"]
        assert "internal-db" not in res.json()["detail"]
        assert res.json()["detail"] == "Internal prediction service error"

    def test_concurrent_blockchain_writes_thread_safety(self, tmp_path):
        """SEC-06 & SEC-07: Verify concurrent writes do not corrupt the blockchain or crash."""
        temp_dir = str(tmp_path / "chain_data")
        bc = Blockchain(data_dir=temp_dir)
        errors = []

        def worker(idx):
            try:
                bc.add_block(f"email_{idx}@example.com", "spam", 0.9)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        # Re-load from disk to verify atomic persistence and integrity
        reloaded = Blockchain(data_dir=temp_dir)
        assert len(reloaded.chain) == 11  # 1 genesis + 10 blocks
        verification = reloaded.verify_chain()
        assert verification["valid"] is True

