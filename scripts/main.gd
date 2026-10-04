extends Node
## Game loop: owns the current room, the player and the UI, turns mouse
## clicks into walk / look / use actions, and gives room scripts a small
## scripting API (say, voice, choose, give, change_room, ...).
##
## Controls: left click = walk / use, right click = look,
## mouse to top edge (or Tab) = inventory, F5 = save, F9 = load, F11 / Alt+Enter = fullscreen.

const PlayerScene := preload("res://scenes/player.tscn")
const PLAYER_COLOR := Color(0.93, 0.86, 0.68)

var room: Room
var player: Player
var busy := false

@onready var world: Node2D = $World
@onready var ui: GameUI = $UI

var _action_token := 0
var _skip := false
var _speaking := false
var _choosing := false
var _waiting_click := false
var _load_requested := false


const SETTINGS := "user://settings.cfg"


func _ready() -> void:
	Input.mouse_mode = Input.MOUSE_MODE_HIDDEN
	_apply_window_settings()
	player = PlayerScene.instantiate()
	ui.inventory_clicked.connect(_on_inventory_clicked)
	_title()


# --- window / fullscreen -----------------------------------------------------
func _apply_window_settings() -> void:
	## Art is 1920x1080 and scales (fractionally) to any window, e.g. exactly 2x on a 4K screen.
	## F11 or Alt+Enter toggles fullscreen; the choice is remembered.
	var cfg := ConfigFile.new()
	cfg.load(SETTINGS)
	if bool(cfg.get_value("video", "fullscreen", false)):
		DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_FULLSCREEN)
	else:
		_fit_window()


func _fit_window() -> void:
	# open the window at the largest 16:9 size that comfortably fits the screen
	var screen := DisplayServer.screen_get_usable_rect(DisplayServer.window_get_current_screen())
	var w := mini(int(screen.size.x * 0.9), int(screen.size.y * 0.9 * 16.0 / 9.0))
	var size := Vector2i(w, int(w * 9.0 / 16.0))
	DisplayServer.window_set_size(size)
	DisplayServer.window_set_position(screen.position + (screen.size - size) / 2)


func toggle_fullscreen() -> void:
	var full := DisplayServer.window_get_mode() == DisplayServer.WINDOW_MODE_FULLSCREEN \
			or DisplayServer.window_get_mode() == DisplayServer.WINDOW_MODE_EXCLUSIVE_FULLSCREEN
	if full:
		DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_WINDOWED)
		_fit_window()
	else:
		DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_FULLSCREEN)
	var cfg := ConfigFile.new()
	cfg.load(SETTINGS)
	cfg.set_value("video", "fullscreen", not full)
	cfg.save(SETTINGS)


# --- title / ending ---------------------------------------------------------
func _title() -> void:
	busy = true
	ui.fade_rect.color.a = 1.0
	ui.show_card(["N I G H T S H I F T", "", "Case 1: Dead Piano Player", "", "",
			"Click to begin" + ("   -   F9 to continue" if Game.has_save() else "")],
			[Color(0.45, 0.75, 1.0), Color.WHITE, Color(0.8, 0.75, 0.65), Color.WHITE, Color.WHITE, Color(1, 0.85, 0.45)])
	await wait_click()
	ui.hide_card()
	if _load_requested:
		await _load()
		return
	Game.reset()
	await change_room("squad_room", "start")
	busy = true
	await room.intro()
	ui.toast("Right click to look, left click to use.", 3.5)
	busy = false


func case_card(time: String, title: String) -> void:
	## Title card between two cases ("1:40 a.m.  Case 2: Five Stars"). Click to go on; F9 loads instead,
	## which frees the calling room, so nothing after this runs in that case.
	busy = true
	await ui.fade_to(1.0, 1.2)
	ui.show_card([time, "", title, "", "", "Click to continue"],
			[Color(0.45, 0.75, 1.0), Color.WHITE, Color(0.85, 0.8, 0.7), Color.WHITE, Color.WHITE, Color(0.6, 0.6, 0.6)])
	await wait_click()
	ui.hide_card()
	if _load_requested:
		await _load()


