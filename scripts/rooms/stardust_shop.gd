extends Room
## Stardust Memorabilia, Hollywood Boulevard (Case 3, scenes 2 and 5). Gus Lindqvist's shop, the Oscar case empty.
## Puzzle 2.1: the door glass is out on the sidewalk, and the case was opened with a key: clue_staged.
## Puzzle 2.2: the catalogue on the certificate (No. 734 twice). Puzzle 2.3: the UV lamp on the signed photo wall.
## Puzzle 2.4: Morty bought the real Oscar. Scene 5: Pearl's story taken apart in three ordered steps (the phone log or
## her headshots, then the floating "Oscar", then the earring), Park takes her out, and the front door leads back to
## Room 214. Pearl, Park and Morty are overlays (Pearl in the chair, then standing for the cuffs).

@onready var pearl_chair: Sprite2D = $Actors/Pearl_chair
@onready var pearl_stand: Sprite2D = $Actors/Pearl_stand
@onready var park: Sprite2D = $Actors/Park
@onready var morty: Sprite2D = $Morty
var _wander := 0         ## actions since the last hint (Ray nudges once per stuck point)


func _ready() -> void:
	super._ready()
	_sync()


func _sync() -> void:
	var gone := Game.flag("pearl_arrested")
	pearl_chair.visible = not gone and not Game.flag("pearl_stands")
	pearl_stand.visible = not gone and Game.flag("pearl_stands")
	park.visible = not gone
	morty.visible = not Game.flag("morty_lyle")
	hotspot("pearl").enabled = pearl_chair.visible
	hotspot("pearl_stand").enabled = pearl_stand.visible
	hotspot("park").enabled = park.visible
	hotspot("morty").enabled = morty.visible
	hotspot("chair").enabled = not pearl_chair.visible


func on_enter(from_room: String) -> void:
	if from_room == "drive" and not Game.flag("met_park3"):
		Game.set_flag("met_park3")
		await main.wait(0.4)
		await main.say("Stardust Memorabilia. Sixty years of other people's dreams, sold by the square inch.")
		await _park("Detective. Small city tonight.")
		await main.say("It always is, after midnight.")
		await _park("Gus Lindqvist, seventy-one, the owner. He's in back, at the bottom of the roof stairs. Dr. Shah's with him.")
		await _park("The 911 call came in at two-nineteen from his assistant, Pearl Danvers. I got here at two twenty-six. The door was like that, and the case was empty.")


