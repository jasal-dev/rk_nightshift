class_name Case5
## Shared pieces of Case 5, "Last Call": the cast's speech colours, the start of the case, Ray's phone (Ike, the take,
## the text to Brenner), Sal's tab book and Danny's set list, the drives to the lab and the pier, and the credits with
## their end cards. The street, the Blue Note's bar and back room and Room 214 connect on foot; Pier 9 has no way back.

const BRENNER_COLOR := Color(0.62, 0.68, 0.76)    ## gunmetal
const TEO_COLOR := Color(0.88, 0.8, 0.62)         ## sand
const MARA_COLOR := Color(0.54, 0.66, 1.0)        ## ink blue
const OKAFOR_COLOR := Color(0.84, 0.6, 0.86)      ## plum
const PRYCE_COLOR := Color(0.96, 0.9, 0.62)       ## pale gold
const HASKELL_COLOR := Color(0.88, 0.64, 0.68)    ## dusty rose
const DANNY_COLOR := Color(1.0, 0.97, 0.88)       ## ivory
const NINA_COLOR := Color(0.75, 0.9, 0.7)
const SAL_COLOR := Color(1.0, 0.62, 0.72)
const DOYLE_COLOR := Color(0.7, 0.85, 1.0)
const OTIS_COLOR := Color(1.0, 0.85, 0.5)
const TINY_COLOR := Color(0.86, 0.74, 0.56)
const VANCE_COLOR := Color(0.78, 0.74, 0.9)
const STAGE := Color(0.62, 0.62, 0.66)            ## stage directions in the take
const CALL_AT := Vector2(1500, 230)               ## a voice on Ray's phone
const TAKE := preload("res://assets/rooms/blue_note_take.png")
const SET_LIST := preload("res://assets/ui/set_list.png")
const KNOCK := ["D", "E", "C", "A", "F"]

## Case 4 things Ray leaves behind when Otis calls about Sal. The lab receipt and the seeds stay pinned on the board.
const CASE4_ITEMS := ["lens_shard", "lens_piece", "valet_ticket", "pryce_invite", "lab_receipt", "danny_phone"]


static func start(main: Node) -> void:
	## Out of Room 214 and across the street: the Case 5 card is already up when this runs.
	for id: String in CASE4_ITEMS:
		Game.remove_item(id)
	Game.set_flag("case5_started")
	Game.add_item("ray_phone")


# --- Ray's phone ------------------------------------------------------------------------------------------------
static func phone(main: Node) -> void:
	## Texts and Calls. Ike is on speed dial; after Vance, a new text to Walt's number. At sunrise it's where the drive goes.
	if main.room.room_id == "pier9_sunrise" and main.room.has_method("choose_ending") and not Game.flag("ending_chosen"):
		await main.room.choose_ending()
		return
	var tab := 0
	while true:
		var rows: Array = []
		var keys: Array = []
		var body := ""
		if tab == 0:
			body = "Maya: thats u too\nMe: Go to sleep."
			if Game.flag("bait_sent"):
				body += "\n\nMe to 213-555-0163: Pier 9, sunrise.\n213-555-0163: Wrong number, son.\n213-555-0163: Sunrise."
			elif Game.flag("clue_brenner_number"):
				rows.append("New message to 213-555-0163"); keys.append("text")
		else:
			body = "Recent: Front desk (Otis). Lt. Doyle. Ike Feld, lab."
			rows.append("Call Ike Feld (lab)"); keys.append("ike")
		var pick: String = await main.device("Ray's phone", ["Texts", "Calls"], tab, body, rows)
		if pick.begins_with("tab:"):
			tab = int(pick.substr(4))
			continue
		main.ui.hide_device()
		if pick == "close":
			return
		var k: String = keys[int(pick.substr(4))]
		if k == "text":
			await text_brenner(main)
		else:
			await call_ike(main)
		return


static func call_ike(main: Node) -> void:
	await main.player.play_action("use")
	if Game.flag("heard_take"):
		await main.voice("Kessler. The drive's in an evidence bag with your name on it. Come get it before you do anything stupid.", CALL_AT, Case4.IKE_COLOR)
	elif Game.flag("knows_password"):
		if main.room.room_id != "blue_note_bar":
			await main.say("Not out here. I want to hear it where he played it.")
		else:
			await take(main)
	elif Game.flag("clue_takes_hint"):
		await main.say("I've got three tries and no answer. Not yet.")
	else:
		await main.voice("You said one hour, Kessler. Go away so I can do it.", CALL_AT, Case4.IKE_COLOR)


