"""Elliot Crane's garage, Mount Washington, 4:35 a.m. (Case 4, scene 5), seen from the back of the garage, looking out
through the rolled-up door at a street so steep the parked cars are holding on.

A fluorescent tube buzzing over a two-car garage. The blue-gray Audi stands nose-in, its face toward us: under a bright
new blue tarp (still creased in squares, a price sticker on the corner) until Crane pulls it off; then washed, the
right headlight a black hole, a shallow dent in the hood, a smear of Chomp yellow deep in the grille. A garden hose
runs across the wet floor into the drain, a bucket of suds and a sponge beside it. Along the right wall a workbench:
soaked Italian loafers on a spread of newspaper, a phone face-up, lit. A suit jacket on a hook by the door up into the
house, two steps up. Outside, rain under a streetlight, the hill across the street, houses stacked up it.

Overlays: the tarp (tarp), Crane standing by the steps in his robe with a glass of water (crane_stand), and Crane
sitting on the step (crane_step)."""
import math, random
import numpy as np
from scene3d import *
import textures as tx
import npc
import cars

GX0, GX1 = -3.4, 3.4          # the garage's side walls
GZ0, GZ1 = -6.6, 4.6          # the door opening (front) and the back wall
GH = 2.75
AUDI = (-1.3, -2.3)           # the car's centre; its nose faces us (+z)
BENCH_X = 2.75                # the workbench's front edge
BENCH_Z = (-5.2, -1.9)
DOOR_Z = (-0.4, 0.6)           # the door up into the house, in the right wall
CRANE_STAND = (1.7, 0.15)
CRANE_STEP = (2.85, 0.1)       # sitting on the upper step's edge (0.4 up), feet on the floor
DRAIN = (0.7, -1.6)
SLOPE = 6.0                   # how steeply the street climbs, left to right (degrees)
BUCKET = (1.25, -0.6)


