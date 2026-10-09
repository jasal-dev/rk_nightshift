extends Room
## The LA River channel under the Fletcher Drive bridge (Case 4, scene 3). Dr. Shah with Owen; Owen's bike at
## Preacher's tent with his phone still in the mount; the stairs and the east bank; the reed island under the bridge.
## Puzzle 3.1: the bike (clue_paint, the lens shard, clue_nursing). Puzzle 3.2: Owen's phone (clue_last_drop, clue_one_star,
## clue_trip_paused). Puzzle 3.3: two sets of tracks (clue_two_tracks). Puzzle 3.4: the reeds, dark until Doss's
## spotlight is on them: half a headlight, and Danny Reyes's phone. Preacher stands at his tent once he's freed.

@onready var preacher: Sprite2D = $Actors/Preacher
@onready var spot: Sprite2D = $Spot
var _wander := 0


func _ready() -> void:
	super._ready()
	add_rain(420, -0.15)
	_sync()


func _sync() -> void:
	preacher.visible = Game.flag("preacher_freed")
	hotspot("preacher").enabled = preacher.visible
	spot.visible = Game.flag("channel_lit")
	hotspot("beam").enabled = spot.visible


func on_enter(_from_room: String) -> void:
	if not Game.flag("in_channel"):
		Game.set_flag("in_channel")
		await main.wait(0.4)
		await main.say("The Los Angeles River. Fifty-one miles of concrete and three inches of water, doing an impression of a river.")
		await _shah("Third time tonight, Ray. One more and I get a free coffee.")
		await main.say("Make it two more and I'll buy.")


func interact(hs: Hotspot, verb: String, item: String) -> void:
	if not hs.id in ["shah", "preacher"]:
		await _maybe_hint()
	match hs.id:
		"owen":
			if verb == "look":
				await main.say("Owen Tate. Twenty-four. His Chomp jacket says SPEED IS SERVICE in letters bigger than his name.")
			elif item != "":
				await default_response(verb, item)
			else:
				await main.say("Shah's got him.")

		"shah":
			if verb == "look":
				await main.say("Dr. Shah, kneeling on wet concrete at four in the morning. Third time tonight.")
			elif item == "lens_shard" or item == "lens_piece":
				await _shah("Same plastic I took out of his hair. Bag it.")
			elif item == "danny_phone":
				await _shah("That's been in the water a lot longer than he has.")
			elif item != "":
				await default_response(verb, item)
			else:
				await _talk_to_shah()

		"bike":
			if verb == "look":
				await main.say("A heavy secondhand e-bike. The back end's crushed: rack bent, rear light smashed, yellow box caved in.")
			elif item != "":
				await default_response(verb, item)
			else:
				await _bike()

		"phone":
			if item != "":
				await default_response(verb, item)
			elif verb == "look":
				await main.say("Owen's phone, still in the mount.")
				if Game.flag("clue_preacher_story") and not Game.flag("clue_phone_left"):
					await main.say("Preacher carried this bike down a flight of stairs and never touched a nine-hundred-dollar phone.")
					main.clue("clue_phone_left")
			else:
				await _owens_phone()

		"tent":
			if item != "":
				await default_response(verb, item)
			elif verb == "look":
				await main.say("A tarp tent pitched square as a barracks. Boots lined up, a folded flag, a Bible on a milk crate.")
			else:
				await main.say("It's his house. I'll knock with my eyes.")

		"preacher":
			if verb == "look":
				await main.say("Preacher, at his tent, reading to the river.")
			elif item == "danny_phone":
				await _seen_this()
			elif item != "":
				await default_response(verb, item)
			else:
				await _talk_to_preacher()

		"east_bank":
			if item != "":
				await default_response(verb, item)
			elif verb == "look":
				await main.say("Two long lines in the green slime, side by side, from the fence gap at the top down to where Owen lies.")
				await main.say("Heels. Somebody dragged him to the edge and let the slope do the rest.")
				main.clue("clue_drag_marks")
				await _two_tracks()
			else:
				await main.say("Too steep and too slick. Owen didn't walk down it either.")

		"stairs":
			if item != "":
				await default_response(verb, item)
			elif verb == "look":
				await main.say("Down the middle of every step, a single muddy tire line, and big boot prints beside it. That's how the bike came down.")
				main.clue("clue_bike_stairs")
				await _two_tracks()
			else:
				await main.change_room("fletcher_bridge", "river_channel")

		"reeds":
			if item != "":
				await default_response(verb, item)
			elif not Game.flag("channel_lit"):
				Game.set_flag("reeds_dark")
				if verb == "look":
					await main.say("A reed island under the bridge, black as a closet. My flashlight makes it look worse.")
				else:
					await main.say("I'm not wading into the LA River blind. Not at my age.")
			elif verb == "look":
				await main.say("Doss's spotlight lays a white oval across the reeds. Something glints in the roots.")
			elif Game.flag("got_danny_phone"):
				await main.say("Water, mud, a shopping cart. Nothing else of anybody's.")
			else:
				await _the_reeds()

		"drain_pipe":
			if item != "":
				await default_response(verb, item)
			elif verb == "look":
				await main.say("A drain pipe sticks out of the pier, dribbling into the reeds. That's where the bridge's gutters come out.")
				if Game.flag("clue_scupper"):
					await main.say("Everything that went down that grate came out right here.")
			else:
				await main.say("I'm not climbing into a drain. I've done enough tonight that I'll have to explain.")

		"water":
			if item != "":
				await default_response(verb, item)
			elif verb == "look":
				await main.say("Three inches deep and in no hurry.")
			else:
				await main.say("It's colder than it looks. Most things are, down here.")

		"willows":
			if item != "":
				await default_response(verb, item)
			else:
				await main.say("Somebody planted willows in the river to make it look like a river. The willows haven't been told.")

		"beam":
			if item != "":
				await default_response(verb, item)
			else:
				await main.say("Doss's spotlight. Brightest thing on the river tonight.")

		_:
			await default_response(verb, item)


