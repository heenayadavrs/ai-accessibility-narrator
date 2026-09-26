#!/usr/bin/env python3
"""Diff webpage extraction order against fixtures."""

from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.services.web_extract import extract_from_file  # noqa: E402


def main() -> None:
    data = ROOT / "data"
    out = ROOT / "reports" / "web_order_eval.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    with (data / "web_pages.csv").open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            path = data / "webpages" / row["fixture_path"]
            result = extract_from_file(path)
            type_seq = " -> ".join(s.type for s in result.segments)
            rows.append(
                {
                    "page_id": row["page_id"],
                    "expected_reading_order": row["expected_reading_order"],
                    "observed_types": type_seq,
                    "parse_status": result.parse_status,
                    "warning": result.warning or "",
                    "segment_count": len(result.segments),
                    "pass_manual": "",
                }
            )
            print(row["page_id"], result.parse_status, type_seq)
    with out.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print("Wrote", out)


if __name__ == "__main__":
    main()
