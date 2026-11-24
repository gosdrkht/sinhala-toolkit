<?php

declare(strict_types=1);

/**
 * SentimentAnalyser.php
 *
 * Rule-based Sinhala Sentiment Analyser — part of sinhala-toolkit
 * Lightweight, zero-dependency dictionary-based sentiment analysis for Sinhala.
 *
 * @package  SinhalaToolkit
 * @author   gosdrkht
 * @license  MIT
 * @link     https://github.com/gosdrkht/sinhala-toolkit
 */

namespace SinhalaToolkit;

class SentimentAnalyser
{
    public const POSITIVE_WORDS = [
        'හොඳ', 'හොඳයි', 'හොඳම', 'හොඳටම',
        'ලස්සන', 'ලස්සනයි',
        'සුන්දර', 'සුන්දරයි',
        'අපූරු', 'අපූරුයි',
        'ජය', 'ජයග්‍රහණය',
        'සතුට', 'සතුටුයි', 'සතුටු',
        'ආදරය', 'ආදරණීය',
        'සාර්ථක', 'සාර්ථකයි',
        'ශ්‍රේෂ්ඨ', 'ශ්‍රේෂ්ඨයි',
        'නියම', 'නියමයි',
        'ඉක්මන්', 'ශක්තිමත්',
        'නිදහස', 'නිදහස්',
        'ප්‍රිය', 'ප්‍රියමනාප',
        'සුඛ', 'සුඛී',
        'දිනුම', 'දිනුවා',
        'ශක්ති',
        'ප්‍රශංසා', 'ප්‍රශංසනීය',
        'දීප්තිමත්', 'දක්ෂ',
        'විශිෂ්ට', 'විශිෂ්ටයි',
        'සමෘද්ධිමත්', 'සමෘද්ධිය',
        'ඔව්', 'හරි', 'ඇත්ත',
        'සාමය', 'ශාන්ත',
        'ගෞරව', 'ගෞරවනීය',
        'කීර්තිමත්', 'කීර්තිය',
        'ප්‍රේමය', 'ප්‍රේමණීය',
        'රසවත්', 'රසවතා',
        'අගේ', 'ගිනිකෙළි',
        'අලංකාර', 'සිත් ගන්නා',
    ];

    public const NEGATIVE_WORDS = [
        'නරක', 'නරකයි', 'නරකම',
        'කණගාටු', 'කණගාටුයි',
        'දුක', 'දුකයි', 'දුක්',
        'රොත්ත', 'කෝපය', 'කෝපයි',
        'අපජය', 'පරාජය',
        'බිය', 'බියයි', 'භය',
        'ගැටලු', 'ගැටලුව',
        'අසාර්ථක', 'අසාර්ථකයි',
        'ශෝකය', 'ශෝකී',
        'නිදහස් නෑ',
        'වේදනා', 'වේදනාකාරී',
        'රෝගය', 'රෝගී',
        'දූෂිත', 'දූෂණය',
        'ක්‍රෝධය', 'ක්‍රෝධී',
        'ද්වේෂය', 'ද්වේෂී',
        'පාඩු', 'අහිමි',
        'හිරිහැර', 'හිරිහැරකාරී',
        'අසාධාරණ', 'අසාධාරණයි',
        'සුසාන', 'ශාපය',
        'මරණය', 'මරණ',
        'හිං', 'හිංසා',
        'ෆේල්',
        'ව්‍යසනය', 'ව්‍යසනකාරී',
        'හරිම නරක',
        'කිළිටි',
    ];

    public const NEGATION_WORDS = [
        'නෑ', 'නැහැ', 'නැත', 'නෙමෙයි', 'බෑ', 'බැරි', 'නෙ', 'නෙමේ',
    ];

    public const INTENSIFIERS = [
        'ඉතා'    => 1.5,
        'ඉතාමත්' => 1.8,
        'බොහෝ'   => 1.3,
        'ගොඩාක්' => 1.4,
        'හරිම'   => 1.6,
        'ඉතාම'   => 1.5,
    ];

    /** @var array<string, bool> */
    private array $positive;

