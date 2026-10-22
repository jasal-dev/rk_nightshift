"""Ray's voice-over for the Steam trailer (promo only: nothing here goes into assets/voice or the game's manifest).
Renders each line with Ray's cast voice (gen_voice.SPEAKERS["ray"]) to <outdir>/vo_NN.wav.
    tools/tts/.venv/Scripts/python tools/tts/gen_promo_voice.py <outdir>
"""
import os
import sys

import soundfile as sf
from kokoro import KPipeline

import gen_voice as g

## (start second in the trailer, text); a [0.6] is a pause of 0.6 s
LINES = [
    (5.0, "Midnight. [0.5] Rain. [0.5] A dead piano player."),
    (10.5, "Everybody in this town has a story. [0.6] Most of them are lying."),
    (17.0, "I've got a notebook, a bad coat, [0.4] and one night."),
    (22.0, "Every case starts the same way. [0.6] Somebody didn't come home."),
    (34.3, "A body in the river. [0.5] A gate camera that saw everything."),
    (41.0, "Nobody stays up for the dead. [0.7] So I do."),
    (49.0, "Five names. [0.4] One of them knows what I'm going to find."),
    (57.0, "Let's go to work."),
]

if __name__ == "__main__":
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    pipe = KPipeline(lang_code="a")
    for i, (t, text) in enumerate(LINES):
        audio = g.render_variant(pipe, g.SPEAKERS["ray"], text)
        sf.write(os.path.join(out, "vo_%02d.wav" % i), audio, g.RATE)
        print("%02d @%.1fs %.1fs  %s" % (i, t, len(audio) / g.RATE, text))
