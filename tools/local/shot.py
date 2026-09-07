#!/usr/bin/env python3
"""Grab the stage canvas itself out of the editor page.

Screenshotting the page was wrong twice over: the stage's screen position moves
when the page scrolls, and the layout clips its left edge so the first columns
could not be photographed at all. toDataURL returns the rendered room with no
page chrome, so tile (0,0) is pixel (0,0) and every tile is reachable.
"""
import asyncio, base64, json, sys
sys.path.insert(0, "/mnt/playground/Playground_V2/celestjux-editors/tools/local")
import websockets
from cjx import find_page

JS = "document.getElementById('stage').toDataURL('image/png')"


async def shot(path):
    port, ws_url = find_page()
    async with websockets.connect(ws_url, max_size=64 * 1024 * 1024) as ws:
        await ws.send(json.dumps({"id": 1, "method": "Runtime.evaluate", "params": {
            "expression": JS, "returnByValue": True}}))
        while True:
            m = json.loads(await ws.recv())
            if m.get("id") != 1:
                continue
            url = m["result"]["result"]["value"]
            open(path, "wb").write(base64.b64decode(url.split(",", 1)[1]))
            return path


print(asyncio.run(shot(sys.argv[1] if len(sys.argv) > 1 else "shot.png")))
