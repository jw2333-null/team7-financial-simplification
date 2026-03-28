# Automatic Simplification of Financial Jargon in Consumer-Facing Documents

**MSIN0221 Natural Language Processing — Group Assignment**
**Team 7 | UCL School of Management | 2025/26 Term 2**

## Research Question

> To what extent can pretrained NLP models simplify consumer-facing financial jargon while preserving the original meaning and key financial content?

## Team Members

| Name | Student ID | Contribution |
|------|-----------|-------------|
| Gianni Chen | 25057622 | Data preprocessing, dataset curation, gold standard creation |
| Hanley Ho | 25120620 | Model development, model inference pipeline (FLAN-T5 notebooks) |
| Stephen Leung | 25084380 | Evaluation, metrics, result validation, BERTScore computation |
| Stefani Poon | 24158473 | Writing, analysis, discussion, report editing |
| Zhengpeng Wang | 25115696 | LLM baseline (Gemini API), writing, analysis, visualisation |

## Repository Structure

```
team7-financial-simplification/
├── data/
│   ├── raw/                              # Extracted .txt files from source PDFs
│   │   ├── financial_institution/        # Bank/building society T&Cs
│   │   └── regulatory_guidance/          # FCA, SEC, CFPB documents
│   ├── processed/
│   │   └── dataset_v2.csv               # 100 sampled snippets with diversity tags
│   └── final/
│       ├── dataset_annotation_v3.csv     # Annotated dataset with human references
│       └── dataset_model_final.csv       # All 4 model outputs + annotations
├── notebooks/                            # All model inference + evaluation notebooks
│   ├── notebook_base_generic.ipynb       # FLAN-T5-base generic prompt
│   ├── notebook_base_financial.ipynb     # FLAN-T5-base financial prompt
│   ├── notebook_xl_financial.ipynb       # FLAN-T5-XL financial prompt
│   ├── notebook_llm.ipynb               # Gemini 1.5 Flash (LLM API)
│   ├── bertscore_calculator.ipynb        # BERTScore F1 computation
│   └── semantic_similarity_calculator.ipynb # Sentence-transformer similarity
├── scripts/                              # Preprocessing and sampling scripts
│   ├── preprocess.py                     # Text extraction → sentence segmentation
│   └── sample.py                         # Stratified sampling → dataset
├── models/                               # Baseline and prompting code
│   ├── generic_prompt.py                 # FLAN-T5 generic prompt
│   ├── financial_prompt.py               # FLAN-T5 financial prompt
│   └── postprocess.py                    # Number preservation + modality checks
├── results/
│   └── dataset_score.csv                 # Evaluation summary (all metrics)
├── docs/
│   ├── annotation_guidelines.md          # Rules for manual simplification
│   └── data_collection_log.md            # Source URLs and access dates
├── README.md
├── requirements.txt
└── .gitignore
```

## Models Tested

| # | System | Model | Parameters |
|---|--------|-------|-----------|
| 1 | Generic prompt | FLAN-T5-base | 250M |
| 2 | Financial prompt | FLAN-T5-base | 250M |
| 3 | Financial prompt | FLAN-T5-XL | 3B |
| 4 | Financial prompt | Gemini 1.5 Flash | LLM (API) |

## Key Results

| Model | FKGL Drop ↑ | Semantic Sim ↑ | SARI ↑ | Modality Shift ↓ |
|-------|------------|----------------|--------|-----------------|
| Generic (T5-base) | -0.03 | 0.90 | 39.75 | 1.0% |
| Financial (T5-base) | -0.09 | 0.95 | 39.56 | 0.0% |
| Financial (T5-XL) | 0.03 | 0.95 | 38.97 | 0.0% |
| Financial (Gemini) | **5.45** | 0.79 | **46.33** | 3.0% |

## Data Sources

### Source A: Financial Institution Documents (9 documents)
Barclaycard, HSBC UK, Bank of Scotland, Nationwide Building Society

### Source B: Regulatory Consumer Guidance (6 documents)
FCA (UK), SEC (US), CFPB (US)

All sources are publicly available. See `docs/data_collection_log.md` for full URLs.

## Setup

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

## Reproducing Results

The model notebooks in `notebooks/` are designed to run on Google Colab.
Upload the relevant CSV and run all cells. Each notebook documents its
model, prompt, and expected output.

## Licence

This repository is for UCL coursework submission only. Do not redistribute.
