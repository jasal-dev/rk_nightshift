"""The Blue Note, the bar, 5:00 a.m. (Case 5, scenes 2 and 5). First time inside.

A long, low room seen from the street end. A mahogany bar runs down the left wall under a mirror, rows of bottles glowing
faintly, the stools turned up on the counter, all but one at the far end. Chairs up on the little round tables. At the
far end a small stage with a black baby grand, its lid down, Danny's set list taped to the music stand; his poster beside
the stage. Red leather booths along the right wall, the last one half in shadow behind a RESERVED card. Sal's work
lights over the bar, a jukebox by the front door, and behind the end of the bar the door to the back room, ajar, with
flashlight beams moving.

build(take=True) is the take (scene 5), a still for the subtitled recording (blue_note_take.py): the room dark, a candle
in the back booth with three men in it, Ray on the end of the piano bench and Danny at the keys, half there.
Overlays: the tab book on the bar (ledger) and the set list on the stand (setlist), gone once Ray takes them."""
import math, random
import numpy as np
from scene3d import *
import textures as tx
import npc

X0, X1, ZB, ZF, H = -4.2, 4.2, -6.0, 3.6, 3.2
BAR_X = (-3.0, -2.5)            # the bar counter (x), from the back of the room to the front
BAR_Z = (-3.6, 2.3)
STAGE = (-2.6, 2.0, -4.35)      # x0, x1, front edge z (it runs back to the wall)
PIANO = (-0.15, -5.2)           # the baby grand's centre; its keyboard faces left (-x)
BENCH = (-1.25, -5.05)
BOOTH = (3.4, -5.25)            # the back booth's table
DOOR_BACK = (-4.15, -3.25)      # the door to the back room (x extent), in the back wall
FRONT_DOOR = (1.7, 2.7)         # the front door (z extent), in the right wall
FG_TABLE = (-1.75, 2.85)        # a table near us, chairs up
TABLES = ((-1.4, -2.3), (0.9, -2.7), (-0.9, 0.2), (1.5, -0.2))   # the tables on the floor, chairs up (walk-behinds)
RACK_Z = -1.15                  # the drying rack on the bar, between two of the upturned stools
STOOLS_UP = (2.05, 0.4, -0.45, -1.85, -2.75)   # stools turned up on the counter, clear of the register and the rack
STOOL = (-1.95, -3.15)          # the one stool left down, at the far end
PALM = (3.55, 3.35)             # a potted palm in the corner by the door


def piano(S, hide, x, z):
    """A baby grand, its long side toward us, keyboard at the left end, lid down."""
    S.mat('ebony', (14, 14, 16), spec=1.6, shin=110, refl=0.25)
    S.mat('keys', (230, 226, 212), tex=tx.piano_keys(), texmode=1, spec=0.6, shin=60)
    S.mat('stand', (18, 18, 20), spec=1.0, shin=80)
    S.mat('set_list', (236, 232, 214), spec=0.1)
    y0 = STAGE_Y
    with S.tag('piano'):
        # the case: a straight-sided body with the curved tail at the right
        S.wboxr(x - 0.75, y0 + 0.62, z - 0.72, x + 0.35, y0 + 0.92, z + 0.72, 'ebony', rnd=0.03)
        S.fcyl((x + 0.35, y0 + 0.77, z - 0.02), 0.7, 0.15, 'ebony')
        S.wboxr(x - 0.78, y0 + 0.92, z - 0.74, x + 0.4, y0 + 0.95, z + 0.74, 'ebony', rnd=0.01)       # the lid, down
        S.fcyl((x + 0.4, y0 + 0.935, z - 0.02), 0.72, 0.015, 'ebony')
        for (lx, lz) in ((x - 0.65, z - 0.6), (x - 0.65, z + 0.6), (x + 0.75, z)):
            S.cone((lx, y0, lz), (lx, y0 + 0.64, lz), 0.05, 0.065, 'ebony')
        # the keyboard, out at the left end, and the cheek blocks
        S.wboxr(x - 1.0, y0 + 0.66, z - 0.68, x - 0.75, y0 + 0.74, z + 0.68, 'ebony')
        S.wbox((x - 0.88, y0 + 0.745, z), (0.11, 0.004, 0.62), 'keys')
        for s in (-1, 1):
            S.wboxr(x - 1.0, y0 + 0.66, z + s * 0.68 - 0.04, x - 0.75, y0 + 0.8, z + s * 0.68 + 0.04, 'ebony')
        S.cyl((x - 0.92, y0 + 0.08, z), (x - 0.92, y0 + 0.08, z + 0.15), 0.012, 'brass')          # the pedals
    with S.tag('set_list'):
        S.wbox((x - 0.7, y0 + 1.08, z), (0.015, 0.16, 0.36), 'stand', rot=Rz(-10))                     # the music stand
        if 'setlist' not in hide:
            S.wbox((x - 0.72, y0 + 1.1, z + 0.08), (0.004, 0.13, 0.1), 'set_list', rot=Rz(-10))
            for k in range(4):
                S.wbox((x - 0.725, y0 + 1.17 - k * 0.04, z + 0.08), (0.003, 0.004, 0.07), 'pen', rot=Rz(-10))
    with S.tag('bench'):
        bx, bz = BENCH
        S.wboxr(bx - 0.2, y0 + 0.46, bz - 0.45, bx + 0.2, y0 + 0.52, bz + 0.45, 'leather', rnd=0.02)
        for (lx, lz) in ((bx - 0.16, bz - 0.4), (bx + 0.16, bz - 0.4), (bx - 0.16, bz + 0.4), (bx + 0.16, bz + 0.4)):
            S.cyl((lx, y0, lz), (lx, y0 + 0.46, lz), 0.025, 'ebony')


