"""The glass house on Glendower Avenue, Los Feliz, 4:20 a.m. (Case 4, scene 4): the driveway of a mid-century glass
pavilion, still lit inside after Harlan Pryce's fundraiser for Councilmember Haskell, the whole city spread out below.

A flat-roofed glass box on a podium at the back, its right end cantilevered on steel columns over the drop, the basin's
lights beyond. Wet pavers under sagging string lights. Left foreground, three cars parked nose-in: Ray's sedan between
two white Teslas. Behind them the catering van, back doors open, a caterer carrying a chafing dish. In the middle the
Starline Valet podium with its key board (one fob left), Andre under an umbrella. Courtney Vail, headset, puffer
jacket over a cocktail dress, clipboard. On the right the gate: stone posts, a camera with a red light, the open
slide gate, the curb, and by it the easel sign ("Friends of Ted Haskell") and a box of unclaimed gift bags."""
import math, random
import numpy as np
from scene3d import *
import textures as tx
import npc
import cars

HX0, HX1, HZ0, HZ1 = -9.0, 3.4, -14.0, -8.2     # the house (glass box)
HY = 0.5                                       # its floor, on a podium
HH = 3.1                                       # its height
EDGE_X = -0.4                                  # the ground ends here on the right: the drop
ANDRE = (-1.6, -0.4)
PODIUM = (-1.0, -0.9)
KEYS = (-2.35, -1.25)
COURTNEY = (0.25, 2.0)
EASEL = (3.95, 1.35)
BAGS = (1.6, 1.4)
GATE_X = 4.7                                   # the gatepost (camera) on the right; the street beyond
CURB = (5.4, 2.8)
VAN = (-7.4, -7.2)
CARS_Z = -0.2
PLANTER = (2.6, 4.3)
TABLE = (-1.4, 4.1)


