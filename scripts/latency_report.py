#!/usr/bin/env python3
"""Record image-drop-to-first-audio latency via the local API."""

from __future__ import annotations

import csv
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
API = "http://localhost:8000"


def main() -> None:
    data = ROOT / "data"
    out = ROOT / "reports" / "latency_report.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    with (data / "image_manifest.csv").open(encoding="utf-8") as f:
        assets = list(csv.DictReader(f))[:5]  # first 5 for a quick report
    for row in assets:
        path = data / row["image_path"]
        t0 = time.perf_counter()
        with path.open("rb") as img, httpx.Client(timeout=300.0) as client:
            res = client.post(
                f"{API}/api/narrate/image",
                files={"image": (path.name, img, "image/png")},
            )
        ms = int((time.perf_counter() - t0) * 1000)
        ok = res.status_code == 200
        server_ms = res.json().get("latency_ms") if ok else None
        rows.append(
            {
                "asset_id": row["asset_id"],
                "http_status": res.status_code,
                "client_latency_ms": ms,
                "server_latency_ms": server_ms or "",
            }
        )
        print(row["asset_id"], res.status_code, ms, "ms")
    with out.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print("Wrote", out)


if __name__ == "__main__":
    main()
