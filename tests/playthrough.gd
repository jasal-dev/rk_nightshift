extends Node
## Automated playthrough of Cases 1 to 4. Runs the real game (scenes/main.tscn) at high speed, clicks
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
var _jig_solved := false


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
	if not _failed and Time.get_ticks_msec() - _step_started > (150000 if "--shots" in OS.get_cmdline_user_args() else 45000):
		_fail("stuck at '%s' (room %s, busy %s, speaking %s, choosing %s, waiting click %s, fade %.2f)" % [_step,
				main.room.room_id if main.room else "-", main.busy, main._speaking, main._choosing,
				main._waiting_click, main.ui.fade_rect.color.a])
	if "--shots" in OS.get_cmdline_user_args():
		for key in ["drive", "phone", "board", "device", "paper", "pier9_dock", "vance_office", "street",
				"mulholland_overlook", "norms_diner", "kenji_apartment", "prius_interior", "stardust_shop",
				"stardust_office", "stardust_roof", "stardust_roof_dark", "fletcher_bridge", "river_channel", "glass_house",
				"crane_garage", "night_lab", "squad_room", "jigsaw"]:
			var ui_key: bool = key in ["drive", "phone", "board", "device", "paper", "jigsaw"]
			var on: bool = (main.ui.get(key) != null) if ui_key \
					else (main.room != null and main.room.room_id == key and not main.busy and main.ui.fade_rect.color.a < 0.01)
			var n_case: int = Game.current_case()
			var shot: String = key + ("_case%d" % n_case if (ui_key or key == "squad_room") and n_case > 1 else "")
			if on:
				_shots[shot] = int(_shots.get(shot, 0)) + 1
			if _shots.get(shot, 0) == 20:      # a few frames in, once fades and layout have settled
				get_viewport().get_texture().get_image().save_png("user://shot_%s.png" % shot)
	if main._speaking:
		main._skip = not ("--shots" in OS.get_cmdline_user_args() and (main.ui.board != null or main.ui.device != null
				or main.ui.paper != null))
	if main._choosing:
		_answer()
	if main.ui.jigsaw != null and not _jig_solved:
		# the headlight fit: drop each piece into its place, the right way up
		_jig_solved = true
		for i in 2:
			main.ui.jigsaw_place(i)
	elif main.ui.jigsaw == null:
		_jig_solved = false


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
	print("Case 2 finished.")
	main._waiting_click = false                         # the "Case 3: Walk of Fame" card, then the drive
	await expect_room("stardust_shop")
	await _case3()
	if _failed:
		return
	print("Case 3 finished.")
	main._waiting_click = false                         # the "Case 4: Low Water" card, then the drive
	await expect_room("fletcher_bridge")
	await _case4()
	if _failed:
		return
	print("PLAYTHROUGH OK - Cases 1 to 4 finished. Flags: ", Game.flags.keys())
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


