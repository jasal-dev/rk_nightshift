extends Room
## Homicide squad room, Room 214. Start of Case 1 and the hub Ray comes back to.
## Scene 1: lamp -> key -> filing cabinet -> Reyes file (needed to leave).
##          mug -> cold coffee -> pour into wastebasket -> dime. Doyle's voicemail on the desk phone.
## Scene 7 (back from Pier 9 with the envelope): the deduction at the murder board, the call to
##          Doyle, then Otis rings with Case 2, and Ray drives up to Mulholland.
## Case 2, scene 5 (back with Devin in custody): the deduction for Kenji, Doyle's call, then Otis with Case 3.
## Case 3, scene 6 (back from Stardust with Pearl arrested): the deduction for Gus, Brenner's card pinned if Ray found it,
## Doyle's call, then Otis with Case 4, and Ray drives to the river.
## Case 4, scene 7 (back from the lab with Crane arrested and Danny's phone with Ike): the deduction for Owen, the lab
## receipt pinned beside Danny (and Pryce's invitation if Ray found it), Doyle's call, then Otis: Sal is dead. Case 5's card.
## Case 5, scenes 4 and 6 (Sal Moretti): the desk phone's call log and the phone list put Nina's police number on
## Doyle's desk; the 1:30 call remembered at the board; Otis's visitor log names Walt Brenner, then Doyle calls and Ike
## calls. Back with the take: the last deduction, Danny's box, Harbor Marine and Otis's car, and the text to Walt.
## The board keeps its pins between cases (overlays shown by flag); once Danny's box is packed its middle is bare.

const DOYLE_COLOR := Color(0.7, 0.85, 1.0)
const OTIS_COLOR := Color(1.0, 0.85, 0.5)
const PHONE_AT := Vector2(860, 630)

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

@onready var mug: Sprite2D = $Actors/Mug
@onready var pin_envelope: Sprite2D = $Board_envelope
@onready var pin_kenji: Sprite2D = $Board_kenji
@onready var pin_receipt: Sprite2D = $Board_receipt
@onready var pin_gus: Sprite2D = $Board_gus
@onready var pin_brenner: Sprite2D = $Board_brenner
@onready var pin_owen: Sprite2D = $Board_owen
@onready var pin_phone: Sprite2D = $Board_phone
@onready var pin_invite: Sprite2D = $Board_invite
@onready var pin_walt: Sprite2D = $Board_walt
@onready var pin_string: Sprite2D = $Board_string
@onready var pin_empty: Sprite2D = $Board_empty


func _ready() -> void:
	super._ready()
	_sync()


func _sync() -> void:
	mug.visible = not Game.flag("took_mug")
	var hs := hotspot("mug")
	if hs:
		hs.enabled = mug.visible
	pin_envelope.visible = Game.flag("board_envelope")
	pin_kenji.visible = Game.flag("case2_deduced")
	pin_receipt.visible = Game.flag("board_ride_receipt")
	pin_gus.visible = Game.flag("case3_deduced")
	pin_brenner.visible = Game.flag("board_brenner_card")
	pin_owen.visible = Game.flag("case4_deduced")
	pin_phone.visible = Game.flag("board_danny_phone")
	pin_invite.visible = Game.flag("board_pryce_invite")
	pin_walt.visible = Game.flag("case5_deduced")
	pin_string.visible = Game.flag("board_string")
	# Danny's box: the middle of the board comes down and goes into it
	var packed := Game.flag("got_danny_box")
	pin_empty.visible = packed
	for pin: Sprite2D in [pin_envelope, pin_receipt, pin_brenner, pin_phone, pin_invite, pin_walt, pin_string]:
		pin.visible = pin.visible and not packed
	var pl := hotspot("phone_list")
	if pl:
		pl.enabled = _case5()


func _back_from_pier() -> bool:
	## Scene 7: Ray is back with the envelope and hasn't reported to Doyle yet.
	return Game.flag("got_envelope") and not Game.flag("case1_done")


func _case2() -> bool:
	## Case 2, scene 5: back from Silver Lake with Devin in custody.
	return Game.flag("devin_arrested") and not Game.flag("case2_done")


func _case3() -> bool:
	## Case 3, scene 6: back from Hollywood Boulevard with Pearl Danvers arrested.
	return Game.flag("pearl_arrested") and not Game.flag("case3_done")


func _case4() -> bool:
	## Case 4, scene 7: back from the lab, Crane in custody and Danny's phone with Ike.
	return Game.flag("phone_at_lab") and not Game.flag("case4_done")


func _case5() -> bool:
	## Case 5, scenes 4 and 6: Sal Moretti, until Ray drives to the pier.
	return Game.flag("case4_done")


func on_enter(_from_room: String) -> void:
	if _back_from_pier() and not Game.flag("back_in_214"):
		Game.set_flag("back_in_214")
		await main.say("Room 214. The coffee's still bad, and Danny's still in the middle of the board.")
	elif _case2() and not Game.flag("back_in_214_case2"):
		Game.set_flag("back_in_214_case2")
		await main.say("Room 214. Danny's still in the middle of the board. Kenji gets a corner.")
	elif _case3() and not Game.flag("back_in_214_case3"):
		Game.set_flag("back_in_214_case3")
		await main.say("Room 214. Danny in the middle, Kenji in one corner. Gus gets the other.")
	elif _case4() and not Game.flag("back_in_214_case4"):
		Game.set_flag("back_in_214_case4")
		await main.say("Room 214. Kenji, Gus, and now Owen in the corners. Danny's still in the middle, waiting for somebody to notice him.")
	elif _case5() and Game.flag("heard_take") and not Game.flag("back_in_214_board"):
		Game.set_flag("back_in_214_board")
		await main.say("Room 214. Five hours ago I pinned an envelope next to Danny and drew a question mark. Time to fill it in.")
	elif _case5() and not Game.flag("back_in_214_case5"):
		Game.set_flag("back_in_214_case5")
		await main.say("Room 214. Whoever came for Sal knew he'd only open to Danny's knock. But he didn't know the knock. He had to call Nina for it.")
		await main.narrate("Danny knocked like that on Vance's door every Tuesday. Tiny and Vance had the rhythm and never needed to ask. This man had the rule and not the rhythm.")
		await main.narrate("I told somebody the rule. Who did I tell?")


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
				await main.say("HOMICIDE. Room 214." if _back_from_pier() or _case2() or _case3() or _case4()
						else "HOMICIDE. Room 214. Home sweet home.")
			elif item != "":
				await main.say("The door's not locked. My problems are.")
			elif _case5():
				if Game.flag("heard_take") and not Game.flag("case5_deduced"):
					await main.say("Not yet. The board first.")
				else:
					await main.change_room("street_crime", "squad_room")
			elif _case4():
				await main.say("Not yet. Owen's waiting on the board.")
			elif _case3():
				await main.say("Not yet. Gus is waiting on the board.")
			elif _case2():
				await main.say("Not yet. Kenji's waiting on the board.")
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
			if _case5():
				await _board5(verb, item)
			elif _case4():
				await _board4(verb, item)
			elif _case3():
				await _board3(verb, item)
			elif _case2():
				await _board2(verb, item)
			elif Game.flag("case1_deduced"):
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
				if not Game.flag("heard_voicemail") and not _back_from_pier() and not _case2() and not _case3() 						and not _case4():
					await main.say("The message light is blinking.")
			elif item != "":
				await default_response(verb, item)
			elif _case5():
				await _phone5()
			elif _case2() or _case3() or _case4():
				await main.say("Nothing to tell anybody yet.")
			elif _back_from_pier():
				if Game.flag("case1_deduced"):
					await _call_doyle()
				else:
					await main.say("Not until I know what I'm telling her.")
			elif not Game.flag("heard_voicemail"):
				await _voicemail()
			else:
				await main.say("Nobody I want to call at this hour.")

		"phone_list":
			if item != "":
				await default_response(verb, item)
			else:
				await _phone_list(verb)

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
			if _case5():
				await main.say("The sky's gone the color of a dirty dime. Sunrise in an hour." if Game.flag("heard_take")
						else "Gray over the parking lot. The rain's thinking about stopping.")
			elif verb == "look":
				await main.say("Four million people out there. One of them killed Danny Reyes.")
			else:
				await main.say("Painted shut. The blinds are the only thing in here that opens.")

		"clock":
			if _case5():
				await main.say("Five to six. Five minutes until I'm off shift. Then I'm a civilian with a badge." if Game.flag("heard_take")
						else "Twenty past five. Forty minutes until I'm supposed to go home.")
			elif _case4():
				await main.say("Ten to five. The sky over the parking lot is thinking about getting lighter.")
			elif _case3():
				await main.say("Quarter to four. The hour when even the coffee gives up.")
			elif _case2():
				await main.say("Two-forty. Two cases down, if you count one that won't close.")
			elif _back_from_pier():
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
	_sync()
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
	await main.case_card("1:40 a.m.", "Case 2: Five Stars")
	await Case2.drive_up(main)
	await main.change_room("mulholland_overlook", "drive")


