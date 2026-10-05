"""The LA River channel under the Fletcher Drive bridge, 4:05 a.m. (Case 4, scene 3), looking downstream with the
bridge's two concrete arches overhead.

Sloped concrete banks green with algae on both sides, a few inches of water sliding down the middle, and under the
bridge, around its pier, a black island of reeds and young willows. A drain pipe pokes out of the pier and dribbles
into the reeds. On the near (west) apron, under the left arch, Preacher's tarp tent pitched square as a barracks, a
milk crate with his Bible, a folded flag, boots in a row, and Owen's heavy e-bike with its crushed yellow box, his
phone still glowing in the handlebar mount. On the far (east) side, at the foot of the bank, Owen lies on the dry
concrete, face away, his yellow bag beside him; Dr. Shah kneels by him with a flashlight. Concrete stairs come down
the east bank from the bridge, and two drag marks run down the algae from the gap in the chain-link at the top.

Overlays: Preacher at his tent (preacher, once he's freed), and Doss's spotlight from the bridge: a hard white beam
dropping onto the reeds, with something glinting in the roots (spot, once it's swung over the rail)."""
import math, random
import numpy as np
from scene3d import *
import textures as tx
import npc

BZ0, BZ1 = -11.0, -4.0        # the bridge's depth (its upstream face at BZ1, toward the camera)
SPRING = 0.6                  # where the arches spring from the pier and the banks
APRON = 8.0                   # the dry aprons run out to x = +-APRON, then the banks rise
BANK_TOP = 6.0                # the banks climb to here at x = +-(APRON + 6)
WATER = 2.4                   # the low-flow channel, x in [-WATER, WATER]
TENT = (-6.3, -5.6)
BIKE = (-4.5, -2.7)
PREACHER = (-5.2, -2.0)
OWEN = (5.7, 0.7)            # his feet; he lies along +x, head toward the bank
SHAH = (6.6, -0.45)           # beyond him, kneeling, facing the camera
STAIRS_X = (APRON, APRON + 6.0)
STAIRS_Z = -3.45
REEDS = (0.0, -2.4)           # the island's centre, in front of the pier
PIPE = (-0.85, 2.4, BZ1 - 0.02)


