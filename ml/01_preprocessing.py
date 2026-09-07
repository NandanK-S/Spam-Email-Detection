"""
01_preprocessing.py — Step 1: Data Loading & Cleaning

Loads the SMS Spam Collection dataset, cleans text, encodes labels,
extracts structural features, and saves the processed DataFrame.

Dataset: SMS Spam Collection (~5,572 rows)
    - Download from: https://www.kaggle.com/datasets/uciml/sms-spam-collection-dataset
    - Place as: ml/data/spam.csv
    - Expected format: CSV with columns 'v1' (label) and 'v2' (message)
      OR columns 'label' and 'message'

Output: ml/data/processed.csv
"""

import os
import sys
import pandas as pd

# Add the ml directory to path so we can import features
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from features import clean_text, extract_structural_features


def load_dataset(filepath: str) -> pd.DataFrame:
    """
    Load the SMS Spam Collection CSV.
    
    Handles multiple common formats:
      - Tab-separated with columns v1, v2 (original UCI format)
      - Comma-separated with columns label, message
    """
    # Try tab-separated first (original UCI format)
    try:
        df = pd.read_csv(filepath, sep='\t', header=None, names=['label', 'message'],
                         encoding='latin-1')
        if df['label'].isin(['ham', 'spam']).all():
            return df
    except Exception:
        pass
    
    # Try comma-separated with header
    try:
        df = pd.read_csv(filepath, encoding='latin-1')
        # Handle v1/v2 column names (Kaggle format)
        if 'v1' in df.columns and 'v2' in df.columns:
            df = df[['v1', 'v2']].rename(columns={'v1': 'label', 'v2': 'message'})
            return df
        elif 'label' in df.columns and 'message' in df.columns:
            return df[['label', 'message']]
    except Exception:
        pass
    
    raise ValueError(
        f"Could not parse {filepath}. Expected tab-separated (label\\tmessage) "
        f"or CSV with columns v1/v2 or label/message."
    )


