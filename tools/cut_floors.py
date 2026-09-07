#!/usr/bin/env python3
"""Cut every Room Builder floor material into one sheet the editor can blit.

A material is a 3x2 block that tiles seamlessly as a unit, so the renderer has
to pick by (tx % 3, ty % 2) -- one representative tile would visibly repeat
wrong. Block order here is sheet_floors.py's order, which is the id in
floors-catalog.png, so "floor/60" means the same thing in both.

    python3 tools/cut_floors.py     # -> public/room/sprites/floors.png
"""
import os
import sys

from PIL import Image

TILE = 32
BLOCK_W, BLOCK_H = 3, 2
COL_X = (0, 4, 8, 12)
PER_ROW = 8

INTERIORS = os.environ.get(
    "MODERN_INTERIORS",
    "/mnt/playground/Playground_V2/tilesets/modern-interiors-full")
SRC = os.path.join(INTERIORS, "1_Interiors/32x32/Room_Bulder_subfiles_32x32",
                   "Room_Builder_Floors_32x32.png")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "..", "public", "room", "sprites", "floors.png")


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


if not os.path.isfile(SRC):
    sys.exit("floors sheet not found: %s\n"
             "  Modern Interiors: https://limezu.itch.io/moderninteriors\n"
             "  export MODERN_INTERIORS=..." % SRC)

found = blocks(Image.open(SRC).convert("RGBA"))
rows = (len(found) + PER_ROW - 1) // PER_ROW
out = Image.new("RGBA", (PER_ROW * BLOCK_W * TILE, rows * BLOCK_H * TILE))
for i, blk in enumerate(found):
    out.paste(blk, ((i % PER_ROW) * BLOCK_W * TILE,
                    (i // PER_ROW) * BLOCK_H * TILE))
out.save(OUT)
print("%d floor materials -> %s (%dx%d, %d per row)"
      % (len(found), os.path.normpath(OUT), out.width, out.height, PER_ROW))
