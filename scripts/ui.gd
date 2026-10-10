class_name GameUI
extends CanvasLayer
## All on-screen UI, built in code so it is easy to read and change:
## hover label, speech text, inventory bar, dialogue choices, fades,
## the title screen, case/end cards and the in-viewport cursor.

signal skip_requested
signal choice_made(index: int)
signal inventory_clicked(id: String, button: int)
signal jigsaw_event(kind: String)   ## "wrong", "done" or "close" (see show_jigsaw)
signal piano_event(key: String)     ## a key's letter ("C" .. "G", "C#" ...) or "close" (see show_piano)
signal notebook_closed              ## the open notebook was put away (see show_notebook)

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
var choices_box: GridContainer
var fade_rect: ColorRect
var card: Control
var title: TitleScreen            ## the title screen, while it's up (see show_title)
var cursor: TextureRect
var cursor_item: TextureRect
var bar_pinned := false
var root: Control
var board: Control                ## murder board close-up (deduction)
var drive: Control                ## rain-on-windshield transition
var phone: PanelContainer         ## text messages
var phone_log: VBoxContainer
var device: PanelContainer        ## a phone or car screen (Kenji's Glide app, the Prius head unit, ...)
var paper: Control                ## a document or picture held up close (a letter, a card, the UV lamp's view)
var jigsaw: Control              ## the fit-the-pieces close-up (Crane's headlight)
var scene_pic: Control            ## a full-screen still under the speech (Case 5: the take, the 1:30 call, the end cards)
var piano: Control                ## Danny's keyboard close-up (Case 5)
var notebook: Control             ## Ray's notebook, open (see show_notebook)
var _piano_keys := {}             ## key name ("C4", "C#4" ...) -> its ColorRect
var _piano_flash: Label
var options: Array[String] = []   ## the options on screen (dialogue choices or device buttons), in choice_made order
var _drive_lights: Array[Sprite2D] = []
var _drive_drops: Array[Sprite2D] = []
var _wiper: Line2D
var _wiper_t := 0.0
var _glow: Texture2D
var _jig_pieces: Array[TextureRect] = []
var _jig_drag: TextureRect
var _jig_grab := Vector2.ZERO
var _jig_press := Vector2.ZERO



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

	choices_box = GridContainer.new()
	choices_box.position = Vector2(48, 780)
	choices_box.size = Vector2(1824, 270)
	choices_box.add_theme_constant_override("v_separation", 0)
	choices_box.add_theme_constant_override("h_separation", 24)
	choices_box.visible = false
	root.add_child(choices_box)

	fade_rect = ColorRect.new()
	fade_rect.color = Color.BLACK
	fade_rect.set_anchors_preset(Control.PRESET_FULL_RECT)
	fade_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.add_child(fade_rect)

	# speech sits above the fade, so a line spoken in the dark (Devin through his door) can be read on black
	speech_label = _make_label(Color(1, 1, 1))
	speech_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	speech_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	speech_label.visible = false
	root.add_child(speech_label)

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
func show_choices(opts: Array) -> void:
	## The options grow upwards from the bottom of the screen. A long list (an evidence list under the murder board)
	## goes into up to three columns, numbered down each column, and the font steps down until it fits.
	for c in choices_box.get_children():
		choices_box.remove_child(c)     # out of the grid now, so the old list doesn't size the new one
		c.queue_free()
	options.clear()
	var texts: Array[String] = []
	for i in opts.size():
		options.append(String(opts[i]))
		texts.append("%d. %s" % [i + 1, opts[i]])
	var top := 640.0 if board != null else 60.0     # under the board's panel when it is up
	var avail := 1050.0 - top
	var fit := _choice_layout(texts, avail)
	var font_size: int = fit[0]
	var cols: int = fit[1]
	var widths: Array = fit[2]
	var rows := ceili(texts.size() / float(cols))
	var row_h := ceilf(font_size * 1.53)
	choices_box.columns = cols
	for r in rows:
		for c in cols:
			var i := c * rows + r
			if i >= texts.size():
				var gap := Control.new()
				gap.custom_minimum_size = Vector2(widths[c], row_h)
				gap.mouse_filter = Control.MOUSE_FILTER_IGNORE
				choices_box.add_child(gap)
				continue
			var b := Button.new()
			b.text = texts[i]
			b.flat = true
			b.alignment = HORIZONTAL_ALIGNMENT_LEFT
			b.focus_mode = Control.FOCUS_NONE
			b.clip_text = true
			b.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
			b.custom_minimum_size = Vector2(widths[c], row_h)
			b.add_theme_font_size_override("font_size", font_size)
			b.add_theme_color_override("font_color", Color(0.75, 0.68, 0.55))
			b.add_theme_color_override("font_hover_color", Color(1, 0.85, 0.45))
			b.add_theme_color_override("font_pressed_color", Color(1, 0.85, 0.45))
			b.mouse_filter = Control.MOUSE_FILTER_STOP
			b.pressed.connect(func(): choice_made.emit(i))
			choices_box.add_child(b)
	choices_box.size = Vector2(1824, 0)
	choices_box.size = Vector2(1824, choices_box.get_combined_minimum_size().y)
	choices_box.position = Vector2(48, 1050 - choices_box.size.y)
	choices_box.visible = true


