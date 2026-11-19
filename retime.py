"""Stretch scenes in index.base.html so each fits its narration clip; write index.html + build/timings.json.

Usage: .venv/bin/python retime.py
Run tts.py first so audio/scene_N.wav exists.
"""
import json
import re
from pathlib import Path

import soundfile as sf

ROOT = Path(__file__).parent
LEAD = 0.5   # seconds from scene start to narration start
FIRST_LEAD = 1.2  # a little longer before the very first line, so the voice doesn't start instantly
TAIL = 1.0   # seconds after narration ends before the next scene (includes 0.5s fade-out)
OUTRO = 3.0  # extra hold at the very end: room for the music fade-out + final silence after the last line

html = (ROOT / "index.base.html").read_text()
bounds = [(float(a), float(b)) for a, b in re.findall(r"<!-- S\d+ [^>]*?([\d.]+)-([\d.]+) -->", html)]

scenes, t = [], 0.0
for i, (a, b) in enumerate(bounds):
    clip = sf.info(str(ROOT / "audio" / f"scene_{i + 1}.wav")).duration
    lead = FIRST_LEAD if i == 0 else LEAD
    new_len = max(b - a, lead + clip + TAIL)
    if i == len(bounds) - 1:
        new_len += OUTRO
    scenes.append({"scene": i + 1, "old": [a, b], "start": round(t, 3), "end": round(t + new_len, 3),
                   "voice_at": round(t + lead, 3), "clip": round(clip, 3)})
    t += new_len
total = round(t, 3)


def remap(x, is_end):
    for s in scenes:
        a, b = s["old"]
        if a <= x < b or (is_end and a < x <= b):
            k = (s["end"] - s["start"]) / (b - a)
            return round(s["start"] + (x - a) * k, 2)
    last = scenes[-1]  # past the last scene boundary (e.g. data-e="77")
    return round(last["end"] + (x - last["old"][1]), 2)


html = re.sub(r'data-s="([\d.]+)"', lambda m: f'data-s="{remap(float(m[1]), False)}"', html)
html = re.sub(r'data-e="([\d.]+)"', lambda m: f'data-e="{remap(float(m[1]), True)}"', html)
html = re.sub(r"const TOTAL=[\d.]+;", f"const TOTAL={total};", html)
(ROOT / "index.html").write_text(html)

(ROOT / "build").mkdir(exist_ok=True)
(ROOT / "build" / "timings.json").write_text(json.dumps({"total": total, "scenes": scenes}, indent=2))
for s in scenes:
    print(f"scene {s['scene']}: {s['start']:6.2f}–{s['end']:6.2f}  voice {s['voice_at']:6.2f} (+{s['clip']:.1f}s)")
print("TOTAL", total)