static func text_brenner(main: Node) -> void:
	## Puzzle 6.3, step three: the bait.
	if not Game.flag("otis_backup"):
		await main.say("Not yet. If he comes, I want a car at the end of that pier that nobody upstairs knows about.")
		return
	await main.player.play_action("use")
	await main.text_message("This is Kessler. I have Danny Reyes's phone, and I know what's on it. Pier 9, San Pedro, sunrise. Come alone and we'll talk about your retirement.", true, "213-555-0163")
	await main.wait(1.2)
	await main.text_message("Wrong number, son.", false)
	await main.wait(1.6)
	await main.text_message("Sunrise.", false)
	main.ui.hide_phone()
	Game.set_flag("bait_sent")
	await main.narrate("He'll come alone. A man like Walt doesn't tell the boss he left a loose end. He ties it off himself.")


# --- Sal's tab book, Danny's set list -------------------------------------------------------------------------------
static func read_tab_book(main: Node) -> void:
	## Puzzle 2.1: three bookmarked pages.
	var pencil := Color(0.2, 0.22, 0.3)
	main.ui.show_paper("SAL'S TAB BOOK  -  THIS WEEK", "WED    CLOSED (DANNY)\nTHU    CLOSED (DANNY)\n\nFRI\n12:30   KESSLER, THRU DOOR.   N/C.\n 3:20   W.B.   CLUB SODA.   N/C.", "", pencil)
	await main.say("Closed since Tuesday, and Sal still wrote down who came. Me, through the door.")
	await main.say("Then W.B., a club soda, no charge, at three-twenty. Sal let somebody in and poured him one on the house.")
	main.clue("clue_wb")
	await main.say("If it isn't in the book, it didn't happen. Sal made sure this did.")
	main.ui.show_paper("SAL'S TAB BOOK  -  TUESDAY", "11:00   CLOSED TO PUBLIC.\nPRIVATE BOOKING, BACK BOOTH, 3.\nMACALLAN 18  x2,  CLUB SODA.\nCASH, NO NAMES.\nD.R. PLAYS LATE,  +$200.", "", pencil)
	await main.say("Tuesday. The night Danny died. A private party in the back booth, three men, cash, no names. Two eighteen-year-old Scotches and a club soda.")
	main.clue("clue_booth_tuesday")
	await main.say("Club soda again.")
	main.ui.show_paper("SAL'S TAB BOOK  -  THE MARGIN", "Every night, the same line, in the same square capitals:", "D.R.  DECAF", pencil)
	await main.say("D.R., decaf. Every night for two years. Sal cut him off the real stuff.")
	main.clue("clue_decaf")
	main.ui.hide_paper()


static func read_set_list(main: Node) -> void:
	## Puzzle 5.1: Tuesday's set, and the staff under "AFTER: for Sal".
	main.ui.show_closeup(SET_LIST)
	await main.say("Tuesday's set, in pencil. 'Round Midnight, for Tiny, if he's in. Body and Soul. Blue in Green. Lush Life.")
	await main.say("And under \"AFTER: for Sal\", one short staff. Five notes. Two slow, three fast.")
	await main.say("He wrote the knock down. I just have to read it.")
	main.ui.hide_paper()


