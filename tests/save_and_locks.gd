extends "res://tests/playthrough.gd"
## The soft-lock fixes and the save slots: the overlook stays on Case 2's car menu, Park takes Kenji's keys only when Ray
## drives off, a left click opens Ray's phone, F9 mid-walk can't fire the click in the loaded game, and the three-slot
## save menu (overwrite question, exit without saving, damaged saves). The player's own slots are put back afterwards.
##
## Godot_v4.7_console.exe --headless --path . res://tests/save_and_locks.tscn
## Exit code 0 = all of it holds; 1 = something went wrong (see the output).


func _run() -> void:
	_step = "waiting for the title screen"
	while not main._on_title and not _failed:
		await get_tree().process_frame
	main.ui.title.new_button.pressed.emit()
	await _idle()
	Game.restore_saves({})
	_step_started = Time.get_ticks_msec()
	_step = "_slots_and_menu"
	await _slots_and_menu()
	_step_started = Time.get_ticks_msec()
	_step = "_f9_mid_walk"
	await _f9_mid_walk()
	_step_started = Time.get_ticks_msec()
	_step = "_overlook_menu"
	await _overlook_menu()
	_step_started = Time.get_ticks_msec()
	_step = "_phone_click"
	await _phone_click()
	_step_started = Time.get_ticks_msec()
	_step = "_case5_door"
	await _case5_door()
	if _failed:
		return
	print("SAVE AND LOCK CHECKS OK")
	_quit(0)


func _slots_and_menu() -> void:
	print("Save slots")
	Game.player_position = Vector2(500, 900)
	Game.set_flag("case1_done")
	if not Game.save_game(2):
		_fail("saving to slot 2 should work")
	if Game.slot_info(1) != {} or int(Game.slot_info(2)["case"]) != 2 or String(Game.slot_info(2)["time"]).length() != 16:
		_fail("slot info should be empty for slot 1 and have the case and 'YYYY-MM-DD HH:MM' for slot 2: %s" % [Game.slot_info(2)])
	# a damaged slot: refused, and nothing changes
	var f := FileAccess.open(Game.slot_path(3), FileAccess.WRITE)
	f.store_string("{\"flags\": {")
	f.close()
	var before := Game.flags.duplicate(true)
	if Game.load_game(3) or Game.flags != before:
		_fail("a damaged slot should not load or change anything")
	if not Game.slot_info(3).get("damaged", false):
		_fail("a damaged slot should say so")
	if await main._load(3):
		_fail("Main._load of a damaged slot should return false")
	# a slot with a good .bak loads from it
	var good := FileAccess.get_file_as_string(Game.slot_path(2))
	f = FileAccess.open(Game.slot_path(3) + ".bak", FileAccess.WRITE)
	f.store_string(good)
	f.close()
	if not Game.load_game(3):
		_fail("a damaged slot with an intact .bak should load the .bak")
	DirAccess.remove_absolute(ProjectSettings.globalize_path(Game.slot_path(3) + ".bak"))
	# the menu
	var results: Array[String] = []
	var menu: SaveMenu = main.ui.open_save_menu("save", true)
	menu.result.connect(func(k: String): results.append(k))
	var buttons: Array = menu.find_children("*", "Button", true, false)
	if buttons.size() != 5:
		_fail("three slots, EXIT WITHOUT SAVING and BACK, not %d buttons" % buttons.size())
		return
	buttons[0].pressed.emit()                       # empty slot 1: saves at once
	buttons[1].pressed.emit()                       # slot 2 holds a game: asks first
	if results != ["save:1"]:
		_fail("an empty slot should save at once and a full one should ask first: %s" % [results])
	var texts: Array[String] = []
	for b: Button in menu.find_children("*", "Button", true, false):
		texts.append(b.text)
	if texts != ["YES, OVERWRITE", "NO"]:
		_fail("the overwrite question should offer YES, OVERWRITE and NO, not %s" % [texts])
	menu.back()                                     # Esc answers NO
	if menu.find_children("*", "Button", true, false).size() != 5:
		_fail("Esc on the overwrite question should go back to the slots")
	menu.find_children("*", "Button", true, false)[1].pressed.emit()
	for b: Button in menu.find_children("*", "Button", true, false):
		if b.text == "YES, OVERWRITE":
			b.pressed.emit()
	if results != ["save:1", "save:2"]:
		_fail("YES should save: %s" % [results])
	main.ui.close_save_menu()
	# load mode: empty and damaged slots can't be picked
	menu = main.ui.open_save_menu("load", false)
	buttons = menu.find_children("*", "Button", true, false)
	var disabled := 0
	for b: Button in buttons:
		disabled += 1 if b.disabled else 0
	if buttons.size() != 4 or disabled != 2:
		_fail("load mode: three slots and BACK, with the empty slot 1 and the damaged slot 3 off (%d buttons, %d off)" % [buttons.size(), disabled])
	main.ui.close_save_menu()
	# Esc: BACK stays in the room, EXIT WITHOUT SAVING goes to the title without touching the slots
	var snap := Game.snapshot_saves()
	var esc := InputEventKey.new()
	esc.keycode = KEY_ESCAPE
	esc.pressed = true
	main._unhandled_input(esc)
	while main.ui.save_menu == null and not _failed:
		await get_tree().process_frame
	main.ui.save_menu.result.emit("back")
	await get_tree().process_frame
	if main._on_title or main.room == null or get_tree().paused:
		_fail("BACK should return to the room")
	main._unhandled_input(esc)
	while main.ui.save_menu == null and not _failed:
		await get_tree().process_frame
	main.ui.save_menu.result.emit("exit")
	while not main._on_title and not _failed:
		await get_tree().process_frame
	if Game.snapshot_saves().hash() != snap.hash():
		_fail("EXIT WITHOUT SAVING shouldn't touch the slots")
	main.ui.title.new_button.pressed.emit()
	await _idle()