func end_case(time: String, next_case: String, done_case: int) -> void:
	## Title card for the next case, which isn't built yet, so this ends the game for now.
	busy = true
	await ui.fade_to(1.0, 1.2)
	ui.show_card([time, "", next_case, "", "",
			"END OF CASE %d - thanks for playing" % done_case, "", "Click to play again"],
			[Color(0.45, 0.75, 1.0), Color.WHITE, Color(0.85, 0.8, 0.7), Color.WHITE, Color.WHITE,
			Color(1, 0.85, 0.45), Color.WHITE, Color(0.6, 0.6, 0.6)])
	await wait_click()
	ui.hide_card()
	if _load_requested:
		await _load()
		return
	Game.reset()
	await change_room("squad_room", "start")
	busy = true
	await room.intro()
	busy = false


func _load() -> void:
	_load_requested = false
	busy = true
	Game.load_game()
	await change_room(Game.current_room, "__load")
	ui.toast("Game loaded.")


# --- rooms ------------------------------------------------------------------
func change_room(id: String, from_room: String) -> void:
	busy = true
	Game.select_item("")
	ui.hide_device()
	if ui.fade_rect.color.a < 0.99:
		await ui.fade_to(1.0, 0.35)
	if player.get_parent():
		player.get_parent().remove_child(player)
	if room:
		room.queue_free()
		room = null
	var scene: PackedScene = load("res://scenes/rooms/%s.tscn" % id)
	room = scene.instantiate()
	room.main = self
	room.player = player
	world.add_child(room)
	room.get_node("Actors").add_child(player)
	player.stop()
	player.position = Game.player_position if from_room == "__load" else room.spawn_point(from_room)
	player.set_room(room)
	player.visible = room.show_player
	if from_room != "__load":
		match from_room:
			"squad_room": player.face("down")
			"street": player.face("down" if id == "squad_room" else "right")
			"pier9_dock": player.face("down")
			"vance_office": player.face("down")
			_: player.face("right")
	Game.current_room = id
	await ui.fade_to(0.0, 0.45)
	await room.on_enter(from_room)
	busy = false


# --- per frame ----------------------------------------------------------------
func _process(_delta: float) -> void:
	var m := world.get_global_mouse_position()
	var hover := ""
	var hot := false
	if room and not _speaking and not _choosing and ui.card.visible == false:
		var inv_item := ui.item_under(m)
		if inv_item != "":
			hover = _hover_text(Game.item_name(inv_item))
			hot = true
		elif not ui.is_over_bar(m):
			var hs := room.hotspot_at(m)
			if hs:
				hover = _hover_text(hs.display_name)
				hot = true
	ui.set_hover("" if busy else hover, m)
	ui.update_cursor(m, hot and not busy)
	ui.update_bar(m, room != null and not busy)


func _hover_text(target: String) -> String:
	if Game.selected_item != "":
		return "Use %s with %s" % [Game.item_name(Game.selected_item), target]
	return target


# --- input --------------------------------------------------------------------
func _unhandled_input(event: InputEvent) -> void:
	var mb := event as InputEventMouseButton
	var key := event as InputEventKey
	if mb and mb.pressed:
		if not (mb.button_index in [MOUSE_BUTTON_LEFT, MOUSE_BUTTON_RIGHT]):
			return
		if _waiting_click:
			_waiting_click = false
			return
		if _speaking:
			_skip = true
			return
		if busy or _choosing or room == null:
			return
		var p: Vector2 = world.get_global_mouse_position()
		var hs := room.hotspot_at(p)
		if mb.button_index == MOUSE_BUTTON_RIGHT:
			if Game.selected_item != "":
				Game.select_item("")
			elif hs:
				_run_action(hs, "look", "", p)
			return
		if Game.selected_item != "":
			if hs:
				_run_action(hs, "use", Game.selected_item, p)
			else:
				Game.select_item("")
		elif hs:
			_run_action(hs, "use", "", p)
		else:
			_action_token += 1
			player.walk_to(room.clamp_to_walkable(p))
	elif key and key.pressed and not key.echo:
		if _choosing and key.keycode >= KEY_1 and key.keycode <= KEY_9:
			var idx: int = key.keycode - KEY_1
			if idx < ui.options.size():
				ui.choice_made.emit(idx)
			return
		if key.keycode == KEY_F11 or (key.keycode == KEY_ENTER and key.alt_pressed):
			toggle_fullscreen()
			return
		match key.keycode:
			KEY_SPACE, KEY_PERIOD:
				if _speaking:
					_skip = true
			KEY_ESCAPE:
				if _speaking:
					_skip = true
				else:
					Game.select_item("")
			KEY_TAB:
				ui.bar_pinned = not ui.bar_pinned
			KEY_F5:
				if not busy and room:
					Game.player_position = player.position
					ui.toast("Game saved." if Game.save_game() else "Could not save.")
			KEY_F9:
				if not Game.has_save():
					ui.toast("No saved game.")
				elif _waiting_click:          # on the title / end card
					_load_requested = true
					_waiting_click = false
				elif not busy and not _speaking and not _choosing:
					await _load()


