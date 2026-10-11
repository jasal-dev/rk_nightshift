# Voicing lines (text-to-speech)

Instructions for an AI agent (or anyone) adding spoken lines to Nightshift. The voices are made with text-to-speech
on this machine; nothing is recorded by hand and nothing goes to a cloud service.

**You can't hear audio, and the user can.** Never choose or change a character's voice on your own judgement. Render
candidates, send the user one comparison file (SendUserFile, or say where it is), and wait for them to pick. Once a
voice is cast (the table below), keep using it for every new line.

## How it works

- `Main.say(text)` (Ray) asks `Audio.voice_clip("ray", text)` for a clip. The id is the first 12 hex digits of
  `sha1("<speaker>|<text>")`; `assets/voice/lines.json` maps ids to `res://assets/voice/<speaker>/<id>.ogg`.
- The match is on the **exact text** the game shows: every character, punctuation and apostrophe included. A line
  whose text changes loses its clip (it goes back to text only) until it is re-rendered; nothing breaks.
- With a clip, the line plays on the Voice bus and stays up at least as long as the clip; a click cuts both. The
  player sets the Voice volume in Settings.
- `Main.say()` and `Main.narrate()` (his voice-over on the drives and the board) are Ray (`"ray"`). Other characters
  speak through `Main.voice(text, anchor, color, speaker)`: the last argument is their speaker id (`"doyle"`), and a
  call without one is text only. Pass the id on every call for a cast character, voiced or not yet (all of Doyle's
  calls already do), so later batches only need clips. `caption()` is text only.
- A line heard over a telephone passes `phone = true` as well (`main.voice(text, PHONE_AT, DOYLE_COLOR, "doyle", true)`):
  the game plays its clip through the Phone bus (`Audio._add_phone_bus()`: 350 to 3,200 Hz, a touch of overdrive,
  +10 dB, limited at -1 dBFS). The clips themselves are clean, so the same character can speak in person (Doyle on the pier in Case 5)
  with the same voice. Use it for anyone on the phone: Nina on the payphone, Otis on the desk phone.
- Stage directions inside a line aren't spoken: sounds in asterisks (`"*beep* Ray, it's Doyle."`) and asides in
  brackets (`"(muffled) Thanks, Walt."`) are dropped from what the voice says, but the id still uses the full text.
- Lines that are only a sound written as text, in asterisks (`"*knock knock*"`), are never voiced.
- Every line asked for by a cast speaker that has no clip goes on `Audio.unvoiced`. The playthrough fails if any such
  line in Case 1 (fully voiced for Ray and Doyle) has no clip; extend `_check_voiced()` in `tests/playthrough.gd` to
  each case you finish.

## Files

| File | What |
| --- | --- |
| `tools/tts/gen_voice.py` | The generator: the cast (`SPEAKERS`, the voices in use), the candidates (`CASTING`, `VARIANTS`), spoken-form fixes (`PRONOUNCE`), rendering, levelling, the manifest. |
| `tools/tts/lines.json` | The lines to voice, `[["speaker", "text", "where"], ...]` ("where" is a note, e.g. `street.gd:35 on_enter`). You edit this. |
| `assets/voice/lines.json` | The manifest the game reads. Written by the generator; don't edit it. |
| `assets/voice/<speaker>/<id>.ogg` | The clips (mono, 24 kHz, Ogg Vorbis). Written by the generator. |
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
   prints every text a `say()` or `narrate()` call can show, as rows for `tools/tts/lines.json`, including both sides
   of `"A" if x else "B"` and every item of `["a", "b"].pick_random()`. Calls it can't read (a variable such as
   `opts[c]`, a `%` format, a string built with `+`) are printed to stderr with their line: read the code and add each
   possible text by hand, exactly as the game shows it. It lists the whole script, so drop the rows that belong to other
   cases (Room 214 holds every case: check which branch, `_case2()` and so on, each line is in).
   Ray's lines also come from shared code: `scripts/main.gd` (`examine_item()` and item descriptions in
   `Game.ITEMS`, `NOTHING_TO_ASK`, "Those two don't go together."), `scripts/room.gd` (`default_response()`), the
   evidence cards' lines in a room's `EVIDENCE` table, dialogue options a room repeats with `main.say(opts[c])`, and
   the shared case scripts (`scripts/case2.gd` … `case5.gd`: drives and car menus).
   For another character, add `--speaker <id>`: it lists the `voice()` calls that pass that id, e.g.
   `gen_voice.py --list scripts/rooms/squad_room.gd --speaker doyle`.
2. **Add the rows** to `tools/tts/lines.json`, keeping the text byte for byte. Work in batches (a room or a scene) so
   the user can listen to each batch.
3. **Render:** `tools/tts/.venv/Scripts/python tools/tts/gen_voice.py`. It renders only lines that have no clip yet,
   rewrites `assets/voice/lines.json`, and deletes clips (and their `.import` files) no row points at any more.
   `--force` re-renders everything, for after a voice preset changes.
4. **Import** so Godot picks up the new clips:
   `<godot console exe> --headless --path . --import` (the path is in the toolchain notes).
5. **Check by ear through the user.** Pronunciation mistakes are the usual problem: names (Reyes, Kessler, Okafor,
   Lindqvist), numbers ("214", "1:52", ".38"), abbreviations ("D.R.", "LAPD") and anything shouted in capitals.
   When a word comes out wrong, don't change the game's text: add it to `PRONOUNCE` in the generator,
   {game text fragment: spoken text}, applied before rendering (the id still comes from the game text), then re-render
   the affected rows (delete their clips, or `--force`). Words in capitals (signs, stamps: BLUE NOTE, PAID) are read
   as words unless they're in `ACRONYMS` (LAPD and the like), which are spelled out.
