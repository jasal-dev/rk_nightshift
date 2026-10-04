extends Room
## Stardust's back office (Case 3, scene 3). Gus at the foot of the roof stairs, Dr. Shah kneeling by him.
## Shah: "How did he die?" gives Gus's keys; "Did he fall?" gives the two small hands (clue_pushed).
## Puzzle 3.1: the desk (the eviction letter, then Calloway's catalogue; the letter hides Walter Brenner's card).
## Puzzle 3.2: Gus's cordless phone (Calls: Calloway's at 12:40, Pearl at 12:52). Puzzle 3.3: the locked drawer and
## the UV lamp. Puzzle 3.4: Pearl's locker (headshots, the practice signatures, the gold pen under UV).
## Puzzle 3.5: the fuse panel's ROOF SIGN override (sign_on); until then the stairs lead to the dark roof.

@onready var sign_glow: Sprite2D = $Sign_glow
var _wander := 0


func _ready() -> void:
	super._ready()
	_sync()


func _sync() -> void:
	sign_glow.visible = Game.flag("sign_on")


func on_enter(from_room: String) -> void:
	if from_room == "stardust_shop" and not Game.flag("in_office"):
		Game.set_flag("in_office")
		await main.wait(0.3)
		await main.say("Gus's office. Everything he ever loved, filed under \"later.\"")
		await main.player.play_action("use")
		await _shah("Look at that. You can be taught.")
		await main.say("You've been saying that for eleven years.")
		await _shah("And look how long it took.")


