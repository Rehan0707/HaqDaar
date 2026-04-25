# HaqDaar - Portable Welfare Access System

HaqDaar is a unified welfare access layer for migrant workers in India. It helps users find and claim schemes across states, even after relocation, with clear guidance and low-literacy-friendly UX.

## What this MVP includes

- **3-bucket welfare matching**
  - `bucket_a`: benefits that can be carried forward (portable)
  - `bucket_b`: benefits claimable in the current state
  - `bucket_c`: close matches that are almost eligible
- **Cross-state discovery endpoint**
  - Recommends additional schemes users may not know they qualify for
- **Claim-readiness guidance**
  - Required documents, missing documents, claim channel, and estimated timeline
- **Accessibility-focused frontend**
  - Multi-step guided flow
  - Simple language toggle
  - Read-aloud dashboard summary (browser speech)

## Project structure

- `api/app.py` - FastAPI backend with eligibility, portability, and discovery logic
- `index.html` + `js/app.js` + `css/styles.css` - frontend app
- `data/processed/portability_baseline.csv` - portability metadata
- `data/processed/final_schemes.csv` - optional full dataset (if available)

If `final_schemes.csv` is not present, the API now uses a built-in fallback demo dataset so the system runs out of the box.

## Quick start

1. Install Python dependencies:

```bash
pip install -r requirements.txt
```

2. Run backend:

```bash
npm run dev
```

3. Open frontend:

- Open `index.html` in a browser (or serve the root directory with any static server).

Backend runs on `http://127.0.0.1:8000` with docs at `http://127.0.0.1:8000/docs`.

## API endpoints

- `GET /health` - health check
- `POST /schemes/search` - primary bucketed welfare match
- `POST /schemes/discover` - additional recommended schemes
- `POST /auth/google` - Google token verification for sign-in
- `GET /auth/google/config` - frontend Google auth configuration check

## Example request

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
    "age": 29,
    "available_documents": ["Aadhaar Card", "Bank Account Details"]
  }'
```

## Notes

- Mongo logging is optional. If MongoDB is unreachable, search still works.
- For production-grade coverage, ingest and merge real datasets into `final_schemes.csv` using scripts in `scripts/`.
