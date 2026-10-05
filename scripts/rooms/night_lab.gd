extends Room
## The crime lab's night intake window at Cal State LA (Case 4, scene 6). Ray hands Danny Reyes's phone to Ike Feld,
## and only to Ike, and gets a receipt (phone_at_lab). The door goes on to Room 214.


func on_enter(_from_room: String) -> void:
	if not Game.flag("at_lab"):
		Game.set_flag("at_lab")
		await main.wait(0.4)
		await _ike("Kessler. You only come here when it's weird.")
		await main.say("It's weird.")


func interact(hs: Hotspot, verb: String, item: String) -> void:
	match hs.id:
		"ike", "tray":
			if verb == "look":
				if hs.id == "ike":
					await main.say("Ike Feld. Nights at the lab for six years. He says the machines are better company.")
				else:
					await main.say("A steel tray under the glass. It's seen worse than a wet phone.")
			elif item == "danny_phone":
				await _hand_over()
			elif item == "lens_piece" or item == "lens_shard":
				await _ike("That's evidence in a different case. Book it properly, I'm not your mom.")
			elif item != "":
				await default_response(verb, item)
			elif Game.flag("phone_at_lab"):
				await _ike("One hour. I heard you. Go away so I can do it.")
			else:
				await _ike("Put something in the tray, Ray. I don't do small talk at this hour. Or any hour.")

		"sign":
			if item != "":
				await default_response(verb, item)
			elif verb == "look":
				await main.say("\"Ringing twice will not make it faster.\" I believe him.")
			else:
				await main.say("I'll ring once.")

		"exit":
			if verb == "look":
				await main.say("Back to the car.")
			elif item != "":
				await default_response(verb, item)
			elif not Game.flag("phone_at_lab"):
				await main.say("Not with Danny's phone still in my pocket.")
			else:
				await Case4.drive_back(main)
				await main.change_room("squad_room", "street")

		_:
			await default_response(verb, item)


func _ike(line: String) -> void:
	await main.voice(line, speaker_at("ike"), Case4.IKE_COLOR)


func _hand_over() -> void:
	await main.player.play_action("use")
	main.take("danny_phone")
	await main.say("I put the phone in the tray. Ike pulls it through and turns it over under his lamp.")
	await _ike("Blue Note sticker. \"If found, call the Blue Note.\"")
	await main.wait(0.6)
	await _ike("Your piano player. Reyes.")
	await main.say("Two nights in the river.")
	await _ike("Phones hate rivers. And the rice thing's a myth, before you ask.")
	await _ike("The board's probably soup. But nobody's phone lives alone anymore, Ray. If he synced it to anything, a cloud, a laptop, a girlfriend's tablet, I can find where it went.")
	await _ike("Give me a few hours.")
	await main.say("You've got one.")
	await _ike("Who do I call?")
	await main.say("Me. Only me. Nobody else hears about this phone, Ike. Not the day shift. Not anybody.")
	await _ike("Nobody ever asks me anything anyway.")
	await main.wait(0.6)
	Game.set_flag("phone_at_lab")
	await main.give("lab_receipt", false)
	await main.say("Danny Reyes's phone. Two nights in the river, and the first thing it found was somebody who'd stay up for it.")
