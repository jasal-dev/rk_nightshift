"""Norm's on Sunset, 2:10 a.m.: a 1950s coffee shop open around the clock. Boomerang counter with the night people on
the stools, Rosa behind it with the coffee pot, a lit pie case, orange vinyl booths along the big windows on Sunset,
Heck in the back booth with three phones, and booth 6 by the window, not yet bussed."""
import math, random
import numpy as np
from scene3d import *
import textures as tx
import npc

ROSA = (-0.6, 0.0, -3.05)
HECK = (4.45, -0.02, -3.55)


def build(hide=()):
    S = Scene()
    rng = random.Random(51)
    # ---------------------------------------------------------------- materials
    S.mat('floor', (255, 255, 255), tex=tx.hires(tx.terrazzo(), 2), texmode=4, texmap=1, texscale=2.2, spec=0.6, shin=60,
          refl=0.07)
    S.mat('wall', (200, 170, 110), namp=0.05, nscale=3)
    S.mat('wall_teal', (60, 130, 126), namp=0.05, nscale=3)
    S.mat('stone', (255, 255, 255), tex=tx.stone_wall(seed=52), texmode=4, texmap=1, texscale=1.4)
    S.mat('wood', (110, 70, 40), namp=0.15, nscale=6, spec=0.4, shin=40)
    S.mat('ceiling', (226, 214, 190))
    S.mat('fascia', (220, 120, 50), spec=0.3)
    S.mat('counter_top', (210, 200, 178), spec=0.7, shin=60, namp=0.05, nscale=40)
    S.mat('counter_face', (210, 100, 46), spec=0.4, shin=40, namp=0.05, nscale=10)
    S.mat('chrome', (180, 180, 186), spec=1.6, shin=80, refl=0.45)
    S.mat('vinyl', (214, 92, 36), spec=0.7, shin=50, namp=0.05, nscale=20)
    S.mat('vinyl_dk', (160, 64, 26), spec=0.6, shin=50)
    S.mat('formica', (170, 206, 196), spec=0.6, shin=60)
    S.mat('steel', (150, 152, 156), spec=1.0, shin=60)
    S.mat('black', (16, 16, 18), spec=0.4)
    S.mat('street', (20, 20, 30), tex=tx.hires(tx.sunset_street(), 2), texmode=3, texemis=1.4, refl=0.25, spec=1.2, shin=100)
    S.mat('frame', (60, 62, 66), spec=0.8, shin=50)
    S.mat('pies', (40, 30, 20), tex=tx.pie_case(), texmode=3, texemis=1.5)
    S.mat('glass', (30, 36, 40), spec=1.5, shin=120, refl=0.4)
    S.mat('kitchen', (90, 60, 30), emis=(255, 190, 120), emis_mult=0.55)
    S.mat('menu', (30, 26, 24), tex=tx.hires(tx.menu_board(), 2), texmode=3, texemis=1.2)
    S.mat('neon', (20, 16, 16), tex=tx.norms_sign(), texmode=3, texemis=3.0)
    S.mat('jukebox', (60, 20, 30), tex=tx.jukebox_front(), texmode=3, texemis=2.2, spec=1.0, shin=60)
    S.mat('bulb', (255, 220, 160), emis=(255, 210, 150), emis_mult=6)
    S.mat('shade', (230, 140, 50), spec=0.5, emis=(120, 60, 20))
    S.mat('cup', (236, 232, 220), spec=0.6, shin=50)
    S.mat('coffee', (40, 22, 14), spec=1.0, shin=80)
    S.mat('plate', (240, 238, 230), spec=0.6, shin=60)
    S.mat('cherry', (130, 20, 30), spec=0.8)
    S.mat('napkin', (240, 240, 236))
    S.mat('pot_glass', (60, 40, 26), spec=1.4, shin=90, refl=0.3)
    S.mat('pot_lid', (200, 100, 30), spec=0.5)
    S.mat('warmer', (200, 30, 20), emis=(255, 40, 20), emis_mult=1.5)
    S.mat('phone_scr', (10, 30, 30), emis=(90, 210, 190), emis_mult=1.4)
    S.mat('door_glass', (20, 20, 30), tex=tx.hires(tx.sunset_street(seed=87), 2), texmode=3, texemis=1.0, refl=0.3)
    S.mat('eggs', (240, 210, 90))

    X0, X1, ZB, H = -5.3, 5.8, -4.6, 3.4
    # ---------------------------------------------------------------- shell
    S.wboxr(X0 - 1, -0.3, ZB - 1, X1 + 1, 0.0, 12, 'floor')
    S.wboxr(X0 - 0.2, 0, ZB - 0.2, X1 + 0.2, H, ZB, 'wall')                       # back wall
    S.wboxr(X0 - 0.2, 0, ZB - 0.2, X1 + 0.2, 1.0, ZB + 0.02, 'stone')
    S.wboxr(X0 - 0.2, 0, ZB, X0, H, 6, 'wall_teal')                                # left wall
    S.wboxr(X0 - 0.2, 0, ZB, X0 + 0.02, 1.0, 6, 'stone')
    S.wboxr(X0 - 0.2, H, ZB - 0.2, X1 + 0.2, H + 0.2, 6, 'ceiling')
    S.wboxr(X0, H - 0.35, ZB, X1, H, ZB + 0.25, 'fascia')
    # the window wall on Sunset (right): a low sill, tall glass in chrome frames, the street outside
    S.wboxr(X1, 0, ZB, X1 + 0.2, 0.85, 6, 'stone')
    S.wboxr(X1, 3.05, ZB, X1 + 0.2, H, 6, 'wall')
    with S.tag('window'):
        S.wbox((X1 + 0.12, 1.95, 0.6), (5.2, 1.1, 0.01), 'street', rot=Ry(-90))
    for z in np.arange(-4.5, 6.0, 1.75):
        S.wboxr(X1 - 0.03, 0.85, z - 0.04, X1 + 0.05, 3.05, z + 0.04, 'frame')
    S.wboxr(X1 - 0.05, 0.82, ZB, X1 + 0.05, 0.88, 6, 'chrome')

    # ---------------------------------------------------------------- back wall: kitchen pass, menu, sign, pie case
    S.wboxr(0.2, 1.3, ZB - 0.1, 2.8, 2.15, ZB + 0.02, 'kitchen')
    S.wboxr(0.15, 1.28, ZB, 2.85, 1.33, ZB + 0.25, 'chrome')
    S.wboxr(-0.7, 2.35, ZB, 3.3, 2.9, ZB + 0.03, 'menu')
    S.wboxr(-4.6, 2.2, ZB, -2.2, 2.95, ZB + 0.04, 'neon')
    S.wboxr(X0 + 0.02, 0, ZB + 0.02, X1, 0.95, ZB + 0.75, 'counter_face')             # back counter
    S.wboxr(X0 + 0.02, 0.95, ZB + 0.02, X1, 1.0, ZB + 0.8, 'counter_top')
    with S.tag('pie_case'):
        S.wboxr(-4.3, 1.0, ZB + 0.1, -2.3, 1.9, ZB + 0.7, 'pies')
        S.wboxr(-4.35, 1.9, ZB + 0.08, -2.25, 1.96, ZB + 0.72, 'chrome')
        S.wboxr(-4.35, 1.0, ZB + 0.7, -2.25, 1.9, ZB + 0.72, 'glass')
    # cups stacked on the back counter, the second warmer with an empty pot
    for k in range(4):
        S.cyl((-1.6 + k * 0.14, 1.0, ZB + 0.5), (-1.6 + k * 0.14, 1.09, ZB + 0.5), 0.045, 'cup')

    # ---------------------------------------------------------------- the boomerang counter and its stools
    CZ = -2.2                     # front edge of the counter
    S.wboxr(-4.0, 0, CZ - 0.6, 2.8, 1.0, CZ, 'counter_face', rnd=0.02)
    S.wboxr(-4.1, 1.0, CZ - 0.65, 2.9, 1.06, CZ + 0.08, 'counter_top', rnd=0.02)
    S.wboxr(-4.0, 0.0, CZ - 0.02, 2.8, 0.12, CZ + 0.02, 'chrome')
    S.fcyl((2.9, 0.5, CZ - 0.3), 0.32, 0.5, 'counter_face')                                # the rounded end
    S.fcyl((2.9, 1.03, CZ - 0.3), 0.4, 0.03, 'counter_top')
    stools = [-3.3, -2.4, -1.5, -0.6, 0.3, 1.2, 2.1]
    for x in stools:
        S.cyl((x, 0, CZ + 0.45), (x, 0.7, CZ + 0.45), 0.035, 'chrome')
        S.fcyl((x, 0.015, CZ + 0.45), 0.2, 0.015, 'chrome')
        S.fcyl((x, 0.75, CZ + 0.45), 0.2, 0.05, 'vinyl')
    # the coffee pot on the warmer, at the end of the counter
    with S.tag('coffee_pot'):
        px, pz = 2.45, CZ - 0.25
        S.fcyl((px, 1.075, pz), 0.11, 0.015, 'warmer')
        S.cone((px, 1.09, pz), (px, 1.27, pz), 0.09, 0.05, 'pot_glass')
        S.cyl((px, 1.27, pz), (px, 1.32, pz), 0.055, 'pot_lid')
        S.cyl((px + 0.07, 1.25, pz), (px + 0.13, 1.16, pz), 0.012, 'black')
    # what's on the counter in front of the regulars
    for x in (-3.3, -2.4, -1.5, 0.3):
        S.cyl((x, 1.06, CZ - 0.25), (x, 1.15, CZ - 0.25), 0.045, 'cup')
        S.cyl((x, 1.143, CZ - 0.25), (x, 1.15, CZ - 0.25), 0.038, 'coffee')
    S.fcyl((-1.5, 1.068, CZ - 0.42), 0.13, 0.008, 'plate')
    S.ell(WORLD, (-1.52, 1.09, CZ - 0.42), (0.06, 0.02, 0.05), 'eggs')

    # ---------------------------------------------------------------- the night people at the counter (backs to us)
    with S.tag('regulars'):
        pass
    for who, x, pose in [('cabbie1', -3.3, dict(lsp=40, le=70, rsp=44, re=74, hp=6)),
                         ('nurse', -2.4, dict(lsp=50, le=80, rsp=30, re=100, rin=30, hp=-4, hy=-20)),
                         ('guard', -1.5, dict(lsp=64, le=40, rsp=64, re=40, lean=24, hp=46)),
                         ('cabbie2', 0.3, dict(lsp=36, le=62, rsp=50, re=90, rin=20, hy=24))]:
        npc.cast(S, who, dict(npc.SEATED, lhp=80, rhp=78, lk=100, rk=96, **pose), (x, 0.36, CZ + 0.5), yaw=180,
                 scale=0.96, tag='regulars')

    # ---------------------------------------------------------------- Rosa behind the counter, coffee pot in hand
    npc.cast(S, 'rosa', dict(npc.STAND, rsp=36, re=58, rin=10, rhand='hold', lsp=10, le=50, lin=30, hp=4, hy=12),
             ROSA, yaw=8, scale=0.92, tag='rosa')
    rpx, rpz = ROSA[0] - 0.32, ROSA[2] + 0.42
    S.cone((rpx, 0.86, rpz), (rpx, 1.04, rpz), 0.09, 0.05, 'pot_glass')
    S.cyl((rpx, 1.04, rpz), (rpx, 1.09, rpz), 0.055, 'pot_lid')

    # ---------------------------------------------------------------- booths along the window
    def booth(z0, tag=None):
        """A booth: two benches facing each other across a table, running in from the window."""
        tz = z0 + 0.85
        for bz, back in ((z0, -1), (z0 + 1.7, 1)):
            S.wboxr(3.75, 0.0, bz - 0.28, X1 - 0.02, 0.45, bz + 0.28, 'vinyl_dk', rnd=0.04)
            S.wboxr(3.75, 0.42, bz - 0.28, X1 - 0.02, 0.52, bz + 0.28, 'vinyl', rnd=0.05)
            S.wboxr(3.75, 0.45, bz + back * 0.2, X1 - 0.02, 1.05, bz + back * 0.32, 'vinyl', rnd=0.06)
        S.wboxr(3.95, 0.72, tz - 0.42, X1 - 0.05, 0.77, tz + 0.42, 'formica', rnd=0.02)
        S.wboxr(3.93, 0.7, tz - 0.44, X1 - 0.05, 0.72, tz + 0.44, 'chrome')
        S.cyl((4.6, 0, tz), (4.6, 0.72, tz), 0.05, 'chrome')
        return tz
    tz_heck = booth(-3.6)
    tz6 = booth(0.15)
    # Heck, three phones lined up in front of him like a poker hand
    npc.cast(S, 'heck', dict(npc.SEATED, lsp=46, le=70, lin=30, rsp=44, re=72, rin=34, hp=8, hy=-18, lean=6),
             HECK, yaw=-8, scale=0.97, tag='heck')
    for k in range(3):
        S.wbox((4.2 + k * 0.2, 0.79, tz_heck + 0.12), (0.045, 0.008, 0.08), 'phone_scr', rot=Ry(rng.uniform(-8, 8)))
    S.cyl((4.85, 0.77, tz_heck - 0.1), (4.85, 0.86, tz_heck - 0.1), 0.045, 'cup')
    # booth 6: two cup rings, a plate with a cherry smear, a napkin somebody did math on
    with S.tag('booth6'):
        S.cyl((4.3, 0.77, tz6 + 0.15), (4.3, 0.86, tz6 + 0.15), 0.045, 'cup')
        S.cyl((5.0, 0.77, tz6 - 0.2), (5.0, 0.86, tz6 - 0.2), 0.045, 'cup')
        S.fcyl((4.65, 0.778, tz6), 0.12, 0.008, 'plate')
        S.ell(WORLD, (4.68, 0.79, tz6 + 0.02), (0.05, 0.006, 0.03), 'cherry')
        S.wbox((4.4, 0.776, tz6 - 0.22), (0.08, 0.003, 0.08), 'napkin', rot=Ry(20))
    S.wboxr(5.1, 1.45, tz6 - 0.06, 5.5, 1.62, tz6 + 0.06, 'chrome')                     # booth number plate

    # ---------------------------------------------------------------- jukebox and the door (left wall)
    with S.tag('jukebox'):
        S.wbox((X0 + 0.32, 0.8, -1.3), (0.38, 0.8, 0.28), 'black', rnd=0.04)
        S.wbox((X0 + 0.61, 0.85, -1.3), (0.32, 0.72, 0.01), 'jukebox', rot=Ry(90))
        S.cyl((X0 + 0.32, 1.6, -1.68), (X0 + 0.32, 1.6, -0.92), 0.28, 'black')
    with S.tag('door'):
        S.wboxr(X0 - 0.3, 0, 0.0, X0 + 0.06, 2.4, 1.4, 'wall_teal', op=1)       # past the wainscot's face, or it skins over
        S.wboxr(X0 - 0.1, 0, 0.05, X0 - 0.04, 2.35, 1.35, 'frame')
        S.wbox((X0 - 0.02, 1.25, 0.7), (0.55, 1.0, 0.01), 'door_glass', rot=Ry(90))
        S.wboxr(X0 + 0.0, 1.0, 1.1, X0 + 0.06, 1.1, 1.25, 'chrome')

    # ---------------------------------------------------------------- ceiling lamps
    for x in (-3.0, -1.0, 1.0):
        S.cyl((x, H, CZ - 0.3), (x, 2.55, CZ - 0.3), 0.01, 'black')
        S.cone((x, 2.55, CZ - 0.3), (x, 2.3, CZ - 0.3), 0.06, 0.24, 'shade')
        S.sph((x, 2.3, CZ - 0.3), 0.06, 'bulb')
    for (x, z) in ((-3.0, 1.5), (1.0, 1.5), (4.6, -1.0)):
        S.sph((x, H - 0.1, z), 0.16, 'bulb')
        for a in range(8):
            ang = a * math.pi / 4
            S.cyl((x, H - 0.1, z), (x + 0.5 * math.cos(ang), H - 0.1, z + 0.5 * math.sin(ang)), 0.01, 'chrome')

    # ---------------------------------------------------------------- lights
    for x in (-3.0, -1.0, 1.0):
        S.light((x, 2.2, CZ - 0.3), (255, 196, 130), power=5, range=6, soft=10, vol=0.3, spot=((0, -1, 0), 50, 80))
    for (x, z) in ((-3.0, 1.5), (1.0, 1.5), (4.6, -1.0)):
        S.light((x, H - 0.3, z), (255, 226, 190), power=4.5, range=9, soft=16, vol=0.1)
    S.light((1.5, 1.7, ZB + 0.3), (255, 190, 120), power=2, range=5, shadow=False)            # kitchen pass
    S.light((-3.3, 1.4, ZB + 1.0), (255, 236, 200), power=1.4, range=3, shadow=False)        # pie case
    S.light((X0 + 0.8, 1.0, -1.3), (255, 140, 70), power=1.2, range=3, shadow=False)          # jukebox
    S.light((X1 + 2.0, 2.5, 0.0), (130, 150, 255), power=10, range=12, vol=0.2, soft=30)     # Sunset through the glass
    S.light((X1 + 2.0, 2.0, -3.0), (255, 90, 140), power=3, range=8, shadow=False)           # neon across the street
    S.light((0.0, 3.0, 7.0), (255, 220, 190), power=3, range=14, shadow=False)                # fill from the front booths

    cam = Camera((0.2, 2.5, 9.6), (0.4, 1.15, -2.2), fov=40, W=3840, H=2160)
    env = dict(sky=(40, 36, 40), bounce=(40, 30, 24), fog_col=(40, 34, 30), fog=0.02, fog_h0=0.0, fog_hf=0.05,
               fog_max=40, vol_scale=4, vol_steps=40, reflections=True, grid=0.5, ao_scale=0.9)
    meta = dict(
        room='norms_diner',
        walk=[(-4.85, -1.2), (3.55, -1.2), (3.55, 3.8), (-4.85, 3.8)],
        obstacles=[(X0, -1.75, X0 + 0.7, -0.85)],                                      # the jukebox
        walk_zmin=-1.2, walk_zmax=3.8, scale_x=0.0,
        spawns={'drive': (-4.5, 0.7), 'mulholland_overlook': (-4.5, 0.7), 'kenji_apartment': (-4.5, 0.7),
                'start': (-2.0, 1.5)},
        hotspots={
            'rosa': ('Rosa', (-0.6, -1.25), 'up'),
            'coffee_pot': ('coffee pot on the warmer', (2.35, -1.25), 'up'),
            'heck': ('Heck', (3.4, -1.15), 'right'),
            'booth6': ('booth 6', (3.4, 1.0), 'right'),
            'pie_case': ('pie case', (-3.3, -1.25), 'up'),
            'regulars': ('counter regulars', (-2.4, -1.25), 'up'),
            'jukebox': ('jukebox', (-3.95, -1.0), 'left'),
            'window': ('window', (3.4, 2.6), 'right'),
            'door': ('door', (-4.6, 0.7), 'left'),
        },
        hotspot_shapes={'rosa': [(ROSA[0] - 0.32, 0.9, ROSA[2] + 0.1), (ROSA[0] + 0.32, 0.9, ROSA[2] + 0.1),
                                 (ROSA[0] + 0.32, 1.72, ROSA[2] + 0.1), (ROSA[0] - 0.32, 1.72, ROSA[2] + 0.1)],
                        # the whole booth, benches and table: the tabletop alone is edge-on from here
                        'booth6': [(x, y, z) for x in (3.75, X1) for y in (0.0, 1.05) for z in (tz6 - 1.13, tz6 + 1.13)]},
        hotspot_order=['window', 'door', 'jukebox', 'pie_case', 'regulars', 'rosa', 'coffee_pot', 'heck', 'booth6'],
        char_fill=((255, 226, 200), 0.18),
        tint=(0.95, 0.85, 0.75),
        exposure=1.25,
    )
    return S, cam, env, meta
