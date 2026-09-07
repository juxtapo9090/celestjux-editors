#!/usr/bin/env python3
"""Contact sheet of the 3D wall sheet's materials, labelled by block coordinate.

sheet_walls.py and sheet_wall_block.py both read Room_Builder_Walls_32x32.png,
the FLAT family -- 54 materials of plain wall face. The editor blits the other
family, Room_Builder_3d_walls_32x32.png, whose materials carry the rail, the
corners and the junctions a room actually needs. Nothing labelled that one, so
picking a material meant guessing at coordinates.

Labels are the block's own top-left tile coordinate, because that is exactly
what cut_wall_material.py takes:

    python3 tools/sheet_walls3d.py
    python3 tools/cut_wall_material.py 8 7 jp
"""
import os

from PIL import Image, ImageDraw

TILE = 32
BLOCK_W, BLOCK_H = 8, 7
SCALE = 2
PAD = 10
LABEL_H = 14
PER_ROW = 3

INTERIORS = os.environ.get(
    "MODERN_INTERIORS",
    "/mnt/playground/Playground_V2/tilesets/modern-interiors-full")
SRC = os.path.join(INTERIORS, "1_Interiors/32x32/Room_Bulder_subfiles_32x32",
                   "Room_Builder_3d_walls_32x32.png")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                   "walls3d-catalog.png")

sheet = Image.open(SRC).convert("RGBA")
cols, rows = sheet.width // TILE, sheet.height // TILE

found = []
for by in range(0, rows - BLOCK_H + 1, BLOCK_H):
    for bx in range(0, cols - BLOCK_W + 1, BLOCK_W):
        blk = sheet.crop((bx * TILE, by * TILE,
                          (bx + BLOCK_W) * TILE, (by + BLOCK_H) * TILE))
        if not blk.getbbox() or blk.getchannel("A").getextrema()[1] < 128:
            continue
        found.append((bx, by, blk))

print("%d materials in the %dx%d tile 3d sheet" % (len(found), cols, rows))

cell_w, cell_h = BLOCK_W * TILE * SCALE, BLOCK_H * TILE * SCALE
n_rows = (len(found) + PER_ROW - 1) // PER_ROW
out = Image.new("RGBA", (PER_ROW * (cell_w + PAD) + PAD,
                         n_rows * (cell_h + LABEL_H + PAD) + PAD), (24, 26, 30, 255))
draw = ImageDraw.Draw(out)
for i, (bx, by, blk) in enumerate(found):
    cx = PAD + (i % PER_ROW) * (cell_w + PAD)
    cy = PAD + (i // PER_ROW) * (cell_h + LABEL_H + PAD)
    out.alpha_composite(blk.resize((cell_w, cell_h), Image.NEAREST), (cx, cy))
    draw.text((cx, cy + cell_h + 2), "%d %d" % (bx, by), fill=(200, 205, 215))
out.save(OUT)
print(os.path.normpath(OUT), out.size)