func _choice_layout(texts: Array[String], avail: float) -> Array:
	## [font size, columns, column widths]: the biggest font, then the fewest columns, where the rows fit the height and
	## each column is as wide as its widest option, the spare width shared out. Falls back to the smallest font in three
	## equal columns (long options get an ellipsis).
	for font_size: int in [FONT_SIZE, 26, 22]:
		var row_h := ceilf(font_size * 1.53)
		for cols: int in [1, 2, 3]:
			var rows := ceili(texts.size() / float(cols))
			if rows * row_h > avail:
				continue
			var widths: Array[float] = []
			var total := 24.0 * (cols - 1)
			for c in cols:
				var widest := 0.0
				for i in range(c * rows, mini((c + 1) * rows, texts.size())):
					widest = maxf(widest, FONT.get_string_size(texts[i], HORIZONTAL_ALIGNMENT_LEFT, -1, font_size).x)
				widths.append(widest + 16.0)
				total += widest + 16.0
			if total <= 1824.0:
				for c in cols:
					widths[c] += (1824.0 - total) / cols
				return [font_size, cols, widths]
	var w := (1824.0 - 48.0) / 3.0
	return [22, 3, [w, w, w]]


func hide_choices() -> void:
	choices_box.visible = false
	options.clear()


# --- device screens ---------------------------------------------------------
## A phone or car screen on the right of the screen: a coloured title bar, optional tabs, a body text,
## tappable rows and a Close button. Buttons emit choice_made with their index in `options`
## (tabs first, then rows, then Close). With interactive = false it only shows (a video, a list).
func show_device(title: String, tabs: Array, active: int, body: String, rows: Array, interactive := true,
		accent := Color(0.12, 0.58, 0.52), lcd := false) -> void:
	hide_device()
	options.clear()
	device = PanelContainer.new()
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0.1, 0.16, 0.08, 0.97) if lcd else Color(0.04, 0.05, 0.06, 0.97)
	sb.border_color = Color(0.22, 0.23, 0.26)
	sb.set_border_width_all(6)
	sb.set_corner_radius_all(30)
	sb.set_content_margin_all(20)
	device.add_theme_stylebox_override("panel", sb)
	device.position = Vector2(1236, 96)
	device.custom_minimum_size = Vector2(600, 0)
	device.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.add_child(device)
	root.move_child(device, 0)
	var vb := VBoxContainer.new()
	vb.add_theme_constant_override("separation", 10)
	device.add_child(vb)
	var head := PanelContainer.new()
	var hs := StyleBoxFlat.new()
	hs.bg_color = accent
	hs.set_corner_radius_all(12)
	hs.set_content_margin_all(10)
	head.add_theme_stylebox_override("panel", hs)
	var hl := Label.new()
	hl.text = title
	hl.add_theme_font_size_override("font_size", 28)
	hl.add_theme_color_override("font_color", Color.WHITE)
	head.add_child(hl)
	vb.add_child(head)
	if not tabs.is_empty():
		var tb := HBoxContainer.new()
		tb.add_theme_constant_override("separation", 6)
		vb.add_child(tb)
		for i in tabs.size():
			var b := _device_button(String(tabs[i]))
			b.size_flags_horizontal = Control.SIZE_EXPAND_FILL
			b.alignment = HORIZONTAL_ALIGNMENT_CENTER
			if i == active:
				b.add_theme_color_override("font_color", accent.lightened(0.5))
				b.add_theme_color_override("font_disabled_color", accent.lightened(0.5))
			tb.add_child(b)
	if body != "":
		var bl := Label.new()
		bl.text = body
		bl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		bl.custom_minimum_size = Vector2(556, 0)
		bl.add_theme_font_size_override("font_size", 24)
		bl.add_theme_color_override("font_color", Color(0.62, 0.95, 0.5) if lcd else Color(0.85, 0.88, 0.9))
		vb.add_child(bl)
	for r in rows:
		var b := _device_button(String(r))
		var rs := StyleBoxFlat.new()
		rs.bg_color = Color(1, 1, 1, 0.07)
		rs.set_corner_radius_all(8)
		rs.set_content_margin_all(8)
		for st in ["normal", "hover", "pressed", "disabled"]:
			b.add_theme_stylebox_override(st, rs)
		vb.add_child(b)
	if interactive:
		var c := _device_button("Close")
		c.alignment = HORIZONTAL_ALIGNMENT_CENTER
		vb.add_child(c)
	else:
		lock_device()


