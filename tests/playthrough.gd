extends Node
## Automated playthrough of Case 1. Runs the real game (scenes/main.tscn) at high speed, clicks
## hotspots through Main's own action path, skips every line and picks dialogue options by text,
## then checks the flags the later cases depend on.
##
## Godot_v4.7_console.exe --headless --path . res://tests/playthrough.tscn
## Exit code 0 = the case can be finished; 1 = something went wrong (see the output).

const MainScene := preload("res://scenes/main.tscn")

var main: Node
var _choices: Array[String] = []
var _failed := false
var _step := "start"
var _step_started := 0
var _shots := {}         ## with `-- --shots`: screenshots of the drive, phone and board, saved to user://


var _user_save := ""     ## the player's own quicksave, put back when the test ends


func _ready() -> void:
	if Game.has_save():
		_user_save = FileAccess.get_file_as_string(Game.SAVE_PATH)
	Engine.time_scale = 8.0
	_step_started = Time.get_ticks_msec()
	main = MainScene.instantiate()
	add_child(main)
	_run()


func _process(_delta: float) -> void:
	if main == null:
		return
	if not _failed and Time.get_ticks_msec() - _step_started > 45000:
		_fail("stuck at '%s' (room %s, busy %s, speaking %s, choosing %s, waiting click %s, fade %.2f)" % [_step,
				main.room.room_id if main.room else "-", main.busy, main._speaking, main._choosing,
				main._waiting_click, main.ui.fade_rect.color.a])
	if "--shots" in OS.get_cmdline_user_args():
		for key in ["drive", "phone", "board", "pier9_dock", "vance_office", "street"]:
			var on: bool = (main.ui.get(key) != null) if key in ["drive", "phone", "board"] 					else (main.room != null and main.room.room_id == key and not main.busy and main.ui.fade_rect.color.a < 0.01)
			if on:
				_shots[key] = int(_shots.get(key, 0)) + 1
			if _shots.get(key, 0) == 20:      # a few frames in, once fades and layout have settled
				get_viewport().get_texture().get_image().save_png("user://shot_%s.png" % key)
	if main._speaking:
		main._skip = not ("--shots" in OS.get_cmdline_user_args() and main.ui.board != null)
	if main._choosing:
		_answer()


func _answer() -> void:
	var opts: Array[String] = []
	for b in main.ui.choices_box.get_children():
		if b is Button and not b.is_queued_for_deletion():
			opts.append(String(b.text).split(". ", true, 1)[1])
	if opts.is_empty():
		return
	if _choices.is_empty():
		_fail("no scripted answer for choice: %s" % [opts])
		return
	var want: String = _choices.pop_front()
	var idx := opts.find(want)
	if idx < 0:
		_fail("option '%s' not offered in %s" % [want, opts])
		return
	print("    > ", want)
	main.ui.choice_made.emit(idx)


func _fail(msg: String) -> void:
	if _failed:
		return
	_failed = true
	printerr("PLAYTHROUGH FAILED: ", msg)
	_quit(1)


func _quit(code: int) -> void:
	if _user_save != "":
		FileAccess.open(Game.SAVE_PATH, FileAccess.WRITE).store_string(_user_save)
	elif Game.has_save():
		DirAccess.remove_absolute(ProjectSettings.globalize_path(Game.SAVE_PATH))
	get_tree().quit(code)


func _idle() -> void:
	## Wait until the game is ready for input again.
	for i in 3:
		await get_tree().process_frame
	while main.busy or main._speaking or main._choosing:
		await get_tree().process_frame


func act(hotspot: String, verb := "use", item := "", answers: Array[String] = []) -> void:
	await _idle()
	if _failed:
		return
	var hs: Hotspot = main.room.hotspot(hotspot)
	if hs == null:
		_fail("no hotspot '%s' in %s" % [hotspot, main.room.room_id])
		return
	if item != "" and not Game.has_item(item):
		_fail("'%s' is not in the inventory (%s)" % [item, Game.inventory])
		return
	_step = "%s %s%s  [%s]" % [verb, hotspot, (" with " + item) if item != "" else "", main.room.room_id]
	_step_started = Time.get_ticks_msec()
	print("  ", _step)
	_choices = answers.duplicate()
	# A room script that changes rooms is freed mid-coroutine and never returns, so don't await the
	# action itself: wait until it finishes, or until a new room has faded in and the game is idle.
	var done := [false]
	var old_room: int = main.room.get_instance_id()
	var run := func() -> void:
		await main._run_action(hs, verb, item, hs.walk_to)
		done[0] = true
	run.call()
	while not done[0] and not _failed:
		await get_tree().process_frame
		if main._waiting_click or (main.room.get_instance_id() != old_room and not main.busy and not main._speaking and not main._choosing):
			break
	if not main._waiting_click:
		await _idle()
	if not _choices.is_empty():
		_fail("answers left over: %s" % [_choices])


