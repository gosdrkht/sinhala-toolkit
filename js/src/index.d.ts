export interface CleanOptions {
  removeStopwords?: boolean;
  removePunctuation?: boolean;
  removeEnglish?: boolean;
  removeNumbers?: boolean;
  keepZwj?: boolean;
}

export type ScriptType = "sinhala" | "tamil" | "english" | "mixed" | "unknown";
export type TokenType = "sinhala" | "english" | "number" | "punctuation" | "mixed" | "unknown";

export class TextCleaner {
  constructor(stopwords?: string[]);
  clean(text: string, options?: CleanOptions): string;
  normaliseUnicode(text: string): string;
  removeInvisibleChars(text: string, keepZwj?: boolean): string;
  normaliseWhitespace(text: string): string;
  removePunctuation(text: string, keepDanda?: boolean): string;
  removeEnglish(text: string): string;
  removeNumbers(text: string): string;
  removeStopwords(text: string): string;
  containsSinhala(text: string): boolean;
  containsTamil(text: string): boolean;
  isPureSinhala(text: string): boolean;
  detectScript(text: string): ScriptType;
  isStopword(word: string): boolean;
}

export class Tokenizer {
  splitSentences(text: string, keepBoundary?: boolean): string[];
  tokenize(text: string, lowercase?: boolean): string[];
  graphemes(text: string): string[];
  classifyToken(token: string): TokenType;
}

export interface SentimentResult {
  label: "positive" | "negative" | "neutral";
  score: number;
  positive: number;
  negative: number;
  tokens: string[];
}

export class SentimentAnalyser {
  constructor(positiveWords?: string[] | null, negativeWords?: string[] | null);
  analyse(text: string): SentimentResult;
}

export interface ProfanityMatch {
  word: string;
  severity: string;
}

export class ProfanityFilter {
  constructor(wordSeverities?: Record<string, string>);
  findMatches(text: string, severities?: string[] | null): ProfanityMatch[];
  containsProfanity(text: string, severities?: string[] | null): boolean;
  censor(text: string, replacement?: string, severities?: string[] | null): string;
  highestSeverity(text: string): string | null;
}

export class Transliterator {
  toSinhala(text: string): string;
  toSinglish(text: string): string;
  slugify(text: string, separator?: string): string;
}

export class Stemmer {
  constructor(minStemGraphemes?: number);
  stem(word: string): string;
  stemText(text: string): string;
}

export interface KeywordItem {
  keyword: string;
  score: number;
  count: number;
}

export class KeywordExtractor {
  constructor(stopwords?: string[]);
  extract(text: string, topK?: number, useStemming?: boolean): KeywordItem[];
  summarize(text: string, numSentences?: number): string;
}

export interface CurrencyMatch {
  raw: string;
  amount: number;
  currency: string;
}

export class Normalizer {
  sinhalaDigitsToAscii(text: string): string;
  asciiDigitsToSinhala(text: string): string;
  extractCurrency(text: string): CurrencyMatch[];
  normalizeText(text: string): string;
}

export class Chunker {
  chunk(text: string, maxChars?: number): string[];
  estimateTokens(text: string): number;
}
