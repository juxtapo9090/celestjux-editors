#!/usr/bin/env python3
"""Find which tiles of a tileset a promo screenshot is actually built from.

Slides every 32x32 tile of the sheet over the image and reports exact pixel
matches with their positions. Answers "do we own this art" with evidence
rather than by eye.

    python3 tools/match_tiles.py <sheet.png> <shot.png> [x0 y0 x1 y1]
"""
import os
import sys
from collections import defaultdict

from PIL import Image

T = 32

sheet = Image.open(sys.argv[1]).convert("RGBA")
shot = Image.open(sys.argv[2]).convert("RGB")
if len(sys.argv) > 6:
    box = tuple(int(a) for a in sys.argv[3:7])
else:
    box = (0, 0, shot.width, shot.height)

tiles = {}
for ty in range(sheet.height // T):
    for tx in range(sheet.width // T):
        t = sheet.crop((tx * T, ty * T, (tx + 1) * T, (ty + 1) * T))
        if t.getchannel("A").getextrema()[0] < 255:
            continue                      # only fully opaque tiles can match
        tiles[(tx, ty)] = t.convert("RGB").tobytes()

hits = defaultdict(list)
for y in range(box[1], box[3] - T + 1):
    for x in range(box[0], box[2] - T + 1):
        key = shot.crop((x, y, x + T, y + T)).tobytes()
        for pos, data in tiles.items():
            if data == key:
                hits[pos].append((x, y))

print("%d opaque tiles in %s" % (len(tiles), os.path.basename(sys.argv[1])))
if not hits:
    print("no exact match in", box)
for pos in sorted(hits, key=lambda p: -len(hits[p])):
    print("tile %2d,%-2d  %3d placements  first at %s"
          % (pos[0], pos[1], len(hits[pos]), hits[pos][0]))
