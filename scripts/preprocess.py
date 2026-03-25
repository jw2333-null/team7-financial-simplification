"""
preprocess.py — Financial-document preprocessing pipeline.

Reads all .txt files from a configurable input folder, segments them into
candidate snippets (1–2 consecutive sentences) using spaCy, computes
Flesch-Kincaid Grade Level with textstat, filters low-quality candidates,
and tags diversity features for downstream sampling.

Usage:
    python scripts/preprocess.py

Outputs:
    data/processed/all_candidates.csv
    data/processed/filtered_candidates.csv
"""

import os
import re
import hashlib
from pathlib import Path

import pandas as pd
import spacy
import textstat

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION — edit these paths / thresholds as needed
# ═══════════════════════════════════════════════════════════════════════════════

INPUT_DIR = "data/raw"
OUTPUT_DIR = "data/processed"

# ── Filtering thresholds ──
MIN_WORD_COUNT = 8            # snippets shorter than this are dropped
MAX_WORD_COUNT = 150          # snippets longer than this are dropped
MIN_FKGL = 6.0               # minimum Flesch-Kincaid Grade Level
SYMBOL_RATIO_LIMIT = 0.30    # drop if >30 % of characters are non-alphanumeric
NEAR_DUP_SIM_CHARS = 50      # prefix length used for near-duplicate hashing

# ── spaCy setup ──
NLP_MODEL = "en_core_web_sm"

# ═══════════════════════════════════════════════════════════════════════════════
# FINANCIAL KEYWORD / REGEX BANKS (used by diversity tagging)
# ═══════════════════════════════════════════════════════════════════════════════

_FINANCIAL_TERMS = re.compile(
    r"\b("
    r"capital|leverage|liquidity|solvency|asset[s]?|liabilit(?:y|ies)|"
    r"equit(?:y|ies)|bond[s]?|securit(?:y|ies)|derivative[s]?|"
    r"interest rate[s]?|credit|loan[s]?|debt|dividend[s]?|yield[s]?|"
    r"portfolio|hedge|collateral|amortis(?:e|ation)|depreciation|"
    r"underwriting|compliance|regulatory|fiduciary|maturity|"
    r"inflation|gdp|monetary|fiscal|default|insolvency|"
    r"return on (?:equity|assets|investment)|"
    r"net interest|tier [12]|risk[- ]?weight"
    r")\b",
    re.IGNORECASE,
)

_FORECAST_GUIDANCE = re.compile(
    r"\b("
    r"forecast|outlook|guidance|projection|expect(?:s|ed|ation)?|"
    r"anticipate[sd]?|forward[- ]looking|estimate[sd]?|predict(?:s|ed|ion)?|"
    r"target[s]?|plan(?:s|ned)?|pipeline|backlog"
    r")\b",
    re.IGNORECASE,
)

_PROFIT_MARGIN = re.compile(
    r"\b("
    r"profit|margin|earnings|ebitda|ebit|net income|"
    r"gross profit|operating profit|bottom line|"
    r"return|roe|roa|roi|eps"
    r")\b",
    re.IGNORECASE,
)

_COST_EXPENSE = re.compile(
    r"\b("
    r"cost[s]?|expense[s]?|expenditure|opex|capex|"
    r"write[- ]?(?:down|off)|impairment|provision[s]?|"
    r"overhead|charge[s]?"
    r")\b",
    re.IGNORECASE,
)

_CASH_BALANCE_SHEET = re.compile(
    r"\b("
    r"cash|balance sheet|working capital|cash flow|"
    r"free cash flow|fcf|receivable[s]?|payable[s]?|"
    r"inventory|goodwill|intangible[s]?|"
    r"total asset[s]?|total liabilit(?:y|ies)|"
    r"current (?:asset[s]?|liabilit(?:y|ies))|"
    r"retained earnings|shareholders.? equity"
    r")\b",
    re.IGNORECASE,
)

_CURRENCY_RE = re.compile(
    r"[$£€¥][\d,]+\.?\d*|"                     # symbol-prefixed
    r"\b\d[\d,]*\.?\d*\s?(?:USD|GBP|EUR|JPY|CHF|AUD|CAD)\b",  # code-suffixed
    re.IGNORECASE,
)