func _shah(line: String) -> void:
	await main.voice(line, speaker_at("shah"), Case2.SHAH_COLOR)


func _preacher(line: String) -> void:
	await main.voice(line, speaker_at("preacher"), Case4.PREACHER_COLOR)


func _maybe_hint() -> void:
	var hint := ""
	var key := ""
	if Game.flag("clue_hit_by_car") and not Game.flag("preacher_freed"):
		key = "hint_channel_uncuff"
		hint = "Shah's sure it was a car. Preacher's still sitting in one. One of those things has to change."
	elif Game.has_item("lens_shard") and not Game.flag("got_lens_piece"):
		key = "hint_channel_shard"
		hint = "A sliver of a headlight. Where's the rest of its face?"
	elif Game.flag("clue_last_drop") and not Game.flag("channel_lit"):
		key = "hint_channel_reeds"
		hint = "Glendower can wait two minutes. Those reeds can't tell me anything in the dark."
	if key == "" or Game.flag(key):
		_wander = 0
		return
	_wander += 1
	if _wander >= 4:
		_wander = 0
		Game.set_flag(key)
		await main.say(hint)


# --- Dr. Shah ---------------------------------------------------------------------------------
func _talk_to_shah() -> void:
	while true:
		var opts := []
		var keys := []
		if not Game.flag("clue_hit_by_car"):
			opts.append("How did he die?"); keys.append("how")
		if not Game.flag("clue_tod_owen"):
			opts.append("When?"); keys.append("when")
		if Game.flag("clue_hit_by_car") and not Game.flag("clue_moved"):
			opts.append("The scrapes on him."); keys.append("scrapes")
		if not Game.flag("clue_headlight_glass"):
			opts.append("Anything else?"); keys.append("else")
		opts.append("Thanks, Anita."); keys.append("done")
		var c: int = await main.choose(opts)
		await main.say(opts[c])
		match keys[c]:
			"how":
				await _shah("A car. Both lower legs broken at the same height, nineteen inches up, from behind. That's a bumper.")
				await _shah("Then he went up onto the hood, the back of his head hit the edge of it, and he came down on the road. It was fast, Ray. He didn't feel the river.")
				await main.say("Not a beating.")
				await _shah("Somebody should tell Officer Doss that a beating doesn't break both shins at bumper height.")
				main.clue("clue_hit_by_car")
			"when":
				await _shah("Between a quarter to two and half past. Rain and cold concrete, so don't hold me to the minute.")
				main.clue("clue_tod_owen")
			"scrapes":
				await _shah("His back and arms are scraped raw. That's the slope. And they barely bled.")
				await main.say("Meaning?")
				await _shah("Meaning his heart had already stopped when he went down the bank. He didn't fall down here, Ray. Somebody slid him.")
				main.clue("clue_moved")
			"else":
				await _shah("Glass in his hair. Not windshield; that crumbles into little cubes. This is hard, clear plastic, with an edge. Headlight.")
				await main.say("From the car.")
				await _shah("From the car's face. Somebody's driving around tonight with one eye.")
				main.clue("clue_headlight_glass")
			"done":
				await _shah("He's got a card in his wallet with his mother's number on it. It says \"In case.\"")
				await main.wait(0.6)
				await _shah("Somebody's going to have to use it.")
				return


