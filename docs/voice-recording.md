# Voicing lines (text-to-speech)

Instructions for an AI agent (or anyone) adding spoken lines to Nightshift. The voices are made with text-to-speech
on this machine; nothing is recorded by hand and nothing goes to a cloud service.

**You can't hear audio, and the user can.** Never choose or change a character's voice on your own judgement. Render
candidates, send the user one comparison file (SendUserFile, or say where it is), and wait for them to pick. Once a
voice is cast (the table below), keep using it for every new line.

## How it works

- `Main.say(text)` (Ray) asks `Audio.voice_clip("ray", text)` for a clip. The id is the first 12 hex digits of
  `sha1("<speaker>|<text>")`; `assets/voice/lines.json` maps ids to `res://assets/voice/<speaker>/<id>.wav`.
- The match is on the **exact text** the game shows: every character, punctuation and apostrophe included. A line
  whose text changes loses its clip (it goes back to text only) until it is re-rendered; nothing breaks.
- With a clip, the line plays on the Voice bus and stays up at least as long as the clip; a click cuts both. The
  player sets the Voice volume in Settings.
- Only `Main.say()` is voiced so far. `voice()` (other characters, phone calls), `narrate()` (Ray's voice-over on the
  drives and the board, which is Ray too) and `caption()` are text only; voicing them means passing a speaker id into
  `Main._show_text()` the way `say()` does, and casting that speaker below.

## Files

| File | What |
| --- | --- |
| `tools/tts/gen_voice.py` | The generator: the cast (`SPEAKERS`), the voice presets (`VARIANTS`), rendering, levelling, the manifest. |
| `tools/tts/lines.json` | The lines to voice, `[["speaker", "text"], ...]`. You edit this. |
| `assets/voice/lines.json` | The manifest the game reads. Written by the generator; don't edit it. |
| `assets/voice/<speaker>/<id>.wav` | The clips (mono, 24 kHz, 16-bit). Written by the generator. |
| `tools/tts/.venv/`, `tools/tts/out/` | The Python environment and listening samples. Not in git. |

## Setup (once per machine)

The venv may already exist; check for `tools/tts/.venv/Scripts/python.exe` first.

```
py -3.12 -m venv tools/tts/.venv
tools/tts/.venv/Scripts/python -m pip install torch --index-url https://download.pytorch.org/whl/cpu
tools/tts/.venv/Scripts/python -m pip install kokoro soundfile
```

The first run downloads the Kokoro-82M weights and voices from Hugging Face (hexgrad/Kokoro-82M) and a small spaCy
model. CPU is fast enough (a few seconds a line). Kokoro and its text-to-phoneme library misaki are Apache-2.0, so the
clips can go in a game that's sold; they're listed in `assets/sounds/LICENSES.md`. Don't switch to a model whose licence
forbids commercial use (for example Coqui XTTS's CPML) or one that needs a cloud account.

## Voicing more lines

1. **Collect the lines.** For one script:
   `tools/tts/.venv/Scripts/python tools/tts/gen_voice.py --list scripts/rooms/<room>.gd`
   prints every `main.say("...")` whose argument is a single string literal, as rows for `tools/tts/lines.json`.
   It misses lines chosen at run time (`main.say("A" if x else "B")`, a variable, a `%` format or a string built with
   `+`): read the script and add each possible text by hand, exactly as the game would show it. Shared case code
   (`scripts/case2.gd` … `case5.gd`) and `scripts/main.gd` have `say()` lines too (`main.say` or plain `say`), so check them.
2. **Add the rows** to `tools/tts/lines.json`, keeping the text byte for byte. Work in batches (a room or a scene) so
   the user can listen to each batch.
3. **Render:** `tools/tts/.venv/Scripts/python tools/tts/gen_voice.py`. It renders only lines that have no clip yet,
   rewrites `assets/voice/lines.json`, and deletes clips (and their `.import` files) no row points at any more.
   `--force` re-renders everything, for after a voice preset changes.
4. **Import** so Godot picks up the new WAVs:
   `<godot console exe> --headless --path . --import` (the path is in the toolchain notes).
5. **Check by ear through the user.** Pronunciation mistakes are the usual problem: names (Reyes, Kessler, Okafor,
   Lindqvist), numbers ("214", "1:52", ".38"), abbreviations ("D.R.", "LAPD") and anything shouted in capitals.
   When a word comes out wrong, don't change the game's text. Add a spoken-form override instead. The generator doesn't have
   one yet; add a `PRONOUNCE` dict, {game text fragment: spoken text}, applied before rendering, while the id
   stays computed from the game text.
6. **Test** (CLAUDE.md): clips and lines alone are assets, so run the case the lines belong to
   (`tests/playthrough.tscn -- --case N`). If you change `main.gd`, `ui.gd`, `audio.gd` or other shared code, run the
   full playthrough. The playthrough checks that Ray's first line still has a clip.
7. **Commit** `tools/tts/lines.json`, `assets/voice/` (the WAVs, their `.import` files and `lines.json`) and any script
   change. Don't commit `tools/tts/out/` or the venv.

## When a line's text changes

Edit the row in `tools/tts/lines.json` to the new text and run the generator. The old clip is removed as stale and the
new one rendered. If you forget, the game simply shows the new text without a voice.

## Casting a new character

1. Choose a speaker id (lower case, e.g. `nina`, `doyle`, `otis`) and wire it in the game: `Main.voice()` and
   friends need a speaker argument passed to `_show_text()`, the way `say()` passes `"ray"`.
2. Pick two or three Kokoro voices that fit (American English: `af_*` female, `am_*` male; British: `bf_*`, `bm_*`;
   see the VOICES list in the Kokoro-82M repo). Render the character's first few lines with each
   (`--compare` takes `CANDIDATES`; or add presets to `VARIANTS` and use `--variants`), and send the user a comparison.
3. When the user picks, add the preset to `VARIANTS` if it isn't there, map the speaker to it in `SPEAKERS`, and add a
   row to the cast table below.

## The cast

| Speaker | Who | Preset | Settings | Chosen |
| --- | --- | --- | --- | --- |
| `ray` | Det. Ray Kessler: LAPD Homicide, twenty-six years on the job, tired, hard-boiled | `2_blend` | Kokoro style vectors `am_onyx` 0.7 + `am_fenrir` 0.3, speed 0.9, no post-processing; levelled to about -18 dBFS RMS, peaks under -1 dBFS | 2026-10-11, by the user, over plain onyx and four rougher variants |

Voiced so far: Ray's first four lines in Room 214 (`SquadRoom.intro()`).
