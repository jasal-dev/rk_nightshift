class_name TitleScreen
extends Control
## The title screen (GameUI.show_title): the street the morning Sal died, empty but for the tape and the patrol car's
## turning light bar, RAY KESSLER in neon over NIGHTSHIFT, and New Game, Load Game, Settings and Exit.
## Emits `chosen` ("new", "load" or "quit").
## The settings panel emits `fullscreen_pressed` and `text_speed_chosen`; Main applies and remembers them.
## Art: tools/r3/title.py (the backdrop, via render_room.py) and tools/r3/gen_title.py (the logo).

signal chosen(action: String)
signal fullscreen_pressed
signal text_speed_chosen(index: int)

const BG := preload("res://assets/rooms/title.png")
const BAR_RED := preload("res://assets/rooms/title_bar_red.png")
const BAR_BLUE := preload("res://assets/rooms/title_bar_blue.png")
const BAR_RED_AT := Vector2(8, 0)       ## overlay offsets, from tools/r3/out/title.json
const BAR_BLUE_AT := Vector2(0, 0)
const LOGO := preload("res://assets/ui/title_logo.png")
const LOGO_DIM := preload("res://assets/ui/title_logo_dim.png")
const SUB := preload("res://assets/ui/title_sub.png")
const TEXT_SPEEDS := ["Slow", "Normal", "Fast", "Manual"]   ## Main.TEXT_TIME; Manual waits for a click
const CREAM := Color(0.85, 0.8, 0.7)
const AMBER := Color(1, 0.85, 0.45)
const BRASS := Color(0.55, 0.42, 0.28)
const GREY := Color(0.5, 0.48, 0.45)

var new_button: Button
var load_button: Button
var settings_button: Button
var exit_button: Button
var menu: VBoxContainer
var settings: PanelContainer
var _fullscreen_button: Button
var _speed_buttons: Array[Button] = []
var _bar_red: TextureRect
var _bar_blue: TextureRect
var _logo: TextureRect
var _sub: TextureRect
var _font: FontVariation
var _blink := 0.0
var _buzz_in := 2.0       ## seconds to the next buzz of the logo's failing tube


func _init(has_save: bool, text_speed: int) -> void:
	set_anchors_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP     # clicks off the buttons go nowhere
	_font = FontVariation.new()
	_font.base_font = GameUI.FONT
	_font.spacing_glyph = 5

	add_child(_rect(BG, Vector2.ZERO))
	_bar_red = _rect(BAR_RED, BAR_RED_AT)
	_bar_blue = _rect(BAR_BLUE, BAR_BLUE_AT)
	add_child(_bar_red)
	add_child(_bar_blue)
	add_child(_rain())
	var dim := ColorRect.new()
	dim.color = Color(0, 0, 0, 0.3)
	dim.set_anchors_preset(Control.PRESET_FULL_RECT)
	dim.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(dim)
	# darker at the top, behind the logo, and in a pool behind the menu
	var top := _rect(_gradient(Color(0, 0, 0, 0.6), Color(0, 0, 0, 0), false), Vector2.ZERO)
	top.size = Vector2(1920, 520)
	add_child(top)
	var pool := _rect(_gradient(Color(0, 0, 0, 0.72), Color(0, 0, 0, 0), true), Vector2(380, 380))
	pool.size = Vector2(1160, 640)
	add_child(pool)

	var add := CanvasItemMaterial.new()
	add.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	_logo = _rect(LOGO, Vector2((1920 - LOGO.get_width()) / 2.0, 6))
	_logo.material = add
	_logo.modulate.a = 0.0
	add_child(_logo)
	_sub = _rect(SUB, Vector2((1920 - SUB.get_width()) / 2.0, 246))
	_sub.material = add
	_sub.modulate.a = 0.0
	add_child(_sub)
	var tag := _label("FIVE CASES.  ONE NIGHT.", 28, CREAM.darkened(0.15))
	tag.position = Vector2(0, 392)
	tag.size = Vector2(1920, 40)
	add_child(tag)

	menu = VBoxContainer.new()
	menu.add_theme_constant_override("separation", 4)
	menu.position = Vector2(660, 530)
	menu.size = Vector2(600, 0)
	add_child(menu)
	new_button = _button("NEW GAME", 46)
	load_button = _button("LOAD GAME", 46)
	settings_button = _button("SETTINGS", 46)
	exit_button = _button("EXIT", 46)
	load_button.disabled = not has_save
	new_button.pressed.connect(func(): chosen.emit("new"))
	load_button.pressed.connect(func(): chosen.emit("load"))
	settings_button.pressed.connect(open_settings)
	exit_button.pressed.connect(func(): chosen.emit("quit"))
	for b in [new_button, load_button, settings_button, exit_button]:
		menu.add_child(b)

	settings = _settings_panel(text_speed)
	settings.visible = false
	add_child(settings)

	var help := _label("Left click to walk and use, right click to look.     F5 save    F9 load    Esc save and quit to title    F11 fullscreen", 22, GREY)
	help.position = Vector2(0, 1020)
	help.size = Vector2(1920, 30)
	add_child(help)


