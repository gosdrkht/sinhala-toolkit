<div align="center">

# 🇱🇰 sinhala-toolkit
**The missing developer toolkit for Sinhala language processing**

සිංහල භාෂා සැකසීම සඳහා නවීන developer toolkit එක
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PHP Version](https://img.shields.io/badge/PHP-8.1%2B-blue.svg)](https://php.net)
[![Sinhala NLP](https://img.shields.io/badge/NLP-Sinhala-green.svg)]()
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![GitHub Stars](https://img.shields.io/github/stars/YOUR_USERNAME/sinhala-toolkit?style=social)]()

[English](#english) · [සිංහල](#sinhala) · [Quick Start](#quick-start) · [API Reference](#api-reference) · [Contributing](#contributing)

</div>

---

## Why this exists

There are academic NLP papers on Sinhala. There are scattered university datasets. But if you're a developer who wants to **just use** a Sinhala tokenizer, cleaner, or stopword filter in your PHP project today — you had nothing.

Until now.

`sinhala-toolkit` is production-ready, zero-dependency Sinhala NLP for PHP developers. Built for the Sri Lankan dev community, by a Sri Lankan developer.

---

<a name="english"></a>

## Features

| Feature | Status |
|---|---|
| 📋 Stopwords list (120+ curated words, categorised) | ✅ Ready |
| 🧹 Text cleaner (Unicode, ZWJ, whitespace, noise) | ✅ Ready |
| ✂️ Sentence tokenizer (danda, mixed punctuation) | ✅ Ready |
| 🔤 Word tokenizer (Sinhala, English, mixed) | ✅ Ready |
| 🔍 Token type classifier (sinhala/english/number/mixed) | ✅ Ready |
| 🧬 Grapheme cluster splitter (ZWJ conjuncts) | ✅ Ready |
| 📊 Word frequency counter | ✅ Ready |
| 🔡 Script detector (sinhala/english/mixed/unknown) | ✅ Ready |
| 💬 Singlish transliterator | 🔲 Coming soon |
| 😊 Sentiment analyser | 🔲 Coming soon |
| 🚫 Profanity filter | 🔲 Coming soon |

---

## Quick Start

### Installation

**Option 1 — Manual (shared hosting friendly)**

Download and drop the `src/` folder into your project:

```php
require_once 'src/TextCleaner.php';
require_once 'src/Tokenizer.php';

use SinhalaToolkit\TextCleaner;
use SinhalaToolkit\Tokenizer;
```

**Option 2 — Composer** *(coming soon)*

```bash
composer require YOUR_USERNAME/sinhala-toolkit
```

---

## Usage Examples

### Text Cleaner

```php
use SinhalaToolkit\TextCleaner;

$cleaner = new TextCleaner('/path/to/data/stopwords.json');

// Full clean pipeline
$raw  = "  මම   සහ  ඔබ   හොඳ  ගුරුවරයා  ළඟ  ඉගෙන  ගත්තා  ";
$text = $cleaner->clean($raw, [
    'remove_stopwords' => true,
]);
// Output: "හොඳ ගුරුවරයා ඉගෙන ගත්තා"

// Remove English and numbers from mixed text
$mixed = "මෙය good idea එකක් වේ 2024 දී";
$clean = $cleaner->clean($mixed, [
    'remove_english' => true,
    'remove_numbers' => true,
]);
// Output: "මෙය එකක් වේ"

// Detect script
$cleaner->detectScript("ආයුබෝවන්");          // "sinhala"
$cleaner->detectScript("Hello World");        // "english"
$cleaner->detectScript("Hello ආයුබෝවන්");   // "mixed"

// Check stopwords
$cleaner->isStopword("මම");      // true
$cleaner->isStopword("ගුරු");    // false
$cleaner->isStopword("සඳහා");    // true
```

---

### Tokenizer

```php
use SinhalaToolkit\Tokenizer;

$tokenizer = new Tokenizer();

// --- Sentence tokenization ---

$text = "ඔහු ගෙදර ගියා། ඇය පාසලට ගියාය། ළමයි ක්‍රීඩා කළා།";
$sentences = $tokenizer->splitSentences($text);
// [
//   "ඔහු ගෙදර ගියා",
//   "ඇය පාසලට ගියාය",
//   "ළමයි ක්‍රීඩා කළා"
// ]

// Works with mixed-language text too
$mixed = "What is your name? ඔබේ නම කුමක්ද?";
$sentences = $tokenizer->splitSentences($mixed);
// ["What is your name", "ඔබේ නම කුමක්ද"]


// --- Word tokenization ---

$tokens = $tokenizer->tokenize("ශ්‍රී ලංකාව ලස්සන රටකි");
// ["ශ්‍රී", "ලංකාව", "ලස්සන", "රටකි"]


// --- Tokenize with type metadata ---

$typed = $tokenizer->tokenizeWithTypes("ලංකා cricket team 2024 දී ජය ගත්තා");
// [
//   ["token" => "ලංකා",   "type" => "sinhala"],
//   ["token" => "cricket", "type" => "english"],
//   ["token" => "team",    "type" => "english"],
//   ["token" => "2024",    "type" => "number"],
//   ["token" => "දී",     "type" => "sinhala"],
//   ["token" => "ජය",     "type" => "sinhala"],
//   ["token" => "ගත්තා",  "type" => "sinhala"],
// ]


// --- Filter by type ---

$text = "Ceylon Ledger මගින් ඔබේ business 2024 සිට manage කරන්න";

$tokenizer->tokenizeByType($text, 'sinhala');
// ["මගින්", "ඔබේ", "සිට", "කරන්න"]

$tokenizer->tokenizeByType($text, 'english');
// ["Ceylon", "Ledger", "business", "manage"]


// --- Word frequency ---

$text = "ශ්‍රී ලංකාව ලස්සන රටකි ශ්‍රී ලංකාව හොඳ රටකි ශ්‍රී ලංකාව";
$freq = $tokenizer->frequency($text);
// ["ශ්‍රී" => 3, "ලංකාව" => 3, "රටකි" => 2, ...]


// --- Grapheme clusters (ZWJ conjuncts) ---

// ශ්‍රී contains a ZWJ conjunct consonant — kept intact as one cluster
$clusters = $tokenizer->graphemes("ශ්‍රී");
// ["ශ්‍රී"]  ← treated as a single grapheme unit
```

---

## Real-World Use Cases

**Search & filtering** — Strip stopwords before indexing Sinhala content so "ගෙදර ගෙදරට ගෙදරයි" all match "ගෙදර"

**Content moderation** — Detect script type to route Sinhala vs English vs mixed comments to the right classifier

**SMS / WhatsApp bots** — Clean noisy user input before passing to your logic

**AI pipelines** — Pre-process Sinhala text before sending to Claude API or any LLM

**News aggregators** — Sentence-split articles, count word frequency, extract keywords

---

## Data Files

### `data/stopwords.json`

120+ curated Sinhala stopwords organised into categories:

```
pronouns       → මම, ඔබ, ඔහු, ඇය, ඔවුන් ...
conjunctions   → හා, සහ, හෝ, නමුත් ...
prepositions   → ඉහත, පහත, සඳහා, ගැන ...
particles      → ද, නේ, යි, ම ...
aux_verbs      → ඇත, නැත, වේ, හැකි ...
question_words → මොකද, ඇයි, කවදා ...
adverbs        → ඉතා, බොහෝ, දැන් ...
```

The `flat_list` key gives you a ready-to-use array of all words:

```php
$data      = json_decode(file_get_contents('data/stopwords.json'), true);
$stopwords = $data['flat_list'];
```

---

## API Reference

### `TextCleaner`

```php
$cleaner = new TextCleaner(?string $stopwordsPath = null);
```

| Method | Parameters | Returns | Description |
|---|---|---|---|
| `clean()` | `string $text, array $options` | `string` | Full pipeline |
| `normaliseUnicode()` | `string $text` | `string` | NFC normalisation |
| `removeInvisibleChars()` | `string $text, bool $keepZwj` | `string` | Strip ZWJ/ZWNJ/BOM |
| `normaliseWhitespace()` | `string $text` | `string` | Collapse spaces |
| `removePunctuation()` | `string $text` | `string` | Strip punctuation |
| `removeEnglish()` | `string $text` | `string` | Strip ASCII letters |
| `removeNumbers()` | `string $text` | `string` | Strip digits |
| `removeStopwords()` | `string $text` | `string` | Filter stopwords |
| `detectScript()` | `string $text` | `string` | sinhala/english/mixed/unknown |
| `isPureSinhala()` | `string $text` | `bool` | Check purity |
| `isStopword()` | `string $word` | `bool` | Single word check |
| `getStopwords()` | — | `array` | Full stopword list |

**`clean()` options:**

```php
[
    'remove_stopwords'   => false,  // Remove stopwords
    'remove_punctuation' => false,  // Remove punctuation
    'remove_english'     => false,  // Remove English characters
    'remove_numbers'     => false,  // Remove digits
    'keep_zwj'           => true,   // Preserve ZWJ (Sinhala conjuncts)
]
```

---

### `Tokenizer`

```php
$tokenizer = new Tokenizer();
```

| Method | Parameters | Returns | Description |
|---|---|---|---|
| `splitSentences()` | `string $text, bool $keepBoundary` | `array` | Split into sentences |
| `tokenize()` | `string $text, bool $lowercase` | `array` | Word tokens |
| `tokenizeWithTypes()` | `string $text` | `array` | Tokens with type metadata |
| `tokenizeByType()` | `string $text, string $type` | `array` | Filter by type |
| `graphemes()` | `string $text` | `array` | Grapheme clusters |
| `classifyToken()` | `string $token` | `string` | sinhala/english/number/mixed |
| `frequency()` | `string $text, array $stopwords` | `array` | Word frequency map |
| `countTokens()` | `string $text` | `int` | Token count |
| `countSentences()` | `string $text` | `int` | Sentence count |

**Token types:** `sinhala` · `english` · `number` · `mixed` · `punctuation` · `unknown`

---

## Project Structure

```
sinhala-toolkit/
├── src/
│   ├── TextCleaner.php      # Text cleaning & normalisation
│   └── Tokenizer.php        # Sentence & word tokenization
├── data/
│   └── stopwords.json       # 120+ curated Sinhala stopwords
├── tests/
│   ├── test_cleaner.php
│   └── test_tokenizer.php
├── CONTRIBUTING.md
├── LICENSE
└── README.md
```

---

## Roadmap

- [ ] `composer require` support
- [ ] Singlish transliterator (`ආයුබෝවන්` ↔ `aayubowan`)
- [ ] Sinhala sentiment analyser
- [ ] Profanity / bad word filter
- [ ] Language detector (Sinhala vs Tamil vs English)
- [ ] Keyword extractor (TF-IDF)
- [ ] Python package (`pip install sinkit`)
- [ ] REST API (hosted)

---

## Contributing

**This project needs your help!** Especially:

- 🔤 More stopwords — open `data/stopwords.json` and add
- 🐛 Bug reports — especially edge cases with Sinhala Unicode
- 🧪 More test cases — real-world Sinhala text samples
- 📖 Sinhala documentation translation

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

<a name="sinhala"></a>

## සිංහල

**sinhala-toolkit** යනු PHP developers ලා සඳහා නිර්මාණය කරන ලද, නිෂ්පාදන-සූදානම් සිංහල NLP toolkit එකකි.

### ස්ථාපනය

```php
require_once 'src/TextCleaner.php';
require_once 'src/Tokenizer.php';
```

### සරල නිදර්ශනයක්

```php
$cleaner   = new SinhalaToolkit\TextCleaner('data/stopwords.json');
$tokenizer = new SinhalaToolkit\Tokenizer();

// පෙළ පිරිසිදු කිරීම
$clean = $cleaner->clean("මම සහ ඔබ හොඳ ගුරුවරයා ළඟ ඉගෙන ගත්තා", [
    'remove_stopwords' => true
]);
// ප්‍රතිඵලය: "හොඳ ගුරුවරයා ඉගෙන ගත්තා"

// වාක්‍ය කැපීම
$sentences = $tokenizer->splitSentences("ඔහු ගෙදර ගියා། ඇය පාසලට ගියාය།");
// ["ඔහු ගෙදර ගියා", "ඇය පාසලට ගියාය"]
```

---

## License

MIT © 2025 [Your Name](https://github.com/gosdrkht)

---

<div align="center">

Built for the Sri Lankan developer community
**ශ්‍රී ලාංකික developer ප්‍රජාව සඳහා නිර්මාණය කරන ලදී**
⭐ If this helped you, please star the repo! 🙏

</div>
