<?php

declare(strict_types=1);

/**
 * test_sentiment.php
 * Run: php tests/test_sentiment.php
 */

require_once __DIR__ . '/../php/src/Tokenizer.php';
require_once __DIR__ . '/../php/src/SentimentAnalyser.php';

use SinhalaToolkit\SentimentAnalyser;

$sa   = new SentimentAnalyser();
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
echo " SentimentAnalyser Tests\n";
echo "========================================\n\n";

echo "Core sentiment:\n";
$pos = $sa->analyse("මෙය ඉතා හොඳ චිත්‍රපටයකි");
assert_eq("Positive text label",       $pos['label'],          "positive");
assert_eq("isPositive helper",         $sa->isPositive("ශ්‍රී ලංකාව ලස්සන රටකි"), true);

$neg = $sa->analyse("මෙය ඉතා නරක අත්දැකීමකි");
assert_eq("Negative text label",       $neg['label'],          "negative");
assert_eq("isNegative helper",         $sa->isNegative("මෙය නරකයි"), true);

$neu = $sa->analyse("ඔහු ගෙදර ගියා");
assert_eq("Neutral text label",        $neu['label'],          "neutral");
assert_eq("Neutral score is 0.5",      $neu['score'],          0.5);

echo "\nSinhala negation:\n";
assert_eq("Post-negation flips positive to negative", $sa->analyse("මෙය හොඳ නෑ")['label'],  "negative");
assert_eq("Post-negation flips negative to positive", $sa->analyse("මෙය නරක නෑ")['label'],  "positive");

echo "\nBatch & custom lexicon:\n";
$batch = $sa->batchAnalyse(["හොඳයි", "නරකයි"]);
assert_eq("Batch count",               count($batch),          2);
assert_eq("Batch item 0 positive",     $batch[0]['label'],     "positive");
assert_eq("Batch item 1 negative",     $batch[1]['label'],     "negative");

$sa->addPositiveWords(["සුපිරි"]);
assert_eq("Custom positive word",      $sa->isPositive("මෙය සුපිරි"), true);

echo "\n========================================\n";
echo " Results: {$pass} passed, {$fail} failed\n";
echo "========================================\n\n";

exit($fail > 0 ? 1 : 0);
