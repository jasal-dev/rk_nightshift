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
  call without one is text only. Pass the id on every call for a cast character, voiced or not yet (every Case 1
  character's calls already do, in all five cases), so later batches only need clips. `caption()` is text only.
- A line heard over a telephone passes `phone = true` as well (`main.voice(text, PHONE_AT, DOYLE_COLOR, "doyle", true)`):
  the game plays its clip through the Phone bus (`Audio._add_phone_bus()`: 350 to 3,200 Hz, a touch of overdrive,
  +10 dB, limited at -1 dBFS). The clips themselves are clean, so the same character can speak in person (Doyle on the pier in Case 5)
  with the same voice. Use it for anyone on the phone: Nina on the payphone, Otis on the desk phone.
- Stage directions inside a line aren't spoken: sounds in asterisks (`"*beep* Ray, it's Doyle."`) and asides in
  brackets (`"(muffled) Thanks, Walt."`) are dropped from what the voice says, but the id still uses the full text.
- Lines that are only a sound written as text, in asterisks (`"*knock knock*"`), are never voiced.
- Every line asked for by a cast speaker that has no clip goes on `Audio.unvoiced`. The playthrough fails if any such
  line in Case 1 (fully voiced: every speaking character) has no clip; extend `_check_voiced()` in `tests/playthrough.gd` to
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
| `nina` | Nina Alvarez: Danny's girlfriend, on the payphone in Case 1, in the Blue Note's cooler in Case 5; guarded, grieving, quick | `af_heart` | 0.95 | 0 | phone-line filter in the game on her payphone lines; in person clean | `SPEAKERS["nina"]` (was `CASTING["nina"]` A) | 2026-10-11, over `af_bella` (B) and `af_sky` (C) | Case 1, all 9 lines (the payphone call) |
| `otis` | Sgt. Otis Bell: the desk phone; warm, funny, tired | `am_liam` | 1.0 | 0 | phone-line filter in the game (all his lines are on the phone) | `SPEAKERS["otis"]` (was `CASTING["otis"]` B) | 2026-10-11, over `am_eric` (A) and `am_echo` (C) | Case 1, all 4 lines (the call with Case 2) |
| `sal` | Sal Moretti: the Blue Note's bartender, through his door; gravel, short sentences, scared and hiding it | `am_santa` | 0.9 | 0 | none | `SPEAKERS["sal"]` (was `CASTING["sal"]` A) | 2026-10-11, over a lowered `am_eric` (B) and a gritty `am_michael`/`am_santa` mix (C) | Case 1, all 12 lines |
| `tiny` | "Tiny" Ruiz: Vance's doorman at Pier 9; enormous, soft-spoken, misses Danny's playing | `am_adam` | 0.85 | -3 | none | `SPEAKERS["tiny"]` (was `CASTING["tiny"]` A) | 2026-10-11, over a lowered `am_echo` (B) and a lowered gritty `am_liam` (C) | Case 1, all 18 lines |
| `vance` | Vance: loan shark, sixties, cardigan over a shoulder holster; courteous and cold. British, by the user's choice | `bm_george` (British English, `"lang": "b"`) | 0.88 | 0 | none | `SPEAKERS["vance"]` (was `CASTING["vance"]` A) | 2026-10-11, over a lowered `am_michael` (B) and a `bm_fable`/`bm_lewis` mix (C) | Case 1, all 31 lines (his office, and through the green door) |
| `doyle` | Lt. Maureen Doyle: Ray's boss, voicemail and phone; clipped, political, not unkind | `af_kore` | 0.95 | 0 | phone-line filter in the game on her phone lines (picked 2026-10-11), not baked in | `SPEAKERS["doyle"]` (was `CASTING["doyle"]` B) | 2026-10-11, over `af_sarah` (A) and an `af_nicole`/`af_sarah` mix (C) | Case 1, all 11 lines (voicemail and the 1:30 call) |
| `shah` | Dr. Anita Shah, coroner's investigator (Cases 2-5): forties, brisk, exact, fond of Ray | `bf_emma` (British English, `"lang": "b"`) | 1 | 0 | none | `SPEAKERS["shah"]` (was `CASTING_REST["shah"]` C) | 2026-10-11, over A and B | not yet (~49 lines, Case 2 on) |
| `park` | Officer Lena Park, Hollywood patrol (Cases 2, 3, 5): early twenties, very thorough, knows the internet | `af_bella` | 1.05 | 0 | none | `SPEAKERS["park"]` (was `CASTING_REST["park"]` A) | 2026-10-11, over B and C | not yet (~38 lines, Case 2 on) |
| `rosa` | Rosa, waitress at Norm's: sixties, pencil in her bun, calls everyone "hon" | `af_jessica` | 0.95 | -1.5 | none | `SPEAKERS["rosa"]` (was `CASTING_REST["rosa"]` B) | 2026-10-11, over A and C | not yet (~19 lines, Case 2 on) |
| `heck` | Hector "Heck" Dominguez, rival Glide driver: forties, three phones, loud, then scared | `am_echo` 60% + `am_puck` 40% | 1.05 | 0 | none | `SPEAKERS["heck"]` (was `CASTING_REST["heck"]` C) | 2026-10-11, over A and B | not yet (~13 lines, Case 2 on) |
| `devin` | Devin Clark, Kenji's roommate, photographer: late twenties, soft-spoken, plausible. The killer | `am_puck` | 0.9 | 0 | none | `SPEAKERS["devin"]` (was `CASTING_REST["devin"]` C) | 2026-10-11, over A and B | not yet (~21 lines, Case 2 on) |
| `brielle` | Brielle V., drunk influencer, Kenji's last fare (a video on Park's phone) | `af_jessica` | 1.05 | 0 | none | `SPEAKERS["brielle"]` (was `CASTING_REST["brielle"]` B) | 2026-10-11, over A and C | not yet (~2 lines, Case 2 on) |
| `cabbie` | A cab driver at Norm's counter (two lines) | `am_michael` | 0.92 | -1.5 | none | `SPEAKERS["cabbie"]` (was `CASTING_REST["cabbie"]` B) | 2026-10-11, over A and C | not yet (~2 lines, Case 2 on) |
| `pearl` | Pearl Danvers, Gus's assistant, actress: 34, warm, quick, a very good crier. The killer | `af_bella` | 1 | 0 | none | `SPEAKERS["pearl"]` (was `CASTING_REST["pearl"]` A) | 2026-10-11, over B and C | not yet (~32 lines, Case 3 on) |
| `morty` | Morty Kahn, rival collector: seventies, bathrobe and loafers, grieving, defensive | `am_michael` | 0.85 | -2.5 | flutter 0.1 | `SPEAKERS["morty"]` (was `CASTING_REST["morty"]` A) | 2026-10-11, over B and C | not yet (~20 lines, Case 3 on) |
| `charlie` | Desmond "Charlie" Pike, Chaplin on the boulevard for thirty years: theatrical, kind, nosy | `bm_daniel` (British English, `"lang": "b"`) | 0.95 | 0 | none | `SPEAKERS["charlie"]` (was `CASTING_REST["charlie"]` C) | 2026-10-11, over A and B | not yet (~18 lines, Case 3 on) |

