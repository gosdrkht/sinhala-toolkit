<?php

/**
 * Tokenizer.php
 *
 * Sinhala Text Tokenizer — part of sinhala-toolkit
 * Splits Sinhala text into sentences, words, and grapheme clusters.
 *
 * Handles:
 *  - Sinhala danda (।) and double danda (॥) as sentence boundaries
 *  - ZWJ conjunct consonants kept intact as single tokens
 *  - Mixed Sinhala / English / number text
 *  - Punctuation-aware word splitting
 *
 * @package  SinhalaToolkit
 * @author   Your Name
 * @license  MIT
 */

namespace SinhalaToolkit;

class Tokenizer
{
    const ZWJ          = "\u{200D}";
    const DANDA        = "\u{0964}";
    const DOUBLE_DANDA = "\u{0965}";

    const TYPE_SINHALA     = 'sinhala';
    const TYPE_ENGLISH     = 'english';
    const TYPE_NUMBER      = 'number';
    const TYPE_PUNCTUATION = 'punctuation';
    const TYPE_MIXED       = 'mixed';
    const TYPE_UNKNOWN     = 'unknown';

    // ----------------------------------------------------------------
    // Sentence Tokenization
    // ----------------------------------------------------------------

    public function splitSentences(string $text, bool $keepBoundary = false): array
    {
        if (trim($text) === '') return [];

        $text = preg_replace('/\r\n|\r/', "\n", $text);

        // Danda and double danda — always sentence end
        $text = preg_replace('/([' . self::DANDA . self::DOUBLE_DANDA . '])\s*/u', "$1\x00", $text);

        // English full stop — sentence end if followed by space + capital/Sinhala
        $text = preg_replace('/(\.)(\s+)(?=[A-Z\x{0D80}-\x{0DFF}])/u', "$1\x00", $text);

        // Question and exclamation
        $text = preg_replace('/([?!])\s*/u', "$1\x00", $text);

        // Newlines as soft breaks
        $text = preg_replace('/\n+/', "\x00", $text);

        $parts     = explode("\x00", $text);
        $sentences = [];

        foreach ($parts as $part) {
            $part = trim($part);
            if ($part === '') continue;

            if (!$keepBoundary) {
                $part = rtrim($part, self::DANDA . self::DOUBLE_DANDA . '.?!');
                $part = trim($part);
            }

            if ($part !== '') $sentences[] = $part;
        }

        return $sentences;
    }

    // ----------------------------------------------------------------
    // Word Tokenization
    // ----------------------------------------------------------------

    public function tokenize(string $text, bool $lowercase = false): array
    {
        if (trim($text) === '') return [];

        if ($lowercase) {
            $text = preg_replace_callback('/[A-Z]+/', fn($m) => strtolower($m[0]), $text);
        }

        $rawTokens = preg_split('/\s+/u', trim($text));
        if (!$rawTokens) return [];

        $tokens = [];
        foreach ($rawTokens as $raw) {
            $raw     = trim($raw);
            $cleaned = $this->stripSurroundingPunctuation($raw);
            if ($cleaned !== '') $tokens[] = $cleaned;
        }

        return $tokens;
    }

    public function tokenizeWithTypes(string $text, bool $lowercase = false): array
    {
        return array_map(fn($t) => [
            'token' => $t,
            'type'  => $this->classifyToken($t),
        ], $this->tokenize($text, $lowercase));
    }

    public function tokenizeByType(string $text, string $type): array
    {
        return array_values(array_map(
            fn($t) => $t['token'],
            array_filter(
                $this->tokenizeWithTypes($text),
                fn($t) => $t['type'] === $type
            )
        ));
    }

    // ----------------------------------------------------------------
    // Grapheme Cluster Tokenization
    // ----------------------------------------------------------------

