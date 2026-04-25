# HaqDaar Data Layer

This repository now includes a data-layer foundation to build a portable welfare access system.

## What is implemented

- Unified eligibility schema (`schemas/unified_eligibility.schema.json`)
- Scheme registry schema (`schemas/scheme_registry.schema.json`)
- Kaggle ingestion pipeline scaffold (`scripts/kaggle_ingest.py`)
- Condition normalizer (`scripts/normalize_conditions.py`)
- Source config for Kaggle datasets (`configs/kaggle_sources.csv`)
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

## Data model goals

- Central vs State scheme classification with portability behavior.
- Unified eligibility rules that support structured condition evaluation.
- Cross-state continuation and equivalent-scheme lookup.

## Next immediate step

Populate `configs/kaggle_sources.csv` with real Kaggle dataset IDs you want to ingest first.
# HaqDaar