func _case3() -> void:
	print("Case 3, scene 2: Stardust Memorabilia")
	for id in ["driver_card", "sd_cards", "ride_receipt", "card_slip"]:
		if Game.has_item(id):
			_fail("Case 2 items should stay behind: %s" % [Game.inventory])
	expect(["case3_started", "met_park3"])
	await act("front_door", "look")                     # the glass went out
	await act("front_door")                             # not before the arrest
	await act("display_case")                           # opened with a key: the robbery was staged
	expect(["clue_glass_out", "clue_key_opened", "clue_staged"])
	await act("register")
	await act("counter", "look")
	await act("window")
	await act("chair")
	await act("pearl", "use", "", ["What happened tonight?", "How long did you work for Gus?",
			"Who has keys to the Oscar case?", "Who'd want the Oscar?", "I'll be back."])
	await act("park", "use", "", ["Who's the man in the bathrobe?", "Anything from the canvass?", "That'll do."])
	await act("morty", "use", "", ["Who are you?", "You wanted the Oscar.", "Where were you tonight?", "Good night, Morty."])
	expect(["clue_register", "clue_pearl_story", "clue_keyholders", "clue_morty_offer", "clue_morty_alibi"])
	await act("curtain")
	await expect_room("stardust_office")

	print("Case 3, scene 3: the back office")
	await act("stairs")                                 # the sign is off: the dark roof
	await expect_room("stardust_roof_dark")
	await act("darkness", "look")
	await act("darkness")
	await act("roof_door")
	await expect_room("stardust_office")
	await act("shah", "use", "", ["How did he die?", "When?", "Did he fall, or was he helped?", "Anything else?",
			"Thanks, Anita."])
	expect(["got_gus_keys", "clue_tod_gus", "clue_pushed", "shah_palm"])
	await act("drawer")                                 # locked
	await act("desk")                                   # the eviction letter
	await act("desk")                                   # Calloway's catalogue
	await act("letter")                                 # the optional seed: Brenner's card
	expect(["clue_eviction", "got_catalogue", "got_brenner_card"])
	await act("drawer", "use", "gus_keys")              # the UV lamp
	await act("phone", "use", "", ["Out  12:52 AM  PEARL CELL  3:04", "Voicemail", "Thu  PRYCE DEV  0:22", "Close"])
	await act("pearl_locker")                           # the headshots
	await act("pearl_locker")                           # the practice signatures
	await act("pearl_locker", "use", "uv_lamp")         # nothing to compare yet
	await act("cabinet")
	await act("gus_locker", "use", "gus_keys")
	await act("gus", "look")
	await act("fuse_panel", "look")
	await act("fuse_panel")                             # the roof sign back on
	expect(["got_uv_lamp", "clue_phone_log", "clue_headshots_left", "clue_practice_sigs", "sign_on"])
	if not main.room.get_node("Sign_glow").visible:
		_fail("the sign's glow should spill down the stairs")
	await act("curtain")
	await expect_room("stardust_shop")
	await act("photo_wall", "use", "uv_lamp")
	await act("certificate", "use", "catalogue")
	await act("morty", "use", "", ["Calloway's sold No. 734.", "What does a real one weigh?", "Good night, Morty."])
	await act("park", "use", "", ["The developer's man.", "That'll do."])
	await act("display_case", "use", "gus_keys")
	expect(["clue_uv_fakes", "clue_same_serial", "clue_morty_bought", "clue_weight", "clue_whitaker_alibi"])
	await act("curtain")
	await expect_room("stardust_office")
	await act("pearl_locker", "use", "uv_lamp")         # same gold pen
	expect(["clue_gold_pen"])
	await act("stairs")
	await expect_room("stardust_roof")

	print("Case 3, scene 4: the roof")
	await act("neon", "look")
	await act("water_tank", "look")
	await act("gravel")
	await act("lawn_chair", "look")
	await act("coffee_can")
	await act("blue_note", "look")
	await act("theatre")
	await act("roof_edge", "use", "uv_lamp")
	await act("glint")                                  # the gold star earring
	await act("water_tank")                             # the "Oscar" floats
	await act("charlie", "use", "", ["What did you see tonight?", "Did you hear anything?", "You knew Gus?",
			"Ever seen this man?", "Good night, Charlie."])
	expect(["clue_footprints", "clue_cigar", "got_star_earring", "got_fake_oscar", "clue_replica", "clue_fiat",
			"clue_shouting", "clue_block_empty"])
	if main.room.get_node("Earring").visible:
		_fail("the earring should be gone from the gravel")
	await act("roof_door")
	await expect_room("stardust_office")
	await act("shah", "use", "star_earring")
	await act("curtain")
	await expect_room("stardust_shop")

	print("Case 3, scene 5: breaking Pearl")
	await act("pearl", "use", "star_earring")           # too early
	await act("pearl", "use", "fake_oscar")             # "Where was he?" "Later."
	await act("pearl", "use", "", ["Gus called you at twelve fifty-two."])
	await act("pearl", "use", "fake_oscar")             # the robbery
	await act("pearl", "look")                          # the torn earlobe
	await act("pearl", "use", "", ["Gus didn't fall."])  # the roof, and Park takes her out
	expect(["pearl_lie1_broken", "pearl_lie2_broken", "clue_bare_ear", "pearl_arrested"])
	for n in ["Actors/Pearl_chair", "Actors/Pearl_stand", "Actors/Park"]:
		if main.room.get_node(n).visible:
			_fail("%s should be gone after the arrest" % n)
	# quick save / load round trip in a Case 3 room
	Game.player_position = main.player.position
	Game.save_game()
	await main._load()
	await expect_room("stardust_shop")
	await act("morty")                                  # "He said he'd be buried with it."
	expect(["morty_lyle"])
	await act("front_door")                             # the drive back, and Maya
	await expect_room("squad_room")

	print("Case 3, scene 6: the murder board")
	await act("door")
	await act("phone")
	await act("clock")
	await act("case_board", "use", "brenner_card")      # "After Gus."
	await act("case_board", "use", "star_earring", ["Morty Kahn, the rival collector.", "Trent Whitaker, Pryce Development.",
			"A burglar off the boulevard.", "Pearl Danvers, his assistant.", "Calloway's catalogue, No. 734 sold",
			"Legal pad: \"Lyle Brandt\" forty times"])
	while not main._waiting_click and not _failed:      # Doyle, then Otis with Case 4
		await get_tree().process_frame
	expect(["case3_deduced", "board_brenner_card", "case3_done"])
	for n in ["Board_kenji", "Board_receipt", "Board_gus", "Board_brenner"]:
		if not main.room.get_node(n).visible:
			_fail("the board should show %s" % n)