def preprocess(data_dir: str = None) -> pd.DataFrame:
    """
    Full preprocessing pipeline:
    1. Load CSV
    2. Handle nulls and duplicates
    3. Store raw_message and clean_message
    4. Encode labels (spam=0, ham=1)
    5. Extract structural features
    6. Save processed.csv
    
    Returns:
        Processed DataFrame.
    """
    if data_dir is None:
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    
    filepath = os.path.join(data_dir, "spam.csv")
    
    if not os.path.exists(filepath):
        print(f"\n❌ ERROR: Dataset not found at: {filepath}")
        print(f"\n📥 Please download the SMS Spam Collection dataset:")
        print(f"   1. Go to: https://www.kaggle.com/datasets/uciml/sms-spam-collection-dataset")
        print(f"   2. Download and extract the CSV file")
        print(f"   3. Place it at: {filepath}")
        print(f"\n   The file should have ~5,572 rows with 'spam'/'ham' labels and message text.")
        sys.exit(1)
    
    print("=" * 70)
    print("STEP 1: DATA LOADING & CLEANING")
    print("=" * 70)
    
    # --- Load ---
    print(f"\n📂 Loading dataset from: {filepath}")
    df = load_dataset(filepath)
    print(f"   Raw dataset shape: {df.shape}")
    
    # --- Handle nulls ---
    null_count = df.isnull().sum().sum()
    print(f"\n🔍 Null values found: {null_count}")
    df = df.dropna(subset=['message'])
    
    # --- Handle duplicates ---
    dup_count = df.duplicated().sum()
    print(f"   Duplicate rows found: {dup_count}")
    df = df.drop_duplicates().reset_index(drop=True)
    print(f"   Shape after cleaning: {df.shape}")
    
    # --- Augment with email-domain phishing and legitimate samples ---
    email_samples = [
        # Phishing & Email Spam samples
        ("spam", "Subject: Urgent Account Verification Required\nYour account will be permanently suspended today. Verify your account now by clicking this link and entering your username, password, and credit card information."),
        ("spam", "Subject: Security Alert: Unauthorized Login Detected\nWe noticed suspicious activity on your online banking account. Please verify your identity immediately to prevent suspension. Click here to confirm your password and security questions."),
        ("spam", "Subject: Important Notice: Update Your Billing Information\nYour monthly subscription could not be renewed due to a billing issue. Update your credit card and banking details within 24 hours to avoid service interruption."),
        ("spam", "Subject: Immediate Action Required: Payroll Discrepancy\nOur finance department identified an error in your tax filing. Enter your Social Security Number and bank routing details here to release your pending salary payment."),
        ("spam", "Subject: Final Warning: Your Mailbox Will Be Terminated\nYour email storage quota has exceeded limits. Click the verification link below and submit your email password to prevent immediate deactivation."),
        ("spam", "Subject: Congratulations! You Won $1,000,000\nDear Customer, you have been selected as the lucky winner of $1,000,000. Click the link below and provide your bank details to claim your prize immediately!"),
        ("spam", "Subject: Get 90% Discount Today!!!\nLIMITED TIME OFFER! Buy our amazing products at 90% OFF. Act NOW!!! Click here to claim your exclusive discount before the offer expires!!!"),
        ("spam", "Subject: Wire Transfer Confirmation Required\nPlease review the attached international wire transfer of $45,000. Confirm your recipient account number and login credentials to accept incoming funds."),
        ("spam", "Subject: IRS Tax Refund Pending Approval\nYou are eligible for an overdue tax rebate of $2,450. Click below to verify your full name, date of birth, SSN, and debit card number to receive your direct deposit."),
        ("spam", "Subject: Critical Security Advisory: Reset Password Immediately\nA login attempt was blocked from Moscow, Russia. If this was not you, click this link to reset your account password and verify your PIN now."),
        ("spam", "Subject: Package Delivery Failed - Action Required\nYour parcel could not be delivered due to an incorrect address. Pay the redelivery fee and update your credit card details immediately by visiting our tracking portal."),
        ("spam", "Subject: Urgent: Verify Your PayPal Account\nYour PayPal account has been limited due to suspicious transactions. Please log in through the link below and verify your account details to restore full access."),

        # Legitimate Workplace & Academic Email samples
        ("ham", "Subject: Meeting Scheduled for Tomorrow\nHi John, just a reminder that our project meeting is scheduled for tomorrow at 10:00 AM in the conference room. Please bring the latest project report."),
        ("ham", "Subject: Your Assignment Submission\nHello Professor, I have completed my assignment and attached the final report. Please let me know if any changes are required. Thank you!"),
        ("ham", "Subject: Weekly Team Sync Notes and Action Items\nTeam, here is a summary of today's standup. Sprint goals are on track for Friday release. Let me know if anyone has blockers."),
        ("ham", "Subject: Quarterly Financial Review Presentation\nPlease find attached the slide deck for tomorrow's executive presentation. Let me know if you would like any revisions on the Q3 metrics."),
        ("ham", "Subject: Lunch Discussion on Research Paper\nHey Sarah, do you have 15 minutes after class to discuss the literature review section of our capstone project? Let me know."),
        ("ham", "Subject: Office Holiday Schedule\nDear staff, please note that the office will be closed on Monday in observance of the public holiday. Normal operations will resume Tuesday morning."),
        ("ham", "Subject: Draft Proposal for Major Project\nHi Dr. Miller, I have uploaded the draft architecture diagram for our major project. Looking forward to your feedback during office hours."),
        ("ham", "Subject: Welcome to the Engineering Team\nHi Alex, we are thrilled to have you join our software engineering group. Your onboarding schedule for this week is attached."),
        ("ham", "Subject: Software Engineering Lab Submission Deadline\nReminder to all enrolled students: the deadline for submitting Lab 4 is this Sunday at 11:59 PM via the course portal."),
        ("ham", "Subject: Thank You for the Interview\nDear Hiring Team, thank you for the insightful conversation today regarding the machine learning engineer position. I enjoyed learning more about the team's initiatives."),
    ]
    
    email_df = pd.DataFrame(email_samples, columns=['label', 'message'])
    df = pd.concat([df, email_df], ignore_index=True)
    print(f"   Augmented dataset with {len(email_samples)} domain-specific email samples.")
    print(f"   Shape after augmentation: {df.shape}")
    
    # --- Store raw_message (preserve original for structural features) ---
    df['raw_message'] = df['message']
    
    # --- Clean text ---
    print(f"\n🧹 Cleaning text...")
    df['clean_message'] = df['message'].apply(clean_text)
    
    # --- Encode labels: spam=0, ham=1 ---
    label_map = {'spam': 0, 'ham': 1}
    df['label_num'] = df['label'].map(label_map)
    
    # Check for unmapped labels
    unmapped = df['label_num'].isnull().sum()
    if unmapped > 0:
        print(f"   ⚠️  {unmapped} rows with unexpected labels, dropping...")
        df = df.dropna(subset=['label_num']).reset_index(drop=True)
    df['label_num'] = df['label_num'].astype(int)
    
    # --- Print class distribution ---
    print(f"\n📊 Class Distribution:")
    dist = df['label'].value_counts()
    for label, count in dist.items():
        pct = count / len(df) * 100
        print(f"   {label:>4s}: {count:5d} ({pct:.1f}%)")
    
    # --- Print sample rows before/after cleaning ---
    print(f"\n📝 Sample rows (before → after cleaning):")
    print("-" * 70)
    for i, row in df.head(5).iterrows():
        print(f"   [{row['label']:>4s}] Raw:     {row['raw_message'][:80]}...")
        print(f"          Cleaned: {row['clean_message'][:80]}...")
        print()
    
    # --- Extract structural features ---
    print(f"🔧 Extracting structural features from raw text...")
    structural = df['raw_message'].apply(extract_structural_features).apply(pd.Series)
    df = pd.concat([df, structural], axis=1)
    
    # --- Print average features by class ---
    print(f"\n📈 Average Structural Features by Class:")
    print("-" * 70)
    feature_cols = [
        'char_count', 'word_count', 'link_count', 'capital_ratio', 'punctuation_count',
        'digit_count', 'special_char_count', 'avg_word_length', 'exclamation_count',
        'urgency_word_count', 'sensitive_word_count'
    ]
    grouped = df.groupby('label')[feature_cols].mean()
    print(grouped.round(4).to_string())
    print()
    
    # Sanity check: spam should generally have higher link_count and capital_ratio
    if 'spam' in grouped.index and 'ham' in grouped.index:
        spam_links = grouped.loc['spam', 'link_count']
        ham_links = grouped.loc['ham', 'link_count']
        spam_caps = grouped.loc['spam', 'capital_ratio']
        ham_caps = grouped.loc['ham', 'capital_ratio']
        print(f"   ✅ Sanity check — spam link_count ({spam_links:.3f}) vs ham ({ham_links:.3f}): "
              f"{'PASS ✓' if spam_links > ham_links else 'UNEXPECTED (spam should be higher)'}")
        print(f"   ✅ Sanity check — spam capital_ratio ({spam_caps:.4f}) vs ham ({ham_caps:.4f}): "
              f"{'PASS ✓' if spam_caps > ham_caps else 'UNEXPECTED (spam should be higher)'}")
    
    # --- Save processed data ---
    output_path = os.path.join(data_dir, "processed.csv")
    df.to_csv(output_path, index=False)
    print(f"\n💾 Saved processed dataset to: {output_path}")
    print(f"   Final shape: {df.shape}")
    print(f"   Columns: {list(df.columns)}")
    
    return df


if __name__ == "__main__":
    preprocess()
