"""The night intake window of the LAPD crime lab at Cal State LA, 4:45 a.m. (Case 4, scene 6).

A bright, bare corridor: linoleum, cinder block painted cream, fluorescent panels. In the far wall a thick window over a
steel pass-through tray, a buzzer beside it and a taped sign: "NIGHT INTAKE. RING ONCE." Behind the glass Ike Feld sits
at his bench with the hood of his sweatshirt up, a Dodgers mug, three monitors glowing. A plastic chair against the
wall, a water fountain, a bulletin board, and the door back out to the lot (left), under an EXIT sign."""
import math, random
import numpy as np
from scene3d import *
import textures as tx
import npc

WZ = -3.0                     # the window wall
WIN = (-1.25, 1.25, 0.95, 2.05)
X0, X1, Z1 = -4.2, 4.2, 5.0
IKE = (0.15, -4.25)
DOOR = (-3.4, -2.3)           # the exit door's x extent, in the window wall


def build(hide=()):
    S = Scene()
    S.mat('lino', (255, 255, 255), tex=tx.hires(tx.linoleum(seed=15), 2), texmode=4, texmap=1, texscale=1.8, spec=0.6,
          shin=50, refl=0.05)
    S.mat('block', (206, 200, 182), namp=0.15, nscale=4, bump=0.08, bscale=12)
    S.mat('block_dk', (150, 146, 134), namp=0.15, nscale=4)
    S.mat('ceiling', (226, 226, 220), tex=tx.ceiling_tiles(), texmode=4, texmap=1, texscale=2.4)
    S.mat('panel_lit', (250, 252, 255), emis=(240, 248, 255), emis_mult=2.6)
    S.mat('steel', (170, 172, 178), spec=1.4, shin=60, refl=0.2)
    S.mat('frame', (60, 64, 70), spec=0.6)
    S.mat('glass', (60, 70, 74), spec=2.0, shin=150, refl=0.08)
    S.mat('sign', (220, 220, 220), tex=tx.lab_sign(), texmode=1)
    S.mat('buzzer', (30, 30, 34), spec=0.6)
    S.mat('button', (180, 20, 20), spec=1.0, shin=60)
    S.mat('door', (110, 120, 130), spec=0.5, shin=40)
    S.mat('exit', (30, 160, 70), tex=tx.sign_board('EXIT', (230, 255, 230), (20, 120, 50), 128, 48), texmode=3,
          texemis=2.0)
    S.mat('chair', (60, 90, 140), spec=0.4)
    S.mat('cork', (170, 130, 86), namp=0.3, nscale=20)
    S.mat('flyer', (236, 232, 220))
    S.mat('flyer2', (250, 220, 120))
    # the lab behind the glass
    S.mat('lab_wall', (210, 216, 214), namp=0.1, nscale=4)
    S.mat('bench', (40, 44, 48), spec=0.8, shin=60, refl=0.1)
    S.mat('mon', (20, 20, 22), spec=0.5)
    S.mat('screen1', (10, 20, 30), tex=tx.lab_monitor('graph'), texmode=3, texemis=1.4)
    S.mat('screen2', (10, 20, 30), tex=tx.lab_monitor('text'), texmode=3, texemis=1.4)
    S.mat('mug', (220, 220, 220), tex=tx.dodgers_mug(), texmode=1, spec=0.6)
    S.mat('lab_lamp', (255, 255, 250), emis=(240, 250, 255), emis_mult=2.0)
    S.mat('cabinet', (180, 186, 190), spec=0.6)
    S.mat('scope', (230, 230, 230), spec=0.8)
    S.mat('caution', (240, 200, 30), tex=tx.sign_board('CAUTION', (20, 20, 20), (240, 200, 30), 128, 128, size=26), texmode=1, spec=0.5)
    S.mat('bin', (60, 66, 70), spec=0.6)

    # ---------------------------------------------------------------- the corridor
    S.wboxr(X0, -0.3, -9, X1, 0.0, Z1, 'lino')
    S.wboxr(X0 - 0.3, 0.0, -9, X0, 3.0, Z1, 'block')
    S.wboxr(X1, 0.0, -9, X1 + 0.3, 3.0, Z1, 'block')
    S.wboxr(X0, 2.9, -9, X1, 3.2, Z1, 'ceiling')
    for z in (-1.4, 2.2):
        S.wboxr(-0.6, 2.88, z - 0.6, 0.6, 2.9, z + 0.6, 'panel_lit')
        S.light((0, 2.7, z), (236, 244, 255), power=6, range=9, soft=16)
    # the window wall, with the opening, the ledge and the tray
    wx0, wx1, wy0, wy1 = WIN
    S.wboxr(X0, 0.0, WZ - 0.25, wx0, 3.0, WZ, 'block')
    S.wboxr(wx1, 0.0, WZ - 0.25, X1, 3.0, WZ, 'block')
    S.wboxr(wx0, 0.0, WZ - 0.25, wx1, wy0, WZ, 'block')
    S.wboxr(wx0, wy1, WZ - 0.25, wx1, 3.0, WZ, 'block')
    S.wboxr(X0, 0.0, WZ, X1, 0.12, WZ + 0.03, 'block_dk')                         # a scuffed baseboard
    for (a, b, c, d) in ((wx0 - 0.06, wy0, wx0, wy1), (wx1, wy0, wx1 + 0.06, wy1), (wx0, wy1, wx1, wy1 + 0.06)):
        S.wboxr(a, b, WZ - 0.27, c, d, WZ + 0.02, 'frame')
    for x in np.arange(wx0 + 0.3, wx1, 0.5):                                  # the speaking holes' brass grille
        S.fcyl((x, wy0 + 0.6, WZ - 0.12), 0.05, 0.01, 'steel', axis='z')
    with S.tag('tray'):
        S.wboxr(wx0 - 0.1, wy0 - 0.04, WZ - 0.25, wx1 + 0.1, wy0, WZ + 0.32, 'steel')    # the ledge
        S.wboxr(-0.32, wy0, WZ - 0.12, 0.32, wy0 + 0.1, WZ + 0.3, 'steel')                # the pass-through tray
        S.wboxr(-0.28, wy0 + 0.02, WZ - 0.1, 0.28, wy0 + 0.11, WZ + 0.28, 'buzzer', op=1)
    with S.tag('sign'):
        S.wbox((wx1 + 0.75, 1.55, WZ + 0.01), (0.42, 0.21, 0.004), 'sign', rot=Rz(-2))
        S.wbox((wx1 + 0.28, 1.15, WZ + 0.02), (0.06, 0.08, 0.02), 'buzzer')
        S.sph((wx1 + 0.28, 1.15, WZ + 0.045), 0.025, 'button')
    with S.tag('exit'):
        S.wboxr(DOOR[0], 0.0, WZ + 0.0, DOOR[1], 2.1, WZ + 0.04, 'door')
        S.wboxr(DOOR[1] - 0.18, 1.0, WZ + 0.04, DOOR[1] - 0.06, 1.05, WZ + 0.1, 'steel')     # the push bar
        S.wboxr(DOOR[0] - 0.05, 2.1, WZ - 0.02, DOOR[1] + 0.05, 2.16, WZ + 0.06, 'frame')
        S.wbox(((DOOR[0] + DOOR[1]) / 2, 2.35, WZ + 0.03), (0.3, 0.11, 0.03), 'exit')
    S.light(((DOOR[0] + DOOR[1]) / 2, 2.3, WZ + 0.3), (60, 255, 120), power=0.3, range=1.5, shadow=False)
    # a plastic chair, a water fountain, a bulletin board (right)
    S.wboxr(3.2, 0.42, -1.6, 3.7, 0.46, -1.1, 'chair')
    S.wboxr(3.65, 0.46, -1.6, 3.7, 0.9, -1.1, 'chair')
    for (x, z) in ((3.25, -1.55), (3.65, -1.55), (3.25, -1.15), (3.65, -1.15)):
        S.cyl((x, 0, z), (x, 0.42, z), 0.015, 'steel')
    S.wboxr(X1 - 0.35, 0.75, 0.6, X1, 1.0, 1.1, 'steel')
    S.wboxr(X1 - 0.03, 1.3, -0.4, X1, 2.1, 1.6, 'cork')
    for (y, z, m) in ((1.8, -0.1, 'flyer'), (1.5, 0.4, 'flyer2'), (1.85, 0.9, 'flyer'), (1.5, 1.25, 'flyer')):
        S.wboxr(X1 - 0.04, y - 0.14, z - 0.1, X1 - 0.03, y + 0.14, z + 0.1, m)

    # ---------------------------------------------------------------- the lab behind the glass, and Ike
    S.wboxr(-4, 0.0, -7.0, 4, 3.0, -6.8, 'lab_wall')
    S.wboxr(-4, 2.85, -7.0, 4, 3.0, WZ - 0.25, 'lab_wall')
    S.wboxr(-2.6, 0.85, -5.0, 2.6, 0.92, -4.45, 'bench')                      # his bench, across the room
    S.wboxr(-2.5, 0.0, -4.95, -2.4, 0.85, -4.5, 'bench')
    S.wboxr(2.4, 0.0, -4.95, 2.5, 0.85, -4.5, 'bench')
    for k, (x, m) in enumerate(((-0.9, 'screen1'), (0.15, 'screen2'), (1.2, 'screen1'))):
        Mf = Frame((x, 1.25, -4.85), Ry((k - 1) * 14))
        S.box(Mf, (0, 0, 0), (0.42, 0.26, 0.03), 0.01, 'mon')
        S.box(Mf, (0, 0, 0.031), (0.39, 0.23, 0.002), 0.0, m)
        S.cyl(Mf.to((0, -0.26, 0)), Mf.to((0, -0.33, 0)), 0.03, 'mon')
    S.light((0.15, 1.3, -4.4), (140, 200, 240), power=1.6, range=3.5, soft=10, shadow=False)
    S.wboxr(-3.6, 0.0, -6.8, -2.8, 1.9, -6.2, 'cabinet')
    S.wbox((2.0, 1.05, -4.7), (0.12, 0.13, 0.12), 'scope', rnd=0.03)
    S.wboxr(-1.0, 2.82, -6.0, 1.0, 2.85, -5.4, 'lab_lamp')
    S.light((0, 2.6, -5.6), (240, 248, 255), power=3, range=7, soft=14)
    with S.tag('ike'):
        npc.cast(S, 'ike', dict(npc.SEATED, lsp=40, le=84, lin=40, rsp=34, re=96, rin=50, lean=12, hp=6, hy=8,
                                props=(('pen', 'l'),)),
                 (IKE[0], 0.32, IKE[1] + 0.6), yaw=0, scale=0.95)                         # swivelled round to the glass
        S.wboxr(IKE[0] - 0.24, 0.72, IKE[1] - 0.2, IKE[0] + 0.24, 0.78, IKE[1] + 0.2, 'mon')     # his tall stool
        S.cyl((IKE[0], 0.0, IKE[1]), (IKE[0], 0.72, IKE[1]), 0.03, 'steel')
    S.fcyl((-0.6, 1.0, -4.55), 0.05, 0.07, 'mug')

    # foreground: a wet-floor sign (left) and a trash can (right)
    if 'wetsign' not in hide:
        with S.tag('wetsign'):
            Wf = Frame((-2.3, 0, 0.75), Ry(25))
            for s_ in (-1, 1):
                S.box(Wf, (0, 0.33, s_ * 0.12), (0.17, 0.33, 0.012), 0.01, 'caution', rot=Rx(s_ * 12))
    if 'bin' not in hide:
        with S.tag('bin'):
            S.tcyl(Frame((2.7, 0.33, 0.6)), (0, 0, 0), (0.22, 0.22), (0.19, 0.19), 0.33, 'bin')
    cam = Camera((0.3, 1.8, 5.0), (0.0, 1.3, -3.0), fov=44, W=3840, H=2160)
    env = dict(sky=(20, 20, 24), bounce=(40, 40, 42), fog=0.0, reflections=True, vol_scale=0, grid=0.4, ao_scale=0.8)
    walk = [(X0 + 0.4, WZ + 0.5), (X1 - 0.6, WZ + 0.5), (X1 - 0.6, 1.1), (X0 + 0.4, 1.1)]
    meta = dict(
        room='night_lab',
        walk=walk,
        walk_zmin=WZ + 0.6, walk_zmax=1.0, scale_x=0.0,
        spawns={'drive': ((DOOR[0] + DOOR[1]) / 2, WZ + 0.9), 'start': (0.0, 1.0)},
        hotspots={
            'ike': ('Ike', (0.0, WZ + 0.75), 'up'),
            'tray': ('tray', (0.0, WZ + 0.75), 'up'),
            'sign': ('sign', (wx1 + 0.7, WZ + 0.8), 'up'),
            'exit': ('exit', ((DOOR[0] + DOOR[1]) / 2, WZ + 0.8), 'up'),
        },
        hotspot_shapes={
            'ike': [(IKE[0] - 0.45, 0.6, WZ - 0.2), (IKE[0] + 0.45, 0.6, WZ - 0.2), (IKE[0] + 0.45, 1.95, WZ - 0.2),
                    (IKE[0] - 0.45, 1.95, WZ - 0.2)],
        },
        hotspot_order=['exit', 'sign', 'ike', 'tray'],
        overlays=[],
        occluders={'wetsign': (-2.3, 0.8), 'bin': (2.7, 0.6)},
        obstacles=[(3.45, -1.35, 0.4), (-2.3, 0.75, 0.35), (2.7, 0.6, 0.3)],
        char_fill=((236, 240, 246), 0.12),
        tint=(0.95, 0.96, 1.0),
        exposure=1.1,
    )
    return S, cam, env, meta
