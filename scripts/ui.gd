class_name GameUI
extends CanvasLayer
## All on-screen UI, built in code so it is easy to read and change:
## hover label, speech text, inventory bar, dialogue choices, fades,
## title/end cards and the in-viewport cursor.

signal skip_requested
signal choice_made(index: int)
signal inventory_clicked(id: String, button: int)

const FONT := preload("res://assets/fonts/DejaVuSansCondensed-Bold.ttf")
const FONT_SIZE := 30
const CURSOR := preload("res://assets/ui/cursor.png")
const CURSOR_HOT := preload("res://assets/ui/cursor_hot.png")
const SCREEN := Vector2(1920, 1080)
const BAR_H := 104
const ICON := 84

var theme_res: Theme
var hover_label: Label
var speech_label: Label
var toast_label: Label
var bar: PanelContainer
var bar_items: HBoxContainer
var choices_box: VBoxContainer
var fade_rect: ColorRect
var card: Control
var cursor: TextureRect
var cursor_item: TextureRect
var bar_pinned := false
var root: Control
var board: Control                ## murder board close-up (deduction)
var drive: Control                ## rain-on-windshield transition
var phone: PanelContainer         ## text messages
var phone_log: VBoxContainer
var _drive_lights: Array[Sprite2D] = []
var _drive_drops: Array[Sprite2D] = []
var _wiper: Line2D
var _wiper_t := 0.0
var _glow: Texture2D



func _ready() -> void:
	layer = 10
	theme_res = Theme.new()
	theme_res.default_font = FONT
	theme_res.default_font_size = FONT_SIZE
	root = Control.new()
	root.set_anchors_preset(Control.PRESET_FULL_RECT)
	root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.theme = theme_res
	add_child(root)

	hover_label = _make_label(Color(0.95, 0.92, 0.8))
	root.add_child(hover_label)

	speech_label = _make_label(Color(1, 1, 1))
	speech_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	speech_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	speech_label.visible = false
	root.add_child(speech_label)

	toast_label = _make_label(Color(0.9, 0.85, 0.6))
	toast_label.position = Vector2(24, 1020)
	root.add_child(toast_label)

	# inventory bar (slides in when the mouse touches the top edge)
	bar = PanelContainer.new()
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0.06, 0.05, 0.08, 0.92)
	sb.border_color = Color(0.55, 0.42, 0.28)
	sb.border_width_bottom = 2
	sb.content_margin_left = 24
	sb.content_margin_top = 9
	sb.content_margin_bottom = 9
	bar.add_theme_stylebox_override("panel", sb)
	bar.position = Vector2(0, -BAR_H)
	bar.size = Vector2(SCREEN.x, BAR_H)
	bar.mouse_filter = Control.MOUSE_FILTER_STOP
	root.add_child(bar)
	var hb := HBoxContainer.new()
	bar.add_child(hb)
	var title := Label.new()
	title.text = "INVENTORY "
	title.add_theme_color_override("font_color", Color(0.55, 0.42, 0.28))
	title.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	hb.add_child(title)
	bar_items = HBoxContainer.new()
	bar_items.add_theme_constant_override("separation", 14)
	hb.add_child(bar_items)

	choices_box = VBoxContainer.new()
	choices_box.position = Vector2(48, 780)
	choices_box.size = Vector2(1824, 270)
	choices_box.alignment = BoxContainer.ALIGNMENT_END
	choices_box.visible = false
	root.add_child(choices_box)

	fade_rect = ColorRect.new()
	fade_rect.color = Color.BLACK
	fade_rect.set_anchors_preset(Control.PRESET_FULL_RECT)
	fade_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.add_child(fade_rect)

	card = Control.new()
	card.set_anchors_preset(Control.PRESET_FULL_RECT)
	card.mouse_filter = Control.MOUSE_FILTER_IGNORE
	card.visible = false
	root.add_child(card)

	cursor_item = TextureRect.new()
	cursor_item.mouse_filter = Control.MOUSE_FILTER_IGNORE
	cursor_item.visible = false
	root.add_child(cursor_item)
	cursor = TextureRect.new()
	cursor.texture = CURSOR
	cursor.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.add_child(cursor)

	Game.inventory_changed.connect(refresh_inventory)
	Game.item_selected.connect(_on_item_selected)
	refresh_inventory()


