# HaqDaar API Service

A portable welfare access API designed to help identify government schemes and their portability across Indian states.

## Core Features (Backend Only)

- **3-Bucket Logic:** Categorizes schemes into Portable (A), New State (B), and Close Matches (C).
- **Eligibility Engine:** Standardized logic for age, income, and occupation matching.
- **Portability Scoring:** Data-driven scoring for scheme transferability.
- **FastAPI Documentation:** Integrated Swagger UI for testing.

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the API:
```bash
npm run dev
```

The API will be available at `http://127.0.0.1:8000`. 
Access the documentation at `http://127.0.0.1:8000/docs`.

## Endpoints

- `POST /schemes/search`: Main search endpoint for welfare discovery.
- `GET /health`: System health check.

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

Response rows now include:

- `portability_level` (`HIGH`/`MEDIUM`/`LOW`/`UNKNOWN`)
- `portability_score` (`0.0` to `1.0`)
- `barrier_summary`
- `mechanism_summary`

Mongo logging behavior:

- If `motor` is installed and MongoDB is reachable at `mongodb://localhost:27017/`, searches are logged.
- If Mongo is unavailable, API still works with CSV data (logging is skipped).

## Data model goals

- Central vs State scheme classification with portability behavior.
- Unified eligibility rules that support structured condition evaluation.
- Cross-state continuation and equivalent-scheme lookup.

## Next immediate step

Populate `configs/kaggle_sources.csv` with real Kaggle dataset IDs, run ingestion, then run `merge_schemes.py`.
# HaqDaar
