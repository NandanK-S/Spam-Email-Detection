"""
run_pipeline.py — Master Pipeline Runner

Runs all ML pipeline steps in order:
    Step 1: Data Loading & Cleaning        (01_preprocessing.py)
    Step 3: Train/Test Split               (02_split_balance.py)
    Step 4: Combined Feature Extraction    (03_feature_matrix.py)
    Step 5: Train & Compare Models         (04_train_compare.py)
    Step 6: Inference Test                 (inference.py)

Usage:
    cd ml
    python run_pipeline.py

NOTE: Step 2 (structural feature engineering) is implemented in features.py
and is called by 01_preprocessing.py — there's no separate script for it.
"""

import time
import sys
import os

# Ensure we're running from the ml directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def run_step(step_name: str, module_func):
    """Run a pipeline step with timing and error handling."""
    print(f"\n\n{'#' * 80}")
    print(f"# {step_name}")
    print(f"{'#' * 80}")
    
    start = time.time()
    try:
        module_func()
        elapsed = time.time() - start
        print(f"\n⏱️  {step_name} completed in {elapsed:.2f}s")
    except Exception as e:
        elapsed = time.time() - start
        print(f"\n❌ {step_name} FAILED after {elapsed:.2f}s")
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    pipeline_start = time.time()
    
    print("=" * 80)
    print("🚀 ML PIPELINE — AI-Based Spam Email Detection")
    print("=" * 80)
    print(f"   Python: {sys.version}")
    print(f"   Working directory: {os.getcwd()}")
    
    # Step 1: Preprocessing
    from importlib import import_module
    
    step1 = import_module("01_preprocessing")
    run_step("STEP 1: Data Loading & Cleaning", step1.preprocess)
    
    # Step 3: Train/Test Split
    step3 = import_module("02_split_balance")
    run_step("STEP 3: Train/Test Split", step3.split_data)
    
    # Step 4: Feature Matrix
    step4 = import_module("03_feature_matrix")
    run_step("STEP 4: Combined Feature Extraction", step4.build_feature_matrices)
    
    # Step 5: Train & Compare
    step5 = import_module("04_train_compare")
    run_step("STEP 5: Train & Compare Models", step5.train_and_compare)
    
    # Step 6: Inference Test
    step6 = import_module("inference")
    print(f"\n\n{'#' * 80}")
    print(f"# STEP 6: Inference Module Test")
    print(f"{'#' * 80}")
    
    start = time.time()
    # Run the inference test
    test_cases = [
        ("SPAM", "CONGRATULATIONS!!! You've WON £1000 CASH! Call NOW: 09061234567 to claim! http://free-prizes.com"),
        ("HAM", "Hey, are we still meeting for lunch tomorrow? I was thinking the Italian place."),
    ]
    
    print("\n🧪 Testing predict_email() function...")
    for expected, text in test_cases:
        result = step6.predict_email(text)
        icon = "🚫" if result["prediction"] == "spam" else "✅"
        match = "✓" if result["prediction"].upper() == expected else "✗ UNEXPECTED"
        print(f"\n   {icon} [{expected}] → {result['prediction'].upper()} "
              f"(confidence: {result['confidence']:.4f}) {match}")
        print(f"      Features: {result['features']}")
    
    elapsed = time.time() - start
    print(f"\n⏱️  Inference test completed in {elapsed:.2f}s")
    
    # Final summary
    total_elapsed = time.time() - pipeline_start
    print(f"\n\n{'=' * 80}")
    print(f"✅ FULL PIPELINE COMPLETED SUCCESSFULLY")
    print(f"{'=' * 80}")
    print(f"   Total time: {total_elapsed:.2f}s")
    print(f"\n   Artifacts saved in: {os.path.join(os.getcwd(), 'artifacts')}")
    print(f"   - best_model.pkl         (selected best model)")
    print(f"   - baseline_model.pkl     (TF-IDF only baseline)")
    print(f"   - tfidf_vectorizer.pkl   (fitted TF-IDF vectorizer)")
    print(f"   - scaler.pkl             (fitted StandardScaler)")
    print(f"   - model_comparison.json  (full comparison results)")
    print(f"\n   Next step: Build FastAPI backend that imports predict_email()")
    print(f"   from ml/inference.py")


if __name__ == "__main__":
    main()
