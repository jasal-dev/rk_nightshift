extends Room
## Inside Kenji's Prius (Case 2, scene 2, a close-up of the overlook): leaning in from the back seat, between the
## front seats, where his killer sat. Ray isn't drawn here; every hotspot is used from where he leans in.
## Nothing gets touched before Shah's gloves (the gloved flag).
## Puzzle 2.1: Kenji's Glide app (last trip 11:52, Heck's threat, and the optional ride receipt seed).
## Puzzle 2.2: the head unit's recent destinations (home, Norm's, here). Both together give clue_off_app.
## Puzzle 2.3: the ignition key only comes out after the screen has been read; it opens the glovebox.


func _init() -> void:
	show_player = false


func interact(hs: Hotspot, verb: String, item: String) -> void:
	if hs.id != "head_unit":
		await Case2.gps_hint(main)
	match hs.id:
		"kenji":
			if verb == "look":
				await main.say("Kenji Ota. Twenty-nine. His hands are still on the wheel, like he was about to go somewhere.")
			elif item != "":
				await default_response(verb, item)
			else:
				await main.say("Shah's already done everything I'd do, and better.")

		"phone_mount":
			if verb == "look":
				await main.say("His phone, still in the mount. The Glide app's open.")
			elif await _gloves(item):
				await _glide_app()

		"head_unit":
			if verb == "look":
				await main.say("The car's screen. Playing the radio to nobody." if not Game.has_item("kenji_keys")
						and not Game.flag("got_kenji_keys") else "The car's screen. Dark, now the engine's off.")
			elif await _gloves(item):
				await _head_unit()

		"dashcam":
			if verb == "look":
				await main.say("A suction mount on the windshield, empty. The power cable's unplugged and coiled neat on the dash.")
			elif await _gloves(item):
				await main.player.play_action("use")
				await main.say("Unscrewed, not ripped off. Both lenses gone, road and back seat. Somebody who knows cameras took their time.")
				main.clue("clue_dashcam")

		"cups":
			if verb == "look":
				await main.say("Two paper cups from Norm's.")
			elif await _gloves(item):
				await main.player.play_action("use")
				await main.say("One black coffee, finished. One with cream, barely touched. Both cold.")
				main.clue("clue_two_cups")

		"door_pocket":
			if verb == "look":
				await main.say("A door pocket full of mints and paper.")
			elif await _gloves(item):
				if not Game.flag("got_receipt"):
					await main.player.play_action("pickup")
					await main.say("A receipt from Norm's on Sunset. Table 6, twelve-fourteen.")
					Game.set_flag("got_receipt")
					await main.give("norms_receipt", false)
				else:
					await main.say("Mints. He cared about his rating.")

		"visor":
			if verb == "look":
				await main.say("A card clipped to the visor.")
			elif await _gloves(item):
				if not Game.flag("got_driver_card"):
					await main.player.play_action("use")
					await main.say("Kenji's Glide card. Photo, plate number, four point nine eight stars.")
					Game.set_flag("got_driver_card")
					await main.give("driver_card", false)
				else:
					await main.say("Just the visor now. And a mirror I'd rather not look in.")

		"ignition":
			if verb == "look":
				await main.say("Keys in the ignition. Engine running." if not Game.flag("got_kenji_keys")
						else "No keys. The engine's off.")
			elif await _gloves(item):
				if Game.flag("got_kenji_keys"):
					await main.say("I've got his keys.")
				elif not Game.flag("clue_gps"):
					await main.say("Kill the engine and the screen dies with it. Read it first.")
				else:
					await main.player.play_action("use")
					await main.say("Engine off. The wipers stop halfway across the glass. First quiet this car's had all night.")
					Game.set_flag("got_kenji_keys")
					await main.give("kenji_keys", false)

		"glovebox":
			if verb == "look":
				if Game.flag("clue_empty_case"):
					await main.say("Empty case, empty year.")
				else:
					await main.say("Locked. A Prius driver who locks his glovebox has something worth more than napkins.")
			elif item == "kenji_keys":
				if Game.flag("clue_empty_case"):
					await main.say("Empty case, empty year.")
				else:
					await main.player.play_action("use")
					await main.say("Registration, insurance, a phone charger. And a little plastic case with twelve slots, labeled by month, January to December.")
					await main.say("Every slot is empty.")
					await main.say("Twelve slots for memory cards. Somebody emptied a year.")
					main.clue("clue_empty_case")
			elif await _gloves(item):
				await main.say("Empty case, empty year." if Game.flag("clue_empty_case") else "Locked.")

		"back_seat":
			if verb == "look":
				await main.say("Back seat, passenger side. The seat belt's still buckled, and the floor mat's scuffed like somebody braced his feet.")
			elif item != "":
				await default_response(verb, item)
			else:
				await main.say("Whoever sat here wasn't a paying customer.")

		"out":
			if verb == "look":
				await main.say("Back out into the rain.")
			elif item != "":
				await default_response(verb, item)
			else:
				await main.change_room("mulholland_overlook", "prius_interior")

		_:
			await default_response(verb, item)


