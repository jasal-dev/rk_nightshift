"""Stardust Memorabilia, Hollywood Boulevard, across from the Chinese Theatre, 3:00 a.m. (Case 3, scenes 2 and 5).

A long, narrow shop crammed floor to ceiling. The storefront is the back wall: the display window and the front door,
its glass panel smashed, with the wet Walk of Fame, a patrol car and the dark theatre forecourt beyond. Along the left
wall glass counters of props, on the right the sales counter with the brass register and the curtained doorway to the
office. In the middle the empty Oscar case on its pedestal, the certificate on an easel beside it, and Pearl in a
canvas director's chair under a patrol blanket. A wall of signed photographs in cheap gold frames.

The people are overlays the game shows or hides by flag, y-sorted with the detective (overlay_bases): Pearl in the
chair, Pearl standing for her confession, Officer Park at the door, Morty outside behind the tape."""
import math, random
import numpy as np
from scene3d import *
import textures as tx
import npc

X0, X1, ZB, H = -4.6, 4.6, -3.2, 3.4
DOOR = (-0.9, 0.3)            # front door opening (x)
WIN = (-4.2, -1.5)            # display window (x)
CASE = (1.0, -0.6)            # the Oscar case on its pedestal (x, z)
EASEL = (1.9, -0.45)          # the certificate
CHAIR = (-1.75, 0.25)         # Pearl's director's chair
PEARL_UP = (0.0, 0.95)        # where she stands for the confession
PARK = (-1.3, -2.25)          # Officer Park, just inside the door, by the window
MORTY = (-0.32, ZB - 0.95)    # outside, behind the tape
CURTAIN = (-2.3, -1.0)        # curtained doorway in the right wall (z)