func _device_button(text: String) -> Button:
	var i := options.size()
	options.append(text)
	var b := Button.new()
	b.text = text
	b.flat = true
	b.alignment = HORIZONTAL_ALIGNMENT_LEFT
	b.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	b.custom_minimum_size = Vector2(0, 40)
	b.focus_mode = Control.FOCUS_NONE
	b.add_theme_font_size_override("font_size", 24)
	b.add_theme_color_override("font_color", Color(0.78, 0.82, 0.84))
	b.add_theme_color_override("font_hover_color", Color(1, 0.85, 0.45))
	b.add_theme_color_override("font_pressed_color", Color(1, 0.85, 0.45))
	b.add_theme_color_override("font_disabled_color", Color(0.78, 0.82, 0.84))
	b.mouse_filter = Control.MOUSE_FILTER_STOP
	b.pressed.connect(func(): choice_made.emit(i))
	return b


func lock_device() -> void:
	## The screen stays up but stops taking clicks (while Ray reads it out).
	options.clear()
	if device == null:
		return
	for b in device.find_children("*", "Button", true, false):
		(b as Button).disabled = true
		(b as Button).mouse_filter = Control.MOUSE_FILTER_IGNORE


func hide_device() -> void:
	if device:
		device.queue_free()
		device = null


# --- paper and picture close-ups ----------------------------------------------
## A document Ray holds up to read (the "paper" skin of the device screen): cream stock, dark type, and an optional
## note in a second hand (Gus's red ink, a ballpoint scrawl) under the type.
func show_paper(title: String, body: String, note := "", note_color := Color(0.62, 0.08, 0.08)) -> void:
	hide_paper()
	var panel := PanelContainer.new()
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0.93, 0.9, 0.82)
	sb.border_color = Color(0.62, 0.56, 0.44)
	sb.set_border_width_all(2)
	sb.set_content_margin_all(30)
	sb.shadow_color = Color(0, 0, 0, 0.55)
	sb.shadow_size = 14
	sb.shadow_offset = Vector2(6, 8)
	panel.add_theme_stylebox_override("panel", sb)
	panel.position = Vector2(1160, 90)
	panel.custom_minimum_size = Vector2(680, 0)
	panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	panel.rotation = deg_to_rad(-1.2)
	var vb := VBoxContainer.new()
	vb.add_theme_constant_override("separation", 14)
	panel.add_child(vb)
	for part in [[title, 30, Color(0.12, 0.12, 0.2)], [body, 24, Color(0.22, 0.2, 0.2)], [note, 27, note_color]]:
		if String(part[0]) == "":
			continue
		var l := Label.new()
		l.text = part[0]
		l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		l.custom_minimum_size = Vector2(620, 0)
		l.add_theme_font_size_override("font_size", part[1])
		l.add_theme_color_override("font_color", part[2])
		vb.add_child(l)
	paper = panel
	root.add_child(paper)
	root.move_child(paper, 0)


## A picture filling most of the screen (the photo wall under the UV lamp), dimming the room behind it.
func show_closeup(tex: Texture2D) -> void:
	hide_paper()
	var c := Control.new()
	c.set_anchors_preset(Control.PRESET_FULL_RECT)
	c.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var dim := ColorRect.new()
	dim.color = Color(0, 0, 0, 0.75)
	dim.set_anchors_preset(Control.PRESET_FULL_RECT)
	dim.mouse_filter = Control.MOUSE_FILTER_IGNORE
	c.add_child(dim)
	var pic := TextureRect.new()
	pic.texture = tex
	pic.position = (SCREEN - tex.get_size()) * 0.5 - Vector2(0, 50)
	pic.mouse_filter = Control.MOUSE_FILTER_IGNORE
	c.add_child(pic)
	paper = c
	root.add_child(paper)
	root.move_child(paper, 0)


