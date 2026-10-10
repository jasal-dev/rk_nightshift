extends Room
## Pier 9 at dawn (Case 5, scene 8). Talk to Tiny and Vance, then set Danny's dead phone on the bollard at the end of
## the pier: Brenner's gray Lincoln comes down between the containers. Puzzle 8.1: three lies, in order (the 1:52 call;
## the tab book and Shah's choke; Vance and the take), with seed options that only change what's said. Puzzle 8.2: his
## pitch, the phone in the harbor, the .38. Puzzle 8.3: talk him down (three beats) or force his hand (Tiny). He's
## arrested either way; then Tiny's answer (tiny_told) and the sun comes up (pier9_sunrise).
## Overlays: the Lincoln, Brenner (standing, gun drawn, cuffed over the hood), the phone and his coffee on the bollard.

## Left-click verbs shown under the cursor (see Room.verb_for); unlisted hotspots are "use".
const VERBS := {
	"tiny": "talk", "vance": "talk", "brenner": "talk", "brenner_cuffed": "talk", "barrel": "look", "crane": "look",
	"warehouse_sign": "look", "car": "drive"
}

const TINY_COLOR := Color(0.86, 0.74, 0.56)
const VANCE_COLOR := Color(0.78, 0.74, 0.9)

@onready var lincoln: Sprite2D = $Lincoln
@onready var brenner: Sprite2D = $Actors/Brenner
@onready var brenner_gun: Sprite2D = $Actors/Brenner_gun
@onready var brenner_cuffed: Sprite2D = $Actors/Brenner_cuffed
@onready var bollard_phone: Sprite2D = $Bollard_phone
@onready var bollard_cup: Sprite2D = $Bollard_cup
var _pose := "brenner"            ## which Brenner overlay shows while he's on the pier
var _seeds_used: Array[String] = []


func _ready() -> void:
	super._ready()
	_sync()


func _sync() -> void:
	var here := Game.flag("brenner_here")
	var gone := Game.flag("brenner_arrested")
	lincoln.visible = here
	brenner.visible = here and not gone and _pose == "brenner"
	brenner_gun.visible = here and not gone and _pose == "brenner_gun"
	brenner_cuffed.visible = here and not gone and _pose == "brenner_cuffed"
	bollard_phone.visible = Game.flag("phone_on_bollard") and not Game.flag("phone_in_harbor")
	bollard_cup.visible = here
	hotspot("lincoln").enabled = here
	hotspot("brenner").enabled = brenner.visible or brenner_gun.visible
	hotspot("brenner_cuffed").enabled = brenner_cuffed.visible


func on_enter(_from_room: String) -> void:
	if not Game.flag("pier_dawn"):
		Game.set_flag("pier_dawn")
		await main.wait(0.5)
		await main.say("Pier 9. The ocean still smells like diesel and money. At this hour you can see which is which.")


