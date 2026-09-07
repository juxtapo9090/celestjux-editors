#!/usr/bin/env python3
"""Cut one wall material out of Room_Builder_3d_walls_32x32.png.

The sheet is 24x59 tiles holding materials in 8-wide x 7-tall blocks -- a whole
autotile run each: white rail, face, baseboard, corners, end caps, junctions.
This lifts one block out whole so the editor can blit from it by neighbour mask.

Block coordinates are the sheet's own tile coordinates of the top-left tile, so
they match what sheet_wall_block.py labels.

    python3 tools/cut_wall_material.py 8 7 jp     # LimeZu's japanese dark wall
"""
import os
import sys
from collections import Counter

from PIL import Image

T = 32
BLOCK_W, BLOCK_H = 8, 7

# Rectangles to heal, in block pixels, per material. LimeZu's block has a stray
# motif -- a dark outline round an olive square -- sitting across the bottom of
# tiles 6,6 and 7,6, which are otherwise the two tiles that patch an awkward
# corner. Rather than lose the tiles, the motif is painted out by extending the
# last clean row of each column downward, so the body's vertical striping keeps
# running. Measured: the motif is x 26..31 of tile 6,6 and x 0..5 of tile 7,6,
# both y 26..31, which is one contiguous rectangle across their shared edge.
HEAL = {
    "jp": [(6 * T + 26, 6 * T + 26, 7 * T + 6, 7 * T)],   # x0, y0, x1, y1
}

# Blank slots to fill with a solid block of the material's own rail colour.
# LimeZu ships no solid tile -- the top surface is always a thin rail, so a wall
# built from the sheet alone can never read as a raised block, which is exactly
# the "it isn't 3D" complaint. Measured: no tile in the whole 24x59 sheet is
# more than 85% one bright colour.
#
# So a set is generated on two rows appended below the block: 16 solids, one
# per combination of which sides carry the material's own dark binding edge.
# The mask is N=1 E=2 S=4 W=8 and the position is mask % 8, SOLID_ROW + mask//8,
# so the editor works the label out from where the tile sits rather than being
# told twice.
SOLID_ROW = BLOCK_H
SOLID_ROWS = 2
EDGE = 2                       # the art's own outline is two pixels

# Where this material's plain body tile is. Two generated sets are keyed off
# it and off the rail colour: 16 solid blocks and 16 body blocks, each carrying
# the material's own binding on any combination of sides. The binding sits ON
# the edge, never down the middle, because the whole point is that two tiles
# placed side by side join into one wall.
BODY = {
    "jp": (4, 4),
}
BODY_ROW = SOLID_ROW + SOLID_ROWS
BODY_ROWS = 2

# Same again, sourced from the material's rail tile instead of its body. A wall
# run seen edge-on is drawn with the rail, and a doorway cut into that run has
# to cap the rail — which nothing in the first two sets can do, because the body
# set has the binding but no rail and LimeZu's own tiles have the rail but never
# a horizontal binding.
RAIL = {
    "jp": (6, 2),
}
RAIL_ROW = BODY_ROW + BODY_ROWS
RAIL_ROWS = 2


def heal(im, rects):
    px = im.load()
    for x0, y0, x1, y1 in rects:
        if y0 == 0:
            sys.exit("cannot heal a rect touching the top edge: nothing to copy from")
        for x in range(x0, x1):
            src = px[x, y0 - 1]
            for y in range(y0, y1):
                px[x, y] = src


def rail_colour(im):
    """The material's own brightest common colour — its top surface."""
    c = Counter()
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if a > 200 and r > 200 and g > 200 and b > 200:
                c[(r, g, b)] += 1
    if not c:
        sys.exit("this block has no bright colour to make a solid tile from")
    return c.most_common(1)[0][0]


def edge_colour(im):
    """The material's own outline — its darkest colour that is actually used."""
    c = Counter()
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if a > 200:
                c[(r, g, b)] += 1
    common = [k for k, n in c.items() if n >= 200]
    if not common:
        sys.exit("this block has no colour common enough to draw an edge with")
    return min(common, key=sum)


def add_masked(im, row, fill=None, source=None):
    """16 blocks appended at `row`, one per combination of bound sides.

    The mask is N=1 E=2 S=4 W=8 and the tile's position is mask % 8, row +
    mask//8 — the position IS the name, so nothing has to be written down twice.
    `fill` paints a flat colour; `source` copies a tile of the material instead,
    which is how the body set keeps its texture.
    """
    edge = edge_colour(im) + (255,)
    px = im.load()
    out = Image.new("RGBA", (im.width, max(im.height, (row + 2) * T)))
    out.paste(im, (0, 0))
    op = out.load()
    for mask in range(16):
        tx, ty = mask % BLOCK_W, row + mask // BLOCK_W
        ox, oy = tx * T, ty * T
        for y in range(T):
            for x in range(T):
                on_edge = ((mask & 1 and y < EDGE) or (mask & 2 and x >= T - EDGE)
                           or (mask & 4 and y >= T - EDGE) or (mask & 8 and x < EDGE))
                if on_edge:
                    op[ox + x, oy + y] = edge
                elif source:
                    op[ox + x, oy + y] = px[source[0] * T + x, source[1] * T + y]
                else:
                    op[ox + x, oy + y] = fill
    return out, edge[:3]

INTERIORS = os.environ.get(
    "MODERN_INTERIORS",
    "/mnt/playground/Playground_V2/tilesets/modern-interiors-full")
SRC = os.path.join(INTERIORS, "1_Interiors/32x32/Room_Bulder_subfiles_32x32",
                   "Room_Builder_3d_walls_32x32.png")
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "public", "room", "sprites")

if not os.path.isfile(SRC):
    sys.exit("3d walls sheet not found: %s\n"
             "  Modern Interiors: https://limezu.itch.io/moderninteriors\n"
             "  export MODERN_INTERIORS=..." % SRC)

x0, y0, name = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
sheet = Image.open(SRC).convert("RGBA")
blk = sheet.crop((x0 * T, y0 * T, (x0 + BLOCK_W) * T, (y0 + BLOCK_H) * T))
if not blk.getbbox():
    sys.exit("block at %d,%d is empty -- wrong coordinates" % (x0, y0))

out = os.path.join(OUT_DIR, "wall-%s.png" % name)
rects = HEAL.get(name, [])
if rects:
    heal(blk, rects)
fill = rail_colour(blk)
blk, edge = add_masked(blk, SOLID_ROW, fill=fill + (255,))
body = BODY.get(name)
if body:
    blk, edge = add_masked(blk, BODY_ROW, source=body)
rail = RAIL.get(name)
if rail:
    blk, edge = add_masked(blk, RAIL_ROW, source=rail)
blk.save(out)
print("%s (%dx%d, %dx%d tiles + 16 solids on rows %d-%d%s%s, %d healed, "
      "fill #%02x%02x%02x edge #%02x%02x%02x)"
      % (os.path.normpath(out), blk.width, blk.height, BLOCK_W, BLOCK_H,
         SOLID_ROW, SOLID_ROW + SOLID_ROWS - 1,
         "" if body is None else " + 16 body on rows %d-%d"
         % (BODY_ROW, BODY_ROW + BODY_ROWS - 1),
         "" if rail is None else " + 16 rail on rows %d-%d"
         % (RAIL_ROW, RAIL_ROW + RAIL_ROWS - 1),
         len(rects), fill[0], fill[1], fill[2], edge[0], edge[1], edge[2]))