func interact(hs: Hotspot, verb: String, item: String) -> void:
	if not hs.id in ["pearl", "pearl_stand", "morty", "park"]:
		await _maybe_hint()
	match hs.id:
		"pearl", "pearl_stand":
			await _pearl_hotspot(verb, item)

		"park":
			if verb == "look":
				await main.say("Officer Park. Same rain cape, still in the neighborhood.")
			elif item != "":
				await main.say("She's holding the door, not the evidence.")
			else:
				await _talk_to_park()

		"morty":
			if verb == "look":
				await main.say("Bathrobe, loafers, no socks. He keeps looking past me at the empty case.")
			elif item == "catalogue":
				if Game.flag("clue_morty_bought"):
					await main.say("He's seen it. He's living it.")
				else:
					await _morty_secret()
			elif item == "fake_oscar":
				await _morty("Is that... that's a prop. Give it here.")
				await main.player.play_action("use")
				await _morty("Two pounds. Gus would've known in a second.")
			elif item != "":
				await default_response(verb, item)
			elif Game.flag("pearl_arrested") and Game.flag("clue_morty_bought") and not Game.flag("morty_lyle"):
				await _morty_last()
			else:
				await _talk_to_morty()

		"display_case":
			if verb == "look":
				await main.say("An empty velvet bed shaped like a statue. A brass plate: \"Lyle Brandt. Best Supporting Actor, 1954. Harbor Lights.\"")
			elif item == "gus_keys":
				await main.player.play_action("use")
				await main.say("The little brass key turns like butter. Same kind Pearl wears around her neck.")
				if not Game.flag("clue_key_opened"):
					main.clue("clue_key_opened")
					await _staged()
			elif item != "":
				await default_response(verb, item)
			elif not Game.flag("clue_key_opened"):
				await main.player.play_action("use")
				await main.say("The lock's clean. No scratches, no pry marks, and the glass is whole. Somebody opened this with a key.")
				main.clue("clue_key_opened")
				await _staged()
			else:
				await main.say("Opened with a key. Lyle didn't let himself out.")

		"certificate":
			if item == "catalogue":
				await _same_serial()
			elif item != "":
				await default_response(verb, item)
			else:
				await main.say("\"Academy Award statuette, Best Supporting Actor, 1954. Lyle Brandt, Harbor Lights. Base serial No. 734. From the Brandt estate, 1988.\"")

		"front_door":
			if item != "":
				await default_response(verb, item)
			elif not Game.flag("clue_glass_out"):
				await main.say("The glass in the door is smashed. Most of it is out on the sidewalk, on the star of a TV cowboy nobody remembers.")
				await main.say("Break into a shop and the glass lands inside. This glass went out.")
				main.clue("clue_glass_out")
				await _staged()
			elif verb == "look":
				await main.say("Smashed. Rain's coming through the hole.")
			elif not Game.flag("pearl_arrested"):
				await main.say("Not yet. Gus is still at the bottom of the stairs.")
			else:
				await main.say("Back to the board.")
				await Case3.drive_back(main)
				await main.change_room("squad_room", "stardust_shop")

		"photo_wall":
			if verb == "look":
				await main.say("Forty years of Hollywood, signed. Bogart, Monroe, Lyle Brandt, and a dozen faces only Gus remembered.")
			elif item == "uv_lamp":
				await _uv_wall()
			elif item != "":
				await default_response(verb, item)
			else:
				await main.say("Gus would've spotted a fake across the room. If he ever looked.")

		"register":
			if verb == "look":
				await main.say("An old brass register. Drawer shut.")
			elif item != "":
				await default_response(verb, item)
			else:
				await main.player.play_action("use")
				await main.say("Two hundred twelve dollars and a roll of quarters. A thief who smashes a door and leaves the cash.")
				main.clue("clue_register")

		"chair":
			if item != "":
				await default_response(verb, item)
			else:
				await main.say("STARDUST, stenciled on the canvas. Nobody's in it now.")

		"counter":
			if verb == "look":
				await main.say("A black bird statuette tagged \"Not THE bird. A bird. $40.\" Gus had a sense of humor.")
			elif item != "":
				await default_response(verb, item)
			else:
				await main.say("I've got enough birds.")

		"window":
			if item != "":
				await default_response(verb, item)
			else:
				await main.say("The Chinese Theatre across the street, dark. The forecourt's handprints full of rain.")

		"curtain":
			if verb == "look":
				await main.say("The back office.")
			elif item != "":
				await default_response(verb, item)
			else:
				await main.change_room("stardust_office", "stardust_shop")

		_:
			await default_response(verb, item)


func _park(line: String) -> void:
	await main.voice(line, speaker_at("park"), Case2.PARK_COLOR)


func _pearl(line: String) -> void:
	await main.voice(line, speaker_at("pearl_stand" if Game.flag("pearl_stands") else "pearl"), Case3.PEARL_COLOR)


func _morty(line: String) -> void:
	await main.voice(line, speaker_at("morty"), Case3.MORTY_COLOR)


func _maybe_hint() -> void:
	## A nudge after a few actions without progress, once per stuck point (the script's hints for the shop).
	var hint := ""
	var key := ""
	if Game.flag("pearl_lie2_broken"):
		if not Game.flag("pearl_arrested"):
			key = "hint_shop_step3"
			hint = "She says he fell. Shah says he was pushed. Something of hers says where."
	elif Game.flag("pearl_lie1_broken"):
		key = "hint_shop_step2"
		hint = "Her story keeps getting shorter. Lyle might shorten it more."
	elif Game.flag("clue_glass_out") and not Game.flag("clue_key_opened"):
		key = "hint_shop_case"
		hint = "Out through the door. I wonder what came out of the case."
	elif Game.has_item("catalogue") and not Game.flag("clue_same_serial"):
		key = "hint_shop_serial"
		hint = "Calloway's has a number for Lyle. So does Gus."
	if key == "" or Game.flag(key):
		_wander = 0
		return
	_wander += 1
	if _wander >= 4:
		_wander = 0
		Game.set_flag(key)
		await main.say(hint)


