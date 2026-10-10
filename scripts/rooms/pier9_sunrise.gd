extends Room
## Pier 9 at sunrise (Case 5, scenes 9 and 10). Ray holds the only playable copy of the take and chooses where it goes:
## Lt. Doyle (Endings A and B: her three objections, each answered by one of the seeds in Danny's box, or "I don't
## have it"), Internal Affairs and the DA (Ending C, Deputy DA Okafor), or Mara Quist at the Times (Ending D). "Not yet"
## leaves the pier live; the bollard or Ray's phone brings the choice back. Then the last scene, Maya's text, and the
## credits (Case5.credits). Doyle, Okafor and Mara are overlays.

## Left-click verbs shown under the cursor (see Room.verb_for); unlisted hotspots are "use".
const VERBS := {
	"tiny": "talk", "vance": "talk", "doyle": "talk", "okafor": "talk", "mara": "talk", "water": "look",
	"lincoln": "look", "car": "look", "barrel": "look", "piling": "look", "crane": "look", "containers": "look",
	"warehouse_sign": "look", "radio": "look"
}

const TINY_COLOR := Color(0.86, 0.74, 0.56)
const VANCE_COLOR := Color(0.78, 0.74, 0.9)

@onready var doyle: Sprite2D = $Actors/Doyle
@onready var okafor: Sprite2D = $Actors/Okafor
@onready var mara: Sprite2D = $Actors/Mara


func _ready() -> void:
	super._ready()
	_show("")


func _show(who: String) -> void:
	doyle.visible = who == "doyle"
	okafor.visible = who == "okafor"
	mara.visible = who == "mara"
	for id in ["doyle", "okafor", "mara"]:
		hotspot(id).enabled = who == id


func on_enter(from_room: String) -> void:
	if from_room == "pier9_dawn" and not Game.flag("ending_chosen"):
		await main.wait(0.6)
		await main.walk(hotspot("bollard").walk_to)
		main.player.face("right")
		await main.narrate("One drive. The original's frozen at Takes until somebody asks a judge for it, and whoever gets this decides whether anybody asks.")
		await main.narrate("Danny's song on a piece of plastic the size of a stick of gum.")
		await main.narrate("Whoever I hand it to decides what Danny Reyes was worth. The department. The law. The paper.")
		await main.wait(0.8)
		await main.narrate("Or Maureen.")
		await choose_ending()


func interact(hs: Hotspot, verb: String, item: String) -> void:
	match hs.id:
		"bollard":
			if verb == "look":
				await main.say("The end of the pier. The sun's on the water now.")
			elif not Game.flag("ending_chosen"):
				await choose_ending()
			else:
				await main.say("Nothing left to put down.")
		"water":
			if item != "":
				await main.say("The harbor's got enough of Danny's things.")
			else:
				await main.say("Gold on the water. The harbor doesn't know what it's holding.")
		"tiny":
			if verb == "look":
				await main.say("Tiny, the radio turned up. He hasn't looked away from the water.")
			else:
				await main.voice("Nobody plays it like Danny.", speaker_at("tiny"), TINY_COLOR)
		"vance":
			if verb == "look":
				await main.say("Vance in his doorway, finishing his tea, watching the morning like it owes him money.")
			else:
				await main.voice("Go home, Detective. Even I'm going home.", speaker_at("vance"), VANCE_COLOR)
		"lincoln":
			await main.say("Brenner's Lincoln, waiting for the lab's tow truck. It'll be the cleanest thing in the impound lot.")
		"car":
			await main.say("My car. It's seen the whole night. It looks it.")
		"barrel", "piling", "crane", "containers", "warehouse_sign", "radio":
			await main.say("The pier in daylight. Everything looks smaller than it did at one in the morning.")
		_:
			await default_response(verb, item)


# --- Scene 9: where the drive goes ------------------------------------------------------------------------------------
func choose_ending() -> void:
	var c: int = await main.choose(["Call Lt. Doyle.", "Call Internal Affairs and the DA.", "Call Mara Quist at the Times.",
			"Not yet."])
	if c == 3:
		await main.narrate("Thirty more seconds of nobody knowing.")
		return
	Game.set_flag("ending_chosen")
	main.busy = true
	await main.player.play_action("use")
	match c:
		0:
			await _doyle_ending()
		1:
			await _by_the_book()
		_:
			await _the_times()
	await _last_scene()


func _doyle(line: String) -> void:
	await main.voice(line, speaker_at("doyle"), Case5.DOYLE_COLOR)


