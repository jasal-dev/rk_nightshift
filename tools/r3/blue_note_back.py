"""The Blue Note's back room, 5:05 a.m. (Case 5, scene 3): Sal's storeroom and office, and the short back hall.

A storeroom that doubles as an office. Kegs along the back wall, cases of liquor stacked to the ceiling, a steel desk
under a gooseneck lamp with a cash box and a pile of mail. A row of six staff lockers, one standing open with a ring of
keys hanging from its lock. A water pipe runs the width of the room, a cut length of white clothesline hanging from it;
under it a step stool on its side, well away from the pipe. Sal on the concrete under a gray sheet, one hand and a
cardigan sleeve at its edge, and Dr. Shah kneeling beside him under her work light. To the left, past a stub of wall, the
back hall: the steel door to the alley, the coat hooks with Sal's coat and a red umbrella dripping into a puddle, and the
heavy white door of the walk-in cooler with a strip of light under it. The door back to the bar is in the right wall.

Overlays: the cooler door, shut (cooler_shut; open and lit behind it once Nina is out), Nina in Ray's raincoat on a
chair by the desk (nina), and Officer Park in the back hall (park), both y-sorted (overlay_bases)."""
import math, random
import numpy as np
from scene3d import *
import textures as tx
import npc

X0, X1, ZB, ZF, H = -5.2, 4.4, -4.0, 3.2, 3.0
HALL_X = -2.5                 # the stub wall between the back hall (left) and the storeroom
COOLER_Z = (-2.95, -1.45)     # the cooler door, in the left wall
ALLEY = (-4.5, -3.45)         # the alley door (x), in the back wall
SAL = (0.9, -1.2)             # Sal's body, under the sheet (centre), lying along x, his head to the right
PIPE_Z = -1.4
ROPE_X = 0.55
STOOL = (1.8, -0.62)         # the step stool, on its side, four feet from where he hung
SHAH = (0.3, -2.0)
DESK = (2.85, -2.9)           # the desk's centre, against the back wall at the right
NINA = (1.5, -2.25)          # Nina on the desk chair, in Ray's raincoat and Shah's blanket
PARK = (-3.75, -1.7)         # Park in the back hall, by the cooler
LOCKERS_X = (-2.2, 0.4)       # six lockers along the back wall; Danny's is the fourth
BAR_DOOR = (0.6, 1.6)         # the door to the bar (z), in the right wall
FG_CRATES = (-3.2, 2.6)       # beer crates stacked near us, at the left
FG_TRUCK = (2.3, 2.75)        # a hand truck with a keg on it, at the right


