#!/usr/bin/env python3
"""Numbered index of one pack theme, cut straight out of the built atlas.

The pack names almost nothing -- pieces are `japanese_interiors/47`, not
"low table" -- so choosing furniture without a picture of the numbers is
guessing, and guessing is what produced two office layouts nobody liked. This
is the generic form of `sheet_office_singles.py`: it reads `pack.json` and
`pack.png`, so it works for every theme the packer built, and it can never
disagree with what the editor actually holds.

    python3 tools/sheet_theme.py japanese_interiors
    python3 tools/sheet_theme.py                      # lists the themes
"""
import json
import os
import sys

from PIL import Image, ImageDraw

SCALE = 2
COLS = 10
PAD = 8
LABEL_H = 12

SPRITES = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "public", "room", "sprites")


def main():
    with open(os.path.join(SPRITES, "pack.json")) as fh:
        pack = json.load(fh)
    themes = pack["themes"]

    if len(sys.argv) < 2:
        for name in sorted(themes):
            print("%-32s %d" % (name, themes[name]))
        return
    theme = sys.argv[1]
    if theme not in themes:
        sys.exit("no such theme: %s\n  run with no argument to list them" % theme)

    atlas = Image.open(os.path.join(SPRITES, "pack.png")).convert("RGBA")
    keys = [k for k in pack["sprites"] if k.startswith(theme + "/")]
    keys.sort(key=lambda k: int(k.rsplit("/", 1)[1]))

    cell_w = max(pack["sprites"][k]["w"] for k in keys) * SCALE
    cell_h = max(pack["sprites"][k]["h"] for k in keys) * SCALE
    rows = (len(keys) + COLS - 1) // COLS
    W = COLS * (cell_w + PAD) + PAD
    H = rows * (cell_h + LABEL_H + PAD) + PAD

    out = Image.new("RGBA", (W, H), (24, 26, 30, 255))
    draw = ImageDraw.Draw(out)
    for i, key in enumerate(keys):
        s = pack["sprites"][key]
        sprite = atlas.crop((s["x"], s["y"], s["x"] + s["w"], s["y"] + s["h"]))
        sprite = sprite.resize((s["w"] * SCALE, s["h"] * SCALE), Image.NEAREST)
        cx = PAD + (i % COLS) * (cell_w + PAD)
        cy = PAD + (i // COLS) * (cell_h + LABEL_H + PAD)
        # bottom-align: these sprites stand on a floor, and a top-aligned
        # index makes a tall wardrobe and a short stool look unrelated.
        out.alpha_composite(sprite, (cx + (cell_w - sprite.width) // 2,
                                     cy + cell_h - sprite.height))
        draw.text((cx, cy + cell_h + 1), key.rsplit("/", 1)[1], fill=(200, 205, 215))

    path = os.path.join(SPRITES, "theme-%s.png" % theme)
    out.save(path)
    print("%d pieces -> %s (%dx%d)" % (len(keys), os.path.normpath(path), W, H))


if __name__ == "__main__":
    main()
