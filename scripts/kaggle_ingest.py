#!/usr/bin/env python3
import argparse
import csv
import subprocess
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description="Download scheme datasets from Kaggle.")
    parser.add_argument("--sources", required=True, help="CSV manifest of Kaggle dataset IDs.")
    parser.add_argument("--out-dir", required=True, help="Output directory for raw files.")
    parser.add_argument(
        "--only-source-id",
        default=None,
        help="Optional source_id filter for a single dataset.",
    )
    return parser.parse_args()


def read_sources(path: Path):
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = [r for r in reader]
    return rows


def run_download(dataset_id: str, destination: Path):
    destination.mkdir(parents=True, exist_ok=True)
    cmd = [
        "kaggle",
        "datasets",
        "download",
        "-d",
        dataset_id,
        "-p",
        str(destination),
        "--unzip",
    ]
    print(f"[INFO] Downloading {dataset_id} -> {destination}")
    subprocess.run(cmd, check=True)


def main():
    args = parse_args()
    manifest = Path(args.sources)
    out_dir = Path(args.out_dir)
    rows = read_sources(manifest)

    if args.only_source_id:
        rows = [r for r in rows if r["source_id"] == args.only_source_id]
        if not rows:
            raise ValueError(f"No source found for source_id={args.only_source_id}")

    for row in rows:
        source_id = row["source_id"].strip()
        dataset_id = row["kaggle_dataset_id"].strip()
        if not dataset_id or "owner_name/" in dataset_id:
            print(f"[SKIP] {source_id}: placeholder dataset id")
            continue
        destination = out_dir / source_id
        run_download(dataset_id, destination)

    print("[DONE] Kaggle ingestion finished.")


if __name__ == "__main__":
    main()
