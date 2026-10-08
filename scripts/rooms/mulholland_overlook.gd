extends Room
## Mulholland scenic overlook (Case 2, scene 2). Kenji Ota dead behind the wheel of his Prius.
## Officer Park: the last passenger (Brielle's video and alibi) and the walker on Mulholland.
## Dr. Shah: gloves first (every Prius interior hotspot needs them), then the ligature and the time of death.
## The open door leads into the car (prius_interior.gd: the Glide app, the car's screen, the glovebox).
## Leaving needs gloves, Brielle's alibi and clue_off_app; Ray's car then opens the car menu.


func _ready() -> void:
	super._ready()
	add_rain(560, -0.42)


func on_enter(from_room: String) -> void:
	if from_room == "drive" and not Game.flag("met_park"):
		Game.set_flag("met_park")
		await main.wait(0.4)
		await main.say("The overlook. Best view in Los Angeles. He had it all to himself, and he isn't looking.")
		await _park("Detective Kessler? Officer Park. Lena. I've held the scene since one twenty-two. Nobody's touched the car but Dr. Shah.")
		await main.say("Who found him?")
		await _park("A couple came up to, uh, look at the view. Engine running, wipers going, nobody moving. I took their statement and let them go home.")


func interact(hs: Hotspot, verb: String, item: String) -> void:
	await Case2.gps_hint(main)
	match hs.id:
		"kenji":
			if verb == "look":
				await main.say("Kenji Ota. Twenty-nine. His hands are still on the wheel, like he was about to go somewhere.")
			elif item != "":
				await default_response(verb, item)
			else:
				await main.say("Shah's already done everything I'd do, and better.")

		"shah":
			if verb == "look":
				await main.say("Dr. Anita Shah, coroner's investigator. She can read a body like I read a liar.")
			elif item == "driver_card":
				await _shah("I know who he is, Ray. I'd like to know who did it.")
			elif item != "":
				await default_response(verb, item)
			else:
				await _talk_to_shah()

		"park":
			if verb == "look":
				await main.say("Officer Park. Rain cape, notebook, the kind of thorough they train out of you by year three.")
			elif item != "":
				await main.say("She's holding the tape, not the evidence.")
			else:
				await _talk_to_park()

		"inside":
			if verb == "look":
				await main.say("The driver's door is open. The dome light's on, and Kenji's still at the wheel.")
			elif item != "":
				await default_response(verb, item)
			else:
				await main.change_room("prius_interior", "mulholland_overlook")

		"prius":
			if verb == "look":
				await main.say("A white Prius. Half the cars in LA are white Priuses, and the other half are waiting for one.")
				await main.say("Somebody keyed RAT into the driver's side. There's rust in the scratch.")
			elif item != "":
				await default_response(verb, item)
			else:
				await main.say("Weeks old. Not tonight's work.")
				main.clue("clue_rat")

		"ground":
			if item != "":
				await default_response(verb, item)
			else:
				await main.say("Pale orange grit, the decomposed granite they pave these lots with. It gets into everything.")
				Game.set_flag("saw_grit")

		"wall", "view":
			if item != "":
				await main.say("I'm not throwing evidence off Mulholland.")
			elif verb == "look":
				await main.say("Four million lights. From up here you can't tell which ones are on fire.")
			else:
				await main.say("It's a long way down. Kenji went the slow way.")

		"van":
			if item != "":
				await default_response(verb, item)
			else:
				await main.say("Shah's van. It'll take him down the hill the slow way.")

		"sign":
			await main.say("MULHOLLAND SCENIC OVERLOOK. Open sunrise to sunset. Somebody came up after hours.")

		"car":
			if verb == "look":
				await main.say("My car. Rain's getting in the dents.")
			elif item != "":
				await default_response(verb, item)
			else:
				await _leave()

		_:
			await default_response(verb, item)


func _park(line: String) -> void:
	await main.voice(line, speaker_at("park"), Case2.PARK_COLOR)


func _shah(line: String) -> void:
	await main.voice(line, speaker_at("shah"), Case2.SHAH_COLOR)


