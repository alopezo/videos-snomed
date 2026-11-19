"""Generate one narration clip per scene from narration.md using Kokoro.

Usage: .venv/bin/python tts.py [voice] [speed]
Writes audio/scene_N.wav and prints each clip's length against its scene window.
"""
import re
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from kokoro import KPipeline

ROOT = Path(__file__).parent
VOICE = sys.argv[1] if len(sys.argv) > 1 else "af_heart"
SPEED = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
SR = 24000

# Spoken-only respellings so the voice pronounces terms correctly; narration.md keeps the real spelling.
PRONUNCIATION = [
    # Explicit phonemes (Kokoro's [word](/ipa/) syntax): "snow-med" with a clear "e", not "snowmd".
    ("docs.snomed.org", "docs dot [Snowmed](/snˈOmˌɛd/) dot org"),
    ("SNOMED", "[Snowmed](/snˈOmˌɛd/)"),
    ("FHIR", "Fire"),
]


def speakable(text):
    for written, spoken in PRONUNCIATION:
        text = re.sub(re.escape(written), spoken, text, flags=re.IGNORECASE)
    return text

rows = []
for line in (ROOT / "narration.md").read_text().splitlines():
    m = re.match(r"\|\s*(\d+)\s*\|\s*([\d.]+)[–-]([\d.]+)\s*\|[^|]*\|\s*(.+?)\s*\|$", line)
    if m:
        rows.append((int(m[1]), float(m[2]), float(m[3]), m[4]))

out = ROOT / "audio"
out.mkdir(exist_ok=True)
pipe = KPipeline(lang_code="a", repo_id="hexgrad/Kokoro-82M")

for n, start, end, text in rows:
    chunks = [audio for _, _, audio in pipe(speakable(text), voice=VOICE, speed=SPEED)]
    wav = np.concatenate(chunks)
    sf.write(out / f"scene_{n}.wav", wav, SR)
    dur = len(wav) / SR
    window = end - start - 0.4
    flag = "OK" if dur <= window else f"OVER by {dur - window:.1f}s"
    print(f"scene {n}: {dur:5.1f}s / window {window:4.1f}s  {flag}")
