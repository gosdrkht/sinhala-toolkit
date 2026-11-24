<?php

declare(strict_types=1);

/**
 * Normalizer.php
 *
 * Sinhala Number, Currency & Date Normaliser — part of sinhala-toolkit
 * Converts Sinhala numerals ↔ ASCII digits, parses LKR / රු. / ලක්ෂ / කෝටි
 * currency amounts, and normalises common Sinhala date phrases.
 *
 * @package  SinhalaToolkit
 * @author   gosdrkht
 * @license  MIT
 * @link     https://github.com/gosdrkht/sinhala-toolkit
 */

namespace SinhalaToolkit;

class Normalizer
{
    private const SINHALA_TO_ASCII_DIGITS = [
        '෦' => '0', '෧' => '1', '෨' => '2', '෩' => '3', '෪' => '4',
        '෫' => '5', '෬' => '6', '෭' => '7', '෮' => '8', '෯' => '9',
    ];

    private const ASCII_TO_SINHALA_DIGITS = [
        '0' => '෦', '1' => '෧', '2' => '෨', '3' => '෩', '4' => '෪',
        '5' => '෫', '6' => '෬', '7' => '෭', '8' => '෮', '9' => '෯',
    ];

    private const MULTIPLIERS = [
        'කෝටි'   => 10000000.0,
        'කෝටිය'  => 10000000.0,
        'කෝටියක්'=> 10000000.0,
        'ලක්ෂ'   => 100000.0,
        'ලක්ෂය'  => 100000.0,
        'ලක්ෂයක්'=> 100000.0,
        'දහස'    => 1000.0,
        'දහසක්'  => 1000.0,
        'දාහ'    => 1000.0,
        'දාහක්'  => 1000.0,
        'සියය'   => 100.0,
        'සියයක්' => 100.0,
    ];

    private const SINHALA_MONTHS = [
        'ජනවාරි'   => 1,
        'පෙබරවාරි' => 2,
        'මාර්තු'   => 3,
        'අප්‍රේල්' => 4,
        'මැයි'     => 5,
        'ජූනි'     => 6,
        'ජූලි'     => 7,
        'අගෝස්තු'  => 8,
        'සැප්තැම්බර්' => 9,
        'ඔක්තෝබර්' => 10,
        'නොවැම්බර්' => 11,
        'දෙසැම්බර්' => 12,
    ];

    /**
     * Convert Sinhala Lith digits (෦–෯) to ASCII digits (0–9).
     */
    public function sinhalaDigitsToAscii(string $text): string
    {
        return strtr($text, self::SINHALA_TO_ASCII_DIGITS);
    }

    /**
     * Convert ASCII digits (0–9) to Sinhala Lith digits (෦–෯).
     */
    public function asciiDigitsToSinhala(string $text): string
    {
        return strtr($text, self::ASCII_TO_SINHALA_DIGITS);
    }

    /**
     * Extract currency amounts (LKR, Rs., රු., රුපියල්) including Sinhala scale words
     * such as ලක්ෂ (100,000), කෝටි (10,000,000), and දහස (1,000).
     *
     * @param  string $text
     * @return array<int, array{raw: string, amount: float, currency: string}>
     */
    public function extractCurrency(string $text): array
    {
        $text = $this->sinhalaDigitsToAscii($text);
        $results = [];

        $multiplierPattern = implode('|', array_map(fn(string $k): string => preg_quote($k, '/'), array_keys(self::MULTIPLIERS)));

        // Pattern 1: Prefix (රු. / රුපියල් / LKR / Rs.) + optional multiplier + number + optional multiplier
        $pattern = '/(?:රුපියල්|රු\.?|LKR|Rs\.?)\s*(?:(' . $multiplierPattern . ')\s*)?(\d[\d,]*(?:\.\d+)?)(?:\s*(' . $multiplierPattern . '))?/iu';

        if (preg_match_all($pattern, $text, $matches, PREG_SET_ORDER)) {
            foreach ($matches as $m) {
                $raw     = trim($m[0]);
                $preMult = $m[1] ?? '';
                $numStr  = str_replace(',', '', $m[2]);
                $postMult = $m[3] ?? '';

                $amount = (float) $numStr;
                if ($preMult !== '' && isset(self::MULTIPLIERS[$preMult])) {
                    $amount *= self::MULTIPLIERS[$preMult];
                } elseif ($postMult !== '' && isset(self::MULTIPLIERS[$postMult])) {
                    $amount *= self::MULTIPLIERS[$postMult];
                }

                $results[] = [
                    'raw'      => $raw,
                    'amount'   => $amount,
                    'currency' => 'LKR',
                ];
            }
        }

        return $results;
    }

    /**
     * Extract Sinhala dates like "2026 නොවැම්බර් 24" into ISO format ("2026-11-24").
     *
     * @param  string $text
     * @return array<int, array{raw: string, iso: string}>
     */
    public function extractDates(string $text): array
    {
        $text = $this->sinhalaDigitsToAscii($text);
        $monthPattern = implode('|', array_map(fn(string $k): string => preg_quote($k, '/'), array_keys(self::SINHALA_MONTHS)));

        $results = [];
        // Matches: "2026 නොවැම්බර් 24" or "24 නොවැම්බර් 2026"
        $p1 = '/(\d{4})\s+(' . $monthPattern . ')\s+(\d{1,2})/u';
        if (preg_match_all($p1, $text, $matches, PREG_SET_ORDER)) {
            foreach ($matches as $m) {
                $year  = (int) $m[1];
                $month = self::SINHALA_MONTHS[$m[2]];
                $day   = (int) $m[3];
                if ($day >= 1 && $day <= 31) {
                    $results[] = [
                        'raw' => $m[0],
                        'iso' => sprintf('%04d-%02d-%02d', $year, $month, $day),
                    ];
                }
            }
        }

        $p2 = '/(\d{1,2})\s+(' . $monthPattern . ')\s+(\d{4})/u';
        if (preg_match_all($p2, $text, $matches, PREG_SET_ORDER)) {
            foreach ($matches as $m) {
                $day   = (int) $m[1];
                $month = self::SINHALA_MONTHS[$m[2]];
                $year  = (int) $m[3];
                if ($day >= 1 && $day <= 31) {
                    $results[] = [
                        'raw' => $m[0],
                        'iso' => sprintf('%04d-%02d-%02d', $year, $month, $day),
                    ];
                }
            }
        }

        return $results;
    }

    /**
     * Normalise Sinhala digits and currency prefixes (රු./රුපියල්/Rs. → LKR).
     */
    public function normalizeText(string $text): string
    {
        $text = $this->sinhalaDigitsToAscii($text);
        $text = preg_replace('/(?:රුපියල්|රු\.?|Rs\.?)\s*(?=\d)/iu', 'LKR ', $text) ?? $text;
        $text = preg_replace('/\s+/u', ' ', trim($text)) ?? trim($text);
        return $text;
    }
}
