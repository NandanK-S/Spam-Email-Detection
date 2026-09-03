/**
 * Mock API Layer
 * ──────────────
 * ALL fake data and simulated async functions live here.
 * To swap to a real backend, replace the internals of each function
 * with a real fetch() call — no component changes needed.
 *
 * Example swap:
 *   Before:  return new Promise(resolve => setTimeout(() => resolve(data), 1000));
 *   After:   return fetch("http://localhost:8000/predict", { method: "POST", body: JSON.stringify({ text }) }).then(r => r.json());
 */

// ─── Helper: simulate network delay ───
function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// ─── Helper: generate a fake SHA-256-ish hash ───
function fakeHash() {
  const chars = "0123456789abcdef";
  let hash = "";
  for (let i = 0; i < 64; i++) {
    hash += chars[Math.floor(Math.random() * chars.length)];
  }
  return hash;
}

// ─── 1. Predict Email ───
export async function mockPredictEmail(text) {
  await delay(1200);

  const lowerText = text.toLowerCase();

  // Simple keyword heuristic for demo realism
  const spamKeywords = [
    "win money",
    "click here",
    "free gift",
    "congratulations",
    "lottery",
    "act now",
    "limited time",
    "buy now",
    "discount",
    "offer expires",
    "no obligation",
    "risk free",
    "winner",
    "urgent",
    "claim your prize",
  ];

  const hasUrl = /https?:\/\/|www\.|\.com|\.net|\.org/i.test(text);
  let spamScore = hasUrl ? 0.3 : 0.05;

  for (const keyword of spamKeywords) {
    if (lowerText.includes(keyword)) {
      spamScore += 0.15;
    }
  }

  // Capital letter ratio boost
  const capitalRatio =
    text.length > 0
      ? (text.replace(/[^A-Z]/g, "").length / text.length)
      : 0;
  if (capitalRatio > 0.3) spamScore += 0.2;

  spamScore = Math.min(spamScore, 0.98);

  const isSpam = spamScore > 0.5;
  const confidence = isSpam
    ? Math.round((0.7 + Math.random() * 0.28) * 100) / 100
    : Math.round((0.65 + Math.random() * 0.3) * 100) / 100;

  // Feature extraction
  const charCount = text.length;
  const wordCount = text.trim().split(/\s+/).filter(Boolean).length;
  const linkCount = (text.match(/https?:\/\/[^\s]+|www\.[^\s]+/gi) || []).length;
  const punctuationCount = (text.match(/[!?,.:;'"()\-]/g) || []).length;

  return {
    prediction: isSpam ? "Spam" : "Ham",
    confidence,
    features: {
      charCount,
      wordCount,
      linkCount,
      capitalRatio: Math.round(capitalRatio * 10000) / 100,
      punctuationCount,
    },
    emailHash: fakeHash(),
  };
}

// ─── 2. Blockchain Log ───
const INITIAL_LOG = [
  {
    blockNumber: 1,
    timestamp: "2025-01-15 09:23:11",
    emailHash: "a3f9d2e8b7c14f6a9d0e3b5c8f2a1d7e4b6c9f0a2d5e8b1c4f7a0d3e6b9c2f5",
    prediction: "Spam",
    confidence: 0.94,
  },
  {
    blockNumber: 2,
    timestamp: "2025-01-15 10:45:33",
    emailHash: "7b2e4f6a8c0d1e3f5a7b9c1d3e5f7a9b1c3d5e7f9a1b3c5d7e9f1a3b5c7d9e1",
    prediction: "Spam",
    confidence: 0.87,
  },
  {
    blockNumber: 3,
    timestamp: "2025-01-16 14:12:07",
    emailHash: "c8d1e3f5a7b9c1d3e5f7a9b1c3d5e7f9a1b3c5d7e9f1a3b5c7d9e1f3a5b7c9d",
    prediction: "Spam",
    confidence: 0.91,
  },
  {
    blockNumber: 4,
    timestamp: "2025-01-17 08:56:44",
    emailHash: "1f3a5b7c9d1e3f5a7b9c1d3e5f7a9b1c3d5e7f9a1b3c5d7e9f1a3b5c7d9e1f3",
    prediction: "Spam",
    confidence: 0.96,
  },
  {
    blockNumber: 5,
    timestamp: "2025-01-18 16:34:29",
    emailHash: "e9f1a3b5c7d9e1f3a5b7c9d1e3f5a7b9c1d3e5f7a9b1c3d5e7f9a1b3c5d7e9f1",
    prediction: "Spam",
    confidence: 0.82,
  },
];

export async function mockGetBlockchainLog() {
  await delay(600);
  return [...INITIAL_LOG];
}

// ─── 3. Chain Verification ───
export async function mockVerifyChain(simulateTamper = false) {
  await delay(1500);

  if (simulateTamper) {
    const tamperedBlock = Math.floor(Math.random() * 5) + 1;
    return {
      valid: false,
      tamperedBlock,
    };
  }

  return {
    valid: true,
    tamperedBlock: null,
  };
}

// ─── 4. Model Comparison ───
export async function mockGetModelComparison() {
  await delay(400);

  return [
    {
      name: "Logistic Regression",
      accuracy: 0.952,
      precision: 0.948,
      recall: 0.939,
      f1Score: 0.943,
      selected: false,
    },
    {
      name: "Naive Bayes",
      accuracy: 0.934,
      precision: 0.921,
      recall: 0.947,
      f1Score: 0.934,
      selected: false,
    },
    {
      name: "SVM (RBF Kernel)",
      accuracy: 0.971,
      precision: 0.968,
      recall: 0.962,
      f1Score: 0.965,
      selected: true,
    },
  ];
}
