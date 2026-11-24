import test from "node:test";
import assert from "node:assert/strict";
import {
  TextCleaner,
  Tokenizer,
  SentimentAnalyser,
  ProfanityFilter,
  Transliterator,
  Stemmer,
  KeywordExtractor,
  Normalizer,
  Chunker,
} from "../src/index.js";

test("TextCleaner cleans, detects trilingual scripts, and preserves Sinhala marks", () => {
  const c = new TextCleaner();
  assert.equal(c.detectScript("ආයුබෝවන්"), "sinhala");
  assert.equal(c.detectScript("வணக்கம்"), "tamil");
  assert.equal(c.detectScript("Hello"), "english");
  assert.equal(c.detectScript("ආයුබෝවන් வணக்கம்"), "mixed");
  assert.equal(c.removePunctuation("ශ්\u200Dරී ලංකාව! හොඳයි."), "ශ්\u200Dරී ලංකාව හොඳයි");
});

test("Tokenizer splits sentences, tokens, and ZWJ graphemes", () => {
  const t = new Tokenizer();
  assert.deepEqual(t.splitSentences("ඔහු ගෙදර ගියා\u0964 ඇය පාසලට ගියාය\u0964"), [
    "ඔහු ගෙදර ගියා",
    "ඇය පාසලට ගියාය",
  ]);
  assert.deepEqual(t.graphemes("ශ්\u200Dරී"), ["ශ්\u200Dරී"]);
});

test("SentimentAnalyser handles Sinhala post-negation", () => {
  const sa = new SentimentAnalyser();
  assert.equal(sa.analyse("මෙය ඉතා හොඳ චිත්‍රපටයකි").label, "positive");
  assert.equal(sa.analyse("මෙය හොඳ නෑ").label, "negative");
});

test("ProfanityFilter detects, censors, and ranks severity", () => {
  const pf = new ProfanityFilter();
  assert.equal(pf.containsProfanity("ඔහු මෝඩයා"), true);
  assert.equal(pf.containsProfanity("I love football"), false);
  assert.equal(pf.censor("ඔහු මෝඩයා"), "ඔහු ***");
  assert.equal(pf.highestSeverity("මෝඩයා සහ වංචාකාරයා"), "moderate");
});

test("Transliterator converts Singlish <-> Sinhala and slugifies", () => {
  const tr = new Transliterator();
  assert.equal(tr.toSinhala("aayubowan lanka"), "ආයුබෝවන් ලංකා");
  assert.equal(tr.slugify("ශ්\u200Dරී ලංකාව ලස්සන රටකි"), "shri-lankawa-lassana-rataki");
});

test("Stemmer strips common Sinhala suffixes", () => {
  const st = new Stemmer();
  assert.equal(st.stem("ගෙදරට"), "ගෙදර");
  assert.equal(st.stem("ගෙදරින්"), "ගෙදර");
  assert.equal(st.stem("ගෙදරයි"), "ගෙදර");
});

test("KeywordExtractor extracts keywords and summarizes", () => {
  const ke = new KeywordExtractor();
  const kw = ke.extract("ශ්\u200Dරී ලංකාව ලස්සන රටකි ශ්\u200Dරී ලංකාව හොඳ රටකි", 2);
  assert.deepEqual(kw.map((k) => k.keyword), ["ශ්\u200Dරී", "ලංකාව"]);
});

test("Normalizer converts digits and extracts LKR currency", () => {
  const norm = new Normalizer();
  assert.equal(norm.sinhalaDigitsToAscii("෨෦෨෪"), "2024");
  const curr = norm.extractCurrency("මිල රු. ලක්ෂ 5 කි");
  assert.equal(curr[0].amount, 500000);
});

test("Chunker splits sentences cleanly and estimates tokens", () => {
  const ch = new Chunker();
  assert.deepEqual(ch.chunk("ඔහු ගෙදර ගියා\u0964 ඇය පාසලට ගියාය\u0964", 20), [
    "ඔහු ගෙදර ගියා\u0964",
    "ඇය පාසලට ගියාය\u0964",
  ]);
  assert.ok(ch.estimateTokens("ශ්\u200Dරී ලංකාව") > 0);
});
