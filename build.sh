#!/usr/bin/env bash
# Build one video end to end: narration → retime → silent render → mix.
# Usage: ./build.sh <name>        (the folder videos/<name>)
set -euo pipefail
cd "$(dirname "$0")"
name="${1:?usage: ./build.sh <video-name>}"
v="videos/$name"
[[ -f "$v/video.json" ]] || { echo "missing $v/video.json" >&2; exit 1; }

.venv/bin/python tts.py "$v"
.venv/bin/python retime.py "$v"
node render.js "$v" "$v/build/video-silent.mp4"
.venv/bin/python mix.py "$v"
