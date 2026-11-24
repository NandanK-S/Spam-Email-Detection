"""
test_features.py — Unit tests for text cleaning and structural feature extraction.
"""

import sys
import os
import pytest

# Ensure ml directory is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from features import clean_text, extract_structural_features


class TestCleanText:
    """Tests for clean_text() function."""

    def test_lowercase_conversion(self):
        assert clean_text("HELLO World!") == "hello world!"

    def test_whitespace_stripping_and_collapsing(self):
        raw = "   lots   of    spaced   words   "
        assert clean_text(raw) == "lots of spaced words"

    def test_newlines_and_tabs(self):
        raw = "Line 1\n\tLine 2\r\nLine 3"
        assert clean_text(raw) == "line 1 line 2 line 3"

    def test_control_character_removal(self):
        raw = "Hello\x00\x08World\x1f\x7f!"
        assert clean_text(raw) == "helloworld!"

    def test_empty_string(self):
        assert clean_text("") == ""

    def test_non_string_inputs(self):
        assert clean_text(None) == ""
        assert clean_text(12345) == ""
        assert clean_text(["text"]) == ""
        assert clean_text({"text": "val"}) == ""

    def test_unicode_preservation(self):
        raw = "Café résumé naïve 🚀"
        cleaned = clean_text(raw)
        assert "café" in cleaned
        assert "résumé" in cleaned


class TestExtractStructuralFeatures:
    """Tests for extract_structural_features() function."""

    EXPECTED_KEYS = {
        "char_count",
        "word_count",
        "link_count",
        "capital_ratio",
        "punctuation_count",
        "digit_count",
        "special_char_count",
        "avg_word_length",
        "exclamation_count",
        "urgency_word_count",
        "sensitive_word_count",
    }

    def test_dictionary_keys_presence(self):
        feats = extract_structural_features("Test email message")
        assert set(feats.keys()) == self.EXPECTED_KEYS

    def test_non_string_input_returns_safe_defaults(self):
        feats = extract_structural_features(None)
        assert set(feats.keys()) == self.EXPECTED_KEYS
        assert feats["char_count"] == 0
        assert feats["word_count"] == 0
        assert feats["capital_ratio"] == 0.0

    def test_empty_string_does_not_divide_by_zero(self):
        feats = extract_structural_features("")
        assert feats["char_count"] == 0
        assert feats["word_count"] == 0
        assert feats["capital_ratio"] == 0.0
        assert feats["avg_word_length"] == 0.0

    def test_no_alphabet_string_division_safety(self):
        feats = extract_structural_features("12345 !!! ???? ###")
        assert feats["capital_ratio"] == 0.0
        assert feats["digit_count"] == 5
        assert feats["exclamation_count"] == 3

    def test_capital_ratio_calculation(self):
        # 4 uppercase out of 8 letters = 0.50
        feats = extract_structural_features("ABCD efgh")
        assert feats["capital_ratio"] == 0.50

        # All uppercase
        all_caps = extract_structural_features("CONGRATULATIONS")
        assert all_caps["capital_ratio"] == 1.0

        # All lowercase
        all_lower = extract_structural_features("congratulations")
        assert all_lower["capital_ratio"] == 0.0

    def test_link_count_detection(self):
        text_with_links = (
            "Visit http://example.com and https://secure-site.org or www.test.net "
            "also check out domain.info for deals."
        )
        feats = extract_structural_features(text_with_links)
        assert feats["link_count"] >= 3

        no_links = extract_structural_features("Hey, let's meet tomorrow at 10 AM.")
        assert no_links["link_count"] == 0

    def test_exclamation_count(self):
        feats = extract_structural_features("URGENT!!! Act now! Claim prize!!!")
        assert feats["exclamation_count"] == 7

    def test_urgency_words_detection(self):
        urgent_text = "URGENT notice: Your account will expire today. Verify immediately!"
        feats = extract_structural_features(urgent_text)
        assert feats["urgency_word_count"] >= 4

    def test_sensitive_words_detection(self):
        phishing_text = (
            "Please enter your password, username and bank details or credit card "
            "to confirm your transaction and claim your prize."
        )
        feats = extract_structural_features(phishing_text)
        assert feats["sensitive_word_count"] >= 4

    def test_word_count_and_avg_length(self):
        text = "Hello world"  # 5 + 5 chars, 2 words -> avg 5.0
        feats = extract_structural_features(text)
        assert feats["word_count"] == 2
        assert feats["avg_word_length"] == 5.0

