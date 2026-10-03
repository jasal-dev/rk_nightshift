extends Room
## Pier 9, Port of Los Angeles (Case 1, scenes 4 and 6).
## Scene 4: show Tiny the matchbook (he drank at the Blue Note), then knock Danny's knock on the
##          green door and Vance lets Ray in.
## Scene 6: after Vance mentions the envelope, fish it out of the burn barrel with the boat hook.
## The car drives back to the squad room once Ray has the envelope.

const TINY_COLOR := Color(0.86, 0.74, 0.56)
const VANCE_COLOR := Color(0.78, 0.74, 0.9)
const TINY_AT := Vector2(1240, 610)
const DOOR_AT := Vector2(1098, 540)

@onready var hook: Sprite2D = $Hook
var _fails := 0          ## knocked too early or flashed the badge (two of these earn a hint)
var _wander := 0         ## actions since Tiny softened without trying the door


func _ready() -> void:
	super._ready()
	add_rain(420)
	_sync()


func _sync() -> void:
	hook.visible = not Game.has_item("gaff")


func on_enter(from_room: String) -> void:
	if from_room == "street" and not Game.flag("pier_arrived"):
		Game.set_flag("pier_arrived")
		await main.say("Pier 9. The ocean smells like diesel and money.")
		await main.say("Green door. And a man the size of the door in front of it.")
	elif from_room == "vance_office" and Game.flag("knows_envelope") and not Game.flag("said_barrel_line"):
		Game.set_flag("said_barrel_line")
		await main.say("Tiny burns the trash every night. Lucky for me it rains every night too.")


func interact(hs: Hotspot, verb: String, item: String) -> void:
	if hs.id != "green_door":
		await _maybe_hint()
	match hs.id:
		"tiny":
			await _tiny(verb, item)

		"green_door":
			if verb == "look":
				await main.say("A steel door, painted green a long time ago. Sal was right.")
			elif item != "":
				await main.say("I'd rather knock.")
			elif Game.flag("in_vance_office"):
				await main.say("Tiny waves me through.")
				await main.change_room("vance_office", "pier9_dock")
			elif not Game.flag("tiny_softened"):
				await main.voice("Knock on that door and you'll be knocking with your teeth.", TINY_AT, TINY_COLOR)
				await main.walk(main.player.position + Vector2(-90, 40))
				await _failed()
			else:
				await _knock()

		"radio":
			if verb == "look":
				await main.say("A transistor radio. Somebody's playing Monk. Danny played it better, I'd bet.")
			elif item != "":
				await default_response(verb, item)
			else:
				await main.say("Not my radio. Not my music, either, these days.")

		"barrel":
			if verb == "look":
				await main.say("A burn barrel. The rain's winning; it only smolders.")
			elif item == "gaff":
				if not Game.flag("knows_envelope"):
					await main.say("Nothing in there I want. Yet.")
				elif Game.flag("got_envelope"):
					await main.say("Nothing else in there but fish heads.")
				else:
					await _fish_envelope()
			elif item != "":
				await default_response(verb, item)
			elif not Game.flag("knows_envelope"):
				await main.say("Warming my hands over Vance's garbage isn't detective work.")
			elif Game.flag("got_envelope"):
				await main.say("Nothing else in there but fish heads.")
			else:
				await main.say("Wet ash, fish heads, and whatever Tiny had for dinner. Not with my hand.")
				await main.say("I need something with reach.")

		"piling":
			if verb == "look":
				if hook.visible:
					await main.say("A boat hook hung on a piling. Every pier has one, and they're never where they belong.")
				else:
					await main.say("A piling with a nail in it. The boat hook's with me.")
			elif item == "gaff":
				await main.player.play_action("use")
				main.take("gaff")
				_sync()
				await main.say("Back on its nail.")
			elif item != "":
				await default_response(verb, item)
			elif Game.has_item("gaff"):
				await main.say("I've already got the hook.")
			else:
				await main.player.play_action("pickup")
				await main.give("gaff", false)
				_sync()
				await main.voice("Bring that back when you're done.", TINY_AT, TINY_COLOR)

		"containers":
			if verb == "look":
				await main.say("Forty-foot boxes from Busan and Shenzhen. Anything can be in them, and usually is.")
			else:
				await main.say("Sealed. Customs gets the fun.")

		"crane":
			await main.say("A gantry crane, blinking red at the top like it's got somewhere to be.")

		"warehouse_sign":
			await main.say("HARBOR MARINE SALVAGE. They salvage people, mostly.")

		"water":
			if item != "":
				await main.say("I might need that. The harbor doesn't.")
			elif verb == "look":
				await main.say("Black water. Whatever goes in here doesn't come back up. Not in this harbor.")
			else:
				await main.say("Not tonight.")

		"car":
			if verb == "look":
				await main.say("Still dented. Now wet and dented.")
			elif item != "":
				await default_response(verb, item)
			elif not Game.flag("in_vance_office"):
				await main.say("Not until I've talked to Vance.")
			elif not Game.has_item("envelope"):
				await main.say("Not without that envelope.")
			else:
				await main.say("Back to the board. Danny's got a new piece of paper on it.")
				await main.drive_begin()
				await main.wait(6.0)
				await main.drive_end()
				await main.change_room("squad_room", "street")

		_:
			await default_response(verb, item)


