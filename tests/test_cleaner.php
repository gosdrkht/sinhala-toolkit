<?php

declare(strict_types=1);

/**
 * test_cleaner.php
 * Run: php tests/test_cleaner.php
 */

require_once __DIR__ . '/../php/src/TextCleaner.php';

use SinhalaToolkit\TextCleaner;

$cleaner = new TextCleaner(__DIR__ . '/../data/stopwords.json');
$pass    = 0;
$fail    = 0;

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
echo " TextCleaner Tests\n";
echo "========================================\n\n";

// --- Whitespace normalisation ---
echo "Whitespace normalisation:\n";
assert_eq(
    "Collapses multiple spaces",
    $cleaner->normaliseWhitespace("  මම   ඔබ   "),
    "මම ඔබ"
);
assert_eq(
    "Trims leading and trailing",
    $cleaner->normaliseWhitespace("   ගෙදර   "),
    "ගෙදර"
);

// --- Stopword removal ---
echo "\nStopword removal:\n";
assert_eq(
    "Removes known stopwords",
    $cleaner->clean("මම සහ ඔබ හොඳ ගුරුවරයා ළඟ ඉගෙන ගත්තා", ['remove_stopwords' => true]),
    "හොඳ ගුරුවරයා ඉගෙන ගත්තා"
);

// --- English removal ---
echo "\nEnglish removal:\n";
assert_eq(
    "Removes ASCII letters",
    $cleaner->clean("මෙය good idea එකක්", ['remove_english' => true]),
    "මෙය එකක්"
);

// --- Number removal ---
echo "\nNumber removal:\n";
assert_eq(
    "Removes ASCII digits",
    $cleaner->clean("2024 දී ජය", ['remove_numbers' => true]),
    "දී ජය"
);

// --- Script detection ---
echo "\nScript detection:\n";
assert_eq("Pure Sinhala",  $cleaner->detectScript("ආයුබෝවන්"),        "sinhala");
assert_eq("Pure English",  $cleaner->detectScript("Hello World"),     "english");
assert_eq("Mixed",         $cleaner->detectScript("Hello ආයුබෝවන්"), "mixed");
assert_eq("Unknown",       $cleaner->detectScript("12345"),            "unknown");

// --- isPureSinhala ---
echo "\nisPureSinhala:\n";
assert_eq("Pure Sinhala word",  $cleaner->isPureSinhala("ආයුබෝවන්"),      true);
assert_eq("English word",       $cleaner->isPureSinhala("Hello"),           false);
assert_eq("Mixed text",         $cleaner->isPureSinhala("Hello ආයුබෝවන්"), false);

// --- isStopword ---
echo "\nisStopword:\n";
assert_eq("'මම' is stopword",  $cleaner->isStopword("මම"),   true);
assert_eq("'ගුරු' not stopword", $cleaner->isStopword("ගුරු"), false);
assert_eq("'සඳහා' is stopword", $cleaner->isStopword("සඳහා"), true);

// --- Stopwords loaded ---
echo "\nStopwords dataset:\n";
assert_eq("At least 100 stopwords loaded", count($cleaner->getStopwords()) >= 100, true);

echo "\n========================================\n";
echo " Results: {$pass} passed, {$fail} failed\n";
echo "========================================\n\n";

exit($fail > 0 ? 1 : 0);