def build(hide=()):
    S = Scene()
    rng = random.Random(33)
    # ---------------------------------------------------------------- materials
    S.mat('floor', (255, 255, 255), tex=tx.hires(tx.checker_floor(), 2), texmode=4, texmap=1, texscale=1.3, spec=0.5,
          shin=50, refl=0.06)
    S.mat('wall', (120, 40, 44), namp=0.08, nscale=8)                                  # oxblood paint
    S.mat('wall_lo', (40, 30, 26), spec=0.3, shin=30)                                   # dark wainscot
    S.mat('ceiling', (70, 62, 54), namp=0.1, nscale=20, spec=0.3)                     # pressed tin, smoke-dark
    S.mat('shade', (30, 70, 50), spec=1.0, shin=60)
    S.mat('trim', (176, 140, 70), spec=0.8, shin=50)                                    # gilt trim
    S.mat('wood', (96, 60, 36), namp=0.15, nscale=6, spec=0.5, shin=40)
    S.mat('wood_dk', (50, 32, 22), namp=0.1, nscale=6, spec=0.4, shin=30)
    S.mat('brass', (200, 160, 72), spec=1.4, shin=70)
    S.mat('glass_edge', (170, 200, 200), spec=1.6, shin=120, refl=0.4)
    S.mat('shelf_glass', (60, 80, 80), spec=1.4, shin=100, refl=0.5)
    S.mat('velvet', (120, 14, 22), namp=0.15, nscale=40, wrap=0.4)
    S.mat('velvet_dk', (60, 6, 12), namp=0.15, nscale=40)
    S.mat('lacquer', (16, 14, 16), spec=1.0, shin=80, refl=0.1)
    S.mat('plate', (200, 160, 72), tex=tx.brass_plate(), texmode=1, spec=1.2, shin=60)
    S.mat('certificate', (230, 220, 196), tex=tx.hires(tx.academy_certificate(), 2), texmode=1, spec=0.3)
    S.mat('gilt_frame', (170, 132, 56), spec=1.2, shin=60)
    S.mat('photo_wall', (40, 30, 26), tex=tx.hires(tx.signed_wall(), 2), texmode=1, spec=0.5, shin=60)
    S.mat('canvas', (30, 30, 34), namp=0.2, nscale=30)
    S.mat('chair_back', (30, 30, 34), tex=tx.chair_back(), texmode=1)
    S.mat('curtain', (130, 18, 28), namp=0.2, nscale=14, spec=0.2, wrap=0.4)
    S.mat('rail', (60, 60, 64), spec=0.8, shin=50)
    S.mat('jacket_purple', (90, 30, 120), spec=1.0, shin=40)
    S.mat('jacket_red', (150, 24, 30), spec=1.0, shin=40)
    S.mat('jacket_black', (20, 20, 24), spec=1.0, shin=40)
    S.mat('jacket_green', (20, 90, 60), spec=1.0, shin=40)
    S.mat('jacket_blue', (24, 50, 130), spec=1.0, shin=40)
    S.mat('hanger', (140, 140, 144), spec=0.8)
    S.mat('register', (128, 92, 40), spec=0.9, shin=50, namp=0.2, nscale=60)
    S.mat('register_dk', (60, 46, 26), spec=0.6)
    S.mat('keys', (230, 226, 210), spec=0.4)
    S.mat('falcon', (14, 14, 16), spec=1.2, shin=70)
    S.mat('tag', (236, 232, 214))
    S.mat('jewel', (230, 230, 255), spec=1.8, shin=120, refl=0.3)
    S.mat('gold', (210, 168, 60), spec=1.6, shin=80)
    S.mat('felt', (30, 50, 40), namp=0.2, nscale=30)
    S.mat('hatbox', (190, 170, 140), namp=0.1, nscale=10)
    S.mat('hatbox2', (60, 70, 110), namp=0.1, nscale=10)
    S.mat('reel', (150, 150, 156), spec=1.2, shin=60)
    S.mat('clapper', (20, 20, 22), spec=0.4)
    S.mat('clapper_w', (230, 230, 230))
    S.mat('mannequin', (200, 190, 176), spec=0.6, shin=40)
    S.mat('hat', (34, 30, 28), namp=0.2, nscale=20)
    S.mat('runner', (90, 22, 26), namp=0.35, nscale=12, spec=0.1)
    S.mat('lampshade', (230, 200, 140), emis=(170, 120, 60))
    S.mat('bulb', (255, 220, 160), emis=(255, 210, 150), emis_mult=5)
    S.mat('shard', (70, 90, 96), spec=2.0, shin=140, refl=0.6)
    S.mat('tape', (230, 196, 30), tex=tx.tape_band(), texmode=1, spec=0.3)
    for i, (title, sub, cols) in enumerate((('HARBOR LIGHTS', 'LYLE BRANDT  1954', ((30, 60, 90), (240, 210, 140))),
                                            ('NIGHT TRAIN', 'A STUDIO PICTURE', ((110, 30, 30), (250, 230, 200))),
                                            ('DESERT STAR', 'IN TECHNICOLOR', ((180, 120, 50), (40, 20, 10))),
                                            ('THE LONG GOODBYE KISS', '1957', ((20, 20, 30), (230, 60, 60))))):
        S.mat(f'poster{i}', (200, 200, 200), tex=tx.hires(tx.movie_poster(title, sub, cols, seed=i), 2), texmode=1)
    # outside
    S.mat('walk', (255, 255, 255), tex=tx.hires(tx.walk_star(), 2), texmode=4, texmap=1, texscale=1.7, refl=0.35,
          ripple=0.3, spec=0.6, shin=50)
    S.mat('curb', (130, 128, 124), namp=0.2, nscale=6, refl=0.15)
    S.mat('asphalt', (255, 255, 255), tex=tx.hires(tx.asphalt(), 2), texmode=4, texmap=1, texscale=3.0, refl=0.55,
          ripple=0.14, spec=0.5, shin=60)
    S.mat('awning', (24, 60, 44), namp=0.15, nscale=10, spec=0.3)
    S.mat('facade', (60, 52, 48), namp=0.15, nscale=4)
    S.mat('theatre', (60, 20, 18), tex=tx.hires(tx.theatre_front(), 2), texmode=3, texemis=0.9)
    S.mat('pagoda', (44, 86, 70), namp=0.2, nscale=3, spec=0.4)
    S.mat('column', (140, 30, 24), spec=0.4, shin=30)
    S.mat('car_paint', (20, 22, 26), spec=1.4, shin=90, refl=0.45)
    S.mat('car_white', (210, 210, 214), spec=1.2, shin=80, refl=0.3)
    S.mat('car_glass', (8, 10, 14), spec=1.5, shin=120, refl=0.6)
    S.mat('tire', (16, 16, 18))
    S.mat('bar_red', (255, 40, 30), emis=(255, 30, 20), emis_mult=4)
    S.mat('bar_blue', (40, 80, 255), emis=(40, 80, 255), emis_mult=4)
    S.mat('lamp_head', (50, 50, 54), spec=0.3)
    S.mat('lamp_glass', (255, 190, 120), emis=(255, 170, 90), emis_mult=6)
    S.mat('palm', (8, 8, 12))

    # ---------------------------------------------------------------- shell
    S.wboxr(X0 - 1, -0.3, ZB, X1 + 1, 0.0, 9, 'floor')
    S.wboxr(X0 - 0.2, 0, ZB - 0.18, X1 + 0.2, H, ZB, 'wall')                          # storefront wall
    S.wboxr(X0 - 0.2, 0, ZB, X0, H, 9, 'wall')                                         # left wall
    S.wboxr(X1, 0, ZB, X1 + 0.2, H, 9, 'wall')                                         # right wall
    S.wboxr(X0 - 0.2, H, ZB - 0.2, X1 + 0.2, H + 0.2, 9, 'ceiling')
    S.wboxr(X0, H - 0.12, ZB, X1, H - 0.06, ZB + 0.04, 'trim')                         # gilt cornice
    for x in (X0, X1 - 0.04):
        S.wboxr(x, H - 0.12, ZB, x + 0.04, H - 0.06, 9, 'trim')
    # cut-outs: display window, front door, curtained doorway
    S.wboxr(WIN[0], 0.75, ZB - 0.4, WIN[1], 3.0, ZB + 0.05, 'wall', op=1)
    S.wboxr(DOOR[0], 0.0, ZB - 0.4, DOOR[1], 2.45, ZB + 0.05, 'wall', op=1)
    S.wboxr(DOOR[0] + 0.05, 2.55, ZB - 0.4, DOOR[1] - 0.05, 3.0, ZB + 0.05, 'wall', op=1)    # transom
    S.wboxr(X1 - 0.1, 0.0, CURTAIN[0], X1 + 0.4, 2.3, CURTAIN[1], 'wall', op=1)
    S.wboxr(X0, 0, ZB, X1, 0.9, ZB + 0.02, 'wall_lo')                                  # wainscot, back
    S.wboxr(X0, 0.9, ZB, X1, 0.94, ZB + 0.04, 'trim')
    # window and door frames (gilt), mullions
    for (a, b, y0, y1) in ((WIN[0], WIN[1], 0.75, 3.0), (DOOR[0], DOOR[1], 0.0, 2.45)):
        S.wboxr(a - 0.06, y0, ZB - 0.06, a, y1 + 0.06, ZB + 0.06, 'trim')
        S.wboxr(b, y0, ZB - 0.06, b + 0.06, y1 + 0.06, ZB + 0.06, 'trim')
        S.wboxr(a - 0.06, y1, ZB - 0.06, b + 0.06, y1 + 0.06, ZB + 0.06, 'trim')
    S.wboxr(DOOR[0], 2.45, ZB - 0.06, DOOR[1], 2.55, ZB + 0.06, 'trim')
    S.wboxr(WIN[0], 2.3, ZB - 0.08, WIN[1], 2.34, ZB - 0.04, 'trim')                  # transom bar in the window

    # ---------------------------------------------------------------- the front door: glass panel smashed out
    with S.tag('front_door'):
        dz = ZB - 0.1
        a, b = DOOR[0] + 0.03, DOOR[1] - 0.03
        S.wboxr(a, 0.0, dz - 0.03, b, 0.75, dz + 0.03, 'wood_dk')                    # kick panel
        S.wboxr(a, 0.0, dz - 0.03, a + 0.12, 2.42, dz + 0.03, 'wood_dk')               # stiles
        S.wboxr(b - 0.12, 0.0, dz - 0.03, b, 2.42, dz + 0.03, 'wood_dk')
        S.wboxr(a, 2.25, dz - 0.03, b, 2.42, dz + 0.03, 'wood_dk')                     # top rail
        S.wboxr(b - 0.2, 1.0, dz + 0.03, b - 0.14, 1.2, dz + 0.07, 'brass')            # push plate / handle
        # jagged shards left in the frame
        for (x, y, w, h, ang) in ((a + 0.12, 0.82, 0.07, 0.16, 25), (a + 0.12, 1.5, 0.05, 0.2, -15),
                                  (b - 0.12, 0.85, 0.12, 0.07, -35), (b - 0.12, 2.05, 0.06, 0.18, 40),
                                  (a + 0.45, 2.25, 0.16, 0.05, 12), (a + 0.12, 2.15, 0.08, 0.1, 60),
                                  (b - 0.38, 0.75, 0.1, 0.06, -12)):
            S.wbox((x + (0.025 if x < b - 0.3 else -0.025), y, dz), (w / 2, h / 2, 0.003), 'shard', rot=Rz(ang))
    # the tape across the door, outside
    S.wboxr(DOOR[0] - 0.4, 1.0, ZB - 0.32, DOOR[1] + 0.4, 1.08, ZB - 0.3, 'tape')
    S.wboxr(DOOR[0] - 0.4, 0.0, ZB - 0.35, DOOR[0] - 0.36, 1.1, ZB - 0.3, 'rail')
    S.wboxr(DOOR[1] + 0.36, 0.0, ZB - 0.35, DOOR[1] + 0.4, 1.1, ZB - 0.3, 'rail')

    # ---------------------------------------------------------------- the display window: a little stage of props
    with S.tag('window'):
        S.wboxr(WIN[0], 0.0, ZB, WIN[1], 0.75, ZB + 0.75, 'velvet_dk', rnd=0.01)
        S.fcyl((-3.6, 0.95, ZB + 0.35), 0.2, 0.025, 'reel', axis='z')                 # film reel on a stand
        S.fcyl((-3.6, 0.95, ZB + 0.35), 0.06, 0.04, 'register_dk', axis='z')
        S.wboxr(-3.62, 0.75, ZB + 0.3, -3.58, 0.8, ZB + 0.4, 'wood_dk')
        S.wbox((-2.85, 0.86, ZB + 0.4), (0.16, 0.1, 0.02), 'clapper', rot=Ry(15))      # clapperboard
        S.wbox((-2.85, 0.98, ZB + 0.4), (0.16, 0.02, 0.022), 'clapper_w', rot=Ry(15) @ Rz(-12))
        S.cyl((-2.1, 0.75, ZB + 0.35), (-2.1, 1.05, ZB + 0.35), 0.03, 'mannequin')      # a head with a fedora
        S.ell(WORLD, (-2.1, 1.22, ZB + 0.35), (0.09, 0.12, 0.1), 'mannequin')
        S.fcyl((-2.1, 1.32, ZB + 0.35), 0.17, 0.008, 'hat')
        S.fcyl((-2.1, 1.38, ZB + 0.35), 0.1, 0.06, 'hat')

    # ---------------------------------------------------------------- the signed photo wall
    with S.tag('photo_wall'):
        S.wboxr(1.3, 0.98, ZB, 4.3, 2.83, ZB + 0.03, 'photo_wall')
    S.light((2.8, 3.15, ZB + 0.7), (255, 220, 170), power=3.0, range=4, soft=14,
            spot=((0, -0.75, -0.66), 30, 62))                                            # picture light

    # ---------------------------------------------------------------- left wall: glass counters of props, posters, hat boxes
    with S.tag('counter'):
        for z0, z1 in ((-2.6, -0.95), (-0.85, 0.9)):
            S.wboxr(X0, 0.0, z0, X0 + 0.7, 0.5, z1, 'wood', rnd=0.01)                  # cabinet
            S.wboxr(X0, 0.5, z0, X0 + 0.7, 0.53, z1, 'felt')                           # felt floor of the vitrine
            S.wboxr(X0, 1.0, z0, X0 + 0.72, 1.03, z1, 'shelf_glass')                   # glass top
            for (x, z) in ((X0 + 0.68, z0), (X0 + 0.68, z1)):
                S.wboxr(x, 0.5, z - 0.02, x + 0.04, 1.03, z + 0.02, 'brass')            # corner posts
            S.wboxr(X0 + 0.68, 1.0, z0, X0 + 0.72, 1.04, z1, 'brass')
            S.wboxr(X0 + 0.69, 0.5, z0, X0 + 0.71, 0.53, z1, 'brass')
            S.wboxr(X0 + 0.69, 0.76, z0, X0 + 0.715, 0.78, z1, 'glass_edge')            # a glint on the front pane
        # in the cases: costume jewelry, a tiara, a prop pistol
        for k in range(10):
            z = rng.uniform(-2.5, 0.8)
            S.sph((X0 + rng.uniform(0.2, 0.55), 0.56, z), rng.uniform(0.015, 0.03), rng.choice(['jewel', 'gold']))
        S.cone((X0 + 0.35, 0.55, -1.6), (X0 + 0.35, 0.64, -1.5), 0.08, 0.02, 'gold')     # tiara
        S.wbox((X0 + 0.4, 0.56, 0.2), (0.12, 0.02, 0.03), 'falcon', rot=Ry(30))         # pistol
        # on top: the black bird with its tag, hats, a rotary phone
        bx, bz = X0 + 0.38, -1.75
        S.wboxr(bx - 0.08, 1.03, bz - 0.08, bx + 0.08, 1.07, bz + 0.08, 'falcon')
        S.ell(WORLD, (bx, 1.2, bz), (0.07, 0.13, 0.08), 'falcon')
        S.sph((bx + 0.01, 1.36, bz + 0.02), 0.045, 'falcon')
        S.cone((bx + 0.01, 1.36, bz + 0.06), (bx + 0.01, 1.34, bz + 0.12), 0.015, 0.003, 'falcon')
        S.wbox((bx + 0.15, 1.05, bz + 0.12), (0.04, 0.003, 0.025), 'tag', rot=Ry(20))
        S.fcyl((X0 + 0.35, 1.06, 0.3), 0.18, 0.01, 'hat')
        S.fcyl((X0 + 0.35, 1.13, 0.3), 0.1, 0.07, 'hat')
        S.wboxr(X0 + 0.25, 1.03, -0.5, X0 + 0.5, 1.12, -0.3, 'clapper')
    # shelf of hat boxes above, posters
    S.wboxr(X0, 2.15, -2.8, X0 + 0.4, 2.19, 1.2, 'wood_dk')
    for k, z in enumerate(np.arange(-2.6, 1.0, 0.55)):
        S.fcyl((X0 + 0.22, 2.32, z), 0.2, 0.13, 'hatbox' if k % 2 else 'hatbox2')
    for i, (z0, z1) in enumerate(((-2.7, -1.95), (-1.0, -0.25), (0.6, 1.35))):
        S.wboxr(X0, 1.2, z0, X0 + 0.02, 2.05, z1, 'gilt_frame')
        S.wbox((X0 + 0.025, 1.625, (z0 + z1) / 2), ((z1 - z0) / 2 - 0.04, 0.385, 0.004), f'poster{i}', rot=Ry(90))
    S.wboxr(X1 - 0.02, 1.25, 0.6, X1, 2.1, 1.3, 'gilt_frame')                         # one on the right wall
    S.wbox((X1 - 0.025, 1.675, 0.95), (0.31, 0.385, 0.004), 'poster3', rot=Ry(-90))

    # ---------------------------------------------------------------- right: the sales counter and the register
    with S.tag('sales_counter'):
        S.wboxr(X1 - 0.85, 0.0, -0.2, X1, 0.95, 2.4, 'wood_dk', rnd=0.01)
        for z0 in np.arange(-0.05, 2.3, 0.62):                                         # gilt-edged panels
            S.wboxr(X1 - 0.86, 0.15, z0, X1 - 0.85, 0.8, z0 + 0.5, 'trim')
            S.wboxr(X1 - 0.865, 0.18, z0 + 0.03, X1 - 0.855, 0.77, z0 + 0.47, 'wood_dk')
        S.wboxr(X1 - 0.88, 0.95, -0.23, X1, 1.0, 2.43, 'wood_dk', rnd=0.01)
    with S.tag('register'):
        rx, rz = X1 - 0.45, 0.6
        S.wboxr(rx - 0.22, 1.0, rz - 0.2, rx + 0.22, 1.16, rz + 0.2, 'register', rnd=0.02)   # cash drawer
        S.wboxr(rx - 0.235, 1.03, rz - 0.21, rx + 0.235, 1.13, rz + 0.21, 'register_dk', rnd=0.01)
        S.wbox((rx - 0.02, 1.3, rz), (0.15, 0.14, 0.17), 'register', rnd=0.04, rot=Rz(18))   # keyboard body
        for i in range(4):
            for j in range(3):
                S.cyl((rx - 0.17 + i * 0.05, 1.33 + j * 0.05, rz - 0.12 + j * 0.0),
                      (rx - 0.2 + i * 0.05, 1.36 + j * 0.05, rz - 0.12), 0.012, 'keys')
        S.wboxr(rx - 0.05, 1.48, rz - 0.15, rx + 0.12, 1.62, rz + 0.15, 'register', rnd=0.02)  # the flag top
        S.cyl((rx + 0.26, 1.15, rz + 0.1), (rx + 0.36, 1.3, rz + 0.1), 0.012, 'brass')         # crank
    S.fcyl((X1 - 0.5, 1.02, 1.6), 0.13, 0.02, 'lacquer')                                       # an ashtray, a lamp
    S.cyl((X1 - 0.35, 1.0, 2.0), (X1 - 0.35, 1.35, 2.0), 0.015, 'brass')
    S.cone((X1 - 0.35, 1.48, 2.0), (X1 - 0.35, 1.32, 2.0), 0.06, 0.13, 'lampshade')

    # ---------------------------------------------------------------- the curtained doorway to the office
    with S.tag('curtain'):
        z0, z1 = CURTAIN
        S.cyl((X1 - 0.12, 2.32, z0 - 0.1), (X1 - 0.12, 2.32, z1 + 0.1), 0.02, 'brass')
        for k, z in enumerate(np.arange(z0 + 0.04, z1, 0.09)):
            if z0 + 0.45 < z < z0 + 0.7:
                continue                                                                  # parted a little
            S.cyl((X1 - 0.12 + 0.03 * (k % 2), 0.02, z), (X1 - 0.12 + 0.03 * (k % 2), 2.3, z), 0.055, 'curtain', k=0.04)
        S.wboxr(X1 - 0.02, 0, z0 + 0.4, X1 + 0.3, 2.3, z0 + 0.75, 'lacquer')            # dark beyond the gap

    # ---------------------------------------------------------------- the empty Oscar case
    cx, cz = CASE
    if 'display_case' not in hide:
        with S.tag('display_case'):
            S.wboxr(cx - 0.32, 0.0, cz - 0.32, cx + 0.32, 0.95, cz + 0.32, 'lacquer', rnd=0.015)   # pedestal
            S.wboxr(cx - 0.36, 0.95, cz - 0.36, cx + 0.36, 1.0, cz + 0.36, 'brass', rnd=0.01)
            S.wbox((cx, 0.62, cz + 0.325), (0.17, 0.05, 0.004), 'plate')                         # brass plate
            S.wboxr(cx - 0.3, 1.0, cz - 0.3, cx + 0.3, 1.05, cz + 0.3, 'velvet')                  # velvet floor
            S.wboxr(cx - 0.3, 1.05, cz - 0.3, cx + 0.3, 2.05, cz - 0.26, 'velvet')                # velvet back
            S.wboxr(cx - 0.05, 1.05, cz - 0.255, cx + 0.05, 1.12, cz - 0.07, 'velvet_dk')        # the dented bed
            S.ell(WORLD, (cx, 1.48, cz - 0.255), (0.06, 0.34, 0.006), 'velvet_dk')              # the statue's shadow
            S.sph((cx, 1.86, cz - 0.255), 0.05, 'velvet_dk')
            for (sx, sz) in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
                S.wboxr(cx + sx * 0.3 - 0.015, 1.0, cz + sz * 0.3 - 0.015, cx + sx * 0.3 + 0.015, 2.12,
                        cz + sz * 0.3 + 0.015, 'brass')                                          # glass case corners
            S.wboxr(cx - 0.32, 2.08, cz - 0.32, cx + 0.32, 2.14, cz + 0.32, 'brass')             # lid
            S.wboxr(cx - 0.3, 1.0, cz + 0.295, cx + 0.3, 1.02, cz + 0.305, 'glass_edge')        # glints on the glass
            S.wboxr(cx + 0.06, 1.1, cz + 0.3, cx + 0.08, 2.0, cz + 0.305, 'glass_edge')
            S.wboxr(cx + 0.295, 1.1, cz - 0.2, cx + 0.305, 2.0, cz - 0.18, 'glass_edge')
    S.light((cx, 3.2, cz + 0.4), (255, 236, 200), power=7, range=5, soft=10, vol=0.15,
            spot=((0, -1, -0.25), 14, 30))                                               # museum spot on the case

    # ---------------------------------------------------------------- the certificate on its easel
    ex, ez = EASEL
    if 'certificate' not in hide:
        with S.tag('certificate'):
            for (dx, dz) in ((-0.22, 0.12), (0.22, 0.12)):
                S.cyl((ex + dx, 0.0, ez + dz), (ex + dx * 0.3, 1.6, ez - 0.05), 0.015, 'wood_dk')
            S.cyl((ex, 0.0, ez - 0.35), (ex, 1.55, ez - 0.05), 0.015, 'wood_dk')
            S.wboxr(ex - 0.26, 0.82, ez + 0.03, ex + 0.26, 0.86, ez + 0.12, 'wood_dk')
            S.wbox((ex, 1.14, ez + 0.06), (0.21, 0.27, 0.015), 'gilt_frame', rot=Rx(-10))
            S.wbox((ex, 1.14, ez + 0.077), (0.18, 0.24, 0.004), 'certificate', rot=Rx(-10))

    # ---------------------------------------------------------------- the director's chair
    chx, chz = CHAIR
    if 'chair' not in hide:
        with S.tag('chair'):
            R = Ry(28)
            F = Frame((chx, 0, chz), R)
            for sx in (-1, 1):
                S.cyl(F.to((sx * 0.26, 0.0, -0.22)), F.to((sx * 0.26, 0.5, 0.22)), 0.018, 'wood')    # crossed legs
                S.cyl(F.to((sx * 0.26, 0.0, 0.22)), F.to((sx * 0.26, 0.5, -0.22)), 0.018, 'wood')
                S.cyl(F.to((sx * 0.26, 0.5, -0.24)), F.to((sx * 0.26, 0.72, -0.24)), 0.016, 'wood')
                S.cyl(F.to((sx * 0.26, 0.72, -0.24)), F.to((sx * 0.26, 0.72, 0.22)), 0.02, 'wood')     # arm rests
                S.cyl(F.to((sx * 0.26, 0.5, -0.24)), F.to((sx * 0.27, 1.02, -0.27)), 0.016, 'wood')   # back posts
            S.box(F, (0, 0.48, 0.0), (0.25, 0.012, 0.21), 0.004, 'canvas')
            S.box(F, (0, 0.9, -0.265), (0.26, 0.09, 0.008), 0.002, 'chair_back', rot=Ry(180))

    # ---------------------------------------------------------------- foreground: the jacket rack (left), a low case (right)
    if 'mannequin' not in hide:
        with S.tag('mannequin'):                                 # a dress form in a gold sequined gown, on a stand
            mx, mz = -3.0, 2.75
            S.cyl((mx, 0.0, mz), (mx, 0.03, mz), 0.3, 'brass')
            S.cyl((mx, 0.0, mz), (mx, 0.3, mz), 0.025, 'brass')
            MQ = (226, 220, 210)
            npc.place(S, 'mannequin', dict(npc.STAND, stubble=False, hair='bald', coatlen=1.05, cop=False, blink=1.0,
                                           lsp=8, le=30, lin=20, rsp=24, re=70, rin=40, rhand='open', hp=-4, hy=24),
                      (mx, 0.3, mz), yaw=28, scale=0.93,
                      colors=dict(coat=(200, 160, 60), coat_dk=(170, 130, 50), lining=(150, 110, 40), shirt=(210, 170, 70),
                                  pants=(200, 160, 60), shoe=(200, 160, 60), sole=(160, 120, 40), skin=MQ, skin_dk=MQ,
                                  hair=MQ, hairgrey=MQ, brow=MQ, lips=MQ, eyew=MQ, iris=MQ, pupil=MQ, stubble=MQ,
                                  button=(230, 200, 120), buckle=(230, 200, 120)))
    if 'lowcase' not in hide:
        with S.tag('lowcase'):
            lx0, lx1, lz0, lz1 = 1.4, 3.6, 2.95, 3.45
            S.wboxr(lx0, 0.0, lz0, lx1, 0.7, lz1, 'wood', rnd=0.01)
            S.wboxr(lx0, 0.7, lz0, lx1, 0.73, lz1, 'felt')
            S.wboxr(lx0 - 0.02, 0.98, lz0 - 0.02, lx1 + 0.02, 1.01, lz1 + 0.02, 'shelf_glass')
            for x in (lx0, lx1 - 0.03):
                for z in (lz0, lz1 - 0.03):
                    S.wboxr(x, 0.7, z, x + 0.03, 0.99, z + 0.03, 'brass')
            for k, x in enumerate(np.arange(lx0 + 0.2, lx1 - 0.1, 0.3)):               # lobby cards and a reel
                S.wbox((x, 0.75, lz0 + 0.25), (0.09, 0.12, 0.006), f'poster{k % 4}', rot=Rx(-75))
            S.fcyl((lx1 - 0.3, 0.76, lz0 + 0.25), 0.15, 0.02, 'reel')
        S.light(((lx0 + lx1) / 2, 0.92, (lz0 + lz1) / 2), (255, 226, 180), power=0.6, range=1.6, shadow=False)

    S.wboxr(-0.75, 0.0, -2.45, 0.25, 0.012, 3.4, 'runner')                              # a worn runner from the door
    if 'ropes' not in hide:
        with S.tag('ropes'):                                     # museum stanchions and a red rope round the case
            pts = [(CASE[0] + 0.72 * math.cos(t), CASE[1] + 0.72 * math.sin(t)) for t in np.radians((20, 90, 160))]
            for (x, z) in pts:
                S.cyl((x, 0, z), (x, 0.02, z), 0.1, 'brass')
                S.cyl((x, 0, z), (x, 0.9, z), 0.02, 'brass')
                S.sph((x, 0.93, z), 0.035, 'brass')
            for (p0, p1) in zip(pts, pts[1:]):
                def rp(t, p0=p0, p1=p1):
                    return (p0[0] + (p1[0] - p0[0]) * t, 0.86 - 0.14 * math.sin(math.pi * t), p0[1] + (p1[1] - p0[1]) * t)
                for t0, t1 in ((0, 0.25), (0.25, 0.5), (0.5, 0.75), (0.75, 1)):
                    S.cyl(rp(t0), rp(t1), 0.022, 'velvet')

    # ---------------------------------------------------------------- ceiling lamps
    for (lx, lz) in ((cx - 0.2, -1.6), (-1.6, 1.0), (2.6, 1.4)):
        S.cyl((lx, H, lz), (lx, 2.95, lz), 0.008, 'rail')
        S.tcyl(Frame((lx, 2.9, lz)), (0, 0, 0), (0.04, 0.04), (0.17, 0.17), 0.06, 'shade', shell=0.006)
        S.sph((lx, 2.83, lz), 0.035, 'bulb')
    S.light((cx - 0.2, 2.75, -1.6), (255, 210, 150), power=2.4, range=6, soft=16, spot=((0, -1, 0), 50, 85))
    S.light((-1.6, 2.75, 1.0), (255, 210, 150), power=3.0, range=7, soft=16, vol=0.1, spot=((0, -1, 0), 50, 85))
    S.light((2.6, 2.75, 1.4), (255, 210, 150), power=2.4, range=6, soft=16, spot=((0, -1, 0), 50, 85))
    S.light((0.0, 2.2, 3.5), (255, 220, 190), power=1.0, range=8, shadow=False)                  # soft fill from the front
    S.light((X0 + 0.4, 0.95, -0.9), (255, 226, 180), power=0.9, range=2.2, shadow=False)        # vitrine lights
    S.light((X1 - 0.35, 1.4, 2.0), (255, 200, 130), power=0.5, range=2.2, shadow=False)        # counter lamp

    # ---------------------------------------------------------------- outside: the Walk of Fame, the boulevard, the theatre
    OZ = ZB - 0.18
    S.wboxr(X0 - 8, -0.02, OZ - 4.2, X1 + 8, 0.0, OZ, 'walk')                          # sidewalk with the stars
    S.wboxr(X0 - 8, -0.16, OZ - 4.4, X1 + 8, -0.02, OZ - 4.2, 'curb')
    S.wboxr(X0 - 8, -0.2, OZ - 26, X1 + 8, -0.16, OZ - 4.4, 'asphalt')
    S.wboxr(X0 - 8, -0.02, OZ - 30, X1 + 8, 0.0, OZ - 26, 'walk')                      # the far sidewalk
    for (a, b) in ((X0 - 8, X0 - 0.2), (X1 + 0.2, X1 + 8)):                             # neighbouring shopfronts
        S.wboxr(a, 0, OZ - 0.02, b, 6, OZ + 0.18, 'facade')
    S.wboxr(X0 - 0.2, H, OZ - 0.02, X1 + 0.2, 6, OZ + 0.18, 'facade')
    S.wbox(((DOOR[0] + WIN[0]) / 2, 2.95, OZ - 0.8), (2.8, 0.03, 0.85), 'awning', rot=Rx(-14))  # awning
    S.wbox(((DOOR[0] + WIN[0]) / 2, 2.62, OZ - 1.62), (2.8, 0.16, 0.02), 'awning')
    # streetlamp and a palm trunk on the curb
    S.cyl((-3.4, 0, OZ - 4.0), (-3.4, 5.2, OZ - 4.0), 0.07, 'lamp_head')
    S.cyl((-3.4, 5.2, OZ - 4.0), (-2.6, 5.4, OZ - 4.0), 0.05, 'lamp_head')
    S.wbox((-2.5, 5.35, OZ - 4.0), (0.25, 0.06, 0.12), 'lamp_glass')
    S.cone((3.2, 0, OZ - 4.0), (3.0, 7, OZ - 4.0), 0.22, 0.16, 'palm')
    # the patrol car at the curb, lights going
    pz = OZ - 5.6
    px = 3.2
    S.wboxr(px - 2.5, 0.3, pz - 0.95, px + 2.5, 0.95, pz + 0.95, 'car_paint', rnd=0.12)
    S.wboxr(px - 1.3, 0.3, pz - 0.97, px + 1.3, 0.95, pz + 0.97, 'car_white', rnd=0.1)            # white doors
    S.wboxr(px - 1.4, 0.9, pz - 0.85, px + 1.5, 1.42, pz + 0.85, 'car_paint', rnd=0.14)
    S.wboxr(px - 1.3, 0.98, pz - 0.88, px + 1.4, 1.36, pz + 0.88, 'car_glass', rnd=0.08)
    S.wboxr(px - 0.45, 1.42, pz - 0.6, px + 0.05, 1.52, pz - 0.05, 'bar_red')
    S.wboxr(px - 0.45, 1.42, pz + 0.05, px + 0.05, 1.52, pz + 0.6, 'bar_blue')
    for x in (px - 1.7, px + 1.7):
        S.fcyl((x, 0.34, pz + 0.95), 0.34, 0.12, 'tire', axis='z')
    S.light((px - 0.2, 1.6, pz + 0.1), (255, 40, 30), power=7, range=12, vol=0.3, soft=10)
    S.light((px - 0.2, 1.6, pz + 0.7), (50, 90, 255), power=7, range=12, vol=0.3, soft=10)
    # the theatre: forecourt lamps, red columns, the dark entrance, the eaves of the green pagoda roof
    tz = OZ - 31
    S.wboxr(-24, 0, tz - 0.5, 12, 9, tz, 'theatre')
    for x in (-13.0, -8.0):                                                                  # the two red columns
        S.cyl((x, 0, tz + 1.5), (x, 7.5, tz + 1.5), 0.5, 'column')
    for x in np.arange(-15.0, 6.0, 3.0):                                                    # forecourt lamp posts
        S.cyl((x, 0, tz + 5.0), (x, 3.2, tz + 5.0), 0.06, 'lamp_head')
        S.sph((x, 3.35, tz + 5.0), 0.2, 'lamp_glass')
    S.wbox((-1.0, 6.4, tz + 2.2), (9.5, 0.12, 3.2), 'pagoda', rot=Rx(16))
    S.wbox((-1.0, 5.6, tz + 4.9), (9.8, 0.3, 0.3), 'pagoda')
    S.light((-1.0, 0.6, tz + 4), (255, 190, 110), power=40, range=18, vol=0.2, shadow=False)
    for x in (-13.0, -8.0):                                                                  # uplights on the columns
        S.light((x, 0.3, tz + 2.8), (255, 150, 90), power=18, range=9, shadow=False)
    S.light((-2.5, 5.1, OZ - 4.0), (255, 170, 90), power=24, range=14, vol=0.4, soft=12)          # sodium lamp
    S.sun((0.3, -1, -0.4), (70, 80, 120), power=0.25, shadow=False)

    # ---------------------------------------------------------------- the people (overlays)
    if 'pearl_chair' not in hide:
        npc.cast(S, 'pearl', dict(npc.SEATED, lsp=36, lsa=10, le=112, lin=86, rsp=30, rsa=10, re=104, rin=92,
                                  lean=10, hp=10, hy=-12, hr=4),
                 (chx + 0.02, 0.0, chz + 0.04), yaw=28, scale=0.92, tag='pearl_chair')
    if 'pearl_stand' not in hide:
        npc.cast(S, 'pearl', dict(npc.STAND, lsp=12, le=40, lin=40, rsp=10, re=44, rin=42, hp=12, hy=-20, hr=6),
                 (PEARL_UP[0], 0, PEARL_UP[1]), yaw=-24, scale=0.92, tag='pearl_stand')
    if 'park' not in hide:
        npc.cast(S, 'park', dict(npc.STAND, lsp=28, le=40, lin=24, rsp=4, re=18, hp=4, hy=12),
                 (PARK[0], 0, PARK[1]), yaw=24, scale=0.94, tag='park')
    if 'morty' not in hide:
        npc.cast(S, 'morty', dict(npc.STAND, lsp=34, le=96, lin=60, rsp=30, re=100, rin=62, hp=6, hy=8),
                 (MORTY[0], 0, MORTY[1]), yaw=-6, scale=0.95, tag='morty')

    cam = Camera((0.0, 2.55, 7.6), (0.0, 1.0, -3.0), fov=42, W=3840, H=2160)
    env = dict(sky=(34, 28, 30), bounce=(36, 24, 20), fog_col=(30, 24, 30), fog=0.018, fog_h0=0.0, fog_hf=0.06,
               fog_max=60, vol_scale=4, vol_steps=40, reflections=True, grid=0.5, ao_scale=0.9)
    meta = dict(
        room='stardust_shop',
        walk=[(-3.75, -2.35), (-0.95, -2.35), (-0.95, -2.55), (0.4, -2.55), (0.4, -2.35), (3.6, -2.35), (3.6, 2.6),
              (-3.75, 2.6)],
        walk_zmin=-2.4, walk_zmax=2.6, scale_x=0.0,
        spawns={'drive': (-0.3, -2.0), 'squad_room': (-0.3, -2.0), 'stardust_office': (3.4, -1.65),
                'start': (0.0, 1.6)},
        hotspots={
            'pearl': ('Pearl', (-0.95, 1.05), 'left'),
            'pearl_stand': ('Pearl', (-0.95, 1.2), 'right'),
            'park': ('Officer Park', (-0.55, -1.75), 'left'),
            'morty': ('Morty', (-0.3, -2.3), 'up'),
            'display_case': ('display case', (cx, 0.95), 'up'),
            'certificate': ('certificate', (ex + 0.1, 0.45), 'up'),
            'front_door': ('front door', (-0.3, -2.4), 'up'),
            'photo_wall': ('signed photos', (2.8, -2.1), 'up'),
            'register': ('cash register', (3.2, 0.6), 'right'),
            'chair': ("director's chair", (-0.95, 1.05), 'left'),
            'counter': ('counter of props', (-3.3, -1.4), 'left'),
            'window': ('window', (-2.8, -2.2), 'up'),
            'curtain': ('curtained doorway', (3.45, -1.65), 'right'),
        },
        hotspot_shapes={
            'pearl': [(chx - 0.35, 0.0, chz + 0.3), (chx + 0.4, 0.0, chz + 0.3), (chx + 0.4, 1.4, chz + 0.3),
                      (chx - 0.35, 1.4, chz + 0.3)],
            'pearl_stand': [(PEARL_UP[0] - 0.3, 0.0, PEARL_UP[1]), (PEARL_UP[0] + 0.3, 0.0, PEARL_UP[1]),
                            (PEARL_UP[0] + 0.3, 1.72, PEARL_UP[1]), (PEARL_UP[0] - 0.3, 1.72, PEARL_UP[1])],
            'park': [(PARK[0] - 0.3, 0.0, PARK[1]), (PARK[0] + 0.3, 0.0, PARK[1]), (PARK[0] + 0.3, 1.78, PARK[1]),
                     (PARK[0] - 0.3, 1.78, PARK[1])],
            'morty': [(DOOR[0] + 0.12, 0.75, ZB - 0.1), (DOOR[1] - 0.12, 0.75, ZB - 0.1), (DOOR[1] - 0.12, 2.25, ZB - 0.1),
                      (DOOR[0] + 0.12, 2.25, ZB - 0.1)],
            'window': [(WIN[0], 0.75, ZB), (WIN[1], 0.75, ZB), (WIN[1], 3.0, ZB), (WIN[0], 3.0, ZB)],
        },
        hotspot_order=['window', 'front_door', 'photo_wall', 'counter', 'curtain', 'sales_counter', 'register',
                       'certificate', 'display_case', 'chair', 'morty', 'park', 'pearl', 'pearl_stand'],
        overlays=['pearl_chair', 'pearl_stand', 'park', 'morty'],
        overlay_bases={'pearl_chair': (chx, chz + 0.35), 'pearl_stand': PEARL_UP, 'park': PARK},
        occluders={'mannequin': (-3.0, 2.75), 'lowcase': (2.5, 2.95), 'ropes': (CASE[0], CASE[1] + 0.75),
                   'display_case': (cx, cz + 0.36), 'certificate': (ex, ez + 0.15), 'chair': (chx, chz + 0.3)},
        obstacles=[(cx, cz, 0.85), (ex, ez, 0.35), (chx, chz, 0.45), (PARK[0], PARK[1], 0.28), (-3.0, 2.75, 0.4)],
        char_fill=((236, 220, 200), 0.18),
        tint=(0.86, 0.78, 0.72),
        exposure=1.35,
    )
    return S, cam, env, meta
