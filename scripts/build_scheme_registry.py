#!/usr/bin/env python3
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


def parse_args():
    parser = argparse.ArgumentParser(description="Build canonical scheme registry JSONL from CSV inputs.")
    parser.add_argument("--schemes", required=True, help="Input schemes CSV.")
    parser.add_argument("--equivalence", required=True, help="Input cross-state equivalence CSV.")
    parser.add_argument("--output", required=True, help="Output JSONL path.")
    return parser.parse_args()


def load_equivalence_map(path: Path):
    df = pd.read_csv(path)
    grouped = {}
    for _, row in df.iterrows():
        source = row.get("source_scheme_id")
        if pd.isna(source):
            continue
        entry = {
            "target_state_code": row.get("target_state_code"),
            "target_scheme_id": row.get("target_scheme_id"),
            "mapping_type": row.get("mapping_type", "equivalent"),
            "confidence_score": float(row.get("confidence_score", 0.5)),
            "notes": row.get("notes") if not pd.isna(row.get("notes")) else None,
        }
        grouped.setdefault(source, []).append(entry)
    return grouped


def main():
    args = parse_args()
    schemes_df = pd.read_csv(args.schemes)
    eq_map = load_equivalence_map(Path(args.equivalence))

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).isoformat()

    with out_path.open("w", encoding="utf-8") as out:
        for _, row in schemes_df.iterrows():
            scheme_id = str(row.get("scheme_id"))
            record = {
                "scheme_id": scheme_id,
                "scheme_name": row.get("scheme_name"),
                "scheme_short_name": row.get("scheme_short_name")
                if not pd.isna(row.get("scheme_short_name"))
                else None,
                "jurisdiction_type": row.get("jurisdiction_type", "STATE"),
                "state_code": row.get("state_code") if not pd.isna(row.get("state_code")) else None,
                "portability_type": row.get(
                    "portability_type", "NOT_PORTABLE_EQUIVALENT_REQUIRED"
                ),
                "benefit_domain": row.get("benefit_domain", "other"),
                "status": row.get("status", "active"),
                "equivalent_scheme_refs": eq_map.get(scheme_id, []),
                "source": {
                    "source_type": row.get("source_type", "kaggle"),
                    "source_name": row.get("source_name", "unknown"),
                    "source_url": row.get("source_url") if not pd.isna(row.get("source_url")) else None,
                    "version": row.get("version") if not pd.isna(row.get("version")) else None,
                    "ingested_at": now,
                },
            }
            out.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"[DONE] Registry written to {out_path}")


if __name__ == "__main__":
    main()
