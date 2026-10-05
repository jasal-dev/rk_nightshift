extends Room
## The Blue Note, the bar (Case 5, scenes 2 and 5). Puzzle 2.1: the tab book by the register (W.B. at 3:20, Tuesday's
## booth, "D.R. decaf"). Puzzle 2.2: one glass washed after closing. The piano does nothing until Ike calls with Danny's
## password hint (clue_takes_hint); then Puzzle 5.2, the knock played on the keys: D, E, C, A, F (knows_password).
## Calling Ike from here plays the take (Case5.take). The tab book and the set list are overlays, gone once taken.

@onready var ledger: Sprite2D = $Ledger
@onready var setlist: Sprite2D = $Setlist
var _back_hint := false


func _ready() -> void:
	super._ready()
	_sync()


func _sync() -> void:
	ledger.visible = not Game.flag("got_tab_book")
	setlist.visible = not Game.flag("got_set_list")


func on_enter(_from_room: String) -> void:
	if not Game.flag("in_blue_note"):
		Game.set_flag("in_blue_note")
		await main.wait(0.3)
		await main.say("The Blue Note. I used to come Thursdays, before I went to nights.")
		await main.say("Sal kept it like a church. Somebody came in and said a different kind of prayer.")
	elif Game.flag("clue_takes_hint") and not Game.flag("knows_password") and not Game.flag("said_piano_line"):
		Game.set_flag("said_piano_line")
		await main.say("The knock, the way he played it. He played it right here every night after closing, for an audience of one.")


