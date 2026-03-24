# Automatic Simplification of Financial Jargon in Consumer-Facing Documents

**MSIN0221 Natural Language Processing — Group Assignment**  
**Team 7 | UCL School of Management | 2025/26 Term 2**

## Research Question

> To what extent can pretrained NLP models simplify consumer-facing financial jargon while preserving the original meaning and key financial content?

## What This Project Does

This project builds a text simplification system for consumer-facing financial documents (credit card agreements, loan terms, mortgage conditions, regulatory guidance). It takes jargon-heavy financial sentences as input and produces clearer, simpler versions as output while preserving all numbers, conditions, warnings, and obligations exactly.

## Team Members

| Name | Student ID | Primary Responsibility |
|------|-----------|----------------------|
| Gianni Chen | 25057622 | |
| Hanley Ho | 25120620 | |
| Stephen Leung | 25084380 | |
| Wing Nok Poon | 24158473 | |
| Zhengpeng Wang | 25115696 | |

## Repository Structure

```
team7-financial-simplification/
├── data/
│   ├── raw/                        # Extracted .txt files from source PDFs
│   │   ├── financial_institution/  # Bank/building society T&Cs
│   │   └── regulatory_guidance/    # FCA, SEC, CFPB documents
│   ├── processed/                  # all_candidates.csv, filtered_candidates.csv
│   ├── final/                      # dataset.csv, dataset.json (frozen v1.0)
│   ├── glossary/                   # glossary.csv (30-40 jargon terms)
│   └── gold/                       # Double-annotated gold-standard subset
├── scripts/                        # Preprocessing, sampling, evaluation scripts
│   ├── preprocess.py               # Text extraction → sentence segmentation → filtering
│   ├── sample.py                   # Stratified sampling → dataset.csv
│   ├── evaluate.py                 # All automatic metrics (FKGL, similarity, SARI, etc.)
│   └── error_analysis.py           # Failure categorisation and cross-tabulation
├── models/                         # Prompting and baseline code
│   ├── glossary_baseline.py        # Lexical replacement using glossary.csv
│   ├── generic_prompt.py           # FLAN-T5 with generic simplification prompt
│   ├── financial_prompt.py         # FLAN-T5 with domain-specific prompt (main system)
│   └── postprocess.py              # Number preservation + modality shift checks
├── results/                        # Evaluation outputs, tables, charts
├── docs/                           # Annotation guidelines, data collection log
│   ├── annotation_guidelines.md    # Rules for manual simplification
│   └── data_collection_log.md      # Source URLs, access dates, issues
├── report/                         # Final report (LaTeX/Jupyter)
├── presentation/                   # Slides and MP4 recording
└── README.md
```

## Setup

### Requirements

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### Data Collection

The source PDFs are **not** stored in this repository (they are too large for Git). To reproduce the dataset:

1. Open each URL listed in `docs/data_collection_log.md` in a browser
2. Save each PDF to the appropriate folder under `data/raw/`
3. Extract text using one of:
   - `pdftotext file.pdf file.txt`
   - The PyPDF2 script in `scripts/preprocess.py`
   - Manual copy-paste from the PDF

### Reproducing Results

```bash
# Step 1: Preprocess (sentence segmentation, FKGL, filtering, tagging)
python scripts/preprocess.py

# Step 2: Sample 80-100 snippets
python scripts/sample.py

# Step 3: Run baselines
python models/glossary_baseline.py
python models/generic_prompt.py
python models/financial_prompt.py

# Step 4: Run post-processing checks
python models/postprocess.py

# Step 5: Run evaluation
python scripts/evaluate.py

# Step 6: Run error analysis
python scripts/error_analysis.py
```

## Data Sources

### Source A: Financial Institution Documents
- Barclaycard — Credit card terms and conditions (2 documents)
- HSBC UK — Credit card T&Cs, personal loan T&Cs, summary box (3 documents)
- Bank of Scotland — Credit card general T&Cs (1 document)
- Nationwide Building Society — Savings T&Cs, mortgage conditions, current account T&Cs (3 documents)

### Source B: Regulatory Consumer Guidance
- FCA (UK) — Consumer lending strategy letter, guide for consumer credit firms (2 documents)
- SEC (US) — Interest rate risk investor bulletin (1 document)
- CFPB (US) — Credit card guide, secured vs unsecured loans guide, consumer advisory (3 documents)

All sources are publicly available consumer-facing documents. See `docs/data_collection_log.md` for full URLs and access dates.

## Evaluation Metrics

| # | Metric | What It Measures |
|---|--------|-----------------|
| 1 | FKGL (Flesch-Kincaid Grade Level) | Surface readability |
| 2 | Flesch Reading Ease | Surface readability (second angle) |
| 3 | Semantic Similarity | Overall meaning preservation |
| 4 | BERTScore F1 | Fine-grained meaning preservation |
| 5 | SARI | Simplification quality vs human reference |
| 6 | Number Preservation Rate | Financial numbers survived intact |
| 7 | Modality Shift Rate | Certainty of statements unchanged |
| 8 | Human Clarity (1–5) | Real person finds it understandable |
| 9 | Human Correctness (1–5) | Real person confirms meaning preserved |

## Version History

- `v0.1` — After pilot annotation (checkpoint)
- `v1.0` — Final frozen dataset (submitted version)

**v1.0 commit hash:** _(to be filled after freeze)_

## Licence

This repository is for UCL coursework submission only. Do not redistribute.

## Acknowledgements

- AI tools used in an assistive capacity as permitted under UCL's AI policy (Assistive category). See report for full AI usage declaration.
