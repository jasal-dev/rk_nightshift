"""Text-to-speech for spoken lines: Kokoro-82M, run locally. How to voice more lines: docs/voice-recording.md.

    tools/tts/.venv/Scripts/python tools/tts/gen_voice.py            # every line in tools/tts/lines.json that has no
                                                                     # clip yet, into assets/voice/ (--force: all)
    tools/tts/.venv/Scripts/python tools/tts/gen_voice.py --list scripts/rooms/squad_room.gd
                                                                     # a script's literal main.say() lines, as JSON
                                                                     # rows for lines.json
    tools/tts/.venv/Scripts/python tools/tts/gen_voice.py --compare  # every candidate, into tools/tts/out/<voice>/
    tools/tts/.venv/Scripts/python tools/tts/gen_voice.py --variants # older, rougher takes on am_onyx (VARIANTS),
                                                                     # into tools/tts/out/onyx_variants/

Setup (once): py -3.12 -m venv tools/tts/.venv, then in it: pip install torch --index-url
https://download.pytorch.org/whl/cpu; pip install kokoro soundfile. The venv and tools/tts/out/ aren't in git.

Kokoro (hexgrad/Kokoro-82M) is Apache-2.0, weights and code, so its output can go in a game that's sold.
Each line is a clip assets/voice/<speaker>/<id>.ogg, id = the first 12 hex digits of sha1("<speaker>|<text>"), so
the game finds it from the text alone (Audio.voice_clip) and a changed line simply has no clip until it's re-rendered.
assets/voice/lines.json lists them. Clips are mono 24 kHz Ogg Vorbis, levelled to about -18 dBFS RMS (roughly -16 LUFS
for speech) with peaks under -1 dBFS.
"""
import hashlib
import json
import os
import re
import sys

import numpy as np
import soundfile as sf
from kokoro import KPipeline

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
VOICE = "am_onyx"          ## the base for the candidate comparisons (--compare, --variants)
CANDIDATES = ["am_onyx", "am_fenrir", "am_michael"]
SPEED = 0.92               ## a touch slow: tired, a quarter past midnight
RATE = 24000
LINES_FILE = os.path.join(ROOT, "tools", "tts", "lines.json")    ## [[speaker, text, where?], ...], text exactly as shown
MANIFEST = os.path.join(ROOT, "assets", "voice", "lines.json")
## The cast: speaker id (as Main passes it; Main.say() is "ray") -> the VARIANTS preset that is their voice.
SPEAKERS = {"ray": "2_blend"}


def load_lines():
    with open(LINES_FILE, encoding="utf-8") as f:
        return [(str(row[0]), str(row[1])) for row in json.load(f)]     # row[2], if any: where the line is


LINES = load_lines()


## Spoken forms: game text -> what the voice should say, for numbers and names the text-to-speech gets wrong. Only the
## audio changes; the clip's id still comes from the game text. Longer keys first where they overlap.
PRONOUNCE = {
    "555-0147": "five five five, oh one four seven",
    "$8,000": "eight thousand dollars",
    ".38": "thirty-eight",
    ".45": "forty-five",
    "Room 214": "Room two-fourteen",
    "6400 block": "sixty-four hundred block",
    "the 110": "the one-ten",
    "The 110": "The one-ten",
    "1 of 3": "one of three",
    "Reyes, 34.": "Reyes, thirty-four.",
}
ACRONYMS = {"LAPD", "DA", "IA", "ID", "TV", "UV", "GPS", "ER"}    ## all-caps words said letter by letter


def spoken(text):
    for k in sorted(PRONOUNCE, key=len, reverse=True):
        text = text.replace(k, PRONOUNCE[k])
    # signs and stamps written in capitals (BLUE NOTE, PAID, HOMICIDE) are words, not letters to spell out
    return re.sub(r"\b[A-Z]{2,}\b", lambda m: m.group(0) if m.group(0) in ACRONYMS else m.group(0).capitalize(), text)


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
    audio = np.concatenate([np.asarray(a, dtype=np.float32) for _, _, a in pipe(spoken(text), voice=voice, speed=speed)])
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


CALL = re.compile(r'(?<![\w.])(?:main\.)?(say|narrate)\(')
STRING = re.compile(r'"((?:[^"\\]|\\.)*)"')


