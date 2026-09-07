#!/usr/bin/env python3
"""Snapshot the room the editor is holding, or push a snapshot back into it.

The editor's own Save is a browser download and its draft is one localStorage
slot that dies with the profile. This writes real files, from here, with no
click -- so an experiment that goes wrong is one load away from undone.

Snapshots land in public/room/rooms/, which the editor already serves, so a
saved room is also reachable at http://<host>/room/rooms/<name>.json

    python3 tools/local/room_io.py save              # timestamped
    python3 tools/local/room_io.py save before-pond  # named
    python3 tools/local/room_io.py list
    python3 tools/local/room_io.py load before-pond
"""
import asyncio
import datetime
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cjx import run

ROOMS = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     "..", "..", "public", "room", "rooms")


def path_for(name):
    return os.path.normpath(os.path.join(ROOMS, name + ".json"))


def save(name):
    raw = asyncio.run(run("JSON.stringify(room)"))
    if not raw:
        sys.exit("the editor is holding no room -- nothing to save")
    room = json.loads(raw)
    if name is None:
        stamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
        name = "%s_%s" % (room.get("name", "room"), stamp)
    os.makedirs(ROOMS, exist_ok=True)
    out = path_for(name)
    with open(out, "w") as fh:
        json.dump(room, fh, indent=1)
    print("%s (%d objects, %dx%d)"
          % (out, len(room["objects"]),
             room["grid"]["cols"], room["grid"]["rows"]))


def load(name):
    src = path_for(name)
    if not os.path.isfile(src):
        sys.exit("no such snapshot: %s\n  have: %s"
                 % (src, ", ".join(names()) or "(none)"))
    with open(src) as fh:
        room = json.load(fh)
    got = asyncio.run(run("loadRoom(%s); draw(); room.name + ' ' + "
                          "room.objects.length" % json.dumps(room)))
    print("loaded %s -> editor now holds: %s" % (src, got))


def names():
    if not os.path.isdir(ROOMS):
        return []
    return sorted(f[:-5] for f in os.listdir(ROOMS) if f.endswith(".json"))


def main():
    verb = sys.argv[1] if len(sys.argv) > 1 else ""
    arg = sys.argv[2] if len(sys.argv) > 2 else None
    if verb == "save":
        save(arg)
    elif verb == "load":
        if arg is None:
            sys.exit("load needs a snapshot name -- have: %s"
                     % (", ".join(names()) or "(none)"))
        load(arg)
    elif verb == "list":
        for n in names():
            print(n)
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
