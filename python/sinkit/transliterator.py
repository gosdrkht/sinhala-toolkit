"""
transliterator.py — Phonetic Singlish ↔ Sinhala Unicode transliterator & slugify
Part of sinkit / sinhala-toolkit

Usage:
    from sinkit.transliterator import Transliterator

    tr = Transliterator()
    tr.to_sinhala("aayubowan lanka")               # "ආයුබෝවන් ලංකා"
    tr.to_singlish("ශ්‍රී ලංකාව ලස්සන රටකි")       # "shri lankawa lassana rataki"
    tr.slugify("ශ්‍රී ලංකාව ලස්සන රටකි")           # "shri-lankawa-lassana-rataki"
"""

from __future__ import annotations

import re

_HAL = "\u0DCA"
_ZWJ = "\u200D"

_WORD_OVERRIDES: dict[str, str] = {
    "aayubowan": "ආයුබෝවන්",
    "ayubowan":  "ආයුබෝවන්",
    "kohomada":  "කොහොමද",
    "istuti":    "ස්තූතියි",
    "sthuthi":   "ස්තූතියි",
    "sthuthiyi": "ස්තූතියි",
    "shri":      "ශ්\u200Dරී",
    "sri":       "ශ්\u200Dරී",
    "lanka":     "ලංකා",
    "lankawa":   "ලංකාව",
    "lankava":   "ලංකාව",
    "sinhala":   "සිංහල",
    "colombo":   "කොළඹ",
    "kolamba":   "කොළඹ",
    "gedara":    "ගෙදර",
    "hondai":    "හොඳයි",
    "hondayi":   "හොඳයි",
    "hoda":      "හොඳ",
    "honda":     "හොඳ",
    "lassana":   "ලස්සන",
    "oyata":     "ඔයාට",
    "mama":      "මම",
    "oba":       "ඔබ",
    "api":       "අපි",
    "ow":        "ඔව්",
    "na":        "නෑ",
    "nae":       "නෑ",
    "naha":      "නැහැ",
}

_CONSONANTS: list[tuple[str, str]] = [
    ("nndh", "ඳ"), ("nnd", "ඬ"), ("nng", "ඟ"), ("ndh", "ඳ"),
    ("mb", "ඹ"), ("kh", "ඛ"), ("gh", "ඝ"), ("ch", "ච"),
    ("jh", "ඣ"), ("th", "ත"), ("dh", "ද"), ("ph", "ඵ"),
    ("bh", "භ"), ("sh", "ශ"), ("Sh", "ෂ"), ("gn", "ඥ"),
    ("kn", "ඤ"), ("ng", "ං"), ("Th", "ථ"), ("Dh", "ධ"),
    ("Ch", "ඡ"), ("Lu", "ළු"),
    ("k", "ක"), ("g", "ග"), ("c", "ච"), ("j", "ජ"),
    ("T", "ට"), ("D", "ඩ"), ("N", "ණ"), ("t", "ට"),
    ("d", "ද"), ("n", "න"), ("p", "ප"), ("b", "බ"),
    ("m", "ම"), ("y", "ය"), ("r", "ර"), ("l", "ල"),
    ("L", "ළ"), ("v", "ව"), ("w", "ව"), ("s", "ස"),
    ("h", "හ"), ("f", "ෆ"),
]

_INDEPENDENT_VOWELS: list[tuple[str, str]] = [
    ("aau", "ඖ"), ("aaE", "ඈ"), ("aee", "ඈ"),
    ("aa", "ආ"), ("ae", "ඇ"), ("ii", "ඊ"), ("ee", "ඊ"),
    ("uu", "ඌ"), ("oo", "ඕ"), ("ai", "ඓ"), ("au", "ඖ"), ("ou", "ඖ"),
    ("a", "අ"), ("i", "ඉ"), ("u", "උ"), ("e", "එ"), ("o", "ඔ"),
]

_VOWEL_SIGNS: list[tuple[str, str]] = [
    ("aee", "ෑ"), ("aa", "ා"), ("ae", "ැ"), ("ii", "ී"), ("ee", "ී"),
    ("uu", "ූ"), ("oo", "ෝ"), ("ai", "ෛ"), ("au", "ෞ"), ("ou", "ෞ"),
    ("a", ""), ("i", "ි"), ("u", "ු"), ("e", "ෙ"), ("o", "ො"),
]

_SINHALA_INDEPENDENT_VOWELS: dict[str, str] = {
    "අ": "a",  "ආ": "aa", "ඇ": "ae", "ඈ": "aee",
    "ඉ": "i",  "ඊ": "ii", "උ": "u",  "ඌ": "uu",
    "ඍ": "ri", "ඎ": "rii","එ": "e",  "ඒ": "ee",
    "ඓ": "ai", "ඔ": "o",  "ඕ": "oo", "ඖ": "au",
}

_SINHALA_CONSONANTS: dict[str, str] = {
    "ක": "k",  "ඛ": "kh", "ග": "g",  "ඝ": "gh", "ඞ": "ng", "ඟ": "ng",
    "ච": "ch", "ඡ": "chh","ජ": "j",  "ඣ": "jh", "ඤ": "gn", "ඥ": "gn",
    "ට": "t",  "ඨ": "th", "ඩ": "d",  "ඪ": "dh", "ණ": "n",  "ඬ": "nd",
    "ත": "th", "ථ": "th", "ද": "d",  "ධ": "dh", "න": "n",  "ඳ": "nd",
    "ප": "p",  "ඵ": "ph", "බ": "b",  "භ": "bh", "ම": "m",  "ඹ": "mb",
    "ය": "y",  "ර": "r",  "ල": "l",  "ව": "w",
    "ශ": "sh", "ෂ": "sh", "ස": "s",  "හ": "h",  "ළ": "l",  "ෆ": "f",
}