func _gloves(item: String) -> bool:
	## Prius interior: nothing gets touched before Shah's gloves. Returns true when Ray may go ahead.
	if not Game.flag("gloved"):
		await main.say("Shah will have my hands off at the wrist.")
		return false
	if item != "":
		await default_response("use", item)
		return false
	return true


# --- Puzzle 2.1: the Glide app ------------------------------------------------------
const STATUS := "You're offline.\n\nToday: 14 trips, $212.40\nRating: 4.98"
const TRIPS := [
	["11:31 PM  Echo Park > Silver Lake  -  Brielle V.  *1", ""],
	["10:46 PM  LAX > Westwood  -  Tom R.  *5", "An LAX run. Forty minutes of brake lights for thirty-one dollars."],
	["9:40 PM  Los Feliz > Cedars-Sinai  -  Ana M.  *5", "A nurse to Cedars. Nurses tip in kindness."],
	["8:52 PM  West Hollywood > Hollywood  -  Kayla + 5  *5", "A bachelorette party. Six riders, five stars, and somebody's tiara in the back seat, I'd bet."],
]
const EARLIER := [
	["Monday", ["Mon 11:58 PM  Koreatown > Los Feliz  -  Sam P.  *5", "Mon 10:12 PM  Union Station > Echo Park  -  Grace L.  *5",
			"Mon 8:30 PM  Burbank Airport > Studio City  -  Ari K.  *4"]],
	["Tuesday", ["Tue 11:41 PM  Hollywood > Silver Lake  -  Devon W.  *5", "Tue 9:05 PM  LAX > Culver City  -  Priya S.  *5",
			"Tue 7:22 PM  Downtown > Highland Park  -  Luis G.  *5"]],
	["Wednesday", ["Wed 1:10 AM  Blue Note, Hollywood > Pryce Tower, Century City  -  Walt B.  *1",
			"Wed 12:20 AM  Sunset Strip > Laurel Canyon  -  Nico F.  *5", "Wed 12:02 AM  Silver Lake > Echo Park  -  Jen T.  *5"]],
]


func _glide_app() -> void:
	await main.player.play_action("use")
	if not Game.flag("opened_glide"):
		Game.set_flag("opened_glide")
		await main.say("The phone's locked behind the app. Glide lets me in. His personal life stays private, for now.")
		main.ui.show_device("Glide Driver", ["Status", "Trips", "Messages"], 0, STATUS, [], false, Case2.GLIDE)
		await main.say("Fourteen trips tonight. Kid worked.")
	var tab := 0
	var page := -1        ## -1: tonight's trips; 0..2: "Earlier this week", one day per page
	while true:
		var body := ""
		var rows: Array = []
		match tab:
			0:
				body = STATUS
			1:
				if page < 0:
					body = "Tonight"
					for t: Array in TRIPS:
						rows.append(t[0])
					rows.append("Earlier this week >")
				else:
					body = "Earlier this week: %s" % EARLIER[page][0]
					rows = (EARLIER[page][1] as Array).duplicate()
					if page < EARLIER.size() - 1:
						rows.append("More v")
					rows.append("< Back to tonight")
			2:
				body = "Heck D.  -  Tuesday 6:02 PM\n\n\"You took my spot in the LAX queue AGAIN. Do it once more and I'll put you in the ground.\""
		var pick: String = await main.device("Glide Driver", ["Status", "Trips", "Messages"], tab, body, rows)
		if pick == "close":
			break
		if pick.begins_with("tab:"):
			tab = int(pick.substr(4))
			page = -1
			if tab == 1 and not Game.flag("clue_last_trip"):
				await main.say("His last fare ended at eleven fifty-two. After that, the app says he went home to bed.")
				main.clue("clue_last_trip")
			elif tab == 2 and not Game.flag("clue_threat"):
				await main.say("Heck D. Some people take the airport very seriously.")
				main.clue("clue_threat")
			continue
		var row: String = rows[int(pick.substr(4))]
		if row == "Earlier this week >" or row == "More v":
			page += 1
		elif row == "< Back to tonight":
			page = -1
		elif row.begins_with("Wed 1:10 AM"):
			await _ride_receipt()
		elif page >= 0:
			await main.say("Another fare, another five stars.")
		else:
			for t: Array in TRIPS:
				if t[0] == row:
					if t[1] == "":
						await main.say("Brielle V. Rider rated you one star: \"camera??\"")
						if not Game.flag("clue_last_trip"):
							await main.say("His last fare ended at eleven fifty-two. After that, the app says he went home to bed.")
							main.clue("clue_last_trip")
					else:
						await main.say(t[1])
	main.ui.hide_device()
	await _insight()


