<?php

declare(strict_types=1);

/**
 * Stemmer.php
 *
 * Rule-based Sinhala Stemmer / Suffix Stripper — part of sinhala-toolkit
 * Reduces inflected Sinhala words to their base stem for search & indexing.
 *
 * @package  SinhalaToolkit
 * @author   gosdrkht
 * @license  MIT
 * @link     https://github.com/gosdrkht/sinhala-toolkit
 */

namespace SinhalaToolkit;

class Stemmer
{
    /**
     * Common Sinhala inflectional & case suffixes ordered longest-first.
     */
    private const SUFFIXES = [
        'වරුන්ගේ', 'වරුන්ට', 'වරුන්', 'වලින්', 'වලට', 'වලදී', 'වල',
        'යින්ගේ', 'යින්ට', 'යන්ගේ', 'යන්ට', 'ගෙන්', 'වලිනි',
        'යින්', 'යන්', 'යෙහි', 'යෙක්', 'යාගේ', 'යාට', 'වරු',
        'ගේ', 'ගෙ', 'ට', 'න්', 'යි', 'ත්', 'ද', 'ම', 'ක්', 'ක',
        'වේ', 'ව', 'ලා', 'හි', 'නි',
    ];

    private Tokenizer $tokenizer;
    private int $minStemGraphemes;

    /**
     * @param int $minStemGraphemes Minimum grapheme clusters preserved in a stem (default 2).
     */
    public function __construct(int $minStemGraphemes = 2)
    {
        $this->tokenizer        = new Tokenizer();
        $this->minStemGraphemes = max(1, $minStemGraphemes);
    }

    /**
     * Stem a single Sinhala word by stripping common suffixes.
     *
     * Example: "ගෙදරට" → "ගෙදර", "ගෙදරින්" → "ගෙදර", "ගෙදරයි" → "ගෙදර"
     *
     * @param  string $word
     * @return string
     */
    public function stem(string $word): string
    {
        $word = trim($word);
        if ($word === '' || !preg_match('/[\x{0D80}-\x{0DFF}]/u', $word)) {
            return $word;
        }

        // Special instrumental/ablative ending: consonant + ින් (e.g. ගෙදරින් → ගෙදර)
        if (str_ends_with($word, 'ින්')) {
            $candidate = mb_substr($word, 0, mb_strlen($word, 'UTF-8') - mb_strlen('ින්', 'UTF-8'), 'UTF-8');
            if ($this->graphemeCount($candidate) >= $this->minStemGraphemes) {
                return $candidate;
            }
        }

        foreach (self::SUFFIXES as $suffix) {
            if (str_ends_with($word, $suffix)) {
                $candidate = mb_substr(
                    $word,
                    0,
                    mb_strlen($word, 'UTF-8') - mb_strlen($suffix, 'UTF-8'),
                    'UTF-8'
                );
                if ($this->graphemeCount($candidate) >= $this->minStemGraphemes) {
                    return $candidate;
                }
            }
        }

        return $word;
    }

    /**
     * Stem an array of tokens.
     *
     * @param  array<string> $tokens
     * @return array<string>
     */
    public function stemTokens(array $tokens): array
    {
        return array_map(fn(string $t): string => $this->stem($t), $tokens);
    }

    /**
     * Stem every word in a text string and return rejoined text.
     *
     * @param  string $text
     * @return string
     */
    public function stemText(string $text): string
    {
        $tokens = $this->tokenizer->tokenize($text);
        return implode(' ', $this->stemTokens($tokens));
    }

    private function graphemeCount(string $text): int
    {
        return count($this->tokenizer->graphemes($text));
    }
}
