"""The roof of Stardust Memorabilia, 3:20 a.m. (Case 3, scene 4), looking out over Hollywood Boulevard.

Tar and gravel in the rain. The giant STARDUST letters stand along the front edge on a steel lattice, facing the
boulevard, so from up here they read backwards. An old wooden water tank on rusted steel legs, a ladder up its side and
a hatch on top. The roof door in its little bulkhead, a plastic lawn chair and a coffee can of cigar ends beside it.
Across a six-foot gap, Charlie on the fire escape of the building next door, under an umbrella, smoking a pipe. Two
roofs over, the Blue Note's sign; across the boulevard, the Chinese Theatre's pagoda roof.

Two lighting states (two rooms, one set): build(dark=True) is the roof with the sign switched off at its 1:00 timer,
almost black but for the door behind Ray and the city glow (stardust_roof_dark.py); the default is the sign back on,
painting the wet gravel red and gold. Overlays in the lit room: the flickering U (neon_u), and the glint of the gold
star earring by the door (earring)."""
import math, random
import numpy as np
from scene3d import *
import textures as tx
import npc

X0, X1 = -5.6, 5.0            # roof edges (x); the front edge with the sign is at ZF, the back at ZK
ZF, ZK = -3.9, 5.5
PARA = 0.55                   # parapet height
LETTERS = 'STARDUST'
LX0, LX1 = -2.9, 4.5          # the sign's extent
LH = 1.85                     # six-foot letters
LZ = ZF + 0.35                # the letters stand just inside the front parapet
TANK = (-4.55, -2.35)         # the water tank (x, z), in the front left corner
DOOR = (-4.2, 4.55)           # the roof door, in the right side of the bulkhead (x, z of the door's centre)
GLINT = (-3.7, 4.05)          # the earring, right at the top of the stairs
CHAIR = (-2.7, 4.75)          # Gus's lawn chair
CHARLIE = (6.15, 0.5)         # on the fire escape across the gap
GAP = 6.6                     # the next building's wall (x)