func interact(hs: Hotspot, verb: String, item: String) -> void:
	if hs.id != "shah":
		await _maybe_hint()
	match hs.id:
		"gus":
			if verb == "look":
				await main.say("Gus Lindqvist. Seventy-one. One slipper on, one on the third step. He came down a lot faster than he went up.")
			elif item != "":
				await default_response(verb, item)
			else:
				await main.say("Shah's got him.")

		"shah":
			if verb == "look":
				await main.say("Dr. Shah. Second time tonight. We should stop meeting like this.")
			elif item == "uv_lamp":
				await _shah("Point that somewhere else, Ray.")
			elif item == "star_earring":
				await _shah("Five points. That fits his palm. Bag it.")
			elif item != "":
				await default_response(verb, item)
			else:
				await _talk_to_shah()

		"desk":
			if verb == "look":
				await main.say("A rolltop desk under paper. A green lamp still burning.")
			elif item != "":
				await default_response(verb, item)
			elif not Game.flag("clue_eviction"):
				await _eviction_letter()
			elif not Game.flag("got_catalogue"):
				await _catalogue()
			elif not Game.flag("got_brenner_card"):
				await _brenner_card()
			else:
				await main.say("Bills, invoices, a racing form from 1997. I've taken everything that mattered.")

		"letter":
			if item != "":
				await default_response(verb, item)
			elif not Game.flag("clue_eviction"):
				await _eviction_letter()
			elif verb == "look":
				await main.say("Pryce's letter. Thirty days, and a week of them gone." if not Game.flag("got_brenner_card")
						else "Pryce's letter. I've kept the card.")
			elif not Game.flag("got_brenner_card"):
				await _brenner_card()
			else:
				await main.say("Pryce's letter. I've kept the card.")

		"drawer":
			if item == "gus_keys":
				if Game.flag("got_uv_lamp"):
					await main.say("Cigars and a loupe. He was a man of simple pleasures and complicated ones.")
				else:
					await _drawer()
			elif item != "":
				await default_response(verb, item)
			elif Game.flag("got_uv_lamp"):
				await main.say("Cigars and a loupe. He was a man of simple pleasures and complicated ones.")
			elif verb == "look":
				await main.say("Locked.")
			else:
				await main.say("Locked. Gus kept the good stuff where his hands could find it.")

		"phone":
			if verb == "look":
				await main.say("A cordless phone older than Officer Park.")
			elif item != "":
				await default_response(verb, item)
			else:
				await _phone()

		"cabinet":
			if verb == "look":
				await main.say("Provenance files, A to Z. Gus kept receipts the way other men keep grudges.")
			elif item != "":
				await default_response(verb, item)
			else:
				await main.player.play_action("use")
				await main.say("B for Brandt: a bill of sale from 1988, eleven thousand dollars. Gus did all right.")

		"fuse_panel":
			if item != "":
				await default_response(verb, item)
			elif verb == "look" and not Game.flag("sign_on"):
				main.ui.show_paper("Fuse panel", "SHOP\nOFFICE\nFRIDGE (NEVER)\nROOF SIGN, TIMER OFF AT 1 ($$$!)",
						"The ROOF SIGN switch has a little timer dial, set to 1:00.", Color(0.3, 0.3, 0.36))
				await main.say("Labels in Gus's capitals. The roof sign switches itself off at one.")
				main.ui.hide_paper()
			elif Game.flag("sign_on"):
				await main.say("The sign's on. Let it burn.")
			else:
				await main.player.play_action("use")
				await main.say("Gus switched the sign off at one every night to save money. Tonight Gus can afford it.")
				Game.set_flag("sign_on")
				_sync()
				await main.wait(0.6)
				await main.say("Red and gold, all the way down the stairs.")

		"pearl_locker":
			if verb == "look":
				await main.say("PEARL, on masking tape. The door's ajar.")
			elif item == "uv_lamp":
				await _gold_pen()
			elif item != "":
				await default_response(verb, item)
			elif not Game.flag("clue_headshots_left"):
				await main.player.play_action("use")
				await main.say("A coat, a spare pair of heels, a makeup bag. And an envelope: \"PEARL DANVERS, HEADSHOTS, 8 x 10\".")
				await main.say("Twenty of them, signed, ready to hand out.")
				main.clue("clue_headshots_left")
				await main.say("She came back at two in the morning for her headshots. Here they are.")
			elif not Game.flag("clue_practice_sigs"):
				await main.player.play_action("use")
				await main.say("Under the envelope, a legal pad. Somebody's written \"Lyle Brandt\" forty times in gold pen.")
				await main.say("The first ones are bad. The last ten are perfect. And a gold paint pen, cap chewed.")
				main.clue("clue_practice_sigs")
			else:
				await main.say("Her headshots, a legal pad of somebody else's name, and a chewed gold pen.")

		"gus_locker":
			if item == "gus_keys":
				await main.say("Nothing in here but Gus.")
			elif item != "":
				await default_response(verb, item)
			else:
				await main.say("GUS. A cardigan, an umbrella, and a photo of a younger Gus shaking hands with Lyle Brandt.")

		"stairs":
			if verb == "look":
				await main.say("Fourteen steep steps up to the roof. One slipper on the third.")
			elif item != "":
				await default_response(verb, item)
			else:
				await main.change_room("stardust_roof" if Game.flag("sign_on") else "stardust_roof_dark", "stardust_office")

		"curtain":
			if verb == "look":
				await main.say("Back to the shop.")
			elif item != "":
				await default_response(verb, item)
			else:
				await main.change_room("stardust_shop", "stardust_office")

		_:
			await default_response(verb, item)


func _shah(line: String) -> void:
	await main.voice(line, speaker_at("shah"), Case2.SHAH_COLOR)


func _maybe_hint() -> void:
	var key := ""
	var hint := ""
	if Game.has_item("catalogue") and not Game.flag("clue_phone_log"):
		key = "hint_office_phone"
		hint = "He read that at midnight. Who'd you call, at midnight, with news like that?"
	elif Game.flag("shah_how") and not Game.flag("clue_pushed"):
		key = "hint_office_shah"
		hint = "Shah's got that look. The one where I haven't asked the right question."
	if key == "" or Game.flag(key):
		_wander = 0
		return
	_wander += 1
	if _wander >= 4:
		_wander = 0
		Game.set_flag(key)
		await main.say(hint)


