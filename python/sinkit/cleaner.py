"""
cleaner.py — Sinhala text cleaner and normaliser
Part of sinkit / sinhala-toolkit

Usage:
    from sinkit.cleaner import TextCleaner

    cleaner = TextCleaner()
    clean   = cleaner.clean("  මම  සහ  ඔබ  ගෙදර  ගියා  ",
                            remove_stopwords=True)
    # "ගෙදර ගියා"
"""

from __future__ import annotations

import re
import unicodedata
from typing import Optional

from .stopwords import Stopwords

# ---------------------------------------------------------------------------
# Unicode constants
# ---------------------------------------------------------------------------
_ZWJ        = "\u200D"   # Zero Width Joiner  — used in Sinhala conjuncts
_ZWNJ       = "\u200C"   # Zero Width Non-Joiner
_ZWSP       = "\u200B"   # Zero Width Space
_BOM        = "\uFEFF"   # Byte Order Mark
_SOFT_HYPHEN = "\u00AD"  # Soft Hyphen
_LRM        = "\u200E"   # Left-to-Right Mark
_RLM        = "\u200F"   # Right-to-Left Mark

# Sinhala Unicode block
_SINHALA_RE  = re.compile(r"[\u0D80-\u0DFF]")
_ENGLISH_RE  = re.compile(r"[a-zA-Z]")
_NUMBER_RE   = re.compile(r"[0-9\u0DE6-\u0DEF]")  # ASCII + Sinhala digits


class TextCleaner:
    """
    Clean and normalise Sinhala (and mixed) text.

    Parameters
    ----------
    stopwords_path : str or None
        Path to stopwords.json. Defaults to ../../data/stopwords.json.

    Examples
    --------
    >>> c = TextCleaner()
    >>> c.clean("  මම  සහ  ඔබ  ගෙදර  ගියා  ", remove_stopwords=True)
    'ගෙදර ගියා'
    >>> c.detect_script("Hello ආයුබෝවන්")
    'mixed'
    """

    def __init__(self, stopwords_path: Optional[str] = None) -> None:
        self._sw = Stopwords(stopwords_path) if stopwords_path else Stopwords()

    # ------------------------------------------------------------------
    # Main pipeline
    # ------------------------------------------------------------------

    def clean(
        self,
        text: str,
        *,
        remove_stopwords: bool = False,
        remove_punctuation: bool = False,
        remove_english: bool = False,
        remove_numbers: bool = False,
        keep_zwj: bool = True,
    ) -> str:
        """
        Full clean pipeline — run all steps in recommended order.

        Parameters
        ----------
        text               : Input text
        remove_stopwords   : Strip Sinhala stopwords
        remove_punctuation : Remove punctuation (keeps Sinhala dandas by default)
        remove_english     : Remove ASCII letter characters
        remove_numbers     : Remove digit characters
        keep_zwj           : Preserve ZWJ (needed for conjunct consonants)
        """
        text = self.normalise_unicode(text)
        text = self.remove_invisible_chars(text, keep_zwj=keep_zwj)
        text = self.normalise_whitespace(text)

        if remove_punctuation:
            text = self.remove_punctuation(text)
        if remove_english:
            text = self.remove_english(text)
        if remove_numbers:
            text = self.remove_numbers(text)
        if remove_stopwords:
            text = self.remove_stopwords(text)

        return text.strip()

    # ------------------------------------------------------------------
    # Individual steps
    # ------------------------------------------------------------------

    def normalise_unicode(self, text: str) -> str:
        """
        Normalise text to NFC form.
        Sinhala text from different sources may use different compositions —
        NFC ensures consistent character representation.
        """
        return unicodedata.normalize("NFC", text)

    def remove_invisible_chars(self, text: str, *, keep_zwj: bool = True) -> str:
        """
        Remove invisible/control characters.

        By default ZWJ is kept because Sinhala uses it for conjunct
        consonants (e.g. ශ් + ZWJ + ර = ශ්‍ර).
        Set keep_zwj=False for bare token comparison.
        """
        # Remove specific invisible chars
        to_remove = [_ZWNJ, _ZWSP, _BOM, _SOFT_HYPHEN, _LRM, _RLM]
        if not keep_zwj:
            to_remove.append(_ZWJ)

        for char in to_remove:
            text = text.replace(char, "")

        # Remove C0 control characters (except \t \n \r)
        text = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", text)

        return text

    def normalise_whitespace(self, text: str) -> str:
        """
        Collapse all whitespace variants into single spaces.
        Handles non-breaking space, ideographic space etc.
        """
        text = re.sub(r"[\s\u00A0\u3000]+", " ", text)
        return text.strip()

    def remove_punctuation(self, text: str, *, keep_danda: bool = True) -> str:
        """
        Remove punctuation marks.

        Parameters
        ----------
        keep_danda : Keep Sinhala danda (।) and double danda (॥). Default True.
        """
        if keep_danda:
            # Remove all punctuation except dandas (\u0964 \u0965)
            text = re.sub(r"[^\w\s\u0964\u0965]", " ", text, flags=re.UNICODE)
        else:
            text = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)

        return self.normalise_whitespace(text)

    def remove_english(self, text: str) -> str:
        """Remove ASCII English letters from text."""
        text = re.sub(r"[a-zA-Z]+", " ", text)
        return self.normalise_whitespace(text)

    def remove_numbers(self, text: str) -> str:
        """Remove digits — both ASCII (0-9) and Sinhala numeral block."""
        text = re.sub(r"[0-9\u0DE6-\u0DEF]", " ", text)
        return self.normalise_whitespace(text)

    def remove_stopwords(self, text: str) -> str:
        """Remove stopwords by splitting, filtering, and rejoining."""
        tokens   = text.split()
        filtered = self._sw.filter(tokens)
        return " ".join(filtered)

    # ------------------------------------------------------------------
    # Detection utilities
    # ------------------------------------------------------------------

    def detect_script(self, text: str) -> str:
        """
        Detect the dominant script in a string.

        Returns
        -------
        'sinhala' | 'english' | 'mixed' | 'unknown'
        """
        has_sinhala = bool(_SINHALA_RE.search(text))
        has_english = bool(_ENGLISH_RE.search(text))

        if has_sinhala and has_english:
            return "mixed"
        if has_sinhala:
            return "sinhala"
        if has_english:
            return "english"
        return "unknown"

    def is_pure_sinhala(self, text: str) -> bool:
        """
        Return True if the text contains only Sinhala characters,
        whitespace, ZWJ, and dandas.
        """
        return bool(re.match(r"^[\u0D80-\u0DFF\u200D\s\u0964\u0965]+$", text.strip()))

    def contains_sinhala(self, text: str) -> bool:
        """Return True if the text contains any Sinhala characters."""
        return bool(_SINHALA_RE.search(text))

    def is_stopword(self, word: str) -> bool:
        """Check if a single word is a stopword."""
        return self._sw.is_stopword(word)

    def tokenize(self, text: str) -> list[str]:
        """
        Simple whitespace tokenizer.
        For advanced tokenization use sinkit.tokenizer.Tokenizer.
        """
        return [t for t in text.split() if t]