func _run_action(hs: Hotspot, verb: String, item: String, click: Vector2) -> void:
	_action_token += 1
	var token := _action_token
	if verb == "use" and hs.walk_to != Vector2.ZERO:
		await player.walk_to(hs.walk_to)
		if token != _action_token:
			return   # player clicked somewhere else while walking
	if hs.face != "none":
		player.face(hs.face)
	else:
		player.face_point(click)
	busy = true
	Game.select_item("")
	await room.interact(hs, verb, item)
	busy = false


func _on_inventory_clicked(id: String, button: int) -> void:
	if busy or _speaking or _choosing:
		return
	if button == MOUSE_BUTTON_RIGHT:
		busy = true
		Game.select_item("")
		await examine_item(id)
		busy = false
	elif button == MOUSE_BUTTON_LEFT:
		if Game.selected_item == "":
			Game.select_item(id)
		elif Game.selected_item == id:
			Game.select_item("")
		else:
			busy = true
			Game.select_item("")
			await say("Those two don't go together.")
			busy = false


func examine_item(id: String) -> void:
	match id:
		"case_file":
			player.face("down")
			await player.play_action("notebook")
			await say("Daniel 'Danny' Reyes, 34. Piano player at the Blue Note.")
			await say("Found in the alley next to the club, two nights ago. Wallet still on him.")
			await say("One shot, a .38, close enough to leave powder on his shirt.")
			clue("clue_38")
			await say("No phone. A musician without a phone. The uniforms looked everywhere but the right place.")
			clue("clue_wallet_phone")
			await say("The bartender, Sal Moretti, told the uniforms he saw nothing.")
			await say("Sal sees everything. That's his job.")
			Game.set_flag("read_file")
		"notebook":
			var lines := Game.clues(Game.current_case())
			if lines.is_empty():
				await say("My notebook. A fresh page. The night is young." if Game.current_case() > 1
						else "My notebook. Empty so far. The night is young.")
				return
			player.face("down")
			await player.play_action("notebook")
			for c in lines:
				await say(Game.clue_text(c))
		"envelope":
			await say("A Blue Note envelope, empty, singed. On the back in Danny's hand: '1 of 3.'")
			await say("Whoever was paying Danny, they were on an installment plan.")
		"frozen_peas":
			if room.has_method("open_peas"):
				await room.open_peas()
			else:
				await say(Game.ITEMS[id]["desc"])
		"ride_receipt":
			await say("My photo of Kenji's screen. Wednesday, 1:10 a.m. Blue Note, Hollywood, to Pryce Tower, Century City.")
			await say("Rider: Walt B. One star. \"Wet, rude, smelled like gun oil.\"")
		_:
			await say(Game.ITEMS.get(id, {}).get("desc", "It's a %s." % Game.item_name(id)))


# --- scripting API used by room scripts -----------------------------------------
func clue(id: String) -> void:
	## Ray writes a fact in his notebook (a flag with the clue's id, see Game.CLUES).
	if Game.flag(id):
		return
	Game.set_flag(id)
	if not Game.flag("notebook_hint"):
		Game.set_flag("notebook_hint")
		ui.toast("Notebook updated. Right-click the notebook in the inventory to read it.", 3.5)
	else:
		ui.toast("Notebook updated.")


