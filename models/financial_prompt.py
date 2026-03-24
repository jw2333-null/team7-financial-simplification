"""
generic_prompt.py — Generic simplification baseline using FLAN-T5.
financial_prompt.py uses the same structure but with a domain-specific prompt.

Usage:
    python models/generic_prompt.py           # generic baseline
    python models/financial_prompt.py         # main system

Tip: Run on Google Colab with GPU for faster inference.
"""

import pandas as pd
from transformers import pipeline
import sys
import os

DATASET = "data/final/dataset.csv"
MODEL_NAME = "google/flan-t5-base"  # Change to flan-t5-large if compute allows

# Detect which script is running
script_name = os.path.basename(sys.argv[0]) if sys.argv else "generic_prompt.py"
is_financial = "financial" in script_name

if is_financial:
    PROMPT_TEMPLATE = (
        "Simplify this financial text for a consumer who is not a financial expert. "
        "Preserve all numbers, percentages, conditions, and warnings exactly. "
        "Replace jargon with plain English: {text}"
    )
    OUTPUT_COL = "output_financial"
    LABEL = "Financial prompt (main system)"
else:
    PROMPT_TEMPLATE = "Simplify this sentence for a general audience: {text}"
    OUTPUT_COL = "output_generic"
    LABEL = "Generic prompt (baseline)"

def main():
    print(f"Running: {LABEL}")
    print(f"Model: {MODEL_NAME}")
    print(f"Loading model...")
    
    simplifier = pipeline(
        "text2text-generation",
        model=MODEL_NAME,
        max_length=256,
        do_sample=False,
    )
    
    df = pd.read_csv(DATASET)
    outputs = []
    
    for i, row in df.iterrows():
        text = str(row["text_original"])
        prompt = PROMPT_TEMPLATE.format(text=text)
        result = simplifier(prompt)[0]["generated_text"]
        outputs.append(result)
        
        if (i + 1) % 10 == 0:
            print(f"  Processed {i+1}/{len(df)} snippets...")
    
    df[OUTPUT_COL] = outputs
    
    # Also add control baseline if not present
    if "output_control" not in df.columns:
        df["output_control"] = df["text_original"]
    
    df.to_csv(DATASET, index=False)
    print(f"\n{LABEL} complete. Results saved to '{OUTPUT_COL}' column in {DATASET}")

if __name__ == "__main__":
    main()
