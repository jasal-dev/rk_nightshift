extends Node
## Global game state (autoload "Game"): flags, inventory, current room, save/load.
## Everything that must survive a room change or a save lives here.

signal inventory_changed
signal item_selected(id: String)

const SLOT_COUNT := 3
const SAVE_VERSION := 2
const LEGACY_PATH := "user://savegame.json"      ## the old single quicksave; copied into slot 1 on first run (Game._ready)
const SHOT_SIZE := Vector2i(384, 216)             ## a slot's screenshot

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

## Each case's title, as on its card and at the top of its notebook page.
const CASE_TITLES := {
	1: "Case 1: Dead Piano Player",
	2: "Case 2: Five Stars",
	3: "Case 3: Walk of Fame",
	4: "Case 4: Low Water",
	5: "Case 5: Last Call",
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
	"clue_off_app": [2, "After 11:52 Kenji drove off the app: home, Norm's, the overlook. Someone he knew."],
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
	"clue_two_tracks": [4, "The bike came down the stairs with somebody in big boots. Owen came down the bank with somebody else."],
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
var slot := 1              ## the save slot the last save or load used (the save and load menus set it)


func _ready() -> void:
	_migrate_legacy()


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
	return case_of(flags)


static func case_of(f: Dictionary) -> int:
	## The same, for any flag set (a save slot's).
	if bool(f.get("case4_done", false)):
		return 5
	if bool(f.get("case3_done", false)):
		return 4
	if bool(f.get("case2_done", false)):
		return 3
	return 2 if bool(f.get("case1_done", false)) else 1


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
## Three slots: user://save_N.json (flags, inventory, room, position, case, local time) and save_N.png (a screenshot).
## Writes go to a temp file that then replaces the slot, and the slot it replaces is kept as save_N.json.bak, which
## a load falls back to if the slot itself turns out to be damaged.
static func slot_path(n: int) -> String:
	return "user://save_%d.json" % n


static func shot_path(n: int) -> String:
	return "user://save_%d.png" % n


func _abs(path: String) -> String:
	return ProjectSettings.globalize_path(path)


func _migrate_legacy() -> void:
	if FileAccess.file_exists(LEGACY_PATH) and not FileAccess.file_exists(slot_path(1)):
		if _write_atomic(slot_path(1), FileAccess.get_file_as_string(LEGACY_PATH)):
			DirAccess.rename_absolute(_abs(LEGACY_PATH), _abs(LEGACY_PATH + ".migrated"))


func _write_atomic(path: String, text: String) -> bool:
	var tmp := path + ".tmp"
	var f := FileAccess.open(tmp, FileAccess.WRITE)
	if f == null:
		return false
	f.store_string(text)
	f.close()
	if FileAccess.get_file_as_string(tmp) != text:
		return false
	if FileAccess.file_exists(path):
		DirAccess.copy_absolute(_abs(path), _abs(path + ".bak"))
		DirAccess.remove_absolute(_abs(path))
	return DirAccess.rename_absolute(_abs(tmp), _abs(path)) == OK


func save_game(n := 0, shot: Image = null) -> bool:
	## Saves into slot `n` (the current slot by default), with a screenshot if given.
	n = clampi(n if n > 0 else slot, 1, SLOT_COUNT)
	var t := Time.get_datetime_dict_from_system(false)
	var data := {
		"version": SAVE_VERSION,
		"flags": flags,
		"inventory": inventory,
		"room": current_room,
		"pos": [player_position.x, player_position.y],
		"case": current_case(),
		"time": "%04d-%02d-%02d %02d:%02d" % [t["year"], t["month"], t["day"], t["hour"], t["minute"]],
	}
	if not _write_atomic(slot_path(n), JSON.stringify(data, "	")):
		return false
	slot = n
	if shot != null and not shot.is_empty():
		var img := shot.duplicate() as Image
		img.resize(SHOT_SIZE.x, SHOT_SIZE.y, Image.INTERPOLATE_BILINEAR)
		img.save_png(shot_path(n))
	else:
		DirAccess.remove_absolute(_abs(shot_path(n)))
	return true


func has_save(n := 0) -> bool:
	## A file in slot `n`, or in any slot with the default (it may still be damaged; see slot_info).
	if n > 0:
		return FileAccess.file_exists(slot_path(n))
	for i in range(1, SLOT_COUNT + 1):
		if FileAccess.file_exists(slot_path(i)):
			return true
	return false


func _read_slot(n: int) -> Dictionary:
	## The slot's save (or, failing that, its .bak), checked; {} when there is none that can be loaded.
	for path: String in [slot_path(n), slot_path(n) + ".bak"]:
		if not FileAccess.file_exists(path):
			continue
		var json := JSON.new()
		if json.parse(FileAccess.get_file_as_string(path)) != OK or typeof(json.data) != TYPE_DICTIONARY:
			continue
		var d: Dictionary = json.data
		var pos: Variant = d.get("pos")
		if typeof(d.get("flags")) != TYPE_DICTIONARY or typeof(d.get("inventory")) != TYPE_ARRAY 				or typeof(d.get("room")) != TYPE_STRING or typeof(pos) != TYPE_ARRAY or (pos as Array).size() != 2:
			continue
		if not ResourceLoader.exists("res://scenes/rooms/%s.tscn" % d["room"]):
			continue
		return d
	return {}


func slot_info(n: int) -> Dictionary:
	## {} for an empty slot, {"damaged": true} for one that can't be loaded, else {"case", "time", "shot"} (a Texture2D or null).
	if not has_save(n):
		return {}
	var d := _read_slot(n)
	if d.is_empty():
		return {"damaged": true}
	var when: String = String(d.get("time", ""))
	if when == "":      # saved by the old single-slot version: its file time, to the minute
		var unix := int(FileAccess.get_modified_time(slot_path(n))) + int(Time.get_time_zone_from_system().get("bias", 0)) * 60
		when = Time.get_datetime_string_from_unix_time(unix, true).substr(0, 16)
	var tex: Texture2D = null
	if FileAccess.file_exists(shot_path(n)):
		var img := Image.load_from_file(_abs(shot_path(n)))
		if img != null and not img.is_empty():
			tex = ImageTexture.create_from_image(img)
	return {"case": case_of(d["flags"]), "time": when, "shot": tex}


func latest_slot() -> int:
	## The slot saved most recently (the one F9 loads on the title screen and at a case card), or the current one.
	var best := slot
	var best_t := -1
	for i in range(1, SLOT_COUNT + 1):
		if FileAccess.file_exists(slot_path(i)):
			var t := int(FileAccess.get_modified_time(slot_path(i)))
			if t > best_t:
				best_t = t
				best = i
	return best


func load_game(n := 0) -> bool:
	## Loads slot `n` (the current slot by default). Nothing changes if the slot is empty or damaged.
	n = clampi(n if n > 0 else slot, 1, SLOT_COUNT)
	var d := _read_slot(n)
	if d.is_empty():
		return false
	slot = n
	flags = d["flags"]
	inventory.clear()
	for id in d["inventory"]:
		inventory.append(String(id))
	current_room = String(d["room"])
	var p: Array = d["pos"]
	player_position = Vector2(float(p[0]), float(p[1]))
	selected_item = ""
	inventory_changed.emit()
	return true


func snapshot_saves() -> Dictionary:
	## Every file of every slot, for a test to put back afterwards (restore_saves).
	var out := {}
	for i in range(1, SLOT_COUNT + 1):
		for path in [slot_path(i), slot_path(i) + ".bak", shot_path(i)]:
			if FileAccess.file_exists(path):
				out[path] = FileAccess.get_file_as_bytes(path)
	return out


func restore_saves(snap: Dictionary) -> void:
	for i in range(1, SLOT_COUNT + 1):
		for path in [slot_path(i), slot_path(i) + ".bak", shot_path(i)]:
			if snap.has(path):
				var f := FileAccess.open(path, FileAccess.WRITE)
				f.store_buffer(snap[path])
				f.close()
			elif FileAccess.file_exists(path):
				DirAccess.remove_absolute(_abs(path))