func _board2(verb: String, item: String) -> void:
	if verb == "look":
		await main.say("Danny in the middle, Kenji in the corner. The board's getting crowded.")
	elif Game.flag("case2_deduced"):
		await main.say("Kenji's closed. Danny isn't.")
	elif item == "ride_receipt":
		await main.say("After Kenji.")
	elif item == "" or item == "sd_cards" or item == "card_slip":
		await _deduction2(item)
	else:
		await main.say("Pinning that up won't solve anything.")


# --- Case 2, scene 5: the deduction for Kenji ----------------------------------------------
## Case 2 evidence cards: [id, card text, slot it proves ("A" with Kenji tonight, "B" what he killed for,
## "" neither), Ray's line when it's pinned wrongly]. Cards from other cases aren't offered, except the
## photo of Walt B.'s ride, which only gets a line.
const EVIDENCE2 := [
	["card_slip", "Norm's card slip, \"D. Clark\", 12:14", "A", "That puts him at Norm's. What did he kill for?"],
	["clue_roommate_norms", "Rosa: the roommate with the camera bag", "A", "That puts him at Norm's. What did he kill for?"],
	["sd_cards", "Dashcam and memory cards, in the peas", "B", "That's what he took. First, who sat with Kenji?"],
	["clue_strap", "Devin's herringbone strap", "", "Half the photographers in LA own that strap. Put him in the car first."],
	["clue_walker", "Walker on Mulholland", "", "That's a man walking home. Show me him sitting down with Kenji."],
	["clue_sneakers", "Orange grit on his shoes", "", "That's a man walking home. Show me him sitting down with Kenji."],
	["norms_receipt", "Norm's receipt", "", "Two coffees and a pie. Which two people?"],
	["clue_off_app", "Off the app: someone he knew", "", "Kenji drove someone he knew. Which someone?"],
	["clue_kenji_quitting", "Kenji's note: giving Carla the cards", "", "That's why Kenji wanted out. What did Devin take home?"],
	["clue_napkin", "Booth 6 napkin, \"11 × 2,500\"", "", "Math on a napkin. Where's the thing the math was about?"],
	["clue_empty_case", "Empty card case in the glovebox", "", "An empty case. Where did the cards end up?"],
	["clue_ligature", "Strangled from behind, herringbone strap", "", "That's how. I need who was there and why."],
	["clue_tod", "Died between 1:00 and 1:15", "", "That's when. The when's not in doubt."],
	["clue_devin_story", "Devin: home all night", "", "That's his story. I'm pinning the truth."],
	["clue_brielle_alibi", "Brielle's video", "", "That clears somebody. I'm here to catch somebody."],
	["clue_heck_alibi", "Heck's alibi, the LAX queue", "", "That clears somebody. I'm here to catch somebody."],
	["clue_threat", "Heck's threat", "", "Heck says things in traffic. Devin did things."],
	["driver_card", "Kenji's driver card", "", "That's Kenji. He's already on the board."],
	["ride_receipt", "Photo of Walt B.'s ride, billed to Pryce Development", "", "That's Tuesday. A different night. Maybe a different case."],
]
const SLOT_LABELS := ["He was with Kenji tonight", "What he killed him for"]


func _deduction2(first: String) -> void:
	main.ui.show_board("Four point nine eight stars, and somebody gave him a zero. Who?", "KENJI OTA\n29. Glide driver")
	await main.narrate("Four point nine eight stars, and somebody gave him a zero. Who?")
	# step 1: the culprit (wrong picks get a line; pick again)
	while true:
		var c: int = await main.choose(["Brielle V., his last passenger.", "Heck Dominguez, the rival driver.",
				"A stranger he picked up off the app.", "Devin Clark, his roommate.", "(Step back from the board)"])
		match c:
			0:
				await main.narrate("Thirty-one thousand people watched her sing in a hot tub from twelve-twenty on. That's an alibi with a comment section.")
			1:
				if Game.flag("clue_heck_alibi"):
					await main.narrate("Heck was in the LAX lot with a hundred drivers and four cameras.")
				else:
					await main.narrate("Heck talks big. I never checked where he was, and the board wants proof, not a grudge.")
			2:
				await main.narrate("Off the app, home for two minutes, then pie? That's not a stranger. That's a friend.")
			3:
				await main.narrate("The one with the camera bag.")
				break
			_:
				main.ui.hide_board()
				return
	# step 2: two labeled slots. A right card stays pinned; a wrong one gets Ray's line and comes down.
	main.ui.set_board_question("Devin Clark. Pin up what proves it.")
	var pins: Array[String] = ["", ""]
	var pre := _card2(first)
	if first != "" and pre[2] != "":
		pins[0 if pre[2] == "A" else 1] = first
	var wrong_tries := 0
	while true:
		main.ui.set_board_pins(_pin_texts2(pins), SLOT_LABELS)
		for slot in 2:
			if pins[slot] != "":
				continue
			main.ui.set_board_question(SLOT_LABELS[slot] + ":")
			var ids := _available_evidence2(pins)
			var opts: Array = []
			for id in ids:
				opts.append(_card2(id)[1])
			opts.append("(Step back from the board)")
			var c: int = await main.choose(opts)
			if c == ids.size():
				main.ui.hide_board()
				return
			pins[slot] = ids[c]
			main.ui.set_board_pins(_pin_texts2(pins), SLOT_LABELS)
		var right := 0
		for slot in 2:
			var card := _card2(pins[slot])
			if card[2] == ("A" if slot == 0 else "B"):
				right += 1
			else:
				await main.narrate(card[3])
				pins[slot] = ""
		if right == 2:
			break
		wrong_tries += 1
		if wrong_tries == 3:
			await main.narrate("Think, Ray. Who sat with Kenji at midnight, and what did he carry home?")
	# solved: Kenji's corner of the board, and a line through the case
	main.ui.set_board_question("OTA, K.  -  CLOSED")
	await main.wait(0.6)
	await main.narrate("Devin Clark. Kenji wanted to give it back, and Devin wanted his half.")
	Game.set_flag("case2_deduced")
	main.ui.hide_board()
	_sync()
	if Game.flag("got_ride_receipt"):
		# no line, no music: the photo goes up at the edge of Danny's corner, near the envelope, no string
		await main.player.play_action("use")
		Game.set_flag("board_ride_receipt")
		_sync()
		await main.wait(1.0)
	await _calls2()


func _card2(id: String) -> Array:
	for e: Array in EVIDENCE2:
		if e[0] == id:
			return e
	return [id, id, "", ""]


func _available_evidence2(exclude: Array[String]) -> Array[String]:
	var out: Array[String] = []
	for e: Array in EVIDENCE2:
		var id: String = e[0]
		if exclude.has(id):
			continue
		if Game.has_item(id) or (id.begins_with("clue_") and Game.flag(id)):
			out.append(id)
	return out


func _pin_texts2(pins: Array[String]) -> Array:
	var out := []
	for id in pins:
		out.append("" if id == "" else _card2(id)[1])
	return out


