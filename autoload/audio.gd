extends Node
## Music (and, later, voice and effects). One track per case, looping, kept playing across room changes;
## `music()` crossfades to another track and does nothing when that track is already on.
## Main switches tracks on the title screen, at each case card and on every room change (new game, Skip to Case N,
## loading a save), so whatever path got Ray into a case, its track is playing.
## Buses: Master > Music, Voice, SFX (made here, so there's no bus layout file to keep in sync). Voice and SFX are
## empty until there is something to play on them. The Music volume is set on the title screen's settings panel and
## kept in user://settings.cfg with the other settings.

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
const SETTINGS := "user://settings.cfg"     ## the same file as Main.SETTINGS
const FADE := 2.5                           ## default crossfade, seconds
const SILENT_DB := -60.0

var track := ""                 ## the track playing (or fading in), "" for none
var music_volume := 0.8         ## 0..1, linear, the Music bus
var _players: Array[AudioStreamPlayer] = []
var _active := 0                ## index of the player with the current track
var _tweens: Array = [null, null]


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	for bus in ["Music", "Voice", "SFX"]:
		if AudioServer.get_bus_index(bus) < 0:
			AudioServer.add_bus()
			var i := AudioServer.bus_count - 1
			AudioServer.set_bus_name(i, bus)
			AudioServer.set_bus_send(i, "Master")
	for i in 2:
		var p := AudioStreamPlayer.new()
		p.bus = "Music"
		p.volume_db = SILENT_DB
		add_child(p)
		_players.append(p)
	var cfg := ConfigFile.new()
	cfg.load(SETTINGS)
	_apply_volume(clampf(float(cfg.get_value("audio", "music", music_volume)), 0.0, 1.0))


static func case_track(n: int) -> String:
	return String(CASE_TRACKS.get(clampi(n, 1, 5)))


static func track_path(id: String) -> String:
	return TRACK_PATH % id


func music(id: String, fade := FADE) -> void:
	## Crossfade to track `id` (a key of CASE_TRACKS' values, e.g. "rainyday"); "" fades the music out.
	if id == track:
		return
	track = id
	_fade(_active, SILENT_DB, fade, true)
	if id == "":
		return
	_active = 1 - _active
	var p := _players[_active]
	var stream := load(track_path(id)) as AudioStreamMP3
	stream.loop = true
	p.stream = stream
	p.volume_db = SILENT_DB
	p.play()
	_fade(_active, 0.0, fade, false)    # kills any fade-out still running on this player


func stop_music(fade := FADE) -> void:
	music("", fade)


func set_music_volume(v: float) -> void:
	## From the settings slider (0..1); remembered in user://settings.cfg.
	_apply_volume(clampf(v, 0.0, 1.0))
	var cfg := ConfigFile.new()
	cfg.load(SETTINGS)
	cfg.set_value("audio", "music", music_volume)
	cfg.save(SETTINGS)


func _apply_volume(v: float) -> void:
	music_volume = v
	var bus := AudioServer.get_bus_index("Music")
	AudioServer.set_bus_volume_db(bus, linear_to_db(v) if v > 0.0 else SILENT_DB)
	AudioServer.set_bus_mute(bus, v <= 0.0)


func _fade(i: int, to_db: float, time: float, stop_after: bool) -> void:
	## Fade player i in linear amplitude (so a crossfade doesn't dip), then stop it if asked.
	if _tweens[i]:
		(_tweens[i] as Tween).kill()
	var p := _players[i]
	if not p.playing:
		return
	var from := db_to_linear(p.volume_db)
	var to := db_to_linear(to_db)
	var t := create_tween()
	t.tween_method(func(a: float): p.volume_db = linear_to_db(maxf(a, 0.001)), from, to, maxf(time, 0.01))
	if stop_after:
		t.tween_callback(p.stop)
	_tweens[i] = t
