class_name Room
extends Node2D
## Base class for every room scene.
##
## Expected children:
##   Background (Sprite2D)       - the painted backdrop, positioned at (0, 0)
##   WalkArea   (Polygon2D)      - where the player can walk (hidden at runtime)
##   Actors     (Node2D, y-sort) - player and walk-behind props. A prop is a Sprite2D whose
##                                 position is its floor baseline and whose offset draws the
##                                 image; the player is drawn behind it while his feet are above
##                                 that baseline on screen.
##   Obstacles  (Node2D)         - optional Polygon2D footprints inside the walk area that the
##                                 player walks around (a hydrant, a lamp post)
##   Hotspots   (Node2D)         - Hotspot children (Area2D + CollisionPolygon2D)
##   Spawns     (Node2D)         - Marker2D entry points, named after the room you come from
##
## Room scripts override `interact()` and optionally `on_enter()`.

@export var room_id := ""
@export var room_name := ""
@export var tint := Color.WHITE  ## fallback colour for the detective when the room has no light probes
@export var reflection_strength := 0.0  ## wet floor: opacity of the detective's reflection (0 = none)
@export_group("Depth scaling")
@export var far_y := 250.0
@export var near_y := 350.0
@export var far_scale := 0.8
@export var near_scale := 1.0

var main: Node            ## set by Main; gives access to say(), choose(), change_room() ...
var player: Player

var _light := PackedFloat32Array()   ## light probe grid, 16 floats per cell (see light_at)
var _light_cell := 32.0
var _light_w := 0
var _light_h := 0
var light_exposure := 1.0

var _walk_poly := PackedVector2Array()
var _obstacles: Array[PackedVector2Array] = []
var _nodes := PackedVector2Array()


func _ready() -> void:
	_load_light()
	var wa := get_node_or_null("WalkArea") as Polygon2D
	if wa:
		wa.visible = false
		_walk_poly = wa.transform * wa.polygon
		var inner := Geometry2D.offset_polygon(_walk_poly, -9.0)
		for p in inner:
			_nodes.append_array(p)
	var obs := get_node_or_null("Obstacles")
	if obs:
		obs.visible = false
		for c in obs.get_children():
			if c is Polygon2D:
				var poly: PackedVector2Array = (c as Polygon2D).transform * (c as Polygon2D).polygon
				_obstacles.append(poly)
				# path nodes just outside each obstacle so routes can go around it
				for p in Geometry2D.offset_polygon(poly, 9.0):
					_nodes.append_array(p)


# --- lighting ------------------------------------------------------------
func _load_light() -> void:
	var path := "res://assets/rooms/%s_light.json" % room_id
	if not FileAccess.file_exists(path):
		return
	var d: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	if not d is Dictionary:
		return
	_light_cell = float(d["cell"])
	_light_w = int(d["gw"])
	_light_h = int(d["gh"])
	light_exposure = float(d.get("exposure", 1.0))
	_light = PackedFloat32Array(d["data"])


func has_light() -> bool:
	return not _light.is_empty()


func light_at(p: Vector2) -> PackedFloat32Array:
	## Light at a floor point (the detective's feet), bilinear between probe cells.
	## [0..2] ambient, [3..5] left key, [6..8] right key, [9..11] rim, [12..14] fog inscatter, [15] fog transmittance
	var out := PackedFloat32Array()
	out.resize(16)
	if _light.is_empty():
		return out
	var fx := p.x / _light_cell - 0.5
	var fy := p.y / _light_cell - 0.5
	var i0 := floori(fx)
	var j0 := floori(fy)
	var tx := fx - i0
	var ty := fy - j0
	for c in 4:
		var i := clampi(i0 + (c & 1), 0, _light_w - 1)
		var j := clampi(j0 + (c >> 1), 0, _light_h - 1)
		var w := (tx if (c & 1) == 1 else 1.0 - tx) * (ty if (c >> 1) == 1 else 1.0 - ty)
		var base := (j * _light_w + i) * 16
		for k in 16:
			out[k] += _light[base + k] * w
	return out


func scale_at(y: float) -> float:
	var t := clampf((y - far_y) / maxf(1.0, near_y - far_y), 0.0, 1.0)
	return lerpf(far_scale, near_scale, t)


func hotspots() -> Array[Hotspot]:
	var out: Array[Hotspot] = []
	var holder := get_node_or_null("Hotspots")
	if holder:
		for c in holder.get_children():
			if c is Hotspot:
				out.append(c)
	return out


func hotspot_at(p: Vector2) -> Hotspot:
	## Topmost enabled hotspot under point p (later children win).
	var found: Hotspot = null
	var gp := global_transform * p
	for h in hotspots():
		if h.enabled and h.visible and h.contains_global(gp):
			found = h
	return found


