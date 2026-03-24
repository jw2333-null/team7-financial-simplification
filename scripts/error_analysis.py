"""
error_analysis.py — Template for categorising and cross-tabulating errors.

Usage:
    python scripts/error_analysis.py

This script loads the human evaluation results and helps structure the error analysis.
The actual error categorisation is done manually — this script provides the framework.
"""

import pandas as pd
import os

DATASET = "data/final/dataset.csv"
EVAL_RESULTS = "results/evaluation_results.csv"
ERROR_FILE = "results/error_analysis.csv"

ERROR_TYPES = [
    "number_changed",       # A number was altered, rounded, or removed
    "condition_dropped",    # An if/unless/when clause was removed
    "warning_weakened",     # A risk warning was softened or removed
    "modality_shifted",     # may→will, must→should, etc.
    "jargon_retained",      # A jargon term was kept unchanged
    "meaning_fabricated",   # The output added information not in the original
    "other",                # Other error not in the above categories
]

def create_template():
    """Create an empty error analysis template for manual filling."""
    print("Creating error analysis template...")
    print(f"Error types to use: {', '.join(ERROR_TYPES)}")
    print()
    
    template = pd.DataFrame(columns=[
        "sample_id", "system", "error_type", "error_description",
        "original_text", "output_text"
    ])
    
    template.to_csv(ERROR_FILE, index=False)
    print(f"Empty template saved to {ERROR_FILE}")
    print("Fill this in manually for each output that scored < 4 on human correctness.")

def cross_tabulate():
    """Cross-tabulate errors with diversity tags."""
    if not os.path.exists(ERROR_FILE):
        print(f"{ERROR_FILE} not found. Run create_template() first and fill it in.")
        return
    
    errors = pd.read_csv(ERROR_FILE)
    if len(errors) == 0:
        print("Error file is empty. Fill it in first.")
        return
    
    dataset = pd.read_csv(DATASET)
    
    # Merge errors with diversity tags
    merged = errors.merge(
        dataset[["sample_id", "source_family", "has_number", "has_condition",
                 "has_warning", "has_negation_or_modality", "complex_syntax"]],
        on="sample_id", how="left"
    )
    
    print("\nError counts by type:")
    print(merged["error_type"].value_counts().to_string())
    
    print("\nError counts by system:")
    print(merged.groupby("system")["error_type"].value_counts().to_string())
    
    print("\nErrors by source family:")
    print(merged.groupby("source_family")["error_type"].value_counts().to_string())
    
    # Cross-tabulate with diversity tags
    tags = ["has_number", "has_condition", "has_warning", "has_negation_or_modality", "complex_syntax"]
    print("\nError rates by diversity tag:")
    for tag in tags:
        with_tag = merged[merged[tag] == True]
        without_tag = merged[merged[tag] == False]
        print(f"\n  {tag}:")
        print(f"    Snippets WITH tag:    {len(with_tag)} errors")
        print(f"    Snippets WITHOUT tag: {len(without_tag)} errors")
    
    # Save cross-tabulation
    cross_tab = merged.groupby(["system", "error_type"]).size().unstack(fill_value=0)
    cross_tab.to_csv("results/error_cross_tabulation.csv")
    print(f"\nCross-tabulation saved to results/error_cross_tabulation.csv")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "analyse":
        cross_tabulate()
    else:
        create_template()
        print("\nAfter filling in errors, run: python scripts/error_analysis.py analyse")
