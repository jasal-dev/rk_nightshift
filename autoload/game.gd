extends Node
## Global game state (autoload "Game"): flags, inventory, current room, save/load.
## Everything that must survive a room change or a save lives here.

signal inventory_changed
signal item_selected(id: String)

const SAVE_PATH := "user://savegame.json"

## Item database. Add new items here; icons live in res://assets/items/<id>.png
const ITEMS := {
	"key": {"name": "small key", "desc": "A small brass key. Opens the filing cabinet."},
	"case_file": {"name": "Reyes file", "desc": ""},
	"coffee": {"name": "cold coffee", "desc": "Stone cold. Something rattles at the bottom of the mug."},
	"dime": {"name": "dime", "desc": "Ten cents. The price of a phone call in this town."},
	"matchbook": {"name": "matchbook", "desc": "Blue Note matches. Someone wrote a number inside: 555-0147."},
	"gaff": {"name": "boat hook", "desc": "A boat hook. Six feet of pole and a bad attitude at the end."},
	"envelope": {"name": "Blue Note envelope", "desc": ""},
	"notebook": {"name": "notebook", "desc": ""},
	# Case 2
	"driver_card": {"name": "Kenji's driver card", "desc": "Kenji's Glide card. Photo, plate number, four point nine eight stars."},
	"norms_receipt": {"name": "Norm's receipt", "desc": "A receipt from Norm's on Sunset. Table 6, twelve-fourteen. Two coffees, one cherry pie."},
	"kenji_keys": {"name": "Kenji's keys", "desc": "Kenji's key ring. The car, a house key, and a little plastic Dodgers bat."},
	"card_slip": {"name": "Norm's card slip", "desc": "The merchant copy. Table six, 12:14 a.m. Signed \"D. Clark\". Looks like a seismograph."},
	"frozen_peas": {"name": "bag of frozen peas", "desc": "A bag of frozen peas, taped shut. Nobody tapes peas."},
	"sd_cards": {"name": "dashcam and memory cards", "desc": "A two-lens dashcam and eleven memory cards, January to November, labeled in Kenji's hand."},
	"ride_receipt": {"name": "photo of Kenji's screen", "desc": ""},
	# Case 3
	"gus_keys": {"name": "Gus's keys", "desc": "Gus's key ring. A door key, a desk key, and a little brass one, like the key Pearl wears."},
	"uv_lamp": {"name": "UV lamp", "desc": ""},
	"catalogue": {"name": "Calloway's catalogue", "desc": ""},
	"star_earring": {"name": "gold star earring", "desc": "A little gold star, five points, the post bent back. Torn out of somebody's ear."},
	"fake_oscar": {"name": "the \"Oscar\"", "desc": ""},
	"brenner_card": {"name": "Walter Brenner's card", "desc": ""},
	# Case 4
	"lens_shard": {"name": "sliver of headlight", "desc": "A sliver of clear plastic with a curved edge, from the crushed box on Owen's bike."},
	"lens_piece": {"name": "half a headlight", "desc": ""},
	"danny_phone": {"name": "Danny's phone", "desc": "A phone in a cracked black case, river water still in it. A half-peeled Blue Note sticker, and white tape: \"D.R. IF FOUND CALL THE BLUE NOTE.\""},
	"valet_ticket": {"name": "valet ticket No. 47", "desc": ""},
	"pryce_invite": {"name": "Pryce's invitation", "desc": ""},
	"lab_receipt": {"name": "lab evidence receipt", "desc": ""},
	# Case 5
	"ray_phone": {"name": "my phone", "desc": ""},
	"reporter_card": {"name": "Mara Quist's card", "desc": ""},
	"tab_book": {"name": "Sal's tab book", "desc": ""},
	"set_list": {"name": "Danny's set list", "desc": ""},
	"danny_box": {"name": "Danny's box", "desc": ""},
	"take_drive": {"name": "the drive", "desc": ""},
	"brenner_38": {"name": "Brenner's .38", "desc": ""},
}

