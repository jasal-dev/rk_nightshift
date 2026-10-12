"""Cut the game's sound loops from the Freesound originals in sounds/ (not in git, see assets/sounds/LICENSES.md).

    tools/tts/.venv/Scripts/python tools/sounds/make_loops.py     (the rain is an .m4a: it needs PyAV, `pip install av`)

assets/sounds/rain.wav       695793 raining-in-my-house (mandaki, CC0): the whole take (13.2 s), its last 1.5 s
                             crossfaded into its start so it loops without a seam, brought up to -28 dBFS RMS (the take
                             is quiet, -33) with any loud drops softly limited to stay under -1 dBFS. Mono, 16-bit,
                             44.1 kHz. (Until 2026-10-11 it was 232198 urban_night_rain_1 by nkroher, CC BY 4.0.)
assets/sounds/footsteps.wav  685287 footsteps-ground: the first eight steps (0.38 s to 4.75 s), which are evenly paced
                             (one every 0.546 s), with a 10 ms fade at each end so the loop doesn't click. The player
                             plays it a little faster to match Ray's walk (Player.STEP_PITCH). Mono, 16-bit, 48 kHz.
assets/sounds/knock_right.wav  437589 3-knock-101 (WakaProduction2018, CC0): one knock (the middle of the three), laid
                             out as Danny's knock, two slow and three fast: knocks at 0, 0.6, 1.2, 1.36 and 1.52 s.
assets/sounds/knock_wrong.wav  the same knock as an ordinary knock on a door, three even knocks 0.32 s apart.
                             Both mono, 16-bit, 44.1 kHz, peaks at -3 dBFS, each knock a touch different in level.
"""
import os
import wave

import numpy as np

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
SRC = os.path.join(ROOT, "sounds")
OUT = os.path.join(ROOT, "assets", "sounds")


def read(path):
    w = wave.open(path)
    n, sr, ch, width = w.getnframes(), w.getframerate(), w.getnchannels(), w.getsampwidth()
    raw = w.readframes(n)
    if width == 2:
        x = np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768
    elif width == 3:
        b = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3).astype(np.int32)
        v = b[:, 0] | (b[:, 1] << 8) | (b[:, 2] << 16)
        x = np.where(v >= 1 << 23, v - (1 << 24), v).astype(np.float32) / (1 << 23)
    else:
        raise ValueError("unsupported sample width %d" % width)
    return x.reshape(-1, ch).mean(axis=1), sr


def read_compressed(path):
    ## Mono float samples and the rate of an .m4a/.mp3/.ogg, through PyAV (FFmpeg).
    import av
    with av.open(path) as c:
        stream = c.streams.audio[0]
        frames = []
        for packet in c.demux(stream):
            try:
                frames += [f.to_ndarray().astype(np.float32) for f in packet.decode()]
            except Exception:       # a damaged packet (the knock has two): skip it, keep the rest
                pass
        rate = stream.rate
    x = np.concatenate(frames, axis=1)
    return x.mean(axis=0), rate


def write(path, x, sr):
    w = wave.open(path, "wb")
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(sr)
    w.writeframes((np.clip(x, -1, 1) * 32767).astype("<i2").tobytes())
    w.close()


def rain():
    x, sr = read_compressed(os.path.join(SRC, "695793__mandaki__raining-in-my-house.m4a"))
    fade = int(sr * 1.5)
    t = np.linspace(0, np.pi / 2, fade, dtype=np.float32)
    body = x[: len(x) - fade].copy()
    body[:fade] = body[:fade] * np.sin(t) + x[len(x) - fade:] * np.cos(t)    # equal power: no dip in the hiss
    body *= 10 ** (-28 / 20) / np.sqrt(np.mean(body ** 2))
    knee, ceiling = 0.6, 0.89      # peaks stay under -1 dBFS
    over = np.abs(body) > knee
    body[over] = np.sign(body[over]) * (knee + (ceiling - knee) * np.tanh((np.abs(body[over]) - knee) / (ceiling - knee)))
    write(os.path.join(OUT, "rain.wav"), body, sr)


def footsteps():
    x, sr = read(os.path.join(SRC, "steps", "685287__emilgasi__footsteps-ground.wav"))
    x = x[: len(x) // 2 * 2].reshape(-1, 2).mean(axis=1)     # 96 kHz to 48 kHz
    sr //= 2
    loop = x[int(0.38 * sr): int(4.75 * sr)].copy()
    edge = int(sr * 0.01)
    ramp = np.linspace(0, 1, edge, dtype=np.float32)
    loop[:edge] *= ramp
    loop[-edge:] *= ramp[::-1]
    loop *= 0.9 / max(1e-6, float(np.abs(loop).max()))
    write(os.path.join(OUT, "footsteps.wav"), loop, sr)


def knocks():
    x, sr = read_compressed(os.path.join(SRC, "437589__wakaproduction2018__3-knock-101.m4a"))
    start = int(0.488 * sr)                     # the middle knock: onset 0.493 s, about 130 ms of ring after it
    one = x[start: start + int(0.24 * sr)].copy()
    ramp_in, ramp_out = int(sr * 0.002), int(sr * 0.04)
    one[:ramp_in] *= np.linspace(0, 1, ramp_in, dtype=np.float32)
    one[-ramp_out:] *= np.linspace(1, 0, ramp_out, dtype=np.float32)
    one /= float(np.abs(one).max())

    def lay(times, levels):
        out = np.zeros(int((times[-1] + 0.3) * sr), np.float32)
        for t, g in zip(times, levels):
            i = int(t * sr)
            out[i: i + len(one)] += one * g
        return out * (10 ** (-3 / 20) / float(np.abs(out).max()))

    write(os.path.join(OUT, "knock_right.wav"), lay([0, 0.6, 1.2, 1.36, 1.52], [1.0, 0.92, 0.95, 0.85, 0.9]), sr)
    write(os.path.join(OUT, "knock_wrong.wav"), lay([0, 0.32, 0.64], [1.0, 0.9, 0.95]), sr)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    rain()
    footsteps()
    knocks()
    print("wrote", OUT)
