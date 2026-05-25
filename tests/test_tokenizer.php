<?php

declare(strict_types=1);

/**
 * test_tokenizer.php
 * Run: php tests/test_tokenizer.php
 */

require_once __DIR__ . '/../php/src/Tokenizer.php';

use SinhalaToolkit\Tokenizer;

$t    = new Tokenizer();
$pass = 0;
$fail = 0;

$DANDA = "\u{0964}";

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
echo " Tokenizer Tests\n";
echo "========================================\n\n";

// --- Sentence splitting ---
echo "Sentence splitting:\n";

$s1 = "ඔහු ගෙදර ගියා{$DANDA} ඇය පාසලට ගියාය{$DANDA}";
assert_eq(
    "Splits on danda",
    $t->splitSentences($s1),
    ["ඔහු ගෙදර ගියා", "ඇය පාසලට ගියාය"]
);

assert_eq(
    "Splits on question mark",
    $t->splitSentences("ඔබේ නම කුමක්ද? මගේ නම ත්‍රිෂාන්."),
    ["ඔබේ නම කුමක්ද", "මගේ නම ත්‍රිෂාන්"]
);

assert_eq(
    "Returns empty for empty string",
    $t->splitSentences(""),
    []
);

// --- Word tokenization ---
echo "\nWord tokenization:\n";

assert_eq(
    "Basic Sinhala tokenize",
    $t->tokenize("ශ්\u{200D}රී ලංකාව ලස්සන රටකි"),
    ["ශ්\u{200D}රී", "ලංකාව", "ලස්සන", "රටකි"]
);

assert_eq(
    "Mixed language tokenize",
    $t->tokenize("මෙය best project එකක් වේ"),
    ["මෙය", "best", "project", "එකක්", "වේ"]
);

assert_eq(
    "Returns empty for empty string",
    $t->tokenize(""),
    []
);

// --- Token type classification ---
echo "\nToken type classification:\n";

assert_eq("Sinhala word",    $t->classifyToken("ලංකාව"),   "sinhala");
assert_eq("English word",    $t->classifyToken("cricket"),  "english");
assert_eq("Number",          $t->classifyToken("2024"),     "number");
assert_eq("Punctuation",     $t->classifyToken(".,!"),      "punctuation");
assert_eq("Mixed token",     $t->classifyToken("v2ලංකා"),   "mixed");

// --- Tokenize by type ---
echo "\nTokenize by type:\n";

$mixed = "Ceylon Ledger මගින් ඔබේ business 2024 සිට manage කරන්න";
assert_eq(
    "Filter Sinhala only",
    $t->tokenizeByType($mixed, "sinhala"),
    ["මගින්", "ඔබේ", "සිට", "කරන්න"]
);
assert_eq(
    "Filter English only",
    $t->tokenizeByType($mixed, "english"),
    ["Ceylon", "Ledger", "business", "manage"]
);
assert_eq(
    "Filter numbers only",
    $t->tokenizeByType($mixed, "number"),
    ["2024"]
);

// --- Counts ---
echo "\nCounts:\n";

$countText = "ඔහු ගෙදර ගියා{$DANDA} ඇය පාසලට ගියාය{$DANDA}";
assert_eq("countSentences", $t->countSentences($countText), 2);
assert_eq("countTokens",    $t->countTokens($countText),    6);

// --- Frequency ---
echo "\nWord frequency:\n";

$freqText = "ශ්\u{200D}රී ලංකාව ලස්සන රටකි ශ්\u{200D}රී ලංකාව හොඳ රටකි ශ්\u{200D}රී ලංකාව";
$freq     = $t->frequency($freqText);
assert_eq("Top word 'ශ්‍රී' appears 3 times",  $freq["ශ්\u{200D}රී"] ?? 0, 3);
assert_eq("Word 'ලංකාව' appears 3 times", $freq["ලංකාව"] ?? 0,           3);
assert_eq("Word 'රටකි' appears 2 times",  $freq["රටකි"] ?? 0,            2);

echo "\n========================================\n";
echo " Results: {$pass} passed, {$fail} failed\n";
echo "========================================\n\n";

exit($fail > 0 ? 1 : 0);
