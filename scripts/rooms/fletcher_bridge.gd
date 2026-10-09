extends Room
## The Fletcher Drive bridge over the LA River (Case 4, scene 2). Officer Doss and his patrol car, Preacher cuffed in
## the back seat. Puzzle 2.1: the motto (preacher_trusts). Puzzle 2.2: the road, the gutter and the storm drain
## (clue_scupper). Puzzle 2.3: uncuff him (clue_hit_by_car plus clue_two_tracks or clue_phone_left).
## Puzzle 2.4: the spotlight on the reeds (channel_lit), offered once Ray has seen them dark (reeds_dark). The stairs
## go down to the channel; Ray's car opens the car menu once Owen's phone has told him where he'd been. Preacher in
## the car and the spotlight's two aims are overlays.

@onready var preacher_car: Sprite2D = $Actors/Preacher_car
@onready var beam_road: Sprite2D = $Beam_road
@onready var beam_down: Sprite2D = $Beam_down
var _wander := 0


func _ready() -> void:
	super._ready()
	add_rain(520, -0.2)
	_sync()


func _sync() -> void:
	preacher_car.visible = not Game.flag("preacher_freed")
	beam_road.visible = not Game.flag("channel_lit")
	beam_down.visible = Game.flag("channel_lit")


func on_enter(from_room: String) -> void:
	if from_room == "drive" and not Game.flag("met_doss"):
		Game.set_flag("met_doss")
		await main.wait(0.4)
		await main.say("Fletcher Drive. Built in 1927, back when the city still thought the river was worth looking at.")
		await _doss("Detective! Brian Doss, Northeast. Sorry to drag you out. Honestly, it's a wrap. Kid's bike, guy's tent. Coroner's just being thorough.")
		await main.say("She usually is.")


func interact(hs: Hotspot, verb: String, item: String) -> void:
	if not hs.id in ["doss", "patrol_car"]:
		await _maybe_hint()
	match hs.id:
		"doss":
			if verb == "look":
				await main.say("Officer Doss. Happy as a man with a short day ahead of him.")
			elif item == "lens_shard" or item == "lens_piece":
				await _doss("Glass. Cool. Want an evidence bag?")
			elif item == "danny_phone":
				await _doss("That's not the kid's. His is on the bike.")
			elif item != "":
				await default_response(verb, item)
			else:
				await _talk_to_doss()

		"patrol_car":
			if verb == "look":
				if Game.flag("preacher_freed"):
					await main.say("Empty. Doss is pretending he never put anybody in it.")
				else:
					await main.say("Preacher, behind the cage. Sitting like he's on parade.")
			elif item != "":
				await default_response(verb, item)
			elif Game.flag("preacher_freed"):
				await main.say("Empty. Doss is pretending he never put anybody in it.")
			else:
				await _talk_to_preacher()

		"spotlight":
			if verb == "look":
				if Game.flag("channel_lit"):
					await main.say("Pointed down at the reeds. Doss is pretending it was his idea.")
				else:
					await main.say("A door-mounted spotlight, aimed at the road like it's expecting a parade.")
			elif item != "":
				await default_response(verb, item)
			else:
				await _doss("Hands off the unit, Detective. City property.")

		"road":
			if item != "":
				await default_response(verb, item)
			elif verb == "look":
				await main.say("Wet asphalt, a painted bike lane, and no skid marks. Not one. Whoever hit him never touched the brakes.")
				main.clue("clue_no_brakes")
			else:
				await main.say("Nothing on the road but rain.")

		"gutter":
			if item == "lens_shard" or item == "lens_piece":
				await main.say("Same plastic. Same headlight.")
			elif item != "":
				await default_response(verb, item)
			else:
				await main.say("Crumbs of clear plastic in the gutter by the bike lane. Not windshield glass; that breaks into little cubes. This has edges. Headlight.")
				main.clue("clue_glass_bridge")

		"storm_drain":
			if item != "":
				await main.say("I'm not feeding it anything else.")
			elif verb == "look":
				await main.say("A storm drain in the gutter, gurgling.")
			else:
				await main.player.play_action("use")
				await main.say("A storm drain, gurgling. Plastic glitter caught in the bars. The rain washed the big pieces down.")
				await main.say("Bridges drain straight into the river. Whatever went through that grate came out under the bridge.")
				main.clue("clue_scupper")

		"fence_gap":
			if item != "":
				await default_response(verb, item)
			elif verb == "look":
				await main.say("A gap in the chain-link where the bridge meets the bank. The concrete lip is scuffed fresh, and there's a smear in the algae going down.")
			else:
				await main.say("Too steep for these shoes. Whoever went down here went down hard. I'll take the stairs.")

		"railing":
			if item == "danny_phone":
				await main.say("It's been over once already.")
			elif item != "":
				await default_response(verb, item)
			elif verb == "look":
				if Game.flag("clue_big_man"):
					await main.say("Deco railing, ninety-some years old. Somebody leaned a bike on it tonight. Somebody leaned on it Tuesday night, too, and threw something over.")
				else:
					await main.say("Deco railing, ninety-some years old. Somebody leaned a bike on it tonight.")
			else:
				await main.say("A long way down to three inches of water.")

		"stairs":
			if verb == "look":
				await main.say("Concrete stairs down into the channel.")
			elif item != "":
				await default_response(verb, item)
			else:
				await main.change_room("river_channel", "fletcher_bridge")

		"lamps":
			if item != "":
				await default_response(verb, item)
			else:
				await main.say("Globes on iron posts. Half of them are out. The city fixes the other half when somebody important drives over.")

		"car":
			if verb == "look":
				await main.say("My car. Rain's getting in the dents.")
			elif item != "" and item != "valet_ticket":
				await default_response(verb, item)
			elif not Game.flag("clue_last_drop"):
				await main.say("Not yet. Owen hasn't told me where he'd been.")
			else:
				await Case4.car_menu(main, "fletcher_bridge")

		_:
			await default_response(verb, item)