def build(hide=()):
    S = Scene()
    rng = random.Random(49)
    # ---------------------------------------------------------------- materials
    S.mat('floor', (150, 148, 142), namp=0.25, nscale=3, refl=0.3, ripple=0.0, spec=0.7, shin=60)
    S.mat('wet', (110, 110, 112), refl=0.45, spec=1.0, shin=100)
    S.mat('wall', (200, 196, 186), namp=0.15, nscale=4, spec=0.1)
    S.mat('ceiling', (180, 176, 168), namp=0.1, nscale=4)
    S.mat('tube', (240, 250, 255), emis=(230, 245, 255), emis_mult=5)
    S.mat('fixture', (220, 220, 222), spec=0.5)
    S.mat('door_roll', (170, 170, 174), spec=0.6, shin=40, namp=0.2, nscale=12)
    S.mat('frame', (120, 116, 108))
    S.mat('bench', (120, 92, 60), namp=0.3, nscale=8, spec=0.3)
    S.mat('pegboard', (160, 130, 96), namp=0.2, nscale=20)
    S.mat('tool', (60, 62, 66), spec=1.0, shin=60)
    S.mat('tool_red', (170, 30, 26), spec=0.6, shin=40)
    S.mat('paper', (220, 220, 220), tex=tx.newspaper(), texmode=1)
    S.mat('loafer', (70, 40, 26), spec=1.0, shin=70, refl=0.15)
    S.mat('mud', (70, 74, 56), spec=0.4)
    S.mat('phone', (14, 14, 16), spec=1.2, shin=90)
    S.mat('phone_lit', (30, 40, 60), emis=(170, 200, 255), emis_mult=1.8)
    S.mat('jacket', (52, 56, 70), spec=0.1, namp=0.1, nscale=40)
    S.mat('badge', (240, 240, 236))
    S.mat('lapel', (38, 42, 54), spec=0.3)
    S.mat('name_badge', (250, 250, 246), emis=(40, 40, 40))
    S.mat('house_door', (110, 76, 50), spec=0.3, namp=0.2, nscale=10)
    S.mat('knob', (200, 170, 90), spec=1.4, shin=60)
    S.mat('step', (170, 166, 158), namp=0.2, nscale=4)
    S.mat('hose', (40, 120, 60), spec=0.6, shin=40)
    S.mat('bucket', (200, 200, 196), spec=0.6, shin=40)
    S.mat('suds', (236, 236, 240), spec=0.4, namp=0.4, nscale=40)
    S.mat('sponge', (240, 200, 60), namp=0.5, nscale=60)
    S.mat('drain', (20, 20, 22), spec=0.5)
    S.mat('tarp', (255, 255, 255), tex=tx.tarp_blue(), texmode=4, texmap=1, texscale=1.6, spec=0.9, shin=60)
    S.mat('sticker', (240, 230, 60), tex=tx.sign_board('$19.99', (20, 20, 20), (250, 220, 60), 128, 64), texmode=1)
    S.mat('yellow', (240, 196, 30), spec=0.6)
    S.mat('shelf', (90, 90, 94), spec=0.6)
    S.mat('box', (150, 116, 76), namp=0.2, nscale=10)
    S.mat('paintcan', (190, 190, 196), spec=1.0, shin=60)
    # outside
    S.mat('street', (255, 255, 255), tex=tx.hires(tx.asphalt(seed=14), 2), texmode=4, texmap=1, texscale=3.0, refl=0.45,
          ripple=0.04, spec=0.8, shin=60)
    S.mat('retain', (140, 132, 120), namp=0.3, nscale=3, spec=0.2)
    S.mat('hillside', (30, 36, 26), namp=0.5, nscale=3, bump=0.5, bscale=4)
    S.mat('house', (110, 104, 96), namp=0.2, nscale=3)
    S.mat('house2', (70, 80, 90), namp=0.2, nscale=3)
    S.mat('win_lit', (60, 50, 40), emis=(255, 196, 120), emis_mult=1.4)
    S.mat('win_dk', (16, 18, 24), spec=1.0, refl=0.3)
    S.mat('iron', (36, 40, 38), spec=0.7, shin=40)
    S.mat('sodium', (255, 180, 100), emis=(255, 170, 90), emis_mult=5)
    S.mat('car_parked', (110, 30, 30), spec=1.2, shin=80, refl=0.3)

    # ---------------------------------------------------------------- the garage
    S.wboxr(GX0 - 0.3, -0.3, GZ0, GX1 + 0.3, 0.0, GZ1 + 0.3, 'floor')
    S.wboxr(GX0 - 0.3, 0.0, GZ0, GX0, GH, GZ1 + 0.3, 'wall')                              # left wall
    S.wboxr(GX1, 0.0, GZ0, GX1 + 0.3, GH, GZ1 + 0.3, 'wall')                              # right wall
    S.wboxr(GX0 - 0.3, 0.0, GZ1, GX1 + 0.3, GH, GZ1 + 0.3, 'wall')                        # back wall (behind us)
    S.wboxr(GX0 - 0.3, GH, GZ0 - 0.3, GX1 + 0.3, GH + 0.2, GZ1 + 0.3, 'ceiling')
    S.wboxr(GX0 - 0.3, 2.3, GZ0 - 0.3, GX1 + 0.3, GH, GZ0 + 0.05, 'wall')                 # the header over the door
    S.wboxr(GX0, 2.2, GZ0 + 0.05, GX1, 2.7, GZ0 + 0.6, 'door_roll')                       # the rolled-up door
    for x in (GX0, GX1):
        S.wboxr(x - 0.06, 0.0, GZ0 - 0.04, x + 0.06, 2.3, GZ0 + 0.12, 'frame')
    # the fluorescent tube and its fixture, buzzing
    S.wboxr(-0.9, GH - 0.1, -1.3, 0.9, GH - 0.02, -1.0, 'fixture')
    S.wboxr(-0.85, GH - 0.14, -1.2, 0.85, GH - 0.1, -1.1, 'tube')
    S.light((0.0, GH - 0.3, -1.15), (226, 240, 255), power=9, range=12, soft=16)
    # shelves along the left wall: paint cans, boxes
    for y in (0.9, 1.6):
        S.wboxr(GX0, y, -5.8, GX0 + 0.45, y + 0.03, -3.6, 'shelf')
    for k in range(5):
        S.fcyl((GX0 + 0.22, 1.03, -5.5 + k * 0.4), 0.1, 0.12, 'paintcan')
    for k in range(3):
        S.wboxr(GX0 + 0.05, 1.63, -5.6 + k * 0.65, GX0 + 0.42, 1.95, -5.05 + k * 0.65, 'box')

    # ---------------------------------------------------------------- the workbench, the loafers, the phone, the jacket
    bz0, bz1 = BENCH_Z
    S.wboxr(BENCH_X, 0.86, bz0, GX1, 0.92, bz1, 'bench')
    for z in (bz0 + 0.1, bz1 - 0.1):
        S.wboxr(BENCH_X + 0.05, 0.0, z - 0.05, BENCH_X + 0.15, 0.86, z + 0.05, 'bench')
    S.wboxr(BENCH_X + 0.05, 0.25, bz0 + 0.1, GX1, 0.3, bz1 - 0.1, 'bench')               # a low shelf
    S.wboxr(GX1 - 0.02, 1.15, bz0 + 0.2, GX1, 2.1, bz1 - 0.2, 'pegboard')
    for (z, y, h) in ((-4.7, 1.8, 0.25), (-4.3, 1.75, 0.3), (-3.8, 1.85, 0.2), (-3.2, 1.7, 0.35), (-2.6, 1.8, 0.25)):
        S.wboxr(GX1 - 0.06, y - h / 2, z - 0.025, GX1 - 0.02, y + h / 2, z + 0.025, 'tool' if z != -3.8 else 'tool_red')
    with S.tag('loafers'):
        S.wbox((BENCH_X + 0.32, 0.925, -2.55), (0.26, 0.2, 0.004), 'paper', rot=Rx(-90) @ Rz(84))
        for dz in (-0.1, 0.1):
            L = Frame((BENCH_X + 0.32, 0.93, -2.55 + dz), Ry(84 + dz * 60))
            S.ell(L, (0, 0.04, 0), (0.05, 0.04, 0.14), 'loafer', k=0.01)
            S.ell(L, (0, 0.0, 0.0), (0.052, 0.012, 0.142), 'mud')
        S.sph((BENCH_X + 0.27, 0.95, -2.45), 0.015, 'suds')                               # a fluff of reed seed
    with S.tag('phone'):
        S.wbox((BENCH_X + 0.3, 0.93, -3.3), (0.04, 0.005, 0.075), 'phone', rot=Ry(20))
        S.wbox((BENCH_X + 0.3, 0.936, -3.3), (0.035, 0.001, 0.068), 'phone_lit', rot=Ry(20))
    S.light((BENCH_X + 0.3, 1.05, -3.3), (170, 200, 255), power=0.1, range=0.8, shadow=False)
    with S.tag('jacket'):
        S.cyl((GX1 - 0.02, 1.75, -1.2), (GX1 - 0.12, 1.78, -1.2), 0.012, 'tool')
        J = Frame((GX1 - 0.12, 1.75, -1.2), Ry(-90))
        for s in (-1, 1):                                                                   # the wire hanger
            S.cyl(J.to((0, 0.04, 0)), J.to((s * 0.21, -0.06, 0)), 0.006, 'tool')
        S.box(J, (0, -0.4, 0), (0.22, 0.34, 0.035), 0.03, 'jacket')                          # the body, hanging flat
        for s in (-1, 1):
            S.box(J, (s * 0.15, -0.1, 0.0), (0.09, 0.05, 0.045), 0.03, 'jacket', rot=Rz(s * 18))   # shoulders
            S.box(J, (s * 0.06, -0.26, 0.037), (0.03, 0.15, 0.004), 0.0, 'lapel', rot=Rz(s * 16))  # lapels
            S.box(J, (s * 0.2, -0.45, 0.01), (0.04, 0.28, 0.035), 0.02, 'jacket')             # sleeves hanging
        S.box(J, (0, -0.2, 0.036), (0.035, 0.09, 0.002), 0.0, 'badge')                     # the shirt in the V
        S.box(J, (-0.12, -0.2, 0.04), (0.035, 0.022, 0.003), 0.0, 'name_badge')              # the name badge

    # ---------------------------------------------------------------- the door up into the house, two steps
    with S.tag('house_door'):
        dz0, dz1 = DOOR_Z
        S.wboxr(GX1 - 0.04, 0.4, dz0, GX1, 2.45, dz1, 'house_door')
        S.sph((GX1 - 0.07, 1.4, dz0 + 0.12), 0.03, 'knob')
        S.wboxr(GX1 - 0.9, 0.0, dz0 - 0.15, GX1, 0.2, dz1 + 0.15, 'step')
        S.wboxr(GX1 - 0.5, 0.2, dz0 - 0.1, GX1, 0.4, dz1 + 0.1, 'step')
    S.light((GX1 - 0.4, 2.35, (DOOR_Z[0] + DOOR_Z[1]) / 2), (255, 220, 170), power=0.5, range=2.5, soft=8)

    # ---------------------------------------------------------------- the hose, the drain, the bucket
    with S.tag('hose'):
        dx, dz = DRAIN
        S.fcyl((dx, 0.003, dz), 0.16, 0.003, 'drain')
        pts = [(GX0 + 0.05, 0.6, 1.0), (GX0 + 0.1, 0.05, 1.0), (-1.2, 0.03, 1.2), (0.2, 0.03, 0.4), (0.4, 0.03, -0.6),
               (dx - 0.05, 0.03, dz + 0.2), (dx, 0.03, dz + 0.05)]
        for a, b in zip(pts, pts[1:]):
            S.cyl(a, b, 0.016, 'hose')
        S.wboxr(GX0, 0.55, 0.95, GX0 + 0.08, 0.68, 1.05, 'tool')                           # the spigot
        S.ell(WORLD, (dx - 0.2, 0.0, dz + 0.5), (0.5, 0.004, 1.1), 'wet')                 # the stream to the drain
        bx, bz = BUCKET
        S.tcyl(Frame((bx, 0.2, bz)), (0, 0, 0), (0.17, 0.17), (0.14, 0.14), 0.2, 'bucket')
        S.fcyl((bx, 0.38, bz), 0.155, 0.02, 'suds')
        S.wbox((bx + 0.3, 0.04, bz + 0.1), (0.07, 0.04, 0.045), 'sponge', rnd=0.015, rot=Ry(30))
    for (x, z, rx, rz) in ((-1.3, 0.4, 1.0, 0.6), (-1.2, -4.0, 1.4, 1.2), (0.3, -3.0, 0.5, 0.8)):
        S.ell(WORLD, (x, 0.0, z), (rx, 0.004, rz), 'wet')

    # ---------------------------------------------------------------- the Audi, washed, nose toward us
    apt = cars.car(S, 'audi', (AUDI[0], 0.0, AUDI[1]), 180, (98, 112, 128), L=4.95, W=1.88, H=1.45, lights=False,
                   broken='r', dent=True, tag='audi')
    with S.tag('grille'):
        F = Frame((AUDI[0], 0.0, AUDI[1]), Ry(180))
        S.box(F, (0.12, 0.6, -2.47), (0.06, 0.02, 0.004), 0.0, 'yellow')                    # Chomp yellow in the grille
        for k in range(4):                                                                  # the four rings, on the grille
            S.tcyl(Frame(F.to((-0.18 + k * 0.12, 0.68, -2.48)), Ry(180) @ Rx(90)), (0, 0, 0), (0.055, 0.055),
                   (0.055, 0.055), 0.004, 'paintcan', shell=0.008)
    with S.tag('headlight'):
        pass
    # the tarp over it all (overlay): a big blue drape, creased, its price sticker on the front corner
    if 'tarp' not in hide:
        with S.tag('tarp'):
            T = Frame((AUDI[0], 0.0, AUDI[1]), Ry(180))
            S.box(T, (0, 0.78, 0.0), (1.02, 0.66, 2.58), 0.25, 'tarp', k=0.05)
            S.box(T, (0, 1.25, 0.25), (0.86, 0.32, 1.25), 0.2, 'tarp', k=0.3)
            for k in range(6):                                                          # folds hanging at the sides
                z = -2.0 + k * 0.8
                for s in (-1, 1):
                    S.cone(T.to((s * 1.02, 1.1, z)), T.to((s * 1.1, 0.25, z + 0.1)), 0.04, 0.07, 'tarp', k=0.08)
            S.box(T, (-0.72, 0.95, -2.63), (0.12, 0.06, 0.004), 0.0, 'sticker', rot=Ry(180))

    # ---------------------------------------------------------------- Crane (overlays)
    if 'crane_stand' not in hide:
        npc.cast(S, 'crane', dict(npc.STAND, props=(('glass', 'r'),), rsp=22, re=86, rin=26, lsp=4, le=14, hp=4,
                                  hy=-18, hr=-4, lhp=6, rhp=-4),
                 (CRANE_STAND[0], 0, CRANE_STAND[1]), yaw=-62, scale=0.95, tag='crane_stand')
    if 'crane_step' not in hide:
        npc.cast(S, 'crane', dict(npc.SEATED, lhp=70, lk=100, rhp=74, rk=96, lean=22, lsp=40, le=70, lin=40, rsp=38,
                                  re=74, rin=42, hp=26, hy=-10),
                 (CRANE_STEP[0], -0.08, CRANE_STEP[1]), yaw=-90, scale=0.95, tag='crane_step')

    # ---------------------------------------------------------------- outside: the steep street, the hill, the houses
    # a level concrete apron runs out from the door; the street beyond climbs left to right, dipping just below it
    S.wboxr(GX0 - 0.3, -0.3, GZ0 - 2.6, GX1 + 0.3, 0.0, GZ0 + 0.01, 'floor')
    S.wbox((0, -0.24, GZ0 - 7.6), (40, 0.1, 5.0), 'street', rot=Rz(SLOPE))
    S.wbox((0, -0.05, GZ0 - 12.8), (40, 0.35, 0.25), 'retain', rot=Rz(SLOPE))           # the far curb and a low wall
    S.wbox((0, 3.0, GZ0 - 26.0), (40, 2.5, 4.0), 'hillside', rot=Rz(SLOPE))
    for (x, z, w, h, m) in ((-6.0, -18.5, 4.0, 3.2, 'house'), (0.5, -19.5, 4.6, 3.6, 'house2'), (6.5, -20.0, 4.2, 3.0, 'house')):
        y0 = x * math.tan(math.radians(SLOPE)) + 0.5
        S.wboxr(x - w / 2, y0, z - 3, x + w / 2, y0 + h, z, m)
        S.wboxr(x - w / 2 - 0.3, y0 + h, z - 3.3, x + w / 2 + 0.3, y0 + h + 0.2, z + 0.3, 'retain')
        for k in range(2):
            S.wboxr(x - w / 2 + 0.6 + k * (w - 1.8), y0 + 1.0, z + 0.01, x - w / 2 + 1.4 + k * (w - 1.8), y0 + 2.1, z + 0.05,
                    'win_lit' if (k + int(x)) % 2 == 0 else 'win_dk')
    S.cyl((3.8, -0.5, GZ0 - 9.5), (3.8, 6.0, GZ0 - 9.5), 0.09, 'iron')                    # the streetlight
    S.cyl((3.8, 6.0, GZ0 - 9.5), (2.6, 6.2, GZ0 - 9.5), 0.06, 'iron')
    S.wbox((2.5, 6.1, GZ0 - 9.5), (0.3, 0.08, 0.16), 'sodium')
    S.light((2.5, 5.8, GZ0 - 9.3), (255, 170, 90), power=26, range=16, soft=12, vol=0.3)
    cars.car(S, 'parked', (-2.6, -0.14 - 2.6 * math.tan(math.radians(SLOPE)), GZ0 - 9.6), -90, (110, 30, 30), L=4.4, W=1.8, H=1.42, lights=False)

    S.sun((0.3, -1, -0.5), (70, 80, 120), power=0.25, shadow=False)

    cam = Camera((0.9, 2.15, 4.2), (-0.4, 0.95, -6.0), fov=56, W=3840, H=2160)
    env = dict(sky=(22, 20, 32), bounce=(30, 30, 34), fog_col=(30, 28, 38), fog=0.02, fog_h0=0.0, fog_hf=0.05,
               fog_max=60, vol_scale=4, vol_steps=40, reflections=True, grid=0.5, ao_scale=0.9)
    walk = [(0.0, GZ0 - 0.8), (2.6, GZ0 - 0.8), (2.6, BENCH_Z[1] + 0.1), (2.2, BENCH_Z[1] + 0.3), (2.2, -0.65),
            (GX1 - 1.0, -0.65), (GX1 - 1.0, 0.95), (2.9, 0.95), (2.9, 3.0), (-2.9, 3.0), (-2.9, 0.55), (0.0, 0.55)]
    meta = dict(
        room='crane_garage',
        walk=walk,
        walk_zmin=GZ0 - 0.6, walk_zmax=2.8, scale_x=0.8,
        spawns={'drive': (1.3, GZ0 - 0.4), 'fletcher_bridge': (1.3, GZ0 - 0.4), 'glass_house': (1.3, GZ0 - 0.4),
                'start': (1.3, -1.0)},
        hotspots={
            'crane': ('Crane', (0.9, 0.6), 'right'),
            'crane_step': ('Crane', (1.4, 0.4), 'right'),
            'audi_tarp': ('car under a tarp', (0.6, 1.0), 'left'),
            'audi': ('Audi', (0.4, 0.9), 'left'),
            'headlight': ('broken headlight', (AUDI[0] - 0.6, 1.1), 'up'),
            'grille': ('grille', (AUDI[0] + 0.1, 1.1), 'up'),
            'hose': ('hose and bucket', (BUCKET[0] - 0.4, BUCKET[1] + 0.7), 'down'),
            'loafers': ('loafers', (BENCH_X - 0.45, -2.5), 'right'),
            'phone': ("Crane's phone", (BENCH_X - 0.45, -3.3), 'right'),
            'jacket': ('suit jacket', (2.0, -1.2), 'right'),
            'house_door': ('door to the house', (2.0, 1.3), 'right'),
            'street': ('street', (1.3, GZ0 - 0.6), 'up'),
        },
        hotspot_shapes={
            'crane': [(CRANE_STAND[0] - 0.3, 0.0, CRANE_STAND[1]), (CRANE_STAND[0] + 0.3, 0.0, CRANE_STAND[1]),
                      (CRANE_STAND[0] + 0.3, 1.78, CRANE_STAND[1]), (CRANE_STAND[0] - 0.3, 1.78, CRANE_STAND[1])],
            'crane_step': [(CRANE_STEP[0] - 0.45, 0.0, CRANE_STEP[1]), (CRANE_STEP[0] + 0.2, 0.0, CRANE_STEP[1]),
                           (CRANE_STEP[0] + 0.2, 1.4, CRANE_STEP[1]), (CRANE_STEP[0] - 0.45, 1.4, CRANE_STEP[1])],
            'audi_tarp': [apt(-1.0, 0.0, -2.5), apt(1.0, 0.0, -2.5), apt(1.0, 1.9, -2.5), apt(-1.0, 1.9, -2.5),
                          apt(-1.0, 1.9, 2.5), apt(1.0, 1.9, 2.5)],
            'audi': [apt(-0.95, 0.0, -2.5), apt(0.95, 0.0, -2.5), apt(0.95, 1.45, -1.0), apt(-0.95, 1.45, -1.0),
                     apt(-0.95, 1.45, 2.4), apt(0.95, 1.45, 2.4)],
            'headlight': [apt(0.3, 0.55, -2.48), apt(0.9, 0.55, -2.48), apt(0.9, 0.82, -2.48), apt(0.3, 0.82, -2.48)],
            'grille': [apt(-0.3, 0.4, -2.48), apt(0.28, 0.4, -2.48), apt(0.28, 0.72, -2.48), apt(-0.3, 0.72, -2.48)],
            'street': [(GX0, 0.0, GZ0 - 0.2), (GX1, 0.0, GZ0 - 0.2), (GX1, 2.2, GZ0 - 0.2), (GX0, 2.2, GZ0 - 0.2)],
        },
        hotspot_order=['street', 'house_door', 'jacket', 'phone', 'loafers', 'hose', 'audi_tarp', 'audi', 'grille',
                       'headlight', 'crane_step', 'crane'],
        overlays=['crane_stand', 'crane_step', 'tarp'],
        overlay_bases={'crane_stand': CRANE_STAND, 'crane_step': CRANE_STEP},
        exclusive_overlays=['crane_stand', 'crane_step'],
        obstacles=[(BUCKET[0], BUCKET[1], 0.3), (CRANE_STAND[0], CRANE_STAND[1], 0.3)],
        char_fill=((220, 226, 236), 0.16),
        tint=(0.86, 0.9, 0.95),
        exposure=1.35,
    )
    return S, cam, env, meta
