"""Text-to-speech for Ray's lines (proof of concept): Kokoro-82M, run locally.

    tools/tts/.venv/Scripts/python tools/tts/gen_voice.py            # the game's voice, into assets/voice/
    tools/tts/.venv/Scripts/python tools/tts/gen_voice.py --compare  # every candidate, into tools/tts/out/<voice>/

Setup (once): py -3.12 -m venv tools/tts/.venv, then in it: pip install torch --index-url
https://download.pytorch.org/whl/cpu; pip install kokoro soundfile. The venv and tools/tts/out/ aren't in git.

Kokoro (hexgrad/Kokoro-82M) is Apache-2.0, weights and code, so its output can go in a game that's sold.
Each line is a clip assets/voice/<speaker>/<id>.wav, id = the first 12 hex digits of sha1("<speaker>|<text>"), so
the game finds it from the text alone (Audio.voice_clip) and a changed line simply has no clip until it's re-rendered.
assets/voice/lines.json lists them. Clips are mono 24 kHz 16-bit, levelled to about -18 dBFS RMS (roughly -16 LUFS
for speech) with peaks under -1 dBFS.
"""
import hashlib
import json
import os
import sys

import numpy as np
import soundfile as sf
from kokoro import KPipeline

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
VOICE = "am_onyx"          ## Ray: the one wired into the game
CANDIDATES = ["am_onyx", "am_fenrir", "am_michael"]
SPEED = 0.92               ## a touch slow: tired, a quarter past midnight
RATE = 24000

## (speaker, text), exactly as the game shows them: Ray's first lines in the squad room (SquadRoom.intro()).
LINES = [
    ("ray", "Quarter past midnight. The squad room is mine again."),
    ("ray", "Danny Reyes. Two nights cold, and the lieutenant wants it closed by Friday."),
    ("ray", "First, the file. I locked it away like a careful man."),
    ("ray", "Then I hid the key like a paranoid one."),
]


def line_id(speaker, text):
    return hashlib.sha1(("%s|%s" % (speaker, text)).encode("utf-8")).hexdigest()[:12]


def render(pipe, voice, text):
    audio = np.concatenate([np.asarray(a, dtype=np.float32) for _, _, a in pipe(text, voice=voice, speed=SPEED)])
    audio = np.concatenate([audio, np.zeros(int(RATE * 0.15), np.float32)])      # a breath of tail
    rms = float(np.sqrt(np.mean(audio ** 2)))
    audio *= 10 ** (-18 / 20) / max(rms, 1e-6)
    peak = float(np.abs(audio).max())
    if peak > 0.89:                                                               # -1 dBFS
        audio *= 0.89 / peak
    return audio


def main():
    pipe = KPipeline(lang_code="a")      # American English
    if "--compare" in sys.argv:
        for voice in CANDIDATES:
            out = os.path.join(ROOT, "tools", "tts", "out", voice)
            os.makedirs(out, exist_ok=True)
            for i, (speaker, text) in enumerate(LINES):
                sf.write(os.path.join(out, "%02d_%s.wav" % (i + 1, line_id(speaker, text))),
                         render(pipe, voice, text), RATE, subtype="PCM_16")
            print("wrote", out)
        return
    manifest = {}
    for speaker, text in LINES:
        lid = line_id(speaker, text)
        rel = "assets/voice/%s/%s.wav" % (speaker, lid)
        os.makedirs(os.path.join(ROOT, "assets", "voice", speaker), exist_ok=True)
        sf.write(os.path.join(ROOT, rel), render(pipe, VOICE, text), RATE, subtype="PCM_16")
        manifest[lid] = {"speaker": speaker, "text": text, "file": "res://" + rel, "voice": "kokoro:" + VOICE}
    with open(os.path.join(ROOT, "assets", "voice", "lines.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(manifest, f, indent="\t", ensure_ascii=False)
        f.write("\n")
    print("wrote %d clips" % len(manifest))


if __name__ == "__main__":
    main()
