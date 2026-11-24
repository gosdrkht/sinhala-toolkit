"""
cli.py — Command-line interface for sinkit (sinhala-toolkit)

Usage:
    sinkit clean "  මම සහ ඔබ ගෙදර ගියා  " --remove-stopwords
    sinkit tokenize "ශ්‍රී ලංකාව ලස්සන රටකි"
    sinkit sentiment "මෙය හොඳ නෑ"
    sinkit profanity "ඔහු මෝඩයා" --censor
    sinkit transliterate "aayubowan lanka"
    sinkit slug "ශ්‍රී ලංකාව ලස්සන රටකි"
    sinkit stem "ගෙදරට ගෙදරින්"
    sinkit keywords "ශ්‍රී ලංකාව ලස්සන රටකි"
    sinkit normalize "මිල රු. ෫,෦෦෦"
    sinkit chunk "ඔහු ගෙදර ගියා। ඇය පාසලට ගියාය।" --max-chars 20
"""

from __future__ import annotations

import argparse
import json
import sys

from . import (
    Chunker,
    KeywordExtractor,
    Normalizer,
    ProfanityFilter,
    SentimentAnalyser,
    Stemmer,
    TextCleaner,
    Tokenizer,
    Transliterator,
    __version__,
)


def _read_text(args_text: str | None) -> str:
    if args_text is not None:
        return args_text
    if not sys.stdin.isatty():
        return sys.stdin.read()
    return ""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="sinkit",
        description="sinhala-toolkit CLI — zero-dependency Sinhala NLP tools",
    )
    parser.add_argument("--version", action="version", version=f"sinkit {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p_clean = sub.add_parser("clean", help="Clean and normalise Sinhala text")
    p_clean.add_argument("text", nargs="?")
    p_clean.add_argument("--remove-stopwords", action="store_true")
    p_clean.add_argument("--remove-punctuation", action="store_true")
    p_clean.add_argument("--remove-english", action="store_true")
    p_clean.add_argument("--remove-numbers", action="store_true")

    p_tok = sub.add_parser("tokenize", help="Tokenize Sinhala text")
    p_tok.add_argument("text", nargs="?")
    p_tok.add_argument("--sentences", action="store_true")
    p_tok.add_argument("--graphemes", action="store_true")

    p_sent = sub.add_parser("sentiment", help="Analyse Sinhala sentiment")
    p_sent.add_argument("text", nargs="?")

    p_prof = sub.add_parser("profanity", help="Check or censor profanity")
    p_prof.add_argument("text", nargs="?")
    p_prof.add_argument("--censor", action="store_true")

    p_tr = sub.add_parser("transliterate", help="Transliterate Singlish <-> Sinhala")
    p_tr.add_argument("text", nargs="?")
    p_tr.add_argument("--to-singlish", action="store_true")

    p_slug = sub.add_parser("slug", help="Generate SEO URL slug from Sinhala text")
    p_slug.add_argument("text", nargs="?")

    p_stem = sub.add_parser("stem", help="Stem Sinhala words")
    p_stem.add_argument("text", nargs="?")

    p_kw = sub.add_parser("keywords", help="Extract top keywords")
    p_kw.add_argument("text", nargs="?")
    p_kw.add_argument("--top-k", type=int, default=5)
    p_kw.add_argument("--stem", action="store_true")

    p_sum = sub.add_parser("summarize", help="Extractive summary of Sinhala text")
    p_sum.add_argument("text", nargs="?")
    p_sum.add_argument("--sentences", type=int, default=2)

    p_norm = sub.add_parser("normalize", help="Normalise Sinhala digits and currency")
    p_norm.add_argument("text", nargs="?")

    p_chunk = sub.add_parser("chunk", help="Split Sinhala text for LLM/RAG pipelines")
    p_chunk.add_argument("text", nargs="?")
    p_chunk.add_argument("--max-chars", type=int, default=500)
    p_chunk.add_argument("--overlap", type=int, default=0)

    args = parser.parse_args(argv)
    text = _read_text(args.text)

    if args.command == "clean":
        print(
            TextCleaner().clean(
                text,
                remove_stopwords=args.remove_stopwords,
                remove_punctuation=args.remove_punctuation,
                remove_english=args.remove_english,
                remove_numbers=args.remove_numbers,
            )
        )
    elif args.command == "tokenize":
        t = Tokenizer()
        if args.sentences:
            out = t.split_sentences(text)
        elif args.graphemes:
            out = t.graphemes(text)
        else:
            out = t.tokenize(text)
        print(json.dumps(out, ensure_ascii=False))
    elif args.command == "sentiment":
        print(json.dumps(SentimentAnalyser().analyse(text), ensure_ascii=False))
    elif args.command == "profanity":
        pf = ProfanityFilter()
        if args.censor:
            print(pf.censor(text))
        else:
            print(
                json.dumps(
                    {
                        "contains_profanity": pf.contains_profanity(text),
                        "highest_severity": pf.highest_severity(text),
                        "matches": pf.find_matches(text),
                    },
                    ensure_ascii=False,
                )
            )
    elif args.command == "transliterate":
        tr = Transliterator()
        print(tr.to_singlish(text) if args.to_singlish else tr.to_sinhala(text))
    elif args.command == "slug":
        print(Transliterator().slugify(text))
    elif args.command == "stem":
        print(Stemmer().stem_text(text))
    elif args.command == "keywords":
        print(
            json.dumps(
                KeywordExtractor().extract(text, top_k=args.top_k, use_stemming=args.stem),
                ensure_ascii=False,
            )
        )
    elif args.command == "summarize":
        print(KeywordExtractor().summarize(text, num_sentences=args.sentences))
    elif args.command == "normalize":
        print(Normalizer().normalize_text(text))
    elif args.command == "chunk":
        print(
            json.dumps(
                Chunker().chunk(text, max_chars=args.max_chars, overlap=args.overlap),
                ensure_ascii=False,
            )
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
