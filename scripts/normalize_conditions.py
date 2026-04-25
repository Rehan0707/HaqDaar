#!/usr/bin/env python3
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


FIELD_MAP = {
    "income_limit_annual": ("annual_income", "<="),
    "income_limit_monthly": ("monthly_income", "<="),
    "category": ("social_category", "IN"),
    "occupation": ("occupation", "IN"),
    "min_age": ("age", ">="),
    "max_age": ("age", "<="),
    "state": ("residency_state", "="),
}


def parse_args():
    parser = argparse.ArgumentParser(description="Normalize eligibility columns into a unified structure.")
    parser.add_argument("--input", required=True, help="Input CSV path.")
    parser.add_argument("--output", required=True, help="Output JSONL path.")
    return parser.parse_args()


def to_condition(field_name: str, value):
    target = FIELD_MAP.get(field_name)
    if not target:
        return None
    field, operator = target
    if pd.isna(value):
        return None

    if operator == "IN":
        parsed_value = [x.strip() for x in str(value).split("|") if x.strip()]
        value_type = "array"
    else:
        parsed_value = value
        value_type = "number" if isinstance(value, (int, float)) else "string"

    return {
        "field": field,
        "operator": operator,
        "value": parsed_value,
        "value_type": value_type,
        "logical_group": "AND_GROUP_1",
    }


def row_to_record(row, index: int):
    jurisdiction_type = str(row.get("jurisdiction_type", "STATE")).upper()
    state_code = row.get("state_code")
    if pd.isna(state_code):
        state_code = None

    conditions = []
    for column in FIELD_MAP:
        if column in row:
            c = to_condition(column, row[column])
            if c:
                conditions.append(c)

    return {
        "rule_id": f"RULE_{index + 1:06d}",
        "scheme_id": str(row.get("scheme_id", f"SCHEME_{index + 1:06d}")),
        "jurisdiction_type": jurisdiction_type,
        "state_code": state_code,
        "conditions": conditions or [
            {
                "field": "bpl_status",
                "operator": "EXISTS",
                "value": True,
                "value_type": "boolean",
                "logical_group": "AND_GROUP_1",
            }
        ],
        "effective_from": str(row.get("effective_from", "2026-01-01")),
        "effective_to": None,
        "benefit_type": str(row.get("benefit_type", "other")),
        "source": {
            "source_type": str(row.get("source_type", "kaggle")),
            "source_name": str(row.get("source_name", "unknown")),
            "source_url": row.get("source_url") if not pd.isna(row.get("source_url")) else None,
            "ingested_at": datetime.now(timezone.utc).isoformat(),
        },
    }


def main():
    args = parse_args()
    df = pd.read_csv(args.input)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as out:
        for idx, row in df.iterrows():
            record = row_to_record(row, idx)
            out.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"[DONE] Wrote {len(df)} normalized records to {output_path}")


if __name__ == "__main__":
    main()
