class_name Case2
## Shared pieces of Case 2, "Five Stars": the cast's speech colours, the drive up Mulholland, the car menu
## that hops between Norm's, Kenji's place and Room 214, and the drive back with Maya's texts.
## Room scripts call these as Case2.car_menu(main, room_id) and so on.

const SHAH_COLOR := Color(0.45, 0.86, 0.82)      ## teal
const PARK_COLOR := Color(1.0, 0.78, 0.56)       ## light orange
const ROSA_COLOR := Color(1.0, 0.56, 0.5)        ## coral
const HECK_COLOR := Color(0.92, 0.78, 0.32)      ## mustard
const DEVIN_COLOR := Color(0.84, 0.78, 0.98)     ## pale lilac
const BRIELLE_COLOR := Color(1.0, 0.36, 0.76)    ## hot pink (her video only)
const CABBIE_COLOR := Color(0.78, 0.8, 0.84)
const GLIDE := Color(0.12, 0.58, 0.52)           ## the Glide app's teal
const BRIELLE_AT := Vector2(1536, 330)           ## lines from a video on a device screen

## Case 1 things Ray leaves on his desk when he goes out on the rideshare call.
const CASE1_ITEMS := ["case_file", "envelope", "matchbook", "dime", "coffee", "key", "gaff"]


static func drive_up(main: Node) -> void:
	## Scene 1: Cahuenga Pass, then the curves of Mulholland, and a text from Otis.
	for id: String in CASE1_ITEMS:
		Game.remove_item(id)
	Game.set_flag("case2_started")
	await main.drive_begin()
	await main.drive_wait(1.0)
	await main.narrate("Mulholland Drive. Twenty miles of curves along the top of the hills, so the rich can look down on the rest of us.")
	await main.drive_wait(0.5)
	await main.text_message("overlook past the Bowl turnoff. patrol is Officer Park. she's new. be nice", false, "Otis")
	await main.text_message("I'm always nice.", true)
	await main.text_message("be nicer", false)
	await main.narrate("Up here the rain comes in sideways. Down there, four million people are asleep, or wish they were.")
	await main.drive_end()


static func gps_hint(main: Node) -> void:
	## Glide says Kenji's night ended at 11:52. If the player stands around without reading the car's own
	## screen, Ray nudges them toward it, once.
	if not Game.flag("clue_last_trip") or Game.flag("clue_gps") or Game.flag("gps_hint"):
		return
	var n := int(Game.flags.get("gps_idle", 0)) + 1
	Game.set_flag("gps_idle", n)
	if n >= 4:
		Game.set_flag("gps_hint")
		await main.say("Glide says his night ended at eleven fifty-two. I'd like a second opinion. Cars talk too, these days.")


static func car_menu(main: Node, here: String) -> void:
	## Where to next. Each hop is a short drive; Room 214 opens once Devin is in custody.
	var opts: Array = []
	var dest: Array = []
	if here != "norms_diner":
		opts.append("Norm's on Sunset"); dest.append("norms_diner")
	if here != "kenji_apartment":
		opts.append("Kenji's place, Silver Lake"); dest.append("kenji_apartment")
	if Game.flag("devin_arrested"):
		opts.append("Room 214"); dest.append("squad_room")
	opts.append("Not yet.")
	var c: int = await main.choose(opts)
	if c >= dest.size():
		return
	var to: String = dest[c]
	match to:
		"norms_diner":
			await main.say("Norm's. Cherry pie, two coffees, twelve-fourteen.")
		"kenji_apartment":
			await main.say("Home, Silver Lake. Two minutes, eleven fifty-six. Somebody was waiting.")
		"squad_room":
			await main.say("Back to the board.")
			await drive_back(main)
			await main.change_room("squad_room", "street")
			return
	await main.drive_begin()
	await main.drive_wait(4.0)
	await main.drive_end()
	if to == "kenji_apartment" and not Game.flag("met_devin"):
		await doorstep(main)
	await main.change_room(to, here)


static func doorstep(main: Node) -> void:
	## Up a flight of wet outdoor steps, in the dark. Devin opens the door.
	var door := Vector2(960, 560)
	await main.narrate("*knock knock knock*")
	await main.wait(0.8)
	await main.voice("It's two in the morning.", door, DEVIN_COLOR)
	await main.narrate("Detective Kessler, LAPD. Does Kenji Ota live here?")
	await main.voice("Yeah. He's driving. He drives nights. Why?", door, DEVIN_COLOR)
	await main.narrate("May I come in?")


static func drive_back(main: Node) -> void:
	## Scene 5: Sunset westbound, the Hollywood sign lost in the clouds, and Maya.
	await main.drive_begin()
	await main.drive_wait(1.2)
	await main.text_message("do u rate ur uber drivers", false, "Maya")
	await main.text_message("I'm a cop. I rate everybody.", true)
	await main.text_message("what am i", false)
	await main.text_message("Five stars. Would drive again.", true)
	await main.text_message("dad", false)
	await main.text_message("ok that was cute", false)
	await main.narrate("Twenty-nine years old, four point nine eight stars. The man who killed him was the only one who knew he wasn't coming home.")
	await main.drive_end()