    /** @var array<string, bool> */
    private array $negative;

    /** @var array<string, bool> */
    private array $negations;

    private Tokenizer $tokenizer;

    /**
     * @param array<string>|null $positiveWords Custom positive lexicon (optional).
     * @param array<string>|null $negativeWords Custom negative lexicon (optional).
     */
    public function __construct(?array $positiveWords = null, ?array $negativeWords = null)
    {
        $this->positive  = array_fill_keys($positiveWords ?? self::POSITIVE_WORDS, true);
        $this->negative  = array_fill_keys($negativeWords ?? self::NEGATIVE_WORDS, true);
        $this->negations = array_fill_keys(self::NEGATION_WORDS, true);
        $this->tokenizer = new Tokenizer();
    }

    /**
     * Analyse the sentiment of a Sinhala text string.
     *
     * @param  string $text
     * @return array{label: string, score: float, positive: int, negative: int, tokens: array<string>}
     */
    public function analyse(string $text): array
    {
        $tokens   = $this->tokenizer->tokenize($text);
        $count    = count($tokens);
        $posScore = 0.0;
        $negScore = 0.0;

        for ($i = 0; $i < $count; $i++) {
            $token = $tokens[$i];

            // Support both pre-negation and Sinhala SOV post-negation
            $prevNeg = $i > 0 && isset($this->negations[$tokens[$i - 1]]);
            $nextNeg = ($i + 1 < $count) && isset($this->negations[$tokens[$i + 1]]);
            $negate  = $prevNeg !== $nextNeg;

            $multiplier = $i > 0 ? (self::INTENSIFIERS[$tokens[$i - 1]] ?? 1.0) : 1.0;

            if (isset($this->positive[$token])) {
                if ($negate) {
                    $negScore += 1.0 * $multiplier;
                } else {
                    $posScore += 1.0 * $multiplier;
                }
            } elseif (isset($this->negative[$token])) {
                if ($negate) {
                    $posScore += 1.0 * $multiplier;
                } else {
                    $negScore += 1.0 * $multiplier;
                }
            }
        }

        $total = $posScore + $negScore;
        if ($total === 0.0) {
            return [
                'label'    => 'neutral',
                'score'    => 0.5,
                'positive' => 0,
                'negative' => 0,
                'tokens'   => $tokens,
            ];
        }

        $posRatio = $posScore / $total;
        $negRatio = $negScore / $total;

        if ($posRatio > $negRatio) {
            $label = 'positive';
            $score = round(0.5 + ($posRatio - 0.5) * 0.9, 3);
        } elseif ($negRatio > $posRatio) {
            $label = 'negative';
            $score = round(0.5 + ($negRatio - 0.5) * 0.9, 3);
        } else {
            $label = 'neutral';
            $score = 0.5;
        }

        return [
            'label'    => $label,
            'score'    => min($score, 1.0),
            'positive' => (int) $posScore,
            'negative' => (int) $negScore,
            'tokens'   => $tokens,
        ];
    }

    /**
     * Analyse an array of texts and return results in order.
     *
     * @param  array<string> $texts
     * @return array<int, array{label: string, score: float, positive: int, negative: int, tokens: array<string>}>
     */
    public function batchAnalyse(array $texts): array
    {
        return array_map(fn(string $t): array => $this->analyse($t), $texts);
    }

    public function isPositive(string $text): bool
    {
        return $this->analyse($text)['label'] === 'positive';
    }

    public function isNegative(string $text): bool
    {
        return $this->analyse($text)['label'] === 'negative';
    }

    /**
     * Add custom positive words to the lexicon at runtime.
     *
     * @param  array<string> $words
     * @return self
     */
    public function addPositiveWords(array $words): self
    {
        foreach ($words as $w) {
            $this->positive[$w] = true;
        }
        return $this;
    }

    /**
     * Add custom negative words to the lexicon at runtime.
     *
     * @param  array<string> $words
     * @return self
     */
    public function addNegativeWords(array $words): self
    {
        foreach ($words as $w) {
            $this->negative[$w] = true;
        }
        return $this;
    }
}