func _ready() -> void:
	# the signs light: a stutter, then on, the blue one a beat later
	var t := create_tween()
	for a in [0.5, 0.0, 0.8, 0.15, 1.0]:
		t.tween_property(_logo, "modulate:a", a, 0.06)
		t.tween_interval(0.08)
	t.tween_interval(0.25)
	for a in [0.7, 0.1, 1.0]:
		t.tween_property(_sub, "modulate:a", a, 0.05)
		t.tween_interval(0.07)


func _process(delta: float) -> void:
	# the light bar turning, as on the street_crime room: red, blue, with a beat of dark
	_blink += delta
	var phase := fmod(_blink, 1.2)
	_bar_red.visible = phase < 0.35
	_bar_blue.visible = phase >= 0.6 and phase < 0.95
	_buzz_in -= delta
	if _buzz_in < 0.0:
		_buzz_in = randf_range(2.5, 7.0)
		var t := create_tween()
		for i in randi_range(2, 4):
			t.tween_callback(func(): _logo.texture = LOGO_DIM)
			t.tween_interval(randf_range(0.03, 0.09))
			t.tween_callback(func(): _logo.texture = LOGO)
			t.tween_interval(randf_range(0.04, 0.16))
	if settings.visible:
		_fullscreen_button.text = "On" if _is_fullscreen() else "Off"    # F11 works here too


func _unhandled_key_input(event: InputEvent) -> void:
	if settings.visible and event.is_pressed() and (event as InputEventKey).keycode == KEY_ESCAPE:
		close_settings()


func open_settings() -> void:
	menu.visible = false
	settings.visible = true


func close_settings() -> void:
	settings.visible = false
	menu.visible = true


func is_hot(p: Vector2) -> bool:
	## True when `p` (screen pixels) is over a button that takes a click (for the hot cursor).
	for b in find_children("*", "Button", true, false):
		var btn := b as Button
		if btn.is_visible_in_tree() and not btn.disabled and btn.get_global_rect().has_point(p):
			return true
	return false


func set_text_speed(index: int) -> void:
	for i in _speed_buttons.size():
		var on := i == index
		_speed_buttons[i].add_theme_color_override("font_color", AMBER if on else GREY)
		_speed_buttons[i].add_theme_color_override("font_hover_color", AMBER if on else CREAM)