# --- Puzzle 2.1: broken in, or broken out ---------------------------------------------
func _staged() -> void:
	if Game.flag("clue_glass_out") and Game.flag("clue_key_opened") and not Game.flag("clue_staged"):
		await main.wait(0.4)
		await main.say("Glass out on the sidewalk. The case opened with a key. Nobody broke in here.")
		await main.say("Somebody with a key broke out, and wanted it to look the other way.")
		main.clue("clue_staged")


# --- Puzzle 2.2: two of the same ---------------------------------------------------------
func _same_serial() -> void:
	if Game.flag("clue_same_serial"):
		await main.say("One number, two statues. Only one of them was real.")
		return
	await main.player.play_action("use")
	main.ui.show_paper("Calloway's: Private Sales, Summer Season", "Academy Award statuette, Best Supporting Actor, 1954. Base serial No. 734. Sold by private treaty.",
			"734?? THREE WEEKS AGO?? IT'S IN MY CASE.")
	await main.say("Calloway's: \"Base serial No. 734. Sold by private treaty.\" Three weeks ago. Gus's certificate: No. 734.")
	await main.say("Every Oscar since 1949 has its own number, like a badge.")
	main.ui.hide_paper()
	await main.say("One statue, two places. Either Calloway's sold a fake, or Gus was saying good night to one.")
	main.clue("clue_same_serial")
	await main.say("And since 1950, winners sign a paper: if you sell it, the Academy gets first refusal for a dollar. Nobody sells one in public. That's why it went quiet.")


# --- Puzzle 2.3: the wall of fame under UV -----------------------------------------------
func _uv_wall() -> void:
	await main.player.play_action("use")
	main.ui.show_closeup(Case3.UV_WALL)
	await main.say("Old ink sits dark under UV. Most of these do.")
	await main.say("Three light up like a premiere: Lyle Brandt, Bogart, Monroe. All the same gold.")
	await main.say("Modern paint pen, not old fountain ink. Good fakes, and new ones.")
	main.ui.hide_paper()
	main.clue("clue_uv_fakes")


# --- Officer Park -------------------------------------------------------------------------
func _talk_to_park() -> void:
	while true:
		var opts := []
		var keys := []
		if not Game.flag("park3_morty"):
			opts.append("Who's the man in the bathrobe?"); keys.append("morty")
		if not Game.flag("park3_canvass"):
			opts.append("Anything from the canvass?"); keys.append("canvass")
		if Game.flag("clue_eviction") and not Game.flag("clue_whitaker_alibi"):
			opts.append("The developer's man."); keys.append("whitaker")
		opts.append("That'll do."); keys.append("done")
		var c: int = await main.topics(opts)
		if c < 0:
			return
		await main.say(opts[c])
		match keys[c]:
			"morty":
				Game.set_flag("park3_morty")
				await _park("Morty Kahn. Owns the collectibles shop three doors down. He came out when he saw the lights.")
				await _park("He keeps asking if \"it\" is gone. I don't think he means Mr. Lindqvist.")
			"canvass":
				Game.set_flag("park3_canvass")
				await _park("The boulevard's shut. There's a Charlie Chaplin who lives next door. He's out on his fire escape, and he says he'll only talk to \"the man in charge.\"")
				await main.say("That's never me.")
				await _park("Tonight it is. You can see his fire escape from Mr. Lindqvist's roof.")
			"whitaker":
				await main.say("There's an eviction notice on Gus's desk from Pryce Development. Their man's Trent Whitaker. Where was he tonight?")
				await _park("Already asked. Miss Danvers mentioned him. Pryce has a night security desk; the supervisor sent me stills in four minutes.")
				await _park("Whitaker's car went into the Pryce Tower garage in Century City at ten fifty-eight. He's on their elevator camera at three-oh-two a.m., still in his tie.")
				await main.say("Four minutes. Nobody's that helpful at three in the morning.")
				await _park("He said they \"always cooperate with the department.\" Like he'd said it before.")
				main.clue("clue_whitaker_alibi")
			"done":
				await _park("I'll keep the door, Detective. Mr. Kahn keeps trying to come in.")
				return