## Notebook clues: facts Ray writes down, as [case, line]. Each is a flag of the same name (set with
## Main.clue()), and each can be pinned as evidence on that case's murder board.
const CLUES := {
	"clue_wallet_phone": [1, "Wallet left on the body. Phone never found."],
	"clue_38": [1, "Shot once, .38, close range."],
	"clue_knock": [1, "Danny's knock: two slow, three fast. Nina gave it to me."],
	"clue_vance": [1, "Vance. Pier 9. Green door."],
	"clue_paid": [1, "Danny paid Vance $8,000 in full, cash, Tuesday afternoon. He was shot that night."],
	"clue_alibi": [1, "Vance was on his boat in Avalon the night Danny died."],
	# Case 2
	"clue_cabin_camera": [2, "Brielle V. posted at 11:58: the driver had a camera pointed at the back seat."],
	"clue_brielle_alibi": [2, "Brielle V. has been live from a hot tub since 12:20. 31,000 witnesses."],
	"clue_walker": [2, "1:15 a.m.: a man walking down Mulholland, hood up, carrying a bag. No car."],
	"clue_ligature": [2, "Strangled from behind, back seat right. Flat woven strap, an inch wide, herringbone."],
	"clue_tod": [2, "Died between 1:00 and 1:15 a.m."],
	"clue_last_trip": [2, "Glide: last trip ended in Silver Lake at 11:52. Offline after."],
	"clue_threat": [2, "Heck D., Tuesday: \"Do it once more and I'll put you in the ground.\""],
	"clue_gps": [2, "Car GPS: Home 11:56, Norm's 12:08, Mulholland overlook 12:58."],
	"clue_off_app": [2, "After 11:52 Kenji drove off the app: home, pie, the overlook. Someone he knew."],
	"clue_dashcam": [2, "Dashcam unscrewed, cable coiled. Taken by someone who knows cameras."],
	"clue_two_cups": [2, "Two Norm's coffees. One drunk, one barely touched."],
	"clue_empty_case": [2, "Card case in the glovebox, JAN to DEC. Every slot empty."],
	"clue_rat": [2, "RAT keyed into the driver's side. Weeks old."],
	"clue_roommate_norms": [2, "Rosa: Kenji was at Norm's with his roommate, \"the one with the camera bag\". They argued about cards."],
	"clue_heck_alibi": [2, "Heck sat in the LAX queue from 11:00 to 1:38. Four cameras on the lot."],
	"clue_side_thing": [2, "Heck: Kenji was quitting \"the side thing\". It got somebody hurt."],
	"clue_napkin": [2, "Booth 6 napkin: \"11 × 2,500\". \"50/50\" crossed out."],
	"clue_devin_story": [2, "Devin: home all night, editing. Asleep by eleven."],
	"clue_kenji_quitting": [2, "Kenji's note: Carla Mendes got fired over a HushHush clip. He was giving her lawyer the cards."],
	"clue_laptop": [2, "Devin's laptop: last save 6:12 p.m."],
	"clue_strap": [2, "Devin's camera bag: inch-wide herringbone strap."],
	"clue_sneakers": [2, "Devin's wet sneakers: orange grit from the overlook lot."],
	"clue_peas_note": [2, "Kenji's fridge note: Devin's peas, untouched since July."],
	# Case 3
	"clue_pearl_story": [3, "Pearl: closed at 9, came back at 2:15 for her headshots, found Gus. Door smashed, Oscar gone."],
	"clue_keyholders": [3, "Two keys to the Oscar case: Gus's and Pearl's."],
	"clue_pushed": [3, "Two fresh bruises on Gus's breastbone, the heels of two small hands. He was pushed backward."],
	"clue_tod_gus": [3, "Gus died between 1:15 and 1:45."],
	"clue_glass_out": [3, "The door glass is out on the sidewalk. Broken from the inside."],
	"clue_key_opened": [3, "The Oscar case was opened with a key. Not a scratch on the lock."],
	"clue_staged": [3, "Nobody broke in. Somebody with a key broke out."],
	"clue_register": [3, "$212 in the register. A burglar who leaves the cash."],
	"clue_eviction": [3, "Pryce Development, final notice to vacate. Delivered a week ago."],
	"clue_whitaker_alibi": [3, "Whitaker, Pryce's agent, was on the Pryce Tower garage cameras from 11 p.m. to 3 a.m."],
	"clue_same_serial": [3, "Calloway's sold Oscar No. 734 privately three weeks ago. Gus's certificate says No. 734."],
	"clue_phone_log": [3, "Gus called Calloway's at 12:40, then Pearl at 12:52. Three minutes."],
	"clue_headshots_left": [3, "Pearl \"came back for her headshots\". They're still in her locker."],
	"clue_practice_sigs": [3, "A legal pad in Pearl's locker: \"Lyle Brandt\", forty times, getting better."],
	"clue_uv_fakes": [3, "Under UV, three \"vintage\" signatures glow. Modern gold paint pen."],
	"clue_gold_pen": [3, "Pearl's headshots are signed in the same gold pen. Same glow."],
	"clue_morty_offer": [3, "Morty offered Gus $250,000 for the Oscar in March. Gus said he'd be buried with it."],
	"clue_morty_alibi": [3, "Morty was bidding in a Tokyo online auction from 12:30 to 2:10."],
	"clue_morty_bought": [3, "Morty bought the real Oscar three weeks ago, $180,000, from \"Stardust Archive\". Pearl runs the shop's email."],
	"clue_weight": [3, "A real Oscar weighs eight and a half pounds. A prop is hollow resin."],
	"clue_cigar": [3, "Gus's cigar, half smoked, by the roof door. He came up here to wait."],
	"clue_footprints": [3, "Small heel prints in the wet gravel: stair door to the water tank and back. Not to the edge."],
	"clue_replica": [3, "The \"Oscar\" in the tank floats. Hollow. A prop with No. 734 freshly engraved."],
	"clue_bare_ear": [3, "Pearl's left earring is missing. The lobe is torn and red."],
	"clue_fiat": [3, "Charlie: Pearl's yellow Fiat was in the alley around one."],
	"clue_shouting": [3, "Charlie: around 1:30, Gus shouting \"How long?\" on the roof. Then nothing."],
	"clue_block_empty": [3, "Charlie: Brenner said the block would be empty by Christmas, \"the jazz club too\"."],
	# Case 4
	"clue_preacher_story": [4, "Preacher: found the bike on the bridge after two, light blinking, carried it down so it wouldn't be stripped."],
	"clue_bang": [4, "Preacher: a bang around two, no brakes. A car door a long while later. A car leaving slow."],
	"clue_no_brakes": [4, "No skid marks on the bridge. The driver never braked."],
	"clue_glass_bridge": [4, "Headlight plastic in the gutter at the east end."],
	"clue_scupper": [4, "The bridge drains into the channel. The big pieces went down the grate."],
	"clue_reeds_tip": [4, "Preacher: everything off the bridge ends in the reeds under the drain."],
	"clue_hit_by_car": [4, "Both legs broken at bumper height, from behind. A car, not a beating."],
	"clue_tod_owen": [4, "Died between 1:45 and 2:30."],
	"clue_moved": [4, "Scrapes from the bank barely bled. He was dead when somebody slid him down."],
	"clue_headlight_glass": [4, "Headlight plastic in his hair."],
	"clue_paint": [4, "Blue-gray paint flakes in the bike's crushed rack."],
	"clue_nursing": [4, "A nursing textbook in his delivery box."],
	"clue_phone_left": [4, "Preacher carried the bike down and left a $900 phone on the handlebars."],
	"clue_last_drop": [4, "Owen's last drop-off: Glendower Ave, Los Feliz, 1:50."],
	"clue_one_star": [4, "One star: \"Threatened that someone would get killed.\""],
	"clue_trip_paused": [4, "Chomp: no movement on Fletcher Drive from 2:04."],
	"clue_drag_marks": [4, "Heel marks down the east bank from the fence gap to Owen."],
	"clue_bike_stairs": [4, "One tire line and boot prints down the stairs."],
	"clue_two_tracks": [4, "The bike came down the stairs with Preacher. Owen came down the bank with somebody else."],
	"clue_audi": [4, "The headlight piece: four rings, part 4K0, blue-gray paint. An Audi."],
	"clue_danny_phone": [4, "Danny's phone, in the reeds under the Fletcher Drive bridge."],
	"clue_big_man": [4, "Preacher: Tuesday after three, a big man in an old cop's coat threw something small and black off the bridge from a long gray car."],
	"clue_host": [4, "The fundraiser was Harlan Pryce's, at a Pryce Development house, for Councilmember Haskell."],
	"clue_warning": [4, "Owen warned a drunk guest not to drive. Courtney took it as a threat."],
	"clue_crane_drunk": [4, "Gate camera, 1:51: a drunk guest takes his own keys. \"Mind your business, delivery boy.\""],
	"clue_gate_clip": [4, "Gate camera, 1:55: a blue-gray Audi follows Owen downhill, both headlights intact."],
	"clue_headlights_intact": [4, "Both headlights were whole at 1:55."],
	"clue_courtney_alibi": [4, "Courtney locked the gate from inside at 2:38. She never left."],
	"clue_plate": [4, "Plate 8KXD392."],
	"clue_pryce_driver": [4, "Andre: Pryce left at eleven in a gray Lincoln. His driver's a big old ex-cop."],
	"clue_curb_scrape": [4, "Blue-gray paint on the curb by the gate."],
	"clue_render": [4, "The invitation's drawing puts a lobby where the Blue Note is."],
	"clue_crane_id": [4, "8KXD392 is Elliot Crane, Haskell's chief of staff, Mount Washington."],
	"clue_crane_story": [4, "Crane: took a car service home; the Audi was in the garage all night."],
	"clue_tarp_new": [4, "The tarp is new tonight. $19.99."],
	"clue_washing": [4, "Somebody's been washing the car for two hours."],
	"clue_loafers": [4, "Crane's loafers: soaked, river mud in the stitching, reed seed on the heel."],
	"clue_crane_calls": [4, "Missed calls on Crane's phone: Ted at 2:31 and 2:48, Harlan Pryce at 3:05."],
	"clue_yellow_paint": [4, "Chomp yellow in the Audi's grille."],
	"clue_lens_match": [4, "Both headlight pieces fit Crane's broken headlight."],
	# Case 5
	"clue_mara_beat": [5, "Mara: Hollywood Core, forty stories, Haskell's the swing vote."],
	"clue_no_note": [5, "No note. Sal wrote down every drink for thirty years."],
	"clue_tape_helper": [5, "Park logged a retired cop named Walt inside Danny's tape on Tuesday for an hour. He asked whether they'd found the phone."],
	"clue_latch": [5, "Front door was on the latch, not the deadbolt. Somebody left and pulled it shut."],
	"clue_tab_habit": [5, "Sal: \"If it isn't in the book, it didn't happen.\""],
	"clue_knock_only": [5, "Since Tuesday Sal only opened the door to Danny's knock."],
	"clue_wb": [5, "Tab book: \"3:20 W.B. club soda. N/C.\" After closing."],
	"clue_booth_tuesday": [5, "Tuesday: back booth, three men, two Macallan 18s and a club soda, cash, no names."],
	"clue_decaf": [5, "\"D.R. decaf,\" every night."],
	"clue_cash": [5, "The cash box untouched. Not a robbery."],
	"clue_wet_glass": [5, "One glass washed after closing."],
	"saw_key_tape": [5, "Letters taped on the piano keys."],
	"clue_choke": [5, "Dead before the rope. A bar-arm choke from behind, a hold the LAPD banned in 1982."],
	"clue_sal_tod": [5, "Sal died between 3:30 and 4:00."],
	"clue_let_in": [5, "No defensive wounds. He turned his back on him."],
	"clue_stool": [5, "Step stool four feet from the pipe."],
	"clue_clean_hands": [5, "No rope burn on Sal's palms."],
	"clue_locker": [5, "Sal's keys in Danny's locker; the sheet music searched."],
	"clue_sal_no": [5, "Pryce's lawyers offered to buy out Sal's lease. Sal wrote NO."],
	"clue_staged_hanging": [5, "Sal let him in, turned his back, and the man staged a suicide."],
	"clue_back_locked": [5, "Alley door deadbolted from inside."],
	"clue_umbrella": [5, "A wet umbrella hung up after closing; small sneaker prints to the cooler."],
	"clue_nina_heard": [5, "Nina heard a man ask \"What did the kid leave you, Sal?\" at 3:30, then the front door at about 4."],
	"clue_young_lady": [5, "The caller called Nina \"young lady\" and showed a police number."],
	"clue_nina_call": [5, "Nina's phone: 1:52 a.m., (323) 555-0186, 2 minutes."],
	"clue_lisbon": [5, "Danny: \"One of three, baby, and then Lisbon.\""],
	"clue_knock_tune": [5, "The knock is a five-note tune Danny wrote Sal about what Sal served him instead of coffee."],
	"clue_takes_app": [5, "Danny recorded every set on his phone."],
	"clue_one_call": [5, "One call out from my desk all night: 1:30, to Doyle's office."],
	"clue_desk_line": [5, "Nina's police number is Doyle's direct line."],
	"clue_walt_aside": [5, "\"Thanks, Walt. Black is fine.\" Somebody was in her office at 1:30."],
	"clue_visitor_log": [5, "Otis: Walter Brenner, retired, in 1:20, out 2:05, brought coffee."],
	"clue_brenner_alone": [5, "Doyle at the copier 1:50 to 1:56; Walt alone in her office at 1:52."],
	"knows_brenner": [5, "W.B. is Walter Brenner."],
	"clue_takes_hint": [5, "Ike: Danny's Takes account, last upload Tuesday 11:52 p.m. Hint: \"the knock, the way I play it.\""],
	"knows_password": [5, "The knock is D, E, C, A, F. Decaf."],
	"clue_take": [5, "The take: Pryce, Haskell, Brenner. \"Then pay him, Walt.\""],
	"clue_cabin_clip": [5, "Kenji's November cabin card: Brenner in the back seat at 1:12 a.m. Wednesday, wiping a revolver, Danny's phone in his lap."],
	"clue_brenner_number": [5, "Brenner's cell, 213-555-0163, from Vance."],
}

