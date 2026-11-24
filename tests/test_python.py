"""
test_python.py — Tests for the Python sinkit package.
Run: PYTHONPATH=python pytest tests/test_python.py
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from sinkit import (
    SentimentAnalyser,
    Stopwords,
    TextCleaner,
    Tokenizer,
    all_stopwords,
    filter_stopwords,
    is_stopword,
)


def test_stopwords_loading_and_queries():
    sw = Stopwords()
    assert len(sw) >= 100
    assert sw.is_stopword("මම") is True
    assert sw.is_stopword("ගුරු") is False
    assert sw.filter(["මම", "ගුරු", "සඳහා"]) == ["ගුරු"]
    assert "pronouns" in sw.categories()
    assert len(sw.by_category("pronouns")) > 0
    assert sw.by_category("flat_list") == []
    assert is_stopword("මම") is True
    assert filter_stopwords(["මම", "ගුරු"]) == ["ගුරු"]
    assert len(all_stopwords()) == len(sw)


def test_text_cleaner():
    c = TextCleaner()
    assert c.normalise_whitespace("  මම   ඔබ   ") == "මම ඔබ"
    assert (
        c.clean("මම සහ ඔබ හොඳ ගුරුවරයා ළඟ ඉගෙන ගත්තා", remove_stopwords=True)
        == "හොඳ ගුරුවරයා ඉගෙන ගත්තා"
    )
    assert c.clean("මෙය good idea එකක්", remove_english=True) == "මෙය එකක්"
    assert c.clean("2024 දී ජය", remove_numbers=True) == "දී ජය"
    assert c.detect_script("ආයුබෝවන්") == "sinhala"
    assert c.detect_script("Hello World") == "english"
    assert c.detect_script("Hello ආයුබෝවන්") == "mixed"
    assert c.detect_script("12345") == "unknown"
    assert c.is_pure_sinhala("ආයුබෝවන්") is True
    assert c.is_pure_sinhala("Hello") is False


def test_text_cleaner_remove_punctuation_preserves_sinhala():
    c = TextCleaner()
    assert (
        c.remove_punctuation("ශ්\u200Dරී ලංකාව! හොඳයි, ගෙදර.")
        == "ශ්\u200Dරී ලංකාව හොඳයි ගෙදර"
    )
    assert c.remove_punctuation("ඔහු ගියා\u0964", keep_danda=True) == "ඔහු ගියා\u0964"
    assert c.remove_punctuation("ඔහු ගියා\u0964", keep_danda=False) == "ඔහු ගියා"
    assert c.remove_punctuation("hello_world!") == "hello world"


def test_tokenizer():
    t = Tokenizer()
    assert t.split_sentences("ඔහු ගෙදර ගියා\u0964 ඇය පාසලට ගියාය\u0964") == [
        "ඔහු ගෙදර ගියා",
        "ඇය පාසලට ගියාය",
    ]
    assert t.split_sentences("ඔහු ප්‍රඥ.") == ["ඔහු ප්‍රඥ"]
    assert t.tokenize("ශ්\u200Dරී ලංකාව ලස්සන රටකි!") == [
        "ශ්\u200Dරී",
        "ලංකාව",
        "ලස්සන",
        "රටකි",
    ]
    assert t.graphemes("ශ්\u200Dරී") == ["ශ්\u200Dරී"]
    assert t.classify_token("ලංකාව") == "sinhala"
    assert t.classify_token("cricket") == "english"
    assert t.classify_token("2024") == "number"
    assert t.classify_token(".,!") == "punctuation"
    assert t.classify_token("v2ලංකා") == "mixed"


def test_sentiment_analyser():
    sa = SentimentAnalyser()
    pos = sa.analyse("මෙය ඉතා හොඳ චිත්‍රපටයකි")
    assert pos["label"] == "positive"
    assert pos["positive"] >= 1

    # Post-negation (standard Sinhala SOV word order)
    neg = sa.analyse("මෙය හොඳ නෑ")
    assert neg["label"] == "negative"
    assert neg["negative"] >= 1

    # Negated negative -> positive
    neg_neg = sa.analyse("මෙය නරක නෑ")
    assert neg_neg["label"] == "positive"

    neutral = sa.analyse("ඔහු ගෙදර ගියා")
    assert neutral["label"] == "neutral"
