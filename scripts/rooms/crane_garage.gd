extends Room
## Elliot Crane's garage, Mount Washington (Case 4, scene 5). Crane's story taken apart in three ordered steps: the car
## service (the valet ticket or the gate camera), the coyote (Puzzle 5.1, the headlight fit), and "I didn't stop" (his
## loafers and Shah's scrapes). The tarp comes off mid-scene (tarp_off), Crane sits down on the step, then Doss takes him.
## Puzzle 5.2: the tarp, the hose, the loafers, his phone and the grille, any time. The street opens the car menu after.
## The tarp and Crane's two poses are overlays.

## Left-click verbs shown under the cursor (see Room.verb_for); unlisted hotspots are "use".
const VERBS := {
	"crane": "talk", "crane_step": "talk", "street": "go", "house_door": "go"
}

const PIECES := [Vector2(433.5, 350.5), Vector2(650.5, 421.5)]   ## the two pieces' places in the close-up (gen_closeups.py)

@onready var tarp: Sprite2D = $Tarp
@onready var crane_stand: Sprite2D = $Actors/Crane_stand
@onready var crane_step: Sprite2D = $Actors/Crane_step
var _wander := 0


func _ready() -> void:
	super._ready()
	_sync()


func _sync() -> void:
	var gone := Game.flag("crane_arrested")
	tarp.visible = not Game.flag("tarp_off")
	crane_stand.visible = not gone and not Game.flag("crane_lie2_broken")
	crane_step.visible = not gone and Game.flag("crane_lie2_broken")
	hotspot("crane").enabled = crane_stand.visible
	hotspot("crane_step").enabled = crane_step.visible
	hotspot("audi_tarp").enabled = tarp.visible
	for id in ["audi", "headlight", "grille"]:
		hotspot(id).enabled = not tarp.visible


func on_enter(_from_room: String) -> void:
	if not Game.flag("met_crane"):
		Game.set_flag("met_crane")
		await main.wait(0.4)
		await main.say("Mount Washington. The houses hang off the hill like they're waiting to be asked in.")
		await _crane("Can I help you? It's four in the morning.")
		await main.say("Detective Kessler, LAPD. You're washing your car at four in the morning, Mr. Crane.")
		await _crane("The car washes are closed at four in the morning, Detective.")


