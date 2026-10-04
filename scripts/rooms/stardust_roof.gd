extends Room
## The Stardust roof with the sign back on (Case 3, scene 4). The STARDUST letters paint the wet gravel red and gold;
## the U flickers. Charlie talks from his fire escape across the gap (the Fiat, the shouting, and Walter Brenner).
## Puzzle 4.1: the heel prints, Gus's cigar, and the glint by the door (the gold star earring).
## Puzzle 4.2: the water tank: the "Oscar" floats (fake_oscar, clue_replica).

@onready var neon_u: Sprite2D = $Neon_u
@onready var earring: Sprite2D = $Earring
var _flicker_t := 0.0
var _wander := 0


func _ready() -> void:
	super._ready()
	add_rain(560, -0.25)
	_sync()


func _process(delta: float) -> void:
	# the U has been flickering since the eighties: Gus said it was winking
	_flicker_t -= delta
	if _flicker_t <= 0.0:
		_flicker_t = randf_range(0.04, 0.18) if randf() < 0.3 else randf_range(0.8, 3.0)
		neon_u.visible = randf() > 0.35 or _flicker_t > 0.6


func _sync() -> void:
	earring.visible = not Game.flag("got_star_earring")
	hotspot("glint").enabled = earring.visible


func on_enter(from_room: String) -> void:
	if not Game.flag("on_roof_lit"):
		Game.set_flag("on_roof_lit")
		await main.wait(0.4)
		await main.say("Gus's roof. A lawn chair, a coffee can of cigar ends, and the best seat on the boulevard.")
		await _charlie("Ah! Lights, at last! Are you the man in charge? You look like the man in charge of being tired.")


func interact(hs: Hotspot, verb: String, item: String) -> void:
	if hs.id != "charlie":
		await _maybe_hint()
	match hs.id:
		"charlie":
			if verb == "look":
				await main.say("Charlie Chaplin, smoking a pipe on a fire escape in the rain. Hollywood never closes.")
			elif item == "brenner_card":
				await _brenner()
			elif item == "fake_oscar":
				await _charlie("Lyle! Oh, that's not Lyle. That's Lyle's understudy.")
			elif item != "":
				await default_response(verb, item)
			else:
				await _talk_to_charlie()

		"neon":
			if item != "":
				await default_response(verb, item)
			elif verb == "look":
				await main.say("S-T-A-R-D-U-S-T, six feet tall. The U's been flickering since the eighties. Gus said it was winking.")
			else:
				await main.say("I'll leave it on. Somebody should, tonight.")

		"water_tank":
			if verb == "look":
				await main.say("An old wooden water tank on steel legs. Nobody's drunk out of it since the Rams left town the first time.")
				await main.say("The ladder's wet, and somebody's scraped the rust off the hatch latch.")
			elif item != "":
				await default_response(verb, item)
			elif Game.flag("got_fake_oscar"):
				await main.say("Water and rust. Nothing else in there. I looked.")
			else:
				await _tank()

		"gravel":
			if item != "":
				await default_response(verb, item)
			else:
				await main.say("Little heel prints in the wet gravel, pressed deep. From the roof door to the water tank, and back again.")
				await main.say("Nobody walked to the edge.")
				main.clue("clue_footprints")

		"glint":
			if verb == "look":
				await main.say("Something gold in the gravel.")
			elif item != "":
				await default_response(verb, item)
			else:
				await main.player.play_action("pickup")
				await main.say("Something gold, right at the top of the stairs. A little star, five points, the post bent back.")
				await main.say("Torn out of somebody's ear.")
				Game.set_flag("got_star_earring")
				_sync()
				await main.give("star_earring", false)
				if Game.flag("shah_palm") or Game.flag("clue_pushed"):
					await main.say("Shah said a little star.")

		"lawn_chair":
			if item != "":
				await default_response(verb, item)
			elif verb == "look":
				await main.say("Gus's chair. His cigar's in the puddle beside it, half smoked.")
				await main.say("He came up here to wait for somebody, and he didn't get to finish.")
				main.clue("clue_cigar")
			else:
				await main.say("I've been standing all night. I'll keep standing.")

		"coffee_can":
			if item != "":
				await default_response(verb, item)
			else:
				await main.say("Thirty years of cigar ends. Gus was a creature of habit. So was the person who knew where to find him.")

		"blue_note":
			if item != "":
				await default_response(verb, item)
			elif verb == "look":
				if Game.flag("clue_block_empty"):
					await main.say("Empty by Christmas. The jazz club too.")
				else:
					await main.say("Two roofs over, a blue neon sign: BLUE NOTE. From up here it's just around the corner.")
			else:
				await main.say("Everything's around the corner tonight.")

		"theatre":
			if item != "":
				await default_response(verb, item)
			else:
				await main.say("The pagoda roof across the street. Under it, a hundred years of hands and feet in cement, waiting for the tourists.")

		"roof_edge":
			if item != "":
				await main.say("Nothing goes off this roof tonight.")
			elif verb == "look":
				await main.say("A long drop to a wet, empty alley. No yellow Fiat now.")
			else:
				await main.say("Gus didn't go off the edge. He went down the stairs.")

		"roof_door":
			if verb == "look":
				await main.say("Back down to the office.")
			elif item != "":
				await default_response(verb, item)
			else:
				await main.change_room("stardust_office", "stardust_roof")

		_:
			await default_response(verb, item)


