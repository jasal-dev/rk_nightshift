extends "res://tests/playthrough.gd"
## Action shots for the web page: runs the playthrough (all five cases and the four endings, or one case with
## `--case N`) and saves a 1920x1080 screenshot to docs/screenshots/ whenever the game reaches one of SHOTS' moments.
## The line, choice or close-up stays up until it is taken; the cursor, hover text, toasts and inventory bar are hidden.
## Run it in a window (not --headless), so the viewport renders:
##
## Godot_v4.7_console.exe --path . res://tests/action_shots.tscn
## Godot_v4.7_console.exe --path . res://tests/action_shots.tscn -- --case 3
## Godot_v4.7_console.exe --path . res://tests/action_shots.tscn -- --log    # also print every line and menu
##
## Like the playthrough, it puts the player's quicksave back when it ends.

const OUT := "res://docs/screenshots/"
const HOLD := 10    ## frames a moment stays up before it is taken, so fades and layout settle

## Each shot is taken the first time all of its conditions hold:
##   room: the room id; case: Game.current_case(); line: a spoken line containing this; choice: a menu with an option
##   containing this; ui: a GameUI close-up that is open ("board", "device", "paper", "jigsaw", "piano", "scene_pic",
##   "drive", "phone", "card", "title"); idle: taken at the start of an action in the room, before Ray moves;
##   bar: the inventory bar pinned open, the cursor on this item; notebook: the notebook open in that case, when the
##   playthrough reads it; title: the title screen, before New Game; hold: frames instead of HOLD; dark: allow the fade.
const SHOTS := [
	{"name": "00_title_screen", "title": true},
	{"name": "01_case1_squad_room", "room": "squad_room", "case": 1, "line": "My coat is wet."},
	{"name": "02_case1_payphone_call", "room": "street", "choice": "Is this Sal?"},
	{"name": "03_case1_drive_text_message", "ui": "phone", "case": 1, "line": "her mother's timing", "hold": 6},
	{"name": "04_case1_pier9_tiny", "room": "pier9_dock", "line": "I'm the sign."},
	{"name": "05_case1_vance_office", "room": "vance_office", "choice": "Danny Reyes owed you money."},
	{"name": "06_case1_murder_board", "ui": "board", "case": 1, "choice": "For something he had."},
	{"name": "07_case2_mulholland_shah", "room": "mulholland_overlook", "line": "Strangled. Not by hand."},
	{"name": "08_case2_prius_glide_app", "room": "prius_interior", "ui": "device", "line": "Blue Note. Two nights ago."},
	{"name": "09_case2_norms_rosa", "room": "norms_diner", "choice": "Who paid?"},
	{"name": "10_case2_kenji_apartment_devin", "room": "kenji_apartment", "line": "Those are mine. Half of those are mine."},
	{"name": "11_case3_stardust_pearl", "room": "stardust_shop", "line": "They keep saying"},
	{"name": "12_case3_uv_lamp", "room": "stardust_shop", "ui": "paper", "line": "Three light up like a premiere"},
	{"name": "13_case3_roof_charlie", "room": "stardust_roof", "line": "more tourists' photographs than the Pope"},
	{"name": "14_case4_bridge_preacher", "room": "fletcher_bridge", "line": "and the waters returned"},
	{"name": "15_case4_reeds_headlight", "room": "river_channel", "line": "Half a headlight, jammed in the roots."},
	{"name": "16_case4_gate_camera", "room": "glass_house", "ui": "device", "line": "You're gonna let him drive?"},
	{"name": "17_case4_crane_garage", "room": "crane_garage", "line": "The car washes are closed"},
	{"name": "18_case4_inventory", "room": "crane_garage", "idle": true, "bar": "lens_piece"},
	{"name": "19_case4_headlight_jigsaw", "room": "crane_garage", "ui": "jigsaw"},
	{"name": "20_case4_night_lab_ike", "room": "night_lab", "line": "You only come here when it's weird."},
	{"name": "21_case4_notebook", "notebook": 4},
	{"name": "22_case5_street_mara", "room": "street_crime", "line": "Mara Quist, the Times."},
	{"name": "23_case5_blue_note_bar", "room": "blue_note_bar", "line": "Sal kept it like a church."},
	{"name": "24_case5_back_room_nina", "room": "blue_note_back", "line": "You're you. That's different."},
	{"name": "25_case5_piano", "room": "blue_note_bar", "ui": "piano"},
	{"name": "26_case5_the_take", "ui": "scene_pic", "line": "(lightly) Then pay him, Walt."},
	{"name": "27_case5_pier_standoff", "room": "pier9_dawn", "line": "I'm better at the second one."},
	{"name": "28_case5_pier_arrest", "room": "pier9_dawn", "line": "you're under arrest"},
	{"name": "29_case5_sunrise_last_choice", "room": "pier9_sunrise", "choice": "Call Mara Quist at the Times."},
	{"name": "30_ending_doyle", "room": "pier9_sunrise", "line": "Not like this. Not like this, Ray."},
	{"name": "31_ending_times", "room": "pier9_sunrise", "line": "I know what it does to them."},
	{"name": "32_ending_end_card", "room": "pier9_sunrise", "ui": "scene_pic", "hold": 20},
]

