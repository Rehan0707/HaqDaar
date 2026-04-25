# Data Layer Design

## 1) Unified Eligibility Schema

The model converts diverse eligibility text into structured conditions:

- `field`: canonical key (income, category, occupation, age, residency, etc.)
- `operator`: `<`, `<=`, `IN`, `EXISTS`, etc.
- `value`: scalar or list
- `logical_group`: supports OR-of-AND logic

This allows one rules engine across all schemes and states.

## 2) Scheme Registry

Each scheme record includes:

- Scope: `CENTRAL` or `STATE`
- Portability behavior:
  - `FULLY_PORTABLE`
  - `PORTABLE_WITH_TRANSFER`
  - `NOT_PORTABLE_EQUIVALENT_REQUIRED`
  - `UNKNOWN`
- Domain tag (`housing`, `food`, `health`, etc.)
- Equivalence references to other states

## 3) Cross-State Mapping

`data/mappings/cross_state_equivalence_template.csv` holds continuation mapping rows:

- source scheme + state
- target state equivalent
- mapping type (`equivalent`, `continuation_path`, `partial_overlap`)
- confidence score
- manual continuation steps

## 4) ETL Flow

1. Download source files from Kaggle with `scripts/kaggle_ingest.py`.
2. Build normalized scheme registry using:
   - `data/processed/scheme_registry_template.csv`
   - `data/mappings/cross_state_equivalence_template.csv`
3. Convert eligibility columns to canonical JSONL with `scripts/normalize_conditions.py`.
