extends Node
## Automated playthrough of Cases 1 and 2. Runs the real game (scenes/main.tscn) at high speed, clicks
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
		for key in ["drive", "phone", "board", "device", "pier9_dock", "vance_office", "street", "mulholland_overlook",
				"norms_diner", "kenji_apartment", "prius_interior"]:
			var ui_key: bool = key in ["drive", "phone", "board", "device"]
			var on: bool = (main.ui.get(key) != null) if ui_key \
					else (main.room != null and main.room.room_id == key and not main.busy and main.ui.fade_rect.color.a < 0.01)
			var shot: String = key + ("_case2" if ui_key and Game.flag("case1_done") else "")
			if on:
				_shots[shot] = int(_shots.get(shot, 0)) + 1
			if _shots.get(shot, 0) == 20:      # a few frames in, once fades and layout have settled
				get_viewport().get_texture().get_image().save_png("user://shot_%s.png" % shot)
	if main._speaking:
		main._skip = not ("--shots" in OS.get_cmdline_user_args() and (main.ui.board != null or main.ui.device != null))
	if main._choosing:
		_answer()


func _answer() -> void:
	var opts: Array[String] = main.ui.options.duplicate()
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
	print("Case 1 finished.")
	main._waiting_click = false                         # the "Case 2: Five Stars" card
	await expect_room("mulholland_overlook")
	if Game.has_item("envelope") or not Game.has_item("notebook"):
		_fail("Case 1 items should stay on the desk, the notebook should come along: %s" % [Game.inventory])
	await _case2()
	if _failed:
		return
	print("PLAYTHROUGH OK - Cases 1 and 2 finished. Flags: ", Game.flags.keys())
	_quit(0)


func _case2() -> void:
	print("Case 2, scene 2: the Mulholland overlook")
	await act("car")                                    # Shah wants a word first
	await act("inside")                                 # lean into the car
	await expect_room("prius_interior")
	if main.player.visible:
		_fail("the detective shouldn't be drawn in the close-up")
	await act("phone_mount")                            # no gloves, no touching
	await act("out")
	await expect_room("mulholland_overlook")
	await act("park", "use", "", ["What have we got?", "Who was his last passenger?", "Anything else from the couple?",
			"That'll do."])
	await act("shah", "use", "", ["How did he die?", "When?", "Anything else?", "Thanks, Anita."])
	expect(["met_park", "gloved", "clue_cabin_camera", "clue_brielle_alibi", "clue_walker", "clue_ligature", "clue_tod"])
	await act("car")                                    # not yet: the car still has things to tell
	await act("inside")
	await expect_room("prius_interior")
	await act("ignition")                               # read the screen first
	await act("phone_mount", "use", "", ["Trips", "Earlier this week >", "More v", "More v",
			"Wed 1:10 AM  Blue Note, Hollywood > Pryce Tower, Century City  -  Walt B.  *1", "< Back to tonight",
			"Messages", "Close"])
	expect(["clue_last_trip", "clue_threat", "got_ride_receipt"])
	await act("head_unit", "use", "", ["Radio", "Navigation", "Recent destinations", "Close"])
	expect(["clue_gps", "clue_off_app"])
	await act("ignition")
	await act("glovebox", "use", "kenji_keys")
	await act("door_pocket")
	await act("visor")
	await act("dashcam")
	await act("cups")
	await act("back_seat", "look")
	await act("kenji", "look")
	await act("out")
	await expect_room("mulholland_overlook")
	if not main.player.visible:
		_fail("the detective should be back in view")
	await act("prius", "look")
	await act("prius")
	await act("ground", "look")
	await act("wall", "use", "driver_card")
	expect(["got_kenji_keys", "clue_empty_case", "got_receipt", "got_driver_card", "clue_dashcam", "clue_two_cups",
			"clue_rat", "saw_grit"])
	await act("car", "use", "", ["Not yet."])
	expect(["left_overlook"])
	if Game.has_item("kenji_keys"):
		_fail("Kenji's keys should have gone to Park")
	await act("car", "use", "", ["Norm's on Sunset"])
	await expect_room("norms_diner")

	print("Case 2, scene 3: Norm's on Sunset")
	await act("rosa")                                   # too busy
	await act("rosa", "use", "driver_card")             # still too busy
	await act("coffee_pot", "look")
	await act("coffee_pot")                             # Ray pours
	await act("rosa", "use", "", ["I'm looking for a Glide driver. Kenji Ota."])
	await act("rosa", "use", "driver_card")
	await act("rosa", "use", "", ["Who paid?", "When did they leave?", "Can I see the card slip?", "Thanks, Rosa."])
	expect(["helped_rosa", "clue_roommate_norms", "got_card_slip"])
	await act("heck", "use", "", ["Kenji Ota.", "\"I'll put you in the ground.\"", "Was Kenji into anything?",
			"What about his roommate?", "Never mind."])
	await act("heck", "use", "driver_card")
	await act("booth6")
	expect(["clue_heck_alibi", "clue_side_thing", "clue_napkin"])
	await act("door", "use", "", ["Kenji's place, Silver Lake"])
	await expect_room("kenji_apartment")

	print("Case 2, scene 4: the apartment")
	await act("fridge")                                 # Devin's leaning on it
	await act("devin", "use", "", ["Who are you?", "When did you last see Kenji?", "Did Kenji have enemies?",
			"Mind if I look around?", "I'll be in touch."])
	await act("camera_bag", "look")
	await act("sneakers", "look")
	await act("laptop", "look")
	await act("kenji_desk")
	await act("photos")
	await act("devin", "use", "card_slip")              # the first lie
	await act("devin", "use", "", ["His car never came back here."])
	expect(["clue_devin_story", "clue_strap", "clue_sneakers", "clue_laptop", "clue_kenji_quitting", "devin_lie1_broken",
			"search_consent"])
	await act("front_door")                             # not before the search
	await act("fridge", "look")
	await act("freezer", "look")
	await act("freezer")
	await _idle()
	main.busy = true
	await main.examine_item("frozen_peas")              # the cards, a lawyer, and Park up the stairs
	main.busy = false
	expect(["clue_peas_note", "got_peas", "got_sd_cards", "devin_arrested"])
	if not Game.has_item("sd_cards") or Game.has_item("frozen_peas"):
		_fail("the peas should have become the dashcam and cards: %s" % [Game.inventory])
	# quick save / load round trip in a Case 2 room
	Game.player_position = main.player.position
	Game.save_game()
	await main._load()
	await expect_room("kenji_apartment")
	if main.room.get_node("Devin_couch").visible or main.room.get_node("Devin_fridge").visible:
		_fail("Devin should be gone after the arrest")
	await act("front_door", "use", "", ["Room 214"])    # the drive back, and Maya
	await expect_room("squad_room")

	print("Case 2, scene 5: the murder board")
	await act("door")
	await act("phone")
	await act("case_board", "use", "ride_receipt")      # "After Kenji."
	await act("case_board", "use", "card_slip", ["A stranger he picked up off the app.", "Heck Dominguez, the rival driver.",
			"Devin Clark, his roommate.", "Kenji's note: giving Carla the cards", "Dashcam and memory cards, in the peas"])
	while not main._waiting_click and not _failed:      # Doyle, then Otis with Case 3
		await get_tree().process_frame
	expect(["case2_deduced", "board_ride_receipt", "case2_done"])
	if not main.room.get_node("Board_kenji").visible or not main.room.get_node("Board_receipt").visible:
		_fail("the board should keep Kenji's corner and the ride receipt")
