#!/usr/bin/env python3
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

import pandas as pd
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from datetime import datetime
import os
from dotenv import load_dotenv
try:
    from google.oauth2 import id_token
    from google.auth.transport import requests as google_requests
except ModuleNotFoundError:  # Optional in local/demo mode
    id_token = None  # type: ignore
    google_requests = None  # type: ignore

load_dotenv()

try:
    from motor.motor_asyncio import AsyncIOMotorClient  # type: ignore
except ModuleNotFoundError:  # Optional dependency in local/demo mode
    AsyncIOMotorClient = None  # type: ignore


DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "processed" / "final_schemes.csv"
MONGODB_URL = "mongodb://localhost:27017/"
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "").strip()
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "").strip()
PORTABILITY_BASELINE_PATH = (
    Path(__file__).resolve().parents[1] / "data" / "processed" / "portability_baseline.csv"
)

app = FastAPI(title="HaqDaar Scheme API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
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
    available_documents: List[str] = Field(default_factory=list)
    preferred_language: str = Field(default="en")


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
    # New Hackathon Metadata
    application_steps: List[str] = Field(default_factory=list)
    required_documents: List[str] = Field(default_factory=list)
    missing_documents: List[str] = Field(default_factory=list)
    time_estimate: str = Field(default="10-15 days")
    claim_channel: str = Field(default="CSC / State Portal")
    discovery_reason: str | None = None


def load_data() -> pd.DataFrame:
    if DATA_PATH.exists():
        return ensure_dataset_columns(pd.read_csv(DATA_PATH))
    # Demo-safe fallback dataset so the project works out-of-the-box.
    return pd.DataFrame(
        [
            {
                "scheme_id": "CENTRAL_ONORC",
                "scheme_name": "One Nation One Ration Card",
                "state_code": "ALL",
                "jurisdiction_type": "CENTRAL",
                "category": "food",
                "portability_type": "FULLY_PORTABLE",
                "is_portable": True,
                "description": "Access subsidized ration from any FPS across India.",
                "source_dataset": "haqdaar_seed",
                "annual_income_limit": 300000,
                "age_min": 18,
                "age_max": 120,
                "occupations": "CONSTRUCTION|FACTORY|AGRICULTURE|DOMESTIC|TRANSPORT|ALL",
                "social_categories": "GEN|OBC|SC|ST|EWS",
                "gender": "ANY",
            },
            {
                "scheme_id": "CENTRAL_PMJAY",
                "scheme_name": "Ayushman Bharat PM-JAY",
                "state_code": "ALL",
                "jurisdiction_type": "CENTRAL",
                "category": "health",
                "portability_type": "FULLY_PORTABLE",
                "is_portable": True,
                "description": "Cashless secondary and tertiary care hospitalization cover.",
                "source_dataset": "haqdaar_seed",
                "annual_income_limit": 250000,
                "age_min": 0,
                "age_max": 120,
                "occupations": "ALL",
                "social_categories": "GEN|OBC|SC|ST|EWS",
                "gender": "ANY",
            },
            {
                "scheme_id": "MH_BOCW",
                "scheme_name": "Maharashtra BOCW Worker Welfare",
                "state_code": "MH",
                "jurisdiction_type": "STATE",
                "category": "worker_support",
                "portability_type": "PORTABLE_WITH_TRANSFER",
                "is_portable": True,
                "description": "Registration-linked benefits for construction workers in Maharashtra.",
                "source_dataset": "haqdaar_seed",
                "annual_income_limit": 350000,
                "age_min": 18,
                "age_max": 60,
                "occupations": "CONSTRUCTION",
                "social_categories": "GEN|OBC|SC|ST|EWS",
                "gender": "ANY",
            },
            {
                "scheme_id": "DL_EWS_HOUSING",
                "scheme_name": "Delhi EWS Rental Housing Support",
                "state_code": "DL",
                "jurisdiction_type": "STATE",
                "category": "housing",
                "portability_type": "NOT_PORTABLE_EQUIVALENT_REQUIRED",
                "is_portable": False,
                "description": "Rental and housing support for eligible low-income migrant families.",
                "source_dataset": "haqdaar_seed",
                "annual_income_limit": 300000,
                "age_min": 18,
                "age_max": 120,
                "occupations": "ALL",
                "social_categories": "GEN|OBC|SC|ST|EWS",
                "gender": "ANY",
            },
            {
                "scheme_id": "BR_STUDENT_GIRL",
                "scheme_name": "Bihar Girls Education Incentive",
                "state_code": "BR",
                "jurisdiction_type": "STATE",
                "category": "education",
                "portability_type": "NOT_PORTABLE_EQUIVALENT_REQUIRED",
                "is_portable": False,
                "description": "State scholarship and retention support for girl students.",
                "source_dataset": "haqdaar_seed",
                "annual_income_limit": 200000,
                "age_min": 10,
                "age_max": 25,
                "occupations": "ALL",
                "social_categories": "GEN|OBC|SC|ST|EWS",
                "gender": "FEMALE",
            },
            {
                "scheme_id": "CENTRAL_E_SHRAM",
                "scheme_name": "e-Shram + PMSBY Worker Insurance",
                "state_code": "ALL",
                "jurisdiction_type": "CENTRAL",
                "category": "insurance",
                "portability_type": "FULLY_PORTABLE",
                "is_portable": True,
                "description": "Portable social security and accidental insurance for unorganized workers.",
                "source_dataset": "haqdaar_seed",
                "annual_income_limit": 500000,
                "age_min": 18,
                "age_max": 59,
                "occupations": "CONSTRUCTION|FACTORY|AGRICULTURE|DOMESTIC|TRANSPORT|RETAIL|ALL",
                "social_categories": "GEN|OBC|SC|ST|EWS",
                "gender": "ANY",
            },
        ]
    )


def ensure_dataset_columns(df: pd.DataFrame) -> pd.DataFrame:
    defaults: Dict[str, Any] = {
        "scheme_id": "",
        "scheme_name": "",
        "state_code": "ALL",
        "jurisdiction_type": "STATE",
        "category": "general",
        "portability_type": "UNKNOWN",
        "is_portable": False,
        "description": None,
        "source_dataset": "unknown",
        "annual_income_limit": None,
        "age_min": 0,
        "age_max": 120,
        "occupations": "ALL",
        "social_categories": "GEN|OBC|SC|ST|EWS",
        "gender": "ANY",
    }
    out = df.copy()
    for col, fallback in defaults.items():
        if col not in out.columns:
            out[col] = fallback
    return out


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


def title_token(value: str) -> str:
    token = (value or "").replace("_", " ").strip().lower()
    return " ".join([w.capitalize() for w in token.split()]) if token else ""


def matches_eligibility(row: pd.Series, req: SchemeSearchRequest, tolerance: float = 0.0) -> bool:
    # 1. Annual Income Check
    income_limit = row.get("annual_income_limit")
    if pd.notna(income_limit) and income_limit is not None:
        try:
            effective_limit = float(income_limit) * (1.0 + tolerance)
            if req.annual_income > effective_limit:
                return False
        except (ValueError, TypeError):
            pass

    # 2. Age Range Check
    try:
        age_min = row.get("age_min")
        age_max = row.get("age_max")
        # Handle NaN/Empty values gracefully
        effective_min = int(age_min) if pd.notna(age_min) else 0
        effective_max = int(age_max) if pd.notna(age_max) else 120
        if req.age < effective_min or req.age > effective_max:
            return False
    except (ValueError, TypeError):
        pass

    # 3. Occupation Check
    occ_list = split_tokens(row.get("occupations"))
    if occ_list:
        req_occ = req.occupation.strip().upper()
        if req_occ != "ALL" and "ALL" not in occ_list and req_occ not in occ_list:
            return False

    # 4. Social Category Check
    cat_list = split_tokens(row.get("social_categories"))
    if cat_list:
        req_cat = req.social_category.strip().upper()
        if req_cat != "ALL" and "ALL" not in cat_list and req_cat not in cat_list:
            return False

    # 5. Gender Check
    gender_raw = row.get("gender")
    if pd.notna(gender_raw) and gender_raw is not None:
        gender = str(gender_raw).strip().upper()
        if gender and gender not in {"ANY", "ALL", "NAN"}:
            req_gender = req.gender.strip().upper()
            if req_gender != gender and req_gender != "ANY":
                return False
    return True


def to_records(df: pd.DataFrame, req: Optional[SchemeSearchRequest] = None) -> List[SchemeResponse]:
    def docs_for_scheme(row: pd.Series) -> List[str]:
        docs = ["Aadhaar Card", "Bank Account Details"]
        category = str(row.get("category") or "").strip().lower()
        jurisdiction = str(row.get("jurisdiction_type") or "STATE").upper()
        portability_type = str(row.get("portability_type") or "UNKNOWN").upper()

        if "food" in category or "ration" in category:
            docs.extend(["Ration Card"])
        if "health" in category:
            docs.extend(["Family ID / Ayushman Card"])
        if "housing" in category:
            docs.extend(["Income Certificate", "Address Proof"])
        if portability_type == "PORTABLE_WITH_TRANSFER":
            docs.extend(["Migration Proof", "Old State Enrollment Reference"])
        if jurisdiction == "STATE":
            docs.extend(["Domicile / Residence Proof"])
        if req and req.occupation.strip().upper() == "CONSTRUCTION":
            docs.append("Labour Card / e-Shram ID")

        # Preserve order while removing duplicates.
        return list(dict.fromkeys(docs))

    def missing_docs(required_documents: List[str]) -> List[str]:
        if not req:
            return []
        available = {d.strip().lower() for d in req.available_documents}
        return [doc for doc in required_documents if doc.strip().lower() not in available]

    def steps_for_scheme(row: pd.Series) -> List[str]:
        jurisdiction = str(row.get("jurisdiction_type") or "STATE").upper()
        portability_type = str(row.get("portability_type") or "UNKNOWN").upper()
        state_code = str(row.get("state_code") or "ALL")

        base_steps = [
            "Check eligibility in HaqDaar and shortlist this scheme.",
            "Collect required documents and keep digital copies ready.",
        ]
        if portability_type == "FULLY_PORTABLE":
            base_steps.extend(
                [
                    "Apply at the nearest CSC or approved online portal in your current state.",
                    "Complete Aadhaar e-KYC and verify bank details for benefit transfer.",
                ]
            )
        elif portability_type == "PORTABLE_WITH_TRANSFER":
            base_steps.extend(
                [
                    "Submit transfer request with origin-state reference details.",
                    "Complete destination-state verification and track approval status.",
                ]
            )
        else:
            if jurisdiction == "STATE":
                base_steps.extend(
                    [
                        f"Apply through {state_code} state portal or district welfare office.",
                        "If transfer is not allowed, register under equivalent destination-state scheme.",
                    ]
                )
            else:
                base_steps.extend(
                    [
                        "Apply through official central portal or CSC support channel.",
                        "Track application ID and complete any additional verification requests.",
                    ]
                )
        return base_steps

    def eta_for_scheme(row: pd.Series) -> str:
        portability_type = str(row.get("portability_type") or "UNKNOWN").upper()
        if portability_type == "FULLY_PORTABLE":
            return "3-7 days"
        if portability_type == "PORTABLE_WITH_TRANSFER":
            return "7-21 days"
        return "10-30 days"

    def channel_for_scheme(row: pd.Series) -> str:
        p = str(row.get("portability_type") or "UNKNOWN").upper()
        j = str(row.get("jurisdiction_type") or "STATE").upper()
        if p == "FULLY_PORTABLE":
            return "Nearest CSC / National Portal"
        if p == "PORTABLE_WITH_TRANSFER":
            return "Origin + Destination Welfare Offices"
        if j == "STATE":
            return "State Welfare Portal / District Office"
        return "National Portal / Helpline"

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
            barrier_summary=None if pd.isna(r.get("barrier_summary")) else str(r.get("barrier_summary")),
            mechanism_summary=None if pd.isna(r.get("mechanism_summary")) else str(r.get("mechanism_summary")),
            application_steps=steps_for_scheme(r),
            required_documents=docs_for_scheme(r),
            missing_documents=missing_docs(docs_for_scheme(r)),
            time_estimate=eta_for_scheme(r),
            claim_channel=channel_for_scheme(r),
        )
        for _, r in df.iterrows()
    ]


