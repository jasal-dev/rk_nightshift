extends Room
## Rainy street outside the precinct, across from the Blue Note (Case 1, scene 2).
## Puzzle: dumpster -> matchbook (number) ; dime + payphone -> Nina gives the knock ;
## knock on the bar door -> Sal names Vance ; the car drives to Pier 9 (scene 3).

const SAL_COLOR := Color(1.0, 0.62, 0.72)
const NINA_COLOR := Color(0.75, 0.9, 0.7)

@onready var neon: Sprite2D = $Neon
var _flicker_t := 0.0


func _ready() -> void:
	super._ready()
	add_rain()


func _process(delta: float) -> void:
	# neon sign buzz: mostly on, with the odd stutter
	_flicker_t -= delta
	if _flicker_t <= 0.0:
		_flicker_t = randf_range(0.05, 0.25) if randf() < 0.15 else randf_range(1.5, 4.0)
		neon.visible = randf() > 0.25 or _flicker_t > 1.0


func on_enter(from_room: String) -> void:
	if from_room == "squad_room" and not Game.flag("been_outside"):
		Game.set_flag("been_outside")
		await main.say("Rain. Of course it's raining.")
		await main.say("The Blue Note's across the street. Lights are off, but somebody's home.")


func interact(hs: Hotspot, verb: String, item: String) -> void:
	match hs.id:
		"precinct_door":
			if verb == "look":
				await main.say("The precinct. Coffee's worse than the company.")
			elif item != "":
				await default_response(verb, item)
			else:
				await main.change_room("squad_room", "street")

		"bar_door":
			if verb == "look":
				await main.say("The Blue Note. Door's locked. The light inside says somebody's home.")
			elif item != "":
				await main.say("I'd rather knock.")
			elif Game.flag("talked_to_sal"):
				await main.say("Sal's said all he's going to say.")
			elif not Game.flag("knows_knock"):
				await main.player.play_action("use")
				await main.say("*knock knock*")
				await main.wait(0.8)
				await main.say("Nothing. Whoever's in there isn't expecting company. Not my kind.")
			else:
				await _talk_to_sal()

		"neon":
			await main.say("BLUE NOTE. Live jazz Thursdays. Dead piano player Tuesday.")

		"rezoning":
			if verb == "look":
				await main.say("NOTICE OF PUBLIC HEARING. Zone change, 6400 block. Applicant: Pryce Development.")
			elif item != "":
				await default_response(verb, item)
			else:
				await main.say("Somebody wants to build something. In this town somebody always does.")
			Game.set_flag("saw_rezoning")

		"payphone":
			if item == "dime":
				if not Game.has_item("matchbook"):
					await main.say("A dime's no good without a number to call.")
				else:
					await _phone_call()
			elif item != "":
				await main.say("It takes dimes. Only dimes.")
			elif verb == "look":
				if Game.flag("looked_payphone"):
					await main.say("The last payphone in Hollywood. Somebody keeps paying the bill on it, and I'd like to know why.")
				else:
					await main.say("A payphone. Ten cents buys you thirty seconds of somebody's attention.")
					Game.set_flag("looked_payphone")
			elif Game.flag("knows_knock"):
				await main.say("I've made my call.")
			else:
				await main.player.play_action("use")
				await main.say("Dial tone. It wants a dime.")
				if not Game.has_item("dime"):
					await main.say("There's always loose change back in the squad room. Usually at the bottom of something.")

		"trash_can":
			if verb == "look":
				await main.say("A dumpster at the mouth of the alley, where they found Danny.")
				if not Game.flag("got_matchbook"):
					await main.say("Something blue is caught under the lid.")
			elif item != "":
				await default_response(verb, item)
			elif not Game.flag("got_matchbook"):
				await main.player.play_action("pickup")
				await main.say("A matchbook from the Blue Note. Wet, but readable.")
				Game.set_flag("got_matchbook")
				await main.give("matchbook", false)
				await main.say("There's a phone number written inside. In a hurry.")
			else:
				await main.say("Just garbage now. The uniforms missed the good stuff.")

		"alley":
			await main.say("Where Danny Reyes stopped being a piano player and started being a case.")

		"streetlamp":
			await main.say("Sodium light. Makes everybody look guilty. Saves time.")

		"car":
			if verb == "look":
				await main.say("My car. Unmarked, if you don't count the dents.")
			elif item != "":
				await default_response(verb, item)
			elif not Game.flag("talked_to_sal"):
				await main.say("Not leaving until I've talked to Sal.")
			else:
				await main.say("Pier 9. San Pedro. Forty minutes if the 110 behaves.")
				await _drive_south()

		"hydrant":
			await main.say("A fire hydrant. Ticket bait.")

		"billboard":
			await main.say("SUNSET INJURY LAW. In this town even the lawyers work the night shift.")

		"precinct_sign":
			await main.say("POLICE. They put it in big letters in case anyone forgets.")

		"bar_window":
			if verb == "look":
				await main.say("Lights on, chairs up, one silhouette at the bar. Closed, they'd tell you.")
			else:
				await main.say("Tapping on the glass gets you a look, not an answer.")

		_:
			await default_response(verb, item)