func interact(hs: Hotspot, verb: String, item: String) -> void:
	if not hs.id in ["crane", "crane_step"]:
		await _maybe_hint()
	match hs.id:
		"crane", "crane_step":
			if verb == "look":
				if Game.flag("crane_lie2_broken"):
					await main.say("Elliot Crane, on the step to his own house, with nowhere left to go up.")
				else:
					await main.say("Elliot Crane. A robe over his suit trousers and a face that's been rehearsing since two o'clock.")
			elif item == "valet_ticket":
				await _step1("ticket")
			elif item == "pryce_invite":
				await _crane("I've got a box of those. Do you want one signed?")
			elif item == "danny_phone":
				await main.say("Not his. Not his kind of trouble.")
			elif item == "lens_piece" or item == "lens_shard":
				await main.say("He'd only argue with it. The car won't.")
			elif item != "":
				await default_response(verb, item)
			else:
				await _talk_to_crane()

		"audi_tarp":
			if verb == "look":
				await main.say("A blue tarp, still creased in squares from the package. Price sticker on the corner: $19.99. It's new tonight.")
				main.clue("clue_tarp_new")
			elif item == "lens_piece" or item == "lens_shard":
				await main.say("Not yet. Let him take the tarp off himself.")
			elif item != "":
				await default_response(verb, item)
			else:
				await _crane("That's my property, Detective. I'd like a warrant before you undress my car.")

		"audi":
			if item == "lens_piece" or item == "lens_shard":
				await _headlight()
			elif item != "":
				await default_response(verb, item)
			elif verb == "look":
				await main.say("A blue-gray A6, washed till it shines. Right headlight gone, a dent in the hood.")
			else:
				await main.say("I'm not touching it till the lab does.")

		"headlight":
			if item == "lens_piece" or item == "lens_shard" or (item == "" and verb == "use"):
				await _headlight()
			elif item != "":
				await default_response(verb, item)
			else:
				await main.say("A black hole with jagged edges, the shape of the pieces in my pocket.")

		"grille":
			if item != "":
				await default_response(verb, item)
			else:
				await main.say("Washed, mostly. Deep in the seam of the grille, a smear of yellow. Chomp yellow.")
				main.clue("clue_yellow_paint")

		"hose":
			if item != "":
				await default_response(verb, item)
			elif verb == "look":
				await main.say("The hose has been running into the drain long enough to make a stream. Somebody's been washing a car for two hours.")
				main.clue("clue_washing")
			else:
				await main.say("I'll let it run. It's not my water bill.")

		"loafers":
			if item != "":
				await default_response(verb, item)
			elif verb == "look":
				await main.say("Italian loafers on a sheet of newspaper, soaked through. Gray-green river mud packed in the stitching, and a fluff of reed seed stuck to one heel.")
				await main.say("Nobody gets river mud on their shoes driving home from Los Feliz.")
				var first := not Game.flag("clue_loafers")
				main.clue("clue_loafers")
				if first and crane_stand.visible:
					await _crane("I walked the dog.")
					await main.say("Where's the dog?")
					await main.wait(1.2)
			else:
				await main.say("They stay where they are. The lab will want them wet.")

		"phone":
			if item != "":
				await default_response(verb, item)
			elif verb == "look":
				main.ui.show_device("Elliot's phone", [], 0, "Locked.", ["Missed call: Ted  2:31 AM", "Missed call: Ted  2:48 AM",
						"Missed call: Harlan Pryce  3:05 AM", "Ted: Harlan says you left in a state. Call me."], false,
						Color(0.2, 0.24, 0.4))
				await main.say("Everybody's up late in Council District 13.")
				main.ui.hide_device()
				main.clue("clue_crane_calls")
			else:
				await main.say("It's locked, and it's his. The lock screen's chatty enough.")

		"jacket":
			if item != "":
				await default_response(verb, item)
			else:
				await main.say("A good suit on a hook. A name badge on the lapel: ELLIOT CRANE, OFFICE OF COUNCILMEMBER TED HASKELL.")

		"house_door":
			if item != "":
				await default_response(verb, item)
			elif verb == "look":
				await main.say("Up to the house. The lights upstairs are off. Somebody up there is sleeping through this.")
			else:
				await main.say("I'm not going in. Everything I need is down here.")

		"street":
			if verb == "look":
				await main.say("A street so steep the parked cars are holding on.")
			elif item != "":
				await default_response(verb, item)
			elif not Game.flag("crane_arrested"):
				await main.say("Not yet. Mr. Crane and I aren't done.")
			else:
				await Case4.car_menu(main, "crane_garage")

		_:
			await default_response(verb, item)


func _crane(line: String) -> void:
	var at := speaker_at("crane_step" if Game.flag("crane_lie2_broken") else "crane")
	await main.voice(line, at, Case4.CRANE_COLOR)


func _maybe_hint() -> void:
	var hint := ""
	var key := ""
	if Game.flag("crane_arrested"):
		pass
	elif Game.flag("crane_lie2_broken"):
		key = "hint_garage_step3"
		hint = "He says he never stopped. His shoes say he went for a walk by the river."
	elif Game.flag("crane_lie1_broken"):
		key = "hint_garage_step2"
		hint = "A coyote. I've got half a headlight that says different."
	elif Game.flag("clue_crane_story"):
		key = "hint_garage_step1"
		hint = "He says a car service. Somebody up on Glendower wrote down otherwise."
	if key == "" or Game.flag(key):
		_wander = 0
		return
	_wander += 1
	if _wander >= 4:
		_wander = 0
		Game.set_flag(key)
		await main.say(hint)


