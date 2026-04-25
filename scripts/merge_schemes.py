#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd


TRUE_VALUES = {"true", "1", "yes", "y", "portable"}
STATE_ALL_VALUES = {"all", "india", "pan india", "pan-india", "national", "central"}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Merge multiple raw scheme CSV files into one canonical dataset."
    )
    parser.add_argument("--raw-dir", required=True, help="Directory containing downloaded source folders/files")
    parser.add_argument("--mapping-config", required=True, help="JSON file with synonym mapping")
    parser.add_argument("--output-csv", required=True, help="Path to final merged CSV")
    parser.add_argument("--output-json", required=True, help="Path to final merged JSON")
    return parser.parse_args()


def load_mapping_config(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def discover_csv_files(raw_dir: Path) -> List[Path]:
    return sorted(p for p in raw_dir.rglob("*.csv") if p.is_file())


def canonicalize_column(df: pd.DataFrame, target: str, synonyms: List[str]) -> pd.Series:
    existing = {c.lower(): c for c in df.columns}
    for candidate in synonyms:
        key = candidate.lower()
        if key in existing:
            return df[existing[key]]
    return pd.Series([None] * len(df), index=df.index)


def parse_income(value) -> Optional[float]:
    if pd.isna(value):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value).lower().replace(",", "").strip()
    if not s:
        return None
    numeric_parts = re.findall(r"\d+(?:\.\d+)?", s)
    if not numeric_parts:
        return None
    income = float(numeric_parts[0])
    if "lakh" in s:
        income *= 100000
    return income


def parse_bool(value) -> bool:
    if pd.isna(value):
        return False
    return str(value).strip().lower() in TRUE_VALUES


def normalize_state(value, state_name_to_code: Dict[str, str], jurisdiction_type: str):
    if pd.isna(value):
        return None if jurisdiction_type == "CENTRAL" else None
    s = str(value).strip()
    if not s:
        return None
    lowered = s.lower()
    if lowered in STATE_ALL_VALUES:
        return "ALL"
    if len(s) == 2 and s.isalpha():
        return s.upper()
    return state_name_to_code.get(lowered, s.upper())


def normalize_jurisdiction(value, state_code):
    if pd.isna(value):
        return "CENTRAL" if state_code in {"ALL", None} else "STATE"
    s = str(value).strip().upper()
    if s in {"CENTRAL", "STATE"}:
        return s
    if "CENTRAL" in s or s in {"NATIONAL", "PAN_INDIA", "PAN INDIA"}:
        return "CENTRAL"
    return "STATE"


def normalize_portability(jurisdiction_type: str, state_code: Optional[str], portability_type_raw, is_portable_raw):
    portability_type = None
    if not pd.isna(portability_type_raw):
        portability_type = str(portability_type_raw).strip().upper().replace(" ", "_")

    if portability_type in {
        "FULLY_PORTABLE",
        "PORTABLE_WITH_TRANSFER",
        "NOT_PORTABLE_EQUIVALENT_REQUIRED",
        "UNKNOWN",
    }:
        pass
    else:
        if jurisdiction_type == "CENTRAL" or state_code == "ALL":
            portability_type = "FULLY_PORTABLE"
        elif parse_bool(is_portable_raw):
            portability_type = "PORTABLE_WITH_TRANSFER"
        else:
            portability_type = "NOT_PORTABLE_EQUIVALENT_REQUIRED"

    is_portable = portability_type in {"FULLY_PORTABLE", "PORTABLE_WITH_TRANSFER"}
    return portability_type, is_portable


def split_multi(value) -> str:
    if pd.isna(value):
        return ""
    s = str(value).strip()
    if not s:
        return ""
    parts = re.split(r"[|,/;]+", s)
    clean = [p.strip() for p in parts if p.strip()]
    return "|".join(dict.fromkeys(clean))