func _phone_call() -> void:
	var phone_pos := Vector2(785, 500)
	await main.player.play_action("use")
	main.take("dime")
	await main.say("555-0147...")
	await main.wait(0.6)
	await main.voice("...Yeah?", phone_pos, NINA_COLOR)
	var asked := false      # past "I'm calling about Danny Reyes"
	while true:
		if not asked:
			var c: int = await main.choose(["Is this Sal?", "I'm calling about Danny Reyes.", "Wrong number. Sorry."])
			if c == 0:
				await main.say("Is this Sal?")
				await main.voice("Sal don't take calls. Who's asking?", phone_pos, NINA_COLOR)
			elif c == 1:
				await main.say("I'm calling about Danny Reyes.")
				await main.voice("...Danny was a good kid. Owed the wrong people.", phone_pos, NINA_COLOR)
				await main.voice("You a friend of his?", phone_pos, NINA_COLOR)
				asked = true
			else:
				await main.say("Wrong number. Sorry.")
				await main.voice("*click*", phone_pos, NINA_COLOR)
				await main.say("There goes my dime. I'll need another one.")
				await main.say("...Actually, I won't. I'm not paying twice for that kind of manners.")
				break
		else:
			var opts := ["How do I get Sal to open the door?", "Never mind."]
			if not Game.flag("met_nina"):
				opts.push_front("Who am I talking to?")
			var c: int = await main.choose(opts)
			var pick: String = opts[c]
			if pick == "Who am I talking to?":
				await main.say("Who am I talking to?")
				await main.voice("Nina. I wait tables at the Note. Waited.", phone_pos, NINA_COLOR)
				await main.voice("I was his girl. Whatever that means now.", phone_pos, NINA_COLOR)
				await main.say("I'm sorry, Nina. Ray Kessler. I work Homicide.")
				await main.voice("Then you're two days late, Ray Kessler.", phone_pos, NINA_COLOR)
				Game.set_flag("met_nina")
			elif pick == "How do I get Sal to open the door?":
				await main.say("How do I get Sal to open the door?")
				await main.voice("Friends of Danny knock like Danny played. Two slow, three fast.", phone_pos, NINA_COLOR)
				if Game.flag("met_nina"):
					await main.voice("Sal's scared, Detective. Don't make me sorry I told you.", phone_pos, NINA_COLOR)
				await main.voice("*click*", phone_pos, NINA_COLOR)
				Game.set_flag("knows_knock")
				await main.say("Two slow, three fast. Like a piano man.")
				main.clue("clue_knock")
				break
			else:
				await main.say("Never mind.")
				await main.voice("*click*", phone_pos, NINA_COLOR)
				break
	if not Game.flag("knows_knock"):
		# the call can't be lost: the phone coughs the dime back up
		await main.say("The phone coughs my dime back up. Small mercies.")
		await main.give("dime", false)


func _talk_to_sal() -> void:
	var door := Vector2(496, 490)
	await main.player.play_action("use")
	await main.say("*knock... knock... knockknockknock*")
	await main.wait(0.9)
	await main.voice("...Danny's knock. Who is this?", door, SAL_COLOR)
	var asked := []
	while true:
		var opts := []
		var keys := []
		if not asked.has("cop"):
			opts.append("Police. Open the door, Sal."); keys.append("cop")
		if not asked.has("friend"):
			opts.append("A friend of Danny's."); keys.append("friend")
		opts.append("Who did Danny owe money to?"); keys.append("owed")
		if not asked.has("saw"):
			opts.append("Did you see who shot him?"); keys.append("saw")
		var c: int = await main.choose(opts)
		var k: String = keys[c]
		asked.append(k)
		match k:
			"cop":
				await main.say("Police. Open the door, Sal.")
				await main.voice("Cops don't know that knock. Somebody gave it to you.", door, SAL_COLOR)
				await main.voice("Door stays shut. Talk through it.", door, SAL_COLOR)
			"friend":
				await main.say("A friend of Danny's.")
				await main.voice("Danny didn't have friends. He had a piano and a tab.", door, SAL_COLOR)
			"saw":
				await main.say("Did you see who shot him?")
				await main.voice("I was counting the till. One shot. When I looked out the back, there was only Danny and the rain.", door, SAL_COLOR)
				await main.say("You told the uniforms you didn't hear anything.")
				await main.voice("I told the uniforms what they wanted to write down.", door, SAL_COLOR)
			"owed":
				await main.say("Who did Danny owe money to?")
				await main.voice("...", door, SAL_COLOR)
				await main.voice("A man named Vance. Vance doesn't send letters, if you follow me.", door, SAL_COLOR)
				await main.say("Where do I find Vance?")
				await main.voice("Pier 9. Warehouse with the green door.", door, SAL_COLOR)
				await main.voice("Who gave you the knock?", door, SAL_COLOR)
				await main.wait(0.5)
				await main.voice("Nina. Had to be.", door, SAL_COLOR)
				await main.voice("Three people alive know that knock now. Her, me, and you. Keep it that way.", door, SAL_COLOR)
				await main.voice("And you didn't hear it from me. You never heard me at all.", door, SAL_COLOR)
				await main.player.play_action("notebook")
				await main.say("Pier 9. Vance. Green door.")
				Game.set_flag("talked_to_sal")
				main.clue("clue_vance")
				await main.say("Sal saw something after all. They always do.")
				return


func _drive_south() -> void:
	## Scene 3: the 110 south, and a text from Maya.
	await main.drive_begin()
	await main.wait(1.0)
	await main.narrate("The 110 at one in the morning. Trucks, cabs, and people who don't want to go home.")
	await main.wait(0.6)
	await main.text_message("is it raining there too", false, "Maya")
	await main.text_message("It's LA. It only rains when I'm working.", true)
	await main.text_message("so always", false)
	await main.narrate("She's got her mother's timing. And my hours.")
	await main.wait(0.5)
	await main.drive_end()
	await main.change_room("pier9_dock", "street")