_PERCENTAGE_RE = re.compile(r"\d+\.?\d*\s?%|per\s?cent", re.IGNORECASE)

_DATE_TIME_RE = re.compile(
    r"\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b|"                         # dd/mm/yyyy
    r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*"
    r"[\s,]+\d{1,2}(?:[\s,]+\d{4})?\b|"                                # Month dd, yyyy
    r"\b\d{1,2}\s(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
    r"[a-z]*[\s,]*\d{4}\b|"                                            # dd Month yyyy
    r"\bQ[1-4]\s?\d{4}\b|"                                             # Q1 2024
    r"\b(?:FY|H[12])\s?\d{2,4}\b|"                                     # FY2024 / H1 2025
    r"\b\d{1,2}:\d{2}(?::\d{2})?\s?(?:AM|PM|am|pm)?\b",               # time
    re.IGNORECASE,
)

# ═══════════════════════════════════════════════════════════════════════════════
# BOILERPLATE / SPEAKER-LABEL PATTERNS (used by normalization)
# ═══════════════════════════════════════════════════════════════════════════════

_SPEAKER_LABEL_RE = re.compile(
    r"^[A-Z][A-Za-z .'\-]{1,40}:\s*",   # e.g.  "John Smith:"  "Operator:"
    re.MULTILINE,
)

_PAGE_NUMBER_RE = re.compile(
    r"(?m)^\s*[-–—]?\s*\d{1,4}\s*[-–—]?\s*$"   # lines that are just page numbers
)

_TIMESTAMP_RE = re.compile(
    r"(?m)^\s*\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM|am|pm)?\s*$"
)

_BOILERPLATE_LINE_RE = re.compile(
    r"(?i)"
    r"^\s*(?:"
    r"(?:good\s+)?(?:morning|afternoon|evening)\b.*|"
    r"thank\s+you\b.*|"
    r"thanks\s+(?:very\s+much|everyone|all)\b.*|"
    r"(?:ladies\s+and\s+gentlemen)\b.*|"
    r"(?:this\s+concludes?\b.*)|"
    r"(?:operator\s+instructions?\b.*)|"
    r"(?:please\s+(?:stand\s+by|hold|press)\b.*)|"
    r"(?:you\s+may\s+(?:now\s+)?disconnect\b.*)|"
    r"(?:copyright|©|all\s+rights\s+reserved)\b.*|"
    r"(?:forward[- ]looking\s+statement[s]?\s+disclaimer)\b.*"
    r")\s*$",
    re.MULTILINE,
)

# ═══════════════════════════════════════════════════════════════════════════════
# FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════


def load_spacy_model(model_name: str) -> spacy.language.Language:
    """Load a spaCy model, raising a clear error if not installed."""
    try:
        nlp = spacy.load(model_name, disable=["ner", "lemmatizer"])
    except OSError:
        raise SystemExit(
            f"spaCy model '{model_name}' not found. "
            f"Install it with:  python -m spacy download {model_name}"
        )
    nlp.max_length = 3_000_000
    return nlp


# ── File I/O ──────────────────────────────────────────────────────────────────


def collect_txt_files(input_dir: str) -> list[Path]:
    """Recursively collect all .txt files under *input_dir*."""
    root = Path(input_dir)
    if not root.is_dir():
        raise SystemExit(f"Input directory not found: {root.resolve()}")
    files = sorted(root.rglob("*.txt"))
    return files


def load_text(filepath: Path) -> str:
    """Read a text file with safe UTF-8 handling."""
    return filepath.read_text(encoding="utf-8", errors="replace")


# ── Text Normalisation ────────────────────────────────────────────────────────


def normalise_text(text: str) -> str:
    """Apply light cleaning to raw document text.

    Steps
    -----
    1. Strip speaker labels  (``Name:``)
    2. Strip page-number-only lines
    3. Strip timestamp-only lines
    4. Strip boilerplate / greeting / sign-off lines
    5. Collapse excessive whitespace and blank lines
    """
    text = _SPEAKER_LABEL_RE.sub("", text)
    text = _PAGE_NUMBER_RE.sub("", text)
    text = _TIMESTAMP_RE.sub("", text)
    text = _BOILERPLATE_LINE_RE.sub("", text)

    # Collapse runs of whitespace (tabs, multiple spaces)
    text = re.sub(r"[ \t]+", " ", text)
    # Collapse 3+ consecutive newlines into 2
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# ── Sentence Segmentation ────────────────────────────────────────────────────


