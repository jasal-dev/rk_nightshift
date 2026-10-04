"""Close-up: inside Kenji's Prius, leaning in between the front seats from the back, where his killer sat.
The same 3D set as the overlook (mulholland_overlook.py) with the camera moved inside and the windshield left out,
so the rain and the basin show past the dash. Kenji is seen from behind, his face to the window.
Ray isn't drawn here (the room hides him); every hotspot is look-and-use from where he leans in."""
from scene3d import Camera
import mulholland_overlook as mo
from mulholland_overlook import car_pt


def fquad(c, hw, hh):
    """A quad facing the back of the car around car-local point c (for hotspot shapes)."""
    x, y, z = c
    return [car_pt(x - hw, y - hh, z), car_pt(x + hw, y - hh, z), car_pt(x + hw, y + hh, z), car_pt(x - hw, y + hh, z)]


def build(hide=()):
    S, _, env, _ = mo.build(hide=set(hide) | {'windshield', 'tail_glow'})
    cam = Camera(car_pt(0.06, 1.37, 1.2), car_pt(-0.12, 0.9, -0.9), fov=66, W=3840, H=2160)
    env = dict(env, fog=0.008)
    # door pocket on the open door, in car-local coordinates (see the door frame in mulholland_overlook.build)
    meta = dict(
        room='prius_interior',
        screen=dict(walk=[(840, 1046), (1080, 1046), (1080, 1076), (840, 1076)],
                    spawns={'mulholland_overlook': (960, 1062), 'start': (960, 1062)},
                    scale=((1046, 1.0), (1076, 1.0))),
        walk=[], spawns={},
        hotspots={
            'kenji': ('Kenji', None, 'none'),
            'phone_mount': ('phone in the dash mount', None, 'none'),
            'head_unit': ('dashboard screen', None, 'none'),
            'dashcam': ('dashcam mount', None, 'none'),
            'cups': ('cup holders', None, 'none'),
            'door_pocket': ("driver's door pocket", None, 'none'),
            'visor': ('sun visor', None, 'none'),
            'ignition': ('ignition', None, 'none'),
            'glovebox': ('glovebox', None, 'none'),
            'back_seat': ('back seat', None, 'none'),
            'out': ('back outside', None, 'none'),
        },
        hotspot_shapes={
            'kenji': fquad((-0.4, 1.12, 0.3), 0.26, 0.32),
            'phone_mount': fquad((-0.16, 1.08, -0.8), 0.07, 0.1),
            'head_unit': fquad((0.0, 0.99, -0.74), 0.13, 0.08),
            'dashcam': fquad((0.0, 1.37, -0.64), 0.1, 0.06),
            'cups': fquad((0.0, 0.8, -0.2), 0.13, 0.08),
            'door_pocket': [car_pt(-1.05, 0.38, -0.05), car_pt(-1.6, 0.38, -0.3), car_pt(-1.6, 0.62, -0.3),
                            car_pt(-1.05, 0.62, -0.05)],
            'visor': fquad((-0.38, 1.4, -0.4), 0.2, 0.06),
            'ignition': fquad((-0.17, 0.88, -0.72), 0.06, 0.05),
            'glovebox': fquad((0.42, 0.8, -0.74), 0.23, 0.09),
            'out': [car_pt(-0.95, 0.4, -0.45), car_pt(-0.95, 0.4, 0.65), car_pt(-0.95, 1.45, 0.65),
                    car_pt(-0.95, 1.45, -0.45)],
        },
        screen_shapes={'back_seat': [(1240, 950), (1920, 950), (1920, 1080), (1240, 1080)]},   # under Ray
        hotspot_order=['out', 'back_seat', 'door_pocket', 'kenji', 'glovebox', 'cups', 'head_unit', 'ignition',
                       'phone_mount', 'dashcam', 'visor'],
        tint=(0.8, 0.76, 0.8),
        exposure=1.7,
    )
    return S, cam, env, meta