func hotspot(id: String) -> Hotspot:
	for h in hotspots():
		if h.id == id:
			return h
	return null


func spawn_point(from_room: String) -> Vector2:
	var spawns := get_node_or_null("Spawns")
	if spawns:
		var m := spawns.get_node_or_null(from_room) as Node2D
		if m == null and spawns.get_child_count() > 0:
			m = spawns.get_child(0) as Node2D
		if m:
			return m.position
	return Vector2(960, 960)


# --- pathfinding (visibility graph inside the walk polygon) -------------
func is_walkable(p: Vector2) -> bool:
	if not _walk_poly.is_empty() and not Geometry2D.is_point_in_polygon(p, _walk_poly):
		return false
	for o in _obstacles:
		if Geometry2D.is_point_in_polygon(p, o):
			return false
	return true


func _all_edges() -> Array[PackedVector2Array]:
	var polys: Array[PackedVector2Array] = [_walk_poly]
	polys.append_array(_obstacles)
	return polys


func clamp_to_walkable(p: Vector2) -> Vector2:
	if is_walkable(p):
		return p
	var best := p
	var best_d := INF
	for poly: PackedVector2Array in _all_edges():
		var n := poly.size()
		for i in n:
			var c := Geometry2D.get_closest_point_to_segment(p, poly[i], poly[(i + 1) % n])
			var d := c.distance_squared_to(p)
			if d < best_d:
				best_d = d
				best = c
	# nudge inside
	for r in [6.0, 12.0, 24.0]:
		for dir in [Vector2.UP, Vector2.DOWN, Vector2.LEFT, Vector2.RIGHT,
				Vector2(1, 1).normalized(), Vector2(-1, 1).normalized(),
				Vector2(1, -1).normalized(), Vector2(-1, -1).normalized()]:
			var q: Vector2 = best + dir * r
			if is_walkable(q):
				return q
	return best


func _visible(a: Vector2, b: Vector2) -> bool:
	for poly: PackedVector2Array in _all_edges():
		var n := poly.size()
		for i in n:
			if Geometry2D.segment_intersects_segment(a, b, poly[i], poly[(i + 1) % n]) != null:
				return false
	return is_walkable((a + b) * 0.5)


func find_path(from: Vector2, to: Vector2) -> PackedVector2Array:
	if _walk_poly.is_empty():
		return PackedVector2Array([from, to])
	var start := clamp_to_walkable(from)
	var goal := clamp_to_walkable(to)
	if _visible(start, goal):
		return PackedVector2Array([from, goal])
	var astar := AStar2D.new()
	var pts := PackedVector2Array([start, goal])
	for v in _nodes:
		if is_walkable(v):
			pts.append(v)
	for i in pts.size():
		astar.add_point(i, pts[i])
	for i in pts.size():
		for j in range(i + 1, pts.size()):
			if _visible(pts[i], pts[j]):
				astar.connect_points(i, j)
	var path := astar.get_point_path(0, 1)
	if path.is_empty():
		return PackedVector2Array([from, goal])
	path[0] = from
	return path


# --- effects -----------------------------------------------------------
func add_rain(amount := 500) -> void:
	## Screen-wide rain in front of everything (outdoor rooms call this from _ready).
	var rain := CPUParticles2D.new()
	rain.name = "Rain"
	rain.texture = preload("res://assets/rooms/raindrop.png")
	rain.amount = amount
	rain.lifetime = 0.9
	rain.preprocess = 1.0
	rain.position = Vector2(960, -40)
	rain.emission_shape = CPUParticles2D.EMISSION_SHAPE_RECTANGLE
	rain.emission_rect_extents = Vector2(1140, 12)
	rain.direction = Vector2(-0.1, 1)
	rain.spread = 2.0
	rain.gravity = Vector2.ZERO
	rain.initial_velocity_min = 1250.0
	rain.initial_velocity_max = 1500.0
	rain.scale_amount_min = 0.7
	rain.scale_amount_max = 1.2
	rain.z_index = 50
	add_child(rain)


# --- hooks for room scripts --------------------------------------------
func on_enter(_from_room: String) -> void:
	## Called after the room has faded in. May be a coroutine (use await).
	pass


func intro() -> void:
	## Called once when a new game starts in this room.
	pass


func interact(_hs: Hotspot, verb: String, item: String) -> void:
	## Override in room scripts. verb is "look" or "use"; item is the
	## selected inventory item id when the player uses an item on the hotspot.
	await default_response(verb, item)


func default_response(verb: String, item: String) -> void:
	if item != "":
		await main.say(["That won't work.", "I don't think so.", "No."].pick_random())
	elif verb == "look":
		await main.say(["Nothing special.", "Seen better. Seen worse."].pick_random())
	else:
		await main.say(["I can't do anything with that.", "Leave it."].pick_random())
