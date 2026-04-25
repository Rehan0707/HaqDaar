# HaqDaar Data Layer

This repository now includes a data-layer foundation to build a portable welfare access system.

## What is implemented

- Unified eligibility schema (`schemas/unified_eligibility.schema.json`)
- Scheme registry schema (`schemas/scheme_registry.schema.json`)
- Kaggle ingestion pipeline scaffold (`scripts/kaggle_ingest.py`)
- Multi-source merger and canonicalizer (`scripts/merge_schemes.py`)
- Condition normalizer (`scripts/normalize_conditions.py`)
- Search API for eligibility + portability (`api/app.py`)
- Source config for Kaggle datasets (`configs/kaggle_sources.csv`)
- Source column mapping config (`configs/source_column_mappings.json`)
- Cross-state mapping templates (`data/mappings/*.csv`)

## Folder structure

```text
configs/                Kaggle dataset source manifest
data/raw/               Raw downloaded files
data/processed/         Cleaned and normalized outputs
data/mappings/          Cross-state and category mappings
docs/                   Notes and modeling documentation
schemas/                JSON schemas for core entities
scripts/                ETL scripts
api/                    FastAPI backend
```

## Quick start

1. Install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Configure Kaggle API credentials:

- Generate token from Kaggle account settings.
- Place it at `~/.kaggle/kaggle.json`.
- Run: `chmod 600 ~/.kaggle/kaggle.json`

3. Download datasets listed in the manifest:

```bash
python3 scripts/kaggle_ingest.py \
  --sources configs/kaggle_sources.csv \
  --out-dir data/raw
```

4. Normalize eligibility conditions:

```bash
python3 scripts/normalize_conditions.py \
  --input data/raw/scheme_registry_raw.csv \
  --output data/processed/scheme_registry_normalized.jsonl
```

5. Merge all source datasets into one canonical file:

```bash
python3 scripts/merge_schemes.py \
  --raw-dir data/raw \
  --mapping-config configs/source_column_mappings.json \
  --output-csv data/processed/final_schemes.csv \
  --output-json data/processed/final_schemes.json
```

6. Run backend API:

```bash
uvicorn api.app:app --reload
```

Then call:

```bash
curl -X POST http://127.0.0.1:8000/schemes/search \
  -H "Content-Type: application/json" \
  -d '{
    "old_state": "BR",
    "new_state": "MH",
    "annual_income": 240000,
    "occupation": "construction",
    "social_category": "OBC",
    "gender": "ANY",
    "age": 29
  }'
```

## Data model goals

- Central vs State scheme classification with portability behavior.
- Unified eligibility rules that support structured condition evaluation.
- Cross-state continuation and equivalent-scheme lookup.

## Next immediate step

Populate `configs/kaggle_sources.csv` with real Kaggle dataset IDs, run ingestion, then run `merge_schemes.py`.
# HaqDaar
