<?php

declare(strict_types=1);

/**
 * ProfanityFilter.php
 *
 * Sinhala Profanity / Bad-Word Filter — part of sinhala-toolkit
 * Detects and censors offensive Sinhala and Singlish words/phrases
 * with severity classification.
 *
 * @package  SinhalaToolkit
 * @author   gosdrkht
 * @license  MIT
 * @link     https://github.com/gosdrkht/sinhala-toolkit
 */

namespace SinhalaToolkit;

class ProfanityFilter
{
    /**
     * Severity ranking from lowest to highest.
     */
    private const SEVERITY_RANK = [
        'mild'           => 1,
        'singlish_slang' => 2,
        'moderate'       => 3,
        'strong'         => 4,
        'hate_speech'    => 5,
    ];

    /**
     * Path to profanity.json.
     */
    private string $profanityPath;

    /**
     * Map of lowercased word/phrase => severity level.
     *
     * @var array<string, string>
     */
    private array $wordSeverities = [];

    /**
     * @param string|null $profanityPath  Full path to profanity.json.
     *                                    Defaults to ../../data/profanity.json.
     */
    public function __construct(?string $profanityPath = null)
    {
        $this->profanityPath = $profanityPath
            ?? __DIR__ . '/../../data/profanity.json';

        $this->loadDataset();
    }

    /**
     * Check whether text contains any profanity (optionally filtered by severities).
     *
     * @param  string             $text
     * @param  array<string>|null $severities  Optional list of severity levels to check.
     * @return bool
     */
    public function containsProfanity(string $text, ?array $severities = null): bool
    {
        return count($this->findMatches($text, $severities)) > 0;
    }

    /**
     * Find all profanity matches in text with their severity levels.
     *
     * @param  string             $text
     * @param  array<string>|null $severities  Optional list of severity levels to include.
     * @return array<int, array{word: string, severity: string}>
     */
    public function findMatches(string $text, ?array $severities = null): array
    {
        $normalised = $this->normaliseForMatching($text);
        if ($normalised === '') {
            return [];
        }

        $candidates = $this->getFilteredWords($severities);
        if (empty($candidates)) {
            return [];
        }

        $matches = [];
        $seen    = [];

        foreach ($candidates as $word => $severity) {
            $pattern = $this->buildWordPattern($word);
            if (preg_match($pattern, $normalised)) {
                if (!isset($seen[$word])) {
                    $seen[$word] = true;
                    $matches[]   = [
                        'word'     => $word,
                        'severity' => $severity,
                    ];
                }
            }
        }

        return $matches;
    }

    /**
     * Censor profanity in text by replacing matched words/phrases.
     *
     * @param  string             $text
     * @param  string             $replacement Replacement string (default '***').
     * @param  array<string>|null $severities  Optional list of severity levels to censor.
     * @return string
     */
    public function censor(string $text, string $replacement = '***', ?array $severities = null): string
    {
        if (trim($text) === '') {
            return $text;
        }

        $candidates = $this->getFilteredWords($severities);
        if (empty($candidates)) {
            return $text;
        }

        $result = $text;
        foreach (array_keys($candidates) as $word) {
            $pattern = $this->buildWordPattern($word, allowZwjBetweenChars: true);
            $result  = preg_replace($pattern, $replacement, $result) ?? $result;
        }

        return $result;
    }

    /**
     * Return the highest severity level found in the text, or null if clean.
     *
     * @param  string $text
     * @return string|null
     */
    public function highestSeverity(string $text): ?string
    {
        $matches = $this->findMatches($text);
        if (empty($matches)) {
            return null;
        }

        $best     = null;
        $bestRank = 0;

        foreach ($matches as $match) {
            $sev  = $match['severity'];
            $rank = self::SEVERITY_RANK[$sev] ?? 1;
            if ($rank > $bestRank) {
                $bestRank = $rank;
                $best     = $sev;
            }
        }

        return $best;
    }

    /**
     * Add custom words/phrases at runtime.
     *
     * @param  array<string> $words
     * @param  string        $severity
     * @return self
     */
    public function addWords(array $words, string $severity = 'moderate'): self
    {
        foreach ($words as $word) {
            $w = $this->normaliseKey($word);
            if ($w !== '') {
                $this->wordSeverities[$w] = $severity;
            }
        }

        return $this;
    }

