class_name TitleScreen
extends Control
## The title screen (GameUI.show_title): the street the morning Sal died, empty but for the tape and the patrol car's
## turning light bar, RAY KESSLER in neon over NIGHTSHIFT, and New Game, Load Game, Settings, Credits and Exit, with a
## row under them that skips to Case 2, 3, 4 or 5 (Main.jump_to_case).
## Emits `chosen` ("new", "load", "case2" to "case5", or "quit").
## Settings is a SettingsPanel (the same one the inventory bar's cog opens in a room); TitleScreen passes on its
## `fullscreen_pressed` and `text_speed_chosen`, and Main applies and remembers them. Credits shows the music attributions.
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
const CREAM := Color(0.85, 0.8, 0.7)
const AMBER := Color(1, 0.85, 0.45)
const BRASS := Color(0.55, 0.42, 0.28)
const GREY := Color(0.5, 0.48, 0.45)

var new_button: Button
var load_button: Button
var settings_button: Button
var credits_button: Button
var exit_button: Button
var case_buttons: Array[Button] = []    ## Case 2 to Case 5, in order
var menu: VBoxContainer
var settings: SettingsPanel
var credits: PanelContainer
var _help: Label
var _bar_red: TextureRect
var _bar_blue: TextureRect
var _logo: TextureRect
var _sub: TextureRect
var _tag: Label
static var _font: FontVariation
var _blink := 0.0
var _buzz_in := 2.0       ## seconds to the next buzz of the logo's failing tube


func _init(has_save: bool, text_speed: int) -> void:
	set_anchors_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP     # clicks off the buttons go nowhere

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
	_tag = menu_label("FIVE CASES.  ONE NIGHT.", 28, CREAM.darkened(0.15))
	_tag.position = Vector2(0, 392)
	_tag.size = Vector2(1920, 40)
	add_child(_tag)

	menu = VBoxContainer.new()
	menu.add_theme_constant_override("separation", 4)
	menu.position = Vector2(560, 530)
	menu.size = Vector2(800, 0)
	add_child(menu)
	new_button = menu_button("NEW GAME", 46)
	load_button = menu_button("LOAD GAME", 46)
	settings_button = menu_button("SETTINGS", 46)
	credits_button = menu_button("CREDITS", 46)
	exit_button = menu_button("EXIT", 46)
	load_button.disabled = not has_save
	new_button.pressed.connect(func(): chosen.emit("new"))
	load_button.pressed.connect(func(): chosen.emit("load"))
	settings_button.pressed.connect(open_settings)
	credits_button.pressed.connect(open_credits)
	exit_button.pressed.connect(func(): chosen.emit("quit"))
	for b in [new_button, load_button, settings_button, credits_button, exit_button]:
		menu.add_child(b)
	menu.add_child(_case_row())

	settings = SettingsPanel.new(text_speed)
	settings.position = Vector2(470, 500)
	settings.visible = false
	settings.fullscreen_pressed.connect(func(): fullscreen_pressed.emit())
	settings.text_speed_chosen.connect(func(i: int): text_speed_chosen.emit(i))
	settings.closed.connect(close_settings)
	add_child(settings)
	credits = _credits_panel()
	credits.visible = false
	add_child(credits)

	_help = menu_label("Left click to walk and use, right click to look.     F5 save    F9 load    Esc save and quit to title    F11 fullscreen", 22, GREY)
	_help.position = Vector2(0, 1020)
	_help.size = Vector2(1920, 30)
	add_child(_help)


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


func _unhandled_key_input(event: InputEvent) -> void:
	if event.is_pressed() and (event as InputEventKey).keycode == KEY_ESCAPE:
		if settings.visible:
			close_settings()
		elif credits.visible:
			close_credits()


func open_settings() -> void:
	menu.visible = false
	settings.visible = true


func close_settings() -> void:
	settings.visible = false
	menu.visible = true


func open_credits() -> void:
	menu.visible = false
	for c: CanvasItem in [_help, _sub, _tag]:     # the credits fill the screen under RAY KESSLER
		c.visible = false
	credits.visible = true


func close_credits() -> void:
	credits.visible = false
	for c: CanvasItem in [_help, _sub, _tag]:
		c.visible = true
	menu.visible = true


func is_hot(p: Vector2) -> bool:
	## True when `p` (screen pixels) is over a button that takes a click (for the hot cursor).
	return button_at(self, p)


static func button_at(under: Control, p: Vector2) -> bool:
	## True when `p` (screen pixels) is over a button under `under` that takes a click.
	for b in under.find_children("*", "Button", true, false):
		var btn := b as Button
		if btn.is_visible_in_tree() and not btn.disabled and btn.get_global_rect().has_point(p):
			return true
	return false


# --- building blocks (SettingsPanel uses them too) -----------------------------------
static func menu_font() -> FontVariation:
	## The menu face: the UI font, letter-spaced.
	if _font == null:
		_font = FontVariation.new()
		_font.base_font = GameUI.FONT
		_font.spacing_glyph = 5
	return _font


func _credits_panel() -> PanelContainer:
	## The music and sound attributions (Audio.MUSIC_CREDITS, Audio.SOUND_CREDITS), under the logo.
	var panel := PanelContainer.new()
	style_panel(panel)
	panel.position = Vector2(190, 262)
	panel.custom_minimum_size = Vector2(1540, 0)
	var vb := VBoxContainer.new()
	vb.add_theme_constant_override("separation", 14)
	panel.add_child(vb)
	vb.add_child(menu_label("CREDITS", 34, BRASS))
	vb.add_child(music_credits(GameUI.FONT, menu_font(), 27, CREAM, GREY))
	var back := menu_button("BACK", 38)
	back.pressed.connect(close_credits)
	vb.add_child(back)
	return panel


