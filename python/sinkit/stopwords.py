"""
stopwords.py — Sinhala stopwords loader
Part of sinkit / sinhala-toolkit

Usage:
    from sinkit.stopwords import Stopwords

    sw = Stopwords()
    print(sw.all())               # full list
    print(sw.by_category("pronouns"))
    print(sw.is_stopword("මම"))   # True
    print(sw.filter(["මම", "ගුරු", "සඳහා"]))  # ["ගුරු"]
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional


# Default path to the shared data file
_DATA_DIR  = Path(__file__).resolve().parent.parent.parent / "data"
_SW_FILE   = _DATA_DIR / "stopwords.json"


class Stopwords:
    """
    Load and query the curated Sinhala stopwords dataset.

    Examples
    --------
    >>> sw = Stopwords()
    >>> sw.is_stopword("මම")
    True
    >>> sw.is_stopword("ගුරු")
    False
    >>> sw.filter(["මම", "ගුරු", "සඳහා"])
    ['ගුරු']
    """

    def __init__(self, json_path: Optional[str | Path] = None) -> None:
        self._path: Path = Path(json_path) if json_path else _SW_FILE
        self._data: dict = {}
        self._flat: list[str] = []
        self._load()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def all(self) -> list[str]:
        """Return the full flat list of stopwords."""
        return list(self._flat)

    def by_category(self, category: str) -> list[str]:
        """
        Return stopwords for a specific category.

        Available: pronouns, conjunctions, prepositions, particles,
                   auxiliary_verbs, question_words, demonstratives,
                   numerals, common_adverbs, discourse_markers
        """
        section = self._data.get(category, {})
        words: list[str] = []

        for key, value in section.items():
            if key == "_description":
                continue
            if isinstance(value, list):
                words.extend(value)
            elif isinstance(value, str):
                words.append(value)

        return list(dict.fromkeys(words))  # deduplicate, preserve order

    def categories(self) -> list[str]:
        """Return all available category names."""
        return [
            k for k in self._data.keys()
            if not k.startswith("_") and k != "flat_list"
        ]

    def is_stopword(self, word: str) -> bool:
        """Check if a single word is a stopword."""
        return word.strip() in self._flat_set

    def filter(self, tokens: list[str]) -> list[str]:
        """Remove stopwords from a list of tokens."""
        return [t for t in tokens if not self.is_stopword(t)]

    def add(self, word: str) -> "Stopwords":
        """Add a custom stopword at runtime (does not persist to file)."""
        w = word.strip()
        if w and w not in self._flat_set:
            self._flat.append(w)
            self._flat_set.add(w)
        return self

    def add_many(self, words: list[str]) -> "Stopwords":
        """Add multiple custom stopwords at runtime."""
        for w in words:
            self.add(w)
        return self

    def remove(self, word: str) -> "Stopwords":
        """Remove a word from the stopwords list at runtime."""
        w = word.strip()
        self._flat = [t for t in self._flat if t != w]
        self._flat_set.discard(w)
        return self

    def meta(self) -> dict:
        """Return dataset metadata."""
        return self._data.get("_meta", {})

    def __len__(self) -> int:
        return len(self._flat)

    def __contains__(self, word: str) -> bool:
        return self.is_stopword(word)

    def __repr__(self) -> str:
        return f"Stopwords(count={len(self)}, path='{self._path}')"

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    def _load(self) -> None:
        if not self._path.exists():
            raise FileNotFoundError(
                f"Stopwords file not found: {self._path}\n"
                "Make sure data/stopwords.json exists."
            )

        with open(self._path, encoding="utf-8") as f:
            self._data = json.load(f)

        self._flat     = self._data.get("flat_list", [])
        self._flat_set = set(self._flat)


# ---------------------------------------------------------------------------
# Module-level convenience functions
# ---------------------------------------------------------------------------

_default: Optional[Stopwords] = None


def _get_default() -> Stopwords:
    global _default
    if _default is None:
        _default = Stopwords()
    return _default


def is_stopword(word: str) -> bool:
    """Module-level shortcut: check if a word is a stopword."""
    return _get_default().is_stopword(word)


def filter_stopwords(tokens: list[str]) -> list[str]:
    """Module-level shortcut: filter stopwords from a token list."""
    return _get_default().filter(tokens)


def all_stopwords() -> list[str]:
    """Module-level shortcut: get all stopwords."""
    return _get_default().all()
