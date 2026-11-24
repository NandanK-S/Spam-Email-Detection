<div align="center">

# 🛡️ AI-Based Spam Email Detection
### with Blockchain Tamper-Proof Audit Logging

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Next.js](https://img.shields.io/badge/Next.js-15-000000?style=for-the-badge&logo=nextdotjs&logoColor=white)](https://nextjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.3+-F7931E?style=for-the-badge&logo=scikitlearn&logoColor=white)](https://scikit-learn.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

<br/>

> **🎓 Final Year Engineering Project** — B.E. (7th Semester)  
> *Combining Machine Learning, Heuristic Analysis, and Blockchain Integrity to build a production-grade email threat detection system.*

<br/>

```
Accuracy: 99.23%  |  F1-Score: 96.95%  |  Precision: 98.45%  |  Recall: 95.49%
```

</div>

---

## 📌 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [ML Pipeline](#-ml-pipeline)
- [Model Performance](#-model-performance)
- [Project Structure](#-project-structure)
- [Tech Stack](#-tech-stack)
- [Getting Started](#-getting-started)
- [API Reference](#-api-reference)
- [Testing](#-testing)
- [Security Hardening](#-security-hardening)
- [Blockchain Logging](#-blockchain-logging)
- [Team & Academic Context](#-team--academic-context)

---

## 🔍 Overview

This project implements a **full-stack AI Spam Email detection system** that classifies emails as spam or legitimate in real time. What sets it apart from conventional solutions is the integration of a **custom blockchain layer** that creates an immutable, tamper-evident audit trail of every prediction — ensuring forensic accountability alongside intelligent classification.

The system is built as a production-grade web application with a **Next.js** frontend, a **FastAPI** inference server, and a 7-stage ML pipeline trained on thousands of real emails.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🤖 **AI Classification** | Random Forest model with TF-IDF + 11 handcrafted heuristic features |
| 🔗 **Blockchain Audit Log** | SHA-256 chained blocks — tamper-proof, immutable prediction history |
| 🔍 **Chain Verification** | Real-time integrity check across the full blockchain |
| 📊 **Model Comparison** | Live dashboard comparing 5 ML models across 2 balancing strategies |
| 🧩 **Feature Breakdown** | Transparent view of every feature that influenced each prediction |
| 🛡️ **Security Hardened** | Input sanitization, HTTP security headers, timeout guards, error masking |
| ⚡ **High Performance** | Model comparison caching, paginated blockchain log, concurrent-safe writes |
| ✅ **76 Automated Tests** | Unit, integration, E2E, security, and load tests |

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Next.js Frontend (Port 3000)            │
│  EmailInputForm → PredictionResult → FeatureBreakdownTable  │
│  BlockchainLog (paginated) → ChainVerifyPanel               │
│  ModelComparisonCard                                         │
└──────────────────────┬──────────────────────────────────────┘
                       │  HTTP (Next.js API Proxy Routes)
                       ▼
┌─────────────────────────────────────────────────────────────┐
│               FastAPI Backend (Port 8000)                   │
│                                                             │
│  POST /predict   ──► inference.py                           │
│                       ├─ features.py  (11 features)         │
│                       ├─ TF-IDF vectorizer                  │
│                       ├─ StandardScaler                     │
│                       └─ Random Forest model                │
│                                                             │
│  GET  /blockchain/log    ──► blockchain.py                  │
│  POST /blockchain/verify ──► SHA-256 chain check            │
│  GET  /models/comparison ──► model_comparison.json (cached) │
└─────────────────────────────────────────────────────────────┘
                       │
                       ▼
              ml/data/blockchain.json
              (SHA-256 Chained Blocks)
```

---

## 🧠 ML Pipeline

The ML pipeline is split into **4 sequential stages**, each implemented as a standalone script for reproducibility:

```
Stage 1: 01_preprocessing.py
         Raw email data → cleaned text, label encoding
         (Includes transactional email samples to prevent false positives)

Stage 2: 02_split_balance.py
         Train/Test split → SMOTE oversampling + class_weight strategies

Stage 3: 03_feature_matrix.py
         TF-IDF vectorization (top 5000 terms) + 11 heuristic features
         → Sparse combined feature matrix (scipy.sparse)

Stage 4: 04_train_compare.py
         Trains 5 models × 2 balancing strategies = 10 experiments
         → Selects best by F1-score → saves artifacts
```

**Run the full pipeline:**
```bash
cd ml
python run_pipeline.py
```

### Heuristic Features (11 total)

| # | Feature | Description |
|---|---|---|
| 1 | `url_count` | Number of hyperlinks in the email |
| 2 | `has_suspicious_url` | Presence of IP-based or shortened URLs |
| 3 | `exclamation_count` | Exclamation mark frequency |
| 4 | `caps_ratio` | Ratio of uppercase characters |
| 5 | `spam_word_count` | Whole-word spam keyword matches |
| 6 | `phishing_word_count` | Phishing-specific keyword matches |
| 7 | `has_html` | Detects HTML markup in email body |
| 8 | `word_count` | Total word count |
| 9 | `avg_word_length` | Average length of words |
| 10 | `urgency_word_count` | Urgency trigger words (whole-word boundary) |
| 11 | `sensitive_word_count` | Sensitive information request patterns |

> **Note:** All keyword matching uses whole-word boundary regex (`\b`) to prevent false positives (e.g., "pin" inside "shopping" will not trigger a match).

---

## 📈 Model Performance

All 10 experiments from the final training run:

| Model | Balancing | Accuracy | Precision | Recall | F1-Score |
|---|---|---|---|---|---|
| **Random Forest** | **class_weight** | **99.23%** | **98.45%** | **95.49%** | **96.95% ✅** |
| Random Forest | SMOTE | 99.23% | 100.00% | 93.98% | 96.90% |
| SVM (Linear) | class_weight | 98.85% | 96.90% | 93.98% | 95.42% |
| Gradient Boosting | class_weight | 98.85% | 96.18% | 94.74% | 95.45% |
| SVM (Linear) | SMOTE | 98.65% | 96.85% | 92.48% | 94.62% |
| Logistic Regression | class_weight | 98.37% | 92.65% | 94.74% | 93.68% |
| Logistic Regression | SMOTE | 98.27% | 92.59% | 93.98% | 93.28% |
| Multinomial NB | class_weight | 97.31% | 83.87% | 97.74% | 90.28% |
| Multinomial NB | SMOTE | 96.92% | 83.44% | 94.74% | 88.73% |
| Baseline (LR + TF-IDF only) | — | 96.63% | 99.00% | 74.44% | 84.98% |

> Best model selected by **F1-Score** to balance precision and recall on imbalanced email data.

---

## 📁 Project Structure

```
major-project/
├── app/                          # Next.js 15 Frontend
│   ├── page.js                   # Main application page
│   ├── layout.js                 # Root layout & metadata
│   ├── globals.css               # Global styles (Tailwind CSS)
│   ├── components/
│   │   ├── EmailInputForm.jsx    # Email submission form
│   │   ├── PredictionResult.jsx  # Classification result display
│   │   ├── FeatureBreakdownTable.jsx  # Per-feature explanation
│   │   ├── BlockchainLog.jsx     # Paginated audit log viewer
│   │   ├── ChainVerifyPanel.jsx  # Blockchain integrity verifier
│   │   ├── ModelComparisonCard.jsx    # Model metrics dashboard
│   │   └── Header.jsx            # App header
│   ├── api/                      # Next.js proxy API routes
│   │   ├── predict/route.js      # → FastAPI /predict
│   │   ├── blockchain/
│   │   │   ├── log/route.js      # → FastAPI /blockchain/log
│   │   │   └── verify/route.js   # → FastAPI /blockchain/verify
│   │   └── models/comparison/route.js  # → FastAPI /models/comparison
│   └── lib/
│       ├── api.js                # Shared API client helpers
│       └── api.test.mjs          # JS API unit tests (Node.js)
│
├── ml/                           # Python ML Backend
│   ├── 01_preprocessing.py       # Data cleaning & label encoding
│   ├── 02_split_balance.py       # Train/test split & SMOTE
│   ├── 03_feature_matrix.py      # TF-IDF + heuristic feature matrix
│   ├── 04_train_compare.py       # Multi-model training & comparison
│   ├── run_pipeline.py           # Orchestrates full ML pipeline
│   ├── features.py               # Heuristic feature extraction
│   ├── inference.py              # Prediction & thresholding logic
│   ├── backend.py                # FastAPI server
│   ├── blockchain.py             # SHA-256 blockchain implementation
│   ├── requirements.txt          # Python dependencies
│   ├── artifacts/                # Trained model artifacts
│   │   ├── best_model.pkl        # Trained Random Forest
│   │   ├── best_model_meta.pkl   # Model metadata & metrics
│   │   ├── scaler.pkl            # StandardScaler
│   │   ├── tfidf_vectorizer.pkl  # Fitted TF-IDF vectorizer
│   │   └── model_comparison.json # All 10 experiment results
│   └── tests/                    # Automated test suite
│       ├── test_features.py      # Feature extraction tests
│       ├── test_inference.py     # Inference & thresholding tests
│       ├── test_blockchain.py    # Blockchain integrity tests
│       ├── test_backend.py       # FastAPI endpoint tests
│       ├── test_integration.py   # End-to-end integration tests
│       ├── test_security.py      # Security & hardening tests
│       └── run_load_test.py      # Concurrent load test
│
├── next.config.mjs               # Next.js config & HTTP security headers
├── package.json                  # Node.js dependencies
└── .gitignore
```

---

## 🛠️ Tech Stack

### Backend / ML
| Technology | Version | Purpose |
|---|---|---|
| Python | 3.11+ | Core ML & backend language |
| FastAPI | 0.110+ | REST API inference server |
| scikit-learn | 1.3+ | ML models & preprocessing |
| imbalanced-learn | 0.11+ | SMOTE oversampling |
| NumPy / SciPy | Latest | Numerical computing |
| Pandas | 2.0+ | Data manipulation |
| Joblib | 1.3+ | Model artifact serialization |
| Uvicorn | 0.27+ | ASGI server |

### Frontend
| Technology | Version | Purpose |
|---|---|---|
| Next.js | 15 | React framework with App Router |
| React | 19 | UI component library |
| Tailwind CSS | 4 | Utility-first styling |

### Infrastructure & Quality
| Technology | Purpose |
|---|---|
| SHA-256 (hashlib) | Blockchain block hashing |
| threading.RLock | Concurrent-safe blockchain writes |
| pytest + httpx | Python testing (67 tests) |
| Node.js test runner | JavaScript testing (9 tests) |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- npm / pnpm

### 1. Clone the Repository
```bash
git clone https://github.com/NandanK-S/Spam-Email-Detection.git
cd Spam-Email-Detection
```

### 2. Set Up the Python Backend
```bash
cd ml
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Train the ML Models *(optional — artifacts already included)*
```bash
python run_pipeline.py
```

### 4. Start the FastAPI Server
```bash
uvicorn backend:app --reload --port 8000
```

### 5. Set Up & Start the Frontend
```bash
# From the project root
npm install
npm run dev
```

### 6. Open the App
Visit **http://localhost:3000** in your browser.

---

## 📡 API Reference

All endpoints are served by FastAPI on `http://localhost:8000`.

### `POST /predict`
Classifies an email as spam or ham.

**Request Body:**
```json
{
  "text": "Congratulations! You've won a $1000 gift card. Click here to claim now!"
}
```

**Response:**
```json
{
  "label": "spam",
  "confidence": 0.94,
  "features": {
    "url_count": 1,
    "spam_word_count": 3,
    "urgency_word_count": 1,
    ...
  },
  "block_hash": "a3f8c2..."
}
```

### `GET /blockchain/log`
Returns the full paginated audit log of all predictions.

### `POST /blockchain/verify`
Verifies the integrity of the entire blockchain (detects tampering).

### `GET /models/comparison`
Returns performance metrics for all 10 trained model experiments.

---

## 🧪 Testing

The project has **76 automated tests** across 7 test files.

### Run Python Tests
```bash
cd ml
pytest tests/ -v
```

**Test Coverage:**
- `test_features.py` — Heuristic feature extraction & edge cases
- `test_inference.py` — Model prediction, threshold logic, legitimate cues
- `test_blockchain.py` — Block creation, SHA-256 chaining, tamper detection
- `test_backend.py` — FastAPI endpoint contracts & error handling
- `test_integration.py` — End-to-end prediction → blockchain flow
- `test_security.py` — Input sanitization, oversized payloads, injection attempts

### Run JavaScript Tests
```bash
# From project root
node --test app/lib/api.test.mjs
```

### Run Load Test
```bash
cd ml
python tests/run_load_test.py
```

---

## 🔐 Security Hardening

The system was designed with security in mind across all layers:

- **Input Sanitization:** All prediction endpoints sanitize and size-limit inputs before processing
- **Error Masking:** Internal error details are never exposed to API consumers
- **HTTP Security Headers:** `Content-Security-Policy`, `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy` configured in `next.config.mjs`
- **Request Timeouts:** All Next.js proxy routes enforce 10-second upstream timeouts
- **Atomic File Writes:** Blockchain JSON uses atomic write with retry backoff (prevents corruption under concurrent load)
- **Thread Safety:** `threading.RLock` guards all blockchain read/write operations
- **Tamper Simulation Gating:** Tamper simulation endpoints are disabled in production via environment flag

---

## 🔗 Blockchain Logging

Every email classification is logged as an immutable block:

```json
{
  "index": 42,
  "timestamp": "2026-11-24T14:30:00Z",
  "data": {
    "label": "spam",
    "confidence": 0.94,
    "text_preview": "Congratulations! You've won..."
  },
  "previous_hash": "a3f8c2d1...",
  "hash": "b7e9f4a2..."
}
```

Each block's `hash` is computed from its index, timestamp, data, and `previous_hash` using **SHA-256** — making any retrospective tampering immediately detectable via the `/blockchain/verify` endpoint.

---

## 👥 Team & Academic Context

<div align="center">

| Field | Details |
|---|---|
| 🎓 **Degree** | Bachelor of Engineering (B.E) |
| 📅 **Academic Year** | Final Year - 7th Semester, 2026 |
| 🏫 **Domain** | Cybersecurity and Blockchain |
| 🧑‍💻 **Developers** | [Nandan K S](https://github.com/NandanK-S) , [Akash D B](https://github.com/Akash-D-B) , [Basavaraj P](https://github.com/BasavarajPatali96)
| 📦 **Repository** | [Spam-Email-Detection](https://github.com/NandanK-S/Spam-Email-Detection) |

</div>

This project was developed as part of the **Final Year Major Project** requirement, demonstrating the integration of:
- Applied Machine Learning (classification, NLP, feature engineering)
- Distributed system concepts (blockchain audit trails)
- Full-stack web development (Next.js + FastAPI)
- Software engineering best practices (testing, security, CI-readiness)




---

<div align="center">

**Built with ❤️ as a Final Year Engineering Project**

*If you found this project useful or interesting, consider giving it a ⭐ on GitHub!*

</div>
