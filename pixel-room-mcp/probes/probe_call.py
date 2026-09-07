#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["mcp>=2", "websockets>=12.0"]
# ///
"""Fire pixel_room_mcp's own call() at the live editor, one branch at a time.

Not a mock: this imports the shipped module and drives the real page, because
the bug being fixed only ever showed up as a string built at runtime.
"""
import asyncio
import importlib.util
import json
import sys
import urllib.request
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "prm", Path(__file__).parent.parent / "pixel_room_mcp.py")
prm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prm)


def room_ws(port):
    with urllib.request.urlopen(f"http://127.0.0.1:{port}/json/list") as r:
        for t in json.load(r):
            if t.get("type") == "page" and "/room/" in t.get("url", ""):
                return t["webSocketDebuggerUrl"]
    sys.exit("no /room/ page open")


PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 9222
ws = room_ws(PORT)   # proves a /room/ tab exists; _page_ws must find it itself
prm.browser.port = PORT


async def main():
    cases = [
        ("cjx.at", [0, 12], "the prefixed name help() itself prints"),
        ("at", [0, 12], "the bare name"),
        ("draw", [], "a verb that legitimately returns undefined"),
        ("nosuchverb", [], "a verb that does not exist"),
        ("at", [], "right verb, wrong arity"),
        ("c.at; alert(1); //", [], "not an identifier"),
    ]
    for verb, args, why in cases:
        out = await prm.browser.call(verb, args)
        print("%-22r %-14s -> %s" % (verb, json.dumps(args), json.dumps(out)[:150]))
        print("%24s%s" % ("", why))

asyncio.run(main())