def segment_sentences(nlp: spacy.language.Language, text: str) -> list[str]:
    """Use spaCy's sentence boundary detector to segment *text*.

    Returns a list of whitespace-normalised sentence strings.
    """
    doc = nlp(text)
    sentences = []
    for sent in doc.sents:
        cleaned = re.sub(r"\s+", " ", sent.text).strip()
        if cleaned:
            sentences.append(cleaned)
    return sentences


# ── Candidate Generation ─────────────────────────────────────────────────────


def generate_candidates(
    sentences: list[str],
    source_file: str,
) -> list[dict]:
    """Build candidate snippets from 1-sentence and 2-sentence windows.

    Each candidate is a dict with preliminary metadata.
    """
    candidates = []
    n = len(sentences)

    for i in range(n):
        # --- single-sentence candidate ---
        candidates.append({
            "source_file": source_file,
            "text": sentences[i],
            "sentence_count": 1,
        })

        # --- two-sentence candidate ---
        if i + 1 < n:
            combined = sentences[i] + " " + sentences[i + 1]
            candidates.append({
                "source_file": source_file,
                "text": combined,
                "sentence_count": 2,
            })

    return candidates


# ── Readability Scoring ───────────────────────────────────────────────────────


def compute_fkgl(text: str) -> float:
    """Return Flesch-Kincaid Grade Level, rounded to one decimal."""
    return round(textstat.flesch_kincaid_grade(text), 1)


# ── Diversity / Content Feature Tagging ───────────────────────────────────────


def tag_diversity_features(text: str) -> dict:
    """Return a dict of boolean / categorical diversity features."""
    return {
        "contains_number": bool(re.search(r"\d", text)),
        "contains_currency": bool(_CURRENCY_RE.search(text)),
        "contains_percentage": bool(_PERCENTAGE_RE.search(text)),
        "contains_date_or_time": bool(_DATE_TIME_RE.search(text)),
        "contains_financial_term": bool(_FINANCIAL_TERMS.search(text)),
        "contains_forecast_or_guidance": bool(_FORECAST_GUIDANCE.search(text)),
        "contains_profit_or_margin_term": bool(_PROFIT_MARGIN.search(text)),
        "contains_cost_or_expense_term": bool(_COST_EXPENSE.search(text)),
        "contains_cash_or_balance_sheet_term": bool(_CASH_BALANCE_SHEET.search(text)),
    }


# ── Filtering ─────────────────────────────────────────────────────────────────


def _word_count(text: str) -> int:
    return len(text.split())


def _symbol_ratio(text: str) -> float:
    """Fraction of characters that are not alphanumeric or whitespace."""
    if not text:
        return 1.0
    non_alnum = sum(1 for ch in text if not ch.isalnum() and not ch.isspace())
    return non_alnum / len(text)


def _near_dup_key(text: str) -> str:
    """Hash based on lowered, whitespace-collapsed prefix for near-dup detection."""
    normalised = re.sub(r"\s+", " ", text.lower().strip())[:NEAR_DUP_SIM_CHARS]
    return hashlib.md5(normalised.encode()).hexdigest()


def _is_boilerplate_snippet(text: str) -> bool:
    """Heuristic check for residual boilerplate that survived normalisation."""
    lower = text.lower()
    # Very short + generic phrases
    if _word_count(text) < 5:
        return True
    boilerplate_phrases = [
        "thank you", "good morning", "good afternoon", "good evening",
        "ladies and gentlemen", "operator", "please stand by",
        "you may disconnect", "this concludes",
    ]
    for phrase in boilerplate_phrases:
        if lower.startswith(phrase):
            return True
    return False


