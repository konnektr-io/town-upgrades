#!/usr/bin/env python3
"""Snapshot the host-owned public vitals endpoints with a receipt.

    env -u PYTHONPATH python3 atlas/tools/fetch_vitals.py

Writes raw bytes to atlas/data/{town-vitals,vitals,model-health}.json and a
sha256/timestamp manifest. The page can also fetch these endpoints directly;
these files are the offline fallback.
"""
import hashlib
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parents[1] / "data"
ORIGIN = "https://seed-0x01.konnektr.io"
PATHS = {
    "town-vitals.json": "/town-vitals.json",
    "vitals.json": "/vitals.json",
    "model-health.json": "/model-health.json",
}
UA = "outpost-atlas/1.0 (+public read-only vitals)"


def main():
    BASE.mkdir(parents=True, exist_ok=True)
    manifest = {
        "origin": ORIGIN,
        "fetched_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "files": {},
    }
    for name, path in PATHS.items():
        req = urllib.request.Request(ORIGIN + path, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=15) as r:
            raw = r.read()
        (BASE / name).write_bytes(raw)
        payload = json.loads(raw)
        manifest["files"][name] = {
            "source": ORIGIN + path,
            "sha256": hashlib.sha256(raw).hexdigest(),
            "bytes": len(raw),
            "schema": payload.get("schema"),
            "iso_utc": payload.get("iso_utc"),
        }
    (BASE / "vitals-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print("vitals snapshot:", json.dumps(manifest["files"], indent=2))


if __name__ == "__main__":
    main()
