class_name SaveMenu
extends PanelContainer
## The save and load menu: three slots, each with a screenshot, the case and the date and time it was saved. In save mode
## a click on a slot that holds a game asks before it overwrites; the menu from Esc also offers EXIT WITHOUT SAVING. In
## load mode empty and damaged slots can't be picked. BACK (or Esc, handled by whoever shows it) leaves.
## Emits `result`: "save:N", "load:N", "exit" or "back". Styled with the title screen's building blocks.

signal result(kind: String)

var mode := "save"                  ## "save" or "load"
var _allow_exit := false
var _vb: VBoxContainer
var _pending := 0                   ## the slot waiting for an answer to "overwrite?", 0 for none


func _init(menu_mode: String, allow_exit: bool) -> void:
	mode = menu_mode
	_allow_exit = allow_exit
	TitleScreen.style_panel(self)
	custom_minimum_size = Vector2(960, 0)
	_vb = VBoxContainer.new()
	_vb.add_theme_constant_override("separation", 10)
	add_child(_vb)
	_build()


func _build() -> void:
	for c in _vb.get_children():
		_vb.remove_child(c)
		c.queue_free()
	_vb.add_child(TitleScreen.menu_label("SAVE GAME" if mode == "save" else "LOAD GAME", 34, TitleScreen.BRASS))
	if _pending > 0:
		_build_confirm()
		return
	for n in range(1, Game.SLOT_COUNT + 1):
		_vb.add_child(_slot_button(n, Game.slot_info(n)))
	if _allow_exit:
		var exit := TitleScreen.menu_button("EXIT WITHOUT SAVING", 34)
		exit.pressed.connect(func(): result.emit("exit"))
		_vb.add_child(exit)
	var back := TitleScreen.menu_button("BACK", 38)
	back.pressed.connect(func(): result.emit("back"))
	_vb.add_child(back)


func _slot_button(n: int, info: Dictionary) -> Button:
	var b := TitleScreen.menu_button("", 30)
	b.custom_minimum_size = Vector2(864, 164)
	b.disabled = mode == "load" and (info.is_empty() or info.get("damaged", false))
	b.pressed.connect(func(): _picked(n, info))
	var row := HBoxContainer.new()
	row.set_anchors_preset(Control.PRESET_FULL_RECT)
	row.offset_left = 8
	row.offset_top = 6
	row.offset_right = -8
	row.offset_bottom = -6
	row.add_theme_constant_override("separation", 22)
	row.mouse_filter = Control.MOUSE_FILTER_IGNORE
	b.add_child(row)
	var pic := TextureRect.new()
	pic.custom_minimum_size = Vector2(256, 144)
	pic.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	pic.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	pic.mouse_filter = Control.MOUSE_FILTER_IGNORE
	pic.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	var frame := PanelContainer.new()
	frame.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0, 0, 0, 0.6)
	sb.border_color = TitleScreen.BRASS
	sb.set_border_width_all(2)
	frame.add_theme_stylebox_override("panel", sb)
	frame.add_child(pic)
	frame.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	row.add_child(frame)
	var col := VBoxContainer.new()
	col.mouse_filter = Control.MOUSE_FILTER_IGNORE
	col.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	col.add_theme_constant_override("separation", 2)
	row.add_child(col)
	var head := "SLOT %d" % n
	if info.is_empty():
		col.add_child(_left(head, 30, TitleScreen.AMBER))
		col.add_child(_left("Empty", 28, TitleScreen.GREY))
	elif info.get("damaged", false):
		col.add_child(_left(head, 30, TitleScreen.AMBER))
		col.add_child(_left("Damaged save", 28, Color(0.9, 0.45, 0.4)))
	else:
		pic.texture = info.get("shot")
		col.add_child(_left(head, 30, TitleScreen.AMBER))
		col.add_child(_left(String(Game.CASE_TITLES[int(info["case"])]), 26, TitleScreen.CREAM))
		col.add_child(_left(String(info["time"]), 26, TitleScreen.GREY))
	return b


func _left(text: String, size: int, col: Color) -> Label:
	var l := TitleScreen.menu_label(text, size, col)
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
	return l


func _picked(n: int, info: Dictionary) -> void:
	if mode == "load":
		result.emit("load:%d" % n)
	elif info.is_empty():
		result.emit("save:%d" % n)
	else:
		_pending = n
		_build()


func _build_confirm() -> void:
	_vb.add_child(TitleScreen.menu_label("Overwrite slot %d?" % _pending, 40, TitleScreen.CREAM))
	_vb.add_child(TitleScreen.menu_label("The game saved there will be lost.", 28, TitleScreen.GREY))
	var yes := TitleScreen.menu_button("YES, OVERWRITE", 38)
	yes.pressed.connect(func(): result.emit("save:%d" % _pending))
	_vb.add_child(yes)
	var no := TitleScreen.menu_button("NO", 38)
	no.pressed.connect(func():
		_pending = 0
		_build())
	_vb.add_child(no)


func back() -> void:
	## Esc: out of the overwrite question first, then out of the menu.
	if _pending > 0:
		_pending = 0
		_build()
	else:
		result.emit("back")
