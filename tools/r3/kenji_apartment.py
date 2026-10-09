"""Kenji and Devin's apartment, a bungalow duplex in Silver Lake, 2:25 a.m. Living room and open kitchen: big framed night
photos of LA, a couch facing the TV on the left wall with a laptop open on the coffee table, a dining table up front,
a camera bag on the hook by the door and wet sneakers on the mat. The round-cornered old fridge is covered in magnets.
Kenji's door stands open on his desk, a Dodgers pennant and a framed certificate; Devin's door is shut.

Devin has two poses, both overlays the game shows or hides: leaning on the fridge, arms folded (until Ray gets his
consent to search), then on the couch, staring at the dark TV."""
import math, random
import numpy as np
from scene3d import *
import textures as tx
import npc

X0, X1, ZB, H = -4.6, 4.8, -3.4, 3.2
KD0, KD1 = 0.0, 1.4          # Kenji's doorway (x)
DD0, DD1 = 1.9, 2.8          # Devin's door
FD0, FD1 = -4.3, -3.3        # front door
COUCH = (-2.05, -0.55)       # couch centre (x, z), facing the TV on the left wall
DINING = (1.75, 1.35)        # dining table centre
FRIDGE = (3.3, -3.0)         # fridge centre on the floor


def build(hide=()):
    S = Scene()
    rng = random.Random(61)
    # ---------------------------------------------------------------- materials
    S.mat('floor', (255, 255, 255), tex=tx.hires(tx.floorboards(), 2), texmode=4, texmap=1, texscale=2.6, spec=0.4,
          shin=40, refl=0.04)
    S.mat('wall', (176, 168, 150))
    S.mat('wall_k', (150, 160, 150))
    S.mat('ceiling', (120, 116, 110))
    S.mat('trim', (220, 216, 204), spec=0.2)
    S.mat('door', (200, 194, 180), spec=0.2, namp=0.05, nscale=6)
    S.mat('knob', (180, 150, 70), spec=1.2, shin=60)
    S.mat('rug', (90, 70, 60), namp=0.4, nscale=20)
    S.mat('couch', (70, 82, 92), namp=0.2, nscale=18, spec=0.1)
    S.mat('couch_dk', (52, 62, 70), namp=0.2, nscale=18)
    S.mat('wood', (110, 74, 46), namp=0.15, nscale=6, spec=0.4, shin=40)
    S.mat('wood_dk', (60, 40, 28), namp=0.1, nscale=6, spec=0.3)
    S.mat('black', (18, 18, 20), spec=0.5, shin=40)
    S.mat('steel', (150, 152, 156), spec=1.0, shin=60)
    S.mat('frame', (20, 20, 22), spec=0.5, shin=40)
    for k in ('freeway', 'bowl', 'overlook'):
        S.mat('photo_' + k, (30, 30, 30), tex=tx.hires(tx.night_photo(k), 2), texmode=3, texemis=0.6, spec=0.6, shin=80)
    S.mat('laptop', (20, 20, 24), tex=tx.laptop_screen(), texmode=3, texemis=1.6)
    S.mat('fridge', (220, 216, 198), tex=tx.hires(tx.fridge_door(), 2), texmode=1, spec=0.6, shin=50)
    S.mat('enamel', (222, 218, 200), spec=0.6, shin=50)
    S.mat('counter', (60, 62, 66), spec=0.7, shin=60)
    S.mat('cabinet', (90, 120, 110), spec=0.3, shin=30)
    S.mat('tile', (220, 220, 214), namp=0.1, nscale=20, spec=0.5)
    S.mat('bag', (22, 22, 24), spec=0.3, shin=20, namp=0.2, nscale=30)
    S.mat('strap', (40, 40, 44), namp=0.6, nscale=120)
    S.mat('sneaker', (64, 70, 84), spec=0.3, namp=0.1, nscale=40)
    S.mat('sneaker_sole', (226, 224, 218), spec=0.2)
    S.mat('sneaker_in', (20, 20, 22))
    S.mat('grit', (190, 120, 70), namp=0.5, nscale=60)
    S.mat('mat', (100, 70, 40), namp=0.5, nscale=40)
    S.mat('printout', (220, 220, 220), tex=tx.hushhush_printout(), texmode=1)
    S.mat('cert', (220, 220, 220), tex=tx.certificate(), texmode=1, spec=0.6, shin=60)
    S.mat('pennant', (20, 60, 150), tex=tx.pennant(), texmode=1)
    S.mat('dcbox', (30, 30, 34), tex=tx.dashcam_box(), texmode=1)
    S.mat('lampshade', (230, 210, 170), emis=(140, 110, 60))
    S.mat('bulb', (255, 220, 160), emis=(255, 210, 150), emis_mult=5)
    S.mat('softbox', (230, 230, 230), spec=0.2)
    S.mat('street', (20, 24, 40), tex=tx.skyline(13, 512, 256), texmode=3, texemis=0.9)
    S.mat('books', (120, 60, 50), namp=0.6, nscale=12)
    S.mat('plant', (40, 70, 40), namp=0.4, nscale=8)
    S.mat('pot', (150, 80, 50))
    S.mat('case', (40, 40, 44), spec=0.6, shin=50)
    S.mat('blind', (210, 204, 190), spec=0.2)
    S.mat('screen_off', (6, 6, 8), spec=1.4, shin=90, refl=0.3)
    S.mat('takeout', (236, 232, 222), spec=0.2)

    # ---------------------------------------------------------------- shell
    S.wboxr(X0 - 1, -0.3, ZB - 5, X1 + 1, 0.0, 12, 'floor')
    S.wboxr(X0 - 0.2, 0, ZB - 0.15, X1 + 0.2, H, ZB, 'wall')                      # back wall (doorways cut below)
    S.wboxr(X0 - 0.2, 0, ZB, X0, H, 6, 'wall')                                     # left wall
    S.wboxr(X1, 0, ZB, X1 + 0.2, H, 6, 'wall_k')                                   # right wall (kitchen)
    S.wboxr(X0 - 0.2, H, ZB - 5, X1 + 0.2, H + 0.2, 6, 'ceiling')
    S.wboxr(X0, 0, ZB, X1, 0.1, ZB + 0.03, 'trim')
    # doorways
    S.wboxr(KD0, 0, ZB - 0.3, KD1, 2.15, ZB + 0.05, 'wall', op=1)
    S.wboxr(DD0, 0, ZB - 0.3, DD1, 2.1, ZB + 0.05, 'wall', op=1)
    S.wboxr(FD0, 0, ZB - 0.3, FD1, 2.1, ZB + 0.05, 'wall', op=1)
    for (a, b, top) in ((KD0, KD1, 2.15), (DD0, DD1, 2.1), (FD0, FD1, 2.1)):
        S.wboxr(a - 0.07, 0, ZB, a, top + 0.07, ZB + 0.04, 'trim')
        S.wboxr(b, 0, ZB, b + 0.07, top + 0.07, ZB + 0.04, 'trim')
        S.wboxr(a - 0.07, top, ZB, b + 0.07, top + 0.07, ZB + 0.04, 'trim')
    S.wboxr(-4.1, 0.0, -2.0, -1.2, 0.01, 0.9, 'rug')

    # ---------------------------------------------------------------- front door (back wall, far left), hook, mat
    with S.tag('front_door'):
        S.wboxr(FD0 + 0.02, 0, ZB - 0.12, FD1 - 0.02, 2.08, ZB - 0.06, 'door')
        S.sph((FD1 - 0.12, 1.0, ZB - 0.02), 0.035, 'knob')
    with S.tag('camera_bag'):
        S.cyl((-2.95, 1.65, ZB), (-2.95, 1.65, ZB + 0.08), 0.012, 'steel')            # coat hook
        S.wbox((-2.95, 1.12, ZB + 0.16), (0.2, 0.14, 0.1), 'bag', rnd=0.03)
        S.cyl((-3.12, 1.24, ZB + 0.16), (-2.97, 1.66, ZB + 0.1), 0.012, 'strap')
        S.cyl((-2.78, 1.24, ZB + 0.16), (-2.93, 1.66, ZB + 0.1), 0.012, 'strap')
    S.wboxr(FD0 - 0.1, 0.0, ZB + 0.05, FD1 + 0.3, 0.015, ZB + 0.7, 'mat')
    with S.tag('sneakers'):
        # a pair of running shoes kicked off on the mat, toes to the room, one tipped on its side
        for (x, z, yaw, roll) in ((-3.98, ZB + 0.42, 18, 0), (-3.62, ZB + 0.5, -26, 70)):
            F = Frame((x, 0.0, z), Ry(yaw) @ Rz(roll))
            lift = 0.055 if roll else 0.0
            S.box(F, (0, 0.022 + lift, 0), (0.05, 0.018, 0.14), 0.015, 'sneaker_sole')        # white midsole
            S.box(F, (0, 0.06 + lift, -0.02), (0.045, 0.035, 0.11), 0.03, 'sneaker')         # upper
            S.box(F, (0, 0.05 + lift, 0.09), (0.042, 0.022, 0.05), 0.022, 'sneaker')          # toe box
            S.box(F, (0, 0.1 + lift, -0.085), (0.034, 0.012, 0.04), 0.008, 'sneaker_in')      # heel opening
            S.box(F, (0, 0.093 + lift, 0.0), (0.02, 0.006, 0.06), 0.004, 'sneaker_sole')      # laces
            S.box(F, (0, 0.006 + lift, 0), (0.048, 0.006, 0.135), 0.004, 'grit')               # orange grit in the treads

    # ---------------------------------------------------------------- photos on the back wall, behind the couch
    with S.tag('photos'):
        for k, (x0, x1, y0, y1) in enumerate([(-2.55, -1.75, 1.35, 1.9), (-1.6, -0.15, 1.2, 2.1), (-2.55, -1.75, 2.0, 2.45)]):
            kind = ('freeway', 'overlook', 'bowl')[k]
            S.wboxr(x0, y0, ZB, x1, y1, ZB + 0.03, 'frame')
            S.wboxr(x0 + 0.05, y0 + 0.05, ZB + 0.03, x1 - 0.05, y1 - 0.05, ZB + 0.035, 'photo_' + kind)

    # ---------------------------------------------------------------- the TV on its console (left wall)
    with S.tag('tv'):
        S.wboxr(X0, 0, -1.55, X0 + 0.45, 0.5, 0.45, 'wood_dk', rnd=0.02)
        S.wboxr(X0 + 0.15, 0.5, -0.65, X0 + 0.3, 0.54, -0.25, 'black')
        S.wboxr(X0 + 0.2, 0.54, -0.5, X0 + 0.25, 0.62, -0.4, 'black')
        S.wboxr(X0 + 0.19, 0.62, -1.25, X0 + 0.25, 1.32, 0.15, 'black')          # dark screen
        S.wboxr(X0 + 0.25, 0.65, -1.22, X0 + 0.255, 1.29, 0.12, 'screen_off')
    # Devin's light stand, between the TV and the bookcase
    S.cyl((-4.15, 0, 0.8), (-4.15, 1.9, 0.8), 0.015, 'black')
    for a in range(3):
        ang = a * 2.1
        S.cyl((-4.15, 0.25, 0.8), (-4.15 + 0.3 * math.cos(ang), 0.0, 0.8 + 0.3 * math.sin(ang)), 0.012, 'black')
    S.wbox((-4.05, 2.05, 0.75), (0.28, 0.28, 0.12), 'softbox', rot=Ry(60) @ Rx(15))
    S.wboxr(X0, 0, 1.0, X0 + 0.4, 1.9, 1.03, 'wood_dk')                              # bookcase on the left wall
    S.wboxr(X0, 0, 2.6, X0 + 0.4, 1.9, 2.63, 'wood_dk')
    S.wboxr(X0, 0, 1.0, X0 + 0.03, 1.9, 2.63, 'wood_dk')
    S.wboxr(X0, 1.87, 1.0, X0 + 0.4, 1.9, 2.63, 'wood_dk')
    for k, y in enumerate((0.05, 0.5, 0.95, 1.4)):
        S.wboxr(X0 + 0.02, y, 1.03, X0 + 0.38, y + 0.03, 2.6, 'wood')
        S.wboxr(X0 + 0.05, y + 0.03, 1.1 + 0.1 * k, X0 + 0.32, y + 0.36, 2.3 - 0.12 * k, 'books')
    S.cyl((X1 - 0.45, 0, 2.6), (X1 - 0.45, 0.4, 2.6), 0.2, 'pot')                  # a plant in the kitchen corner
    S.ell(WORLD, (X1 - 0.45, 0.9, 2.6), (0.4, 0.55, 0.4), 'plant', k=0.1)

    # ---------------------------------------------------------------- the couch (facing the TV), coffee table, lamp
    cx, cz = COUCH
    if 'couch' not in hide:
        with S.tag('couch'):
            S.wboxr(cx - 0.42, 0.0, cz - 1.0, cx + 0.42, 0.42, cz + 1.0, 'couch_dk', rnd=0.04)
            S.wboxr(cx - 0.4, 0.38, cz - 0.9, cx + 0.3, 0.52, cz + 0.9, 'couch', rnd=0.06)
            S.wboxr(cx + 0.22, 0.4, cz - 1.0, cx + 0.45, 0.9, cz + 1.0, 'couch', rnd=0.08)       # back, toward the room
            for sz in (-1, 1):
                S.wboxr(cx - 0.42, 0.0, cz + sz * 1.0 - 0.13, cx + 0.42, 0.66, cz + sz * 1.0 + 0.13, 'couch', rnd=0.07)
    if 'table' not in hide:
        with S.tag('table'):
            tx_, tz_ = cx - 1.1, cz
            S.wboxr(tx_ - 0.3, 0.4, tz_ - 0.65, tx_ + 0.3, 0.45, tz_ + 0.65, 'wood', rnd=0.01)
            for sx in (-1, 1):
                for sz in (-1, 1):
                    S.wboxr(tx_ + sx * 0.25 - 0.025, 0, tz_ + sz * 0.6 - 0.025, tx_ + sx * 0.25 + 0.025, 0.4,
                            tz_ + sz * 0.6 + 0.025, 'wood_dk')
            with S.tag('laptop'):                                                     # open, turned to the room
                S.wbox((tx_ + 0.04, 0.46, tz_ + 0.25), (0.17, 0.008, 0.12), 'black', rot=Ry(80))
                S.wbox((tx_ - 0.09, 0.58, tz_ + 0.27), (0.17, 0.115, 0.006), 'black', rot=Ry(80) @ Rx(-12))
                S.wbox((tx_ - 0.083, 0.58, tz_ + 0.269), (0.155, 0.1, 0.002), 'laptop', rot=Ry(80) @ Rx(-12))
            S.cyl((tx_ + 0.1, 0.45, tz_ - 0.35), (tx_ + 0.1, 0.55, tz_ - 0.35), 0.04, 'enamel')
    lx, lz = cx + 0.1, cz - 1.35                                                         # floor lamp at the couch's end
    S.cyl((lx, 0, lz), (lx, 0.02, lz), 0.16, 'black')
    S.cyl((lx, 0, lz), (lx, 1.45, lz), 0.012, 'black')
    S.cone((lx, 1.65, lz), (lx, 1.38, lz), 0.12, 0.2, 'lampshade')

    # ---------------------------------------------------------------- the dining table, up front by the kitchen
    if 'dining' not in hide:
        with S.tag('dining'):
            dx, dz = DINING
            S.wboxr(dx - 0.75, 0.72, dz - 0.45, dx + 0.75, 0.77, dz + 0.45, 'wood', rnd=0.01)
            for sx in (-1, 1):
                for sz in (-1, 1):
                    S.wboxr(dx + sx * 0.68 - 0.03, 0, dz + sz * 0.38 - 0.03, dx + sx * 0.68 + 0.03, 0.72,
                            dz + sz * 0.38 + 0.03, 'wood_dk')
            for (chx, chz, back) in ((dx - 0.35, dz - 0.75, -1), (dx + 0.35, dz - 0.72, -1), (dx - 0.3, dz + 0.78, 1),
                                     (dx + 1.05, dz + 0.1, 0)):
                S.wboxr(chx - 0.21, 0.43, chz - 0.21, chx + 0.21, 0.47, chz + 0.21, 'wood')
                for sx in (-1, 1):
                    for sz in (-1, 1):
                        S.wboxr(chx + sx * 0.18 - 0.02, 0, chz + sz * 0.18 - 0.02, chx + sx * 0.18 + 0.02, 0.43,
                                chz + sz * 0.18 + 0.02, 'wood_dk')
                if back:
                    S.wboxr(chx - 0.21, 0.47, chz + back * 0.17, chx + 0.21, 0.95, chz + back * 0.21, 'wood')
                else:
                    S.wboxr(chx + 0.17, 0.47, chz - 0.21, chx + 0.21, 0.95, chz + 0.21, 'wood')
            S.fcyl((dx - 0.3, 0.775, dz - 0.15), 0.12, 0.006, 'enamel')                           # two dinner plates
            S.fcyl((dx + 0.35, 0.775, dz + 0.1), 0.12, 0.006, 'enamel')
            S.wbox((dx + 0.05, 0.78, dz + 0.25), (0.15, 0.04, 0.1), 'takeout', rnd=0.02)

    # ---------------------------------------------------------------- Kenji's room through the open door
    KZ = ZB - 3.1
    S.wboxr(KD0 - 1.0, 0, KZ - 0.15, KD1 + 1.0, H, KZ, 'wall')                       # his back wall
    S.wboxr(KD0 - 1.15, 0, KZ, KD0 - 1.0, H, ZB, 'wall')
    S.wboxr(KD1 + 1.0, 0, KZ, KD1 + 1.15, H, ZB, 'wall')
    with S.tag('kenji_desk'):
        S.wboxr(KD0 + 0.05, 0.72, KZ, KD1 - 0.05, 0.77, KZ + 0.6, 'wood')
        S.wboxr(KD0 + 0.08, 0, KZ + 0.05, KD0 + 0.12, 0.72, KZ + 0.55, 'wood_dk')
        S.wboxr(KD1 - 0.12, 0, KZ + 0.05, KD1 - 0.08, 0.72, KZ + 0.55, 'wood_dk')
        S.wbox((KD0 + 0.6, 0.776, KZ + 0.3), (0.11, 0.14, 0.004), 'printout', rot=Rx(-90))
        S.cyl((KD1 - 0.3, 0.77, KZ + 0.2), (KD1 - 0.3, 1.1, KZ + 0.15), 0.012, 'black')   # desk lamp
        S.cone((KD1 - 0.3, 1.12, KZ + 0.15), (KD1 - 0.3, 1.02, KZ + 0.22), 0.03, 0.09, 'lampshade')
    with S.tag('pennant'):
        S.wbox((KD0 + 0.55, 1.82, KZ + 0.01), (0.4, 0.13, 0.005), 'pennant')
    with S.tag('certificate'):
        S.wboxr(KD0 + 0.25, 1.25, KZ, KD0 + 0.75, 1.6, KZ + 0.03, 'frame')
        S.wboxr(KD0 + 0.28, 1.28, KZ + 0.03, KD0 + 0.72, 1.57, KZ + 0.035, 'cert')
    with S.tag('dashcam_box'):
        S.wboxr(KD0 + 0.85, 1.3, KZ, KD1 - 0.05, 1.33, KZ + 0.25, 'wood')             # shelf
        S.wbox((KD0 + 1.08, 1.43, KZ + 0.13), (0.1, 0.1, 0.1), 'dcbox')

    # ---------------------------------------------------------------- Devin's door
    with S.tag('devin_door'):
        S.wboxr(DD0 + 0.02, 0, ZB - 0.1, DD1 - 0.02, 2.08, ZB - 0.04, 'door')
        S.sph((DD0 + 0.12, 1.0, ZB), 0.035, 'knob')

    # ---------------------------------------------------------------- open kitchen: counter, sink, the fridge
    S.wboxr(3.75, 0, ZB, X1, 0.9, ZB + 0.62, 'cabinet')
    S.wboxr(3.73, 0.9, ZB, X1, 0.95, ZB + 0.65, 'counter')
    S.wboxr(3.75, 0.95, ZB, X1, 1.5, ZB + 0.02, 'tile')
    S.wboxr(X1 - 0.62, 0, -2.2, X1, 0.9, 1.2, 'cabinet')                              # counter along the right wall
    S.wboxr(X1 - 0.65, 0.9, -2.2, X1, 0.95, 1.2, 'counter')
    with S.tag('sink'):
        S.wboxr(X1 - 0.5, 0.88, -0.6, X1 - 0.1, 0.96, 0.1, 'steel', op=1)              # sink
        S.wboxr(X1 - 0.52, 0.86, -0.62, X1 - 0.08, 0.88, 0.12, 'steel')
        S.cyl((X1 - 0.08, 0.95, -0.25), (X1 - 0.08, 1.25, -0.25), 0.015, 'steel')
        S.cyl((X1 - 0.08, 1.25, -0.25), (X1 - 0.3, 1.22, -0.25), 0.012, 'steel')
    S.wboxr(X1 - 0.35, 1.55, -2.2, X1, 2.3, 1.2, 'cabinet')                           # upper cabinets
    # kitchen window over the sink: blinds, street light outside
    S.wboxr(X1 - 0.05, 1.05, -0.9, X1 + 0.3, 1.5, 0.4, 'wall_k', op=1)
    S.wbox((X1 + 0.25, 1.3, -0.25), (0.65, 0.25, 0.01), 'street', rot=Ry(-90))
    for y in np.arange(1.08, 1.5, 0.06):
        S.wboxr(X1 - 0.02, y, -0.88, X1 + 0.0, y + 0.03, 0.38, 'blind')
    fx, fz = FRIDGE
    with S.tag('fridge'):
        S.wbox((fx, 0.75, fz), (0.37, 0.75, 0.34), 'enamel', rnd=0.1)
        S.wbox((fx, 0.75, fz + 0.35), (0.34, 0.72, 0.012), 'fridge', rnd=0.01)
    with S.tag('freezer'):
        S.wbox((fx, 1.8, fz), (0.37, 0.3, 0.34), 'enamel', rnd=0.1)
        S.wboxr(fx - 0.33, 1.52, fz + 0.34, fx + 0.33, 2.06, fz + 0.36, 'enamel', rnd=0.02)
        S.wboxr(fx + 0.22, 1.6, fz + 0.36, fx + 0.27, 1.95, fz + 0.4, 'steel')
    S.ell(WORLD, (fx, 0.003, fz + 0.55), (0.25, 0.004, 0.1), 'steel')                 # the puddle under the door

    # ---------------------------------------------------------------- Devin (overlays: one pose shows at a time)
    if 'devin_fridge' not in hide:
        npc.cast(S, 'devin', dict(npc.ARMS_FOLDED, lean=-9, pyaw=6, sway=3, hp=10, hy=-24, hr=-6,
                                  lhp=4, labd=1, lk=6, rhp=16, rabd=-7, rk=10, rfp=-14),
                 (fx + 0.02, 0, fz + 0.62), yaw=-14, scale=0.96, tag='devin_fridge')
    if 'devin_couch' not in hide:
        npc.cast(S, 'devin', dict(npc.SEATED, lsp=20, le=60, lin=30, rsp=22, re=64, rin=30, lean=14, hp=8),
                 (cx - 0.05, 0.02, cz + 0.45), yaw=-90, scale=0.96, tag='devin_couch')

    # ---------------------------------------------------------------- lights
    S.light((lx, 1.5, lz), (255, 200, 140), power=4.0, range=8, shadow=False, vol=0.15)             # floor lamp
    S.light((DINING[0], 2.4, DINING[1]), (255, 222, 180), power=1.6, range=4, soft=16)              # pendant glow
    S.light((KD1 - 0.3, 1.0, KZ + 0.3), (255, 196, 130), power=2.5, range=4, soft=10, vol=0.15)    # Kenji's desk lamp
    S.light((3.4, 1.45, ZB + 0.3), (240, 236, 220), power=1.6, range=3.5, shadow=False)           # under-cabinet strip
    S.light((2.3, 1.7, -1.3), (255, 226, 196), power=1.3, range=3.0, shadow=False)                 # soft fill on the fridge
    S.light((X1 - 0.2, 1.4, 0.4), (240, 236, 220), power=1.4, range=3.5, shadow=False)
    S.light((X1 + 1.5, 2.2, -0.25), (140, 160, 230), power=6, range=8, vol=0.3, soft=20)          # street light
    S.light((cx - 0.9, 0.7, cz + 0.25), (200, 210, 255), power=0.6, range=2, shadow=False)        # laptop glow
    S.light((0.0, 1.7, 4.5), (255, 226, 196), power=2.4, range=12, soft=24)                        # spill from the hall

    cam = Camera((0.1, 2.95, 7.6), (0.1, 0.65, -2.2), fov=42, W=3840, H=2160)
    env = dict(sky=(30, 30, 36), bounce=(30, 24, 20), fog_col=(30, 28, 30), fog=0.02, fog_h0=0.0, fog_hf=0.05,
               fog_max=40, vol_scale=4, vol_steps=40, reflections=True, grid=0.5, ao_scale=0.9)
    meta = dict(
        room='kenji_apartment',
        walk=[(-3.5, -2.9), (2.7, -2.9), (2.7, -1.95), (4.05, -1.95), (4.05, 2.6), (-3.95, 2.6), (-3.95, 1.2),
              (-3.85, 1.2), (-3.85, 0.55), (-4.05, 0.55), (-4.05, -1.75), (-3.5, -1.75)],
        walk_zmin=-2.9, walk_zmax=2.6, scale_x=0.0,
        spawns={'drive': (-3.8, -2.6), 'mulholland_overlook': (-3.8, -2.6), 'norms_diner': (-3.8, -2.6),
                'start': (0.0, 1.5)},
        hotspots={
            'devin': ('Devin', (2.55, -1.75), 'right'),
            'devin_couch': ('Devin', (-1.0, 0.3), 'left'),
            'kenji_desk': ("Kenji's desk", (0.7, -2.75), 'up'),
            'dashcam_box': ('box on the shelf', (0.7, -2.75), 'up'),
            'certificate': ('certificate', (0.7, -2.75), 'up'),
            'pennant': ('Dodgers pennant', (0.7, -2.75), 'up'),
            'camera_bag': ('camera bag', (-2.95, -2.7), 'up'),
            'sneakers': ('wet sneakers', (-3.3, -2.5), 'left'),
            'laptop': ('laptop', (-3.1, 1.0), 'up'),
            'photos': ('photos on the wall', (-1.2, -2.5), 'up'),
            'tv': ('TV', (-3.7, 1.0), 'left'),
            'dining': ('dining table', (0.6, 1.4), 'right'),
            'fridge': ('fridge', (3.3, -1.8), 'up'),
            'freezer': ('freezer', (3.3, -1.8), 'up'),
            'sink': ('sink', (3.95, -0.25), 'right'),
            'devin_door': ("Devin's door", (2.35, -2.75), 'up'),
            'front_door': ('front door', (-3.8, -2.75), 'up'),
        },
        hotspot_shapes={
            'devin': [(fx - 0.32, 0.0, fz + 0.75), (fx + 0.36, 0.0, fz + 0.75), (fx + 0.36, 1.78, fz + 0.75),
                      (fx - 0.32, 1.78, fz + 0.75)],
            'devin_couch': [(cx - 0.5, 0.45, cz + 0.5), (cx + 0.3, 0.45, cz + 0.5), (cx + 0.3, 1.45, cz + 0.5),
                            (cx - 0.5, 1.45, cz + 0.5)],
            'laptop': [(cx - 1.35, 0.42, cz + 0.45), (cx - 0.95, 0.42, cz + 0.45), (cx - 0.95, 0.75, cz + 0.2),
                       (cx - 1.35, 0.75, cz + 0.2)],
        },
        hotspot_order=['photos', 'front_door', 'devin_door', 'kenji_desk', 'certificate', 'pennant', 'dashcam_box',
                       'camera_bag', 'sneakers', 'tv', 'dining', 'sink', 'fridge', 'freezer', 'laptop', 'devin_couch', 'devin'],
        overlays=['devin_fridge', 'devin_couch'],
        occluders={'couch': (cx + 0.45, cz + 1.0), 'table': (cx - 1.1, cz + 0.65), 'dining': (DINING[0], DINING[1] + 0.95)},
        obstacles=[(cx, cz - 0.6, 0.55), (cx, cz + 0.6, 0.55), (cx - 1.1, cz - 0.35, 0.4), (cx - 1.1, cz + 0.35, 0.4),
                   (DINING[0] - 0.45, DINING[1], 0.7), (DINING[0] + 0.45, DINING[1], 0.7), (DINING[0] + 1.05, DINING[1] + 0.1, 0.3),
                   (cx + 0.1, cz - 1.35, 0.2), (-4.15, 0.8, 0.3)],
        char_fill=((236, 220, 200), 0.2),
        tint=(0.86, 0.8, 0.74),
        exposure=1.45,
    )
    return S, cam, env, meta