# --- Dr. Shah ---------------------------------------------------------------------------
func _talk_to_shah() -> void:
	while true:
		var opts := []
		var keys := []
		if not Game.flag("shah_how"):
			opts.append("How did he die?"); keys.append("how")
		if not Game.flag("clue_tod_gus"):
			opts.append("When?"); keys.append("when")
		if Game.flag("shah_how") and not Game.flag("clue_pushed"):
			opts.append("Did he fall, or was he helped?"); keys.append("fall")
		if not Game.flag("shah_palm"):
			opts.append("Anything else?"); keys.append("else")
		opts.append("Thanks, Anita."); keys.append("done")
		var c: int = await main.choose(opts)
		await main.say(opts[c])
		match keys[c]:
			"how":
				Game.set_flag("shah_how")
				await _shah("Backward down fourteen wooden stairs. Skull fracture at the bottom, neck too. He'd have been gone before he stopped moving.")
				await _shah("Here. His keys were in his cardigan. I'm done with them.")
				Game.set_flag("got_gus_keys")
				await main.give("gus_keys")
			"when":
				await _shah("Between one-fifteen and one-forty-five. The roof door's been letting the rain in on him, so don't hold me to the minute.")
				main.clue("clue_tod_gus")
			"fall":
				await _shah("Old men fall. But old men fall forward, Ray, they grab for the rail. He went over backward.")
				await _shah("Two fresh bruises on the breastbone, side by side. The heels of two hands. Small hands.")
				await main.say("Somebody pushed him.")
				await _shah("Somebody put both hands on his chest and shoved. Facing him.")
				main.clue("clue_pushed")
			"else":
				Game.set_flag("shah_palm")
				await _shah("His right hand. Something scratched his palm, small and sharp, with points. And he smells of cigar.")
				await main.say("Points.")
				await _shah("Like a little star. I don't guess, Ray. I just notice.")
			"done":
				await _shah("He had a nice face. Find out who he made it at, last.")
				return


# --- Puzzle 3.1: the desk ---------------------------------------------------------------
func _eviction_letter() -> void:
	await main.player.play_action("use")
	await main.say("Bills, invoices, a racing form from 1997. And on top, where he'd want to see it every morning...")
	main.ui.show_paper("PRYCE DEVELOPMENT",
			"FINAL NOTICE TO VACATE\n\nPursuant to the pending Hollywood Core rezoning, Council District 13, the lease on the premises terminates in thirty (30) days.\n\nT. Whitaker, Acquisitions",
			"Certified mail. Delivered, Thursday, 10:14 a.m.", Color(0.2, 0.25, 0.55))
	await main.say("Last Thursday. A week old. If Pryce wanted Gus gone, all they had to do was wait twenty-three days.")
	main.ui.hide_paper()
	main.clue("clue_eviction")


func _catalogue() -> void:
	await main.player.play_action("use")
	await main.say("Calloway's Auctions, Beverly Hills. \"Hollywood Legends, Fall Season.\" Came in today's mail, still in its plastic.")
	main.ui.show_paper("Calloway's: Private Sales, Summer Season",
			"[photo of an Oscar]\nAcademy Award statuette, Best Supporting Actor, 1954. Base serial No. 734. Sold by private treaty.",
			"734?? THREE WEEKS AGO?? IT'S IN MY CASE.")
	await main.say("A page turned down at the corner. Red ink, shaky capitals.")
	await main.say("Gus found it tonight.")
	main.ui.hide_paper()
	Game.set_flag("got_catalogue")
	await main.give("catalogue", false)


