extends Room
## The Blue Note's back room and back hall (Case 5, scene 3). Shah on how Sal died (clue_choke, the bar-arm choke).
## Puzzle 3.1: the stool, Sal's clean palms, Danny's locker and Pryce's letter on the desk; with the choke and two of
## those Ray sums it up (clue_staged_hanging). Puzzle 3.2: the alley door, the umbrella and the prints to the cooler.
## Puzzle 3.3: talking Nina out of the walk-in (nina_out); then her phone shows the 1:52 call (clue_nina_call), the
## gate to Room 214. Nina, Park (in the hall once Nina is out) and the cooler door are overlays.

@onready var nina: Sprite2D = $Actors/Nina
@onready var park: Sprite2D = $Actors/Park
@onready var cooler: Sprite2D = $Cooler_shut
var _hints := 0
var _knock_tried := false


func _ready() -> void:
	super._ready()
	_sync()


func _sync() -> void:
	var out := Game.flag("nina_out")
	nina.visible = out
	park.visible = out
	cooler.visible = not out
	hotspot("nina").enabled = out
	hotspot("park").enabled = out


func on_enter(_from_room: String) -> void:
	if not Game.flag("in_back_room"):
		Game.set_flag("in_back_room")
		await main.wait(0.4)
		await _shah("Four, Ray. That's my free coffee.")
		await main.say("I said two more.")
		await _shah("There isn't going to be a fifth. I'm not doing a fifth.")
		await _shah("I'm sorry. I know you liked him.")


func interact(hs: Hotspot, verb: String, item: String) -> void:
	if not hs.id in ["shah", "nina", "cooler"]:
		await _maybe_hint()
	match hs.id:
		"shah":
			if verb == "look":
				await main.say("Dr. Shah, kneeling on a concrete floor for the fourth time tonight.")
			elif item == "tab_book":
				await _shah("I do bodies, Ray, not bookkeeping.")
			elif item != "":
				await default_response(verb, item)
			else:
				await _talk_shah()

		"sal":
			if verb == "look":
				await main.say("Sal Moretti. Sixty-four. Thirty-one years behind that bar.")
			elif item == "tab_book":
				await main.say("You wrote it down, Sal. I'm reading it.")
			elif item != "":
				await default_response(verb, item)
			else:
				await main.player.play_action("pickup")
				await main.say("I lift the edge of the sheet at his hand.")
				await main.say("His palms are clean. A man who hangs himself with clothesline gets rope burn climbing up to it. Sal's hands are cleaner than mine.")
				main.clue("clue_clean_hands")
				await _staged()

		"stool":
			if verb == "look":
				await main.say("A step stool on its side, four feet from where Sal hung. Sal was five foot six. He'd have had to jump for it.")
				main.clue("clue_stool")
				await _staged()
			elif item != "":
				await default_response(verb, item)
			else:
				await main.say("It stays where he kicked it. Where somebody kicked it.")

		"pipe":
			if verb == "look":
				await main.say("A water pipe and two feet of white clothesline where Park cut it. The rest of the coil's on the supply shelf.")
			else:
				await main.say("I'll leave it for the lab.")

		"locker":
			if verb == "look":
				await main.say("Six lockers. One's open with keys hanging from it.")
			elif item != "":
				await default_response(verb, item)
			else:
				await main.player.play_action("use")
				await main.say("D. REYES on a strip of tape. Sal's own keys hanging from the lock: bar, cooler, lockers.")
				await main.say("Inside, a spare shirt and a stack of sheet music, every page turned and put back crooked.")
				await main.say("Sal knew what was in Danny's locker. Somebody who didn't wanted to look.")
				main.clue("clue_locker")
				await _staged()

		"desk":
			if verb == "look":
				await main.say("A steel desk, a gooseneck lamp, a cash box and a pile of mail.")
			elif item != "":
				await default_response(verb, item)
			else:
				await main.player.play_action("use")
				await main.say("A cash box with Tuesday's float still in it.")
				await main.say("And a letter from Pryce Development's lawyers, offering to buy out the last six years of Sal's lease. Across it, in red: NO. Underlined three times.")
				main.clue("clue_sal_no")
				main.clue("clue_cash")
				if Game.flag("clue_eviction"):
					await main.say("Same letterhead as Gus's eviction.")
				await _staged()

		"kegs":
			if verb == "look":
				await main.say("Beer, rye, and enough Campari to float a gondola.")
			else:
				await main.say("Nobody's hiding behind the Campari.")

		"alley_door":
			if verb == "look":
				await main.say("Steel door to the alley, deadbolted from inside with a key. Nobody left this way.")
				main.clue("clue_back_locked")
			else:
				await main.say("Locked with a key, from in here. I'll leave it that way.")

		"hooks":
			if verb == "look":
				if not Game.flag("clue_umbrella"):
					await main.say("Sal's coat. And a red umbrella, still dripping into a puddle on the floor.")
					await main.say("It's been raining since midnight, and the bar's been dark since Tuesday. Somebody came in out of the rain tonight.")
					main.clue("clue_umbrella")
				else:
					await main.say("Small wet sneaker prints, from the alley door to the cooler. They don't come back.")
					Game.set_flag("saw_prints")
			else:
				await main.say("It's her umbrella. She'll want it.")

		"cooler":
			if Game.flag("nina_out"):
				await main.say("Limes, kegs, and a crate where she sat for an hour and a half.")
			elif verb == "look":
				await main.say("The walk-in. The light's on inside and the hasp is open. Bartenders don't leave a cooler lit.")
			elif item != "":
				await main.say("It won't open. Someone's holding the handle from the inside.")
			else:
				if not Game.flag("cooler_tried"):
					Game.set_flag("cooler_tried")
					await main.player.play_action("use")
					await main.say("It won't open. Someone's holding the handle from the inside.")
				await _cooler()

		"nina":
			if verb == "look":
				await main.say("Nina Alvarez, in my raincoat and Shah's blanket. Her lips are getting their color back.")
			elif item == "tab_book":
				await _nina("D.R., decaf. Every night. Sal's little joke.")
			elif item == "set_list":
				await _nina("His set list. The bit at the bottom is Sal's tune. I never could read his music.")
			elif item != "":
				await default_response(verb, item)
			else:
				await _talk_nina()

		"park":
			if verb == "look":
				await main.say("Officer Park, guarding a cooler that's empty now.")
			elif item != "":
				await default_response(verb, item)
			else:
				await main.voice("The girlfriend was in the cooler the whole time, Detective. Hiding. That's not a great look.",
						speaker_at("park"), Case2.PARK_COLOR)
				await main.say("She was hiding from the man who did this. She's the only one in here with any sense.")

		"bar_door":
			if verb == "look":
				await main.say("Back to the bar.")
			elif item != "":
				await default_response(verb, item)
			else:
				await main.change_room("blue_note_bar", "blue_note_back")

		_:
			await default_response(verb, item)