func interact(hs: Hotspot, verb: String, item: String) -> void:
	match hs.id:
		"tiny":
			if verb == "look":
				await main.say("Tiny, in his chair, with the radio. The sign.")
			elif item != "":
				await default_response(verb, item)
			elif Game.flag("brenner_arrested"):
				await _tinys_answer()
			else:
				await _tiny("Detective. You said you'd come tell me.")
				await main.say("In a few minutes. Stay in your chair, Tiny, whatever happens.")
				await main.wait(0.6)
				await _tiny("I'm the sign.")
				Game.set_flag("talked_tiny5")

		"radio":
			if verb == "look":
				await main.say("KJAZZ, low.")
			else:
				await main.say("KJAZZ. Somebody's playing 'Round Midnight. Not as good as Danny did it.")
				await _tiny("Nobody is.")

		"vance":
			if verb == "look":
				await main.say("Vance in the green door, an overcoat over the cardigan, holding his tea like a weapon.")
			elif item == "envelope" or item == "danny_box":
				await _vance("One of three. He only ever paid the first.")
			elif item != "":
				await default_response(verb, item)
			elif Game.flag("brenner_arrested"):
				await _vance("We're square, Detective. Danny paid his debts. So do I.")
				await main.say("Nobody's square tonight.")
				await _vance("Then we're less crooked than we were. In my business that's a good morning.")
			else:
				await _talk_vance()

		"bollard":
			if verb == "look":
				await main.say("An iron bollard at the end of the pier. A good place to put something down and wait.")
			elif Game.flag("brenner_here"):
				await main.say("That's where he left me a coffee.")
			elif item != "" and item != "danny_phone":
				await default_response(verb, item)
			elif not (Game.flag("talked_tiny5") and Game.flag("talked_vance5")):
				await main.say("Tiny and Vance know their places. Then I wait at the end of the pier.")
			else:
				await _arrival()

		"brenner":
			if verb == "look":
				await main.say("Walter Brenner. Six-three in an old belted raincoat, shoes like a parade.")
				await main.say("He looks like somebody's grandfather. He is somebody's grandfather.")
			elif item == "tab_book" and Game.flag("brenner_lie1_broken") and not Game.flag("brenner_lie2_broken"):
				await _lie2()
			elif item == "envelope":
				await _brenner("A piano player's envelope. So he could write.")
			elif item == "reporter_card":
				await _brenner("Going to the papers already? Maureen said you were dramatic.")
			elif item == "danny_box":
				await _brenner("A box of paper. I've filed boxes like that in the dumpster.")
			elif item != "":
				await _brenner("You'll have to do better than that, son.")
			else:
				await _confront()

		"brenner_cuffed":
			if verb == "look":
				await main.say("Walt Brenner, over the hood of his boss's car.")
			else:
				await main.say("Anything you want to say, Walt, save it for a lawyer.")

		"lincoln":
			if verb == "look":
				if Game.flag("clue_big_man"):
					await main.say("A long gray car. Preacher saw it stop on the Fletcher Drive bridge.")
				else:
					await main.say("A gray Lincoln Town Car. Long, clean, and somebody else's.")
			else:
				await main.say("It's not my car. I'll let the lab drive it.")

		"water":
			if item != "":
				await main.say("The harbor's got enough of Danny's things.")
			elif verb == "look":
				await main.say("Black water going pink. Whatever goes in here doesn't come back up.")
			else:
				await main.say("Not today.")

		"barrel":
			await main.say("Cold. Tiny's taking the morning off.")

		"piling":
			if verb == "look":
				await main.say("The boat hook, back where it belongs. Tiny counts.")
			else:
				await main.say("I've fished enough out of this pier.")

		"crane":
			await main.say("The gantry crane, red lights still blinking, though the sky's doing that job now.")

		"containers":
			if verb == "look":
				await main.say("Boxes from Busan and Shenzhen, pink in the dawn.")
			else:
				await main.say("Sealed.")

		"warehouse_sign":
			await main.say("HARBOR MARINE SALVAGE. Vance's front, and his back.")

		"car":
			if verb == "look":
				await main.say("My car, looking worse in daylight.")
			elif Game.flag("brenner_arrested"):
				await main.say("Not yet.")
			else:
				await main.say("I'm not leaving. This is where it ends.")

		_:
			await default_response(verb, item)


func _tiny(line: String) -> void:
	await main.voice(line, speaker_at("tiny"), TINY_COLOR)


func _vance(line: String) -> void:
	await main.voice(line, speaker_at("vance"), VANCE_COLOR)


func _brenner(line: String) -> void:
	await main.voice(line, speaker_at("brenner_cuffed" if _pose == "brenner_cuffed" else "brenner"), Case5.BRENNER_COLOR)


