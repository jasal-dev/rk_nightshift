"""End-card stills for Case 5's credits: the only time the player sees Harlan Pryce. Writes assets/endcards/pryce_<kind>.png
(1280x720): 'cuffs' (walked out of Pryce Tower in handcuffs, Ending A), 'shovel' (a gold shovel at the groundbreaking,
Ending B), 'press' (a press conference, forty-one motions, Ending C) and 'umbrella' (leaving his lawyer's office under
umbrellas, Ending D).

python endcards.py [kind ...]"""
import math, os, sys
import numpy as np
from PIL import Image
from scene3d import *
from render_room import finish
import textures as tx
import npc
import cars

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
W, H = 1280, 720


def tower(S, z=-3.0, lit=False):
    """A glass lobby front: tall panes in steel mullions, PRYCE TOWER in steel letters over the doors."""
    S.mat('glass_t', (60, 80, 100), spec=1.6, shin=120, refl=0.55)
    S.mat('mullion', (150, 154, 160), spec=1.2, shin=60)
    S.mat('lobby', (200, 190, 170), emis=(255, 236, 200), emis_mult=0.9 if lit else 0.4)
    S.mat('tower_sign', (200, 200, 200), tex=tx.sign_board('PRYCE TOWER', (220, 222, 226), (40, 44, 52), 512, 96),
          texmode=1, spec=1.0, shin=60)
    S.wboxr(-20, 0.0, z - 0.6, 20, 30, z - 0.5, 'lobby')
    S.wboxr(-20, 0.0, z - 0.1, 20, 30, z, 'glass_t')
    for x in np.arange(-20, 20, 1.6):
        S.wboxr(x - 0.04, 0.0, z - 0.05, x + 0.04, 30, z + 0.06, 'mullion')
    for y in (3.6, 7.2, 10.8):
        S.wboxr(-20, y - 0.05, z - 0.05, 20, y + 0.05, z + 0.06, 'mullion')
    S.wboxr(-1.8, 0.0, z - 0.12, 1.8, 2.8, z - 0.02, 'lobby', op=1)
    S.wboxr(-2.6, 3.0, z + 0.06, 2.6, 3.5, z + 0.12, 'tower_sign')


def ground(S, mat='plaza'):
    S.mat('plaza', (255, 255, 255), tex=tx.hires(tx.concrete(seed=131, base=(160, 156, 150)), 2), texmode=4, texmap=1,
          texscale=2.5, spec=0.4, shin=40, refl=0.08)
    S.wboxr(-40, -1, -40, 40, 0, 40, mat)