# --- Morty Kahn, through the broken door --------------------------------------------------
func _talk_to_morty() -> void:
	if not Game.flag("met_morty"):
		Game.set_flag("met_morty")
		await _morty("Is it gone? Tell me it's not gone.")
		await _morty("I'm not going anywhere, young lady. I've known Gus fifty years.")
	while true:
		var opts := []
		var keys := []
		if not Game.flag("morty_who"):
			opts.append("Who are you?"); keys.append("who")
		if not Game.flag("clue_morty_offer"):
			opts.append("You wanted the Oscar."); keys.append("offer")
		if not Game.flag("clue_morty_alibi"):
			opts.append("Where were you tonight?"); keys.append("alibi")
		if Game.flag("clue_same_serial") and not Game.flag("clue_morty_bought"):
			opts.append("Calloway's sold No. 734."); keys.append("bought")
		if Game.flag("clue_morty_bought") and not Game.flag("clue_weight"):
			opts.append("What does a real one weigh?"); keys.append("weight")
		opts.append("Good night, Morty."); keys.append("done")
		var c: int = await main.topics(opts)
		if c < 0:
			return
		if keys[c] != "bought":
			await main.say(opts[c])
		match keys[c]:
			"who":
				Game.set_flag("morty_who")
				await _morty("Morty Kahn. Kahn's Collectibles, three doors down. Gus and I have been fighting over the same estate sales since Nixon.")
			"offer":
				await _morty("Wanted it? In March I offered him two hundred fifty thousand dollars. Cash. He said he'd be buried with it.")
				await main.wait(0.5)
				await _morty("Stubborn old Swede.")
				main.clue("clue_morty_offer")
			"alibi":
				await _morty("Upstairs, in my pajamas, losing a Kurosawa script to a dentist in Osaka. Look.")
				main.ui.show_device("Yamato Online Auctions", [], 0,
						"Lot 118: \"Ran\" (1985), shooting script, annotated.\n\nYour bid history:",
						["12:31 AM   bid placed", "12:58 AM   bid placed", "1:20 AM   bid placed", "1:44 AM   bid placed",
						"2:09 AM   You have been outbid."], false, Color(0.75, 0.2, 0.25))
				await _morty("Two hours of my life. I came down when I saw the lights.")
				main.ui.hide_device()
				main.clue("clue_morty_alibi")
			"bought":
				await _morty_secret()
			"weight":
				await _morty("Eight and a half pounds. Solid britannium, gold plate. You could stop a door with it.")
				await _morty("The props they sell on this boulevard are hollow resin, two pounds. They'd float in your bathtub.")
				main.clue("clue_weight")
			"done":
				await _morty("Find who did this. And whatever was in that case, I want to know what it was.")
				return


func _morty_secret() -> void:
	## Puzzle 2.4: Morty's the buyer, and Pearl runs the shop's email.
	await main.say("Calloway's private sales, three weeks ago. Lyle Brandt's Oscar, serial number 734. Somebody bought it, Morty.")
	await main.wait(1.2)
	await _morty("It was me. All right? Me.")
	await _morty("A broker at Calloway's called. A collection selling quietly, no names. I wired a hundred and eighty thousand to something called Stardust Archive.")
	await main.say("And you thought?")
	await _morty("I thought the eviction finally broke him. Too proud to sell to me to my face, so I let him not. I never said a word.")
	await _morty("Fifty years, and I never said a word.")
	await main.wait(0.5)
	await _morty("It's in my safe right now, Detective. It's real. I'd know.")
	await main.say("Who handles the shop's email?")
	await _morty("Gus? Gus thought email was a fad. The girl does it. Pearl. The website, the listings, everything with a screen.")
	main.clue("clue_morty_bought")


func _morty_last() -> void:
	## Optional, after the arrest: Morty knows what to do with the real one.
	await _morty("Was it real? The one in the case?")
	await main.say("The one in your safe is.")
	await main.wait(1.2)
	await _morty("He said he'd be buried with it.")
	await main.say("Then you know what to do, Morty.")
	await main.ui.fade_to(1.0, 0.5)
	Game.set_flag("morty_lyle")
	_sync()
	await main.ui.fade_to(0.0, 0.5)


