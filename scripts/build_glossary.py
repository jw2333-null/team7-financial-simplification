"""
build_glossary.py — Extract unique financial jargon terms from dataset.csv
and create a glossary template for manual annotation.

Logic:
  - Reads jargon_terms column (comma-separated values per row)
  - Deduplicates and counts frequency across all snippets
  - Keeps top 40 most frequent terms (or all if fewer than 30)
  - Writes data/glossary/glossary.csv with empty fields for manual completion

Usage:
    python scripts/build_glossary.py

Input:  data/final/dataset.csv
Output: data/glossary/glossary.csv
"""

import os
import pandas as pd
from collections import Counter

INPUT_FILE  = 'data/final/dataset.csv'
OUTPUT_FILE = 'data/glossary/glossary.csv'
MAX_TERMS   = 40
MIN_TERMS   = 30  # Keep all if fewer than this


def main():
    # ------------------------------------------------------------------ #
    # 1. Load dataset                                                      #
    # ------------------------------------------------------------------ #
    if not os.path.exists(INPUT_FILE):
        print(f"Error: '{INPUT_FILE}' not found. Run sample.py first.")
        return

    df = pd.read_csv(INPUT_FILE)
    print(f"Loaded {len(df)} rows from {INPUT_FILE}")

    # ------------------------------------------------------------------ #
    # 2. Extract all jargon terms with source and frequency               #
    # ------------------------------------------------------------------ #
    term_counts = Counter()
    # Keep first-seen source for each term
    term_source = {}

    for _, row in df.iterrows():
        val = row.get('jargon_terms', '')
        if pd.isna(val) or str(val).strip() == '':
            continue

        # Normalise source_file path separator then take the top-level folder
        source = (
            str(row['source_file'])
            .replace('\\', '/')
            .split('/')[0]
        )

        for term in str(val).split(','):
            term = term.strip()
            if not term:
                continue
            term_counts[term] += 1
            if term not in term_source:
                term_source[term] = source

    total_unique = len(term_counts)
    print(f"\nUnique jargon terms found: {total_unique}")
    print("\nFull list of unique terms:")
    for term in sorted(term_counts.keys()):
        print(f"  [{term_counts[term]:2d}x]  {term}")

    # ------------------------------------------------------------------ #
    # 3. Select terms to include in glossary                              #
    # ------------------------------------------------------------------ #
    if total_unique <= MIN_TERMS:
        # Keep all terms
        selected = list(term_counts.keys())
        print(f"\nFewer than {MIN_TERMS} terms found — keeping all {total_unique}.")
    else:
        # Keep the MAX_TERMS most frequent
        selected = [term for term, _ in term_counts.most_common(MAX_TERMS)]
        print(f"\nMore than {MAX_TERMS} terms found — keeping top {MAX_TERMS} by frequency.")

    # Sort alphabetically for readability
    selected.sort(key=str.lower)

    # ------------------------------------------------------------------ #
    # 4. Build glossary dataframe                                          #
    # ------------------------------------------------------------------ #
    rows = []
    for term in selected:
        rows.append({
            'jargon_term':              term,
            'plain_english_equivalent': '',
            'definition':               '',
            'source':                   term_source[term],
        })

    glossary = pd.DataFrame(rows, columns=[
        'jargon_term',
        'plain_english_equivalent',
        'definition',
        'source',
    ])

    # ------------------------------------------------------------------ #
    # 5. Write output                                                      #
    # ------------------------------------------------------------------ #
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    glossary.to_csv(OUTPUT_FILE, index=False)

    # ------------------------------------------------------------------ #
    # 6. Summary                                                           #
    # ------------------------------------------------------------------ #
    print(f"\n=== Glossary Summary ===")
    print(f"Total unique terms extracted : {total_unique}")
    print(f"Terms saved to glossary      : {len(glossary)}")
    print(f"Output file                  : {OUTPUT_FILE}")
    print("\nTerms by source:")
    print(glossary['source'].value_counts().to_string())


if __name__ == '__main__':
    main()