func _doyle_ending() -> void:
	await main.say("Lieutenant. Come to Pier 9. Bring the briefing for the captain. You'll want to rewrite it.")
	await main.ui.fade_to(1.0, 0.8)
	_show("doyle")
	await main.walk(Vector2(hotspot("doyle").walk_to))
	main.player.face("left")
	await main.ui.fade_to(0.0, 1.0)
	await main.narrate("A dark sedan comes down the pier. Lt. Maureen Doyle: a good wool coat, her hair pinned up for a meeting at eight, a face that hasn't slept.")
	await _doyle("Harbor Division just booked Walt Brenner for two homicides on your say-so. Walt. Ray, have you lost your mind?")
	await main.say("I found it. It was in a piano.")
	await main.narrate("I open Danny's box on the hood of my car and lay it out, and give her the gist: the one-thirty call, the copier, the one fifty-two call to Nina, the knock, Sal, the take.")
	await _doyle("(very quietly) He was in my office. He brought coffee.")
	await _doyle("Give me the hard version, Ray. The one the captain's going to give me.")
	# Puzzle 9.1: three objections; the box holds only what Ray pinned
	var objections := [
		["Walt drives for half the money in Century City. Car service, security, whatever's going. That doesn't make him Pryce's man.",
			"board_brenner_card", "That's not Walt and Pryce on paper, Ray."],
		["All right. He works for Pryce. That tape's still a voice under a piano. Pryce's lawyers will find a man who swears it's an actor. You can't put Walt with Pryce the night Reyes died.",
			"board_ride_receipt", "That doesn't put him in Century City on Tuesday night."],
		["And Haskell? Ted Haskell is a sitting councilman. Fifty thousand in a booth is his word against a dead piano player's phone. He'll call it a campaign donation and the captain will thank him for it.",
			"board_pryce_invite", "That's not Pryce and Haskell together, Ray."],
	]
	for i in objections.size():
		var o: Array = objections[i]
		await _doyle(o[0])
		while true:
			var cards := _box_cards()
			var opts: Array = []
			for card: Array in cards:
				opts.append(card[1])
			if not Game.flag(o[1]):
				opts.append("I don't have it.")
			var c: int = await main.choose(opts)
			if c >= cards.size():
				await _bitter(i)
				return
			var id: String = cards[c][0]
			if id == o[1]:
				await _answer(i)
				break
			await _doyle(o[2])
	await _best()


func _box_cards() -> Array:
	## What's in Danny's box: the case's own papers, and whichever seeds were on the board.
	var out := [["board_envelope", "Envelope, \"1 of 3\""], ["index_card", "Index card: WALT BRENNER, for H. PRYCE, T. HASKELL"],
			["tab_photo", "Photo of the tab book: \"3:20 W.B. club soda\""]]
	if Game.flag("board_brenner_card"):
		out.append(["board_brenner_card", "Walter Brenner's card"])
	if Game.flag("board_ride_receipt"):
		out.append(["board_ride_receipt", "Photo of Walt B.'s ride, billed to Pryce Development"])
	if Game.flag("clue_cabin_clip"):
		out.append(["cabin_still", "Kenji's cabin camera: the back seat, 1:12 a.m."])
	if Game.flag("board_pryce_invite"):
		out.append(["board_pryce_invite", "Pryce's invitation"])
	return out


func _answer(i: int) -> void:
	match i:
		0:
			await main.say("\"Walter Brenner, LAPD, retired. Security Consultant, Pryce Development.\" He handed these out on the Blue Note's block last Thursday.")
			await main.say("Empty by Christmas, the jazz club too.")
		1:
			await main.say("Wednesday, ten past one. A Glide from the Blue Note to Pryce Tower, billed to Pryce Development's business account. Rider: Walt B.")
			await main.say("The driver gave him one star and wrote that he smelled like gun oil. An hour after Danny went down, Walt went straight to the boss, on the boss's account.")
			if Game.flag("clue_cabin_clip"):
				await main.say("And the driver's back-seat camera has him in that car holding Danny's phone.")
		_:
			await main.say("Pryce threw him a party last night. \"Friends of Ted Haskell.\" Look inside. They've drawn a lobby where the Blue Note is.")
			await main.say("The vote's next Wednesday, and he's the swing. His own chief of staff told me so, right before he asked for a lawyer.")


func _best() -> void:
	## Ending A: all three answered.
	await main.narrate("Doyle looks at the hood of the car for a long time. The ride receipt, the card, the invitation, the envelope, the string still knotted to the pins.")
	await _doyle("He brought me coffee. He asked how my night was going. And I told him about your bartender like it was gossip. Like it was nothing.")
	await main.say("You told me everything closes eventually.")
	await main.wait(0.8)
	await _doyle("Not like this. Not like this, Ray.")
	await main.narrate("She takes out her phone.")
	await _doyle("Captain. It's Doyle. No, sir, it can't wait until eight.")
	await main.wait(0.8)
	await _doyle("Yes, sir. I'll be the one testifying.")
	await _doyle("The call, the copier, all of it. It'll cost me.")
	await main.say("It cost Sal more.")
	await _doyle("I know. I'll carry the box. You carry the drive, and you don't let go of it until the DA signs for it in front of both of us.")
	await main.say("Every comma.")
	await _doyle("Every comma.")
	await _doyle("Go home after, Ray. That's not an order. I don't think I get to give you those this morning.")
	Game.set_flag("ending_doyle_best")


