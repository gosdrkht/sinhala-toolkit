/**
 * sinhala-toolkit (JavaScript / TypeScript ESM)
 * Zero-dependency Sinhala NLP toolkit — works in Node.js 18+ and browsers.
 *
 * @license MIT
 * @see https://github.com/gosdrkht/sinhala-toolkit
 */

const ZWJ = "\u200D";
const HAL = "\u0DCA";
const DANDA = "\u0964";
const DOUBLE_DANDA = "\u0965";

const SINHALA_RE = /[\u0D80-\u0DFF]/;
const TAMIL_RE = /[\u0B80-\u0BFF]/;
const ENGLISH_RE = /[a-zA-Z]/;
const NUMBER_RE = /[0-9\u0DE6-\u0DEF]/;

const DEFAULT_STOPWORDS = [
  "මම", "ඔබ", "ඔහු", "ඇය", "අපි", "ඔවුන්", "එය", "මේ", "ඒ", "සහ", "හා",
  "හෝ", "නමුත්", "සඳහා", "ගැන", "ළඟ", "වේ", "ඇත", "නැත", "ඉතා", "බොහෝ",
];

const POSITIVE_WORDS = new Set([
  "හොඳ", "හොඳයි", "හොඳම", "හොඳටම", "ලස්සන", "ලස්සනයි", "සුන්දර", "සුන්දරයි",
  "අපූරු", "ජය", "සතුට", "සතුටුයි", "ආදරය", "සාර්ථක", "ශ්‍රේෂ්ඨ", "නියම",
  "නියමයි", "විශිෂ්ට", "ඔව්", "හරි", "ඇත්ත", "සාමය", "රසවත්",
]);

const NEGATIVE_WORDS = new Set([
  "නරක", "නරකයි", "නරකම", "කණගාටු", "කණගාටුයි", "දුක", "දුකයි", "කෝපය",
  "පරාජය", "බිය", "ගැටලු", "අසාර්ථක", "ශෝකය", "වේදනා", "දූෂිත", "පාඩු",
  "හිරිහැර", "අසාධාරණ", "ෆේල්", "ව්‍යසනය", "කිළිටි",
]);

const NEGATION_WORDS = new Set([
  "නෑ", "නැහැ", "නැත", "නෙමෙයි", "බෑ", "බැරි", "නෙ", "නෙමේ",
]);

const INTENSIFIERS = {
  "ඉතා": 1.5,
  "ඉතාමත්": 1.8,
  "බොහෝ": 1.3,
  "ගොඩාක්": 1.4,
  "හරිම": 1.6,
  "ඉතාම": 1.5,
};

const DEFAULT_PROFANITY = {
  "ගොන": "mild",
  "ගොන්නා": "mild",
  "බල්ලා": "mild",
  "මෝඩ": "mild",
  "මෝඩයා": "mild",
  "හරක්": "moderate",
  "හරකා": "moderate",
  "බොරු කාරයා": "moderate",
  "කුණු": "moderate",
  "කැත": "moderate",
  "වංචාකාරයා": "moderate",
  "සොරා": "moderate",
  "හූ": "strong",
  "හූකාරයා": "strong",
  "stupid": "singlish_slang",
  "idiot": "singlish_slang",
  "fool": "singlish_slang",
  "loser": "singlish_slang",
  "trash": "singlish_slang",
};

const SEVERITY_RANK = {
  mild: 1,
  singlish_slang: 2,
  moderate: 3,
  strong: 4,
  hate_speech: 5,
};

function isDiacritic(ch) {
  const cp = ch.codePointAt(0);
  return (
    (cp >= 0x0dca && cp <= 0x0ddf) ||
    (cp >= 0x0df2 && cp <= 0x0df3) ||
    cp === 0x0d82 ||
    cp === 0x0d83
  );
}

export class TextCleaner {
  constructor(stopwords = DEFAULT_STOPWORDS) {
    this.stopwords = new Set(stopwords);
  }

  clean(text, options = {}) {
    const opts = {
      removeStopwords: false,
      removePunctuation: false,
      removeEnglish: false,
      removeNumbers: false,
      keepZwj: true,
      ...options,
    };

    let out = this.normaliseUnicode(text);
    out = this.removeInvisibleChars(out, opts.keepZwj);
    out = this.normaliseWhitespace(out);
    if (opts.removePunctuation) out = this.removePunctuation(out);
    if (opts.removeEnglish) out = this.removeEnglish(out);
    if (opts.removeNumbers) out = this.removeNumbers(out);
    if (opts.removeStopwords) out = this.removeStopwords(out);
    return out.trim();
  }

