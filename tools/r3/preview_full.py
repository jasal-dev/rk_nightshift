"""Quick look at a set with every overlay showing: python preview_full.py <room> [hide,tags] -> out/<room>_full.png (960x540)."""
import importlib, os, sys
import numpy as np
from PIL import Image
from scene3d import composite, Camera
from render_room import finish

HERE = os.path.dirname(os.path.abspath(__file__))
room = sys.argv[1]
hide = set(sys.argv[2].split(',')) if len(sys.argv) > 2 and sys.argv[2] else set()
mod = importlib.import_module(room)
S, cam, env, meta = mod.build(hide=hide)
cam = Camera(cam.pos, cam.target, cam.fov, 960, 540)
env = dict(env, vol_scale=2)
surf, depth, vol = S.render(cam, env, room + '_full')
img, _ = composite(surf, vol, 1, exposure=meta.get('exposure', 1.0), grade=meta.get('grade'))
Image.fromarray(finish(img)).save(os.path.join(HERE, 'out', f'{room}_full.png'))
print('ok')
