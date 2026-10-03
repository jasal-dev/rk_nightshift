extends Room
## Homicide squad room, Room 214. Start of Case 1 and the hub Ray comes back to.
## Scene 1: lamp -> key -> filing cabinet -> Reyes file (needed to leave).
##          mug -> cold coffee -> pour into wastebasket -> dime. Doyle's voicemail on the desk phone.
## Scene 7 (back from Pier 9 with the envelope): the deduction at the murder board, the call to
##          Doyle, then Otis rings with Case 2.

const DOYLE_COLOR := Color(0.7, 0.85, 1.0)
const OTIS_COLOR := Color(1.0, 0.85, 0.5)
const PHONE_AT := Vector2(1010, 560)

## Murder board evidence cards: [id, card text, Ray's line when it's pinned wrongly ("" = correct)].
## An id is an inventory item or a notebook clue; only the ones Ray has found are offered.
const EVIDENCE := [
	["envelope", "Envelope, \"1 of 3\"", ""],
	["clue_wallet_phone", "Wallet left, phone gone", ""],
	["clue_paid", "Paid in full, $8,000",
		"That says he had money. What says there was more coming, and what the killer wanted instead?"],
	["clue_38", "Shot once, .38, close range", "The gun tells me how. I need why."],
	["clue_alibi", "Vance was in Avalon", "That clears Vance. It doesn't tell me why Danny died."],
	["clue_knock", "Danny's knock", "That's how I got through a door, not why he's dead."],
	["clue_vance", "Vance, Pier 9, green door", "That's where I went, not what I found."],
	["matchbook", "Matchbook, 555-0147", "A phone number. Nina's, it turns out. Not a motive."],
]

@onready var mug: Sprite2D = $Mug


func _ready() -> void:
	super._ready()
	_sync()


func _sync() -> void:
	mug.visible = not Game.flag("took_mug")
	var hs := hotspot("mug")
	if hs:
		hs.enabled = mug.visible


func _back_from_pier() -> bool:
	## Scene 7: Ray is back with the envelope and hasn't reported to Doyle yet.
	return Game.flag("got_envelope") and not Game.flag("case1_done")


func on_enter(_from_room: String) -> void:
	if _back_from_pier() and not Game.flag("back_in_214"):
		Game.set_flag("back_in_214")
		await main.say("Room 214. The coffee's still bad, and Danny's still in the middle of the board.")


func intro() -> void:
	await main.wait(0.4)
	await main.say("Quarter past midnight. The squad room is mine again.")
	await main.say("Danny Reyes. Two nights cold, and the lieutenant wants it closed by Friday.")
	await main.say("First, the file. I locked it away like a careful man.")
	await main.say("Then I hid the key like a paranoid one.")


