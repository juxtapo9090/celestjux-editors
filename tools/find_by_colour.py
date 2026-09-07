#!/usr/bin/env python3
"""Find which japanese_interiors singles carry the green of a reference crop.

Point it at a region of a promo screenshot; it reads the colours that region
actually uses, then reports every 32x32 single whose opaque pixels overlap
those colours -- so a piece is identified by its palette, not by eyeballing a
133-piece contact sheet.
"""
import os
import sys
from collections import Counter

from PIL import Image

SRC = ("/mnt/playground/Playground_V2/tilesets/modern-interiors-full/"
       "1_Interiors/32x32/Theme_Sorter_Singles_32x32/"
       "20_Japanese_Interiors_Singles_32x32")

ref = Image.open(sys.argv[1]).convert("RGBA")
box = tuple(int(a) for a in sys.argv[2:6])
crop = ref.crop(box)

greens = Counter()
for px in crop.getdata():
    r, g, b, a = px
    if a > 200 and g > r + 20 and g > b + 20:
        greens[(r, g, b)] += 1
print("greens in the reference:", greens.most_common(6))
want = {c for c, _ in greens.most_common(6)}


def near(c):
    return any(abs(c[0] - w[0]) <= 12 and abs(c[1] - w[1]) <= 12
               and abs(c[2] - w[2]) <= 12 for w in want)


hits = []
for f in sorted(os.listdir(SRC)):
    if not f.endswith(".png"):
        continue
    im = Image.open(os.path.join(SRC, f)).convert("RGBA")
    bbox = im.getbbox()
    if not bbox:
        continue
    n = 0
    opaque = 0
    for r, g, b, a in im.crop(bbox).getdata():
        if a <= 200:
            continue
        opaque += 1
        if near((r, g, b)):
            n += 1
    if n:
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        hits.append((n / opaque, n, f, w, h))

hits.sort(reverse=True)
for frac, n, f, w, h in hits[:20]:
    print("%5.1f%%  %4d px  %-46s %dx%d" % (frac * 100, n, f, w, h))