  normaliseUnicode(text) {
    return text.normalize("NFC");
  }

  removeInvisibleChars(text, keepZwj = true) {
    let out = text.replace(/[\u200B\u200C\uFEFF\u00AD\u200E\u200F]/g, "");
    if (!keepZwj) out = out.replaceAll(ZWJ, "");
    return out.replace(/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/g, "");
  }

  normaliseWhitespace(text) {
    return text.replace(/[\s\u00A0\u3000]+/g, " ").trim();
  }

  removePunctuation(text, keepDanda = true) {
    const re = keepDanda
      ? /[^\p{L}\p{M}\p{N}\s\u200D\u0964\u0965]/gu
      : /[^\p{L}\p{M}\p{N}\s\u200D]/gu;
    return this.normaliseWhitespace(text.replace(re, " "));
  }

  removeEnglish(text) {
    return this.normaliseWhitespace(text.replace(/[a-zA-Z]+/g, " "));
  }

  removeNumbers(text) {
    return this.normaliseWhitespace(text.replace(/[0-9\u0DE6-\u0DEF]/g, " "));
  }

  removeStopwords(text) {
    return this.normaliseWhitespace(text)
      .split(" ")
      .filter((t) => t && !this.stopwords.has(t))
      .join(" ");
  }

  containsSinhala(text) {
    return SINHALA_RE.test(text);
  }

  containsTamil(text) {
    return TAMIL_RE.test(text);
  }

  isPureSinhala(text) {
    return /^[\u0D80-\u0DFF\u200D\s\u0964\u0965]+$/.test(text.trim());
  }

  detectScript(text) {
    const hasSi = this.containsSinhala(text);
    const hasTa = this.containsTamil(text);
    const hasEn = ENGLISH_RE.test(text);
    const count = Number(hasSi) + Number(hasTa) + Number(hasEn);
    if (count > 1) return "mixed";
    if (hasSi) return "sinhala";
    if (hasTa) return "tamil";
    if (hasEn) return "english";
    return "unknown";
  }

  isStopword(word) {
    return this.stopwords.has(word.trim());
  }
}

export class Tokenizer {
  splitSentences(text, keepBoundary = false) {
    if (!text.trim()) return [];
    let s = text.replace(/\r\n|\r/g, "\n");
    s = s.replace(new RegExp(`([${DANDA}${DOUBLE_DANDA}])\\s*`, "gu"), "$1\x00");
    s = s.replace(/(\.)(\s+)(?=[A-Z\u0D80-\u0DFF])/gu, "$1\x00");
    s = s.replace(/([?!])\s*/gu, "$1\x00");
    s = s.replace(/\n+/g, "\x00");

    const stripRe = new RegExp(`[${DANDA}${DOUBLE_DANDA}.?!]+$`, "u");
    return s
      .split("\x00")
      .map((part) => {
        let p = part.trim();
        if (!keepBoundary) p = p.replace(stripRe, "").trim();
        return p;
      })
      .filter(Boolean);
  }

  tokenize(text, lowercase = false) {
    if (!text.trim()) return [];
    const s = lowercase ? text.replace(/[A-Z]+/g, (m) => m.toLowerCase()) : text;
    return s
      .trim()
      .split(/\s+/)
      .map((raw) =>
        raw
          .replace(/^[^\p{L}\p{N}\u200D\u0D80-\u0DF3]+/u, "")
          .replace(/[^\p{L}\p{N}\u200D\u0D80-\u0DF3]+$/u, "")
      )
      .filter(Boolean);
  }

  graphemes(text) {
    if (!text.trim()) return [];
    const chars = Array.from(text);
    const clusters = [];
    let i = 0;
    while (i < chars.length) {
      let cluster = chars[i++];
      while (i < chars.length && isDiacritic(chars[i])) cluster += chars[i++];
      while (i < chars.length && chars[i] === ZWJ) {
        cluster += chars[i++];
        if (i < chars.length) {
          cluster += chars[i++];
          while (i < chars.length && isDiacritic(chars[i])) cluster += chars[i++];
        }
      }
      clusters.push(cluster);
    }
    return clusters;
  }

  classifyToken(token) {
    const hasSi = SINHALA_RE.test(token);
    const hasEn = ENGLISH_RE.test(token);
    const hasNum = NUMBER_RE.test(token);
    const isPunct = /^[^\p{L}\p{M}\p{N}]+$/u.test(token);
    if (isPunct) return "punctuation";
    if (hasSi && !hasEn && !hasNum) return "sinhala";
    if (hasEn && !hasSi && !hasNum) return "english";
    if (hasNum && !hasSi && !hasEn) return "number";
    if (hasSi || hasEn || hasNum) return "mixed";
    return "unknown";
  }
}

