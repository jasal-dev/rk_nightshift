"""Cut the game's sound loops from the Freesound originals in sounds/ (not in git, see assets/sounds/LICENSES.md).

    python tools/sounds/make_loops.py

assets/sounds/rain.wav       232198 urban_night_rain_1: the whole take, its last 1.5 s crossfaded into its start so it
                             loops without a seam, brought up to -28 dBFS RMS (the take is quiet, -34) with its few
                             loud drops softly limited to stay under -1 dBFS. Mono, 16-bit, 44.1 kHz.
assets/sounds/footsteps.wav  685287 footsteps-ground: the first eight steps (0.38 s to 4.75 s), which are evenly paced
                             (one every 0.546 s), with a 10 ms fade at each end so the loop doesn't click. The player
                             plays it a little faster to match Ray's walk (Player.STEP_PITCH). Mono, 16-bit, 48 kHz.
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


def write(path, x, sr):
    w = wave.open(path, "wb")
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(sr)
    w.writeframes((np.clip(x, -1, 1) * 32767).astype("<i2").tobytes())
    w.close()


def rain():
    x, sr = read(os.path.join(SRC, "rain", "232198__nkroher__urban_night_rain_1.wav"))
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


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    rain()
    footsteps()
    print("wrote", OUT)
