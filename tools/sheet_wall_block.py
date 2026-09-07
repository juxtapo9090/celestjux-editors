#!/usr/bin/env python3
"""Blow up one wall material's autotile block, one labelled cell per tile.

sheet_walls.py shows the block whole, which answers "what colour is it" and
not "which tile is the left end". This numbers every tile in the 10x2 run so a
neighbour-mask can be mapped to an index by looking rather than by guessing.

    python3 tools/sheet_wall_block.py 40
"""
import os
import sys

from PIL import Image, ImageDraw

TILE = 32
BLOCK_W, BLOCK_H = 10, 2
COL_X = (0, 11, 22)
SCALE = 5
PAD = 14
LABEL_H = 18

INTERIORS = os.environ.get(
    "MODERN_INTERIORS",
    "/mnt/playground/Playground_V2/tilesets/modern-interiors-full")
SRC = os.path.join(INTERIORS, "1_Interiors/32x32/Room_Bulder_subfiles_32x32",
                   "Room_Builder_Walls_32x32.png")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "wall-block.png")


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


n = int(sys.argv[1]) if len(sys.argv) > 1 else 1
blk = blocks(Image.open(SRC).convert("RGBA"))[n - 1]

cell = TILE * SCALE
W = BLOCK_W * (cell + PAD) + PAD
H = BLOCK_H * (cell + LABEL_H + PAD) + PAD
out = Image.new("RGBA", (W, H), (30, 32, 38, 255))
draw = ImageDraw.Draw(out)
for ty in range(BLOCK_H):
    for tx in range(BLOCK_W):
        t = blk.crop((tx * TILE, ty * TILE, (tx + 1) * TILE, (ty + 1) * TILE))
        cx = PAD + tx * (cell + PAD)
        cy = PAD + ty * (cell + LABEL_H + PAD)
        out.alpha_composite(Image.new("RGBA", (cell, cell), (90, 92, 100, 255)), (cx, cy))
        out.alpha_composite(t.resize((cell, cell), Image.NEAREST), (cx, cy))
        draw.text((cx, cy + cell + 3), "%d,%d" % (tx, ty), fill=(210, 214, 224))
out.save(OUT)
print("wall/%d ->" % n, os.path.normpath(OUT), out.size)
