#!/usr/bin/env python3
"""Evaluate captions on the demo image fixtures."""

from __future__ import annotations

import csv
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.config import get_settings  # noqa: E402
from app.services.captioning import CaptioningService  # noqa: E402


def main() -> None:
    settings = get_settings()
    manifest = settings.data_dir / "image_manifest.csv"
    out = ROOT / "reports" / "caption_eval.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    svc = CaptioningService(settings.caption_model_id)
    rows = []
    with manifest.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            path = settings.data_dir / row["image_path"]
            t0 = time.perf_counter()
            caption = svc.caption(path)
            ms = int((time.perf_counter() - t0) * 1000)
            rows.append(
                {
                    "asset_id": row["asset_id"],
                    "expected_caption": row["expected_caption"],
                    "model_caption": caption,
                    "latency_ms": ms,
                    "human_usefulness_1_to_5": "",
                    "factual_error_count": "",
                }
            )
            print(row["asset_id"], ms, "ms", caption[:80])
    with out.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print("Wrote", out)


if __name__ == "__main__":
    main()