func expect_room(id: String) -> void:
	await _idle()
	if main.room.room_id != id:
		_fail("expected to be in %s, but in %s" % [id, main.room.room_id])


func expect(flags: Array[String]) -> void:
	for f in flags:
		if not Game.flag(f):
			_fail("flag '%s' not set" % f)


func _run() -> void:
	# title card -> new game
	while not main._waiting_click:
		await get_tree().process_frame
	main._waiting_click = false
	await expect_room("squad_room")
	print("Scene 1: the squad room")
	await act("lamp", "look")
	await act("door")                                   # refuses without the file
	await act("lamp")
	await act("cabinet", "use", "key")
	await _idle()
	main.busy = true
	await main.examine_item("case_file")
	await main.examine_item("notebook")
	main.busy = false
	await act("phone")                                  # Doyle's voicemail
	await act("mug")
	await act("wastebasket", "use", "coffee")
	expect(["got_key", "cabinet_open", "read_file", "clue_38", "clue_wallet_phone", "heard_voicemail", "found_dime"])
	await act("door")
	await expect_room("street")

	print("Scene 2: the street")
	await act("rezoning", "look")
	await act("payphone", "look")
	await act("payphone", "look")
	await act("payphone", "use", "dime")                 # no number yet
	await act("bar_door")                               # nobody answers
	await act("car")                                    # not before Sal
	await act("trash_can")
	await act("payphone", "use", "dime", ["Wrong number. Sorry."])
	await act("payphone", "use", "dime", ["Is this Sal?", "I'm calling about Danny Reyes.", "Who am I talking to?",
			"How do I get Sal to open the door?"])
	await act("bar_door", "use", "", ["Police. Open the door, Sal.", "Did you see who shot him?",
			"Who did Danny owe money to?"])
	expect(["got_matchbook", "met_nina", "knows_knock", "clue_knock", "talked_to_sal", "clue_vance", "saw_rezoning"])
	await act("car")                                    # the drive south (scene 3)
	await expect_room("pier9_dock")

	print("Scene 4: Pier 9")
	await act("tiny", "look")
	await act("tiny", "use", "", ["Nice radio.", "LAPD.", "Never mind."])
	await act("green_door")                             # too early: second failure gives the hint
	await act("barrel")
	await act("car")
	await act("tiny", "use", "matchbook")
	await act("green_door")                             # Danny's knock
	expect(["tiny_softened", "in_vance_office"])
	await expect_room("vance_office")

	print("Scene 5: Vance's office")
	await act("gun", "look")
	await act("vance", "use", "case_file")
	await act("ledger")
	await act("vance", "use", "", ["Danny Reyes owed you money.", "Where were you Tuesday night?", "That's a .45.",
			"I'll be going."])
	await expect_room("pier9_dock")
	await act("green_door")                             # Tiny waves him through now
	await expect_room("vance_office")
	await act("markers")
	await act("vance", "use", "", ["Danny's marker says PAID.", "How did he pay you?", "Anyone else asking about Danny?",
			"I'll be going."])
	expect(["clue_alibi", "saw_paid", "clue_paid", "knows_envelope", "heard_caller"])
	await expect_room("pier9_dock")

	print("Scene 6: the burn barrel")
	await act("barrel")                                 # not with his hand
	await act("tiny")
	await act("car")                                    # not without the envelope
	await act("piling")
	await act("barrel", "use", "gaff")
	expect(["got_envelope"])
	if Game.has_item("gaff"):
		_fail("the boat hook should be back on the piling")
	# quick save / load round trip
	Game.player_position = main.player.position
	Game.save_game()
	await main._load()
	await expect_room("pier9_dock")
	await act("car")                                    # drive back
	await expect_room("squad_room")

	print("Scene 7: the murder board")
	await act("door")
	await act("phone")
	await act("case_board", "use", "envelope", ["A street robbery gone wrong.", "Over the money he owed Vance.",
			"For something he had.", "Vance was in Avalon", "Wallet left, phone gone"])
	expect(["case1_deduced", "board_envelope"])
	await act("phone")                                  # Doyle, then Otis with Case 2
	while not main._waiting_click and not _failed:
		await get_tree().process_frame
	expect(["told_doyle", "case1_done"])
	if _failed:
		return
	print("PLAYTHROUGH OK - Case 1 finished. Flags: ", Game.flags.keys())
	_quit(0)