var _taken := {}
var _pending := {}         ## the shot being held, while its frames count down
var _pending_frames := 0
var _log := false
var _last_line := ""
var _last_menu := ""
var _last_ui := ""


func _ready() -> void:
	_log = "--log" in OS.get_cmdline_user_args()
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT))
	super._ready()


func _process(delta: float) -> void:
	if main != null and not _failed:
		if _log:
			_log_state()
		_watch()
	if _pending.is_empty():
		super._process(delta)       # clicks lines away and answers menus: not while a shot is held


func _watch() -> void:
	if not _pending.is_empty():
		_pending_frames += 1
		_hide_hud()
		if _pending_frames >= int(_pending.get("hold", HOLD)):
			_save(String(_pending["name"]))
			_pending = {}
			main.set_process(true)
		return
	for s: Dictionary in SHOTS:
		if not _taken.has(s["name"]) and not s.has("idle") and not s.has("notebook") and not s.has("title") 				and _matches(s):
			_pending = s
			_pending_frames = 0
			main.set_process(false)     # Main's hover, cursor and bar follow the real mouse
			_hide_hud()
			return


func _matches(s: Dictionary) -> bool:
	var ui: GameUI = main.ui
	if s.has("room") and (main.room == null or main.room.room_id != s["room"]):
		return false
	if s.has("case") and Game.current_case() != int(s["case"]):
		return false
	if not s.has("dark") and ui.fade_rect.color.a > 0.01:
		return false
	if s.has("line") and not (main._speaking and ui.speech_label.visible and ui.speech_label.text.contains(s["line"])):
		return false
	if s.has("choice"):
		if not main._choosing:
			return false
		var hit := false
		for o in ui.options:
			hit = hit or o.contains(s["choice"])
		if not hit:
			return false
	if s.has("ui"):
		var key: String = s["ui"]
		var on: bool = ui.card.visible if key == "card" else is_instance_valid(ui.get(key))
		if not on:
			return false
	return true


func _hide_hud() -> void:
	var ui: GameUI = main.ui
	ui.cursor.visible = false
	ui.cursor_item.visible = false
	ui.hover_label.visible = false
	ui.verb_left.visible = false
	ui.verb_right.visible = false
	ui.toast_label.visible = false
	ui.bar.position.y = -GameUI.BAR_H