func _make_label(col: Color) -> Label:
	var l := Label.new()
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	l.add_theme_color_override("font_color", col)
	l.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.92))
	l.add_theme_constant_override("outline_size", 8)
	l.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.6))
	l.add_theme_constant_override("shadow_offset_x", 3)
	l.add_theme_constant_override("shadow_offset_y", 3)
	return l


# --- per-frame ------------------------------------------------------------
func update_cursor(p: Vector2, hot: bool) -> void:
	cursor.position = p - Vector2(24, 24)
	cursor.texture = CURSOR_HOT if hot else CURSOR
	cursor_item.position = p + Vector2(12, 12)


func set_hover(text: String, p: Vector2) -> void:
	hover_label.text = text
	if text == "":
		return
	var w := FONT.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, FONT_SIZE).x
	hover_label.position = Vector2(clampf(p.x - w * 0.5, 12, SCREEN.x - 12 - w), clampf(p.y - 72, BAR_H + 6, SCREEN.y - 60))


func update_bar(mouse: Vector2, allowed: bool) -> void:
	var want := allowed and (bar_pinned or mouse.y < 24 or (bar.position.y > -BAR_H + 1 and mouse.y < BAR_H + 18))
	var target := 0.0 if want else -float(BAR_H)
	bar.position.y = move_toward(bar.position.y, target, 18.0)


func is_over_bar(p: Vector2) -> bool:
	return bar.position.y > -BAR_H + 1 and p.y < bar.position.y + BAR_H


func refresh_inventory() -> void:
	for c in bar_items.get_children():
		c.queue_free()
	for id in Game.inventory:
		var slot := TextureRect.new()
		slot.texture = Game.item_icon(id)
		slot.custom_minimum_size = Vector2(ICON, ICON)
		slot.stretch_mode = TextureRect.STRETCH_KEEP_CENTERED
		slot.tooltip_text = ""
		slot.set_meta("item", id)
		slot.mouse_filter = Control.MOUSE_FILTER_STOP
		slot.gui_input.connect(_on_slot_input.bind(id))
		slot.mouse_entered.connect(func(): slot.modulate = Color(1.3, 1.2, 0.9))
		slot.mouse_exited.connect(func(): slot.modulate = Color.WHITE)
		bar_items.add_child(slot)


func item_under(p: Vector2) -> String:
	if not is_over_bar(p):
		return ""
	for slot in bar_items.get_children():
		if slot is Control and (slot as Control).get_global_rect().has_point(p):
			return String(slot.get_meta("item", ""))
	return ""


func _on_slot_input(event: InputEvent, id: String) -> void:
	var mb := event as InputEventMouseButton
	if mb and mb.pressed:
		inventory_clicked.emit(id, mb.button_index)
		get_viewport().set_input_as_handled()


func _on_item_selected(id: String) -> void:
	cursor_item.visible = id != ""
	if id != "":
		cursor_item.texture = Game.item_icon(id)


# --- speech -----------------------------------------------------------------
func show_speech(text: String, anchor: Vector2, col: Color) -> void:
	var width := 780.0
	var sz := FONT.get_multiline_string_size(text, HORIZONTAL_ALIGNMENT_CENTER, width, FONT_SIZE)
	speech_label.text = text
	speech_label.add_theme_color_override("font_color", col)
	speech_label.size = Vector2(width, sz.y)
	var pos := anchor - Vector2(width * 0.5, sz.y + 12)
	pos.x = clampf(pos.x, 18, SCREEN.x - width - 18)
	pos.y = clampf(pos.y, 18, SCREEN.y - 90 - sz.y)
	speech_label.position = pos
	speech_label.visible = true


func hide_speech() -> void:
	speech_label.visible = false


func toast(text: String, hold := 1.6) -> void:
	toast_label.text = text
	toast_label.modulate.a = 1.0
	var t := create_tween()
	t.tween_interval(hold)
	t.tween_property(toast_label, "modulate:a", 0.0, 0.6)


