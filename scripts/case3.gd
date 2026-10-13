class_name Case3
## Shared pieces of Case 3, "Walk of Fame": the cast's speech colours, the drive to Hollywood Boulevard and the drive
## back with Maya's texts. The shop, the back office and the roof connect on foot, so there's no car menu; the shop's
## front door leads back to Room 214 once Pearl is arrested.

const PEARL_COLOR := Color(0.98, 0.7, 0.62)      ## rose gold
const MORTY_COLOR := Color(0.74, 0.76, 0.42)     ## olive
const CHARLIE_COLOR := Color(0.78, 0.8, 0.84)    ## silver grey
const UV_WALL := preload("res://assets/ui/uv_wall.png")
const UV_HEADSHOT := preload("res://assets/ui/uv_headshot.png")

## Case 2 things Ray leaves behind when he goes out on the Stardust call. The ride receipt stays pinned on the board.
const CASE2_ITEMS := ["driver_card", "norms_receipt", "kenji_keys", "card_slip", "frozen_peas", "sd_cards",
		"ride_receipt"]


static func drive_in(main: Node) -> void:
	## Scene 1: off Highland onto Hollywood Boulevard, wet stars in the sidewalk, and a text from Shah.
	for id: String in CASE2_ITEMS:
		Game.remove_item(id)
	Game.set_flag("case3_started")
	await main.drive_begin()
	await main.drive_wait(1.0)
	await main.narrate("Hollywood Boulevard. Twenty-seven hundred stars in the sidewalk, and everybody walks on them.")
	await main.drive_wait(0.5)
	await main.text_message("stardust. back stairs. bring the good coffee not the squad room coffee", false, "Anita Shah")
	await main.text_message("There's no good coffee at three a.m.", true)
	await main.text_message("then just bring yourself", false)
	await main.narrate("An old man, a staircase, and a missing Oscar. In this town the statue gets top billing.")
	await main.drive_end()


static func has_motive_card() -> bool:
	## The board's first slot ("she was selling him out") needs one of these three. Pearl can be arrested without any
	## of them (the phone log and Lyle in the tank break her story), so the drive back and the board check this.
	return Game.flag("clue_practice_sigs") or Game.flag("clue_gold_pen") or Game.flag("clue_morty_bought")


static func drive_back(main: Node) -> void:
	## Scene 6: Highland southbound, the boulevard's lights shrinking in the mirror, and Maya.
	await main.drive_begin()
	await main.drive_wait(1.2)
	if Game.flag("drove_back3"):
		# Went back to the Stardust for a missing card: no second round of Maya's texts
		await main.drive_wait(1.0)
		await main.drive_end()
		return
	Game.set_flag("drove_back3")
	await main.text_message("would u ever want an oscar", false, "Maya")
	await main.text_message("For what?", true)
	await main.text_message("best supporting dad", false)
	await main.text_message("I'd want to know where it's been first.", true)
	await main.text_message("ok thats dark. goodnight", false)
	await main.text_message("It's morning.", true)
	await main.text_message("goodnight anyway", false)
	await main.narrate("Gus Lindqvist kept other people's dreams under glass for forty years. In the end the only real thing in his shop was him.")
	await main.drive_end()