func _save(shot: String) -> void:
	var img := get_viewport().get_texture().get_image()
	if img.get_size() != Vector2i(1920, 1080):
		img.resize(1920, 1080, Image.INTERPOLATE_LANCZOS)
	img.save_png(ProjectSettings.globalize_path(OUT + shot + ".png"))
	_taken[shot] = true
	print("    [shot] ", shot)
	var ui: GameUI = main.ui
	ui.cursor.visible = true
	ui.hover_label.visible = true
	ui.verb_left.visible = true
	ui.verb_right.visible = true
	ui.toast_label.visible = true


func act(hotspot: String, verb := "use", item := "", answers: Array[String] = []) -> void:
	await _idle()
	if not _failed:
		for s: Dictionary in SHOTS:
			if not _taken.has(s["name"]) and s.has("idle") and _matches(s):
				await _snap_idle(s)
	await super.act(hotspot, verb, item, answers)


func _snap_idle(s: Dictionary) -> void:
	## A shot of the room between actions; with "bar", the inventory open and the cursor on that item.
	var ui: GameUI = main.ui
	main.set_process(false)
	_hide_hud()
	if s.has("bar"):
		for slot in ui.bar_items.get_children():
			if String(slot.get_meta("item", "")) == s["bar"]:
				ui.bar.position.y = 0
				await get_tree().process_frame
				var p: Vector2 = (slot as Control).get_global_rect().get_center()
				ui.cursor.visible = true
				ui.update_cursor(p, true)
				ui.set_hover(Game.item_name(s["bar"]), p)
				ui.hover_label.visible = true
	for i in int(s.get("hold", HOLD)):
		await get_tree().process_frame
		if s.has("bar"):
			ui.bar.position.y = 0
	_save(String(s["name"]))
	ui.bar.position.y = -GameUI.BAR_H
	main.set_process(true)


func _new_game() -> void:
	while not main._on_title and not _failed:
		await get_tree().process_frame
	for s: Dictionary in SHOTS:
		if s.has("title") and not _taken.has(s["name"]):
			main.set_process(false)
			for i in 30:
				await get_tree().process_frame
				_hide_hud()
			_save(String(s["name"]))
			main.set_process(true)
	await super._new_game()


func read_notebook() -> void:
	## The notebook, open at the current case, before the playthrough reads it.
	var name := ""
	for s: Dictionary in SHOTS:
		if int(s.get("notebook", 0)) == Game.current_case():
			name = s["name"]
	await _idle()
	if name != "" and not _failed and not _taken.has(name):
		main.set_process(false)
		main._on_inventory_clicked("notebook", MOUSE_BUTTON_LEFT)
		for i in HOLD:
			await get_tree().process_frame
			_hide_hud()
		_save(name)
		main.set_process(true)
		var esc := InputEventKey.new()
		esc.keycode = KEY_ESCAPE
		esc.pressed = true
		get_viewport().push_input(esc)
		for i in 3:
			await get_tree().process_frame
	await super.read_notebook()


func _quit(code: int) -> void:
	var missing: Array = []
	for s: Dictionary in SHOTS:
		if not _taken.has(s["name"]):
			missing.append(s["name"])
	print("ACTION SHOTS: %d taken, missing %s" % [_taken.size(), missing])
	super._quit(code)


func _log_state() -> void:
	var ui: GameUI = main.ui
	var where: String = main.room.room_id if main.room else "-"
	var line: String = ui.speech_label.text if main._speaking and ui.speech_label.visible else ""
	if line != "" and line != _last_line:
		print("LINE [%s] %s" % [where, line.replace("\n", " / ")])
	_last_line = line
	var menu := " | ".join(ui.options) if main._choosing else ""
	if menu != "" and menu != _last_menu:
		print("MENU [%s] %s" % [where, menu])
	_last_menu = menu
	var open: Array[String] = []
	for key in ["board", "device", "paper", "jigsaw", "piano", "scene_pic", "drive", "phone", "notebook", "title"]:
		if ui.get(key) != null:
			open.append(key)
	if ui.card.visible:
		open.append("card")
	var u := ",".join(open)
	if u != _last_ui:
		print("UI [%s] %s" % [where, u])
	_last_ui = u