func interact(hs: Hotspot, verb: String, item: String) -> void:
	match hs.id:
		"register":
			if verb == "look":
				await main.say("A fat green ledger by the register. Sal's tab book." if not Game.flag("got_tab_book")
						else "The register. Sal rang up thirty-one years on it.")
				if Game.flag("clue_tab_habit") and not Game.flag("got_tab_book"):
					await main.say("\"If it isn't in the book, it didn't happen.\"")
			elif item != "":
				await default_response(verb, item)
			elif not Game.flag("got_tab_book"):
				await main.player.play_action("pickup")
				Game.set_flag("got_tab_book")
				_sync()
				await main.give("tab_book", false)
				await main.say("Sal's tab book. Three pages with bookmarks in them. Right-click it to read it.")
			else:
				await main.player.play_action("use")
				await main.say("The till's empty; the bar's been closed since Tuesday. Nobody came here for money.")
				main.clue("clue_cash")

		"rack":
			if verb == "look":
				await main.say("Every glass dried and racked, except one. Upside down, still beaded with water.")
				await main.say("The bar's been closed since Tuesday. Somebody washed this one tonight.")
				main.clue("clue_wet_glass")
			elif item != "":
				await default_response(verb, item)
			else:
				await main.say("No prints on a washed glass. Whoever it was knew that.")
				main.clue("clue_wet_glass")

		"bar":
			if verb == "look":
				await main.say("Thirty feet of mahogany, wiped clean. Closed since Tuesday, and Sal still wiped it every night like a man who expected to open again.")
			elif item != "":
				await default_response(verb, item)
			else:
				await main.say("I'm not sitting at Sal's bar without Sal behind it.")

		"mirror":
			await main.say("The bar mirror. I look like a man who's been up since yesterday.")

		"bottles":
			if verb == "look":
				await main.say("Thirty years of bottles. The good ones are on the top shelf, where Sal could see who reached for them.")
			else:
				await main.say("Not on duty. Not with Sal in the back.")

		"front_door":
			if verb == "look":
				if Game.flag("clue_latch"):
					await main.say("Deadbolt open, chain hanging loose. Somebody went out this way and let it shut behind him.")
				else:
					await main.say("Deadbolt open, chain hanging loose. Teo says it was on the latch.")
			elif item != "":
				await default_response(verb, item)
			else:
				await main.change_room("street_crime", "blue_note_bar")

		"back_booth":
			if verb == "look":
				if Game.flag("heard_take"):
					await main.say("Three men and a piano player who could hear. Just a booth now. That's the worst part.")
				else:
					await main.say("The back booth, half in shadow. A RESERVED card so old the corners curl.")
					await main.say("You'd hear every note from the piano here, and the piano would hear you.")
			elif item != "":
				await default_response(verb, item)
			elif Game.flag("heard_take"):
				await main.say("I'm not sitting there.")
			else:
				await main.say("Best seat in the house for not being seen.")

		"booths":
			await main.say("Red leather booths. Every one of them has heard a proposal, a confession or a lie. Usually all three.")

		"piano":
			if item == "set_list" or (item == "" and verb == "use"):
				await _piano(item == "set_list")
			elif item != "":
				await default_response(verb, item)
			else:
				await main.say("A baby grand, scuffed where a coffee cup sat on it every night.")
				await main.say("Masking tape on the white keys with letters in ballpoint: C, D, E, F, G, A, B. Somebody was teaching somebody.")
				main.clue("saw_key_tape")

		"set_list":
			if verb == "look":
				await main.say("Danny's set list, taped to the music stand. Tuesday's date." if not Game.flag("got_set_list")
						else "The music stand, empty now.")
			elif item != "":
				await default_response(verb, item)
			elif not Game.flag("got_set_list"):
				await main.player.play_action("pickup")
				Game.set_flag("got_set_list")
				_sync()
				await main.give("set_list", false)
				await Case5.read_set_list(main)
			else:
				await main.say("I've got it. It's still telling me the same thing.")

		"poster":
			if verb == "look":
				await main.say("DANNY REYES. PIANO. THURSDAYS. Somebody drew a small heart in the corner in eyeliner.")
			else:
				await main.say("I'll leave it up.")

		"jukebox":
			if verb == "look":
				await main.say("A jukebox full of records nobody played, because Danny played them better.")
			else:
				await main.say("Not tonight.")

		"chairs":
			await main.say("Every chair up, legs in the air. Except one stool at the end of the bar.")

		"stool":
			if verb == "look":
				await main.say("One stool down, at the end of the bar, where Sal could pour without walking.")
			elif Game.flag("clue_wb"):
				await main.say("Somebody sat there after closing. With a club soda.")
			else:
				await main.say("A stool, down off the bar. Somebody sat there after closing.")

		"back_door":
			if verb == "look":
				await main.say("The back room. Flashlights moving.")
			elif item != "":
				await default_response(verb, item)
			else:
				if not _back_hint and not Game.flag("got_tab_book") and Game.flag("clue_tab_habit"):
					_back_hint = true
					await main.say("Sal wrote everything down. I should read what he wrote.")
				await main.change_room("blue_note_back", "blue_note_bar")

		_:
			await default_response(verb, item)


# --- Puzzle 5.2: the knock, played on Danny's piano ---------------------------------------------------------------
func _piano(with_set_list: bool) -> void:
	if Game.flag("knows_password"):
		await main.say("I've played my one song.")
		return
	if not Game.flag("clue_takes_hint"):
		if with_set_list:
			await main.say("The notes are on the paper. The letters are on the keys.")
		else:
			await main.say("I play like a cop. Hit things until they confess.")
		return
	await main.player.play_action("use")
	var ok: bool = await main.piano(Case5.KNOCK, Case5.SET_LIST if Game.has_item("set_list") else null)
	if not ok:
		await main.say("Not yet. I'll come back to it.")
		return
	await main.say("D. E. C, A, F.")
	await main.wait(0.6)
	await main.say("Decaf.")
	main.ui.hide_piano()
	await main.say("Sal cut him off coffee at ten, so Danny wrote him a song about it, and Sal laughed every night for two years.")
	main.clue("knows_password")
	await main.say("Three tries, and I only need one. Time to call Ike.")