# --- dialogue choices -------------------------------------------------------
func show_choices(options: Array) -> void:
	for c in choices_box.get_children():
		c.queue_free()
	for i in options.size():
		var b := Button.new()
		b.text = "%d. %s" % [i + 1, options[i]]
		b.flat = true
		b.alignment = HORIZONTAL_ALIGNMENT_LEFT
		b.focus_mode = Control.FOCUS_NONE
		b.add_theme_color_override("font_color", Color(0.75, 0.68, 0.55))
		b.add_theme_color_override("font_hover_color", Color(1, 0.85, 0.45))
		b.add_theme_color_override("font_pressed_color", Color(1, 0.85, 0.45))
		b.mouse_filter = Control.MOUSE_FILTER_STOP
		b.pressed.connect(func(): choice_made.emit(i))
		choices_box.add_child(b)
	# grow upwards from the bottom of the screen when there are many options
	choices_box.size = Vector2(1824, 46.0 * options.size())
	choices_box.position = Vector2(48, 1050 - choices_box.size.y)
	choices_box.visible = true


func hide_choices() -> void:
	choices_box.visible = false


# --- fades and cards --------------------------------------------------------
func fade_to(alpha: float, time := 0.5) -> void:
	var t := create_tween()
	t.tween_property(fade_rect, "color:a", alpha, time)
	await t.finished


func show_card(lines: Array, colors: Array = []) -> void:
	for c in card.get_children():
		c.queue_free()
	var vb := VBoxContainer.new()
	vb.alignment = BoxContainer.ALIGNMENT_CENTER
	vb.set_anchors_preset(Control.PRESET_FULL_RECT)
	vb.add_theme_constant_override("separation", 16)
	card.add_child(vb)
	for i in lines.size():
		var l := _make_label(colors[i] if i < colors.size() else Color(0.85, 0.8, 0.7))
		l.text = lines[i]
		l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		vb.add_child(l)
	card.visible = true


func hide_card() -> void:
	card.visible = false


# --- murder board (deduction) ---------------------------------------------------
## A close-up of the board: Danny's photo in the middle, the question above it and up to two
## evidence cards pinned either side with red string. Choices and speech are drawn on top.
func show_board(question: String) -> void:
	hide_board()
	board = Control.new()
	board.set_anchors_preset(Control.PRESET_FULL_RECT)
	board.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.add_child(board)
	root.move_child(board, 0)
	var dim := ColorRect.new()
	dim.color = Color(0, 0, 0, 0.6)
	dim.set_anchors_preset(Control.PRESET_FULL_RECT)
	dim.mouse_filter = Control.MOUSE_FILTER_IGNORE
	board.add_child(dim)
	board.add_child(_card_panel(Rect2(150, 40, 1620, 580), Color(0.42, 0.31, 0.2), Color(0.25, 0.17, 0.1), 6))
	var q := _make_label(Color(1, 0.88, 0.55))
	q.name = "Question"
	q.text = question
	q.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	q.position = Vector2(150, 62)
	q.size = Vector2(1620, 40)
	board.add_child(q)
	var strings := Node2D.new()
	strings.name = "Strings"
	board.add_child(strings)
	var photo := _card_panel(Rect2(830, 140, 260, 330), Color(0.88, 0.86, 0.8), Color(0.3, 0.28, 0.25), 2)
	board.add_child(photo)
	var face := ColorRect.new()
	face.color = Color(0.32, 0.3, 0.3)
	face.position = Vector2(20, 18)
	face.size = Vector2(220, 220)
	face.mouse_filter = Control.MOUSE_FILTER_IGNORE
	photo.add_child(face)
	var head := TextureRect.new()
	head.texture = _glow_tex()
	head.modulate = Color(0.75, 0.62, 0.52, 0.9)
	head.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	head.position = Vector2(60, 40)
	head.size = Vector2(100, 120)
	face.add_child(head)
	var cap := Label.new()
	cap.text = "DANNY REYES\n34. Piano, Blue Note"
	cap.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	cap.add_theme_color_override("font_color", Color(0.15, 0.15, 0.25))
	cap.add_theme_font_size_override("font_size", 24)
	cap.position = Vector2(0, 248)
	cap.size = Vector2(260, 70)
	photo.add_child(cap)
	_pin(board, Vector2(960, 150))
	set_board_pins([])