# --- fit-the-pieces close-up (Case 4's headlight) ---------------------------------------------
## A picture with holes in it (bg) and loose pieces in a tray below. Drag a piece into its hole; click a piece to turn
## it a quarter. A piece snaps in only in the right place the right way up; otherwise it slides back to the tray and
## jigsaw_event("wrong") fires. jigsaw_event("done") when every piece is in, ("close") when the player steps back.
## pieces: [{"tex": Texture2D, "target": Vector2 (the piece's centre in bg pixels), "turns": int (start quarter turns
## away from upright)}].
func show_jigsaw(bg: Texture2D, pieces: Array) -> void:
	hide_jigsaw()
	jigsaw = Control.new()
	jigsaw.set_anchors_preset(Control.PRESET_FULL_RECT)
	jigsaw.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.add_child(jigsaw)
	root.move_child(jigsaw, 0)
	var dim := ColorRect.new()
	dim.color = Color(0, 0, 0, 0.8)
	dim.set_anchors_preset(Control.PRESET_FULL_RECT)
	dim.mouse_filter = Control.MOUSE_FILTER_STOP           # the room behind can't be clicked
	jigsaw.add_child(dim)
	var origin := Vector2((SCREEN.x - bg.get_size().x) * 0.5, 30)
	var pic := TextureRect.new()
	pic.texture = bg
	pic.position = origin
	pic.mouse_filter = Control.MOUSE_FILTER_IGNORE
	jigsaw.add_child(pic)
	_jig_pieces.clear()
	var tray_x := 560.0
	for i in pieces.size():
		var p: Dictionary = pieces[i]
		var tex: Texture2D = p["tex"]
		var r := TextureRect.new()
		r.texture = tex
		r.size = tex.get_size()
		r.pivot_offset = r.size * 0.5
		var home := Vector2(tray_x, 760 + (230 - r.size.y) * 0.5)
		tray_x += r.size.x + 160
		r.position = home
		var turns := int(p.get("turns", 0))
		r.rotation = turns * PI * 0.5
		r.mouse_filter = Control.MOUSE_FILTER_STOP
		r.set_meta("home", home)
		r.set_meta("turns", turns)
		r.set_meta("target", origin + Vector2(p["target"]) - r.size * 0.5)
		r.set_meta("placed", false)
		r.gui_input.connect(_on_jig_input.bind(r))
		jigsaw.add_child(r)
		_jig_pieces.append(r)
	var hint := _make_label(Color(0.85, 0.8, 0.65))
	hint.text = "Drag a piece into place. Click it to turn it."
	hint.position = Vector2(80, 950)
	jigsaw.add_child(hint)
	var back := Button.new()
	back.text = "Step back"
	back.flat = true
	back.focus_mode = Control.FOCUS_NONE
	back.position = Vector2(1640, 990)
	back.add_theme_color_override("font_color", Color(0.78, 0.82, 0.84))
	back.add_theme_color_override("font_hover_color", Color(1, 0.85, 0.45))
	back.pressed.connect(func(): jigsaw_event.emit("close"))
	jigsaw.add_child(back)


func hide_jigsaw() -> void:
	if jigsaw:
		jigsaw.queue_free()
		jigsaw = null
	_jig_pieces.clear()
	_jig_drag = null


func jigsaw_place(i: int) -> void:
	## Put piece i in its place the right way up, as if the player had (used by the automated playthrough).
	var r: TextureRect = _jig_pieces[i]
	r.set_meta("turns", 0)
	r.rotation = 0.0
	r.global_position = r.get_meta("target")
	_jig_drop(r)


func _on_jig_input(event: InputEvent, r: TextureRect) -> void:
	if r.get_meta("placed"):
		return
	var mb := event as InputEventMouseButton
	if mb and mb.button_index == MOUSE_BUTTON_LEFT:
		if mb.pressed:
			_jig_drag = r
			_jig_grab = r.get_global_mouse_position() - r.global_position
			_jig_press = r.get_global_mouse_position()
			r.move_to_front()
		elif _jig_drag == r:
			_jig_drag = null
			if r.get_global_mouse_position().distance_to(_jig_press) < 8.0:
				# a click: a quarter turn
				r.set_meta("turns", (int(r.get_meta("turns")) + 1) % 4)
				var t := create_tween()
				t.tween_property(r, "rotation", r.rotation + PI * 0.5, 0.15)
			else:
				_jig_drop(r)
	elif event is InputEventMouseMotion and _jig_drag == r:
		r.global_position = r.get_global_mouse_position() - _jig_grab


func _jig_drop(r: TextureRect) -> void:
	var target: Vector2 = r.get_meta("target")
	if r.global_position.distance_to(target) < 60.0 and int(r.get_meta("turns")) % 4 == 0:
		r.global_position = target
		r.set_meta("placed", true)
		r.mouse_filter = Control.MOUSE_FILTER_IGNORE
		var t := create_tween()
		t.tween_property(r, "modulate", Color(1.6, 1.6, 1.5), 0.12)
		t.tween_property(r, "modulate", Color.WHITE, 0.3)
		for p in _jig_pieces:
			if not p.get_meta("placed"):
				return
		jigsaw_event.emit("done")
	else:
		var t := create_tween()
		t.tween_property(r, "position", r.get_meta("home"), 0.3).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
		jigsaw_event.emit("wrong")

