"""
profanity.py — Sinhala profanity / bad-word filter
Part of sinkit / sinhala-toolkit

Usage:
    from sinkit.profanity import ProfanityFilter

    pf = ProfanityFilter()
    pf.contains_profanity("ඔහු මෝඩයා")          # True
    pf.censor("ඔහු මෝඩයා")                      # "ඔහු ***"
    pf.highest_severity("ඔහු කුණු කාරයා")       # "moderate"
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Optional, TypedDict


_SEVERITY_RANK: dict[str, int] = {
    "mild":           1,
    "singlish_slang": 2,
    "moderate":       3,
    "strong":         4,
    "hate_speech":    5,
}

# Boundary class: letters, digits, Sinhala marks (U+0D80-U+0DF3)
_WORD_CHAR_CLASS = r"[\w\u0D80-\u0DF3]"


def _default_profanity_path() -> Path:
    """Locate profanity.json across repo checkout, package dir, or installed data."""
    candidates = [
        Path(__file__).resolve().parent / "data" / "profanity.json",
        Path(__file__).resolve().parent.parent.parent / "data" / "profanity.json",
        Path(sys.prefix) / "share" / "sinkit" / "data" / "profanity.json",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[1]


class ProfanityMatch(TypedDict):
    word: str
    severity: str


class ProfanityFilter:
    """
    Detect and censor offensive Sinhala and Singlish words/phrases
    with severity classification.

    Examples
    --------
    >>> pf = ProfanityFilter()
    >>> pf.contains_profanity("ඔහු මෝඩයා")
    True
    >>> pf.censor("ඔහු මෝඩයා")
    'ඔහු ***'
    >>> pf.highest_severity("ආයුබෝවන්") is None
    True
    """

    def __init__(self, json_path: Optional[str | Path] = None) -> None:
        self._path: Path = Path(json_path) if json_path else _default_profanity_path()
        self._word_severities: dict[str, str] = {}
        self._load()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def contains_profanity(
        self,
        text: str,
        *,
        severities: Optional[list[str]] = None,
    ) -> bool:
        """Return True if text contains any matched profanity."""
        return len(self.find_matches(text, severities=severities)) > 0

    def find_matches(
        self,
        text: str,
        *,
        severities: Optional[list[str]] = None,
    ) -> list[ProfanityMatch]:
        """Find all matched profanity words/phrases with severity levels."""
        normalised = self._normalise_for_matching(text)
        if not normalised:
            return []

        candidates = self._filtered_words(severities)
        if not candidates:
            return []

        matches: list[ProfanityMatch] = []
        seen: set[str] = set()

        for word, severity in candidates:
            pattern = self._build_word_pattern(word)
            if pattern.search(normalised) and word not in seen:
                seen.add(word)
                matches.append({"word": word, "severity": severity})

        return matches

    def censor(
        self,
        text: str,
        replacement: str = "***",
        *,
        severities: Optional[list[str]] = None,
    ) -> str:
        """Replace matched profanity words/phrases with replacement string."""
        if not text.strip():
            return text

        candidates = self._filtered_words(severities)
        if not candidates:
            return text

        result = text
        for word, _ in candidates:
            pattern = self._build_word_pattern(word, allow_zwj_between_chars=True)
            result = pattern.sub(replacement, result)

        return result

    def highest_severity(self, text: str) -> Optional[str]:
        """Return the highest severity level found in text, or None if clean."""
        matches = self.find_matches(text)
        if not matches:
            return None

        best: Optional[str] = None
        best_rank = 0
        for match in matches:
            sev = match["severity"]
            rank = _SEVERITY_RANK.get(sev, 1)
            if rank > best_rank:
                best_rank = rank
                best = sev
        return best

    def add_words(self, words: list[str], severity: str = "moderate") -> "ProfanityFilter":
        """Add custom words/phrases at runtime."""
        for word in words:
            key = self._normalise_key(word)
            if key:
                self._word_severities[key] = severity
        return self

    def remove_words(self, words: list[str]) -> "ProfanityFilter":
        """Remove words/phrases from the active filter at runtime."""
        for word in words:
            self._word_severities.pop(self._normalise_key(word), None)
        return self

    def words(self, severity: Optional[str] = None) -> list[str]:
        """Return loaded words, optionally filtered by severity level."""
        if severity is None:
            return list(self._word_severities.keys())
        return [w for w, sev in self._word_severities.items() if sev == severity]

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _load(self) -> None:
        if not self._path.exists():
            raise FileNotFoundError(
                f"Profanity file not found: {self._path}\n"
                "Make sure data/profanity.json exists."
            )

        with open(self._path, encoding="utf-8") as f:
            data = json.load(f)

        severity_map: dict[str, str] = data.get("severity_map", {})
        flat_list: list[str] = data.get("flat_list", [])

        category_severity: dict[str, str] = {}
        for cat_name, section in data.get("categories", {}).items():
            if not isinstance(section, dict):
                continue
            for sub_key, value in section.items():
                if sub_key.startswith("_") or not isinstance(value, list):
                    continue
                for word in value:
                    if isinstance(word, str):
                        category_severity[self._normalise_key(word)] = cat_name

        for word in flat_list:
            if not isinstance(word, str):
                continue
            key = self._normalise_key(word)
            if not key:
                continue
            self._word_severities[key] = (
                severity_map.get(word)
                or category_severity.get(key)
                or "moderate"
            )

    def _filtered_words(self, severities: Optional[list[str]]) -> list[tuple[str, str]]:
        if severities is None:
            items = list(self._word_severities.items())
        else:
            allowed = set(severities)
            items = [(w, sev) for w, sev in self._word_severities.items() if sev in allowed]

        # Longest phrases first so multi-word phrases match before single words
        items.sort(key=lambda pair: len(pair[0]), reverse=True)
        return items

    def _normalise_key(self, word: str) -> str:
        return re.sub(r"\s+", " ", word.strip()).lower()

    def _normalise_for_matching(self, text: str) -> str:
        # Strip zero-width characters (including ZWJ bypasses) for detection
        text = re.sub(r"[\u200B\u200C\u200D\uFEFF]", "", text)
        return re.sub(r"\s+", " ", text.strip())

    def _build_word_pattern(
        self,
        word: str,
        *,
        allow_zwj_between_chars: bool = False,
    ) -> re.Pattern[str]:
        if allow_zwj_between_chars:
            body = r"[\u200B\u200C\u200D]*".join(re.escape(ch) for ch in word)
        else:
            body = re.escape(word)

        return re.compile(
            rf"(?<!{_WORD_CHAR_CLASS}){body}(?!{_WORD_CHAR_CLASS})",
            re.IGNORECASE | re.UNICODE,
        )
