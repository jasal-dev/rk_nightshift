extends Room
## The glass house on Glendower Avenue, Los Feliz (Case 4, scene 4). Courtney Vail, the event planner, and Andre, the
## valet. Puzzle 4.1: tell Courtney about Owen (courtney_cam), then her gate camera app: five clips (the drunk taking his
## keys, the Audi following Owen out, Courtney locking up). Andre's valet ticket No. 47. The optional seed: Pryce's
## invitation in the box of gift bags. Puzzle 4.2: with a plate, Ray's car rings Otis before the car menu opens.

const OWEN_COLOR := Color(0.95, 0.82, 0.4)        ## Owen, on the gate camera
const CAM_AT := Vector2(1536, 330)                 ## lines from a clip on the gate camera app

var _wander := 0


func _ready() -> void:
	super._ready()
	add_rain(440, -0.12)


func on_enter(_from_room: String) -> void:
	if not Game.flag("at_glass_house"):
		Game.set_flag("at_glass_house")
		await main.wait(0.4)
		await main.say("Los Feliz. Up here the rain falls on a better class of people.")


func interact(hs: Hotspot, verb: String, item: String) -> void:
	if not hs.id in ["courtney", "andre"]:
		await _maybe_hint()
	match hs.id:
		"courtney":
			if verb == "look":
				await main.say("Courtney Vail, Vail Events. A headset, a clipboard, and a jaw that hasn't unclenched since Labor Day.")
			elif item == "lens_piece" or item == "lens_shard":
				await _courtney("Is that... from a car?")
			elif item == "danny_phone":
				await _courtney("That's not mine.")
			elif item != "":
				await default_response(verb, item)
			else:
				await _talk_to_courtney()

		"andre":
			if verb == "look":
				await main.say("The valet. Nineteen, soaked, still standing up straight.")
			elif item == "valet_ticket":
				await _andre("I wrote it down. I swear I wrote it down.")
			elif item != "":
				await default_response(verb, item)
			else:
				await _talk_to_andre()

		"valet_board":
			if item != "":
				await default_response(verb, item)
			elif verb == "look":
				await main.say("A board of hooks. One key left, on a Range Rover fob.")
			else:
				await main.say("It's not my car, and it's not his.")

		"gate_camera":
			if item != "":
				await default_response(verb, item)
			elif verb == "look":
				await main.say("A camera on the gatepost, red light blinking.")
			else:
				await main.say("Courtney's got the app.")

		"curb":
			if item == "lens_piece":
				await main.say("Same blue-gray.")
			elif item != "":
				await default_response(verb, item)
			else:
				await main.say("A fresh scrape along the curb, and a fleck of blue-gray paint in it.")
				main.clue("clue_curb_scrape")

		"easel":
			if item != "":
				await default_response(verb, item)
			elif verb == "look":
				await main.say("\"Friends of Ted Haskell. Hollywood Core: The Future Has a Skyline.\" The future has good lighting.")
			else:
				await main.say("I'll leave it for the next party.")

		"gift_bags":
			if item != "":
				await default_response(verb, item)
			elif verb == "look":
				await main.say("A box of unclaimed gift bags. \"Hollywood Core\" printed on the side. Rich people leave free things behind the way they leave tips.")
			elif not Game.flag("got_pryce_invite"):
				await main.player.play_action("pickup")
				await main.say("A candle, a bottle of olive oil with a councilman's smile on the label, and a card.")
				Game.set_flag("got_pryce_invite")
				await main.give("pryce_invite", false)
			else:
				await main.say("More candles and more olive oil. One invitation's enough.")

		"van":
			if item != "":
				await default_response(verb, item)
			elif verb == "look":
				await main.say("Chafing dishes going home to Burbank. Two hundred people ate well tonight.")
			else:
				await main.say("Nothing in there but tomorrow's leftovers.")

		"house":
			if item != "":
				await default_response(verb, item)
			elif verb == "look":
				await main.say("A glass house on a hill, lit up like a display case. Nobody inside it throws anything.")
			else:
				await main.say("I'm not invited. I'm never invited.")

		"city":
			if item != "":
				await default_response(verb, item)
			else:
				await main.say("The whole basin, down to the port. Somewhere down there, the river.")

		"car":
			if verb == "look":
				await main.say("My car, parked between two Teslas like a stray between show dogs.")
			elif item != "" and item != "valet_ticket":
				await default_response(verb, item)
			else:
				await Case4.car_menu(main, "glass_house")

		_:
			await default_response(verb, item)


func _courtney(line: String) -> void:
	await main.voice(line, speaker_at("courtney"), Case4.COURTNEY_COLOR)


