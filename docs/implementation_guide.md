# Implementation Guide: Merge + Project Integration

## A) Merge all datasets into one

1. Put all downloaded CSVs under `data/raw/<dataset_name>/`.
2. Keep source IDs in `configs/kaggle_sources.csv`.
3. Run:

```bash
python3 scripts/merge_schemes.py \
  --raw-dir data/raw \
  --mapping-config configs/source_column_mappings.json \
  --output-csv data/processed/final_schemes.csv \
  --output-json data/processed/final_schemes.json
```

### What merge_schemes.py does

- Detects all CSV files inside `data/raw/`
- Maps different input column names into canonical fields
- Normalizes state values to state codes
- Classifies `CENTRAL` vs `STATE`
- Infers portability when missing
- Deduplicates by `(scheme_name, state_code, jurisdiction_type)`

## B) Use it in your app

Start API:

```bash
uvicorn api.app:app --reload
```

Endpoint:

- `POST /schemes/search`

Input:

```json
{
  "old_state": "BR",
  "new_state": "MH",
  "annual_income": 240000,
  "occupation": "construction",
  "social_category": "OBC",
  "gender": "ANY",
  "age": 29
}
```

Output sections:

- `eligible_schemes`
- `transferable_schemes`
- `new_state_schemes`

## C) Can you access Kaggle data without manual download?

Yes:

- Use Kaggle API (`scripts/kaggle_ingest.py`) so users do not manually download files.
- Kaggle Notebooks can read datasets without local download, but your external app still needs copied/exported data.

For this project, Kaggle API is the right path for reproducible ingestion.
