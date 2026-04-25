#!/usr/bin/env python3
from pathlib import Path
from typing import List, Literal

import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "processed" / "final_schemes.csv"

app = FastAPI(title="HaqDaar Scheme API", version="0.1.0")


class SchemeSearchRequest(BaseModel):
    old_state: str = Field(..., min_length=2, description="Previous state code e.g. BR")
    new_state: str = Field(..., min_length=2, description="Current state code e.g. MH")
    annual_income: float = Field(..., ge=0)
    occupation: str = Field(..., min_length=1)
    social_category: str = Field(..., min_length=1, description="GEN/OBC/SC/ST/EWS etc")
    gender: str = Field(default="ANY")
    age: int = Field(default=30, ge=0, le=120)


class SchemeResponse(BaseModel):
    scheme_id: str
    scheme_name: str
    state_code: str | None
    jurisdiction_type: Literal["CENTRAL", "STATE"]
    category: str | None
    portability_type: str
    is_portable: bool
    description: str | None
    source_dataset: str | None


def load_data() -> pd.DataFrame:
    if not DATA_PATH.exists():
        raise HTTPException(
            status_code=500,
            detail=f"Dataset not found at {DATA_PATH}. Run merge_schemes.py first.",
        )
    return pd.read_csv(DATA_PATH)


def split_tokens(v) -> List[str]:
    if pd.isna(v):
        return []
    return [x.strip().upper() for x in str(v).split("|") if x.strip()]


def matches_eligibility(row: pd.Series, req: SchemeSearchRequest) -> bool:
    income_limit = row.get("annual_income_limit")
    if not pd.isna(income_limit) and req.annual_income > float(income_limit):
        return False

    if req.age < int(row.get("age_min", 0)) or req.age > int(row.get("age_max", 200)):
        return False

    occ = split_tokens(row.get("occupations"))
    if occ and req.occupation.strip().upper() not in occ:
        return False

    cats = split_tokens(row.get("social_categories"))
    if cats and req.social_category.strip().upper() not in cats:
        return False

    gender = str(row.get("gender", "")).strip().upper()
    if gender and gender not in {"ANY", "ALL"} and req.gender.strip().upper() != gender:
        return False
    return True


def to_records(df: pd.DataFrame) -> List[SchemeResponse]:
    return [
        SchemeResponse(
            scheme_id=str(r["scheme_id"]),
            scheme_name=str(r["scheme_name"]),
            state_code=None if pd.isna(r.get("state_code")) else str(r.get("state_code")),
            jurisdiction_type=str(r.get("jurisdiction_type", "STATE")),
            category=None if pd.isna(r.get("category")) else str(r.get("category")),
            portability_type=str(r.get("portability_type", "UNKNOWN")),
            is_portable=bool(r.get("is_portable", False)),
            description=None if pd.isna(r.get("description")) else str(r.get("description")),
            source_dataset=None if pd.isna(r.get("source_dataset")) else str(r.get("source_dataset")),
        )
        for _, r in df.iterrows()
    ]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/schemes/search")
def search_schemes(req: SchemeSearchRequest):
    df = load_data()
    df["state_code"] = df["state_code"].fillna("ALL").astype(str).str.upper()
    df["jurisdiction_type"] = df["jurisdiction_type"].fillna("STATE").astype(str).str.upper()
    df["is_portable"] = df["is_portable"].fillna(False).astype(bool)
    df["portability_type"] = df["portability_type"].fillna("UNKNOWN").astype(str)

    eligible = df[df.apply(lambda r: matches_eligibility(r, req), axis=1)].copy()

    old_or_central = eligible[
        (eligible["state_code"].isin([req.old_state.upper(), "ALL"]))
        | (eligible["jurisdiction_type"] == "CENTRAL")
    ].copy()
    new_or_central = eligible[
        (eligible["state_code"].isin([req.new_state.upper(), "ALL"]))
        | (eligible["jurisdiction_type"] == "CENTRAL")
    ].copy()

    transferable = old_or_central[
        (old_or_central["is_portable"] == True)
        | (old_or_central["portability_type"].isin(["FULLY_PORTABLE", "PORTABLE_WITH_TRANSFER"]))
    ].copy()

    new_state_only = new_or_central[
        (~new_or_central["scheme_id"].isin(old_or_central["scheme_id"]))
        & (new_or_central["state_code"].isin([req.new_state.upper(), "ALL"]))
    ].copy()

    return {
        "input": req.model_dump(),
        "counts": {
            "eligible_schemes": int(len(eligible)),
            "transferable_schemes": int(len(transferable)),
            "new_state_schemes": int(len(new_state_only)),
        },
        "eligible_schemes": to_records(eligible),
        "transferable_schemes": to_records(transferable),
        "new_state_schemes": to_records(new_state_only),
    }