## Proposed, awaiting a pick

Every speaker in Cases 2 to 5, proposed 2026-10-11 and rendered by `gen_voice.py --casting-rest` into
`tools/tts/out/casting_rest/` (presets and the line used are in `CASTING_REST`; `all_caseN.wav` plays a case's
characters). When the user picks, copy the preset into `SPEAKERS`, move the row to the cast table, tag the
character's `voice()` calls with their id (phone lines `phone = true`) and voice their lines. Danny, Pryce and Haskell
are heard only on the take (a recording); Brielle only in a phone video; Owen only on the gate camera.

| Speaker | Case | Who | Lines | A | B | C |
| --- | --- | --- | --- | --- | --- | --- |
| `preacher` | 4 | Calvin "Preacher" Odom: sixties, Army, First Cavalry; formal, scriptural, sharp | ~35 | am_echo, -2.5 semitones, speed 0.85, warmth 3 | am_michael 50% + am_fenrir 50%, -2 semitones, speed 0.85, grit 1.5 | am_eric, -3 semitones, speed 0.82, warmth 4, flutter 0.08 |
| `doss` | 4 | Officer Brian Doss, Northeast patrol: thirties, cheerful, lazy, wants to be done by five | ~18 | am_puck, speed 1.05 | am_eric, speed 1 | am_echo, speed 1.05 |
| `courtney` | 4 | Courtney Vail, event planner: thirties, headset, adrenaline and cold brew | ~19 | af_nova, speed 1.1 | af_jessica, speed 1.1 | af_alloy, speed 1.1 |
| `andre` | 4 | Andre Mitchell, valet: nineteen, afraid of losing the job, honest | ~11 | am_puck, +1 semitones, speed 1.05 | am_echo, +1.5 semitones, speed 1.05 | am_eric, +1 semitones, speed 1 |
| `crane` | 4 | Elliot Crane, Haskell's chief of staff: forties, lawyerly, still a little drunk, frightened. The killer | ~24 | am_michael, speed 0.95 | am_eric 60% + am_michael 40%, speed 0.95 | am_echo, -1 semitones, speed 0.92 |
| `ike` | 4 | Ike Feld, night tech at the crime lab (Cases 4-5): thirties, hoodie, dry, curious | ~35 | am_eric, speed 1 | am_puck, speed 0.95 | am_echo, speed 1 |
| `owen` | 4 | Owen Tate, delivery rider, 24 (heard only on the gate camera clips) | ~3 | am_puck, +0.5 semitones, speed 0.92 | am_echo, +1 semitones, speed 0.92 | am_eric, +1 semitones, speed 0.92 |
| `teo` | 5 | Teodoro "Teo" Alcaraz, the Blue Note's porter: sixties, gentle, shaken, precise about habits | ~12 | am_eric, -2 semitones, speed 0.88 | am_michael, -1.5 semitones, speed 0.85, warmth 2 | am_echo, -2 semitones, speed 0.85, warmth 3 |
| `mara` | 5 | Mara Quist, Los Angeles Times metro reporter: forties, persistent, fair, unimpressed | ~15 | af_river, speed 1 | af_nicole, speed 0.95 | af_alloy, speed 1 |
| `brenner` | 5 | Walter "Walt" Brenner, LAPD retired, Doyle's training officer: sixties, big, avuncular. The killer | ~50 | am_echo, -3 semitones, speed 0.88, warmth 3 | am_eric 50% + am_santa 50%, -2 semitones, speed 0.88, warmth 2 | am_michael, -3 semitones, speed 0.86, grit 1.5 |
| `okafor` | 5 | Deputy DA Helen Okafor (Ending C): forties, raincoat over gym clothes, precise | ~5 | af_aoede, speed 0.95 | af_sarah, speed 0.95 | bf_isabella, speed 0.95 (British) |
| `danny` | 5 | Danny Reyes, the piano player, 34 (heard only on the take) | ~2 | am_echo, speed 1 | am_puck, speed 0.95 | am_michael, +1 semitones, speed 1 |
| `pryce` | 5 | Harlan Pryce, developer (heard only on the take): smooth, used to being obeyed | ~5 | bm_lewis, speed 0.95 (British) | am_michael, -1 semitones, speed 0.92 | am_eric 50% + am_michael 50%, -1.5 semitones, speed 0.92, warmth 2 |
| `haskell` | 5 | Councilman Ted Haskell (heard only on the take): nervous, wants to go home | ~3 | am_eric, speed 1.05 | am_echo, speed 1.05 | am_puck, -1 semitones, speed 1 |