def build(hide=(), dark=False):
    S = Scene()
    rng = random.Random(35)
    # ---------------------------------------------------------------- materials
    S.mat('gravel', (255, 255, 255), tex=tx.hires(tx.tar_gravel(), 2), texmode=4, texmap=1, texscale=1.6, refl=0.3,
          ripple=0.25, spec=0.6, shin=50, bump=0.15, bscale=40)
    S.mat('puddle', (24, 24, 28), refl=0.9, ripple=0.08, spec=1.0, shin=120)
    S.mat('parapet', (110, 104, 96), namp=0.25, nscale=5, refl=0.05)
    S.mat('coping', (140, 136, 128), spec=0.3)
    S.mat('brick', (255, 255, 255), tex=tx.hires(tx.brick(5, base=(96, 54, 44)), 2), texmode=4, texmap=1, texscale=2.4)
    S.mat('steel', (60, 60, 64), spec=0.7, shin=40, refl=0.1)
    S.mat('rust', (96, 54, 36), namp=0.4, nscale=8, spec=0.3)
    S.mat('tank', (255, 255, 255), tex=tx.hires(tx.tank_staves(), 2), texmode=4, texmap=1, texscale=1.4, spec=0.3)
    S.mat('tank_roof', (60, 50, 44), namp=0.3, nscale=6, spec=0.4, refl=0.15)
    S.mat('hoop', (60, 40, 30), spec=0.6, shin=40)
    S.mat('bulkhead', (120, 110, 98), namp=0.2, nscale=5)
    S.mat('door', (70, 50, 40), spec=0.3, namp=0.1, nscale=8)
    S.mat('doorway', (255, 200, 140), emis=(255, 190, 120), emis_mult=0.9)
    S.mat('chair', (220, 220, 210), spec=0.4)
    S.mat('strap', (40, 120, 90), spec=0.4)
    S.mat('can', (150, 150, 150), spec=1.0, shin=60, namp=0.3, nscale=20)
    S.mat('cigar', (90, 54, 30), spec=0.2)
    S.mat('ash', (150, 146, 140))
    S.mat('print', (12, 12, 14), refl=0.5, spec=1.0, shin=80)
    S.mat('gold', (230, 180, 70), spec=2.0, shin=120, emis=(255, 220, 140), emis_mult=0.6)
    S.mat('vent', (130, 132, 136), spec=0.8, shin=40, refl=0.1)
    S.mat('tarpaper', (30, 30, 32), spec=0.4, refl=0.2)
    S.mat('grate', (40, 40, 44), spec=0.6)
    S.mat('window_lit', (60, 50, 40), emis=(255, 196, 120), emis_mult=0.8)
    S.mat('window_dk', (16, 18, 24), spec=1.0, refl=0.3)
    S.mat('pagoda', (52, 100, 82), namp=0.2, nscale=1.5, spec=0.5, shin=30)
    S.mat('pagoda_dk', (30, 60, 50), namp=0.2, nscale=2)
    S.mat('facade', (120, 30, 24), namp=0.2, nscale=2)
    S.mat('column', (170, 36, 28), spec=0.4, shin=30)
    S.mat('bldg', (40, 38, 46), tex=tx.windows_grid(41, 10, 6, lit=0.18), texmode=3, texemis=1.0)
    S.mat('bldg2', (40, 38, 46), tex=tx.windows_grid(42, 8, 8, lit=0.12, warm=False), texmode=3, texemis=0.9)
    S.mat('sky', (16, 12, 24), tex=tx.skyline(19, 1024, 256, k=3), texmode=3, texemis=1.0)
    S.mat('neon_blue', (20, 20, 30), tex=tx.neon_text('BLUE NOTE', (80, 150, 255), size=72,
          fnt='DejaVuSerif-BoldItalic.ttf'), texmode=2, texemis=5.0)
    S.mat('backing', (16, 14, 20), spec=0.2)
    S.mat('umbrella_c', (20, 20, 24), spec=0.5)
    for i, ch in enumerate(LETTERS):
        col = (255, 70, 50) if i % 2 == 0 else (255, 186, 70)                       # red and gold
        lit = not dark and not (ch == 'U' and 'neon_u' in hide)
        if lit:
            S.mat(f'letter{i}', (34, 30, 30), tex=tx.stardust_letter(ch, col), texmode=3, texemis=3.2, spec=0.4)
        else:                                                                       # cold glass tubes on steel
            S.mat(f'letter{i}', (255, 255, 255), tex=tx.stardust_letter(ch, (90, 84, 84)), texmode=1, spec=0.6)

    # ---------------------------------------------------------------- the roof and its parapet
    S.wboxr(X0, -0.3, ZF, X1, 0.0, ZK, 'gravel')
    for (x, z, rx, rz) in ((-1.0, 1.4, 1.1, 0.5), (0.8, -1.6, 0.8, 0.4), (-2.2, 3.4, 0.7, 0.35), (1.6, 0.8, 0.5, 0.25)):
        S.ell(WORLD, (x, 0.0, z), (rx, 0.012, rz), 'puddle')                        # rain puddles
    S.wboxr(X0 - 0.25, 0, ZF - 0.25, X1 + 0.25, PARA, ZF, 'parapet')                  # front
    S.wboxr(X0 - 0.25, 0, ZF, X0, PARA, ZK, 'parapet')                                 # left
    S.wboxr(X1, 0, ZF, X1 + 0.25, PARA, ZK, 'parapet')                                 # right
    for (a, b, c, d) in ((X0 - 0.28, ZF - 0.28, X1 + 0.28, ZF + 0.03), (X0 - 0.28, ZF, X0 + 0.03, ZK),
                         (X1 - 0.03, ZF, X1 + 0.28, ZK)):
        S.wboxr(a, PARA, b, c, PARA + 0.06, d, 'coping')
    # the building's own walls dropping away below the parapets (seen past the edges)
    S.wboxr(X0 - 0.25, -12, ZF - 0.25, X1 + 0.25, 0, ZF, 'brick')
    S.wboxr(X1, -12, ZF, X1 + 0.25, 0, ZK, 'brick')

    # ---------------------------------------------------------------- the STARDUST sign: steel lattice, eight letters
    with S.tag('neon'):
        n = len(LETTERS)
        lw = (LX1 - LX0) / n
        for i, ch in enumerate(LETTERS):
            cx = LX1 - (i + 0.5) * lw                          # seen from behind: S on the right, T on the left
            S.wbox((cx, PARA + 0.35 + LH / 2, LZ), (lw / 2 - 0.06, LH / 2, 0.04), f'letter{i}', rot=Ry(180))
        # the lattice behind the letters (between them and the roof), and its braces down to the roof
        for y in (PARA + 0.45, PARA + 0.35 + LH * 0.5, PARA + 0.3 + LH):
            S.wboxr(LX0, y - 0.03, LZ + 0.1, LX1, y + 0.03, LZ + 0.16, 'steel')
        for x in np.arange(LX0, LX1 + 0.01, lw):
            S.wboxr(x - 0.03, 0, LZ + 0.1, x + 0.03, PARA + 0.35 + LH, LZ + 0.16, 'steel')
            S.cyl((x, PARA + 0.3 + LH * 0.8, LZ + 0.13), (x, 0.0, LZ + 1.3), 0.025, 'rust')
        for x in np.arange(LX0, LX1, lw):                                          # cross bracing
            S.cyl((x, PARA + 0.45, LZ + 0.13), (x + lw, PARA + 0.3 + LH, LZ + 0.13), 0.015, 'steel')
        S.wboxr(LX0 - 0.1, 0, LZ + 0.6, LX0 + 0.3, 0.5, LZ + 1.0, 'steel')                 # transformer box
        S.cyl((LX0 + 0.1, 0.5, LZ + 0.8), (LX0 + 0.1, PARA + 0.45, LZ + 0.15), 0.02, 'steel')
    if not dark:
        for i in range(4):                                                          # the sign lights the roof
            x = LX0 + (i + 0.5) * (LX1 - LX0) / 4
            col = (255, 80, 50) if i % 2 else (255, 170, 70)
            if 'neon_u' in hide and i == 1:
                col = (255, 120, 70)
            S.light((x, PARA + 1.2, LZ + 0.5), col, power=5.5, range=9, soft=16, vol=0.35)
        if 'neon_u' not in hide:
            ux = LX1 - (LETTERS.index('U') + 0.5) * (LX1 - LX0) / len(LETTERS)
            S.light((ux, PARA + 1.3, LZ + 0.3), (255, 186, 70), power=2.5, range=6, soft=10, vol=0.3)

    # ---------------------------------------------------------------- the water tank on its legs
    tx_, tz_ = TANK
    with S.tag('water_tank'):
        legs_h = 1.7
        for (sx, sz) in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
            x, z = tx_ + sx * 0.8, tz_ + sz * 0.8
            S.wboxr(x - 0.06, 0, z - 0.06, x + 0.06, legs_h, z + 0.06, 'rust')
        S.cyl((tx_ - 0.8, 0.3, tz_ + 0.8), (tx_ + 0.8, legs_h - 0.2, tz_ + 0.8), 0.025, 'rust')     # cross bracing
        S.cyl((tx_ + 0.8, 0.3, tz_ + 0.8), (tx_ - 0.8, legs_h - 0.2, tz_ + 0.8), 0.025, 'rust')
        S.wboxr(tx_ - 1.0, legs_h, tz_ - 1.0, tx_ + 1.0, legs_h + 0.1, tz_ + 1.0, 'rust')
        S.fcyl((tx_, legs_h + 0.1 + 1.1, tz_), 1.05, 1.1, 'tank')                    # the barrel, 2.2 m of staves
        for y in (0.35, 1.1, 1.85):
            S.fcyl((tx_, legs_h + 0.1 + y, tz_), 1.07, 0.03, 'hoop')
        S.tcyl(Frame((tx_, legs_h + 2.2 + 0.28, tz_)), (0, 0, 0), (0.15, 0.15), (1.15, 1.15), 0.28, 'tank_roof')  # conical cap
        S.wboxr(tx_ - 0.25, legs_h + 2.5, tz_ + 0.35, tx_ + 0.25, legs_h + 2.6, tz_ + 0.75, 'tank_roof')  # the hatch
        # the ladder up the front, toward the roof door
        for sx in (-1, 1):
            S.cyl((tx_ + sx * 0.22, 0, tz_ + 1.12), (tx_ + sx * 0.22, legs_h + 2.4, tz_ + 1.12), 0.022, 'rust')
        for y in np.arange(0.3, legs_h + 2.3, 0.3):
            S.cyl((tx_ - 0.22, y, tz_ + 1.12), (tx_ + 0.22, y, tz_ + 1.12), 0.015, 'rust')

    # ---------------------------------------------------------------- the roof door bulkhead, the lawn chair, the can
    bx0, bx1, bz0, bz1 = X0, -4.3, 3.5, ZK                       # the bulkhead over the stairs, back left corner
    if 'roof_door' not in hide:
        with S.tag('roof_door'):
            S.wboxr(bx0, 0, bz0, bx1, 2.5, bz1, 'bulkhead')
            S.wboxr(bx0, 2.5, bz0 - 0.1, bx1 + 0.1, 2.6, bz1, 'tarpaper')
            S.wboxr(bx1 - 0.05, 0, DOOR[1] - 0.5, bx1 + 0.1, 2.1, DOOR[1] + 0.5, 'doorway')     # the lit stairwell
            S.wboxr(bx1 + 0.04, 0, DOOR[1] - 0.56, bx1 + 0.12, 2.16, DOOR[1] - 0.5, 'door')    # frame
            S.wboxr(bx1 + 0.04, 0, DOOR[1] + 0.5, bx1 + 0.12, 2.16, DOOR[1] + 0.56, 'door')
            S.wboxr(bx1 + 0.04, 2.1, DOOR[1] - 0.56, bx1 + 0.12, 2.16, DOOR[1] + 0.56, 'door')
            D = Frame((bx1 + 0.08, 0, DOOR[1] - 0.5), Ry(-80))                                 # propped open on a brick
            S.box(D, (0.5, 1.05, 0.0), (0.49, 1.04, 0.03), 0.0, 'door')
            S.wboxr(bx1 + 0.25, 0, DOOR[1] - 1.15, bx1 + 0.45, 0.1, DOOR[1] - 1.0, 'brick')
    S.light((bx1 + 0.6, 1.9, DOOR[1]), (255, 196, 130), power=1.8 if not dark else 2.4, range=4.5, soft=12, vol=0.2)
    cx, cz = CHAIR
    if 'lawn_chair' not in hide:
        with S.tag('lawn_chair'):
            F = Frame((cx, 0, cz), Ry(20))
            for sx in (-1, 1):
                S.cyl(F.to((sx * 0.28, 0.0, 0.3)), F.to((sx * 0.28, 0.38, -0.25)), 0.015, 'chair')
                S.cyl(F.to((sx * 0.28, 0.0, -0.3)), F.to((sx * 0.28, 0.38, 0.25)), 0.015, 'chair')
                S.cyl(F.to((sx * 0.28, 0.38, -0.25)), F.to((sx * 0.28, 0.95, -0.42)), 0.015, 'chair')
                S.cyl(F.to((sx * 0.28, 0.55, 0.28)), F.to((sx * 0.28, 0.55, -0.3)), 0.016, 'chair')
            for k in range(5):
                S.box(F, (0, 0.38, -0.2 + k * 0.1), (0.27, 0.008, 0.03), 0.0, 'strap')
                S.box(F, (0, 0.5 + k * 0.1, -0.3 - k * 0.025), (0.27, 0.03, 0.008), 0.0, 'strap', rot=Rx(-15))
    # the cigar ends are rolled before the hide check, so rng stays in step when the can is hidden
    cigars = [((cx + 0.55 + rng.uniform(-0.05, 0.05), 0.26, cz - 0.15 + rng.uniform(-0.05, 0.05)),
               (cx + 0.55 + rng.uniform(-0.06, 0.06), 0.31, cz - 0.15 + rng.uniform(-0.06, 0.06))) for k in range(5)]
    if 'coffee_can' not in hide:
        with S.tag('coffee_can'):
            S.fcyl((cx + 0.55, 0.13, cz - 0.15), 0.1, 0.13, 'can')
            for (c0, c1) in cigars:
                S.cyl(c0, c1, 0.012, 'cigar')
    S.ell(WORLD, (cx + 0.1, 0.0, cz - 0.7), (0.3, 0.01, 0.18), 'puddle')
    S.cyl((cx + 0.02, 0.008, cz - 0.68), (cx + 0.14, 0.008, cz - 0.74), 0.013, 'cigar')                  # his last one
    S.sph((cx + 0.15, 0.008, cz - 0.745), 0.012, 'ash')

    # ---------------------------------------------------------------- the gravel: heel prints from the door to the tank
    with S.tag('gravel'):
        path = [(bx1 + 0.5, DOOR[1] - 0.2), (-3.3, 2.6), (-3.6, 0.4), (tx_ + 0.2, tz_ + 1.4)]
        for leg, off in ((0, -0.09), (1, 0.09)):
            pts = path if leg == 0 else path[::-1]
            for (a, b) in zip(pts, pts[1:]):
                d = math.hypot(b[0] - a[0], b[1] - a[1])
                nx, nz = -(b[1] - a[1]) / d, (b[0] - a[0]) / d
                for t in np.arange(0.12, d, 0.42):
                    side = 1 if int(t / 0.42) % 2 else -1
                    x = a[0] + (b[0] - a[0]) * t / d + nx * (off + side * 0.06)
                    z = a[1] + (b[1] - a[1]) * t / d + nz * (off + side * 0.06)
                    S.ell(WORLD, (x, 0.0, z), (0.035, 0.008, 0.035), 'print')               # a small heel
    if 'earring' not in hide and not dark:
        with S.tag('earring'):                                                          # a gold star in the gravel
            gx, gz = GLINT
            for k in range(5):
                t = math.radians(k * 72)
                S.cyl((gx, 0.015, gz), (gx + 0.035 * math.sin(t), 0.015, gz + 0.035 * math.cos(t)), 0.009, 'gold')
            S.light((gx, 0.12, gz + 0.05), (255, 220, 150), power=0.08, range=0.5, shadow=False)

    # ---------------------------------------------------------------- vents and pipes (the foreground, left)
    if 'vents' not in hide:
        with S.tag('vents'):
            S.fcyl((3.9, 0.55, 4.5), 0.32, 0.55, 'vent')
            S.tcyl(Frame((3.9, 1.2, 4.5)), (0, 0, 0), (0.08, 0.08), (0.5, 0.5), 0.1, 'vent')
            S.fcyl((3.9, 1.12, 4.5), 0.2, 0.06, 'grate')
            S.wboxr(1.6, 0, 4.8, 2.9, 0.75, 5.5, 'vent')                                       # an old AC unit
            S.wboxr(1.65, 0.1, 4.78, 2.85, 0.65, 4.8, 'grate')
            for k in range(9):                                                           # louvres
                S.wboxr(1.68, 0.14 + k * 0.055, 4.76, 2.82, 0.16 + k * 0.055, 4.79, 'vent')
            S.fcyl((2.25, 0.77, 5.15), 0.28, 0.02, 'grate')                                 # the fan on top
            S.fcyl((2.25, 0.79, 5.15), 0.06, 0.02, 'vent')
            S.cyl((4.8, 0.3, 4.5), (3.9, 0.3, 4.5), 0.06, 'rust')
    S.cyl((4.8, 0.3, 4.5), (4.8, 0.3, -1.0), 0.06, 'rust')         # a pipe along the parapet, behind Ray (not a walk-behind)

    # ---------------------------------------------------------------- next door: brick wall, the fire escape, Charlie
    S.wboxr(GAP, -12, ZF - 6, GAP + 4, 4.5, ZK + 4, 'brick')
    for (wy, wz) in ((1.6, -2.2), (1.6, 3.2), (-1.5, 0.4)):
        S.wboxr(GAP - 0.02, wy, wz - 0.5, GAP, wy + 1.3, wz + 0.5, 'window_lit' if wz == 0.4 or wz == 3.2 else 'window_dk')
    with S.tag('charlie'):
        fx0, fx1, fz0, fz1, fy = GAP - 0.9, GAP, -0.6, 1.8, 0.45
        S.wboxr(fx0, fy - 0.04, fz0, fx1, fy, fz1, 'grate')                              # grating
        for z in np.arange(fz0, fz1 + 0.01, 0.6):
            S.cyl((fx0, fy, z), (fx0, fy + 1.0, z), 0.018, 'steel')
        S.cyl((fx0, fy + 1.0, fz0), (fx0, fy + 1.0, fz1), 0.02, 'steel')
        S.cyl((fx0, fy + 0.5, fz0), (fx0, fy + 0.5, fz1), 0.014, 'steel')
        S.cyl((fx0, fy, fz0), (fx1, fy - 0.5, fz0 - 0.4), 0.02, 'steel')               # brackets
        S.cyl((fx0, fy, fz1), (fx1, fy - 0.5, fz1 + 0.4), 0.02, 'steel')
        S.wboxr(GAP - 0.02, fy, 0.0, GAP, fy + 2.0, 0.9, 'window_lit')                     # his window behind him
        npc.cast(S, 'charlie', dict(npc.STAND, props=(('pipe', 'r'), ('umbrella', 'l')), rsp=24, re=96, rin=24,
                                    lsp=12, le=74, lin=8, hp=4, hy=-12),
                 (CHARLIE[0], fy, CHARLIE[1]), yaw=-78, scale=0.9)
    S.light((GAP - 0.4, fy + 1.4, 0.45), (255, 200, 130), power=1.6 if not dark else 0.5, range=3.0, soft=12)

    # ---------------------------------------------------------------- the city: the Blue Note two roofs over, the theatre
    S.wboxr(-24, -12, -16, -9.5, 0.4, -5, 'bldg')                                        # the roofs to the left
    S.wboxr(-24, -12, -5, -8.0, 1.6, 6, 'bldg2')
    with S.tag('blue_note'):
        bnx, bnz = -11.6, -8.0
        S.cyl((bnx - 1.4, 0.4, bnz), (bnx - 1.4, 2.6, bnz), 0.05, 'steel')
        S.cyl((bnx + 1.4, 0.4, bnz), (bnx + 1.4, 2.6, bnz), 0.05, 'steel')
        S.wbox((bnx, 3.1, bnz), (2.2, 0.6, 0.06), 'backing', rot=Ry(20))
        S.wbox((bnx + 0.034, 3.1, bnz + 0.094), (2.1, 0.55, 0.02), 'neon_blue', rot=Ry(20))   # in front of the backing
    S.light((-11.6, 1.6, -7.4), (80, 140, 255), power=3, range=6, vol=0.1, shadow=False)
    with S.tag('theatre'):
        tz = -46.0
        S.wboxr(-12, -14, tz - 6, 12, 1.0, tz, 'facade')
        for x in (-4.5, 4.5):
            S.cyl((x, -14, tz + 1.2), (x, 2.0, tz + 1.2), 0.9, 'column')
        S.tcyl(Frame((0, 3.0, tz - 2.0)), (0, 0, 0), (7.0, 2.6), (14.0, 6.0), 1.6, 'pagoda')          # lower roof
        S.tcyl(Frame((0, 5.7, tz - 2.6)), (0, 0, 0), (2.4, 1.1), (6.8, 3.0), 1.2, 'pagoda')           # upper roof
        S.tcyl(Frame((0, 4.5, tz - 2.4)), (0, 0, 0), (6.6, 2.6), (6.6, 2.6), 0.3, 'pagoda_dk')
        S.cyl((0, 6.9, tz - 2.6), (0, 8.2, tz - 2.6), 0.18, 'pagoda')
    for x in (-7.0, 0.0, 7.0):
        S.light((x, 0.5, tz + 5), (255, 170, 100), power=70, range=16, shadow=False)              # floodlights
    S.light((0.0, 9.0, tz + 4), (255, 150, 90), power=30, range=14, shadow=False)
    S.wboxr(-40, -14, -70, -12, 9, -52, 'bldg')                                           # across the boulevard
    S.wboxr(12, -14, -66, 40, 12, -50, 'bldg2')
    S.wbox((0, 6, -120), (140, 34, 1), 'sky')
    S.light((0.0, -9.0, -18), (255, 160, 90), power=60, range=30, shadow=False)            # the boulevard's glow below
    S.sun((0.3, -1, -0.5), (70, 80, 120), power=0.22 if not dark else 0.1, shadow=False)

    cam = Camera((0.4, 3.3, 11.2), (-0.2, 1.3, -3.5), fov=44, W=3840, H=2160)
    env = dict(sky=(22, 22, 36), bounce=(14, 12, 18), fog_col=(26, 20, 34), fog=0.022, fog_h0=0.0, fog_hf=0.12,
               fog_max=140, vol_scale=4, vol_steps=40, reflections=True, grid=0.75, ao_scale=1.3)
    walk = [(-5.1, -1.05), (-3.2, -1.05), (-3.2, -2.85), (4.6, -2.85), (4.6, 4.2), (1.4, 4.2), (1.4, 5.1),
            (-4.15, 5.1), (-4.15, 3.4), (-5.1, 3.4)]
    meta = dict(
        room='stardust_roof',
        walk=walk,
        walk_zmin=-2.8, walk_zmax=5.0, scale_x=0.0,
        spawns={'stardust_office': (DOOR[0] + 0.75, DOOR[1]), 'start': (0.0, 2.0)},
        hotspots={
            'charlie': ('Charlie', (4.3, 0.5), 'right'),
            'neon': ('neon letters', None, 'up'),
            'water_tank': ('water tank', (tx_ + 0.2, tz_ + 1.65), 'up'),
            'gravel': ('gravel', (-2.6, 1.6), 'left'),
            'glint': ('something gold', (GLINT[0] + 0.35, GLINT[1] - 0.15), 'left'),
            'lawn_chair': ('lawn chair', (CHAIR[0] + 0.25, CHAIR[1] - 0.75), 'left'),
            'coffee_can': ('coffee can', (CHAIR[0] + 0.25, CHAIR[1] - 0.75), 'left'),
            'blue_note': ('Blue Note sign', None, 'left'),
            'theatre': ('Chinese Theatre', None, 'up'),
            'roof_edge': ('roof edge', (4.3, -1.4), 'right'),
            'roof_door': ('roof door', (DOOR[0] + 0.8, DOOR[1]), 'left'),
        },
        hotspot_shapes={
            'gravel': [(-3.9, 0.0, -0.4), (-2.6, 0.0, -0.4), (-2.6, 0.0, 3.3), (-3.9, 0.0, 3.3)],
            'glint': [(GLINT[0] - 0.5, 0.0, GLINT[1] - 0.4), (GLINT[0] + 0.15, 0.0, GLINT[1] - 0.4),
                      (GLINT[0] + 0.15, 0.0, GLINT[1] + 0.6), (GLINT[0] - 0.5, 0.0, GLINT[1] + 0.6)],
            'charlie': [(CHARLIE[0], 0.4, CHARLIE[1] - 0.45), (CHARLIE[0], 0.4, CHARLIE[1] + 0.45),
                        (CHARLIE[0], 2.5, CHARLIE[1] + 0.45), (CHARLIE[0], 2.5, CHARLIE[1] - 0.45)],
            'roof_edge': [(X1 - 0.1, 0.0, -2.6), (X1 + 0.3, 0.0, -2.6), (X1 + 0.3, 0.7, 1.6), (X1 - 0.1, 0.7, 1.6)],
            'theatre': [(-14, -2, -46), (14, -2, -46), (14, 8.5, -46), (-14, 8.5, -46)],
        },
        hotspot_order=['theatre', 'blue_note', 'neon', 'roof_edge', 'gravel', 'water_tank', 'lawn_chair', 'coffee_can',
                       'roof_door', 'charlie', 'glint'],
        overlays=['neon_u', 'earring'],
        occluders={'vents': (2.25, 4.8), 'roof_door': (-4.95, 3.5), 'lawn_chair': (CHAIR[0] + 0.1, CHAIR[1] + 0.3),
                   'coffee_can': (CHAIR[0] + 0.55, CHAIR[1] - 0.05)},
        obstacles=[(CHAIR[0], CHAIR[1], 0.5)],
        char_fill=((220, 200, 210), 0.16),
        tint=(0.86, 0.66, 0.6),
        exposure=1.5,
    )
    if dark:
        meta.update(
            room='stardust_roof_dark',
            walk=[(-4.15, 3.6), (-2.9, 3.6), (-2.9, 5.1), (-4.15, 5.1)],
            walk_zmin=3.6, walk_zmax=5.1,
            spawns={'stardust_office': (DOOR[0] + 0.75, DOOR[1]), 'start': (DOOR[0] + 0.75, DOOR[1])},
            hotspots={'darkness': ('darkness', None, 'left'), 'roof_door': ('roof door', (2.5, DOOR[1]), 'right')},
            hotspot_shapes={},
            screen_shapes={'darkness': [(0, 0), (1920, 0), (1920, 1080), (0, 1080)]},
            hotspot_order=['darkness', 'roof_door'],
            overlays=[], obstacles=[],
            char_fill=((200, 190, 210), 0.1),
            tint=(0.5, 0.5, 0.62),
            exposure=0.85,
        )
    return S, cam, env, meta
