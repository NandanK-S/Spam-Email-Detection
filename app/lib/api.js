/**
 * api.js — Real API client for the FastAPI backend.
 *
 * Calls Next.js API proxy routes (which forward to FastAPI at localhost:8000).
 * This avoids CORS issues entirely since all requests stay on the same origin.
 */

const API_BASE = "/api";

/**
 * Predict whether an email is spam or ham.
 * @param {string} text - The email text to classify.
 * @returns {Promise<{prediction: string, confidence: number, emailHash: string, features: object, blockNumber: number}>}
 */
export async function predictEmail(text) {
  const res = await fetch(`${API_BASE}/predict`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Prediction failed" }));
    throw new Error(err.detail || "Prediction failed");
  }

  return res.json();
}

/**
 * Fetch the full blockchain audit log.
 * @returns {Promise<Array<{blockNumber: number, timestamp: string, emailHash: string, prediction: string, confidence: number}>>}
 */
export async function getBlockchainLog() {
  const res = await fetch(`${API_BASE}/blockchain/log`);

  if (!res.ok) {
    throw new Error("Failed to fetch blockchain log");
  }

  return res.json();
}

/**
 * Verify blockchain chain integrity.
 * @param {boolean} simulateTamper - If true, simulate tampering for demo.
 * @returns {Promise<{valid: boolean, tampered_block?: number}>}
 */
export async function verifyChain(simulateTamper = false) {
  const res = await fetch(`${API_BASE}/blockchain/verify`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ simulate_tamper: simulateTamper }),
  });

  if (!res.ok) {
    throw new Error("Chain verification failed");
  }

  return res.json();
}

/**
 * Fetch model comparison data from the training pipeline.
 * @returns {Promise<Array<{name: string, accuracy: number, precision: number, recall: number, f1Score: number, selected: boolean}>>}
 */
export async function getModelComparison() {
  const res = await fetch(`${API_BASE}/models/comparison`);

  if (!res.ok) {
    throw new Error("Failed to fetch model comparison");
  }

  return res.json();
}