# --- Case 2, scene 5: Doyle calls, then Otis with Case 3 -----------------------------------
func _calls2() -> void:
	# No branches: Case 5 throws "Everything closes eventually" back at Doyle.
	await main.wait(0.6)
	await main.voice("*RIIING*", PHONE_AT, Color.WHITE)
	await main.walk(hotspot("phone").walk_to)
	main.player.face("up")
	await main.player.play_action("use")
	await main.voice("Ray. Otis says you closed the rideshare in an hour.", PHONE_AT, DOYLE_COLOR)
	await main.say("The roommate. He's in a cell asking for a lawyer.")
	await main.voice("See? That's what closing feels like. Try it on Reyes.", PHONE_AT, DOYLE_COLOR)
	await main.say("Reyes isn't closed, Lieutenant.")
	await main.voice("Everything closes eventually, Ray. Goodnight. *click*", PHONE_AT, DOYLE_COLOR)
	await main.say("It's not night anymore. It's not morning yet, either. That's my shift.")
	await main.wait(0.8)
	await main.say("Two forty-five.")
	await main.voice("*RIIING*", PHONE_AT, Color.WHITE)
	await main.player.play_action("use")
	await main.voice("Ray. You still awake?", PHONE_AT, OTIS_COLOR)
	await main.say("Somebody has to be.")
	await main.voice("Hollywood Boulevard. Stardust Memorabilia, across from the Chinese Theatre.", PHONE_AT, OTIS_COLOR)
	await main.voice("Owner's at the bottom of the stairs to his own roof. Gus Lindqvist, seventy-one. And his Oscar's gone.", PHONE_AT, OTIS_COLOR)
	await main.say("His Oscar.")
	await main.voice("Nineteen fifty-four, Best Supporting Actor. Not his, he bought it. Patrol thinks somebody came for the statue.", PHONE_AT, OTIS_COLOR)
	await main.say("Everybody in this town wants one.")
	await main.voice("Not like this, they don't.", PHONE_AT, OTIS_COLOR)
	Game.set_flag("case2_done")
	await main.case_card("2:45 a.m.", "Case 3: Walk of Fame")
	await Case3.drive_in(main)
	await main.change_room("stardust_shop", "drive")


func _board3(verb: String, item: String) -> void:
	if verb == "look":
		await main.say("Danny in the middle, Kenji and Gus in the corners. Three faces, one night.")
	elif Game.flag("case3_deduced"):
		await main.say("Gus is closed. Danny isn't.")
	elif item == "brenner_card":
		await main.say("After Gus.")
	elif item == "" or item == "star_earring" or item == "fake_oscar":
		await _deduction3(item)
	else:
		await main.say("Pinning that up won't solve anything.")


# --- Case 3, scene 6: the deduction for Gus -------------------------------------------------
## Case 3 evidence cards: [id, card text, slot it proves ("A" she was selling him out, "B" she was at the top of his
## stairs, "" neither), Ray's line when it's pinned wrongly]. Only Case 3 cards, plus Brenner's card for a line.
const EVIDENCE3 := [
	["clue_practice_sigs", "Legal pad: \"Lyle Brandt\" forty times", "A", "That's what she was doing. I need where she was."],
	["clue_gold_pen", "Headshots in the same gold pen", "A", "That's what she was doing. I need where she was."],
	["clue_morty_bought", "Morty paid \"Stardust Archive\"; Pearl runs the email", "A",
			"That's what she was doing. I need where she was."],
	["star_earring", "Gold star earring, top of the stairs", "B", "That's where she was. First, why."],
	["catalogue", "Calloway's catalogue, No. 734 sold", "", "That proves Lyle was sold. Who sold him?"],
	["clue_uv_fakes", "Three fake signatures under UV", "", "Fakes on the wall. Whose hand?"],
	["clue_phone_log", "Gus called Pearl at 12:52", "", "That's when he called her. I need why."],
	["fake_oscar", "The floating prop Oscar", "", "That's what she did after. I need the top of the stairs."],
	["clue_pushed", "Two small hands on his chest", "", "That's how he went down. Whose hands?"],
	["clue_footprints", "Small heel prints to the tank", "", "Small heels. Half of Hollywood wears small heels."],
	["clue_bare_ear", "Pearl's torn earlobe", "", "A torn ear. Torn where?"],
	["clue_fiat", "Charlie: the yellow Fiat", "", "That's Charlie's eyes and ears. I want something Pearl left behind."],
	["clue_shouting", "Charlie: the shouting", "", "That's Charlie's eyes and ears. I want something Pearl left behind."],
	["clue_glass_out", "Glass outside", "", "That proves the robbery was a show. I need who killed him."],
	["clue_key_opened", "Key-opened case", "", "That proves the robbery was a show. I need who killed him."],
	["clue_staged", "Staged robbery", "", "That proves the robbery was a show. I need who killed him."],
	["clue_register", "Cash in the register", "", "That proves the robbery was a show. I need who killed him."],
	["clue_headshots_left", "Headshots still in the locker", "", "That's a lie about her pictures. I'm pinning the truth about Gus."],
	["clue_pearl_story", "Pearl's story", "", "That's her story. It's had three drafts."],
	["clue_eviction", "Eviction notice", "", "That's Pryce's business. This one was personal."],
	["clue_whitaker_alibi", "Whitaker's alibi", "", "That's Pryce's business. This one was personal."],
	["clue_morty_offer", "Morty's offer", "", "That's Morty. Morty didn't do it."],
	["clue_morty_alibi", "Morty's alibi", "", "That's Morty. Morty didn't do it."],
	["clue_tod_gus", "Time of death", "", "That's when, and why he was up there. The board wants who."],
	["clue_cigar", "Gus's cigar", "", "That's when, and why he was up there. The board wants who."],
	["brenner_card", "Walter Brenner's card", "", "That's a man who wanted Gus out. Gus went out another way."],
]
const SLOT_LABELS3 := ["She was selling him out", "She was at the top of his stairs"]


func _deduction3(first: String) -> void:
	main.ui.show_board("Seventy-one years, fourteen stairs, and two small hands. Whose?", "GUS LINDQVIST\n71. Stardust")
	await main.narrate("Seventy-one years, fourteen stairs, and two small hands. Whose?")
	# step 1: the culprit (wrong picks get a line; pick again)
	while true:
		var c: int = await main.choose(["Morty Kahn, the rival collector.", "Trent Whitaker, Pryce Development.",
				"A burglar off the boulevard.", "Pearl Danvers, his assistant.", "(Step back from the board)"])
		match c:
			0:
				if Game.flag("clue_morty_bought"):
					await main.narrate("Morty had the real Lyle in his safe. You don't kill a man over the copy.")
				elif Game.flag("clue_morty_alibi"):
					await main.narrate("Morty spent the night losing to a dentist in Osaka.")
				else:
					await main.narrate("Morty wanted it. Wanting isn't pushing. And I never asked where he was.")
			1:
				if Game.flag("clue_whitaker_alibi"):
					await main.narrate("Whitaker was in a Century City elevator in his tie. And a letter with twenty-three days to run doesn't need a push.")
				else:
					await main.narrate("Pryce sent a letter. A letter isn't a pair of hands. I never checked where Whitaker was.")
			2:
				await main.narrate("A burglar who breaks out, uses a key, leaves the cash and hides the loot on the roof? That's not a burglar. That's a stage manager.")
			3:
				await main.narrate("Pearlie.")
				break
			_:
				main.ui.hide_board()
				return
	# step 2: two labeled slots. A right card stays pinned; a wrong one gets Ray's line and comes down.
	main.ui.set_board_question("Pearl Danvers. Pin up what proves it.")
	var pins: Array[String] = ["", ""]
	var pre := _card3(first)
	if first != "" and pre[2] != "":
		pins[0 if pre[2] == "A" else 1] = first
	var wrong_tries := 0
	while true:
		main.ui.set_board_pins(_pin_texts3(pins), SLOT_LABELS3)
		for slot in 2:
			if pins[slot] != "":
				continue
			main.ui.set_board_question(SLOT_LABELS3[slot] + ":")
			var ids := _available_evidence3(pins)
			var opts: Array = []
			for id in ids:
				opts.append(_card3(id)[1])
			opts.append("(Step back from the board)")
			var c: int = await main.choose(opts)
			if c == ids.size():
				main.ui.hide_board()
				return
			pins[slot] = ids[c]
			main.ui.set_board_pins(_pin_texts3(pins), SLOT_LABELS3)
		var right := 0
		for slot in 2:
			var card := _card3(pins[slot])
			if card[2] == ("A" if slot == 0 else "B"):
				right += 1
			else:
				await main.narrate(card[3])
				pins[slot] = ""
		if right == 2:
			break
		wrong_tries += 1
		if wrong_tries == 3:
			await main.narrate("Think, Ray. What was she doing behind his back, and what did she leave at the top of his stairs?")
	# solved: a Polaroid of the dripping prop, the earring in its bag, the catalogue page; a line through the case
	main.ui.set_board_question("LINDQVIST, G.  -  CLOSED")
	await main.wait(0.6)
	await main.narrate("Pearl Danvers. She sold him the fake, then she sold him the fall.")
	Game.set_flag("case3_deduced")
	main.ui.hide_board()
	_sync()
	if Game.flag("got_brenner_card"):
		# no line, no music: the card goes up at the edge of Danny's corner, by the envelope (and the ride receipt)
		await main.player.play_action("use")
		Game.set_flag("board_brenner_card")
		_sync()
		await main.wait(1.4)
	await _calls3()


