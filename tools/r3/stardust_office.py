"""Stardust's back office, 3:10 a.m. (Case 3, scene 3). A small, warm, cluttered room: Gus's rolltop desk under a green
banker's lamp, buried in paper, the cordless phone on the grey filing cabinet, an old fuse panel with hand-written labels,
two tall staff lockers (GUS, and PEARL with its door ajar), and steep wooden stairs climbing the right wall to the roof
door, propped open, rain drifting down. Gus lies at the foot of the stairs in his cardigan, face turned to the wall, one
slipper on and one on the third step; Dr. Shah kneels beside him. Both are part of the set.

One overlay: the red and gold light that spills down the stairs once the roof sign is switched back on (sign_glow)."""
import math, random
import numpy as np
from scene3d import *
import textures as tx
import npc

X0, X1, ZB, H = -3.8, 3.8, -2.7, 4.2
ST_X = (2.55, 3.8)            # the stairs, along the right wall (x)
ST_Z0, ST_Z1 = 1.0, -1.75     # bottom step (front) to top step (back)
ST_TOP = 2.75                 # landing height
STEPS = 14
GUS = (2.8, 0.95)             # Gus's feet, on the floor at the foot of the stairs; he lies toward the front
DESK = (-2.0, ZB)             # the rolltop desk, against the back wall
LOCKERS = (-0.15, 0.95)       # the two lockers (x)
CURTAIN = (0.2, 1.3)          # curtained doorway back to the shop, in the left wall (z)


