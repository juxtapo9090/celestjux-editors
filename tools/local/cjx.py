#!/usr/bin/env python3
"""Run JavaScript inside the editor page pixelmag has open.

pixelmag's own verbs are one call per action, which is fine for a nudge and
absurd for laying forty tatami mats. This talks the same CDP the gateway talks,
so a loop that calls `cjx.place(...)` forty times is one round trip -- and every
mutation still goes through cjx, so it lands on abang's own Ctrl+Z stack.

The debug port changes every launch and Chrome writes no DevToolsActivePort
here, so it is discovered from the listening sockets rather than passed in.

    python3 tools/local/cjx.py 'cjx.describe()'
    python3 tools/local/cjx.py -f script.js
"""
import asyncio
import json
import re
import subprocess
import sys
import urllib.error
import urllib.request

import websockets


def chrome_ports():
    """Every listening debug port, whichever Chromium is holding the editor.

    pixelmag launches Chrome, but the editor opens just as well in abang's own
    Brave -- and matching only the word "chrome" made the tool answer "no editor
    page found" while the page was sitting right there in Brave.
    """
    out = subprocess.run(["ss", "-lntp"], capture_output=True, text=True).stdout
    ports = []
    for line in out.splitlines():
        if not any(b in line for b in ("chrome", "chromium", "brave")):
            continue
        m = re.search(r"127\.0\.0\.1:(\d+)", line)
        if m:
            ports.append(int(m.group(1)))
    return sorted(set(ports))


def find_page():
    for port in chrome_ports():
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/json", timeout=2) as r:
                targets = json.load(r)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
            continue
        pages = [t for t in targets
                 if t.get("type") == "page" and t.get("webSocketDebuggerUrl")]
        for t in pages:
            if "/room/" in t.get("url", ""):
                return port, t["webSocketDebuggerUrl"]
    raise SystemExit("no editor page found — is pixelmag's browser open on /room/ ?")


async def run(expression):
    port, ws_url = find_page()
    async with websockets.connect(ws_url, max_size=64 * 1024 * 1024) as ws:
        await ws.send(json.dumps({"id": 1, "method": "Runtime.evaluate", "params": {
            "expression": expression, "returnByValue": True, "awaitPromise": True}}))
        while True:
            m = json.loads(await ws.recv())
            if m.get("id") != 1:
                continue
            r = m.get("result", {})
            if "exceptionDetails" in r:
                d = r["exceptionDetails"]
                raise SystemExit("page threw: %s %s" % (
                    d.get("text", ""),
                    (d.get("exception") or {}).get("description", "")))
            return r.get("result", {}).get("value")


def main():
    if len(sys.argv) >= 3 and sys.argv[1] == "-f":
        with open(sys.argv[2]) as fh:
            expression = fh.read()
    elif len(sys.argv) >= 2:
        expression = sys.argv[1]
    else:
        sys.exit(__doc__)
    print(json.dumps(asyncio.run(run(expression)), indent=2, default=str))


if __name__ == "__main__":
    main()