def build(hide=()):
    S = Scene()
    rng = random.Random(77)
    # ---------------------------------------------------------------- materials
    S.mat('floor', (150, 146, 138), tex=tx.hires(tx.concrete(seed=61, base=(118, 116, 110)), 2), texmode=4, texmap=1,
          texscale=2.2, spec=0.3, shin=30, refl=0.05)
    S.mat('wall', (176, 168, 146), namp=0.15, nscale=4, bump=0.06, bscale=10)             # painted block, nicotine yellow
    S.mat('wall_lo', (90, 96, 84), namp=0.1, nscale=4)
    S.mat('ceiling', (120, 116, 108), namp=0.1, nscale=6)
    S.mat('pipe', (120, 110, 96), spec=0.7, shin=40, namp=0.2, nscale=20)
    S.mat('rope', (236, 232, 222), namp=0.2, nscale=60)
    S.mat('steel', (130, 134, 138), spec=1.0, shin=50)
    S.mat('steel_dk', (70, 74, 78), spec=0.8, shin=40)
    S.mat('locker', (70, 96, 110), spec=0.7, shin=40, namp=0.05, nscale=30)
    S.mat('locker_in', (40, 50, 56))
    S.mat('label_d', (226, 222, 200), tex=tx.locker_label('D. REYES'), texmode=1)
    S.mat('label_n', (226, 222, 200), tex=tx.locker_label('NINA'), texmode=1)
    S.mat('label_t', (226, 222, 200), tex=tx.locker_label('TEO'), texmode=1)
    S.mat('keg', (190, 192, 196), spec=1.4, shin=70, refl=0.2)
    S.mat('case0', (255, 255, 255), tex=tx.liquor_case(1), texmode=1, namp=0.1, nscale=20)
    S.mat('case1', (255, 255, 255), tex=tx.liquor_case(2), texmode=1, namp=0.1, nscale=20)
    S.mat('case2', (255, 255, 255), tex=tx.liquor_case(3), texmode=1, namp=0.1, nscale=20)
    S.mat('desk', (90, 98, 96), spec=0.6, shin=40)
    S.mat('lamp', (40, 44, 40), spec=0.8, shin=50)
    S.mat('bulb', (255, 220, 160), emis=(255, 210, 150), emis_mult=5)
    S.mat('cashbox', (60, 30, 26), spec=0.8, shin=40)
    S.mat('mail', (226, 222, 210))
    S.mat('letter', (240, 238, 230), tex=tx.pryce_lease_letter(), texmode=1)
    S.mat('sheet', (112, 114, 120), namp=0.15, nscale=20, wrap=0.3)
    S.mat('skin', (200, 160, 140), wrap=0.3)
    S.mat('cardigan', (110, 92, 70), namp=0.3, nscale=60)
    S.mat('stool', (180, 30, 30), spec=0.6, shin=40)
    S.mat('alley_door', (90, 94, 98), spec=0.7, shin=40)
    S.mat('cooler', (226, 228, 226), spec=0.8, shin=50)
    S.mat('cooler_in', (200, 220, 230), emis=(150, 190, 220), emis_mult=0.9)
    S.mat('strip', (190, 220, 240), emis=(170, 210, 240), emis_mult=1.5)
    S.mat('coat', (40, 36, 34), namp=0.2, nscale=30)
    S.mat('umbrella', (180, 26, 30), spec=0.8, shin=50)
    S.mat('puddle', (40, 40, 44), refl=0.8, spec=1.0, shin=100)
    S.mat('print', (70, 66, 60), refl=0.4, spec=0.8)
    S.mat('lime', (110, 170, 50), spec=0.5)
    S.mat('crate', (150, 116, 76), namp=0.2, nscale=20)
    S.mat('worklight', (240, 245, 255), emis=(240, 245, 255), emis_mult=6)
    S.mat('tripod', (30, 30, 34), spec=0.6)
    S.mat('chair', (40, 40, 44), spec=0.5)
    S.mat('door_wood', (70, 40, 28), namp=0.12, nscale=8, spec=0.4)
    S.mat('music', (236, 232, 214))
    S.mat('brass', (200, 160, 72), spec=1.4, shin=70)
    S.mat('bag', (40, 40, 44), spec=0.4)
    S.mat('beer_crate', (40, 90, 60), spec=0.3, namp=0.1, nscale=20)
    S.mat('bottle_brown', (90, 50, 20), spec=1.4, shin=90)
    S.mat('tire_s', (20, 20, 22))

    # ---------------------------------------------------------------- shell
    S.wboxr(X0 - 0.3, -0.3, ZB - 0.3, X1 + 0.3, 0.0, ZF + 3, 'floor')
    S.wboxr(X0 - 0.3, 0.0, ZB - 0.3, X1 + 0.3, H, ZB, 'wall')
    S.wboxr(X0 - 0.3, 0.0, ZB, X0, H, ZF, 'wall')
    S.wboxr(X1, 0.0, ZB, X1 + 0.3, H, ZF, 'wall')
    S.wboxr(X0 - 0.3, H, ZB - 0.3, X1 + 0.3, H + 0.2, ZF, 'ceiling')
    for (a, b, c, d) in ((X0, ZB, X1, ZB + 0.02), (X0, ZB, X0 + 0.02, ZF), (X1 - 0.02, ZB, X1, ZF)):
        S.wboxr(a, 0.0, b, c, 0.9, d, 'wall_lo')
    S.wboxr(HALL_X - 0.12, 0.0, ZB, HALL_X + 0.12, H, -1.0, 'wall')                       # the stub wall
    S.wboxr(HALL_X - 0.13, 0.0, ZB, HALL_X + 0.13, 0.9, -1.0, 'wall_lo')

    # ---------------------------------------------------------------- the pipe and the rope
    with S.tag('pipe'):
        S.cyl((X0, 2.65, PIPE_Z), (X1, 2.65, PIPE_Z), 0.07, 'pipe')
        for x in (-3.5, -0.5, 2.5):
            S.wboxr(x - 0.03, 2.65, PIPE_Z - 0.03, x + 0.03, H, PIPE_Z + 0.03, 'steel_dk')
        S.cyl((ROPE_X - 0.05, 2.72, PIPE_Z), (ROPE_X + 0.05, 2.72, PIPE_Z), 0.075, 'rope')        # the knot
        S.cone((ROPE_X, 2.66, PIPE_Z), (ROPE_X + 0.02, 2.05, PIPE_Z + 0.02), 0.012, 0.012, 'rope')
        S.ell(WORLD, (ROPE_X + 0.02, 2.04, PIPE_Z + 0.02), (0.02, 0.012, 0.02), 'rope')             # the cut end

    # ---------------------------------------------------------------- Sal, under the sheet
    with S.tag('sal'):
        sx, sz = SAL
        F = Frame((sx, 0.0, sz), Ry(-8))
        S.ell(F, (0.0, 0.07, 0.0), (1.0, 0.08, 0.4), 'sheet', k=0.1)                       # the sheet, loose
        S.ell(F, (0.66, 0.11, 0.0), (0.2, 0.1, 0.2), 'sheet', k=0.14)                      # over the head
        S.ell(F, (0.12, 0.14, 0.02), (0.36, 0.1, 0.3), 'sheet', k=0.14)                    # over the chest
        S.ell(F, (-0.5, 0.1, 0.0), (0.4, 0.07, 0.26), 'sheet', k=0.12)                     # over the legs
        S.ell(F, (-0.98, 0.13, 0.0), (0.09, 0.09, 0.24), 'sheet', k=0.1)                   # the feet, tenting it
        for k in range(5):                                                                # folds
            z = -0.3 + k * 0.15
            S.cone(F.to((-0.8 + k * 0.3, 0.06, z)), F.to((-0.5 + k * 0.32, 0.03, z + 0.28)), 0.02, 0.012, 'sheet', k=0.05)
        S.wbox(F.to((0.0, 0.008, 0.0)), (1.05, 0.008, 0.46), 'sheet', rnd=0.008, rot=Ry(-8))  # the hem on the floor
        # one hand and a cardigan sleeve out from under the edge, toward us
        S.cone(F.to((0.2, 0.05, 0.36)), F.to((0.18, 0.035, 0.52)), 0.045, 0.042, 'cardigan')
        S.ell(F, (0.17, 0.025, 0.6), (0.042, 0.018, 0.07), 'skin', k=0.01)
        for k in range(3):
            S.ell(F, (0.14 + k * 0.025, 0.014, 0.67), (0.01, 0.008, 0.035), 'skin', k=0.008)
    # the step stool, on its side
    with S.tag('stool'):
        fx, fz = STOOL
        Fs = Frame((fx, 0.2, fz), Ry(30) @ Rz(90))                        # an upright stool, tipped onto its side
        S.box(Fs, (0.0, 0.5, 0.0), (0.2, 0.022, 0.24), 0.01, 'stool')
        S.box(Fs, (0.0, 0.25, 0.0), (0.17, 0.018, 0.2), 0.01, 'stool')
        for sx_ in (-1, 1):
            for sz_ in (-1, 1):
                S.cyl(Fs.to((sx_ * 0.17, 0.0, sz_ * 0.2)), Fs.to((sx_ * 0.17, 0.5, sz_ * 0.2)), 0.014, 'steel')
    # Dr. Shah, kneeling at the sheet, and her work light on its tripod
    npc.cast(S, 'shah', dict(npc.CROUCH, lean=34, rsp=66, re=22, rin=10, lsp=40, le=70, lin=30, hp=30, hy=8),
             (SHAH[0], 0.0, SHAH[1]), yaw=-8, scale=0.92, tag='shah')
    with S.tag('worklight'):
        S.cyl((-0.6, 0.0, 0.3), (-0.6, 1.9, 0.3), 0.02, 'tripod')
        for a in range(3):
            ang = a * 2.1
            S.cyl((-0.6, 0.6, 0.3), (-0.6 + 0.35 * math.cos(ang), 0.0, 0.3 + 0.35 * math.sin(ang)), 0.012, 'tripod')
        S.wbox((-0.6, 1.98, 0.3), (0.14, 0.1, 0.05), 'tripod', rot=Ry(-40) @ Rx(-35))
        S.wbox((-0.56, 1.95, 0.25), (0.11, 0.07, 0.01), 'worklight', rot=Ry(-40) @ Rx(-35))
    S.light((-0.5, 1.9, 0.2), (236, 242, 255), power=16, range=8, soft=8, vol=0.25, volshadow=True,
            spot=((0.55, -0.65, -0.55), 28, 52))

    # ---------------------------------------------------------------- lockers along the back wall
    lx0, lx1 = LOCKERS_X
    w = (lx1 - lx0) / 6
    with S.tag('locker'):
        for i in range(6):
            x0 = lx0 + i * w
            if i == 3:
                # Danny's, standing open: a spare shirt, sheet music turned over, Sal's keys hanging from the lock
                S.wboxr(x0, 0.0, ZB, x0 + w - 0.01, 1.9, ZB + 0.45, 'locker_in')
                S.wboxr(x0 + 0.03, 0.02, ZB + 0.02, x0 + w - 0.04, 1.87, ZB + 0.43, 'locker', op=1)
                S.wboxr(x0 + 0.06, 0.4, ZB + 0.05, x0 + w - 0.07, 0.75, ZB + 0.35, 'music')
                for k in range(5):
                    S.wbox((x0 + w / 2, 0.76 + k * 0.012, ZB + 0.2), (0.15, 0.004, 0.11), 'music',
                           rot=Ry(rng.uniform(-14, 14)))
                S.wbox((x0 + w / 2, 1.35, ZB + 0.2), (0.14, 0.32, 0.03), 'bag')                  # the spare shirt
                S.wbox((x0 + w + 0.12, 0.95, ZB + 0.58), (0.012, 0.92, w / 2 - 0.01), 'locker', rot=Ry(-48))
                S.wbox((x0 + w + 0.1, 1.55, ZB + 0.55), (0.014, 0.04, 0.12), 'label_d', rot=Ry(-48))
                S.ell(WORLD, (x0 + w - 0.03, 1.05, ZB + 0.47), (0.03, 0.03, 0.01), 'steel')
                S.cyl((x0 + w - 0.03, 1.02, ZB + 0.47), (x0 + w - 0.01, 0.92, ZB + 0.49), 0.006, 'brass')
                S.ell(WORLD, (x0 + w - 0.01, 0.9, ZB + 0.49), (0.035, 0.035, 0.008), 'brass')       # the key ring
            else:
                S.wboxr(x0, 0.0, ZB, x0 + w - 0.01, 1.9, ZB + 0.45, 'locker', rnd=0.005)
                for k in range(4):
                    S.wboxr(x0 + 0.06, 1.6 + k * 0.04, ZB + 0.45, x0 + w - 0.07, 1.62 + k * 0.04, ZB + 0.46, 'steel_dk')
                lab = {1: 'label_t', 4: 'label_n'}.get(i)
                if lab:
                    S.wboxr(x0 + 0.08, 1.4, ZB + 0.45, x0 + w - 0.09, 1.47, ZB + 0.462, lab)
        S.wboxr(lx0 - 0.02, 1.9, ZB, lx1 + 0.02, 1.95, ZB + 0.47, 'steel_dk')

    # ---------------------------------------------------------------- kegs, cases to the ceiling
    with S.tag('kegs'):
        for k, (x, z) in enumerate(((0.95, -3.55), (1.45, -3.6), (1.2, -3.15))):
            S.tcyl(Frame((x, 0.33, z)), (0, 0, 0), (0.22, 0.22), (0.22, 0.22), 0.33, 'keg')
            S.fcyl((x, 0.68, z), 0.06, 0.03, 'steel_dk')
        for j in range(5):
            for i in range(2):
                for d in range(2):
                    S.wboxr(X1 - 0.95 + i * 0.47, j * 0.36, -1.0 + d * 0.62, X1 - 0.5 + i * 0.47, j * 0.36 + 0.35,
                            -0.4 + d * 0.62, f'case{(i + j + d) % 3}', rnd=0.01)
        for j in range(3):
            S.wboxr(X1 - 0.9, j * 0.36, 0.3, X1 - 0.45, j * 0.36 + 0.35, 0.75, f'case{j % 3}', rnd=0.01)

    # ---------------------------------------------------------------- Sal's desk, lamp, cash box, mail, the letter
    dx, dz = DESK
    with S.tag('desk'):
        S.wboxr(dx - 0.75, 0.74, dz - 0.4, dx + 0.75, 0.78, dz + 0.4, 'desk', rnd=0.01)
        S.wboxr(dx - 0.72, 0.0, dz - 0.36, dx - 0.3, 0.74, dz + 0.36, 'desk')
        S.wboxr(dx + 0.68, 0.0, dz - 0.36, dx + 0.72, 0.74, dz + 0.36, 'desk')
        S.wbox((dx + 0.15, 0.84, dz - 0.05), (0.18, 0.06, 0.12), 'cashbox', rnd=0.01)
        S.wbox((dx - 0.25, 0.8, dz + 0.1), (0.15, 0.02, 0.11), 'mail', rot=Ry(15))
        S.wbox((dx - 0.25, 0.815, dz + 0.1), (0.1, 0.002, 0.13), 'letter', rot=Ry(105))
        S.cyl((dx + 0.55, 0.78, dz - 0.2), (dx + 0.55, 0.8, dz - 0.2), 0.08, 'lamp')
        S.cyl((dx + 0.55, 0.8, dz - 0.2), (dx + 0.5, 1.3, dz - 0.15), 0.012, 'lamp')
        S.cyl((dx + 0.5, 1.3, dz - 0.15), (dx + 0.3, 1.28, dz - 0.0), 0.012, 'lamp')
        S.cone((dx + 0.32, 1.3, dz - 0.02), (dx + 0.26, 1.18, dz + 0.04), 0.03, 0.08, 'lamp')
        S.sph((dx + 0.27, 1.19, dz + 0.03), 0.03, 'bulb')
    S.light((dx + 0.27, 1.15, dz + 0.05), (255, 200, 130), power=4.5, range=6, soft=8, vol=0.2,
            spot=((-0.2, -1, 0.15), 50, 85))
    nx, nz = NINA
    S.wboxr(nx - 0.22, 0.42, nz - 0.22, nx + 0.22, 0.47, nz + 0.22, 'chair')                # the desk chair
    S.cyl((nx, 0.06, nz), (nx, 0.42, nz), 0.025, 'chair')
    S.wboxr(nx - 0.2, 0.47, nz - 0.26, nx + 0.2, 0.95, nz - 0.22, 'chair')
    for a in range(5):
        ang = a * 2 * math.pi / 5
        S.cyl((nx, 0.06, nz), (nx + 0.28 * math.cos(ang), 0.04, nz + 0.28 * math.sin(ang)), 0.015, 'chair')
    if 'nina' not in hide:
        npc.cast(S, 'nina', dict(npc.SEATED, lsp=36, lsa=10, le=110, lin=88, rsp=32, rsa=10, re=104, rin=92,
                                 lean=14, hp=14, hy=-20, hr=4), (nx, 0.02, nz + 0.04), yaw=18, scale=0.9, tag='nina')

    # ---------------------------------------------------------------- the back hall: alley door, hooks, cooler
    a0, a1 = ALLEY
    with S.tag('alley_door'):
        S.wboxr(a0 - 0.06, 0.0, ZB, a1 + 0.06, 2.2, ZB + 0.06, 'steel_dk')
        S.wboxr(a0, 0.0, ZB + 0.02, a1, 2.12, ZB + 0.08, 'alley_door')
        S.wboxr(a1 - 0.2, 1.0, ZB + 0.08, a1 - 0.08, 1.12, ZB + 0.12, 'steel')
        S.wboxr(a1 - 0.18, 1.3, ZB + 0.08, a1 - 0.1, 1.42, ZB + 0.11, 'brass')               # the deadbolt
        S.wboxr(a0 + 0.2, 2.0, ZB + 0.08, a1 - 0.2, 2.06, ZB + 0.1, 'steel')
    with S.tag('hooks'):
        hz = -3.4
        S.wboxr(HALL_X - 0.14, 1.7, hz - 0.5, HALL_X - 0.12, 1.75, hz + 0.6, 'door_wood')
        for k in range(4):
            S.cyl((HALL_X - 0.13, 1.72, hz - 0.35 + k * 0.3), (HALL_X - 0.22, 1.76, hz - 0.35 + k * 0.3), 0.01, 'brass')
        S.ell(WORLD, (HALL_X - 0.24, 1.3, hz - 0.35), (0.08, 0.42, 0.2), 'coat', k=0.04)   # Sal's coat
        S.ell(WORLD, (HALL_X - 0.22, 1.66, hz - 0.35), (0.07, 0.1, 0.16), 'coat', k=0.04)
        uz = hz + 0.25
        S.cyl((HALL_X - 0.22, 1.72, uz), (HALL_X - 0.22, 1.62, uz), 0.012, 'umbrella')      # the red umbrella
        S.cone((HALL_X - 0.24, 1.62, uz), (HALL_X - 0.26, 0.85, uz), 0.08, 0.02, 'umbrella', k=0.02)
        S.cyl((HALL_X - 0.26, 0.85, uz), (HALL_X - 0.26, 0.75, uz), 0.006, 'steel')
        S.ell(WORLD, (HALL_X - 0.4, 0.002, uz + 0.05), (0.32, 0.004, 0.24), 'puddle')
        for k in range(7):                                                                    # small wet prints
            t = k / 6
            px = a1 + 0.1 + (X0 + 0.5 - a1 - 0.1) * t * 0.7 - 0.1 * (k % 2)
            pz = ZB + 0.6 + (COOLER_Z[0] + 0.5 - ZB - 0.6) * t
            S.ell(WORLD, (px, 0.003, pz), (0.05, 0.003, 0.1), 'print', rot=Ry(30))
    c0, c1 = COOLER_Z
    with S.tag('cooler'):
        S.wboxr(X0 - 0.02, 0.0, c0 - 0.12, X0 + 0.1, 2.3, c1 + 0.12, 'steel')               # frame
        S.wboxr(X0 - 1.6, 0.0, c0, X0, 2.2, c1, 'cooler_in', op=1)
        S.wboxr(X0 - 1.6, 0.0, c0 - 0.4, X0 - 0.1, 2.4, c0, 'cooler')                      # the box itself, behind
        S.wboxr(X0 - 1.6, 0.0, c1, X0 - 0.1, 2.4, c1 + 0.4, 'cooler')
        S.wboxr(X0 - 1.7, 0.0, c0 - 0.4, X0 - 1.6, 2.4, c1 + 0.4, 'cooler_in')
        for y in (0.6, 1.2, 1.8):                                                          # shelves of limes, kegs
            S.wboxr(X0 - 1.6, y, c0 + 0.02, X0 - 1.1, y + 0.03, c1 - 0.02, 'steel')
            for k in range(6):
                S.sph((X0 - 1.35 + 0.08 * (k % 3), y + 0.07, c0 + 0.25 + 0.18 * k), 0.05, 'lime')
        S.tcyl(Frame((X0 - 0.75, 0.33, c0 + 0.4)), (0, 0, 0), (0.22, 0.22), (0.22, 0.22), 0.33, 'keg')
        S.wboxr(X0 - 0.75, 0.0, c1 - 0.55, X0 - 0.35, 0.36, c1 - 0.15, 'crate')             # where she sat
    S.light((X0 - 0.8, 2.1, (c0 + c1) / 2), (190, 220, 245), power=3.5, range=4, soft=10)
    if 'cooler_shut' not in hide:
        with S.tag('cooler_shut'):
            S.wboxr(X0 + 0.02, 0.02, c0, X0 + 0.14, 2.18, c1, 'cooler', rnd=0.02)
            S.wboxr(X0 + 0.14, 1.0, c1 - 0.32, X0 + 0.22, 1.16, c1 - 0.08, 'steel')        # the handle
            S.wboxr(X0 + 0.14, 1.32, c1 - 0.2, X0 + 0.17, 1.4, c1 - 0.08, 'steel')         # the hasp, open
            S.wboxr(X0 + 0.14, 0.0, c0 + 0.1, X0 + 0.2, 0.004, c1 - 0.1, 'strip')         # light under the door
    else:
        S.wbox((X0 + 0.55, 1.1, c0 - 0.05), (0.06, 1.08, 0.72), 'cooler', rnd=0.02, rot=Ry(-70))   # standing open

    # ---------------------------------------------------------------- the door to the bar (right wall, near us)
    b0, b1 = BAR_DOOR
    with S.tag('bar_door'):
        S.wboxr(X1 - 0.05, 0.0, b0 - 0.08, X1 + 0.02, 2.25, b1 + 0.08, 'door_wood')
        S.wboxr(X1 - 0.6, 0.0, b0, X1, 2.15, b1, 'door_wood', op=1)
        S.wbox((X1 - 0.45, 1.07, b0 + 0.35), (0.03, 1.06, 0.42), 'door_wood', rot=Ry(-60))
        S.wboxr(X1 + 0.02, 0.0, b0, X1 + 0.08, 2.15, b1, 'cooler_in')
    S.light((X1 - 0.3, 1.6, (b0 + b1) / 2), (255, 190, 130), power=1.2, range=3, soft=10)

    # ---------------------------------------------------------------- foreground: beer crates, a hand truck with a keg
    if 'fg_crates' not in hide:
        with S.tag('fg_crates'):
            cx, cz = FG_CRATES
            for j in range(4):
                for i in range(2):
                    if j == 3 and i == 1:
                        continue
                    S.wboxr(cx - 0.42 + i * 0.44, j * 0.3, cz - 0.3, cx + i * 0.44, j * 0.3 + 0.29, cz + 0.08,
                            'beer_crate', rnd=0.01)
                    for b in range(3):
                        S.cyl((cx - 0.35 + i * 0.44 + b * 0.13, j * 0.3 + 0.29, cz - 0.11),
                              (cx - 0.35 + i * 0.44 + b * 0.13, j * 0.3 + 0.33, cz - 0.11), 0.03, 'bottle_brown')
    if 'fg_truck' not in hide:
        with S.tag('fg_truck'):
            hx, hz = FG_TRUCK
            S.tcyl(Frame((hx, 0.42, hz)), (0, 0, 0), (0.22, 0.22), (0.22, 0.22), 0.33, 'keg')
            S.fcyl((hx, 0.77, hz), 0.06, 0.03, 'steel_dk')
            for s_ in (-1, 1):
                S.cyl((hx + s_ * 0.2, 0.05, hz - 0.28), (hx + s_ * 0.2, 1.3, hz - 0.33), 0.02, 'steel_dk')
                S.fcyl((hx + s_ * 0.26, 0.11, hz - 0.3), 0.11, 0.03, 'tire_s', axis='x')
            S.cyl((hx - 0.2, 1.3, hz - 0.33), (hx + 0.2, 1.3, hz - 0.33), 0.02, 'steel_dk')
            S.wboxr(hx - 0.24, 0.0, hz - 0.3, hx + 0.24, 0.04, hz + 0.05, 'steel_dk')

    # ---------------------------------------------------------------- overhead: a bare bulb, the flashlights
    S.cyl((-0.8, H, -2.3), (-0.8, 2.55, -2.3), 0.008, 'lamp')
    S.sph((-0.8, 2.5, -2.3), 0.05, 'bulb')
    S.light((-0.8, 2.45, -2.3), (255, 210, 150), power=5, range=8, soft=10, vol=0.15)
    S.light((-3.6, 2.3, -2.0), (200, 210, 230), power=2.2, range=5, soft=10)                 # the hall's own light

    # ---------------------------------------------------------------- Officer Park, in the back hall (overlay)
    if 'park' not in hide:
        npc.cast(S, 'park', dict(npc.ARMS_FOLDED, hp=4, hy=-30, lhp=4, rhp=-4), (PARK[0], 0.0, PARK[1]), yaw=40,
                 scale=0.94, tag='park')

    cam = Camera((-0.2, 2.75, 6.6), (-0.5, 0.85, -1.9), fov=50, W=3840, H=2160)
    env = dict(sky=(40, 40, 44), bounce=(40, 38, 36), fog_col=(34, 34, 38), fog=0.02, fog_h0=0.0, fog_hf=0.06,
               fog_max=60, vol_scale=4, vol_steps=40, reflections=True, grid=0.5, ao_scale=0.9)

    def rect(x, z, w, h):
        return [(x - w, 0.0, z), (x + w, 0.0, z), (x + w, h, z), (x - w, h, z)]
    walk = [(-4.8, 2.8), (-4.8, -0.8), (-4.65, -0.8), (-4.65, -3.55), (-2.85, -3.55), (-2.85, -0.8), (-2.15, -0.8),
            (-2.15, -3.45), (0.45, -3.45), (0.45, -2.6), (-0.15, -2.6), (-0.15, -0.45), (2.05, -0.45), (2.05, -2.05),
            (3.3, -2.05), (3.3, 2.8)]
    meta = dict(
        room='blue_note_back',
        walk=walk,
        walk_zmin=-3.5, walk_zmax=2.8, scale_x=-1.0,
        spawns={'blue_note_bar': (3.0, 1.1), 'start': (0.0, 1.5)},
        hotspots={
            'sal': ('Sal', (0.8, -0.2), 'up'),
            'shah': ('Dr. Shah', (-0.5, -1.55), 'right'),
            'pipe': ('pipe and rope', None, 'up'),
            'stool': ('step stool', (2.4, -0.15), 'left'),
            'locker': ("Danny's locker", (-0.5, -3.2), 'up'),
            'desk': ("Sal's desk", (2.6, -1.85), 'up'),
            'kegs': ('kegs and cases', None, 'up'),
            'alley_door': ('alley door', (-4.0, -3.3), 'up'),
            'hooks': ('coat hooks', (-3.1, -3.0), 'right'),
            'cooler': ('walk-in cooler', (-4.4, -2.2), 'left'),
            'nina': ('Nina', (2.25, -1.6), 'left'),
            'park': ('Officer Park', (-3.3, -1.0), 'left'),
            'bar_door': ('door to the bar', (3.15, 1.1), 'right'),
        },
        hotspot_shapes={
            'sal': [(SAL[0] - 1.05, 0.0, SAL[1] + 0.75), (SAL[0] + 1.05, 0.0, SAL[1] + 0.75), (SAL[0] + 1.05, 0.0, SAL[1] - 0.45),
                    (SAL[0] - 1.05, 0.0, SAL[1] - 0.45), (SAL[0], 0.32, SAL[1])],
            'shah': rect(SHAH[0], SHAH[1], 0.4, 1.25),
            'nina': rect(NINA[0], NINA[1] + 0.2, 0.38, 1.35),
            'park': rect(PARK[0], PARK[1], 0.3, 1.78),
            'pipe': [(-1.5, 2.55, PIPE_Z), (X1, 2.55, PIPE_Z), (X1, 2.78, PIPE_Z), (-1.5, 2.78, PIPE_Z),
                     (ROPE_X - 0.15, 1.95, PIPE_Z), (ROPE_X + 0.15, 1.95, PIPE_Z)],
            'cooler': [(X0, 0.0, COOLER_Z[0]), (X0, 0.0, COOLER_Z[1]), (X0, 2.3, COOLER_Z[1]), (X0, 2.3, COOLER_Z[0])],
            'locker': [(LOCKERS_X[0], 0.0, ZB + 0.45), (LOCKERS_X[1] + 0.4, 0.0, ZB + 0.6), (LOCKERS_X[1] + 0.4, 1.95, ZB + 0.6),
                       (LOCKERS_X[0], 1.95, ZB + 0.45)],
        },
        hotspot_order=['pipe', 'kegs', 'locker', 'alley_door', 'hooks', 'cooler', 'desk', 'bar_door', 'stool', 'sal',
                       'shah', 'nina', 'park'],
        overlays=['nina', 'park', 'cooler_shut'],
        occluders={'fg_crates': (FG_CRATES[0] - 0.2, FG_CRATES[1] - 0.3), 'fg_truck': (FG_TRUCK[0], FG_TRUCK[1] - 0.35)},
        overlay_bases={'nina': (NINA[0], NINA[1] + 0.25), 'park': PARK},
        obstacles=[(FG_CRATES[0] - 0.2, FG_CRATES[1] - 0.1, 0.5), (FG_TRUCK[0], FG_TRUCK[1] - 0.1, 0.4), (SHAH[0], SHAH[1] + 0.05, 0.42), (STOOL[0], STOOL[1], 0.35), (-0.6, 0.3, 0.3), (PARK[0], PARK[1], 0.3)],
        char_fill=((230, 230, 236), 0.2),
        tint=(0.86, 0.86, 0.84),
        exposure=1.7,
    )
    return S, cam, env, meta
