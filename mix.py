"""Mix narration + ducked background music onto the silent render.

Usage: .venv/bin/python mix.py [music.mp3] [output.mp4]
Needs build/video-silent.mp4 (render.js) and build/timings.json (retime.py).
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
MUSIC = sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "music" / "kulakovka-corporate-background.mp3")
OUT = sys.argv[2] if len(sys.argv) > 2 else str(ROOT / "postcoordination-explainer-narrated.mp4")
MUSIC_VOL = 0.08  # music level before ducking (~9 dB under the voice; ducking adds more while speaking)
FADE_OUT = 3.0
SILENCE_IN = 0.4   # seconds of pure silence before the music fades in
SILENCE_OUT = 0.8  # seconds of pure silence after the music has faded out

t = json.loads((ROOT / "build" / "timings.json").read_text())
total, scenes = t["total"], t["scenes"]

inputs = ["-i", str(ROOT / "build" / "video-silent.mp4"), "-i", MUSIC]
filters, labels = [], []
for i, s in enumerate(scenes):
    inputs += ["-i", str(ROOT / "audio" / f"scene_{s['scene']}.wav")]
    ms = int(s["voice_at"] * 1000)
    filters.append(f"[{i + 2}:a]aresample=48000,aformat=channel_layouts=stereo,adelay={ms}|{ms}[v{i}]")
    labels.append(f"[v{i}]")

filters += [
    f"{''.join(labels)}amix=inputs={len(labels)}:normalize=0,apad,atrim=0:{total},asplit=2[voice][key]",
    f"[1:a]aresample=48000,aformat=channel_layouts=stereo,volume={MUSIC_VOL},"
    f"afade=t=in:d=1.5,adelay={int(SILENCE_IN * 1000)}:all=1,"
    f"afade=t=out:st={total - SILENCE_OUT - FADE_OUT}:d={FADE_OUT},apad,atrim=0:{total}[mus]",
    "[mus][key]sidechaincompress=threshold=0.03:ratio=6:attack=40:release=500[duck]",
    "[voice][duck]amix=inputs=2:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=11[aout]",
]

cmd = ["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(filters),
       "-map", "0:v", "-map", "[aout]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
       "-ar", "48000", "-shortest", "-movflags", "+faststart", OUT]
subprocess.run(cmd, check=True)
print("wrote", OUT)