# --- Case 5: full-screen stills, the piano, the end cards ---------------------------------------
## A still filling the screen under the speech and choices (the take, the end cards). dim > 0 darkens it; a caption
## sits in the lower third.
func show_scene(tex: Texture2D, dim := 0.0, caption := "") -> void:
	hide_scene()
	scene_pic = Control.new()
	scene_pic.set_anchors_preset(Control.PRESET_FULL_RECT)
	scene_pic.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var back := ColorRect.new()
	back.color = Color.BLACK
	back.set_anchors_preset(Control.PRESET_FULL_RECT)
	back.mouse_filter = Control.MOUSE_FILTER_IGNORE
	scene_pic.add_child(back)
	if tex:
		var pic := TextureRect.new()
		pic.texture = tex
		pic.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		pic.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
		pic.set_anchors_preset(Control.PRESET_FULL_RECT)
		pic.mouse_filter = Control.MOUSE_FILTER_IGNORE
		scene_pic.add_child(pic)
	if dim > 0.0:
		var d := ColorRect.new()
		d.color = Color(0, 0, 0, dim)
		d.set_anchors_preset(Control.PRESET_FULL_RECT)
		d.mouse_filter = Control.MOUSE_FILTER_IGNORE
		scene_pic.add_child(d)
	if caption != "":
		var l := _make_label(Color(1, 0.92, 0.7))
		l.text = caption
		l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		l.add_theme_font_size_override("font_size", 36)
		l.position = Vector2(160, 780)
		l.size = Vector2(1600, 220)
		scene_pic.add_child(l)
	root.add_child(scene_pic)
	root.move_child(scene_pic, 0)


func hide_scene() -> void:
	if scene_pic:
		scene_pic.queue_free()
		scene_pic = null


## Danny's piano, seen from the bench: an octave and a half of keys from middle C, Nina's masking-tape letters on the
## white keys of the first octave, the set list on the stand above when Ray has it. A click on a key emits
## piano_event(letter) and flashes the letter; "Step back" emits piano_event("close").
const WHITE_KEYS := ["C4", "D4", "E4", "F4", "G4", "A4", "B4", "C5", "D5", "E5", "F5", "G5"]
const BLACK_KEYS := {"C#4": 0, "D#4": 1, "F#4": 3, "G#4": 4, "A#4": 5, "C#5": 7, "D#5": 8, "F#5": 10}


func show_piano(set_list: Texture2D = null) -> void:
	hide_piano()
	piano = Control.new()
	piano.set_anchors_preset(Control.PRESET_FULL_RECT)
	piano.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.add_child(piano)
	root.move_child(piano, 0)
	var dim := ColorRect.new()
	dim.color = Color(0.03, 0.02, 0.03, 0.92)
	dim.set_anchors_preset(Control.PRESET_FULL_RECT)
	dim.mouse_filter = Control.MOUSE_FILTER_STOP           # the room behind can't be clicked
	piano.add_child(dim)
	piano.add_child(_card_panel(Rect2(180, 540, 1560, 400), Color(0.04, 0.04, 0.05), Color(0.2, 0.2, 0.22), 4))
	if set_list:
		var sl := TextureRect.new()
		sl.texture = set_list
		sl.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		sl.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT
		sl.position = Vector2(700, 60)
		sl.size = Vector2(520, 438)
		sl.mouse_filter = Control.MOUSE_FILTER_IGNORE
		piano.add_child(sl)
	_piano_keys.clear()
	var kw := 120.0
	var x0 := 960.0 - kw * WHITE_KEYS.size() * 0.5
	for i in WHITE_KEYS.size():
		var k := ColorRect.new()
		k.color = Color(0.93, 0.91, 0.85)
		k.position = Vector2(x0 + i * kw + 2, 580)
		k.size = Vector2(kw - 4, 330)
		k.mouse_filter = Control.MOUSE_FILTER_STOP
		var key_name: String = WHITE_KEYS[i]
		k.gui_input.connect(_on_piano_input.bind(key_name))
		piano.add_child(k)
		_piano_keys[key_name] = k
		if i < 7:                                       # Nina's masking tape, the letters in ballpoint
			var tape := ColorRect.new()
			tape.color = Color(0.84, 0.77, 0.55)
			tape.position = Vector2(18, 250)
			tape.size = Vector2(kw - 40, 56)
			tape.mouse_filter = Control.MOUSE_FILTER_IGNORE
			k.add_child(tape)
			var l := Label.new()
			l.text = key_name.substr(0, 1)
			l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
			l.add_theme_color_override("font_color", Color(0.12, 0.16, 0.45))
			l.add_theme_font_size_override("font_size", 36)
			l.size = tape.size
			tape.add_child(l)
	for key_name: String in BLACK_KEYS:
		var b := ColorRect.new()
		b.color = Color(0.06, 0.06, 0.07)
		b.position = Vector2(x0 + (int(BLACK_KEYS[key_name]) + 1) * kw - 36, 580)
		b.size = Vector2(72, 200)
		b.mouse_filter = Control.MOUSE_FILTER_STOP
		b.gui_input.connect(_on_piano_input.bind(key_name))
		piano.add_child(b)
		_piano_keys[key_name] = b
	_piano_flash = _make_label(Color(1, 0.9, 0.6))
	_piano_flash.add_theme_font_size_override("font_size", 110)
	_piano_flash.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_piano_flash.position = Vector2(140, 250)
	_piano_flash.size = Vector2(460, 200)
	_piano_flash.modulate.a = 0.0
	piano.add_child(_piano_flash)
	var hint := _make_label(Color(0.85, 0.8, 0.65))
	hint.text = "Click the keys to play."
	hint.position = Vector2(200, 960)
	piano.add_child(hint)
	var back := Button.new()
	back.text = "Step back"
	back.flat = true
	back.focus_mode = Control.FOCUS_NONE
	back.position = Vector2(1600, 990)
	back.add_theme_color_override("font_color", Color(0.78, 0.82, 0.84))
	back.add_theme_color_override("font_hover_color", Color(1, 0.85, 0.45))
	back.pressed.connect(func(): piano_event.emit("close"))
	piano.add_child(back)