func _card3(id: String) -> Array:
	for e: Array in EVIDENCE3:
		if e[0] == id:
			return e
	return [id, id, "", ""]


func _available_evidence3(exclude: Array[String]) -> Array[String]:
	var out: Array[String] = []
	for e: Array in EVIDENCE3:
		var id: String = e[0]
		if exclude.has(id):
			continue
		if Game.has_item(id) or (id.begins_with("clue_") and Game.flag(id)):
			out.append(id)
	return out


func _pin_texts3(pins: Array[String]) -> Array:
	var out := []
	for id in pins:
		out.append("" if id == "" else _card3(id)[1])
	return out


# --- Case 3, scene 6: Doyle calls, then Otis with Case 4 -------------------------------------
func _calls3() -> void:
	# No branches: Case 5 throws "I see the captain at eight" back at Doyle.
	await main.wait(0.6)
	await main.voice("*RIIING*", PHONE_AT, Color.WHITE)
	await main.walk(hotspot("phone").walk_to)
	main.player.face("up")
	await main.player.play_action("use")
	await main.voice("Ray. Otis says your Oscar turned up in a water tank.", PHONE_AT, DOYLE_COLOR)
	await main.say("It was a fake. The killer wasn't.")
	await main.voice("The assistant? Hollywood. Everybody's auditioning. Anything on Reyes?", PHONE_AT, DOYLE_COLOR)
	await main.say("Danny's still on the board.")
	await main.voice("I see the captain at eight. I'd like to hand him one thing that's finished.", PHONE_AT, DOYLE_COLOR)
	await main.say("Hand him three. He likes numbers.")
	await main.voice("Go home at six, Ray. That's an order dressed up as advice. *click*", PHONE_AT, DOYLE_COLOR)
	await main.say("Six. Sure. This whole town's full of optimists.")
	await main.wait(0.8)
	await main.say("Ten to four.")
	await main.voice("*RIIING*", PHONE_AT, Color.WHITE)
	await main.player.play_action("use")
	await main.voice("Ray. You want the good news or the river?", PHONE_AT, OTIS_COLOR)
	await main.say("There's good news?")
	await main.voice("No. LA River, Elysian Valley, under the Fletcher Drive bridge. Delivery rider, twenty-four, Owen Tate. Down in the channel.", PHONE_AT, OTIS_COLOR)
	await main.say("The river's dry this time of year.")
	await main.voice("That's how they saw him. Uniforms already cuffed a fella from the camp by the bridge. They call him Preacher. The kid's bike was at his tent.", PHONE_AT, OTIS_COLOR)
	await main.say("Then it's closed. Why call me?")
	await main.voice("Because the uniforms are happy. When uniforms are happy at four in the morning, somebody ought to check.", PHONE_AT, OTIS_COLOR)
	await main.say("On my way.")
	await main.voice("And Ray? Preacher's Army. He says he'll only talk to somebody who's been somewhere.", PHONE_AT, OTIS_COLOR)
	Game.set_flag("case3_done")
	await main.case_card("3:50 a.m.", "Case 4: Low Water")
	await Case4.drive_in(main)
	await main.change_room("fletcher_bridge", "drive")


func _board4(verb: String, item: String) -> void:
	if verb == "look":
		await main.say("Four corners and a middle. Kenji, Gus, Owen, and Danny, still waiting.")
	elif Game.flag("case4_deduced"):
		await main.say("Owen's closed. Danny's got his phone back, sort of.")
	elif item == "pryce_invite":
		await main.say("After Owen.")
	elif item == "" or item == "lens_piece" or item == "valet_ticket":
		await _deduction4(item)
	else:
		await main.say("Pinning that up won't solve anything.")


# --- Case 4, scene 7: the deduction for Owen ---------------------------------------------------------
## Case 4 evidence cards: [id, card text, slot it proves ("A" his car hit Owen, "B" he was behind the wheel, "" neither),
## Ray's line when it's pinned wrongly]. Only Case 4 cards, plus Pryce's invitation for a line.
const EVIDENCE4 := [
	["clue_lens_match", "Both headlight pieces fit Crane's Audi", "A", "That's his car. Now put him in it."],
	["clue_yellow_paint", "Chomp yellow in the grille", "A", "That's his car. Now put him in it."],
	["valet_ticket", "Valet ticket No. 47, \"Crane, out 1:55\"", "B", "That's who drove. First, what his car did."],
	["clue_gate_clip", "Gate camera, 1:55, the Audi follows Owen", "B", "That's who drove. First, what his car did."],
	["lens_piece", "Half a headlight, an Audi part", "", "An Audi, sure. Whose Audi?"],
	["clue_audi", "The headlight piece: an Audi", "", "An Audi, sure. Whose Audi?"],
	["clue_paint", "Blue-gray paint on the bike", "", "Blue-gray. Half the hills are blue-gray."],
	["clue_curb_scrape", "Blue-gray paint on the curb", "", "Blue-gray. Half the hills are blue-gray."],
	["clue_glass_bridge", "Headlight glass on the bridge", "", "A headlight broke. I need the face it broke off."],
	["clue_headlight_glass", "Headlight glass in his hair", "", "A headlight broke. I need the face it broke off."],
	["clue_hit_by_car", "Shah: hit by a car from behind", "", "That's what killed him. I need which car."],
	["clue_crane_drunk", "Gate camera, 1:51, the drunk takes his keys", "", "He took the keys. I want him on the road."],
	["clue_loafers", "Crane's loafers, river mud", "", "That's what he did after. I need who was behind the wheel."],
	["clue_moved", "Shah: he was moved after death", "", "Somebody slid him. Pin who was driving."],
	["clue_drag_marks", "Drag marks down the bank", "", "That's how Owen got down the bank. Pin how he got hit."],
	["clue_two_tracks", "Two tracks: the bike, and Owen", "", "That's how Owen got down the bank. Pin how he got hit."],
	["clue_trip_paused", "Chomp: trip paused at 2:04", "", "That's when and where. The board wants who."],
	["clue_no_brakes", "No skid marks", "", "That's when and where. The board wants who."],
	["clue_one_star", "One-star review", "", "That's what Owen saw coming. Pin what came."],
	["clue_warning", "Owen's warning at the gate", "", "That's what Owen saw coming. Pin what came."],
	["clue_preacher_story", "Preacher's story", "", "That clears Preacher. I'm here to catch somebody."],
	["clue_bang", "Preacher: the bang, no brakes", "", "That clears Preacher. I'm here to catch somebody."],
	["clue_phone_left", "The phone left on the bike", "", "That clears Preacher. I'm here to catch somebody."],
	["clue_tarp_new", "A new tarp", "", "That's a man hiding something. I'm pinning the thing."],
	["clue_washing", "Two hours of washing", "", "That's a man hiding something. I'm pinning the thing."],
	["clue_crane_calls", "Missed calls from Ted and Harlan", "", "That's a man hiding something. I'm pinning the thing."],
	["clue_courtney_alibi", "Courtney's alibi", "", "That's somebody else's night."],
	["clue_pryce_driver", "Andre: Pryce's Lincoln", "", "That's somebody else's night."],
	["pryce_invite", "Pryce's invitation", "", "That's who paid for the party. Not who drove home from it."],
]
const SLOT_LABELS4 := ["His car hit Owen", "He was behind the wheel"]