func _andre(line: String) -> void:
	await main.voice(line, speaker_at("andre"), Case4.ANDRE_COLOR)


func _maybe_hint() -> void:
	var hint := ""
	var key := ""
	if Game.flag("courtney_reported") and not Game.flag("courtney_cam"):
		key = "hint_glass_owen"
		hint = "She thinks he threatened her. Somebody should tell her what he was worried about."
	elif Game.flag("clue_plate") and not Game.flag("clue_crane_id"):
		key = "hint_glass_plate"
		hint = "I've got a plate. Otis can run it faster than I can spell it."
	if key == "" or Game.flag(key):
		_wander = 0
		return
	_wander += 1
	if _wander >= 4:
		_wander = 0
		Game.set_flag(key)
		await main.say(hint)


# --- Courtney Vail ------------------------------------------------------------------------------
func _talk_to_courtney() -> void:
	if not Game.flag("met_courtney"):
		Game.set_flag("met_courtney")
		await _courtney("No, the chafing dishes go back to Burbank, the linens go to...")
		await _courtney("We're closed. The event's over. If you're press, it was lovely.")
		await main.say("LAPD. Ray Kessler.")
		await _courtney("Oh God. Is this the noise thing? We had a permit.")
	while true:
		var opts := []
		var keys := []
		if Game.flag("courtney_cam"):
			opts.append("Show me the gate camera."); keys.append("cam")
		if not Game.flag("clue_host"):
			opts.append("Whose party was it?"); keys.append("host")
		if not Game.flag("courtney_chomp"):
			opts.append("You ordered from Chomp tonight."); keys.append("chomp")
		if Game.flag("clue_one_star") and not Game.flag("courtney_reported"):
			opts.append("You reported the rider."); keys.append("reported")
		if Game.flag("courtney_reported") and not Game.flag("courtney_cam"):
			opts.append("Tell her about Owen."); keys.append("owen")
		if not Game.flag("courtney_drunk"):
			opts.append("Who left drunk tonight?"); keys.append("drunk")
		opts.append("I'll let you work."); keys.append("done")
		var c: int = await main.choose(opts)
		if keys[c] != "owen" and keys[c] != "cam":
			await main.say(opts[c])
		match keys[c]:
			"cam":
				await _gate_camera()
			"host":
				await _courtney("Mr. Pryce's. Harlan Pryce, Pryce Development. It's his house, well, the company's.")
				await _courtney("A fundraiser for Councilmember Haskell. Two hundred guests, a string quartet, and a man who gave a forty-minute speech about density.")
				main.clue("clue_host")
			"chomp":
				Game.set_flag("courtney_chomp")
				await _courtney("For my crew. Eight pad thai. Forty minutes late and stone cold. The guests eat first. The staff eats last, or not at all.")
			"reported":
				Game.set_flag("courtney_reported")
				await _courtney("He was rude. He was late, and then he stood at my gate lecturing me about my guests. He said somebody was going to get killed.")
				await _courtney("I'm a woman alone at two in the morning with a gate code, Detective. That's a threat.")
			"owen":
				await _tell_her()
			"drunk":
				if Game.flag("courtney_cam"):
					Game.set_flag("courtney_drunk")
					await _courtney("Watch the one at one fifty-one.")
				else:
					await _courtney("Our guest list is confidential. You can call Mr. Pryce's office in the morning.")
			"done":
				await _courtney("Thank you.")
				await main.wait(0.6)
				await _courtney("The pad thai was cold because it was raining. I knew that. I knew it then.")
				return


func _tell_her() -> void:
	await main.say("His name was Owen Tate. He's dead, Ms. Vail. He's under the Fletcher Drive bridge.")
	await main.say("A car hit him at about two o'clock, ten minutes after he left your gate.")
	await main.wait(1.2)
	await _courtney("He said somebody was going to get killed.")
	await main.wait(0.6)
	await _courtney("He didn't mean me. He meant...")
	await _courtney("There's a camera on the gate. Mr. Pryce's people put cameras on everything. I have the app. Here.")
	Game.set_flag("courtney_cam")
	await _gate_camera()


# --- Puzzle 4.1: the gate camera ------------------------------------------------------------------
const CLIPS := ["1:49 AM  Front gate", "1:51 AM  Driveway", "1:53 AM  Front gate", "1:55 AM  Front gate",
		"2:38 AM  Front gate"]


