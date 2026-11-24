"""
keywords.py — Zero-dependency Sinhala keyword extractor & extractive summariser
Part of sinkit / sinhala-toolkit

Usage:
    from sinkit.keywords import KeywordExtractor

    ke = KeywordExtractor()
    ke.extract("ශ්‍රී ලංකාව ලස්සන රටකි. ශ්‍රී ලංකාව සංචාරක රටකි.", top_k=3)
    ke.summarize(long_article, num_sentences=2)
"""

from __future__ import annotations

import math
from typing import Optional, TypedDict

from .cleaner import TextCleaner
from .stemmer import Stemmer
from .tokenizer import TYPE_PUNCTUATION, Tokenizer


class KeywordItem(TypedDict):
    keyword: str
    score: float
    count: int


class KeywordExtractor:
    """
    Extract top keywords and generate extractive summaries for Sinhala text.

    Examples
    --------
    >>> ke = KeywordExtractor()
    >>> kw = ke.extract("ශ්‍රී ලංකාව ලස්සන රටකි ශ්‍රී ලංකාව හොඳ රටකි", top_k=2)
    >>> [item["keyword"] for item in kw]
    ['ශ්‍රී', 'ලංකාව']
    """

    def __init__(self, stopwords_path: Optional[str] = None) -> None:
        self._cleaner = TextCleaner(stopwords_path)
        self._tokenizer = Tokenizer()
        self._stemmer = Stemmer()

    def extract(
        self,
        text: str,
        top_k: int = 5,
        *,
        use_stemming: bool = False,
    ) -> list[KeywordItem]:
        """Extract top_k keywords ranked by stopword-filtered TF + early-position boost."""
        if not text.strip() or top_k <= 0:
            return []

        tokens = self._tokenizer.tokenize(text, lowercase=True)
        total = len(tokens)
        if total == 0:
            return []

        counts: dict[str, int] = {}
        scores: dict[str, float] = {}

        for idx, token in enumerate(tokens):
            if self._cleaner.is_stopword(token):
                continue
            if self._tokenizer.classify_token(token) == TYPE_PUNCTUATION:
                continue

            key = self._stemmer.stem(token) if use_stemming else token
            if not key or self._cleaner.is_stopword(key):
                continue

            pos_weight = 1.0 + 0.25 * (1.0 - (idx / max(1, total)))
            counts[key] = counts.get(key, 0) + 1
            scores[key] = scores.get(key, 0.0) + pos_weight

        if not scores:
            return []

        max_score = max(scores.values())
        ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)[:top_k]

        return [
            {
                "keyword": kw,
                "score": round(score / max_score, 3),
                "count": counts[kw],
            }
            for kw, score in ranked
        ]

    def summarize(self, text: str, num_sentences: int = 2) -> str:
        """Extractive summariser selecting top sentences in original document order."""
        sentences = self._tokenizer.split_sentences(text, keep_boundary=True)
        if len(sentences) <= num_sentences:
            return " ".join(sentences)

        weights = {item["keyword"]: item["score"] for item in self.extract(text, top_k=20)}

        scored: list[tuple[int, float]] = []
        for idx, sentence in enumerate(sentences):
            tokens = self._tokenizer.tokenize(sentence, lowercase=True)
            score = sum(weights.get(t, 0.0) for t in tokens)
            scored.append((idx, score / max(1.0, math.sqrt(len(tokens)))))

        top_indices = sorted(
            idx for idx, _ in sorted(scored, key=lambda pair: pair[1], reverse=True)[:num_sentences]
        )
        return " ".join(sentences[i] for i in top_indices)