var flags: Dictionary = {}
var inventory: Array[String] = []
var selected_item: String = ""
var current_room: String = "squad_room"
var player_position: Vector2 = Vector2.ZERO


func reset() -> void:
	flags = {}
	inventory = ["notebook"]
	selected_item = ""
	current_room = "squad_room"
	player_position = Vector2.ZERO
	inventory_changed.emit()


# --- flags --------------------------------------------------------------
func set_flag(key: String, value: Variant = true) -> void:
	flags[key] = value


func flag(key: String) -> bool:
	return bool(flags.get(key, false))


func current_case() -> int:
	## The case Ray is working: each one starts when Otis's call ends the one before.
	if flag("case4_done"):
		return 5
	if flag("case3_done"):
		return 4
	if flag("case2_done"):
		return 3
	return 2 if flag("case1_done") else 1


func clues(case_no := 0) -> Array[String]:
	## Clue ids Ray has written down (for one case, or all of them with 0), in notebook order.
	var out: Array[String] = []
	for id: String in CLUES:
		if flag(id) and (case_no == 0 or int(CLUES[id][0]) == case_no):
			out.append(id)
	return out


func clue_text(id: String) -> String:
	return String(CLUES[id][1])


# --- inventory ----------------------------------------------------------
func has_item(id: String) -> bool:
	return inventory.has(id)