@app.post("/auth/google")
async def google_auth(token_data: dict):
    if id_token is None or google_requests is None:
        raise HTTPException(status_code=503, detail="Google OAuth dependencies are not installed.")
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=500, detail="Google OAuth is not configured on the server.")
    token = token_data.get("token")
    if not token:
        raise HTTPException(status_code=400, detail="Token missing")
    
    try:
        # Verify the ID token
        idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), GOOGLE_CLIENT_ID)
        
        # User details from Google
        user_email = idinfo['email']
        user_name = idinfo.get('name', 'User')
        user_picture = idinfo.get('picture', '')

        return {
            "status": "success",
            "user": {
                "email": user_email,
                "name": user_name,
                "picture": user_picture
            }
        }
    except ValueError as e:
        # Invalid token
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")


@app.get("/auth/google/config")
def google_auth_config():
    return {
        "configured": bool(GOOGLE_CLIENT_ID),
        "client_id": GOOGLE_CLIENT_ID,
    }


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

    # 1. Bucket A & B: Fully Eligible
    eligible = df[df.apply(lambda r: matches_eligibility(r, req), axis=1)].copy()
    
    # 2. Bucket C: Close Matches (e.g. 15% income tolerance)
    close_matches = df[
        (df.apply(lambda r: matches_eligibility(r, req, tolerance=0.15), axis=1)) &
        (~df["scheme_id"].isin(eligible["scheme_id"]))
    ].copy()

    # Split eligible into Bucket A (Portable) and Bucket B (New State)
    origin_portable = eligible[
        (eligible["state_code"].isin([req.old_state.upper(), "ALL"])) &
        ((eligible["is_portable"] == True) | 
         (eligible["portability_type"].isin(["FULLY_PORTABLE", "PORTABLE_WITH_TRANSFER"])))
    ].copy()

    new_state_only = eligible[
        (eligible["state_code"].isin([req.new_state.upper()])) &
        (~eligible["scheme_id"].isin(origin_portable["scheme_id"]))
    ].copy()

    # Enrich all
    origin_portable = enrich_portability(origin_portable, baseline_df)
    new_state_only = enrich_portability(new_state_only, baseline_df)
    close_matches = enrich_portability(close_matches, baseline_df)

    result = {
        "input": req.model_dump(),
        "buckets": {
            "bucket_a": to_records(origin_portable.head(10), req),  # Limit for demo
            "bucket_b": to_records(new_state_only.head(10), req),
            "bucket_c": to_records(close_matches.head(5), req),
        },
        "counts": {
            "bucket_a": int(len(origin_portable)),
            "bucket_b": int(len(new_state_only)),
            "bucket_c": int(len(close_matches)),
        }
    }

    if mongo_enabled:
        background_tasks.add_task(log_search, req, result["counts"])
    return result


