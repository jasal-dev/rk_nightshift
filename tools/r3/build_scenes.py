"""Generate Godot room scenes (scenes/rooms/*.tscn) from the render metadata in tools/r3/out/*.json.

Hotspot shapes, the walk area, spawns and depth scaling all come from projecting the 3D set,
so they line up with the background. Re-run after re-rendering a room."""
import json, os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))

ROOMS = {
    'squad_room': dict(node='SquadRoom', script='res://scripts/rooms/squad_room.gd', name='Homicide, Room 214'),
    'street': dict(node='Street', script='res://scripts/rooms/street.gd', name='Street', reflection=0.2),
    'pier9_dock': dict(node='Pier9Dock', script='res://scripts/rooms/pier9_dock.gd', name='Pier 9', reflection=0.2),
    'vance_office': dict(node='VanceOffice', script='res://scripts/rooms/vance_office.gd', name="Vance's office"),
    'mulholland_overlook': dict(node='MulhollandOverlook', script='res://scripts/rooms/mulholland_overlook.gd',
                                name='Mulholland overlook', reflection=0.15),
    'prius_interior': dict(node='PriusInterior', script='res://scripts/rooms/prius_interior.gd',
                           name="Kenji's Prius"),
    'norms_diner': dict(node='NormsDiner', script="res://scripts/rooms/norms_diner.gd", name="Norm's on Sunset",
                        reflection=0.08),
    'kenji_apartment': dict(node='KenjiApartment', script='res://scripts/rooms/kenji_apartment.gd',
                            name="Kenji's apartment"),
    'stardust_shop': dict(node='StardustShop', script='res://scripts/rooms/stardust_shop.gd',
                          name='Stardust Memorabilia', reflection=0.06),
    'stardust_office': dict(node='StardustOffice', script='res://scripts/rooms/stardust_office.gd',
                            name="Stardust's back office"),
    'stardust_roof': dict(node='StardustRoof', script='res://scripts/rooms/stardust_roof.gd',
                          name='Stardust roof', reflection=0.18),
    'stardust_roof_dark': dict(node='StardustRoofDark', script='res://scripts/rooms/stardust_roof_dark.gd',
                               name='Stardust roof', reflection=0.1),
    'fletcher_bridge': dict(node='FletcherBridge', script='res://scripts/rooms/fletcher_bridge.gd',
                            name='Fletcher Drive bridge', reflection=0.2),
    'river_channel': dict(node='RiverChannel', script='res://scripts/rooms/river_channel.gd',
                          name='LA River channel', reflection=0.12),
    'glass_house': dict(node='GlassHouse', script='res://scripts/rooms/glass_house.gd', name='Glendower Avenue',
                        reflection=0.12),
    'crane_garage': dict(node='CraneGarage', script='res://scripts/rooms/crane_garage.gd', name="Crane's garage",
                         reflection=0.1),
    'night_lab': dict(node='NightLab', script='res://scripts/rooms/night_lab.gd', name='Crime lab, night intake'),
}


def pv(pts):
    return 'PackedVector2Array(' + ', '.join(f'{x:g}, {y:g}' for x, y in pts) + ')'


def neon_overlay(room, poly):
    """Bright pixels of the neon sign, cut out of the background, for a flicker overlay."""
    bg = np.asarray(Image.open(os.path.join(ROOT, 'assets', 'rooms', f'{room}.png')).convert('RGB')).astype(float)
    xs, ys = [p[0] for p in poly], [p[1] for p in poly]
    x0, y0, x1, y1 = int(min(xs)), int(min(ys)), int(max(xs)) + 1, int(max(ys)) + 1
    crop = bg[y0:y1, x0:x1]
    lum = crop.max(-1)
    a = np.clip((lum - 110) / 80, 0, 1)
    rgba = np.dstack([crop * 0.55, a * 200]).clip(0, 255).astype(np.uint8)
    Image.fromarray(rgba, 'RGBA').save(os.path.join(ROOT, 'assets', 'rooms', f'{room}_neon.png'))
    return x0, y0


