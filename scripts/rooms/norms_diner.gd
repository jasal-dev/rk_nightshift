extends Room
## Norm's on Sunset (Case 2, scene 3). Puts Devin with Kenji at midnight and clears the rival driver.
## Puzzle 3.1: Rosa's too busy to talk until Ray pours the counter's coffee from the pot on the warmer.
## Puzzle 3.2: she knows faces, not names: show her Kenji's driver card (his roommate, the camera bag, "cards").
## Puzzle 3.3: Kenji's receipt (table six, 12:14) gets the signed card slip from the register.
## Heck (optional): his threat on Kenji's phone, his LAX queue alibi, and "the side thing".
## The door opens the car menu.


func on_enter(from_room: String) -> void:
	if not Game.flag("been_to_norms"):
		Game.set_flag("been_to_norms")
		await main.say("Norm's. Open twenty-four hours since 1957. The coffee's improved since then. Not by much.")
		await _rosa("Sit anywhere, hon. I'll get to you when I get to you.")


func interact(hs: Hotspot, verb: String, item: String) -> void:
	match hs.id:
		"rosa":
			if verb == "look":
				await main.say("Rosa. Thirty years on this floor, and she's still faster than the cook.")
			elif not Game.flag("helped_rosa"):
				await _rosa("Hold that thought, hon. Twelve cups, two hands, and Luis called in sick.")
			elif item == "driver_card":
				if Game.flag("clue_roommate_norms"):
					await _rosa("That's him, hon. I already told you. Booth six.")
				else:
					await _show_card()
			elif item == "norms_receipt":
				if Game.flag("got_card_slip"):
					await _rosa("You've got the slip, hon. The receipt's all yours too.")
				else:
					await _card_slip()
			elif item != "":
				await _rosa("Unless it's a tip, hon, I don't need it.")
			else:
				await _talk_to_rosa()

		"coffee_pot":
			if verb == "look":
				if Game.flag("helped_rosa"):
					await main.say("A full pot on the warmer.")
				else:
					await main.say("A full pot on the warmer. Rosa's got the other one, and six empty cups are waving at her.")
			elif item != "":
				await default_response(verb, item)
			elif Game.flag("helped_rosa"):
				await main.say("I've done my shift. Rosa's got it.")
			else:
				await _pour()

		"heck":
			if verb == "look":
				await main.say("Glide jacket, three phones in a row. Two driving apps and one for the horses.")
			elif item == "driver_card":
				await _heck("Yeah, that's him. Four point nine eight. Show-off.")
			elif item != "":
				await default_response(verb, item)
			else:
				await _talk_to_heck()

		"booth6":
			if verb == "look":
				await main.say("Booth six. Two cup rings, a plate with a cherry smear, and a napkin somebody did math on.")
			elif item != "":
				await default_response(verb, item)
			else:
				await main.player.play_action("use")
				await main.say("\"11 × 2,500.\" Under it, \"50/50\", crossed out so hard the pen went through.")
				await main.say("Twenty-seven thousand five hundred dollars of somebody's math. And somebody disagreed with it.")
				main.clue("clue_napkin")

		"pie_case":
			if verb == "look":
				await main.say("Cherry, apple, and a lemon meringue that's seen things.")
			else:
				await main.say("I've got an appetite to protect.")

		"regulars":
			if verb == "look":
				await main.say("Cabbies, a nurse off a double, a guard asleep in his eggs. The night shift's congregation.")
			elif item != "":
				await default_response(verb, item)
			else:
				await main.say("Let them eat.")

		"jukebox":
			if verb == "look":
				await main.say("Somebody put a quarter on Chet Baker.")
			else:
				await main.say("Danny would've approved.")

		"window":
			await main.say("Rain on Sunset. A bus goes by with nobody on it.")

		"door":
			if verb == "look":
				await main.say("Back to the car.")
			elif item != "":
				await default_response(verb, item)
			else:
				await Case2.car_menu(main, "norms_diner")

		_:
			await default_response(verb, item)


func _rosa(line: String) -> void:
	await main.voice(line, speaker_at("rosa"), Case2.ROSA_COLOR)


func _heck(line: String) -> void:
	await main.voice(line, speaker_at("heck"), Case2.HECK_COLOR)


# --- Rosa -------------------------------------------------------------------------
func _pour() -> void:
	## Puzzle 3.1: Ray works his way down the counter with the pot.
	await main.player.play_action("pickup")
	await main.walk(hotspot("regulars").walk_to)
	main.player.face("up")
	await main.say("Coffee. Coffee.")
	await main.player.play_action("use")
	await main.say("You're asleep, you don't need coffee. Coffee.")
	await main.voice("Thanks, officer.", speaker_at("regulars"), Case2.CABBIE_COLOR)
	await main.say("Detective.")
	await main.voice("Thanks, detective.", speaker_at("regulars"), Case2.CABBIE_COLOR)
	await main.walk(hotspot("rosa").walk_to)
	main.player.face("up")
	await _rosa("Well. A cop who pours. Now I've seen everything. Put that down before you get ideas, hon. What do you need?")
	Game.set_flag("helped_rosa")