    public function graphemes(string $text): array
    {
        if (trim($text) === '') return [];

        $clusters = [];
        $chars    = $this->splitToCodepoints($text);
        $len      = count($chars);
        $i        = 0;

        while ($i < $len) {
            $cluster = $chars[$i++];

            // Consume trailing diacritics/vowel signs
            while ($i < $len && $this->isDiacritic($chars[$i])) {
                $cluster .= $chars[$i++];
            }

            // Consume ZWJ + next consonant (conjunct)
            if ($i < $len && $chars[$i] === self::ZWJ) {
                $cluster .= $chars[$i++]; // ZWJ
                if ($i < $len) {
                    $cluster .= $chars[$i++]; // following consonant
                    while ($i < $len && $this->isDiacritic($chars[$i])) {
                        $cluster .= $chars[$i++];
                    }
                }
            }

            $clusters[] = $cluster;
        }

        return $clusters;
    }

    // ----------------------------------------------------------------
    // Utilities
    // ----------------------------------------------------------------

    public function classifyToken(string $token): string
    {
        $hasSinhala = (bool) preg_match('/[\x{0D80}-\x{0DFF}]/u', $token);
        $hasEnglish = (bool) preg_match('/[a-zA-Z]/', $token);
        $hasNumber  = (bool) preg_match('/[0-9\x{0DE6}-\x{0DEF}]/u', $token);
        $isPunct    = (bool) preg_match('/^[^\p{L}\p{N}]+$/u', $token);

        if ($isPunct)                                         return self::TYPE_PUNCTUATION;
        if ($hasSinhala && !$hasEnglish && !$hasNumber)      return self::TYPE_SINHALA;
        if ($hasEnglish && !$hasSinhala && !$hasNumber)      return self::TYPE_ENGLISH;
        if ($hasNumber  && !$hasSinhala && !$hasEnglish)     return self::TYPE_NUMBER;
        if ($hasSinhala || $hasEnglish || $hasNumber)        return self::TYPE_MIXED;

        return self::TYPE_UNKNOWN;
    }

    public function countTokens(string $text): int
    {
        return count($this->tokenize($text));
    }

    public function countSentences(string $text): int
    {
        return count($this->splitSentences($text));
    }

    public function frequency(string $text, array $stopwords = []): array
    {
        $tokens = $this->tokenize($text, lowercase: true);

        if (!empty($stopwords)) {
            $tokens = array_filter($tokens, fn($t) => !in_array($t, $stopwords, true));
        }

        $freq = array_count_values(array_values($tokens));
        arsort($freq);

        return $freq;
    }

    // ----------------------------------------------------------------
    // Private helpers
    // ----------------------------------------------------------------

    private function stripSurroundingPunctuation(string $token): string
    {
        // Keep Sinhala Unicode block (U+0D80-U+0DFF) so vowel signs are preserved
        $token = preg_replace('/^[^\p{L}\p{N}\x{200D}\x{0D80}-\x{0DFF}]+/u', '', $token) ?? '';
        $token = preg_replace('/[^\p{L}\p{N}\x{200D}\x{0D80}-\x{0DFF}]+$/u', '', $token) ?? '';
        return $token;
    }

    private function isDiacritic(string $char): bool
    {
        $cp = $this->codepoint($char);
        return (
            ($cp >= 0x0DCA && $cp <= 0x0DDF) ||
            ($cp >= 0x0DF2 && $cp <= 0x0DF4) ||
            $cp === 0x0D82 ||
            $cp === 0x0D83
        );
    }

    private function codepoint(string $char): int
    {
        // Convert UTF-8 char to Unicode codepoint without mb_convert_encoding
        $bytes = array_map('ord', str_split($char));
        $count = count($bytes);

        if ($count === 1) return $bytes[0];
        if ($count === 2) return (($bytes[0] & 0x1F) << 6)  | ($bytes[1] & 0x3F);
        if ($count === 3) return (($bytes[0] & 0x0F) << 12) | (($bytes[1] & 0x3F) << 6) | ($bytes[2] & 0x3F);
        if ($count === 4) return (($bytes[0] & 0x07) << 18) | (($bytes[1] & 0x3F) << 12) | (($bytes[2] & 0x3F) << 6) | ($bytes[3] & 0x3F);

        return 0;
    }

    private function splitToCodepoints(string $text): array
    {
        return preg_split('//u', $text, -1, PREG_SPLIT_NO_EMPTY) ?: [];
    }
}
