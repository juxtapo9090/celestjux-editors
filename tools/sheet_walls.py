#!/usr/bin/env python3
"""Numbered catalogue of LimeZu's Room Builder wall materials.

`Room_Builder_Walls_16x16.png` is 32x40 tiles holding three groups of walls
separated by one blank tile column (measured: empty cols 10 and 21), and each
material is a 10-wide x 2-tall block -- the whole autotile run for one colour,
corners included. The catalogue draws the block whole rather than picking a
"representative" tile, because which tile is the plain face is exactly what a
person needs to see.

Reading order is row-major over blocks: left group, middle, right, then down.
That order is the id, so it must never change once anything refers to it.

    python3 tools/sheet_walls.py            # -> public/room/sprites/walls-catalog.png
"""
import os
import sys

from PIL import Image, ImageDraw

TILE = 16
BLOCK_W, BLOCK_H = 10, 2
COL_X = (0, 11, 22)              # first tile column of each group
SCALE = 2
PAD = 10
LABEL_H = 14

INTERIORS = os.environ.get(
    "MODERN_INTERIORS",
    "/mnt/playground/Playground_V2/tilesets/modern-interiors-full")
SRC = os.path.join(INTERIORS, "1_Interiors/16x16/Room_Builder_subfiles",
                   "Room_Builder_Walls_16x16.png")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "..", "public", "room", "sprites", "walls-catalog.png")


def checker(w, h, size=8):
    """Mid-grey checkerboard, so a wall's transparent gaps read as gaps."""
    im = Image.new("RGBA", (w, h), (150, 152, 158, 255))
    d = ImageDraw.Draw(im)
    for y in range(0, h, size):
        for x in range(0, w, size):
            if (x // size + y // size) % 2:
                d.rectangle([x, y, x + size - 1, y + size - 1], fill=(122, 124, 130, 255))
    return im


def blocks(sheet):
    out = []
    for by in range((sheet.height // TILE) // BLOCK_H):
        for bx in COL_X:
            blk = sheet.crop((bx * TILE, by * BLOCK_H * TILE,
                              (bx + BLOCK_W) * TILE, (by + 1) * BLOCK_H * TILE))
            if not blk.getbbox():
                continue
            if blk.getchannel("A").getextrema()[1] < 128:
                continue
            out.append(blk)
    return out


def main():
    if not os.path.isfile(SRC):
        sys.exit("walls sheet not found: %s\n"
                 "  Modern Interiors: https://limezu.itch.io/moderninteriors\n"
                 "  export MODERN_INTERIORS=..." % SRC)
    sheet = Image.open(SRC).convert("RGBA")
    found = blocks(sheet)

    cell_w = BLOCK_W * TILE * SCALE
    cell_h = BLOCK_H * TILE * SCALE
    cols = 3
    rows = (len(found) + cols - 1) // cols
    W = cols * (cell_w + PAD) + PAD
    H = rows * (cell_h + LABEL_H + PAD) + PAD

    out = Image.new("RGBA", (W, H), (24, 26, 30, 255))
    draw = ImageDraw.Draw(out)
    for i, blk in enumerate(found):
        cx = PAD + (i % cols) * (cell_w + PAD)
        cy = PAD + (i // cols) * (cell_h + LABEL_H + PAD)
        out.alpha_composite(checker(cell_w, cell_h), (cx, cy))
        out.alpha_composite(blk.resize((cell_w, cell_h), Image.NEAREST), (cx, cy))
        draw.text((cx, cy + cell_h + 2), "wall/%d" % (i + 1), fill=(200, 205, 215))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    out.save(OUT)
    print("%d wall materials -> %s (%dx%d)" % (len(found), os.path.normpath(OUT), W, H))


if __name__ == "__main__":
    main()
