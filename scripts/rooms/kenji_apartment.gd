extends Room
## Kenji and Devin's apartment, Silver Lake (Case 2, scene 4). Break Devin's story, get his consent, find the cards.
## Puzzle 4.1: "home all night" falls to Norm's (the card slip, or Rosa's word).
## Puzzle 4.2: "he dropped me back here" falls to the car's GPS; Devin says search, and gets off the fridge.
## Puzzle 4.3: the freezer: a bag of frozen peas, taped shut. Using it on the sink ends the scene:
## the dashcam and the cards, Devin asks for a lawyer, Park takes him down the stairs.
## Devin is part of the set in two poses (overlays): at the fridge until search_consent, then on the couch.

@onready var devin_fridge: Sprite2D = $Devin_fridge
@onready var devin_couch: Sprite2D = $Devin_couch
var _wander := 0         ## actions after consent without opening the freezer (a hint after a few)


func _ready() -> void:
	super._ready()
	_sync()


func _sync() -> void:
	devin_fridge.visible = not Game.flag("search_consent")
	devin_couch.visible = Game.flag("search_consent") and not Game.flag("devin_arrested")
	hotspot("devin").enabled = devin_fridge.visible
	hotspot("devin_couch").enabled = devin_couch.visible


func on_enter(_from_room: String) -> void:
	if not Game.flag("met_devin"):
		Game.set_flag("met_devin")
		await main.say("I'm sorry. Kenji was found dead tonight, in his car, up on Mulholland.")
		await main.wait(1.0)
		await _devin("No. No, no. What happened? Was it a crash?")
		await main.say("Somebody killed him.")
		await _devin("Jesus. Who would... He's a Glide driver. He gives people water bottles.")


func interact(hs: Hotspot, verb: String, item: String) -> void:
	if not hs.id in ["freezer", "fridge", "devin", "devin_couch"]:
		await _maybe_hint()
	if item == "frozen_peas" and hs.id != "sink":
		await main.say("Not here. Whatever's in that bag, I'll open it over the sink.")
		return
	match hs.id:
		"devin", "devin_couch":
			if verb == "look":
				await main.say("Wet hair at two in the morning. Grief takes a lot of shapes. So does a shower.")
				if not Game.flag("search_consent"):
					await main.say("He hasn't moved off that fridge since I came in.")
			elif item == "card_slip" and not Game.flag("devin_lie1_broken"):
				if Game.flag("clue_devin_story"):
					await _first_lie()
				else:
					await main.say("Let him tell me his story first. Then I'll show him mine.")
			elif item == "driver_card":
				await _devin("Don't. Please.")
			elif item != "":
				await main.say("He's seen enough tonight. So have I.")
			elif Game.flag("search_consent"):
				await _devin("Search. Go ahead. You won't find anything.")
			else:
				await _talk_to_devin()

		"kenji_desk":
			if verb == "look":
				await main.say("A printout from HushHush: \"STUDIO ASSISTANT'S BACK-SEAT MELTDOWN\". The photo's from a dashcam, looking at the back seat.")
			elif item != "":
				await default_response(verb, item)
			else:
				await main.player.play_action("use")
				await main.say("A sticky note in Kenji's hand: \"Carla Mendes. Fired over this. My fault. Giving her lawyer the cards. Done with HH.\"")
				await main.say("So the camera wasn't for safety.")
				main.clue("clue_kenji_quitting")

		"dashcam_box":
			await main.say("An empty box on Kenji's shelf. DuoCam 2: road and cabin. Memory cards sold separately.")

		"certificate":
			await main.say("GLIDE DRIVER OF THE MONTH. Five stars, every ride, for thirty days. I've never managed thirty minutes.")

		"pennant":
			await main.say("Dodgers, 2020. He was an optimist.")

		"camera_bag":
			if verb == "look":
				if Game.flag("clue_ligature"):
					await main.say("A black camera bag on the hook. An inch wide, woven herringbone. Shah would want to meet this strap.")
					main.clue("clue_strap")
				else:
					await main.say("A black camera bag on the hook. The strap's an inch wide.")
			elif item != "":
				await default_response(verb, item)
			else:
				await main.say("His bag, and he's watching me look at it. Not without paper.")

		"sneakers":
			if verb == "look":
				if Game.flag("saw_grit"):
					await main.say("Running shoes, soaked through. Pale orange grit in the treads. Decomposed granite, same as the overlook lot.")
					main.clue("clue_sneakers")
				else:
					await main.say("Running shoes, soaked through. Grit in the treads.")
			elif item != "":
				await default_response(verb, item)
			else:
				await main.say("I'll let the lab pick his shoes.")

		"laptop":
			if verb == "look":
				await main.say("Open to a photo editor. A folder called WEDDINGS_OCT. Last saved at 6:12 p.m.")
				await main.say("Editing all night, and the last save was before dinner.")
				main.clue("clue_laptop")
			elif item != "":
				await default_response(verb, item)
			else:
				await main.say("Looking is free. Touching isn't.")

		"photos":
			await main.say("Night shots of LA. Good ones. Freeway ramps, the Bowl, and the Mulholland overlook, from exactly where Kenji's car is parked.")

		"fridge":
			if not Game.flag("search_consent"):
				await main.say("Devin's leaning on that fridge like it owes him rent.")
			elif verb == "look":
				await main.say("Magnets, takeout menus, and a note in Kenji's hand.")
				await main.say("\"D, your peas have been in here since July. Eat them or I'm tossing them. K.\"")
				main.clue("clue_peas_note")
			elif item != "":
				await default_response(verb, item)
			else:
				await _freezer()

		"freezer":
			if not Game.flag("search_consent"):
				await main.say("Devin's leaning on that fridge like it owes him rent.")
			elif verb == "look":
				if Game.flag("got_peas"):
					await main.say("Ice and vodka. I'm on duty.")
				else:
					await main.say("Fresh finger marks in the frost, and a puddle under the door. Somebody opened this tonight with wet hands.")
			elif item != "":
				await default_response(verb, item)
			else:
				await _freezer()

		"sink":
			if verb == "look":
				await main.say("A steel sink under the kitchen window. Clean. Cleaner than the rest of the place.")
			elif item == "frozen_peas":
				await open_peas()
			elif item != "":
				await default_response(verb, item)
			elif Game.has_item("frozen_peas"):
				await main.say("Good place to open a bag of peas.")
			else:
				await main.say("I'm not here to do the dishes.")

		"tv":
			if verb == "look":
				await main.say("A big TV, switched off. A dark screen's easier to look at than a cop.")
			else:
				await main.say("I didn't come here to watch anything.")

		"dining":
			if verb == "look":
				await main.say("Two plates and a takeout box. Dinner at six, Devin said. That part might even be true.")
			else:
				await main.say("Leftovers. Not evidence.")

		"devin_door":
			await main.say("Closed. His room, his rules, until I've got paper.")

		"front_door":
			if verb == "look":
				await main.say("Back down the stairs.")
			elif item != "":
				await default_response(verb, item)
			elif Game.flag("search_consent") and not Game.flag("devin_arrested"):
				await main.say("Not now. Devin said search, and I haven't finished searching.")
			else:
				await Case2.car_menu(main, "kenji_apartment")

		_:
			await default_response(verb, item)