func _doss(line: String) -> void:
	await main.voice(line, speaker_at("doss"), Case4.DOSS_COLOR)


func _preacher(line: String) -> void:
	await main.voice(line, speaker_at("patrol_car"), Case4.PREACHER_COLOR)


func _maybe_hint() -> void:
	## A nudge after a few actions without progress, once per stuck point.
	var hint := ""
	var key := ""
	if Game.flag("clue_hit_by_car") and not Game.flag("preacher_freed"):
		key = "hint_bridge_uncuff"
		hint = "Shah says a car. Doss says a tent. Only one of them went to medical school."
	elif Game.flag("reeds_dark") and not Game.flag("channel_lit"):
		key = "hint_bridge_spot"
		hint = "Everything that went down that drain is in the reeds. Doss has a spotlight he's very proud of."
	if key == "" or Game.flag(key):
		_wander = 0
		return
	_wander += 1
	if _wander >= 4:
		_wander = 0
		Game.set_flag(key)
		await main.say(hint)


# --- Officer Doss ------------------------------------------------------------------------------
func _talk_to_doss() -> void:
	while true:
		var opts := []
		var keys := []
		if not Game.flag("doss_got"):
			opts.append("What have you got?"); keys.append("got")
		if not Game.flag("doss_found"):
			opts.append("Who found him?"); keys.append("found")
		if not Game.flag("doss_why"):
			opts.append("Why's he in your car?"); keys.append("why")
		if not Game.flag("preacher_freed"):
			opts.append("Uncuff him."); keys.append("uncuff")
		if not Game.flag("channel_lit") and Game.flag("reeds_dark"):
			opts.append("Put your spotlight on the reeds."); keys.append("spot")
		opts.append("That'll do."); keys.append("done")
		var c: int = await main.topics(opts)
		if c < 0:
			return
		await main.say(opts[c])
		match keys[c]:
			"got":
				Game.set_flag("doss_got")
				await _doss("Owen Tate, twenty-four, rides for Chomp. He's down on the concrete under the east end. His e-bike was parked at that guy's tent. Two thousand bucks of bike. Guy says he \"found it.\"")
				await main.say("Maybe he did.")
				await _doss("They always found it.")
				await main.say("Who's they?")
				await _doss("You know. Them.")
			"found":
				Game.set_flag("doss_found")
				await _doss("Metro bus driver on the owl route, three twenty-two. Saw a yellow bag down in the channel in his headlights and called it in. Good eyes. I'd have missed it.")
				await main.say("That's what worries me, Officer.")
			"why":
				Game.set_flag("doss_why")
				await _doss("Calvin Odom, they call him Preacher. Army guy, lives under the bridge. Won't say a word to me. Says he'll only talk to \"somebody who's been somewhere.\"")
				await main.wait(0.5)
				await _doss("I've been to Rancho Cucamonga.")
			"uncuff":
				var freed: bool = await _uncuff()
				if freed:
					return
			"spot":
				await _spotlight()
				return
			"done":
				await _doss("I'll be right here. My shift ends at five, so, you know. No rush.")
				return


