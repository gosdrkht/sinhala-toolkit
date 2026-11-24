<?php

declare(strict_types=1);

/**
 * Chunker.php
 *
 * Sinhala-aware LLM / RAG Text Chunker — part of sinhala-toolkit
 * Splits long Sinhala documents into chunks without breaking mid-sentence,
 * mid-word, mid-vowel-sign, or mid-ZWJ-conjunct.
 *
 * @package  SinhalaToolkit
 * @author   gosdrkht
 * @license  MIT
 * @link     https://github.com/gosdrkht/sinhala-toolkit
 */

namespace SinhalaToolkit;

class Chunker
{
    private Tokenizer $tokenizer;

    public function __construct()
    {
        $this->tokenizer = new Tokenizer();
    }

    /**
     * Split text into chunks of at most $maxChars characters (measured in Unicode codepoints),
     * preserving sentence boundaries, word boundaries, and Sinhala grapheme clusters / ZWJ conjuncts.
     *
     * @param  string $text
     * @param  int    $maxChars Maximum characters per chunk (default 500).
     * @param  int    $overlap  Optional overlap characters carried from previous chunk (default 0).
     * @return array<int, string>
     */
    public function chunk(string $text, int $maxChars = 500, int $overlap = 0): array
    {
        $text = trim($text);
        if ($text === '' || $maxChars <= 0) {
            return [];
        }

        $overlap = max(0, min($overlap, $maxChars - 1));
        $sentences = $this->tokenizer->splitSentences($text, keepBoundary: true);
        if (empty($sentences)) {
            $sentences = [$text];
        }

        // Break any oversized sentence into word/grapheme pieces first
        $units = [];
        foreach ($sentences as $sentence) {
            if (mb_strlen($sentence, 'UTF-8') <= $maxChars) {
                $units[] = $sentence;
            } else {
                foreach ($this->splitOversized($sentence, $maxChars) as $piece) {
                    $units[] = $piece;
                }
            }
        }

        $chunks  = [];
        $current = '';

        foreach ($units as $unit) {
            if ($current === '') {
                $current = $unit;
                continue;
            }

            $candidate = $current . ' ' . $unit;
            if (mb_strlen($candidate, 'UTF-8') <= $maxChars) {
                $current = $candidate;
            } else {
                $chunks[] = $current;
                if ($overlap > 0) {
                    $tail    = $this->graphemeTail($current, $overlap);
                    $current = (mb_strlen($tail . ' ' . $unit, 'UTF-8') <= $maxChars)
                        ? trim($tail . ' ' . $unit)
                        : $unit;
                } else {
                    $current = $unit;
                }
            }
        }

        if ($current !== '') {
            $chunks[] = $current;
        }

        return $chunks;
    }

    /**
     * Estimate LLM token count for Sinhala, English, or mixed text.
     * Sinhala Unicode characters typically consume ~1.5 BPE tokens each on modern LLMs,
     * while ASCII English averages ~0.25 tokens per character.
     *
     * @param  string $text
     * @return int
     */
    public function estimateTokens(string $text): int
    {
        if (trim($text) === '') {
            return 0;
        }

        $sinhalaCount = preg_match_all('/[\x{0D80}-\x{0DFF}]/u', $text);
        $totalChars   = mb_strlen($text, 'UTF-8');
        $otherCount   = max(0, $totalChars - (int) $sinhalaCount);

        return max(1, (int) ceil(((int) $sinhalaCount * 1.5) + ($otherCount * 0.25)));
    }

    /**
     * @return array<int, string>
     */
    private function splitOversized(string $text, int $maxChars): array
    {
        $words  = preg_split('/\s+/u', trim($text)) ?: [];
        $pieces = [];
        $buf    = '';

        foreach ($words as $word) {
            if (mb_strlen($word, 'UTF-8') > $maxChars) {
                if ($buf !== '') {
                    $pieces[] = $buf;
                    $buf      = '';
                }
                foreach ($this->splitByGraphemes($word, $maxChars) as $gPiece) {
                    $pieces[] = $gPiece;
                }
                continue;
            }

            if ($buf === '') {
                $buf = $word;
            } elseif (mb_strlen($buf . ' ' . $word, 'UTF-8') <= $maxChars) {
                $buf .= ' ' . $word;
            } else {
                $pieces[] = $buf;
                $buf      = $word;
            }
        }

        if ($buf !== '') {
            $pieces[] = $buf;
        }

        return $pieces;
    }

    /**
     * @return array<int, string>
     */
    private function splitByGraphemes(string $word, int $maxChars): array
    {
        $graphemes = $this->tokenizer->graphemes($word);
        $pieces    = [];
        $buf       = '';

        foreach ($graphemes as $g) {
            if ($buf !== '' && mb_strlen($buf . $g, 'UTF-8') > $maxChars) {
                $pieces[] = $buf;
                $buf      = $g;
            } else {
                $buf .= $g;
            }
        }

        if ($buf !== '') {
            $pieces[] = $buf;
        }

        return $pieces;
    }

    private function graphemeTail(string $text, int $targetChars): string
    {
        $graphemes = $this->tokenizer->graphemes($text);
        $tail      = '';
        for ($i = count($graphemes) - 1; $i >= 0; $i--) {
            $candidate = $graphemes[$i] . $tail;
            if (mb_strlen($candidate, 'UTF-8') > $targetChars && $tail !== '') {
                break;
            }
            $tail = $candidate;
        }
        return trim($tail);
    }
}