func _talk_to_crane() -> void:
	while true:
		var opts := []
		var keys := []
		if not Game.flag("crane_where"):
			opts.append("Where were you tonight?"); keys.append("where")
		if not Game.flag("clue_crane_story"):
			opts.append("How did you get home?"); keys.append("home")
		if not Game.flag("crane_tarp") and not Game.flag("tarp_off"):
			opts.append("Why the tarp?"); keys.append("tarp")
		if Game.flag("clue_crane_story") and not Game.flag("crane_lie1_broken"):
			if Game.has_item("valet_ticket"):
				opts.append("Starline Valet, ticket forty-seven."); keys.append("ticket")
			if Game.flag("clue_gate_clip"):
				opts.append("There's a camera on Mr. Pryce's gate."); keys.append("camera")
		if Game.flag("crane_lie2_broken"):
			opts.append("You stopped."); keys.append("stopped")
		opts.append("I'll wait."); keys.append("done")
		var c: int = await main.topics(opts)
		if c < 0:
			return
		var k: String = keys[c]
		if k in ["where", "home", "tarp", "done"]:
			await main.say(opts[c])
		match k:
			"where":
				Game.set_flag("crane_where")
				await _crane("At a fundraiser for the councilman. I'm Councilmember Haskell's chief of staff.")
				await main.say("He says it like a badge.")
				await _crane("I left around one-thirty.")
			"home":
				await _crane("A car service. I'd had a glass of wine; I'm responsible. The Audi's been in here all evening.")
				main.clue("clue_crane_story")
			"tarp":
				Game.set_flag("crane_tarp")
				await _crane("Birds. There's a jacaranda. Would you like to see the jacaranda, Detective?")
			"ticket", "camera":
				await _step1(k)
				return
			"stopped":
				await _step3()
				return
			"done":
				await _crane("Wait for what?")
				await main.say("You'll know it when it gets here.")
				return


# --- Step 1: the car service ----------------------------------------------------------------------
func _step1(how: String) -> void:
	if not Game.flag("clue_crane_story"):
		await main.say("Let him tell me his story first. Then I'll show him mine.")
		return
	if Game.flag("crane_lie1_broken"):
		await main.say("He's seen it. He's moved on to coyotes.")
		return
	if how == "ticket":
		await main.player.play_action("use")
		await main.say("Starline Valet, ticket forty-seven. \"Crane. Out one fifty-five. Guest insisted.\"")
	else:
		await main.say("There's a camera on Mr. Pryce's gate. It has you taking your own keys off the board at one fifty-one, and a delivery rider telling you that you can't drive like that.")
	await main.wait(1.2)
	await main.say("He puts the glass down on the bench, very carefully.")
	await _crane("All right. I drove. I'd had two glasses. Three. I was fine. I drove home slowly.")
	await _crane("And on Avenue 43 a coyote ran out. A big one. I hit it.")
	await main.ui.fade_to(1.0, 0.4)
	Game.set_flag("crane_lie1_broken")
	Game.set_flag("tarp_off")
	_sync()
	await main.ui.fade_to(0.0, 0.4)
	await _crane("There. That's what the tarp's for. I didn't want the neighbors seeing it and thinking I'd done something.")
	await main.say("Washed and gleaming. The right headlight is a black hole with jagged edges. A shallow dent in the hood.")
	await main.say("A coyote.")
	await _crane("They're everywhere up here.")


