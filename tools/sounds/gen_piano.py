"""Synthesise Danny's piano: the keys of the piano close-up and the tune on his recording (the take).

    python tools/sounds/gen_piano.py          (numpy only; writes into assets/sounds/)

Nothing here is sampled from a recording, so there is no licence to credit: the tones are additive synthesis (a few
slightly detuned strings per note, partials that die away faster the higher they are, a short felt thump for the
hammer) and the tune is an original slow D-minor ballad written out in TUNE below (not 'Round Midnight, which is
Monk's and still in copyright; the script only names it).

assets/sounds/piano/<note>.wav   the 20 keys of GameUI.show_piano, C4 to G5 with the sharps ("C#4.wav"), mono, 16-bit,
                                 22.05 kHz, 2.4 s, peak about -4 dBFS. Audio.piano_note() plays them.
assets/sounds/take_tune.wav      the tune: 20 bars at 52 bpm (about 92 s), a piano with a touch of room, and one wrong
                                 note in bar 11 (the one Danny plays when he hears Brenner). Audio.take_tune() plays it.
"""
import os
import wave

import numpy as np

SR = 22050
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', '..', 'assets', 'sounds')
NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
rng = np.random.default_rng(7)


def freq(m):
    return 440.0 * 2 ** ((m - 69) / 12.0)


def piano(m, dur, vel=0.8, sr=SR):
    """One struck note, midi number m, ringing for dur seconds (the tail past dur is a short release)."""
    n = int((dur + 0.35) * sr)
    t = np.arange(n) / sr
    f0 = freq(m)
    pos = (m - 21) / 87.0                                       # 0 low .. 1 high
    out = np.zeros(n)
    top = int(min(16, (sr * 0.45) / f0))
    for k in range(1, top + 1):
        fk = f0 * k * np.sqrt(1 + 0.00035 * k * k * (1.0 + 2.0 * (1 - pos)))      # stiff strings: slightly sharp partials
        if fk > sr * 0.45:
            break
        amp = (1.0 / k ** (1.05 + 0.35 * pos)) * (0.55 + 0.45 * vel ** (1 + 0.15 * k)) * (1.0 if k % 7 else 0.4)
        decay = (0.55 + 0.9 * pos) + 0.28 * k * (0.6 + pos)                        # per second
        for cents, w in ((-1.6, 0.5), (1.6, 0.5)):                                 # two strings, beating a little
            ph = rng.uniform(0, 2 * np.pi)
            out += w * amp * np.sin(2 * np.pi * fk * 2 ** (cents / 1200) * t + ph) * np.exp(-decay * t)
    # a quick 'hammer' thump: lowpassed noise over the first 25 ms
    th = int(0.025 * sr)
    noise = rng.normal(0, 1, th)
    noise = np.convolve(noise, np.ones(6) / 6, mode='same') * np.exp(-np.arange(th) / (0.006 * sr))
    out[:th] += noise * 0.35 * vel * (0.5 + 0.5 * (1 - pos))
    att = int(0.004 * sr)
    out[:att] *= np.linspace(0, 1, att)
    rel = int(0.35 * sr)
    out[-rel:] *= np.linspace(1, 0, rel) ** 2
    return out * vel


