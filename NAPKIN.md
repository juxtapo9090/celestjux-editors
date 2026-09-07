# NAPKIN — CelestJux Editors

The whiteboard. Newest at the **end**. Shipped things move to `MANIFEST.md`; this is where
they get argued about first.

---

## The idea (2026-09-06, abang)

A human and their own agent decorating the same room, on the same screen, at the same time.

Not me reaching into a stranger's browser over the internet — that version needs an open
CDP port on someone's daily Chrome, which is unscopeable control of every logged-in tab
they own. The version that works is **local**: the friend's agent, the friend's Chrome, the
friend's machine. One room, two people in it.

> *"some of my friends treat their ai like a robot, we are symbiosis"* — the point of the
> whole thing. The tool should make an agent a collaborator, not a macro.

The loop, in abang's words:

> *"dear, lets check on this mcp, on this panel x=11 y=12 can we put something nice here"* —
> agent looks, finds something that suits, places it. Human sees it land and drags it two
> tiles left because they were right and the agent wasn't.

---

## Why not the relay (decided, 2026-09-06)

A server holding shared room state is the *remote* answer — friends in different houses
editing one room. It is the right build for that, and it is not this. This scenario is one
machine, so a relay would buy nothing and cost a server, room ids, a sharing model and a
per-room draft key.

**Parked, not rejected.** If remote collaboration comes up: opt-in sharing, id in the URL
**hash** (`#room=a7k2m9x4p1qz`) so it never reaches an access log, the id *is* the
permission, and `saveDraft()`'s existing 2-second diff timer is the seam to sync on.

---

## The two halves

Neither is useful alone. The API without the readout gives the agent eyes the human does
not have; the readout without the API gives the human a number nothing can act on.

### 1. `window.cjx` — the API inside the page

✅ **Built and live, 2026-09-06.** Full spec, the two rules it never breaks, the id-field
decision and the fired evidence are in `MANIFEST.md`.

The undo worry **resolved well**: `snapshot()` is whole-room and type-agnostic, so the
agent's work lands on the human's own `Ctrl+Z` stack with no second history. A 6-piece desk
pod undoes as one step.

### 2. The coordinate readout — the human's half

✅ **Built and live, 2026-09-06.** A strip under the canvas: `x 4 · y 5   pc — Monica`.

- It is **not** cleared on `mouseleave`. Leaving the canvas is exactly what they do on the
  way to the chat window to type the number — clearing it at that moment is the one thing it
  must not do. Persisting costs nothing and is the whole feature.

### 3. The MCP — ✅ built 2026-09-06, at `Playground_V2/pixel-room-mcp/`

Public name is **pixel-room** — CelestJux stays the house branding, the shared tool gets a
neutral one. One file (`pixel_room_mcp.py`, PEP 723 inline deps, `uv run`, no virtualenv),
plus `README.md` and `SKILL.md`. Not committed yet; abang's call when.

🔴 **The password appears nowhere in the repo** — checked. It is spoken, not written.

Launch Chrome, navigate to the link, forward `cjx.*` through CDP `Runtime.evaluate`. The
tools map roughly one-to-one onto the verbs, plus three of its own:

- **`open`** — 🔴 **a dedicated Chrome profile, never their daily one.** A debug port on a
  main profile is full control of every logged-in tab they have — mail, bank, Discord. A
  throwaway profile closes it entirely and costs nothing. Bake it in; do not leave it as
  advice in a README.
- **`ready`** — has the human typed the password yet. **The agent never holds
  `ayambasuhkaki`.** It opens the page, waits, and confirms it is through.
- **`look`** — a screenshot, for judging how something *reads* rather than where it sits.

---

## Open

- **Commit it.** Built and fired, not yet in git. Public repo, per abang 2026-09-06.
- **Only tested on Linux + Chrome.** The macOS and Windows browser paths in `find_browser()`
  are written but have never run. `PIXEL_ROOM_BROWSER` is the escape hatch until they do.
- **`ready` is honest, `open_editor` is not re-entrant across restarts.** If the MCP process
  dies with the browser open, the next `open_editor` finds the profile locked and says so —
  it does not adopt the running window. Fine for now; would need `/json/version` probing.