# --- building blocks ------------------------------------------------------------
func _settings_panel(text_speed: int) -> PanelContainer:
	var panel := PanelContainer.new()
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0.06, 0.05, 0.08, 0.92)
	sb.border_color = BRASS
	sb.set_border_width_all(2)
	sb.content_margin_left = 48
	sb.content_margin_right = 48
	sb.content_margin_top = 28
	sb.content_margin_bottom = 20
	panel.add_theme_stylebox_override("panel", sb)
	panel.position = Vector2(470, 500)
	panel.custom_minimum_size = Vector2(980, 0)
	var vb := VBoxContainer.new()
	vb.add_theme_constant_override("separation", 14)
	panel.add_child(vb)
	var head := _label("SETTINGS", 34, BRASS)
	vb.add_child(head)

	var row := _row(vb, "Fullscreen")
	_fullscreen_button = _button("Off", 34)
	_fullscreen_button.custom_minimum_size = Vector2(130, 0)
	_fullscreen_button.pressed.connect(func(): fullscreen_pressed.emit())
	row.add_child(_fullscreen_button)

	row = _row(vb, "Text speed")
	for i in TEXT_SPEEDS.size():
		var b := _button(String(TEXT_SPEEDS[i]), 34)
		b.custom_minimum_size = Vector2(130, 0)
		b.pressed.connect(func():
			set_text_speed(i)
			text_speed_chosen.emit(i))
		_speed_buttons.append(b)
		row.add_child(b)
	set_text_speed(text_speed)

	var back := _button("BACK", 38)
	back.pressed.connect(close_settings)
	vb.add_child(back)
	return panel


func _row(parent: Control, caption: String) -> HBoxContainer:
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 10)
	parent.add_child(row)
	var l := _label(caption, 34, CREAM)
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
	l.custom_minimum_size = Vector2(260, 0)
	row.add_child(l)
	return row


func _button(text: String, font_size: int) -> Button:
	var b := Button.new()
	b.text = text
	b.flat = true
	b.focus_mode = Control.FOCUS_NONE
	b.mouse_filter = Control.MOUSE_FILTER_STOP
	b.add_theme_font_override("font", _font)
	b.add_theme_font_size_override("font_size", font_size)
	b.add_theme_color_override("font_color", CREAM)
	b.add_theme_color_override("font_hover_color", AMBER)
	b.add_theme_color_override("font_pressed_color", AMBER)
	b.add_theme_color_override("font_hover_pressed_color", AMBER)
	b.add_theme_color_override("font_disabled_color", Color(GREY, 0.45))
	b.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.9))
	b.add_theme_constant_override("outline_size", 8)
	return b


func _label(text: String, font_size: int, col: Color) -> Label:
	var l := Label.new()
	l.text = text
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	l.add_theme_font_override("font", _font)
	l.add_theme_font_size_override("font_size", font_size)
	l.add_theme_color_override("font_color", col)
	l.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.9))
	l.add_theme_constant_override("outline_size", 6)
	return l


func _rect(tex: Texture2D, at: Vector2) -> TextureRect:
	var r := TextureRect.new()
	r.texture = tex
	r.position = at
	r.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	r.size = tex.get_size()
	r.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return r


func _gradient(from: Color, to: Color, radial: bool) -> Texture2D:
	var g := Gradient.new()
	g.set_color(0, from)
	g.set_color(1, to)
	var t := GradientTexture2D.new()
	t.gradient = g
	t.width = 128
	t.height = 128
	if radial:
		t.fill = GradientTexture2D.FILL_RADIAL
		t.fill_from = Vector2(0.5, 0.5)
		t.fill_to = Vector2(1.0, 0.5)
	else:
		t.fill_from = Vector2(0, 0)
		t.fill_to = Vector2(0, 1)
	return t


func _rain() -> CPUParticles2D:
	## The same rain as the outdoor rooms (Room.add_rain), lighter.
	var rain := CPUParticles2D.new()
	rain.texture = preload("res://assets/rooms/raindrop.png")
	rain.amount = 160
	rain.lifetime = 0.9
	rain.preprocess = 1.0
	rain.position = Vector2(985, -40)
	rain.emission_shape = CPUParticles2D.EMISSION_SHAPE_RECTANGLE
	rain.emission_rect_extents = Vector2(1170, 12)
	rain.direction = Vector2(-0.05, 1)
	rain.spread = 2.0
	rain.gravity = Vector2.ZERO
	rain.initial_velocity_min = 1250.0
	rain.initial_velocity_max = 1500.0
	rain.scale_amount_min = 0.7
	rain.scale_amount_max = 1.2
	return rain


func _is_fullscreen() -> bool:
	var mode := DisplayServer.window_get_mode()
	return mode == DisplayServer.WINDOW_MODE_FULLSCREEN or mode == DisplayServer.WINDOW_MODE_EXCLUSIVE_FULLSCREEN
