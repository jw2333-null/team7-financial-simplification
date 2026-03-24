"""
glossary_baseline.py — Lexical replacement baseline using glossary.csv.

Usage:
    python models/glossary_baseline.py

Input:  data/final/dataset.csv, data/glossary/glossary.csv
Output: Adds 'output_glossary' column to dataset.csv
"""

import pandas as pd
import re

DATASET = "data/final/dataset.csv"
GLOSSARY = "data/glossary/glossary.csv"

def main():
    df = pd.read_csv(DATASET)
    glossary = pd.read_csv(GLOSSARY)
    
    # Sort by term length (longest first) to avoid partial matches
    glossary = glossary.sort_values(by="term", key=lambda x: x.str.len(), ascending=False)
    
    outputs = []
    for _, row in df.iterrows():
        text = str(row["text_original"])
        for _, g in glossary.iterrows():
            term = str(g["term"])
            replacement = str(g["plain_english_equivalent"])
            # Case-insensitive whole-word replacement
            pattern = r'\b' + re.escape(term) + r'\b'
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        outputs.append(text)
    
    df["output_glossary"] = outputs
    df.to_csv(DATASET, index=False)
    
    # Count how many snippets were changed
    changed = sum(1 for o, r in zip(df["text_original"], outputs) if str(o) != str(r))
    print(f"Glossary baseline complete. {changed}/{len(df)} snippets modified.")

if __name__ == "__main__":
    main()