func _deduction4(first: String) -> void:
	main.ui.show_board("Twenty-four, a yellow box and a red light. Who didn't stop?", "OWEN TATE\n24. Chomp rider")
	await main.narrate("Twenty-four, a yellow box and a red light. Who didn't stop?")
	# step 1: the culprit (wrong picks get a line; pick again)
	while true:
		var c: int = await main.choose(["Calvin \"Preacher\" Odom.", "Courtney Vail, the customer.", "Councilman Ted Haskell.",
				"Elliot Crane, Haskell's chief of staff.", "(Step back from the board)"])
		match c:
			0:
				await main.narrate("Preacher carried the bike down to save it. Shah says a car, and Preacher hasn't driven anything since 1991.")
			1:
				if Game.flag("clue_courtney_alibi"):
					await main.narrate("Courtney sent him out into the rain. Her own camera says she never left the house.")
				else:
					await main.narrate("Courtney gave him one star. That's cruelty, not a car. And I never checked where she was.")
			2:
				await main.narrate("Haskell left at eleven with his wife and a driver. Men like Haskell don't drive themselves anywhere.")
			3:
				await main.narrate("The man he told not to drive.")
				break
			_:
				main.ui.hide_board()
				return
	# step 2: two labeled slots. A right card stays pinned; a wrong one gets Ray's line and comes down.
	main.ui.set_board_question("Elliot Crane. Pin up what proves it.")
	var pins: Array[String] = ["", ""]
	var pre := _card4(first)
	if first != "" and pre[2] != "":
		pins[0 if pre[2] == "A" else 1] = first
	var wrong_tries := 0
	while true:
		main.ui.set_board_pins(_pin_texts4(pins), SLOT_LABELS4)
		for slot in 2:
			if pins[slot] != "":
				continue
			main.ui.set_board_question(SLOT_LABELS4[slot] + ":")
			var ids := _available_evidence4(pins)
			var opts: Array = []
			for id in ids:
				opts.append(_card4(id)[1])
			opts.append("(Step back from the board)")
			var c: int = await main.choose(opts)
			if c == ids.size():
				main.ui.hide_board()
				return
			pins[slot] = ids[c]
			main.ui.set_board_pins(_pin_texts4(pins), SLOT_LABELS4)
		var right := 0
		for slot in 2:
			var card := _card4(pins[slot])
			if card[2] == ("A" if slot == 0 else "B"):
				right += 1
			else:
				await main.narrate(card[3])
				pins[slot] = ""
		if right == 2:
			break
		wrong_tries += 1
		if wrong_tries == 3:
			await main.narrate("Think, Ray. What on his car came from the river, and who saw him take the keys?")
	# solved: a Polaroid of the headlight with the pieces fitted back, the valet ticket beside it, a line through the case
	main.ui.set_board_question("TATE, O.  -  CLOSED")
	await main.wait(0.6)
	await main.narrate("Elliot Crane. He ran down the one man who told him not to drive, then tried to give him to the river.")
	Game.set_flag("case4_deduced")
	main.ui.hide_board()
	_sync()
	# every time: the lab receipt goes up beside Danny's photo, under the envelope and the question mark
	await main.player.play_action("use")
	Game.set_flag("board_danny_phone")
	_sync()
	await main.wait(1.2)
	if Game.flag("got_pryce_invite"):
		# no line, no music: the invitation, folded open on the watercolour tower, on the other side of Danny's photo
		await main.player.play_action("use")
		Game.set_flag("board_pryce_invite")
		_sync()
		await main.wait(1.2)
		if Game.flag("board_ride_receipt") and Game.flag("board_brenner_card"):
			await main.wait(0.8)
			await main.narrate("Three pieces of paper that haven't been introduced.")
	await _calls4()


func _card4(id: String) -> Array:
	for e: Array in EVIDENCE4:
		if e[0] == id:
			return e
	return [id, id, "", ""]


func _available_evidence4(exclude: Array[String]) -> Array[String]:
	var out: Array[String] = []
	for e: Array in EVIDENCE4:
		var id: String = e[0]
		if exclude.has(id):
			continue
		if Game.has_item(id) or (id.begins_with("clue_") and Game.flag(id)):
			out.append(id)
	return out


func _pin_texts4(pins: Array[String]) -> Array:
	var out := []
	for id in pins:
		out.append("" if id == "" else _card4(id)[1])
	return out


# --- Case 4, scene 7: Doyle calls, then Otis: Sal Moretti ------------------------------------------
func _calls4() -> void:
	# No branches: Ray keeps the phone from Doyle, and Case 5 starts with Sal.
	await main.wait(0.6)
	await main.voice("*RIIING*", PHONE_AT, Color.WHITE)
	await main.walk(hotspot("phone").walk_to)
	main.player.face("up")
	await main.player.play_action("use")
	await main.voice("Ray. A councilman's chief of staff. At four in the morning.", PHONE_AT, DOYLE_COLOR)
	await main.say("He was driving at two.")
	await main.voice("Ted Haskell called the captain at home. The captain called me at home. Do you know how often the captain calls me at home?", PHONE_AT, DOYLE_COLOR)
	await main.say("Then it's a big night for both of you.")
	await main.voice("Is it solid?", PHONE_AT, DOYLE_COLOR)
	await main.say("The headlight fits like a key. A valet ticket, a gate camera, river mud on his shoes.")
	await main.wait(0.6)
	await main.voice("Then book him. By the book, every comma. I don't want to read about one shortcut.", PHONE_AT, DOYLE_COLOR)
	await main.say("You won't.")
	await main.voice("Anything on Reyes?", PHONE_AT, DOYLE_COLOR)
	await main.wait(1.2)
	await main.say("Nothing you can hand the captain.")
	await main.voice("Then I'll hand him nothing at eight. Go home at six, Ray. *click*", PHONE_AT, DOYLE_COLOR)
	await main.narrate("I didn't tell her about the phone. I couldn't have told you why. Twenty-six years, and some nights the job keeps its mouth shut for you.")
	await main.wait(1.0)
	await main.say("Ten to five.")
	await main.voice("*RIIING*", PHONE_AT, Color.WHITE)
	await main.wait(1.2)
	await main.voice("*RIIING*", PHONE_AT, Color.WHITE)
	await main.player.play_action("use")
	await main.voice("Ray.", PHONE_AT, OTIS_COLOR)
	await main.wait(0.8)
	await main.say("Go ahead.")
	await main.voice("It's the Blue Note. The porter came in to mop at half past four. Sal Moretti. He's hanging in the back room.", PHONE_AT, OTIS_COLOR)
	await main.wait(2.0)
	await main.voice("Ray?", PHONE_AT, OTIS_COLOR)
	await main.say("I talked to him tonight. Through the door.")
	await main.voice("Uniforms are calling it a suicide.", PHONE_AT, OTIS_COLOR)
	await main.say("Sal had a bar to open at four this afternoon. He wasn't the kind to leave the glasses dirty.")
	await main.voice("I'm sorry, Ray.", PHONE_AT, OTIS_COLOR)
	await main.say("On my way.")
	# on his way out he stops at the board, looks at Danny's photo, and touches the edge of the envelope
	await main.walk(hotspot("door").walk_to)
	main.player.face("right")
	await main.wait(1.2)
	Game.set_flag("case4_done")
	await main.case_card("4:50 a.m.", "Case 5: Last Call")
	Case5.start(main)
	await main.change_room("street_crime", "squad_room")


# --- Case 5: the leak, the board, the meet -------------------------------------------------------------------------
func _board5(verb: String, item: String) -> void:
	if verb == "look":
		if Game.flag("got_danny_box"):
			await main.say("Four corners and a hole in the middle where a piano player used to be.")
		elif Game.flag("case5_deduced"):
			await main.say("Danny in the middle, Sal beside him now, and a name on the back of an index card.")
		else:
			await main.say("Four corners and a middle. Danny's still in the middle, and now Sal is somewhere in it too.")
	elif Game.flag("got_danny_box"):
		await main.say("Packed.")
	elif Game.flag("case5_deduced"):
		await _pack_box()
	elif Game.flag("heard_take"):
		await _deduction5(item)
	elif item == "tab_book":
		await main.say("After I know what Danny had.")
	elif item != "":
		await main.say("Pinning that up won't solve anything.")
	elif Game.flag("clue_desk_line") and not Game.flag("clue_walt_aside"):
		await _remember()
	else:
		await main.say("Not yet. I need what Danny had.")


