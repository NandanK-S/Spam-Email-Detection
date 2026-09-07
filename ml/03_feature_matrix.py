"""
03_feature_matrix.py — Step 4: Combined Feature Extraction

Builds the final feature matrices by combining TF-IDF vectors with
scaled structural features. Also applies SMOTE on the combined feature
space for the balanced training variant.

Input:  ml/data/train.csv, ml/data/test.csv
Output:
    - Feature matrices saved as .npz files in ml/data/
    - Fitted TfidfVectorizer → ml/artifacts/tfidf_vectorizer.pkl
    - Fitted StandardScaler  → ml/artifacts/scaler.pkl
"""

import os
import sys
import numpy as np
import pandas as pd
import joblib
import scipy.sparse as sp
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE


def build_feature_matrices(data_dir: str = None, artifacts_dir: str = None):
    """
    Build combined TF-IDF + structural feature matrices.
    
    Creates two training variants:
        (a) Raw imbalanced training data
        (b) SMOTE-balanced training data
    
    Both share the same test set.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    if data_dir is None:
        data_dir = os.path.join(base_dir, "data")
    if artifacts_dir is None:
        artifacts_dir = os.path.join(base_dir, "artifacts")
    
    os.makedirs(artifacts_dir, exist_ok=True)
    
    train_path = os.path.join(data_dir, "train.csv")
    test_path = os.path.join(data_dir, "test.csv")
    
    for path in [train_path, test_path]:
        if not os.path.exists(path):
            print(f"\n❌ ERROR: {path} not found. Run 02_split_balance.py first.")
            sys.exit(1)
    
    print("\n" + "=" * 70)
    print("STEP 4: COMBINED FEATURE EXTRACTION")
    print("=" * 70)
    
    # Load splits
    train_df = pd.read_csv(train_path)
    test_df = pd.read_csv(test_path)
    
    print(f"\n📂 Loaded train ({train_df.shape[0]} rows) and test ({test_df.shape[0]} rows)")
    
    # Fill any NaN in clean_message
    train_df['clean_message'] = train_df['clean_message'].fillna('')
    test_df['clean_message'] = test_df['clean_message'].fillna('')
    
    # =========================================================================
    # 1. TF-IDF Vectorization
    # =========================================================================
    print(f"\n🔤 Fitting TF-IDF Vectorizer (max_features=5000, ngram_range=(1,2), stop_words='english')...")
    tfidf = TfidfVectorizer(max_features=5000, ngram_range=(1, 2), stop_words='english')
    
    # Fit on training set ONLY, then transform both
    X_train_tfidf = tfidf.fit_transform(train_df['clean_message'])
    X_test_tfidf = tfidf.transform(test_df['clean_message'])
    
    print(f"   Train TF-IDF shape: {X_train_tfidf.shape}")
    print(f"   Test TF-IDF shape:  {X_test_tfidf.shape}")
    
    # =========================================================================
    # 2. Scale Structural Features
    # =========================================================================
    structural_cols = [
        'char_count', 'word_count', 'link_count', 'capital_ratio', 'punctuation_count',
        'digit_count', 'special_char_count', 'avg_word_length', 'exclamation_count',
        'urgency_word_count', 'sensitive_word_count'
    ]
    
    print(f"\n📐 Scaling structural features: {structural_cols}")
    scaler = StandardScaler()
    
    # Fit on training set ONLY, then transform both
    X_train_struct = scaler.fit_transform(train_df[structural_cols].values)
    X_test_struct = scaler.transform(test_df[structural_cols].values)
    
    print(f"   Train structural shape: {X_train_struct.shape}")
    print(f"   Test structural shape:  {X_test_struct.shape}")
    
    # =========================================================================
    # 3. Combine TF-IDF (sparse) + Structural (dense) via hstack
    # =========================================================================
    print(f"\n🔗 Combining TF-IDF + structural features via scipy.sparse.hstack...")
    
    X_train_combined = sp.hstack([X_train_tfidf, sp.csr_matrix(X_train_struct)])
    X_test_combined = sp.hstack([X_test_tfidf, sp.csr_matrix(X_test_struct)])
    
    y_train = train_df['label_num'].values
    y_test = test_df['label_num'].values
    
    print(f"   Combined train shape: {X_train_combined.shape}")
    print(f"   Combined test shape:  {X_test_combined.shape}")
    
    # =========================================================================
    # 4. Apply SMOTE on combined training features
    # =========================================================================
    print(f"\n⚖️  Applying SMOTE on combined training feature matrix...")
    print(f"   Class distribution BEFORE SMOTE:")
    unique, counts = np.unique(y_train, return_counts=True)
    for u, c in zip(unique, counts):
        label = "spam" if u == 0 else "ham"
        print(f"     {label} ({u}): {c} samples")
    
    smote = SMOTE(random_state=42)
    X_train_smote, y_train_smote = smote.fit_resample(X_train_combined, y_train)
    
    print(f"\n   Class distribution AFTER SMOTE:")
    unique, counts = np.unique(y_train_smote, return_counts=True)
    for u, c in zip(unique, counts):
        label = "spam" if u == 0 else "ham"
        print(f"     {label} ({u}): {c} samples")
    print(f"   SMOTE train shape: {X_train_smote.shape}")
    
    # =========================================================================
    # 5. Also create TF-IDF-only matrices (for baseline model)
    # =========================================================================
    print(f"\n📊 Creating TF-IDF-only matrices for baseline comparison...")
    print(f"   Baseline train shape: {X_train_tfidf.shape}")
    print(f"   Baseline test shape:  {X_test_tfidf.shape}")
    
    # =========================================================================
    # 6. Save everything
    # =========================================================================
    print(f"\n💾 Saving artifacts...")
    
    # Save fitted transformers
    joblib.dump(tfidf, os.path.join(artifacts_dir, "tfidf_vectorizer.pkl"))
    joblib.dump(scaler, os.path.join(artifacts_dir, "scaler.pkl"))
    print(f"   ✅ tfidf_vectorizer.pkl")
    print(f"   ✅ scaler.pkl")
    
    # Save feature matrices
    sp.save_npz(os.path.join(data_dir, "X_train_combined.npz"), sp.csr_matrix(X_train_combined))
    sp.save_npz(os.path.join(data_dir, "X_train_smote.npz"), sp.csr_matrix(X_train_smote))
    sp.save_npz(os.path.join(data_dir, "X_test_combined.npz"), sp.csr_matrix(X_test_combined))
    sp.save_npz(os.path.join(data_dir, "X_train_tfidf.npz"), sp.csr_matrix(X_train_tfidf))
    sp.save_npz(os.path.join(data_dir, "X_test_tfidf.npz"), sp.csr_matrix(X_test_tfidf))
    
    # Save labels
    np.save(os.path.join(data_dir, "y_train.npy"), y_train)
    np.save(os.path.join(data_dir, "y_train_smote.npy"), y_train_smote)
    np.save(os.path.join(data_dir, "y_test.npy"), y_test)
    
    print(f"   ✅ Feature matrices saved to {data_dir}")
    
    print(f"\n📋 Final Summary:")
    print(f"   {'Matrix':<25s} {'Shape':>20s}")
    print(f"   {'-'*25} {'-'*20}")
    print(f"   {'X_train_combined':<25s} {str(X_train_combined.shape):>20s}")
    print(f"   {'X_train_smote':<25s} {str(X_train_smote.shape):>20s}")
    print(f"   {'X_test_combined':<25s} {str(X_test_combined.shape):>20s}")
    print(f"   {'X_train_tfidf (baseline)':<25s} {str(X_train_tfidf.shape):>20s}")
    print(f"   {'X_test_tfidf (baseline)':<25s} {str(X_test_tfidf.shape):>20s}")
    
    return {
        "X_train_combined": X_train_combined,
        "X_train_smote": X_train_smote,
        "X_test_combined": X_test_combined,
        "X_train_tfidf": X_train_tfidf,
        "X_test_tfidf": X_test_tfidf,
        "y_train": y_train,
        "y_train_smote": y_train_smote,
        "y_test": y_test,
    }


if __name__ == "__main__":
    build_feature_matrices()
