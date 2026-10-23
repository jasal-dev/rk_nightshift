## Renders the lines in chatterbox_lines.json with Chatterbox (acted take), then voice-converts the take to the speaker's
## Kokoro timbre (the speaker's reference clips), levels it like gen_voice.py and writes the clip + manifest entry.
## Run with its own venv:  tools/tts/.venv_cb/Scripts/python tools/tts/gen_chatterbox.py [--force]
## gen_voice.py leaves these lines alone while their clip and signature are current.
import hashlib, json, os, sys
import numpy as np
import soundfile as sf
import torch

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
CONFIG = os.path.join(ROOT, "tools", "tts", "chatterbox_lines.json")
MANIFEST = os.path.join(ROOT, "assets", "voice", "lines.json")
RATE = 24000


def line_id(speaker, text):
    return hashlib.sha1(("%s|%s" % (speaker, text)).encode("utf-8")).hexdigest()[:12]


def clip_path(speaker, text):
    return os.path.join(ROOT, "assets", "voice", speaker, line_id(speaker, text) + ".ogg")


def sig_of(entry, reference):
    return "cb" + hashlib.sha1(json.dumps([entry, reference], sort_keys=True).encode("utf-8")).hexdigest()[:10]


def trim(a, lead=0.04, tail=0.12):
    loud = np.where(np.abs(a) > np.abs(a).max() * 0.02)[0]
    return a[max(0, loud[0] - int(RATE * lead)): loud[-1] + int(RATE * tail)] if len(loud) else a


def level(audio):
    audio = np.concatenate([audio, np.zeros(int(RATE * 0.15), np.float32)])
    audio *= 10 ** (-18 / 20) / max(float(np.sqrt(np.mean(audio ** 2))), 1e-6)
    peak = float(np.abs(audio).max())
    if peak > 0.89:
        audio *= 0.89 / peak
    return audio


def main():
    cfg = json.load(open(CONFIG, encoding="utf-8"))
    force = "--force" in sys.argv
    old = json.load(open(MANIFEST, encoding="utf-8"))
    ref_cfg = cfg["reference"]
    todo = []
    for e in cfg["lines"]:
        sig = sig_of(e, ref_cfg)
        lid = line_id(e["speaker"], e["text"])
        if force or old.get(lid, {}).get("sig") != sig or not os.path.exists(clip_path(e["speaker"], e["text"])):
            todo.append((e, sig, lid))
    if not todo:
        print("all current")
        return
    from chatterbox.tts import ChatterboxTTS
    from chatterbox.vc import ChatterboxVC
    tts = ChatterboxTTS.from_pretrained(device="cuda")
    vc = ChatterboxVC.from_pretrained("cuda")
    tmp = os.path.join(ROOT, "tools", "tts", "out", "chatterbox")
    os.makedirs(tmp, exist_ok=True)
    ref_audio = np.concatenate([np.concatenate([sf.read(clip_path(ref_cfg["speaker"], t))[0].astype(np.float32),
                                                np.zeros(6000, np.float32)]) for t in ref_cfg["lines"]])
    ref_path = os.path.join(tmp, "ref_%s.wav" % ref_cfg["speaker"])
    sf.write(ref_path, ref_audio, RATE)
    for e, sig, lid in todo:
        torch.manual_seed(e.get("seed", 1))
        wav = tts.generate(e["text"], audio_prompt_path=ref_path, exaggeration=e["exaggeration"], cfg_weight=e["cfg_weight"])
        raw = os.path.join(tmp, lid + "_raw.wav")
        sf.write(raw, wav.squeeze().cpu().numpy(), tts.sr)
        conv = vc.generate(raw, target_voice_path=ref_path).squeeze().cpu().numpy().astype(np.float32)
        audio = level(trim(conv))
        path = clip_path(e["speaker"], e["text"])
        sf.write(path, audio, RATE, format="OGG", subtype="VORBIS")
        old[lid] = {"speaker": e["speaker"], "text": e["text"], "file": "res://assets/voice/%s/%s.ogg" % (e["speaker"], lid),
                    "voice": "chatterbox (exaggeration %s, cfg %s, seed %s) voice-converted to the Kokoro timbre"
                             % (e["exaggeration"], e["cfg_weight"], e.get("seed", 1)),
                    "sig": sig}
        print("rendered", lid, e["text"][:50])
    with open(MANIFEST, "w", encoding="utf-8", newline="\n") as f:
        json.dump(old, f, indent="\t", ensure_ascii=False)
        f.write("\n")


if __name__ == "__main__":
    main()