func interact(hs: Hotspot, verb: String, item: String) -> void:
	match hs.id:
		"door":
			if verb == "look":
				await main.say("HOMICIDE. Room 214." if _back_from_pier() else "HOMICIDE. Room 214. Home sweet home.")
			elif item != "":
				await main.say("The door's not locked. My problems are.")
			elif _back_from_pier():
				await main.say("Not yet. Danny's waiting on the board.")
			elif not Game.has_item("case_file"):
				await main.say("Not without the Reyes file.")
			else:
				await main.say("Let's go see what the Blue Note didn't see.")
				await main.change_room("street", "squad_room")

		"coat_rack":
			if verb == "look":
				await main.say("My raincoat. Twenty years old and it still leaks at the collar.")
			else:
				await main.say("It's raining out. I'll be wet either way.")

		"case_board":
			if Game.flag("case1_deduced"):
				if verb == "look":
					await main.say("Danny's in the middle. Everything I know is on that board, and it isn't enough.")
				else:
					await main.say("Danny, the envelope, and a question mark. It's a start.")
			elif _back_from_pier():
				if verb == "look":
					await main.say("Danny's in the middle. Everything I know is on that board, and it isn't enough.")
				elif item == "" or item == "envelope":
					await _deduction(item == "envelope")
				else:
					await main.say("Pinning that up won't solve anything.")
			elif verb == "look" or item == "":
				await main.say("The murder board. Every case up there has a name. Most have a face.")
				await main.say("Reyes is the one in the middle. String leads to the Blue Note.")
			else:
				await main.say("Pinning that up won't solve anything.")

		"lamp":
			if verb == "look":
				await main.say("Green banker's lamp. Older than half the squad.")
				if not Game.flag("got_key"):
					await main.say("The base sits a little crooked.")
			elif item != "":
				await default_response(verb, item)
			elif not Game.flag("got_key"):
				await main.player.play_action("use")
				await main.say("Old habit. Tape a key under the lamp base, where nobody looks.")
				Game.set_flag("got_key")
				await main.give("key", false)
			else:
				await main.say("Nothing else under there but dust.")

		"typewriter":
			if verb == "look":
				await main.say("Department computer. It takes four passwords to tell me nothing.")
			else:
				await main.say("Reyes, Daniel. No priors, no warrants, no next of kin who'll pick up.")
				await main.say("The report can wait. The report can always wait.")

		"phone":
			if verb == "look":
				await main.say("The desk phone. It only rings when someone's dead.")
				if not Game.flag("heard_voicemail") and not _back_from_pier():
					await main.say("The message light is blinking.")
			elif item != "":
				await default_response(verb, item)
			elif _back_from_pier():
				if Game.flag("case1_deduced"):
					await _call_doyle()
				else:
					await main.say("Not until I know what I'm telling her.")
			elif not Game.flag("heard_voicemail"):
				await _voicemail()
			else:
				await main.say("Nobody I want to call at this hour.")

		"mug":
			if verb == "look":
				await main.say("My coffee. Made at six. It's past midnight now.")
			else:
				await main.say("Waste not.")
				await main.player.play_action("pickup")
				Game.set_flag("took_mug")
				_sync()
				await main.give("coffee", false)

		"desk":
			if verb == "look":
				await main.say("My desk. Government issue, scarred by three chiefs and a budget freeze.")
			else:
				await main.say("Old reports and older sandwiches. Nothing for Reyes.")

		"wastebasket":
			if item == "coffee":
				await main.player.play_action("use")
				await main.say("Down the hatch. Somebody else's hatch.")
				main.take("coffee")
				await main.say("Well. There's a dime at the bottom of the mug.")
				await main.give("dime", false)
				Game.set_flag("found_dime")
			elif verb == "look":
				await main.say("The wastebasket. Where most of my theories end up.")
			else:
				await main.say("I'm not digging through that again.")

		"cabinet":
			if item == "key":
				await main.player.play_action("use")
				await main.say("Second drawer. Reyes, Daniel.")
				main.take("key")
				Game.set_flag("cabinet_open")
				await main.give("case_file", false)
				await main.say("I should read it before I go anywhere. Right-click it in the inventory.")
			elif verb == "look":
				if Game.flag("cabinet_open"):
					await main.say("Open files and closed cases. Should be the other way around.")
				else:
					await main.say("The filing cabinet. Locked. I keep the key somewhere clever.")
			elif Game.flag("cabinet_open"):
				await main.say("I've got what I need from it.")
			else:
				await main.say("Locked. I'm the one who locked it, too.")

		"window":
			if verb == "look":
				await main.say("Four million people out there. One of them killed Danny Reyes.")
			else:
				await main.say("Painted shut. The blinds are the only thing in here that opens.")

		"clock":
			if _back_from_pier():
				await main.say("One twenty-five. The city's second shift is half over and I've got one envelope to show for it.")
			else:
				await main.say("Twelve-fifteen. The city's second shift.")

		"radiator":
			if verb == "look":
				await main.say("It clanks all night, like a drunk in the cells.")
			else:
				await main.say("Hot enough to brand a man. I'll pass.")

		"coffee_machine":
			if item == "coffee":
				await main.say("Reheating it won't make it coffee.")
			elif verb == "look":
				await main.say("The squad's coffee machine. It makes something brown and hot. Usually.")
			else:
				await main.say("Out of filters since March. Nobody's filed the requisition.")

		_:
			await default_response(verb, item)


# --- scene 1: Doyle's voicemail ---------------------------------------------------
func _voicemail() -> void:
	await main.player.play_action("use")
	Game.set_flag("heard_voicemail")
	await main.voice("*beep* Ray, it's Doyle. Eleven-forty. I've got the captain asking about Reyes.", PHONE_AT, DOYLE_COLOR)
	await main.voice("It's a gambling debt and a .38 in an alley, it's not the Black Dahlia. Get me a name by Friday.", PHONE_AT, DOYLE_COLOR)
	await main.wait(0.4)
	await main.voice("And answer your cell once in a while. *beep*", PHONE_AT, DOYLE_COLOR)
	await main.say("My cell is in my coat. My coat is wet. We all have problems.")