# --- Shah ------------------------------------------------------------------------------------------------------------
func _shah(line: String) -> void:
	await main.voice(line, speaker_at("shah"), Case2.SHAH_COLOR)


func _talk_shah() -> void:
	while true:
		var opts := []
		var keys := []
		if not Game.flag("clue_choke"):
			opts.append("How did he die?"); keys.append("how")
		if not Game.flag("clue_sal_tod"):
			opts.append("When?"); keys.append("when")
		if not Game.flag("clue_let_in"):
			opts.append("Did he fight?"); keys.append("fight")
		if not Game.flag("shah5_else"):
			opts.append("Anything else?"); keys.append("else")
		opts.append("Thanks, Anita."); keys.append("done")
		var c: int = await main.topics(opts)
		if c < 0:
			return
		match keys[c]:
			"how":
				await main.say("How did he die?")
				await _shah("Not the rope. The rope mark is a clean line with no bruising under it, no bleeding. He was dead when it went on.")
				await _shah("But here, straight across the front of the throat, a band of bruising, and the small bones are cracked. A forearm. From behind.")
				await main.say("A choke.")
				await _shah("A bar-arm choke. A police hold, Ray, an old one. The department banned it in 1982 after it killed too many people.")
				await _shah("You never learned it. Whoever did this learned it before you could shave.")
				main.clue("clue_choke")
				await _staged()
			"when":
				await main.say("When?")
				await _shah("Between half past three and four. The back room's cold, so give me ten minutes either way.")
				main.clue("clue_sal_tod")
			"fight":
				await main.say("Did he fight?")
				await _shah("No defensive wounds. Nothing under his nails. He turned his back on whoever it was.")
				await _shah("Like your rideshare driver. You don't see it coming from someone you've let in.")
				main.clue("clue_let_in")
			"else":
				Game.set_flag("shah5_else")
				await main.say("Anything else?")
				await _shah("Whoever did this put a man on a pipe and made it look like his choice. That's somebody who's stood in a lot of rooms like this one, writing the word \"suicide.\"")
			_:
				await main.say("Thanks, Anita.")
				if not Game.flag("nina_out"):
					await _shah("And Ray? Somebody's in that cooler. I heard it shift when I came in. Park thinks it's the compressor. Park is very young.")
					Game.set_flag("shah_cooler")
				return


