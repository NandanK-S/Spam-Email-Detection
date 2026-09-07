"""
04_train_compare.py — Step 5: Train & Compare Models

Trains 3 classifiers × 2 balancing strategies (6 runs) + 1 baseline (7 total).
Evaluates each on the held-out test set, prints a summary comparison table,
and saves the best model + baseline model.

Models:
    1. Logistic Regression
    2. Multinomial Naive Bayes (uses MaxAbsScaler for non-negative features)
    3. SVM (linear kernel, probability=True)

Balancing Strategies:
    A. SMOTE-balanced training data
    B. class_weight='balanced' (no SMOTE)

Baseline:
    TF-IDF only + Logistic Regression (no structural features, no balancing)

Input:  ml/data/X_*.npz, ml/data/y_*.npy
Output: ml/artifacts/best_model.pkl, ml/artifacts/baseline_model.pkl,
        ml/artifacts/model_comparison.json
"""

import os
import sys
import json
import numpy as np
import joblib
import scipy.sparse as sp
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.preprocessing import MaxAbsScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report
)


def load_matrices(data_dir: str):
    """Load all feature matrices and labels."""
    data = {}
    matrix_files = {
        "X_train_combined": "X_train_combined.npz",
        "X_train_smote": "X_train_smote.npz",
        "X_test_combined": "X_test_combined.npz",
        "X_train_tfidf": "X_train_tfidf.npz",
        "X_test_tfidf": "X_test_tfidf.npz",
    }
    label_files = {
        "y_train": "y_train.npy",
        "y_train_smote": "y_train_smote.npy",
        "y_test": "y_test.npy",
    }
    
    for key, filename in matrix_files.items():
        path = os.path.join(data_dir, filename)
        if not os.path.exists(path):
            print(f"❌ ERROR: {path} not found. Run 03_feature_matrix.py first.")
            sys.exit(1)
        data[key] = sp.load_npz(path)
    
    for key, filename in label_files.items():
        path = os.path.join(data_dir, filename)
        if not os.path.exists(path):
            print(f"❌ ERROR: {path} not found. Run 03_feature_matrix.py first.")
            sys.exit(1)
        data[key] = np.load(path)
    
    return data


def evaluate_model(model, X_test, y_test, model_name: str, method: str) -> dict:
    """Evaluate a trained model and return metrics dict."""
    y_pred = model.predict(X_test)
    
    # Metrics focused on spam class (label=0)
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, pos_label=0, zero_division=0)
    rec = recall_score(y_test, y_pred, pos_label=0, zero_division=0)
    f1 = f1_score(y_test, y_pred, pos_label=0, zero_division=0)
    cm = confusion_matrix(y_test, y_pred)
    
    return {
        "model": model_name,
        "method": method,
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1_score": round(f1, 4),
        "confusion_matrix": cm.tolist(),
    }