export class SentimentAnalyser {
  constructor(positiveWords = null, negativeWords = null) {
    this.positive = new Set(positiveWords || POSITIVE_WORDS);
    this.negative = new Set(negativeWords || NEGATIVE_WORDS);
    this.tokenizer = new Tokenizer();
  }

  analyse(text) {
    const tokens = this.tokenizer.tokenize(text);
    let posScore = 0;
    let negScore = 0;

    for (let i = 0; i < tokens.length; i++) {
      const token = tokens[i];
      const prevNeg = i > 0 && NEGATION_WORDS.has(tokens[i - 1]);
      const nextNeg = i + 1 < tokens.length && NEGATION_WORDS.has(tokens[i + 1]);
      const negate = prevNeg !== nextNeg;
      const mult = i > 0 ? INTENSIFIERS[tokens[i - 1]] || 1.0 : 1.0;

      if (this.positive.has(token)) {
        if (negate) negScore += mult;
        else posScore += mult;
      } else if (this.negative.has(token)) {
        if (negate) posScore += mult;
        else negScore += mult;
      }
    }

    const total = posScore + negScore;
    if (total === 0) {
      return { label: "neutral", score: 0.5, positive: 0, negative: 0, tokens };
    }
    const posRatio = posScore / total;
    const negRatio = negScore / total;
    let label = "neutral";
    let score = 0.5;
    if (posRatio > negRatio) {
      label = "positive";
      score = Math.min(1, Number((0.5 + (posRatio - 0.5) * 0.9).toFixed(3)));
    } else if (negRatio > posRatio) {
      label = "negative";
      score = Math.min(1, Number((0.5 + (negRatio - 0.5) * 0.9).toFixed(3)));
    }
    return {
      label,
      score,
      positive: Math.trunc(posScore),
      negative: Math.trunc(negScore),
      tokens,
    };
  }
}

export class ProfanityFilter {
  constructor(wordSeverities = DEFAULT_PROFANITY) {
    this.wordSeverities = new Map(
      Object.entries(wordSeverities).map(([k, v]) => [k.trim().toLowerCase(), v])
    );
  }

  _escapeRegex(s) {
    return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  }

  _buildPattern(word, allowZwj = false) {
    const body = allowZwj
      ? Array.from(word).map((c) => this._escapeRegex(c)).join("[\\u200B\\u200C\\u200D]*")
      : this._escapeRegex(word);
    return new RegExp(`(?<![\\p{L}\\p{M}\\p{N}])${body}(?![\\p{L}\\p{M}\\p{N}])`, "giu");
  }

  _entries(severities = null) {
    const allowed = severities ? new Set(severities) : null;
    return Array.from(this.wordSeverities.entries())
      .filter(([, sev]) => !allowed || allowed.has(sev))
      .sort((a, b) => b[0].length - a[0].length);
  }

  findMatches(text, severities = null) {
    const norm = text.replace(/[\u200B\u200C\u200D\uFEFF]/g, "").replace(/\s+/g, " ").trim();
    if (!norm) return [];
    const matches = [];
    for (const [word, severity] of this._entries(severities)) {
      if (this._buildPattern(word).test(norm)) {
        matches.push({ word, severity });
      }
    }
    return matches;
  }

  containsProfanity(text, severities = null) {
    return this.findMatches(text, severities).length > 0;
  }

  censor(text, replacement = "***", severities = null) {
    let out = text;
    for (const [word] of this._entries(severities)) {
      out = out.replace(this._buildPattern(word, true), replacement);
    }
    return out;
  }

  highestSeverity(text) {
    const matches = this.findMatches(text);
    if (!matches.length) return null;
    return matches.reduce((best, m) =>
      (SEVERITY_RANK[m.severity] || 1) > (SEVERITY_RANK[best] || 0) ? m.severity : best
    , matches[0].severity);
  }
}

const WORD_OVERRIDES = {
  aayubowan: "ආයුබෝවන්",
  ayubowan: "ආයුබෝවන්",
  kohomada: "කොහොමද",
  shri: "ශ්\u200Dරී",
  sri: "ශ්\u200Dරී",
  lanka: "ලංකා",
  lankawa: "ලංකාව",
  sinhala: "සිංහල",
  gedara: "ගෙදර",
  hondai: "හොඳයි",
  lassana: "ලස්සන",
  mama: "මම",
  oba: "ඔබ",
};

