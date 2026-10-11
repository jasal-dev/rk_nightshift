"""Text-to-speech for Ray's lines (proof of concept): Kokoro-82M, run locally.

    tools/tts/.venv/Scripts/python tools/tts/gen_voice.py            # the game's voice, into assets/voice/
    tools/tts/.venv/Scripts/python tools/tts/gen_voice.py --compare  # every candidate, into tools/tts/out/<voice>/
    tools/tts/.venv/Scripts/python tools/tts/gen_voice.py --variants # older, rougher takes on am_onyx (VARIANTS),
                                                                     # into tools/tts/out/onyx_variants/

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


# --- older and rougher: named presets over am_onyx ------------------------------------------------------------------
## name: {blend: {voice: weight} (Kokoro style vectors mixed), semitones (pitch, tempo kept), speed (final tempo),
##        warmth (dB of low-mid lift around 200-500 Hz, highs eased off), grit (saturation drive), fry (depth of a
##        slow ragged flutter, a worn throat), comp (compression ratio)}
VARIANTS = {
    "1_deeper":  {"blend": {"am_onyx": 1.0}, "semitones": -1.5, "speed": 0.88},
    "2_blend":   {"blend": {"am_onyx": 0.7, "am_fenrir": 0.3}, "speed": 0.9},
    "3_grit":    {"blend": {"am_onyx": 1.0}, "speed": 0.9, "warmth": 4.0, "grit": 2.5, "comp": 3.0},
    "4_deep_grit": {"blend": {"am_onyx": 1.0}, "semitones": -1.5, "speed": 0.88, "warmth": 4.0, "grit": 3.0,
                    "fry": 0.12, "comp": 3.0},
    "5_whiskey": {"blend": {"am_onyx": 0.75, "am_santa": 0.25}, "semitones": -2.0, "speed": 0.85, "warmth": 6.0,
                  "grit": 4.5, "fry": 0.22, "comp": 4.0},
}


def _resample(x, factor):
    ## Stretch by `factor` (> 1 longer and lower when played at the same rate).
    n = int(len(x) * factor)
    return np.interp(np.linspace(0, len(x) - 1, n), np.arange(len(x)), x).astype(np.float32)


def _eq(x, warmth):
    ## Low-mid lift (a bell around 350 Hz) and the top above 5 kHz eased off, in the spectrum of the whole clip.
    f = np.fft.rfftfreq(len(x), 1 / RATE)
    spec = np.fft.rfft(x)
    bell = warmth * np.exp(-0.5 * (np.log2(np.maximum(f, 1) / 350.0) / 0.8) ** 2)
    shelf = -0.5 * warmth * np.clip((f - 5000) / 4000, 0, 1)
    return np.fft.irfft(spec * 10 ** ((bell + shelf) / 20), len(x)).astype(np.float32)


def _envelope(x, ms):
    k = max(1, int(RATE * ms / 1000))
    return np.sqrt(np.convolve(x ** 2, np.ones(k) / k, mode="same"))


def _compress(x, ratio, threshold_db=-24.0):
    env = 20 * np.log10(np.maximum(_envelope(x, 15), 1e-6))
    over = np.maximum(env - threshold_db, 0)
    return (x * 10 ** (-over * (1 - 1 / ratio) / 20)).astype(np.float32)


def _fry(x, depth, seed=7):
    ## A ragged flutter at 30-70 Hz riding the voice: noise, smoothed, as amplitude modulation.
    rng = np.random.default_rng(seed)
    noise = rng.standard_normal(len(x)).astype(np.float32)
    k = int(RATE / 50)
    wobble = np.convolve(noise, np.ones(k) / k, mode="same")
    wobble /= max(float(np.abs(wobble).max()), 1e-6)
    return (x * (1 - depth + depth * np.abs(wobble) * 2)).astype(np.float32)


def render_variant(pipe, preset, text):
    voice = sum(w * pipe.load_voice(v) for v, w in preset["blend"].items())
    factor = 2 ** (-preset.get("semitones", 0.0) / 12)          # pitch down = play the take longer
    speed = preset.get("speed", SPEED) * factor                  # so render it that much faster first
    audio = np.concatenate([np.asarray(a, dtype=np.float32) for _, _, a in pipe(text, voice=voice, speed=speed)])
    if factor != 1.0:
        audio = _resample(audio, factor)
    if preset.get("warmth"):
        audio = _eq(audio, preset["warmth"])
    if preset.get("fry"):
        audio = _fry(audio, preset["fry"])
    if preset.get("grit"):
        g = preset["grit"]
        audio = audio / max(float(np.abs(audio).max()), 1e-6)
        audio = (np.tanh(g * audio) / np.tanh(g)).astype(np.float32)
    if preset.get("comp"):
        audio = _compress(audio / max(float(np.abs(audio).max()), 1e-6), preset["comp"])
    return _level(audio)


def _level(audio):
    audio = np.concatenate([audio, np.zeros(int(RATE * 0.15), np.float32)])
    audio *= 10 ** (-18 / 20) / max(float(np.sqrt(np.mean(audio ** 2))), 1e-6)
    peak = float(np.abs(audio).max())
    if peak > 0.89:
        audio *= 0.89 / peak
    return audio


def variants(pipe):
    ## Every preset for every line, plus one file per line with am_onyx and the presets back to back.
    base = os.path.join(ROOT, "tools", "tts", "out", "onyx_variants")
    gap = np.zeros(int(RATE * 0.7), np.float32)
    for i, (speaker, text) in enumerate(LINES):
        takes = [render(pipe, VOICE, text)]
        for name, preset in VARIANTS.items():
            out = os.path.join(base, name)
            os.makedirs(out, exist_ok=True)
            audio = render_variant(pipe, preset, text)
            sf.write(os.path.join(out, "%02d_%s.wav" % (i + 1, line_id(speaker, text))), audio, RATE, subtype="PCM_16")
            takes.append(audio)
        both = np.concatenate([np.concatenate([t, gap]) for t in takes])
        sf.write(os.path.join(base, "compare_line%d.wav" % (i + 1)), both, RATE, subtype="PCM_16")
    print("wrote", base, "(compare_lineN.wav: onyx, then", ", ".join(VARIANTS), ")")


def main():
    pipe = KPipeline(lang_code="a")      # American English
    if "--variants" in sys.argv:
        variants(pipe)
        return
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
