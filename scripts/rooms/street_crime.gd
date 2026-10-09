extends Room
## The street outside the precinct at 4:52 a.m. (Case 5, scene 1): crime tape across the Blue Note's open door, Park at
## the door, Teo on a crate by the hydrant, Mara Quist at the tape. Mara stops Ray the first time he heads for the
## Blue Note and gives him her card (got_reporter_card). The precinct door opens once Ray has Nina's police number
## (clue_nina_call); the car, once Danny's box is packed and the meet is set (Scene 7: the lab, then Pier 9).
## Park goes into the back room once Nina is out (an overlay here and there); the patrol car's light bar turns
## (two overlays, red and blue).

const PARK_COLOR := Color(1.0, 0.78, 0.56)

@onready var park: Sprite2D = $Actors/Park
@onready var bar_red: Sprite2D = $Bar_red
@onready var bar_blue: Sprite2D = $Bar_blue
var _blink := 0.0
var _wander := 0


func _ready() -> void:
	super._ready()
	add_rain(160, -0.05)
	_sync()


func _sync() -> void:
	park.visible = not Game.flag("nina_out")
	hotspot("park").enabled = park.visible


func _process(delta: float) -> void:
	# the light bar turning: red, blue, red, blue, with a beat of dark
	_blink += delta
	var phase := fmod(_blink, 1.2)
	bar_red.visible = phase < 0.35
	bar_blue.visible = phase >= 0.6 and phase < 0.95


func on_enter(from_room: String) -> void:
	if not Game.flag("street5_arrived"):
		Game.set_flag("street5_arrived")
		await main.wait(0.4)
		await main.say("Three hours ago I stood here and knocked like a dead man. Sal opened up.")
		await main.say("The neon's off. Eight years across the street, and I've never seen it off.")


func interact(hs: Hotspot, verb: String, item: String) -> void:
	await _maybe_hint(hs.id)
	match hs.id:
		"bar_door", "tape":
			if verb == "look":
				if hs.id == "tape":
					await main.say("Yellow tape from the lamp to the hydrant. It keeps out everyone who'd behave anyway.")
				else:
					await main.say("The door I talked through. It's open now. That's worse.")
			elif item != "":
				await default_response(verb, item)
			elif not Game.flag("got_reporter_card"):
				await _mara_first()
			else:
				if hs.id == "tape":
					await main.say("I duck under it.")
				await main.change_room("blue_note_bar", "street_crime")

		"mara":
			if verb == "look":
				await main.say("Mara Quist, LA Times. Notebook dry under her coat. She's been up longer than me.")
			elif item == "reporter_card":
				await main.say("She knows where I keep it.")
			elif item == "tab_book":
				await main.say("Not for the paper.")
			elif item != "":
				await default_response(verb, item)
			elif not Game.flag("got_reporter_card"):
				await _mara_first()
			else:
				await _talk_mara()

		"park":
			if verb == "look":
				await main.say("Officer Park. Third scene tonight, and her rain cape's still pressed.")
			elif item != "":
				await default_response(verb, item)
			else:
				await _talk_park()

		"teo":
			if verb == "look":
				await main.say("The porter. Sixties, a mop bucket, and a face that hasn't caught up with what it saw.")
			elif item != "":
				await default_response(verb, item)
			else:
				await _talk_teo()

		"precinct_door":
			if verb == "look":
				await main.say("The precinct. Room 214's one flight up. So's the lieutenant's office.")
			elif item != "":
				await default_response(verb, item)
			elif not Game.flag("clue_nina_call"):
				await main.say("Not yet. Sal first.")
			else:
				await main.change_room("squad_room", "street")

		"payphone":
			if verb == "look":
				await main.say("The payphone. Three hours ago I put a dime in it and started all this.")
			elif item != "":
				await default_response(verb, item)
			else:
				await main.say("I've made my call. It cost more than a dime.")

		"rezoning":
			if verb == "look":
				if Game.flag("saw_rezoning"):
					await main.say("NOTICE OF PUBLIC HEARING. Applicant: Pryce Development. It was taped to the Blue Note's wall the whole time.")
				else:
					await main.say("NOTICE OF PUBLIC HEARING. Zone change, 6400 block. Applicant: Pryce Development.")
			elif item != "":
				await default_response(verb, item)
			else:
				await main.say("It's somebody else's paperwork. For now.")
			Game.set_flag("saw_rezoning")

		"trash_can":
			if verb == "look":
				await main.say("The dumpster where I found the matchbook. Seems like a week ago.")
			elif item != "":
				await default_response(verb, item)
			else:
				await main.say("Nothing in there tonight but rain.")

		"alley":
			if verb == "look":
				await main.say("Where they found Danny on Tuesday. The back door to the Blue Note opens onto it.")
			else:
				await main.say("Locked from the inside. I'll go in the front.")

		"van":
			if verb == "look":
				await main.say("Shah's van. She beat me here. She always does.")
			else:
				await main.say("Not my van.")

		"patrol_car":
			await main.say("Park's unit, lights turning for nobody.")

		"flares":
			await main.say("Road flares, burning down in the wet. Somebody wanted the traffic to slow down for Sal. Nobody's driving.")

		"neon":
			await main.say("BLUE NOTE. Dark. I've never seen it dark.")

		"car":
			if verb == "look":
				await main.say("My car. Still wet, still dented.")
			elif item != "":
				await default_response(verb, item)
			else:
				await _car()

		_:
			await default_response(verb, item)