def build(hide=()):
    S = Scene()
    rng = random.Random(48)
    # ---------------------------------------------------------------- materials
    S.mat('pavers', (255, 255, 255), tex=tx.hires(tx.sidewalk(seed=12, slab=64), 2), texmode=4, texmap=1, texscale=2.0,
          refl=0.18, ripple=0.0, spec=0.6, shin=50)
    S.mat('podium', (200, 196, 186), namp=0.15, nscale=4, spec=0.3)
    S.mat('wall', (190, 186, 176), namp=0.2, nscale=3, spec=0.2)
    S.mat('steel', (34, 36, 38), spec=0.9, shin=60, refl=0.1)
    S.mat('roof', (230, 228, 222), spec=0.3)
    S.mat('glass', (20, 26, 30), spec=1.6, shin=120, refl=0.25)
    S.mat('interior', (120, 92, 66), namp=0.2, nscale=6)
    S.mat('panel', (150, 110, 70), namp=0.3, nscale=8, spec=0.3)
    S.mat('cloth', (240, 236, 226), spec=0.1)
    S.mat('chair', (230, 226, 220), spec=0.4)
    S.mat('ceiling_lit', (255, 230, 190), emis=(255, 220, 170), emis_mult=1.6)
    S.mat('piano', (14, 14, 16), spec=1.6, shin=100, refl=0.3)
    S.mat('plant', (40, 70, 40), namp=0.5, nscale=4, bump=0.4, bscale=6)
    S.mat('pot', (60, 56, 52), spec=0.3)
    S.mat('bulb', (255, 220, 160), emis=(255, 210, 140), emis_mult=4)
    S.mat('wire', (20, 20, 20))
    S.mat('basin', (0, 0, 0), tex=tx.city_basin(w=3072, h=384), texmode=3, texemis=2.4)
    S.mat('sky', (0, 0, 0), tex=tx.night_clouds(), texmode=3, texemis=0.5)
    S.mat('hill', (20, 22, 18), namp=0.5, nscale=3, bump=0.4, bscale=4)
    S.mat('stone', (150, 136, 112), namp=0.35, nscale=5, bump=0.2, bscale=10)
    S.mat('gate', (30, 30, 32), spec=0.7, shin=40)
    S.mat('cam_body', (220, 220, 224), spec=0.8, shin=50)
    S.mat('cam_led', (120, 10, 10), emis=(255, 20, 20), emis_mult=6)
    S.mat('curb', (170, 166, 156), namp=0.2, nscale=6, spec=0.3)
    S.mat('scrape', (96, 110, 126), spec=0.6, shin=40)
    S.mat('asphalt', (255, 255, 255), tex=tx.hires(tx.asphalt(seed=13), 2), texmode=4, texmap=1, texscale=3.0, refl=0.4,
          ripple=0.2, spec=0.7)
    S.mat('easel', (110, 80, 50), spec=0.3)
    S.mat('easel_sign', (220, 220, 220), tex=tx.haskell_easel(), texmode=1, spec=0.4)
    S.mat('box', (150, 116, 76), namp=0.2, nscale=10)
    S.mat('box_side', (220, 220, 220), tex=tx.giftbag_side(), texmode=1)
    S.mat('bag', (24, 34, 72), spec=0.4)
    S.mat('bag_handle', (220, 180, 90), spec=0.6)
    S.mat('podium_front', (220, 220, 220), tex=tx.starline_podium(), texmode=1, spec=0.4)
    S.mat('podium_top', (30, 30, 34), spec=0.6)
    S.mat('keyboard', (220, 220, 220), tex=tx.key_board(), texmode=1, spec=0.3)
    S.mat('lamp', (255, 236, 200), emis=(255, 230, 190), emis_mult=3)
    S.mat('van', (232, 232, 230), spec=1.0, shin=60, refl=0.2)
    S.mat('van_dark', (30, 30, 34), spec=0.4)
    S.mat('van_in', (120, 116, 108), spec=0.2)
    S.mat('agave', (80, 110, 90), spec=0.5, shin=30, namp=0.2, nscale=10)
    S.mat('chafing', (190, 192, 198), spec=1.6, shin=80, refl=0.4)

    # ---------------------------------------------------------------- ground, the drop, the city below
    S.wboxr(-30, -1.0, -20, EDGE_X, 0.0, 14, 'pavers')
    S.wboxr(EDGE_X, -1.0, 0.8, 30, 0.0, 14, 'pavers')                      # the forecourt runs on to the gate
    S.wboxr(EDGE_X - 0.05, 0.0, -20, EDGE_X + 0.25, 0.45, 0.8, 'wall')      # a low wall at the drop
    S.wboxr(EDGE_X - 0.05, 0.0, 0.6, 30, 0.45, 0.85, 'wall')
    S.wboxr(EDGE_X + 0.2, -40, -60, EDGE_X + 0.5, -1.0, 0.8, 'hill')        # the drop
    S.wboxr(-220, -70, -121, 220, 1.6, -120, 'basin')
    S.wboxr(-240, 0.5, -131, 240, 60, -130, 'sky')
    S.light((40, -30, -80), (255, 170, 100), power=120, range=140, shadow=False)          # the city's glow from below

    # ---------------------------------------------------------------- the glass house, lit inside
    with S.tag('house'):
        S.wboxr(HX0 - 0.5, 0.0, HZ0 - 0.5, EDGE_X, HY, HZ1 + 0.6, 'podium')
        S.wboxr(HX0 - 0.6, HY + HH, HZ0 - 0.8, HX1 + 0.8, HY + HH + 0.3, HZ1 + 0.9, 'roof')       # the flat roof
        S.wboxr(HX0, HY, HZ0, HX1, HY + 0.05, HZ1, 'interior')                                   # the floor
        S.wboxr(HX0, HY, HZ0 - 0.1, HX1, HY + HH, HZ0, 'panel')                                  # the back wall
        for x in np.arange(HX0, HX1 + 0.01, 1.55):                                               # steel mullions
            S.wboxr(x - 0.04, HY, HZ1 - 0.04, x + 0.04, HY + HH, HZ1 + 0.04, 'steel')
        S.wboxr(HX0, HY + HH - 0.12, HZ1 - 0.04, HX1, HY + HH, HZ1 + 0.04, 'steel')
        for x in (HX0, HX1):
            S.wboxr(x - 0.04, HY, HZ0, x + 0.04, HY + HH, HZ1, 'steel')
        S.wboxr(HX0, HY + HH - 0.02, HZ0, HX1, HY + HH, HZ1, 'ceiling_lit')
        # inside: the party's leftovers. A long table, chairs, the piano, a big plant
        S.wboxr(HX0 + 1.0, HY + 0.72, HZ0 + 1.8, HX0 + 5.0, HY + 0.78, HZ0 + 2.8, 'cloth')
        S.wboxr(HX0 + 1.05, HY, HZ0 + 1.8, HX0 + 4.95, HY + 0.72, HZ0 + 2.8, 'cloth')
        for k in range(5):
            x = HX0 + 1.4 + k * 0.85
            S.wboxr(x - 0.2, HY + 0.42, HZ0 + 3.0, x + 0.2, HY + 0.47, HZ0 + 3.4, 'chair')
            S.wboxr(x - 0.2, HY + 0.47, HZ0 + 3.35, x + 0.2, HY + 0.95, HZ0 + 3.4, 'chair', rnd=0.02)
        S.ell(WORLD, (HX0 + 7.6, HY + 0.7, HZ0 + 2.6), (1.0, 0.18, 0.7), 'piano')
        S.wboxr(HX0 + 7.0, HY, HZ0 + 2.2, HX0 + 8.2, HY + 0.65, HZ0 + 3.0, 'piano')
        S.fcyl((HX1 - 1.0, HY + 0.25, HZ1 - 1.0), 0.3, 0.25, 'pot')
        S.ell(WORLD, (HX1 - 1.0, HY + 1.2, HZ1 - 1.0), (0.6, 0.8, 0.6), 'plant', k=0.2)
    # the cantilever over the drop: steel columns down into the dark
    for x in (EDGE_X + 1.4, HX1 - 0.2):
        for z in (HZ1 + 0.4, HZ0 + 0.6):
            S.wboxr(x - 0.12, -14, z - 0.12, x + 0.12, HY, z + 0.12, 'steel')
    S.wboxr(EDGE_X, HY - 0.4, HZ0, HX1 + 0.2, HY, HZ1 + 0.5, 'podium')
    for k, x in enumerate(np.linspace(HX0 + 1.0, HX1 - 1.0, 5)):                              # the light inside
        S.light((x, HY + HH - 0.4, (HZ0 + HZ1) / 2), (255, 214, 160), power=7, range=12, soft=14)
    S.light(((HX0 + HX1) / 2, HY + 1.5, HZ1 + 2.0), (255, 210, 160), power=8, range=14, shadow=False)  # spill out

    # ---------------------------------------------------------------- string lights over the drive
    poles = [(-8.5, 3.6), (-8.5, -5.5), (5.0, 3.6), (5.0, -5.0)]
    for (x, z) in poles:
        S.cyl((x, 0, z), (x, 4.0, z), 0.05, 'steel')
    for (a, b) in ((poles[1], poles[2]), (poles[0], poles[3]), (poles[1], poles[3])):
        pts = []
        for t in np.linspace(0, 1, 22):
            x = a[0] + (b[0] - a[0]) * t; z = a[1] + (b[1] - a[1]) * t
            y = 3.9 - 0.9 * 4 * t * (1 - t)
            pts.append((x, y, z))
        for p, q in zip(pts, pts[1:]):
            S.cyl(p, q, 0.006, 'wire')
        for p in pts[1:-1:2]:
            S.sph((p[0], p[1] - 0.08, p[2]), 0.05, 'bulb')
        for t in (0.25, 0.5, 0.75):
            p = pts[int(t * 21)]
            S.light((p[0], p[1] - 0.2, p[2]), (255, 200, 140), power=2.2, range=7, soft=12, shadow=False)

    # ---------------------------------------------------------------- the gate, its camera, the curb, the street
    with S.tag('gate_camera'):
        S.wboxr(GATE_X - 0.3, 0.0, 1.8, GATE_X + 0.3, 2.1, 2.4, 'stone')
        S.wboxr(GATE_X - 0.36, 2.1, 1.74, GATE_X + 0.36, 2.2, 2.46, 'stone')
        S.wbox((GATE_X, 2.32, 2.1), (0.09, 0.08, 0.16), 'cam_body', rnd=0.03, rot=Ry(-30) @ Rx(12))
        S.sph((GATE_X - 0.08, 2.32, 2.24), 0.018, 'cam_led')
    S.light((GATE_X - 0.1, 2.35, 2.3), (255, 30, 20), power=0.06, range=0.8, shadow=False)
    S.wboxr(GATE_X + 4.2, 0.0, 1.8, GATE_X + 4.8, 2.1, 2.4, 'stone')
    for k in range(9):                                                      # the slide gate, rolled open behind the post
        x = GATE_X + 4.8 + k * 0.25
        S.cyl((x, 0.1, 2.1), (x, 1.9, 2.1), 0.02, 'gate')
    S.cyl((GATE_X + 4.8, 1.9, 2.1), (GATE_X + 7.0, 1.9, 2.1), 0.03, 'gate')
    S.light((GATE_X - 0.2, 2.6, 2.6), (255, 220, 170), power=2.0, range=6, soft=10)            # a lamp on the post
    S.sph((GATE_X, 2.5, 2.42), 0.08, 'lamp')
    with S.tag('curb'):
        S.wboxr(GATE_X - 0.4, 0.0, CURB[1] - 0.05, 14, 0.14, CURB[1] + 0.15, 'curb', rnd=0.02)
        S.wbox((CURB[0], 0.08, CURB[1] - 0.06), (0.35, 0.02, 0.006), 'scrape')
    S.wboxr(GATE_X - 0.4, -0.2, CURB[1] + 0.15, 14, 0.0, 14, 'asphalt')                       # Glendower, steep, wet

    # ---------------------------------------------------------------- the easel and the gift bags
    if 'easel' not in hide:
        with S.tag('easel'):
            ex, ez = EASEL
            E = Frame((ex, 0, ez), Ry(-32))
            for s in (-1, 1):
                S.cyl(E.to((s * 0.32, 0, 0.12)), E.to((s * 0.24, 1.75, 0.0)), 0.022, 'easel')
            S.cyl(E.to((0, 0, -0.4)), E.to((0, 1.65, 0.0)), 0.02, 'easel')
            S.box(E, (0, 1.18, 0.05), (0.38, 0.52, 0.02), 0.0, 'easel_sign', rot=Rx(-6))
            S.box(E, (0, 0.62, 0.1), (0.4, 0.02, 0.05), 0.0, 'easel')
    if 'gift_bags' not in hide:
        with S.tag('gift_bags'):
            bx, bz = BAGS
            G = Frame((bx, 0, bz), Ry(-20))
            S.box(G, (0, 0.2, 0), (0.42, 0.2, 0.28), 0.01, 'box')
            S.box(G, (0, 0.2, 0.282), (0.4, 0.18, 0.002), 0.0, 'box_side')
            for k in range(6):
                x = -0.3 + (k % 3) * 0.3; z = -0.12 + (k // 3) * 0.24
                S.box(G, (x, 0.42, z), (0.11, 0.14, 0.06), 0.005, 'bag', rot=Rz(rng.uniform(-8, 8)))
                S.cyl(G.to((x - 0.05, 0.56, z)), G.to((x, 0.64, z)), 0.006, 'bag_handle')
                S.cyl(G.to((x + 0.05, 0.56, z)), G.to((x, 0.64, z)), 0.006, 'bag_handle')
            S.box(G, (0.42, 0.21, -0.29), (0.02, 0.2, 0.01), 0.0, 'box', rot=Ry(30))           # an open flap

    # ---------------------------------------------------------------- the valet podium, the key board, Andre, Courtney
    px, pz = PODIUM
    P = Frame((px, 0, pz), Ry(-10))
    if 'podium' not in hide:
        with S.tag('podium'):
            S.box(P, (0, 0.55, 0), (0.32, 0.55, 0.25), 0.02, 'podium_top')
            S.box(P, (0, 0.55, 0.252), (0.3, 0.53, 0.002), 0.0, 'podium_front')
            S.box(P, (0, 1.12, -0.02), (0.36, 0.03, 0.29), 0.01, 'podium_top', rot=Rx(10))
            S.sph(P.to((0.2, 1.2, -0.1)), 0.05, 'lamp')
    S.light(P.to((0.2, 1.4, 0.0)), (255, 230, 190), power=0.7, range=2.5, soft=8)
    with S.tag('valet_board'):
        kx, kz = KEYS
        K = Frame((kx, 0, kz), Ry(16))
        S.cyl(K.to((-0.2, 0, 0)), K.to((-0.2, 1.6, 0)), 0.025, 'steel')
        S.cyl(K.to((0.2, 0, 0)), K.to((0.2, 1.6, 0)), 0.025, 'steel')
        S.box(K, (0, 1.3, 0.03), (0.3, 0.38, 0.015), 0.0, 'keyboard')
    if 'andre' not in hide:
        npc.cast(S, 'andre', dict(npc.STAND, props=(('umbrella', 'r'),), rsp=30, rsa=26, re=92, rin=18, lsp=6, le=20,
                                  hp=4, hy=10),
                 (ANDRE[0], 0, ANDRE[1]), yaw=14, scale=0.95, tag='andre')
    S.light((COURTNEY[0] + 0.6, 2.6, COURTNEY[1] + 1.4), (255, 220, 180), power=1.2, range=4, soft=10)   # a garden lamp
    if 'courtney' not in hide:
        npc.cast(S, 'courtney', dict(npc.STAND, props=(('clipboard', 'l'), ('phone', 'r')), lsp=34, le=92, lin=44,
                                     rsp=40, re=74, rin=12, hp=6, hy=-26, hr=4, lhp=4, rhp=-6),
                 (COURTNEY[0], 0, COURTNEY[1]), yaw=-24, scale=0.92, tag='courtney')

    # ---------------------------------------------------------------- the catering van, doors open, and a caterer
    vx, vz = VAN
    V = Frame((vx, 0, vz), Ry(-8))                            # side-on to us, rear to the right
    with S.tag('van'):
        S.box(V, (0, 1.25, 0), (2.6, 0.95, 1.0), 0.12, 'van')
        S.box(V, (0, 1.25, 0), (2.5, 0.85, 0.9), 0.05, 'van_in', op=1)
        S.box(V, (-2.3, 0.8, 0), (0.5, 0.5, 0.98), 0.15, 'van')                   # the nose
        S.box(V, (-1.9, 1.75, 0), (0.35, 0.35, 0.99), 0.05, 'van_dark')           # windshield
        S.box(V, (0.2, 1.25, 1.001), (1.8, 0.5, 0.004), 0.0, 'van_dark')          # a cargo window band
        S.box(V, (2.62, 1.25, 0), (0.03, 0.85, 0.9), 0.0, 'van_in', op=1)          # the open back
        for s in (-1, 1):                                                           # the back doors, swung wide
            S.box(V, (2.65 + 0.42, 1.25, s * 1.1), (0.42, 0.85, 0.03), 0.02, 'van', rot=Ry(s * 15))
        for wx in (-1.7, 1.7):
            for s in (-1, 1):
                wf = Frame(V.to((wx, 0.36, s * 0.92)), V.M @ Rx(90))
                S.tcyl(wf, (0, 0, 0), (0.36, 0.36), (0.36, 0.36), 0.12, 'van_dark')
        S.wboxr(vx + 1.2, 0.5, vz - 0.6, vx + 2.4, 1.2, vz + 0.6, 'chafing')      # racks of dishes inside
    S.light(V.to((2.0, 1.9, 0)), (255, 240, 220), power=1.6, range=4, soft=8)
    npc.cast(S, 'caterer', dict(npc.STAND, props=(('box', 'r'), ('box', 'l')), lsp=42, le=78, lin=10, rsp=42, re=78,
                                rin=10, lhp=18, lk=10, rhp=-16, rk=24, hp=4),
             (vx + 3.6, 0, vz + 1.6), yaw=-62, scale=0.93, tag='caterer')

    # ---------------------------------------------------------------- parked: a Tesla, Ray's car, a Tesla (left foreground)
    for i, (name, x, col, kind) in enumerate((('tesla1', -8.6, (232, 232, 234), 'sedan'),
                                              ('ray', -6.0, (34, 38, 44), 'sedan'),
                                              ('tesla2', -3.4, (226, 228, 230), 'sedan'))):
        if name in hide or (name == 'ray' and 'car' in hide):
            continue
        with S.tag(name if name != 'ray' else 'car'):
            cars.car(S, name, (x, 0, CARS_Z), 0, col, L=4.8, W=1.88, H=1.42, kind=kind, lights=False,
                     tag=name if name != 'ray' else 'car')

    # a cocktail table left over from the party, its cloth still on (left of centre, foreground)
    if 'table' not in hide:
        with S.tag('table'):
            tx0, tz0 = TABLE
            S.fcyl((tx0, 0.55, tz0), 0.3, 0.55, 'cloth')
            S.tcyl(Frame((tx0, 1.1, tz0)), (0, 0, 0), (0.33, 0.33), (0.33, 0.33), 0.015, 'cloth')
            for k in range(3):
                a = k * 2.1
                S.cone((tx0 + 0.15 * math.cos(a), 1.12, tz0 + 0.15 * math.sin(a)),
                       (tx0 + 0.15 * math.cos(a), 1.26, tz0 + 0.15 * math.sin(a)), 0.025, 0.035, 'chafing')
    # a concrete planter with an agave, right foreground
    if 'planter' not in hide:
        with S.tag('planter'):
            S.wboxr(PLANTER[0] - 0.7, 0.0, PLANTER[1] - 0.5, PLANTER[0] + 0.7, 0.6, PLANTER[1] + 0.5, 'wall', rnd=0.02)
            for k in range(16):
                a = k * 2 * math.pi / 16 + 0.2
                S.cone((PLANTER[0], 0.62, PLANTER[1]), (PLANTER[0] + 0.55 * math.cos(a), 0.9 + 0.35 * (k % 3) / 2,
                                                        PLANTER[1] + 0.38 * math.sin(a)), 0.07, 0.01, 'agave')
    S.sun((0.3, -1, -0.5), (70, 80, 120), power=0.35, shadow=False)
    S.light((0, 5, 10), (120, 130, 170), power=1.4, range=18, shadow=False)

    cam = Camera((-0.2, 2.4, 10.4), (-0.6, 1.4, -4.0), fov=46, W=3840, H=2160)
    env = dict(sky=(26, 22, 38), bounce=(16, 14, 20), fog_col=(34, 28, 40), fog=0.008, fog_h0=-20.0, fog_hf=0.02,
               fog_max=300, vol_scale=4, vol_steps=40, reflections=True, grid=0.8, ao_scale=1.2)
    walk = [(-9.2, -3.1), (-5.6, -3.1), (-5.6, -6.0), (EDGE_X - 0.4, -6.0), (EDGE_X - 0.4, 0.5),
            (GATE_X + 1.0, 1.2), (GATE_X + 1.0, 2.5), (PLANTER[0] + 0.9, 3.6), (PLANTER[0] - 0.9, 3.6),
            (PLANTER[0] - 0.9, 5.3), (-9.2, 5.3), (-9.2, 2.6), (-2.3, 2.6), (-2.3, -3.1)]
    meta = dict(
        room='glass_house',
        walk=walk,
        walk_zmin=-5.5, walk_zmax=5.2, scale_x=-1.0,
        spawns={'drive': (-4.8, 3.4), 'fletcher_bridge': (-4.8, 3.4), 'crane_garage': (-4.8, 3.4), 'start': (-1.0, 2.0)},
        hotspots={
            'courtney': ('Courtney', (COURTNEY[0] - 0.9, COURTNEY[1] + 0.5), 'right'),
            'andre': ('Andre', (ANDRE[0] + 0.5, ANDRE[1] + 1.1), 'left'),
            'valet_board': ('valet board', (KEYS[0] + 0.3, KEYS[1] + 1.0), 'up'),
            'gate_camera': ('gate camera', (GATE_X - 0.8, 1.4), 'right'),
            'curb': ('curb by the gate', (CURB[0] - 0.4, CURB[1] - 0.6), 'down'),
            'easel': ('easel sign', (EASEL[0] - 0.6, EASEL[1] + 0.8), 'right'),
            'gift_bags': ('gift bags', (BAGS[0] - 0.7, BAGS[1] + 0.4), 'right'),
            'van': ('catering van', (VAN[0] + 3.6, -5.4), 'left'),
            'house': ('the glass house', None, 'up'),
            'city': ('city view', None, 'right'),
            'car': ('my car', (-6.0, 3.2), 'up'),
        },
        hotspot_shapes={
            'courtney': [(COURTNEY[0] - 0.32, 0.0, COURTNEY[1]), (COURTNEY[0] + 0.32, 0.0, COURTNEY[1]),
                         (COURTNEY[0] + 0.32, 1.72, COURTNEY[1]), (COURTNEY[0] - 0.32, 1.72, COURTNEY[1])],
            'andre': [(ANDRE[0] - 0.32, 0.0, ANDRE[1]), (ANDRE[0] + 0.32, 0.0, ANDRE[1]), (ANDRE[0] + 0.32, 1.78, ANDRE[1]),
                      (ANDRE[0] - 0.32, 1.78, ANDRE[1])],
            'curb': [(CURB[0] - 0.7, 0.0, CURB[1] - 0.25), (CURB[0] + 0.7, 0.0, CURB[1] - 0.25),
                     (CURB[0] + 0.7, 0.2, CURB[1] + 0.2), (CURB[0] - 0.7, 0.2, CURB[1] + 0.2)],
            'house': [(HX0, 0.0, HZ1), (HX1, 0.0, HZ1), (HX1, HY + HH + 0.3, HZ1), (HX0, HY + HH + 0.3, HZ1)],
        },
        screen_shapes={'city': [(1255, 456), (1672, 456), (1672, 700), (1255, 700)]},   # the basin, right of the house
        hotspot_order=['city', 'house', 'van', 'curb', 'easel', 'gift_bags', 'gate_camera', 'valet_board', 'car', 'andre',
                       'courtney'],
        overlays=[],
        occluders={'tesla2': (-3.4, CARS_Z - 2.4), 'car': (-6.0, CARS_Z - 2.4), 'podium': (PODIUM[0], PODIUM[1] + 0.3), 'planter': (PLANTER[0], PLANTER[1] - 0.5),
                   'table': (TABLE[0], TABLE[1]), 'gift_bags': (BAGS[0], BAGS[1] + 0.3),
                   'courtney': (COURTNEY[0], COURTNEY[1] + 0.05), 'andre': (ANDRE[0], ANDRE[1] + 0.05),
                   'easel': (EASEL[0], EASEL[1] + 0.15)},
        obstacles=[(PODIUM[0], PODIUM[1], 0.45), (ANDRE[0], ANDRE[1], 0.3), (COURTNEY[0], COURTNEY[1], 0.3),
                   (KEYS[0], KEYS[1], 0.3), (EASEL[0], EASEL[1], 0.4), (BAGS[0], BAGS[1], 0.5),
                   (VAN[0] + 3.6, VAN[1] + 1.6, 0.35), (TABLE[0], TABLE[1], 0.5)],
        char_fill=((220, 205, 196), 0.18),
        tint=(0.86, 0.8, 0.76),
        exposure=1.5,
    )
    return S, cam, env, meta