func _talk_vance() -> void:
	if not Game.flag("vance5_hello"):
		Game.set_flag("vance5_hello")
		await _vance("Detective. You look like a man who hasn't slept, and has decided not to.")
	while true:
		var opts := []
		var keys := []
		if not Game.flag("vance5_thanks"):
			opts.append("Thanks for coming."); keys.append("thanks")
		if not Game.flag("vance5_voice"):
			opts.append("The man on the phone."); keys.append("voice")
		if not Game.flag("vance5_sight"):
			opts.append("Stay out of sight."); keys.append("sight")
		opts.append("I'm ready."); keys.append("done")
		var c: int = await main.topics(opts)
		if c < 0:
			return
		match keys[c]:
			"thanks":
				Game.set_flag("vance5_thanks")
				await main.say("Thanks for coming.")
				await _vance("Don't thank me. I don't like men who telephone and ask about my clients. It's bad manners and worse for business.")
			"voice":
				Game.set_flag("vance5_voice")
				await main.say("The man on the phone.")
				if Game.flag("heard_caller"):
					await _vance("You asked me that before. This morning I get to hear the voice twice.")
				else:
					await _vance("I'll know his voice. I never forget a voice I disliked.")
			"sight":
				Game.set_flag("vance5_sight")
				await main.say("Stay out of sight.")
				await _vance("I've stayed out of sight for forty years, Detective. It's my one real talent.")
				await _vance("And I keep my .45 for people who want to be romantic.")
			_:
				await main.say("I'm ready.")
				Game.set_flag("talked_vance5")
				return


# --- Brenner arrives ------------------------------------------------------------------------------------------------
func _arrival() -> void:
	await main.player.play_action("use")
	main.take("danny_phone")
	Game.set_flag("phone_on_bollard")
	_sync()
	await main.say("Sunrise in twenty minutes. He'll be early. Cops are always early to the things that scare them.")
	await main.ui.fade_to(1.0, 0.8)
	Game.set_flag("brenner_here")
	_pose = "brenner"
	_sync()
	await main.wait(0.6)
	await main.ui.fade_to(0.0, 1.0)
	await main.narrate("Headlights between the containers, pale against the dawn. A long gray Lincoln rolls down slowly and stops. The engine runs a moment, then quits.")
	await main.narrate("He carries two paper cups of coffee. He walks to me without hurrying and sets one on the bollard beside the phone.")
	main.player.face("left")
	await _brenner("Detective Kessler. Maureen talks about you. Best she's got, she says, and the biggest pain in her neck.")
	await _brenner("Black. I was told you take it black.")
	await main.say("You're good with coffee.")
	await _brenner("Forty years of night shifts, son. You learn what people need at this hour. Coffee, and somebody to tell them to go home.")
	await _brenner("That it?")
	await main.say("That's it.")
	await _brenner("Then let's talk about my retirement.")
	await _brenner("I don't know what you think you've got. I'm a retired man who drives a car for a living. I've never been in that bar in my life. Can't stand jazz.")
	await _confront()


func _confront() -> void:
	## Puzzle 8.1: three lies in order, the seed options any time before step 3 resolves.
	while not Game.flag("brenner_lie3_broken"):
		var opts: Array[String] = []
		if not Game.flag("brenner_lie1_broken"):
			if Game.flag("clue_brenner_alone") and Game.flag("clue_nina_call"):
				opts.append("You called Nina Alvarez.")
		elif not Game.flag("brenner_lie2_broken"):
			if Game.has_item("tab_book") and Game.flag("clue_choke"):
				opts.append("Sal wrote you down.")
		elif Game.flag("heard_take"):
			opts.append("You were in the booth Tuesday.")
		for sd: Array in _seed_options():
			opts.append(sd[0])
		opts.append("Let's see what you've got, Walt.")
		var c: int = await main.choose(opts)
		var pick: String = opts[c]
		match pick:
			"You called Nina Alvarez.":
				await _lie1()
			"Sal wrote you down.":
				await _lie2()
			"You were in the booth Tuesday.":
				await _lie3()
			"Let's see what you've got, Walt.":
				await main.say("Let's see what you've got, Walt.")
				await _brenner("I've got all morning, son. You're the one with a shift.")
				return
			_:
				await _seed(pick)
	await _pitch()


func _seed_options() -> Array:
	var out := []
	if Game.flag("got_ride_receipt"):
		out.append(["Wednesday, ten past one."])
	if Game.flag("got_brenner_card") or Game.flag("clue_block_empty"):
		out.append(["Empty by Christmas."])
	if Game.flag("got_pryce_invite"):
		out.append(["They drew a lobby."])
	if Game.flag("clue_big_man") or Game.flag("clue_pryce_driver"):
		out.append(["A long gray car."])
	if Game.flag("clue_tape_helper"):
		out.append(["Officer Park logged you."])
	return out.filter(func(o: Array) -> bool: return not _seeds_used.has(o[0]))


