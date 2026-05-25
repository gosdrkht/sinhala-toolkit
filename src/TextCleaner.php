<?php

/**
 * TextCleaner.php
 * 
 * Sinhala Text Cleaner — part of sinhala-toolkit
 * Cleans, normalises, and filters Sinhala Unicode text.
 * 
 * @package  SinhalaToolkit
 * @author   Your Name
 * @license  MIT
 * @link     https://github.com/YOUR_USERNAME/sinhala-toolkit
 */

namespace SinhalaToolkit;

class TextCleaner
{
    /**
     * Path to the stopwords JSON file.
     * @var string
     */
    private string $stopwordsPath;

    /**
     * Loaded flat list of stopwords.
     * @var array
     */
    private array $stopwords = [];

    /**
     * Unicode Zero Width Joiner — used in Sinhala rendering (e.g. ක්‍ර)
     * Must be preserved in some cases, stripped in others.
     */
    const ZWJ = "\u{200D}";

    /**
     * Unicode Zero Width Non-Joiner
     */
    const ZWNJ = "\u{200C}";

    /**
     * Sinhala Unicode block range: U+0D80 to U+0DFF
     */
    const SINHALA_BLOCK_START = 0x0D80;
    const SINHALA_BLOCK_END   = 0x0DFF;

    // -------------------------------------------------------------------------
    // Constructor
    // -------------------------------------------------------------------------

    /**
     * @param string|null $stopwordsPath  Full path to stopwords.json.
     *                                    Defaults to ../data/stopwords.json
     *                                    relative to this file.
     */
    public function __construct(?string $stopwordsPath = null)
    {
        $this->stopwordsPath = $stopwordsPath
            ?? __DIR__ . '/../data/stopwords.json';

        $this->loadStopwords();
    }

    // -------------------------------------------------------------------------
    // Public API
    // -------------------------------------------------------------------------

    /**
     * Full clean pipeline — runs all steps in recommended order.
     *
     * Steps:
     *   1. Normalise Unicode (NFC)
     *   2. Remove invisible/control characters (keep ZWJ where needed)
     *   3. Normalise whitespace
     *   4. Remove non-Sinhala noise (optional — keep punctuation by default)
     *   5. Remove stopwords (optional)
     *
     * @param  string $text             Raw Sinhala text input.
     * @param  array  $options {
     *     @type bool $remove_stopwords   Remove stopwords from text. Default false.
     *     @type bool $remove_punctuation Remove punctuation marks.    Default false.
     *     @type bool $remove_english     Remove English characters.   Default false.
     *     @type bool $remove_numbers     Remove digit characters.     Default false.
     *     @type bool $keep_zwj           Preserve ZWJ characters.     Default true.
     * }
     * @return string Cleaned text.
     */
    public function clean(string $text, array $options = []): string
    {
        $opts = array_merge([
            'remove_stopwords'   => false,
            'remove_punctuation' => false,
            'remove_english'     => false,
            'remove_numbers'     => false,
            'keep_zwj'           => true,
        ], $options);

        $text = $this->normaliseUnicode($text);
        $text = $this->removeInvisibleChars($text, $opts['keep_zwj']);
        $text = $this->normaliseWhitespace($text);

        if ($opts['remove_punctuation']) {
            $text = $this->removePunctuation($text);
        }

        if ($opts['remove_english']) {
            $text = $this->removeEnglish($text);
        }

        if ($opts['remove_numbers']) {
            $text = $this->removeNumbers($text);
        }

        if ($opts['remove_stopwords']) {
            $text = $this->removeStopwords($text);
        }

        return trim($text);
    }

    /**
     * Normalise Unicode to NFC form.
     * Sinhala text from different sources may use different compositions.
     * NFC ensures consistent character representation.
     *
     * @param  string $text
     * @return string
     */
    public function normaliseUnicode(string $text): string
    {
        if (!class_exists('Normalizer')) {
            // intl extension not available — return as-is
            return $text;
        }

        return \Normalizer::normalize($text, \Normalizer::FORM_C) ?: $text;
    }

    /**
     * Remove invisible and control characters from text.
     * 
     * By default, ZWJ (U+200D) is preserved because Sinhala uses it for
     * conjunct consonants (e.g. ක් + ZWJ + ර = ක්‍ර).
     * Set $keepZwj = false if you need bare token comparison.
     *
     * Characters removed:
     *  - U+200C  ZWNJ (Zero Width Non-Joiner)
     *  - U+200B  Zero Width Space
     *  - U+FEFF  BOM / Zero Width No-Break Space
     *  - U+00AD  Soft Hyphen
     *  - U+200E/F Left/Right-to-Right Mark
     *  - All C0/C1 control characters except \t \n \r
     *
     * @param  string $text
     * @param  bool   $keepZwj  Whether to preserve ZWJ. Default true.
     * @return string
     */
    public function removeInvisibleChars(string $text, bool $keepZwj = true): string
    {
        // Remove ZWNJ, zero-width space, BOM, soft hyphen, directional marks
        $text = preg_replace('/[\x{200B}\x{200C}\x{FEFF}\x{00AD}\x{200E}\x{200F}]/u', '', $text);

        // Optionally remove ZWJ
        if (!$keepZwj) {
            $text = str_replace(self::ZWJ, '', $text);
        }

        // Remove C0 control characters (except tab, newline, carriage return)
        $text = preg_replace('/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/u', '', $text);

        return $text;
    }

