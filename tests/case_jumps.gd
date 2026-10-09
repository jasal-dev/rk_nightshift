extends "res://tests/playthrough.gd"
## The title screen's Case 2 to 5 buttons: each one shows its card, drives to the case's first room, and starts the
## case with everything from the cases before it (every clue, the board pins, the notebook) and nothing else
## in the inventory. Nothing is saved: the player's quicksave is the same afterwards.
##
## Godot_v4.7_console.exe --headless --path . res://tests/case_jumps.tscn
## Exit code 0 = every jump starts its case; 1 = something went wrong (see the output).

const JUMPS := {
	2: ["mulholland_overlook", ["case2_started", "board_envelope", "case1_deduced"]],
	3: ["stardust_shop", ["case3_started", "met_park3", "board_ride_receipt", "case2_deduced"]],
	4: ["fletcher_bridge", ["case4_started", "met_doss", "board_brenner_card", "case3_deduced"]],
	5: ["street_crime", ["case5_started", "board_danny_phone", "board_pryce_invite", "case4_deduced"]],
}


func _run() -> void:
	for n: int in JUMPS:
		await _jump(n)
		if _failed:
			return
		main._title()                                   # back to the title screen for the next one
	var save_now := FileAccess.get_file_as_string(Game.SAVE_PATH) if Game.has_save() else ""
	if save_now != _user_save:
		_fail("a case jump shouldn't touch the quicksave")
		return
	print("CASE JUMPS OK - Cases 2 to 5 start from the title screen.")
	_quit(0)


func _jump(n: int) -> void:
	print("Case %d from the title screen" % n)
	while not main._on_title and not _failed:
		await get_tree().process_frame
	_step = "jump to Case %d" % n
	_step_started = Time.get_ticks_msec()
	main.ui.title.case_buttons[n - 2].pressed.emit()
	while not main._waiting_click and not _failed:      # the case card
		await get_tree().process_frame
	if not main.ui.card.visible:
		_fail("Case %d should start with its card" % n)
	main._waiting_click = false
	await expect_room(String(JUMPS[n][0]))
	var flags: Array[String] = []
	flags.assign(JUMPS[n][1])
	expect(flags)
	for id: String in Game.CLUES:
		if int(Game.CLUES[id][0]) < n and not Game.flag(id):
			_fail("Case %d should start with %s in the notebook" % [n, id])
		elif int(Game.CLUES[id][0]) >= n and Game.flag(id):
			_fail("Case %d shouldn't start with %s" % [n, id])
	for d in range(1, 5):
		if Game.flag("case%d_done" % d) != (d < n):
			_fail("case%d_done should be %s at the start of Case %d" % [d, d < n, n])
	var want: Array[String] = ["notebook"]
	if n == 5:
		want.append("ray_phone")
	if Game.inventory != want:
		_fail("Case %d should start with just %s, not %s" % [n, want, Game.inventory])
	print("  in %s, %d clues, inventory %s" % [main.room.room_id, Game.clues().size(), Game.inventory])
