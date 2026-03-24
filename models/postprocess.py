"""
postprocess.py — Add number preservation and modality shift flags to all outputs.

Usage:
    python models/postprocess.py

Input:  data/final/dataset.csv (with output columns)
Output: Updates dataset.csv with flag columns per system
"""

import pandas as pd
import re

DATASET = "data/final/dataset.csv"
SYSTEMS = ["output_control", "output_glossary", "output_generic", "output_financial"]

def extract_numbers(text):
    return set(re.findall(r'\b\d+[\.,]?\d*%?\b', str(text)))

def extract_modals(text):
    return [m.lower() for m in re.findall(r'\b(may|might|could|must|shall|should|will)\b', str(text), re.I)]

def modal_category(modal):
    if modal in ("must", "shall", "will"): return "strong"
    if modal in ("should",): return "medium"
    if modal in ("may", "might", "could"): return "weak"
    return None

def main():
    df = pd.read_csv(DATASET)
    available = [s for s in SYSTEMS if s in df.columns]
    
    for system in available:
        num_flags = []
        mod_flags = []
        
        for _, row in df.iterrows():
            orig = str(row["text_original"])
            out = str(row[system])
            
            # Number preservation
            orig_nums = extract_numbers(orig)
            out_nums = extract_numbers(out)
            nums_ok = orig_nums.issubset(out_nums) if orig_nums else True
            num_flags.append(nums_ok)
            
            # Modality shift
            orig_cats = sorted([modal_category(m) for m in extract_modals(orig)])
            out_cats = sorted([modal_category(m) for m in extract_modals(out)])
            shifted = orig_cats != out_cats
            mod_flags.append(shifted)
        
        short_name = system.replace("output_", "")
        df[f"numbers_preserved_{short_name}"] = num_flags
        df[f"modality_shifted_{short_name}"] = mod_flags
    
    df.to_csv(DATASET, index=False)
    
    # Print summary
    print("Post-processing complete.\n")
    for system in available:
        short = system.replace("output_", "")
        num_rate = df[f"numbers_preserved_{short}"].mean() * 100
        mod_rate = df[f"modality_shifted_{short}"].mean() * 100
        print(f"  {system}:")
        print(f"    Number preservation: {num_rate:.1f}%")
        print(f"    Modality shift rate: {mod_rate:.1f}%")

if __name__ == "__main__":
    main()