# --- the take (Puzzle 5.3) -------------------------------------------------------------------------------------------
static func take(main: Node) -> void:
	var first := not Game.flag("heard_take")
	await main.voice("Talk to me.", CALL_AT, Case4.IKE_COLOR)
	await main.say("D, E, C, A, F. Lowercase, I'd guess. Decaf.")
	await main.voice("(typing) ...One try. Okay. I'm in. Two years of takes, Thursdays mostly.", CALL_AT, Case4.IKE_COLOR)
	await main.voice("Tuesday. Last upload, eleven fifty-two. He called it \"tues late, practice.\" Eleven minutes.", CALL_AT, Case4.IKE_COLOR)
	await main.say("Play it.")
	await main.voice("I'm not putting this on your phone, Ray. Your phone belongs to the city. I'll play it down the line. Sit somewhere.", CALL_AT, Case4.IKE_COLOR)
	await main.ui.fade_to(1.0, 0.8)
	main.ui.show_scene(TAKE)
	await main.ui.fade_to(0.0, 1.2)
	var lines := [
		["", "Piano: 'Round Midnight, slow.", STAGE],
		["HASKELL", "Harlan, not here. Christ.", HASKELL_COLOR],
		["PRYCE", "Ted, nobody in this room is listening to anything but the music. That's why I like it here.", PRYCE_COLOR],
		["", "Paper rustles.", STAGE],
		["PRYCE", "The second fifty. The rest after the vote.", PRYCE_COLOR],
		["HASKELL", "Elliot says the hearing will be packed. The neighborhood groups, the jazz people...", HASKELL_COLOR],
		["PRYCE", "Jazz people don't vote, Ted. They barely get up before noon.", PRYCE_COLOR],
		["BRENNER", "The piano player gets up.", BRENNER_COLOR],
		["PRYCE", "Mr. Reyes and I have an arrangement. Eight thousand on Monday, sixteen to come, and he forgets what he heard.", PRYCE_COLOR],
		["BRENNER", "He was close enough to hear, last time. He's close enough now.", BRENNER_COLOR],
		["BRENNER", "You don't pay a man like that three times, Harlan. You pay him once.", BRENNER_COLOR],
		["", "The piano keeps going. One wrong note, then it carries on.", STAGE],
		["PRYCE", "(lightly) Then pay him, Walt.", PRYCE_COLOR],
		["HASKELL", "I didn't hear that. I'm going home.", HASKELL_COLOR],
		["", "The booth creaks. Footsteps. The tune ends. Nobody claps. Then, very close to the microphone, quietly:", STAGE],
		["DANNY", "Got you.", DANNY_COLOR],
		["", "A pause. Then, louder, away from the phone:", STAGE],
		["DANNY", "Sal, I'm taking five.", DANNY_COLOR],
		["SAL", "(far off) Take an umbrella, kid.", SAL_COLOR],
	]
	for l: Array in lines:
		var who: String = l[0]
		await main.caption((who + ": " if who != "" else "") + String(l[1]), l[2], not first)
	await main.ui.fade_to(1.0, 0.8)
	main.ui.hide_scene()
	await main.ui.fade_to(0.0, 0.8)
	Game.set_flag("heard_take")
	main.clue("clue_take")
	await main.say("(barely) Then pay him, Walt.")
	await main.narrate("Three men in a booth, setting the price of a piano player. And Danny ten feet away, playing 'Round Midnight for them like it was any other Tuesday.")
	await main.narrate("He heard every word. He played one wrong note.")
	await main.voice("Ray? I heard it too. I wish I hadn't.", CALL_AT, Case4.IKE_COLOR)
	await main.voice("Here's what I'm doing. I don't touch the original. I image the take to one drive, hashed and logged, in an evidence bag with your name on it.", CALL_AT, Case4.IKE_COLOR)
	await main.voice("Then I send Takes a preservation letter and they freeze the account until a judge signs a warrant. Nobody deletes it, nobody plays it, not even me.", CALL_AT, Case4.IKE_COLOR)
	await main.voice("If somebody killed two people for this, they'll come for the cloud next. Let them find a locked door.", CALL_AT, Case4.IKE_COLOR)
	await main.say("Change the password first.")
	await main.voice("Already did. Something only an idiot would guess. Come get it before you do anything stupid.", CALL_AT, Case4.IKE_COLOR)
	await main.say("I'll come get it on the way to doing something stupid.")
	if Game.flag("asked_cabin_clip"):
		await main.voice("And Ray. Your November card. Wednesday, twelve past one, back seat. A big man in an old raincoat, soaked, wiping down a revolver with a handkerchief.", CALL_AT, Case4.IKE_COLOR)
		await main.voice("In his lap, a phone in a cracked black case with a Blue Note sticker. He tries a passcode twice and gives up. I'm texting you a still.", CALL_AT, Case4.IKE_COLOR)
		await main.say("Smelled like gun oil.")
		main.clue("clue_cabin_clip")


# --- Scene 7: the lab and the drive to the pier ---------------------------------------------------------------------
static func drive_to_lab(main: Node) -> void:
	await main.drive_begin()
	await main.drive_wait(1.5)
	await main.drive_end()


static func drive_to_pier(main: Node) -> void:
	await main.drive_begin()
	await main.drive_wait(1.0)
	await main.narrate("The 110 at six in the morning. Trucks, cabs, and people who couldn't go home. Same as five hours ago. The difference is I know what I'm driving to.")
	await main.drive_wait(0.6)
	await main.narrate("Twenty-six years. You learn the job is mostly paper. Once in a while it's a pier at dawn and a man with a revolver.")
	await main.narrate("I'd rather the paper. The paper doesn't get to choose.")
	await main.drive_end()


