<?php

declare(strict_types=1);

/**
 * Transliterator.php
 *
 * Phonetic Singlish ↔ Sinhala Unicode Transliterator & URL Slug Generator
 * Part of sinhala-toolkit
 *
 * @package  SinhalaToolkit
 * @author   gosdrkht
 * @license  MIT
 * @link     https://github.com/gosdrkht/sinhala-toolkit
 */

namespace SinhalaToolkit;

class Transliterator
{
    private const HAL = "\u{0DCA}";
    private const ZWJ = "\u{200D}";

    /**
     * Common full-word Singlish → Sinhala dictionary overrides for everyday Sri Lankan usage.
     */
    private const WORD_OVERRIDES = [
        'aayubowan'  => 'ආයුබෝවන්',
        'ayubowan'   => 'ආයුබෝවන්',
        'kohomada'   => 'කොහොමද',
        'istuti'     => 'ස්තූතියි',
        'sthuthi'    => 'ස්තූතියි',
        'sthuthiyi'  => 'ස්තූතියි',
        'shri'       => "ශ්\u{200D}රී",
        'sri'        => "ශ්\u{200D}රී",
        'lanka'      => 'ලංකා',
        'lankawa'    => 'ලංකාව',
        'lankava'    => 'ලංකාව',
        'sinhala'    => 'සිංහල',
        'colombo'    => 'කොළඹ',
        'kolamba'    => 'කොළඹ',
        'gedara'     => 'ගෙදර',
        'hondai'     => 'හොඳයි',
        'hondayi'    => 'හොඳයි',
        'hoda'       => 'හොඳ',
        'honda'      => 'හොඳ',
        'lassana'    => 'ලස්සන',
        'oyata'      => 'ඔයාට',
        'mama'       => 'මම',
        'oba'        => 'ඔබ',
        'api'        => 'අපි',
        'ow'         => 'ඔව්',
        'na'         => 'නෑ',
        'nae'        => 'නෑ',
        'naha'       => 'නැහැ',
    ];

    /**
     * Singlish consonant sequences (longest-first).
     */
    private const CONSONANTS = [
        'nndh' => 'ඳ',
        'nnd'  => 'ඬ',
        'nng'  => 'ඟ',
        'ndh'  => 'ඳ',
        'mb'   => 'ඹ',
        'kh'   => 'ඛ',
        'gh'   => 'ඝ',
        'ch'   => 'ච',
        'jh'   => 'ඣ',
        'th'   => 'ත',
        'dh'   => 'ද',
        'ph'   => 'ඵ',
        'bh'   => 'භ',
        'sh'   => 'ශ',
        'Sh'   => 'ෂ',
        'gn'   => 'ඥ',
        'kn'   => 'ඤ',
        'ng'   => 'ං',
        'Th'   => 'ථ',
        'Dh'   => 'ධ',
        'Ch'   => 'ඡ',
        'Lu'   => 'ළු',
        'k'    => 'ක',
        'g'    => 'ග',
        'c'    => 'ච',
        'j'    => 'ජ',
        'T'    => 'ට',
        'D'    => 'ඩ',
        'N'    => 'ණ',
        't'    => 'ට',
        'd'    => 'ද',
        'n'    => 'න',
        'p'    => 'ප',
        'b'    => 'බ',
        'm'    => 'ම',
        'y'    => 'ය',
        'r'    => 'ර',
        'l'    => 'ල',
        'L'    => 'ළ',
        'v'    => 'ව',
        'w'    => 'ව',
        's'    => 'ස',
        'h'    => 'හ',
        'f'    => 'ෆ',
    ];

    /**
     * Independent Sinhala vowels (used at word start or after another vowel).
     */
    private const INDEPENDENT_VOWELS = [
        'aau' => 'ඖ',
        'aa'  => 'ආ',
        'ae'  => 'ඇ',
        'aaE' => 'ඈ',
        'aee' => 'ඈ',
        'ii'  => 'ඊ',
        'ee'  => 'ඊ',
        'uu'  => 'ඌ',
        'oo'  => 'ඕ',
        'ai'  => 'ඓ',
        'au'  => 'ඖ',
        'ou'  => 'ඖ',
        'a'   => 'අ',
        'i'   => 'ඉ',
        'u'   => 'උ',
        'e'   => 'එ',
        'o'   => 'ඔ',
    ];

