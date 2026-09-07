#!/bin/sh
# Serve the editors locally so the art loop is a refresh, not a deploy.
#
# There is no middleware here, so there is no password gate and no CDN cache.
# That is the whole point: `cut_pack.py` then Ctrl+R, instead of a Vercel round
# trip that serves a stale pack.png against a fresh manifest.
#
# Bound to 10.0.0.2 (the house WireGuard address), not 0.0.0.0 — the art is
# LimeZu's and must not be reachable from outside the house.
set -e
ROOT=$(cd "$(dirname "$0")/../../public" && pwd)
exec python3 -m http.server 8970 --bind 10.0.0.2 -d "$ROOT"
