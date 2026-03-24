"""
preprocess.py — Extract text from .txt files, segment sentences, compute readability, filter, tag.

Usage:
    python scripts/preprocess.py

Input:  data/raw/**/*.txt
Output: data/processed/all_candidates.csv
        data/processed/filtered_candidates.csv
"""

import os
import re
import csv
import spacy
import textstat
import pandas as pd

# ──── Config ────
RAW_DIR = "data/raw"
OUTPUT_DIR = "data/processed"
FKGL_THRESHOLD = 10
MIN_WORD_COUNT = 10

# ──── Load spaCy ────
nlp = spacy.load("en_core_web_sm")
nlp.max_length = 2_000_000

def get_source_family(filepath):
    if "financial_institution" in filepath:
        return "financial_institution"
    elif "regulatory_guidance" in filepath:
        return "regulatory_guidance"
    return "unknown"

def get_source_name(filename):
    """Extract a readable source name from the filename."""
    name = filename.replace(".txt", "").replace("_", " ").title()
    return name

def is_boilerplate(text):
    """Filter out headers, footers, copyright notices, etc."""
    patterns = [
        r'^\d+\s*$',                          # Page numbers
        r'^(contents|page \d|section \d)',      # TOC entries
        r'registered (in|office)',              # Legal boilerplate
        r'(prudential regulation|financial conduct) authority',
        r'copyright|©',
        r'^\s*$',                              # Empty
    ]
    for p in patterns:
        if re.search(p, text, re.I):
            return True
    return len(text.strip()) < 20
    
def tag_features(text):
    """Compute diversity tags."""
    wc = len(re.findall(r"[a-zA-Z']+", text))
    return {
        "word_count": wc,
        "has_number": bool(re.search(r'\d+[\.,]?\d*%?', text)),
        "has_condition": bool(re.search(r'\b(if|unless|provided that|subject to|where|when)\b', text, re.I)),
        "has_warning": bool(re.search(r'\b(may lose|risk|warning|caution|not guaranteed|could lose|at risk|be aware|important|must not)\b', text, re.I)),
        "has_negation_or_modality": bool(re.search(r"\b(not|never|no|n't|may|might|could|must|shall|should|will)\b", text, re.I)),
        "complex_syntax": wc > 30 or text.count(',') >= 3 or ';' in text,
    }

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    all_rows = []
    
    # Walk through all .txt files
    for root, dirs, files in os.walk(RAW_DIR):
        for fname in sorted(files):
            if not fname.endswith(".txt"):
                continue
            
            filepath = os.path.join(root, fname)
            source_family = get_source_family(filepath)
            source_name = get_source_name(fname)
            
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                text = f.read()
            
            # Sentence segmentation
            doc = nlp(text)
            for i, sent in enumerate(doc.sents):
                sent_text = sent.text.strip()
                sent_text = re.sub(r'\s+', ' ', sent_text)  # normalise whitespace
                
                if is_boilerplate(sent_text):
                    continue
                
                tags = tag_features(sent_text)
                
                row = {
                    "source_family": source_family,
                    "source_name": source_name,
                    "document_title": fname.replace(".txt", ""),
                    "snippet_id": f"sent_{i+1}",
                    "sentence_text": sent_text,
                    "word_count": tags["word_count"],
                    "fkgl": round(textstat.flesch_kincaid_grade(sent_text), 1),
                    "flesch_re": round(textstat.flesch_reading_ease(sent_text), 1),
                    "has_number": tags["has_number"],
                    "has_condition": tags["has_condition"],
                    "has_warning": tags["has_warning"],
                    "has_negation_or_modality": tags["has_negation_or_modality"],
                    "complex_syntax": tags["complex_syntax"],
                }
                all_rows.append(row)
    
    # Save all candidates
    df_all = pd.DataFrame(all_rows)
    df_all.to_csv(os.path.join(OUTPUT_DIR, "all_candidates.csv"), index=False)
    print(f"All candidates: {len(df_all)} sentences from {df_all['document_title'].nunique()} documents")
    
    # Filter
    df_filtered = df_all[
        (df_all["fkgl"] >= FKGL_THRESHOLD) &
        (df_all["word_count"] >= MIN_WORD_COUNT)
    ].copy()
    
    df_filtered.to_csv(os.path.join(OUTPUT_DIR, "filtered_candidates.csv"), index=False)
    print(f"Filtered candidates: {len(df_filtered)} sentences")
    print(f"  Source A (financial_institution): {len(df_filtered[df_filtered['source_family']=='financial_institution'])}")
    print(f"  Source B (regulatory_guidance):   {len(df_filtered[df_filtered['source_family']=='regulatory_guidance'])}")
    print(f"  has_number: {df_filtered['has_number'].sum()}")
    print(f"  has_condition: {df_filtered['has_condition'].sum()}")
    print(f"  has_warning: {df_filtered['has_warning'].sum()}")
    print(f"  has_negation_or_modality: {df_filtered['has_negation_or_modality'].sum()}")
    print(f"  complex_syntax: {df_filtered['complex_syntax'].sum()}")

if __name__ == "__main__":
    main()
