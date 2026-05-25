"""
tokenizer.py — Sinhala text tokenizer
Part of sinkit / sinhala-toolkit

Usage:
    from sinkit.tokenizer import Tokenizer

    t = Tokenizer()
    t.split_sentences("ඔහු ගෙදර ගියා། ඇය පාසලට ගියාය།")
    # ["ඔහු ගෙදර ගියා", "ඇය පාසලට ගියාය"]

    t.tokenize("ශ්‍රී ලංකාව ලස්සන රටකි")
    # ["ශ්‍රී", "ලංකාව", "ලස්සන", "රටකි"]
"""

from __future__ import annotations

import re
import unicodedata
from collections import Counter
from typing import TypedDict

# ---------------------------------------------------------------------------
# Unicode constants
# ---------------------------------------------------------------------------
_ZWJ          = "\u200D"
_DANDA        = "\u0964"   # ।
_DOUBLE_DANDA = "\u0965"   # ॥

# Regex patterns
_SINHALA_RE   = re.compile(r"[\u0D80-\u0DFF]")
_ENGLISH_RE   = re.compile(r"[a-zA-Z]")
_NUMBER_RE    = re.compile(r"[0-9\u0DE6-\u0DEF]")
_DIACRITIC_RE = re.compile(r"[\u0DCA-\u0DDF\u0DF2-\u0DF4\u0D82\u0D83]")

# Token types
TYPE_SINHALA     = "sinhala"
TYPE_ENGLISH     = "english"
TYPE_NUMBER      = "number"
TYPE_PUNCTUATION = "punctuation"
TYPE_MIXED       = "mixed"
TYPE_UNKNOWN     = "unknown"


class TokenWithType(TypedDict):
    token: str
    type: str


