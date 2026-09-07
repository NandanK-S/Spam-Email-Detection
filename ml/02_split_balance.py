"""
02_split_balance.py — Step 3: Train/Test Split

Splits the processed dataset into 80/20 train/test sets with stratification.

NOTE on ordering: SMOTE is applied AFTER feature extraction (in 03_feature_matrix.py),
not here. This is intentional — SMOTE operates on the combined numeric feature space
(TF-IDF + structural features), not on raw text. This script only handles the split.

Input:  ml/data/processed.csv
Output: ml/data/train.csv, ml/data/test.csv
"""

import os
import sys
import pandas as pd
from sklearn.model_selection import train_test_split


def split_data(data_dir: str = None) -> tuple:
    """
    Perform stratified 80/20 train/test split.
    
    Returns:
        Tuple of (train_df, test_df).
    """
    if data_dir is None:
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    
    input_path = os.path.join(data_dir, "processed.csv")
    
    if not os.path.exists(input_path):
        print(f"\n❌ ERROR: Processed dataset not found at: {input_path}")
        print(f"   Run 01_preprocessing.py first.")
        sys.exit(1)
    
    print("\n" + "=" * 70)
    print("STEP 3: TRAIN/TEST SPLIT")
    print("=" * 70)
    
    # Load processed data
    df = pd.read_csv(input_path)
    print(f"\n📂 Loaded processed dataset: {df.shape}")
    
    # --- Print original class distribution ---
    print(f"\n📊 Full Dataset Class Distribution:")
    dist = df['label'].value_counts()
    for label, count in dist.items():
        pct = count / len(df) * 100
        print(f"   {label:>4s}: {count:5d} ({pct:.1f}%)")
    
    # --- Stratified 80/20 split ---
    train_df, test_df = train_test_split(
        df,
        test_size=0.2,
        random_state=42,
        stratify=df['label_num']
    )
    
    train_df = train_df.reset_index(drop=True)
    test_df = test_df.reset_index(drop=True)
    
    print(f"\n✂️  Split Results:")
    print(f"   Train set: {train_df.shape[0]} samples ({train_df.shape[0] / len(df) * 100:.1f}%)")
    print(f"   Test set:  {test_df.shape[0]} samples ({test_df.shape[0] / len(df) * 100:.1f}%)")
    
    # --- Print class distribution in each split ---
    print(f"\n📊 Train Set Class Distribution:")
    train_dist = train_df['label'].value_counts()
    for label, count in train_dist.items():
        pct = count / len(train_df) * 100
        print(f"   {label:>4s}: {count:5d} ({pct:.1f}%)")
    
    print(f"\n📊 Test Set Class Distribution:")
    test_dist = test_df['label'].value_counts()
    for label, count in test_dist.items():
        pct = count / len(test_df) * 100
        print(f"   {label:>4s}: {count:5d} ({pct:.1f}%)")
    
    # --- Save splits ---
    train_path = os.path.join(data_dir, "train.csv")
    test_path = os.path.join(data_dir, "test.csv")
    
    train_df.to_csv(train_path, index=False)
    test_df.to_csv(test_path, index=False)
    
    print(f"\n💾 Saved train set to: {train_path}")
    print(f"   Saved test set to:  {test_path}")
    
    # --- Note about SMOTE ---
    print(f"\n📌 NOTE: SMOTE balancing will be applied in 03_feature_matrix.py")
    print(f"   after TF-IDF + structural feature extraction, as it operates")
    print(f"   on the combined numeric feature space.")
    
    return train_df, test_df


if __name__ == "__main__":
    split_data()