func narrate(text: String) -> void:
	## Ray's voice-over, for scenes where he isn't on screen (the drive, the murder board).
	await _show_text(text, Vector2(960, 1000), PLAYER_COLOR)


func drive_begin() -> void:
	## Cut to the rain-on-windshield transition. Follow with narrate()/text_message(), then drive_end().
	busy = true
	await ui.fade_to(1.0, 0.6)
	ui.show_drive()
	await ui.fade_to(0.0, 0.6)


func drive_wait(seconds: float) -> void:
	## Let the drive roll for a while. A click (or Space) skips it.
	_speaking = true
	_skip = false
	var t := 0.0
	while t < seconds and not _skip:
		await get_tree().process_frame
		t += get_process_delta_time()
	_speaking = false
	_skip = false


func drive_end() -> void:
	## Fade to black and drop the transition; change_room() fades the next room in.
	await ui.fade_to(1.0, 0.6)
	ui.hide_drive()


func text_message(text: String, outgoing: bool, contact := "") -> void:
	## A text on Ray's phone. Stays on screen until drive_end() or ui.hide_phone().
	ui.show_phone_text(text, outgoing, contact)
	_speaking = true
	_skip = false
	var t := 0.0
	var duration := clampf(1.2 + text.length() * 0.05, 1.8, 5.0)
	while t < duration and not _skip:
		await get_tree().process_frame
		t += get_process_delta_time()
	_speaking = false
	_skip = false


func say(text: String) -> void:
	## The detective says a line. Await it.
	player.set_talking(true)
	var anchor := player.global_position - Vector2(0, player.height() + 12)
	await _show_text(text, anchor, PLAYER_COLOR)
	player.set_talking(false)


func voice(text: String, anchor: Vector2, color := Color(0.6, 0.85, 1.0)) -> void:
	## Someone off-screen or unseen speaks from `anchor` (room coordinates).
	await _show_text(text, anchor, color)


func _show_text(text: String, anchor: Vector2, color: Color) -> void:
	ui.set_hover("", Vector2.ZERO)
	ui.show_speech(text, anchor, color)
	_speaking = true
	_skip = false
	var duration := clampf(0.9 + text.length() * 0.055, 1.6, 6.5)
	var t := 0.0
	while t < duration and not _skip:
		await get_tree().process_frame
		t += get_process_delta_time()
	_speaking = false
	_skip = false
	ui.hide_speech()


func device(title: String, tabs: Array, active: int, body: String, rows: Array) -> String:
	## A phone or car screen (see GameUI.show_device): tabs along the top, a body text, tappable rows and a
	## Close button. Returns "tab:<i>", "row:<i>" or "close". The screen stays up while Ray talks about
	## what he tapped; call it again to show the next state, or ui.hide_device() when done.
	_choosing = true
	ui.show_device(title, tabs, active, body, rows, true)
	var idx: int = await ui.choice_made
	ui.lock_device()
	_choosing = false
	if idx < tabs.size():
		return "tab:%d" % idx
	if idx < tabs.size() + rows.size():
		return "row:%d" % (idx - tabs.size())
	return "close"


func choose(options: Array) -> int:
	## Show dialogue options and return the chosen index.
	_choosing = true
	ui.show_choices(options)
	var idx: int = await ui.choice_made
	ui.hide_choices()
	_choosing = false
	return idx


func give(item: String, animate := true) -> void:
	if animate:
		await player.play_action("pickup")
	Game.add_item(item)
	ui.toast("Picked up: %s" % Game.item_name(item))


func take(item: String) -> void:
	Game.remove_item(item)


func walk(to: Vector2) -> void:
	await player.walk_to(to)


func wait(seconds: float) -> void:
	await get_tree().create_timer(seconds).timeout


func wait_click() -> void:
	_waiting_click = true
	while _waiting_click:
		await get_tree().process_frame