# --- Puzzle 3.1: the bike ---------------------------------------------------------------------
func _bike() -> void:
	if not Game.flag("got_lens_shard"):
		await main.player.play_action("use")
		await main.say("Hit from behind. The rack's bent flat and the box is caved in like somebody stepped on a lunchbox.")
		await main.say("Blue-gray paint flakes in the bent metal. Somebody's car left a little of itself here.")
		main.clue("clue_paint")
		await main.say("And wedged in a crack in the box, a sliver of clear plastic with a curved edge.")
		Game.set_flag("got_lens_shard")
		await main.give("lens_shard", false)
	elif not Game.flag("clue_nursing"):
		await main.player.play_action("use")
		await main.say("Under the crushed lid, a stack of receipts and a used textbook. Anatomy and Physiology, a community college sticker on the spine.")
		await main.say("He rode nights so he could study days.")
		main.clue("clue_nursing")
	else:
		await main.say("Receipts, a textbook, and a bent rack. That's all Owen had back there.")


# --- Puzzle 3.2: Owen's phone -----------------------------------------------------------------
const OWEN_NOTES := ["Chomp  12:58 AM\nNew order #4471. Glendower Ave, Los Feliz. 8 x pad thai.\nNote: STAFF, USE SIDE GATE, ASK VALET.",
		"Chomp  1:50 AM\nOrder #4471 delivered. Customer rating: 1 star.\n\"LATE. Cold. Rude. Threatened that someone would get killed.\"",
		"Chomp  2:04 AM\nTrip paused. No movement detected. Fletcher Dr.",
		"Chomp  2:20 AM\nStill riding? Tap to resume.",
		"Mom  2:31 AM\nhome yet? text me",
		"Mom  3:15 AM\nOwen?"]


func _owens_phone() -> void:
	await main.player.play_action("use")
	main.ui.show_device("Locked", [], 0, "Cracked, still on. Notifications:", OWEN_NOTES, false, Case4.CHOMP)
	if Game.flag("clue_last_drop"):
		await main.say("Glendower at one-fifty. A one-star review. Two-oh-four, the trip paused. And his mother.")
		main.ui.hide_device()
		return
	await main.say("It's locked, but the notifications show.")
	await main.say("Glendower Avenue, up in the hills over Los Feliz. That's where his night ended.")
	main.clue("clue_last_drop")
	await main.say("One star. \"Threatened that someone would get killed.\"")
	main.clue("clue_one_star")
	await main.say("Two-oh-four, he stopped moving on Fletcher Drive.")
	main.clue("clue_trip_paused")
	await main.wait(1.2)
	await main.say("Not yet.")
	main.ui.hide_device()


# --- Puzzle 3.3: two sets of tracks -------------------------------------------------------------
func _two_tracks() -> void:
	if Game.flag("clue_drag_marks") and Game.flag("clue_bike_stairs") and not Game.flag("clue_two_tracks"):
		await main.wait(0.4)
		await main.say("The bike came down the stairs with Preacher. Owen came down the bank with somebody else.")
		main.clue("clue_two_tracks")