func hide_piano() -> void:
	if piano:
		piano.queue_free()
		piano = null
	_piano_keys.clear()


func _on_piano_input(event: InputEvent, key: String) -> void:
	var mb := event as InputEventMouseButton
	if mb and mb.pressed and mb.button_index == MOUSE_BUTTON_LEFT:
		piano_press(key)


func piano_press(key: String, emit := true) -> void:
	## Press a key ("D4", "C#5"): it goes down and its letter flashes with a note glyph. Emits piano_event with the
	## letter (sharps as "C#"). Also used by the automated playthrough and to replay the knock.
	if piano == null or not _piano_keys.has(key):
		return
	var k: ColorRect = _piano_keys[key]
	var up := Color(0.93, 0.91, 0.85) if key.length() == 2 else Color(0.06, 0.06, 0.07)
	k.color = Color(0.72, 0.64, 0.42) if key.length() == 2 else Color(0.32, 0.27, 0.2)
	_piano_flash.text = key.substr(0, key.length() - 1) + "  ♪"
	_piano_flash.modulate.a = 1.0
	get_tree().create_timer(0.18).timeout.connect(_piano_key_up.bind(k, up))
	var t := create_tween()
	t.tween_interval(0.18)
	t.tween_property(_piano_flash, "modulate:a", 0.0, 0.7)
	if emit:
		piano_event.emit(key.substr(0, key.length() - 1))


func _piano_key_up(k: ColorRect, up: Color) -> void:
	if is_instance_valid(k):
		k.color = up


## One end card over the credits: a still (a room, or Pryce), dimmed, with its line under it.
func show_endcard(tex: Texture2D, text: String) -> void:
	show_scene(tex, 0.5, text)


func hide_paper() -> void:
	if paper:
		paper.queue_free()
		paper = null


# --- the notebook ---------------------------------------------------------------------------------
## Ray's notebook, open on the desk: two ruled pages in his ink. Each case starts on a fresh page under its title and
## runs on to the next page when it fills one. It opens on the current case; the corner arrows turn back to the cases
## before. A note the player hasn't read yet is marked with a highlighter and NEW in the margin. Close, Esc (see Main),
## a right click or a click outside the book emit notebook_closed.
## sections: [{"title": String, "notes": [[text, new: bool], ...], "current": bool}], oldest case first.
const NB_BOOK := Rect2(190, 50, 1540, 950)
const NB_SIZE := 26           ## note font size
const NB_RULE := 40.0         ## ruled line spacing; each line of a note sits on one
const NB_TOP := 150.0         ## where the rules start, under the page's heading
const NB_LINES := 17          ## rules on a page
const NB_TEXT_W := 600.0
const NB_INK := Color(0.1, 0.14, 0.34)
var _nb_spreads: Array = []   ## the pages in pairs (see _nb_pages)
var _nb_spread := 0


func show_notebook(sections: Array) -> void:
	hide_notebook()
	var pages := _nb_pages(sections)
	var first := 0
	for i in pages.size():
		if bool(pages[i]["current"]):
			first = i
			break
	for i in range(0, pages.size(), 2):
		_nb_spreads.append(pages.slice(i, i + 2))
	notebook = Control.new()
	notebook.set_anchors_preset(Control.PRESET_FULL_RECT)
	notebook.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.add_child(notebook)
	root.move_child(notebook, 0)
	var dim := ColorRect.new()
	dim.color = Color(0, 0, 0, 0.7)
	dim.set_anchors_preset(Control.PRESET_FULL_RECT)
	dim.mouse_filter = Control.MOUSE_FILTER_STOP           # a click outside the book closes it
	dim.gui_input.connect(_on_nb_outside)
	notebook.add_child(dim)
	var close := _nb_button("Close", Vector2(NB_BOOK.end.x - 110, NB_BOOK.end.y + 12), func(): notebook_closed.emit())
	close.add_theme_color_override("font_color", Color(0.78, 0.82, 0.84))
	close.add_theme_color_override("font_hover_color", Color(1, 0.85, 0.45))
	notebook.add_child(close)
	_nb_show(first / 2)


