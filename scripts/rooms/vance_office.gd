extends Room
## Vance's office, a shipping container inside the salvage warehouse (Case 1, scene 5).
## Puzzle: find Danny's marker on the wall of IOUs (stamped PAID) and put it to Vance. That opens
## the money, the envelope and the man who telephoned. Using the Reyes file on Vance points a stuck
## player at the wall.

## Left-click verbs shown under the cursor (see Room.verb_for); unlisted hotspots are "use".
const VERBS := {
	"vance": "talk", "door": "go", "boat_photo": "look", "heater": "look"
}

const VANCE_COLOR := Color(0.78, 0.74, 0.9)
const VANCE_AT := Vector2(1259, 440)


func on_enter(from_room: String) -> void:
	if from_room == "pier9_dock" and not Game.flag("met_vance"):
		Game.set_flag("met_vance")
		await main.voice("Detective. Tiny tells me you're a friend of Danny's. Tiny is sentimental. I'm not.", VANCE_AT, VANCE_COLOR)
		await main.voice("Sit, if you like. The chair is uncomfortable. I bought it that way.", VANCE_AT, VANCE_COLOR)


func interact(hs: Hotspot, verb: String, item: String) -> void:
	match hs.id:
		"vance":
			if verb == "look":
				await main.say("Sixties. Cardigan, reading glasses, shoulder holster. A grandfather who forecloses.")
			elif item == "case_file":
				await main.say("Close range. A .38. Wallet left on him.")
				await main.voice("If I'd had him shot, they'd have taken the wallet. It saves my people the trouble of sending flowers.", VANCE_AT, VANCE_COLOR)
				await main.say("And his phone was gone.")
				await main.voice("Was it? Interesting. Not to me.", VANCE_AT, VANCE_COLOR)
				await main.wait(0.4)
				await main.voice("Look at my wall, Detective. I keep better records than your department.", VANCE_AT, VANCE_COLOR)
			elif item == "envelope":
				await main.voice("That's it. One of three. Sounds like a man with a payment plan.", VANCE_AT, VANCE_COLOR)
			elif item != "":
				await main.voice("I don't pawn, Detective.", VANCE_AT, VANCE_COLOR)
			else:
				await _interrogate()

		"markers":
			if verb == "look":
				await main.say("IOUs. Dozens of them, pinned in rows like butterflies.")
			elif item != "":
				await default_response(verb, item)
			elif not Game.flag("saw_paid"):
				await main.player.play_action("use")
				await main.say("Reyes, D. $8,000. Stamped PAID in red, dated Tuesday.")
				Game.set_flag("saw_paid")
			else:
				await main.say("Danny's is the only one stamped PAID. The only one.")

		"gun":
			if verb == "look":
				await main.say("A Colt .45 on the blotter, next to a cup of tea. A man of contrasts.")
				Game.set_flag("saw_gun")
			elif item != "":
				await default_response(verb, item)
			else:
				await main.say("Touching a loan shark's gun in his own office is the kind of thing they carve on your headstone.")

		"tea":
			if verb == "look":
				await main.say("Chamomile. The man sleeps fine.")
			else:
				await main.say("I'll pass.")

		"ledger":
			if verb == "look":
				await main.say("A green ledger. Vance's real business. He'd sooner give me a kidney.")
			else:
				await main.voice("Hands, Detective.", VANCE_AT, VANCE_COLOR)

		"boat_photo":
			await main.say("A sport fisher called Second Chance. Loan sharks all have the same sense of humor.")

		"lamp":
			if verb == "look":
				await main.say("Green banker's lamp. Same as mine. We buy from the same catalog, and that's all we share.")
			else:
				await main.say("No key under this one. I checked.")

		"heater":
			await main.say("Glowing orange. It's the warmest thing in the room, Vance included.")

		"door":
			if verb == "look":
				await main.say("Back to the rain.")
			elif item != "":
				await default_response(verb, item)
			else:
				await main.change_room("pier9_dock", "vance_office")

		_:
			await default_response(verb, item)