# --- Tiny -----------------------------------------------------------------------
func _tiny(verb: String, item: String) -> void:
	if verb == "look":
		await main.say("Six-five, maybe more. Built like a vending machine.")
		if not Game.flag("tiny_softened"):
			await main.say("There's a Blue Note cocktail napkin folded in his breast pocket.")
		return
	match item:
		"":
			pass
		"matchbook":
			if Game.flag("tiny_softened"):
				await main.say("He's seen it. Once was enough.")
			else:
				await _show_matchbook()
			return
		"case_file":
			await main.say("He's not going to read it.")
			return
		"dime":
			await main.say("Tiny doesn't look like a man who takes tips.")
			return
		_:
			await default_response(verb, item)
			return
	if Game.flag("got_envelope"):
		await main.voice("You find who did Danny, you come tell me.", TINY_AT, TINY_COLOR)
	elif Game.flag("knows_envelope"):
		if Game.has_item("gaff"):
			await main.voice("Bring that back when you're done.", TINY_AT, TINY_COLOR)
		else:
			await main.voice("Boat hook's on the piling. Bring it back after.", TINY_AT, TINY_COLOR)
	elif Game.flag("in_vance_office"):
		await main.say("Five minutes, he said. Tiny looks like a man who counts.")
	else:
		await _talk_to_tiny()


func _talk_to_tiny() -> void:
	if not Game.flag("met_tiny"):
		Game.set_flag("met_tiny")
		await main.voice("We're closed.", TINY_AT, TINY_COLOR)
		await main.say("I didn't see a sign.")
		await main.voice("I'm the sign.", TINY_AT, TINY_COLOR)
	while true:
		var c: int = await main.choose(["I need to see Vance.", "LAPD.", "Nice radio.", "Never mind."])
		match c:
			0:
				await main.say("I need to see Vance.")
				await main.voice("Mr. Vance doesn't see people at night. Mr. Vance doesn't see people in the day, either.", TINY_AT, TINY_COLOR)
			1:
				await main.say("LAPD.")
				await main.player.play_action("badge")
				await main.voice("A badge gets you a lawyer, not a door. Come back with paper.", TINY_AT, TINY_COLOR)
				await _failed()
			2:
				await main.say("Nice radio.")
				await main.voice("KJAZZ. Only station that still plays piano after midnight.", TINY_AT, TINY_COLOR)
				await main.wait(0.4)
				await main.voice("Used to be I didn't need a radio for that.", TINY_AT, TINY_COLOR)
			3:
				await main.say("Never mind.")
				return


func _show_matchbook() -> void:
	await main.player.play_action("use")
	await main.say("You drink at the Blue Note.")
	await main.wait(1.2)
	await main.voice("Thursdays. Kid used to play 'Round Midnight' for me without me asking.", TINY_AT, TINY_COLOR)
	await main.voice("Danny. Somebody put him down in that alley like a dog.", TINY_AT, TINY_COLOR)
	await main.say("That's why I'm here.")
	await main.voice("Still can't let you in. Mr. Vance only opens up for people who've been here before.", TINY_AT, TINY_COLOR)
	await main.say("People who've been here before. People who knock like they've been here before.")
	Game.set_flag("tiny_softened")


func _failed() -> void:
	_fails += 1
	if _fails == 2 and not Game.flag("tiny_softened"):
		await main.say("Badges don't move him. Maybe something from the Blue Note would.")


func _maybe_hint() -> void:
	## After the matchbook, if the player wanders: point at the door.
	if not Game.flag("tiny_softened") or Game.flag("in_vance_office") or Game.flag("door_hint"):
		return
	_wander += 1
	if _wander >= 4:
		Game.set_flag("door_hint")
		await main.say("Danny knocked on Sal's door. He must have knocked on this one too.")


func _knock() -> void:
	await main.player.play_action("use")
	await main.say("*knock... knock... knockknockknock*")
	await main.wait(0.8)
	await main.voice("...That's Danny's knock. He came every Tuesday to pay.", TINY_AT, TINY_COLOR)
	await main.voice("Knocked like that every time, like he was playing it.", TINY_AT, TINY_COLOR)
	await main.voice("Tiny? Who is it?", DOOR_AT, VANCE_COLOR)
	await main.voice("(low) Five minutes.", TINY_AT, TINY_COLOR)
	await main.voice("Friend of Danny's, Mr. Vance.", TINY_AT, TINY_COLOR)
	Game.set_flag("in_vance_office")
	await main.change_room("vance_office", "pier9_dock")


# --- scene 6: the envelope in the burn barrel ---------------------------------------
func _fish_envelope() -> void:
	await main.player.play_action("use")
	await main.wait(0.6)
	await main.say("Blue Note envelope. Singed at one corner, soaked through, but the back survived.")
	await main.say("Danny's handwriting. Two words. \"1 of 3.\"")
	await main.give("envelope", false)
	Game.set_flag("got_envelope")
	await main.say("One of three. One of three what?")
	# hang the boat hook back where it lives
	await main.walk(hotspot("piling").walk_to)
	main.player.face("right")
	await main.player.play_action("use")
	main.take("gaff")
	_sync()
	await main.voice("Detective. You find who did Danny, you come tell me. I want to hear it from somebody.", TINY_AT, TINY_COLOR)
	await main.say("You'll hear it.")