def build_canonical_df(df: pd.DataFrame, dataset_name: str, file_name: str, cfg: dict) -> pd.DataFrame:
    synonyms = cfg["column_synonyms"]
    state_name_to_code = cfg["state_name_to_code"]

    out = pd.DataFrame(index=df.index)
    for target_col in cfg["default_required_output_columns"]:
        out[target_col] = None

    out["scheme_name"] = canonicalize_column(df, "scheme_name", synonyms["scheme_name"]).astype("string")
    out["description"] = canonicalize_column(df, "description", synonyms["description"]).astype("string")
    state_raw = canonicalize_column(df, "state_code", synonyms["state_code"])
    out["category"] = canonicalize_column(df, "category", synonyms["category"]).astype("string")
    out["annual_income_limit"] = canonicalize_column(df, "annual_income_limit", synonyms["annual_income_limit"]).map(
        parse_income
    )
    out["occupations"] = canonicalize_column(df, "occupations", synonyms["occupations"]).map(split_multi)
    out["social_categories"] = canonicalize_column(
        df, "social_categories", synonyms["social_categories"]
    ).map(split_multi)
    out["gender"] = canonicalize_column(df, "gender", synonyms["gender"]).map(
        lambda x: str(x).strip().upper() if not pd.isna(x) else ""
    )
    out["age_min"] = pd.to_numeric(
        canonicalize_column(df, "age_min", synonyms["age_min"]), errors="coerce"
    ).fillna(0).astype(int)
    out["age_max"] = pd.to_numeric(
        canonicalize_column(df, "age_max", synonyms["age_max"]), errors="coerce"
    ).fillna(200).astype(int)

    jurisdiction_raw = canonicalize_column(df, "jurisdiction_type", synonyms["jurisdiction_type"])
    portability_raw = canonicalize_column(df, "portability_type", synonyms["portability_type"])
    portable_raw = canonicalize_column(df, "is_portable", synonyms["is_portable"])

    out["state_code"] = state_raw.map(lambda x: normalize_state(x, state_name_to_code, "STATE"))
    out["jurisdiction_type"] = pd.Series(
        [normalize_jurisdiction(j, s) for j, s in zip(jurisdiction_raw, out["state_code"])], index=df.index
    )

    normalized_portability = [
        normalize_portability(j, s, p, ip)
        for j, s, p, ip in zip(out["jurisdiction_type"], out["state_code"], portability_raw, portable_raw)
    ]
    out["portability_type"] = [x[0] for x in normalized_portability]
    out["is_portable"] = [x[1] for x in normalized_portability]

    out["source_dataset"] = dataset_name
    out["source_file"] = file_name
    out["scheme_id"] = (
        out["jurisdiction_type"].fillna("STATE")
        + "_"
        + out["state_code"].fillna("NA")
        + "_"
        + out["scheme_name"].fillna("UNKNOWN").str.lower().str.replace(r"[^a-z0-9]+", "_", regex=True).str.strip("_")
    )

    out["description"] = out["description"].fillna("")
    out["scheme_name"] = out["scheme_name"].fillna("")
    out = out[out["scheme_name"].str.len() > 1].copy()
    return out


def deduplicate(df: pd.DataFrame) -> pd.DataFrame:
    work = df.copy()
    work["dedupe_key"] = (
        work["scheme_name"].str.lower().str.strip()
        + "|"
        + work["state_code"].fillna("ALL")
        + "|"
        + work["jurisdiction_type"]
    )
    work = work.sort_values(by=["scheme_name", "source_dataset"]).drop_duplicates("dedupe_key", keep="first")
    return work.drop(columns=["dedupe_key"])


def main():
    args = parse_args()
    raw_dir = Path(args.raw_dir)
    cfg = load_mapping_config(Path(args.mapping_config))
    csv_files = discover_csv_files(raw_dir)

    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {raw_dir}")

    merged_chunks = []
    for csv_path in csv_files:
        df = pd.read_csv(csv_path)
        dataset_name = csv_path.parent.name
        chunk = build_canonical_df(df, dataset_name=dataset_name, file_name=csv_path.name, cfg=cfg)
        merged_chunks.append(chunk)
        print(f"[INFO] processed {csv_path} rows={len(df)} normalized={len(chunk)}")

    merged = pd.concat(merged_chunks, ignore_index=True)
    merged = deduplicate(merged)

    output_csv = Path(args.output_csv)
    output_json = Path(args.output_json)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    output_json.parent.mkdir(parents=True, exist_ok=True)

    merged.to_csv(output_csv, index=False)
    merged.to_json(output_json, orient="records", force_ascii=False, indent=2)
    print(f"[DONE] merged_rows={len(merged)} csv={output_csv} json={output_json}")


if __name__ == "__main__":
    main()