def filter_candidates(df: pd.DataFrame) -> pd.DataFrame:
    """Apply quality filters and return the cleaned DataFrame.

    Filters
    -------
    1. Word count within [MIN_WORD_COUNT, MAX_WORD_COUNT]
    2. FKGL >= MIN_FKGL  (non-trivial reading level)
    3. Symbol ratio <= SYMBOL_RATIO_LIMIT
    4. Not residual boilerplate
    5. No near-duplicates (keep first occurrence)
    """
    df = df.copy()

    # 1. word count bounds
    df = df[(df["word_count"] >= MIN_WORD_COUNT) & (df["word_count"] <= MAX_WORD_COUNT)]

    # 2. minimum readability complexity
    df = df[df["fkgl"] >= MIN_FKGL]

    # 3. symbol ratio
    df = df[df["text"].apply(_symbol_ratio) <= SYMBOL_RATIO_LIMIT]

    # 4. residual boilerplate
    df = df[~df["text"].apply(_is_boilerplate_snippet)]

    # 5. near-duplicate removal (keep first)
    df["_dup_key"] = df["text"].apply(_near_dup_key)
    df = df.drop_duplicates(subset="_dup_key", keep="first")
    df = df.drop(columns=["_dup_key"])

    return df.reset_index(drop=True)


# ── Output ────────────────────────────────────────────────────────────────────


def save_csv(df: pd.DataFrame, path: str) -> None:
    """Write a DataFrame to CSV, creating parent directories as needed."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN PIPELINE
# ═══════════════════════════════════════════════════════════════════════════════


def main() -> None:
    # ── Load resources ──
    print("Loading spaCy model …")
    nlp = load_spacy_model(NLP_MODEL)

    # ── Collect input files ──
    txt_files = collect_txt_files(INPUT_DIR)
    if not txt_files:
        print(f"No .txt files found under '{INPUT_DIR}'. Nothing to do.")
        return
    print(f"Found {len(txt_files)} .txt file(s) in '{INPUT_DIR}'.\n")

    # ── Process each file ──
    all_candidates: list[dict] = []

    for filepath in txt_files:
        relative_name = str(filepath.relative_to(INPUT_DIR))
        print(f"  Processing: {relative_name}")

        raw_text = load_text(filepath)
        if not raw_text.strip():
            print(f"    ⚠ Empty file — skipped.")
            continue

        clean_text = normalise_text(raw_text)
        sentences = segment_sentences(nlp, clean_text)
        candidates = generate_candidates(sentences, source_file=relative_name)
        all_candidates.extend(candidates)

    if not all_candidates:
        print("No candidates generated. Check that input files contain text.")
        return

    # ── Build DataFrame & enrich ──
    df = pd.DataFrame(all_candidates)

    # Assign unique candidate IDs
    df.insert(0, "candidate_id", [f"C{str(i+1).zfill(5)}" for i in range(len(df))])

    # Word count & readability
    df["word_count"] = df["text"].apply(_word_count)
    df["fkgl"] = df["text"].apply(compute_fkgl)

    # Diversity features
    feature_dicts = df["text"].apply(tag_diversity_features).tolist()
    feature_df = pd.DataFrame(feature_dicts)
    df = pd.concat([df, feature_df], axis=1)

    # ── Save all candidates ──
    all_path = os.path.join(OUTPUT_DIR, "all_candidates.csv")
    save_csv(df, all_path)

    # ── Filter & save ──
    df_filtered = filter_candidates(df)
    # Re-assign contiguous IDs after filtering
    df_filtered["candidate_id"] = [
        f"F{str(i+1).zfill(5)}" for i in range(len(df_filtered))
    ]
    filtered_path = os.path.join(OUTPUT_DIR, "filtered_candidates.csv")
    save_csv(df_filtered, filtered_path)

    # ── Console summary ──
    n_files = len(txt_files)
    n_all = len(df)
    n_filtered = len(df_filtered)
    avg_words = (
        round(df_filtered["word_count"].mean(), 1) if n_filtered > 0 else 0
    )

    print("\n" + "=" * 60)
    print("  PREPROCESSING SUMMARY")
    print("=" * 60)
    print(f"  Files processed          : {n_files}")
    print(f"  Total candidates         : {n_all}")
    print(f"  Filtered candidates      : {n_filtered}")
    print(f"  Avg words (filtered)     : {avg_words}")
    print("=" * 60)
    print(f"\n  Saved → {all_path}")
    print(f"  Saved → {filtered_path}")


if __name__ == "__main__":
    main()