6. **Test** (CLAUDE.md): clips and lines alone are assets, so run the case the lines belong to
   (`tests/playthrough.tscn -- --case N`). If you change `main.gd`, `ui.gd`, `audio.gd` or other shared code, run the
   full playthrough. The playthrough checks that Ray's first line still has a clip, and that no cast speaker's line in
   a fully voiced case is missing one (`_check_voiced()`).
7. **Commit** `tools/tts/lines.json`, `assets/voice/` (the clips, their `.import` files and `lines.json`) and any script
   change. Don't commit `tools/tts/out/` or the venv.

### Example: Doyle's Case 2 lines

```
tools/tts/.venv/Scripts/python tools/tts/gen_voice.py --list scripts/rooms/squad_room.gd --speaker doyle
```

Copy the rows whose "where" is `_calls2` into `tools/tts/lines.json`, run `gen_voice.py` (it renders only the new rows,
in Doyle's cast voice from `SPEAKERS`), import, run `--case 2`, and add `_check_voiced(2)` once all of Case 2's cast
lines are in. Nothing about her voice needs choosing again.

## When a line's text changes

Edit the row in `tools/tts/lines.json` to the new text and run the generator. The old clip is removed as stale and the
new one rendered. If you forget, the game simply shows the new text without a voice.

## Casting a new character

1. Choose a speaker id (lower case, e.g. `nina`, `sal`, `otis`) and pass it as the last argument of every
   `main.voice()` call for that character (the colour constant tells you whose line it is: `NINA_COLOR`, `SAL_COLOR`).
2. Pick three Kokoro voices that fit (American English: `af_*` female, `am_*` male; British: `bf_*`, `bm_*`, with
   `"lang": "b"`; see the VOICES list in the Kokoro-82M repo) and the character's description in the case script
   (`docs/case1-script.md` and so on). Add them to `CASTING` as A, B and C with one characterful line, run
   `gen_voice.py --casting`, and send the user `tools/tts/out/casting_case1/all.wav` or the character's
   `compare.wav`. Record the proposals under "Proposed, awaiting a pick" below.
3. When the user picks, copy that preset into `SPEAKERS` exactly (with `"from"` naming the proposal), move the
   character's row to the cast table with the date, and voice their lines.

## The cast

These are the voices in use. `SPEAKERS` in `tools/tts/gen_voice.py` holds the same settings as code; a re-run with
them gives the same voice. All clips are levelled the same way (about -18 dBFS RMS, roughly -16 LUFS for speech, peaks
under -1 dBFS, mono 24 kHz Ogg Vorbis). "Semitones" lowers the pitch without changing the pace; warmth, grit and
flutter are the post-processing in `render_variant()` (none of the cast uses them yet).

| Speaker | Who | Kokoro voice | Speed | Semitones | Processing | Preset in code | Picked | Voiced |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `ray` | Det. Ray Kessler: LAPD Homicide, twenty-six years on the job, tired, hard-boiled | `am_onyx` 70% + `am_fenrir` 30% (style vectors mixed) | 0.9 | 0 | none | `SPEAKERS["ray"]` (was `VARIANTS["2_blend"]`) | 2026-10-11, over plain onyx and four rougher variants | Case 1, all 244 lines (Room 214's Case 2 to 5 lines not yet) |
| `doyle` | Lt. Maureen Doyle: Ray's boss, voicemail and phone; clipped, political, not unkind | `af_kore` | 0.95 | 0 | phone-line filter in the game on her phone lines (picked 2026-10-11), not baked in | `SPEAKERS["doyle"]` (was `CASTING["doyle"]` B) | 2026-10-11, over `af_sarah` (A) and an `af_nicole`/`af_sarah` mix (C) | Case 1, all 11 lines (voicemail and the 1:30 call) |

## Proposed, awaiting a pick

Rendered by `gen_voice.py --casting` (presets and the line used are in `CASTING`); the user hasn't chosen yet. Not
voiced in the game: their `voice()` calls don't pass a speaker id yet.

| Speaker | Who | A | B | C |
| --- | --- | --- | --- | --- |
| `nina` | Nina Alvarez, Danny's girlfriend, on the payphone: guarded, grieving, quick | `af_heart`, speed 0.95 | `af_bella`, speed 0.92 | `af_sky`, speed 0.9 |
| `sal` | Sal Moretti, the Blue Note's bartender, through the door: gravel, short sentences, scared | `am_santa`, speed 0.9 | `am_eric`, -1.5 semitones, speed 0.88, warmth 3 | `am_michael` 60% + `am_santa` 40%, -1 semitone, speed 0.88, grit 2, flutter 0.1 |
| `tiny` | "Tiny" Ruiz, Vance's doorman at Pier 9: enormous, soft-spoken | `am_adam`, -3 semitones, speed 0.85 | `am_echo`, -2.5 semitones, speed 0.85, warmth 4 | `am_liam`, -3.5 semitones, speed 0.8, warmth 5, grit 2 |
| `vance` | Vance, the loan shark: sixties, cardigan over a shoulder holster, courteous and cold | `bm_george` (British), speed 0.88 | `am_michael`, -2 semitones, speed 0.85, warmth 3 | `bm_fable` 60% + `bm_lewis` 40% (British), -1 semitone, speed 0.88 |
| `otis` | Sgt. Otis Bell, on the desk phone: warm, funny, tired | `am_eric`, speed 1.0 | `am_liam`, speed 1.0 | `am_echo`, speed 0.95 |