# --- scene 7: the deduction -----------------------------------------------------
func _deduction(envelope_first: bool) -> void:
	if not Game.flag("read_file"):
		await main.say("Let me go over the file once more.")
		await main.examine_item("case_file")
	main.ui.show_board("Two nights, one bullet, one piano player. Why?")
	await main.narrate("Two nights, one bullet, one piano player. Why?")
	# step 1: the question (wrong answers just get a line from Ray; pick again)
	while true:
		var c: int = await main.choose(["Over the money he owed Vance.", "A street robbery gone wrong.",
				"For something he had.", "(Step back from the board)"])
		if c == 0:
			if Game.flag("clue_paid"):
				await main.narrate("Vance doesn't shoot paying customers, and Danny had paid.")
			else:
				await main.narrate("I haven't proved that. Doyle would love it if I had.")
		elif c == 1:
			await main.narrate("A robber who leaves the wallet. Worst robber in Hollywood.")
		elif c == 2:
			await main.narrate("Not what he owed. What he had.")
			break
		else:
			main.ui.hide_board()
			return
	# step 2: two pieces of evidence. A right card stays pinned; a wrong one gets Ray's line and comes down.
	main.ui.set_board_question("Not what he owed. What he had. Pin up what proves it.")
	var pins: Array[String] = []
	if envelope_first:
		pins.append("envelope")
	var wrong_tries := 0
	while true:
		main.ui.set_board_pins(_pin_texts(pins))
		while pins.size() < 2:
			var ids := _available_evidence(pins)
			var opts: Array = []
			for id in ids:
				opts.append(_card(id)[1])
			opts.append("(Step back from the board)")
			var c: int = await main.choose(opts)
			if c == ids.size():
				main.ui.hide_board()
				return
			pins.append(ids[c])
			main.ui.set_board_pins(_pin_texts(pins))
		var keep: Array[String] = []
		for id in pins:
			var line: String = _card(id)[2]
			if line == "":
				keep.append(id)
			else:
				await main.narrate(line)
		if keep.size() == 2:
			break
		pins = keep
		wrong_tries += 1
		if wrong_tries == 3:
			await main.narrate("Think, Ray. What did the killer leave behind, and what did he take? And who still owed Danny?")
	# solved: the envelope goes up next to Danny's photo, with a string to a question mark
	main.ui.set_board_question("REYES, D.  -  OPEN")
	main.ui.set_board_pins(["Envelope, \"1 of 3\"", "?"])
	await main.wait(0.6)
	await main.narrate("Danny wasn't killed for what he owed. He was killed for what he had.")
	await main.narrate("Somebody paid a broke piano player eight grand and promised two more. Then they stopped paying.")
	Game.set_flag("case1_deduced")
	Game.set_flag("board_envelope")
	main.ui.hide_board()
	await main.say("Case stays open. I should tell the lieutenant. She'll want to hear it's not closed.")
	await main.say("She won't like hearing it.")


func _card(id: String) -> Array:
	for e: Array in EVIDENCE:
		if e[0] == id:
			return e
	return [id, id, ""]


func _available_evidence(exclude: Array[String]) -> Array[String]:
	## Cards Ray has actually found: items he carries and clues in his notebook.
	var out: Array[String] = []
	for e: Array in EVIDENCE:
		var id: String = e[0]
		if exclude.has(id):
			continue
		if Game.has_item(id) or (id.begins_with("clue_") and Game.flag(id)):
			out.append(id)
	return out


func _pin_texts(pins: Array[String]) -> Array:
	var out := []
	for id in pins:
		out.append(_card(id)[1])
	return out


# --- scene 7: the call to Doyle, then Otis with the next case ----------------------------
func _call_doyle() -> void:
	# No branches on purpose: Case 5 depends on Ray telling Doyle about Sal, Nina and the knock.
	await main.player.play_action("use")
	await main.wait(0.8)
	await main.voice("Doyle.", PHONE_AT, DOYLE_COLOR)
	await main.say("It's Kessler. Reyes isn't a debt killing.")
	await main.voice("Ray, it's one-thirty.", PHONE_AT, DOYLE_COLOR)
	await main.say("Danny paid Vance off in full the afternoon he died. Eight thousand, cash.")
	await main.say("Vance was on his boat on Catalina.")
	await main.voice("So the loan shark has a boat. Congratulations. Where'd you even get Vance?", PHONE_AT, DOYLE_COLOR)
	await main.say("Sal Moretti. The bartender.")
	await main.voice("Moretti told the uniforms he was blind and deaf.", PHONE_AT, DOYLE_COLOR)
	await main.say("He talks through his door if you knock right. Danny's knock. His girl, Nina, gave it to me.")
	await main.voice("(muffled) Thanks, Walt. Black is fine.", PHONE_AT, DOYLE_COLOR.darkened(0.3))
	await main.voice("Sorry. Ray, I have the captain on Friday and a dead piano player who paid his bills.", PHONE_AT, DOYLE_COLOR)
	await main.voice("That's not a lead, that's a eulogy.", PHONE_AT, DOYLE_COLOR)
	await main.say("It's a motive. Somebody gave a broke man eight grand, and he was expecting more.")
	await main.voice("Then write it up. And stop wasting the night on one case. Otis has a stack. *click*", PHONE_AT, DOYLE_COLOR)
	await main.say("Wasting the night. That's what nights are for.")
	Game.set_flag("told_doyle")
	await main.wait(0.7)
	await main.voice("*RIIING*", PHONE_AT, Color.WHITE)
	await main.player.play_action("use")
	await main.voice("Ray, it's Otis. Hope I'm not interrupting your social life.", PHONE_AT, OTIS_COLOR)
	await main.say("You're interrupting Danny Reyes.")
	await main.voice("Danny'll keep. I've got a rideshare driver dead behind the wheel up at the Mulholland overlook.", PHONE_AT, OTIS_COLOR)
	await main.voice("Engine still running. Patrol's holding it for you.", PHONE_AT, OTIS_COLOR)
	await main.say("On my way.")
	await main.voice("Bring a coat. It's windy up there.", PHONE_AT, OTIS_COLOR)
	await main.say("I've got a coat. It leaks.")
	Game.set_flag("case1_done")
	await main.end_case("1:40 a.m.", "Case 2: Five Stars")
