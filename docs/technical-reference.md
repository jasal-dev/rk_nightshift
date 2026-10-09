# Nightshift: technical reference

This is the reference for how the game and its art pipeline fit together, as of Case 5 (the whole game). The README covers
running the game, the scripting API in short, and the regeneration commands; `CLAUDE.md` holds the rules for
agents. This file fills in the rest: the runtime architecture, the data formats, every key a set file can use,
the room map, and the conventions each case follows.

## Contents

1. Runtime architecture
2. Game state, flags and saves
3. Rooms and hotspots
4. Main: input, actions and the scripting API
5. UI components
6. Cases: structure and conventions
7. Room map
8. Art pipeline
9. Set file reference (`meta` keys)
10. File formats
11. Testing
12. Checklists
13. Leftovers and known stale bits

## 1. Runtime architecture

```
project.godot ── autoload Game (autoload/game.gd)    flags, inventory, item and clue tables, save/load
      │
      └── main scene scenes/main.tscn  (Main, scripts/main.gd)
            ├── World (Node2D)
            │     └── <current room>  scenes/rooms/<id>.tscn, script scripts/rooms/<id>.gd (extends Room)
            │           ├── Background, overlay Sprite2Ds
            │           ├── WalkArea (Polygon2D), Obstacles/*
            │           ├── Actors (y-sorted): Player (scenes/player.tscn, scripts/player.gd),
            │           │                       walk-behind props, people overlays
            │           ├── Spawns/* (Marker2D), Hotspots/* (Area2D + hotspot.gd)
            │           └── Rain (CPUParticles2D, outdoor rooms)
            └── UI (CanvasLayer, scripts/ui.gd: GameUI)  every UI element, built in code
```

- One room is loaded at a time. `Main.change_room()` frees the old room, instances the new scene, moves the
  single `Player` node into its `Actors`, places him at the spawn named after the room he came from, and calls
  the room's `on_enter()`.
- Shared per-case code lives in static classes: `Case2` (`scripts/case2.gd`), `Case3`, `Case4`, `Case5`. They hold speech
  colours, drives, car menus and preloaded close-up textures.
- Engine settings: Godot 4.7, Forward Plus, D3D12 on Windows, 1920×1080 viewport, `canvas_items` stretch.
  There are no plugins and no C#.

## 2. Game state, flags and saves

`Game` (`autoload/game.gd`) is the only global state.

| Member | Meaning |
| --- | --- |
| `flags: Dictionary` | Every story fact. `set_flag(key, value := true)`, `flag(key) -> bool`. |
| `inventory: Array[String]` | Item ids in pickup order. `add_item`, `remove_item`, `has_item`. A new game starts with `["notebook"]`. |
| `selected_item` | The item on the cursor (`select_item(id)`, `""` for none). |
| `current_room`, `player_position` | Written on room change and on quicksave. |
| `ITEMS` | Item database: `id → {name, desc}`. Icon is `res://assets/items/<id>.png`. |
| `CLUES` | Notebook clues: `id → [case, line]`. A clue is also a flag of the same id. |
| `current_case()` | 1 to 5, derived from `case1_done` … `case4_done`. |
| `clues(case_no)` | Clue ids Ray has, in `CLUES` order, for one case (or all with 0). |

Signals: `inventory_changed`, `item_selected(id)`.

