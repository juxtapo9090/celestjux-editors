#!/usr/bin/env python3
"""Grab the stage canvas itself out of the editor page.

Screenshotting the page was wrong twice over: the stage's screen position moves
when the page scrolls, and the layout clips its left edge so the first columns
could not be photographed at all. toDataURL returns the rendered room with no
page chrome, so tile (0,0) is pixel (0,0) and every tile is reachable.
"""
import asyncio, base64, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cjx import run

JS = "canvas.toDataURL('image/png')"


async def shot(path):
    url = await run(JS)
    open(path, "wb").write(base64.b64decode(url.split(",", 1)[1]))
    return path


print(asyncio.run(shot(sys.argv[1] if len(sys.argv) > 1 else "shot.png")))