func _phone5() -> void:
	## The desk phone: its call log, Otis (after the lieutenant's line turns up), Harbor Marine (after the board).
	while true:
		var opts := ["Call log"]
		if Game.flag("clue_desk_line"):
			opts.append("Call Otis")
		if Game.flag("case5_deduced"):
			opts.append("Call Harbor Marine")
		opts.append("Hang up")
		var c: int = await main.choose(opts)
		match String(opts[c]):
			"Call log":
				await _call_log()
			"Call Otis":
				await _call_otis()
				return
			"Call Harbor Marine":
				await _call_harbor()
				return
			_:
				return


func _call_log() -> void:
	## Puzzle 4.1: the phone remembers.
	await main.player.play_action("use")
	main.ui.show_device("CALL LOG   x2140", [], 0, "4:50a  IN   x1000  FRONT DESK\n4:46a  IN   (310) 555-0122  DOYLE M CELL\n" +
			"3:50a  IN   x1000  FRONT DESK\n3:46a  IN   (310) 555-0122  DOYLE M CELL\n2:45a  IN   x1000  FRONT DESK\n" +
			"2:41a  IN   (310) 555-0122  DOYLE M CELL\n1:31a  IN   x1000  FRONT DESK\n1:30a  OUT  x2186  LT DOYLE   4:12\n" +
			"11:40p IN   x2186  LT DOYLE (VMAIL)", [], false, Color(0.2, 0.4, 0.16), true)
	await main.say("One call out, all night. One-thirty, to the lieutenant's office, one floor up.")
	await main.say("I told her about Sal, and the knock, and Nina.")
	main.clue("clue_one_call")
	main.ui.hide_device()


func _phone_list(verb: String) -> void:
	## Puzzle 4.2: the lieutenant's direct line.
	main.ui.show_paper("HOLLYWOOD STATION  -  INTERNAL", "Front desk ................ x1000\nWatch commander ....... x1100\n" +
			"Homicide, Room 214 ...... x2140\nDoyle, Lt. M. ............... x2186\n      direct (323) 555-0186\nDetectives, 2nd fl ........ x2150")
	if not Game.flag("clue_nina_call"):
		await main.say("HOLLYWOOD STATION, INTERNAL. Every extension in the building." if verb == "look"
				else "Every extension in the building. One of them made a call it shouldn't have.")
	elif not Game.flag("clue_desk_line"):
		await main.say("Three-two-three, five-five-five, oh-one-eight-six. The lieutenant's direct line.")
		await main.say("That's Nina's police number. One fifty-two, twenty-two minutes after I hung up on her.")
		main.clue("clue_desk_line")
		main.ui.hide_paper()
		await main.narrate("Maureen Doyle doesn't call waitresses at two in the morning. She doesn't call anybody. She has people for that.")
	else:
		await main.say("The lieutenant's direct line. Somebody else was holding it at one fifty-two.")
	main.ui.hide_paper()


func _remember() -> void:
	## Puzzle 4.3: the 1:30 call, replayed. The player picks the line that matters.
	main.ui.show_scene(null, 0.0, "1:30 a.m.")
	await main.narrate("One-thirty. Rain on the window. Her voice on the line, one floor up.")
	while true:
		var c: int = await main.choose(["\"Ray, it's one-thirty.\"", "\"Where'd you even get Vance?\"",
				"\"Moretti told the uniforms he was blind and deaf.\"", "\"Thanks, Walt. Black is fine.\"",
				"\"Stop wasting the night on one case.\""])
		match c:
			0:
				await main.narrate("She says that every time I call. It's always one-thirty somewhere.")
			1:
				await main.narrate("And I told her. Sal Moretti, the bartender.")
			2:
				await main.narrate("And I told her how he talks: through his door, if you knock right. Danny's knock. His girl Nina gave it to me. I said all of it.")
			3:
				await main.narrate("\"Thanks, Walt. Black is fine.\" Muffled, away from the phone, right in the middle of it.")
				break
			_:
				await main.narrate("Her favorite song. Not the line.")
	main.ui.hide_scene()
	await main.say("There was somebody in her office at one-thirty in the morning, bringing her coffee and listening to her half of my call.")
	await main.say("Her half had Sal's name in it. The rest she could tell him after she hung up.")
	main.clue("clue_walt_aside")


func _call_otis() -> void:
	await main.player.play_action("use")
	if not Game.flag("knows_brenner"):
		await _visitor_log()
	elif Game.flag("vance_in") and not Game.flag("otis_backup"):
		await main.say("Otis. I need a black-and-white at Pier 9, San Pedro, at a quarter to seven. Lights off. No radio.")
		await main.voice("Harbor's not our division, Ray.", PHONE_AT, OTIS_COLOR)
		await main.say("I know.")
		await main.voice("Does the lieutenant know?", PHONE_AT, OTIS_COLOR)
		await main.say("No.")
		await main.wait(1.0)
		await main.voice("Then I don't either. Harbor Division owes me a favor from 2011. I'll call it in myself.", PHONE_AT, OTIS_COLOR)
		await main.voice("Ray. Bring the coat back.", PHONE_AT, OTIS_COLOR)
		Game.set_flag("otis_backup")
	elif Game.flag("otis_backup"):
		await main.voice("Front desk. Your car's called in, Ray. Lights off, no radio, quarter to seven. I don't know a thing.", PHONE_AT, OTIS_COLOR)
	else:
		await main.voice("Front desk. I've lost a page, Ray. Like I said.", PHONE_AT, OTIS_COLOR)


func _visitor_log() -> void:
	## Puzzle 4.4: Otis's visitor log, then the name on the board, Doyle's call (4.5) and Ike's (4.6).
	await main.voice("Front desk. Ray, I'm sorry about Sal.", PHONE_AT, OTIS_COLOR)
	await main.say("Otis. Who came up to see the lieutenant last night?")
	await main.voice("(pages turning) One visitor after midnight. In at one-twenty, out at two-oh-five. Walter Brenner.", PHONE_AT, OTIS_COLOR)
	await main.voice("Retired, showed me his old ID and signed in like a civilian. He brought the lieutenant a coffee from the place on Cahuenga, and he brought me one too. Black.", PHONE_AT, OTIS_COLOR)
	await main.voice("Nobody ever brings the desk a coffee.", PHONE_AT, OTIS_COLOR)
	await main.say("Walt.")
	await main.voice("Old-timer. Rampart, way back. He was her training officer. She thinks the world of him. He drives for some developer now. Says the hours are better than ours.", PHONE_AT, OTIS_COLOR)
	main.clue("clue_visitor_log")
	await main.say("Was she with him the whole time?")
	await main.voice("Funny you ask. I've got her hallway on my monitor. Ten to two she went down to the copier with a stack the size of a phone book. The captain's briefing.", PHONE_AT, OTIS_COLOR)
	await main.voice("Six, seven minutes. He stayed in her office.", PHONE_AT, OTIS_COLOR)
	await main.say("Alone.")
	await main.voice("With the coffee. Ray, what's this about?", PHONE_AT, OTIS_COLOR)
	await main.say("Nothing yet. Don't write down that I asked.")
	await main.voice("I write everything down, Ray. But I've been known to lose a page.", PHONE_AT, OTIS_COLOR)
	main.clue("clue_brenner_alone")
	# at the board, with the first line that applies to each seed and echo
	await main.walk(hotspot("case_board").walk_to if hotspot("case_board").walk_to != Vector2.ZERO else main.player.position)
	if Game.flag("clue_wb"):
		await main.say("W.B., club soda. Walter Brenner.")
	if Game.flag("got_ride_receipt"):
		await main.say("Walt B. A Glide from the Blue Note to Pryce Tower an hour after Danny died. One star. Gun oil. And Kenji had a camera on his back seat.")
	if Game.flag("got_brenner_card"):
		await main.say("Walter Brenner, LAPD, retired. Security consultant, Pryce Development.")
	if Game.flag("clue_tape_helper"):
		await main.say("Park's old-timer at Danny's tape. An old ID, coffee from Cahuenga, and one question: did we find the phone.")
	if Game.flag("clue_pryce_driver"):
		await main.say("\"He drives for some developer.\" Andre said Pryce's driver was a big old guy who used to be a cop.")
	if Game.flag("clue_block_empty") or Game.flag("clue_big_man"):
		await main.say("Big fellow, old cop's coat.")
	if Game.flag("heard_caller"):
		await main.say("A cop who'd stopped being one.")
	await main.narrate("Maureen didn't make that call. She went to copy the captain's briefing, and the man who taught her to drive a black-and-white picked up her phone.")
	await main.narrate("She told him what I told her, because I told her, because she's my boss. That's how it works.")
	main.clue("knows_brenner")
	await _doyle_calls()
	await _ike_calls()


