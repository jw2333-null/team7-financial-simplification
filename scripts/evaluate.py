"""
evaluate.py — Run all automatic metrics on model outputs.

Usage:
    python scripts/evaluate.py

Input:  data/final/dataset.csv (with output columns: output_control, output_glossary, output_generic, output_financial)
Output: results/evaluation_results.csv
        results/results_summary.csv
"""

import pandas as pd
import numpy as np
import textstat
from sentence_transformers import SentenceTransformer, util
from bert_score import score as bert_score
import re
import os

DATASET = "data/final/dataset.csv"
OUTPUT_DIR = "results"
SYSTEMS = ["output_control", "output_glossary", "output_generic", "output_financial"]

def compute_readability(text):
    return {
        "fkgl": round(textstat.flesch_kincaid_grade(text), 1),
        "flesch_re": round(textstat.flesch_reading_ease(text), 1),
    }

def compute_number_preservation(original, output):
    orig_nums = set(re.findall(r'\d+[\.,]?\d*%?', original))
    out_nums = set(re.findall(r'\d+[\.,]?\d*%?', output))
    if len(orig_nums) == 0:
        return True  # No numbers to preserve
    return orig_nums.issubset(out_nums)

def compute_modality_shift(original, output):
    strong = {"must", "shall", "will"}
    medium = {"should"}
    weak = {"may", "might", "could"}
    
    def get_category(word):
        w = word.lower()
        if w in strong: return "strong"
        if w in medium: return "medium"
        if w in weak: return "weak"
        return None
    
    orig_modals = re.findall(r'\b(may|might|could|must|shall|should|will)\b', original, re.I)
    out_modals = re.findall(r'\b(may|might|could|must|shall|should|will)\b', output, re.I)
    
    orig_cats = [get_category(m) for m in orig_modals]
    out_cats = [get_category(m) for m in out_modals]
    
    # Simple check: did the set of categories change?
    if sorted(orig_cats) != sorted(out_cats):
        return True
    return False

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df = pd.read_csv(DATASET)
    
    # Check which output columns exist
    available_systems = [s for s in SYSTEMS if s in df.columns]
    if not available_systems:
        print("No output columns found. Run the models first (Steps 7.1-7.4).")
        return
    
    # Load sentence transformer
    print("Loading sentence transformer...")
    st_model = SentenceTransformer("all-MiniLM-L6-v2")
    
    results = []
    
    for system in available_systems:
        print(f"\nEvaluating: {system}")
        
        for _, row in df.iterrows():
            original = str(row["text_original"])
            output = str(row[system])
            
            if not output or output == "nan" or output.strip() == "":
                continue
            
            # Readability
            orig_read = compute_readability(original)
            out_read = compute_readability(output)
            
            # Semantic similarity
            emb_orig = st_model.encode(original, convert_to_tensor=True)
            emb_out = st_model.encode(output, convert_to_tensor=True)
            sem_sim = util.cos_sim(emb_orig, emb_out).item()
            
            # Domain-specific
            num_preserved = compute_number_preservation(original, output)
            modality_shifted = compute_modality_shift(original, output)
            
            results.append({
                "sample_id": row["sample_id"],
                "source_family": row["source_family"],
                "system": system,
                "fkgl_original": orig_read["fkgl"],
                "fkgl_output": out_read["fkgl"],
                "fkgl_drop": orig_read["fkgl"] - out_read["fkgl"],
                "flesch_re_original": orig_read["flesch_re"],
                "flesch_re_output": out_read["flesch_re"],
                "semantic_similarity": round(sem_sim, 3),
                "number_preserved": num_preserved,
                "modality_shifted": modality_shifted,
            })
    
    results_df = pd.DataFrame(results)
    results_df.to_csv(os.path.join(OUTPUT_DIR, "evaluation_results.csv"), index=False)
    
    # Summary per system
    summary = results_df.groupby("system").agg({
        "fkgl_drop": ["mean", "median", "std"],
        "semantic_similarity": ["mean", "median", "std"],
        "number_preserved": "mean",
        "modality_shifted": "mean",
    }).round(3)
    
    summary.to_csv(os.path.join(OUTPUT_DIR, "results_summary.csv"))
    print(f"\n{'='*60}")
    print("RESULTS SUMMARY")
    print(f"{'='*60}")
    print(summary.to_string())
    print(f"\nFull results: {OUTPUT_DIR}/evaluation_results.csv")

if __name__ == "__main__":
    main()
