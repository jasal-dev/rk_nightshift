class_name Case4
## Shared pieces of Case 4, "Low Water": the cast's speech colours, the drive to the river, the car menu between the
## bridge, the glass house on Glendower and Crane's garage, Otis running the plate, and the drive to the night lab
## with Maya's texts. The bridge and the channel connect on foot.

const PREACHER_COLOR := Color(0.8, 0.6, 0.36)     ## bronze
const DOSS_COLOR := Color(0.56, 0.7, 0.86)        ## steel blue
const COURTNEY_COLOR := Color(0.8, 0.7, 0.96)     ## lilac
const ANDRE_COLOR := Color(0.58, 0.92, 0.78)      ## mint
const CRANE_COLOR := Color(0.96, 0.92, 0.78)      ## cream
const IKE_COLOR := Color(0.74, 0.94, 0.38)        ## lime
const OTIS_COLOR := Color(1.0, 0.85, 0.5)
const CHOMP := Color(0.86, 0.66, 0.06)            ## the Chomp app's yellow
const CALL_AT := Vector2(1500, 230)               ## a voice on Ray's phone
const INVITE_RENDER := preload("res://assets/ui/invite_render.png")
const HEADLIGHT := preload("res://assets/ui/headlight_hole.png")
const PIECE_LENS := preload("res://assets/ui/headlight_piece.png")
const PIECE_SHARD := preload("res://assets/ui/headlight_shard.png")

## Case 3 things Ray leaves behind when he goes out on the river call. Brenner's card stays pinned on the board.
const CASE3_ITEMS := ["gus_keys", "uv_lamp", "catalogue", "star_earring", "fake_oscar", "brenner_card"]


static func drive_in(main: Node) -> void:
	## Scene 1: off the freeway at Fletcher Drive, the river a dark gap between the houses, and Shah's texts.
	for id: String in CASE3_ITEMS:
		Game.remove_item(id)
	Game.set_flag("case4_started")
	await main.drive_begin()
	await main.drive_wait(1.0)
	await main.narrate("The Los Angeles River. Most people in this town don't know it's there. The ones who do mostly live under it.")
	await main.drive_wait(0.5)
	await main.text_message("fletcher bridge. east end. bring boots", false, "Anita Shah")
	await main.text_message("the uniforms are very pleased with themselves", false)
	await main.narrate("A kid on a bike, a man in a tent, and a patrol cop who wants to be home by five. Somebody's going to be disappointed.")
	await main.drive_end()


static func car_menu(main: Node, here: String) -> void:
	## Where to next. Otis runs the plate first if Ray has one; Room 214 opens once Crane is in custody, by way of the lab.
	if Game.flag("clue_plate") and not Game.flag("clue_crane_id"):
		await plate_call(main)
	var opts: Array = []
	var dest: Array = []
	if here != "fletcher_bridge":
		opts.append("Fletcher Drive bridge"); dest.append("fletcher_bridge")
	if here != "glass_house" and Game.flag("clue_last_drop"):
		opts.append("Glendower Avenue, Los Feliz"); dest.append("glass_house")
	if here != "crane_garage" and Game.flag("clue_crane_id"):
		opts.append("Crane's house, Mount Washington"); dest.append("crane_garage")
	if Game.flag("crane_arrested"):
		opts.append("Room 214"); dest.append("night_lab")
	opts.append("Stay here.")
	var c: int = await main.choose(opts)
	if c >= dest.size():
		return
	var to: String = dest[c]
	match to:
		"fletcher_bridge":
			await main.say("Back to the river.")
		"glass_house":
			await main.say("Up the hill, where the delivery ended and the party didn't.")
		"crane_garage":
			await main.say("Mount Washington. The kind of hill where the streets give up and become stairs.")
		"night_lab":
			await main.say("One stop on the way. Danny's waited two nights; he can wait for a red light.")
			await drive_to_lab(main)
			await main.change_room("night_lab", "drive")
			return
	await main.drive_begin()
	await main.drive_wait(4.0)
	await main.drive_end()
	await main.change_room(to, here)


static func plate_call(main: Node) -> void:
	## Puzzle 4.2: Otis runs 8KXD392.
	await main.player.play_action("use")
	await main.voice("Room 214. The night is young and so am I.", CALL_AT, OTIS_COLOR)
	await main.say("Run a plate for me. Eight, K, X, D, three, nine, two. Blue-gray Audi.")
	await main.voice("Registered to an Elliot Crane, Mount Washington. Crane, Crane... Ray, that's Councilman Haskell's chief of staff.", CALL_AT, OTIS_COLOR)
	await main.voice("He's on the news every time Haskell won't comment.", CALL_AT, OTIS_COLOR)
	await main.say("He's about to be on it again.")
	await main.voice("You're about to ruin a whole lot of mornings.", CALL_AT, OTIS_COLOR)
	await main.say("Owen Tate's mother's already up. Send Doss to meet me there. Tell him to bring his cuffs. He's had them on the wrong man all night.")
	await main.voice("I'll put it nicer.", CALL_AT, OTIS_COLOR)
	main.clue("clue_crane_id")


static func drive_to_lab(main: Node) -> void:
	## Scene 6: the lights of the 5, an empty lot at Cal State LA, and Maya, who can't sleep.
	await main.drive_begin()
	await main.drive_wait(1.2)
	await main.text_message("cant sleep. stats midterm at 9", false, "Maya")
	await main.text_message("You'll do fine.", true)
	await main.text_message("what r u doing", false)
	await main.text_message("Standing next to a river.", true)
	await main.text_message("is it pretty", false)
	await main.text_message("No. But it's trying.", true)
	await main.text_message("thats u too", false)
	await main.text_message("Go to sleep.", true)
	await main.drive_end()


static func drive_back(main: Node) -> void:
	## From the lab to Room 214: a short hop, no texts.
	await main.drive_begin()
	await main.drive_wait(2.5)
	await main.drive_end()