func _charlie(line: String) -> void:
	await main.voice(line, speaker_at("charlie"), Case3.CHARLIE_COLOR)


func _maybe_hint() -> void:
	var key := ""
	var hint := ""
	if Game.has_item("fake_oscar") and Game.has_item("star_earring"):
		key = "hint_roof_done"
		hint = "I've got what she hid and what she lost. Time to go downstairs and see what she says."
	elif Game.has_item("star_earring") and not Game.flag("got_fake_oscar"):
		key = "hint_roof_tank"
		hint = "Her heels went to that tank and came back. People don't visit water tanks."
	if key == "" or Game.flag(key):
		_wander = 0
		return
	_wander += 1
	if _wander >= 4:
		_wander = 0
		Game.set_flag(key)
		await main.say(hint)


# --- Puzzle 4.2: the water tank ----------------------------------------------------------
func _tank() -> void:
	await main.player.play_action("use")
	await main.say("Neon light slides across black water a foot below the rim. Something floats face down in it, gold, like a drowned starlet.")
	await main.player.play_action("pickup")
	await main.say("Lyle Brandt. Best Supporting Actor, 1954. Floating.")
	await main.say("It comes up far too easily. Eight and a half pounds of metal doesn't float. This is resin, hollow as a promise.")
	if Game.flag("clue_weight"):
		await main.say("Morty said they'd float in a bathtub.")
	await main.say("No. 734 engraved on the base, and the cuts still shine. Somebody had this made.")
	Game.set_flag("got_fake_oscar")
	await main.give("fake_oscar", false)
	main.clue("clue_replica")
	await main.say("Nobody stole Lyle tonight. Lyle left three weeks ago.")
	await main.say("Somebody hid this one up here to make a robbery out of it, because nobody walks down Hollywood Boulevard at two in the morning with a gold statue under their arm.")
	await main.say("Not past forty cameras.")


# --- Charlie ------------------------------------------------------------------------------
func _talk_to_charlie() -> void:
	if not Game.flag("met_charlie"):
		Game.set_flag("met_charlie")
		await main.say("Detective Kessler. And you are?")
		await _charlie("On the boulevard, Charlie. To the IRS, Desmond Pike. Thirty-one years in the forecourt.")
		await _charlie("I've been in more tourists' photographs than the Pope.")
	while true:
		var opts := []
		var keys := []
		if not Game.flag("clue_fiat"):
			opts.append("What did you see tonight?"); keys.append("saw")
		if not Game.flag("clue_shouting"):
			opts.append("Did you hear anything?"); keys.append("heard")
		if not Game.flag("charlie_gus"):
			opts.append("You knew Gus?"); keys.append("gus")
		if Game.has_item("brenner_card") and not Game.flag("clue_block_empty"):
			opts.append("Ever seen this man?"); keys.append("brenner")
		opts.append("Good night, Charlie."); keys.append("done")
		var c: int = await main.choose(opts)
		if keys[c] != "brenner":
			await main.say(opts[c])
		match keys[c]:
			"saw":
				await _charlie("I came home at midnight. At one I came out for my pipe, as I do.")
				await _charlie("Pearl's little yellow Fiat was down in the alley, behind Gus's back door. I thought, he's working that poor girl late again.")
				await main.say("Around one.")
				await _charlie("My pipe keeps better time than the studio. One o'clock, one pipe. Like Gus and his cigar.")
				main.clue("clue_fiat")
			"heard":
				await _charlie("Half past one, perhaps. Gus, up here, shouting. \"How long? How long?\" Over and over.")
				await _charlie("I couldn't hear who he was shouting at. The rain, and I'm seventy-three, and I'd gone inside. Then nothing. I thought, good, they've made up.")
				await main.wait(1.0)
				await _charlie("I should have come out.")
				main.clue("clue_shouting")
			"gus":
				Game.set_flag("charlie_gus")
				await _charlie("Thirty years. He sold me this derby. Told me it was Chaplin's own. It wasn't. He told me that too, after I'd paid.")
				await _charlie("He'd have hated this fuss.")
			"brenner":
				await _brenner()
			"done":
				await _charlie("Good night, Detective. Tell Pearl...")
				await main.wait(0.8)
				await _charlie("No. Don't tell Pearl anything. She was always kind to me.")
				return


func _brenner() -> void:
	## The seed's second half: Brenner on the block last Thursday, "the jazz club too".
	if Game.flag("clue_block_empty"):
		await _charlie("Him again? I told you. Big fellow, cop's shoes. Empty by Christmas.")
		return
	await main.player.play_action("use")
	await main.say("Ever seen this man?")
	await _charlie("Him. Big fellow, old raincoat, cop's shoes. Last Thursday he went door to door, handing those out like a priest with wafers.")
	await _charlie("Said the whole block would be empty by Christmas. \"The jazz club too,\" he said. As if it were good news.")
	await main.say("The jazz club.")
	await _charlie("The Blue Note, round the corner. You can see the sign from here. Gus told him to go to hell. In Swedish, so it took longer.")
	main.clue("clue_block_empty")
	await main.wait(1.5)
