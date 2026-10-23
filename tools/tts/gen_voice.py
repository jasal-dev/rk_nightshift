"""Text-to-speech for spoken lines: Kokoro-82M, run locally. How to voice more lines: docs/voice-recording.md.

    tools/tts/.venv/Scripts/python tools/tts/gen_voice.py            # every line in tools/tts/lines.json that has no
                                                                     # clip yet, into assets/voice/ (--force: all)
    tools/tts/.venv/Scripts/python tools/tts/gen_voice.py --list scripts/rooms/squad_room.gd
                                                                     # a script's literal main.say() lines, as JSON
                                                                     # rows for lines.json
    tools/tts/.venv/Scripts/python tools/tts/gen_voice.py --compare  # every candidate, into tools/tts/out/<voice>/
    tools/tts/.venv/Scripts/python tools/tts/gen_voice.py --casting  # three voices for each other Case 1 character
                                                                     # (CASTING), into tools/tts/out/casting_case1/
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
## Everyone but Ray has a 0.3 s beat between sentences ("sentence_pause"; the user's call, 2026-10-16).
## The cast: speaker id (as Main passes it: say() and narrate() are "ray", voice(..., "doyle") is "doyle") -> their
## voice, picked by the user by ear. Same keys as the presets below (VARIANTS); "from" says which proposal it was.
## Keep this in step with the cast table in docs/voice-recording.md. Changing a voice means re-rendering its lines
## (--force), so don't, unless the user asks.
SPEAKERS = {
    "ray":   {"blend": {"am_onyx": 0.7, "am_fenrir": 0.3}, "speed": 0.9, "from": "VARIANTS 2_blend"},
    "doyle": {"blend": {"af_kore": 1.0}, "speed": 0.95, "sentence_pause": 0.3, "from": "CASTING doyle B"},
    "nina":  {"blend": {"af_heart": 1.0}, "speed": 0.95, "sentence_pause": 0.3, "from": "CASTING nina A"},
    "sal":   {"blend": {"am_santa": 1.0}, "speed": 0.9, "sentence_pause": 0.3, "from": "CASTING sal A"},
    "tiny":  {"blend": {"am_adam": 1.0}, "semitones": -3.0, "speed": 0.85, "sentence_pause": 0.3, "from": "CASTING tiny A"},
    "vance": {"blend": {"bm_george": 1.0}, "speed": 0.88, "lang": "b", "sentence_pause": 0.3, "from": "CASTING vance A"},
    "otis":  {"blend": {"am_liam": 1.0}, "speed": 1.0, "sentence_pause": 0.3, "from": "CASTING otis B"},
    # Cases 2-5, picked 2026-10-11, not voiced yet
    "shah":  {"blend": {"bf_emma": 1.0}, "speed": 1.0, "lang": "b", "sentence_pause": 0.3, "from": "CASTING_REST shah C"},
    "park":  {"blend": {"af_bella": 1.0}, "speed": 1.05, "sentence_pause": 0.3, "from": "CASTING_REST park A"},
    "rosa":  {"blend": {"af_jessica": 1.0}, "semitones": -1.5, "speed": 0.95, "sentence_pause": 0.3, "from": "CASTING_REST rosa B"},
    "heck":  {"blend": {"am_echo": 0.6, "am_puck": 0.4}, "speed": 1.05, "sentence_pause": 0.3, "from": "CASTING_REST heck C"},
    "devin": {"blend": {"am_puck": 1.0}, "speed": 0.9, "sentence_pause": 0.3, "from": "CASTING_REST devin C"},
    "brielle": {"blend": {"af_jessica": 1.0}, "speed": 1.05, "sentence_pause": 0.3, "from": "CASTING_REST brielle B"},
    "cabbie": {"blend": {"am_michael": 1.0}, "semitones": -1.5, "sentence_pause": 0.3, "from": "CASTING_REST cabbie B"},
    "pearl": {"blend": {"af_bella": 1.0}, "speed": 1.0, "sentence_pause": 0.3, "from": "CASTING_REST pearl A"},
    "morty": {"blend": {"am_michael": 1.0}, "semitones": -2.5, "speed": 0.85, "fry": 0.1, "sentence_pause": 0.3, "from": "CASTING_REST morty A"},
    "charlie": {"blend": {"bm_daniel": 1.0}, "speed": 0.95, "lang": "b", "sentence_pause": 0.3, "from": "CASTING_REST charlie C"},
    "preacher": {"blend": {"am_eric": 1.0}, "semitones": -3.0, "speed": 0.82, "warmth": 4.0, "fry": 0.08, "sentence_pause": 0.3, "from": "CASTING_REST preacher C"},
    "doss":  {"blend": {"am_puck": 1.0}, "speed": 1.05, "sentence_pause": 0.3, "from": "CASTING_REST doss A"},
    "courtney": {"blend": {"af_nova": 1.0}, "speed": 1.1, "sentence_pause": 0.3, "from": "CASTING_REST courtney A"},
    "andre": {"blend": {"am_puck": 1.0}, "semitones": 1.0, "speed": 1.05, "sentence_pause": 0.3, "from": "CASTING_REST andre A"},
    "crane": {"blend": {"am_michael": 1.0}, "speed": 0.95, "sentence_pause": 0.3, "from": "CASTING_REST crane A"},
    "ike":   {"blend": {"am_echo": 1.0}, "speed": 1.0, "sentence_pause": 0.3, "from": "CASTING_REST ike C"},
    "owen":  {"blend": {"am_eric": 1.0}, "semitones": 1.0, "sentence_pause": 0.3, "from": "CASTING_REST owen C"},
    "teo":   {"blend": {"am_michael": 1.0}, "semitones": -1.5, "speed": 0.85, "warmth": 2.0, "sentence_pause": 0.3, "from": "CASTING_REST teo B"},
    "mara":  {"blend": {"af_river": 1.0}, "speed": 1.0, "sentence_pause": 0.3, "from": "CASTING_REST mara A"},
    "brenner": {"blend": {"am_eric": 0.5, "am_santa": 0.5}, "semitones": -2.0, "speed": 0.88, "warmth": 2.0, "sentence_pause": 0.3, "from": "CASTING_REST brenner B"},
    "okafor": {"blend": {"af_aoede": 1.0}, "speed": 0.95, "sentence_pause": 0.3, "from": "CASTING_REST okafor A"},
    "danny": {"blend": {"am_michael": 1.0}, "semitones": 1.0, "speed": 1.0, "sentence_pause": 0.3, "from": "CASTING_REST danny C"},
    "pryce": {"blend": {"am_eric": 0.5, "am_michael": 0.5}, "semitones": -1.5, "speed": 0.92, "warmth": 2.0, "sentence_pause": 0.3, "from": "CASTING_REST pryce C"},
    "haskell": {"blend": {"am_eric": 1.0}, "speed": 1.05, "sentence_pause": 0.3, "from": "CASTING_REST haskell A"},
    "whitaker": {"blend": {"am_michael": 0.5, "am_puck": 0.5}, "speed": 1.05, "sentence_pause": 0.3, "from": "CASTING_REST whitaker B"},
}


## Direction for single lines, by (speaker, game text), as the user asked for it by ear:
##   "say": what Kokoro gets instead of the game text, with "[0.8]" for a pause of 0.8 s (the game text is unchanged)
##   "gain_db": louder or quieter than the speaker's other lines (a "(low)" line)
## A line with direction is re-rendered when its direction changes (the manifest keeps a "sig").
DIRECTION = {
    ("ray", "Rain. Of course it's raining."): {"say": "Rain. [0.9] Of course it's raining."},
    ("ray", "One of three. One of three what?"): {"say": "One of three. [0.9] One of three what?"},
    ("ray", "Coffee. Coffee."): {"say": "Coffee. [1.0] Coffee."},
    ("tiny", "(low) Five minutes."): {"gain_db": -9.0},
    ("brielle", "Reported. One star. Creep."): {"say": "Reported. [0.6] One star. [0.6] Creep."},
    ("heck", "No. No, man. I yelled at him. I didn't, I would never."):
        {"say": "No. [0.5] No, man. [0.6] I yelled at him. [0.6] I didn't, [0.4] I would never."},
    ("devin", "No. No, no. What happened? Was it a crash?"):
        {"say": "No. [0.6] No, [0.4] no. [0.7] What happened? [0.7] Was it a crash?"},
    ("devin", "Jesus. Who would... He's a Glide driver. He gives people water bottles."):
        {"say": "Jesus. [0.8] Who would... [0.8] He's a Glide driver. [0.5] He gives people water bottles."},
    ("devin", "I panicked! My roommate's dead!"): {"say": "I panicked! [0.7] My roommate's dead!"},
    # "No." before an abbreviation is read as "number": say it on its own
    ("otis", "No. LA River, Elysian Valley, under the Fletcher Drive bridge. Delivery rider, twenty-four, Owen Tate. Down in the channel."):
        {"say": "No. [0.35] LA River, Elysian Valley, under the Fletcher Drive bridge. Delivery rider, twenty-four, Owen Tate. Down in the channel."},
}


def take_sig(preset, direction):
    ## What a clip was rendered with; a change re-renders it.
    return hashlib.sha1(json.dumps([preset, direction], sort_keys=True).encode("utf-8")).hexdigest()[:10]


def chatterbox_sigs():
    ## {line id: signature} of the lines acted with Chatterbox (tools/tts/gen_chatterbox.py); this script leaves them alone
    path = os.path.join(ROOT, "tools", "tts", "chatterbox_lines.json")
    if not os.path.exists(path):
        return {}
    cfg = json.load(open(path, encoding="utf-8"))
    return {line_id(e["speaker"], e["text"]):
            "cb" + hashlib.sha1(json.dumps([e, cfg["reference"]], sort_keys=True).encode("utf-8")).hexdigest()[:10]
            for e in cfg["lines"]}


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
    "KJAZZ": "K-Jazz",
    "Done with HH.": "Done with HushHush.",
    "WEDDINGS_OCT": "Weddings October",
    "Dodgers, 2020": "Dodgers, twenty twenty",
    "since 1957": "since nineteen fifty-seven",
    "11 × 2,500": "eleven times twenty-five hundred",
    "50/50": "fifty-fifty",
    "6:12 p.m.": "six-twelve p.m.",
    "12:14 a.m.": "twelve-fourteen a.m.",
    "1:10 a.m.": "one-ten a.m.",
    "No. 734": "number seven thirty-four",
    "number 734": "number seven thirty-four",
    "8 x 10": "eight by ten",
    "911": "nine one one",
    "$40": "forty dollars",
    "Avenue 43": "Avenue forty-three",
    "A6": "A-six",
    "$19.99": "nineteen ninety-nine",
    "District 13": "District thirteen",
    "8KXD392": "eight, K, X, D, three, nine, two",
    "4K0": "four, K, zero",
    "in '96": "in ninety-six",
    "Los Angeles": "Loss Angelus",       # said "lawss AN-juh-lus"; spelled right, Kokoro gives "lohz AIN-jelz"
}
ACRONYMS = {"LAPD", "LA", "LAX", "DA", "IA", "ID", "TV", "UV", "GPS", "ER", "SD", "DUI", "CSI", "IRS", "MP"}    ## all-caps words said letter by letter


def spoken(text):
    # stage directions aren't said: sounds in asterisks ("*beep*"), asides in brackets ("(muffled)")
    text = " ".join(re.sub(r"\*[^*]*\*|\([^)]*\)", " ", text).split())
    for k in sorted(PRONOUNCE, key=len, reverse=True):
        text = text.replace(k, PRONOUNCE[k])
    # years said the way people say them: 1954 is "nineteen fifty-four", 2011 "twenty eleven"
    text = re.sub(r"(?<![\d$.,:])\b(19[0-9]{2}|20[0-2][0-9])\b(?![\d,.:]\d)", lambda m: _year(int(m.group(1))), text)
    # signs and stamps written in capitals (BLUE NOTE, PAID, HOMICIDE) are words, not letters to spell out; acronyms
    # are spelled out, dotted (L.A.P.D), because Kokoro reads some bare ones as words ("LAPD" came out "lapt", "LAX" "lax")
    return re.sub(r"\b[A-Z]{2,}\b", lambda m: ".".join(m.group(0)) if m.group(0) in ACRONYMS else m.group(0).capitalize(),
                  text)


_ONES = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen " \
        "seventeen eighteen nineteen".split()
_TENS = "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()


def _two(n):
    return _ONES[n] if n < 20 else _TENS[n // 10] + ("-" + _ONES[n % 10] if n % 10 else "")


def _year(y):
    hi, lo = divmod(y, 100)
    if lo == 0:
        return _two(hi) + " hundred"
    if hi == 20 and lo < 10:
        return "two thousand " + _ONES[lo]
    return _two(hi) + " " + ("oh-" + _ONES[lo] if lo < 10 else _two(lo))


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


PAUSE = re.compile(r"\[(\d+(?:\.\d+)?)\]")
SENTENCE_END = re.compile(r"(?<=[.!?])\s+(?=\S)")
NOT_AN_END = {"Mr.", "Mrs.", "Ms.", "Dr.", "Lt.", "Sgt.", "St.", "Ave.", "Jr.", "Sr.", "vs.", "Mt."}


def sentences(text):
    ## `text` split into sentences, but not after a title or an initial ("Mr. Vance", "D. Clark", "W.B.", "No. 734").
    out = []
    for piece in SENTENCE_END.split(text.strip()):
        prev = out[-1].split()[-1] if out else ""
        if out and (prev in NOT_AN_END or re.fullmatch(r"(?:[A-Z]\.)+", prev) or (prev == "No." and piece[:1].isdigit())):
            out[-1] += " " + piece
        else:
            out.append(piece)
    return out


def _speak(pipe, voice, text, speed, sentence_pause):
    ## Kokoro's audio for `text`. "[0.8]" in the text is a pause of 0.8 s (each piece is rendered on its own and the
    ## silence put between them); a sentence_pause puts that much silence after each sentence as well.
    parts = PAUSE.split(text)
    out = []
    for i, part in enumerate(parts):
        if i % 2:
            out.append(np.zeros(int(RATE * float(part)), np.float32))
            continue
        pieces = sentences(part) if sentence_pause else [part]
        for j, piece in enumerate(pieces):
            said = spoken(piece)
            if not any(c.isalnum() for c in said):
                continue
            out.append(np.concatenate([np.asarray(a, dtype=np.float32) for _, _, a in pipe(said, voice=voice, speed=speed)]))
            if sentence_pause and j < len(pieces) - 1:
                out.append(np.zeros(int(RATE * sentence_pause), np.float32))
    if len(out) == 1:
        return out[0]
    # Kokoro pads every piece with about 0.25 s of silence before and 0.4 s after; trim it so a [0.6] is a 0.6 s pause
    return np.concatenate([_trim(a) if a.any() else a for a in out])


def _trim(a, lead=0.04, tail=0.12):
    loud = np.where(np.abs(a) > np.abs(a).max() * 0.02)[0]
    if not len(loud):
        return a
    return a[max(0, loud[0] - int(RATE * lead)): loud[-1] + int(RATE * tail)]


def render_variant(pipe, preset, text):
    voice = sum(w * pipe.load_voice(v) for v, w in preset["blend"].items())
    factor = 2 ** (-preset.get("semitones", 0.0) / 12)          # pitch down = play the take longer
    speed = preset.get("speed", SPEED) * factor                  # so render it that much faster first
    audio = _speak(pipe, voice, text, speed, preset.get("sentence_pause", 0.0) / factor)
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


# --- casting: three proposals per character, one line each (--casting) --------------------------------------------
## character: (who, from docs/case1-script.md; line as in the game; {A/B/C: preset}). Presets as in VARIANTS; "lang": "b" for British voices.
CASTING = {
    "doyle": ("Lt. Maureen Doyle, Ray's boss, voicemail and phone: clipped, political, not unkind",
              "It's a gambling debt and a .38 in an alley, it's not the Black Dahlia. Get me a name by Friday.", {
                  "A": {"blend": {"af_sarah": 1.0}, "speed": 1.0},
                  "B": {"blend": {"af_kore": 1.0}, "speed": 0.95},
                  "C": {"blend": {"af_nicole": 0.7, "af_sarah": 0.3}, "semitones": -1.0, "speed": 0.95},
              }),
    "nina": ("Nina Alvarez, Danny's girlfriend, on the payphone: guarded, grieving, quick",
             "Friends of Danny knock like Danny played. Two slow, three fast.", {
                 "A": {"blend": {"af_heart": 1.0}, "speed": 0.95},
                 "B": {"blend": {"af_bella": 1.0}, "speed": 0.92},
                 "C": {"blend": {"af_sky": 1.0}, "speed": 0.9},
             }),
    "sal": ("Sal Moretti, the Blue Note's bartender, through the door: gravel, short sentences, scared and hiding it",
            "Danny didn't have friends. He had a piano and a tab.", {
                "A": {"blend": {"am_santa": 1.0}, "speed": 0.9},
                "B": {"blend": {"am_eric": 1.0}, "semitones": -1.5, "speed": 0.88, "warmth": 3.0},
                "C": {"blend": {"am_michael": 0.6, "am_santa": 0.4}, "semitones": -1.0, "speed": 0.88, "grit": 2.0,
                      "fry": 0.1},
            }),
    "tiny": ("\"Tiny\" Ruiz, Vance's doorman at Pier 9: enormous, soft-spoken, misses Danny's playing",
             "Knock on that door and you'll be knocking with your teeth.", {
                 "A": {"blend": {"am_adam": 1.0}, "semitones": -3.0, "speed": 0.85},
                 "B": {"blend": {"am_echo": 1.0}, "semitones": -2.5, "speed": 0.85, "warmth": 4.0},
                 "C": {"blend": {"am_liam": 1.0}, "semitones": -3.5, "speed": 0.8, "warmth": 5.0, "grit": 2.0},
             }),
    "vance": ("Vance, the loan shark: sixties, cardigan over a shoulder holster, courteous and cold",
              "Sit, if you like. The chair is uncomfortable. I bought it that way.", {
                  "A": {"blend": {"bm_george": 1.0}, "speed": 0.88, "lang": "b"},
                  "B": {"blend": {"am_michael": 1.0}, "semitones": -2.0, "speed": 0.85, "warmth": 3.0},
                  "C": {"blend": {"bm_fable": 0.6, "bm_lewis": 0.4}, "semitones": -1.0, "speed": 0.88, "lang": "b"},
              }),
    "otis": ("Sgt. Otis Bell, on the desk phone: warm, funny, tired",
             "Ray, it's Otis. Hope I'm not interrupting your social life.", {
                 "A": {"blend": {"am_eric": 1.0}, "speed": 1.0},
                 "B": {"blend": {"am_liam": 1.0}, "speed": 1.0},
                 "C": {"blend": {"am_echo": 1.0}, "speed": 0.95},
             }),
}


def casting(pipes):
    ## tools/tts/out/casting_case1/<character>/{A,B,C}.wav, <character>/compare.wav (A, B, C), all.wav (everyone),
    ## and README.md describing each proposal.
    base = os.path.join(ROOT, "tools", "tts", "out", "casting_case1")
    gap = np.zeros(int(RATE * 0.8), np.float32)
    everyone = []
    rows = ["| Character | Line | A | B | C |", "| --- | --- | --- | --- | --- |"]
    for who, (desc, line, options) in CASTING.items():
        out = os.path.join(base, who)
        os.makedirs(out, exist_ok=True)
        takes = []
        for name, preset in options.items():
            audio = render_variant(pipes[preset.get("lang", "a")], preset, line)
            sf.write(os.path.join(out, "%s.wav" % name), audio, RATE, subtype="PCM_16")
            takes.append(audio)
        both = np.concatenate([np.concatenate([t, gap]) for t in takes])
        sf.write(os.path.join(out, "compare.wav"), both, RATE, subtype="PCM_16")
        everyone += [both, gap]
        rows.append("| **%s**: %s | \"%s\" | %s |" % (who, desc, line, " | ".join(_describe(p) for p in options.values())))
    sf.write(os.path.join(base, "all.wav"), np.concatenate(everyone), RATE, subtype="PCM_16")
    with open(os.path.join(base, "README.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write("# Case 1 voice casting\n\nEach character's line in three voices. `<character>/compare.wav` plays A, B and"
                " C in order; `all.wav` plays every character's A, B, C in the order below.\n\n" + "\n".join(rows) + "\n")
    print("wrote", base)


def _describe(preset):
    parts = [" + ".join("%s %d%%" % (v, round(w * 100)) if len(preset["blend"]) > 1 else v
                        for v, w in preset["blend"].items())]
    if preset.get("semitones"):
        parts.append("%+g semitones" % preset["semitones"])
    parts.append("speed %g" % preset.get("speed", SPEED))
    for k, label in (("warmth", "warmth"), ("grit", "grit"), ("fry", "flutter")):
        if preset.get(k):
            parts.append("%s %g" % (label, preset[k]))
    return ", ".join(parts)


# --- casting the rest: everyone in Cases 2 to 5 (--casting-rest) -----------------------------------------------------
## character: (case, who (docs/caseN-script.md), lines in the game (about), a line as in the game, {A/B/C: preset}).
## Kept clear of the cast's voices (onyx/fenrir, af_kore, af_heart, am_santa, am_adam -3, bm_george, am_liam), or only
## in blends and at other pitches. "lang": "b" for British voices.
CASTING_REST = {
    "shah": (2, "Dr. Anita Shah, coroner's investigator (Cases 2-5): forties, brisk, exact, fond of Ray", 49,
             "I do bodies, Ray, not bookkeeping.", {
                 "A": {"blend": {"af_nicole": 1.0}, "speed": 1.0},
                 "B": {"blend": {"af_sarah": 0.6, "af_aoede": 0.4}, "speed": 1.0},
                 "C": {"blend": {"bf_emma": 1.0}, "speed": 1.0, "lang": "b"},
             }),
    "park": (2, "Officer Lena Park, Hollywood patrol (Cases 2, 3, 5): early twenties, very thorough, knows the internet", 38,
             "Kenji Ota, twenty-nine, Silver Lake address. Drives for Glide. Four point nine eight stars, which is higher than my mom.", {
                 "A": {"blend": {"af_bella": 1.0}, "speed": 1.05},
                 "B": {"blend": {"af_nova": 1.0}, "speed": 1.05},
                 "C": {"blend": {"af_sky": 1.0}, "speed": 1.0},
             }),
    "rosa": (2, "Rosa, waitress at Norm's: sixties, pencil in her bun, calls everyone \"hon\"", 19,
             "Well. A cop who pours. Now I've seen everything. Put that down before you get ideas, hon. What do you need?", {
                 "A": {"blend": {"af_sarah": 1.0}, "semitones": -2.0, "speed": 0.95, "warmth": 2.0},
                 "B": {"blend": {"af_jessica": 1.0}, "semitones": -1.5, "speed": 0.95},
                 "C": {"blend": {"af_aoede": 0.5, "af_nicole": 0.5}, "semitones": -2.5, "speed": 0.92, "grit": 1.5},
             }),
    "heck": (2, "Hector \"Heck\" Dominguez, rival Glide driver: forties, three phones, loud, then scared", 13,
             "If you're a rider, I'm on break. If you're a cop, I'm on break harder.", {
                 "A": {"blend": {"am_puck": 1.0}, "speed": 1.05},
                 "B": {"blend": {"am_eric": 1.0}, "speed": 1.05},
                 "C": {"blend": {"am_echo": 0.6, "am_puck": 0.4}, "speed": 1.05},
             }),
    "devin": (2, "Devin Clark, Kenji's roommate, photographer: late twenties, soft-spoken, plausible. The killer", 21,
              "Dinner. Like six? Then he went out for his shift. I've been home all night, editing. I was asleep by eleven.", {
                  "A": {"blend": {"am_echo": 1.0}, "speed": 0.95},
                  "B": {"blend": {"am_michael": 1.0}, "semitones": 1.0, "speed": 0.92},
                  "C": {"blend": {"am_puck": 1.0}, "speed": 0.9},
              }),
    "brielle": (2, "Brielle V., drunk influencer, Kenji's last fare (a video on Park's phone)", 2,
                "My Glide driver has a camera pointed at the back seat? Like, at me?", {
                    "A": {"blend": {"af_sky": 1.0}, "speed": 1.05},
                    "B": {"blend": {"af_jessica": 1.0}, "speed": 1.05},
                    "C": {"blend": {"af_nova": 1.0}, "speed": 1.0},
                }),
    "cabbie": (2, "A cab driver at Norm's counter (two lines)", 2,
               "Thanks, detective.", {
                   "A": {"blend": {"am_eric": 1.0}, "semitones": -1.0},
                   "B": {"blend": {"am_michael": 1.0}, "semitones": -1.5},
                   "C": {"blend": {"am_puck": 1.0}, "semitones": -2.0, "grit": 1.5},
               }),
    "pearl": (3, "Pearl Danvers, Gus's assistant, actress: 34, warm, quick, a very good crier. The killer", 32,
              "Are you the detective? They keep saying \"the detective's coming,\" like it's a casting call.", {
                  "A": {"blend": {"af_bella": 1.0}, "speed": 1.0},
                  "B": {"blend": {"af_aoede": 1.0}, "speed": 1.0},
                  "C": {"blend": {"af_river": 1.0}, "speed": 1.0},
              }),
    "morty": (3, "Morty Kahn, rival collector: seventies, bathrobe and loafers, grieving, defensive", 20,
              "Wanted it? In March I offered him two hundred fifty thousand dollars. Cash. He said he'd be buried with it.", {
                  "A": {"blend": {"am_michael": 1.0}, "semitones": -2.5, "speed": 0.85, "fry": 0.1},
                  "B": {"blend": {"am_santa": 0.5, "am_eric": 0.5}, "semitones": -1.0, "speed": 0.88},
                  "C": {"blend": {"bm_lewis": 1.0}, "semitones": -2.0, "speed": 0.85, "lang": "b"},
              }),
    "charlie": (3, "Desmond \"Charlie\" Pike, Chaplin on the boulevard for thirty years: theatrical, kind, nosy", 18,
                "Ah! Lights, at last! Are you the man in charge? You look like the man in charge of being tired.", {
                    "A": {"blend": {"bm_fable": 1.0}, "speed": 1.0, "lang": "b"},
                    "B": {"blend": {"am_puck": 1.0}, "speed": 1.0},
                    "C": {"blend": {"bm_daniel": 1.0}, "speed": 0.95, "lang": "b"},
                }),
    "preacher": (4, "Calvin \"Preacher\" Odom: sixties, Army, First Cavalry; formal, scriptural, sharp", 35,
                 "That young man says I killed a boy for a bicycle. I told him I'd speak to somebody who's been somewhere.", {
                     "A": {"blend": {"am_echo": 1.0}, "semitones": -2.5, "speed": 0.85, "warmth": 3.0},
                     "B": {"blend": {"am_michael": 0.5, "am_fenrir": 0.5}, "semitones": -2.0, "speed": 0.85, "grit": 1.5},
                     "C": {"blend": {"am_eric": 1.0}, "semitones": -3.0, "speed": 0.82, "warmth": 4.0, "fry": 0.08},
                 }),
    "doss": (4, "Officer Brian Doss, Northeast patrol: thirties, cheerful, lazy, wants to be done by five", 18,
             "Detective! Brian Doss, Northeast. Sorry to drag you out. Honestly, it's a wrap. Kid's bike, guy's tent. Coroner's just being thorough.", {
                 "A": {"blend": {"am_puck": 1.0}, "speed": 1.05},
                 "B": {"blend": {"am_eric": 1.0}, "speed": 1.0},
                 "C": {"blend": {"am_echo": 1.0}, "speed": 1.05},
             }),
    "courtney": (4, "Courtney Vail, event planner: thirties, headset, adrenaline and cold brew", 19,
                 "A fundraiser for Councilmember Haskell. Two hundred guests, a string quartet, and a man who gave a forty-minute speech about density.", {
                     "A": {"blend": {"af_nova": 1.0}, "speed": 1.1},
                     "B": {"blend": {"af_jessica": 1.0}, "speed": 1.1},
                     "C": {"blend": {"af_alloy": 1.0}, "speed": 1.1},
                 }),
    "andre": (4, "Andre Mitchell, valet: nineteen, afraid of losing the job, honest", 11,
              "I'm not supposed to say. I'm not supposed to give keys to drunk guests. It's policy. I could lose the job.", {
                  "A": {"blend": {"am_puck": 1.0}, "semitones": 1.0, "speed": 1.05},
                  "B": {"blend": {"am_echo": 1.0}, "semitones": 1.5, "speed": 1.05},
                  "C": {"blend": {"am_eric": 1.0}, "semitones": 1.0, "speed": 1.0},
              }),
    "crane": (4, "Elliot Crane, Haskell's chief of staff: forties, lawyerly, still a little drunk, frightened. The killer", 24,
              "That's my property, Detective. I'd like a warrant before you undress my car.", {
                  "A": {"blend": {"am_michael": 1.0}, "speed": 0.95},
                  "B": {"blend": {"am_eric": 0.6, "am_michael": 0.4}, "speed": 0.95},
                  "C": {"blend": {"am_echo": 1.0}, "semitones": -1.0, "speed": 0.92},
              }),
    "ike": (4, "Ike Feld, night tech at the crime lab (Cases 4-5): thirties, hoodie, dry, curious", 35,
            "Kessler. You only come here when it's weird.", {
                "A": {"blend": {"am_eric": 1.0}, "speed": 1.0},
                "B": {"blend": {"am_puck": 1.0}, "speed": 0.95},
                "C": {"blend": {"am_echo": 1.0}, "speed": 1.0},
            }),
    "owen": (4, "Owen Tate, delivery rider, 24 (heard only on the gate camera clips)", 3,
             "Hey, man. You can't drive like that.", {
                 "A": {"blend": {"am_puck": 1.0}, "semitones": 0.5},
                 "B": {"blend": {"am_echo": 1.0}, "semitones": 1.0},
                 "C": {"blend": {"am_eric": 1.0}, "semitones": 1.0},
             }),
    "teo": (5, "Teodoro \"Teo\" Alcaraz, the Blue Note's porter: sixties, gentle, shaken, precise about habits", 12,
            "Nineteen years, I never once came in on just the latch.", {
                "A": {"blend": {"am_eric": 1.0}, "semitones": -2.0, "speed": 0.88},
                "B": {"blend": {"am_michael": 1.0}, "semitones": -1.5, "speed": 0.85, "warmth": 2.0},
                "C": {"blend": {"am_echo": 1.0}, "semitones": -2.0, "speed": 0.85, "warmth": 3.0},
            }),
    "mara": (5, "Mara Quist, Los Angeles Times metro reporter: forties, persistent, fair, unimpressed", 15,
             "Detective Kessler? Mara Quist, the Times. I heard it on the scanner. Same bar as the piano player Tuesday. Is that a pattern?", {
                 "A": {"blend": {"af_river": 1.0}, "speed": 1.0},
                 "B": {"blend": {"af_nicole": 1.0}, "speed": 0.95},
                 "C": {"blend": {"af_alloy": 1.0}, "speed": 1.0},
             }),
    "brenner": (5, "Walter \"Walt\" Brenner, LAPD retired, Doyle's training officer: sixties, big, avuncular. The killer", 50,
                "Forty years of night shifts, son. You learn what people need at this hour. Coffee, and somebody to tell them to go home.", {
                    "A": {"blend": {"am_echo": 1.0}, "semitones": -3.0, "speed": 0.88, "warmth": 3.0},
                    "B": {"blend": {"am_eric": 0.5, "am_santa": 0.5}, "semitones": -2.0, "speed": 0.88, "warmth": 2.0},
                    "C": {"blend": {"am_michael": 1.0}, "semitones": -3.0, "speed": 0.86, "grit": 1.5},
                }),
    "okafor": (5, "Deputy DA Helen Okafor (Ending C): forties, raincoat over gym clothes, precise", 5,
               "You understand this goes through every desk in your building. Including your lieutenant's.", {
                   "A": {"blend": {"af_aoede": 1.0}, "speed": 0.95},
                   "B": {"blend": {"af_sarah": 1.0}, "speed": 0.95},
                   "C": {"blend": {"bf_isabella": 1.0}, "speed": 0.95, "lang": "b"},
               }),
    "danny": (5, "Danny Reyes, the piano player, 34 (heard only on the take)", 2,
              "Sal, I'm taking five.", {
                  "A": {"blend": {"am_echo": 1.0}, "speed": 1.0},
                  "B": {"blend": {"am_puck": 1.0}, "speed": 0.95},
                  "C": {"blend": {"am_michael": 1.0}, "semitones": 1.0, "speed": 1.0},
              }),
    "pryce": (5, "Harlan Pryce, developer (heard only on the take): smooth, used to being obeyed", 5,
              "Mr. Reyes and I have an arrangement. Eight thousand on Monday, sixteen to come, and he forgets what he heard.", {
                  "A": {"blend": {"bm_lewis": 1.0}, "speed": 0.95, "lang": "b"},
                  "B": {"blend": {"am_michael": 1.0}, "semitones": -1.0, "speed": 0.92},
                  "C": {"blend": {"am_eric": 0.5, "am_michael": 0.5}, "semitones": -1.5, "speed": 0.92, "warmth": 2.0},
              }),
    "haskell": (5, "Councilman Ted Haskell (heard only on the take): nervous, wants to go home", 3,
                "Elliot says the hearing will be packed. The neighborhood groups, the jazz people...", {
                    "A": {"blend": {"am_eric": 1.0}, "speed": 1.05},
                    "B": {"blend": {"am_echo": 1.0}, "speed": 1.05},
                    "C": {"blend": {"am_puck": 1.0}, "semitones": -1.0, "speed": 1.0},
                }),
    "whitaker": (3, "Trent Whitaker, Pryce Development's acquisitions agent (only Gus's saved voicemail): polite, corporate, a threat in a nice suit", 1,
                 "Mr. Lindqvist, Trent Whitaker again. Thirty days. Please don't make this ugly.", {
                     "A": {"blend": {"bm_lewis": 1.0}, "speed": 1.0, "lang": "b"},
                     "B": {"blend": {"am_michael": 0.5, "am_puck": 0.5}, "speed": 1.05},
                     "C": {"blend": {"am_eric": 1.0}, "semitones": -0.5, "speed": 0.95},
                 }),
}


def casting_rest(pipes):
    ## tools/tts/out/casting_rest/<character>/{A,B,C,compare}.wav, all_case2.wav ... all_case5.wav (every character of
    ## that case, A, B, C each), and README.md.
    base = os.path.join(ROOT, "tools", "tts", "out", "casting_rest")
    gap = np.zeros(int(RATE * 0.8), np.float32)
    per_case = {}
    rows = ["| Character | Case | Who | Lines | Line used | A | B | C |", "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for who, (case, desc, count, line, options) in CASTING_REST.items():
        out = os.path.join(base, who)
        os.makedirs(out, exist_ok=True)
        takes = []
        for name, preset in options.items():
            audio = render_variant(pipes[preset.get("lang", "a")], preset, line)
            sf.write(os.path.join(out, "%s.wav" % name), audio, RATE, subtype="PCM_16")
            takes.append(audio)
        both = np.concatenate([np.concatenate([t, gap]) for t in takes])
        sf.write(os.path.join(out, "compare.wav"), both, RATE, subtype="PCM_16")
        per_case.setdefault(case, []).extend([both, gap])
        rows.append("| **%s** | %d | %s | ~%d | \"%s\" | %s |" % (who, case, desc, count, line,
                                                                 " | ".join(_describe(p) for p in options.values())))
    for case, parts in per_case.items():
        sf.write(os.path.join(base, "all_case%d.wav" % case), np.concatenate(parts), RATE, subtype="PCM_16")
    with open(os.path.join(base, "README.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write("# Voice casting, Cases 2 to 5\n\nEach character's line in three voices. `<character>/compare.wav` plays A, B"
                " and C in order; `all_caseN.wav` plays every character first met in that case, in the order below. Lines"
                " are a count of their lines in the game. Phone lines get the phone filter in the game, not here.\n\n"
                + "\n".join(rows) + "\n")
    print("wrote", base)


CALL = re.compile(r'(?<![\w.])(?:main\.)?(say|narrate)\(')
VOICE_CALL = re.compile(r'(?<![\w.])(?:main\.)?voice\(')
STRING = re.compile(r'"((?:[^"\\]|\\.)*)"')


def _calls(src, call=CALL):
    ## (line number, function, argument source) for every call `call` matches, the arguments up to the closing paren.
    func = ""
    starts = [0]
    for line in src.split("\n"):
        starts.append(starts[-1] + len(line) + 1)
    for m in call.finditer(src):
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


def _split_first(arg):
    ## (first argument, the rest) at the first comma outside brackets and strings.
    depth, in_str, i = 0, False, 0
    while i < len(arg):
        ch = arg[i]
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
        elif ch == "," and depth == 0:
            return arg[:i], arg[i + 1:]
        i += 1
    return arg, ""


def list_says(path, speaker="ray"):
    ## Ray's lines in a script: every say() and narrate() argument's string literals, so `"a" if x else "b"` and
    ## `["a", "b"].pick_random()` give each text. Strings handed to another call inside the argument (a flag name) are
    ## skipped. Calls whose text is built at run time (a variable, `%`, `+`) are printed to stderr with their line and
    ## function, to be read and added by hand. stdout: rows for lines.json, ["ray", text, "<file>:<line> <function>"].
    ## With another speaker (--speaker doyle): the voice() calls that pass that speaker id as their last argument.
    src = open(path, encoding="utf-8").read()
    found = []
    calls = _calls(src)
    if speaker != "ray":
        calls = [(n, f, _split_first(a)[0]) for n, f, a in _calls(src, VOICE_CALL)
                 if re.search(r',\s*"%s"\s*(,\s*\w+\s*)?$' % re.escape(speaker), _split_first(a)[1])]
        # a room's helper for the character, `func _shah(line)`, called as _shah("...")
        calls += list(_calls(src, re.compile(r'(?<![\w.])_%s\(' % re.escape(speaker))))
        calls.sort()   # [, phone]
    for line_no, func, arg in calls:
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
    print("[\n" + ",\n".join("\t" + json.dumps([speaker, t, "%s:%d %s" % (where, n, f)], ensure_ascii=False)
                             for t, n, f in found) + "\n]")


def main():
    if "--list" in sys.argv:
        speaker = sys.argv[sys.argv.index("--speaker") + 1] if "--speaker" in sys.argv else "ray"
        list_says(sys.argv[sys.argv.index("--list") + 1], speaker)
        return
    pipe = KPipeline(lang_code="a")      # American English
    if "--casting" in sys.argv:
        casting({"a": pipe, "b": KPipeline(lang_code="b")})
        return
    if "--casting-rest" in sys.argv:
        casting_rest({"a": pipe, "b": KPipeline(lang_code="b")})
        return
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
    old = json.load(open(MANIFEST, encoding="utf-8")) if os.path.exists(MANIFEST) else {}
    pipes = {"a": pipe}         ## American English; British voices ("lang": "b") get their own
    manifest = {}
    chatterbox = chatterbox_sigs()
    made = 0
    for speaker, text in LINES:
        if speaker not in SPEAKERS:
            sys.exit("no voice cast for speaker '%s' (SPEAKERS; see docs/voice-recording.md)" % speaker)
        preset = SPEAKERS[speaker]
        lid = line_id(speaker, text)
        rel = "assets/voice/%s/%s.ogg" % (speaker, lid)
        path = os.path.join(ROOT, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if lid in chatterbox and old.get(lid, {}).get("sig") == chatterbox[lid] and os.path.exists(path) and not force:
            manifest[lid] = old[lid]            # acted with Chatterbox: current, keep it
            continue
        direction = DIRECTION.get((speaker, text), {})
        if direction:
            # a directed line is timed by hand: the speaker's sentence_pause doesn't apply (nor change its signature)
            preset = {k: v for k, v in preset.items() if k != "sentence_pause"}
        sig = take_sig(preset, direction)
        # a clip from before signatures (no "sig") counts as current, so adding them didn't re-render everything
        stale_take = old.get(lid, {}).get("sig", sig) != sig
        if force or stale_take or not os.path.exists(path):
            lang = preset.get("lang", "a")
            if lang not in pipes:
                pipes[lang] = KPipeline(lang_code=lang)
            audio = render_variant(pipes[lang], preset, direction.get("say", text))
            if direction.get("gain_db"):
                audio = audio * 10 ** (direction["gain_db"] / 20)
            sf.write(path, audio, RATE, format="OGG", subtype="VORBIS")
            made += 1
        manifest[lid] = {"speaker": speaker, "text": text, "file": "res://" + rel, "voice": "kokoro: " + _describe(preset),
                         "sig": sig}
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
