# Nightshift

A small point-and-click detective adventure built in **pure Godot 4** (no plugins), with pre-rendered 1080p art.
It's present-day Los Angeles, after midnight and raining.
This is **Case 1: Dead Piano Player**, about 35 minutes of play: four rooms (the squad room, the street
outside the Blue Note, Pier 9 and Vance's office), eight items, six notebook clues, five conversations,
a drive and the deduction at the murder board. It ends on the title card for Case 2.

## Running it

Open the `nigthshift` folder in Godot 4.7 and press **F5**. The game is authored at 1920×1080 and
scales to any window size, keeping 16:9 with black bars if needed. On a 4K screen in fullscreen
that's an exact 2×. The window opens at the largest 16:9 size that fits your screen.

| Input | Action |
|---|---|
| Left click | Walk / use / talk to a hotspot |
| Right click | Look at a hotspot (or examine an item in the inventory) |
| Mouse at top edge, or **Tab** | Show the inventory bar |
| Click an item, then a hotspot | Use the item on it (right click or Esc to put it away) |
| Click / Space | Skip a line of dialogue |
| 1–9 | Pick a dialogue option |
| **F5** / **F9** | Quick save / quick load |
| **F11** or **Alt+Enter** | Toggle fullscreen (remembered between sessions) |

**Walkthrough (spoilers):**

1. *Squad room.* Look at the desk lamp, then use it to get the key. Use the key on the filing cabinet
   to get the Reyes file, and read it with a right click in the inventory (that fills the notebook).
   Pick up the mug, then use the coffee on the wastebasket to get a dime. The desk phone has a
   voicemail from Lt. Doyle. Go out the door at the back.
2. *Street.* Use the dumpster for a matchbook. Use the dime on the payphone, say you're calling about
   Danny and ask how to get Sal to open the door. Knock on the Blue Note door and ask Sal who Danny owed
   money to. Use the car.
3. *Pier 9.* Tiny won't let you in. Use the matchbook on Tiny, then use the green door: Danny's knock
   gets you in.
4. *Vance's office.* Use the wall of IOUs to find Danny's marker, then talk to Vance: ask about the
   PAID marker, then how Danny paid. (Using the Reyes file on Vance hints at the wall.)
5. *Pier 9 again.* Take the boat hook from the piling and use it on the burn barrel to get the
   envelope. Use the car.
6. *Squad room.* Use the murder board (or the envelope on it): "For something he had", then pin the
   envelope and "Wallet left, phone gone". Use the desk phone to call Doyle.

## Project layout

```
autoload/game.gd          Global state (autoload "Game"): flags, inventory, item database, save/load
scenes/main.tscn          Root scene: World (current room) + UI
scripts/main.gd           Game loop, input, and the scripting API used by rooms
scripts/ui.gd             All UI, built in code: hover label, speech, inventory bar, choices, fades
scripts/player.gd         Detective: path following, animation selection, depth scaling, relighting
shaders/relight.gdshader  Relights the detective with the room's light, fog, grain and vignette
scripts/detective_anims.gd  Frame table for assets/characters/detective.png (generated)
scripts/room.gd           Base class for rooms: walk-area pathfinding, hotspot lookup, hooks
scripts/hotspot.gd        Clickable area (Area2D + CollisionPolygon2D), with walk_to and face
scenes/rooms/*.tscn       Room scenes: Background, WalkArea, Actors (+ walk-behind props), Obstacles, Spawns, Hotspots
scripts/rooms/*.gd        Room logic: one interact() function per room
tests/playthrough.tscn    Automated playthrough of Case 1 (see "Testing")
assets/                   Generated room art, character sheets, light probes, item icons, cursors
tools/                    Python generators for the art (Pillow + numpy)
```

## Adding a room

1. Make the background at 1920×1080 (a 3D set in `tools/r3/`) and put it in `assets/rooms/`.
2. Duplicate `scenes/rooms/street.tscn` and swap the background.
3. Edit `WalkArea` (a Polygon2D) in the editor to cover the floor.
4. Add a `Hotspot` (an Area2D using `hotspot.gd`) with a `CollisionPolygon2D` child for each
   clickable thing. Set its `id`, `display_name`, `walk_to` and `face`.
5. Add `Marker2D` spawns under `Spawns`, each named after the room you arrive from.
6. Write a script that `extends Room` and implement `interact(hs, verb, item)` with a `match hs.id:`.
7. Bake its light probes (`light_probes.py`) so the detective is lit by the room. Without them he's
   drawn unlit, tinted with the room's `tint`.
8. Go there with `await main.change_room("my_room", room_id)`.

## Scripting API (available in room scripts as `main.*`)

```gdscript
await main.say("Line spoken by the detective.")
await main.voice("Line from someone unseen.", Vector2(x, y), Color.PINK)
var i: int = await main.choose(["Option A", "Option B"])
await main.give("item_id")          # pickup animation and inventory toast
main.take("item_id")
await main.player.play_action("use")  # use / pickup / notebook / shrug / badge
await main.walk(Vector2(x, y))
await main.change_room("street", "squad_room")   # the calling room is freed: nothing after this runs
main.clue("clue_id")                # write a Game.CLUES line in the notebook ("Notebook updated")
await main.narrate("Voice-over.")     # Ray speaking off-screen (drives, the murder board)
await main.drive_begin(); await main.text_message("hi", false, "Maya"); await main.drive_end()
await main.end_case("1:40 a.m.", "Case 2: Five Stars")
main.ui.show_board("Question?"); main.ui.set_board_pins(["card", "card"]); main.ui.hide_board()
Game.set_flag("x"); Game.flag("x"); Game.has_item("id")
```

Tiny and Vance are part of their rooms' 3D sets (`tools/r3/npc.py` poses the detective's rig,
recolours it and bakes it into the background), so they don't animate; they talk with
`main.voice()` from where they sit. Off-screen voices use colours per character: Sal pink, Nina
green, Doyle pale blue, Otis warm yellow, Tiny tan, Vance grey-violet.