# --- Step 2: the coyote (Puzzle 5.1, the headlight fit) ------------------------------------------------
func _headlight() -> void:
	if not Game.flag("crane_lie1_broken"):
		await main.say("He'd tell me it's his car and his garage. Let him show it to me.")
		return
	if Game.flag("crane_lie2_broken"):
		await main.say("Both pieces fit. The rings line up. Nothing more to prove with plastic.")
		return
	if not Game.has_item("lens_piece"):
		await main.say("A black hole where a headlight was. The rest of it's somewhere between here and Los Feliz.")
		return
	if not Game.has_item("lens_shard"):
		await main.say("It fits, almost. There's a sliver still missing. Owen's bike had something of it.")
		return
	await main.player.play_action("use")
	var done: bool = await main.jigsaw(Case4.HEADLIGHT, [{"tex": Case4.PIECE_LENS, "target": PIECES[0], "turns": 1},
			{"tex": Case4.PIECE_SHARD, "target": PIECES[1], "turns": 2}])
	if not done:
		return
	await main.say("The two pieces settle into the hole, and the four rings moulded into the plastic join up across the break as if they'd never left.")
	main.ui.hide_jigsaw()
	main.clue("clue_lens_match")
	await main.say("This piece was in the reeds under the Fletcher Drive bridge. This one was in a delivery box on Owen Tate's bike.")
	await main.say("They fit your headlight like a key, Mr. Crane. Coyotes don't carry headlights into the river.")
	if Game.flag("clue_yellow_paint"):
		await main.say("And there's Chomp yellow in your grille.")
	await main.ui.fade_to(1.0, 0.4)
	Game.set_flag("crane_lie2_broken")
	_sync()
	await main.ui.fade_to(0.0, 0.4)
	await _crane("Okay. Okay. Something hit me. On the bridge. A shape, in the rain, in the dark.")
	await _crane("I didn't stop. I panicked, I drove home. I didn't know it was a person until I saw it on the news.")
	await main.say("He had a yellow box the size of a television on his back with a red light blinking on it.")
	await main.wait(0.6)
	await main.say("And there isn't any news, Mr. Crane. Nobody's found him on the news. They found him in the river.")


# --- Step 3: "I didn't stop." ------------------------------------------------------------------------
func _step3() -> void:
	if not Game.flag("clue_loafers") or not Game.flag("clue_moved"):
		await main.say("He says he didn't stop. Something in this garage got out of the car.")
		return
	await main.say("You stopped. Your shoes are on the bench, Mr. Crane. Five-hundred-dollar loafers with river mud in the stitching and reed seed stuck to the heel.")
	await main.say("And Owen's back is scraped raw from the bank, and it barely bled. He was dead when you slid him down it.")
	await main.wait(1.6)
	await _crane("He was right there at the end of the bridge. In the road. I got out. I thought I'd help. I thought...")
	await main.wait(0.6)
	await _crane("And I knew him. That's the thing. I knew him. The kid from the gate. \"You can't drive like that.\"")
	await _crane("And I looked down, and there were tents. And I thought, nobody looks twice at that river. Nobody looks twice at those people.")
	await main.say("Somebody did.")
	await _crane("Do you know what Wednesday is? The council votes on Hollywood Core. Ted's the swing vote.")
	await _crane("Eleven years I've carried that man's briefcase. If his chief of staff is a DUI story on Friday morning, they postpone, and Harlan...")
	await main.wait(1.0)
	await main.say("Harlan.")
	await _crane("Mr. Pryce has been a good friend to the district.")
	if Game.flag("clue_nursing"):
		await main.say("Owen Tate was twenty-four. He rode nights so he could study nursing in the day. He told you not to drive.")
	else:
		await main.say("Owen Tate was twenty-four. He told you not to drive.")
	await main.wait(0.8)
	var street := speaker_at("street")
	await main.voice("Detective. Otis said you've got somebody who deserves these more.", street, Case4.DOSS_COLOR)
	await main.say("Elliot Crane. Gross vehicular manslaughter, felony hit and run, and whatever the DA calls what he did after. Read him the rest, Officer.")
	await main.ui.fade_to(1.0, 0.8)
	Game.set_flag("crane_arrested")
	_sync()
	await main.wait(0.8)
	await main.ui.fade_to(0.0, 0.8)
	await main.voice("I had a vet in my car for this. A guy who fought in a war.", street, Case4.DOSS_COLOR)
	await main.wait(0.6)
	await main.voice("\"Sorry\" doesn't really cover it, huh.", street, Case4.DOSS_COLOR)
	await main.say("Say it anyway. He told me you already did.")
	await main.wait(0.8)
	await main.say("The phone on the workbench buzzes again. Nobody answers it.")