**Saves.** One quicksave slot at `user://savegame.json` (F5 saves, and so does Esc before it returns to the title; F9 loads, as does the title screen's Load Game, or F9 there):

```json
{ "version": 1, "flags": {...}, "inventory": ["notebook", ...], "room": "street", "pos": [812.0, 944.0] }
```

Loading restores the room and position but not mid-conversation state, so a save is only allowed when nothing
is running (`Main.busy` is false). Settings are stored separately in `user://settings.cfg`:
`[video] fullscreen` and `[text] speed` (0 slow, 1 normal, 2 fast, 3 manual; `Main.TEXT_TIME` scales how long lines stay up, and Manual
keeps each line up until a click, see `Main._hold()`). On Windows, `user://` is `%APPDATA%\Godot\app_userdata\Nightshift\`.

**Flag conventions.**

- `caseN_started` is set by the case's drive in (`Case2.drive_up`, `Case3.drive_in`, `Case4.drive_in`), which also
  removes the previous case's items (`CASE1_ITEMS`, `CASE2_ITEMS`, `CASE3_ITEMS`). Case 5 has no drive in: Ray walks
  across the street, and `Case5.start()` removes `CASE4_ITEMS` and gives him his phone (`ray_phone`).
- `caseN_done` is set by the squad room once the case's closing calls are over; it moves `current_case()` on.
- `board_<thing>` flags show the murder-board pins that persist between cases (the envelope, Kenji, the ride
  receipt, Gus, Brenner's card, Owen, Danny's phone, Pryce's invitation). Case 5 adds Walt's name on the back of
  the index card (shown by `case5_deduced`), the red string between the seeds (`board_string`), and the bare middle
  of the board once Danny's case goes into its box (`got_danny_box`, which hides the middle pins).
- The optional seeds toward the best ending are ordinary flags/pins: the ride receipt (Case 2), Brenner's card
  (Case 3), Pryce's invitation (Case 4). In Case 5 each one answers one of Doyle's three objections; all three on
  the board (`board_ride_receipt`, `board_brenner_card`, `board_pryce_invite`) make Ending A possible.
- The endings: `ending_doyle_best`, `ending_doyle_bitter`, `ending_by_book`, `ending_times` (exactly one), then
  `game_done` after the credits. `brenner_talked_down` or `brenner_forced` and `morty_lyle` add end cards.

## 3. Rooms and hotspots

### Room (`scripts/room.gd`, `class_name Room`)

Exported properties (written by `build_scenes.py`): `room_id`, `room_name`, `tint` (detective colour when a room
has no light probes), `reflection_strength` (wet-floor reflection opacity), and the depth-scaling pair
`far_y/far_scale`, `near_y/near_scale` (detective scale is linear in screen y between them).

Runtime fields: `main` (untyped, so type dynamic results explicitly), `player`, `show_player` (false for close-ups),
`light_exposure`.

Hooks for room scripts:

| Hook | When |
| --- | --- |
| `_ready()` | Scene load. Outdoor rooms call `add_rain(amount, slant)` here; rooms sync overlay visibility to flags. Call `super._ready()` first if you override it. |
| `on_enter(from_room)` | After the fade-in. May await. `from_room` is the spawn name, `"start"` or `"__load"`. |
| `intro()` | Once, when a new game starts in this room (the squad room). |
| `interact(hs, verb, item)` | Every click on a hotspot. `verb` is `"look"` or `"use"`, `item` is the used item id or `""`. Fall back to `await default_response(verb, item)`. |

Helpers: `hotspot(id)`, `hotspots()`, `hotspot_at(p)` (topmost enabled one; later children win, so
`hotspot_order` in the set decides overlap), `speaker_at(id)` (just above a hotspot, for `main.voice()`),
`spawn_point(from)`, `light_at(p)`, `scale_at(y)`, `is_walkable(p)`, `clamp_to_walkable(p)`, `find_path(a, b)`.

**Pathfinding** is a visibility graph: nodes are the walk polygon shrunk by 9 px plus each obstacle grown by 9 px,
edges are straight segments that cross no polygon edge, and `AStar2D` finds the route.

**Overlays.** Overlay sprites in a scene are named after their tag, capitalised (`board_envelope` becomes
`Board_envelope`, `pearl_chair` becomes `Pearl_chair`). Room scripts look them up with `$Name`/`get_node` and set
`visible` from flags, usually in a `_sync()` called from `_ready()` and after the flag changes.

### Hotspot (`scripts/hotspot.gd`, `class_name Hotspot`)

`Area2D` with one or more `CollisionPolygon2D` children. Exports: `id`, `display_name` (the hover label),
`walk_to` (`Vector2.ZERO` = don't walk), `face` (`none/left/right/up/down`; `none` faces the click point),
`enabled` (disabled hotspots are ignored by clicks and hover). Hide one with `enabled = false` or `visible = false`.

## 4. Main: input, actions and the scripting API

**Click flow.** Left click on a hotspot runs `_run_action(hs, "use", item)`: walk to `walk_to` (cancelled if the
player clicks elsewhere meanwhile), face, set `busy`, clear the selected item, `await room.interact(...)`, clear
`busy`. Right click runs `"look"` without walking. Left click on empty floor walks there. While `busy` is true,
clicks and hover are ignored; while a line is showing, a click skips it. That click (and the one that dismisses a case
card) is taken in `Main._input`, before the GUI, so a close-up's backdrop (the jigsaw, the piano, a device screen)
can't swallow it.

**Inventory.** Right click on an item calls `Main.examine_item(id)`: special cases live in its `match`
(`case_file`, `notebook`, `envelope`, `frozen_peas`, `ride_receipt`, `lens_piece`, `valet_ticket`, `pryce_invite`,
`lab_receipt`, and Case 5's `ray_phone`, `reporter_card`, `tab_book`, `set_list`, `danny_box`, `take_drive`,
`brenner_38`), everything else says `ITEMS[id].desc`. Ray's phone is `Case5.phone()`: Texts and Calls (Ike, the take,
the text to Brenner), and at sunrise the choice of where the drive goes. `frozen_peas` delegates to the room's `open_peas()` when
it has one. Using one item on another always says "Those two don't go together."

**Scripting API.** Everything a room script needs, beyond the README's summary:

| Call | Notes |
| --- | --- |
| `say(text)` | Ray speaks above his head. Duration scales with length (1.6 to 6.5 s). |
| `voice(text, anchor, color)` | Someone else speaks from `anchor` (room pixels). Use `speaker_at(id)` for people with a hotspot. |
| `narrate(text)` | Ray's voice-over at the bottom of the screen. |
| `choose(options) -> int` | Dialogue choices; keys 1 to 9 also pick. |
| `device(title, tabs, active, body, rows) -> String` | Phone or car screen. Returns `"tab:i"`, `"row:i"` or `"close"`. |
| `jigsaw(bg, pieces) -> bool` | Fit-the-pieces close-up. Each piece: `{tex, target: Vector2, turns}`. |
| `give(item, animate := true)`, `take(item)` | Inventory with pickup animation and toast. |
| `clue(id)` | Sets the clue flag and toasts "Notebook updated" (first time with a hint). |
| `walk(to)`, `wait(seconds)`, `wait_click()` | |
| `drive_begin()`, `drive_wait(s)`, `text_message(text, outgoing, contact)`, `drive_end()` | The rain-on-windshield transition. Follow `drive_end()` with `change_room()`. |
| `change_room(id, from_room)` | Frees the calling room: nothing after it runs. Make it the last line. |
| `case_card(time, title) -> bool` | Title card between cases. True if F9 loaded a save from it instead. |
| `caption(text, color, skippable)` | A subtitle in the lower third (the take). `skippable = false` ignores clicks. |
| `piano(notes, set_list) -> bool` | Danny's keyboard. True once the last five notes played spell `notes` by letter; false if the player stepped back. Hints after three and six wrong runs of five. |
| `the_end()` | The last card after Case 5's credits; a new game starts after it (or F9 loads). |
| `player.play_action(kind)` | `use`, `pickup`, `notebook`, `shrug`, `badge`, `look_around`. |
| `player.face(dir)`, `player.face_point(p)` | |

`change_room()` also has a small hard-coded table for which way Ray faces on arrival (`main.gd`); new rooms get
`"right"` unless added there.

## 5. UI components

All UI is built in code in `scripts/ui.gd` (`class_name GameUI`), with DejaVu Sans Condensed Bold at 30 px.

| Element | API | Used for |
| --- | --- | --- |
| Hover label, cursor, item cursor | `set_hover`, `update_cursor` | Hotspot and item names; "Use X with Y". |
| Inventory bar (104 px, 84 px icons) | `update_bar`, `bar_pinned`, `item_under`, signal `inventory_clicked(id, button)` | Slides down at the top edge; Tab pins it. |
| Speech | `show_speech`, `hide_speech` | `say`, `voice`, `narrate`. Drawn above the fade, so lines read on black (Case 2's doorstep). |
| Toast | `toast(text, hold)` | Pickups, notebook, save/load. |
| Choices | `show_choices`, `hide_choices`, `options`, signal `choice_made(i)` | Dialogue; also device buttons. Long lists (the boards' evidence) go into up to three columns under the board, with a smaller font if needed. |
| Title | `show_title(has_save, text_speed)`, `hide_title` | The title screen (`scripts/title_screen.gd`): New Game, Load Game, Settings, Exit (quits), and a SKIP TO row for Case 2 to 5 (`Main.jump_to_case(n)`). `Main._title()` runs it at start, after THE END, and on Esc in a room (`_save_to_title()` quicksaves first). |
| Card | `show_card(lines, colors)`, `hide_card` | Case cards and the end card. |
| Fade | `fade_rect`, `fade_to(alpha, time)` | Room changes, drives. |
| Murder board | `show_board(question, caption)`, `set_board_question`, `set_board_pins(pins, labels)`, `hide_board` | Deductions. |
| Drive | `show_drive`, `hide_drive` | Windshield, wipers, passing lights. |
| Phone texts | `show_phone_text(text, outgoing, contact)`, `hide_phone` | Maya, Shah, Otis. |
| Device | `show_device(title, tabs, active, body, rows, interactive)`, `lock_device`, `hide_device` | Glide app, Prius head unit, Chomp app, gate camera, phones. |
| Paper | `show_paper(title, body, note, note_color)`, `show_closeup(tex)`, `hide_paper` | Letters, cards, receipts, UV views, the invitation drawing. |
| Jigsaw | `show_jigsaw(bg, pieces)`, `hide_jigsaw`, `jigsaw_place(i)`, signal `jigsaw_event(kind)` | Crane's headlight. |
| Scene still | `show_scene(tex, dim, caption)`, `hide_scene`, `show_endcard(tex, text)` | The take, the 1:30 call remembered, the end cards. |
| Piano | `show_piano(set_list)`, `hide_piano`, `piano_press(key)`, signal `piano_event(letter)` | Danny's piano (Case 5). |

`show_device(..., accent, lcd)` with `lcd = true` is the desk phone's green call log. `change_room()` hides the
device, paper, jigsaw, piano and scene still, so a close-up never leaks into the next room.

## 6. Cases: structure and conventions

Every case follows the same shape:

1. **Call.** Otis rings the squad room desk phone at the end of the previous case. `main.case_card(time, title)`
   shows the title.
2. **Drive in.** `CaseN.drive_in/drive_up(main)`: removes the previous case's items, sets `caseN_started`, plays the
   drive with texts, then `change_room()` to the first location.
3. **Investigation.** Room scripts in `scripts/rooms/`. Cases 2 and 4 move between places with the car menu
   (`Case2.car_menu`, `Case4.car_menu`); Case 3's rooms connect on foot.
4. **Drive back** to Room 214 (Case 4 goes by way of the night lab).
5. **Deduction** at the murder board in `squad_room.gd`: `_deduction()`, `_deduction2()` … `_deduction4()`. The
   player picks the culprit, then evidence cards from that case's clues and items. Wrong picks get a line from
   Ray and a retry, never a penalty.
6. **Closing calls** (`_call_doyle`, `_calls2` … `_calls4`): Doyle, then Otis with the next case. This sets
   `caseN_done`. After Case 4, the Case 5 card, then `Case5.start()` and the street.

Case 5 is the finale and breaks the shape on purpose: no drive in (the Blue Note is across the street), the street,
the bar, the back room and Room 214 connect on foot, and its deduction (`_deduction5()`) has two culprit steps
with two slots each. After the board come Danny's box and the three calls that set the meet (Harbor Marine, Otis,
the text to Brenner), then the street's car goes by way of the lab to `pier9_dawn` (the confrontation, no way
back), `pier9_sunrise` (the choice and the ending) and `Case5.credits()`.

`squad_room.gd` is the hub: `_case2()` … `_case5()` tell which case's board, phone and lines apply.

**Cast and colours.** Supporting characters are baked into the room art (section 8), not animated sprites, and
speak with `main.voice()` from `speaker_at(id)`. Speech colours: Ray `Main.PLAYER_COLOR`; Case 1 colours are
constants in its room scripts (Sal pink, Nina green, Doyle pale blue, Otis warm yellow, Tiny tan, Vance grey-violet); Cases 2
to 4 are constants in `Case2`, `Case3`, `Case4`.

## 7. Room map

| Room id | Case | Kind | Spawns (arrive from) | Overlays shown by flag |
| --- | --- | --- | --- | --- |
| `squad_room` | hub | interior | `start`, `street` | `mug`, `board_*` pins |
| `street` | 1 | exterior, rain | `squad_room`, `start` | (neon flicker) |
| `pier9_dock` | 1 | exterior, rain | `street`, `vance_office` | `hook` |
| `vance_office` | 1 | interior | `pier9_dock` | |
| `mulholland_overlook` | 2 | exterior | `drive`, `prius_interior` | |
| `prius_interior` | 2 | close-up, no player | `mulholland_overlook` | `visor_card` |
| `norms_diner` | 2 | interior | `drive`, `mulholland_overlook`, `kenji_apartment` | |
| `kenji_apartment` | 2 | interior | `drive`, `mulholland_overlook`, `norms_diner` | `devin_fridge`, `devin_couch` (exclusive) |
| `stardust_shop` | 3 | interior | `drive`, `squad_room`, `stardust_office` | `pearl_chair`, `pearl_stand`, `park`, `morty` |
| `stardust_office` | 3 | interior | `stardust_shop`, `stardust_roof`, `stardust_roof_dark` | `sign_glow` |
| `stardust_roof_dark` | 3 | exterior, before the breaker | `stardust_office` | |
| `stardust_roof` | 3 | exterior, sign lit | `stardust_office` | `neon_u`, `earring` |
| `fletcher_bridge` | 4 | exterior, rain | `drive`, `river_channel`, `glass_house`, `crane_garage` | `preacher_car`, `beam_road`, `beam_down` |
| `river_channel` | 4 | exterior | `fletcher_bridge` | `preacher`, `spot` |
| `glass_house` | 4 | exterior | `drive`, `fletcher_bridge`, `crane_garage` | |
| `crane_garage` | 4 | exterior | `drive`, `fletcher_bridge`, `glass_house` | `crane_stand`, `crane_step` (exclusive), `tarp` |
| `night_lab` | 4, 5 | interior | `drive` | |
| `street_crime` | 5 | exterior, light rain | `squad_room`, `blue_note_bar` | `park`, `bar_red`, `bar_blue` (exclusive) |
| `blue_note_bar` | 5 | interior | `street_crime`, `blue_note_back` | `ledger`, `setlist` |
| `blue_note_back` | 5 | interior | `blue_note_bar` | `cooler_shut`, `nina`, `park` |
| `pier9_dawn` | 5 | exterior, dawn | `drive` | `lincoln`, `bollard_phone`, `bollard_cup`, `brenner`, `brenner_gun`, `brenner_cuffed` (exclusive) |
| `pier9_sunrise` | 5 | exterior, sunrise | `pier9_dawn`, `drive` | `doyle`, `okafor`, `mara` (exclusive) |

`blue_note_take` is rendered like a room but isn't one: a still for the take (`Case5.TAKE`).

Every room also has a `start` spawn for loading a room directly. The `drive` spawn is used after a drive
transition.

## 8. Art pipeline

All art is generated. Nothing is hand-painted, so change the generator and re-run it.

```
tools/r3/<room>.py ──build()──▶ Scene, Camera, env, meta
        │
render_room.py <room> ──▶ r3 (C ray-marcher) ──▶ assets/rooms/<room>.png
        │                                       assets/rooms/<room>_<overlay|occluder>.png
        │                                       tools/r3/out/<room>.json   (projected hotspots, walk area, spawns, scale)
        └──▶ light_probes.bake() ──▶ assets/rooms/<room>_light.json
build_scenes.py ──▶ scenes/rooms/<room>.tscn   (from out/*.json and the ROOMS table)

detective.py (rig) + gen_sprites.py (poses) ──▶ assets/characters/detective.png, detective_light.png,
                                                scripts/detective_anims.gd
npc.py (CAST: the rig, recoloured and restyled) ──▶ baked into room sets
cars.py ──▶ cars in sets      gen_icons.py ──▶ assets/items/*.png      gen_closeups.py ──▶ assets/ui/*.png
title.py (street_crime, emptied) ──▶ render_room.py title      gen_title.py ──▶ assets/ui/title_logo*.png
```

**Requirements.** Python 3 with numpy and Pillow (matplotlib only as a fallback source of DejaVu fonts), and the
`r3` binary built from `tools/r3/r3.c` with OpenMP. On Windows with no gcc, `tools/r3/build_r3.bat` builds
`r3.exe` with the VS 2019 Build Tools (`cl /O2 /fp:fast /openmp /arch:AVX2`). `scene3d.py` writes each render job
to the temp folder (override with the `R3_TMP` environment variable) and runs `tools/r3/r3`.

**GPU rendering.** `r3` runs its surface and volumetric passes on the GPU through OpenCL when it finds one
(`tools/r3/r3_gpu.h` is the host side, `tools/r3/r3.cl` the kernels, built at run time from the folder `r3` sits in).
`OpenCL.dll` comes with the graphics driver and is loaded dynamically, so no SDK is needed to build and `r3` falls back
to the CPU (OpenMP) path when there is no GPU or the kernel fails. `R3_DEVICE=cpu` forces the CPU path, and
`R3_DEVICE=gpu` makes a GPU failure an error instead of a fallback. Probe mode (`light_probes.py`) always runs on the
CPU. `r3.cl` mirrors `r3.c` function by function, so a change to shading, SDFs or fog goes into both files. The two
paths agree to within float rounding (PSNR 57 to 70 dB on glass house, street_crime and Blue Note bar; a few
grazing-angle pixels differ). On the RTX 4090 a 4K room render takes about 1 s against 15 to 30 s on the CPU.

**`render_room.py` options.**

| Option | Effect |
| --- | --- |
| `--preview` | Half resolution, coarser fog; writes only `tools/r3/out/<room>_final.png`. |
| `--meta-only` | Re-projects hotspots, walk area and spawns into `out/<room>.json` without rendering. Keeps the existing overlays and occluders. Use it after moving a hotspot or walk point. |
| `--exposure X` | Overrides the set's `exposure`. |
| `--colors N` | Parsed but unused (left from the pixel-art version). |

**What a full render does**, in order:

1. Renders the set at 2× supersampling and composites fog, ACES tone curve and the set's `grade`.
2. For each `overlays` tag, in order, re-renders with that prop (and the earlier ones) hidden and cuts the
   difference out as `<room>_<tag>.png`. The background ends up with no overlays in it.
3. For each `exclusive_overlays` tag, cuts it against the bare background with every other overlay hidden, so two
   poses of one person don't carry each other's pixels.
   For `overlay_bases` tags, above the person's floor line the sprite keeps only the person (where they are the
   nearest surface): their reflections and light on the floor and walls behind them would otherwise draw over the
   detective when he walks behind them. Below the line (their shadow and reflection in front) it is unchanged.
4. For each `occluders` tag, re-renders depth without it and cuts out the pixels where it was the nearest surface.
   The cut-out uses the background's own pixels, so it is invisible until the detective walks behind it.
5. Adds the vignette and grain (`finish()`), writes the PNGs and `out/<room>.json`, and bakes light probes
   (skipped for close-ups with a `screen` entry).

**Supporting cast.** `npc.CAST` maps a name to rig options (hair style, beard, mustache, stubble, coat length,
headset, sleeves, `cop` badge) and colours. `npc.cast(S, who, pose, pos, yaw, scale, tag)` drops a posed copy into
a set. Give it a `tag` that matches an `overlays` entry to make the person appear and disappear by flag.

**Cars.** `cars.car(S, name, origin, yaw, paint, kind='sedan'|'suv', ...)` builds a car in its own frame, with an
optional open rear door and a broken headlight.

**Variant sets.** A second room on the same set is a tiny module that calls the first with a flag:
`stardust_roof_dark.py` calls `stardust_roof.build(hide, dark=True)`; `street_crime.py` calls
`street.build(hide, crime=True)`, and `pier9_dawn.py` / `pier9_sunrise.py` call `pier9_dock.build(hide, time=...)`.

**Stills.** `blue_note_take.py` is the bar's set in its take state with its own camera and a `screen` entry; the
game shows the PNG full screen. `endcards.py` renders the four Pryce stills to `assets/endcards/`.
`preview_full.py <room> [hidden,tags]` renders a quick 960×540 look with every overlay showing.

## 9. Set file reference (`meta` keys)

A set module defines `build(hide=()) -> (S, cam, env, meta)`. `hide` holds the tags `render_room.py` wants left
out; each hideable prop is wrapped in `with S.tag('name'):` behind `if 'name' not in hide:`. World units are
metres, y up, and the floor is at y = 0 (points are projected at y = 0.1).

| Key | Type | Meaning |
| --- | --- | --- |
| `room` | str | Room id, same as the module and scene name. |
| `walk` | `[(x, z), ...]` | Floor polygon of the walk area. |
| `walk_zmin`, `walk_zmax`, `scale_x` | float | Depth range and x used to sample the detective's scale (1.83 m tall). |
| `spawns` | `{name: (x, z)}` | Entry points, named after the room you arrive from, plus `start`. |
| `hotspots` | `{tag: (name, (x, z) or None, face)}` | Display name, floor walk-to point (`None` = don't walk) and facing. The shape is the convex hull of the geometry tagged `tag`, unless overridden below. |
| `hotspot_shapes` | `{tag: [(x, y, z), ...]}` | Explicit 3D points for a hotspot's hull (people, far things). |
| `screen_shapes` | `{tag: [(px, py), ...]}` | Hotspot polygon directly in screen pixels. |
| `hotspot_order` | `[tag, ...]` | Scene order; later entries are on top when hotspots overlap. Tags not listed are dropped. |
| `overlays` | `[tag, ...]` | Props cut out as sprites the game shows by flag. |
| `exclusive_overlays` | `[tag, ...]` | Subset of `overlays` that never show together (two poses). |
| `overlay_bases` | `{tag: (x, z)}` | Overlays that stand on the floor: placed under `Actors` and y-sorted with the detective at that floor point. Above that line the sprite is cut to the person only. |
| `occluders` | `{tag: (x, z)}` | Walk-behind props and the floor point they stand on. The set must leave the tag out when it is in `hide` (`if 'tag' not in hide:`), or the cut-out is empty. |
| `obstacles` | `[(x, z, r) or (x0, z0, x1, z1), ...]` | Footprints pathfinding steers around: round ones (a 12-sided ring) or floor rectangles. |
| `screen` | `{walk, spawns, scale}` | Close-ups: walk polygon and spawns in pixels, `scale = ((y0, s0), (y1, s1))`. Also skips the light probes. |
| `char_fill` | `((r, g, b), power)` | Soft fill light from the camera side for the detective, baked into the probes. |
| `tint` | `(r, g, b)` | Detective colour when a room has no probes. |
| `exposure` | float | Render exposure (default 1.0). |
| `grade` | optional | Colour grade passed to `composite()`. |
| `extra` | dict | Free-form data copied into `out/<room>.json`. |
| `ghosts` | `{tag: k}` | Figures that are half there: the frame is blended toward a render without the tag (`k` = 0.5 is half). |

`env` keys used by `scene3d.Scene.write`: `sky`, `bounce`, `fog_col`, `fog`, `fog_h0`, `fog_hf`, `fog_max`,
`reflections`, `shadows`, `vol_scale`, `vol_steps`, `grid`, `ao_scale`. Primary rays stop at `fog_max`, so keep
backdrops inside it.

`build_scenes.py` also needs an entry in its `ROOMS` table: node name, script path, display name, and
`reflection` for wet floors.

## 10. File formats

**`tools/r3/out/<room>.json`** (kept in git; `build_scenes.py` and `light_probes.py` read it):

```
room, hotspots{tag: {name, polygon[[x,y]...], walk_to[x,y]|null, face}}, order[tags], walk[[x,y]...],
spawns{name: [x,y]}, obstacles[[[x,y]...]], overlay_bases{tag: [x,y]}, overlays{tag: [x0,y0]},
occluders{tag: {pos: [x0,y0], base: [x,y]}}, far_y, far_scale, near_y, near_scale, tint, extra
```

**`assets/rooms/<room>_light.json`**: `cell` (32), `gw`, `gh` (60 × 34 for 1920×1080), `exposure`, and `data`, with
16 floats per cell, row-major: ambient rgb, left key rgb, right key rgb, rim rgb, fog inscatter rgb, fog
transmittance. `Room.light_at()` interpolates it bilinearly at the detective's feet and `player.gd` feeds it to
`shaders/relight.gdshader`. The three key directions must match `gen_sprites.BASIS` and `light_probes.BASIS`.

**`scripts/detective_anims.gd`** is generated by `gen_sprites.py`: the frame table for `detective.png` and
`detective_light.png`, which must keep the same layout.

## 11. Testing

`tests/playthrough.tscn` runs the real main scene at 8× speed, clicks hotspots through `Main._run_action`, plays with
the Manual text speed and ends every line with a real click pushed through the viewport (so an overlay that swallows
clicks hangs the test), answers choices and device screens by matching text, solves the jigsaw, and checks the flags later
cases depend on. It ends with `PLAYTHROUGH OK` and exit code 0, or names the step where it got stuck (a step gets
45 s, or 150 s with `--shots`).

```
Godot_v4.7.2-stable_win64_console.exe --headless --path . res://tests/playthrough.tscn
Godot_v4.7.2-stable_win64_console.exe --path . res://tests/playthrough.tscn -- --shots   # screenshots to user://
Godot_v4.7.2-stable_win64_console.exe --headless --path . res://tests/playthrough.tscn -- --case 3   # Case 3 only
```

`--case N` runs `_caseN()` alone. Case 1 starts with New Game and stops when its case card comes up; Cases 2 to 5
press the title's SKIP TO button (so they start from `scripts/case_starts.gd`, see "Case jumps" below) and stop
when the next card comes up, or after the endings for Case 5. One case takes 20 to 35 s (Case 5, with its four
endings, about 75 s) against about 3 minutes for the full run. Run only the case a change touches; run the full
playthrough when a change touches several cases, shared code (`main.gd`, `ui.gd`, `game.gd`, `room.gd`,
`hotspot.gd`, `player.gd`, the shaders, the playthrough's helpers) or a case's clues or flags, since the later cases
start from the captured state.

At the end of Case 5 the test snapshots the flags and inventory at sunrise and plays each ending from there (Ending
B with Pryce's invitation taken off the board), checking that exactly one ending flag is set and the credits finish.
The test saves and later restores the player's own quicksave, so running it doesn't destroy a real save. When a
new case is added, extend `_run()` with its steps and add its rooms to the `--shots` list.

**Case jumps.** The title screen's Case 2 to 5 buttons (`Main.jump_to_case`) load the flags and inventory from
`scripts/case_starts.gd`, then show the case card and run the drive, as at the end of the case before. That file is
generated: `tests/capture_case_starts.tscn` runs the playthrough and snapshots the state as each case card comes up
(every earlier case fully solved, with every clue and board seed, so the best ending stays reachable), failing if an
earlier clue is missing. Re-run it whenever a case gains or renames a clue or flag. `tests/case_jumps.tscn` presses
each button and checks the start room, the notebook, the board flags and the inventory, and that the quicksave is
untouched. Send the output to a
file rather than piping it through `tail`, and if a run hangs, stop Godot by process id, not by name, in case the
editor is open.

## 12. Checklists

**A new room**

1. Write `tools/r3/<room>.py` with `build(hide=())` and its `meta` (section 9).
2. `python render_room.py <room> --preview` until it looks right, then a full render.
3. Add it to `ROOMS` in `build_scenes.py` and run `python build_scenes.py`.
4. Write `scripts/rooms/<room>.gd` (`extends Room`, `interact()`, overlay sync in `_ready()`).
5. Add the arrival facing to `Main.change_room()` if it shouldn't be `"right"`.
6. Hook it up with `await main.change_room("<room>", room_id)` from wherever you enter it.

**A new item:** an entry in `Game.ITEMS`, a prop in `gen_icons.py` and its id in `main()`'s default list, then
`python gen_icons.py <id>`. Add a `Main.examine_item()` case if it needs more than `desc`.

**A new clue:** `Game.CLUES[id] = [case, line]`, then `main.clue(id)` where Ray learns it. The notebook and that
case's murder board pick it up.

**A new case**

1. A `scripts/caseN.gd` class with speech colours, the drive in (remove the previous case's items, set
   `caseN_started`), any car menu, and the drive back.
2. Rooms, items and clues as above. Tag clues with the case number.
3. Make `Game.current_case()` return N once `case(N-1)_done` is set.
4. In `squad_room.gd`: a `_caseN()` predicate, the board handler, `_deductionN()`, its card and evidence
   functions, and the closing calls that set `caseN_done`.
5. Any board pin that should stay for later cases: an overlay in `squad_room.py` and a `board_*` flag.
6. Lead the previous case's closing calls into the new one with `case_card()`. (The game now ends with
   Case 5's credits and `the_end()`.)
7. Extend `tests/playthrough.gd`, re-run `tests/capture_case_starts.tscn`, update the README walkthrough, and add a `CLAUDE.md` line if there's a new rule.

## 13. Leftovers and known stale bits

- `tools/gen_detective.py`, `tools/gen_font.py` and `assets/fonts/pixel.*` are from the 640×360 pixel-art version
  and unused.
- `project.godot`'s description still says "A pixel-art point-and-click detective adventure (demo)".
- `render_room.py`'s docstring still says it converts to pixel art, and `--colors` and
  `scene3d.palette_quantize()` and `painterly()` are unused by the current pipeline.
- `.claude/`, `tools/r3/out/*.png`, `r3`/`r3.exe` and quicksaves are ignored by git.