def _calls(src):
    ## (line number, function, argument source) for every say( / narrate( call, the argument up to its closing paren.
    func = ""
    starts = [0]
    for line in src.split("\n"):
        starts.append(starts[-1] + len(line) + 1)
    for m in CALL.finditer(src):
        line_start = src.rfind("\n", 0, m.start()) + 1
        if src[:m.start()].endswith("func ") or "#" in src[line_start:m.start()]:    # a definition or a comment
            continue
        i, depth, in_str = m.end(), 1, False
        while i < len(src) and depth:
            ch = src[i]
            if in_str:
                if ch == "\\":
                    i += 1
                elif ch == '"':
                    in_str = False
            elif ch == '"':
                in_str = True
            elif ch in "([{":
                depth += 1
            elif ch in ")]}":
                depth -= 1
            i += 1
        line_no = next(n for n in range(len(starts)) if starts[n + 1] > m.start())
        head = src[:m.start()]
        fm = list(re.finditer(r'^(?:static )?func (\w+)', head, re.M))
        func = fm[-1].group(1) if fm else ""
        yield line_no + 1, func, src[m.end():i - 1]


def list_says(path):
    ## Ray's lines in a script: every say() and narrate() argument's string literals, so `"a" if x else "b"` and
    ## `["a", "b"].pick_random()` give each text. Strings handed to another call inside the argument (a flag name) are
    ## skipped. Calls whose text is built at run time (a variable, `%`, `+`) are printed to stderr with their line and
    ## function, to be read and added by hand. stdout: rows for lines.json, ["ray", text, "<file>:<line> <function>"].
    src = open(path, encoding="utf-8").read()
    found = []
    for line_no, func, arg in _calls(src):
        texts = []
        for m in STRING.finditer(arg):
            before = arg[:m.start()].rstrip()
            if re.search(r'(\w\(|[\w\])]\[)$', before):    # an argument to another call (Game.flag("x")) or a key (d["k"])
                continue
            texts.append(json.loads('"%s"' % m.group(1)))
        bare = STRING.sub('""', arg)
        dynamic = not texts or re.search(r'%|\+|\b(?!if\b|else\b|and\b|or\b|not\b|pick_random\b)[A-Za-z_]\w*\s*(?:\[|$)', bare)
        if dynamic:
            sys.stderr.write("by hand: %s:%d %s(): %s\n" % (path, line_no, func, " ".join(arg.split())))
            continue
        for t in texts:
            if all(t != f[0] for f in found):
                found.append((t, line_no, func))
    where = os.path.basename(path)
    print("[\n" + ",\n".join("\t" + json.dumps(["ray", t, "%s:%d %s" % (where, n, f)], ensure_ascii=False)
                             for t, n, f in found) + "\n]")


def main():
    if "--list" in sys.argv:
        list_says(sys.argv[sys.argv.index("--list") + 1])
        return
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
    force = "--force" in sys.argv
    manifest = {}
    made = 0
    for speaker, text in LINES:
        if speaker not in SPEAKERS:
            sys.exit("no voice cast for speaker '%s' (SPEAKERS; see docs/voice-recording.md)" % speaker)
        preset = SPEAKERS[speaker]
        lid = line_id(speaker, text)
        rel = "assets/voice/%s/%s.ogg" % (speaker, lid)
        path = os.path.join(ROOT, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if force or not os.path.exists(path):
            sf.write(path, render_variant(pipe, VARIANTS[preset], text), RATE, format="OGG", subtype="VORBIS")
            made += 1
        manifest[lid] = {"speaker": speaker, "text": text, "file": "res://" + rel, "voice": "kokoro:" + preset}
    # clips no line points at any more (its text changed, it went, or an older format): remove them and their .import
    stale = 0
    used = {m["file"] for m in manifest.values()}
    for speaker in SPEAKERS:
        folder = os.path.join(ROOT, "assets", "voice", speaker)
        for name in os.listdir(folder) if os.path.isdir(folder) else []:
            if name.endswith((".wav", ".ogg")) and "res://assets/voice/%s/%s" % (speaker, name) not in used:
                for f in (name, name + ".import"):
                    if os.path.exists(os.path.join(folder, f)):
                        os.remove(os.path.join(folder, f))
                stale += 1
    with open(MANIFEST, "w", encoding="utf-8", newline="\n") as f:
        json.dump(manifest, f, indent="\t", ensure_ascii=False)
        f.write("\n")
    print("%d lines, %d rendered, %d stale clips removed" % (len(manifest), made, stale))


if __name__ == "__main__":
    main()
