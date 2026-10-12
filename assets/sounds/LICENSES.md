# Sound and music licences

Every sound in the game, where it came from and its licence. The game is meant to be sold, so only licences that
allow commercial use go in (CC0, CC BY, or a bought licence); no CC BY-NC. Anything that needs attribution is
credited on the title screen's Credits and on the last end-credits card (`Audio.MUSIC_CREDITS`, `Audio.SOUND_CREDITS`).

## Sound effects

The originals are in `sounds/` at the project root (not in git, and ignored by Godot through `sounds/.gdignore`);
`tools/sounds/make_loops.py` cuts the game's files from them.

| Game file | Original | Source | Author | Licence | Downloaded |
| --- | --- | --- | --- | --- | --- |
| `assets/sounds/rain.wav` | `695793__mandaki__raining-in-my-house.m4a` | https://freesound.org/s/695793/ | mandaki | CC0 (credited anyway) | 2026-10-11 |
| `assets/sounds/knock_right.wav`, `knock_wrong.wav` | `437589__wakaproduction2018__3-knock-101.m4a` (one knock of three) | https://freesound.org/s/437589/ | WakaProduction2018 | CC0 | 2026-10-12 |
| `assets/sounds/hang_up.wav` | `273213__e_vice__hang-up-tone.wav` (its first second) | https://freesound.org/s/273213/ | E_Vice | CC0 | 2026-10-12 |
| `assets/sounds/text_tone.wav` | `636401__dvidrio02__text-tone-5.mp3` | https://freesound.org/s/636401/ | dVidrio02 | CC0 | 2026-10-12 |
| `assets/sounds/footsteps.wav` | `685287__emilgasi__footsteps-ground.wav` | https://freesound.org/s/685287/ | emilgasi | CC0 (credited anyway) | 2026-10-11 |

## Voice

Spoken lines are made with text-to-speech, run locally: `tools/tts/gen_voice.py` writes `assets/voice/<speaker>/*.wav`
and `assets/voice/lines.json`.

| Tool | Source | Licence | Notes |
| --- | --- | --- | --- |
| Kokoro-82M (model weights and code), voices `am_onyx`, `am_fenrir` (Ray) `af_kore` (Doyle), `af_heart` (Nina), `am_santa` (Sal), `am_adam` (Tiny), `bm_george` (Vance) and `am_liam` (Otis) | https://huggingface.co/hexgrad/Kokoro-82M | Apache-2.0 | The output may be used commercially; no credit required. |
| misaki (Kokoro's text-to-phoneme) | https://github.com/hexgrad/misaki | Apache-2.0 | Used only to make the files. |

## Music

Bensound licences, one per track; the licence codes are in `Audio.MUSIC_CREDITS` and shown in the credits.

| Game file | Artist | Licence code |
| --- | --- | --- |
| `assets/music/bensound-sleepless.mp3` | Diffie Bosman | NEDTC8SIKQPAI6T8 |
| `assets/music/bensound-echoofsadness.mp3` | TURNIQUE | YHZCQFSRSBTPWIAZ |
| `assets/music/bensound-november.mp3` | Benjamin Tissot | YBABDKFYYZMYCBIF |
| `assets/music/bensound-entenca.mp3` | Dreamt | GZGCSGJPOTTD5QOA |
| `assets/music/bensound-rainyday.mp3` | Yunior Arronte | FXE0HMJQCIWEMGOG |
