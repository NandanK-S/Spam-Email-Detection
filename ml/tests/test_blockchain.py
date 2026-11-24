"""
test_blockchain.py — Unit tests for Blockchain data structure, PoW, verification, and persistence.
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from blockchain import Block, Blockchain


class TestBlock:
    """Tests for individual Block data structure and hashing."""

    def test_block_compute_hash_length(self):
        b = Block(
            index=1,
            timestamp="2026-10-30 12:00:00",
            email_hash="a" * 64,
            prediction="spam",
            confidence=0.95,
            previous_hash="0" * 64,
            nonce=0,
        )
        h = b.compute_hash()
        assert len(h) == 64
        assert int(h, 16) > 0

    def test_block_hash_determinism(self):
        b1 = Block(1, "2026-10-30 12:00:00", "a" * 64, "spam", 0.95, "0" * 64, 42)
        b2 = Block(1, "2026-10-30 12:00:00", "a" * 64, "spam", 0.95, "0" * 64, 42)
        assert b1.compute_hash() == b2.compute_hash()

    def test_block_hash_avalanche_effect(self):
        base = Block(1, "2026-10-30 12:00:00", "a" * 64, "spam", 0.95, "0" * 64, 0)
        h_base = base.compute_hash()

        # Changing prediction
        b_pred = Block(1, "2026-10-30 12:00:00", "a" * 64, "ham", 0.95, "0" * 64, 0)
        assert b_pred.compute_hash() != h_base

        # Changing confidence slightly
        b_conf = Block(1, "2026-10-30 12:00:00", "a" * 64, "spam", 0.96, "0" * 64, 0)
        assert b_conf.compute_hash() != h_base

        # Changing nonce
        b_nonce = Block(1, "2026-10-30 12:00:00", "a" * 64, "spam", 0.95, "0" * 64, 1)
        assert b_nonce.compute_hash() != h_base

    def test_block_dict_serialization_roundtrip(self):
        orig = Block(2, "2026-10-30 12:30:00", "b" * 64, "ham", 0.88, "c" * 64, 100)
        d = orig.to_dict()
        restored = Block.from_dict(d)

        assert restored.index == orig.index
        assert restored.timestamp == orig.timestamp
        assert restored.email_hash == orig.email_hash
        assert restored.prediction == orig.prediction
        assert restored.confidence == orig.confidence
        assert restored.previous_hash == orig.previous_hash
        assert restored.nonce == orig.nonce
        assert restored.hash == orig.hash


class TestBlockchain:
    """Tests for Blockchain operations with isolated temporary directories."""

    @pytest.fixture
    def test_chain(self, tmp_path):
        """Creates an isolated Blockchain in a temporary directory."""
        return Blockchain(data_dir=str(tmp_path))

    def test_genesis_block_creation(self, test_chain):
        assert len(test_chain.chain) == 1
        genesis = test_chain.chain[0]
        assert genesis.index == 0
        assert genesis.prediction == "genesis"
        assert genesis.confidence == 1.0
        assert genesis.previous_hash == "0" * 64
        assert genesis.email_hash == "0" * 64

    def test_add_block_and_proof_of_work(self, test_chain):
        block_dict = test_chain.add_block(
            email_text="Special discount offer!",
            prediction="spam",
            confidence=0.9823,
        )

        assert len(test_chain.chain) == 2
        assert block_dict["index"] == 1
        assert block_dict["prediction"] == "spam"
        assert block_dict["confidence"] == 0.9823
        assert block_dict["previous_hash"] == test_chain.chain[0].hash
        # Proof-of-work difficulty check (leading zeros)
        assert block_dict["hash"].startswith("0" * test_chain.DIFFICULTY)

    def test_get_chain_excludes_genesis(self, test_chain):
        test_chain.add_block("Email 1", "spam", 0.90)
        test_chain.add_block("Email 2", "ham", 0.85)

        chain_list = test_chain.get_chain()
        assert len(chain_list) == 2
        assert chain_list[0]["index"] == 1
        assert chain_list[1]["index"] == 2

    def test_verify_chain_on_valid_chain(self, test_chain):
        test_chain.add_block("Email 1", "spam", 0.90)
        test_chain.add_block("Email 2", "ham", 0.85)
        test_chain.add_block("Email 3", "spam", 0.99)

        result = test_chain.verify_chain()
        assert result == {"valid": True}

    def test_verify_chain_detects_data_tampering(self, test_chain):
        test_chain.add_block("Email 1", "spam", 0.90)
        test_chain.add_block("Email 2", "ham", 0.85)

        # Deliberately mutate data in block 1 without updating hash
        test_chain.chain[1].prediction = "ham"

        result = test_chain.verify_chain()
        assert result["valid"] is False
        assert result["tampered_block"] == 1

    def test_verify_chain_detects_broken_link(self, test_chain):
        test_chain.add_block("Email 1", "spam", 0.90)
        test_chain.add_block("Email 2", "ham", 0.85)

        # Alter the previous_hash link
        test_chain.chain[2].previous_hash = "f" * 64
        # Recompute hash so block 2 hash matches its content, but link to block 1 is broken
        test_chain.chain[2].hash = test_chain.chain[2].compute_hash()

        result = test_chain.verify_chain()
        assert result["valid"] is False
        assert result["tampered_block"] == 2

    def test_simulate_tamper_and_restore(self, test_chain):
        test_chain.add_block("Email 1", "spam", 0.90)
        test_chain.add_block("Email 2", "ham", 0.85)

        tampered_idx = test_chain.simulate_tamper()
        assert tampered_idx in [1, 2]

        result = test_chain.verify_chain()
        assert result["valid"] is False
        assert result["tampered_block"] == tampered_idx

        # Restore from disk
        test_chain.restore_chain()
        restored_result = test_chain.verify_chain()
        assert restored_result == {"valid": True}

    def test_persistence_reloads_chain(self, tmp_path):
        chain_dir = str(tmp_path)
        bc1 = Blockchain(data_dir=chain_dir)
        bc1.add_block("Persisted email", "spam", 0.95)

        # Create a second instance pointing to the same directory
        bc2 = Blockchain(data_dir=chain_dir)
        assert len(bc2.chain) == 2
        assert bc2.chain[1].prediction == "spam"
        assert bc2.chain[1].confidence == 0.95
        assert bc2.verify_chain() == {"valid": True}