@app.get("/meta/options")
def options_meta():
    df = load_data()
    df["state_code"] = df["state_code"].fillna("ALL").astype(str).str.upper()

    states = sorted({s for s in df["state_code"].unique().tolist() if s and s != "ALL"})
    occupations = sorted(
        {
            title_token(token)
            for value in df.get("occupations", pd.Series(dtype=str)).tolist()
            for token in split_tokens(value)
            if token and token != "ALL"
        }
    )
    social_categories = sorted(
        {
            token
            for value in df.get("social_categories", pd.Series(dtype=str)).tolist()
            for token in split_tokens(value)
            if token and token != "ALL"
        }
    )
    benefit_domains = sorted(
        {
            title_token(str(v))
            for v in df.get("category", pd.Series(dtype=str)).fillna("").tolist()
            if str(v).strip()
        }
    )

    return {
        "states": states,
        "occupations": occupations or ["Construction", "Factory", "Agriculture", "Domestic", "Transport"],
        "social_categories": social_categories or ["GEN", "OBC", "SC", "ST", "EWS"],
        "benefit_domains": benefit_domains,
        "documents": [
            "Aadhaar Card",
            "Ration Card",
            "Voter ID",
            "PAN Card",
            "Bank Account",
            "Labour Card",
            "BPL Certificate",
            "Domicile Certificate",
            "Income Certificate",
            "Migration Proof",
        ],
        "income_ranges": ["Below ₹1 Lakh", "₹1-3 Lakh", "₹3-5 Lakh", "₹5-8 Lakh", "Above ₹8 Lakh"],
        "age_groups": ["18-25", "26-35", "36-45", "46-55", "55+"],
    }