def build(hide=()):
    S = Scene()
    rng = random.Random(47)
    # ---------------------------------------------------------------- materials
    S.mat('apron', (255, 255, 255), tex=tx.hires(tx.channel_concrete(algae=0.15), 2), texmode=4, texmap=1,
          texscale=4.0, refl=0.2, ripple=0.1, spec=0.5, shin=40)
    S.mat('bank', (255, 255, 255), tex=tx.hires(tx.channel_concrete(algae=0.75), 2), texmode=4, texmap=1, texscale=4.0,
          refl=0.25, spec=0.6, shin=50)
    S.mat('bridge', (255, 255, 255), tex=tx.hires(tx.channel_concrete(seed=105, algae=0.05), 2), texmode=4, texmap=1,
          texscale=5.0, spec=0.2)
    S.mat('graffiti', (255, 255, 255), tex=tx.graffiti_wall(), texmode=1)
    S.mat('water', (16, 22, 24), refl=0.85, ripple=0.12, spec=1.2, shin=120)
    S.mat('silt', (54, 50, 40), namp=0.4, nscale=6, refl=0.3, spec=0.5)
    S.mat('reed', (84, 96, 52), namp=0.4, nscale=20, spec=0.3)
    S.mat('reed_dk', (50, 66, 36), namp=0.4, nscale=20, spec=0.3)
    S.mat('reed_dry', (150, 132, 84), namp=0.4, nscale=20, spec=0.2)
    S.mat('willow', (34, 52, 30), namp=0.6, nscale=4, bump=0.5, bscale=6)
    S.mat('trunk', (60, 50, 40), namp=0.3, nscale=10)
    S.mat('pipe', (90, 70, 56), spec=0.6, shin=40, namp=0.3, nscale=10)
    S.mat('pipe_in', (6, 6, 8))
    S.mat('rail', (172, 166, 152), namp=0.25, nscale=4)
    S.mat('iron', (36, 40, 38), spec=0.7, shin=40)
    S.mat('globe_on', (255, 230, 190), emis=(255, 214, 160), emis_mult=4)
    S.mat('stair', (150, 146, 136), namp=0.3, nscale=5, refl=0.1, spec=0.3)
    S.mat('mud', (40, 36, 28), spec=0.4, refl=0.2)
    S.mat('drag', (26, 30, 20), spec=0.6, refl=0.3)
    S.mat('chain', (120, 124, 126), spec=0.9, shin=50)
    S.mat('post', (90, 92, 94), spec=0.8, shin=40)
    S.mat('pathlamp', (255, 220, 160), emis=(255, 200, 130), emis_mult=3)
    S.mat('hills', (0, 0, 0), tex=tx.night_hills(seed=106), texmode=3, texemis=1.4)
    # the camp
    S.mat('tarp', (255, 255, 255), tex=tx.tent_tarp(), texmode=4, texmap=1, texscale=1.2, spec=0.4, refl=0.05)
    S.mat('crate', (40, 70, 140), spec=0.3)
    S.mat('bible', (30, 24, 22), spec=0.3)
    S.mat('flag', (255, 255, 255), tex=tx.flag_folded(), texmode=1)
    S.mat('boot', (44, 34, 26), spec=0.4)
    S.mat('cart', (150, 152, 156), spec=1.2, shin=60, refl=0.2)
    S.mat('rope', (150, 130, 90))
    S.mat('cart_red', (150, 30, 30), spec=0.5)
    S.mat('cone', (220, 90, 20), spec=0.4)
    S.mat('bag', (190, 190, 196), spec=0.8, shin=40)
    # the bike, Owen, the coroner's things
    S.mat('frame', (40, 44, 48), spec=0.9, shin=60)
    S.mat('tire', (16, 16, 18))
    S.mat('chomp', (240, 196, 30), tex=tx.chomp_box(), texmode=1, spec=0.4)
    S.mat('chomp_plain', (240, 196, 30), spec=0.4)
    S.mat('phone_lit', (20, 30, 40), emis=(150, 190, 230), emis_mult=1.6)
    S.mat('red_lamp', (120, 10, 10), emis=(255, 20, 20), emis_mult=1.5)
    S.mat('lantern', (255, 240, 220), emis=(255, 240, 220), emis_mult=4)
    S.mat('case', (150, 150, 156), spec=1.0, shin=60)
    S.mat('glint', (240, 244, 250), spec=3.0, shin=200, emis=(200, 210, 230), emis_mult=1.2)
    S.mat('phone_blk', (14, 14, 16), spec=1.2, shin=90)

    # ---------------------------------------------------------------- the bridge: a block with two arches cut through it
    S.wboxr(-24, SPRING - 0.4, BZ0, 24, 10.0, BZ1, 'bridge')
    for sx in (-1, 1):
        cx = sx * (1.25 + 6.6)
        S.tcyl(Frame((cx, SPRING, (BZ0 + BZ1) / 2), Rx(90)), (0, 0, 0), (6.6, 8.4), (6.6, 8.4), (BZ1 - BZ0) / 2 + 0.2,
               'bridge', op=1)
    S.wboxr(-24, 10.0, BZ0 - 0.2, 24, 10.25, BZ1 + 0.2, 'rail')                    # the deck's edge
    with S.tag('bridge_face'):
        S.wbox((-0.0, SPRING + 0.8, BZ1 + 0.01), (1.2, 0.6, 0.005), 'graffiti')      # tags on the pier
    # the balustrade along the top, with two lamp posts, one lit
    for x in np.arange(-16, 16, 0.24):
        S.wboxr(x - 0.04, 10.25, BZ1 + 0.1, x + 0.04, 11.0, BZ1 + 0.2, 'rail')
    S.wboxr(-16, 11.0, BZ1 + 0.05, 16, 11.12, BZ1 + 0.26, 'rail')
    for px, on in ((-5.0, True), (4.2, False)):
        S.cyl((px, 10.25, BZ1 + 0.15), (px, 14.0, BZ1 + 0.15), 0.07, 'iron')
        S.sph((px, 14.3, BZ1 + 0.15), 0.25, 'globe_on' if on else 'iron')
        if on:
            S.light((px, 14.2, BZ1 + 0.6), (255, 196, 130), power=26, range=22, soft=14, vol=0.25)
    # work lights hung under the arches (the city's, for the bike path below the bridge)
    S.cyl((-6.0, 7.2, BZ1 - 2.0), (-6.0, 6.6, BZ1 - 2.0), 0.03, 'iron')
    S.sph((-6.0, 6.5, BZ1 - 2.0), 0.14, 'globe_on')
    S.light((-6.0, 6.2, BZ1 - 1.8), (255, 180, 110), power=9, range=12, soft=12, vol=0.25)
    S.cyl((6.4, 7.2, BZ1 - 2.0), (6.4, 6.6, BZ1 - 2.0), 0.03, 'iron')
    S.sph((6.4, 6.5, BZ1 - 2.0), 0.14, 'iron')
    # the patrol car's lights, turning up on the deck
    S.light((3.0, 11.6, BZ1 - 3.0), (255, 40, 30), power=7, range=10, soft=10, vol=0.2)
    S.light((2.0, 11.6, BZ1 - 3.0), (60, 100, 255), power=7, range=10, soft=10, vol=0.2)

    # ---------------------------------------------------------------- the channel: aprons, banks, water (after the cut)
    S.wboxr(-APRON, -0.5, -60, APRON, 0.0, 14, 'apron')
    for sx in (-1, 1):
        # the banks: 45 degree concrete slopes up to the bike paths
        S.wbox((sx * (APRON + 3.0), BANK_TOP / 2 - 0.2, -23), (0.25, 4.6, 37), 'bank', rot=Rz(-sx * 45))
        S.wboxr(sx * (APRON + 6.0) if sx > 0 else -40, BANK_TOP - 0.3, -60, 40 if sx > 0 else -(APRON + 6.0), BANK_TOP,
                14, 'apron')
    # the pier's base and cutwater, standing in the water (it carries the bridge between the arches)
    S.wboxr(-1.25, 0.0, BZ0, 1.25, SPRING + 0.2, BZ1, 'bridge')
    S.wbox((0, (SPRING + 0.2) / 2, BZ1), (0.9, (SPRING + 0.2) / 2, 0.9), 'bridge', rot=Ry(45))
    S.wboxr(-WATER, -0.08, -60, WATER, -0.02, 14, 'water')
    for (x, z, rx, rz) in ((-4.2, 2.6, 1.0, 0.3), (3.6, 4.4, 0.8, 0.25), (6.8, 1.8, 0.7, 0.2), (-6.2, 0.4, 0.6, 0.2)):
        S.ell(WORLD, (x, 0.0, z), (rx, 0.01, rz), 'water')
    # the drain pipe out of the pier, dribbling into the reeds
    with S.tag('drain_pipe'):
        S.fcyl((PIPE[0], PIPE[1], PIPE[2]), 0.2, 0.55, 'pipe', axis='z')
        S.cyl((PIPE[0], PIPE[1], PIPE[2] + 0.5), (PIPE[0], PIPE[1], PIPE[2] + 0.57), 0.15, 'pipe_in')
        for k in range(6):
            y = PIPE[1] - 0.2 - k * 0.45
            S.cyl((PIPE[0], y, PIPE[2] + 0.6 + k * 0.02), (PIPE[0], y - 0.35, PIPE[2] + 0.62 + k * 0.02), 0.012,
                  'water')
    # the reed island and its young willows
    with S.tag('reeds'):
        rx0, rz0 = REEDS
        for (dx, dz, a, b) in ((0, 0, 2.3, 1.5), (-1.0, 0.4, 1.4, 1.0), (1.2, -0.2, 1.3, 1.1), (0.3, 0.8, 1.0, 0.7)):
            S.ell(WORLD, (rx0 + dx, -0.02, rz0 + dz), (a, 0.18, b), 'silt', k=0.3)
        for k in range(70):                                   # clumps of reed, each a fan of long blades
            a = rng.uniform(0, 2 * math.pi); r = math.sqrt(rng.random())
            wob = 1.0 + 0.22 * math.sin(3 * a + 1.0) + 0.12 * math.sin(5 * a)            # a ragged edge
            x, z = rx0 + 2.2 * r * wob * math.cos(a), rz0 + 1.5 * r * wob * math.sin(a)
            h = rng.uniform(1.3, 2.4) * (1.15 - 0.35 * r)
            mat_ = rng.choice(('reed', 'reed', 'reed_dk', 'reed_dry'))
            for b in range(7):
                d = rng.uniform(0, 2 * math.pi); spread = rng.uniform(0.05, 0.45)
                mid = (x + spread * 0.4 * math.cos(d), h * 0.55, z + spread * 0.4 * math.sin(d))
                tip = (x + spread * math.cos(d) * 1.4, h * rng.uniform(0.75, 1.0), z + spread * math.sin(d) * 1.4)
                S.cone((x, 0.0, z), mid, 0.022, 0.014, mat_)
                S.cone(mid, tip, 0.014, 0.003, mat_)
    with S.tag('willows'):
        for (x, z, r) in ((-1.7, -3.5, 0.75), (1.8, -3.3, 0.7)):
            S.cyl((x, 0.0, z), (x + 0.1, 1.6, z), 0.08, 'trunk')
            for k in range(14):                               # weeping fronds hanging from a little crown
                a = k * 2 * math.pi / 14
                top = (x + 0.1 + 0.25 * math.cos(a), 1.75, z + 0.25 * math.sin(a))
                bot = (x + 0.1 + r * 0.8 * math.cos(a), 0.55 + 0.2 * math.sin(a * 3), z + r * 0.8 * math.sin(a))
                S.cone(top, bot, 0.09, 0.03, 'willow', k=0.04)
            S.ell(WORLD, (x + 0.1, 1.8, z), (0.4, 0.2, 0.4), 'willow', k=0.1)

    # ---------------------------------------------------------------- the east bank: the stairs, the fence, the drag marks
    x0s, x1s = STAIRS_X
    with S.tag('stairs'):
        n = 20
        for k in range(n):
            xa = x0s + k * (x1s - x0s) / n
            y = (k + 1) * BANK_TOP / n
            S.wboxr(xa, 0.0, STAIRS_Z - 0.75, xa + (x1s - x0s) / n + 0.02, y, STAIRS_Z + 0.75, 'stair')
            if k % 2 == 0:                                    # the tire line and boot prints, muddy, down the middle
                S.wboxr(xa + 0.05, y, STAIRS_Z - 0.03, xa + 0.25, y + 0.004, STAIRS_Z + 0.03, 'mud')
                S.wboxr(xa + 0.1, y, STAIRS_Z + 0.18, xa + 0.24, y + 0.004, STAIRS_Z + 0.3, 'mud')
        S.cyl((x0s, 1.0, STAIRS_Z + 0.8), (x1s, BANK_TOP + 1.0, STAIRS_Z + 0.8), 0.03, 'post')
        for k in range(4):
            xa = x0s + k * (x1s - x0s) / 3
            S.cyl((xa, xa - x0s, STAIRS_Z + 0.8), (xa, xa - x0s + 1.0, STAIRS_Z + 0.8), 0.03, 'post')
    xf = APRON + 6.2
    for z in np.arange(-3.0, 14, 2.4):                       # the chain-link along the top of the east bank
        S.cyl((xf, BANK_TOP, z), (xf, BANK_TOP + 1.8, z), 0.035, 'post')
    S.cyl((xf, BANK_TOP + 1.75, -3.0), (xf, BANK_TOP + 1.75, 14), 0.025, 'post')
    for z in np.arange(-1.4, 14, 0.5):
        S.cyl((xf, BANK_TOP + 0.1, z), (xf, BANK_TOP + 1.7, z + 0.5), 0.008, 'chain')
    with S.tag('east_bank'):
        # two heel lines from the gap at the top (z ~ -2.2) down the slope to Owen's head
        for dz in (-0.12, 0.12):
            pts = [(xf - 0.1, BANK_TOP, -1.6 + dz), (APRON + 3.0, 3.0, -0.4 + dz), (APRON + 0.2, 0.2, 0.6 + dz)]
            for a, b in zip(pts, pts[1:]):
                S.cyl((a[0], a[1] + 0.02, a[2]), (b[0], b[1] + 0.02, b[2]), 0.045, 'drag')
    S.light((xf - 1.0, BANK_TOP + 2.5, -1.5), (255, 200, 140), power=3, range=8, soft=10)     # a path lamp, up top

    # ---------------------------------------------------------------- downstream: the far channel, the valley, the hills
    for z in np.arange(4, -60, -14):
        for sx in (-1, 1):
            S.sph((sx * (APRON + 7.0), BANK_TOP + 2.6, z), 0.16, 'pathlamp')
            S.cyl((sx * (APRON + 7.0), BANK_TOP, z), (sx * (APRON + 7.0), BANK_TOP + 2.5, z), 0.05, 'iron')
    S.light((0, BANK_TOP, -40), (255, 170, 100), power=14, range=30, shadow=False)
    S.wbox((0, 6, -90), (120, 18, 1), 'hills')

    # ---------------------------------------------------------------- Preacher's camp, under the left arch
    tx_, tz_ = TENT
    with S.tag('tent'):
        T = Frame((tx_, 0, tz_), Ry(8))
        for s in (-1, 1):                                   # a ridge tent: two pitched tarp slopes, guyed square
            S.box(T, (s * 0.62, 0.62, 0), (0.02, 0.86, 1.25), 0.0, 'tarp', rot=Rz(s * 44))
        S.box(T, (0, 0.62, -1.24), (0.62, 0.6, 0.02), 0.0, 'tarp')
        S.cyl(T.to((0, 1.22, -1.3)), T.to((0, 1.22, 1.3)), 0.02, 'rope')
        S.wbox(T.to((0.0, 0.0, 1.5)), (0.04, 0.04, 0.04), 'iron')
        S.box(T, (0.9, 0.17, 1.6), (0.2, 0.17, 0.15), 0.01, 'crate')                       # the milk crate
        S.box(T, (0.9, 0.36, 1.6), (0.08, 0.02, 0.11), 0.005, 'bible')                     # his Bible on it
        S.box(T, (0.5, 0.05, 1.65), (0.12, 0.05, 0.12), 0.01, 'flag', rot=Ry(45))          # the folded flag
        S.fcyl(T.to((1.3, 0.14, 1.2)), 0.08, 0.14, 'lantern')                             # his camp lantern
        for k in range(2):                                                                 # boots, lined up
            S.box(T, (-0.4 + k * 0.16, 0.08, 1.45), (0.05, 0.08, 0.13), 0.03, 'boot')
    # Owen's e-bike, propped at the tent, its rack bent flat and the yellow box caved in
    bx, bz = BIKE
    B = Frame((bx, 0, bz), Ry(-14))                           # side-on to the camera, front to the right
    with S.tag('bike'):
        for wx in (-0.55, 0.55):                              # fat tires on spoked rims
            ring = [B.to((wx + 0.34 * math.cos(a), 0.36 + 0.34 * math.sin(a), 0)) for a in np.linspace(0, 2 * math.pi, 19)]
            for a, b in zip(ring, ring[1:]):
                S.cyl(a, b, 0.035, 'tire')
            for k in range(8):
                a = k * math.pi / 8
                S.cyl(B.to((wx - 0.3 * math.cos(a), 0.36 - 0.3 * math.sin(a), 0)),
                      B.to((wx + 0.3 * math.cos(a), 0.36 + 0.3 * math.sin(a), 0)), 0.004, 'case')
            S.cyl(B.to((wx, 0.36, -0.03)), B.to((wx, 0.36, 0.03)), 0.04, 'frame')
        S.cyl(B.to((-0.55, 0.36, 0)), B.to((0.0, 0.42, 0)), 0.03, 'frame')
        S.cyl(B.to((0.0, 0.42, 0)), B.to((0.42, 0.95, 0)), 0.035, 'frame')                    # down tube
        S.cyl(B.to((-0.2, 0.85, 0)), B.to((0.42, 0.95, 0)), 0.03, 'frame')                    # top tube
        S.cyl(B.to((-0.2, 0.85, 0)), B.to((-0.55, 0.36, 0)), 0.025, 'frame')
        S.cyl(B.to((0.0, 0.42, 0)), B.to((-0.2, 0.85, 0)), 0.03, 'frame')                     # seat tube
        S.box(B, (-0.24, 0.9, 0), (0.12, 0.03, 0.06), 0.02, 'tire')                           # saddle
        S.box(B, (0.12, 0.65, 0), (0.18, 0.06, 0.06), 0.02, 'frame', rot=Rz(50))              # battery
        S.cyl(B.to((0.42, 0.95, 0)), B.to((0.55, 0.36, 0)), 0.025, 'frame')                   # fork
        S.cyl(B.to((0.42, 0.95, 0)), B.to((0.38, 1.1, 0)), 0.025, 'frame')
        S.cyl(B.to((0.38, 1.1, -0.3)), B.to((0.38, 1.1, 0.3)), 0.018, 'frame')                # handlebar
        # the crushed rack and box
        S.box(B, (-0.62, 0.62, 0), (0.24, 0.02, 0.16), 0.0, 'frame', rot=Rz(-12))
        S.box(B, (-0.62, 0.88, 0), (0.24, 0.2, 0.22), 0.02, 'chomp', rot=Rz(-16) @ Rx(6))
        S.ell(B, (-0.7, 1.08, 0.05), (0.18, 0.08, 0.16), 'chomp_plain', op=1, k=0.04)        # caved in
        S.box(B, (-0.9, 0.6, 0), (0.02, 0.03, 0.04), 0.0, 'red_lamp')
    with S.tag('phone'):                                      # Owen's phone, still on, in the handlebar mount
        S.box(B, (0.38, 1.17, 0.02), (0.04, 0.07, 0.006), 0.004, 'phone_lit', rot=Rx(-90) @ Rx(30) @ Rz(90))
    S.light(B.to((0.4, 1.3, 0.1)), (150, 190, 230), power=0.12, range=0.8, shadow=False)

    # ---------------------------------------------------------------- the shopping cart in the foreground (left)
    if 'cart' not in hide:
        with S.tag('cart'):
            C = Frame((-3.6, 0, 5.9), Ry(28) @ Rz(-4))
            # the basket: a wire box, wider at the handle end, on a chassis with four casters
            def ring(y, w, z0, z1):
                pts = [(-w, y, z0), (w, y, z0), (w, y, z1), (-w, y, z1), (-w, y, z0)]
                for a, b in zip(pts, pts[1:]):
                    S.cyl(C.to(a), C.to(b), 0.011, 'cart')
            for k, y in enumerate((0.5, 0.65, 0.8, 0.95)):
                ring(y, 0.27 + k * 0.012, -0.42 - k * 0.02, 0.5)
            for s_ in (-1, 1):
                for z in np.arange(-0.42, 0.51, 0.09):
                    S.cyl(C.to((s_ * 0.27, 0.5, z)), C.to((s_ * 0.31, 0.95, z - 0.03)), 0.006, 'cart')
            for x in np.arange(-0.26, 0.27, 0.065):
                S.cyl(C.to((x, 0.5, -0.42)), C.to((x * 1.1, 0.95, -0.48)), 0.006, 'cart')
                S.cyl(C.to((x, 0.5, -0.42)), C.to((x, 0.5, 0.5)), 0.005, 'cart')
            S.cyl(C.to((-0.32, 1.08, 0.62)), C.to((0.32, 1.08, 0.62)), 0.022, 'cart_red')               # the handle
            for s_ in (-1, 1):
                S.cyl(C.to((s_ * 0.3, 0.95, 0.5)), C.to((s_ * 0.31, 1.08, 0.62)), 0.012, 'cart')
                S.cyl(C.to((s_ * 0.22, 0.08, -0.4)), C.to((s_ * 0.26, 0.5, -0.4)), 0.014, 'cart')
                S.cyl(C.to((s_ * 0.26, 0.08, 0.45)), C.to((s_ * 0.27, 0.5, 0.48)), 0.014, 'cart')
                S.cyl(C.to((s_ * 0.22, 0.08, -0.4)), C.to((s_ * 0.26, 0.08, 0.45)), 0.014, 'cart')
                for z in (-0.4, 0.45):
                    S.fcyl(C.to((s_ * 0.24, 0.045, z)), 0.045, 0.015, 'tire', axis='x')
            S.ell(C, (0.0, 0.62, 0.0), (0.24, 0.12, 0.38), 'tarp')                                  # a bundle in it

    # a heap of river junk in the right foreground: a tire, a broken pallet, a traffic cone, plastic bags
    if 'debris' not in hide:
        with S.tag('debris'):
            dx, dz = 3.4, 6.4
            T2 = Frame((dx, 0.115, dz), Ry(20) @ Rx(6))                 # an old tire, lying flat
            ring = [T2.to((0.3 * math.cos(a), 0, 0.3 * math.sin(a))) for a in np.linspace(0, 2 * math.pi, 17)]
            for a, b in zip(ring, ring[1:]):
                S.cyl(a, b, 0.11, 'tire')
            for k in range(4):
                S.wbox((dx + 0.6, 0.06 + k * 0.02, dz - 0.5 + k * 0.2), (0.6, 0.02, 0.06), 'trunk', rot=Ry(30 + k * 4))
            S.cone((dx - 0.5, 0.0, dz - 0.4), (dx - 0.62, 0.55, dz - 0.38), 0.17, 0.03, 'cone')
            S.ell(WORLD, (dx + 0.75, 0.12, dz + 0.35), (0.3, 0.12, 0.2), 'bag', k=0.05)
    # ---------------------------------------------------------------- Owen, Dr. Shah, the coroner's lantern
    ox, oz = OWEN
    # on his side, face away: knees drawn up a little, the top leg resting forward on the lower one, arms loose
    npc.cast(S, 'owen', dict(npc.STAND, lhp=46, lk=70, labd=-4, rhp=26, rk=48, rabd=0, lsp=40, lsa=0, le=50, lin=20,
                             rsp=56, rsa=4, re=30, hy=14, hp=16, lean=8),
             (ox, 0.21, oz), yaw=180, scale=0.94, rot=Rz(90), tag='owen')
    with S.tag('owen'):
        S.box(WORLD, (ox + 0.7, 0.22, oz + 0.75), (0.24, 0.22, 0.2), 0.03, 'chomp', rot=Ry(-20))   # his yellow bag
    npc.cast(S, 'shah', dict(npc.CROUCH, rsp=58, re=26, rin=24, lsp=40, le=70, lin=36, hp=30, hy=-6,
                             props=(('torch', 'r'),)),
             (SHAH[0], 0, SHAH[1]), yaw=-18, scale=0.95, tag='shah')
    S.wbox((SHAH[0] - 0.9, 0.12, SHAH[1] - 0.2), (0.16, 0.12, 0.1), 'case', rnd=0.02)          # her kit
    S.fcyl((OWEN[0] - 0.5, 0.15, OWEN[1] + 1.0), 0.07, 0.15, 'lantern')
    S.light((OWEN[0] - 0.5, 0.6, OWEN[1] + 1.05), (255, 240, 220), power=4.5, range=7, soft=10)
    S.light((SHAH[0] + 0.1, 0.8, SHAH[1] + 0.3), (255, 245, 230), power=1.4, range=3, soft=8,
            spot=((0.1, -0.7, 0.6), 15, 35))                                                     # her flashlight

    # ---------------------------------------------------------------- Preacher at his tent (overlay, once he's freed)
    if 'preacher' not in hide:
        npc.cast(S, 'preacher', dict(npc.STAND, props=(('book', 'r'),), rsp=32, re=84, rin=34, lsp=4, le=16, hp=18,
                                     hy=-8),
                 (PREACHER[0], 0, PREACHER[1]), yaw=40, scale=0.94, tag='preacher')
        S.light((PREACHER[0] + 0.5, 1.7, PREACHER[1] + 0.8), (255, 210, 150), power=0.6, range=2.5, soft=8)

    # ---------------------------------------------------------------- Doss's spotlight on the reeds (overlay)
    if 'spot' not in hide:
        S.light((REEDS[0] + 0.8, 11.3, BZ1 + 0.6), (255, 250, 236), power=170, range=18, soft=6, vol=0.7,
                spot=(nrm((REEDS[0] - 0.6, -11.3, REEDS[1] - 0.2 - BZ1 - 0.6)), 8, 13))
        S.cyl((REEDS[0] + 0.8, 11.1, BZ1 + 0.25), (REEDS[0] + 0.8, 11.5, BZ1 + 0.6), 0.1, 'globe_on')
        with S.tag('glint'):                                  # the broken headlight in the roots, catching the light
            gx, gz = REEDS[0] + 0.5, REEDS[1] + 1.1
            S.box(WORLD, (gx, 0.08, gz), (0.14, 0.05, 0.08), 0.01, 'glint', rot=Ry(30) @ Rz(25))
            S.box(WORLD, (gx - 0.5, 0.05, gz + 0.2), (0.04, 0.012, 0.075), 0.006, 'phone_blk', rot=Ry(-20))

    S.sun((0.3, -1, -0.5), (70, 80, 120), power=0.3, shadow=False)
    S.light((0, 4, 12), (110, 120, 160), power=3.0, range=24, shadow=False)                    # city glow behind
    S.light(Frame((TENT[0], 0, TENT[1]), Ry(8)).to((1.3, 0.5, 1.2)), (255, 200, 140), power=1.6, range=4.5, soft=10)

    cam = Camera((0.6, 2.2, 13.6), (0.3, 3.4, -5.0), fov=48, W=3840, H=2160)
    env = dict(sky=(26, 22, 38), bounce=(16, 14, 20), fog_col=(30, 26, 40), fog=0.03, fog_h0=0.0, fog_hf=0.08,
               fog_max=110, vol_scale=4, vol_steps=48, reflections=True, grid=0.7, ao_scale=1.2)
    walk = [(-7.6, 7.2), (-7.6, -4.2), (-4.9, -4.2), (-3.4, -1.0), (-2.5, 0.0), (2.5, 0.0), (3.3, -1.0),
            (APRON - 0.4, -2.6), (APRON - 0.4, -0.9), (5.2, -0.9), (5.2, 2.3), (APRON - 0.4, 2.3), (APRON - 0.4, 7.2)]
    meta = dict(
        room='river_channel',
        walk=walk,
        walk_zmin=-3.8, walk_zmax=7.0, scale_x=0.0,
        spawns={'fletcher_bridge': (APRON - 0.6, -2.4), 'start': (0.0, 3.0)},
        hotspots={
            'owen': ('Owen', (OWEN[0] - 0.6, OWEN[1] - 0.1), 'right'),
            'shah': ('Dr. Shah', (SHAH[0] - 1.5, SHAH[1] - 0.9), 'right'),
            'bike': ('e-bike', (BIKE[0] + 0.3, -1.6), 'up'),
            'phone': ("Owen's phone", (BIKE[0] + 0.5, -1.6), 'up'),
            'tent': ("Preacher's tent", (TENT[0] + 1.6, -3.4), 'left'),
            'preacher': ('Preacher', (PREACHER[0] + 0.9, -1.2), 'left'),
            'east_bank': ('east bank', (APRON - 0.8, -0.8), 'right'),
            'stairs': ('stairs', (APRON - 0.6, -2.4), 'right'),
            'reeds': ('reeds', (REEDS[0] + 0.8, 0.4), 'up'),
            'drain_pipe': ('drain pipe', (REEDS[0] + 0.8, 0.4), 'up'),
            'water': ('water', (-0.8, 2.5), 'down'),
            'willows': ('willows', None, 'up'),
            'beam': ("Doss's spotlight", None, 'up'),
        },
        hotspot_shapes={
            'owen': [(ox - 0.2, 0.0, oz - 0.5), (ox + 2.0, 0.0, oz - 0.5), (ox + 2.0, 0.5, oz + 1.0), (ox - 0.2, 0.5, oz + 1.0)],
            'shah': [(SHAH[0] - 0.4, 0.0, SHAH[1]), (SHAH[0] + 0.4, 0.0, SHAH[1]), (SHAH[0] + 0.4, 1.35, SHAH[1]),
                     (SHAH[0] - 0.4, 1.35, SHAH[1])],
            'phone': [B.to((0.3, 1.08, 0)), B.to((0.48, 1.08, 0)), B.to((0.48, 1.28, 0)), B.to((0.3, 1.28, 0))],
            'preacher': [(PREACHER[0] - 0.35, 0.0, PREACHER[1]), (PREACHER[0] + 0.35, 0.0, PREACHER[1]),
                         (PREACHER[0] + 0.35, 1.8, PREACHER[1]), (PREACHER[0] - 0.35, 1.8, PREACHER[1])],
            'east_bank': [(APRON, 0.0, -1.2), (APRON + 6.0, BANK_TOP, -1.2), (APRON + 6.0, BANK_TOP, 4.0),
                          (APRON, 0.0, 4.0)],
            'reeds': [(-2.4, 0.0, REEDS[1] + 1.6), (2.4, 0.0, REEDS[1] + 1.6), (2.4, 1.8, REEDS[1]),
                      (-2.4, 1.8, REEDS[1])],
            'drain_pipe': [(PIPE[0] - 0.3, PIPE[1] - 0.3, PIPE[2]), (PIPE[0] + 0.3, PIPE[1] - 0.3, PIPE[2]),
                           (PIPE[0] + 0.3, PIPE[1] + 0.3, PIPE[2]), (PIPE[0] - 0.3, PIPE[1] + 0.3, PIPE[2])],
            'water': [(-WATER, 0.0, 0.2), (WATER, 0.0, 0.2), (WATER, 0.0, 6.0), (-WATER, 0.0, 6.0)],
            'beam': [(REEDS[0] - 0.4, 2.6, BZ1 + 0.4), (REEDS[0] + 1.6, 2.6, BZ1 + 0.4),
                     (REEDS[0] + 1.6, 10.8, BZ1 + 0.4), (REEDS[0] - 0.4, 10.8, BZ1 + 0.4)],
        },
        hotspot_order=['beam', 'willows', 'water', 'east_bank', 'stairs', 'reeds', 'drain_pipe', 'tent', 'bike', 'phone',
                       'preacher', 'owen', 'shah'],
        overlays=['preacher', 'spot'],
        overlay_bases={'preacher': PREACHER},
        occluders={'cart': (-3.6, 5.9), 'debris': (3.4, 6.4)},
        obstacles=[(BIKE[0], BIKE[1], 0.6), (SHAH[0], SHAH[1], 0.4), (OWEN[0] + 0.8, OWEN[1], 0.6),
                   (TENT[0], TENT[1] + 0.6, 0.9), (-3.6, 5.9, 0.6), (3.4, 6.4, 0.7)],
        char_fill=((200, 196, 220), 0.2),
        tint=(0.76, 0.78, 0.86),
        exposure=2.25,
    )
    return S, cam, env, meta