func _bitter(i: int) -> void:
	## Ending B: an objection Ray can't answer.
	match i:
		0:
			await main.narrate("I had a name and a voice. I didn't have a single piece of paper with Walt and Pryce on it.")
		1:
			await main.narrate("I couldn't put Walt with Pryce that night. Somewhere in a dead driver's app there was a receipt I never looked for.")
		_:
			await main.narrate("I had nothing with Pryce and Haskell on the same page. Somewhere up in Los Feliz there was a box of gift bags I walked past.")
	await _doyle("That's what I thought.")
	await _doyle("Give me the drive, Ray. I'll take it to IA myself, today, properly. We do this by the book.")
	await main.narrate("I hold the evidence bag a moment longer than I should. Then I put it in her hand.")
	main.take("take_drive")
	await _doyle("Walt killed a bartender. That we can prove, and that's what he'll go down for.")
	await main.say("And Danny?")
	await _doyle("Danny was a blackmailer who got shot in an alley. I'm sorry, Ray. That's what the captain will see.")
	await main.ui.fade_to(1.0, 0.8)
	_show("")
	await main.ui.fade_to(0.0, 0.8)
	await main.narrate("She gets back in her car. I watch it go.")
	await main.narrate("She meant it. That's what I keep coming back to. She meant every word.")
	Game.set_flag("ending_doyle_bitter")


func _by_the_book() -> void:
	## Ending C: Internal Affairs and the DA.
	await main.say("Professional Standards Bureau? Detective Ray Kessler, Hollywood Homicide. I need to report a leak from a lieutenant's office.")
	await main.say("And I need a deputy DA from Public Integrity at Pier 9, San Pedro, before the sun's all the way up.")
	await main.ui.fade_to(1.0, 0.8)
	_show("okafor")
	await main.walk(Vector2(hotspot("okafor").walk_to))
	main.player.face("left")
	await main.ui.fade_to(0.0, 1.0)
	await main.narrate("Forty minutes later: two cars. Deputy DA Helen Okafor, a raincoat over gym clothes, and a silent IA sergeant with a camera.")
	await main.narrate("She reads the index card, listens to me, and holds out an evidence envelope for the drive. I hand her Ike's hash sheet with it.")
	main.take("take_drive")
	await _okafor("And the original?")
	await main.say("Frozen at Takes since five fifty-one. The lab sent a preservation letter. You'll want a warrant.")
	await _okafor("I'll have one before lunch.")
	await _okafor("You understand this goes through every desk in your building. Including your lieutenant's.")
	await main.say("That's the idea.")
	await _okafor("It'll be slow. Men like Pryce make everything slow.")
	await main.say("Slow's fine. Slow is how things stay done.")
	await _okafor("(signing the chain-of-custody form) Go home, Detective. You'll be hearing from us more than you'd like.")
	Game.set_flag("ending_by_book")


func _okafor(line: String) -> void:
	await main.voice(line, speaker_at("okafor"), Case5.OKAFOR_COLOR)


func _the_times() -> void:
	## Ending D: Mara Quist, LA Times.
	await main.narrate("I take her card out of my coat and dial.")
	await main.voice("Quist.", Case5.CALL_AT, Case5.MARA_COLOR)
	await main.say("It's a pattern.")
	await main.voice("(instantly awake) Where are you?", Case5.CALL_AT, Case5.MARA_COLOR)
	await main.ui.fade_to(1.0, 0.8)
	_show("mara")
	await main.walk(Vector2(hotspot("mara").walk_to))
	main.player.face("left")
	await main.ui.fade_to(0.0, 1.0)
	await main.narrate("Twenty-five minutes later her hatchback bumps down the pier. She listens to the take on her laptop, headphones on, twice, without a word. Then she takes them off.")
	await main.voice("You know what this does to you.", speaker_at("mara"), Case5.MARA_COLOR)
	await main.say("I know what it does to them.")
	await main.voice("When I've made my copy, the drive goes to the DA. I'll walk it over myself.", speaker_at("mara"), Case5.MARA_COLOR)
	await main.voice("It goes up at noon. They'll know where it came from.", speaker_at("mara"), Case5.MARA_COLOR)
	await main.say("Everybody always does.")
	main.take("take_drive")
	Game.set_flag("ending_times")


# --- Scene 10: the last scene, the same for everyone ------------------------------------------------------------------
func _last_scene() -> void:
	await main.ui.fade_to(1.0, 1.0)
	_show("")
	main.player.position = Vector2(hotspot("bollard").walk_to)
	main.player.face("right")
	await main.wait(0.8)
	await main.ui.fade_to(0.0, 1.2)
	await main.narrate("Five names on a board. Danny, Kenji, Gus, Owen, Sal. Nobody important stayed up for any of them.")
	await main.wait(0.8)
	await main.narrate("Somebody has to.")
	await main.wait(0.6)
	await main.text_message("you up?", false, "Maya")
	await main.wait(1.2)
	await main.text_message("Always.", true)
	await main.wait(1.0)
	main.ui.hide_phone()
	await Case5.credits(main)