# --- Mara Quist ---------------------------------------------------------------------------------------------------
func _mara(line: String) -> void:
	await main.voice(line, speaker_at("mara"), Case5.MARA_COLOR)


func _mara_first() -> void:
	## Plays the first time Ray heads for the Blue Note.
	await main.walk(hotspot("mara").walk_to)
	main.player.face("down")
	await _mara("Detective Kessler? Mara Quist, the Times. I heard it on the scanner. Same bar as the piano player Tuesday. Is that a pattern?")
	await main.say("It's a bar. People keep dying near it.")
	await _mara("That's what a pattern is.")
	var c: int = await main.choose(["No comment.", "How do you know my name?", "Go home, Ms. Quist."])
	match c:
		0:
			await main.say("No comment.")
			await _mara("You'd be amazed how many stories start with that.")
		1:
			await main.say("How do you know my name?")
			await _mara("You're the only detective in Hollywood who works nights on purpose. People talk about you. Not always kindly.")
		_:
			await main.say("Go home, Ms. Quist.")
			await _mara("I am home. I live on the scanner.")
	await _mara("When it's a pattern, call me. Not the press office. Me.")
	Game.set_flag("got_reporter_card")
	await main.give("reporter_card")


func _talk_mara() -> void:
	while true:
		var opts := []
		var keys := []
		if not Game.flag("mara_working"):
			opts.append("What are you working on?"); keys.append("working")
		if not Game.flag("clue_mara_beat"):
			opts.append("What do you know about the block?"); keys.append("block")
		opts.append("Goodnight."); keys.append("done")
		var c: int = await main.topics(opts)
		if c < 0:
			return
		match keys[c]:
			"working":
				Game.set_flag("mara_working")
				await main.say("What are you working on?")
				await _mara("City Hall. Who pays for whose vote. It's like homicide, but nobody ever gets caught.")
			"block":
				await main.say("What do you know about the block?")
				await _mara("Hollywood Core. Pryce Development wants forty stories where this bar is. The council votes next Wednesday.")
				await _mara("Ted Haskell's the swing vote, and nobody can find out which way he swings. I've been on it a year. Nobody will talk to me.")
				main.clue("clue_mara_beat")
				if Game.flag("saw_rezoning"):
					await main.say("Pryce Development. It was taped to the Blue Note's wall the whole time.")
			_:
				await main.say("Goodnight.")
				await _mara("It isn't. But thanks.")
				return


# --- Officer Park -------------------------------------------------------------------------------------------------
func _park(line: String) -> void:
	await main.voice(line, speaker_at("park"), PARK_COLOR)


func _talk_park() -> void:
	if not Game.flag("park5_hello"):
		Game.set_flag("park5_hello")
		await _park("Detective. Third time tonight. They should give us a punch card.")
	while true:
		var opts := []
		var keys := []
		if not Game.flag("park5_what"):
			opts.append("What happened?"); keys.append("what")
		if not Game.flag("park5_cut"):
			opts.append("Who cut him down?"); keys.append("cut")
		if not Game.flag("clue_no_note"):
			opts.append("What's patrol calling it?"); keys.append("patrol")
		if not Game.flag("clue_tape_helper"):
			opts.append("Danny's alley, Tuesday."); keys.append("alley")
		opts.append("That'll do."); keys.append("done")
		var c: int = await main.topics(opts)
		if c < 0:
			return
		match keys[c]:
			"what":
				Game.set_flag("park5_what")
				await main.say("What happened?")
				await _park("The porter found him at four thirty-one and called it in on the bar phone. I was two blocks away.")
				await _park("He's in the back room. Dr. Shah's with him.")
			"cut":
				Game.set_flag("park5_cut")
				await main.say("Who cut him down?")
				await _park("Me. To check for a pulse. There wasn't one.")
				await _park("I'm sorry, Detective. Otis said you knew him.")
			"patrol":
				await main.say("What's patrol calling it?")
				await _park("The watch commander says suicide. Front door locked, back door locked, a man alone in his own bar with a rope.")
				await main.say("A note?")
				await _park("No note.")
				await main.say("Sal wrote down every drink he poured for thirty years. And he didn't leave a note.")
				main.clue("clue_no_note")
			"alley":
				await main.say("Danny's alley, Tuesday.")
				await _park("I held his tape. Midnight to four, in the rain.")
				await main.say("Anybody hang around?")
				await _park("The usual. Two drunks and a man with a dog. And a retired cop. Big old-timer, white hair, belted raincoat.")
				await _park("He showed me his old ID and stood inside the tape with us for an hour like he never left the job. Brought us all coffee from the place on Cahuenga.")
				await main.say("He ask anything?")
				await _park("Whether we'd found the victim's phone. I said no. He said kids today lose everything. A car came for him around ten past one.")
				await main.say("Name?")
				await _park("Walt something. He said everybody at Hollywood knows him. It's in my scene log. I log everybody inside my tape.")
				await main.say("An old cop at a fresh scene, asking about the one thing that's missing.")
				main.clue("clue_tape_helper")
			_:
				await main.say("That'll do.")
				await _park("I'll keep the Times on the right side of the tape. She's very polite about ignoring me.")
				return