func set_board_question(question: String) -> void:
	if board:
		(board.get_node("Question") as Label).text = question


func set_board_pins(pins: Array) -> void:
	## pins: up to two card texts ("" = empty slot, shown as a question mark).
	if board == null:
		return
	for c in board.get_children():
		if c.has_meta("slot"):
			c.queue_free()
	var strings := board.get_node("Strings") as Node2D
	for c in strings.get_children():
		c.queue_free()
	var rects := [Rect2(250, 250, 460, 190), Rect2(1210, 250, 460, 190)]
	for i in 2:
		var r: Rect2 = rects[i]
		var filled := i < pins.size() and String(pins[i]) != ""
		var card := _card_panel(r, Color(0.95, 0.93, 0.84) if filled else Color(0.3, 0.22, 0.15, 0.6),
				Color(0.4, 0.36, 0.3) if filled else Color(0.7, 0.6, 0.45, 0.6), 2)
		card.set_meta("slot", i)
		var l := Label.new()
		l.text = String(pins[i]) if filled else "?"
		l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		l.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
		l.add_theme_color_override("font_color", Color(0.12, 0.12, 0.2) if filled else Color(0.85, 0.75, 0.55))
		l.add_theme_font_size_override("font_size", 30 if filled else 64)
		l.position = Vector2(16, 10)
		l.size = r.size - Vector2(32, 20)
		card.add_child(l)
		board.add_child(card)
		if filled:
			_pin(card, Vector2(r.size.x * 0.5, 8))
			var line := Line2D.new()
			line.width = 4
			line.default_color = Color(0.8, 0.1, 0.1)
			line.points = PackedVector2Array([Vector2(960, 150), r.position + Vector2(r.size.x * 0.5, 8)])
			strings.add_child(line)


func hide_board() -> void:
	if board:
		board.queue_free()
		board = null


func _card_panel(r: Rect2, bg: Color, border: Color, bw: int) -> Panel:
	var p := Panel.new()
	var sb := StyleBoxFlat.new()
	sb.bg_color = bg
	sb.border_color = border
	sb.set_border_width_all(bw)
	sb.shadow_color = Color(0, 0, 0, 0.45)
	sb.shadow_size = 8
	sb.shadow_offset = Vector2(4, 6)
	p.add_theme_stylebox_override("panel", sb)
	p.position = r.position
	p.size = r.size
	p.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return p


func _pin(parent: Control, at: Vector2) -> void:
	var pin := TextureRect.new()
	pin.texture = _glow_tex()
	pin.modulate = Color(0.9, 0.15, 0.12)
	pin.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	pin.size = Vector2(22, 22)
	pin.position = at - Vector2(11, 11)
	pin.mouse_filter = Control.MOUSE_FILTER_IGNORE
	parent.add_child(pin)


func _glow_tex() -> Texture2D:
	## Soft round blob used for pins, lights and raindrops.
	if _glow == null:
		var g := Gradient.new()
		g.set_color(0, Color(1, 1, 1, 1))
		g.set_color(1, Color(1, 1, 1, 0))
		g.add_point(0.5, Color(1, 1, 1, 0.8))
		var t := GradientTexture2D.new()
		t.gradient = g
		t.fill = GradientTexture2D.FILL_RADIAL
		t.fill_from = Vector2(0.5, 0.5)
		t.fill_to = Vector2(1.0, 0.5)
		t.width = 64
		t.height = 64
		_glow = t
	return _glow


