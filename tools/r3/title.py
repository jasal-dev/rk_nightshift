"""The title screen's backdrop: the street in its Case 5 crime-scene state (street.build(crime=True)) with nobody in
it, Park, Teo and Mara left out. Only the patrol car's light bar turns (bar_red / bar_blue, exclusive overlays).
Not a room: no hotspots, no light probes ('screen'), and no scene from build_scenes.py.

python render_room.py title   ->  assets/rooms/title.png, title_bar_red.png, title_bar_blue.png
"""
import street

EMPTY = {'park', 'teo', 'mara'}


def build(hide=()):
    S, cam, env, meta = street.build(set(hide) | EMPTY, crime=True)
    meta = dict(meta, room='title', hotspots={}, hotspot_order=[], hotspot_shapes={}, occluders={}, obstacles=[],
                overlay_bases={}, overlays=['bar_red', 'bar_blue'], exclusive_overlays=['bar_red', 'bar_blue'],
                screen={'walk': [(0, 0), (1920, 0), (1920, 1080)], 'spawns': {}, 'scale': ((0, 1.0), (1080, 1.0))})
    return S, cam, env, meta