# --- Pearl Danvers ------------------------------------------------------------------------
func _pearl_hotspot(verb: String, item: String) -> void:
	if verb == "look":
		if Game.has_item("star_earring") or Game.flag("clue_bare_ear"):
			await main.say("One gold star in her right ear. Under the hair, the left lobe's bare, torn and red.")
			main.clue("clue_bare_ear")
		else:
			await main.say("Pearl Danvers. Patrol blanket, hair down over one side of her face. An hour of crying and her mascara hasn't moved.")
		return
	match item:
		"":
			await _talk_to_pearl()
		"gus_keys":
			await _pearl("Those are Gus's. Please put them away.")
		"fake_oscar":
			await _step2()
		"star_earring":
			await _step3()
		_:
			await main.say("She's had enough things shoved at her tonight.")


func _talk_to_pearl() -> void:
	if not Game.flag("met_pearl"):
		Game.set_flag("met_pearl")
		await _pearl("Are you the detective? They keep saying \"the detective's coming,\" like it's a casting call.")
		await _pearl("Sorry. I'm sorry. I don't know what I'm saying.")
		await main.say("Ray Kessler. Take your time, Miss Danvers.")
		await _pearl("Pearl. Gus calls me Pearlie.")
		await main.wait(0.8)
		await _pearl("Called.")
	while true:
		var opts := []
		var keys := []
		if not Game.flag("clue_pearl_story"):
			opts.append("What happened tonight?"); keys.append("story")
		if not Game.flag("pearl_years"):
			opts.append("How long did you work for Gus?"); keys.append("years")
		if not Game.flag("clue_keyholders"):
			opts.append("Who has keys to the Oscar case?"); keys.append("keys")
		if not Game.flag("pearl_who"):
			opts.append("Who'd want the Oscar?"); keys.append("who")
		if Game.flag("clue_pearl_story") and not Game.flag("pearl_lie1_broken"):
			if Game.flag("clue_phone_log"):
				opts.append("Gus called you at twelve fifty-two."); keys.append("call")
			if Game.flag("clue_headshots_left"):
				opts.append("Your headshots are still in your locker."); keys.append("headshots")
		if Game.flag("pearl_lie1_broken") and not Game.flag("pearl_lie2_broken") and Game.has_item("fake_oscar"):
			opts.append("Lyle was in the water tank."); keys.append("step2")
		if Game.flag("pearl_lie2_broken") and Game.has_item("star_earring"):
			opts.append("Gus didn't fall."); keys.append("step3")
		opts.append("I'll be back."); keys.append("done")
		var c: int = await main.topics(opts)
		if c < 0:
			return
		var k: String = keys[c]
		if k in ["story", "years", "keys", "who", "done"]:
			await main.say(opts[c])
		match k:
			"story":
				await _pearl("We closed at nine. I went home. I've got an audition at nine this morning, a pharmacy ad, \"concerned mom\", and I left my headshots in my locker.")
				await _pearl("So I came back. Two-fifteen, maybe? The door was smashed. Lyle was gone. And Gus was at the bottom of the stairs. I called 911.")
				await main.say("Two in the morning, for headshots.")
				await _pearl("You don't know casting directors.")
				main.clue("clue_pearl_story")
			"years":
				Game.set_flag("pearl_years")
				await _pearl("Six years. I came in to sell him a lobby card from my grandmother's attic, and he gave me a job instead. Said I had an eye.")
				await _pearl("He trusted me with everything.")
				await main.wait(0.8)
				await _pearl("Everything.")
			"keys":
				await _pearl("Gus has one. I have one. That's it. Gus didn't let anyone else near Lyle.")
				await main.say("Lyle?")
				await _pearl("Lyle Brandt. The Oscar. Gus called it by name. \"Morning, Lyle. Night, Lyle.\"")
				main.clue("clue_keyholders")
			"who":
				Game.set_flag("pearl_who")
				await _pearl("Everybody. Morty out there's been begging Gus for years. And the developer. Pryce.")
				await _pearl("Their man Whitaker was here yesterday yelling that Gus had thirty days. Gus told him to put it in writing, and he said it already was.")
			"call", "headshots":
				await _step1(k)
				if Game.flag("pearl_lie1_broken"):
					return
			"step2":
				await _step2()
				return
			"step3":
				await _step3()
				return
			"done":
				await _pearl("I'm not going anywhere.")
				await _pearl("Where would I go?")
				return


