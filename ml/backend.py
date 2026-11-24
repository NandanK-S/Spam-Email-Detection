"""
backend.py — FastAPI Backend for AI-Based Spam Email Detection

Endpoints:
    POST /api/predict        — Predict spam/ham and log to blockchain
    GET  /api/blockchain/log — Get the full blockchain audit log
    POST /api/blockchain/verify — Verify chain integrity
    GET  /api/models/comparison — Get model comparison data

Usage:
    cd ml
    .\\venv\\Scripts\\Activate
    uvicorn backend:app --reload --port 8000
"""

import os
import sys
import json
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Ensure ml directory is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from inference import predict_email
from blockchain import Blockchain


# =============================================================================
# Lifespan — initialize blockchain on startup
# =============================================================================

blockchain = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the blockchain on startup."""
    global blockchain
    blockchain = Blockchain()
    print("🔗 Blockchain initialized")
    print(f"   Chain length: {len(blockchain.chain)} blocks")
    
    # Pre-load ML artifacts by making a dummy prediction
    try:
        predict_email("test")
        print("🤖 ML model loaded successfully")
    except Exception as e:
        print(f"⚠️  ML model load warning: {e}")
    
    yield
    
    # Cleanup
    print("👋 Shutting down...")


# =============================================================================
# FastAPI App
# =============================================================================

app = FastAPI(
    title="Spam Detection API",
    description="AI-Based Spam Email Detection with Blockchain Tamper-Proof Logging",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow Next.js dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# Request/Response Models
# =============================================================================

class PredictRequest(BaseModel):
    text: str


class VerifyRequest(BaseModel):
    simulate_tamper: bool = False


# Maximum allowable payload length for email analysis (50 KB)
MAX_EMAIL_LENGTH = 50_000


# =============================================================================
# Endpoints
# =============================================================================

@app.post("/api/predict")
async def api_predict(request: PredictRequest):
    """
    Predict whether an email is spam or ham.
    Logs the prediction to the blockchain.
    """
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="Email text cannot be empty")
    
    if len(request.text) > MAX_EMAIL_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Email text exceeds maximum allowed length of {MAX_EMAIL_LENGTH} characters"
        )
    
    try:
        # Run ML prediction
        result = predict_email(request.text)
        
        # Log to blockchain (all predictions, not just spam)
        block = blockchain.add_block(
            email_text=request.text,
            prediction=result["prediction"],
            confidence=result["confidence"],
        )
        
        return {
            "prediction": result["prediction"].capitalize(),  # "Spam" or "Ham"
            "confidence": result["confidence"],
            "features": {
                "charCount": result["features"]["char_count"],
                "wordCount": result["features"]["word_count"],
                "linkCount": result["features"]["link_count"],
                "capitalRatio": round(result["features"]["capital_ratio"] * 100, 2),
                "punctuationCount": result["features"]["punctuation_count"],
                "digitCount": result["features"]["digit_count"],
                "specialCharCount": result["features"]["special_char_count"],
                "avgWordLength": result["features"]["avg_word_length"],
                "exclamationCount": result["features"]["exclamation_count"],
                "urgencyWordCount": result["features"].get("urgency_word_count", 0),
                "sensitiveWordCount": result["features"].get("sensitive_word_count", 0),
            },
            "emailHash": "0x" + block["email_hash"][:40],
            "blockNumber": block["index"],
            "blockHash": block["hash"],
        }
    except HTTPException:
        raise
    except Exception as e:
        import logging
        logging.error(f"Internal prediction error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal prediction service error")


@app.get("/api/blockchain/log")
async def api_blockchain_log():
    """Get the full blockchain audit log (excluding genesis block)."""
    chain = blockchain.get_chain()
    
    # Format for frontend
    blocks = []
    for block in reversed(chain):  # Newest first
        blocks.append({
            "blockNumber": block["index"],
            "timestamp": block["timestamp"],
            "emailHash": "0x" + block["email_hash"][:40],
            "prediction": block["prediction"].capitalize(),
            "confidence": block["confidence"],
            "blockHash": block["hash"],
            "previousHash": block["previous_hash"],
        })
    
    return blocks


@app.post("/api/blockchain/verify")
async def api_blockchain_verify(request: VerifyRequest):
    """
    Verify blockchain chain integrity.
    Optionally simulate tampering for demonstration (can be disabled via ALLOW_TAMPER_SIMULATION=false).
    """
    if request.simulate_tamper:
        allow_tamper = os.getenv("ALLOW_TAMPER_SIMULATION", "true").lower() in ("true", "1", "yes")
        if not allow_tamper:
            raise HTTPException(status_code=403, detail="Tamper simulation is disabled in this environment")
        # Simulate tampering in memory (doesn't persist)
        tampered_idx = blockchain.simulate_tamper()
        result = blockchain.verify_chain()
        # Restore the chain after simulation
        blockchain.restore_chain()
        if not result.get("valid", True):
            result["tamperedBlock"] = result.get("tampered_block")
        return result
    else:
        result = blockchain.verify_chain()
        if not result.get("valid", True):
            result["tamperedBlock"] = result.get("tampered_block")
        return result


_model_comparison_cache = None


@app.get("/api/models/comparison")
async def api_model_comparison():
    """Return model comparison data from the training pipeline (cached in memory)."""
    global _model_comparison_cache
    if _model_comparison_cache is not None:
        return _model_comparison_cache

    artifacts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "artifacts")
    comparison_path = os.path.join(artifacts_dir, "model_comparison.json")
    
    if not os.path.exists(comparison_path):
        raise HTTPException(
            status_code=404,
            detail="Model comparison data not found. Run the training pipeline first."
        )
    
    with open(comparison_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    best_model_name = data.get("best_model", {}).get("model_name", "")
    best_method = data.get("best_model", {}).get("balancing_method", "")
    
    # Pick the best run per distinct model (exclude baseline, choose highest F1)
    best_per_model = {}
    for result in data["results"]:
        name = result["model"]
        if name.startswith("Baseline"):
            continue
        if name not in best_per_model or result["f1_score"] > best_per_model[name]["f1_score"]:
            best_per_model[name] = result
    
    # Sort models by F1-score descending and select top 3 (ensures selected best model is included)
    sorted_models = sorted(best_per_model.values(), key=lambda x: x["f1_score"], reverse=True)
    top_3 = sorted_models[:3]
    
    # Format for frontend ModelComparisonCard component
    models = []
    for result in top_3:
        models.append({
            "name": result["model"],
            "method": result["method"],
            "accuracy": result["accuracy"],
            "precision": result["precision"],
            "recall": result["recall"],
            "f1Score": result["f1_score"],
            "selected": (result["model"] == best_model_name and 
                        result["method"] == best_method),
        })
    
    _model_comparison_cache = models
    return models


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "blockchain_length": len(blockchain.chain),
        "model_loaded": True,
    }