    /**
     * Dependent Sinhala vowel signs (attached after a consonant).
     */
    private const VOWEL_SIGNS = [
        'aee' => 'ෑ',
        'aa'  => 'ා',
        'ae'  => 'ැ',
        'ii'  => 'ී',
        'ee'  => 'ී',
        'uu'  => 'ූ',
        'oo'  => 'ෝ',
        'ai'  => 'ෛ',
        'au'  => 'ෞ',
        'ou'  => 'ෞ',
        'a'   => '',   // inherent vowel
        'i'   => 'ි',
        'u'   => 'ු',
        'e'   => 'ෙ',
        'o'   => 'ො',
    ];

    /**
     * Sinhala Unicode → Romanized Singlish mappings.
     */
    private const SINHALA_INDEPENDENT_VOWELS = [
        'අ' => 'a',  'ආ' => 'aa', 'ඇ' => 'ae', 'ඈ' => 'aee',
        'ඉ' => 'i',  'ඊ' => 'ii', 'උ' => 'u',  'ඌ' => 'uu',
        'ඍ' => 'ri', 'ඎ' => 'rii','එ' => 'e',  'ඒ' => 'ee',
        'ඓ' => 'ai', 'ඔ' => 'o',  'ඕ' => 'oo', 'ඖ' => 'au',
    ];

    private const SINHALA_CONSONANTS = [
        'ක' => 'k',  'ඛ' => 'kh', 'ග' => 'g',  'ඝ' => 'gh', 'ඞ' => 'ng', 'ඟ' => 'ng',
        'ච' => 'ch', 'ඡ' => 'chh','ජ' => 'j',  'ඣ' => 'jh', 'ඤ' => 'gn', 'ඥ' => 'gn',
        'ට' => 't',  'ඨ' => 'th', 'ඩ' => 'd',  'ඪ' => 'dh', 'ණ' => 'n',  'ඬ' => 'nd',
        'ත' => 'th', 'ථ' => 'th', 'ද' => 'd',  'ධ' => 'dh', 'න' => 'n',  'ඳ' => 'nd',
        'ප' => 'p',  'ඵ' => 'ph', 'බ' => 'b',  'භ' => 'bh', 'ම' => 'm',  'ඹ' => 'mb',
        'ය' => 'y',  'ර' => 'r',  'ල' => 'l',  'ව' => 'w',
        'ශ' => 'sh', 'ෂ' => 'sh', 'ස' => 's',  'හ' => 'h',  'ළ' => 'l',  'ෆ' => 'f',
    ];

    private const SINHALA_VOWEL_SIGNS = [
        'ා' => 'a',  'ැ' => 'ae', 'ෑ' => 'ae', 'ි' => 'i',  'ී' => 'i',
        'ු' => 'u',  'ූ' => 'u',  'ෘ' => 'ru', 'ෙ' => 'e',  'ේ' => 'e',
        'ෛ' => 'ai', 'ො' => 'o',  'ෝ' => 'o',  'ෞ' => 'au', 'ෟ' => 'u',
        'ෲ' => 'ruu','ෳ' => 'au',
    ];

    private const SINHALA_SPECIALS = [
        'ං' => 'n',
        'ඃ' => 'h',
    ];

    /**
     * Convert phonetic Singlish text into Sinhala Unicode.
     *
     * @param  string $text
     * @return string
     */
    public function toSinhala(string $text): string
    {
        if (trim($text) === '') {
            return '';
        }

        // Process word-by-word while preserving whitespace and punctuation
        return preg_replace_callback('/[a-zA-Z]+/', function (array $m): string {
            return $this->transliterateWordToSinhala($m[0]);
        }, $text) ?? $text;
    }

    /**
     * Convert Sinhala Unicode text into readable Romanized Singlish.
     *
     * @param  string $text
     * @return string
     */
    public function toSinglish(string $text): string
    {
        if (trim($text) === '') {
            return '';
        }

        $chars = preg_split('//u', $text, -1, PREG_SPLIT_NO_EMPTY) ?: [];
        $len   = count($chars);
        $out   = '';
        $i     = 0;

        while ($i < $len) {
            $ch = $chars[$i];

            if (isset(self::SINHALA_CONSONANTS[$ch])) {
                $base = self::SINHALA_CONSONANTS[$ch];
                $i++;

                // Check for hal kirima (්)
                if ($i < $len && $chars[$i] === self::HAL) {
                    $i++;
                    // Check for ZWJ conjunct (rakaransaya ්‍ර or yansaya ්‍ය)
                    if ($i < $len && $chars[$i] === self::ZWJ) {
                        $i++;
                        $out .= $base;
                        continue;
                    }
                    $out .= $base;
                    continue;
                }

                // Check for dependent vowel sign
                if ($i < $len && isset(self::SINHALA_VOWEL_SIGNS[$chars[$i]])) {
                    $out .= $base . self::SINHALA_VOWEL_SIGNS[$chars[$i]];
                    $i++;
                    continue;
                }

                // Default inherent 'a' vowel
                $out .= $base . 'a';
                continue;
            }

            if (isset(self::SINHALA_INDEPENDENT_VOWELS[$ch])) {
                $out .= self::SINHALA_INDEPENDENT_VOWELS[$ch];
                $i++;
                continue;
            }

            if (isset(self::SINHALA_SPECIALS[$ch])) {
                $out .= self::SINHALA_SPECIALS[$ch];
                $i++;
                continue;
            }

            if ($ch === self::ZWJ || $ch === self::HAL) {
                $i++;
                continue;
            }

            // Pass through English, digits, spaces, punctuation
            $out .= $ch;
            $i++;
        }

        return $out;
    }

