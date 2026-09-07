"""
features.py — Reusable text cleaning and structural feature extraction module.

This module is imported by both training scripts and inference.py.
It provides the SAME cleaning logic and feature extraction used at training
time, ensuring consistency between training and prediction.
"""

import re
import string


def clean_text(text: str) -> str:
    """
    Clean raw email/SMS text for TF-IDF vectorization.
    
    Steps:
        1. Lowercase
        2. Strip leading/trailing whitespace
        3. Collapse multiple whitespace characters into a single space
        4. Remove non-essential noise characters (control chars, etc.)
    
    NOTE: This is applied AFTER extracting structural features from the raw text,
    since structural features depend on the original casing, URLs, etc.
    
    Args:
        text: Raw message text.
    
    Returns:
        Cleaned text suitable for TF-IDF.
    """
    if not isinstance(text, str):
        return ""
    
    # Lowercase
    text = text.lower()
    
    # Remove control characters and non-printable chars (keep basic printable ASCII + common unicode)
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    
    # Collapse multiple whitespace into single space
    text = re.sub(r'\s+', ' ', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text


def extract_structural_features(text: str) -> dict:
    """
    Extract structural features from RAW (uncleaned) text.
    
    These features capture characteristics that distinguish spam from ham
    (e.g., spam tends to have more URLs, more capitalization, more punctuation).
    
    Args:
        text: Raw message text (before cleaning).
    
    Returns:
        Dictionary with keys:
            - char_count (int): Total character count
            - word_count (int): Number of whitespace-separated tokens
            - link_count (int): Number of URL-like patterns
            - capital_ratio (float): Proportion of uppercase letters to total letters
            - punctuation_count (int): Count of punctuation characters
            - digit_count (int): Count of digit characters
            - special_char_count (int): Count of non-alpha, non-digit, non-space chars
            - avg_word_length (float): Average word length
            - exclamation_count (int): Count of '!' characters
            - urgency_word_count (int): Count of urgency/pressure words
            - sensitive_word_count (int): Count of sensitive info / financial words
    """
    if not isinstance(text, str):
        return {
            "char_count": 0,
            "word_count": 0,
            "link_count": 0,
            "capital_ratio": 0.0,
            "punctuation_count": 0,
            "digit_count": 0,
            "special_char_count": 0,
            "avg_word_length": 0.0,
            "exclamation_count": 0,
            "urgency_word_count": 0,
            "sensitive_word_count": 0,
        }
    
    # Character count
    char_count = len(text)
    
    # Word count (whitespace-separated tokens)
    words = text.split()
    word_count = len(words)
    
    # Link/URL count — match http://, https://, www., and domain-like patterns
    url_pattern = r'(?:https?://|www\.)\S+|(?:[a-zA-Z0-9][-a-zA-Z0-9]*\.)+(?:com|org|net|co|uk|edu|gov|io|info|biz)\b'
    link_count = len(re.findall(url_pattern, text))
    
    # Capital ratio — proportion of uppercase letters to total letters
    letters = [c for c in text if c.isalpha()]
    total_letters = len(letters)
    if total_letters > 0:
        uppercase_count = sum(1 for c in letters if c.isupper())
        capital_ratio = round(uppercase_count / total_letters, 4)
    else:
        capital_ratio = 0.0
    
    # Punctuation count
    punctuation_count = sum(1 for c in text if c in string.punctuation)
    
    # Digit count — spam often contains phone numbers, amounts
    digit_count = sum(1 for c in text if c.isdigit())
    
    # Special character count — non-alpha, non-digit, non-space
    special_char_count = sum(1 for c in text if not c.isalnum() and not c.isspace())
    
    # Average word length
    avg_word_length = round(sum(len(w) for w in words) / max(word_count, 1), 4)
    
    # Exclamation count — strong spam indicator (urgency)
    exclamation_count = text.count('!')
    
    # Urgency word count — phishing/spam pressure tactics
    text_lower = text.lower()
    urgency_words = [
        'urgent', 'immediately', 'now', 'today', 'expire', 'expires', 'expired',
        'suspend', 'suspended', 'verify', 'verified', 'verification',
        'act now', 'limited time', 'don\'t miss', 'last chance', 'hurry',
        'warning', 'alert', 'attention', 'important', 'required', 'mandatory',
        'deadline', 'final notice', 'action required', 'respond immediately',
        'claim', 'winner', 'won', 'congratulations', 'selected',
    ]
    urgency_word_count = sum(1 for w in urgency_words if w in text_lower)
    
    # Sensitive/financial word count — phishing indicators
    sensitive_words = [
        'password', 'credit card', 'bank', 'account', 'ssn', 'social security',
        'login', 'username', 'pin', 'routing number', 'wire transfer',
        'payment', 'billing', 'invoice', 'refund', 'transaction',
        'click here', 'click the link', 'click below', 'click this',
        'provide your', 'enter your', 'confirm your', 'update your',
        'bank details', 'personal information', 'financial',
        'free', 'prize', 'reward', 'bonus', 'discount', 'offer',
    ]
    sensitive_word_count = sum(1 for w in sensitive_words if w in text_lower)
    
    return {
        "char_count": char_count,
        "word_count": word_count,
        "link_count": link_count,
        "capital_ratio": capital_ratio,
        "punctuation_count": punctuation_count,
        "digit_count": digit_count,
        "special_char_count": special_char_count,
        "avg_word_length": avg_word_length,
        "exclamation_count": exclamation_count,
        "urgency_word_count": urgency_word_count,
        "sensitive_word_count": sensitive_word_count,
    }


if __name__ == "__main__":
    # Quick sanity check
    sample_spam = "CONGRATULATIONS!!! You've WON a FREE iPhone!!! Visit http://spam-link.com NOW to claim!!!"
    sample_ham = "Hey, are we still meeting for lunch tomorrow at the cafe?"
    
    print("=== Structural Feature Extraction Demo ===\n")
    
    for label, text in [("SPAM", sample_spam), ("HAM", sample_ham)]:
        feats = extract_structural_features(text)
        cleaned = clean_text(text)
        print(f"[{label}] Raw: {text}")
        print(f"  Cleaned: {cleaned}")
        print(f"  Features: {feats}")
        print()
