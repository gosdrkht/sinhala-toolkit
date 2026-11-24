"""
stemmer.py — Rule-based Sinhala stemmer / suffix stripper
Part of sinkit / sinhala-toolkit

Usage:
    from sinkit.stemmer import Stemmer

    st = Stemmer()
    st.stem("ගෙදරට")     # "ගෙදර"
    st.stem("ගෙදරින්")    # "ගෙදර"
    st.stem("ගෙදරයි")     # "ගෙදර"
"""

from __future__ import annotations

import re
from .tokenizer import Tokenizer

_SINHALA_RE = re.compile(r"[\u0D80-\u0DFF]")

_SUFFIXES: tuple[str, ...] = (
    "වරුන්ගේ", "වරුන්ට", "වරුන්", "වලින්", "වලට", "වලදී", "වල",
    "යින්ගේ", "යින්ට", "යන්ගේ", "යන්ට", "ගෙන්", "වලිනි",
    "යින්", "යන්", "යෙහි", "යෙක්", "යාගේ", "යාට", "වරු",
    "ගේ", "ගෙ", "ට", "න්", "යි", "ත්", "ද", "ම", "ක්", "ක",
    "වේ", "ව", "ලා", "හි", "නි",
)


class Stemmer:
    """
    Rule-based Sinhala suffix stripper for search & keyword normalisation.

    Examples
    --------
    >>> st = Stemmer()
    >>> st.stem("ගෙදරට")
    'ගෙදර'
    >>> st.stem("ගෙදරින්")
    'ගෙදර'
    >>> st.stem("ගෙදරයි")
    'ගෙදර'
    """

    def __init__(self, min_stem_graphemes: int = 2) -> None:
        self._tokenizer = Tokenizer()
        self._min_stem_graphemes = max(1, min_stem_graphemes)

    def stem(self, word: str) -> str:
        """Stem a single Sinhala word."""
        word = word.strip()
        if not word or not _SINHALA_RE.search(word):
            return word

        # Handle instrumental/ablative ending -ින් (e.g. ගෙදරින් → ගෙදර)
        if word.endswith("ින්"):
            candidate = word[:-len("ින්")]
            if len(self._tokenizer.graphemes(candidate)) >= self._min_stem_graphemes:
                return candidate

        for suffix in _SUFFIXES:
            if word.endswith(suffix):
                candidate = word[:-len(suffix)]
                if len(self._tokenizer.graphemes(candidate)) >= self._min_stem_graphemes:
                    return candidate

        return word

    def stem_tokens(self, tokens: list[str]) -> list[str]:
        """Stem a list of tokens."""
        return [self.stem(t) for t in tokens]

    def stem_text(self, text: str) -> str:
        """Stem all words in a text string."""
        tokens = self._tokenizer.tokenize(text)
        return " ".join(self.stem_tokens(tokens))