func _seed(pick: String) -> void:
	_seeds_used.append(pick)
	match pick:
		"Wednesday, ten past one.":
			await main.say("An hour after Danny went down, Harlan's office booked you a Glide on the company account, Blue Note to Pryce Tower.")
			await main.say("Your driver gave you one star. He wrote that you smelled like gun oil.")
			await _brenner("Kids today. No respect for a man who cleans his weapon.")
			if Game.flag("clue_cabin_clip"):
				await main.say("Kenji had a camera on his back seat. November's card. You, at twelve past one, wiping down a revolver, with a phone in a cracked case with a Blue Note sticker in your lap.")
				await main.wait(1.0)
				await _brenner("I saw the camera. Kids put those in to sell clips of drunk actresses. Nobody was ever going to pay to watch an old man in a raincoat.")
				await _brenner("And a wet revolver rusts by morning, son. You dry it when it's wet, not when it's smart. Thirty years of habit doesn't stop to check who's filming.")
		"Empty by Christmas.":
			await main.say("You handed out cards on that block last Thursday. Security consultant, Pryce Development. \"Empty by Christmas. The jazz club too.\"")
			await _brenner("It was a forecast. I'm good at forecasts.")
		"They drew a lobby.":
			await main.say("Your boss threw a party for Ted Haskell last night and drew a forty-story lobby where the Blue Note is.")
			await _brenner("Harlan likes a nice drawing.")
		"A long gray car.":
			await main.say("A long gray car stopped on the Fletcher Drive bridge Tuesday after three, and a big man in an old cop's coat threw something into the reeds. I fished it out tonight.")
			await _brenner("The river was supposed to keep it.")
			await main.say("The river's been concrete since 1938.")
		"Officer Park logged you.":
			await main.say("Tuesday night you stood inside Danny's tape for an hour with an old ID and a tray of coffee, asking my uniforms if they'd found his phone. Officer Park logs everybody.")
			await _brenner("Old habits. I like to help.")
			await main.say("You came back to see what you'd missed.")


func _lie1() -> void:
	await main.say("You signed in to see Maureen at one-twenty. At one-thirty you heard her half of my call, and her half had Sal Moretti's name in it.")
	await main.say("When she hung up, you asked, the way an old cop asks, and she told you the rest: the knock, and the girl who gave it to me.")
	await main.say("At ten to two she went to the copier, and you picked up her desk phone and called Nina Alvarez. You told her you were my partner. You called her \"young lady.\" You got Danny's knock.")
	await main.say("Otis has you on his log, and Nina's phone has Maureen's number at one fifty-two.")
	await _brenner("(a small smile) So I made a call. Maureen was upset about your bartender. I was helping. That's what I do.")
	Game.set_flag("brenner_lie1_broken")
	await _brenner("I called the girl. I went home. I was asleep by three. Ask my pillow.")


func _lie2() -> void:
	await main.player.play_action("notebook")
	await main.say("Three-twenty. W.B., club soda, no charge. Sal Moretti wrote down every drink he ever poured, and he wrote you down so somebody would find you.")
	await main.say("And Dr. Shah says Sal died from a bar-arm choke, from behind. The department banned it in 1982. You came on in 1979.")
	await _brenner("(the smile goes) A dead man's handwriting and a coroner's opinion. I've beaten better than that on a bad day.")
	Game.set_flag("brenner_lie2_broken")
	await _brenner("And the piano player? You want to hang him on me too? Reyes owed money to every shark in the harbor. I read the file. Maureen showed me.")


func _lie3() -> void:
	await _vance("Dead men don't pay, Mr. Brenner. Danny paid me. All of it, Tuesday afternoon.")
	await _vance("And I know your voice. You telephoned me Wednesday to ask.")
	await main.narrate("Brenner turns and looks at Vance for the first time. Then at Tiny.")
	await main.say("Tuesday night, eleven o'clock, a private booking in the back booth at the Blue Note. Two eighteen-year-old Scotches and a club soda. Harlan Pryce, Ted Haskell, and you.")
	await main.say("Danny was playing 'Round Midnight ten feet away, and his phone was recording. \"You don't pay a man like that three times, Harlan. You pay him once.\"")
	await main.wait(0.8)
	await main.say("\"Then pay him, Walt.\"")
	await main.wait(1.2)
	Game.set_flag("brenner_lie3_broken")


