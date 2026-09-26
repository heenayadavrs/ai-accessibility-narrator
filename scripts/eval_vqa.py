#!/usr/bin/env python3
"""Evaluate VQA on seeded gold pairs."""

from __future__ import annotations

import csv
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.config import get_settings  # noqa: E402
from app.services.vqa import VQAService  # noqa: E402


def main() -> None:
    settings = get_settings()
    pairs = settings.data_dir / "vqa_pairs.csv"
    manifest = {
        r["asset_id"]: r["image_path"]
        for r in csv.DictReader((settings.data_dir / "image_manifest.csv").open(encoding="utf-8"))
    }
    out = ROOT / "reports" / "vqa_eval.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    svc = VQAService(settings.vqa_model_id)
    rows = []
    with pairs.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            path = settings.data_dir / manifest[row["asset_id"]]
            t0 = time.perf_counter()
            answer = svc.ask(path, row["question"])
            ms = int((time.perf_counter() - t0) * 1000)
            rows.append(
                {
                    "asset_id": row["asset_id"],
                    "question": row["question"],
                    "expected_answer": row["expected_answer"],
                    "model_answer": answer,
                    "latency_ms": ms,
                    "relevant_yes_no": "",
                }
            )
            print(row["asset_id"], row["question"][:40], "->", answer[:60])
    with out.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print("Wrote", out)


if __name__ == "__main__":
    main()