func _doyle_calls() -> void:
	## Puzzle 4.5: scripted, no branches. Ray lies to a lieutenant for the first time.
	await main.wait(0.6)
	await main.voice("*RIIING*", PHONE_AT, Color.WHITE)
	await main.walk(hotspot("phone").walk_to)
	main.player.face("up")
	await main.player.play_action("use")
	await main.voice("Ray. Otis says you're at the Blue Note.", PHONE_AT, DOYLE_COLOR)
	await main.say("Sal Moretti's dead.")
	await main.voice("I heard. Patrol says he hanged himself. I know you talked to him tonight. That's not on you.", PHONE_AT, DOYLE_COLOR)
	await main.wait(0.8)
	await main.say("Isn't it.")
	await main.voice("Walt Brenner called me ten minutes ago. My old training officer; you've never met him. He listens to the scanner like it's a ballgame.", PHONE_AT, DOYLE_COLOR)
	await main.voice("He heard the Blue Note call and asked if you were on it. He's worried about you. He says you sound like a man who's been up all night chasing a ghost.", PHONE_AT, DOYLE_COLOR)
	await main.say("He's never heard me.")
	await main.voice("He's heard me talk about you. That's worse. Tell me you're going home at six.", PHONE_AT, DOYLE_COLOR)
	await main.wait(1.2)
	await main.say("I'm going home at six.")
	await main.voice("That's the first time you've ever listened to me.", PHONE_AT, DOYLE_COLOR)
	await main.say("First time for everything.")
	await main.voice("I see the captain at eight. Get some sleep. *click*", PHONE_AT, DOYLE_COLOR)
	await main.narrate("Twenty-six years, and the first time I lied to a lieutenant it felt like the right thing. It felt like being sick. Both.")
	Game.set_flag("lied_to_doyle")


func _ike_calls() -> void:
	## Puzzle 4.6: Ray's own phone buzzes before he's put the receiver down.
	await main.wait(0.5)
	await main.voice("*bzzz bzzz*", Case5.CALL_AT, Color.WHITE)
	await main.player.play_action("use")
	await main.voice("Kessler. You said one hour. It's been fifty minutes. I'm a man of my word.", Case5.CALL_AT, Case4.IKE_COLOR)
	await main.say("Tell me.")
	await main.voice("The phone's soup, like I said. But your piano player recorded every set on an app called Takes. Every take uploads to the cloud the second you hit stop.", Case5.CALL_AT, Case4.IKE_COLOR)
	await main.voice("Account name \"reyes.keys.\" Last upload: Tuesday, eleven fifty-two p.m.", Case5.CALL_AT, Case4.IKE_COLOR)
	await main.say("Eight minutes before he died.")
	await main.voice("His mother in Fresno is next of kin. She gave written consent ten minutes ago, so this is legal, and I'd like to keep it that way.", Case5.CALL_AT, Case4.IKE_COLOR)
	await main.voice("I can get in through account recovery, but it wants the password, and he left himself a hint. Quote: \"the knock, the way I play it.\"", Case5.CALL_AT, Case4.IKE_COLOR)
	await main.voice("Three wrong tries and it locks for a day. You know what that means?", Case5.CALL_AT, Case4.IKE_COLOR)
	await main.say("Maybe. Give me ten minutes and a piano.")
	main.clue("clue_takes_hint")
	if Game.flag("got_ride_receipt"):
		await main.say("One more thing. The rideshare case. Eleven dashcam cards came in from a freezer around three. Pull November. Wednesday, ten past one, the back-seat lens.")
		await main.voice("You know what my job is, right? It's this. Fine.", Case5.CALL_AT, Case4.IKE_COLOR)
		Game.set_flag("asked_cabin_clip")


func _call_harbor() -> void:
	## Puzzle 6.3, step one: Tiny, then Vance, and a cell number.
	await main.player.play_action("use")
	if Game.flag("vance_in"):
		await main.voice("Harbor Marine. Sunrise, Detective. Mr. Vance doesn't like to be asked twice.", PHONE_AT, Case5.TINY_COLOR)
		return
	await main.voice("Harbor Marine.", PHONE_AT, Case5.TINY_COLOR)
	await main.say("Tiny. Ray Kessler. Friend of Danny's.")
	await main.wait(1.2)
	await main.voice("You found him.", PHONE_AT, Case5.TINY_COLOR)
	await main.say("I found him. I need your pier at sunrise, and I need Mr. Vance.")
	await main.voice("(muffled talk)", PHONE_AT, Case5.TINY_COLOR)
	await main.voice("Detective. Dawn is an unchristian hour.", PHONE_AT, Case5.VANCE_COLOR)
	if Game.flag("heard_caller"):
		await main.say("You said a man telephoned you Wednesday, asking whether Danny paid you. You keep records, Mr. Vance.")
	else:
		await main.say("Did anyone else ask you about Danny this week?")
		await main.voice("A man telephoned Wednesday. He wanted to know if Danny had paid me, and in what. He talked like a cop who'd stopped being one.", PHONE_AT, Case5.VANCE_COLOR)
		await main.say("You keep records, Mr. Vance.")
	await main.voice("I keep everyone's number. It's the only way to be sure of people.", PHONE_AT, Case5.VANCE_COLOR)
	await main.voice("Two-one-three, five-five-five, oh-one-six-three. A cell telephone. A cop's voice and a civilian's manners.", PHONE_AT, Case5.VANCE_COLOR)
	main.clue("clue_brenner_number")
	if Game.flag("got_brenner_card"):
		await main.say("Same number as the card on Gus's desk.")
	await main.say("I'd like to meet him on your pier at sunrise. I'd like you there. Tiny too.")
	await main.voice("You want witnesses who aren't police.", PHONE_AT, Case5.VANCE_COLOR)
	await main.say("I want witnesses who aren't anybody's.")
	await main.wait(0.8)
	await main.voice("Danny paid his debts, Detective. I like to think I pay mine. Sunrise.", PHONE_AT, Case5.VANCE_COLOR)
	Game.set_flag("vance_in")
	await main.say("Otis can find me a patrol car nobody upstairs knows about.")


# --- Case 5: the deduction (Puzzle 6.1) ------------------------------------------------------------------------------
## Case 5 evidence cards: [id, card text, slot it proves ("A" he got the knock, "B" he was in the bar at 3:20, "C" what
## Danny had, "D" what it was costing them, "" none), Ray's line when it's pinned wrongly]. An id is an inventory item, a
## notebook clue, or a board flag (the envelope and the seeds pinned in earlier cases).
const EVIDENCE5 := [
	["clue_brenner_alone", "Otis: Walt alone in Doyle's office at 1:52", "A", "That's how he got the knock. Put him in the bar."],
	["tab_book", "Tab book: \"3:20 W.B. club soda\"", "B", "That puts him at Sal's bar. First, how he got in."],
	["clue_desk_line", "Nina's caller was Doyle's desk line", "", "That's Maureen's phone. Who was holding it?"],
	["clue_nina_call", "Nina's call at 1:52", "", "That's when the knock got out. Not who took it."],
	["clue_walt_aside", "\"Thanks, Walt. Black is fine.\"", "", "Walt was in the room. Was he alone with the phone?"],
	["clue_one_call", "One call out, at 1:30", "", "That's what I told. Pin who listened."],
	["clue_choke", "Bar-arm choke, banned in 1982", "", "That's how. Put him in the room."],
	["clue_wet_glass", "One glass washed after closing", "", "Somebody washed a glass. Whose name goes with it?"],
	["clue_nina_heard", "Nina heard a man ask what the kid left", "", "Nina heard a voice. She never saw a face."],
	["clue_latch", "Front door on the latch, back door locked", "", "That's how he left. Pin him arriving."],
	["clue_staged_hanging", "Stool, clean hands, no note", "", "That proves it wasn't Sal. It doesn't prove it was Walt."],
	["clue_locker", "Danny's locker, Sal's keys", "", "Somebody was looking. Pin who."],
	["clue_sal_no", "Pryce's letter, Sal's NO", "", "That's why Pryce wanted him gone. Not who came."],
	["clue_take", "The take: \"Then pay him, Walt.\"", "C", "That's what Danny had. First, what it was costing them." ],
	["board_envelope", "Envelope, \"1 of 3\"", "D", "That's the bill. First, what Danny had."],
	["clue_booth_tuesday", "Tuesday's back booth, three men, cash", "", "That's who sat there. Pin what they said."],
	["clue_takes_app", "Danny recorded every set", "", "He recorded a lot of sets. Pin the one that mattered."],
	["clue_paid", "Paid Vance $8,000 in full", "", "That says he had money. What says there was more coming?"],
	["clue_lisbon", "\"One of three, and then Lisbon\"", "", "Nina knew the dream. Pin the bill."],
	["board_ride_receipt", "Photo of Walt B.'s ride, billed to Pryce Development", "*", ""],
	["board_brenner_card", "Walter Brenner's card", "*", ""],
	["board_pryce_invite", "Pryce's invitation", "*", ""],
]


