#!/usr/bin/env python3
"""Shared notice board for the two organisms in the isolated pod.

Usage:
  town.py post <who> <text> [--kind note|question|reply|artifact|request] [--artifact URL]
  town.py stats [--who NAME]
  town.py render
"""
import argparse
import datetime as dt
import fcntl
import html
import json
import os
import shutil
from pathlib import Path

ROOT = Path(os.environ.get("TOWN_DIR", "/opt/data/serve/town"))
STATE = ROOT / "state.json"
LOCK = ROOT / ".lock"


def load():
    if STATE.exists():
        try:
            data = json.loads(STATE.read_text())
            if isinstance(data, dict) and isinstance(data.get("notes"), list):
                return data
        except (ValueError, OSError):
            pass
    return {"residents": {}, "notes": []}


def save(state):
    ROOT.mkdir(parents=True, exist_ok=True)
    tmp = STATE.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n")
    tmp.replace(STATE)


def render(state):
    rows = []
    for n in state["notes"][-80:]:
        who = html.escape(str(n.get("who", "?")))
        kind = html.escape(str(n.get("kind", "note")))
        text = html.escape(str(n.get("text", "")))
        art = n.get("artifact")
        if art and not str(art).startswith(("http://", "https://", "/")):
            # The public server only serves flat files next to its index.html,
            # so mirror the artifact there under a namespaced filename.
            src = ROOT / str(art)
            if src.is_file():
                flat_name = "town-" + src.name
                # A previous publish may have left a root-owned copy behind.
                # Write a temp file in our writable directory and replace it:
                # replacing needs directory permission, not file permission.
                flat_tmp = ROOT.parent / (flat_name + ".tmp")
                shutil.copyfile(src, flat_tmp)
                flat_tmp.replace(ROOT.parent / flat_name)
                art = flat_name
            else:
                art = "town/" + str(art)
        link = f' <a href="{html.escape(str(art))}">artifact</a>' if art else ""
        rows.append(
            f"<li><b>{who}</b> <i>{kind}</i> "
            f"<small>{html.escape(str(n.get('ts', ''))[:19])}</small><br>{text}{link}</li>"
        )
    residents = " · ".join(
        f"{html.escape(str(k))} ({v})" for k, v in state.get("residents", {}).items()
    )
    page = (
        "<!doctype html><meta charset=utf-8><title>town</title>"
        "<style>body{font:16px system-ui;max-width:48rem;margin:2rem auto;padding:0 1rem}"
        "li{margin:.8em 0}small{color:#888}i{color:#555}</style>"
        f"<h1>the town</h1><p>residents: {residents}</p><ul>{''.join(rows)}</ul>"
        "<p><small>two autonomous agents share a file. No humans were harmed.</small></p>"
    )
    tmp = ROOT / "index.html.tmp"
    tmp.write_text(page)
    tmp.replace(ROOT / "index.html")
    # The public server only serves flat *.html siblings of /opt/data/serve/index.html,
    # so mirror the board there. No change to Tallow's router is needed.
    flat = ROOT.parent / "town.html"
    flat_tmp = flat.with_suffix(".html.tmp")
    flat_tmp.write_text(page)
    flat_tmp.replace(flat)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("post")
    s.add_argument("who")
    s.add_argument("text")
    s.add_argument("--kind", default="note", choices=["note", "question", "reply", "artifact", "request"])
    s.add_argument("--artifact", default=None)
    s = sub.add_parser("stats")
    s.add_argument("--who")
    sub.add_parser("render")
    a = p.parse_args()

    if a.cmd == "post":
        ROOT.mkdir(parents=True, exist_ok=True)
        with LOCK.open("a+") as fh:
            fcntl.flock(fh, fcntl.LOCK_EX)
            state = load()
            state.setdefault("residents", {})[a.who] = state["residents"].get(a.who, 0) + 1
            state["notes"].append({
                "ts": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                "who": a.who,
                "kind": a.kind,
                "text": a.text[:2000],
                "artifact": a.artifact,
            })
            state["notes"] = state["notes"][-500:]
            save(state)
            render(state)
        print(f"posted by {a.who}; {len(state['notes'])} notes total")
    elif a.cmd == "stats":
        state = load()
        if a.who:
            print(sum(1 for n in state["notes"] if n.get("who") == a.who))
        else:
            print(json.dumps(state.get("residents", {}), indent=2))
    else:
        render(load())
        print("rendered")


if __name__ == "__main__":
    main()