def build(room):
    cfg = ROOMS[room]
    d = json.load(open(os.path.join(HERE, 'out', f'{room}.json')))
    ext = [('Script', cfg['script'], 'script'), ('Texture2D', f'res://assets/rooms/{room}.png', 'bg'),
           ('Script', 'res://scripts/hotspot.gd', 'hs')]
    for tag in d.get('overlays', {}):
        ext.append(('Texture2D', f'res://assets/rooms/{room}_{tag}.png', f'ov_{tag}'))
    for tag in d.get('occluders', {}):
        ext.append(('Texture2D', f'res://assets/rooms/{room}_{tag}.png', f'occ_{tag}'))
    neon_pos = None
    if room == 'street' and 'neon' in d['hotspots']:
        neon_pos = neon_overlay(room, d['hotspots']['neon']['polygon'])
        ext.append(('Texture2D', f'res://assets/rooms/{room}_neon.png', 'neon'))
    L = ['[gd_scene format=3]', '']
    for t, p, i in ext:
        L.append(f'[ext_resource type="{t}" path="{p}" id="{i}"]')
    L.append('')
    if neon_pos:
        L += ['[sub_resource type="CanvasItemMaterial" id="add"]', 'blend_mode = 1', '']
    tint = d.get('tint', (1, 1, 1))
    L += [f'[node name="{cfg["node"]}" type="Node2D"]', 'script = ExtResource("script")',
          f'room_id = "{room}"', f'room_name = "{cfg["name"]}"',
          f'far_y = {d["far_y"]}', f'near_y = {d["near_y"]}', f'far_scale = {d["far_scale"]}',
          f'near_scale = {d["near_scale"]}', f'reflection_strength = {cfg.get("reflection", 0.0)}', f'tint = Color({tint[0]}, {tint[1]}, {tint[2]}, 1)', '',
          '[node name="Background" type="Sprite2D" parent="."]', 'texture = ExtResource("bg")', 'centered = false', '']
    bases = d.get('overlay_bases', {})
    for tag, (x, y) in d.get('overlays', {}).items():
        if tag in bases:
            continue                      # people standing on the floor go under Actors, below
        nm = tag.capitalize()
        L += [f'[node name="{nm}" type="Sprite2D" parent="."]', f'texture = ExtResource("ov_{tag}")', 'centered = false',
              f'position = Vector2({x}, {y})', '']
    if neon_pos:
        L += ['[node name="Neon" type="Sprite2D" parent="."]', 'material = SubResource("add")',
              'texture = ExtResource("neon")', 'centered = false', f'position = Vector2({neon_pos[0]}, {neon_pos[1]})', '']
    L += ['[node name="WalkArea" type="Polygon2D" parent="."]', 'color = Color(0.2, 0.9, 0.4, 0.3)',
          f'polygon = {pv(d["walk"])}', '',
          '[node name="Actors" type="Node2D" parent="."]', 'y_sort_enabled = true', '']
    # people as overlays (shown by flag): y-sorted with the detective like the props below
    for tag, (bx, by) in bases.items():
        x0, y0 = d['overlays'][tag]
        L += [f'[node name="{tag.capitalize()}" type="Sprite2D" parent="Actors"]', f'texture = ExtResource("ov_{tag}")',
              'centered = false', f'position = Vector2({bx}, {by})', f'offset = Vector2({x0 - bx}, {y0 - by})', '']
    # walk-behind props: position = floor baseline (the y-sort key), offset places the cut-out image
    for tag, o in d.get('occluders', {}).items():
        (x0, y0), (bx, by) = o['pos'], o['base']
        nm = ''.join(w.capitalize() for w in tag.split('_'))
        L += [f'[node name="{nm}" type="Sprite2D" parent="Actors"]', f'texture = ExtResource("occ_{tag}")',
              'centered = false', f'position = Vector2({bx}, {by})', f'offset = Vector2({x0 - bx}, {y0 - by})', '']
    if d.get('obstacles'):
        L += ['[node name="Obstacles" type="Node2D" parent="."]', '']
        for i, poly in enumerate(d['obstacles']):
            L += [f'[node name="Obstacle{i + 1}" type="Polygon2D" parent="Obstacles"]', 'color = Color(0.9, 0.3, 0.2, 0.4)',
                  f'polygon = {pv(poly)}', '']
    L += ['[node name="Spawns" type="Node2D" parent="."]', '']
    for name, (x, y) in d['spawns'].items():
        L += [f'[node name="{name}" type="Marker2D" parent="Spawns"]', f'position = Vector2({x}, {y})', '']
    L += ['[node name="Hotspots" type="Node2D" parent="."]', '']
    for hid in d['order']:
        if hid not in d['hotspots']:
            continue
        h = d['hotspots'][hid]
        w = h['walk_to'] or (0, 0)
        L += [f'[node name="{hid}" type="Area2D" parent="Hotspots"]', 'script = ExtResource("hs")', f'id = "{hid}"',
              f'display_name = "{h["name"]}"', f'walk_to = Vector2({w[0]}, {w[1]})', f'face = "{h["face"]}"', '',
              f'[node name="Shape" type="CollisionPolygon2D" parent="Hotspots/{hid}"]', f'polygon = {pv(h["polygon"])}', '']
    path = os.path.join(ROOT, 'scenes', 'rooms', f'{room}.tscn')
    open(path, 'w', newline='\n').write('\n'.join(L))
    print('wrote', path)


if __name__ == '__main__':
    for r in ROOMS:
        build(r)