func _card5(id: String) -> Array:
	for e: Array in EVIDENCE5:
		if e[0] == id:
			return e
	return [id, id, "", ""]


func _available5(exclude: Array[String]) -> Array[String]:
	var out: Array[String] = []
	for e: Array in EVIDENCE5:
		var id: String = e[0]
		if exclude.has(id):
			continue
		if Game.has_item(id) or ((id.begins_with("clue_") or id.begins_with("board_")) and Game.flag(id)):
			out.append(id)
	return out


func _pins5(labels: Array, slots: Array, first: String, seed_line: String, nudge: String) -> bool:
	## Two labeled slots; a right card stays pinned, a wrong one gets Ray's line and comes down. Returns false if the
	## player stepped back from the board.
	var pins: Array[String] = ["", ""]
	var pre := _card5(first)
	if first != "" and slots.has(pre[2]):
		pins[slots.find(pre[2])] = first
	var wrong_tries := 0
	while true:
		main.ui.set_board_pins(_texts5(pins), labels)
		for slot in 2:
			if pins[slot] != "":
				continue
			main.ui.set_board_question(String(labels[slot]) + ":")
			var ids := _available5(pins)
			var opts: Array = []
			for id in ids:
				opts.append(_card5(id)[1])
			opts.append("(Step back from the board)")
			var c: int = await main.choose(opts)
			if c == ids.size():
				main.ui.hide_board()
				return false
			pins[slot] = ids[c]
			main.ui.set_board_pins(_texts5(pins), labels)
		var right := 0
		for slot in 2:
			var card := _card5(pins[slot])
			if card[2] == slots[slot]:
				right += 1
			else:
				await main.narrate(seed_line if card[2] == "*" else String(card[3]))
				pins[slot] = ""
		if right == 2:
			return true
		wrong_tries += 1
		if wrong_tries == 3:
			await main.narrate(nudge)
	return false


func _texts5(pins: Array[String]) -> Array:
	var out := []
	for id in pins:
		out.append("" if id == "" else _card5(id)[1])
	return out


func _deduction5(first: String) -> void:
	# step 1: who killed Sal
	main.ui.show_board("Thirty-one years behind a bar, and he opened the door one last time. Who for?",
			"SAL MORETTI\n64. The Blue Note")
	await main.narrate("Thirty-one years behind a bar, and he opened the door one last time. Who for?")
	while true:
		var c: int = await main.choose(["Nobody. Sal hanged himself.", "Nina Alvarez", "Lt. Maureen Doyle", "Vance",
				"Walt Brenner", "(Step back from the board)"])
		match c:
			0:
				if Game.flag("clue_stool") or Game.flag("clue_clean_hands"):
					await main.narrate("Shah says he was dead before the rope. And he'd have had to fly to that pipe.")
				else:
					await main.narrate("Shah says he was dead before the rope.")
			1:
				await main.narrate("Nina was in a cooler with a paring knife, hiding from the man who did it. She couldn't put a bar-arm choke on a man if he lay down for her.")
			2:
				await main.narrate("Her phone made the call. She was at the copier when it did. And nobody taught that hold to anyone who joined in '96.")
			3:
				await main.narrate("Vance and Tiny heard Danny's knock every Tuesday. Whoever killed Sal had to call Nina to get it.")
			4:
				await main.narrate("The man who brought the coffee.")
				break
			_:
				main.ui.hide_board()
				return
	# step 2: how Walt got to Sal
	main.ui.set_board_question("Walt Brenner. Pin up how he got to Sal.")
	var ok: bool = await _pins5(["He got the knock", "He was in the bar at 3:20"], ["A", "B"], first,
			"That's on the string. The board wants Tuesday and tonight.",
			"Think, Ray. Who was holding Maureen's phone, and who did Sal write down?")
	if not ok:
		return
	# step 3: who wanted Danny dead
	main.ui.hide_board()
	main.ui.show_board("Somebody pulled the trigger on Danny. Somebody else named the price. Who?")
	await main.narrate("Somebody pulled the trigger on Danny. Somebody else named the price. Who?")
	while true:
		var c: int = await main.choose(["Vance", "Nina Alvarez", "Lt. Maureen Doyle",
				"Harlan Pryce, to protect the Haskell bribe", "(Step back from the board)"])
		match c:
			0:
				await main.narrate("Dead men don't pay, and Danny had paid.")
			1:
				await main.narrate("Nina had a plan for Lisbon. You don't kill the man who's buying the tickets.")
			2:
				await main.narrate("Maureen never heard of Danny Reyes until he was a file on her desk.")
			3:
				await main.narrate("\"Then pay him, Walt.\"")
				break
			_:
				main.ui.hide_board()
				return
	main.ui.set_board_question("Harlan Pryce. Pin up what Danny had, and what it cost.")
	ok = await _pins5(["What Danny had", "What it was costing them"], ["C", "D"], "",
			"That's on the string. The board wants what Danny had and what he charged.",
			"What did Danny have, and what was he charging for it?")
	if not ok:
		return
	# solved: the name on the back of the Case 1 index card, the tab book photo and Sal's card beside Danny
	main.ui.set_board_question("REYES, D.   MORETTI, S.   -   BRENNER, W.")
	main.ui.set_board_pins(["WALT BRENNER\nfor H. PRYCE, T. HASKELL", "3:20 W.B. CLUB SODA\nand Sal's bar card"])
	await main.wait(0.6)
	await main.narrate("Walt Brenner. He killed Danny for a price somebody else named, and he killed Sal for opening a door.")
	Game.set_flag("case5_deduced")
	main.ui.hide_board()
	_sync()
	# the string, depending on the seeds pinned
	var seeds := 0
	for f in ["board_ride_receipt", "board_brenner_card", "board_pryce_invite"]:
		if Game.flag(f):
			seeds += 1
	await main.player.play_action("use")
	if seeds == 3:
		Game.set_flag("board_string")
		_sync()
		await main.wait(1.0)
		await main.narrate("A ride receipt, a business card and a party invitation. Three pieces of paper that hadn't been introduced. Now they're family.")
	elif seeds > 0:
		await main.narrate("A string with gaps in it. Gaps are where lawyers live.")
	else:
		await main.narrate("No string. A name, a dead man's handwriting, and a song I haven't picked up yet.")
	await main.say("Danny's case goes in a box. Then I need a place, a witness, and a way to get Walt there.")


func _pack_box() -> void:
	## Puzzle 6.2: Danny's middle of the board goes into an evidence box.
	await main.player.play_action("pickup")
	await main.say("An empty evidence box from under the desk. Danny's photo, the envelope, the lab receipt, the index card, the tab book photo" +
			(", and the three pieces of paper on the string." if Game.flag("board_string") else "."))
	Game.set_flag("got_danny_box")
	_sync()
	await main.give("danny_box", false)
	await main.say("If I'm wrong about the next hour, somebody should find all of this in one box.")