func _staged() -> void:
	## Puzzle 3.1: once Shah has said how, and two of the four observations are in.
	if Game.flag("clue_staged_hanging") or not Game.flag("clue_choke"):
		return
	var n := 0
	for id in ["clue_stool", "clue_clean_hands", "clue_locker", "clue_sal_no"]:
		if Game.flag(id):
			n += 1
	if n < 2:
		return
	await main.say("No forced entry. Sal let him in, turned his back on him, and the man used a hold they stopped teaching in 1982.")
	await main.say("Then he dressed it up as a suicide, the way he'd seen a hundred of them.")
	main.clue("clue_staged_hanging")


# --- Puzzle 3.3: who's in the cooler ---------------------------------------------------------------------------------
func _nina(line: String) -> void:
	var at := speaker_at("nina") if Game.flag("nina_out") else speaker_at("cooler")
	await main.voice(line, at, Case5.NINA_COLOR)


func _cooler() -> void:
	await main.say("Somebody in there?")
	await main.wait(0.8)
	await _nina("Go away. I've got a knife.")
	while true:
		var opts := ["LAPD. Come on out.", "Nina? It's Ray Kessler."]
		if not _knock_tried:
			opts.append("(Knock two slow, three fast.)")
		var c: int = await main.choose(opts)
		var pick: String = opts[c]
		if pick == "LAPD. Come on out.":
			await main.say("LAPD. Come on out.")
			await _nina("That's what he said. He said he was police.")
		elif pick.begins_with("(Knock"):
			_knock_tried = true
			await main.narrate("I raise my hand to the door and stop. No. That knock's done enough tonight.")
		else:
			await main.say("Nina? It's Ray Kessler.")
			if Game.flag("met_nina"):
				await main.wait(0.8)
				await _nina("...Kessler. The payphone. \"Two days late.\"")
				await main.say("Later than that now. Come out, Nina. You're freezing.")
				break
			await _nina("He said he worked with Ray Kessler. He knew your name. How do I know you're you?")
			var done := false
			while not done:
				var d: int = await main.choose(["I called you from the payphone across the street.", "I know the knock.",
						"I'm the one who talked to Sal."])
				match d:
					0:
						await main.say("I called you from the payphone across the street.")
						await _nina("...The payphone. Nobody calls from that payphone except Danny. And you.")
						done = true
					1:
						await main.say("I know the knock.")
						await _nina("Everybody knows the knock now. That's the problem.")
					_:
						await main.say("I'm the one who talked to Sal.")
						await _nina("So did he.")
			break
	await main.ui.fade_to(1.0, 0.5)
	await main.wait(0.4)
	await main.ui.fade_to(0.0, 0.5)
	await main.narrate("The handle turns. A wall of cold comes out. Nina Alvarez, on a crate between the limes and the kegs, lips blue, a paring knife in her fist.")
	await main.narrate("She looks at me a long time. Then she puts the knife down on the crate.")
	await main.say("It leaks at the collar. It's still warmer than this.")
	await _shah("Bring her here, under the lamp. Not you, Ray. Her.")
	await main.ui.fade_to(1.0, 0.5)
	Game.set_flag("nina_out")
	_sync()
	await main.ui.fade_to(0.0, 0.6)


