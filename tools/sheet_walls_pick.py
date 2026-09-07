#!/usr/bin/env python3
"""Show chosen wall materials from the 32px Room Builder sheet, big.

Same block order as sheet_walls.py, so the ids match walls-catalog.png -- but
read from Room_Builder_Walls_32x32.png, which is what the editor would
actually blit. No upscaling anywhere.

    python3 tools/sheet_walls_pick.py 2 22 26 29 32 40
"""
import os
import sys

from PIL import Image, ImageDraw

TILE = 32
BLOCK_W, BLOCK_H = 10, 2
COL_X = (0, 11, 22)
SCALE = 3
PAD = 12
LABEL_H = 16

INTERIORS = os.environ.get(
    "MODERN_INTERIORS",
    "/mnt/playground/Playground_V2/tilesets/modern-interiors-full")
SRC = os.path.join(INTERIORS, "1_Interiors/32x32/Room_Bulder_subfiles_32x32",
                   "Room_Builder_Walls_32x32.png")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "..", "walls-pick.png")


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


sheet = Image.open(SRC).convert("RGBA")
found = blocks(sheet)
print("%d wall materials in the 32px sheet" % len(found))

want = [int(a) for a in sys.argv[1:]] or list(range(1, len(found) + 1))
cell_w, cell_h = BLOCK_W * TILE * SCALE // 2, BLOCK_H * TILE * SCALE // 2
out = Image.new("RGBA", (cell_w + 2 * PAD,
                         len(want) * (cell_h + LABEL_H + PAD) + PAD), (24, 26, 30, 255))
draw = ImageDraw.Draw(out)
for i, n in enumerate(want):
    blk = found[n - 1]
    cy = PAD + i * (cell_h + LABEL_H + PAD)
    out.alpha_composite(blk.resize((cell_w, cell_h), Image.NEAREST), (PAD, cy))
    draw.text((PAD, cy + cell_h + 2), "wall/%d" % n, fill=(200, 205, 215))
out.save(OUT)
print(os.path.normpath(OUT), out.size)