func _talk_to_rosa() -> void:
	if not Game.flag("clue_roommate_norms"):
		var c: int = await main.choose(["I'm looking for a Glide driver. Kenji Ota.", "Never mind."])
		if c == 0:
			await main.say("I'm looking for a Glide driver. Kenji Ota.")
			await _rosa("Hon, I know faces, not names. Half my counter drives for somebody.")
			if Game.has_item("driver_card"):
				await main.say("Faces. I've got one of those in my pocket.")
		else:
			await main.say("Never mind.")
		return
	while true:
		var opts := []
		var keys := []
		if not Game.flag("rosa_paid"):
			opts.append("Who paid?"); keys.append("paid")
		if not Game.flag("rosa_left"):
			opts.append("When did they leave?"); keys.append("left")
		if Game.flag("rosa_paid") and not Game.flag("got_card_slip"):
			opts.append("Can I see the card slip?"); keys.append("slip")
		opts.append("Thanks, Rosa."); keys.append("done")
		var c: int = await main.choose(opts)
		await main.say(opts[c])
		match keys[c]:
			"paid":
				Game.set_flag("rosa_paid")
				await _rosa("The roommate, for once. On a card. I noticed, because Kenji always pays.")
			"left":
				Game.set_flag("rosa_left")
				await _rosa("Twenty to one, about. Together. The roommate carried that bag out like there was a baby in it.")
			"slip":
				if Game.has_item("norms_receipt"):
					await _card_slip()
				else:
					await _rosa("I know the booth, hon. The drawer doesn't. Two hundred merchant copies, stacked by the minute they rang up.")
					await _rosa("\"Around midnight\" is forty of them. Bring me his check and I'll find it.")
			"done":
				await _rosa("He tipped twenty percent on a two-dollar coffee, Detective. You get whoever did this.")
				return


func _show_card() -> void:
	## Puzzle 3.2: a face she knows.
	await main.player.play_action("use")
	await _rosa("Kenji. Sure. Coffee black, cherry pie à la mode, tips like a man who's waited tables.")
	await main.say("He was killed tonight, Rosa. Up on Mulholland.")
	await main.wait(0.6)
	await _rosa("He was in that booth two hours ago. Number six. I haven't even bussed it.")
	await main.say("Was he alone?")
	await _rosa("With his roommate. The one with the camera bag. Skinny, little beard, never says thank you. They come in after Kenji's shift sometimes.")
	await _rosa("Tonight they were going at it. Low, but going at it. Something about cards. The roommate kept saying \"they're half mine.\" I figured baseball cards. Boys.")
	main.clue("clue_roommate_norms")


func _card_slip() -> void:
	## Puzzle 3.3: table six, 12:14, and a signature.
	await main.player.play_action("use")
	await _rosa("Table six, twelve-fourteen. We still take a signature here. Norm's is a historic landmark, and so's the card machine.")
	await main.wait(0.8)
	await _rosa("Here. Signed \"D. Clark\". Looks like a seismograph.")
	await main.say("Can I keep this?")
	await _rosa("You poured. Keep it.")
	Game.set_flag("got_card_slip")
	await main.give("card_slip")


# --- Heck -------------------------------------------------------------------------
func _talk_to_heck() -> void:
	if not Game.flag("met_heck"):
		Game.set_flag("met_heck")
		await _heck("If you're a rider, I'm on break. If you're a cop, I'm on break harder.")
	while true:
		var opts := []
		var keys := []
		if not Game.flag("clue_heck_alibi"):
			opts.append("Kenji Ota."); keys.append("kenji")
			if Game.flag("clue_threat"):
				opts.append("\"I'll put you in the ground.\""); keys.append("threat")
		else:
			if not Game.flag("clue_side_thing"):
				opts.append("Was Kenji into anything?"); keys.append("into")
			if not Game.flag("heck_roommate"):
				opts.append("What about his roommate?"); keys.append("roommate")
		opts.append("Never mind."); keys.append("done")
		var c: int = await main.choose(opts)
		await main.say(opts[c])
		match keys[c]:
			"kenji":
				if not Game.flag("heck_told"):
					Game.set_flag("heck_told")
					await _heck("The queue jumper? What'd he do, cut in line at the Pearly Gates?")
					await main.say("Somebody strangled him tonight. Up on Mulholland.")
					await main.wait(0.6)
					await _heck("No. No, man. I yelled at him. I didn't, I would never.")
				else:
					await main.say("Where were you tonight?")
					await _alibi()
			"threat":
				await main.say("Tuesday, six-oh-two p.m. \"Do it once more and I'll put you in the ground.\"")
				await _heck("It's an expression! You never said something in traffic?")
				await main.say("Where were you from midnight to one-thirty?")
				await _alibi()
			"into":
				await _heck("Everybody knew he had a camera looking at the back seat. \"For safety.\" Then he's got new tires and a new phone on what Glide pays?")
				await _heck("Last week he told me he was quitting the side thing. Said it got somebody hurt.")
				main.clue("clue_side_thing")
			"roommate":
				Game.set_flag("heck_roommate")
				await _heck("The photographer? Rode along sometimes, in the back like a passenger, filming out the window.")
				await _heck("Kenji called it \"B-roll\". Whatever that is.")
			"done":
				if Game.flag("heck_told"):
					await _heck("Hey. Detective. I'm sorry, okay? About the ground thing.")
				else:
					await _heck("Suit yourself.")
				return


func _alibi() -> void:
	await _heck("The LAX lot. Eleven to one-forty, sitting in the queue like a good boy. Look.")
	main.ui.show_device("Glide Driver  -  LAX queue", [], 0, "Heck D.  -  tonight",
			["11:02 PM   queue position 41", "12:14 AM   queue position 18", "1:05 AM   queue position 6",
			"1:31 AM   queue position 1", "1:38 AM   Ride accepted"], false, Case2.GLIDE)
	await _heck("And the lot's got four cameras. Check 'em.")
	main.ui.hide_device()
	await main.say("Forty-one cars ahead of him at eleven. Nobody gets from LAX to Mulholland and back in that line.")
	main.clue("clue_heck_alibi")