class Tokenizer:
    """
    Tokenize Sinhala text into sentences, words, and grapheme clusters.

    Handles:
    - Sinhala danda (।) and double danda (॥) as sentence boundaries
    - ZWJ conjunct consonants kept intact as single tokens
    - Mixed Sinhala / English / number text
    - Punctuation-aware word splitting

    Examples
    --------
    >>> t = Tokenizer()
    >>> t.split_sentences("ඔහු ගෙදර ගියා། ඇය පාසලට ගියාය།")
    ['ඔහු ගෙදර ගියා', 'ඇය පාසලට ගියාය']

    >>> t.tokenize("ශ්‍රී ලංකාව ලස්සන රටකි")
    ['ශ්‍රී', 'ලංකාව', 'ලස්සන', 'රටකි']
    """

    # ------------------------------------------------------------------
    # Sentence tokenization
    # ------------------------------------------------------------------

    def split_sentences(self, text: str, *, keep_boundary: bool = False) -> list[str]:
        """
        Split text into sentences.

        Boundaries detected:
        - Sinhala danda (।) and double danda (॥)
        - Full stop followed by space + capital/Sinhala character
        - Question mark (?) and exclamation mark (!)
        - Newlines

        Parameters
        ----------
        keep_boundary : Include the boundary character in the sentence.
        """
        if not text.strip():
            return []

        text = text.replace("\r\n", "\n").replace("\r", "\n")

        # Mark sentence boundaries with null byte
        MARKER = "\x00"

        # Danda / double danda
        text = re.sub(f"([{_DANDA}{_DOUBLE_DANDA}])\\s*", f"\\1{MARKER}", text)

        # English full stop before capital or Sinhala
        text = re.sub(r"(\.)(\s+)(?=[A-Z\u0D80-\u0DFF])", f"\\1{MARKER}", text)

        # Question / exclamation
        text = re.sub(r"([?!])\s*", f"\\1{MARKER}", text)

        # Newlines
        text = re.sub(r"\n+", MARKER, text)

        parts = [p.strip() for p in text.split(MARKER)]

        sentences = []
        for part in parts:
            if not part:
                continue
            if not keep_boundary:
                part = part.rstrip(f"{_DANDA}{_DOUBLE_DANDA}.?!").strip()
            if part:
                sentences.append(part)

        return sentences

    # ------------------------------------------------------------------
    # Word tokenization
    # ------------------------------------------------------------------

    def tokenize(self, text: str, *, lowercase: bool = False) -> list[str]:
        """
        Split text into word tokens.

        Preserves full Sinhala words including vowel signs and ZWJ conjuncts.
        Strips surrounding punctuation from each token.

        Parameters
        ----------
        lowercase : Lowercase English portions (Sinhala has no case).
        """
        if not text.strip():
            return []

        if lowercase:
            text = re.sub(r"[A-Z]+", lambda m: m.group().lower(), text)

        raw_tokens = text.split()
        tokens = []

        for raw in raw_tokens:
            cleaned = self._strip_surrounding_punctuation(raw)
            if cleaned:
                tokens.append(cleaned)

        return tokens

    def tokenize_with_types(self, text: str, *, lowercase: bool = False) -> list[TokenWithType]:
        """
        Tokenize and return each token with its type classification.

        Returns
        -------
        List of dicts: [{"token": str, "type": str}, ...]
        """
        return [
            {"token": t, "type": self.classify_token(t)}
            for t in self.tokenize(text, lowercase=lowercase)
        ]

    def tokenize_by_type(self, text: str, token_type: str) -> list[str]:
        """
        Tokenize and return only tokens of a specific type.

        Parameters
        ----------
        token_type : One of 'sinhala', 'english', 'number', 'mixed',
                     'punctuation', 'unknown'
        """
        return [
            item["token"]
            for item in self.tokenize_with_types(text)
            if item["type"] == token_type
        ]

    # ------------------------------------------------------------------
    # Grapheme cluster tokenization
    # ------------------------------------------------------------------

    def graphemes(self, text: str) -> list[str]:
        """
        Split text into Sinhala grapheme clusters.

        A grapheme cluster is a base character + its diacritics/vowel signs.
        ZWJ + following consonant is treated as ONE cluster (conjunct consonant).

        Examples
        --------
        >>> t = Tokenizer()
        >>> t.graphemes("ශ්‍රී")   # ZWJ conjunct
        ['ශ්‍රී']
        """
        if not text.strip():
            return []

        chars    = list(text)
        clusters = []
        i        = 0

        while i < len(chars):
            cluster = chars[i]
            i += 1

            # Consume trailing diacritics / vowel signs
            while i < len(chars) and self._is_diacritic(chars[i]):
                cluster += chars[i]
                i += 1

            # Consume ZWJ + following consonant (conjunct)
            if i < len(chars) and chars[i] == _ZWJ:
                cluster += chars[i]  # ZWJ
                i += 1
                if i < len(chars):
                    cluster += chars[i]  # following consonant
                    i += 1
                    while i < len(chars) and self._is_diacritic(chars[i]):
                        cluster += chars[i]
                        i += 1

            clusters.append(cluster)

        return clusters

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    def classify_token(self, token: str) -> str:
        """
        Classify a token by script type.

        Returns
        -------
        'sinhala' | 'english' | 'number' | 'mixed' | 'punctuation' | 'unknown'
        """
        has_sinhala = bool(_SINHALA_RE.search(token))
        has_english = bool(_ENGLISH_RE.search(token))
        has_number  = bool(_NUMBER_RE.search(token))
        is_punct    = bool(re.match(r"^[^\w]+$", token, re.UNICODE))

        if is_punct:                                  return TYPE_PUNCTUATION
        if has_sinhala and not has_english and not has_number: return TYPE_SINHALA
        if has_english and not has_sinhala and not has_number: return TYPE_ENGLISH
        if has_number  and not has_sinhala and not has_english: return TYPE_NUMBER
        if has_sinhala or has_english or has_number:  return TYPE_MIXED
        return TYPE_UNKNOWN

    def frequency(self, text: str, stopwords: list[str] | None = None) -> dict[str, int]:
        """
        Return word frequency map, sorted by count descending.

        Parameters
        ----------
        stopwords : Optional list of stopwords to exclude.
        """
        tokens = self.tokenize(text, lowercase=True)

        if stopwords:
            tokens = [t for t in tokens if t not in stopwords]

        return dict(Counter(tokens).most_common())

    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        return len(self.tokenize(text))

    def count_sentences(self, text: str) -> int:
        """Count sentences in text."""
        return len(self.split_sentences(text))

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _strip_surrounding_punctuation(self, token: str) -> str:
        """Strip punctuation from start/end of token, preserving Sinhala diacritics."""
        token = re.sub(r"^[^\w\u200D\u0D80-\u0DFF]+", "", token)
        token = re.sub(r"[^\w\u200D\u0D80-\u0DFF]+$", "", token)
        return token

    def _is_diacritic(self, char: str) -> bool:
        """Check if a character is a Sinhala diacritic/vowel sign."""
        cp = ord(char)
        return (
            (0x0DCA <= cp <= 0x0DDF) or
            (0x0DF2 <= cp <= 0x0DF4) or
            cp == 0x0D82 or
            cp == 0x0D83
        )