# --- Scene 5: breaking Pearl, three steps in order -------------------------------------------
func _step1(how: String) -> void:
	if how == "call":
		await main.say("Gus called you at twelve fifty-two. Three minutes.")
	else:
		await main.say("You came back at two in the morning for your headshots. They're in your locker, Pearl. All twenty.")
	await main.wait(1.0)
	await _pearl("Okay. Okay! He called. He was upset, he'd seen something in a catalogue, he wasn't making sense. So I came in. At one.")
	await _pearl("We talked in the office, he calmed down, he went up for his cigar, and I went home. And at two he wasn't answering, so I came back, and...")
	await main.say("And the door was smashed.")
	await _pearl("It was like that!")
	Game.set_flag("pearl_lie1_broken")


func _step2() -> void:
	if not Game.flag("pearl_lie1_broken"):
		await _pearl("You found him! Where was he?")
		await main.say("Later.")
		return
	if Game.flag("pearl_lie2_broken"):
		await main.say("She's seen him. She knows where he's been.")
		return
	await main.player.play_action("use")
	await main.say("Lyle was in the water tank on the roof. He floats, Pearl. Real ones don't.")
	if Game.flag("clue_morty_bought"):
		await main.say("The real one went through Calloway's three weeks ago. A buyer wired a hundred and eighty thousand dollars to \"Stardust Archive\". You run the shop's email.")
	else:
		await main.say("The real one went through Calloway's three weeks ago.")
	await main.say("Nobody broke in. You opened the case with your key, broke the glass from the inside, and put Lyle where nobody would look.")
	await main.say("Because you couldn't carry him down the boulevard past every camera in Hollywood.")
	await main.wait(1.5)
	await _pearl("Yes. Okay. Yes. I sold things. I sold Lyle.")
	await _pearl("But I didn't hurt him. When I got here at one, he was already at the bottom of the stairs. He'd fallen.")
	await _pearl("He's seventy-one, he goes up there in the rain in his slippers. And I thought, they'll look at the case, and then they'll look at me, and I'll go to prison for a fall.")
	await _pearl("So I made it a robbery. That's all I did. I swear to God, that's all I did.")
	Game.set_flag("pearl_lie2_broken")
	await main.say("That's a better story. It's still a story.")


func _step3() -> void:
	if not Game.flag("pearl_lie2_broken"):
		await main.say("She'll have a reason for that. Let her run out of reasons first.")
		return
	await main.say("Gus didn't fall. He went down those stairs backward, with the heels of two small hands on his chest.")
	await main.say("And in his right palm there's a scratch shaped like a little star.")
	await main.player.play_action("use")
	await main.say("It was at the top of his stairs, Pearl. Push your hair back.")
	await main.wait(1.6)
	await main.say("Her left earlobe is torn and red.")
	main.clue("clue_bare_ear")
	await _pearl("He kept saying \"How long? How long?\" So I told him. Eighteen months. A Bogart letter first, for rent. Then the photos. Then Lyle.")
	await _pearl("I'm good, you know? I'm good at being somebody else. It's the only thing I've ever been good at.")
	await _pearl("He said he'd call the police in the morning. He took my arm, and his hand caught my earring, and it tore, and it hurt, and I just...")
	await _pearl("I put my hands on him. To get him off me. And then he wasn't there. He was just gone. Down the stairs. One slipper.")
	await main.wait(1.2)
	await _pearl("I'm thirty-four. I've died on four cop shows. Corpse number two. I've never had a line that wasn't a scream.")
	await _pearl("Was I any good tonight?")
	await main.say("Gus thought so. For six years.")
	await main.wait(0.6)
	await _park("Pearl Danvers. Stand up for me, please.")
	await main.ui.fade_to(1.0, 0.4)
	Game.set_flag("pearl_stands")
	_sync()
	await main.ui.fade_to(0.0, 0.4)
	await main.wait(0.8)
	await _pearl("Night, Lyle.")
	await main.ui.fade_to(1.0, 0.8)
	Game.set_flag("pearl_arrested")
	_sync()
	await main.wait(0.8)
	await main.ui.fade_to(0.0, 0.8)
	await main.say("Forty years of fakes and favorites, and a note on a lamp that said trust nobody.")
	await main.say("He trusted one person.")