# --- the drive (transition between locations) -------------------------------------
## Night freeway seen through a rainy windshield: lamps and tail lights sliding past,
## drops on the glass and a wiper. Lines are spoken over it with Main.narrate().
func show_drive() -> void:
	hide_drive()
	drive = Control.new()
	drive.set_anchors_preset(Control.PRESET_FULL_RECT)
	drive.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.add_child(drive)
	root.move_child(drive, 0)
	var sky := TextureRect.new()
	var g := Gradient.new()
	g.set_color(0, Color(0.05, 0.04, 0.09))
	g.set_color(1, Color(0.02, 0.02, 0.03))
	g.add_point(0.43, Color(0.22, 0.12, 0.1))
	g.add_point(0.47, Color(0.06, 0.05, 0.07))
	var gt := GradientTexture2D.new()
	gt.gradient = g
	gt.fill_from = Vector2(0, 0)
	gt.fill_to = Vector2(0, 1)
	gt.width = 16
	gt.height = 256
	sky.texture = gt
	sky.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	sky.set_anchors_preset(Control.PRESET_FULL_RECT)
	sky.mouse_filter = Control.MOUSE_FILTER_IGNORE
	drive.add_child(sky)
	# road edges converging on the vanishing point
	for side in [-1, 1]:
		var edge := Line2D.new()
		edge.width = 3
		edge.default_color = Color(0.5, 0.45, 0.4, 0.35)
		edge.points = PackedVector2Array([Vector2(960 + side * 40, 470), Vector2(960 + side * 1300, 1080)])
		drive.add_child(edge)
	_drive_lights.clear()
	for i in 34:
		var s := Sprite2D.new()
		s.texture = _glow_tex()
		s.material = _additive()
		drive.add_child(s)
		_drive_lights.append(s)
		_reset_light(s, randf())
	_drive_drops.clear()
	for i in 60:
		var d := Sprite2D.new()
		d.texture = _glow_tex()
		d.modulate = Color(0.75, 0.8, 0.95, randf_range(0.15, 0.4))
		d.scale = Vector2.ONE * randf_range(0.12, 0.4)
		d.position = Vector2(randf_range(0, 1920), randf_range(0, 900))
		drive.add_child(d)
		_drive_drops.append(d)
	# dashboard and wheel
	var dash := Polygon2D.new()
	dash.color = Color(0.03, 0.03, 0.035)
	dash.polygon = PackedVector2Array([Vector2(0, 880), Vector2(700, 840), Vector2(1300, 845), Vector2(1920, 900),
			Vector2(1920, 1080), Vector2(0, 1080)])
	drive.add_child(dash)
	var wheel := Line2D.new()
	wheel.width = 34
	wheel.default_color = Color(0.06, 0.06, 0.065)
	var pts := PackedVector2Array()
	for k in 33:
		var a := PI + PI * k / 32.0
		pts.append(Vector2(560, 1120) + Vector2(cos(a), sin(a)) * 330)
	wheel.points = pts
	drive.add_child(wheel)
	var glow := Sprite2D.new()
	glow.texture = _glow_tex()
	glow.material = _additive()
	glow.modulate = Color(0.25, 0.5, 0.9, 0.5)
	glow.position = Vector2(560, 905)
	glow.scale = Vector2(2.4, 0.5)
	drive.add_child(glow)
	_wiper = Line2D.new()
	_wiper.width = 12
	_wiper.default_color = Color(0.02, 0.02, 0.02)
	_wiper.points = PackedVector2Array([Vector2.ZERO, Vector2(0, -980)])
	_wiper.position = Vector2(1250, 1000)
	drive.add_child(_wiper)
	_wiper_t = 0.0


func hide_drive() -> void:
	hide_phone()
	if drive:
		drive.queue_free()
		drive = null
	_drive_lights.clear()
	_drive_drops.clear()


func _additive() -> CanvasItemMaterial:
	var m := CanvasItemMaterial.new()
	m.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	return m


func _reset_light(s: Sprite2D, t: float) -> void:
	## Lights travel outward from the vanishing point; t (0..1) is how far along they start.
	var kind := randi() % 3
	s.set_meta("kind", kind)
	s.set_meta("t", t)
	s.set_meta("speed", randf_range(0.18, 0.3) if kind == 0 else randf_range(0.03, 0.08))
	s.set_meta("lane", randf_range(-1.0, 1.0))
	match kind:
		0: s.modulate = Color(1.0, 0.6, 0.25, 0.9)        # sodium lamps overhead
		1: s.modulate = Color(1.0, 0.12, 0.08, 0.85)      # tail lights ahead
		_: s.modulate = Color(0.85, 0.9, 1.0, 0.75)       # oncoming headlights


