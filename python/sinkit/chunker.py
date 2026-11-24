"""
chunker.py — Sinhala-aware LLM / RAG text chunker & token estimator
Part of sinkit / sinhala-toolkit

Usage:
    from sinkit.chunker import Chunker

    ch = Chunker()
    chunks = ch.chunk(long_sinhala_doc, max_chars=500, overlap=50)
    tokens = ch.estimate_tokens("ශ්‍රී ලංකාව ලස්සන රටකි")
"""

from __future__ import annotations

import math
import re
from .tokenizer import Tokenizer

_SINHALA_RE = re.compile(r"[\u0D80-\u0DFF]")


class Chunker:
    """
    Split Sinhala documents into LLM/RAG-ready chunks without ever breaking
    mid-sentence, mid-word, mid-vowel-sign, or mid-ZWJ-conjunct.

    Examples
    --------
    >>> ch = Chunker()
    >>> ch.chunk("ඔහු ගෙදර ගියා। ඇය පාසලට ගියාය।", max_chars=20)
    ['ඔහු ගෙදර ගියා।', 'ඇය පාසලට ගියාය।']
    >>> ch.estimate_tokens("ශ්‍රී ලංකාව") > 0
    True
    """

    def __init__(self) -> None:
        self._tokenizer = Tokenizer()

    def chunk(self, text: str, max_chars: int = 500, overlap: int = 0) -> list[str]:
        """Split text into chunks preserving sentence, word, and grapheme boundaries."""
        text = text.strip()
        if not text or max_chars <= 0:
            return []

        overlap = max(0, min(overlap, max_chars - 1))
        sentences = self._tokenizer.split_sentences(text, keep_boundary=True) or [text]

        units: list[str] = []
        for sentence in sentences:
            if len(sentence) <= max_chars:
                units.append(sentence)
            else:
                units.extend(self._split_oversized(sentence, max_chars))

        chunks: list[str] = []
        current = ""

        for unit in units:
            if not current:
                current = unit
                continue

            candidate = f"{current} {unit}"
            if len(candidate) <= max_chars:
                current = candidate
            else:
                chunks.append(current)
                if overlap > 0:
                    tail = self._grapheme_tail(current, overlap)
                    combined = f"{tail} {unit}".strip()
                    current = combined if len(combined) <= max_chars else unit
                else:
                    current = unit

        if current:
            chunks.append(current)

        return chunks

    def estimate_tokens(self, text: str) -> int:
        """Estimate LLM BPE token count for Sinhala, English, or mixed text."""
        if not text.strip():
            return 0
        sinhala_count = len(_SINHALA_RE.findall(text))
        other_count = max(0, len(text) - sinhala_count)
        return max(1, math.ceil(sinhala_count * 1.5 + other_count * 0.25))

    def _split_oversized(self, text: str, max_chars: int) -> list[str]:
        words = text.split()
        pieces: list[str] = []
        buf = ""

        for word in words:
            if len(word) > max_chars:
                if buf:
                    pieces.append(buf)
                    buf = ""
                pieces.extend(self._split_by_graphemes(word, max_chars))
                continue

            if not buf:
                buf = word
            elif len(buf) + 1 + len(word) <= max_chars:
                buf = f"{buf} {word}"
            else:
                pieces.append(buf)
                buf = word

        if buf:
            pieces.append(buf)
        return pieces

    def _split_by_graphemes(self, word: str, max_chars: int) -> list[str]:
        pieces: list[str] = []
        buf = ""
        for g in self._tokenizer.graphemes(word):
            if buf and len(buf) + len(g) > max_chars:
                pieces.append(buf)
                buf = g
            else:
                buf += g
        if buf:
            pieces.append(buf)
        return pieces

    def _grapheme_tail(self, text: str, target_chars: int) -> str:
        graphemes = self._tokenizer.graphemes(text)
        tail = ""
        for g in reversed(graphemes):
            candidate = g + tail
            if len(candidate) > target_chars and tail:
                break
            tail = candidate
        return tail.strip()