    /**
     * Collapse multiple spaces/newlines into single spaces.
     * Also trims leading/trailing whitespace.
     *
     * @param  string $text
     * @return string
     */
    public function normaliseWhitespace(string $text): string
    {
        // Replace all whitespace variants (including nbsp, ideographic space) with regular space
        $text = preg_replace('/[\s\x{00A0}\x{3000}]+/u', ' ', $text);
        return trim($text);
    }

    /**
     * Remove punctuation marks from text.
     * Keeps Sinhala-specific punctuation like '|' (dandas) by default.
     *
     * @param  string $text
     * @param  bool   $keepDanda  Keep Sinhala danda (।) and double danda (॥). Default true.
     * @return string
     */
    public function removePunctuation(string $text, bool $keepDanda = true): string
    {
        if ($keepDanda) {
            // Remove all punctuation except Sinhala dandas
            $text = preg_replace('/[^\p{L}\p{N}\s\x{0964}\x{0965}]/u', ' ', $text);
        } else {
            $text = preg_replace('/[^\p{L}\p{N}\s]/u', ' ', $text);
        }

        return $this->normaliseWhitespace($text);
    }

    /**
     * Remove ASCII English letters from text.
     * Useful when processing pure Sinhala content.
     *
     * @param  string $text
     * @return string
     */
    public function removeEnglish(string $text): string
    {
        $text = preg_replace('/[a-zA-Z]+/u', ' ', $text);
        return $this->normaliseWhitespace($text);
    }

    /**
     * Remove digit characters (both ASCII and Sinhala numerals).
     *
     * @param  string $text
     * @return string
     */
    public function removeNumbers(string $text): string
    {
        // ASCII digits + Sinhala digits (U+0DE6–U+0DEF)
        $text = preg_replace('/[0-9\x{0DE6}-\x{0DEF}]/u', ' ', $text);
        return $this->normaliseWhitespace($text);
    }

    /**
     * Remove stopwords from text.
     * Splits text into tokens, filters stopwords, rejoins.
     *
     * @param  string $text
     * @return string
     */
    public function removeStopwords(string $text): string
    {
        $tokens = $this->tokenize($text);

        $filtered = array_filter($tokens, function (string $token): bool {
            return !in_array($token, $this->stopwords, true);
        });

        return implode(' ', $filtered);
    }

    /**
     * Simple whitespace tokenizer.
     * Splits text on spaces and returns non-empty tokens.
     *
     * Note: For advanced tokenization (morpheme-aware), use the Tokenizer class.
     *
     * @param  string $text
     * @return array<string>
     */
    public function tokenize(string $text): array
    {
        return array_values(
            array_filter(
                explode(' ', $this->normaliseWhitespace($text)),
                fn(string $t) => $t !== ''
            )
        );
    }

    /**
     * Check whether a given string contains Sinhala characters.
     *
     * @param  string $text
     * @return bool
     */
    public function containsSinhala(string $text): bool
    {
        return (bool) preg_match('/[\x{0D80}-\x{0DFF}]/u', $text);
    }

    /**
     * Check whether a string is purely Sinhala (no English, digits, etc.)
     *
     * @param  string $text
     * @return bool
     */
    public function isPureSinhala(string $text): bool
    {
        // Allow Sinhala block + whitespace + ZWJ + dandas only
        return (bool) preg_match(
            '/^[\x{0D80}-\x{0DFF}\x{200D}\s\x{0964}\x{0965}]+$/u',
            trim($text)
        );
    }

    /**
     * Detect the primary script in a mixed-language string.
     * Returns 'sinhala', 'english', 'mixed', or 'unknown'.
     *
     * @param  string $text
     * @return string
     */
    public function detectScript(string $text): string
    {
        $hasSinhala = $this->containsSinhala($text);
        $hasEnglish = (bool) preg_match('/[a-zA-Z]/', $text);

        if ($hasSinhala && $hasEnglish) return 'mixed';
        if ($hasSinhala) return 'sinhala';
        if ($hasEnglish) return 'english';
        return 'unknown';
    }

    /**
     * Return the loaded stopwords list.
     *
     * @return array<string>
     */
    public function getStopwords(): array
    {
        return $this->stopwords;
    }

    /**
     * Check if a single word is a stopword.
     *
     * @param  string $word
     * @return bool
     */
    public function isStopword(string $word): bool
    {
        return in_array(trim($word), $this->stopwords, true);
    }

    // -------------------------------------------------------------------------
    // Private helpers
    // -------------------------------------------------------------------------

    /**
     * Load stopwords from the JSON file into $this->stopwords.
     * Silently skips if file not found (allows use without data file).
     */
    private function loadStopwords(): void
    {
        if (!file_exists($this->stopwordsPath)) {
            return;
        }

        $json = file_get_contents($this->stopwordsPath);
        if ($json === false) return;

        $data = json_decode($json, true);
        if (json_last_error() !== JSON_ERROR_NONE) return;

        $this->stopwords = $data['flat_list'] ?? [];
    }
}