func _devin(line: String) -> void:
	var at := speaker_at("devin_couch" if Game.flag("search_consent") else "devin")
	await main.voice(line, at, Case2.DEVIN_COLOR)


func _maybe_hint() -> void:
	## After the consent, if the player wanders: point at the fridge.
	if not Game.flag("search_consent") or Game.flag("got_peas") or Game.flag("fridge_hint"):
		return
	_wander += 1
	if _wander >= 4:
		Game.set_flag("fridge_hint")
		await main.say("He couldn't get off that fridge fast enough once I said search. Before that, he couldn't get off it at all.")


# --- talking to Devin -------------------------------------------------------------
func _has_norms_proof() -> bool:
	return Game.has_item("card_slip") or Game.flag("clue_roommate_norms")


func _talk_to_devin() -> void:
	while true:
		var opts := []
		var keys := []
		if not Game.flag("devin_who"):
			opts.append("Who are you?"); keys.append("who")
		if not Game.flag("clue_devin_story"):
			opts.append("When did you last see Kenji?"); keys.append("last")
		if not Game.flag("devin_enemies"):
			opts.append("Did Kenji have enemies?"); keys.append("enemies")
		if not Game.flag("devin_look"):
			opts.append("Mind if I look around?"); keys.append("look")
		if Game.flag("clue_devin_story") and _has_norms_proof() and not Game.flag("devin_lie1_broken"):
			opts.append("You weren't home all night."); keys.append("lie1")
		if Game.flag("devin_lie1_broken") and Game.flag("clue_gps"):
			opts.append("His car never came back here."); keys.append("lie2")
		opts.append("I'll be in touch."); keys.append("done")
		var c: int = await main.topics(opts)
		if c < 0:
			return
		var k: String = keys[c]
		if k != "lie1":
			await main.say(opts[c])
		match k:
			"who":
				Game.set_flag("devin_who")
				await _devin("Devin. Devin Clark. Roommate, three years. I'm a photographer. Weddings, headshots, whatever pays.")
			"last":
				await _devin("Dinner. Like six? Then he went out for his shift. I've been home all night, editing. I was asleep by eleven.")
				await _devin("I just got up and had a shower, I couldn't sleep.")
				await main.say("Asleep by eleven and editing all night.")
				await _devin("Both. You know what I mean.")
				main.clue("clue_devin_story")
			"enemies":
				Game.set_flag("devin_enemies")
				await _devin("There's this driver, Heck something. He keyed Kenji's car. And riders, people get crazy in the back seat. You should ask Glide.")
			"look":
				Game.set_flag("devin_look")
				await _devin("Kenji's room, sure. Whatever helps. Mine's a mess. And I'm not okay with you going through my stuff, you know?")
				await main.wait(0.6)
				await _devin("Sorry. I'm not thinking straight.")
			"lie1":
				await _first_lie()
			"lie2":
				await _second_lie()
				return
			"done":
				if Game.flag("clue_devin_story") and not _has_norms_proof():
					await main.say("He says he was home. Norm's might say different.")
				return