    /**
     * Generate a clean, SEO-friendly URL slug from Sinhala, English, or mixed text.
     *
     * Example: "ශ්‍රී ලංකාව ලස්සන රටකි" → "shri-lankawa-lassana-rataki"
     *
     * @param  string $text
     * @param  string $separator  Word separator (default '-').
     * @return string
     */
    public function slugify(string $text, string $separator = '-'): string
    {
        $romanized = $this->toSinglish($text);
        $romanized = mb_strtolower($romanized, 'UTF-8');
        $slug      = preg_replace('/[^a-z0-9]+/', $separator, $romanized) ?? '';
        return trim($slug, $separator);
    }

    // -------------------------------------------------------------------------
    // Private helpers
    // -------------------------------------------------------------------------

    private function transliterateWordToSinhala(string $word): string
    {
        $lower = strtolower($word);
        if (isset(self::WORD_OVERRIDES[$lower])) {
            return self::WORD_OVERRIDES[$lower];
        }

        $len = strlen($word);
        $out = '';
        $i   = 0;

        while ($i < $len) {
            // Try matching a consonant first
            $matchedConsonant = $this->matchPrefix($word, $i, self::CONSONANTS);
            if ($matchedConsonant !== null) {
                [$key, $sinhalaCons] = $matchedConsonant;
                $i += strlen($key);

                // Special case: anusvaraya 'ng' doesn't take hal kirima or vowel sign
                if ($sinhalaCons === 'ං') {
                    $out .= $sinhalaCons;
                    continue;
                }

                // Check for rakaransaya (consonant + 'r' + vowel) e.g. 'kra', 'pri'
                if ($i < $len && $word[$i] === 'r' && $i + 1 < $len && $this->matchPrefix($word, $i + 1, self::VOWEL_SIGNS) !== null && $key !== 'r') {
                    $i++; // consume 'r'
                    $vowelMatch = $this->matchPrefix($word, $i, self::VOWEL_SIGNS);
                    $sign       = '';
                    if ($vowelMatch !== null) {
                        [$vKey, $sign] = $vowelMatch;
                        $i += strlen($vKey);
                    }
                    $out .= $sinhalaCons . self::HAL . self::ZWJ . 'ර' . $sign;
                    continue;
                }

                // Check for following vowel sign
                $vowelMatch = $this->matchPrefix($word, $i, self::VOWEL_SIGNS);
                if ($vowelMatch !== null) {
                    [$vKey, $sign] = $vowelMatch;
                    $i += strlen($vKey);
                    $out .= $sinhalaCons . $sign;
                } else {
                    // Consonant without following vowel gets hal kirima (්)
                    $out .= $sinhalaCons . self::HAL;
                }
                continue;
            }

            // Try matching an independent vowel
            $vowelMatch = $this->matchPrefix($word, $i, self::INDEPENDENT_VOWELS);
            if ($vowelMatch !== null) {
                [$vKey, $sinhalaVowel] = $vowelMatch;
                $i += strlen($vKey);
                $out .= $sinhalaVowel;
                continue;
            }

            // Fallback: keep character as-is
            $out .= $word[$i];
            $i++;
        }

        return $out;
    }

    /**
     * @param  array<string, string> $map
     * @return array{0: string, 1: string}|null
     */
    private function matchPrefix(string $word, int $offset, array $map): ?array
    {
        $slice = substr($word, $offset);
        foreach ($map as $key => $val) {
            if (str_starts_with($slice, $key)) {
                return [$key, $val];
            }
        }
        // Retry case-insensitively on lowercased slice
        $lowerSlice = strtolower($slice);
        foreach ($map as $key => $val) {
            if (str_starts_with($lowerSlice, strtolower($key))) {
                return [$key, $val];
            }
        }
        return null;
    }
}
