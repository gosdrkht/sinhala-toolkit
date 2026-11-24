"""
normalizer.py — Sinhala number, currency & date normaliser
Part of sinkit / sinhala-toolkit

Usage:
    from sinkit.normalizer import Normalizer

    norm = Normalizer()
    norm.sinhala_digits_to_ascii("෨෦෨෪")         # "2024"
    norm.extract_currency("මිල රු. 5,000 කි")     # [{"raw": "රු. 5,000", "amount": 5000.0, "currency": "LKR"}]
    norm.extract_dates("2026 නොවැම්බර් 24")       # [{"raw": "2026 නොවැම්බර් 24", "iso": "2026-11-24"}]
"""

from __future__ import annotations

import re
from typing import TypedDict

_SINHALA_TO_ASCII = str.maketrans("෦෧෨෩෪෫෬෭෮෯", "0123456789")
_ASCII_TO_SINHALA = str.maketrans("0123456789", "෦෧෨෩෪෫෬෭෮෯")

_MULTIPLIERS: dict[str, float] = {
    "කෝටි":    10_000_000.0,
    "කෝටිය":   10_000_000.0,
    "කෝටියක්": 10_000_000.0,
    "ලක්ෂ":    100_000.0,
    "ලක්ෂය":   100_000.0,
    "ලක්ෂයක්": 100_000.0,
    "දහස":     1_000.0,
    "දහසක්":   1_000.0,
    "දාහ":     1_000.0,
    "දාහක්":   1_000.0,
    "සියය":    100.0,
    "සියයක්":  100.0,
}

_SINHALA_MONTHS: dict[str, int] = {
    "ජනවාරි":     1,
    "පෙබරවාරි":   2,
    "මාර්තු":     3,
    "අප්‍රේල්":   4,
    "මැයි":       5,
    "ජූනි":       6,
    "ජූලි":       7,
    "අගෝස්තු":    8,
    "සැප්තැම්බර්": 9,
    "ඔක්තෝබර්":   10,
    "නොවැම්බර්":  11,
    "දෙසැම්බර්":  12,
}

_MULT_RE = "|".join(re.escape(k) for k in _MULTIPLIERS)
_CURRENCY_RE = re.compile(
    rf"(?:රුපියල්|රු\.?|LKR|Rs\.?)\s*(?:({_MULT_RE})\s*)?(\d[\d,]*(?:\.\d+)?)(?:\s*({_MULT_RE}))?",
    re.IGNORECASE | re.UNICODE,
)
_MONTH_RE = "|".join(re.escape(k) for k in _SINHALA_MONTHS)
_DATE_YMD_RE = re.compile(rf"(\d{{4}})\s+({_MONTH_RE})\s+(\d{{1,2}})", re.UNICODE)
_DATE_DMY_RE = re.compile(rf"(\d{{1,2}})\s+({_MONTH_RE})\s+(\d{{4}})", re.UNICODE)


class CurrencyMatch(TypedDict):
    raw: str
    amount: float
    currency: str


class DateMatch(TypedDict):
    raw: str
    iso: str


class Normalizer:
    """
    Normalise Sinhala digits, currency amounts, and dates.

    Examples
    --------
    >>> n = Normalizer()
    >>> n.sinhala_digits_to_ascii("෨෦෨෪")
    '2024'
    >>> n.ascii_digits_to_sinhala("2024")
    '෨෦෨෪'
    """

    def sinhala_digits_to_ascii(self, text: str) -> str:
        """Convert Sinhala Lith digits (෦–෯) to ASCII digits (0–9)."""
        return text.translate(_SINHALA_TO_ASCII)

    def ascii_digits_to_sinhala(self, text: str) -> str:
        """Convert ASCII digits (0–9) to Sinhala Lith digits (෦–෯)."""
        return text.translate(_ASCII_TO_SINHALA)

    def extract_currency(self, text: str) -> list[CurrencyMatch]:
        """Extract LKR / Rs. / රු. / රුපියල් currency amounts including ලක්ෂ & කෝටි."""
        text = self.sinhala_digits_to_ascii(text)
        results: list[CurrencyMatch] = []

        for m in _CURRENCY_RE.finditer(text):
            raw = m.group(0).strip()
            pre_mult = m.group(1) or ""
            num_str = m.group(2).replace(",", "")
            post_mult = m.group(3) or ""

            amount = float(num_str)
            if pre_mult in _MULTIPLIERS:
                amount *= _MULTIPLIERS[pre_mult]
            elif post_mult in _MULTIPLIERS:
                amount *= _MULTIPLIERS[post_mult]

            results.append({"raw": raw, "amount": amount, "currency": "LKR"})

        return results

    def extract_dates(self, text: str) -> list[DateMatch]:
        """Extract Sinhala dates (e.g. '2026 නොවැම්බර් 24') into ISO YYYY-MM-DD."""
        text = self.sinhala_digits_to_ascii(text)
        results: list[DateMatch] = []

        for m in _DATE_YMD_RE.finditer(text):
            year, month, day = int(m.group(1)), _SINHALA_MONTHS[m.group(2)], int(m.group(3))
            if 1 <= day <= 31:
                results.append({"raw": m.group(0), "iso": f"{year:04d}-{month:02d}-{day:02d}"})

        for m in _DATE_DMY_RE.finditer(text):
            day, month, year = int(m.group(1)), _SINHALA_MONTHS[m.group(2)], int(m.group(3))
            if 1 <= day <= 31:
                results.append({"raw": m.group(0), "iso": f"{year:04d}-{month:02d}-{day:02d}"})

        return results

    def normalize_text(self, text: str) -> str:
        """Convert Sinhala digits to ASCII and standardise currency prefixes to 'LKR '."""
        text = self.sinhala_digits_to_ascii(text)
        text = re.sub(r"(?:රුපියල්|රු\.?|Rs\.?)\s*(?=\d)", "LKR ", text, flags=re.IGNORECASE | re.UNICODE)
        return re.sub(r"\s+", " ", text.strip())
