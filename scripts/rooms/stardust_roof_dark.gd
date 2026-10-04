extends Room
## The Stardust roof before the sign is back on (Case 3, scene 4, dark state): the sign's timer switched it off at one.
## Almost black; only the darkness and the door back down respond. The breaker is on the fuse panel in the office.


func _ready() -> void:
	super._ready()
	add_rain(380, -0.25)


func on_enter(_from_room: String) -> void:
	await main.wait(0.3)
	await main.say("Can't see my own feet. There's a sign up here the size of a bus. It must have a switch.")


func interact(hs: Hotspot, verb: String, item: String) -> void:
	match hs.id:
		"darkness":
			if item == "uv_lamp":
				await main.say("Lovely. Now the rain is purple.")
			elif item != "":
				await default_response(verb, item)
			elif verb == "look":
				await main.say("Can't see my own feet. There's a sign up here the size of a bus. It must have a switch somewhere.")
			else:
				await main.say("I'm not walking around a roof blind. Gus already showed me how that ends.")

		"roof_door":
			if verb == "look":
				await main.say("Back down to the office.")
			elif item != "":
				await default_response(verb, item)
			else:
				await main.change_room("stardust_office", "stardust_roof_dark")

		_:
			await default_response(verb, item)
