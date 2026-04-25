#!/usr/bin/env python3
from pathlib import Path
from typing import List, Literal

import pandas as pd
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from datetime import datetime

try:
    from motor.motor_asyncio import AsyncIOMotorClient  # type: ignore
except ModuleNotFoundError:  # Optional dependency in local/demo mode
    AsyncIOMotorClient = None  # type: ignore


DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "processed" / "final_schemes.csv"
MONGODB_URL = "mongodb://localhost:27017/"
PORTABILITY_BASELINE_PATH = (
    Path(__file__).resolve().parents[1] / "data" / "processed" / "portability_baseline.csv"
)

app = FastAPI(title="HaqDaar Scheme API", version="0.1.0")
mongo_enabled = False
user_logs = None
if AsyncIOMotorClient is not None:
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client.haqdaar_db
    user_logs = db.search_logs
    mongo_enabled = True


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
    portability_level: str
    portability_score: float
    barrier_summary: str | None
    mechanism_summary: str | None


def load_data() -> pd.DataFrame:
    if not DATA_PATH.exists():
        raise HTTPException(
            status_code=500,
            detail=f"Dataset not found at {DATA_PATH}. Run merge_schemes.py first.",
        )
    return pd.read_csv(DATA_PATH)


def normalize_scheme_key(value: str) -> str:
    return (
        str(value)
        .strip()
        .lower()
        .replace("&", "and")
        .replace("-", "_")
        .replace("/", "_")
        .replace("(", " ")
        .replace(")", " ")
        .replace(".", "")
        .replace("  ", " ")
        .strip()
        .replace(" ", "_")
    )


def load_portability_baseline() -> pd.DataFrame:
    if not PORTABILITY_BASELINE_PATH.exists():
        return pd.DataFrame(
            columns=[
                "scheme_key",
                "portability_level",
                "portability_score",
                "barrier_summary",
                "mechanism_summary",
            ]
        )
    base = pd.read_csv(PORTABILITY_BASELINE_PATH)
    if "scheme_key" in base.columns:
        base["scheme_key"] = base["scheme_key"].astype(str).map(normalize_scheme_key)
    return base


def default_portability_from_type(portability_type: str) -> tuple[str, float]:
    p = (portability_type or "UNKNOWN").upper()
    if p == "FULLY_PORTABLE":
        return ("HIGH", 0.85)
    if p == "PORTABLE_WITH_TRANSFER":
        return ("MEDIUM", 0.60)
    if p == "NOT_PORTABLE_EQUIVALENT_REQUIRED":
        return ("LOW", 0.25)
    return ("UNKNOWN", 0.50)


def enrich_portability(df: pd.DataFrame, baseline_df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.copy()
    out["scheme_key"] = out["scheme_name"].map(normalize_scheme_key)
    if not baseline_df.empty:
        out = out.merge(
            baseline_df[
                [
                    "scheme_key",
                    "portability_level",
                    "portability_score",
                    "barrier_summary",
                    "mechanism_summary",
                ]
            ],
            how="left",
            on="scheme_key",
        )
    else:
        out["portability_level"] = None
        out["portability_score"] = None
        out["barrier_summary"] = None
        out["mechanism_summary"] = None

    defaults = out["portability_type"].map(default_portability_from_type)
    out["portability_level"] = out["portability_level"].fillna(defaults.map(lambda x: x[0]))
    out["portability_score"] = out["portability_score"].fillna(defaults.map(lambda x: x[1]))
    out["barrier_summary"] = out["barrier_summary"].where(
        out["barrier_summary"].notna(), None
    )
    out["mechanism_summary"] = out["mechanism_summary"].where(
        out["mechanism_summary"].notna(), None
    )
    return out


def split_tokens(v) -> List[str]:
    if pd.isna(v) or v is None:
        return []
    s = str(v).strip()
    if not s or s.lower() == "nan":
        return []
    return [x.strip().upper() for x in s.split("|") if x.strip()]


def matches_eligibility(row: pd.Series, req: SchemeSearchRequest) -> bool:
    income_limit = row.get("annual_income_limit")
    if not pd.isna(income_limit) and income_limit is not None:
        if req.annual_income > float(income_limit):
            return False

    age_min = row.get("age_min", 0)
    age_max = row.get("age_max", 200)
    if req.age < int(age_min) or req.age > int(age_max):
        return False

    occ = split_tokens(row.get("occupations"))
    if occ and req.occupation.strip().upper() not in occ:
        return False

    cats = split_tokens(row.get("social_categories"))
    if cats and req.social_category.strip().upper() not in cats:
        return False

    gender_raw = row.get("gender")
    if not pd.isna(gender_raw) and gender_raw is not None:
        gender = str(gender_raw).strip().upper()
        if gender and gender not in {"ANY", "ALL", "NAN"} and req.gender.strip().upper() != gender:
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
            portability_level=str(r.get("portability_level", "UNKNOWN")),
            portability_score=float(r.get("portability_score", 0.50)),
            barrier_summary=None
            if pd.isna(r.get("barrier_summary"))
            else str(r.get("barrier_summary")),
            mechanism_summary=None
            if pd.isna(r.get("mechanism_summary"))
            else str(r.get("mechanism_summary")),
        )
        for _, r in df.iterrows()
    ]


@app.get("/")
def read_root():
    return {
        "message": "Welcome to HaqDaar Scheme API",
        "documentation": "/docs",
        "health_check": "/health",
        "search_endpoint": "/schemes/search (POST)"
    }


@app.get("/health")
def health():
    return {"status": "ok", "mongo_logging_enabled": mongo_enabled}


async def log_search(req: SchemeSearchRequest, counts: dict):
    if user_logs is None:
        return
    log_entry = {
        "timestamp": datetime.utcnow(),
        "input": req.model_dump(),
        "result_counts": counts
    }
    try:
        await user_logs.insert_one(log_entry)
    except Exception:
        # Non-blocking logging; API responses should not fail on analytics writes.
        return


@app.post("/schemes/search")
async def search_schemes(req: SchemeSearchRequest, background_tasks: BackgroundTasks):
    df = load_data()
    baseline_df = load_portability_baseline()
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

    eligible = enrich_portability(eligible, baseline_df).sort_values(
        by=["portability_score", "scheme_name"], ascending=[False, True]
    )
    transferable = enrich_portability(transferable, baseline_df).sort_values(
        by=["portability_score", "scheme_name"], ascending=[False, True]
    )
    new_state_only = enrich_portability(new_state_only, baseline_df).sort_values(
        by=["portability_score", "scheme_name"], ascending=[False, True]
    )

    result = {
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

    if mongo_enabled:
        background_tasks.add_task(log_search, req, result["counts"])
    return result
