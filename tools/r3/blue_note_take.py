"""The take (Case 5, scene 5): the Blue Note gone dark while Danny's last recording plays. A still, not a room: the
game shows it full screen under the subtitles (GameUI.show_scene). A candle in the back booth and three men in it, Ray on
the end of the piano bench, and Danny at the keys, half there (a ghost: blended toward the frame without him)."""
import blue_note_bar as bar
from scene3d import Camera


def build(hide=()):
    S, _, env, meta = bar.build(hide, take=True)
    cam = Camera((-2.3, 1.6, -3.4), (1.6, 0.9, -5.7), fov=52, W=3840, H=2160)
    meta = dict(meta, room='blue_note_take', overlays=[], occluders={}, obstacles=[], ghosts={'danny': 0.5},
                exposure=2.3, hotspots={}, hotspot_order=[],
                screen=dict(walk=[(0, 0), (1920, 0), (1920, 1080), (0, 1080)], spawns={'start': (960, 900)},
                            scale=((0, 1.0), (1080, 1.0))))
    return S, cam, env, meta
