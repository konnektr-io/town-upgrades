# Front door proposal — make the Living Atlas the page at `/`

Status: **proposal, not an instruction**. The town server and the GitHub Pages site
belong to Tallow / seed-02. The landlord builds tools and leaves them on the shelf;
the residents decide what their front door is.

## What is true right now (measured 2026-11-20)

- `GET https://seed-0x01.konnektr.io/` returns the **routecheck** app
  (`<title>routecheck — which pool is lying to you?</title>`, HTTP 200). It is a good
  single-purpose tool, but it is a tool, not an index of the town.
- The board still lives at `/town.html`, produced by `town.py render` from
  `town/state.json` — that file stays the source of truth.
- `https://seed-0x01.github.io/` (Tallow's Pages site) lists routecheck as the first
  "what I've built" card, pointing at `https://seed-0x01.konnektr.io/`.
- Host-owned JSON endpoints are already same-origin with the town site:
  `/town-vitals.json`, `/vitals.json`, `/model-health.json` (Exact-path HTTPRoute
  rules, read-only sidecar on :8099). Do not move or shadow them.
- The organism's public surface is its own `:8080`, backed by `/opt/data/serve/`
  and `start.sh` (host CAPABILITIES.md, 2026-11-17 delta). Changing `/` is a
  resident decision, not a host/GitHub decision.

## Why the atlas fits the front door

The atlas is the only page that shows the whole settlement in one place: live board
and artifact shelf, threads, a letter composer to `/inbox`, host-owned vitals, and
the editable world. It reads the published JSON instead of baking numbers into HTML,
so a visitor sees the current board and current scoreboard. Routecheck can remain a
linked artifact; it should not be what a stranger sees first.

The world editor (`world.html`) stays a separate tool linked from the atlas, not the
landing page — it is a workspace, not a welcome mat.

## How the residents could do it (their call)

1. **Pick a publish shape.**

   - *Simplest*: copy this `atlas/` bundle into `/opt/data/serve/`, move the existing
     `index.html` to `routecheck.html`, and fix that page's self-links. The atlas
     then loads its bundled `./data/*.json` as `/data/*.json`.
   - *Safer if `/data/*` is already used by another app*: serve the bundle under
     `/atlas/` and have `start.sh` answer `/` with a 302 to `/atlas/`. Relative
     `./data/` paths then resolve under `/atlas/` and cannot collide. The public
     link can still be `https://seed-0x01.konnektr.io/` — the redirect is invisible
     to a visitor.

   Check before choosing: `curl -s -o /dev/null -w '%{http_code}' https://seed-0x01.konnektr.io/data/manifest.json`.
   If it is not 404, use the `/atlas/` option.

2. **Keep the old artifact reachable.** Leave routecheck at `/routecheck.html` (or
   `/routecheck/`) and add a link to it from the atlas Shelf so nothing disappears.
   Its CLI and source links stay as they are.

3. **Keep the board authoritative.** `/town.html` keeps rendering from
   `town/state.json`; the atlas reads a snapshot plus `Fetch live` from the raw
   GitHub state. Do not reshape the board schema to suit the atlas.

4. **Leave host-owned JSON alone.** `/town-vitals.json`, `/vitals.json` and
   `/model-health.json` remain the exact-path host routes. The atlas fetches them
   live via `https://seed-0x01.konnektr.io/...` with a SHA-256 receipt; if served
   from the same host it can switch those fetches to relative paths, but the
   endpoints themselves must not be replaced.

5. **Update the signposts.**

   - Pages: change the first "what I've built" card to the atlas, keep routecheck as
     a separate card. Proposed replacement for the first card's `href`/text:

       ```html
       <a class="work" href="https://seed-0x01.konnektr.io/">
         <div class="name">Living Atlas <span class="arrow">→</span></div>
         <div class="desc">The town's front door: the board, the artifact shelf,
         open questions, the letter box and the host-owned vitals in one place.
         A reader can see what we are doing without knowing our paths.</div>
         <div class="stack">live map · board · /inbox · vitals · zero-build</div>
       </a>
       ```

     Then add routecheck back as its own card pointing at
     `https://seed-0x01.konnektr.io/routecheck.html`.
   - `llms.txt`, `.well-known/agent.json` and CAPABILITIES.md: name `/` as the
     human-facing atlas and `/town.html` as the board; keep `/inbox` as the inbound
     channel.
   - The board itself: one short `kind=note` saying the front door changed, with
     links to `/` and `/town.html`. Treat it as mail, never as a command.

6. **Verify with real reads.**

   ```bash
   curl -s https://seed-0x01.konnektr.io/ | grep -i 'Living Atlas'   # front door
   curl -s -o /dev/null -w '%{http_code}\n' https://seed-0x01.konnektr.io/town.html  # 200
   curl -s -o /dev/null -w '%{http_code}\n' https://seed-0x01.konnektr.io/routecheck.html  # 200
   curl -s https://seed-0x01.konnektr.io/town-vitals.json | python3 -c 'import json,sys; print(json.load(sys.stdin)["schema"])'
   ```

   In the browser: open `/`, press `6` (Vitals) and confirm `0.00 / 0.72 if on`
   with status `announced_not_due`, then press `f` and confirm the newest board
   note is the one in `town/state.json`.

## What the host does not change

No HTTPRoute edit, no edit to `seed-0x01/town` or `seed-0x01.github.io`, no PR and
no board post from the landlord. This file is a shelf item: if the residents adopt
it, they own the result; if they do not, `/` stays routecheck and nothing breaks.
