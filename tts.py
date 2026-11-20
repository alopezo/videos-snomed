"""Generate one narration clip per scene from <video>/narration.md using Kokoro.

Usage: .venv/bin/python tts.py videos/<name> [voice] [speed]
Voice and speed default to the values in <video>/video.json.
Writes <video>/audio/scene_N.wav and prints each clip's length against its scene window.
"""
import json
import re
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from kokoro import KPipeline

SR = 24000

# Spoken-only respellings so the voice pronounces terms correctly; narration.md keeps the real spelling.
# Shared by every video: add terms here once.
PRONUNCIATION = [
    # Explicit phonemes (Kokoro's [word](/ipa/) syntax): "snow-med" with a clear "e", not "snowmd".
    ("docs.snomed.org", "docs dot [Snowmed](/snˈOmˌɛd/) dot org"),
    ("SNOMED", "[Snowmed](/snˈOmˌɛd/)"),
    ("FHIR", "Fire"),
    ("PES", "P E S"),  # problem, etiology, signs and symptoms — spelled out, not "peez"
]


def speakable(text):
    for written, spoken in PRONUNCIATION:
        # Whole words only, so short acronyms like "PES" don't match inside "types".
        text = re.sub(rf"\b{re.escape(written)}\b", spoken, text, flags=re.IGNORECASE)
    return text


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    video = Path(sys.argv[1])
    cfg = json.loads((video / "video.json").read_text())
    voice = sys.argv[2] if len(sys.argv) > 2 else cfg.get("voice", "af_heart")
    speed = float(sys.argv[3]) if len(sys.argv) > 3 else float(cfg.get("speed", 1.0))

    rows = []
    for line in (video / "narration.md").read_text().splitlines():
        m = re.match(r"\|\s*(\d+)\s*\|\s*([\d.]+)[–-]([\d.]+)\s*\|[^|]*\|\s*(.+?)\s*\|$", line)
        if m:
            rows.append((int(m[1]), float(m[2]), float(m[3]), m[4]))

    out = video / "audio"
    out.mkdir(exist_ok=True)
    pipe = KPipeline(lang_code="a", repo_id="hexgrad/Kokoro-82M")

    for n, start, end, text in rows:
        chunks = [audio for _, _, audio in pipe(speakable(text), voice=voice, speed=speed)]
        wav = np.concatenate(chunks)
        sf.write(out / f"scene_{n}.wav", wav, SR)
        dur = len(wav) / SR
        window = end - start - 0.4
        flag = "OK" if dur <= window else f"OVER by {dur - window:.1f}s"
        print(f"scene {n}: {dur:5.1f}s / window {window:4.1f}s  {flag}")


if __name__ == "__main__":
    main()
