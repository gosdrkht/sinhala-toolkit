<?php

declare(strict_types=1);

/**
 * test_profanity.php
 * Run: php tests/test_profanity.php
 */

require_once __DIR__ . '/../php/src/ProfanityFilter.php';

use SinhalaToolkit\ProfanityFilter;

$pf   = new ProfanityFilter();
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
echo " ProfanityFilter Tests\n";
echo "========================================\n\n";

echo "Dataset loading:\n";
assert_eq("Loads profanity words", count($pf->getWords()) >= 40, true);

echo "\nDetection:\n";
assert_eq("Detects Sinhala profanity",         $pf->containsProfanity("ඔහු මෝඩයා"),           true);
assert_eq("Detects multi-word phrase",         $pf->containsProfanity("ඔහු බොරු කාරයා"),       true);
assert_eq("Detects Singlish slang",            $pf->containsProfanity("This is stupid!"),      true);
assert_eq("Clean Sinhala text returns false",  $pf->containsProfanity("ආයුබෝවන් ලංකාව"),       false);
assert_eq("Whole-word boundary (football)",    $pf->containsProfanity("I love football"),      false);
assert_eq("Detects ZWJ bypass attempt",        $pf->containsProfanity("ඔහු මෝ\u{200D}ඩයා"),    true);

echo "\nSeverity filtering:\n";
assert_eq("Highest severity moderate",         $pf->highestSeverity("මෝඩයා සහ වංචාකාරයා"),     "moderate");
assert_eq("Highest severity strong",           $pf->highestSeverity("හූකාරයා"),                "strong");
assert_eq("Highest severity null on clean",    $pf->highestSeverity("ආයුබෝවන්"),               null);
assert_eq("Filter by severity excludes mild",  $pf->containsProfanity("ඔහු මෝඩයා", ["strong"]), false);
assert_eq("Filter by severity includes mild",  $pf->containsProfanity("ඔහු මෝඩයා", ["mild"]),   true);

echo "\nCensoring:\n";
assert_eq("Censors Sinhala word",              $pf->censor("ඔහු මෝඩයා"),                        "ඔහු ***");
assert_eq("Censors multi-word phrase",         $pf->censor("ඔහු බොරු කාරයා වේ"),               "ඔහු *** වේ");
assert_eq("Censors with custom mask",          $pf->censor("That is stupid", "[redacted]"),     "That is [redacted]");
assert_eq("Censors ZWJ bypass",                $pf->censor("ඔහු මෝ\u{200D}ඩයා"),               "ඔහු ***");

echo "\nCustom words:\n";
$pf->addWords(["කුජීත"], "moderate");
assert_eq("Custom added word detected",        $pf->containsProfanity("මෙය කුජීත"),             true);
$pf->removeWords(["කුජීත"]);
assert_eq("Removed word no longer detected",   $pf->containsProfanity("මෙය කුජීත"),             false);

echo "\n========================================\n";
echo " Results: {$pass} passed, {$fail} failed\n";
echo "========================================\n\n";

exit($fail > 0 ? 1 : 0);
