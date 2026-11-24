<?php

declare(strict_types=1);

/**
 * KeywordExtractor.php
 *
 * Zero-dependency Sinhala Keyword Extractor & Extractive Summariser
 * Part of sinhala-toolkit
 *
 * @package  SinhalaToolkit
 * @author   gosdrkht
 * @license  MIT
 * @link     https://github.com/gosdrkht/sinhala-toolkit
 */

namespace SinhalaToolkit;

class KeywordExtractor
{
    private TextCleaner $cleaner;
    private Tokenizer $tokenizer;
    private Stemmer $stemmer;

    public function __construct(?string $stopwordsPath = null)
    {
        $this->cleaner   = new TextCleaner($stopwordsPath);
        $this->tokenizer = new Tokenizer();
        $this->stemmer   = new Stemmer();
    }

    /**
     * Extract top keywords from Sinhala or mixed text using stopword-filtered
     * frequency + early-position weighting.
     *
     * @param  string $text
     * @param  int    $topK         Number of keywords to return (default 5).
     * @param  bool   $useStemming  Group inflected words by stem (default false).
     * @return array<int, array{keyword: string, score: float, count: int}>
     */
    public function extract(string $text, int $topK = 5, bool $useStemming = false): array
    {
        if (trim($text) === '' || $topK <= 0) {
            return [];
        }

        $tokens = $this->tokenizer->tokenize($text, lowercase: true);
        $total  = count($tokens);
        if ($total === 0) {
            return [];
        }

        $counts = [];
        $scores = [];

        foreach ($tokens as $idx => $token) {
            if ($this->cleaner->isStopword($token)) {
                continue;
            }
            if ($this->tokenizer->classifyToken($token) === Tokenizer::TYPE_PUNCTUATION) {
                continue;
            }

            $key = $useStemming ? $this->stemmer->stem($token) : $token;
            if ($key === '' || $this->cleaner->isStopword($key)) {
                continue;
            }

            // Slight boost for words appearing earlier in the document
            $posWeight    = 1.0 + 0.25 * (1.0 - ($idx / max(1, $total)));
            $counts[$key] = ($counts[$key] ?? 0) + 1;
            $scores[$key] = ($scores[$key] ?? 0.0) + $posWeight;
        }

        if (empty($scores)) {
            return [];
        }

        $maxScore = max($scores);
        arsort($scores);

        $results = [];
        foreach (array_slice($scores, 0, $topK, true) as $keyword => $score) {
            $results[] = [
                'keyword' => (string) $keyword,
                'score'   => round($score / $maxScore, 3),
                'count'   => $counts[$keyword],
            ];
        }

        return $results;
    }

    /**
     * Extractive summariser — selects the top N most informative sentences
     * while preserving their original order in the text.
     *
     * @param  string $text
     * @param  int    $numSentences Number of sentences to include (default 2).
     * @return string
     */
    public function summarize(string $text, int $numSentences = 2): string
    {
        $sentences = $this->tokenizer->splitSentences($text, keepBoundary: true);
        if (count($sentences) <= $numSentences) {
            return implode(' ', $sentences);
        }

        $keywords = $this->extract($text, topK: 20);
        $weights  = [];
        foreach ($keywords as $item) {
            $weights[$item['keyword']] = $item['score'];
        }

        $sentenceScores = [];
        foreach ($sentences as $idx => $sentence) {
            $tokens = $this->tokenizer->tokenize($sentence, lowercase: true);
            $score  = 0.0;
            foreach ($tokens as $t) {
                $score += $weights[$t] ?? 0.0;
            }
            // Normalise slightly by sentence length so very long sentences don't dominate unfairly
            $sentenceScores[$idx] = $score / max(1.0, sqrt((float) count($tokens)));
        }

        arsort($sentenceScores);
        $selectedIndices = array_slice(array_keys($sentenceScores), 0, $numSentences);
        sort($selectedIndices);

        $selected = array_map(fn(int $i): string => $sentences[$i], $selectedIndices);
        return implode(' ', $selected);
    }
}