def train_and_compare(data_dir: str = None, artifacts_dir: str = None):
    """
    Train all model combinations, evaluate, compare, and save the best.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    if data_dir is None:
        data_dir = os.path.join(base_dir, "data")
    if artifacts_dir is None:
        artifacts_dir = os.path.join(base_dir, "artifacts")
    
    os.makedirs(artifacts_dir, exist_ok=True)
    
    print("\n" + "=" * 70)
    print("STEP 5: TRAIN & COMPARE MODELS")
    print("=" * 70)
    
    # Load matrices
    print(f"\n📂 Loading feature matrices...")
    data = load_matrices(data_dir)
    
    X_train = data["X_train_combined"]       # Imbalanced
    X_train_smote = data["X_train_smote"]    # SMOTE-balanced
    X_test = data["X_test_combined"]
    y_train = data["y_train"]
    y_train_smote = data["y_train_smote"]
    y_test = data["y_test"]
    X_train_tfidf = data["X_train_tfidf"]    # For baseline
    X_test_tfidf = data["X_test_tfidf"]
    
    print(f"   X_train: {X_train.shape}, X_train_smote: {X_train_smote.shape}")
    print(f"   X_test: {X_test.shape}")
    print(f"   X_train_tfidf (baseline): {X_train_tfidf.shape}")
    
    results = []
    trained_models = {}
    
    # =========================================================================
    # Define model configurations
    # =========================================================================
    
    # For MultinomialNB, features must be non-negative.
    # StandardScaler output can be negative, and SMOTE interpolation can also
    # produce negatives. We apply MaxAbsScaler then clip any remaining negatives
    # to zero on the sparse matrix's internal data array.
    
    # Pre-scale data for NB (make non-negative)
    max_abs_scaler = MaxAbsScaler()
    X_train_nb = sp.csr_matrix(max_abs_scaler.fit_transform(X_train))
    X_train_smote_nb = sp.csr_matrix(max_abs_scaler.transform(X_train_smote))
    X_test_nb = sp.csr_matrix(max_abs_scaler.transform(X_test))
    
    # Clip any remaining negative values to 0 (required by MultinomialNB)
    X_train_nb.data = np.maximum(X_train_nb.data, 0)
    X_train_smote_nb.data = np.maximum(X_train_smote_nb.data, 0)
    X_test_nb.data = np.maximum(X_test_nb.data, 0)
    X_train_nb.eliminate_zeros()
    X_train_smote_nb.eliminate_zeros()
    X_test_nb.eliminate_zeros()
    
    configs = [
        # (name, model_class, kwargs, uses_nb_data)
        ("Logistic Regression", LogisticRegression, {"max_iter": 1000, "random_state": 42}, False),
        ("Multinomial NB", MultinomialNB, {}, True),
        ("SVM (Linear)", SVC, {"kernel": "linear", "probability": True, "random_state": 42}, False),
        ("Random Forest", RandomForestClassifier, {"n_estimators": 200, "random_state": 42, "n_jobs": -1}, False),
        ("Gradient Boosting", HistGradientBoostingClassifier, {"max_iter": 200, "random_state": 42}, False),
    ]
    
    # =========================================================================
    # Train each model with SMOTE + class_weight='balanced'
    # =========================================================================
    
    for model_name, model_cls, base_kwargs, uses_nb_data in configs:
        for method, X_tr, y_tr in [
            ("SMOTE", X_train_smote if not uses_nb_data else X_train_smote_nb, y_train_smote),
            ("class_weight", X_train if not uses_nb_data else X_train_nb, y_train),
        ]:
            # Configure class_weight for non-SMOTE runs
            kwargs = base_kwargs.copy()
            if method == "class_weight":
                if model_name == "Multinomial NB":
                    # NB doesn't support class_weight; use class_prior instead
                    # Set equal priors to simulate balanced classes
                    kwargs["class_prior"] = [0.5, 0.5]
                elif model_name == "Gradient Boosting":
                    # HistGradientBoostingClassifier uses class_weight parameter
                    kwargs["class_weight"] = "balanced"
                else:
                    kwargs["class_weight"] = "balanced"
            
            print(f"\n{'─'*60}")
            print(f"🏋️ Training: {model_name} [{method}]")
            print(f"{'─'*60}")
            
            model = model_cls(**kwargs)
            
            X_te = X_test_nb if uses_nb_data else X_test
            
            # HistGradientBoostingClassifier needs dense numpy arrays
            X_tr_fit = X_tr
            X_te_eval = X_te
            if model_name == "Gradient Boosting":
                X_tr_fit = X_tr.toarray() if sp.issparse(X_tr) else X_tr
                X_te_eval = X_te.toarray() if sp.issparse(X_te) else X_te
            
            model.fit(X_tr_fit, y_tr)
            result = evaluate_model(model, X_te_eval, y_test, model_name, method)
            results.append(result)
            trained_models[f"{model_name}_{method}"] = model
            
            # Print confusion matrix
            cm = np.array(result["confusion_matrix"])
            print(f"   Accuracy:  {result['accuracy']:.4f}")
            print(f"   Precision: {result['precision']:.4f} (spam class)")
            print(f"   Recall:    {result['recall']:.4f} (spam class)")
            print(f"   F1-Score:  {result['f1_score']:.4f} (spam class)")
            print(f"   Confusion Matrix:")
            print(f"                 Predicted")
            print(f"              spam    ham")
            print(f"   Actual spam  {cm[0][0]:5d}  {cm[0][1]:5d}")
            print(f"   Actual ham   {cm[1][0]:5d}  {cm[1][1]:5d}")
    
    # =========================================================================
    # Baseline: TF-IDF only + Logistic Regression (no structural, no balancing)
    # =========================================================================
    print(f"\n{'─'*60}")
    print(f"🏋️ Training: BASELINE (TF-IDF only + Logistic Regression)")
    print(f"{'─'*60}")
    
    baseline_model = LogisticRegression(max_iter=1000, random_state=42)
    baseline_model.fit(X_train_tfidf, y_train)
    baseline_result = evaluate_model(baseline_model, X_test_tfidf, y_test, "Baseline (LR + TF-IDF only)", "none")
    results.append(baseline_result)
    
    cm = np.array(baseline_result["confusion_matrix"])
    print(f"   Accuracy:  {baseline_result['accuracy']:.4f}")
    print(f"   Precision: {baseline_result['precision']:.4f} (spam class)")
    print(f"   Recall:    {baseline_result['recall']:.4f} (spam class)")
    print(f"   F1-Score:  {baseline_result['f1_score']:.4f} (spam class)")
    print(f"   Confusion Matrix:")
    print(f"                 Predicted")
    print(f"              spam    ham")
    print(f"   Actual spam  {cm[0][0]:5d}  {cm[0][1]:5d}")
    print(f"   Actual ham   {cm[1][0]:5d}  {cm[1][1]:5d}")
    
    # =========================================================================
    # Summary Comparison Table
    # =========================================================================
    print(f"\n\n{'='*80}")
    print(f"📊 MODEL COMPARISON SUMMARY TABLE")
    print(f"{'='*80}")
    print(f"{'Model':<35s} {'Method':<14s} {'Acc':>7s} {'Prec':>7s} {'Rec':>7s} {'F1':>7s}")
    print(f"{'─'*35} {'─'*14} {'─'*7} {'─'*7} {'─'*7} {'─'*7}")
    
    for r in results:
        print(f"{r['model']:<35s} {r['method']:<14s} "
              f"{r['accuracy']:>7.4f} {r['precision']:>7.4f} "
              f"{r['recall']:>7.4f} {r['f1_score']:>7.4f}")
    
    # =========================================================================
    # Select Best Model (by F1-score on spam class)
    # =========================================================================
    # Exclude baseline from best selection (it's saved separately)
    enhanced_results = [r for r in results if r['model'] != "Baseline (LR + TF-IDF only)"]
    best = max(enhanced_results, key=lambda r: r['f1_score'])
    
    print(f"\n{'='*80}")
    print(f"🏆 BEST MODEL SELECTED")
    print(f"{'='*80}")
    print(f"   Model:    {best['model']}")
    print(f"   Method:   {best['method']}")
    print(f"   F1-Score: {best['f1_score']:.4f} (spam class)")
    print(f"   Reason:   Highest F1-score on the spam class among all 6 runs")
    
    # Save best model
    best_key = f"{best['model']}_{best['method']}"
    best_model = trained_models[best_key]
    best_model_path = os.path.join(artifacts_dir, "best_model.pkl")
    joblib.dump(best_model, best_model_path)
    print(f"\n💾 Saved best model to: {best_model_path}")
    
    # Save metadata about which model was selected
    best_meta = {
        "model_name": best['model'],
        "balancing_method": best['method'],
        "uses_nb_data": "Multinomial NB" in best['model'],
        "metrics": {
            "accuracy": best['accuracy'],
            "precision": best['precision'],
            "recall": best['recall'],
            "f1_score": best['f1_score'],
        }
    }
    joblib.dump(best_meta, os.path.join(artifacts_dir, "best_model_meta.pkl"))
    
    # Save MaxAbsScaler if NB was selected (needed for inference)
    if best_meta["uses_nb_data"]:
        joblib.dump(max_abs_scaler, os.path.join(artifacts_dir, "max_abs_scaler.pkl"))
        print(f"   ✅ MaxAbsScaler saved (required for NB model)")
    
    # Save baseline model
    baseline_path = os.path.join(artifacts_dir, "baseline_model.pkl")
    joblib.dump(baseline_model, baseline_path)
    print(f"💾 Saved baseline model to: {baseline_path}")
    
    # Save full comparison as JSON (for potential frontend consumption)
    comparison_path = os.path.join(artifacts_dir, "model_comparison.json")
    # Convert results for JSON serialization
    json_results = []
    for r in results:
        jr = r.copy()
        jr.pop("confusion_matrix")  # Not needed in JSON
        json_results.append(jr)
    
    with open(comparison_path, 'w') as f:
        json.dump({
            "results": json_results,
            "best_model": best_meta,
        }, f, indent=2)
    print(f"💾 Saved comparison results to: {comparison_path}")
    
    return results, best


if __name__ == "__main__":
    train_and_compare()
