"""
sinkit — Sinhala NLP Toolkit (Python)
Part of sinhala-toolkit

The missing developer toolkit for Sinhala language processing.
සිංහල භාෂා සැකසීම සඳහා නවීන developer toolkit එක.

Quick start:
    from sinkit.cleaner import TextCleaner
    from sinkit.tokenizer import Tokenizer
    from sinkit.stopwords import Stopwords
    from sinkit.sentiment import SentimentAnalyser

GitHub: https://github.com/gosdrkht/sinhala-toolkit
License: MIT
"""

from .cleaner   import TextCleaner
from .tokenizer import Tokenizer
from .stopwords import Stopwords, is_stopword, filter_stopwords, all_stopwords
from .sentiment import SentimentAnalyser

__version__   = "1.0.0"
__author__    = "gosdrkht"
__license__   = "MIT"
__all__ = [
    "TextCleaner",
    "Tokenizer",
    "Stopwords",
    "SentimentAnalyser",
    "is_stopword",
    "filter_stopwords",
    "all_stopwords",
]