const SINHALA_CONS_MAP = {
  ක: "k", ඛ: "kh", ග: "g", ඝ: "gh", ඞ: "ng", ඟ: "ng",
  ච: "ch", ඡ: "chh", ජ: "j", ඣ: "jh", ඤ: "gn", ඥ: "gn",
  ට: "t", ඨ: "th", ඩ: "d", ඪ: "dh", ණ: "n", ඬ: "nd",
  ත: "th", ථ: "th", ද: "d", ධ: "dh", න: "n", ඳ: "nd",
  ප: "p", ඵ: "ph", බ: "b", භ: "bh", ම: "m", ඹ: "mb",
  ය: "y", ර: "r", ල: "l", ව: "w",
  ශ: "sh", ෂ: "sh", ස: "s", හ: "h", ළ: "l", ෆ: "f",
};

const SINHALA_VOWEL_MAP = {
  අ: "a", ආ: "aa", ඇ: "ae", ඈ: "aee", ඉ: "i", ඊ: "ii",
  උ: "u", ඌ: "uu", එ: "e", ඒ: "ee", ඔ: "o", ඕ: "oo",
};

const SINHALA_SIGN_MAP = {
  "ා": "a", "ැ": "ae", "ෑ": "ae", "ි": "i", "ී": "i",
  "ු": "u", "ූ": "u", "ෘ": "ru", "ෙ": "e", "ේ": "e",
  "ෛ": "ai", "ො": "o", "ෝ": "o", "ෞ": "au",
};

export class Transliterator {
  toSinhala(text) {
    if (!text.trim()) return "";
    return text.replace(/[a-zA-Z]+/g, (word) => {
      const lower = word.toLowerCase();
      return WORD_OVERRIDES[lower] || word;
    });
  }

  toSinglish(text) {
    if (!text.trim()) return "";
    const chars = Array.from(text);
    let out = "";
    let i = 0;
    while (i < chars.length) {
      const ch = chars[i];
      if (SINHALA_CONS_MAP[ch]) {
        const base = SINHALA_CONS_MAP[ch];
        i++;
        if (chars[i] === HAL) {
          i++;
          if (chars[i] === ZWJ) i++;
          out += base;
          continue;
        }
        if (SINHALA_SIGN_MAP[chars[i]]) {
          out += base + SINHALA_SIGN_MAP[chars[i++]];
          continue;
        }
        out += base + "a";
        continue;
      }
      if (SINHALA_VOWEL_MAP[ch]) {
        out += SINHALA_VOWEL_MAP[ch];
        i++;
        continue;
      }
      if (ch === "ං") { out += "n"; i++; continue; }
      if (ch === "ඃ") { out += "h"; i++; continue; }
      if (ch === ZWJ || ch === HAL) { i++; continue; }
      out += ch;
      i++;
    }
    return out;
  }

  slugify(text, separator = "-") {
    return this.toSinglish(text)
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, separator)
      .replace(new RegExp(`^${separator}+|${separator}+$`, "g"), "");
  }
}

const STEM_SUFFIXES = [
  "වරුන්ගේ", "වරුන්ට", "වරුන්", "වලින්", "වලට", "වලදී", "වල",
  "යින්ගේ", "යින්ට", "යන්ගේ", "යන්ට", "ගෙන්", "යින්", "යන්",
  "ගේ", "ගෙ", "ට", "න්", "යි", "ත්", "ද", "ම", "ක්", "ක", "වේ", "ව", "ලා",
];

export class Stemmer {
  constructor(minStemGraphemes = 2) {
    this.tokenizer = new Tokenizer();
    this.minStemGraphemes = Math.max(1, minStemGraphemes);
  }

  stem(word) {
    const w = word.trim();
    if (!w || !SINHALA_RE.test(w)) return w;
    if (w.endsWith("ින්")) {
      const cand = w.slice(0, -"ින්".length);
      if (this.tokenizer.graphemes(cand).length >= this.minStemGraphemes) return cand;
    }
    for (const suf of STEM_SUFFIXES) {
      if (w.endsWith(suf)) {
        const cand = w.slice(0, -suf.length);
        if (this.tokenizer.graphemes(cand).length >= this.minStemGraphemes) return cand;
      }
    }
    return w;
  }

  stemText(text) {
    return this.tokenizer.tokenize(text).map((t) => this.stem(t)).join(" ");
  }
}

export class KeywordExtractor {
  constructor(stopwords = DEFAULT_STOPWORDS) {
    this.cleaner = new TextCleaner(stopwords);
    this.tokenizer = new Tokenizer();
    this.stemmer = new Stemmer();
  }