def scene(kind):
    S = Scene()
    if kind == 'cuffs':
        ground(S)
        tower(S, z=-2.5, lit=True)
        npc.cast(S, 'pryce', dict(npc.STAND, lsp=-22, lsa=10, le=96, lin=96, rsp=-22, rsa=10, re=96, rin=96, hp=6, hy=-8,
                                  lhp=14, rhp=-12), (0.0, 0.0, 0.2), yaw=-8, scale=1.0)
        for (x, yaw) in ((-0.75, 12), (0.8, -20)):
            npc.cast(S, 'park', dict(npc.STAND, lsp=20, le=40, lin=30, rsp=4, re=18, hp=4, hy=10, lhp=10, rhp=-8,
                                     stubble=False, hair='cap'), (x, 0.0, 0.0), yaw=yaw, scale=1.02)
        S.sun((-0.4, -0.8, -0.5), (255, 236, 210), power=2.0, soft=8)
        S.sun((0.3, -1, 0.3), (150, 170, 210), power=0.5, shadow=False)
        cam = Camera((0.6, 1.5, 5.6), (0.0, 1.25, 0.0), fov=34, W=W * 2, H=H * 2)
        env = dict(sky=(150, 170, 200), bounce=(90, 86, 80), fog_col=(170, 180, 200), fog=0.004, fog_max=80)
    elif kind == 'shovel':
        ground(S)
        S.mat('dirt', (110, 76, 50), namp=0.5, nscale=8, bump=0.4, bscale=10)
        S.mat('gold', (230, 180, 70), spec=1.8, shin=80, refl=0.3)
        S.mat('banner', (220, 220, 220), tex=tx.sign_board('PRYCE HOLLYWOOD  -  BREAKING GROUND', (240, 230, 200), (24, 30, 60), 1024, 128, size=48),
              texmode=1)
        S.mat('pole', (150, 150, 156), spec=1.0)
        S.ell(WORLD, (0.4, 0.0, 0.3), (1.2, 0.35, 0.9), 'dirt', k=0.1)
        S.wboxr(-3.0, 1.5, -2.0, 3.0, 2.6, -1.95, 'banner')
        for x in (-3.0, 3.0):
            S.cyl((x, 0.0, -1.97), (x, 2.7, -1.97), 0.04, 'pole')
        npc.cast(S, 'pryce', dict(npc.STAND, lsp=40, le=50, lin=30, rsp=44, re=46, rin=20, hp=4, hy=-6, lhp=8, rhp=-6,
                                  rhand='fist', lhand='fist'), (-0.4, 0.0, 0.4), yaw=20, scale=1.0)
        # the gold shovel, held across him, its blade in the dirt
        S.cyl((-0.42, 1.12, 0.72), (0.2, 0.28, 0.72), 0.02, 'gold')
        S.wbox((0.27, 0.17, 0.72), (0.12, 0.16, 0.015), 'gold', rot=Rz(-36))
        S.sun((-0.4, -0.7, -0.6), (255, 240, 214), power=2.2, soft=8)
        S.sun((0.3, -1, 0.3), (150, 170, 210), power=0.5, shadow=False)
        S.mat('sky', (120, 160, 210), emis=(120, 160, 220), emis_mult=1.0)
        S.wboxr(-60, -1, -30, 60, 40, -29, 'sky')
        cam = Camera((0.4, 1.45, 5.0), (0.0, 1.15, 0.0), fov=36, W=W * 2, H=H * 2)
        env = dict(sky=(150, 180, 220), bounce=(100, 90, 80), fog_col=(170, 190, 220), fog=0.003, fog_max=80)
    elif kind == 'press':
        ground(S)
        S.mat('podium', (40, 40, 46), spec=0.8, shin=50)
        S.mat('seal', (200, 170, 80), spec=1.2)
        S.mat('mic', (20, 20, 22), spec=0.8)
        S.mat('backdrop', (220, 220, 220), tex=tx.sign_board('PRYCE DEVELOPMENT     PRYCE DEVELOPMENT     PRYCE DEVELOPMENT', (230, 230, 236), (30, 40, 80), 1024, 160, size=30),
              texmode=1, spec=0.2)
        S.wboxr(-3.5, 0.0, -1.2, 3.5, 3.0, -1.1, 'backdrop')
        S.wboxr(-0.45, 0.0, 0.5, 0.45, 1.15, 0.9, 'podium', rnd=0.02)
        S.fcyl((0.0, 0.7, 0.92), 0.14, 0.01, 'seal', axis='z')
        for k in range(6):
            a = (k - 2.5) * 0.12
            S.cyl((a, 1.15, 0.6), (a * 0.6, 1.42, 0.35), 0.01, 'mic')
            S.sph((a * 0.6, 1.44, 0.34), 0.03, 'mic')
        npc.cast(S, 'pryce', dict(npc.STAND, lsp=36, le=70, lin=40, rsp=36, re=70, rin=40, hp=2, hy=4),
                 (0.0, 0.0, 0.05), yaw=0, scale=1.0)
        S.light((0.0, 3.0, 3.0), (255, 240, 220), power=20, range=10, soft=10, spot=((0, -0.6, -1), 25, 50))
        S.light((-3.0, 2.0, 3.0), (210, 220, 255), power=8, range=10, soft=10)
        cam = Camera((0.0, 1.5, 4.6), (0.0, 1.3, 0.0), fov=36, W=W * 2, H=H * 2)
        env = dict(sky=(60, 60, 70), bounce=(50, 48, 50), fog_col=(40, 40, 46), fog=0.0, fog_max=80)
    else:   # umbrella
        S.mat('wet', (255, 255, 255), tex=tx.hires(tx.asphalt(seed=33), 2), texmode=4, texmap=1, texscale=3.0, refl=0.6,
              ripple=0.1, spec=0.8, shin=60)
        S.wboxr(-40, -1, -40, 40, 0, 40, 'wet')
        S.mat('stone', (150, 140, 126), namp=0.2, nscale=4)
        S.mat('brass_p', (200, 170, 90), spec=1.2, shin=60)
        S.mat('door_g', (30, 34, 40), spec=1.4, shin=80, refl=0.3)
        S.wboxr(-10, 0.0, -2.6, 10, 12, -2.5, 'stone')
        S.wboxr(-1.0, 0.0, -2.62, 1.0, 2.6, -2.5, 'door_g')
        S.wboxr(1.2, 1.4, -2.52, 1.7, 1.75, -2.48, 'brass_p')                      # the firm's brass plate
        cars.car(S, 'limo', (2.2, 0.0, 1.0), 90, (14, 14, 16), L=5.4, W=1.9, H=1.45, lights=False)
        npc.cast(S, 'pryce', dict(npc.STAND, lsp=10, le=40, lin=30, rsp=10, re=40, rin=30, hp=-6, hy=-30, lhp=16,
                                  rhp=-14), (0.0, 0.0, -0.4), yaw=50, scale=1.0)
        for (x, z, yaw) in ((-0.65, -0.1, 40), (0.6, -0.9, 60)):
            npc.cast(S, 'shadow', dict(npc.STAND, props=(('umbrella', 'r'),), rsp=30, rsa=26, re=92, rin=18, lsp=6,
                                       le=20, hp=4, hy=10), (x, 0.0, z), yaw=yaw, scale=1.0)
        S.light((0.0, 4.0, 2.0), (220, 230, 255), power=10, range=12, soft=14)
        S.sun((0.3, -1, 0.3), (120, 130, 160), power=0.8, shadow=False)
        cam = Camera((-1.0, 1.55, 5.4), (0.2, 1.2, -0.5), fov=40, W=W * 2, H=H * 2)
        env = dict(sky=(80, 86, 100), bounce=(40, 40, 46), fog_col=(90, 96, 110), fog=0.02, fog_max=80)
    env = dict(env, reflections=True, grid=0.5, ao_scale=1.0)
    return S, cam, env


def render(kind):
    S, cam, env = scene(kind)
    surf, depth, vol = S.render(cam, env, 'endcard_' + kind)
    img, _ = composite(surf, vol, 2, exposure=1.0)
    out = Image.fromarray(finish(img, seed=3))
    os.makedirs(os.path.join(ROOT, 'assets', 'endcards'), exist_ok=True)
    out.save(os.path.join(ROOT, 'assets', 'endcards', f'pryce_{kind}.png'))
    print('wrote', kind)


if __name__ == '__main__':
    for k in (sys.argv[1:] or ['cuffs', 'shovel', 'press', 'umbrella']):
        render(k)