func _first_lie() -> void:
	## Puzzle 4.1: Norm's says he went out.
	await main.player.play_action("use")
	if Game.has_item("card_slip"):
		await main.say("Norm's on Sunset. Table six, twelve-fourteen. Two coffees, one cherry pie. Signed D. Clark.")
	else:
		await main.say("A waitress at Norm's puts Kenji in booth six at midnight with his roommate. The one with the camera bag.")
	await main.wait(1.0)
	await _devin("Okay. Okay, I went out. I knew how it would look. We got pie.")
	await _devin("He dropped me back here at like twelve-forty and drove off. That's the last time I saw him. I swear to God.")
	await main.say("You told me you were asleep by eleven.")
	await _devin("I panicked! My roommate's dead!")
	Game.set_flag("devin_lie1_broken")
	if not Game.flag("clue_gps"):
		await main.say("He's got a new story. Kenji's car will have an opinion about it.")


func _second_lie() -> void:
	## Puzzle 4.2: the car never came back.
	await main.say("Kenji's car keeps a diary. Home at eleven fifty-six, two minutes. Norm's at eight past twelve. Then straight up Mulholland.")
	await main.say("It never came back here, Devin.")
	await main.say("So how did you get home?")
	await main.wait(1.2)
	if Game.flag("clue_walker"):
		await main.say("A couple driving up passed a man walking down Mulholland at one-fifteen. Hood up. Carrying a bag.")
	if Game.flag("clue_sneakers"):
		await main.say("And your shoes are full of that overlook.")
	await _devin("You want to search? Search. Search the whole place. You won't find anything, because there's nothing to find.")
	await main.ui.fade_to(1.0, 0.35)
	Game.set_flag("search_consent")
	_sync()
	await main.ui.fade_to(0.0, 0.35)
	await main.say("Off the fridge, and onto the couch. Staring at a TV that isn't on.")


# --- Puzzle 4.3: the freezer ------------------------------------------------------
func _freezer() -> void:
	if Game.flag("got_peas"):
		await main.say("Ice and vodka. I'm on duty.")
		return
	await main.player.play_action("use")
	await main.say("Ice trays, a bottle of vodka, and a bag of frozen peas taped shut. Nobody tapes peas.")
	Game.set_flag("got_peas")
	await main.give("frozen_peas", false)


func open_peas() -> void:
	## The peas used on the sink. The cards, a lawyer, and Park up the stairs.
	await main.player.play_action("use")
	await main.say("Peas rattle into the sink. Underneath, a zip bag.")
	await main.say("A two-lens dashcam, and a clear plastic case of memory cards, labeled in Kenji's handwriting. January to November.")
	main.take("frozen_peas")
	Game.set_flag("got_sd_cards")
	await main.give("sd_cards", false)
	await main.say("Nobody ever got killed over frozen peas.")
	await _devin("Those are mine. Half of those are mine. A year of work, and he was going to give them away.")
	await _devin("Give them away, to some assistant who got what she...")
	await main.wait(1.0)
	await _devin("I want a lawyer.")
	await main.say("You'll get one.")
	await main.player.play_action("use")
	await main.say("Park, it's Kessler. Silver Lake. Come up the stairs.")
	await main.wait(1.2)
	var door := speaker_at("front_door")
	await main.voice("I was taking the Ota car down the hill. Silver Lake was on the way.", door, Case2.PARK_COLOR)
	await main.voice("Devin Clark? Stand up for me.", door, Case2.PARK_COLOR)
	await _devin("Can I take my bag?")
	if Game.flag("clue_strap"):
		await main.say("No. That one stays. The strap's going to meet Dr. Shah.")
	else:
		await main.say("No. That one stays.")
	await main.ui.fade_to(1.0, 0.6)
	Game.set_flag("devin_arrested")
	_sync()
	await main.wait(0.6)
	await main.ui.fade_to(0.0, 0.6)
	await main.say("Eleven cards. Twenty-five hundred apiece. Twenty-seven thousand dollars, and a man who wanted to give it back.")
