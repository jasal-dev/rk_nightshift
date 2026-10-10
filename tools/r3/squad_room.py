"""Homicide squad room, present day, a little past midnight. Seen from high up like the old adventure games."""
import math, random
import numpy as np
from scene3d import *
import textures as tx


def build(hide=()):
    S = Scene()
    # ---------------------------------------------------------------- materials
    S.mat('floor', (150, 156, 170), tex=tx.hires(tx.linoleum(), 2), texmode=4, texmap=1, texscale=1.2, refl=0.0, spec=0.15, shin=30)
    S.mat('wall', (122, 128, 118), namp=0.05, nscale=2)
    S.mat('wall_lo', (84, 70, 58), namp=0.1, nscale=6)
    S.mat('trim', (58, 46, 38), spec=0.2)
    S.mat('ceiling', (150, 150, 146))
    S.mat('desk', (92, 74, 58), namp=0.12, nscale=5, spec=0.25, shin=25)
    S.mat('desk_metal', (88, 92, 96), spec=0.3, shin=20)
    S.mat('basket', (120, 126, 120), spec=0.5, shin=20, namp=0.15, nscale=40)
    S.mat('chair', (28, 28, 32), spec=0.3)
    S.mat('plastic_dk', (24, 25, 28), spec=0.4, shin=30)
    S.mat('plastic_lt', (170, 168, 160), spec=0.2)
    S.mat('paper', (226, 222, 206))
    S.mat('folder', (196, 160, 96))
    S.mat('folder_r', (150, 50, 40))
    S.mat('lamp_shade', (40, 110, 76), spec=0.9, shin=60)
    S.mat('brass', (176, 140, 60), spec=1.2, shin=50)
    S.mat('bulb', (255, 220, 160), emis=(255, 210, 150), emis_mult=5)
    S.mat('mug', (220, 214, 200), spec=0.5, shin=40)
    S.mat('mug_band', (150, 30, 30), spec=0.5)
    S.mat('coffee', (40, 22, 14), spec=1.0, shin=80)
    S.mat('cabinet', (96, 104, 100), spec=0.4, shin=25, namp=0.05, nscale=6)
    S.mat('label', (230, 224, 200))
    S.mat('board', (230, 232, 226), tex=tx.hires(tx.murder_board(), 2), texmode=1, spec=0.3)
    S.mat('glass_door', (60, 66, 64), tex=tx.sign_board('HOMICIDE', (40, 40, 40), (190, 205, 198), 256, 64), texmode=3,
          texemis=0.5)
    S.mat('exit', (30, 160, 70), tex=tx.sign_board('EXIT', (230, 255, 230), (20, 120, 50), 128, 48), texmode=3, texemis=2.0)
    S.mat('door', (110, 80, 56), namp=0.1, nscale=6)
    S.mat('city', (14, 12, 22), tex=tx.skyline(12, 1024, 256, k=3), texmode=3, texemis=1.3)
    S.mat('slat', (164, 158, 140), spec=0.2)
    S.mat('radiator', (120, 122, 116), spec=0.3)
    S.mat('fixture', (60, 62, 64))
    S.mat('fluor_on', (240, 245, 240), emis=(220, 235, 230), emis_mult=2.2)
    S.mat('fluor_off', (120, 124, 120), spec=0.3)
    for i, kind in enumerate(['code', 'mug', 'code', 'off', 'code']):
        S.mat(f'screen{i}', (8, 10, 14), tex=tx.hires(tx.monitor(i, kind=kind), 3), texmode=3, texemis=1.8, spec=0.8, shin=60)
    S.mat('coatfab', (52, 50, 56), namp=0.1, nscale=8)
    S.mat('clock_face', (230, 228, 220), emis=(60, 60, 56))
    S.mat('black', (12, 12, 14))
    S.mat('cooler_blue', (90, 130, 190), spec=0.8, shin=40, refl=0.1)
    S.mat('plant', (40, 60, 34), namp=0.3, nscale=10)
    S.mat('pot', (120, 60, 40))

    X0, X1, Z0, ZB = -6.0, 5.8, -4.6, 9.0      # room extents (front wall omitted)
    WH = 3.7
    S.mat('ceil_tiles', (210, 210, 205), tex=tx.hires(tx.ceiling_tiles(), 2), texmode=4, texmap=1, texscale=2.4)
    S.wboxr(X0 - 1, -0.5, Z0 - 1, X1 + 1, 0.0, ZB, 'floor')
    S.wboxr(X0 - 0.3, 0, Z0 - 0.3, X1 + 0.3, WH, Z0, 'wall')          # back wall
    S.wboxr(X0 - 0.3, 0, Z0, X0, WH, ZB, 'wall')                        # left wall
    S.wboxr(X1, 0, Z0, X1 + 0.3, WH, ZB, 'wall')                        # right wall
    for (a, b, c, d) in [(X0, Z0, X1, Z0 + 0.02), (X0, Z0, X0 + 0.02, ZB), (X1 - 0.02, Z0, X1, ZB)]:
        S.wboxr(a, 0, b, c, 1.0, d, 'wall_lo')                          # lower wall paint
    S.wboxr(X0, 1.0, Z0, X1, 1.06, Z0 + 0.05, 'trim')
    S.wboxr(X0, 1.0, Z0, X0 + 0.05, 1.06, ZB, 'trim')
    S.wboxr(X1 - 0.05, 1.0, Z0, X1, 1.06, ZB, 'trim')
    S.wboxr(X0, 0, Z0, X1, 0.1, Z0 + 0.04, 'trim')
    S.wboxr(X0 - 0.3, WH, Z0 - 0.3, X1 + 0.3, WH + 0.2, ZB, 'ceil_tiles')

    # ---------------------------------------------------------------- back wall: windows with blinds
    with S.tag('window'):
        for (wx0, wx1) in [(-1.6, 1.0), (1.4, 4.0)]:
            S.wboxr(wx0, 1.1, Z0 - 0.35, wx1, 2.9, Z0 + 0.02, 'wall', op=1)
            S.wboxr(wx0 - 0.08, 1.02, Z0 - 0.3, wx1 + 0.08, 1.1, Z0 + 0.12, 'trim')   # sill
            for y in np.arange(1.16, 2.86, 0.085):
                S.wbox(((wx0 + wx1) / 2, y, Z0 - 0.12), ((wx1 - wx0) / 2 - 0.02, 0.006, 0.035), 'slat', rot=Rx(-35))
            S.cyl((wx0 + 0.3, 1.2, Z0 - 0.08), (wx0 + 0.3, 2.85, Z0 - 0.08), 0.004, 'slat')
    S.wboxr(-30, -5, Z0 - 16.2, 30, 20, Z0 - 16, 'city')               # the city outside
    S.wboxr(-30, -5, Z0 - 16, 30, -4.0, Z0 - 0.3, 'black')
    with S.tag('radiator'):
        S.wboxr(-1.3, 0.15, Z0, 0.7, 0.85, Z0 + 0.22, 'radiator', rnd=0.02)
        for x in np.arange(-1.25, 0.7, 0.12):
            S.wboxr(x, 0.2, Z0 + 0.2, x + 0.06, 0.8, Z0 + 0.24, 'radiator')
    with S.tag('clock'):
        S.cyl((-2.7, 2.85, Z0), (-2.7, 2.85, Z0 + 0.06), 0.24, 'black')
        S.cyl((-2.7, 2.85, Z0 + 0.05), (-2.7, 2.85, Z0 + 0.07), 0.21, 'clock_face')
        S.cyl((-2.7, 2.85, Z0 + 0.075), (-2.7, 3.01, Z0 + 0.075), 0.008, 'black')
        S.cyl((-2.7, 2.85, Z0 + 0.075), (-2.58, 2.87, Z0 + 0.075), 0.01, 'black')
    # the flag in the corner: an oak pole on a round base with a brass ball, and the Stars and Stripes hanging from it
    # in vertical pleats, its fly sagging away from the pole. Each pleat is a thin box with its own slice of the flag.
    FX, FZ, FTOP, HOIST, FLY, NP = 5.45, Z0 + 0.35, 2.4, 0.72, 1.25, 10
    S.tcyl(Frame((FX, 0.03, FZ)), (0, 0, 0), (0.17, 0.17), (0.19, 0.19), 0.03, 'trim')
    S.cyl((FX, 0.06, FZ), (FX, 2.46, FZ), 0.018, 'trim')
    S.cyl((FX, 2.44, FZ), (FX, 2.47, FZ), 0.026, 'brass')
    S.sph((FX, 2.51, FZ), 0.045, 'brass')
    flag = tx.us_flag()
    fw = flag.width / NP
    px, pz = FX - 0.02, FZ
    for i in range(NP):
        S.mat(f'flag{i}', (220, 220, 220), tex=flag.crop((round(i * fw), 0, round((i + 1) * fw), flag.height)),
              texmode=1, wrap=0.4, spec=0.1, shin=10)
        yaw = 180 - 12 + (32 if i % 2 == 0 else -32)                 # zigzag pleats around a fly 12 deg off the wall
        dx, dz = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
        w = FLY / NP
        top = FTOP - 0.12 * ((i + 0.5) / NP) ** 2                       # the fly end droops
        cx, cz = px + dx * w / 2, pz + dz * w / 2
        rot = Ry(math.degrees(math.atan2(-dz, dx)))
        S.wbox((cx, top - HOIST / 2, cz), (w / 2 + 0.004, HOIST / 2, 0.004), f'flag{i}', rot=rot)
        S.wbox((cx, top - HOIST - 0.015, cz), (w / 2 + 0.004, 0.015, 0.006), 'brass', rot=rot)    # gold fringe
        px, pz = px + dx * w, pz + dz * w

    # ---------------------------------------------------------------- murder board (left back)
    with S.tag('case_board'):
        S.wboxr(-3.55, 1.0, Z0 + 0.35, -1.85, 2.3, Z0 + 0.4, 'board')
        S.wboxr(-3.6, 0.95, Z0 + 0.3, -1.8, 1.0, Z0 + 0.5, 'desk_metal')
        for x in (-3.45, -1.95):
            S.cyl((x, 0, Z0 + 0.42), (x, 0.95, Z0 + 0.42), 0.03, 'desk_metal')
            S.wboxr(x - 0.25, 0.0, Z0 + 0.3, x + 0.25, 0.06, Z0 + 0.55, 'desk_metal')

    # pins that stay up between cases (overlays the game shows by flag): Danny's envelope (Case 1),
    # Kenji's corner (Case 2), the photo of Walt B.'s ride beside the envelope (Case 2, optional), Gus's corner
    # (Case 3), Walter Brenner's card above the ride receipt (Case 3, optional), Owen's corner (Case 4), the lab's receipt for
    # Danny's phone beside his photo (Case 4) and Pryce's invitation on the other side (Case 4, optional)
    BZ = Z0 + 0.4
    for tag, (x, y, w, h) in (('board_envelope', (-2.62, 1.36, 0.22, 0.29)), ('board_kenji', (-3.3, 1.92, 0.3, 0.4)),
                              ('board_receipt', (-2.34, 1.33, 0.15, 0.2)), ('board_gus', (-2.08, 1.36, 0.3, 0.4)),
                              ('board_brenner', (-2.36, 1.62, 0.15, 0.2)), ('board_owen', (-3.3, 1.42, 0.3, 0.4)),
                              ('board_phone', (-2.98, 2.0, 0.15, 0.2)), ('board_invite', (-2.5, 2.02, 0.16, 0.2))):
        if tag not in hide:
            S.mat(tag, (220, 220, 220), tex=tx.board_pins(tag.split('_')[1]), texmode=1, spec=0.2)
            S.wbox((x, y, BZ + 0.006), (w / 2, h / 2, 0.003), tag)
    # Case 5: Walt Brenner's name on the back of the Case 1 index card, the tab book photo and Sal's card beside Danny
    # (board_walt); the red string between the three seeds, the envelope and the name (board_string); and, once
    # Danny's case is packed in its box, the bare middle of the board (board_empty)
    if 'board_walt' not in hide:
        S.mat('board_walt', (220, 220, 220), tex=tx.board_pins('walt'), texmode=1, spec=0.2)
        S.wbox((-2.82, 1.62, BZ + 0.007), (0.1, 0.13, 0.003), 'board_walt')
    if 'board_string' not in hide:
        S.mat('red_string', (200, 20, 20), spec=0.3)
        pts = [(-2.34, 1.42), (-2.36, 1.71), (-2.5, 2.1), (-2.62, 1.48), (-2.82, 1.74)]
        for (a, b) in zip(pts, pts[1:]):
            S.cyl((a[0], a[1], BZ + 0.012), (b[0], b[1], BZ + 0.012), 0.004, 'red_string')
    if 'board_empty' not in hide:
        S.mat('board_empty', (214, 216, 208), tex=tx.board_pins('bare'), texmode=1, spec=0.2)
        S.wbox((-2.675, 1.66, BZ + 0.011), (0.425, 0.5, 0.003), 'board_empty')

    # ---------------------------------------------------------------- desks: pairs pushed together face to face
    # Each desk has its chair on the open side (s = +1: towards the camera, s = -1: towards the back wall) and its
    # monitor near the shared edge, screen towards the chair. The two monitors of a pair sit apart in x.
    def chair(cx, cz, s, yaw=0.0):
        """Office chair at (cx, cz) for a desk on the -s side; its back is on the far side from the desk."""
        f = Frame((cx, 0, cz), Ry(yaw))
        S.box(f, (0, 0.46, 0), (0.25, 0.04, 0.25), 0.03, 'chair')
        S.box(f, (0, 0.78, s * 0.23), (0.24, 0.27, 0.03), 0.04, 'chair')
        S.cyl((cx, 0.08, cz), (cx, 0.42, cz), 0.03, 'chair')
        S.box(f, (0, 0.06, 0), (0.28, 0.02, 0.03), 0.0, 'chair')
        S.box(f, (0, 0.06, 0), (0.03, 0.02, 0.28), 0.0, 'chair')

    GLOW = []                                         # (x, z, s): screens, for their glow lights

    def monitor(mx, mz, s, scr, kb=True):
        GLOW.append((mx, mz, s))
        S.wboxr(mx - 0.32, 0.92, mz - 0.02, mx + 0.32, 1.3, mz + 0.02, 'plastic_dk')
        if s > 0:
            S.wboxr(mx - 0.3, 0.94, mz + 0.02, mx + 0.3, 1.28, mz + 0.03, scr)
        else:
            S.wboxr(mx - 0.3, 0.94, mz - 0.03, mx + 0.3, 1.28, mz - 0.02, scr)
        S.cyl((mx, 0.78, mz), (mx, 0.95, mz), 0.025, 'plastic_dk')
        S.wboxr(mx - 0.12, 0.78, mz - 0.08, mx + 0.12, 0.79, mz + 0.08, 'plastic_dk')
        if kb:
            k0, k1 = sorted((mz + s * 0.28, mz + s * 0.43))
            S.wboxr(mx - 0.25, 0.78, k0, mx + 0.25, 0.8, k1, 'plastic_dk')

    def desk(x0, z0, s, scr, w=1.6, d=0.8, mx_off=0.0, seat=True):
        """A desk whose seat side is +z (s = 1) or -z (s = -1); returns the chair's floor point."""
        rng = random.Random(f'{x0:.2f},{z0:.2f}')         # its own clutter, the same whichever props are hidden
        z1 = z0 + d
        zb, zf = (z0, z1) if s > 0 else (z1, z0)               # back (shared) edge, seat edge
        S.wboxr(x0, 0.74, z0, x0 + w, 0.78, z1, 'desk')
        S.wboxr(x0 + 0.04, 0.05, z0 + 0.05, x0 + 0.5, 0.74, z1 - 0.05, 'desk_metal')        # drawer pedestal
        for y in (0.2, 0.45, 0.66):
            a, b = sorted((zf - s * 0.05, zf - s * 0.03))
            S.wboxr(x0 + 0.2, y, a, x0 + 0.34, y + 0.025, b, 'brass')
        S.wboxr(x0 + w - 0.06, 0.0, z0 + 0.05, x0 + w - 0.03, 0.74, z1 - 0.05, 'desk_metal')
        a, b = sorted((zb + s * 0.02, zb + s * 0.05))
        S.wboxr(x0 + 0.5, 0.32, a, x0 + w - 0.06, 0.74, b, 'desk_metal')                    # modesty panel
        mx = x0 + w * 0.5 + mx_off
        monitor(mx, zb + s * 0.2, s, scr)
        for k in range(rng.randint(1, 3)):
            # papers on the side away from the monitor and keyboard
            px = x0 + (rng.uniform(0.06, mx - x0 - 0.6) if mx_off > 0 else rng.uniform(mx - x0 + 0.3, w - 0.36))
            a, b = sorted((zf - s * 0.05, zf - s * 0.4))
            S.wboxr(px, 0.78, a, px + 0.3, 0.78 + 0.02 * (k + 1), b, rng.choice(['paper', 'folder', 'folder_r']))
        cz = zf + s * 0.38
        if seat:
            chair(mx + rng.uniform(-0.08, 0.08), cz, s, yaw=rng.uniform(-12, 12))
        return mx, cz

    def pair(x0, z0, near, far, w=1.6, d=0.8):
        """Two desks pushed together: the far one's seat faces the back wall, the near one's the camera."""
        desk(x0, z0, -1, far, w, d, mx_off=0.3)
        return desk(x0, z0 + d, 1, near, w, d, mx_off=-0.3)

    BACK_Z = -3.25                                    # back clusters: desks from z -3.25 to -1.65
    pair(-0.9, BACK_Z, 'screen0', 'screen3')          # back middle, in front of the radiator
    pair(1.8, BACK_Z, 'screen1', 'screen4')           # back right
    FRONT_Z = 0.75                                    # front clusters: far desk from z 0.75, near desk from 1.55
    if 'fr_desks' not in hide:
        with S.tag('fr_desks'):
            desk(2.2, FRONT_Z, -1, 'screen3', mx_off=0.3)
            desk(2.2, FRONT_Z + 0.8, 1, 'screen4', mx_off=-0.3, seat=False)
    FR_CHAIR = (2.2 + 0.5 + 0.05, FRONT_Z + 1.6 + 0.4)
    chair(FR_CHAIR[0], FR_CHAIR[1], 1, yaw=-8)    # not part of the walk-behind cut: the player only passes in front

    # ---------------------------------------------------------------- the detective's desk (front left) and the one facing it
    hx0, hz0, HW, HD = -3.95, FRONT_Z + 0.8, 2.4, 0.95       # his desk; his chair is on the camera side
    if 'ray_desks' not in hide:
        with S.tag('partner_desk'):
            desk(hx0, FRONT_Z, -1, 'screen3', w=HW, mx_off=0.65)
        with S.tag('desk'):
            S.wboxr(hx0, 0.74, hz0, hx0 + HW, 0.79, hz0 + HD, 'desk')
            S.wboxr(hx0 + 0.04, 0.03, hz0 + 0.05, hx0 + 0.55, 0.74, hz0 + HD - 0.05, 'desk')     # drawer pedestal
            S.wboxr(hx0 + HW - 0.1, 0.0, hz0 + 0.05, hx0 + HW - 0.04, 0.74, hz0 + HD - 0.05, 'desk')
            S.wboxr(hx0 + 0.6, 0.35, hz0 + 0.03, hx0 + HW - 0.1, 0.74, hz0 + 0.07, 'desk')     # modesty panel
            for y in (0.15, 0.4, 0.62):
                S.wboxr(hx0 + 0.2, y, hz0 + HD - 0.02, hx0 + 0.4, y + 0.03, hz0 + HD + 0.01, 'brass')
            S.wboxr(hx0 + 1.7, 0.79, hz0 + 0.45, hx0 + 2.25, 0.86, hz0 + 0.8, 'folder')          # file stack
            S.wboxr(hx0 + 1.72, 0.86, hz0 + 0.47, hx0 + 2.23, 0.9, hz0 + 0.78, 'folder_r')
        with S.tag('lamp'):
            lx, lz = hx0 + 0.35, hz0 + 0.35
            S.cyl((lx, 0.79, lz), (lx, 0.82, lz), 0.12, 'brass')
            S.cyl((lx, 0.82, lz), (lx, 1.12, lz), 0.015, 'brass')
            S.ell(WORLD, (lx + 0.05, 1.16, lz + 0.05), (0.2, 0.07, 0.1), 'lamp_shade', rot=Ry(-30))
            S.ell(WORLD, (lx + 0.05, 1.11, lz + 0.05), (0.12, 0.02, 0.05), 'bulb', rot=Ry(-30))
        with S.tag('typewriter'):
            mx, mz = hx0 + 1.15, hz0 + 0.25
            S.wbox((mx, 1.1, mz), (0.3, 0.2, 0.02), 'plastic_dk', rot=Ry(-8))
            S.wbox((mx + 0.003, 1.1, mz + 0.022), (0.28, 0.18, 0.005), 'screen2', rot=Ry(-8))
            S.cyl((mx, 0.79, mz), (mx, 0.92, mz), 0.025, 'plastic_dk')
            S.wbox((mx - 0.02, 0.8, mz + 0.42), (0.24, 0.01, 0.08), 'plastic_dk', rot=Ry(-5))
        with S.tag('phone_list'):
            S.mat('phone_list', (236, 236, 228), tex=tx.sign_board('HOLLYWOOD STN  x2186', (30, 30, 40), (236, 236, 228), 256, 64,
                  size=18), texmode=1, spec=0.6, shin=60)
            # on top of the file stack, white on the red folder, where it can be seen from across the room
            S.wbox((hx0 + 1.97, 0.902, hz0 + 0.625), (0.13, 0.002, 0.09), 'phone_list', rot=Ry(-6))
        with S.tag('phone'):
            px, pz = hx0 + 2.08, hz0 + 0.24
            S.wbox((px, 0.82, pz), (0.12, 0.03, 0.1), 'plastic_dk', rot=Ry(-10))
            S.ell(WORLD, (px, 0.87, pz - 0.02), (0.11, 0.025, 0.03), 'plastic_dk')
    if 'mug' not in hide:
        with S.tag('mug'):
            mx2, mz2 = hx0 + 1.55, hz0 + 0.72
            S.cyl((mx2, 0.79, mz2), (mx2, 0.9, mz2), 0.045, 'mug')
            S.cyl((mx2, 0.84, mz2), (mx2, 0.86, mz2), 0.047, 'mug_band')
            S.cyl((mx2, 0.893, mz2), (mx2, 0.9, mz2), 0.038, 'coffee')
            S.cone((mx2 + 0.045, 0.875, mz2), (mx2 + 0.07, 0.84, mz2), 0.012, 0.012, 'mug')
    RAY_CHAIR = (hx0 + 1.1, hz0 + HD + 0.4)
    chair(RAY_CHAIR[0], RAY_CHAIR[1], 1, yaw=14)              # his chair, rolled back a little from the desk
    BASKET = (hx0 + HW + 0.3, hz0 + 0.6)
    with S.tag('wastebasket'):
        bx, bz = BASKET
        S.tcyl(Frame((bx, 0.19, bz)), (0, 0, 0), (0.17, 0.17), (0.14, 0.14), 0.19, 'basket')
        S.tcyl(Frame((bx, 0.24, bz)), (0, 0, 0), (0.155, 0.155), (0.13, 0.13), 0.19, 'basket', op=1)
        S.ell(WORLD, (bx, 0.3, bz), (0.09, 0.07, 0.08), 'paper', k=0.03)
        S.ell(WORLD, (bx + 0.05, 0.33, bz - 0.05), (0.06, 0.05, 0.06), 'paper', k=0.03)

    # ---------------------------------------------------------------- left wall: door, coat rack
    with S.tag('door'):
        dx0, dx1 = -5.1, -3.9
        S.wboxr(dx0, 0, Z0 - 0.4, dx1, 2.2, Z0 + 0.02, 'wall', op=1)
        S.wboxr(dx0 - 0.08, 0, Z0, dx1 + 0.08, 2.28, Z0 + 0.06, 'trim')
        S.wboxr(dx0 + 0.04, 0, Z0 - 0.2, dx1 - 0.04, 2.16, Z0 - 0.12, 'door')
        S.wboxr(dx0 + 0.2, 1.25, Z0 - 0.12, dx1 - 0.2, 1.95, Z0 - 0.1, 'glass_door')
        S.sph((dx1 - 0.15, 1.0, Z0 - 0.08), 0.04, 'brass')
    S.wboxr(-4.75, 2.38, Z0, -4.25, 2.56, Z0 + 0.06, 'exit')
    with S.tag('coat_rack'):
        rx, rz = -5.6, Z0 + 0.6
        S.cyl((rx, 0, rz), (rx, 1.8, rz), 0.025, 'trim')
        for a in range(3):
            ang = a * 2.1
            S.cyl((rx, 0.02, rz), (rx + 0.28 * math.cos(ang), 0.0, rz + 0.28 * math.sin(ang)), 0.02, 'trim')
            S.cyl((rx, 1.72, rz), (rx + 0.16 * math.cos(ang), 1.82, rz + 0.16 * math.sin(ang)), 0.012, 'trim')
        S.ell(WORLD, (rx + 0.06, 1.35, rz + 0.05), (0.2, 0.38, 0.14), 'coatfab', k=0.05)
        S.ell(WORLD, (rx + 0.06, 1.65, rz + 0.05), (0.18, 0.1, 0.16), 'coatfab', k=0.05)

    # ---------------------------------------------------------------- right wall: filing cabinets, coffee, cooler
    with S.tag('cabinet'):
        for k, z in enumerate((-2.2, -1.45)):
            S.wboxr(X1 - 0.68, 0, z, X1 - 0.02, 1.38, z + 0.7, 'cabinet', rnd=0.01)
            for j in range(4):
                y = 0.08 + j * 0.33
                S.wboxr(X1 - 0.7, y, z + 0.05, X1 - 0.67, y + 0.29, z + 0.65, 'cabinet')
                S.wboxr(X1 - 0.72, y + 0.18, z + 0.28, X1 - 0.69, y + 0.21, z + 0.42, 'brass')
                S.wboxr(X1 - 0.705, y + 0.08, z + 0.27, X1 - 0.695, y + 0.15, z + 0.43, 'label')
        S.wboxr(X1 - 0.6, 1.38, -2.1, X1 - 0.1, 1.62, -1.6, 'folder')
    with S.tag('coffee_machine'):
        S.wboxr(3.9, 0, Z0, 5.1, 0.9, Z0 + 0.6, 'desk')
        S.wboxr(4.3, 0.9, Z0 + 0.08, 4.75, 1.4, Z0 + 0.5, 'plastic_dk', rnd=0.02)
        S.wboxr(4.35, 1.2, Z0 + 0.5, 4.7, 1.3, Z0 + 0.52, 'bulb')
        S.cyl((4.0, 0.9, Z0 + 0.3), (4.0, 1.12, Z0 + 0.3), 0.07, 'black')
        S.cyl((4.95, 0.9, Z0 + 0.3), (4.95, 1.0, Z0 + 0.3), 0.045, 'mug')
    S.cyl((X1 - 0.35, 0, 3.0), (X1 - 0.35, 1.0, 3.0), 0.16, 'plastic_lt')
    S.cyl((X1 - 0.35, 1.0, 3.0), (X1 - 0.35, 1.45, 3.0), 0.14, 'cooler_blue')
    S.cyl((X1 - 0.4, 0, 4.6), (X1 - 0.4, 0.35, 4.6), 0.2, 'pot')
    S.ell(WORLD, (X1 - 0.4, 0.75, 4.6), (0.35, 0.45, 0.35), 'plant', k=0.1)

    # ---------------------------------------------------------------- ceiling fixtures (hanging)
    for i, (x, z, on) in enumerate([(-3.0, -3.0, False), (1.5, -3.0, True), (-3.0, 0.5, False), (1.5, 0.5, False),
                                    ]):
        S.wboxr(x - 0.7, WH - 0.08, z - 0.3, x + 0.7, WH, z + 0.3, 'fixture')
        S.wboxr(x - 0.65, WH - 0.1, z - 0.26, x + 0.65, WH - 0.08, z + 0.26, 'fluor_on' if on else 'fluor_off')

    # ---------------------------------------------------------------- lights
    S.light((hx0 + 0.42, 1.08, hz0 + 0.42), (255, 196, 120), power=7, range=7, soft=10, vol=0.6,
            spot=((0.1, -1, 0.1), 50, 80))
    S.light((hx0 + 0.42, 1.25, hz0 + 0.42), (255, 190, 120), power=0.9, range=6, shadow=False, vol=0.2)
    S.light((1.5, WH - 0.2, -3.0), (210, 230, 225), power=9, range=9, vol=0.3, spot=((0, -1, 0), 60, 85))
    S.light((-3.0, WH - 0.2, -1.2), (200, 225, 220), power=3, range=9, vol=0.15, soft=8, spot=((0, -1, 0), 60, 88))
    S.light((2.7, 3.0, Z0 - 2.5), (255, 150, 80), power=420, range=18, vol=1.4, volshadow=True, soft=60,
            spot=((-2.2, -3.0, 6.6), 16, 30))            # sodium streetlight through the blinds
    S.light((-0.3, 3.4, Z0 - 2.5), (120, 140, 220), power=110, range=14, vol=0.6, volshadow=True, soft=60,
            spot=((-0.6, -2.4, 4.6), 16, 30))              # cold light through the other window
    S.light((-4.5, 1.6, Z0 + 0.4), (200, 220, 210), power=1.5, range=5, vol=0.3, shadow=False)   # hallway glow
    S.light((-4.5, 2.4, Z0 + 0.3), (60, 255, 120), power=0.5, range=3, shadow=False)
    for (x, z, s) in GLOW + [(hx0 + 1.15, hz0 + 0.25, 1)]:
        S.light((x, 1.1, z + s * 0.3), (110, 150, 220), power=0.6, range=3, shadow=False)
    S.light((4.5, 1.35, Z0 + 0.8), (255, 200, 140), power=0.5, range=2.5, shadow=False)

    cam = Camera((0.4, 3.4, 9.8), (-0.4, 0.85, -2.5), fov=38, W=3840, H=2160)
    env = dict(sky=(30, 34, 46), bounce=(22, 20, 22), fog_col=(18, 18, 24), fog=0.05, fog_h0=0.0, fog_hf=0.05,
               fog_max=60, vol_scale=4, vol_steps=48, reflections=True, grid=0.5, ao_scale=0.8)
    meta = dict(
        room='squad_room',
        # the back clusters are cut out of the walk area (nobody squeezes between them and the wall); the front ones are
        # walk-behind props with rectangular footprints, and the two chairs on the camera side are round obstacles
        walk=[(-5.5, -3.9), (-1.15, -3.9), (-1.15, -0.9), (3.65, -0.9), (3.65, -3.9), (5.0, -3.9), (5.0, 3.4),
              (-4.7, 3.4), (-5.5, 1.6)],
        # the desk footprints have a body's width of margin at the sides, so walking past them doesn't clip into them
        obstacles=[(hx0 - 0.3, FRONT_Z - 0.7, hx0 + HW + 0.3, hz0 + HD + 0.05), RAY_CHAIR + (0.3,), BASKET + (0.3,),
                   (1.9, FRONT_Z - 0.7, 4.1, FRONT_Z + 1.65), FR_CHAIR + (0.3,)],
        walk_zmin=-3.9, walk_zmax=3.4, scale_x=-2.0,
        spawns={'start': (-1.1, 2.95), 'street': (-4.5, -3.7)},
        hotspots={
            'desk': ('desk', (-2.1, 2.95), 'up'),
            'door': ('door', (-4.5, -3.75), 'up'),
            'coat_rack': ('coat rack', (-5.1, -3.3), 'left'),
            'case_board': ('murder board', None, 'up'),
            'lamp': ('desk lamp', (-3.6, 3.0), 'up'),
            'typewriter': ('computer', (-2.3, 2.95), 'up'),
            'phone': ('desk phone', (-1.8, 2.95), 'up'),
            'phone_list': ('phone list', (-2.0, 2.95), 'up'),
            'mug': ('coffee mug', (-2.25, 2.95), 'up'),
            'clock': ('clock', None, 'up'),
            'window': ('window', None, 'up'),
            'radiator': ('radiator', None, 'up'),
            'wastebasket': ('wastebasket', (-0.85, 2.6), 'left'),
            'cabinet': ('filing cabinet', (4.6, -1.0), 'right'),
            'coffee_machine': ('coffee machine', (4.45, -3.55), 'up'),
        },
        hotspot_order=['window', 'radiator', 'clock', 'case_board', 'desk', 'door', 'coat_rack', 'typewriter', 'lamp',
                       'phone', 'phone_list', 'mug', 'wastebasket', 'cabinet', 'coffee_machine'],
        overlays=['board_empty', 'mug', 'board_envelope', 'board_kenji', 'board_receipt', 'board_gus', 'board_brenner',
                  'board_owen', 'board_phone', 'board_invite', 'board_walt', 'board_string'],
        # walk-behind props: tag -> (x, z) floor point; the player is drawn behind while further away than it
        occluders={'ray_desks': (hx0 + 1.2, hz0 + HD), 'fr_desks': (3.0, FRONT_Z + 1.6)},
        # the mug stands on his desk, which is a walk-behind prop: sort it just in front so the desk doesn't cover it
        overlay_bases={'mug': (hx0 + 1.55, hz0 + HD + 0.02)},
        char_fill=((236, 222, 200), 0.3),
        tint=(0.78, 0.74, 0.7),
        exposure=1.5,
    )
    return S, cam, env, meta