func _talk_nina() -> void:
	if Game.flag("heard_take") and not Game.flag("nina_after_take"):
		Game.set_flag("nina_after_take")
		await _nina("You found it. His song.")
		await main.say("Somebody would have paid a lot never to hear it.")
		await _nina("Was he scared?")
		await main.say("No. He sounded like he'd won.")
		return
	if Game.flag("case5_deduced") and not Game.flag("nina_going"):
		Game.set_flag("nina_going")
		await _nina("Where are you going?")
		await main.say("To give back something of Danny's.")
		await _nina("Come back after. Tell me.")
		await main.say("Everybody wants to be told tonight.")
		return
	while true:
		var opts := []
		var keys := []
		if not Game.flag("clue_nina_heard"):
			opts.append("What happened tonight?"); keys.append("tonight")
		if not Game.flag("clue_young_lady"):
			opts.append("The man who called you."); keys.append("caller")
		if not Game.flag("clue_nina_call"):
			opts.append("Can I see your phone?"); keys.append("phone")
		if not Game.flag("clue_lisbon"):
			opts.append("What did Danny have?"); keys.append("danny")
		if not Game.flag("clue_knock_tune"):
			opts.append("Where does the knock come from?"); keys.append("knock")
		if not Game.flag("clue_takes_app"):
			opts.append("Did Danny record his sets?"); keys.append("sets")
		opts.append("Stay with Dr. Shah."); keys.append("done")
		var c: int = await main.topics(opts)
		if c < 0:
			return
		match keys[c]:
			"tonight":
				await main.say("What happened tonight?")
				await _nina("A man called me before two. He said he was your partner, that you'd sent him to check on Sal, and Sal wouldn't open up. He needed the knock.")
				await _nina("He was so calm. I gave it to him.")
				await _nina("Then I couldn't sleep. I called Sal three times. Sal never picks up the phone, I know that, but I kept calling. At half past three I took a cab and came in the back with my key.")
				await _nina("There was a man in the bar with Sal. I couldn't see him. I heard him. Low and polite, like a doctor with bad news.")
				await _nina("He said, \"What did the kid leave you, Sal?\" And Sal said, \"A tab.\"")
				await _nina("I went into the cooler. I don't know why the cooler.")
				await main.say("Because it locks from the inside.")
				await _nina("Then they went in the back. Something fell. Then nothing for a long time. Then his shoes went right past the cooler door, slowly. Then the front door, a long way off.")
				await _nina("Then Teo screaming. Then police. He said he was police, Ray. What was I supposed to do, come out to police?")
				main.clue("clue_nina_heard")
			"caller":
				await main.say("The man who called you.")
				await _nina("Old. Calm. He called me \"young lady.\" Nobody's called me young lady since Catholic school.")
				await _nina("And it came up on my phone as a police number. I checked it after. That's why I believed him.")
				main.clue("clue_young_lady")
			"phone":
				await main.say("Can I see your phone?")
				await main.player.play_action("pickup")
				main.ui.show_device("Nina's phone", ["Recent calls"], 0, "", ["1:52 AM  Incoming  (323) 555-0186   2 min",
						"2:31 AM  Outgoing  Sal   no answer", "2:50 AM  Outgoing  Sal   no answer",
						"3:10 AM  Outgoing  Sal   no answer", "3:22 AM  Outgoing  Yellow Cab"], false)
				await main.say("Three-two-three, five-five-five, oh-one-eight-six. One fifty-two.")
				main.clue("clue_nina_call")
				main.ui.hide_device()
				await main.say("That number's a police line. I'd like to know whose.")
			"danny":
				await main.say("What did Danny have?")
				await _nina("He never told me. He said he'd found a song somebody would pay never to hear again. \"One of three, baby, and then Lisbon.\"")
				await _nina("He'd never been anywhere. He'd never even been to San Diego.")
				main.clue("clue_lisbon")
			"knock":
				await main.say("Where does the knock come from?")
				await _nina("A joke with Sal. Sal cut him off coffee at ten o'clock every night, and Danny said it made him play slow.")
				await _nina("So he wrote Sal a little tune about what Sal served him instead. Five notes. He only ever played it after closing, when the room was empty and Sal was counting the till.")
				await _nina("Sal laughed every single time. Nobody else ever heard it. Then it was how we knocked.")
				main.clue("clue_knock_tune")
			"sets":
				await main.say("Did Danny record his sets?")
				await _nina("Every one. On his phone, on an app. He said one day he'd pick the good ones and make a record.")
				main.clue("clue_takes_app")
			_:
				await main.say("Stay with Dr. Shah.")
				await _nina("Ray. Find him. And don't tell anybody where I am. Not even police. Especially not police.")
				await main.say("I'm police.")
				await _nina("You're you. That's different.")
				return


func _maybe_hint() -> void:
	_hints += 1
	if _hints % 6 != 0:
		return
	if Game.flag("shah_cooler") and not Game.flag("nina_out"):
		await main.say("Shah says something's moving in the cooler. Bartenders don't leave a cooler lit.")
	elif Game.flag("nina_out") and not Game.flag("clue_nina_call"):
		await main.say("She said it came up as a police number. I'd like to see that number.")
	elif Game.flag("clue_nina_call") and Game.flag("clue_choke") and not Game.flag("clue_desk_line"):
		await main.say("A police number at one fifty-two. I know a phone with a long memory. It's on my desk.")