# --- Officer Park -----------------------------------------------------------------
func _talk_to_park() -> void:
	while true:
		var opts := []
		var keys := []
		if not Game.flag("park_what"):
			opts.append("What have we got?"); keys.append("what")
		if not Game.flag("clue_brielle_alibi"):
			opts.append("Who was his last passenger?"); keys.append("passenger")
		if Game.flag("park_what") and Game.flag("clue_brielle_alibi") and not Game.flag("clue_walker"):
			opts.append("Anything else from the couple?"); keys.append("couple")
		opts.append("That'll do."); keys.append("done")
		var c: int = await main.choose(opts)
		await main.say(opts[c])
		match keys[c]:
			"what":
				Game.set_flag("park_what")
				await _park("Kenji Ota, twenty-nine, Silver Lake address. Drives for Glide. Four point nine eight stars, which is higher than my mom.")
				await _park("Wallet in his jacket, phone in the dash mount. The dashcam mount's empty.")
				await main.say("Wallet left on the body. I've seen that one this week.")
			"passenger":
				await _park("The app says a Brielle V., dropped in Silver Lake at eleven fifty-two. I looked her up. She's, kind of famous?")
				await _park("She posted this at eleven fifty-eight.")
				main.ui.show_device("@brielle.v  -  11:58 PM", [], 0,
						"Shaky selfie video, from the back seat of a car. Bad light, worse angle.", [], false, Case2.BRIELLE_COLOR)
				await main.voice("My Glide driver has a camera pointed at the back seat? Like, at me?", Case2.BRIELLE_AT, Case2.BRIELLE_COLOR)
				await main.voice("Reported. One star. Creep.", Case2.BRIELLE_AT, Case2.BRIELLE_COLOR)
				main.ui.hide_device()
				await _park("And she's been live since twelve-twenty. Hot tub, Hollywood Hills, thirty-one thousand people watching. She's doing karaoke now.")
				await main.say("Thirty-one thousand witnesses. Best alibi I've ever seen, and I hated every second of it.")
				main.clue("clue_cabin_camera")
				main.clue("clue_brielle_alibi")
			"couple":
				await _park("Driving up, around one-fifteen, they passed a guy walking down Mulholland. Hood up, carrying a bag. No car anywhere.")
				await main.say("Walking. On Mulholland. At one in the morning, in the rain.")
				await _park("They figured he was a hiker.")
				await main.say("Hikers go up.")
				main.clue("clue_walker")
			"done":
				await _park("I'll be at the tape, Detective.")
				return


# --- Dr. Shah ---------------------------------------------------------------------
func _talk_to_shah() -> void:
	if not Game.flag("gloved"):
		await _shah("Ray. Gloves before you touch anything. I mean it this time.")
		await main.say("You say that every time.")
		await _shah("You need it every time.")
		await main.player.play_action("use")
		Game.set_flag("gloved")
		main.ui.toast("Nitrile gloves on.")
	while true:
		var opts := []
		var keys := []
		if not Game.flag("clue_ligature"):
			opts.append("How did he die?"); keys.append("how")
		if not Game.flag("clue_tod"):
			opts.append("When?"); keys.append("when")
		if not Game.flag("shah_else"):
			opts.append("Anything else?"); keys.append("else")
		opts.append("Thanks, Anita."); keys.append("done")
		var c: int = await main.choose(opts)
		await main.say(opts[c])
		match keys[c]:
			"how":
				await _shah("Strangled. Not by hand. A ligature, flat, about an inch wide. See the bruise? It has a pattern. A woven herringbone, like a strap.")
				await _shah("Pulled from behind and a little to the right. Whoever did it was in the back seat on the passenger side, or leaning between the seats.")
				await main.say("Somebody he let sit behind him.")
				await _shah("No defensive wounds to speak of. He didn't see it coming. You don't, from someone you know.")
				main.clue("clue_ligature")
			"when":
				await _shah("The heater's been blowing on him for an hour, which doesn't help me. Between one and one-fifteen.")
				main.clue("clue_tod")
			"else":
				Game.set_flag("shah_else")
				await _shah("Two black nylon fibers under his collar. I'll know more at the lab. And there's cherry pie crust on his shirt.")
				await main.say("Last meal, cherry pie. Somebody should put that on a menu.")
			"done":
				await _shah("Don't thank me. Find who did it, and then don't thank me again.")
				return


# --- leaving ----------------------------------------------------------------------
func _leave() -> void:
	if not Game.flag("gloved"):
		await main.say("Shah's going to want a word. Shah always wants a word.")
		return
	if not Game.flag("clue_brielle_alibi") or not Game.flag("clue_off_app"):
		await main.say("Not yet. Kenji's car still has things to tell me.")
		return
	if not Game.flag("left_overlook"):
		Game.set_flag("left_overlook")
		if Game.has_item("kenji_keys"):
			await main.say("Park. His keys.")
			main.take("kenji_keys")
		await _park("I'll ride down with the car. Call if you need a unit, Detective. I'll be in the neighborhood all night.")
	await Case2.car_menu(main, "mulholland_overlook")
