class_name Player
extends Node2D
## The detective. Walks along paths supplied by the room, picks animations from
## movement direction, scales with depth and plays talk/action animations.

signal arrived

const Anims := preload("res://scripts/detective_anims.gd")
const SHEET := preload("res://assets/characters/detective.png")
const LIGHT_SHEET := preload("res://assets/characters/detective_light.png")
const RELIGHT := preload("res://shaders/relight.gdshader")

@export var walk_speed := 186.0  ## pixels per second at scale 1.0

var facing := "right"           ## right / left / up / down
var talking := false
var _path: PackedVector2Array = []
var _room: Room
var _base_scale := 1.0

@onready var sprite: AnimatedSprite2D = $Sprite
var _mat: ShaderMaterial
var _reflection: AnimatedSprite2D
var _shadow: Sprite2D
var _lit_at := Vector2.INF


func _ready() -> void:
	var frames := _build_frames()
	_mat = ShaderMaterial.new()
	_mat.shader = RELIGHT
	_mat.set_shader_parameter("light_tex", LIGHT_SHEET)
	sprite.sprite_frames = frames
	sprite.centered = false
	sprite.offset = -Anims.PIVOT
	sprite.material = _mat
	# soft contact shadow under the feet, drawn before the body
	_shadow = Sprite2D.new()
	_shadow.name = "Shadow"
	_shadow.texture = _make_shadow_texture()
	_shadow.scale = Vector2(0.78, 0.2)
	_shadow.modulate = Color(0, 0, 0, 0.55)
	add_child(_shadow)
	move_child(_shadow, 0)
	# upside-down copy for wet floors (shown only where the room asks for it)
	_reflection = AnimatedSprite2D.new()
	_reflection.name = "Reflection"
	_reflection.sprite_frames = frames
	_reflection.centered = false
	_reflection.offset = -Anims.PIVOT
	_reflection.scale = Vector2(1, -1)
	var rm := ShaderMaterial.new()
	rm.shader = RELIGHT
	rm.set_shader_parameter("light_tex", LIGHT_SHEET)
	rm.set_shader_parameter("reflection", true)
	_reflection.material = rm
	_reflection.visible = false
	add_child(_reflection)
	move_child(_reflection, 0)
	_play_idle()


func _make_shadow_texture() -> Texture2D:
	var g := Gradient.new()
	g.set_color(0, Color(1, 1, 1, 1))
	g.set_color(1, Color(1, 1, 1, 0))
	g.add_point(0.45, Color(1, 1, 1, 0.55))
	var t := GradientTexture2D.new()
	t.gradient = g
	t.fill = GradientTexture2D.FILL_RADIAL
	t.fill_from = Vector2(0.5, 0.5)
	t.fill_to = Vector2(1.0, 0.5)
	t.width = 128
	t.height = 128
	return t


func _update_light() -> void:
	## Pull the room's light at the feet into the relight shader.
	if _room == null or not _room.has_light():
		return
	_lit_at = position
	var l := _room.light_at(position)
	for m: ShaderMaterial in [_mat, _reflection.material as ShaderMaterial]:
		m.set_shader_parameter("ambient", Vector3(l[0], l[1], l[2]))
		m.set_shader_parameter("key_left", Vector3(l[3], l[4], l[5]))
		m.set_shader_parameter("key_right", Vector3(l[6], l[7], l[8]))
		m.set_shader_parameter("key_rim", Vector3(l[9], l[10], l[11]))
		m.set_shader_parameter("fog_add", Vector3(l[12], l[13], l[14]))
		m.set_shader_parameter("fog_t", l[15])
		m.set_shader_parameter("exposure", _room.light_exposure)