# --- the credits ---------------------------------------------------------------------------------------------------------
static func credits(main: Node) -> void:
	## Scene 10 has played: fade to white, then the end cards for this ending, the ones that depend on what Ray did, and the
	## ones everybody sees. A click moves on; each card also moves on by itself.
	var cards: Array = []     ## [still, line]
	var bar := load("res://assets/rooms/blue_note_bar.png")
	var pier := load("res://assets/rooms/pier9_sunrise.png")
	var squad := load("res://assets/rooms/squad_room.png")
	var glass := load("res://assets/rooms/glass_house.png")
	if Game.flag("ending_doyle_best"):
		cards.append([load("res://assets/endcards/pryce_cuffs.png"), "Harlan Pryce was indicted for bribery and for conspiracy to murder Daniel Reyes."])
		cards.append([glass, "Councilman Ted Haskell resigned and pleaded guilty to accepting bribes. Hollywood Core was withdrawn."])
		cards.append([pier, "Walter Brenner was convicted of the murders of Daniel Reyes and Salvatore Moretti. The .38 matched."])
		cards.append([squad, "Lt. Maureen Doyle testified for two days. She kept her badge. She stopped taking visitors after midnight."])
		cards.append([bar, "The Blue Note reopened in November. Nina Alvarez runs the floor. Danny's piano stays where it is, lid up."])
	elif Game.flag("ending_doyle_bitter"):
		cards.append([pier, "Walter Brenner pleaded guilty to the murder of Salvatore Moretti. The Reyes case was closed as a robbery."])
		cards.append([squad, "The drive was logged into Internal Affairs on Friday. By Monday there was no record of it. Nobody asked a judge for Danny's account, and after ninety days Takes let the hold lapse."])
		cards.append([glass, "Hollywood Core passed seven to six. Councilman Haskell voted yes."])
		cards.append([load("res://assets/endcards/pryce_shovel.png"), "Harlan Pryce broke ground on Pryce Hollywood in March. He used a gold shovel."])
		cards.append([bar, "The Blue Note closed on New Year's Eve. Nina Alvarez took a one-way flight to Lisbon."])
		cards.append([squad, "Lt. Maureen Doyle made captain the following spring."])
	elif Game.flag("ending_by_book"):
		cards.append([pier, "Walter Brenner was charged with both murders and denied bail."])
		cards.append([load("res://assets/rooms/crane_garage.png"), "Facing the hit-and-run, Elliot Crane told the DA about the envelopes. Councilman Haskell resigned in February, citing his family."])
		cards.append([load("res://assets/endcards/pryce_press.png"), "Harlan Pryce's lawyers have filed forty-one motions. He has not been charged. Hollywood Core is postponed indefinitely."])
		cards.append([squad, "Lt. Maureen Doyle was reassigned to Valley Traffic."])
		cards.append([bar, "The Blue Note's lease is in court. It stays open while it is."])
	else:
		cards.append([load("res://assets/rooms/street_crime.png"), "\"The Piano Player Was Close Enough to Hear\" ran at noon. The audio was played eleven million times."])
		cards.append([glass, "Pryce Development withdrew Hollywood Core that Monday. Councilman Haskell resigned the same week. Walter Brenner was charged with both murders."])
		cards.append([load("res://assets/endcards/pryce_umbrella.png"), "Harlan Pryce has not been charged. He says he has never been to a jazz club."])
		cards.append([bar, "Detective Ray Kessler was suspended for sixty days for releasing evidence to the press. He spent them at the Blue Note."])
		cards.append([squad, "Lt. Maureen Doyle's name appeared in paragraph nine. She asked for a transfer."])
	if Game.flag("brenner_talked_down"):
		cards.append([pier, "Walt Brenner wrote Maureen Doyle one letter from county jail. She didn't open it."])
	if Game.flag("brenner_forced"):
		cards.append([pier, "Walt Brenner's right wrist never set properly. Tiny says he's sorry about that."])
	if Game.flag("morty_lyle"):
		cards.append([load("res://assets/rooms/stardust_shop.png"), "Morty Kahn buried Gus Lindqvist with Lyle Brandt's Oscar."])
	cards.append([load("res://assets/rooms/kenji_apartment.png"), "Carla Mendes got her job back."])
	cards.append([load("res://assets/rooms/river_channel.png"), "Calvin \"Preacher\" Odom still reads to the river. Officer Doss brings him coffee on Thursdays."])
	cards.append([load("res://assets/rooms/fletcher_bridge.png"), "Owen Tate's mother started a scholarship at his community college, for nursing students who work nights."])
	cards.append([load("res://assets/rooms/mulholland_overlook.png"), "Dr. Anita Shah got her free coffee. Ray paid."])
	cards.append([pier, "Tiny Ruiz still sits under the awning at Pier 9 with the radio on KJAZZ."])
	main.busy = true
	main.ui.fade_rect.color = Color(1, 1, 1, main.ui.fade_rect.color.a)
	await main.ui.fade_to(1.0, 1.6)
	await main.wait(0.8)
	for c: Array in cards:
		main.ui.show_endcard(c[0], c[1])
		await main.ui.fade_to(0.0, 0.8)
		await main.drive_wait(clampf(2.5 + String(c[1]).length() * 0.045, 4.0, 8.0))
		await main.ui.fade_to(1.0, 0.6)
	main.ui.fade_rect.color = Color(0, 0, 0, 1)
	main.ui.hide_scene()
	Game.set_flag("game_done")
	await main.the_end()
