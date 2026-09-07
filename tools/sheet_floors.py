#!/usr/bin/env python3
"""Numbered catalogue of LimeZu's Room Builder floor materials.

The pack names nothing. `Room_Builder_Floors_16x16.png` is 15x40 tiles holding
four columns of materials separated by one blank tile column, and every material
is a 3-wide x 2-tall block that tiles seamlessly as a unit. Without a numbered
picture of them, nobody -- me, Luc, abang -- can say "use floor 34", which is
exactly the wall the Office pack hit until `sheet_office_singles.py` existed.

Reading order is row-major over blocks: left to right across the four columns,
then down. That order is the id, so it must never change once anything refers
to it.

    python3 tools/sheet_floors.py           # -> public/room/sprites/floors-catalog.png
"""
import os
import sys

from PIL import Image, ImageDraw

TILE = 16
BLOCK_W, BLOCK_H = 3, 2          # measured, not assumed: empty tile cols 3/7/11
COL_X = (0, 4, 8, 12)            # first tile column of each material column
SCALE = 2
REPEAT = 2                       # draw the block twice over, so seams show
PAD = 10
LABEL_H = 14

INTERIORS = os.environ.get(
    "MODERN_INTERIORS",
    "/mnt/playground/Playground_V2/tilesets/modern-interiors-full")
SRC = os.path.join(INTERIORS, "1_Interiors/16x16/Room_Builder_subfiles",
                   "Room_Builder_Floors_16x16.png")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "..", "public", "room", "sprites", "floors-catalog.png")


def blocks(sheet):
    """Every non-empty 3x2 block, in id order. Yields (id, Image)."""
    rows = sheet.height // TILE
    out = []
    for by in range(rows // BLOCK_H):
        for bx in COL_X:
            box = (bx * TILE, by * BLOCK_H * TILE,
                   (bx + BLOCK_W) * TILE, (by + 1) * BLOCK_H * TILE)
            blk = sheet.crop(box)
            if not blk.getbbox():
                continue                      # blank slot: the sheet is ragged
            if blk.getchannel("A").getextrema()[1] < 128:
                continue                      # the ragged top rows are ~10%
            out.append(blk)                   # shadow overlays, not materials
    return out


def checker(w, h, size=8):
    """Mid-grey checkerboard. Several of these floors are deliberately
    translucent overlays meant to lay on top of another floor; on a flat dark
    ground they read as broken art rather than as alpha."""
    im = Image.new("RGBA", (w, h), (150, 152, 158, 255))
    d = ImageDraw.Draw(im)
    for y in range(0, h, size):
        for x in range(0, w, size):
            if (x // size + y // size) % 2:
                d.rectangle([x, y, x + size - 1, y + size - 1], fill=(122, 124, 130, 255))
    return im


def main():
    if not os.path.isfile(SRC):
        sys.exit("floors sheet not found: %s\n"
                 "  Modern Interiors: https://limezu.itch.io/moderninteriors\n"
                 "  export MODERN_INTERIORS=..." % SRC)
    sheet = Image.open(SRC).convert("RGBA")
    found = blocks(sheet)

    cell_w = BLOCK_W * TILE * REPEAT * SCALE
    cell_h = BLOCK_H * TILE * REPEAT * SCALE
    cols = 6
    rows = (len(found) + cols - 1) // cols
    W = cols * (cell_w + PAD) + PAD
    H = rows * (cell_h + LABEL_H + PAD) + PAD

    out = Image.new("RGBA", (W, H), (24, 26, 30, 255))
    draw = ImageDraw.Draw(out)
    for i, blk in enumerate(found):
        swatch = Image.new("RGBA", (blk.width * REPEAT, blk.height * REPEAT))
        for ry in range(REPEAT):
            for rx in range(REPEAT):
                swatch.paste(blk, (rx * blk.width, ry * blk.height))
        swatch = swatch.resize((cell_w, cell_h), Image.NEAREST)
        cx = PAD + (i % cols) * (cell_w + PAD)
        cy = PAD + (i // cols) * (cell_h + LABEL_H + PAD)
        out.alpha_composite(checker(cell_w, cell_h), (cx, cy))
        out.alpha_composite(swatch, (cx, cy))
        draw.text((cx, cy + cell_h + 2), "floor/%d" % (i + 1), fill=(200, 205, 215))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    out.save(OUT)
    print("%d floor materials -> %s (%dx%d)" % (len(found), os.path.normpath(OUT), W, H))


if __name__ == "__main__":
    main()
