"""
test_python.py — Tests for the Python sinkit package.
Run: PYTHONPATH=python pytest tests/test_python.py
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from sinkit import (
    Chunker,
    KeywordExtractor,
    Normalizer,
    ProfanityFilter,
    SentimentAnalyser,
    Stemmer,
    Stopwords,
    TextCleaner,
    Tokenizer,
    Transliterator,
    all_stopwords,
    filter_stopwords,
    is_stopword,
)
from sinkit.cli import main as cli_main


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
    assert c.detect_script("வணக்கம்") == "tamil"
    assert c.detect_script("Hello World") == "english"
    assert c.detect_script("Hello ආයුබෝවන්") == "mixed"
    assert c.detect_script("ආයුබෝවන් வணக்கம்") == "mixed"
    assert c.contains_tamil("வணக்கம்") is True
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


def test_profanity_filter():
    pf = ProfanityFilter()
    assert len(pf.words()) >= 40
    assert pf.contains_profanity("ඔහු මෝඩයා") is True
    assert pf.contains_profanity("ඔහු බොරු කාරයා") is True
    assert pf.contains_profanity("This is stupid!") is True
    assert pf.contains_profanity("ආයුබෝවන් ලංකාව") is False
    assert pf.contains_profanity("I love football") is False
    assert pf.contains_profanity("ඔහු මෝ\u200Dඩයා") is True
    assert pf.highest_severity("මෝඩයා සහ වංචාකාරයා") == "moderate"
    assert pf.highest_severity("හූකාරයා") == "strong"
    assert pf.highest_severity("ආයුබෝවන්") is None
    assert pf.contains_profanity("ඔහු මෝඩයා", severities=["strong"]) is False
    assert pf.contains_profanity("ඔහු මෝඩයා", severities=["mild"]) is True
    assert pf.censor("ඔහු මෝඩයා") == "ඔහු ***"
    assert pf.censor("ඔහු බොරු කාරයා වේ") == "ඔහු *** වේ"
    assert pf.censor("ඔහු මෝ\u200Dඩයා") == "ඔහු ***"

    pf.add_words(["කුජීත"], severity="moderate")
    assert pf.contains_profanity("මෙය කුජීත") is True
    pf.remove_words(["කුජීත"])
    assert pf.contains_profanity("මෙය කුජීත") is False


def test_transliterator_and_slugify():
    tr = Transliterator()
    assert tr.to_sinhala("aayubowan lanka") == "ආයුබෝවන් ලංකා"
    assert tr.to_sinhala("kama") == "කම"
    assert tr.to_singlish("ශ්\u200Dරී ලංකාව") == "shri lankawa"
    assert tr.slugify("ශ්\u200Dරී ලංකාව ලස්සන රටකි") == "shri-lankawa-lassana-rataki"
    assert tr.slugify("ලංකා Cricket 2026!") == "lanka-cricket-2026"


def test_stemmer():
    st = Stemmer()
    assert st.stem("ගෙදරට") == "ගෙදර"
    assert st.stem("ගෙදරින්") == "ගෙදර"
    assert st.stem("ගෙදරයි") == "ගෙදර"
    assert st.stem("මම") == "මම"


def test_keyword_extractor_and_summarizer():
    ke = KeywordExtractor()
    kw = ke.extract("ශ්\u200Dරී ලංකාව ලස්සන රටකි ශ්\u200Dරී ලංකාව හොඳ රටකි", top_k=2)
    assert [item["keyword"] for item in kw] == ["ශ්\u200Dරී", "ලංකාව"]

    doc = "ශ්\u200Dරී ලංකාව ඉතා ලස්සන රටකි\u0964 ශ්\u200Dරී ලංකාව සංචාරකයන් අතර ජනප්‍රියයි\u0964 අද වැස්ස වහිනවා\u0964"
    summary = ke.summarize(doc, num_sentences=2)
    assert len(Tokenizer().split_sentences(summary)) == 2


def test_normalizer():
    norm = Normalizer()
    assert norm.sinhala_digits_to_ascii("෨෦෨෪") == "2024"
    assert norm.ascii_digits_to_sinhala("2024") == "෨෦෨෪"
    assert norm.extract_currency("මිල රු. 5,000 කි")[0]["amount"] == 5000.0
    assert norm.extract_currency("වටිනාකම රු. ලක්ෂ 5 කි")[0]["amount"] == 500000.0
    assert norm.extract_dates("උත්සවය 2026 නොවැම්බර් 24 පැවැත්වේ")[0]["iso"] == "2026-11-24"
    assert norm.normalize_text("මිල රු. ෫,෦෦෦") == "මිල LKR 5,000"


def test_chunker():
    ch = Chunker()
    assert ch.chunk("ඔහු ගෙදර ගියා\u0964 ඇය පාසලට ගියාය\u0964", max_chars=20) == [
        "ඔහු ගෙදර ගියා\u0964",
        "ඇය පාසලට ගියාය\u0964",
    ]
    assert ch.estimate_tokens("ශ්\u200Dරී ලංකාව") > 0
    assert ch.estimate_tokens("") == 0


def test_cli(capsys):
    assert cli_main(["slug", "ශ්\u200Dරී ලංකාව ලස්සන රටකි"]) == 0
    assert capsys.readouterr().out.strip() == "shri-lankawa-lassana-rataki"

    assert cli_main(["profanity", "ඔහු මෝඩයා", "--censor"]) == 0
    assert capsys.readouterr().out.strip() == "ඔහු ***"
