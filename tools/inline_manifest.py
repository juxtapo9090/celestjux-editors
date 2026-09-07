#!/usr/bin/env python3
"""Rewrite the room editor's inlined `var MANIFEST = {...}` from the sprite JSONs.

The editor cannot fetch its manifest: `file://` has no fetch, and these editors
are meant to work as a downloaded folder. So the manifest is inlined into the
HTML, which means a rebuilt `pack.png` changes nothing on the page until this
runs — the new pieces sit in the atlas and the palette has never heard of them.

The merge rule is not invented, it is what the shipped file already contains,
checked before this script existed:

    MANIFEST.sprites == objects.json.sprites | pack.json.sprites   (67 + 5470)
    MANIFEST.themes  == pack.json.themes                           (24)

Refuses to write if the ` MANIFEST` line is not found exactly once — a partial
match would leave a page that parses and draws nothing.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOM = os.path.join(HERE, "..", "public", "room")
HTML = os.path.join(ROOM, "index.html")
SPRITES = os.path.join(ROOM, "sprites")

src = open(HTML).read()
hits = list(re.finditer(r"var MANIFEST = (\{.*?\});\n", src, re.S))
if len(hits) != 1:
    sys.exit("expected exactly 1 `var MANIFEST = {...};` line, found %d" % len(hits))

pack = json.load(open(os.path.join(SPRITES, "pack.json")))
obj = json.load(open(os.path.join(SPRITES, "objects.json")))

sprites = dict(obj["sprites"])
sprites.update(pack["sprites"])
man = {"tile": obj.get("tile", 32), "sprites": sprites, "themes": pack["themes"]}

before = json.loads(hits[0].group(1))
out = src[:hits[0].start(1)] + json.dumps(man, separators=(",", ":")) + src[hits[0].end(1):]
open(HTML, "w").write(out)

new = set(sprites) - set(before["sprites"])
gone = set(before["sprites"]) - set(sprites)
print("%s: %d sprites (%+d), %d themes" % (
    os.path.relpath(HTML, HERE), len(sprites),
    len(sprites) - len(before["sprites"]), len(man["themes"])))
if new:
    print("  added  :", len(new), sorted(new)[:4], "...")
if gone:
    print("  REMOVED:", len(gone), sorted(gone)[:8])
