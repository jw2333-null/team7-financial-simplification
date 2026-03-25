"""
sample.py — Randomly sample snippets from filtered_candidates.csv for annotation.

Sources:
  Source A: financial_institution/ (Bank of Scotland, HSBC, Barclaycard, Nationwide)
  Source B: regulatory_guidance/   (FCA, SEC, CFPB)

Targets:
  ~50 from Source A, ~45 from Source B
  Max 15 snippets per individual document
  Total: 80-100 snippets, random seed 42

Usage:
    python scripts/sample.py

Input:  data/processed/filtered_candidates.csv
Output: data/final/dataset.csv
"""

import os
import pandas as pd

INPUT_FILE  = 'data/processed/filtered_candidates.csv'
OUTPUT_FILE = 'data/final/dataset.csv'
RANDOM_SEED = 42

TARGET_SOURCE_A = 50
TARGET_SOURCE_B = 45
MAX_PER_DOC     = 15

# Empty columns added ready for annotation
ANNOTATION_COLS = [
    'text_simplified_reference',
    'annotator_id',
    'confidence',
    'notes',
    'jargon_terms',
]


def sample_with_cap(df, target, max_per_doc):
    """
    Sample up to `target` rows from df,
    with at most `max_per_doc` rows per source document.
    """
    # Extract doc filename from source_file (handles both / and \ separators)
    doc_names = df['source_file'].str.replace('\\', '/', regex=False).str.split('/').str[-1]

    capped = (
        df.assign(_doc=doc_names)
          .groupby('_doc', group_keys=False)
          .apply(lambda g: g.sample(n=min(len(g), max_per_doc), random_state=RANDOM_SEED),
                 include_groups=False)
          .reset_index(drop=True)
    )

    if len(capped) > target:
        capped = capped.sample(n=target, random_state=RANDOM_SEED)

    return capped


def main():
    # ------------------------------------------------------------------ #
    # 1. Load and inspect input                                            #
    # ------------------------------------------------------------------ #
    if not os.path.exists(INPUT_FILE):
        print(f"Error: '{INPUT_FILE}' not found. "
              "Run preprocess.py first to generate filtered candidates.")
        return

    df = pd.read_csv(INPUT_FILE)

    print(f"Loaded {len(df)} rows from {INPUT_FILE}")
    print(f"\nColumn names:\n  {list(df.columns)}\n")
    print("First 3 rows:")
    print(df.head(3).to_string())
    print()

    # ------------------------------------------------------------------ #
    # 2. Split into Source A and Source B by source_file prefix           #
    # ------------------------------------------------------------------ #
    # Normalise separators for reliable prefix matching
    normalised = df['source_file'].str.replace('\\', '/', regex=False)

    source_a = df[normalised.str.startswith('financial_institution/')].copy()
    source_b = df[normalised.str.startswith('regulatory_guidance/')].copy()

    print(f"Source A candidates (financial_institution): {len(source_a)}")
    print(f"Source B candidates (regulatory_guidance):   {len(source_b)}\n")

    # ------------------------------------------------------------------ #
    # 3. Sample                                                            #
    # ------------------------------------------------------------------ #
    sampled_a = sample_with_cap(source_a, TARGET_SOURCE_A, MAX_PER_DOC)
    sampled_b = sample_with_cap(source_b, TARGET_SOURCE_B, MAX_PER_DOC)

    result = (
        pd.concat([sampled_a, sampled_b])
          .sample(frac=1, random_state=RANDOM_SEED)   # shuffle final order
          .reset_index(drop=True)
    )

    # ------------------------------------------------------------------ #
    # 4. Add empty annotation columns                                      #
    # ------------------------------------------------------------------ #
    for col in ANNOTATION_COLS:
        result[col] = ''

    # ------------------------------------------------------------------ #
    # 5. Write output                                                      #
    # ------------------------------------------------------------------ #
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    result.to_csv(OUTPUT_FILE, index=False)

    # ------------------------------------------------------------------ #
    # 6. Summary                                                           #
    # ------------------------------------------------------------------ #
    doc_col = result['source_file'].str.replace('\\', '/', regex=False).str.split('/').str[-1]

    print("=== Sampling Summary ===")
    print(f"Total rows sampled : {len(result)}")
    print(f"  Source A (financial_institution) : {len(sampled_a)}")
    print(f"  Source B (regulatory_guidance)   : {len(sampled_b)}")
    print()
    print("Per document:")
    for doc, count in doc_col.value_counts().sort_index().items():
        print(f"  {doc}: {count}")
    print(f"\nOutput written to: {OUTPUT_FILE}")


if __name__ == '__main__':
    main()