func _case4() -> void:
	print("Case 4, scene 2: the Fletcher Drive bridge")
	for id in ["gus_keys", "uv_lamp", "catalogue", "star_earring", "fake_oscar", "brenner_card"]:
		if Game.has_item(id):
			_fail("Case 3 items should stay behind: %s" % [Game.inventory])
	expect(["case4_started", "met_doss"])
	await act("car")                                    # not before Owen's phone
	await act("doss", "use", "", ["What have you got?", "Who found him?", "Why's he in your car?", "Uncuff him.",
			"That'll do."])                             # "On what, a feeling?"
	await act("patrol_car", "use", "", ["Did you kill him?", "I've been somewhere.", "Hollywood Division, twenty-six years.",
			"I've been somewhere.", "Baghdad, oh-three. Military Police.", "Semper Fidelis.", "I've been somewhere.",
			"Baghdad, oh-three. Military Police.", "Assist, Protect, Defend.", "What happened tonight?",
			"Did you hear anything?", "Did you see the boy?", "Why carry the bike all the way down?", "That'll do."])
	await act("road", "look")
	await act("gutter")
	await act("storm_drain", "look")
	await act("storm_drain")
	await act("fence_gap", "look")
	await act("railing", "look")
	await act("lamps", "look")
	await act("spotlight")                              # hands off the unit
	expect(["preacher_trusts", "clue_preacher_story", "clue_bang", "clue_no_brakes", "clue_glass_bridge", "clue_scupper"])
	await act("stairs")
	await expect_room("river_channel")

	print("Case 4, scene 3: the channel")
	await act("shah", "use", "", ["How did he die?", "When?", "The scrapes on him.", "Anything else?", "Thanks, Anita."])
	await act("bike")                                   # the paint and the sliver of headlight
	await act("bike")                                   # the nursing textbook
	await act("phone", "look")                          # a $900 phone left on the bike
	await act("phone")                                  # the lock screen: Glendower, one star, 2:04
	await act("reeds")                                  # too dark
	await act("drain_pipe", "look")
	await act("east_bank", "look")
	await act("stairs", "look")                         # two sets of tracks
	await act("owen", "look")
	await act("tent", "look")
	await act("water")
	await act("willows", "look")
	expect(["clue_hit_by_car", "clue_tod_owen", "clue_moved", "clue_headlight_glass", "clue_paint", "got_lens_shard",
			"clue_nursing", "clue_phone_left", "clue_last_drop", "clue_one_star", "clue_trip_paused", "clue_drag_marks",
			"clue_bike_stairs", "clue_two_tracks"])
	if main.room.get_node("Actors/Preacher").visible or main.room.get_node("Spot").visible:
		_fail("Preacher and the spotlight shouldn't be in the channel yet")
	await act("stairs")
	await expect_room("fletcher_bridge")
	await act("doss", "use", "", ["Uncuff him."])
	await act("doss", "use", "", ["Put your spotlight on the reeds."])
	await act("patrol_car", "look")
	expect(["preacher_freed", "channel_lit"])
	# quick save / load round trip in a Case 4 room
	Game.player_position = main.player.position
	Game.save_game()
	await main._load()
	await expect_room("fletcher_bridge")
	if main.room.get_node("Preacher_car").visible or main.room.get_node("Beam_road").visible \
			or not main.room.get_node("Beam_down").visible:
		_fail("after loading, the patrol car should be empty and the spotlight on the reeds")
	await act("stairs")
	await expect_room("river_channel")
	if not main.room.get_node("Actors/Preacher").visible or not main.room.get_node("Spot").visible:
		_fail("Preacher should be at his tent and the reeds lit")
	await act("preacher", "use", "", ["Where does stuff end up, off that bridge?", "Will you be all right?",
			"Take care, Preacher."])
	await act("reeds")                                  # half a headlight, and Danny's phone
	await act("preacher", "use", "danny_phone")         # the big man in the old cop's coat
	await act("reeds")                                  # nothing else
	expect(["clue_reeds_tip", "got_lens_piece", "clue_audi", "got_danny_phone", "clue_danny_phone", "clue_big_man"])
	await act("stairs")
	await expect_room("fletcher_bridge")
	await act("car", "use", "", ["Glendower Avenue, Los Feliz"])
	await expect_room("glass_house")

	print("Case 4, scene 4: the glass house")
	await act("courtney", "use", "", ["Whose party was it?", "You ordered from Chomp tonight.", "Who left drunk tonight?",
			"You reported the rider.", "Tell her about Owen.", "1:49 AM  Front gate", "1:51 AM  Driveway",
			"1:53 AM  Front gate", "1:55 AM  Front gate", "2:38 AM  Front gate", "Close", "Who left drunk tonight?",
			"I'll let you work."])
	await act("andre", "use", "", ["Who left drunk tonight?", "I need the ticket.", "Who's the last car?", "Who left early?",
			"Thanks, Andre."])
	await act("gift_bags", "look")
	await act("gift_bags")                              # the optional seed: Pryce's invitation
	await act("curb")
	await act("easel", "look")
	await act("valet_board", "look")
	await act("gate_camera")
	await act("van", "look")
	await act("house", "look")
	await act("city")
	await _idle()
	main.busy = true
	await main.examine_item("pryce_invite")
	await main.examine_item("valet_ticket")
	main.busy = false
	expect(["clue_host", "courtney_cam", "clue_warning", "clue_crane_drunk", "clue_gate_clip", "clue_headlights_intact",
			"clue_plate", "clue_courtney_alibi", "got_valet_ticket", "clue_pryce_driver", "clue_curb_scrape",
			"got_pryce_invite", "clue_render"])
	await act("car", "use", "", ["Crane's house, Mount Washington"])    # Otis runs the plate first
	expect(["clue_crane_id"])
	await expect_room("crane_garage")

	print("Case 4, scene 5: Crane's garage")
	await act("street")                                 # not yet
	await act("audi_tarp", "look")
	await act("audi_tarp")                              # he wants a warrant
	await act("crane", "use", "", ["Where were you tonight?", "How did you get home?", "Why the tarp?", "I'll wait."])
	await act("hose", "look")
	await act("loafers", "look")
	await act("phone", "look")
	await act("jacket", "look")
	await act("house_door")
	await act("crane", "use", "valet_ticket")          # step 1: he drove; the tarp comes off
	if main.room.get_node("Tarp").visible:
		_fail("the tarp should be off")
	await act("grille")
	await act("headlight", "use", "lens_piece")         # step 2: the headlight fit
	await act("crane_step", "use", "", ["You stopped."])   # step 3, and Doss
	expect(["clue_crane_story", "clue_tarp_new", "clue_washing", "clue_loafers", "clue_crane_calls", "crane_lie1_broken",
			"tarp_off", "clue_yellow_paint", "clue_lens_match", "crane_lie2_broken", "crane_arrested"])
	for n in ["Actors/Crane_stand", "Actors/Crane_step"]:
		if main.room.get_node(n).visible:
			_fail("%s should be gone after the arrest" % n)
	Game.player_position = main.player.position
	Game.save_game()
	await main._load()
	await expect_room("crane_garage")
	if main.room.get_node("Tarp").visible or main.room.get_node("Actors/Crane_step").visible:
		_fail("after loading, the tarp should stay off and Crane gone")
	await act("street", "use", "", ["Room 214"])        # Maya, then the lab
	await expect_room("night_lab")

	print("Case 4, scene 6: the night lab")
	await act("exit")                                   # not with Danny's phone
	await act("ike")
	await act("sign", "look")
	await act("tray", "use", "danny_phone")
	expect(["phone_at_lab"])
	if Game.has_item("danny_phone") or not Game.has_item("lab_receipt"):
		_fail("the phone should be with Ike and the receipt with Ray: %s" % [Game.inventory])
	await _idle()
	main.busy = true
	await main.examine_item("lab_receipt")
	main.busy = false
	await act("exit")
	await expect_room("squad_room")

	print("Case 4, scene 7: the murder board")
	await act("door")
	await act("phone")
	await act("clock")
	await act("case_board", "use", "pryce_invite")      # "After Owen."
	await act("case_board", "use", "valet_ticket", ["Calvin \"Preacher\" Odom.", "Courtney Vail, the customer.",
			"Councilman Ted Haskell.", "Elliot Crane, Haskell's chief of staff.", "Half a headlight, an Audi part",
			"Both headlight pieces fit Crane's Audi"])
	while not main._waiting_click and not _failed:      # Doyle, then Otis: Sal. The Case 5 card.
		await get_tree().process_frame
	expect(["case4_deduced", "board_danny_phone", "board_pryce_invite", "case4_done"])
	for n in ["Board_kenji", "Board_receipt", "Board_gus", "Board_brenner", "Board_owen", "Board_phone", "Board_invite"]:
		if not main.room.get_node(n).visible:
			_fail("the board should show %s" % n)