@app.post("/schemes/discover")
async def discover_schemes(req: SchemeSearchRequest):
    df = load_data()
    baseline_df = load_portability_baseline()
    df["state_code"] = df["state_code"].fillna("ALL").astype(str).str.upper()
    scoped = df[df["state_code"].isin([req.new_state.upper(), "ALL", req.old_state.upper()])].copy()
    eligible = scoped[scoped.apply(lambda r: matches_eligibility(r, req, tolerance=0.20), axis=1)].copy()
    enriched = enrich_portability(eligible, baseline_df)
    if enriched.empty:
        return {"recommended": []}
    enriched["rank"] = (
        enriched["portability_score"].fillna(0.5) * 0.6
        + enriched["is_portable"].astype(float) * 0.2
        + (enriched["jurisdiction_type"].str.upper() == "CENTRAL").astype(float) * 0.2
    )
    ranked = enriched.sort_values(by="rank", ascending=False).head(8).copy()
    records = to_records(ranked, req)
    for rec in records:
        if rec.portability_level == "HIGH":
            rec.discovery_reason = "High portability with low migration friction."
        elif rec.portability_level == "MEDIUM":
            rec.discovery_reason = "Eligible, but requires transfer or re-verification."
        else:
            rec.discovery_reason = "Potential match; verify local office-specific criteria."
    return {"recommended": records}