func _nb_pages(sections: Array) -> Array:
	## Lays the notes out on pages: [{"title", "cont": bool, "current": bool, "notes": [[text, new, first rule]]}].
	var pages: Array = []
	for s: Dictionary in sections:
		var page := {"title": s["title"], "cont": false, "current": s["current"], "notes": []}
		pages.append(page)
		var notes: Array = s["notes"]
		if notes.is_empty():
			page["notes"].append(["Nothing yet. The night is young.", false, 0, "blank"])
		var rule := 0
		for n: Array in notes:
			var lines := _nb_line_count(String(n[0]))
			if rule > 0 and rule + lines > NB_LINES:
				page = {"title": s["title"], "cont": true, "current": s["current"], "notes": []}
				pages.append(page)
				rule = 0
			page["notes"].append([n[0], n[1], rule])
			rule += lines
	return pages


func _nb_line_count(text: String) -> int:
	var h := FONT.get_multiline_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, NB_TEXT_W, NB_SIZE).y
	return maxi(1, roundi(h / FONT.get_height(NB_SIZE)))


func _nb_show(spread: int) -> void:
	## Draws one spread (two pages) of the open book, in place of the one before.
	_nb_spread = clampi(spread, 0, _nb_spreads.size() - 1)
	var old := notebook.get_node_or_null("Book")
	if old:
		notebook.remove_child(old)
		old.queue_free()
	var book := Control.new()
	book.name = "Book"
	book.position = NB_BOOK.position
	book.size = NB_BOOK.size
	book.mouse_filter = Control.MOUSE_FILTER_STOP
	book.gui_input.connect(_on_nb_book)
	notebook.add_child(book)
	book.add_child(_card_panel(Rect2(Vector2.ZERO, NB_BOOK.size), Color(0.2, 0.11, 0.07), Color(0.12, 0.06, 0.04), 4))
	var pw := (NB_BOOK.size.x - 36) * 0.5
	var ph := NB_BOOK.size.y - 36
	var pages: Array = _nb_spreads[_nb_spread]
	for side in 2:
		var sheet := ColorRect.new()
		sheet.color = Color(0.94, 0.91, 0.82)
		sheet.position = Vector2(18 + side * pw, 18)
		sheet.size = Vector2(pw, ph)
		sheet.mouse_filter = Control.MOUSE_FILTER_IGNORE
		book.add_child(sheet)
		for i in NB_LINES:                                   # blue rules
			_nb_rect(sheet, Rect2(0, NB_TOP + (i + 1) * NB_RULE - 4, pw, 2), Color(0.45, 0.6, 0.8, 0.45))
		_nb_rect(sheet, Rect2(76, 0, 2, ph), Color(0.8, 0.3, 0.3, 0.6))                          # red margin
		_nb_rect(sheet, Rect2(pw - 26 if side == 0 else 0, 0, 26, ph), Color(0, 0, 0, 0.16))      # the gutter
		if side < pages.size():
			_nb_page(sheet, pages[side], _nb_spread * 2 + side + 1)
	if _nb_spread > 0:
		book.add_child(_nb_button("◀", Vector2(44, ph - 40), func(): _nb_show(_nb_spread - 1)))
	if _nb_spread < _nb_spreads.size() - 1:
		book.add_child(_nb_button("▶", Vector2(NB_BOOK.size.x - 84, ph - 40), func(): _nb_show(_nb_spread + 1)))


