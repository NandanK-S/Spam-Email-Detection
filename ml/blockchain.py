"""
blockchain.py — Simple Blockchain for Tamper-Proof Logging

Implements a basic blockchain where each block records an email prediction.
Uses SHA-256 hashing and chain verification to detect tampering.

Persistence: JSON file at ml/data/blockchain.json
"""

import hashlib
import json
import os
import time
from datetime import datetime, timezone


class Block:
    """A single block in the blockchain."""
    
    def __init__(self, index: int, timestamp: str, email_hash: str,
                 prediction: str, confidence: float, previous_hash: str,
                 nonce: int = 0, block_hash: str = None):
        self.index = index
        self.timestamp = timestamp
        self.email_hash = email_hash
        self.prediction = prediction
        self.confidence = confidence
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = block_hash or self.compute_hash()
    
    def compute_hash(self) -> str:
        """Compute SHA-256 hash of the block's contents."""
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "email_hash": self.email_hash,
            "prediction": self.prediction,
            "confidence": self.confidence,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def to_dict(self) -> dict:
        """Serialize block to dictionary."""
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "email_hash": self.email_hash,
            "prediction": self.prediction,
            "confidence": self.confidence,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "hash": self.hash,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Block":
        """Deserialize block from dictionary."""
        return cls(
            index=data["index"],
            timestamp=data["timestamp"],
            email_hash=data["email_hash"],
            prediction=data["prediction"],
            confidence=data["confidence"],
            previous_hash=data["previous_hash"],
            nonce=data.get("nonce", 0),
            block_hash=data["hash"],
        )


class Blockchain:
    """
    Simple blockchain for tamper-proof email prediction logging.
    
    Each block records:
        - Email hash (SHA-256 of the email text)
        - Prediction (spam/ham)
        - Confidence score
        - Timestamp
        - Link to previous block (previous_hash)
    """
    
    DIFFICULTY = 2  # Number of leading zeros required in hash (simple proof-of-work)
    
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
        self.data_dir = data_dir
        self.chain_file = os.path.join(data_dir, "blockchain.json")
        self.chain: list[Block] = []
        self._load_chain()
    
    def _load_chain(self):
        """Load chain from disk, or create genesis block if none exists."""
        if os.path.exists(self.chain_file):
            try:
                with open(self.chain_file, 'r') as f:
                    data = json.load(f)
                self.chain = [Block.from_dict(b) for b in data]
                if len(self.chain) == 0:
                    self._create_genesis_block()
            except (json.JSONDecodeError, KeyError):
                self._create_genesis_block()
        else:
            self._create_genesis_block()
    
    def _create_genesis_block(self):
        """Create the first block in the chain."""
        genesis = Block(
            index=0,
            timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
            email_hash="0" * 64,
            prediction="genesis",
            confidence=1.0,
            previous_hash="0" * 64,
        )
        self.chain = [genesis]
        self._save_chain()
    
    def _save_chain(self):
        """Persist chain to disk."""
        os.makedirs(self.data_dir, exist_ok=True)
        with open(self.chain_file, 'w') as f:
            json.dump([b.to_dict() for b in self.chain], f, indent=2)
    
    def _proof_of_work(self, block: Block) -> Block:
        """Simple proof-of-work: find a nonce that makes the hash start with DIFFICULTY zeros."""
        block.nonce = 0
        computed_hash = block.compute_hash()
        prefix = "0" * self.DIFFICULTY
        while not computed_hash.startswith(prefix):
            block.nonce += 1
            computed_hash = block.compute_hash()
        block.hash = computed_hash
        return block
    
    @staticmethod
    def hash_email(text: str) -> str:
        """Generate SHA-256 hash of email text."""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()
    
    def add_block(self, email_text: str, prediction: str, confidence: float) -> dict:
        """
        Add a new block logging an email prediction.
        
        Args:
            email_text: Raw email text (will be hashed).
            prediction: "spam" or "ham".
            confidence: Model confidence score (0.0-1.0).
        
        Returns:
            Dictionary representation of the new block.
        """
        last_block = self.chain[-1]
        
        new_block = Block(
            index=len(self.chain),
            timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
            email_hash=self.hash_email(email_text),
            prediction=prediction,
            confidence=round(confidence, 4),
            previous_hash=last_block.hash,
        )
        
        # Apply proof-of-work
        new_block = self._proof_of_work(new_block)
        
        self.chain.append(new_block)
        self._save_chain()
        
        return new_block.to_dict()
    
    def get_chain(self) -> list[dict]:
        """Return the full chain as a list of dicts (excluding genesis block)."""
        return [b.to_dict() for b in self.chain[1:]]  # Skip genesis
    
    def verify_chain(self) -> dict:
        """
        Verify the integrity of the entire chain.
        
        Returns:
            {"valid": True} if chain is intact, or
            {"valid": False, "tampered_block": index} if tampering detected.
        """
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]
            
            # Check if current block's hash is correct
            if current.hash != current.compute_hash():
                return {"valid": False, "tampered_block": current.index}
            
            # Check if current block points to previous block's hash
            if current.previous_hash != previous.hash:
                return {"valid": False, "tampered_block": current.index}
        
        return {"valid": True}
    
    def simulate_tamper(self) -> int:
        """
        Simulate tampering for demonstration purposes.
        Modifies a random non-genesis block's data without updating its hash.
        
        Returns:
            Index of the tampered block.
        """
        import random
        if len(self.chain) <= 1:
            # Need at least one non-genesis block; add a fake one
            self.add_block("test@tamper.com", "spam", 0.99)
        
        # Pick a random non-genesis block
        idx = random.randint(1, len(self.chain) - 1)
        # Corrupt the prediction (change without recomputing hash)
        original = self.chain[idx].prediction
        self.chain[idx].prediction = "TAMPERED"
        # Don't recompute hash — this is the tampering
        
        return idx
    
    def restore_chain(self):
        """Restore chain from disk (undo in-memory tampering)."""
        self._load_chain()


