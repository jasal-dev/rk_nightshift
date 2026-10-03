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
}

## Notebook clues: facts Ray writes down. Each is a flag of the same name (set with Main.clue()),
## and each can be pinned as evidence on the murder board.
const CLUES := {
	"clue_wallet_phone": "Wallet left on the body. Phone never found.",
	"clue_38": "Shot once, .38, close range.",
	"clue_knock": "Danny's knock: two slow, three fast. Nina gave it to me.",
	"clue_vance": "Vance. Pier 9. Green door.",
	"clue_paid": "Danny paid Vance $8,000 in full, cash, Tuesday afternoon. He was shot that night.",
	"clue_alibi": "Vance was on his boat in Avalon the night Danny died.",
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


func clues() -> Array[String]:
	## Clue ids Ray has written down, in notebook order.
	var out: Array[String] = []
	for id: String in CLUES:
		if flag(id):
			out.append(id)
	return out


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