# --- Puzzle 8.2 and 8.3: the pitch and the .38 ------------------------------------------------------------------------
func _pitch() -> void:
	await _brenner("Let me tell you how this city works, Ray, since nobody told you in twenty-six years. A city is a deal.")
	await _brenner("Every street you drive on, somebody got paid to put it there. Harlan builds towers. Ted votes for towers. The towers get built, the city collects the taxes, the taxes pay your salary.")
	await _brenner("The piano player tried to cut himself a slice of that and the slice cut back.")
	await _brenner("Maureen? I taught her to drive a black-and-white. I wrote her letter for detective. I carried her through two shootings and a divorce.")
	await _brenner("If this goes where you want it to go, she goes with me. You want that on your board?")
	await _brenner("Or. Harlan needs a head of security, a real one, not an old man who drives. Two-fifty a year, a car, a pension on top of your pension.")
	await _brenner("You'd sleep nights, Ray. You haven't slept nights in eight years.")
	var c: int = await main.choose(["I sleep days.", "How much was Sal worth?", "You don't know Maureen."])
	match c:
		0:
			await main.say("I sleep days.")
			await _brenner("So did Danny, now.")
		1:
			await main.say("How much was Sal worth?")
			await _brenner("Less than he thought. He wouldn't sell his lease, and he wouldn't tell me what the kid left him. He just kept saying, \"A tab.\"")
		_:
			await main.say("You don't know Maureen.")
			await _brenner("I know her better than you do. I know what she'd do to keep her badge. I taught her.")
	await _brenner("The phone, Ray.")
	await main.player.play_action("pickup")
	await main.narrate("I pick Danny's phone up off the bollard and put it in his hand. He weighs it, looks at the Blue Note sticker, and flicks it out over the water.")
	Game.set_flag("phone_in_harbor")
	_sync()
	await main.wait(0.8)
	await _brenner("Whatever goes in here doesn't come back up. I've been told.")
	await main.say("That's the second time you've thrown him in the water.")
	await main.say("It was dead before you threw it in the river, Walt. Danny's song wasn't on it. It went up to the cloud the second he stopped playing, and now it's in a place you'll never get to.")
	await main.narrate("He sets his coffee down on the bollard, very carefully. When his hand comes back out of his raincoat it has a .38 in it, held low and steady, the way they taught it in 1979.")
	_pose = "brenner_gun"
	_sync()
	await _brenner("I was a cop for thirty years and a civilian for seventeen, son. I'm better at the second one.")
	var d: int = await main.choose(["Put it down, Walt.", "Go ahead. Everybody on this pier is watching."])
	if d == 0:
		await _talk_down()
	else:
		await _force()
	await _arrest()


func _talk_down() -> void:
	await main.say("Put it down, Walt.")
	# beat 1
	while true:
		var c: int = await main.choose(["Put it down, Walt.", "There are people watching.", "Think about Maureen."])
		if c == 0:
			await _brenner("Make me a better offer.")
		elif c == 1:
			await _vance("He's right. I'm watching.")
			await _brenner("A loan shark and a doorman. Who's going to believe them?")
		else:
			await main.say("She keeps your picture in her desk drawer, Walt. Right now she's going over a briefing she copied while you used her phone.")
			await main.say("You pull that trigger and she's the one who reads my name on the board.")
			await _brenner("(the gun dips an inch) Leave her out of it.")
			await main.say("You put her in it.")
			break
	# beat 2
	while true:
		var c: int = await main.choose(["Danny was a kid.", "It's over.", "Sal poured you a drink."])
		if c == 0:
			await _brenner("Danny was a blackmailer. He named his price.")
		elif c == 1:
			await _brenner("It's never over. Ask Harlan.")
		else:
			await main.say("Sal opened his door to a dead man's knock and poured you a club soda on the house. Then he wrote it down, because that's who he was.")
			await main.say("You killed the only man on that block who kept honest books.")
			await main.wait(1.0)
			await _brenner("He wouldn't tell me anything. He just kept saying, \"A tab.\" Like it was a joke.")
			await main.say("It was. You were the punch line.")
			break
	# beat 3
	while true:
		var c: int = await main.choose(["Give me the gun.", "Who taught Maureen to clear a revolver?", "Harlan's not coming, Walt."])
		if c == 0:
			await _brenner("Come and take it.")
		elif c == 1:
			await _brenner("I did. Muzzle down, cylinder out, rounds in your palm. She was the best I ever had.")
		else:
			await main.say("You came alone because you didn't want Harlan to know you'd left a loose end.")
			await main.say("He'll be at his desk at nine like nothing happened. He'll have a new driver by lunch.")
			break
	await main.narrate("He looks past me at the gray Lincoln, then at the sun coming up behind the crane. He points the muzzle at the concrete, swings the cylinder out, and tips six rounds into his palm.")
	_pose = "brenner"
	_sync()
	await main.narrate("He sets the empty revolver on the bollard next to my coffee, and the rounds beside it, in a neat row.")
	await _brenner("Muzzle down. Cylinder out. Rounds in your palm.")
	await _brenner("Tell Maureen...")
	await main.say("Tell her yourself. You'll see her in court.")
	Game.set_flag("brenner_talked_down")


