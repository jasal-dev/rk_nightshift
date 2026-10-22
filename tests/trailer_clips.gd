extends "res://tests/action_shots.gd"
## Trailer footage: runs the playthrough (all five cases, or one with `-- --case N`) and, at each of CLIPS' moments,
## slows the game to real time and records a short clip as numbered JPEGs (1920x1080, 30 fps) into <out>/<clip>/.
## Hold clips freeze the playthrough's clicks, so the line, menu or close-up stays up for its length; walk clips
## record the next action (Ray walking) as it plays. Case 5's culprit and endings are left out on purpose.
## Needs a window, and a fixed frame rate so every frame is exactly 1/30 s of game time:
##
## Godot_v4.7_console.exe --path . --fixed-fps 30 res://tests/trailer_clips.tscn -- --out <abs dir> [--case N]
##
## Reuses action_shots' conditions (_matches) and HUD hiding, but not its screenshots. Like the playthrough, it puts
## the player's quicksave back when it ends.

const FPS := 30
const FAST := 8.0   ## the playthrough's own speed between clips

## Same conditions as action_shots' SHOTS, plus "secs" (clip length), or "walk": true (taken at the start of an
## action, and recorded while Ray walks).
const CLIPS := [
	{"name": "c01_squad_room", "room": "squad_room", "case": 1, "line": "My coat is wet.", "secs": 3.0},
	{"name": "c01_payphone", "room": "street", "choice": "Is this Sal?", "secs": 2.5},
	{"name": "c01_walk_street", "room": "street", "case": 1, "walk": true, "secs": 3.0},
	{"name": "c01_tiny", "room": "pier9_dock", "line": "I'm the sign.", "secs": 3.0},
	{"name": "c01_vance", "room": "vance_office", "choice": "Danny Reyes owed you money.", "secs": 2.5},
	{"name": "c01_board", "ui": "board", "case": 1, "choice": "For something he had.", "secs": 2.5},
	{"name": "c02_shah", "room": "mulholland_overlook", "line": "Strangled. Not by hand.", "secs": 3.0},
	{"name": "c02_prius", "room": "prius_interior", "ui": "device", "line": "Blue Note. Two nights ago.", "secs": 3.0},
	{"name": "c02_norms", "room": "norms_diner", "choice": "Who paid?", "secs": 2.5},
	{"name": "c02_devin", "room": "kenji_apartment", "line": "Those are mine. Half of those are mine.", "secs": 3.0},
	{"name": "c03_pearl", "room": "stardust_shop", "line": "They keep saying", "secs": 3.0},
	{"name": "c03_uv", "room": "stardust_shop", "ui": "paper", "line": "Three light up like a premiere", "secs": 3.0},
	{"name": "c03_roof", "room": "stardust_roof", "line": "more tourists' photographs than the Pope", "secs": 3.0},
	{"name": "c04_bridge", "room": "fletcher_bridge", "line": "and the waters returned", "secs": 3.0},
	{"name": "c04_reeds", "room": "river_channel", "line": "Half a headlight, jammed in the roots.", "secs": 3.0},
	{"name": "c04_camera", "room": "glass_house", "ui": "device", "line": "You're gonna let him drive?", "secs": 3.0},
	{"name": "c04_jigsaw", "room": "crane_garage", "ui": "jigsaw", "secs": 3.0},
	{"name": "c04_lab", "room": "night_lab", "line": "You only come here when it's weird.", "secs": 3.0},
	{"name": "c05_mara", "room": "street_crime", "line": "Mara Quist, the Times.", "secs": 3.0},
	{"name": "c05_bar", "room": "blue_note_bar", "line": "Sal kept it like a church.", "secs": 3.0},
	{"name": "c05_nina", "room": "blue_note_back", "line": "You're you. That's different.", "secs": 3.0},
	{"name": "c05_piano", "room": "blue_note_bar", "ui": "piano", "secs": 3.0},
]

var _out := ""
var _done := {}
var _clip := {}
var _clip_frame := 0
var _clip_total := 0


func _ready() -> void:
	var args := OS.get_cmdline_user_args()
	var i := args.find("--out")
	_out = args[i + 1] if i >= 0 and i + 1 < args.size() else ProjectSettings.globalize_path("user://trailer")
	DirAccess.make_dir_recursive_absolute(_out)
	DisplayServer.window_set_size(Vector2i(1920, 1080))
	super._ready()


func _watch() -> void:
	## Replaces action_shots' watcher. While a hold clip records, _pending is non-empty, which keeps the
	## playthrough from clicking the line or answering the menu.
	if not _clip.is_empty():
		_record()
		return
	for c: Dictionary in CLIPS:
		if not _done.has(c["name"]) and not c.has("walk") and _matches(c):
			_start(c)
			_pending = c
			return


func _start(c: Dictionary) -> void:
	_clip = c
	_clip_frame = 0
	_clip_total = int(float(c["secs"]) * FPS)
	DirAccess.make_dir_recursive_absolute(_out + "/" + String(c["name"]))
	Engine.time_scale = 1.0
	print("    [clip] ", c["name"])


func _record() -> void:
	_hide_hud()
	var img := get_viewport().get_texture().get_image()
	if img.get_size() != Vector2i(1920, 1080):
		img.resize(1920, 1080, Image.INTERPOLATE_LANCZOS)
	img.save_jpg("%s/%s/%05d.jpg" % [_out, _clip["name"], _clip_frame], 0.95)
	_clip_frame += 1
	_step_started = Time.get_ticks_msec()     # saving frames is slow in real time; don't trip the stuck check
	if _clip_frame >= _clip_total:
		_done[_clip["name"]] = true
		_clip = {}
		_pending = {}
		Engine.time_scale = FAST


func act(hotspot: String, verb := "use", item := "", answers: Array[String] = []) -> void:
	await _idle()
	if not _failed and _clip.is_empty():
		for c: Dictionary in CLIPS:
			if not _done.has(c["name"]) and c.has("walk") and _matches(c):
				_start(c)
				break
	await super.act(hotspot, verb, item, answers)


func _save(_shot: String) -> void:
	pass      # no screenshots: that's action_shots' job


func _snap_idle(_s: Dictionary) -> void:
	pass


func _quit(code: int) -> void:
	var missing: Array = []
	for c: Dictionary in CLIPS:
		if not _done.has(c["name"]):
			missing.append(c["name"])
	print("TRAILER CLIPS: %d recorded, missing %s" % [_done.size(), missing])
	Engine.time_scale = 1.0
	super._quit(code)