if __name__ == "__main__":
    print("=" * 60)
    print("BLOCKCHAIN MODULE TEST")
    print("=" * 60)
    
    # Use a temp directory for testing
    bc = Blockchain()
    
    # Add some blocks
    b1 = bc.add_block("CONGRATULATIONS! You WON!", "spam", 0.95)
    print(f"\n✅ Block added: #{b1['index']} — {b1['prediction']} (conf: {b1['confidence']})")
    print(f"   Hash: {b1['hash'][:16]}...")
    
    b2 = bc.add_block("Hey, lunch tomorrow?", "ham", 0.92)
    print(f"✅ Block added: #{b2['index']} — {b2['prediction']} (conf: {b2['confidence']})")
    print(f"   Hash: {b2['hash'][:16]}...")
    
    # Verify chain
    result = bc.verify_chain()
    print(f"\n🔒 Chain verification: {'VALID ✓' if result['valid'] else 'INVALID ✗'}")
    
    # Simulate tampering
    tampered_idx = bc.simulate_tamper()
    print(f"\n⚠️  Simulated tampering on block #{tampered_idx}")
    
    result = bc.verify_chain()
    if result['valid']:
        print("🔒 Chain verification: VALID ✓")
    else:
        tb = result['tampered_block']
        print(f"🔒 Chain verification: INVALID ✗ — tampered block #{tb}")
    
    # Restore
    bc.restore_chain()
    result = bc.verify_chain()
    print(f"🔒 After restore: {'VALID ✓' if result['valid'] else 'INVALID ✗'}")
    
    print(f"\n📋 Full chain ({len(bc.get_chain())} blocks):")
    for block in bc.get_chain():
        print(f"   #{block['index']} | {block['timestamp']} | {block['prediction']} | {block['hash'][:12]}...")
