"""The Fletcher Drive bridge over the LA River, 4:00 a.m. (Case 4, scene 2), looking across the deck from the south
sidewalk toward the north rail and, beyond it, the river channel running away into Elysian Valley.

A 1927 concrete bridge: deco balustrades with pylons, tall iron lamp posts with globes (half of them out), wet asphalt
and a painted bike lane along the near curb. Officer Doss's patrol car stands mid-span with its lights turning, the
door spotlight on the road and the driver-side back door open: Preacher sits in the back behind the cage. Headlight
crumbs in the near gutter, a storm drain grate just past them. At the east end (right) the north balustrade gives way
to chain-link where the bridge meets the bank, with a gap in it, and concrete stairs go down into the channel. Ray's
car is parked at the west end (left). The near balustrade runs along the bottom of the frame, a walk-behind prop.

Overlays: Preacher in the back seat (preacher_car), the spotlight's pool on the road (beam_road, until it's swung over
the rail) and the spotlight aimed down over the rail (beam_down, after)."""
import math, random
import numpy as np
from scene3d import *
import textures as tx
import npc
import cars

ZN, ZF = 7.5, -5.6            # near and far balustrades
CURB_N, CURB_F = 3.0, -4.1    # curbs (sidewalks beyond them)
X_EAST = 7.0                  # the bridge's east end: chain-link and the bank beyond
CAR = (2.4, -2.0)             # Doss's patrol car (centre), nose to the east
RAYCAR = (-6.0, 1.95)         # Ray's car at the near curb, west end, nose to the east
DOSS = (4.75, -0.75)
BUS = (-1.8, CURB_N + 0.55)   # a Metro stop on the near sidewalk (the owl bus saw the bag)
GRATE = (4.7, CURB_N - 0.05)  # the storm drain, in the near gutter
GLASS = (3.6, CURB_N - 0.3)   # headlight crumbs in the gutter
GAP = (7.55, ZF)              # the gap in the chain-link
STAIRS = (9.6, ZF)            # top of the stairs down to the channel


def balustrade(S, x0, x1, z, pylons, lamps, lit, tag=None):
    """A deco concrete balustrade along x at depth z: base and top rails, slim balusters, pylons with lamp posts."""
    S.wboxr(x0, 0.0, z - 0.14, x1, 0.18, z + 0.14, 'rail')
    S.wboxr(x0, 0.92, z - 0.16, x1, 1.06, z + 0.16, 'rail', rnd=0.02)
    x = x0 + 0.12
    while x < x1 - 0.1:
        if all(abs(x - p) > 0.45 for p in pylons):
            S.wboxr(x - 0.045, 0.18, z - 0.07, x + 0.045, 0.92, z + 0.07, 'rail')
            S.wboxr(x - 0.06, 0.5, z - 0.08, x + 0.06, 0.58, z + 0.08, 'rail')       # a deco collar
        x += 0.24
    for i, px in enumerate(pylons):
        S.wboxr(px - 0.32, 0.0, z - 0.26, px + 0.32, 1.25, z + 0.26, 'rail', rnd=0.02)
        S.wboxr(px - 0.36, 1.25, z - 0.3, px + 0.36, 1.33, z + 0.3, 'rail', rnd=0.02)
        for k in range(3):                                                         # stepped deco fluting
            S.wboxr(px - 0.22 + k * 0.17, 0.3, z - 0.27, px - 0.17 + k * 0.17, 1.1, z + 0.27, 'rail_dk')
        if i in lamps:
            S.cyl((px, 1.33, z), (px, 4.4, z), 0.07, 'iron')
            S.cone((px, 1.33, z), (px, 1.9, z), 0.13, 0.07, 'iron')
            S.cyl((px, 4.4, z), (px, 4.6, z), 0.1, 'iron')
            on = i in lit
            S.sph((px, 4.85, z), 0.25, 'globe_on' if on else 'globe_off')
            S.cone((px, 5.08, z), (px, 5.25, z), 0.1, 0.02, 'iron')
            if on:
                S.light((px, 4.85, z + (0.4 if z < 0 else -0.4)), (255, 196, 130), power=30, range=18, soft=14, vol=0.1)


