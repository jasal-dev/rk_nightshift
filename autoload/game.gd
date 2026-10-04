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
	"clue_rat": [2, "RAT keyed into the driver's door. Weeks old."],
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
	## The case Ray is working: Case 2 starts once Otis's call ends Case 1.
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