func _nb_page(sheet: Control, page: Dictionary, number: int) -> void:
	var cont := bool(page["cont"])
	var head := Label.new()
	head.text = String(page["title"]) + (" (cont.)" if cont else "")
	head.position = Vector2(96, 62 if cont else 54)
	head.add_theme_font_size_override("font_size", 26 if cont else 36)
	head.add_theme_color_override("font_color", Color(NB_INK, 0.6) if cont else NB_INK)
	head.mouse_filter = Control.MOUSE_FILTER_IGNORE
	sheet.add_child(head)
	var lh := FONT.get_height(NB_SIZE)
	for n: Array in page["notes"]:
		var lines := _nb_line_count(String(n[0]))
		var y := NB_TOP + int(n[2]) * NB_RULE + 4
		var new := bool(n[1])
		if new:
			_nb_rect(sheet, Rect2(90, y + 2, NB_TEXT_W + 12, lines * NB_RULE - 6), Color(1.0, 0.92, 0.25, 0.5))
		var tag := Label.new()                              # NEW in red, or a bullet, in the margin at each note
		tag.text = "NEW" if new else "•"
		tag.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		tag.position = Vector2(8, y + (6 if new else 0))
		tag.size = Vector2(64, 30)
		tag.add_theme_font_size_override("font_size", 20 if new else NB_SIZE)
		tag.add_theme_color_override("font_color", Color(0.72, 0.1, 0.08) if new else NB_INK)
		tag.mouse_filter = Control.MOUSE_FILTER_IGNORE
		tag.visible = n.size() < 4                          # not on an empty page's line
		sheet.add_child(tag)
		var l := Label.new()
		l.text = String(n[0])
		l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		l.position = Vector2(96, y)
		l.size = Vector2(NB_TEXT_W, lines * NB_RULE)
		l.add_theme_font_size_override("font_size", NB_SIZE)
		l.add_theme_constant_override("line_spacing", int(NB_RULE - lh))
		l.add_theme_color_override("font_color", NB_INK)
		l.mouse_filter = Control.MOUSE_FILTER_IGNORE
		sheet.add_child(l)
	var num := Label.new()
	num.text = str(number)
	num.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	num.position = Vector2(0, sheet.size.y - 46)
	num.size = Vector2(sheet.size.x, 30)
	num.add_theme_font_size_override("font_size", 20)
	num.add_theme_color_override("font_color", Color(NB_INK, 0.5))
	num.mouse_filter = Control.MOUSE_FILTER_IGNORE
	sheet.add_child(num)


func _nb_rect(parent: Control, r: Rect2, col: Color) -> void:
	var c := ColorRect.new()
	c.color = col
	c.position = r.position
	c.size = r.size
	c.mouse_filter = Control.MOUSE_FILTER_IGNORE
	parent.add_child(c)


func _nb_button(text: String, at: Vector2, on_press: Callable) -> Button:
	var b := Button.new()
	b.text = text
	b.flat = true
	b.focus_mode = Control.FOCUS_NONE
	b.position = at
	b.add_theme_color_override("font_color", NB_INK)
	b.add_theme_color_override("font_hover_color", Color(0.75, 0.3, 0.1))
	b.add_theme_color_override("font_pressed_color", Color(0.75, 0.3, 0.1))
	b.mouse_filter = Control.MOUSE_FILTER_STOP
	b.pressed.connect(on_press)
	return b


func notebook_page_turn(step: int) -> void:
	## Turn to the next (1) or previous (-1) spread, as the corner arrows do. Also used by the automated playthrough.
	if notebook:
		_nb_show(_nb_spread + step)


func _on_nb_outside(event: InputEvent) -> void:
	var mb := event as InputEventMouseButton
	if mb and mb.pressed and mb.button_index in [MOUSE_BUTTON_LEFT, MOUSE_BUTTON_RIGHT]:
		notebook_closed.emit()


func _on_nb_book(event: InputEvent) -> void:
	var mb := event as InputEventMouseButton
	if mb and mb.pressed and mb.button_index == MOUSE_BUTTON_RIGHT:
		notebook_closed.emit()


func hide_notebook() -> void:
	if notebook:
		notebook.queue_free()
		notebook = null
	_nb_spreads.clear()

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


func show_title(has_save: bool, text_speed: int) -> TitleScreen:
	## The title screen, under the fade (so Main can fade it in and out) and the cursor.
	hide_title()
	title = TitleScreen.new(has_save, text_speed)
	root.add_child(title)
	root.move_child(title, fade_rect.get_index())
	return title


func hide_title() -> void:
	if title:
		title.queue_free()
		title = null


# --- murder board (deduction) ---------------------------------------------------
## A close-up of the board: the victim's photo in the middle, the question above it and up to two
## evidence cards pinned either side with red string. Choices and speech are drawn on top.
func show_board(question: String, caption := "DANNY REYES\n34. Piano, Blue Note") -> void:
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
	cap.text = caption
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


func set_board_pins(pins: Array, labels: Array = []) -> void:
	## pins: up to two card texts ("" = empty slot, shown as a question mark, or as its label when given).
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
		var label := String(labels[i]) if i < labels.size() else ""
		var l := Label.new()
		l.text = String(pins[i]) if filled else ("?" if label == "" else label)
		l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		l.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
		l.add_theme_color_override("font_color", Color(0.12, 0.12, 0.2) if filled else Color(0.85, 0.75, 0.55))
		l.add_theme_font_size_override("font_size", 30 if filled or label != "" else 64)
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