func _force() -> void:
	await main.say("Go ahead, Walt. Do it in front of everybody. A loan shark, a doorman, and the sun.")
	await main.narrate("He raises the .38 to my face. Behind him Tiny stands up out of his chair, and the chair scrapes on the concrete. Brenner half turns toward the sound.")
	main.ui.fade_rect.color = Color(1, 1, 1, 0)
	await main.ui.fade_to(0.85, 0.08)
	await main.ui.fade_to(0.0, 0.5)
	main.ui.fade_rect.color = Color(0, 0, 0, 0)
	await main.narrate("Tiny's hand closes over his wrist. The shot goes into the sky; the gulls come off the containers all at once.")
	_pose = "brenner_cuffed"
	_sync()
	await main.narrate("Tiny folds Brenner over the hood of the Lincoln like a man folding a towel.")
	await _vance("A revolver, Mr. Brenner. I did tell the detective. They're for people who want to be romantic about it.")
	await main.say("Thanks, Tiny.")
	await _tiny("I'm the sign.")
	Game.set_flag("brenner_forced")


func _arrest() -> void:
	await main.walk(hotspot("brenner_cuffed").walk_to)
	main.player.face("left")
	_pose = "brenner_cuffed"
	_sync()
	await main.player.play_action("use")
	await main.say("Walter Brenner, you're under arrest for the murders of Salvatore Moretti and Daniel Reyes.")
	await main.say("Anything you want to say, I'd save it for a lawyer, and get a good one. Harlan's will be busy.")
	await main.give("brenner_38")
	await main.say("A .38. Shah will want to introduce it to Danny.")
	await main.narrate("A patrol car with Harbor Division markings rolls down the pier with no lights and no siren, the way Otis promised, and two uniforms get out.")
	await _brenner("You think a drive full of piano music stops a forty-story building? Harlan's lawyers bill more an hour than you make in a week.")
	await main.say("Then it'll be a long week.")
	if Game.flag("brenner_talked_down"):
		await _brenner("Kessler. The coffee was a peace offering. I meant it.")
		await main.say("I know. That's the worst part.")
	else:
		await main.narrate("He says nothing. He looks straight ahead.")
	await main.ui.fade_to(1.0, 0.8)
	Game.set_flag("brenner_arrested")
	_sync()
	await main.wait(0.6)
	await main.ui.fade_to(0.0, 0.8)
	await main.narrate("The patrol car pulls away between the containers.")


func _tinys_answer() -> void:
	await main.say("That's him, Tiny. That's who did Danny.")
	await main.wait(1.2)
	await _tiny("Thank you.")
	await main.wait(0.6)
	await _tiny("He played 'Round Midnight for me. Without me asking.")
	await main.say("I know. I heard him. Tuesday. You weren't in, so he played it anyway.")
	await main.narrate("Tiny sits back down. He turns the radio up.")
	Game.set_flag("tiny_told")
	await main.wait(0.6)
	await main.change_room("pier9_sunrise", "pier9_dawn")