## Testing

`tests/playthrough.tscn` plays all of Case 1 at 8× speed through the game's own click handling,
answering every dialogue by text, and checks the flags later cases depend on. From the project folder:

```
Godot_v4.7.2-stable_win64_console.exe --headless --path . res://tests/playthrough.tscn
```

It prints each action and ends with `PLAYTHROUGH OK` (exit code 0), or says where it got stuck.

## Regenerating art

The rooms, the detective and the item icons are 3D scenes, rendered with real light, fog and wet
reflections by a small SDF ray-marcher (`tools/r3/r3.c`) at 2× supersampling, then finished at
1920×1080 with a light vignette and film grain.
Hotspot outlines, walk areas, spawn points and depth scaling are projected from the same 3D
sets, so they always match the pictures.

```
cd tools/r3
gcc -O3 -march=native -ffast-math -fopenmp r3.c -o r3 -lm   # once (Linux / MinGW)
cl /O2 /fp:fast /openmp /arch:AVX2 r3.c /Fe:r3.exe            # or once with MSVC, from a VS x64 prompt
python render_room.py street          # -> assets/rooms/street.png + out/street.json
python render_room.py squad_room      # (add --preview for a fast low-res look)
python gen_sprites.py                 # -> assets/characters/detective.png + detective_light.png + scripts/detective_anims.gd
python light_probes.py street         # -> assets/rooms/street_light.json (render_room.py also does this)
python gen_icons.py                   # -> assets/items/*.png (84x84)
python build_scenes.py                # -> scenes/rooms/*.tscn from out/*.json
cd ..; python gen_art.py              # cursors, raindrop
```

- `street.py`, `squad_room.py`, `pier9_dock.py` and `vance_office.py` describe the sets: geometry,
  materials, lights, camera, and each hotspot's 3D walk-to point. `npc.py` places Tiny and Vance.
- Text on signs comes from the DejaVu fonts. `textures.py` looks for them in
  `/usr/share/fonts/truetype/dejavu/` and then in matplotlib's copy, so it works on Windows too.
- **Walk-behind props.** In a set file, wrap the prop in `with S.tag('name'):` behind an
  `if 'name' not in hide:` check, then add `occluders={'name': (x, z)}` to `meta`, where `(x, z)` is the
  floor point the prop stands on. `render_room.py` renders the set again without the prop and cuts
  out every pixel where the prop was the nearest surface. `build_scenes.py` puts that cut-out in
  `Actors` as a Sprite2D whose position is the projected floor point, so Godot's y-sort draws the
  detective behind the prop whenever his feet are further back. Small props you can walk around also
  get a footprint in `obstacles=[(x, z, radius)]`, which becomes a polygon under `Obstacles` that
  pathfinding steers around. The hydrant and lamp post on the street and the partner's desk in the
  squad room work this way.
- **How the detective blends in.** He isn't painted with fixed lighting. `gen_sprites.py` renders every
  frame twice. `detective.png` holds his colours with ambient occlusion. `detective_light.png` holds his
  shading from three light directions in its R, G and B channels: a left key, a right key, and a
  top/back rim. `light_probes.py` asks the renderer how much of each room light (with shadows) reaches a
  body standing on each 32×32 cell of the floor, and how much fog lies between him and the camera. In
  the game, `relight.gdshader` mixes the three shading channels with those light colours at his feet,
  adds the fog, and applies the room's exposure and the same ACES tone curve, vignette and grain as the
  background. Walking from the neon to the sodium lamp changes his light like it changes the set's.
  `char_fill` in a set's `meta` adds a soft fill light from the camera side, an actor's eye light,
  so he stays readable in back-lit rooms. `reflection` in `build_scenes.py`'s `ROOMS` turns on a rippled
  reflection on wet floors. After changing a room's lights, re-run `light_probes.py <room>`.
- `detective.py` is the character rig and `gen_sprites.py` holds the animation poses.
- `textures.py` draws the signs, bricks, posters, the murder board and so on.

`build_scenes.py` rewrites the room scenes, so put room logic in `scripts/rooms/*.gd`, not in the
`.tscn` files. A full room render takes 1-3 minutes, the detective about a minute.
`tools/gen_detective.py`, `tools/gen_font.py` and `assets/fonts/pixel.*` are left over from the
640×360 pixel-art version. They're no longer used.
`r3.c` changed (probe mode), so recompile it once with the gcc line above.