STAGE_Y = 0.3


def build(hide=(), take=False):
    S = Scene()
    rng = random.Random(55)
    # ---------------------------------------------------------------- materials
    S.mat('floor', (255, 255, 255), tex=tx.hires(tx.floorboards(seed=88, base=(98, 64, 40)), 2), texmode=4, texmap=1,
          texscale=1.6, spec=0.5, shin=50, refl=0.1)
    S.mat('wallpaper', (255, 255, 255), tex=tx.bar_wallpaper(), texmode=4, texmap=1, texscale=1.4, namp=0.05, nscale=6)
    S.mat('wainscot', (60, 34, 22), namp=0.12, nscale=8, spec=0.4, shin=30)
    S.mat('ceiling', (34, 28, 26), namp=0.1, nscale=10)
    S.mat('mahogany', (92, 40, 24), namp=0.12, nscale=10, spec=0.9, shin=60, refl=0.08)
    S.mat('mahogany_dk', (56, 24, 16), namp=0.1, nscale=10, spec=0.6, shin=40)
    S.mat('brass', (200, 160, 72), spec=1.4, shin=70)
    S.mat('mirror', (60, 64, 66), spec=1.6, shin=120, refl=0.75)
    S.mat('shelf_glass', (50, 60, 60), spec=1.4, shin=100, refl=0.4)
    S.mat('leather', (120, 22, 26), spec=0.7, shin=40, namp=0.1, nscale=30)
    S.mat('leather_dk', (70, 14, 18), spec=0.5, shin=30)
    S.mat('table', (40, 26, 20), spec=0.9, shin=60, refl=0.05)
    S.mat('chair', (34, 24, 20), spec=0.5, shin=30)
    S.mat('stage', (40, 28, 22), spec=0.5, shin=40, namp=0.1, nscale=10)
    S.mat('curtain', (90, 16, 24), namp=0.2, nscale=14, spec=0.2, wrap=0.4)
    S.mat('poster', (220, 220, 220), tex=tx.danny_poster(), texmode=1, spec=0.3)
    S.mat('reserved', (226, 216, 190), tex=tx.reserved_card(), texmode=1)
    S.mat('jukebox', (60, 20, 30), tex=tx.jukebox_front(), texmode=3, texemis=0.9 if not take else 0.15, spec=1.0, shin=60)
    S.mat('chrome', (180, 180, 186), spec=1.6, shin=80, refl=0.4)
    S.mat('trunk', (70, 54, 36), namp=0.3, nscale=30)
    S.mat('frond', (40, 70, 36), namp=0.3, nscale=20, wrap=0.3)
    S.mat('register', (60, 62, 60), spec=1.0, shin=50)
    S.mat('ledger', (40, 80, 50), spec=0.3, namp=0.1, nscale=40)
    S.mat('paper', (226, 222, 206))
    S.mat('pen', (20, 20, 24))
    S.mat('glass_c', (170, 190, 200), spec=1.8, shin=110, refl=0.3)
    S.mat('rack', (30, 30, 32), spec=0.3)
    S.mat('door', (70, 40, 28), namp=0.12, nscale=8, spec=0.4)
    S.mat('door_glass', (40, 46, 56), emis=(70, 80, 100), emis_mult=0.8 if not take else 0.1, spec=1.0)
    S.mat('backroom', (40, 44, 50), emis=(110, 124, 150), emis_mult=1.2 if not take else 0.0)
    S.mat('shade', (130, 90, 40), spec=0.8, shin=40)
    S.mat('bulb', (255, 210, 150), emis=(255, 200, 130), emis_mult=0.0 if take else 4.0)
    S.mat('candle_glass', (180, 40, 30), emis=(255, 120, 50), emis_mult=3.0 if take else 0.0, spec=1.0)
    S.mat('flame', (255, 200, 120), emis=(255, 190, 110), emis_mult=8.0 if take else 0.0)
    for i, col in enumerate([(120, 60, 20), (40, 90, 50), (150, 120, 60), (90, 20, 26), (200, 190, 150), (60, 60, 120)]):
        S.mat(f'bottle{i}', col, spec=1.6, shin=100, refl=0.15, emis=col, emis_mult=0.05 if take else 0.35)

    # ---------------------------------------------------------------- the room
    S.wboxr(X0 - 0.3, -0.3, ZB - 0.3, X1 + 0.3, 0.0, ZF + 3, 'floor')
    S.wboxr(X0 - 0.3, 0.0, ZB - 0.3, X1 + 0.3, H, ZB, 'wallpaper')                   # back wall
    S.wboxr(X0 - 0.3, 0.0, ZB, X0, H, ZF, 'wallpaper')                              # left wall (behind the bar)
    S.wboxr(X1, 0.0, ZB, X1 + 0.3, H, ZF, 'wallpaper')                              # right wall (the booths)
    S.wboxr(X0 - 0.3, H, ZB - 0.3, X1 + 0.3, H + 0.2, ZF, 'ceiling')
    for (a, b, c, d) in ((X0, ZB, X1, ZB + 0.03), (X1 - 0.03, ZB, X1, ZF)):
        S.wboxr(a, 0.0, b, c, 1.0, d, 'wainscot')
        S.wboxr(a - 0.01, 1.0, b - 0.01, c + 0.01, 1.05, d + 0.01, 'brass')
    for x in np.arange(X0 + 0.7, X1, 1.4):                                             # ceiling beams
        S.wboxr(x - 0.08, H - 0.2, ZB, x + 0.08, H, ZF, 'mahogany_dk')

    # ---------------------------------------------------------------- the bar, the back bar, the mirror, the bottles
    bx0, bx1 = BAR_X
    bz0, bz1 = BAR_Z
    if 'bar' not in hide:
        with S.tag('bar'):                  # a walk-behind: Ray goes behind its far end on the way to the back
            S.wboxr(bx0, 0.0, bz0, bx1, 1.04, bz1, 'mahogany', rnd=0.02)
            S.wboxr(bx0 - 0.05, 1.04, bz0 - 0.05, bx1 + 0.12, 1.1, bz1 + 0.05, 'mahogany', rnd=0.025)
            S.cyl((bx1 + 0.16, 0.2, bz0), (bx1 + 0.16, 0.2, bz1), 0.025, 'brass')                   # the foot rail
            for z in np.arange(bz0 + 0.3, bz1 - 0.95, 1.15):
                S.wboxr(bx1 - 0.01, 0.12, z, bx1 + 0.01, 0.95, z + 0.9, 'mahogany_dk')            # panels, within the bar
    with S.tag('bottles'):
        S.wboxr(X0, 0.0, bz0 - 0.2, X0 + 0.45, 0.95, bz1 - 0.05, 'mahogany_dk')                # back bar cabinet
        for y in (1.35, 1.85, 2.3):
            S.wboxr(X0, y - 0.02, bz0 + 0.3, X0 + 0.28, y, bz1 - 0.3, 'shelf_glass')
            for z in np.arange(bz0 + 0.4, bz1 - 0.35, 0.16):
                if rng.random() < 0.85:
                    m = f'bottle{rng.randint(0, 5)}'
                    hb = rng.uniform(0.22, 0.32)
                    S.cyl((X0 + 0.14, y, z), (X0 + 0.14, y + hb * 0.7, z), 0.04, m)
                    S.cone((X0 + 0.14, y + hb * 0.7, z), (X0 + 0.14, y + hb, z), 0.04, 0.012, m)
    with S.tag('mirror'):
        S.wboxr(X0, 1.2, bz0 + 0.3, X0 + 0.02, 2.55, bz1 - 0.3, 'mirror')
        S.wboxr(X0, 2.55, bz0 + 0.25, X0 + 0.05, 2.62, bz1 - 0.25, 'brass')
    # the register and Sal's tab book, by the front end of the bar
    with S.tag('register'):
        rz = 1.5
        # facing the bartender (-x): the cash drawer and the sloped keys on his side, the little display for customers
        S.wbox((bx0 + 0.28, 1.2, rz), (0.17, 0.1, 0.2), 'register', rnd=0.02)
        S.wbox((bx0 + 0.09, 1.16, rz), (0.04, 0.05, 0.18), 'register', rnd=0.01)                 # cash drawer
        S.wbox((bx0 + 0.22, 1.33, rz), (0.12, 0.03, 0.18), 'register', rot=Rz(22))               # keys, sloping his way
        S.wbox((bx0 + 0.38, 1.45, rz), (0.03, 0.06, 0.12), 'register', rnd=0.01)                 # display for customers
    if 'ledger' not in hide:
        with S.tag('ledger'):
            S.wbox((bx0 + 0.32, 1.13, 1.02), (0.16, 0.025, 0.22), 'ledger', rot=Ry(8))
            S.wbox((bx0 + 0.32, 1.155, 1.02), (0.15, 0.002, 0.2), 'paper', rot=Ry(8))
    # the drying rack: every glass upside down and dry, but one still beaded
    with S.tag('rack'):
        rz = RACK_Z
        S.wboxr(bx0 + 0.05, 1.1, rz - 0.26, bx0 + 0.42, 1.12, rz + 0.26, 'rack')
        for i in range(3):
            for j in range(4):
                S.tcyl(Frame((bx0 + 0.12 + i * 0.12, 1.17, rz - 0.195 + j * 0.13)), (0, 0, 0), (0.035, 0.035),
                       (0.03, 0.03), 0.05, 'glass_c')
    # the stools: pedestal stools turned up on the counter, base in the air, except the one at the far end
    def stool(x, z, up):
        if up:
            S.fcyl((x, 1.14, z), 0.19, 0.04, 'leather')
            S.cyl((x, 1.18, z), (x, 1.82, z), 0.03, 'chrome')
            S.fcyl((x, 1.84, z), 0.2, 0.015, 'chrome')
        else:
            S.fcyl((x, 0.75, z), 0.19, 0.04, 'leather')
            S.cyl((x, 0.0, z), (x, 0.71, z), 0.03, 'chrome')
            S.fcyl((x, 0.015, z), 0.2, 0.015, 'chrome')
            S.tcyl(Frame((x, 0.3, z)), (0, 0, 0), (0.15, 0.15), (0.15, 0.15), 0.008, 'chrome', shell=0.008)
    if 'bar' not in hide:
        with S.tag('bar'):
            for z in STOOLS_UP:
                stool((bx0 + bx1) / 2 + 0.02, z, True)
    if 'stool' not in hide:
        with S.tag('stool'):
            stool(STOOL[0], STOOL[1], False)

    # Sal's work lights over the bar
    for z in (-2.8, -0.4, 1.9):
        S.cyl((bx0 + 0.1, H - 0.2, z), (bx0 + 0.1, 2.3, z), 0.008, 'pen')
        S.cone((bx0 + 0.1, 2.32, z), (bx0 + 0.1, 2.18, z), 0.03, 0.13, 'shade')
        S.sph((bx0 + 0.1, 2.18, z), 0.045, 'bulb')
        if not take:
            S.light((bx0 + 0.1, 2.08, z), (255, 196, 130), power=3.2, range=6, soft=12, vol=0.25,
                    spot=((0, -1, 0), 40, 75))
    if not take:
        S.light((X0 + 0.3, 1.6, -1.0), (255, 180, 110), power=1.3, range=4, shadow=False)          # bottle glow
        S.light((X0 + 0.3, 1.6, 1.4), (255, 180, 110), power=1.0, range=4, shadow=False)
        # the house lights the uniforms found: two warm cans over the floor, one over the stage, one over the booths
        for (x, z, pw) in ((-0.6, -1.2, 9), (0.8, 1.2, 6), (-0.4, -4.9, 5), (3.0, -1.6, 4), (3.2, -4.9, 1.2)):
            S.fcyl((x, H - 0.03, z), 0.1, 0.03, 'bulb')
            S.light((x, H - 0.15, z), (255, 196, 140), power=pw, range=9, soft=14, vol=0.2, spot=((0, -1, 0), 40, 80))

    # ---------------------------------------------------------------- the door to the back, ajar, flashlights moving
    d0, d1 = DOOR_BACK
    with S.tag('back_door'):
        S.wboxr(d0, 0.0, ZB - 0.4, d1, 2.15, ZB + 0.02, 'wallpaper', op=1)
        S.wboxr(d0 - 0.06, 0.0, ZB, d1 + 0.06, 2.22, ZB + 0.05, 'mahogany_dk')
        S.wboxr(d0, 0.0, ZB - 0.45, d1, 2.15, ZB - 0.4, 'backroom')
        S.wbox((d1 - 0.05, 1.07, ZB + 0.3), (0.03, 1.06, 0.4), 'door', rot=Ry(-12))
    if not take:
        S.light(((d0 + d1) / 2, 1.5, ZB - 0.2), (210, 225, 255), power=7, range=7, vol=0.9, volshadow=True, soft=6,
                spot=((0.3, -0.35, 1.0), 10, 26))                                       # a flashlight beam
        S.light(((d0 + d1) / 2, 1.0, ZB - 0.3), (190, 210, 255), power=2.5, range=4, vol=0.4, soft=10)
        S.light(((d0 + d1) / 2, 1.9, ZB - 0.9), (200, 215, 255), power=6, range=6, vol=0.5, soft=8)

    # ---------------------------------------------------------------- the stage, the piano, the poster
    sx0, sx1, sz = STAGE
    S.wboxr(sx0, 0.0, ZB, sx1, STAGE_Y, sz, 'stage', rnd=0.01)
    S.wboxr(sx0 + 0.2, 0.0, sz, sx0 + 1.0, 0.15, sz + 0.3, 'stage')                      # a step up
    S.wboxr(sx0, 0.5, ZB, sx1, H - 0.2, ZB + 0.08, 'curtain')                            # a curtain behind the stage
    for x in np.arange(sx0 + 0.1, sx1, 0.22):
        S.cyl((x, 0.5, ZB + 0.1), (x, H - 0.2, ZB + 0.1), 0.05, 'curtain')
    piano(S, hide, *PIANO)
    with S.tag('poster'):
        S.wboxr(2.25, 1.35, ZB + 0.01, 2.85, 2.25, ZB + 0.03, 'poster')

    # ---------------------------------------------------------------- the booths along the right wall
    def booth(z0, z1, back=False):
        for zz, s in ((z0, 1), (z1, -1)):
            S.wboxr(X1 - 1.45, 0.0, zz, X1, 0.45, zz + s * 0.5, 'leather_dk')
            S.wboxr(X1 - 1.45, 0.45, zz + s * 0.05, X1, 0.52, zz + s * 0.5, 'leather', rnd=0.03)
            S.wboxr(X1 - 1.45, 0.5, zz, X1, 1.15, zz + s * 0.14, 'leather', rnd=0.04)
            S.wboxr(X1 - 1.5, 1.13, zz - s * 0.01, X1, 1.2, zz + s * 0.16, 'mahogany_dk')
        tz = (z0 + z1) / 2                       # the table between the benches, with its lamp
        S.wboxr(X1 - 1.25, 0.72, tz - 0.36, X1 - 0.05, 0.77, tz + 0.36, 'table', rnd=0.02)
        S.cyl((X1 - 0.65, 0.0, tz), (X1 - 0.65, 0.72, tz), 0.05, 'chrome')
        S.wboxr(X1 - 0.95, 0.0, tz - 0.22, X1 - 0.35, 0.03, tz + 0.22, 'chrome')
        S.tcyl(Frame((X1 - 0.3, 0.8, tz)), (0, 0, 0), (0.035, 0.035), (0.045, 0.045), 0.04, 'candle_glass')
    with S.tag('booths'):
        booth(-4.05, -2.05)
        booth(-1.75, 0.25)
    with S.tag('back_booth'):
        # the last one, in the corner: a U of red leather round a table, the RESERVED card
        S.wboxr(X1 - 0.6, 0.0, ZB, X1, 0.45, -4.3, 'leather_dk')
        S.wboxr(X1 - 0.6, 0.45, ZB, X1, 1.35, ZB + 0.15, 'leather', rnd=0.04)
        S.wboxr(X1 - 0.18, 0.45, ZB, X1, 1.35, -4.3, 'leather', rnd=0.04)
        S.wboxr(X1 - 2.0, 0.0, ZB, X1 - 0.6, 0.45, ZB + 0.55, 'leather_dk')
        S.wboxr(X1 - 2.0, 0.45, ZB, X1 - 0.6, 1.35, ZB + 0.15, 'leather', rnd=0.04)
        S.wboxr(X1 - 2.0, 0.45, ZB + 0.05, X1 - 0.6, 0.52, ZB + 0.55, 'leather', rnd=0.03)
        S.wboxr(X1 - 0.6, 0.45, ZB + 0.05, X1 - 0.18, 0.52, -4.3, 'leather', rnd=0.03)
        bx, bz = BOOTH
        S.fcyl((bx, 0.74, bz), 0.48, 0.02, 'table')
        S.cyl((bx, 0.0, bz), (bx, 0.72, bz), 0.05, 'chrome')
        S.wbox((bx - 0.2, 0.8, bz + 0.12), (0.08, 0.045, 0.004), 'reserved', rot=Ry(30) @ Rx(-12))
        S.tcyl(Frame((bx + 0.1, 0.8, bz - 0.1)), (0, 0, 0), (0.04, 0.04), (0.045, 0.045), 0.045, 'candle_glass')
        if take:
            S.ell(WORLD, (bx + 0.1, 0.88, bz - 0.1), (0.012, 0.03, 0.012), 'flame')
            S.tcyl(Frame((bx - 0.25, 0.8, bz + 0.25)), (0, 0, 0), (0.036, 0.036), (0.03, 0.03), 0.05, 'glass_c')
            S.tcyl(Frame((bx + 0.3, 0.8, bz + 0.2)), (0, 0, 0), (0.036, 0.036), (0.03, 0.03), 0.05, 'glass_c')
            S.tcyl(Frame((bx - 0.05, 0.8, bz - 0.35)), (0, 0, 0), (0.036, 0.036), (0.03, 0.03), 0.05, 'glass_c')
            S.wbox((bx + 0.05, 0.77, bz + 0.05), (0.12, 0.03, 0.08), 'paper', rot=Ry(20))              # the envelope
    # a wall sconce over each booth, dark tonight
    for z in (-3.05, -0.75):
        S.wbox((X1 - 0.05, 1.9, z), (0.04, 0.12, 0.08), 'brass')
        S.sph((X1 - 0.12, 1.98, z), 0.06, 'shade')

    # ---------------------------------------------------------------- the floor: tables with the chairs up on them
    for n, (tx_, tz_) in enumerate(TABLES):
        if f'table{n}' in hide:
            rng.uniform(-0.3, 0.3); rng.uniform(-0.3, 0.3)               # keep the other tables' chairs where they were
            continue
        with S.tag(f'table{n}'):
            S.fcyl((tx_, 0.74, tz_), 0.42, 0.02, 'table')
            S.cyl((tx_, 0.0, tz_), (tx_, 0.72, tz_), 0.04, 'chrome')
            S.fcyl((tx_, 0.01, tz_), 0.24, 0.01, 'chrome')
            for k in range(2):                                                 # two chairs, seats down, legs up
                a = k * math.pi + rng.uniform(-0.3, 0.3)
                cx, cz = tx_ + 0.18 * math.cos(a), tz_ + 0.18 * math.sin(a)
                S.wbox((cx, 0.8, cz), (0.2, 0.025, 0.2), 'chair', rot=Ry(math.degrees(a)))
                for (lx, lz) in ((-0.16, -0.16), (0.16, -0.16), (-0.16, 0.16), (0.16, 0.16)):
                    p = np.array([cx, 0.82, cz]) + Ry(math.degrees(a)) @ np.array([lx, 0, lz])
                    S.cyl(p, p + np.array([0, 0.45, 0]), 0.016, 'chair')
                bp = np.array([cx, 0.82, cz]) + Ry(math.degrees(a)) @ np.array([0, 0, 0.19])
                S.wbox(bp + np.array([0, -0.2, 0]), (0.19, 0.18, 0.02), 'chair', rot=Ry(math.degrees(a)))

    # ---------------------------------------------------------------- foreground: a table near us, a palm by the door
    if 'fg_table' not in hide:
        with S.tag('fg_table'):
            tx_, tz_ = FG_TABLE
            S.fcyl((tx_, 0.74, tz_), 0.42, 0.02, 'table')
            S.cyl((tx_, 0.0, tz_), (tx_, 0.72, tz_), 0.04, 'chrome')
            S.fcyl((tx_, 0.01, tz_), 0.24, 0.01, 'chrome')
            for k, a in enumerate((0.4, 3.4)):
                cx, cz = tx_ + 0.18 * math.cos(a), tz_ + 0.18 * math.sin(a)
                R = Ry(math.degrees(a))
                S.wbox((cx, 0.8, cz), (0.2, 0.025, 0.2), 'chair', rot=R)
                for (lx, lz) in ((-0.16, -0.16), (0.16, -0.16), (-0.16, 0.16), (0.16, 0.16)):
                    p = np.array([cx, 0.82, cz]) + R @ np.array([lx, 0, lz])
                    S.cyl(p, p + np.array([0, 0.45, 0]), 0.016, 'chair')
                bp = np.array([cx, 0.82, cz]) + R @ np.array([0, 0, 0.19])
                S.wbox(bp + np.array([0, -0.2, 0]), (0.19, 0.18, 0.02), 'chair', rot=R)
            S.tcyl(Frame((tx_ + 0.15, 0.82, tz_ - 0.2)), (0, 0, 0), (0.07, 0.07), (0.06, 0.06), 0.02, 'glass_c')  # ashtray
    if 'palm' not in hide:
        with S.tag('palm'):
            px, pz = PALM
            S.tcyl(Frame((px, 0.28, pz)), (0, 0, 0), (0.26, 0.26), (0.2, 0.2), 0.28, 'brass')
            S.cone((px, 0.5, pz), (px + 0.05, 1.3, pz), 0.05, 0.03, 'trunk')
            for k in range(9):
                a = k / 9 * 2 * math.pi
                p1 = (px + 0.4 * math.cos(a), 1.6, pz + 0.4 * math.sin(a))
                p2 = (px + 0.8 * math.cos(a), 1.1, pz + 0.8 * math.sin(a))
                S.cone((px + 0.05, 1.3, pz), p1, 0.02, 0.09, 'frond', k=0.02)
                S.cone(p1, p2, 0.09, 0.02, 'frond', k=0.02)

    # ---------------------------------------------------------------- the front door (right wall, near us), the jukebox
    f0, f1 = FRONT_DOOR
    with S.tag('front_door'):
        S.wboxr(X1 - 0.05, 0.0, f0 - 0.08, X1 + 0.02, 2.3, f1 + 0.08, 'mahogany_dk')
        S.wboxr(X1 - 0.08, 0.0, f0, X1 - 0.02, 2.2, f1, 'door')
        S.wboxr(X1 - 0.09, 1.4, f0 + 0.2, X1 - 0.07, 1.95, f1 - 0.2, 'door_glass')
        S.sph((X1 - 0.12, 1.05, f0 + 0.12), 0.035, 'brass')
        S.wbox((X1 - 0.11, 1.5, f0 + 0.1), (0.01, 0.03, 0.05), 'brass')                  # deadbolt
        S.cyl((X1 - 0.12, 1.62, f0 + 0.08), (X1 - 0.13, 1.45, f0 + 0.2), 0.006, 'chrome')   # chain, hanging loose
    if not take:
        S.light((X1 - 0.4, 1.7, (f0 + f1) / 2), (170, 186, 220), power=1.6, range=4, soft=14, vol=0.2)  # gray dawn
    with S.tag('jukebox'):
        jz = 1.05
        S.wboxr(X1 - 0.55, 0.0, jz - 0.35, X1 - 0.05, 1.25, jz + 0.35, 'mahogany', rnd=0.03)
        S.wbox((X1 - 0.56, 0.75, jz), (0.28, 0.45, 0.005), 'jukebox', rot=Ry(-90))      # the front, facing the room
        S.fcyl((X1 - 0.3, 1.25, jz), 0.35, 0.25, 'mahogany', axis='x')            # the arched top, its lower half in the box
    if not take:
        S.light((X1 - 0.8, 0.9, 1.05), (255, 150, 90), power=0.6, range=2.5, shadow=False)

    # ---------------------------------------------------------------- the take: three men in the booth, Danny, Ray
    if take:
        bx, bz = BOOTH
        S.light((bx + 0.1, 0.98, bz - 0.1), (255, 150, 70), power=6, range=6, soft=10, vol=0.3)    # the candle
        S.light((PIANO[0] - 0.6, 3.0, PIANO[1] + 0.4), (120, 140, 210), power=7, range=6, soft=16, vol=0.6,
                spot=((0.05, -1, -0.05), 25, 55))                                     # a cold light on the piano
        S.light((X0 + 0.3, 1.6, -1.0), (255, 180, 110), power=0.25, range=4, shadow=False)
        seat = dict(npc.SEATED, lsp=40, le=70, lin=40, rsp=40, re=70, rin=40, lean=10, hp=6)
        npc.cast(S, 'shadow', dict(seat, hy=-14), (bx - 0.35, 0.06, ZB + 0.42), yaw=0, scale=1.0, tag='pryce')
        npc.cast(S, 'shadow', dict(seat, hy=20, lean=16, lsp=50, le=90), (X1 - 0.42, 0.06, bz + 0.05), yaw=-90,
                 scale=1.0, tag='haskell')
        S.wboxr(bx - 0.78, 0.42, bz + 0.45, bx - 0.38, 0.46, bz + 0.85, 'chair')                # Brenner's chair
        for (lx, lz) in ((-0.74, 0.49), (-0.42, 0.49), (-0.74, 0.81), (-0.42, 0.81)):
            S.cyl((bx + lx, 0.0, bz + lz), (bx + lx, 0.42, bz + lz), 0.015, 'chair')
        npc.cast(S, 'shadow', dict(seat, hy=10, hp=10), (bx - 0.58, 0.0, bz + 0.62), yaw=139, scale=1.08,
                 tag='brenner')
        bx2, bz2 = BENCH
        if 'danny' not in hide:
            npc.cast(S, 'danny', dict(npc.SEATED, lsp=44, le=62, lin=12, rsp=44, re=64, rin=10, lean=12, hp=10, hy=-28,
                                      lw=-20, rw=-20), (bx2, STAGE_Y - 0.05, bz2 - 0.2), yaw=90, scale=0.98, tag='danny')
        npc.place(S, 'ray', dict(npc.SEATED, lsp=20, le=56, lin=24, rsp=18, re=60, rin=26, lean=8, hp=14, hy=36),
                  (bx2, STAGE_Y - 0.05, bz2 + 0.3), yaw=80, scale=1.0, tag='ray')

    cam = Camera((0.3, 3.15, 8.2), (0.0, 0.85, -3.0), fov=46, W=3840, H=2160)
    env = dict(sky=(30, 26, 30), bounce=(46, 32, 28) if not take else (8, 6, 8), fog_col=(30, 24, 30), fog=0.02,
               fog_h0=0.0, fog_hf=0.06, fog_max=60, vol_scale=4, vol_steps=40, reflections=True, grid=0.5, ao_scale=0.9)
    walk = [(-2.25, 2.9), (-2.25, -3.8), (-3.95, -3.95), (-3.95, -5.6), (-3.3, -5.6), (-2.7, -4.45), (-2.7, -4.0),
            (2.55, -4.0), (2.55, 1.5), (3.75, 1.5), (3.75, 2.9)]
    meta = dict(
        room='blue_note_bar',
        walk=walk,
        walk_zmin=-4.2, walk_zmax=2.9, scale_x=0.0,
        spawns={'street_crime': (3.35, 2.2), 'blue_note_back': (-3.6, -5.2), 'start': (0.0, 1.5)},
        hotspots={
            'bar': ('bar', (-1.95, 0.15), 'left'),
            'register': ('register and tab book', (-1.95, 1.25), 'left'),
            'rack': ('drying rack', (-1.95, RACK_Z), 'left'),
            'mirror': ('mirror', None, 'left'),
            'bottles': ('bottles', None, 'left'),
            'front_door': ('front door', (3.4, 2.2), 'right'),
            'back_booth': ('back booth', (2.3, -3.85), 'right'),
            'booths': ('booths', (2.6, -1.5), 'right'),
            'piano': ('piano', (-1.6, -3.95), 'up'),
            'set_list': ('set list', (-1.6, -3.95), 'up'),
            'poster': ("Danny's poster", (2.3, -3.95), 'up'),
            'jukebox': ('jukebox', (3.3, 1.2), 'right'),
            'chairs': ('chairs on tables', None, 'up'),
            'stool': ('stool', (-1.45, -2.7), 'left'),
            'back_door': ('door to the back', (-3.7, -5.4), 'up'),
        },
        hotspot_shapes={
            'register': [(BAR_X[0], 1.0, 1.0 - 0.35), (BAR_X[0], 1.0, 1.75), (BAR_X[0], 1.55, 1.75), (BAR_X[0], 1.55, 0.65),
                         (BAR_X[1] + 0.1, 1.0, 1.75), (BAR_X[1] + 0.1, 1.0, 0.65)],
            'rack': [(BAR_X[0], 1.08, RACK_Z - 0.32), (BAR_X[0], 1.08, RACK_Z + 0.32), (BAR_X[1], 1.3, RACK_Z + 0.32),
                     (BAR_X[1], 1.3, RACK_Z - 0.32)],
            'chairs': [p for (x, z) in TABLES for p in ((x - 0.45, 0.0, z), (x + 0.45, 0.0, z), (x - 0.45, 1.3, z),
                                                        (x + 0.45, 1.3, z))],
        },
        hotspot_order=['mirror', 'bottles', 'bar', 'booths', 'back_booth', 'poster', 'piano', 'set_list', 'back_door',
                       'chairs', 'jukebox', 'front_door', 'stool', 'rack', 'register'],
        overlays=['ledger', 'setlist'],
        occluders=dict({'fg_table': FG_TABLE, 'palm': PALM, 'bar': ((BAR_X[0] + BAR_X[1]) / 2, BAR_Z[0]),
                        'stool': STOOL}, **{f'table{n}': t for n, t in enumerate(TABLES)}),
        obstacles=[FG_TABLE + (0.55,)] + [t + (0.55,) for t in TABLES] + [STOOL + (0.3,)],
        char_fill=((236, 214, 190), 0.22),
        tint=(0.86, 0.76, 0.7),
        exposure=1.9,
    )
    return S, cam, env, meta
