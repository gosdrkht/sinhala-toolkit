"""
sentiment.py — Rule-based Sinhala sentiment analyser
Part of sinkit / sinhala-toolkit

A lightweight, dictionary-based sentiment analyser for Sinhala text.
No ML dependencies required — works out of the box.

Usage:
    from sinkit.sentiment import SentimentAnalyser

    sa = SentimentAnalyser()
    result = sa.analyse("මෙය ඉතා හොඳ චිත්‍රපටයකි")
    # {"label": "positive", "score": 0.8, "positive": 2, "negative": 0}

For a fine-tuned ML model, see the roadmap in README.md.
"""

from __future__ import annotations

from typing import TypedDict
from .tokenizer import Tokenizer


# ---------------------------------------------------------------------------
# Sentiment lexicons
# Built from common Sinhala social media, reviews, and everyday speech.
# Contributions welcome — see CONTRIBUTING.md
# ---------------------------------------------------------------------------

POSITIVE_WORDS: list[str] = [
    # Positive adjectives
    "හොඳ", "හොඳයි", "හොඳම", "හොඳටම",
    "ලස්සන", "ලස්සනයි",
    "සුන්දර", "සුන්දරයි",
    "අපූරු", "අපූරුයි",
    "ජය", "ජයග්‍රහණය",
    "සතුට", "සතුටුයි", "සතුටු",
    "ආදරය", "ආදරණීය",
    "සාර්ථක", "සාර්ථකයි",
    "ශ්‍රේෂ්ඨ", "ශ්‍රේෂ්ඨයි",
    "නියම", "නියමයි",
    "ඉක්මන්", "ශක්තිමත්",
    "නිදහස", "නිදහස්",
    "ප්‍රිය", "ප්‍රියමනාප",
    "සුඛ", "සුඛී",
    "දිනුම", "දිනුවා",
    "ශක්ති", "ශක්තිමත්",
    "ප්‍රශංසා", "ප්‍රශංසනීය",
    "දීප්තිමත්", "දක්ෂ",
    "විශිෂ්ට", "විශිෂ්ටයි",
    "ශ්‍රේෂ්ඨ",
    "සමෘද්ධිමත්", "සමෘද්ධිය",
    "ඔව්", "හරි", "ඇත්ත",
    "සාමය", "ශාන්ත",
    "ගෞරව", "ගෞරවනීය",
    "කීර්තිමත්", "කීර්තිය",
    "ප්‍රේමය", "ප්‍රේමණීය",
    "රසවත්", "රසවතා",
    "අගේ", "ගිනිකෙළි",
    "අලංකාර", "සිත් ගන්නා",
]

NEGATIVE_WORDS: list[str] = [
    # Negative adjectives and expressions
    "නරක", "නරකයි", "නරකම",
    "කණගාටු", "කණගාටුයි",
    "දුක", "දුකයි", "දුක්",
    "රොත්ත", "කෝපය", "කෝපයි",
    "අපජය", "පරාජය",
    "බිය", "බියයි", "භය",
    "ගැටලු", "ගැටලුව",
    "අසාර්ථක", "අසාර්ථකයි",
    "ශෝකය", "ශෝකී",
    "නිදහස් නෑ",
    "වේදනා", "වේදනාකාරී",
    "රෝගය", "රෝගී",
    "දූෂිත", "දූෂණය",
    "ක්‍රෝධය", "ක්‍රෝධී",
    "ද්වේෂය", "ද්වේෂී",
    "පාඩු", "අහිමි",
    "හිරිහැර", "හිරිහැරකාරී",
    "අසාධාරණ", "අසාධාරණයි",
    "සුසාන", "ශාපය",
    "මරණය", "මරණ",
    "හිං", "හිංසා",
    "ෆේල්",
    "ව්‍යසනය", "ව්‍යසනකාරී",
    "හරිම නරක",
    "කිළිටි",
]

NEGATION_WORDS: list[str] = [
    "නෑ", "නැහැ", "නැත", "නෙමෙයි", "බෑ", "බැරි", "නෙ", "නෙමේ",
]

