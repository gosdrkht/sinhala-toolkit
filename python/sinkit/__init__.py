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

from .cleaner        import TextCleaner
from .tokenizer      import Tokenizer
from .stopwords      import Stopwords, is_stopword, filter_stopwords, all_stopwords
from .sentiment      import SentimentAnalyser
from .profanity      import ProfanityFilter
from .transliterator import Transliterator
from .stemmer        import Stemmer
from .keywords       import KeywordExtractor
from .normalizer     import Normalizer
from .chunker        import Chunker

__version__   = "1.2.0"
__author__    = "gosdrkht"
__license__   = "MIT"
__all__ = [
    "TextCleaner",
    "Tokenizer",
    "Stopwords",
    "SentimentAnalyser",
    "ProfanityFilter",
    "Transliterator",
    "Stemmer",
    "KeywordExtractor",
    "Normalizer",
    "Chunker",
    "is_stopword",
    "filter_stopwords",
    "all_stopwords",
]