def write(path, x, peak_db=-4.0):
    x = x / max(1e-9, np.abs(x).max()) * 10 ** (peak_db / 20)
    pcm = (np.clip(x, -1, 1) * 32767).astype('<i2')
    with wave.open(path, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def keys():
    os.makedirs(os.path.join(OUT, 'piano'), exist_ok=True)
    for octave in (4, 5):
        for i, nm in enumerate(NAMES):
            m = 12 * (octave + 1) + i
            if (octave == 4) or (octave == 5 and m <= 79):                   # C4 .. G5
                write(os.path.join(OUT, 'piano', f'{nm}{octave}.wav'), piano(m, 2.0))


# ---- the tune --------------------------------------------------------------------------------------------------------
BPM = 52
BEAT = 60.0 / BPM
# per bar: (bass, [chord tones])
CHORDS = [
    (38, [53, 57, 60, 64]), (43, [53, 59, 64]), (36, [52, 59, 62]), (41, [57, 60, 64]),
    (35, [53, 57, 62]), (40, [56, 62, 65]), (45, [55, 60, 64]), (45, [55, 61, 65]),
    (38, [53, 57, 60, 64]), (43, [53, 58, 62]), (36, [58, 64, 69]), (41, [57, 60, 64]),
    (46, [57, 62, 65]), (40, [55, 58, 62]), (45, [55, 61]), (38, [53, 57, 60, 64]),
    (43, [53, 58, 62]), (45, [55, 61, 64]), (38, [53, 57, 60, 64]), (38, [57, 62]),
]
# per bar: (beat, midi, beats)
MELODY = [
    [(0, 76, 1.5), (1.5, 74, .5), (2, 72, 2)],
    [(0, 71, 1), (1, 74, 1), (2, 76, 2)],
    [(0, 79, 2), (2, 76, 1), (3, 74, 1)],
    [(0, 72, 3.5)],
    [(0, 74, 1.5), (1.5, 77, .5), (2, 81, 2)],
    [(0, 80, 1), (1, 77, 1), (2, 74, 1), (3, 71, 1)],
    [(0, 76, 3.5)],
    [(0, 73, 1), (1, 77, 1), (2, 76, 2)],
    [(0, 74, 1), (1, 77, 1), (2, 81, 2)],
    [(0, 79, 1.5), (1.5, 77, .5), (2, 74, 2)],
    [(0, 76, 1), (1, 80, 1.2), (2.5, 82, 1), (3.5, 81, .5)],                  # bar 11: the 80 is the wrong note
    [(0, 81, 2), (2, 79, 1), (3, 77, 1)],
    [(0, 74, 1.5), (1.5, 77, .5), (2, 81, 2)],
    [(0, 79, 2), (2, 76, 1), (3, 74, 1)],
    [(0, 73, 1), (1, 76, 1), (2, 79, 1), (3, 77, 1)],
    [(0, 74, 4)],
    [(0, 77, 2), (2, 74, 2)],
    [(0, 76, 2), (2, 73, 2)],
    [(0, 74, 3.5)],
    [],
]


def tune():
    bars = len(CHORDS)
    total = bars * 4 * BEAT + 5.0
    y = np.zeros(int(total * SR))

    def add(x, t0):
        i = int(t0 * SR)
        y[i:i + len(x)] += x[:len(y) - i]

    for b, (bass, chord) in enumerate(CHORDS):
        t0 = b * 4 * BEAT
        last = b == bars - 1
        add(piano(bass, 3.2 if last else 2.2, 0.62), t0 + rng.normal(0, 0.008))
        add(piano(bass + 12, 2.0, 0.35), t0 + 2 * BEAT + rng.normal(0, 0.01)) if not last else None
        for t_off, vel in (((1.5, 0.38), (3.0, 0.3)) if not last else ((0.4, 0.3),)):
            for j, m in enumerate(chord):                              # rolled a little, soft
                add(piano(m, 1.4, vel * rng.uniform(0.9, 1.1)), t0 + t_off * BEAT + j * 0.018 + rng.normal(0, 0.006))
        for (beat, m, d) in MELODY[b]:
            add(piano(m, d * BEAT * 1.15, rng.uniform(0.62, 0.76)), t0 + beat * BEAT + rng.normal(0, 0.012))
    # a touch of room: a few soft echoes, and the tail fades out
    wet = np.zeros_like(y)
    for d, g in ((0.043, 0.28), (0.071, 0.22), (0.113, 0.17), (0.173, 0.12), (0.259, 0.08), (0.371, 0.05)):
        k = int(d * SR)
        wet[k:] += y[:-k] * g
    y = y + wet
    fade = int(3.0 * SR)
    y[-fade:] *= np.linspace(1, 0, fade)
    return y


if __name__ == '__main__':
    keys()
    write(os.path.join(OUT, 'take_tune.wav'), tune(), peak_db=-5.0)
    print('done')
