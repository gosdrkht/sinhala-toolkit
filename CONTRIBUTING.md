# Contributing to sinhala-toolkit

පළමුව — **ස්තූතියි!** Thank you for taking the time to contribute. 🙏

This project exists to serve the Sri Lankan developer community, and every contribution — big or small — makes it better for everyone.

---

## Ways to Contribute

### 1. 🔤 Add Stopwords

The easiest contribution. Open `data/stopwords.json` and add missing Sinhala stopwords to the right category. Then add them to `flat_list` too.

**Rules:**
- Words must be common, carry little semantic meaning (like "the", "is" in English)
- Add to the correct category (`pronouns`, `conjunctions`, `particles` etc.)
- No duplicates — check `flat_list` before adding
- Keep both the categorised section AND `flat_list` in sync

### 2. 🐛 Report a Bug

Found a word that tokenizes wrong? A sentence that doesn't split correctly? Please open a GitHub Issue with:

- The input text (actual Sinhala text)
- What you expected
- What you got instead

### 3. 🧪 Add Test Cases

Real-world Sinhala text samples are very welcome — especially:
- News article sentences
- Social media / WhatsApp style text
- Mixed Sinhala + English (Singlish) sentences
- Sentences with ZWJ conjunct consonants

Add them to `tests/test_cleaner.php` or `tests/test_tokenizer.php`.

### 4. 📖 Improve Documentation

- Fix typos or unclear explanations
- Add Sinhala translations to the README
- Add usage examples for specific use cases

### 5. 💡 Build a New Feature

Check the [Roadmap](README.md#roadmap) for planned features. Comment on the relevant GitHub Issue before starting so we don't duplicate work.

---

## Development Setup

No special tools needed — just PHP 8.1+ and Git.

```bash
# 1. Fork the repo on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/sinhala-toolkit.git
cd sinhala-toolkit

# 2. Run the tests to make sure everything works
php tests/test_cleaner.php
php tests/test_tokenizer.php

# 3. Make your changes

# 4. Run tests again to make sure nothing is broken
php tests/test_cleaner.php
php tests/test_tokenizer.php
```

---

## Submitting a Pull Request

1. **Fork** the repo
2. **Create a branch** with a descriptive name:
   ```bash
   git checkout -b add-more-stopwords
   # or
   git checkout -b fix-tokenizer-zwj-bug
   ```
3. **Make your changes**
4. **Run the tests** — make sure both test files pass with no errors
5. **Commit** with a clear message:
   ```bash
   git add .
   git commit -m "Add 15 more conjunction stopwords"
   ```
6. **Push** to your fork:
   ```bash
   git push origin add-more-stopwords
   ```
7. **Open a Pull Request** on GitHub — describe what you changed and why

---

## Code Style

- PHP 8.1+ syntax
- Use `declare(strict_types=1)` in new files
- PHPDoc comments on all public methods
- Method names in `camelCase`
- Constants in `UPPER_SNAKE_CASE`
- UTF-8 encoding everywhere, always

---

## Questions?

Open a GitHub Issue and tag it `question`. We're friendly here! 😊

**ආයුබෝවන්! සාදරයෙන් පිළිගනිමු** 🇱🇰
