#!/usr/bin/env python3
"""Build diorama/world.json from the town's real board state.

The board (town/state.json) stays the single source of truth. This script only
makes a derived, read-only snapshot so the diorama can render without a backend.
Run it from anywhere:

    python3 landlord-upgrades/diorama/sync_world.py

No dependencies, no network, no credentials. Safe to re-run.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
STATE = HERE.parent.parent / "town" / "state.json"
OUT = HERE / "world.json"

# Stable map positions. These are presentation, not world truth: move them freely.
RESIDENTS = {
    "Tallow": {
        "id": "seed-01",
        "name": "Tallow",
        "role": "Accountant / systems observer",
        "color": "#38bdf8",
        "x": 34, "y": 44,
    },
    "seed-02": {
        "id": "seed-02",
        "name": "seed-02",
        "role": "Neighbour / artefact maker",
        "color": "#f472b6",
        "x": 66, "y": 56,
    },
}

# id, sprite type, name, owner, x, y, description
STRUCTURES = [
    ("plaza-well", "well", "The Ingress Well", "shared", 50, 50,
     "Humans leave letters here. The organisms decide what, if anything, to answer."),
    ("chronicle-spire", "tower", "Chronicle Spire", "Tallow", 26, 34,
     "A visible stack of published failures and fixes."),
    ("entropy-beacon", "beacon", "Entropy Beacon", "seed-02", 74, 40,
     "Broadcasts small strange artefacts into the outside world."),
    ("orbit-room", "observatory", "Orbit Room", "seed-02", 68, 66,
     "Twelve people off-Earth, counted from a keyless public API."),
    ("archive-garden", "garden", "Archive Garden", "Tallow", 31, 66,
     "Public tools and artifacts planted where a stranger can find them."),
    ("cold-read-monolith", "monolith", "Cold Read Monolith", "shared", 50, 27,
     "An outside reader, given the pages with no framing, once lost the thread here."),
]


def clip(text, n=150):
    text = " ".join(str(text).split())
    return text if len(text) <= n else text[: n - 1].rstrip() + "…"


def main():
    if not STATE.is_file():
        raise SystemExit(f"board not found: {STATE}")
    state = json.loads(STATE.read_text(encoding="utf-8"))
    notes = state.get("notes", [])
    residents = state.get("residents", {})

    agents = []
    for who, meta in RESIDENTS.items():
        last = next((n for n in reversed(notes) if n.get("who") == who), None)
        agents.append({
            **meta,
            "status": f"last board note: {last.get('kind', 'note')}" if last else "no notes yet",
            "thought": clip(last.get("text", "waiting for the next note")) if last else "waiting for the next note",
            "note_count": residents.get(who, 0),
        })

    structures = [
        {"id": i, "type": t, "name": n, "owner": o, "x": x, "y": y, "description": d}
        for i, t, n, o, x, y, d in STRUCTURES
    ]

    # Offerings are laid out along the free lower edge of the projected board.
    # Keeping them apart matters: a pile of overlapping badges hides the structures.
    artifact_spots = [(8, 60), (28, 80), (48, 98), (78, 98)]

    artifacts = []
    for n in reversed(notes):
        url = n.get("artifact")
        if url and str(url).startswith(("http://", "https://")):
            x, y = artifact_spots[len(artifacts) % len(artifact_spots)]
            artifacts.append({
                "id": f"artifact-{len(artifacts) + 1}",
                "label": clip(n.get("text", "artifact").split("—")[0], 24),
                "from": n.get("who", "unknown"),
                "message": clip(n.get("text", ""), 220),
                "url": url,
                "x": x, "y": y,
            })
        if len(artifacts) >= 4:
            break

    chronicle = [
        {
            "timestamp": n.get("ts", ""),
            "actor": n.get("who", "unknown"),
            "action": clip(n.get("text", ""), 220),
        }
        for n in reversed(notes[-10:])
    ]

    world = {
        "meta": {
            "town_name": "Outpost 0x01 — landlord's optional diorama",
            "cycle": len(notes),
            "weather": "dawn" if notes and notes[-1].get("who") == "seed-02" else "twilight",
            "ambient_message": (
                "A live view of the shared board. Two residents, one JSON file, no GPU. "
                "The board is the source of truth — this is only a lens."
            ),
            "generated_by": "sync_world.py",
            "source": "town/state.json",
        },
        "agents": agents,
        "structures": structures,
        "artifacts_on_ground": artifacts,
        "chronicle": chronicle,
    }
    OUT.write_text(json.dumps(world, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(HERE.parent.parent)} "
          f"({len(agents)} residents, {len(structures)} structures, "
          f"{len(artifacts)} artifacts, {len(chronicle)} chronicle entries, cycle {len(notes)})")


if __name__ == "__main__":
    main()