func _ride_receipt() -> void:
	## The optional seed. No fanfare: one line, a photo, and it's in Ray's phone.
	main.ui.show_device("Glide Driver", [], 0,
			"Wed 1:10 a.m.\nPickup: Blue Note, Hollywood\nDrop-off: Pryce Tower, Century City\nRider: Walt B.\n\nYou rated: 1 star\nNote: \"wet, rude, smelled like gun oil.\"",
			[], false, Case2.GLIDE)
	await main.say("Blue Note. Two nights ago. Huh.")
	if not Game.flag("got_ride_receipt"):
		Game.set_flag("got_ride_receipt")
		await main.give("ride_receipt", false)


# --- Puzzle 2.2: the car's own diary ------------------------------------------------
func _head_unit() -> void:
	await main.player.play_action("use")
	if Game.flag("got_kenji_keys"):
		await main.say("Dark. The keys are in my pocket.")
		return
	var tab := 0
	var recent := false
	while true:
		var body := ""
		var rows: Array = []
		match tab:
			0:
				body = "KJAZZ 88.1 FM\n\nPlaying to nobody."
			1:
				body = "Phone: disconnected."
			2:
				if recent:
					body = "Recent destinations\n\n12:58 AM  Mulholland Scenic Overlook (parked)\n12:08 AM  Norm's, Sunset Blvd (stopped 30 min)\n11:56 PM  Home, Silver Lake (stopped 2 min)"
				else:
					rows = ["Recent destinations", "Home", "Search"]
		var pick: String = await main.device("PRIUS", ["Radio", "Phone", "Navigation"], tab, body, rows)
		if pick == "close":
			break
		if pick.begins_with("tab:"):
			tab = int(pick.substr(4))
			recent = false
			continue
		var row: String = rows[int(pick.substr(4))]
		if row == "Recent destinations":
			recent = true
			main.ui.show_device("PRIUS", ["Radio", "Phone", "Navigation"], 2,
					"Recent destinations\n\n12:58 AM  Mulholland Scenic Overlook (parked)\n12:08 AM  Norm's, Sunset Blvd (stopped 30 min)\n11:56 PM  Home, Silver Lake (stopped 2 min)",
					[], false, Case2.GLIDE)
			if not Game.flag("clue_gps"):
				await main.say("The car keeps its own diary. Home at eleven fifty-six, for two minutes. Norm's at eight past twelve. Then up here.")
				main.clue("clue_gps")
			else:
				await main.say("Home, Norm's, then up here.")
		elif row == "Home":
			await main.say("Home: Silver Lake. I can read an address without the car driving me there.")
		else:
			await main.say("I know where I'm going. Mostly.")
	main.ui.hide_device()
	await _insight()


func _insight() -> void:
	## Once the app and the car disagree, Ray puts them together (once).
	if Game.flag("clue_last_trip") and Game.flag("clue_gps") and not Game.flag("clue_off_app"):
		await main.say("The app says his night ended at eleven fifty-two. The car says it didn't. He went home for two minutes, then out for pie, then up here. Off the clock.")
		await main.say("Nobody drives a stranger around for free. He picked someone up at home.")
		main.clue("clue_off_app")