func _uncuff() -> bool:
	## Puzzle 2.3: a car, not a beating, and the bike and Owen came down two different ways.
	if not Game.flag("clue_hit_by_car") or not (Game.flag("clue_two_tracks") or Game.flag("clue_phone_left")):
		await _doss("On what, a feeling?")
		await main.say("I'll come back with more than a feeling.")
		return false
	await main.say("Shah says a car hit that kid from behind, hard enough to break both his legs at bumper height. Your man doesn't have a car.")
	if Game.flag("clue_two_tracks"):
		await main.say("And the bike came down the stairs on one wheel. Owen came down the bank on his heels, dragged. Two trips, two different people.")
	else:
		await main.say("And a man who steals a two-thousand-dollar bike leaves a nine-hundred-dollar phone on the handlebars?")
	await main.wait(1.4)
	await _doss("Northeast is gonna love this.")
	await main.ui.fade_to(1.0, 0.5)
	Game.set_flag("preacher_freed")
	_sync()
	await main.ui.fade_to(0.0, 0.5)
	await main.say("He rubbed his wrists, looked at me, and said nothing. Then he walked down the stairs into the channel, back straight.")
	return true


func _spotlight() -> void:
	## Puzzle 2.4: Doss lights up the river.
	await main.say("Swing your spotlight over the rail. Under the bridge, on the reeds below the drain pipe.")
	await _doss("You want me to light up the river? At four in the morning?")
	await main.wait(0.4)
	await _doss("Sure. Not my electricity.")
	await main.ui.fade_to(0.6, 0.3)
	Game.set_flag("channel_lit")
	_sync()
	await main.ui.fade_to(0.0, 0.4)
	await main.say("A hard white beam drops over the railing into the channel, onto a black island of reeds.")