func _process(delta: float) -> void:
	if drive == null:
		return
	var vp := Vector2(960, 470)
	for s in _drive_lights:
		var t: float = float(s.get_meta("t")) + delta * float(s.get_meta("speed"))
		if t > 1.0:
			_reset_light(s, 0.0)
			t = 0.0
		s.set_meta("t", t)
		var k: int = s.get_meta("kind")
		var e := t * t * t
		var lane: float = s.get_meta("lane")
		var p: Vector2
		match k:
			0: p = vp + Vector2(lane * 30 + signf(lane) * 1500 * e, -560 * e)
			1: p = vp + Vector2(lane * 18 + 200 * e * lane, 40 * e + 4)
			_: p = vp + Vector2(-60 - 1200 * e, 260 * e)
		s.position = p
		s.scale = Vector2.ONE * (0.15 + 3.2 * e) * (0.6 if k == 1 else 1.0)
	# wiper: one sweep every 2.6 s, clearing the drops it passes
	_wiper_t += delta
	var phase := fmod(_wiper_t, 2.6) / 1.1
	var ang := -1.15 + 2.1 * sin(clampf(phase, 0.0, 1.0) * PI)
	_wiper.rotation = ang
	for d in _drive_drops:
		d.position.y += delta * randf_range(2, 14)
		var rel := d.position - _wiper.position
		if phase < 1.0 and absf(wrapf(rel.angle() + PI / 2 - ang, -PI, PI)) < 0.06 and rel.length() < 980:
			d.position = Vector2(randf_range(0, 1920), randf_range(0, 860))
	if randf() < delta * 8.0 and not _drive_drops.is_empty():
		var d: Sprite2D = _drive_drops.pick_random()
		d.position = Vector2(randf_range(0, 1920), randf_range(0, 860))


# --- text messages on Ray's phone ---------------------------------------------------
func show_phone_text(text: String, outgoing: bool, contact := "") -> void:
	if phone == null:
		phone = PanelContainer.new()
		var sb := StyleBoxFlat.new()
		sb.bg_color = Color(0.05, 0.05, 0.07, 0.96)
		sb.border_color = Color(0.25, 0.25, 0.3)
		sb.set_border_width_all(4)
		sb.set_corner_radius_all(28)
		sb.content_margin_left = 22
		sb.content_margin_right = 22
		sb.content_margin_top = 26
		sb.content_margin_bottom = 26
		phone.add_theme_stylebox_override("panel", sb)
		phone.position = Vector2(1420, 300)
		phone.custom_minimum_size = Vector2(420, 480)
		phone.mouse_filter = Control.MOUSE_FILTER_IGNORE
		root.add_child(phone)
		root.move_child(phone, 1 if drive else 0)
		phone_log = VBoxContainer.new()
		phone_log.add_theme_constant_override("separation", 14)
		phone_log.alignment = BoxContainer.ALIGNMENT_END
		phone.add_child(phone_log)
		var head := Label.new()
		head.text = contact if contact != "" else "Messages"
		head.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		head.add_theme_color_override("font_color", Color(0.7, 0.7, 0.75))
		head.add_theme_font_size_override("font_size", 24)
		phone_log.add_child(head)
	var bubble := PanelContainer.new()
	var bs := StyleBoxFlat.new()
	bs.bg_color = Color(0.2, 0.45, 0.95) if outgoing else Color(0.22, 0.22, 0.25)
	bs.set_corner_radius_all(18)
	bs.content_margin_left = 16
	bs.content_margin_right = 16
	bs.content_margin_top = 10
	bs.content_margin_bottom = 10
	bubble.add_theme_stylebox_override("panel", bs)
	bubble.size_flags_horizontal = Control.SIZE_SHRINK_END if outgoing else Control.SIZE_SHRINK_BEGIN
	var l := Label.new()
	l.text = text
	l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	l.custom_minimum_size = Vector2(minf(300, FONT.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, 26).x + 4), 0)
	l.add_theme_font_size_override("font_size", 26)
	l.add_theme_color_override("font_color", Color.WHITE)
	bubble.add_child(l)
	phone_log.add_child(bubble)


func hide_phone() -> void:
	if phone:
		phone.queue_free()
		phone = null
		phone_log = null
