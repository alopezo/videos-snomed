# AGENTS.md

Guidance for AI coding agents (and humans) working in this repo.
See `README.md` for the user-facing overview.

## What this repo is

A code-only pipeline that turns a video folder into a narrated vertical video (1080×1920, 30 fps). Each folder holds an HTML scene file, a narration script and a config.

- **Multi-video.** Each video lives in `videos/<name>/`. The scripts at the repo root (`tts.py`, `retime.py`, `render.js`, `mix.py`, `build.sh`) are shared and take the video folder as their first argument.
- **No media is committed.** `*.mp4`, `*.mp3`, `*.wav`, `*.png`, every `audio/` and `build/` folder, and the root `music/` library are gitignored. Never add them, and never force-add them.

## Where things go

| Shared (repo root) | Per video (`videos/<name>/`) |
|--------------------|------------------------------|
| Pipeline scripts, `build.sh` | `video.json`: title, voice, speed, music, output |
| `PRONUNCIATION` fixes in `tts.py` | `narration.md`: one row per scene |
| Timing and mix settings in `retime.py` / `mix.py` | `index.base.html`: the scenes (the source of truth) |
| `music/` library (gitignored) | `index.html`: generated, but committed |
| README, AGENTS.md, LICENSE | `audio/`, `build/`, output MP4: generated, gitignored |

When something becomes useful to more than one video, such as a style, a helper or a pronunciation fix, move it to the shared layer. Don't copy it into each folder.

## Creating a new video ("make a video about X")

1. `mkdir videos/<kebab-name>`. Copy `video.json`, `narration.md` and `index.base.html` from an existing video as a starting point.
2. Write the scenes in `index.base.html`, with one comment `<!-- S<n> <label> <start>-<end> -->` per scene, in order. Keep the shared look: the CSS variables, 540×960 canvas and footer.
3. Write `narration.md` with the same scene numbers and times. Budget about 2 spoken words per second.
4. Set `video.json`. `music` is a path relative to the repo root (`music/<file>.mp3`), and `output` is the file name inside the video folder.
5. Ask the user before downloading a music track. Credit it in the README's music table.
6. Run `./build.sh <name>`. Check frames with `node render.js videos/<name> x 3,20,42`.
7. Add the video to the README's "Videos" table.

## Pipeline (what `build.sh` runs)

1. `tts.py videos/<name>`: `narration.md` → `audio/scene_N.wav`. "OVER" in its output is expected, because the next step stretches the scene.
2. `retime.py videos/<name>`: `index.base.html` + clip lengths → `index.html` + `build/timings.json`.
3. `render.js videos/<name> videos/<name>/build/video-silent.mp4`: takes about 2.5 min for about 100 s of video.
4. `mix.py videos/<name>`: produces the final MP4 with voice, ducked music and −16 LUFS loudness.

## Rules of thumb

- **Edit `index.base.html`, not `index.html`.** `retime.py` regenerates `index.html`.
- `narration.md` rows must keep the shape `| n | start–end | budget | text |`, because `tts.py` parses them with a regex. The scene count must match `index.base.html`.
- Write SNOMED CT terms in their real spelling in `narration.md`. Spoken-only fixes go in `PRONUNCIATION` in `tts.py`, using Kokoro's `[word](/ipa/)` syntax. Current fixes: SNOMED → /snˈOmˌɛd/ ("snow-med", with a clear *e*), FHIR → "Fire".
- To check a pronunciation without listening, print the phonemes with `KPipeline(lang_code="a").g2p(text)[0]`.
- Don't hard-code timings in a video folder. The knobs live at the top of `retime.py` and `mix.py`.
- Verify audio by measuring, not by guessing. Use `ffmpeg -af ebur128` for integrated loudness (target −16 LUFS), and `volumedetect` on short segments for silences and ducking. Music should sit about 8 dB under the voice when no one is speaking.

## Content accuracy

- Concept IDs and terms shown on screen must be real SNOMED CT concepts. Validate any new ones before adding them, for example against a Snowstorm/FHIR terminology server.
- Expressions must follow SNOMED CT compositional grammar.
- Base the content on the relevant guide on docs.snomed.org and cite it.

## Conventions

- Code, comments, commit messages and docs are in English.
- Video folder names are kebab-case and describe the topic, for example `postcoordination` or `ecl-basics`.
- Python 3.10–3.12, using the `.venv` in the repo root. Node 18+, with Playwright from `package.json`.
- Keep scripts small, dependency-light and runnable from the repo root.