func _build_frames() -> SpriteFrames:
	var frames := SpriteFrames.new()
	frames.remove_animation("default")
	var fs: Vector2i = Anims.FRAME_SIZE
	for anim_name in Anims.ANIMS:
		var a: Array = Anims.ANIMS[anim_name]
		frames.add_animation(anim_name)
		frames.set_animation_speed(anim_name, float(a[2]))
		frames.set_animation_loop(anim_name, bool(a[3]))
		for i in int(a[1]):
			var at := AtlasTexture.new()
			at.atlas = SHEET
			at.region = Rect2(i * fs.x, int(a[0]) * fs.y, fs.x, fs.y)
			frames.add_frame(anim_name, at)
	return frames


func set_room(room: Room) -> void:
	_room = room
	if room.has_light():
		modulate = Color.WHITE
		sprite.material = _mat
	else:
		modulate = room.tint          # no probes: plain sprite tinted to the room
		sprite.material = null
	_reflection.visible = room.has_light() and room.reflection_strength > 0.0
	(_reflection.material as ShaderMaterial).set_shader_parameter("reflection_alpha", room.reflection_strength)
	_update_scale()
	_update_light()


func height() -> float:
	return Anims.HEIGHT * scale.y


# --- movement -------------------------------------------------------------
func walk_to(target: Vector2) -> void:
	## Walk to target (room coordinates) and return when arrived or interrupted.
	if _room == null:
		return
	_path = _room.find_path(position, target)
	if _path.size() < 2:
		_path = []
		_play_idle()
		arrived.emit()
		return
	_path.remove_at(0)
	await arrived


func stop() -> void:
	if not _path.is_empty():
		_path = []
		_play_idle()
		arrived.emit()


func is_walking() -> bool:
	return not _path.is_empty()


func _process(delta: float) -> void:
	if position != _lit_at:
		_update_light()
	if _reflection.visible:
		if _reflection.animation != sprite.animation:
			_reflection.animation = sprite.animation
		_reflection.frame = sprite.frame
	if _path.is_empty():
		return
	var target := _path[0]
	var to := target - position
	var step := walk_speed * scale.y * delta
	if to.length() <= step:
		position = target
		_path.remove_at(0)
		if _path.is_empty():
			_play_idle()
			arrived.emit()
			return
		to = _path[0] - position
	else:
		position += to.normalized() * step
	_face_vector(to)
	_play("walk_" + facing)
	_update_scale()


func _update_scale() -> void:
	if _room:
		var s := _room.scale_at(position.y)
		scale = Vector2(s, s)


func _face_vector(v: Vector2) -> void:
	if v.length() < 0.01:
		return
	if absf(v.x) >= absf(v.y) * 0.75:
		facing = "right" if v.x > 0 else "left"
	else:
		facing = "down" if v.y > 0 else "up"


func face(dir: String) -> void:
	if dir in ["left", "right", "up", "down"]:
		facing = dir
		_play_idle()


func face_point(p: Vector2) -> void:
	_face_vector(p - position)
	_play_idle()


# --- animation ------------------------------------------------------------
func _play(anim_name: String) -> void:
	if sprite.animation != anim_name or not sprite.is_playing():
		sprite.play(anim_name)


func _play_idle() -> void:
	if talking:
		_play_talk()
	else:
		_play("idle_" + facing)


func _play_talk() -> void:
	match facing:
		"up": _play("idle_up")
		"down": _play("talk_down")
		_: _play("talk_" + facing)


func set_talking(on: bool) -> void:
	talking = on
	if _path.is_empty():
		_play_idle()


func play_action(kind: String) -> void:
	## One-shot actions: "pickup", "use", "notebook", "shrug", "badge", "look_around".
	var anim_name := kind
	match kind:
		"pickup", "use", "notebook":
			var side := facing if facing in ["left", "right"] else "right"
			facing = side
			anim_name = "%s_%s" % [kind, side]
		"badge":
			facing = "down"
			anim_name = "show_badge"
	if not sprite.sprite_frames.has_animation(anim_name):
		return
	sprite.play(anim_name)
	if sprite.sprite_frames.get_animation_loop(anim_name):
		await get_tree().create_timer(2.0).timeout
	else:
		await sprite.animation_finished
	_play_idle()