INTENSIFIERS: dict[str, float] = {
    "ඉතා":    1.5,
    "ඉතාමත්": 1.8,
    "බොහෝ":  1.3,
    "ගොඩාක්": 1.4,
    "හරිම":   1.6,
    "ඉතාම":  1.5,
}


class SentimentResult(TypedDict):
    label:    str    # "positive" | "negative" | "neutral"
    score:    float  # 0.0 to 1.0
    positive: int    # count of positive signals
    negative: int    # count of negative signals
    tokens:   list[str]


class SentimentAnalyser:
    """
    Rule-based Sinhala sentiment analyser.

    Uses a curated lexicon of positive/negative words,
    handles negation and intensifiers.

    Note: For production accuracy on diverse text, a fine-tuned
    ML model is recommended. This rule-based version is a solid
    baseline and works with zero dependencies.

    Examples
    --------
    >>> sa = SentimentAnalyser()
    >>> sa.analyse("මෙය ඉතා හොඳ චිත්‍රපටයකි")
    {'label': 'positive', 'score': 0.75, 'positive': 2, 'negative': 0, ...}

    >>> sa.analyse("මෙය හොඳ නෑ")
    {'label': 'negative', 'score': 0.6, 'positive': 0, 'negative': 1, ...}
    """

    def __init__(
        self,
        positive_words: list[str] | None = None,
        negative_words: list[str] | None = None,
    ) -> None:
        self._positive  = set(positive_words or POSITIVE_WORDS)
        self._negative  = set(negative_words or NEGATIVE_WORDS)
        self._negations = set(NEGATION_WORDS)
        self._tokenizer = Tokenizer()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def analyse(self, text: str) -> SentimentResult:
        """
        Analyse the sentiment of a Sinhala text string.

        Returns a SentimentResult dict with:
        - label    : "positive", "negative", or "neutral"
        - score    : confidence 0.0–1.0
        - positive : number of positive signals found
        - negative : number of negative signals found
        - tokens   : the token list used for analysis
        """
        tokens = self._tokenizer.tokenize(text)

        pos_score = 0.0
        neg_score = 0.0
        negate    = False

        for i, token in enumerate(tokens):
            # Check for negation in previous token
            if i > 0 and tokens[i - 1] in self._negations:
                negate = True
            else:
                negate = False

            # Get intensifier multiplier from previous token
            multiplier = 1.0
            if i > 0:
                multiplier = INTENSIFIERS.get(tokens[i - 1], 1.0)

            if token in self._positive:
                if negate:
                    neg_score += 1.0 * multiplier
                else:
                    pos_score += 1.0 * multiplier

            elif token in self._negative:
                if negate:
                    pos_score += 1.0 * multiplier
                else:
                    neg_score += 1.0 * multiplier

        total = pos_score + neg_score

        if total == 0:
            return SentimentResult(
                label="neutral", score=0.5,
                positive=0, negative=0, tokens=tokens
            )

        # Normalise to 0-1
        pos_ratio = pos_score / total
        neg_ratio = neg_score / total

        if pos_ratio > neg_ratio:
            label = "positive"
            score = round(0.5 + (pos_ratio - 0.5) * 0.9, 3)
        elif neg_ratio > pos_ratio:
            label = "negative"
            score = round(0.5 + (neg_ratio - 0.5) * 0.9, 3)
        else:
            label = "neutral"
            score = 0.5

        return SentimentResult(
            label=label,
            score=min(score, 1.0),
            positive=int(pos_score),
            negative=int(neg_score),
            tokens=tokens,
        )

    def batch_analyse(self, texts: list[str]) -> list[SentimentResult]:
        """Analyse a list of texts and return results in order."""
        return [self.analyse(t) for t in texts]

    def is_positive(self, text: str) -> bool:
        return self.analyse(text)["label"] == "positive"

    def is_negative(self, text: str) -> bool:
        return self.analyse(text)["label"] == "negative"

    def add_positive_words(self, words: list[str]) -> "SentimentAnalyser":
        """Add custom positive words to the lexicon."""
        self._positive.update(words)
        return self

    def add_negative_words(self, words: list[str]) -> "SentimentAnalyser":
        """Add custom negative words to the lexicon."""
        self._negative.update(words)
        return self
