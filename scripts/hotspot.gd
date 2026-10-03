class_name Hotspot
extends Area2D
## A clickable thing in a room. Draw its shape with a CollisionPolygon2D child.
## `walk_to` is where the detective stands to use it (room coordinates);
## `face` is the direction he faces when he gets there.

@export var id := ""
@export var display_name := ""
@export var walk_to := Vector2.ZERO
@export_enum("none", "left", "right", "up", "down") var face: String = "none"
@export var enabled := true


func contains_global(global_point: Vector2) -> bool:
	for c in get_children():
		if c is CollisionPolygon2D:
			var cp := c as CollisionPolygon2D
			var local := cp.global_transform.affine_inverse() * global_point
			if Geometry2D.is_point_in_polygon(local, cp.polygon):
				return true
	return false