func _key(code: int) -> void:
	var k := InputEventKey.new()
	k.keycode = code
	k.pressed = true
	main._unhandled_input(k)


func _f9_mid_walk() -> void:
	print("F9 while walking to a hotspot")
	Game.reset()
	await main.change_room("squad_room", "start")
	await _idle()
	Game.player_position = main.player.position
	Game.save_game(1)
	var hs: Hotspot = main.room.hotspot("lamp")
	var run := func() -> void:
		await main._run_action(hs, "use", "", hs.walk_to)
	run.call()
	for i in 6:
		await get_tree().process_frame
	if not main.player.is_walking():
		_fail("Ray should still be walking to the lamp")
	Game.slot = 1
	await main._load()
	for i in 300:
		await get_tree().process_frame
	await _idle()
	if Game.flag("got_key") or Game.has_item("key"):
		_fail("a click Ray was still walking to shouldn't fire after a load")


func _overlook_menu() -> void:
	print("Case 2: the car menu keeps the overlook")
	Game.reset()
	for f in ["case1_done", "case2_started", "gloved", "clue_brielle_alibi", "clue_last_trip", "clue_gps", "clue_off_app",
			"been_to_norms"]:
		Game.set_flag(f)
	Game.add_item("kenji_keys")
	await main.change_room("mulholland_overlook", "drive")
	await _idle()
	await act("car", "use", "", ["Not yet."])
	if Game.flag("left_overlook") or not Game.has_item("kenji_keys"):
		_fail("'Not yet.' shouldn't send Park off with the keys")
	await act("car", "use", "", ["Norm's on Sunset"])
	await expect_room("norms_diner")
	if Game.has_item("kenji_keys") or not Game.flag("left_overlook"):
		_fail("driving off should hand Park the keys")
	await act("door", "use", "", ["Mulholland overlook"])      # Rosa's coffee isn't needed to leave
	await expect_room("mulholland_overlook")
	await act("inside")
	await expect_room("prius_interior")
	await act("visor")
	if not Game.has_item("driver_card"):
		_fail("the driver card should still be on the visor, back at the overlook")


func _phone_click() -> void:
	print("Ray's phone opens on a left click")
	Game.add_item("ray_phone")
	await _idle()
	main._on_inventory_clicked("ray_phone", MOUSE_BUTTON_LEFT)
	var t0 := Time.get_ticks_msec()
	while not main._choosing and Time.get_ticks_msec() - t0 < 5000:
		await get_tree().process_frame
	if not main._choosing or main.ui.device == null:
		_fail("a left click on the phone should open it")
		return
	main.ui.choice_made.emit(99)                    # Close
	await _idle()


func _case5_door() -> void:
	print("Case 5: Room 214's door needs Shah's answer about Sal")
	Game.reset()
	for f in ["case4_done", "case5_started", "clue_nina_call"]:
		Game.set_flag(f)
	await main.change_room("squad_room", "street")
	await _idle()
	await act("door")
	await expect_room("blue_note_back")
	Game.set_flag("clue_choke")
	await act("bar_door")
	await expect_room("blue_note_bar")
