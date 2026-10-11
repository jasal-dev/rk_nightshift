class_name SettingsPanel
extends PanelContainer
## SETTINGS: fullscreen, text speed and music volume, then BACK. The title screen shows it in place of its menu,
## and the cog at the right end of the inventory bar opens it over a room (GameUI.open_settings, the game paused).
## Emits `fullscreen_pressed` and `text_speed_chosen`, which Main applies and remembers; the Music volume slider goes
## straight to the Audio autoload, which remembers it. BACK (or Esc, handled by whoever shows it) emits `closed`.
## Styled with the title screen's building blocks (TitleScreen.menu_button and the rest).

signal fullscreen_pressed
signal text_speed_chosen(index: int)
signal closed

const TEXT_SPEEDS := ["Slow", "Normal", "Fast", "Manual"]   ## Main.TEXT_TIME; Manual waits for a click

var music_slider: HSlider
var _fullscreen_button: Button
var _speed_buttons: Array[Button] = []
var _volume_label: Label


func _init(text_speed: int) -> void:
	TitleScreen.style_panel(self)
	custom_minimum_size = Vector2(980, 0)
	var vb := VBoxContainer.new()
	vb.add_theme_constant_override("separation", 14)
	add_child(vb)
	vb.add_child(TitleScreen.menu_label("SETTINGS", 34, TitleScreen.BRASS))

	var row := TitleScreen.menu_row(vb, "Fullscreen")
	_fullscreen_button = TitleScreen.menu_button("Off", 34)
	_fullscreen_button.custom_minimum_size = Vector2(130, 0)
	_fullscreen_button.pressed.connect(func(): fullscreen_pressed.emit())
	row.add_child(_fullscreen_button)

	row = TitleScreen.menu_row(vb, "Text speed")
	for i in TEXT_SPEEDS.size():
		var b := TitleScreen.menu_button(String(TEXT_SPEEDS[i]), 34)
		b.custom_minimum_size = Vector2(130, 0)
		b.pressed.connect(func():
			set_text_speed(i)
			text_speed_chosen.emit(i))
		_speed_buttons.append(b)
		row.add_child(b)
	set_text_speed(text_speed)

	row = TitleScreen.menu_row(vb, "Music volume")
	music_slider = TitleScreen.menu_slider()
	music_slider.value = roundf(Audio.music_volume * 100.0)
	row.add_child(music_slider)
	_volume_label = TitleScreen.menu_label("%d%%" % int(music_slider.value), 34, TitleScreen.AMBER)
	_volume_label.custom_minimum_size = Vector2(120, 0)
	_volume_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	row.add_child(_volume_label)
	music_slider.value_changed.connect(func(v: float):
		_volume_label.text = "%d%%" % int(v)
		Audio.set_music_volume(v / 100.0))

	var back := TitleScreen.menu_button("BACK", 38)
	back.pressed.connect(func(): closed.emit())
	vb.add_child(back)


func _process(_delta: float) -> void:
	if visible:
		_fullscreen_button.text = "On" if _is_fullscreen() else "Off"    # F11 works here too


func set_text_speed(index: int) -> void:
	for i in _speed_buttons.size():
		var on := i == index
		_speed_buttons[i].add_theme_color_override("font_color", TitleScreen.AMBER if on else TitleScreen.GREY)
		_speed_buttons[i].add_theme_color_override("font_hover_color", TitleScreen.AMBER if on else TitleScreen.CREAM)


func _is_fullscreen() -> bool:
	var mode := DisplayServer.window_get_mode()
	return mode == DisplayServer.WINDOW_MODE_FULLSCREEN or mode == DisplayServer.WINDOW_MODE_EXCLUSIVE_FULLSCREEN