  extract(text, topK = 5, useStemming = false) {
    const tokens = this.tokenizer.tokenize(text, true);
    const counts = new Map();
    const scores = new Map();
    tokens.forEach((t, idx) => {
      if (this.cleaner.isStopword(t)) return;
      const key = useStemming ? this.stemmer.stem(t) : t;
      if (!key || this.cleaner.isStopword(key)) return;
      const w = 1 + 0.25 * (1 - idx / Math.max(1, tokens.length));
      counts.set(key, (counts.get(key) || 0) + 1);
      scores.set(key, (scores.get(key) || 0) + w);
    });
    if (!scores.size) return [];
    const maxScore = Math.max(...scores.values());
    return Array.from(scores.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, topK)
      .map(([keyword, score]) => ({
        keyword,
        score: Number((score / maxScore).toFixed(3)),
        count: counts.get(keyword),
      }));
  }

  summarize(text, numSentences = 2) {
    const sentences = this.tokenizer.splitSentences(text, true);
    if (sentences.length <= numSentences) return sentences.join(" ");
    const weights = new Map(this.extract(text, 20).map((k) => [k.keyword, k.score]));
    const scored = sentences.map((s, idx) => {
      const toks = this.tokenizer.tokenize(s, true);
      const score = toks.reduce((acc, t) => acc + (weights.get(t) || 0), 0);
      return [idx, score / Math.max(1, Math.sqrt(toks.length))];
    });
    const topIdx = scored
      .sort((a, b) => b[1] - a[1])
      .slice(0, numSentences)
      .map(([idx]) => idx)
      .sort((a, b) => a - b);
    return topIdx.map((i) => sentences[i]).join(" ");
  }
}

const SI_DIGITS = "෦෧෨෩෪෫෬෭෮෯";
const CURRENCY_MULT = {
  "කෝටි": 1e7, "ලක්ෂ": 1e5, "ලක්ෂය": 1e5, "දහස": 1e3, "දාහ": 1e3,
};

export class Normalizer {
  sinhalaDigitsToAscii(text) {
    return text.replace(/[෦-෯]/g, (ch) => String(SI_DIGITS.indexOf(ch)));
  }

  asciiDigitsToSinhala(text) {
    return text.replace(/[0-9]/g, (d) => SI_DIGITS[Number(d)]);
  }

  extractCurrency(text) {
    const s = this.sinhalaDigitsToAscii(text);
    const re = /(?:රුපියල්|රු\.?|LKR|Rs\.?)\s*(?:(කෝටි|ලක්ෂය|ලක්ෂ|දහස|දාහ)\s*)?(\d[\d,]*(?:\.\d+)?)(?:\s*(කෝටි|ලක්ෂය|ලක්ෂ|දහස|දාහ))?/giu;
    const out = [];
    for (const m of s.matchAll(re)) {
      let amount = Number(m[2].replace(/,/g, ""));
      if (m[1] && CURRENCY_MULT[m[1]]) amount *= CURRENCY_MULT[m[1]];
      else if (m[3] && CURRENCY_MULT[m[3]]) amount *= CURRENCY_MULT[m[3]];
      out.push({ raw: m[0].trim(), amount, currency: "LKR" });
    }
    return out;
  }

  normalizeText(text) {
    return this.sinhalaDigitsToAscii(text)
      .replace(/(?:රුපියල්|රු\.?|Rs\.?)\s*(?=\d)/giu, "LKR ")
      .replace(/\s+/g, " ")
      .trim();
  }
}

export class Chunker {
  constructor() {
    this.tokenizer = new Tokenizer();
  }

  chunk(text, maxChars = 500) {
    const trimmed = text.trim();
    if (!trimmed || maxChars <= 0) return [];
    const sentences = this.tokenizer.splitSentences(trimmed, true);
    const units = sentences.length ? sentences : [trimmed];
    const chunks = [];
    let current = "";
    for (const u of units) {
      if (!current) {
        current = u;
      } else if (`${current} ${u}`.length <= maxChars) {
        current = `${current} ${u}`;
      } else {
        chunks.push(current);
        current = u;
      }
    }
    if (current) chunks.push(current);
    return chunks;
  }

  estimateTokens(text) {
    if (!text.trim()) return 0;
    const si = (text.match(/[\u0D80-\u0DFF]/g) || []).length;
    const other = Math.max(0, text.length - si);
    return Math.max(1, Math.ceil(si * 1.5 + other * 0.25));
  }
}