    /**
     * Remove words/phrases from the active filter at runtime.
     *
     * @param  array<string> $words
     * @return self
     */
    public function removeWords(array $words): self
    {
        foreach ($words as $word) {
            $w = $this->normaliseKey($word);
            unset($this->wordSeverities[$w]);
        }

        return $this;
    }

    /**
     * Return loaded words (optionally filtered by severity).
     *
     * @param  string|null $severity
     * @return array<string>
     */
    public function getWords(?string $severity = null): array
    {
        if ($severity === null) {
            return array_keys($this->wordSeverities);
        }

        $filtered = [];
        foreach ($this->wordSeverities as $word => $sev) {
            if ($sev === $severity) {
                $filtered[] = $word;
            }
        }

        return $filtered;
    }

    // -------------------------------------------------------------------------
    // Private helpers
    // -------------------------------------------------------------------------

    private function loadDataset(): void
    {
        if (!file_exists($this->profanityPath)) {
            return;
        }

        $json = file_get_contents($this->profanityPath);
        if ($json === false) {
            return;
        }

        $data = json_decode($json, true);
        if (json_last_error() !== JSON_ERROR_NONE || !is_array($data)) {
            return;
        }

        $severityMap = $data['severity_map'] ?? [];
        $flatList    = $data['flat_list'] ?? [];

        // Populate from categories first so every flat_list word gets a category severity
        $categorySeverity = [];
        foreach (($data['categories'] ?? []) as $catName => $section) {
            if (!is_array($section)) {
                continue;
            }
            foreach ($section as $subKey => $value) {
                if (str_starts_with((string) $subKey, '_') || !is_array($value)) {
                    continue;
                }
                foreach ($value as $word) {
                    if (is_string($word)) {
                        $categorySeverity[$this->normaliseKey($word)] = (string) $catName;
                    }
                }
            }
        }

        foreach ($flatList as $word) {
            if (!is_string($word)) {
                continue;
            }
            $key = $this->normaliseKey($word);
            if ($key === '') {
                continue;
            }
            $this->wordSeverities[$key] = $severityMap[$word]
                ?? $categorySeverity[$key]
                ?? 'moderate';
        }
    }

    /**
     * Return candidate word => severity map sorted by phrase length descending
     * so multi-word phrases match before single words.
     *
     * @param  array<string>|null $severities
     * @return array<string, string>
     */
    private function getFilteredWords(?array $severities): array
    {
        $words = $this->wordSeverities;

        if ($severities !== null) {
            $allowed = array_flip($severities);
            $words   = array_filter($words, fn(string $sev): bool => isset($allowed[$sev]));
        }

        uksort($words, fn(string $a, string $b): int => mb_strlen($b, 'UTF-8') <=> mb_strlen($a, 'UTF-8'));

        return $words;
    }

    private function normaliseKey(string $word): string
    {
        $word = trim($word);
        $word = preg_replace('/\s+/u', ' ', $word) ?? $word;
        return mb_strtolower($word, 'UTF-8');
    }

    private function normaliseForMatching(string $text): string
    {
        // Strip zero-width characters (including ZWJ bypasses) for detection
        $text = preg_replace('/[\x{200B}\x{200C}\x{200D}\x{FEFF}]/u', '', $text) ?? $text;
        $text = preg_replace('/\s+/u', ' ', trim($text)) ?? trim($text);
        return $text;
    }

    private function buildWordPattern(string $word, bool $allowZwjBetweenChars = false): string
    {
        if ($allowZwjBetweenChars) {
            $chars = preg_split('//u', $word, -1, PREG_SPLIT_NO_EMPTY) ?: [];
            $parts = array_map(fn(string $ch): string => preg_quote($ch, '/'), $chars);
            $body  = implode('[\x{200B}\x{200C}\x{200D}]*', $parts);
        } else {
            $body = preg_quote($word, '/');
        }

        // Boundary check: not preceded or followed by Unicode letter, mark, or digit
        return '/(?<![\p{L}\p{M}\p{N}])' . $body . '(?![\p{L}\p{M}\p{N}])/iu';
    }
}