# --- Teo ------------------------------------------------------------------------------------------------------------
func _teo(line: String) -> void:
	await main.voice(line, speaker_at("teo"), Case5.TEO_COLOR)


func _talk_teo() -> void:
	if not Game.flag("met_teo"):
		Game.set_flag("met_teo")
		await _teo("You're the detective from across the street. Sal said you came by. Through the door.")
		await main.say("I did.")
		await _teo("He was scared after. He told me, \"Teo, I talked.\" Like it was a sin.")
	while true:
		var opts := []
		var keys := []
		if not Game.flag("teo_found"):
			opts.append("You found him?"); keys.append("found")
		if not Game.flag("clue_latch"):
			opts.append("The front door."); keys.append("door")
		if not Game.flag("clue_tab_habit"):
			opts.append("Sal's habits."); keys.append("habits")
		if not Game.flag("clue_knock_only"):
			opts.append("Who knows the knock?"); keys.append("knock")
		opts.append("Go home, Teo."); keys.append("done")
		var c: int = await main.topics(opts)
		if c < 0:
			return
		match keys[c]:
			"found":
				Game.set_flag("teo_found")
				await main.say("You found him?")
				await _teo("Four-thirty, like every morning. Nineteen years. We've been closed since Danny, but Sal said keep coming, we open again Saturday.")
				await _teo("I let myself in, I take the chairs down, I go to the back for the mop. And he was...")
				await _teo("I called 911 on the bar phone. Then I came out here. I haven't been able to go back in.")
			"door":
				await main.say("The front door.")
				await _teo("It was on the latch. Just the latch. Sal threw the deadbolt every night, and the chain, and he checked it twice.")
				await _teo("Nineteen years, I never once came in on just the latch.")
				await main.say("Somebody went out the front and pulled it shut behind him.")
				main.clue("clue_latch")
			"habits":
				await main.say("Sal's habits.")
				await _teo("He wrote everything down. Every drink, in the book by the register. Even mine, and I don't drink.")
				await _teo("\"Teo, water, four thirty-five,\" every morning. He used to say, \"If it isn't in the book, it didn't happen.\"")
				main.clue("clue_tab_habit")
			"knock":
				await main.say("Who knows the knock?")
				await _teo("I don't knock. I have a key. Since Tuesday Sal only opened that door to Danny's knock.")
				await _teo("He said, \"Teo, if anybody knocks it any other way, I'm not home.\"")
				main.clue("clue_knock_only")
			_:
				await main.say("Go home, Teo.")
				await _teo("Who's going to mop?")
				await main.say("Not tonight.")
				return


# --- the car: Scene 7 -------------------------------------------------------------------------------------------------
func _car() -> void:
	if not Game.has_item("danny_box"):
		await main.say("Not yet. Whatever I need is on this block.")
		return
	var missing: Array[String] = []
	for pair: Array in [["got_danny_box", "box"], ["vance_in", "pier"], ["otis_backup", "backup"], ["bait_sent", "bait"]]:
		if not Game.flag(pair[0]):
			missing.append(pair[1])
	if not missing.is_empty():
		var words := ", ".join(missing)
		await main.say("Not yet. " + words.substr(0, 1).to_upper() + words.substr(1) + ".")
		return
	await main.say("Pier 9. Last time I drove down there, Danny was a debt.")
	await Case5.drive_to_lab(main)
	await main.change_room("night_lab", "drive")


func _maybe_hint(id: String) -> void:
	## Lingering on the street after talking to everyone.
	if Game.flag("got_reporter_card") and Game.flag("met_teo") and Game.flag("park5_hello") \
			and not Game.flag("got_tab_book") and not id in ["bar_door", "tape"]:
		_wander += 1
		if _wander == 5:
			await main.say("Sal's inside. So's whatever he left me.")
