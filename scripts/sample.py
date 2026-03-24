"""
sample.py — Stratified sampling from filtered candidates to build the final dataset.

Usage:
    python scripts/sample.py

Input:  data/processed/filtered_candidates.csv
Output: data/final/dataset.csv
"""

import pandas as pd
import os

INPUT = "data/processed/filtered_candidates.csv"
OUTPUT = "data/final/dataset.csv"
TARGET_TOTAL = 95          # Aim for 80-100
TARGET_PER_FAMILY = 47     # Roughly balanced
MAX_PER_DOC = 15           # No single document dominates

def main():
    df = pd.read_csv(INPUT)
    
    sampled = []
    
    for family in ["financial_institution", "regulatory_guidance"]:
        pool = df[df["source_family"] == family].copy()
        
        # Ensure no document contributes more than MAX_PER_DOC
        doc_counts = pool.groupby("document_title").size()
        
        family_sample = []
        for doc_title, group in pool.groupby("document_title"):
            n = min(len(group), MAX_PER_DOC)
            # Prioritise diverse snippets
            group = group.sort_values(
                by=["has_number", "has_condition", "has_warning", "complex_syntax"],
                ascending=False
            )
            family_sample.append(group.head(n))
        
        family_df = pd.concat(family_sample)
        
        # If we have more than target, sample down
        if len(family_df) > TARGET_PER_FAMILY:
            family_df = family_df.sample(n=TARGET_PER_FAMILY, random_state=42)
        
        sampled.append(family_df)
    
    result = pd.concat(sampled).reset_index(drop=True)
    
    # Assign sample IDs
    fin_count = 0
    reg_count = 0
    ids = []
    for _, row in result.iterrows():
        if row["source_family"] == "financial_institution":
            fin_count += 1
            ids.append(f"FIN_{fin_count:03d}")
        else:
            reg_count += 1
            ids.append(f"REG_{reg_count:03d}")
    
    result.insert(0, "sample_id", ids)
    
    # Add empty columns for annotation
    result["unit_type"] = "sentence"
    result["text_original"] = result["sentence_text"]
    result["text_simplified_reference"] = ""
    result["jargon_terms"] = ""
    result["fkgl_original"] = result["fkgl"]
    result["fkgl_simplified"] = ""
    result["word_count_original"] = result["word_count"]
    result["word_count_simplified"] = ""
    result["annotator_id"] = ""
    result["second_annotator_id"] = ""
    result["confidence"] = ""
    result["rejected"] = "FALSE"
    result["rejection_reason"] = ""
    result["notes"] = ""
    
    # Select final columns in schema order
    final_cols = [
        "sample_id", "source_family", "source_name", "document_title",
        "snippet_id", "unit_type", "text_original", "text_simplified_reference",
        "jargon_terms", "has_number", "has_condition", "has_warning",
        "has_negation_or_modality", "complex_syntax",
        "fkgl_original", "fkgl_simplified",
        "word_count_original", "word_count_simplified",
        "annotator_id", "second_annotator_id",
        "confidence", "rejected", "rejection_reason", "notes"
    ]
    
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    result[final_cols].to_csv(OUTPUT, index=False)
    
    print(f"Dataset created: {len(result)} snippets")
    print(f"  FIN: {fin_count}, REG: {reg_count}")
    print(f"  Diversity tag coverage:")
    for tag in ["has_number", "has_condition", "has_warning", "has_negation_or_modality", "complex_syntax"]:
        pct = result[tag].sum() / len(result) * 100
        print(f"    {tag}: {result[tag].sum()} ({pct:.0f}%)")
    print(f"Saved to {OUTPUT}")

if __name__ == "__main__":
    main()