def build(hide=()):
    S = Scene()
    rng = random.Random(34)
    # ---------------------------------------------------------------- materials
    S.mat('floor', (255, 255, 255), tex=tx.hires(tx.floorboards(seed=94, base=(100, 70, 46)), 2), texmode=4, texmap=1,
          texscale=2.4, spec=0.35, shin=40, refl=0.03)
    S.mat('wall', (150, 128, 96), namp=0.1, nscale=6)                                    # nicotine-yellow plaster
    S.mat('wall_lo', (70, 50, 36), spec=0.3, shin=30)
    S.mat('ceiling', (110, 100, 86), namp=0.1, nscale=10)
    S.mat('trim', (90, 62, 40), spec=0.3)
    S.mat('wood', (110, 70, 40), namp=0.15, nscale=6, spec=0.5, shin=40)
    S.mat('wood_dk', (62, 38, 24), namp=0.12, nscale=6, spec=0.4, shin=30)
    S.mat('stair', (120, 86, 56), namp=0.2, nscale=5, spec=0.3)
    S.mat('steel', (120, 126, 132), spec=0.8, shin=40, namp=0.05, nscale=10)
    S.mat('steel_dk', (70, 74, 80), spec=0.6, shin=30)
    S.mat('locker', (84, 104, 96), spec=0.6, shin=40, namp=0.05, nscale=20)
    S.mat('locker_in', (36, 40, 40))
    S.mat('tape_gus', (222, 206, 156), tex=tx.tape_label('GUS'), texmode=1)
    S.mat('tape_pearl', (222, 206, 156), tex=tx.tape_label('PEARL'), texmode=1)
    S.mat('fuse', (120, 124, 128), tex=tx.hires(tx.fuse_panel(), 2), texmode=1, spec=0.5, shin=30)
    S.mat('paper', (226, 222, 208), namp=0.08, nscale=30)
    S.mat('paper2', (206, 200, 180), namp=0.08, nscale=30)
    S.mat('letter', (240, 238, 230), tex=tx.hires(tx.pryce_letter(), 2), texmode=1)
    S.mat('catalogue', (20, 20, 24), tex=tx.hires(tx.catalogue_cover(), 2), texmode=1, spec=1.0, shin=60)
    S.mat('green_glass', (20, 110, 60), emis=(30, 120, 60), emis_mult=0.6, spec=1.2, shin=80)
    S.mat('brass', (200, 160, 72), spec=1.4, shin=70)
    S.mat('bulb', (255, 220, 160), emis=(255, 210, 150), emis_mult=5)
    S.mat('phone', (40, 40, 44), spec=0.8, shin=50)
    S.mat('phone_led', (60, 255, 80), emis=(60, 255, 80), emis_mult=3)
    S.mat('coat', (60, 30, 50), namp=0.2, nscale=20)
    S.mat('heels', (150, 20, 30), spec=1.0, shin=60)
    S.mat('envelope', (196, 170, 120))
    S.mat('cardboard', (150, 116, 76), namp=0.2, nscale=10)
    S.mat('cardboard_dk', (120, 92, 60), namp=0.2, nscale=10)
    S.mat('slipper', (110, 40, 40), namp=0.2, nscale=30)
    S.mat('rain_door', (40, 50, 70), emis=(70, 90, 130), emis_mult=0.7)
    S.mat('roof_door', (70, 60, 50), spec=0.3)
    S.mat('poster', (200, 200, 200), tex=tx.hires(tx.movie_poster('HARBOR LIGHTS', 'LYLE BRANDT  1954',
                                                                    ((30, 60, 90), (240, 210, 140)), seed=0), 2), texmode=1)
    S.mat('calendar', (230, 226, 214), namp=0.05, nscale=20)
    S.mat('red', (160, 30, 30))
    S.mat('cigarbox', (120, 60, 30), spec=0.6, shin=40)
    S.mat('fridge', (210, 206, 190), spec=0.6, shin=50)
    S.mat('rug', (90, 50, 40), namp=0.4, nscale=16)
    S.mat('leather', (90, 46, 30), spec=0.5, shin=30, namp=0.15, nscale=12)
    S.mat('umbrella', (30, 30, 36), spec=0.5)
    S.mat('sign_door', (120, 40, 30), emis=(255, 90, 50), emis_mult=1.1)
    for i in range(3):                                                                    # Gus with the stars
        S.mat('photo%d' % i, (60, 60, 60), tex=tx.signed_wall().crop((int(i * 128) + 10, 8, int(i * 128) + 114, 98)),
              texmode=1)

    # ---------------------------------------------------------------- shell
    S.wboxr(X0 - 1, -0.3, ZB - 1, X1 + 1, 0.0, 9, 'floor')
    S.wboxr(X0 - 0.2, 0, ZB - 0.15, X1 + 0.2, H, ZB, 'wall')                           # back wall
    S.wboxr(X0 - 0.2, 0, ZB, X0, H, 9, 'wall')                                          # left wall
    S.wboxr(X1, 0, ZB - 0.2, X1 + 0.2, H, 9, 'wall')                                    # right wall
    S.wboxr(X0 - 0.2, H, ZB - 0.2, X1 + 0.2, H + 0.2, 9, 'ceiling')
    S.wboxr(X0, 0, ZB, X1, 1.0, ZB + 0.02, 'wall_lo')                                   # wainscot
    S.wboxr(X0, 0, ZB, X0 + 0.02, 1.0, 9, 'wall_lo')
    S.wboxr(X0, 1.0, ZB, X1, 1.04, ZB + 0.04, 'trim')
    S.wboxr(X0, 1.0, ZB, X0 + 0.04, 1.04, 9, 'trim')
    S.wboxr(X0, 0, ZB, X1, 0.1, ZB + 0.03, 'trim')
    S.wboxr(-3.0, 0.0, -1.2, 1.4, 0.012, 1.6, 'rug')

    # ---------------------------------------------------------------- the curtained doorway back to the shop (left wall)
    with S.tag('curtain'):
        z0, z1 = CURTAIN
        S.wboxr(X0 - 0.4, 0, z0, X0 + 0.1, 2.25, z1, 'wall', op=1)
        S.wboxr(X0 - 0.3, 0, z0, X0 - 0.2, 2.25, z1, 'roof_door')                       # the dark shop beyond
        S.cyl((X0 + 0.08, 2.28, z0 - 0.08), (X0 + 0.08, 2.28, z1 + 0.08), 0.02, 'brass')
        for k, z in enumerate(np.arange(z0 + 0.05, z1, 0.09)):
            if 0.45 < z - z0 < 0.7:
                continue
            S.cyl((X0 + 0.07 + 0.02 * (k % 2), 0.02, z), (X0 + 0.07 + 0.02 * (k % 2), 2.27, z), 0.05, 'red', k=0.04)

    # ---------------------------------------------------------------- Gus's rolltop desk and the green lamp
    dx, dz = DESK
    with S.tag('desk'):
        for x in (dx - 0.72, dx + 0.42):                                                # pedestals with drawers
            S.wboxr(x, 0, dz, x + 0.3, 0.74, dz + 0.68, 'wood', rnd=0.01)
            for k in range(3):
                S.wboxr(x + 0.03, 0.08 + k * 0.22, dz + 0.68, x + 0.27, 0.26 + k * 0.22, dz + 0.7, 'wood_dk')
                S.sph((x + 0.15, 0.17 + k * 0.22, dz + 0.71), 0.012, 'brass')
        S.wboxr(dx - 0.76, 0.74, dz, dx + 0.76, 0.78, dz + 0.74, 'wood', rnd=0.01)       # writing surface
        S.wboxr(dx - 0.76, 0.78, dz, dx + 0.76, 1.3, dz + 0.24, 'wood_dk')              # hutch with pigeonholes
        for k in range(6):
            S.wboxr(dx - 0.68 + k * 0.23, 0.82, dz + 0.2, dx - 0.5 + k * 0.23, 1.02, dz + 0.25, 'paper2')
        S.wboxr(dx - 0.76, 1.24, dz, dx + 0.76, 1.32, dz + 0.36, 'wood')                 # the roll, rolled up
        S.wbox((dx, 1.34, dz + 0.3), (0.76, 0.05, 0.12), 'wood', rnd=0.04, rot=Rx(-35))
        S.wboxr(dx - 0.8, 0.74, dz, dx - 0.76, 1.36, dz + 0.42, 'wood')                 # the curved side panels
        S.wboxr(dx + 0.76, 0.74, dz, dx + 0.8, 1.36, dz + 0.42, 'wood')
        # paper, everywhere: bills, invoices, a racing form
        for k in range(9):
            S.wbox((dx + rng.uniform(-0.55, 0.55), 0.785 + k * 0.004, dz + rng.uniform(0.35, 0.6)),
                   (0.11, 0.002, 0.15), rng.choice(['paper', 'paper2']), rot=Ry(rng.uniform(-30, 30)))
        S.wboxr(dx - 0.65, 0.78, dz + 0.3, dx - 0.35, 0.9, dz + 0.5, 'paper2')           # a stack
        S.wbox((dx + 0.42, 0.79, dz + 0.5), (0.11, 0.01, 0.14), 'catalogue', rot=Ry(12) @ Rx(-90))
    with S.tag('letter'):                                                               # on top, where he'd see it
        S.wbox((dx - 0.05, 0.81, dz + 0.5), (0.1, 0.13, 0.002), 'letter', rot=Ry(-8) @ Rx(-90))
    with S.tag('drawer'):
        S.wboxr(dx - 0.42, 0.66, dz + 0.72, dx + 0.42, 0.74, dz + 0.745, 'wood_dk')     # the center drawer
        S.sph((dx, 0.7, dz + 0.75), 0.014, 'brass')
    with S.tag('lamp'):
        S.cyl((dx + 0.5, 0.78, dz + 0.32), (dx + 0.5, 0.8, dz + 0.32), 0.08, 'brass')
        S.cyl((dx + 0.5, 0.8, dz + 0.32), (dx + 0.5, 1.12, dz + 0.32), 0.012, 'brass')
        S.wbox((dx + 0.5, 1.15, dz + 0.38), (0.16, 0.04, 0.07), 'green_glass', rnd=0.035, rot=Rx(-12))
    S.light((dx + 0.5, 1.02, dz + 0.42), (255, 220, 160), power=3.0, range=4, soft=12, vol=0.08)   # banker's lamp
    # the chair, pushed back
    cf = Frame((dx + 0.1, 0, dz + 1.2), Ry(-14))
    S.box(cf, (0, 0.46, 0), (0.24, 0.03, 0.22), 0.02, 'wood_dk')
    S.box(cf, (0, 0.78, -0.2), (0.22, 0.2, 0.03), 0.03, 'wood_dk')
    S.cyl(cf.to((0, 0.06, 0)), cf.to((0, 0.44, 0)), 0.03, 'steel_dk')
    for a in range(5):
        t = math.radians(a * 72)
        S.cyl(cf.to((0, 0.05, 0)), cf.to((0.28 * math.cos(t), 0.03, 0.28 * math.sin(t))), 0.018, 'steel_dk')
    # a Harbor Lights poster and a calendar above the desk
    S.wboxr(dx - 0.35, 1.6, ZB, dx + 0.35, 2.65, ZB + 0.02, 'trim')
    S.wbox((dx, 2.125, ZB + 0.025), (0.32, 0.5, 0.003), 'poster')
    S.wboxr(dx + 0.6, 1.55, ZB, dx + 0.95, 2.0, ZB + 0.015, 'calendar')
    S.wboxr(dx + 0.62, 1.8, ZB + 0.015, dx + 0.93, 1.83, ZB + 0.018, 'red')

    # ---------------------------------------------------------------- the filing cabinet (left wall) and the phone on it
    fz = -1.3
    with S.tag('cabinet'):
        S.wboxr(X0, 0, fz - 0.3, X0 + 0.66, 1.32, fz + 0.3, 'steel', rnd=0.01)
        for k in range(4):
            y = 0.06 + k * 0.32
            S.wboxr(X0 + 0.66, y, fz - 0.26, X0 + 0.68, y + 0.28, fz + 0.26, 'steel')
            S.wboxr(X0 + 0.68, y + 0.2, fz - 0.07, X0 + 0.7, y + 0.23, fz + 0.07, 'steel_dk')
            S.wboxr(X0 + 0.68, y + 0.08, fz - 0.05, X0 + 0.685, y + 0.14, fz + 0.05, 'paper')
    with S.tag('phone'):
        S.wboxr(X0 + 0.2, 1.32, fz - 0.12, X0 + 0.42, 1.36, fz + 0.12, 'phone', rnd=0.01)      # the cradle
        S.wbox((X0 + 0.31, 1.45, fz - 0.02), (0.03, 0.11, 0.025), 'phone', rnd=0.015, rot=Rz(-8))  # the handset
        S.sph((X0 + 0.36, 1.37, fz + 0.09), 0.01, 'phone_led')
    S.wboxr(X0, 1.36, fz - 0.28, X0 + 0.5, 1.6, fz - 0.15, 'cardboard')                     # a box of receipts

    # ---------------------------------------------------------------- the fuse panel
    fx0, fx1 = -0.95, -0.45
    with S.tag('fuse_panel'):
        S.wboxr(fx0 - 0.03, 1.2, ZB, fx1 + 0.03, 1.96, ZB + 0.1, 'steel_dk')
        S.wbox(((fx0 + fx1) / 2, 1.58, ZB + 0.102), ((fx1 - fx0) / 2, 0.34, 0.002), 'fuse')
        S.cyl((fx1 - 0.05, 1.96, ZB + 0.05), (fx1 - 0.05, 3.9, ZB + 0.05), 0.02, 'steel_dk')     # conduit up

    # ---------------------------------------------------------------- the lockers: GUS (shut), PEARL (ajar)
    lx0, lx1 = LOCKERS
    lw = (lx1 - lx0) / 2
    for i, name in enumerate(('gus_locker', 'pearl_locker')):
        a = lx0 + i * lw
        with S.tag(name):
            S.wboxr(a + 0.01, 0.0, ZB, a + lw - 0.01, 1.95, ZB + 0.5, 'locker')
            S.wboxr(a + 0.01, 0.0, ZB + 0.5, a + lw - 0.01, 0.08, ZB + 0.52, 'steel_dk')
            if i == 0:
                S.wbox((a + lw / 2, 1.75, ZB + 0.52), (0.13, 0.03, 0.002), 'tape_gus')
            else:                                                                        # PEARL, on the frame above
                S.wbox((a + lw / 2, 1.93, ZB + 0.505), (0.13, 0.03, 0.002), 'tape_pearl')
            if i == 0:                                                                   # GUS: shut
                S.wboxr(a + 0.03, 0.1, ZB + 0.5, a + lw - 0.03, 1.9, ZB + 0.51, 'locker')
                for k in range(4):
                    S.wboxr(a + 0.12, 1.55 + k * 0.04, ZB + 0.51, a + lw - 0.12, 1.565 + k * 0.04, ZB + 0.515, 'steel_dk')
                S.wboxr(a + lw - 0.1, 0.9, ZB + 0.51, a + lw - 0.07, 1.05, ZB + 0.53, 'steel_dk')
            else:                                                                        # PEARL: door ajar, swung out
                S.wboxr(a + 0.03, 0.1, ZB + 0.02, a + lw - 0.03, 1.9, ZB + 0.56, 'locker_in', op=1)
                S.wboxr(a + 0.03, 0.1, ZB + 0.0, a + lw - 0.03, 1.9, ZB + 0.02, 'locker_in')       # dark inside
                hinge = (a + 0.03, 0, ZB + 0.5)
                D = Frame(hinge, Ry(-62))
                S.box(D, ((lw - 0.06) / 2, 1.0, 0.0), ((lw - 0.06) / 2, 0.9, 0.006), 0.0, 'locker')
                for k in range(4):
                    S.box(D, ((lw - 0.06) / 2, 1.6 + k * 0.04, 0.007), ((lw - 0.2) / 2, 0.008, 0.002), 0.0, 'steel_dk')
                # inside: a coat on a hook, heels, a makeup bag, the envelope of headshots on the shelf
                S.wboxr(a + 0.04, 1.62, ZB + 0.04, a + lw - 0.04, 1.64, ZB + 0.48, 'steel_dk')       # shelf
                S.wbox((a + lw / 2, 1.2, ZB + 0.25), (0.15, 0.36, 0.08), 'coat', rnd=0.06)
                S.wboxr(a + 0.08, 1.645, ZB + 0.1, a + lw - 0.06, 1.7, ZB + 0.4, 'envelope')
                S.wboxr(a + 0.1, 0.1, ZB + 0.15, a + 0.2, 0.2, ZB + 0.35, 'heels')
                S.wboxr(a + 0.24, 0.1, ZB + 0.15, a + 0.33, 0.2, ZB + 0.35, 'heels')

    # ---------------------------------------------------------------- a little fridge (NEVER), the umbrella, boxes
    S.wboxr(1.1, 0.0, ZB, 1.75, 0.85, ZB + 0.6, 'fridge', rnd=0.04)
    S.wboxr(1.12, 0.84, ZB + 0.04, 1.73, 0.86, ZB + 0.58, 'steel_dk')
    S.wboxr(1.2, 0.86, ZB + 0.1, 1.5, 0.95, ZB + 0.35, 'cigarbox')

    # ---------------------------------------------------------------- the stairs to the roof, the open roof door
    with S.tag('stairs'):
        sx0, sx1 = ST_X
        run = (ST_Z0 - ST_Z1) / STEPS
        rise = ST_TOP / STEPS
        for k in range(STEPS):
            z = ST_Z0 - k * run
            y = (k + 1) * rise
            S.wboxr(sx0, y - 0.04, z - run - 0.03, sx1, y, z, 'stair')                 # tread
            S.wboxr(sx0 + 0.02, y - rise, z - 0.02, sx1, y - 0.04, z, 'wood_dk')       # riser
        # stringer and handrail on the open side
        S.wbox((sx0 - 0.03, ST_TOP / 2 - 0.1, (ST_Z0 + ST_Z1) / 2), (0.03, 0.14, math.hypot(ST_Z0 - ST_Z1, ST_TOP) / 2),
               'wood_dk', rot=Rx(math.degrees(math.atan2(ST_TOP, ST_Z0 - ST_Z1))))
        for k in range(0, STEPS + 1, 4):
            z = ST_Z0 - k * run
            S.cyl((sx0 - 0.02, k * rise, z), (sx0 - 0.02, k * rise + 0.9, z), 0.02, 'wood_dk')
        S.cyl((sx0 - 0.02, 0.9, ST_Z0), (sx0 - 0.02, ST_TOP + 0.9, ST_Z1), 0.025, 'wood')
        # the landing and its door in the back wall
        S.wboxr(sx0, ST_TOP - 0.06, ZB, sx1, ST_TOP, ST_Z1, 'stair')
        S.wboxr(sx0 - 0.03, 0.0, ST_Z1 - 0.02, sx0, ST_TOP, ST_Z1 + 0.02, 'wood_dk')
    S.wboxr(sx0 + 0.05, ST_TOP, ZB - 0.3, sx1 - 0.1, ST_TOP + 2.0, ZB + 0.05, 'wall', op=1)
    with S.tag('roof_door'):
        S.wboxr(sx0 + 0.05, ST_TOP, ZB - 0.25, sx1 - 0.1, ST_TOP + 2.0, ZB - 0.2,
                'rain_door' if 'sign_glow' in hide else 'sign_door')                            # night, or neon
        D = Frame((sx0 + 0.05, ST_TOP, ZB - 0.05), Ry(-70))                                   # propped open, inward
        S.box(D, ((sx1 - sx0 - 0.15) / 2, 1.0, 0.0), ((sx1 - sx0 - 0.15) / 2, 0.99, 0.03), 0.0, 'roof_door')
        S.wboxr(sx0 + 0.02, ST_TOP, ZB - 0.02, sx0 + 0.05, ST_TOP + 2.05, ZB + 0.05, 'trim')
        S.wboxr(sx1 - 0.1, ST_TOP, ZB - 0.02, sx1 - 0.07, ST_TOP + 2.05, ZB + 0.05, 'trim')
        S.wboxr(sx0 + 0.02, ST_TOP + 2.0, ZB - 0.02, sx1 - 0.07, ST_TOP + 2.05, ZB + 0.05, 'trim')
    # rain light from the door, and (overlay) the sign's red-gold glow spilling down the stairs once it's back on
    S.light(((sx0 + sx1) / 2, ST_TOP + 1.6, ZB + 0.3), (110, 130, 180), power=2.2, range=5, soft=12, vol=0.3)
    if 'sign_glow' not in hide:
        S.light(((sx0 + sx1) / 2, ST_TOP + 1.7, ZB + 0.15), (255, 80, 44), power=7, range=8, soft=14, vol=0.35,
                spot=((0, -0.75, 0.66), 35, 75))
        S.light(((sx0 + sx1) / 2 - 0.2, ST_TOP + 1.5, ZB + 0.12), (255, 180, 70), power=4, range=7, soft=14, vol=0.2,
                spot=((0, -0.7, 0.7), 30, 70))

    # ---------------------------------------------------------------- one slipper on the third step
    k = 2
    z3 = ST_Z0 - (k + 0.5) * (ST_Z0 - ST_Z1) / STEPS
    with S.tag('slipper'):
        S.wbox((ST_X[0] + 0.4, (k + 1) * ST_TOP / STEPS + 0.03, z3), (0.05, 0.03, 0.12), 'slipper', rnd=0.025, rot=Ry(30))

    # ---------------------------------------------------------------- Gus at the foot of the stairs; Dr. Shah kneeling by him
    gx, gz = GUS
    npc.cast(S, 'gus', dict(npc.STAND, lsp=-8, lsa=48, le=24, rsp=-4, rsa=30, re=36, lhp=6, lk=8, rhp=-2, rk=4,
                            labd=6, rabd=4, hy=-70, hp=-8, hr=0),
             (gx, 0.15, gz), yaw=180, scale=0.93, rot=Rx(-90), tag='gus')
    npc.cast(S, 'shah', dict(npc.CROUCH, rsp=48, re=18, rin=16, lsp=30, le=70, lin=30, hp=30, hy=6),
             (gx - 0.75, 0, gz + 1.0), yaw=90, scale=0.95, tag='shah')

    # ---------------------------------------------------------------- foreground: archive boxes (left), coat tree (right)
    if 'boxes' not in hide:
        with S.tag('boxes'):
            for (x, z, y, rot) in ((-3.1, 2.75, 0.0, 6), (-2.45, 2.85, 0.0, -4), (-2.95, 2.8, 0.36, 14), (-3.2, 2.2, 0.0, -10)):
                S.wbox((x, y + 0.18, z), (0.28, 0.18, 0.2), 'cardboard' if rot > 0 else 'cardboard_dk', rnd=0.01, rot=Ry(rot))
                S.wbox((x, y + 0.2, z + 0.205), (0.12, 0.05, 0.002), 'paper', rot=Ry(rot))
    # a tall shelf of stock on the left wall, framed photos of Gus with the stars, a clock
    with S.tag('shelf'):
        sz0, sz1 = -0.85, 0.05
        for z in (sz0, sz1):
            S.wboxr(X0, 0, z - 0.02, X0 + 0.45, 2.3, z + 0.02, 'wood_dk')
        for k, y in enumerate((0.05, 0.6, 1.15, 1.7, 2.25)):
            S.wboxr(X0, y, sz0, X0 + 0.45, y + 0.03, sz1, 'wood_dk')
            if y < 2.2:
                for j, z in enumerate(np.arange(sz0 + 0.06, sz1 - 0.15, 0.3)):
                    if (k + j) % 3 == 2:
                        S.fcyl((X0 + 0.22, y + 0.13, z + 0.12), 0.16, 0.1, 'steel', axis='y')          # film cans
                    else:
                        S.wboxr(X0 + 0.04, y + 0.03, z, X0 + 0.42, y + 0.03 + rng.uniform(0.25, 0.42), z + 0.26,
                                rng.choice(['cardboard', 'cardboard_dk']))
    for i, (x, y, w, h) in enumerate(((-0.1, 2.35, 0.36, 0.44), (0.4, 2.42, 0.3, 0.36), (0.85, 2.3, 0.4, 0.5),
                                       (-1.25, 2.45, 0.3, 0.36), (1.45, 2.15, 0.3, 0.3))):
        S.wboxr(x - w / 2, y - h / 2, ZB, x + w / 2, y + h / 2, ZB + 0.025, 'trim')
        S.wboxr(x - w / 2 + 0.03, y - h / 2 + 0.03, ZB + 0.025, x + w / 2 - 0.03, y + h / 2 - 0.03, ZB + 0.03,
                'photo%d' % (i % 3))
    # Gus's armchair and a side table piled with auction catalogues
    if 'armchair' not in hide:
        with S.tag('armchair'):
            af = Frame((-1.15, 0, 0.75), Ry(-35))
            S.box(af, (0, 0.22, 0), (0.42, 0.2, 0.4), 0.06, 'leather')
            S.box(af, (0, 0.46, 0.02), (0.32, 0.06, 0.32), 0.05, 'leather')
            S.box(af, (0, 0.72, -0.34), (0.42, 0.34, 0.1), 0.08, 'leather')
            for sx in (-1, 1):
                S.box(af, (sx * 0.38, 0.55, 0), (0.08, 0.14, 0.38), 0.06, 'leather')
            S.cyl((-0.35, 0, 0.3), (-0.35, 0.55, 0.3), 0.025, 'wood_dk')
            S.fcyl((-0.35, 0.56, 0.3), 0.24, 0.015, 'wood')
            for k in range(4):
                S.wbox((-0.35 + 0.02 * k, 0.6 + k * 0.022, 0.3), (0.11, 0.01, 0.15), 'catalogue' if k == 3 else 'paper2',
                       rot=Ry(10 * k - 15))
            S.fcyl((-0.25, 0.7, 0.2), 0.05, 0.03, 'cigarbox')
    S.fcyl((-2.0, 3.25, ZB + 0.025), 0.2, 0.025, 'wood_dk', axis='z')                          # wall clock
    S.fcyl((-2.0, 3.25, ZB + 0.052), 0.17, 0.004, 'paper', axis='z')
    S.wbox((-2.0, 3.31, ZB + 0.06), (0.006, 0.06, 0.003), 'wood_dk')                              # ten past three
    S.wbox((-1.96, 3.24, ZB + 0.06), (0.045, 0.006, 0.003), 'wood_dk', rot=Rz(-15))

    # ---------------------------------------------------------------- the bare bulb overhead
    S.cyl((0.0, H, 0.2), (0.0, 3.3, 0.2), 0.008, 'steel_dk')
    S.sph((0.0, 3.25, 0.2), 0.05, 'bulb')
    S.light((0.0, 3.15, 0.2), (255, 214, 160), power=2.6, range=8, soft=18)
    S.light((0.0, 2.2, 4.5), (255, 220, 190), power=1.2, range=9, shadow=False)                  # soft fill from the front
    S.light((1.6, 1.6, 3.2), (255, 220, 190), power=0.9, range=3.5, shadow=False)                # on Gus and Shah

    cam = Camera((0.0, 2.75, 7.4), (0.0, 1.25, -2.2), fov=44, W=3840, H=2160)
    env = dict(sky=(30, 26, 22), bounce=(34, 26, 20), fog_col=(30, 26, 24), fog=0.02, fog_h0=0.0, fog_hf=0.06,
               fog_max=40, vol_scale=4, vol_steps=40, reflections=True, grid=0.5, ao_scale=0.9)
    meta = dict(
        room='stardust_office',
        walk=[(-3.05, -1.75), (2.35, -1.75), (2.35, 0.95), (2.45, 0.95), (2.45, 1.4), (2.0, 2.4), (-2.3, 2.4),
              (-2.3, 2.0), (-3.4, 2.0), (-3.4, 0.2), (-3.2, 0.2), (-3.2, -0.85), (-3.05, -0.85)],
        walk_zmin=-1.75, walk_zmax=2.4, scale_x=0.0,
        spawns={'stardust_shop': (-3.1, 0.75), 'stardust_roof': (2.2, -1.2), 'stardust_roof_dark': (2.2, -1.2),
                'start': (0.0, 1.0)},
        hotspots={
            'gus': ('Gus', (1.55, 2.05), 'right'),
            'shah': ('Dr. Shah', (1.55, 2.05), 'right'),
            'desk': ('desk', (dx, -1.5), 'up'),
            'drawer': ('desk drawer', (dx, -1.5), 'up'),
            'letter': ('eviction letter', (dx, -1.5), 'up'),
            'phone': ('cordless phone', (-3.0, -1.2), 'left'),
            'cabinet': ('filing cabinet', (-3.0, -1.2), 'left'),
            'fuse_panel': ('fuse panel', (-0.7, -1.6), 'up'),
            'pearl_locker': ('PEARL locker', (0.7, -1.55), 'up'),
            'gus_locker': ('GUS locker', (0.25, -1.55), 'up'),
            'stairs': ('stairs', (2.25, -1.3), 'right'),
            'curtain': ('curtain', (-3.3, 0.75), 'left'),
        },
        hotspot_shapes={
            'gus': [(gx - 0.35, 0.0, gz - 0.1), (gx + 0.4, 0.0, gz - 0.1), (gx + 0.4, 0.0, gz + 1.9),
                    (gx - 0.35, 0.0, gz + 1.9), (gx - 0.35, 0.4, gz + 1.0), (gx + 0.4, 0.4, gz + 1.0)],
            'shah': [(gx - 1.05, 0.0, gz + 1.0), (gx - 0.45, 0.0, gz + 1.0), (gx - 0.45, 1.2, gz + 1.0),
                     (gx - 1.05, 1.2, gz + 1.0)],
            'stairs': [(ST_X[0] - 0.05, 0.0, ST_Z0 + 0.05), (ST_X[1], 0.0, ST_Z0 + 0.05), (ST_X[1], ST_TOP + 2.0, ZB),
                       (ST_X[0], ST_TOP + 2.0, ZB)],
            'pearl_locker': [(lx0 + lw, 0.0, ZB + 0.5), (lx1 + 0.2, 0.0, ZB + 0.7), (lx1 + 0.2, 1.95, ZB + 0.7),
                             (lx0 + lw, 1.95, ZB + 0.5)],
        },
        hotspot_order=['curtain', 'cabinet', 'phone', 'desk', 'lamp', 'drawer', 'letter', 'fuse_panel', 'gus_locker',
                       'pearl_locker', 'stairs', 'gus', 'shah'],
        overlays=['sign_glow'],
        occluders={'boxes': (-2.9, 2.55), 'armchair': (-1.0, 1.15)},
        obstacles=[(gx - 0.75, gz + 1.0, 0.38), (-1.15, 0.75, 0.55), (-0.35, 0.3, 0.3)],
        char_fill=((236, 220, 200), 0.18),
        tint=(0.88, 0.8, 0.7),
        exposure=1.4,
    )
    return S, cam, env, meta
