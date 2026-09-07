#!/usr/bin/env python3
"""Crop a tile rectangle out of a stage grab and upscale it, so a 32px detail
is actually lookable-at. Tile coords, not pixels.

    python3 crop.py shot.png out.png x0 y0 x1 y1 [scale]

shot.py returns the canvas itself, so tile (0,0) is pixel (0,0) -- no page
offset to track, and no column hidden behind the layout.
"""
import sys

from PIL import Image

TILE = 32

src, dst = sys.argv[1], sys.argv[2]
x0, y0, x1, y1 = [int(a) for a in sys.argv[3:7]]
scale = int(sys.argv[7]) if len(sys.argv) > 7 else 4

im = Image.open(src).convert("RGB")
out = im.crop((x0 * TILE, y0 * TILE, x1 * TILE, y1 * TILE))
out = out.resize((out.width * scale, out.height * scale), Image.NEAREST)
out.save(dst)
print(dst, out.size)