def build(hide=()):
    S = Scene()
    rng = random.Random(44)
    # ---------------------------------------------------------------- materials
    S.mat('asphalt', (255, 255, 255), tex=tx.hires(tx.asphalt(), 2), texmode=4, texmap=1, texscale=3.0, refl=0.45,
          ripple=0.0, spec=0.8, shin=60)
    S.mat('walk', (255, 255, 255), tex=tx.hires(tx.sidewalk(), 2), texmode=4, texmap=1, texscale=2.2, refl=0.25,
          ripple=0.2, spec=0.5, shin=40)
    S.mat('curb', (150, 148, 140), namp=0.2, nscale=6, refl=0.15, spec=0.4)
    S.mat('paint_w', (226, 226, 218), refl=0.3, spec=0.6)
    S.mat('lane', (60, 120, 70), tex=tx.bike_lane(), texmode=1, refl=0.35, ripple=0.2, spec=0.7, shin=50)
    S.mat('rail', (172, 166, 152), namp=0.25, nscale=4, bump=0.1, bscale=20, refl=0.05)
    S.mat('rail_dk', (140, 134, 122), namp=0.25, nscale=4)
    S.mat('iron', (36, 40, 38), spec=0.7, shin=40, refl=0.1)
    S.mat('globe_on', (255, 230, 190), emis=(255, 214, 160), emis_mult=4)
    S.mat('globe_off', (150, 150, 146), spec=1.2, shin=80, refl=0.2)
    S.mat('grate', (255, 255, 255), tex=tx.storm_grate(), texmode=1)
    S.mat('glass_bits', (230, 236, 240), spec=3.0, shin=160, emis=(60, 64, 70))
    S.mat('chain', (120, 124, 126), spec=0.9, shin=50)
    S.mat('post', (90, 92, 94), spec=0.8, shin=40)
    S.mat('bank', (255, 255, 255), tex=tx.hires(tx.channel_concrete(), 2), texmode=4, texmap=1, texscale=4.0,
          spec=0.3, refl=0.1)
    S.mat('stair', (140, 136, 126), namp=0.3, nscale=5, refl=0.1, spec=0.3)
    S.mat('bridge_side', (130, 124, 112), namp=0.3, nscale=3)
    S.mat('dirt', (40, 36, 30), namp=0.4, nscale=4)
    S.mat('weeds', (34, 44, 28), namp=0.5, nscale=6, bump=0.4, bscale=8)
    S.mat('water', (14, 18, 22), refl=0.85, ripple=0.03, spec=1.0, shin=120)
    S.mat('channel', (255, 255, 255), tex=tx.hires(tx.channel_concrete(algae=0.3), 2), texmode=4, texmap=1,
          texscale=8.0, refl=0.1)
    S.mat('pathlamp', (255, 220, 160), emis=(255, 200, 130), emis_mult=3)
    S.mat('sodium', (255, 170, 90), emis=(255, 160, 70), emis_mult=4)
    S.mat('taillight', (130, 10, 10), emis=(255, 30, 30), emis_mult=4)
    S.mat('headlite', (240, 240, 230), emis=(255, 245, 225), emis_mult=5)
    S.mat('hills', (0, 0, 0), tex=tx.night_hills(), texmode=3, texemis=1.6)
    S.mat('house', (40, 38, 44), namp=0.2, nscale=3)
    S.mat('win_lit', (60, 50, 40), emis=(255, 190, 120), emis_mult=1.2)
    S.mat('tree', (16, 22, 16), namp=0.5, nscale=3, bump=0.5, bscale=4)
    # the patrol car: black and white, the light bar turning
    S.mat('metro', (230, 230, 230), tex=tx.sign_board('M', (250, 250, 250), (200, 90, 20), 128, 160), texmode=1)
    S.mat('bench', (60, 70, 66), spec=0.6, shin=40, refl=0.1)
    S.mat('can', (54, 60, 58), spec=0.5, namp=0.2, nscale=20)
    S.mat('bar_red', (120, 10, 10), emis=(255, 30, 20), emis_mult=4)
    S.mat('bar_blue', (10, 20, 120), emis=(40, 80, 255), emis_mult=4)
    S.mat('door_white', (226, 228, 228), spec=1.3, shin=90, refl=0.3)
    S.mat('lapd', (226, 228, 228), tex=tx.sign_board('POLICE', (20, 24, 40), (0, 0, 0), 256, 64, alpha_bg=0),
          texmode=1, spec=1.2, shin=90, refl=0.3)
    S.mat('spot_lamp', (240, 240, 230), emis=(255, 250, 230), emis_mult=5)
    S.mat('spot_dark', (60, 60, 60), spec=1.0, shin=60)
    S.mat('cage', (20, 20, 22), spec=0.5)

    # ---------------------------------------------------------------- the deck
    S.wboxr(-16, -0.6, CURB_F, 13, 0.0, CURB_N, 'asphalt')
    S.wboxr(-16, -0.6, CURB_N, 13, 0.16, ZN + 0.4, 'walk')                       # sidewalks, a curb's height up
    S.wboxr(-16, -0.6, ZF - 0.3, 13, 0.16, CURB_F, 'walk')
    S.wboxr(-16, 0.0, CURB_N - 0.02, 13, 0.17, CURB_N + 0.12, 'curb', rnd=0.02)
    S.wboxr(-16, 0.0, CURB_F - 0.12, 13, 0.17, CURB_F + 0.02, 'curb', rnd=0.02)
    for x in np.arange(-15.5, 13, 3.0):                                          # the dashed centre line
        S.wboxr(x, 0.0, -0.08, x + 1.5, 0.006, 0.08, 'paint_w')
    S.wboxr(-16, 0.0, CURB_N - 1.5, 13, 0.006, CURB_N - 1.38, 'paint_w')         # the bike lane's line
    with S.tag('road'):
        S.wbox((-2.4, 0.004, CURB_N - 0.75), (0.45, 0.7, 0.002), 'lane', rot=Rx(-90))          # its stencil
        S.wbox((10.2, 0.004, CURB_N - 0.75), (0.45, 0.7, 0.002), 'lane', rot=Rx(-90))
    for (x, z, rx, rz) in ((-5.0, -1.2, 1.0, 0.3), (5.5, -2.6, 0.8, 0.25), (-1.0, 3.1, 0.9, 0.2)):
        S.ell(WORLD, (x, 0.0, z), (rx, 0.008, rz), 'water')                      # rain puddles
    # the storm drain in the near curb, and the headlight crumbs in the gutter before it
    with S.tag('storm_drain'):
        gx, gz = GRATE
        S.wbox((gx, 0.006, gz - 0.25), (0.45, 0.22, 0.004), 'grate', rot=Rx(-90))
        S.wboxr(gx - 0.5, 0.02, CURB_N - 0.02, gx + 0.5, 0.12, CURB_N + 0.03, 'grate')       # the curb opening
    with S.tag('gutter'):
        for k in range(26):
            x = GLASS[0] + rng.uniform(-0.7, 0.7); z = GLASS[1] + rng.uniform(-0.15, 0.2)
            S.wbox((x, 0.012, z), (rng.uniform(0.006, 0.018), 0.006, rng.uniform(0.006, 0.014)), 'glass_bits',
                   rot=Ry(rng.uniform(0, 180)))

    # ---------------------------------------------------------------- balustrades and lamp posts
    with S.tag('railing'):
        balustrade(S, -16, X_EAST, ZF, pylons=(-12.6, -7.8, -3.0, 1.8, 6.6), lamps=(0, 1, 2, 3, 4), lit=(0, 1, 3))
    with S.tag('lamps'):
        pass
    balustrade(S, -16, 13, ZN, pylons=(-5.4, 5.4), lamps=(), lit=())          # (behind the camera: reflections)
    # the bridge's own side, falling away beyond the far rail
    S.wboxr(-16, -9, ZF - 0.5, X_EAST, 0.0, ZF - 0.3, 'bridge_side')

    # ---------------------------------------------------------------- the east end: bank, chain-link and its gap, stairs
    S.wboxr(X_EAST, -0.6, ZF - 0.3, 13, 0.16, CURB_F, 'walk')
    S.wboxr(X_EAST + 0.1, -0.3, ZF - 3.0, 13, 0.1, ZF - 0.3, 'dirt')            # the bank's top, past the bridge
    def chainlink(x0, x1, z, h=1.8):
        for x in np.arange(x0, x1 + 0.01, 2.0):
            S.cyl((x, 0.1, z), (x, h + 0.1, z), 0.035, 'post')
        S.cyl((x0, h + 0.05, z), (x1, h + 0.05, z), 0.025, 'post')
        step = 0.16
        for t in np.arange(x0 - h, x1, step):                                   # the diamond mesh
            a0, a1 = max(x0, t), min(x1, t + h)
            if a1 > a0:
                S.cyl((a0, 0.1 + (a0 - t), z), (a1, 0.1 + (a1 - t), z), 0.006, 'chain')
                S.cyl((a0, 0.1 + h - (a0 - t), z), (a1, 0.1 + h - (a1 - t), z), 0.006, 'chain')
    with S.tag('fence_gap'):
        chainlink(X_EAST + 0.05, GAP[0] - 0.4, ZF)
        S.cyl((GAP[0] + 0.45, 0.1, ZF), (GAP[0] + 0.45, 1.9, ZF), 0.035, 'post')
        # the mesh peeled back from the gap, and a scuffed lip
        S.cyl((GAP[0] - 0.4, 0.4, ZF), (GAP[0] - 0.1, 0.9, ZF - 0.35), 0.02, 'chain')
        S.cyl((GAP[0] - 0.4, 1.2, ZF), (GAP[0] - 0.05, 1.0, ZF - 0.3), 0.02, 'chain')
    chainlink(GAP[0] + 0.45, STAIRS[0] - 0.7, ZF)
    chainlink(STAIRS[0] + 0.7, 13, ZF)
    with S.tag('stairs'):
        sx = STAIRS[0]
        for k in range(14):                                                     # concrete steps down the bank
            y = 0.12 - (k + 1) * 0.19
            z = ZF - 0.2 - k * 0.3
            S.wboxr(sx - 0.65, y - 0.4, z - 0.3, sx + 0.65, y, z, 'stair')
        for s in (-1, 1):
            S.cyl((sx + s * 0.7, 0.1, ZF), (sx + s * 0.7, 1.05, ZF), 0.03, 'post')
            S.cyl((sx + s * 0.7, 1.05, ZF), (sx + s * 0.7, 1.05 - 2.6, ZF - 4.2), 0.025, 'post')
    S.light((sx, 1.0, ZF - 1.5), (255, 190, 120), power=1.2, range=5, soft=10)
    S.wboxr(X_EAST + 0.2, -12, ZF - 30, 13, -0.3, ZF - 0.4, 'bank')  # the bank falling away

    # ---------------------------------------------------------------- beyond the rail: the channel, the valley, the hills
    S.wboxr(-60, -9.2, -200, 60, -9.0, ZF - 0.5, 'channel')
    S.wboxr(-6, -9.05, -200, 6, -8.98, ZF - 0.5, 'water')                       # the low-flow channel
    for sx in (-1, 1):
        S.wbox((sx * 32, -5.0, -100), (10, 0.3, 96), 'channel', rot=Rz(sx * 30))   # sloped banks
        for z in np.arange(-12, -190, -12):                                     # bike-path lamps along the top
            S.sph((sx * 40, -0.6, z), 0.18, 'pathlamp')
    S.light((0, -5, -30), (255, 170, 100), power=10, range=40, shadow=False)
    for (x, z, w, h) in ((-58, -60, 9, 5), (-50, -90, 8, 6), (52, -70, 10, 5), (60, -110, 9, 7), (-62, -130, 10, 6)):
        S.wboxr(x - w / 2, -3, z - 4, x + w / 2, -3 + h, z + 4, 'house')
        S.wboxr(x - 1, -1, z + 4.01, x + 1, 0.2, z + 4.05, 'win_lit')
    for (x, z, r) in ((-46, -40, 4), (-40, -75, 5), (44, -45, 4.5), (48, -95, 5), (-30, -150, 6), (34, -160, 6)):
        S.ell(WORLD, (x, -2 + r * 0.6, z), (r, r * 1.1, r), 'tree', k=0.5)
    S.wbox((0, 4, -205), (230, 26, 1), 'hills')
    # the freeway viaduct crossing the river downstream: concrete piers, a deck, sodium lamps and traffic
    VZ = -105.0
    S.wboxr(-120, 2.0, VZ - 7, 120, 3.4, VZ + 7, 'bridge_side')
    for x in np.arange(-100, 101, 25):
        S.wboxr(x - 1.2, -9.2, VZ - 4, x + 1.2, 2.0, VZ + 4, 'bridge_side')
    for x in np.arange(-110, 111, 14):
        S.cyl((x, 3.4, VZ + 6.5), (x, 7.5, VZ + 6.5), 0.15, 'iron')
        S.sph((x, 7.6, VZ + 6.3), 0.45, 'sodium')
    S.light((0, 9, VZ + 12), (255, 160, 80), power=60, range=40, shadow=False)
    for k in range(40):
        x = rng.uniform(-110, 110)
        S.wbox((x, 4.0, VZ + 7.05), (0.5, 0.12, 0.02), 'taillight' if k % 2 else 'headlite')

    # ---------------------------------------------------------------- Doss's patrol car, mid-span, and Preacher in back
    cpt = cars.car(S, 'patrol', (CAR[0], 0.0, CAR[1]), -90, (34, 34, 38), L=4.95, W=1.9, H=1.62, tag='patrol_car',
                   rear_door_open=66, door_side=1, interior=True)
    F = Frame((CAR[0], 0.0, CAR[1]), Ry(-90))
    with S.tag('patrol_car'):
        for sx in (-1, 1):                                                      # white doors
            S.box(F, (sx * 0.955, 0.6, -0.35), (0.012, 0.2, 0.62), 0.01, 'door_white')
            S.box(F, (sx * 0.962, 0.6, -0.35), (0.004, 0.08, 0.4), 0.0, 'lapd', rot=Ry(sx * 90))
        S.box(F, (0, 1.67, 0.1), (0.62, 0.05, 0.13), 0.02, 'cage')                # the light bar
        for sx in (-1, 1):
            S.box(F, (sx * 0.32, 1.7, 0.1), (0.26, 0.045, 0.11), 0.02, 'bar_red' if sx > 0 else 'bar_blue')
    S.light(cpt(0.4, 2.0, 0.1), (255, 40, 30), power=7, range=9, soft=10, vol=0.25)
    S.light(cpt(-0.4, 2.0, 0.1), (60, 100, 255), power=7, range=8, soft=10, vol=0.25)
    S.light(cpt(0, 0.6, 2.8), (255, 30, 20), power=0.6, range=3, shadow=False)          # tail glow
    S.light(cpt(0, 0.6, -3.0), (255, 245, 225), power=2.5, range=7, soft=10,           # headlights down the road
            spot=((1, -0.12, 0), 25, 45))
    # the door spotlight on the passenger's A-pillar (toward Doss)
    sp = cpt(1.02, 1.15, -0.7)
    with S.tag('spotlight'):
        S.cyl(cpt(0.95, 1.0, -0.7), sp, 0.02, 'spot_dark')
        S.cyl(sp, cpt(1.04, 1.18, -0.86), 0.09, 'spot_dark')
        S.cyl(cpt(1.04, 1.18, -0.86), cpt(1.04, 1.18, -0.875), 0.08, 'spot_lamp')
    if 'beam_road' not in hide:                                                 # aimed at the road, ahead of the car
        S.light(cpt(1.06, 1.2, -1.0), (255, 250, 235), power=22, range=14, soft=10, vol=0.2,
                spot=((1.0, -0.22, 0.3), 6, 13))
    if 'beam_down' not in hide:                                                 # swung over the rail, down at the reeds
        S.light(cpt(1.06, 1.25, -1.0), (255, 250, 235), power=14, range=22, soft=10, vol=0.3,
                spot=(nrm((-0.1, -0.55, -1.0)), 5, 10))
    S.light(cpt(0.1, 1.3, 0.75), (255, 226, 180), power=2.2, range=3.0, soft=8)        # dome light, door open
    if 'preacher_car' not in hide:
        # cuffed, hands behind him, sitting upright behind the cage, eyes closed
        npc.cast(S, 'preacher', dict(npc.SEATED, lhp=74, lk=112, rhp=76, rk=114, lean=-6, lsp=-30, lsa=14, le=58, lin=70, rsp=-30, rsa=14, re=58, rin=70,
                                     hp=4, blink=1.0, mouth=0.2),
                 cpt(0.4, 0.31, 0.95), yaw=62, scale=0.9, tag='preacher_car')
    # Officer Doss, leaning on his front fender, arms folded, very pleased
    npc.cast(S, 'doss', dict(npc.ARMS_FOLDED, lean=-7, sway=2, hp=6, hy=12, lhp=2, rhp=-10, rk=10),
             (DOSS[0], 0, DOSS[1]), yaw=-20, scale=0.96, tag='doss')

    # ---------------------------------------------------------------- a Metro bus stop on the near sidewalk
    if 'busstop' not in hide:
        with S.tag('busstop'):
            bx, bz = BUS
            S.cyl((bx, 0.16, bz), (bx, 2.9, bz), 0.04, 'post')
            S.wbox((bx, 2.6, bz), (0.2, 0.26, 0.015), 'metro')
            S.fcyl((bx - 0.7, 0.62, bz + 0.1), 0.26, 0.46, 'can')                          # a trash can
    # ---------------------------------------------------------------- Ray's car at the west end
    if 'raycar' not in hide:
        with S.tag('raycar'):
            cars.car(S, 'ray', (RAYCAR[0], 0.0, RAYCAR[1]), -90, (34, 38, 44), L=4.8, W=1.82, H=1.42, lights=False,
                     tag='car')

    S.sun((0.3, -1, -0.4), (80, 90, 130), power=0.45, shadow=False)
    S.light((0, 6, 8), (120, 130, 170), power=1.0, range=16, shadow=False)    # sky fill toward the camera side

    cam = Camera((0.0, 4.2, 9.2), (0.0, 0.6, -3.0), fov=44, W=3840, H=2160)
    env = dict(sky=(26, 22, 38), bounce=(14, 12, 18), fog_col=(30, 26, 40), fog=0.016, fog_h0=-9.0, fog_hf=0.04,
               fog_max=240, vol_scale=4, vol_steps=40, reflections=True, grid=0.8, ao_scale=1.2)
    walk = [(-11.5, ZF + 0.5), (X_EAST, ZF + 0.5), (STAIRS[0] + 0.6, ZF + 0.4), (STAIRS[0] + 0.9, -3.2),
            (X_EAST + 1.0, 1.0), (8.0, 3.5), (-11.5, 3.5)]
    meta = dict(
        room='fletcher_bridge',
        walk=walk,
        walk_zmin=ZF + 0.6, walk_zmax=3.4, scale_x=0.0,
        spawns={'drive': (RAYCAR[0] + 3.0, 0.6), 'river_channel': (STAIRS[0], ZF + 0.7), 'glass_house': (RAYCAR[0] + 3.0, 0.6),
                'crane_garage': (RAYCAR[0] + 3.0, 0.6), 'start': (-3.0, 2.0)},
        hotspots={
            'doss': ('Officer Doss', (DOSS[0] - 0.2, 0.35), 'up'),
            'patrol_car': ('patrol car', (cpt(1.75, 0, 1.2)[0], cpt(1.75, 0, 1.2)[2]), 'up'),
            'spotlight': ('spotlight', (DOSS[0] - 0.7, 0.1), 'up'),
            'road': ('road', (3.6, 1.6), 'down'),
            'gutter': ('gutter', (GLASS[0], CURB_N - 0.9), 'down'),
            'storm_drain': ('storm drain', (GRATE[0], CURB_N - 0.9), 'down'),
            'fence_gap': ('gap in the fence', (GAP[0], ZF + 0.7), 'up'),
            'railing': ('railing', (-4.8, ZF + 0.7), 'up'),
            'stairs': ('stairs', (STAIRS[0], ZF + 0.7), 'up'),
            'lamps': ('lamp posts', None, 'up'),
            'car': ('my car', (RAYCAR[0] + 3.0, 0.6), 'left'),
        },
        hotspot_shapes={
            'road': [(1.4, 0.0, -0.3), (6.8, 0.0, -0.3), (6.8, 0.0, 2.4), (1.4, 0.0, 2.4)],
            'gutter': [(GLASS[0] - 0.9, 0.0, CURB_N - 0.6), (GLASS[0] + 0.8, 0.0, CURB_N - 0.6),
                       (GLASS[0] + 0.8, 0.0, CURB_N + 0.05), (GLASS[0] - 0.9, 0.0, CURB_N + 0.05)],
            'storm_drain': [(GRATE[0] - 0.55, 0.0, CURB_N - 0.55), (GRATE[0] + 0.55, 0.0, CURB_N - 0.55),
                            (GRATE[0] + 0.55, 0.15, CURB_N + 0.05), (GRATE[0] - 0.55, 0.15, CURB_N + 0.05)],
            'railing': [(-11.5, 0.0, ZF), (-3.6, 0.0, ZF), (-3.6, 1.1, ZF), (-11.5, 1.1, ZF)],
            'fence_gap': [(GAP[0] - 0.45, 0.0, ZF), (GAP[0] + 0.45, 0.0, ZF), (GAP[0] + 0.45, 1.9, ZF),
                          (GAP[0] - 0.45, 1.9, ZF)],
            'stairs': [(STAIRS[0] - 0.7, 0.0, ZF + 0.2), (STAIRS[0] + 0.7, 0.0, ZF + 0.2), (STAIRS[0] + 0.7, 1.1, ZF),
                       (STAIRS[0] - 0.7, 1.1, ZF)],
            'lamps': [(-8.3, 1.4, ZF), (-7.3, 1.4, ZF), (-7.3, 5.3, ZF), (-8.3, 5.3, ZF)],
            'doss': [(DOSS[0] - 0.32, 0.0, DOSS[1]), (DOSS[0] + 0.32, 0.0, DOSS[1]), (DOSS[0] + 0.32, 1.8, DOSS[1]),
                     (DOSS[0] - 0.32, 1.8, DOSS[1])],
            'spotlight': [cpt(1.15, 1.0, -0.6), cpt(1.15, 1.0, -1.0), cpt(1.15, 1.35, -1.0), cpt(1.15, 1.35, -0.6)],
        },
        hotspot_order=['lamps', 'railing', 'fence_gap', 'stairs', 'road', 'gutter', 'storm_drain', 'car', 'patrol_car',
                       'spotlight', 'doss'],
        overlays=['preacher_car', 'beam_road', 'beam_down'],
        exclusive_overlays=['beam_road', 'beam_down'],
        occluders={'raycar': (RAYCAR[0], RAYCAR[1] - 0.95), 'busstop': (BUS[0], BUS[1])},
        obstacles=[(CAR[0] - 1.6, CAR[1], 1.0), (CAR[0], CAR[1], 1.0), (CAR[0] + 1.6, CAR[1], 1.0),
                   (RAYCAR[0] - 0.9, RAYCAR[1], 0.95), (RAYCAR[0] + 0.7, RAYCAR[1], 0.95), (DOSS[0], DOSS[1], 0.3),
                   (cpt(1.6, 0, 1.0)[0] + 0.1, cpt(1.6, 0, 1.0)[2] + 0.1, 0.32)],
        char_fill=((210, 200, 220), 0.18),
        tint=(0.8, 0.78, 0.86),
        exposure=1.75,
    )
    return S, cam, env, meta
