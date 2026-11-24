<?php

declare(strict_types=1);

/**
 * test_nlp_features.php
 * Tests for Transliterator, Stemmer, KeywordExtractor, Normalizer, and Chunker.
 * Run: php tests/test_nlp_features.php
 */

require_once __DIR__ . '/../php/src/TextCleaner.php';
require_once __DIR__ . '/../php/src/Tokenizer.php';
require_once __DIR__ . '/../php/src/Transliterator.php';
require_once __DIR__ . '/../php/src/Stemmer.php';
require_once __DIR__ . '/../php/src/KeywordExtractor.php';
require_once __DIR__ . '/../php/src/Normalizer.php';
require_once __DIR__ . '/../php/src/Chunker.php';

use SinhalaToolkit\Chunker;
use SinhalaToolkit\KeywordExtractor;
use SinhalaToolkit\Normalizer;
use SinhalaToolkit\Stemmer;
use SinhalaToolkit\Transliterator;

$pass = 0;
$fail = 0;

function assert_eq(string $label, mixed $got, mixed $expected): void {
    global $pass, $fail;
    if ($got === $expected) {
        echo "  ✅ $label\n";
        $pass++;
    } else {
        echo "  ❌ $label\n";
        echo "     Expected : " . json_encode($expected, JSON_UNESCAPED_UNICODE) . "\n";
        echo "     Got      : " . json_encode($got,      JSON_UNESCAPED_UNICODE) . "\n";
        $fail++;
    }
}

echo "\n========================================\n";
echo " NLP Features Tests (v1.2.0)\n";
echo "========================================\n\n";

// --- Transliterator & Slugify ---
echo "Transliterator & slugify:\n";
$tr = new Transliterator();
assert_eq("Singlish -> Sinhala override", $tr->toSinhala("aayubowan lanka"), "ආයුබෝවන් ලංකා");
assert_eq("Singlish -> Sinhala phonetic", $tr->toSinhala("kama"), "කම");
assert_eq("Sinhala -> Singlish",          $tr->toSinglish("ශ්\u{200D}රී ලංකාව"), "shri lankawa");
assert_eq("Slugify Sinhala title",        $tr->slugify("ශ්\u{200D}රී ලංකාව ලස්සන රටකි"), "shri-lankawa-lassana-rataki");
assert_eq("Slugify mixed title",          $tr->slugify("ලංකා Cricket 2026!"), "lanka-cricket-2026");

// --- Stemmer ---
echo "\nStemmer:\n";
$st = new Stemmer();
assert_eq("Stems ගෙදරට -> ගෙදර",   $st->stem("ගෙදරට"),  "ගෙදර");
assert_eq("Stems ගෙදරින් -> ගෙදර",  $st->stem("ගෙදරින්"), "ගෙදර");
assert_eq("Stems ගෙදරයි -> ගෙදර",   $st->stem("ගෙදරයි"),  "ගෙදර");
assert_eq("Preserves short word මම", $st->stem("මම"),     "මම");

// --- KeywordExtractor & Summariser ---
echo "\nKeywordExtractor & Summariser:\n";
$ke  = new KeywordExtractor();
$kw  = $ke->extract("ශ්\u{200D}රී ලංකාව ලස්සන රටකි ශ්\u{200D}රී ලංකාව හොඳ රටකි", 2);
assert_eq("Top keyword #1", $kw[0]['keyword'] ?? '', "ශ්\u{200D}රී");
assert_eq("Top keyword #2", $kw[1]['keyword'] ?? '', "ලංකාව");

$doc = "ශ්\u{200D}රී ලංකාව ඉතා ලස්සන රටකි\u{0964} ශ්\u{200D}රී ලංකාව සංචාරකයන් අතර ජනප්‍රියයි\u{0964} අද වැස්ස වහිනවා\u{0964}";
$sum = $ke->summarize($doc, 2);
assert_eq("Summary keeps 2 sentences", count((new \SinhalaToolkit\Tokenizer())->splitSentences($sum)), 2);

// --- Normalizer ---
echo "\nNormalizer:\n";
$norm = new Normalizer();
assert_eq("Sinhala digits -> ASCII",  $norm->sinhalaDigitsToAscii("෨෦෨෪"), "2024");
assert_eq("ASCII digits -> Sinhala",  $norm->asciiDigitsToSinhala("2024"), "෨෦෨෪");

$curr1 = $norm->extractCurrency("මිල රු. 5,000 කි");
assert_eq("Extracts රු. 5,000",       $curr1[0]['amount'] ?? 0.0, 5000.0);

$curr2 = $norm->extractCurrency("වටිනාකම රු. ලක්ෂ 5 කි");
assert_eq("Extracts ලක්ෂ 5 -> 500000", $curr2[0]['amount'] ?? 0.0, 500000.0);

$dates = $norm->extractDates("උත්සවය 2026 නොවැම්බර් 24 පැවැත්වේ");
assert_eq("Extracts Sinhala date ISO", $dates[0]['iso'] ?? '', "2026-11-24");

assert_eq("Normalizes text currency",  $norm->normalizeText("මිල රු. ෫,෦෦෦"), "මිල LKR 5,000");

// --- Chunker ---
echo "\nChunker:\n";
$ch     = new Chunker();
$chunks = $ch->chunk("ඔහු ගෙදර ගියා\u{0964} ඇය පාසලට ගියාය\u{0964}", 20);
assert_eq("Chunks on sentence boundaries", $chunks, ["ඔහු ගෙදර ගියා\u{0964}", "ඇය පාසලට ගියාය\u{0964}"]);
assert_eq("Token estimation positive",     $ch->estimateTokens("ශ්\u{200D}රී ලංකාව") > 0, true);
assert_eq("Token estimation empty = 0",    $ch->estimateTokens(""), 0);

echo "\n========================================\n";
echo " Results: {$pass} passed, {$fail} failed\n";
echo "========================================\n\n";

exit($fail > 0 ? 1 : 0);