func _brenner_card() -> void:
	## The optional seed: the business card under the letter.
	await main.player.play_action("use")
	await main.say("Under the letter, a business card. Cream stock, raised blue type.")
	main.ui.show_paper("WALTER BRENNER", "LAPD (Ret.)\nSecurity Consultant, Pryce Development",
			"On the back, in ballpoint: \"Gus. Think it over. Nobody else is going to offer. W.\"", Color(0.15, 0.2, 0.5))
	await main.say("A cop's card, from a cop who isn't one anymore.")
	main.ui.hide_paper()
	Game.set_flag("got_brenner_card")
	await main.give("brenner_card", false)
	if Game.flag("got_ride_receipt"):
		await main.wait(1.0)
		await main.say("Walter.")
		await main.wait(1.0)
		await main.say("Lot of Walts in this town.")


# --- Puzzle 3.2: Gus's phone --------------------------------------------------------------
const CALLS := ["Out  12:52 AM  PEARL CELL  3:04", "Out  12:40 AM  CALLOWAY'S  0:41", "In   4:15 PM  MORTY K.  1:12",
		"In   11:02 AM  PRYCE DEV  0:08"]


func _phone() -> void:
	await main.player.play_action("use")
	var tab := 0
	while true:
		var body := "Recent calls" if tab == 0 else "1 saved message"
		var rows: Array = CALLS if tab == 0 else ["Thu  PRYCE DEV  0:22"]
		var pick: String = await main.device("Gus's phone", ["Calls", "Voicemail"], tab, body, rows)
		if pick == "close":
			break
		if pick.begins_with("tab:"):
			tab = int(pick.substr(4))
			continue
		var i := int(pick.substr(4))
		if tab == 1:
			await main.voice("Mr. Lindqvist, Trent Whitaker again. Thirty days. Please don't make this ugly.", Vector2(1530, 330),
					Color(0.7, 0.74, 0.8))
			await main.say("He's polite about ugly. That's how you know he does it for a living.")
		elif i <= 1:
			if not Game.flag("clue_phone_log"):
				await main.say("Twelve-forty, Calloway's. Nobody answers an auction house at midnight, so he left a message.")
				await main.say("Twelve fifty-two, Pearl. Three minutes.")
				main.clue("clue_phone_log")
				await main.say("She told me she went home at nine and came back at two-fifteen for her pictures. She left out the part where Gus called.")
			else:
				await main.say("Calloway's at twelve-forty. Pearl at twelve fifty-two.")
		elif i == 2:
			await main.say("Morty, at four in the afternoon. A minute of arguing about something, I'd bet.")
		else:
			await main.say("Pryce, eight seconds. Gus hung up on them.")
	main.ui.hide_device()


# --- Puzzle 3.3: the UV lamp --------------------------------------------------------------
func _drawer() -> void:
	await main.player.play_action("use")
	await main.say("A cigar box, a loupe, and a handheld UV lamp. Masking tape on it, in Gus's hand:")
	main.ui.show_paper("", "MODERN INK GLOWS.\nOLD INK DOESN'T.\nTRUST NOBODY.  G.", "", Color.BLACK)
	await main.say("\"Modern ink glows. Old ink doesn't. Trust nobody.\"")
	main.ui.hide_paper()
	Game.set_flag("got_uv_lamp")
	await main.give("uv_lamp", false)
	await main.say("Trust nobody. He wrote it on a lamp, then trusted somebody.")


# --- Puzzle 3.4: the gold pen ---------------------------------------------------------------
func _gold_pen() -> void:
	if not Game.flag("clue_uv_fakes"):
		await main.say("Nothing to compare it to yet.")
		return
	if not Game.flag("clue_headshots_left"):
		await main.say("Let me see what's in there first.")
		return
	if Game.flag("clue_gold_pen"):
		await main.say("Same gold. Same hand.")
		return
	await main.player.play_action("use")
	main.ui.show_closeup(Case3.UV_HEADSHOT)
	await main.say("Her autograph on the headshots glows the same gold as Bogart's on the wall.")
	await main.say("Same pen. Same hand, practicing.")
	main.ui.hide_paper()
	main.clue("clue_gold_pen")
