#!/usr/bin/env python3
"""Pack every LimeZu "single" object into one atlas the editor can browse.

Forked from `room-editor/tools/cut_pack.py` (Selene's, left untouched) to add a
second source: Modern Office. Interiors sorts its 5470 singles into one folder
per theme; Modern Office ships its 339 flat in a single folder, so the walk has
to handle both shapes rather than one.

Each single is trimmed to its opaque bounding box first — the declared canvas
carries padding, and an untrimmed sprite floats above the floor it is supposed
to be standing on.

Writes `sprites/pack.png` + `sprites/pack.json`. The editor does NOT fetch that
JSON — `file://` cannot fetch, so the manifest is inlined into the HTML. Run
`inline_manifest.py` after this or the new pieces exist in the atlas and the
page has no idea they are there.
"""
import json
import os
import sys

from PIL import Image

INTERIORS = os.environ.get(
    "MODERN_INTERIORS",
    "/mnt/playground/Playground_V2/tilesets/modern-interiors-full")
OFFICE = os.environ.get(
    "MODERN_OFFICE",
    "/mnt/playground/Playground_V2/tilesets/modern-office-full")
# Whole desk units cut straight out of LimeZu's own Office_Design_2 furniture
# layer. Assembling one from singles cannot be exact — the pack composes on a
# free canvas, so five of nine measured pieces sit off the 32px grid. Cut as
# one piece, the composition is exact by construction.
DESKSETS = os.environ.get(
    "OFFICE_DESKSETS",
    "/mnt/playground/Playground_V2/tilesets/office-desksets")
# The same units with the chair cut off. A chair baked into the sprite is one
# an agent can never sit on, so an agent's desk is built from a bare unit plus
# a real chair object; the chaired ones are for background rows.
DESKBARE = os.environ.get(
    "OFFICE_DESKBARE",
    "/mnt/playground/Playground_V2/tilesets/office-deskbare")

# (path, theme) — a theme of None means "one folder per theme underneath".
SOURCES = [
    (os.path.join(INTERIORS, "1_Interiors/32x32/Theme_Sorter_Singles_32x32"), None),
    (os.path.join(OFFICE, "4_Modern_Office_singles/32x32"), "office"),
    (os.path.join(DESKSETS, "32x32"), "deskset"),
    (os.path.join(DESKBARE, "32x32"), "deskbare"),
]

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "public", "room", "sprites")
ATLAS_W = 2048


def theme_name(d):
    """'12_Kitchen_Singles_32x32' -> 'kitchen'"""
    s = d.split("_", 1)[1] if d[0].isdigit() else d
    s = s.replace("_Singles_32x32", "").replace("_SIngles_32x32", "")
    s = s.replace("_32x32", "")
    return s.lower().strip("_")


def take(path, theme, items):
    """Trim and key every PNG in one folder. `..._47.png` -> `<theme>/47`."""
    for f in sorted(os.listdir(path)):
        if not f.endswith(".png"):
            continue
        im = Image.open(os.path.join(path, f)).convert("RGBA")
        box = im.getbbox()
        if not box:
            continue                          # a blank single: nothing to place
        # box[0] is how much transparent margin the artist left on the left of
        # the canvas. Trimming it and forgetting it draws every piece flush
        # against its tile's left edge, which is what tears a multi-part table
        # apart: piece 216 loses 4px, its neighbour starts on the tile boundary,
        # and the gap is exactly the margin that was thrown away.
        # The bottom margin carries height: a monitor meant to stand ON a desk
        # is drawn 16px up its canvas. Trim that away and bottom-align what is
        # left, and the monitor lands on the floor instead.
        items.append((theme + "/" + f.rsplit("_", 1)[-1][:-4], theme,
                      im.crop(box), box[0], im.height - box[3]))


def load_all():
    items = []
    for src, fixed in SOURCES:
        if not os.path.isdir(src):
            sys.exit(
                "pack source not found: %s\n"
                "  Modern Interiors: https://limezu.itch.io/moderninteriors\n"
                "  Modern Office:    https://limezu.itch.io/modernoffice\n"
                "  export MODERN_INTERIORS=... / MODERN_OFFICE=..." % src)
        if fixed:
            take(src, fixed, items)
            continue
        for d in sorted(os.listdir(src)):
            p = os.path.join(src, d)
            if os.path.isdir(p):
                take(p, theme_name(d), items)
    return items


def shelf_pack(items):
    """Sort tall-first and lay shelves. Good enough: the waste is a few percent
    and the alternative is a bin packer nobody will ever tune."""
    items.sort(key=lambda t: -t[2].height)
    x = y = shelf_h = 0
    placed = []
    for key, theme, im, dx, dy in items:
        w, h = im.size
        if x + w > ATLAS_W:
            x = 0
            y += shelf_h
            shelf_h = 0
        placed.append((key, theme, im, x, y, dx, dy))
        x += w
        shelf_h = max(shelf_h, h)
    return placed, y + shelf_h


def main():
    items = load_all()
    placed, height = shelf_pack(items)
    atlas = Image.new("RGBA", (ATLAS_W, height), (0, 0, 0, 0))
    sprites, themes = {}, {}
    for key, theme, im, x, y, dx, dy in placed:
        atlas.paste(im, (x, y))
        sprites[key] = {"x": x, "y": y, "w": im.width, "h": im.height,
                        "frames": 1, "sheet": 1}
        if dx:
            sprites[key]["dx"] = dx
        if dy:
            sprites[key]["dy"] = dy
        themes.setdefault(theme, []).append(key)

    os.makedirs(OUT_DIR, exist_ok=True)
    png = os.path.join(OUT_DIR, "pack.png")
    atlas.save(png, optimize=True)
    with open(os.path.join(OUT_DIR, "pack.json"), "w") as f:
        json.dump({"tile": 32, "sprites": sprites,
                   "themes": {k: len(v) for k, v in sorted(themes.items())}}, f)

    print("%d sprites  atlas %dx%d  %.1f MB  %d themes"
          % (len(sprites), ATLAS_W, height,
             os.path.getsize(png) / 1e6, len(themes)))
    for t in sorted(themes):
        print("  %-28s %d" % (t, len(themes[t])))


main()