func _interrogate() -> void:
	## The menu loops; options appear as they unlock and drop out once asked.
	while true:
		var opts := []
		var keys := []
		if not Game.flag("asked_owed"):
			opts.append("Danny Reyes owed you money."); keys.append("owed")
		if not Game.flag("clue_alibi"):
			opts.append("Where were you Tuesday night?"); keys.append("where")
		if Game.flag("saw_gun") and not Game.flag("asked_gun"):
			opts.append("That's a .45."); keys.append("gun")
		if Game.flag("saw_paid") and not Game.flag("clue_paid"):
			opts.append("Danny's marker says PAID."); keys.append("paid")
		if Game.flag("clue_paid") and not Game.flag("knows_envelope"):
			opts.append("How did he pay you?"); keys.append("how")
		if Game.flag("clue_paid") and not Game.flag("heard_caller"):
			opts.append("Anyone else asking about Danny?"); keys.append("anyone")
		opts.append("I'll be going."); keys.append("leave")
		var c: int = await main.topics(opts)
		if c < 0:
			return
		var k: String = keys[c]
		await main.say(opts[c])
		match k:
			"owed":
				Game.set_flag("asked_owed")
				await main.voice("Half this city owes me money, Detective. The other half owes the bank. I'm friendlier.", VANCE_AT, VANCE_COLOR)
				await main.say("He's dead.")
				await main.voice("I read the papers. Dead men are bad for business. Think about that.", VANCE_AT, VANCE_COLOR)
			"where":
				await main.voice("On my boat in Avalon harbor. I lost four hundred dollars at cards to a dentist from Torrance.", VANCE_AT, VANCE_COLOR)
				await main.voice("Harbor patrol logged me in at six and out Wednesday at noon. Check it.", VANCE_AT, VANCE_COLOR)
				await main.say("I will.")
				await main.voice("I know. That's why I told you.", VANCE_AT, VANCE_COLOR)
				main.clue("clue_alibi")
			"gun":
				Game.set_flag("asked_gun")
				await main.voice("It is. Your piano player was shot with a .38, if the Times is right.", VANCE_AT, VANCE_COLOR)
				await main.voice("I've never owned a revolver. They're for people who want to be romantic about it.", VANCE_AT, VANCE_COLOR)
			"paid":
				await main.say("Third row, fourth from the left. Reyes, D. Eight thousand. Stamped PAID, Tuesday's date.")
				await main.wait(0.6)
				await main.voice("Dead men don't pay, Detective. Danny paid. All of it, Tuesday afternoon, in cash.", VANCE_AT, VANCE_COLOR)
				await main.say("Eight grand. From a man who played for tips.")
				await main.voice("I asked him the same thing. He smiled, which was new.", VANCE_AT, VANCE_COLOR)
				await main.voice("Said he'd come into some money and there was more where it came from.", VANCE_AT, VANCE_COLOR)
				await main.say("More from where?")
				await main.voice("I don't ask where money comes from. Only where it's going.", VANCE_AT, VANCE_COLOR)
				await main.player.play_action("notebook")
				await main.say("Paid in full Tuesday afternoon. Dead by Tuesday midnight.")
				main.clue("clue_paid")
			"how":
				await main.voice("In a Blue Note envelope, like a boy bringing his allowance.", VANCE_AT, VANCE_COLOR)
				await main.voice("He'd written something on the back. I didn't read it. I'm not his diary.", VANCE_AT, VANCE_COLOR)
				await main.say("Where's the envelope now?")
				await main.voice("Tiny burns the trash every night. If it's anywhere, it's in the barrel.", VANCE_AT, VANCE_COLOR)
				Game.set_flag("knows_envelope")
			"anyone":
				await main.voice("You're the second this week. Yesterday a man telephoned.", VANCE_AT, VANCE_COLOR)
				await main.voice("Wanted to know if Danny had paid me, and in what.", VANCE_AT, VANCE_COLOR)
				await main.say("Name?")
				await main.voice("He didn't offer one. He talked like a cop who'd stopped being one.", VANCE_AT, VANCE_COLOR)
				await main.voice("You'd know the type better than I would.", VANCE_AT, VANCE_COLOR)
				await main.say("What did you tell him?")
				await main.voice("What I'm telling you. Less, actually. I liked his voice less.", VANCE_AT, VANCE_COLOR)
				Game.set_flag("heard_caller")
			"leave":
				if Game.flag("knows_envelope"):
					await main.voice("Detective. Whoever did Danny, it wasn't for my eight thousand. He'd already paid it.", VANCE_AT, VANCE_COLOR)
					await main.voice("Find out who he was expecting to pay him.", VANCE_AT, VANCE_COLOR)
				else:
					await main.voice("Tiny will see you out. Come back when you've got a better question.", VANCE_AT, VANCE_COLOR)
				await main.change_room("pier9_dock", "vance_office")
				return
