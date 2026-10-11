extends Node
## Music, ambience and effects. One music track per case, looping, kept playing across room changes; `music()`
## crossfades to another track and does nothing when that track is already on. `ambience()` does the same for the
## background loop (rain in the rooms that show rain, on the title screen and on the drives), so it carries on between
## two rainy rooms and fades out going into a dry one. Footsteps are the player's own (Player, on the SFX bus).
## Main switches tracks on the title screen, at each case card and on every room change (new game, Skip to Case N,
## loading a save), so whatever path got Ray into a case, its track is playing.
## Voice: spoken lines (`speak()`), recorded clips found by speaker and text (`voice_clip()`, assets/voice/lines.json,
## made by tools/tts/gen_voice.py); Main plays one with each line that has one.
## Buses: Master > Music, Voice, SFX (made here, so there's no bus layout file to keep in sync). The Music, Voice and
## Effects (SFX) volumes are set on the settings panel and kept in user://settings.cfg with the other settings.
## Sound sources and licences: assets/sounds/LICENSES.md (the loops are cut by tools/sounds/make_loops.py).

const TRACK_PATH := "res://assets/music/bensound-%s.mp3"
const TITLE_TRACK := "rainyday"
## Case 5, the pier at dawn, the endings, the end cards and the end credits are all "rainyday", as is the title screen.
const CASE_TRACKS := {1: "sleepless", 2: "november", 3: "entenca", 4: "echoofsadness", 5: "rainyday"}
## The licence attributions, as the user wrote them, in that order (shown under Credits and in the end credits).
## Track for each: sleepless, echoofsadness, november, entenca, rainyday.
const MUSIC_CREDITS := [
	"Music I use: Bensound\nLicense code: NEDTC8SIKQPAI6T8\nArtist: Diffie Bosman",
	"Royalty Free Music: Bensound.com/royalty-free-music\nLicense code: YHZCQFSRSBTPWIAZ\nArtist: TURNIQUE",
	"Music by: Bensound\nLicense code: YBABDKFYYZMYCBIF\nArtist: Benjamin Tissot",
	"Music: Bensound.com/royalty-free-music\nLicense code: GZGCSGJPOTTD5QOA\nArtist: Dreamt",
	"Music by https://www.bensound.com\nLicense code: FXE0HMJQCIWEMGOG\nArtist: Yunior Arronte",
]
## Freesound sounds, shown under SOUND after the music (assets/sounds/LICENSES.md has the full list).
const SOUND_CREDITS := [
	"\"urban_night_rain_1\" by nkroher\nfreesound.org/s/232198 · CC BY 4.0",
	"\"Footsteps ground\" by emilgasi\nfreesound.org/s/685287 · CC0",
]
const AMBIENCE := {"rain": ["res://assets/sounds/rain.wav", 0.0]}    ## id: [file, level in dB]
const VOICE_LINES := "res://assets/voice/lines.json"     ## id: {speaker, text, file, voice}
const SETTINGS := "user://settings.cfg"     ## the same file as Main.SETTINGS
const FADE := 2.5                           ## default crossfade, seconds
const SILENT_DB := -60.0

var track := ""                 ## the music track playing (or fading in), "" for none
var ambient := ""               ## the ambience playing, "" for none
var music_volume := 0.8         ## 0..1, linear, the Music bus
var effects_volume := 0.8       ## 0..1, linear, the SFX bus (footsteps and ambience)
var voice_volume := 0.8         ## 0..1, linear, the Voice bus
var _voice: AudioStreamPlayer
var unvoiced: Array[String] = []   ## lines asked for that have no clip, in order (tests/playthrough.gd)
var _voice_lines := {}          ## id: res:// path, from VOICE_LINES
var _music: Crossfader
var _ambience: Crossfader