func _gate_camera() -> void:
	await main.player.play_action("use")
	var body := "Motion clips, tonight."
	while true:
		var pick: String = await main.device("Gate camera", [], 0, body, CLIPS)
		if pick == "close":
			break
		var i := int(pick.substr(4))
		match i:
			0:
				main.ui.show_device("Gate camera", [], 0, "1:49 AM. Owen at the gate with two yellow bags, soaked through.", [], false)
				await main.voice("You're forty minutes late.", CAM_AT, Case4.COURTNEY_COLOR)
				await main.voice("It's raining, ma'am. The app stacks the orders.", CAM_AT, OWEN_COLOR)
			1:
				main.ui.show_device("Gate camera", [], 0, "1:51 AM. A man in a dark suit weaves past the valet podium and takes a key off the board himself.", [], false)
				await main.voice("Sir, I can call you a car...", CAM_AT, Case4.ANDRE_COLOR)
				await main.voice("I'm fine.", CAM_AT, Case4.CRANE_COLOR)
				main.ui.show_device("Gate camera", [], 0, "1:51 AM. At the gate, Owen steps into his way.", [], false)
				await main.voice("Hey, man. You can't drive like that.", CAM_AT, OWEN_COLOR)
				await main.voice("Mind your business, delivery boy.", CAM_AT, Case4.CRANE_COLOR)
				await main.voice("You're gonna let him drive? Somebody's gonna get killed.", CAM_AT, OWEN_COLOR)
				await main.voice("Just go.", CAM_AT, Case4.COURTNEY_COLOR)
				main.clue("clue_warning")
				main.clue("clue_crane_drunk")
			2:
				main.ui.show_device("Gate camera", [], 0, "1:53 AM. Owen rides off downhill, the red light blinking on the back of his box.", [], false)
				await main.say("Downhill toward Riverside Drive. Toward the river.")
			3:
				main.ui.show_device("Gate camera", [], 0, "1:55 AM. A blue-gray Audi rolls out of the drive, scrapes the curb and turns downhill, the same way. Both headlights bright.\n\nPaused, the plate reads 8KXD392.", [], false)
				await main.say("Both headlights at one fifty-five. Two minutes behind a kid on a bike, going the same way, in a hurry.")
				main.clue("clue_gate_clip")
				main.clue("clue_headlights_intact")
				main.clue("clue_plate")
			4:
				main.ui.show_device("Gate camera", [], 0, "2:38 AM. Courtney locks the gate from the inside, alone, and goes back up to the house.", [], false)
				await main.say("She never left.")
				main.clue("clue_courtney_alibi")
		body = "Motion clips, tonight."
	main.ui.hide_device()


# --- Andre Mitchell --------------------------------------------------------------------------------
func _talk_to_andre() -> void:
	if not Game.flag("met_andre"):
		Game.set_flag("met_andre")
		await _andre("Evening, sir. Morning. Are you picking up? I've only got one car left.")
	while true:
		var opts := []
		var keys := []
		if not Game.flag("andre_drunk"):
			opts.append("Who left drunk tonight?"); keys.append("drunk")
		if not Game.flag("andre_last"):
			opts.append("Who's the last car?"); keys.append("last")
		if not Game.flag("clue_pryce_driver"):
			opts.append("Who left early?"); keys.append("early")
		if Game.flag("andre_drunk") and not Game.flag("got_valet_ticket"):
			opts.append("I need the ticket."); keys.append("ticket")
		opts.append("Thanks, Andre."); keys.append("done")
		var c: int = await main.choose(opts)
		await main.say(opts[c])
		match keys[c]:
			"drunk":
				Game.set_flag("andre_drunk")
				await _andre("I'm not supposed to say. I'm not supposed to give keys to drunk guests. It's policy. I could lose the job.")
				await main.say("Did you give him the keys?")
				await _andre("No! He took them off the board himself. I offered him an Uber. I wrote it on the ticket so it's not on me. That's what they tell you to write.")
			"ticket":
				await _andre("Here.")
				await main.player.play_action("pickup")
				Game.set_flag("got_valet_ticket")
				await main.give("valet_ticket", false)
				await main.say("Number forty-seven. Audi A6, blue-gray, 8KXD392. Crane. Out one fifty-five. Guest insisted, offered rideshare, declined.")
				main.clue("clue_plate")
				await _andre("Am I in trouble?")
				await main.say("You wrote it down, Andre. You're the only one up here who did.")
			"last":
				Game.set_flag("andre_last")
				await _andre("A Range Rover. The lady took an Uber like a grown-up. She'll pick it up in the morning.")
			"early":
				await _andre("The councilman, at eleven, with his wife and a driver. Mr. Pryce too, around eleven. Gray Lincoln.")
				await _andre("He's got his own driver, big old guy, used to be a cop, you can tell. Sat in the car all night with the engine running and never came in. Didn't tip.")
				main.clue("clue_pryce_driver")
			"done":
				await _andre("Sir? The delivery guy. He was nice to me. He gave me a spring roll.")
				return