static func music_credits(font: Font, head_font: Font, font_size: int, col: Color, head_col: Color) -> VBoxContainer:
	## MUSIC over the five attributions, two to a row, and SOUND over the Freesound ones, three to a row (they're
	## short; a little smaller), each block as written (line breaks kept). Also the last of the end credits (GameUI.show_music_credits).
	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", 16)
	box.mouse_filter = Control.MOUSE_FILTER_IGNORE
	for section: Array in [["MUSIC", Audio.MUSIC_CREDITS, 2], ["SOUND", Audio.SOUND_CREDITS, 3]]:
		box.add_child(_text_label(String(section[0]), head_font, font_size, head_col))
		var blocks: Array = section[1]
		var per_row: int = section[2]
		var row: HBoxContainer = null
		for i in blocks.size():
			if i % per_row == 0:
				row = HBoxContainer.new()
				row.alignment = BoxContainer.ALIGNMENT_CENTER
				row.add_theme_constant_override("separation", 60)
				row.mouse_filter = Control.MOUSE_FILTER_IGNORE
				box.add_child(row)
			var l := _text_label(String(blocks[i]), font, font_size - (3 if per_row > 2 else 0), col)
			l.custom_minimum_size = Vector2(1240.0 / per_row, 0)
			row.add_child(l)
	return box


static func _text_label(text: String, font: Font, font_size: int, col: Color) -> Label:
	var l := Label.new()
	l.text = text
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	l.add_theme_font_override("font", font)
	l.add_theme_font_size_override("font_size", font_size)
	l.add_theme_color_override("font_color", col)
	l.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.9))
	l.add_theme_constant_override("outline_size", 6)
	l.add_theme_constant_override("line_spacing", 4)
	return l


func _case_row() -> VBoxContainer:
	## SKIP TO  CASE 2  CASE 3  CASE 4  CASE 5, smaller, a little below the main buttons.
	var box := VBoxContainer.new()
	var gap := Control.new()
	gap.custom_minimum_size = Vector2(0, 18)
	box.add_child(gap)
	var row := HBoxContainer.new()
	row.alignment = BoxContainer.ALIGNMENT_CENTER
	row.add_theme_constant_override("separation", 26)
	box.add_child(row)
	row.add_child(menu_label("SKIP TO", 26, GREY))
	for n in [2, 3, 4, 5]:
		var b := menu_button("CASE %d" % n, 30)
		b.pressed.connect(func(): chosen.emit("case%d" % n))
		case_buttons.append(b)
		row.add_child(b)
	return box


static func style_panel(panel: PanelContainer) -> void:
	## The menu's dark, brass-edged box.
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0.06, 0.05, 0.08, 0.92)
	sb.border_color = BRASS
	sb.set_border_width_all(2)
	sb.content_margin_left = 48
	sb.content_margin_right = 48
	sb.content_margin_top = 28
	sb.content_margin_bottom = 20
	panel.add_theme_stylebox_override("panel", sb)


static func menu_slider() -> HSlider:
	## 0 to 100 in steps of 5: a dim brass track, amber up to a cream knob.
	var s := HSlider.new()
	s.min_value = 0
	s.max_value = 100
	s.step = 5
	s.focus_mode = Control.FOCUS_NONE
	s.custom_minimum_size = Vector2(360, 40)
	s.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	var track := StyleBoxFlat.new()
	track.bg_color = Color(BRASS, 0.55)
	track.content_margin_top = 4
	track.content_margin_bottom = 4
	track.set_corner_radius_all(3)
	var fill := track.duplicate() as StyleBoxFlat
	fill.bg_color = AMBER.darkened(0.2)
	s.add_theme_stylebox_override("slider", track)
	s.add_theme_stylebox_override("grabber_area", fill)
	s.add_theme_stylebox_override("grabber_area_highlight", fill)
	var knob := Image.create(28, 28, false, Image.FORMAT_RGBA8)
	for y in 28:
		for x in 28:
			var d := Vector2(x - 13.5, y - 13.5).length()
			knob.set_pixel(x, y, Color(AMBER if d > 10.0 else CREAM, clampf(13.5 - d, 0.0, 1.0)))
	var tex := ImageTexture.create_from_image(knob)
	s.add_theme_icon_override("grabber", tex)
	s.add_theme_icon_override("grabber_highlight", tex)
	return s


static func menu_row(parent: Control, caption: String) -> HBoxContainer:
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 10)
	parent.add_child(row)
	var l := menu_label(caption, 34, CREAM)
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
	l.custom_minimum_size = Vector2(330, 0)
	row.add_child(l)
	return row


static func menu_button(text: String, font_size: int) -> Button:
	var b := Button.new()
	b.text = text
	b.flat = true
	b.focus_mode = Control.FOCUS_NONE
	b.mouse_filter = Control.MOUSE_FILTER_STOP
	b.add_theme_font_override("font", menu_font())
	b.add_theme_font_size_override("font_size", font_size)
	b.add_theme_color_override("font_color", CREAM)
	b.add_theme_color_override("font_hover_color", AMBER)
	b.add_theme_color_override("font_pressed_color", AMBER)
	b.add_theme_color_override("font_hover_pressed_color", AMBER)
	b.add_theme_color_override("font_disabled_color", Color(GREY, 0.45))
	b.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.9))
	b.add_theme_constant_override("outline_size", 8)
	return b


static func menu_label(text: String, font_size: int, col: Color) -> Label:
	var l := Label.new()
	l.text = text
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	l.add_theme_font_override("font", menu_font())
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