# --- Preacher, at his tent ----------------------------------------------------------------------
func _talk_to_preacher() -> void:
	if not Game.flag("preacher_at_tent"):
		Game.set_flag("preacher_at_tent")
		await _preacher("You didn't have to do that.")
		await main.say("I did, actually. That's the job.")
		await _preacher("Then it's a good job, tonight.")
	while true:
		var opts := []
		var keys := []
		if not Game.flag("clue_reeds_tip"):
			opts.append("Where does stuff end up, off that bridge?"); keys.append("reeds")
		if Game.has_item("danny_phone") and not Game.flag("clue_big_man"):
			opts.append("Ever seen this?"); keys.append("phone")
		if not Game.flag("preacher_ok"):
			opts.append("Will you be all right?"); keys.append("ok")
		opts.append("Take care, Preacher."); keys.append("done")
		var c: int = await main.choose(opts)
		if keys[c] != "phone":
			await main.say(opts[c])
		match keys[c]:
			"reeds":
				await _preacher("The reeds, under the drain. Everything comes to the reeds. Shopping carts. Shoes. A wedding dress, once. I didn't ask.")
				main.clue("clue_reeds_tip")
			"phone":
				await _seen_this()
			"ok":
				Game.set_flag("preacher_ok")
				await _preacher("The uniform said sorry, after. Nobody's said sorry to me since 1991.")
				await main.wait(0.5)
				await _preacher("I'll be all right. Go find who did that boy.")
			"done":
				await _preacher("\"The Lord is nigh unto them that are of a broken heart.\" Psalm thirty-four. Go on.")
				return


func _seen_this() -> void:
	if Game.flag("clue_big_man"):
		await _preacher("I told you what I saw. I'll tell it again in a courtroom if somebody asks me.")
		return
	await main.say("Ever seen this?")
	await main.player.play_action("use")
	await main.wait(0.6)
	await _preacher("Not up close. But I seen it fly. Tuesday night, past three. Bars closed, freeway quiet.")
	await _preacher("A long gray car stops in the middle of the bridge. A big man gets out. Old cop's coat, the kind with the belt.")
	await _preacher("Stands at the rail like he's praying. Then he throws something. Small. Black. Into the reeds, under the drain.")
	await main.say("You see his face?")
	await _preacher("Didn't need to. I've seen a thousand like him. He stood like a cop. Cops stand like the ground owes them money.")
	main.clue("clue_big_man")
	if Game.flag("clue_block_empty"):
		await main.say("Big fellow, old raincoat, cop's shoes.")
	elif Game.flag("heard_caller"):
		await main.say("A cop who'd stopped being one.")
	else:
		await main.say("Thanks, Preacher.")


# --- Puzzle 3.4: the reeds, under the spotlight ---------------------------------------------------
func _the_reeds() -> void:
	await main.player.play_action("use")
	await main.say("I step off the concrete into the water. It's colder than it looks.")
	await main.say("There. Half a headlight, jammed in the roots. Clear plastic, curved, chrome on the back.")
	Game.set_flag("got_lens_piece")
	await main.give("lens_piece", false)
	await main.examine_item("lens_piece")
	await main.wait(0.6)
	await main.say("Something else catches the light, a few feet deeper in, pressed into the mud. A phone in a cracked black case.")
	await main.say("Somebody else lost something down here.")
	await main.player.play_action("pickup")
	await main.say("River water runs out of the case. On the back, a Blue Note sticker, half peeled. Under it, white tape, in marker:")
	main.ui.show_paper("", "D.R.\nIF FOUND CALL\nTHE BLUE NOTE", "", Color.BLACK)
	await main.say("\"D.R. If found call the Blue Note.\"")
	main.ui.hide_paper()
	await main.wait(1.4)
	await main.say("Hello, Danny.")
	Game.set_flag("got_danny_phone")
	await main.give("danny_phone", false)
	main.clue("clue_danny_phone")
	await main.say("Danny Reyes's phone. Two nights in the river. Somebody wanted it to go out to sea.")
	await main.say("This river hasn't taken anything anywhere since they poured the concrete.")