func add_item(id: String) -> void:
	if not inventory.has(id):
		inventory.append(id)
		inventory_changed.emit()


func remove_item(id: String) -> void:
	inventory.erase(id)
	if selected_item == id:
		select_item("")
	inventory_changed.emit()


func select_item(id: String) -> void:
	selected_item = id
	item_selected.emit(id)


func item_name(id: String) -> String:
	return ITEMS.get(id, {}).get("name", id)


func item_icon(id: String) -> Texture2D:
	return load("res://assets/items/%s.png" % id)


# --- save / load ----------------------------------------------------------
func save_game() -> bool:
	var data := {
		"version": 1,
		"flags": flags,
		"inventory": inventory,
		"room": current_room,
		"pos": [player_position.x, player_position.y],
	}
	var f := FileAccess.open(SAVE_PATH, FileAccess.WRITE)
	if f == null:
		return false
	f.store_string(JSON.stringify(data, "\t"))
	return true


func has_save() -> bool:
	return FileAccess.file_exists(SAVE_PATH)


func load_game() -> bool:
	if not has_save():
		return false
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(SAVE_PATH))
	if typeof(parsed) != TYPE_DICTIONARY:
		return false
	flags = parsed.get("flags", {})
	inventory.clear()
	for id in parsed.get("inventory", []):
		inventory.append(String(id))
	current_room = String(parsed.get("room", "squad_room"))
	var p: Array = parsed.get("pos", [0, 0])
	player_position = Vector2(float(p[0]), float(p[1]))
	selected_item = ""
	inventory_changed.emit()
	return true