_SINHALA_VOWEL_SIGNS: dict[str, str] = {
    "ා": "a",  "ැ": "ae", "ෑ": "ae", "ි": "i",  "ී": "i",
    "ු": "u",  "ූ": "u",  "ෘ": "ru", "ෙ": "e",  "ේ": "e",
    "ෛ": "ai", "ො": "o",  "ෝ": "o",  "ෞ": "au", "ෟ": "u",
    "ෲ": "ruu","ෳ": "au",
}

_SINHALA_SPECIALS: dict[str, str] = {
    "ං": "n",
    "ඃ": "h",
}


class Transliterator:
    """
    Phonetic Singlish ↔ Sinhala Unicode transliterator and URL slug generator.

    Examples
    --------
    >>> tr = Transliterator()
    >>> tr.to_sinhala("aayubowan lanka")
    'ආයුබෝවන් ලංකා'
    >>> tr.slugify("ශ්‍රී ලංකාව ලස්සන රටකි")
    'shri-lankawa-lassana-rataki'
    """

    def to_sinhala(self, text: str) -> str:
        """Convert phonetic Singlish text to Sinhala Unicode."""
        if not text.strip():
            return ""
        return re.sub(r"[a-zA-Z]+", lambda m: self._word_to_sinhala(m.group(0)), text)

    def to_singlish(self, text: str) -> str:
        """Convert Sinhala Unicode text to readable Romanized Singlish."""
        if not text.strip():
            return ""

        chars = list(text)
        n = len(chars)
        out: list[str] = []
        i = 0

        while i < n:
            ch = chars[i]

            if ch in _SINHALA_CONSONANTS:
                base = _SINHALA_CONSONANTS[ch]
                i += 1

                if i < n and chars[i] == _HAL:
                    i += 1
                    if i < n and chars[i] == _ZWJ:
                        i += 1
                    out.append(base)
                    continue

                if i < n and chars[i] in _SINHALA_VOWEL_SIGNS:
                    out.append(base + _SINHALA_VOWEL_SIGNS[chars[i]])
                    i += 1
                    continue

                out.append(base + "a")
                continue

            if ch in _SINHALA_INDEPENDENT_VOWELS:
                out.append(_SINHALA_INDEPENDENT_VOWELS[ch])
                i += 1
                continue

            if ch in _SINHALA_SPECIALS:
                out.append(_SINHALA_SPECIALS[ch])
                i += 1
                continue

            if ch in (_ZWJ, _HAL):
                i += 1
                continue

            out.append(ch)
            i += 1

        return "".join(out)

    def slugify(self, text: str, separator: str = "-") -> str:
        """Generate an SEO-friendly ASCII URL slug from Sinhala, English, or mixed text."""
        romanized = self.to_singlish(text).lower()
        slug = re.sub(r"[^a-z0-9]+", separator, romanized)
        return slug.strip(separator)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _word_to_sinhala(self, word: str) -> str:
        lower = word.lower()
        if lower in _WORD_OVERRIDES:
            return _WORD_OVERRIDES[lower]

        n = len(word)
        out: list[str] = []
        i = 0

        while i < n:
            cons = self._match_prefix(word, i, _CONSONANTS)
            if cons is not None:
                key, sinhala_cons = cons
                i += len(key)

                if sinhala_cons == "ං":
                    out.append(sinhala_cons)
                    continue

                # Rakaransaya (consonant + 'r' + vowel), e.g. 'kra', 'pri'
                if (
                    i < n
                    and word[i] == "r"
                    and i + 1 < n
                    and self._match_prefix(word, i + 1, _VOWEL_SIGNS) is not None
                    and key != "r"
                ):
                    i += 1
                    vm = self._match_prefix(word, i, _VOWEL_SIGNS)
                    sign = ""
                    if vm is not None:
                        vkey, sign = vm
                        i += len(vkey)
                    out.append(sinhala_cons + _HAL + _ZWJ + "ර" + sign)
                    continue

                vm = self._match_prefix(word, i, _VOWEL_SIGNS)
                if vm is not None:
                    vkey, sign = vm
                    i += len(vkey)
                    out.append(sinhala_cons + sign)
                else:
                    out.append(sinhala_cons + _HAL)
                continue

            vm = self._match_prefix(word, i, _INDEPENDENT_VOWELS)
            if vm is not None:
                vkey, sinhala_vowel = vm
                i += len(vkey)
                out.append(sinhala_vowel)
                continue

            out.append(word[i])
            i += 1

        return "".join(out)

    def _match_prefix(
        self, word: str, offset: int, table: list[tuple[str, str]]
    ) -> tuple[str, str] | None:
        sub = word[offset:]
        for key, val in table:
            if sub.startswith(key):
                return key, val
        lower_sub = sub.lower()
        for key, val in table:
            if lower_sub.startswith(key.lower()):
                return key, val
        return None