class Crossfader:
	## Two players on one bus: the new sound fades in on one while the old one fades out on the other.
	var players: Array[AudioStreamPlayer] = []
	var active := 0
	var tweens: Array = [null, null]
	var owner: Node

	func _init(parent: Node, bus: String) -> void:
		owner = parent
		for i in 2:
			var p := AudioStreamPlayer.new()
			p.bus = bus
			p.volume_db = SILENT_DB
			parent.add_child(p)
			players.append(p)

	func play(stream: AudioStream, level_db: float, fade: float) -> void:
		## Fade out what's on (if anything), then fade `stream` in to `level_db`; a null stream just fades out.
		_fade(active, SILENT_DB, fade, true)
		if stream == null:
			return
		active = 1 - active
		var p := players[active]
		p.stream = stream
		p.volume_db = SILENT_DB
		p.play()
		_fade(active, level_db, fade, false)    # kills any fade-out still running on this player

	func _fade(i: int, to_db: float, time: float, stop_after: bool) -> void:
		## Fade player i in linear amplitude (so a crossfade doesn't dip), then stop it if asked.
		if tweens[i]:
			(tweens[i] as Tween).kill()
		var p := players[i]
		if not p.playing:
			return
		var from := db_to_linear(p.volume_db)
		var to := db_to_linear(to_db)
		var t := owner.create_tween()
		t.tween_method(func(a: float): p.volume_db = linear_to_db(maxf(a, 0.001)), from, to, maxf(time, 0.01))
		if stop_after:
			t.tween_callback(p.stop)
		tweens[i] = t


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	for bus in ["Music", "Voice", "SFX"]:
		if AudioServer.get_bus_index(bus) < 0:
			AudioServer.add_bus()
			var i := AudioServer.bus_count - 1
			AudioServer.set_bus_name(i, bus)
			AudioServer.set_bus_send(i, "Master")
	_music = Crossfader.new(self, "Music")
	_ambience = Crossfader.new(self, "SFX")
	_voice = AudioStreamPlayer.new()
	_voice.bus = "Voice"
	add_child(_voice)
	if FileAccess.file_exists(VOICE_LINES):
		var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(VOICE_LINES))
		if parsed is Dictionary:
			for id: String in parsed:
				_voice_lines[id] = String((parsed[id] as Dictionary).get("file", ""))
	var cfg := ConfigFile.new()
	cfg.load(SETTINGS)
	music_volume = _apply_volume("Music", float(cfg.get_value("audio", "music", music_volume)))
	effects_volume = _apply_volume("SFX", float(cfg.get_value("audio", "effects", effects_volume)))
	voice_volume = _apply_volume("Voice", float(cfg.get_value("audio", "voice", voice_volume)))


static func case_track(n: int) -> String:
	return String(CASE_TRACKS.get(clampi(n, 1, 5)))


static func track_path(id: String) -> String:
	return TRACK_PATH % id


func music(id: String, fade := FADE) -> void:
	## Crossfade to track `id` (one of CASE_TRACKS' values, e.g. "rainyday"); "" fades the music out.
	if id == track:
		return
	track = id
	var stream: AudioStreamMP3 = null
	if id != "":
		stream = load(track_path(id)) as AudioStreamMP3
		stream.loop = true
	_music.play(stream, 0.0, fade)


func stop_music(fade := FADE) -> void:
	music("", fade)


func ambience(id: String, fade := 1.5) -> void:
	## Crossfade to the background loop `id` (a key of AMBIENCE, e.g. "rain"); "" fades it out.
	if id == ambient:
		return
	ambient = id
	if id == "":
		_ambience.play(null, SILENT_DB, fade)
		return
	var a: Array = AMBIENCE[id]
	_ambience.play(load(String(a[0])), float(a[1]), fade)


static func line_id(speaker: String, text: String) -> String:
	## The clip id for a line: the first 12 hex digits of sha1("<speaker>|<text>") (as tools/tts/gen_voice.py).
	return ("%s|%s" % [speaker, text]).sha1_text().substr(0, 12)


func voice_clip(speaker: String, text: String) -> AudioStream:
	## The recorded clip for this exact line, or null (and the line goes on `unvoiced`, which the playthrough checks).
	var path: String = _voice_lines.get(line_id(speaker, text), "")
	if path != "" and ResourceLoader.exists(path):
		return load(path) as AudioStream
	if not unvoiced.has(text):
		unvoiced.append(text)
	return null


func speak(clip: AudioStream) -> void:
	## Play a spoken line on the Voice bus, cutting off the one before.
	_voice.stream = clip
	_voice.play()


func stop_voice() -> void:
	_voice.stop()


func set_voice_volume(v: float) -> void:
	## From the settings slider (0..1); remembered in user://settings.cfg.
	voice_volume = _apply_volume("Voice", v)
	_save("voice", voice_volume)


func set_music_volume(v: float) -> void:
	## From the settings slider (0..1); remembered in user://settings.cfg.
	music_volume = _apply_volume("Music", v)
	_save("music", music_volume)


func set_effects_volume(v: float) -> void:
	## From the settings slider (0..1); remembered in user://settings.cfg.
	effects_volume = _apply_volume("SFX", v)
	_save("effects", effects_volume)


func _save(key: String, v: float) -> void:
	var cfg := ConfigFile.new()
	cfg.load(SETTINGS)
	cfg.set_value("audio", key, v)
	cfg.save(SETTINGS)


func _apply_volume(bus_name: String, v: float) -> float:
	v = clampf(v, 0.0, 1.0)
	var bus := AudioServer.get_bus_index(bus_name)
	AudioServer.set_bus_volume_db(bus, linear_to_db(v) if v > 0.0 else SILENT_DB)
	AudioServer.set_bus_mute(bus, v <= 0.0)
	return v
