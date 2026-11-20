#!/usr/bin/env bash
# Build one video end to end: (fetch music) → narration → retime → silent render → mix.
# Usage: ./build.sh <name>        (the folder videos/<name>)
set -euo pipefail
cd "$(dirname "$0")"
name="${1:?usage: ./build.sh <video-name>}"
v="videos/$name"
[[ -f "$v/video.json" ]] || { echo "missing $v/video.json" >&2; exit 1; }

# Music is never committed (third-party licenses forbid redistributing the files).
# If the track named in video.json is missing locally, download it from its source URL.
cfg() { .venv/bin/python -c 'import json,sys; print(json.load(open(sys.argv[1])).get(sys.argv[2],""))' "$v/video.json" "$1"; }
music="$(cfg music)"; music_url="$(cfg music_url)"
if [[ -n "$music" && ! -f "$music" ]]; then
  [[ -n "$music_url" ]] || { echo "missing $music and no music_url in $v/video.json" >&2; exit 1; }
  echo "fetching $music"
  mkdir -p "$(dirname "$music")"
  curl -fsSL -A "Mozilla/5.0" -o "$music.part" "$music_url" && mv "$music.part" "$music"
fi

.venv/bin/python tts.py "$v"
.venv/bin/python retime.py "$v"
node render.js "$v" "$v/build/video-silent.mp4"
.venv/bin/python mix.py "$v"