# --- Preacher, in the back of the patrol car -----------------------------------------------------
func _talk_to_preacher() -> void:
	if not Game.flag("met_preacher"):
		Game.set_flag("met_preacher")
		await main.say("Hands cuffed behind him, a gray beard, an Army field jacket. His lips are moving.")
		await _preacher("\"...and the waters returned from off the earth continually.\" Genesis, eight. You're the detective.")
		await main.say("Ray Kessler.")
		await _preacher("That young man says I killed a boy for a bicycle. I told him I'd speak to somebody who's been somewhere.")
	if not Game.flag("preacher_trusts"):
		await _somewhere()
		if not Game.flag("preacher_trusts"):
			return
	while true:
		var opts := []
		var keys := []
		if not Game.flag("clue_preacher_story"):
			opts.append("What happened tonight?"); keys.append("story")
		if not Game.flag("clue_bang"):
			opts.append("Did you hear anything?"); keys.append("bang")
		if not Game.flag("preacher_saw"):
			opts.append("Did you see the boy?"); keys.append("saw")
		if not Game.flag("preacher_carry"):
			opts.append("Why carry the bike all the way down?"); keys.append("carry")
		opts.append("That'll do."); keys.append("done")
		var c: int = await main.topics(opts)
		if c < 0:
			return
		await main.say(opts[c])
		match keys[c]:
			"story":
				await _preacher("I was in my tent with Deuteronomy. Some while after two, I see a red light blinking on the water. Off, on, off, on. Up on the bridge. So I went up the stairs.")
				await _preacher("A bicycle, leaning on the rail, light still going, nobody with it. Big yellow box on the back, all stove in.")
				await _preacher("I carried it down. By sunup the strippers would've had the wheels, the battery, the seat. I meant to hand it to the first police I saw.")
				await main.wait(0.5)
				await _preacher("The first police I saw put me in this car.")
				main.clue("clue_preacher_story")
			"bang":
				await _preacher("Two o'clock, about. A bang up top, like a dumpster lid. No brakes before it. I know brakes.")
				await _preacher("Then quiet. Then a long while after, a car door. Then a car going away slow, like it was ashamed of itself.")
				await main.say("How long a while?")
				await _preacher("Long enough for a man to do something. Not long enough to do it right.")
				main.clue("clue_bang")
			"saw":
				Game.set_flag("preacher_saw")
				await _preacher("No, sir. He was on the far side, under the east end, in the dark. If I'd seen him I'd have gone to him.")
				await main.wait(0.5)
				await _preacher("I'd have sat with him.")
			"carry":
				Game.set_flag("preacher_carry")
				await _preacher("Because nobody steals from my camp. That's the rule down there. I'm the rule.")
			"done":
				await _preacher("I'll be in this car. Unless somebody decides different.")
				return


func _somewhere() -> void:
	## Puzzle 2.1: somebody who's been somewhere. Wrong answers just loop back.
	while true:
		var c: int = await main.choose(["I've been somewhere.", "Did you kill him?", "Never mind."])
		if c == 2:
			await main.say("Never mind.")
			return
		if c == 1:
			await main.say("Did you kill him?")
			await _preacher("The Lord knows I did not. That young man doesn't. Ask me better.")
			continue
		await main.say("I've been somewhere.")
		await _preacher("Where?")
		var w: int = await main.choose(["Baghdad, oh-three. Military Police.", "Hollywood Division, twenty-six years.",
				"Everywhere, friend."])
		match w:
			1:
				await main.say("Hollywood Division, twenty-six years.")
				await _preacher("That's a long time somewhere. It ain't what I asked.")
				continue
			2:
				await main.say("Everywhere, friend.")
				await _preacher("A man who's been everywhere has been nowhere twice.")
				continue
		await main.say("Baghdad, oh-three. Military Police.")
		await _preacher("MP. Then you know your motto, MP.")
		var m: int = await main.choose(["Assist, Protect, Defend.", "Semper Fidelis.", "Rangers lead the way.",
				"To protect and to serve."])
		match m:
			1:
				await main.say("Semper Fidelis.")
				await _preacher("That's a Marine. You don't stand like a Marine.")
				await main.say("Twenty years. They take the motto back with the uniform.")
				continue
			2:
				await main.say("Rangers lead the way.")
				await _preacher("You ain't no Ranger. Rangers don't drink that much coffee.")
				continue
			3:
				await main.say("To protect and to serve.")
				await _preacher("That's painted on your car door. I asked about the Army.")
				continue
		await main.say("Assist, protect, defend.")
		await main.wait(0.8)
		await _preacher("Assist, protect, defend. First Cavalry, Desert Storm. Seventy-two hours to Kuwait City and thirty years to get here.")
		await _preacher("Calvin Odom. They call me Preacher because I read to the river.")
		await main.say("Does it listen?")
		await _preacher("Better than most.")
		Game.set_flag("preacher_trusts")
		return
