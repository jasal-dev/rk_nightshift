"""Street outside the precinct: rain, sodium light, neon, the Blue Note, an alley that goes on too long."""
import math, random
import numpy as np
from scene3d import *
import textures as tx

def build(hide=()):
    S = Scene()
    rng = random.Random(4)
    # ---------------------------------------------------------------- materials
    S.mat('asphalt', (255, 255, 255), tex=tx.hires(tx.asphalt(), 2), texmode=4, texmap=1, texscale=3.0, refl=0.55, ripple=0.14,
          spec=0.5, shin=60)
    S.mat('puddle', (30, 30, 34), refl=0.95, ripple=0.06, spec=0.9, shin=120)
    S.mat('sidewalk', (255, 255, 255), tex=tx.hires(tx.sidewalk(), 2), texmode=4, texmap=1, texscale=2.4, refl=0.28, ripple=0.4,
          spec=0.3, shin=40)
    S.mat('curb', (150, 148, 144), namp=0.2, nscale=6, refl=0.15)
    S.mat('brick', (255, 255, 255), tex=tx.hires(tx.brick(1), 2), texmode=4, texmap=1, texscale=2.2, bump=0.15, bscale=8)
    S.mat('brick_dk', (170, 170, 170), tex=tx.brick(2, base=(80, 46, 40)), texmode=4, texmap=1, texscale=2.2)
    S.mat('concrete', (190, 190, 196), tex=tx.hires(tx.concrete(), 2), texmode=4, texmap=1, texscale=4.0)
    S.mat('trim', (70, 70, 74), spec=0.2, shin=20)
    S.mat('metal_dk', (40, 42, 46), spec=0.6, shin=40)
    S.mat('glass_dk', (12, 14, 20), spec=1.2, shin=90, refl=0.35)
    S.mat('wood_dk', (52, 30, 22), namp=0.2, nscale=8)
    S.mat('backing', (16, 14, 20), spec=0.2)
    S.mat('bar_window', (40, 24, 18), tex=tx.hires(tx.bar_interior(), 3), texmode=3, texemis=1.6, refl=0.15)
    S.mat('door_glow', (120, 70, 40), tex=tx.bar_door_glass(), texmode=3, texemis=1.1)
    S.mat('neon_blue', (20, 20, 30), tex=tx.neon_text('BLUE NOTE', (80, 150, 255), size=72,
          fnt='DejaVuSerif-BoldItalic.ttf'), texmode=2, texemis=5.0)
    S.mat('neon_open', (20, 20, 30), tex=tx.neon_text('OPEN', (255, 60, 150), size=48), texmode=2, texemis=4.0)
    S.mat('neon_bar', (20, 20, 30), tex=tx.neon_text('COCKTAILS', (255, 90, 170), size=40, vertical=True), texmode=2,
          texemis=4.0)
    S.mat('phone_sign', (30, 30, 40), tex=tx.sign_board('PHONE', (220, 235, 255), (30, 70, 160), 256, 64), texmode=3,
          texemis=2.0)
    S.mat('police_letters', (60, 62, 66), tex=tx.sign_board('POLICE', (220, 222, 226), (60, 62, 66), 512, 96,
          fnt='DejaVuSans-Bold.ttf'), texmode=1, spec=0.6, shin=30)
    S.mat('entrance_glass', (20, 26, 34), tex=tx.hires(tx.lobby(), 2), texmode=3, texemis=1.15, refl=0.25)
    S.mat('blue_lamp', (60, 110, 255), emis=(70, 120, 255), emis_mult=4)
    S.mat('win_upper', (14, 16, 24), tex=tx.windows_grid(7, 8, 3, lit=0.3, warm=False), texmode=3, texemis=0.8,
          refl=0.25)
    S.mat('win_bar_up', (14, 16, 24), tex=tx.windows_grid(8, 3, 1, lit=0.34), texmode=3, texemis=1.8, refl=0.2)
    S.mat('win_ground', (14, 16, 24), tex=tx.windows_grid(9, 3, 1, lit=0.67, warm=False), texmode=3, texemis=0.65,
          refl=0.25)
    S.mat('sky', (16, 12, 24), tex=tx.skyline(9, 1024, 256, k=3), texmode=3, texemis=1.1)
    S.mat('billboard', (120, 120, 120), tex=tx.hires(tx.billboard(), 3), texmode=1, namp=0.1, nscale=4)
    S.mat('palm', (8, 8, 12))
    S.mat('car_paint', (34, 38, 44), spec=1.4, shin=90, refl=0.45)
    S.mat('car_glass', (8, 10, 14), spec=1.5, shin=120, refl=0.6)
    S.mat('chrome', (150, 150, 156), spec=1.6, shin=80, refl=0.5)
    S.mat('tire', (16, 16, 18))
    S.mat('taillight', (120, 10, 10), emis=(220, 30, 30), emis_mult=1.2)
    S.mat('plate', (200, 200, 200), tex=tx.hires(tx.car_plate(), 4), texmode=1)
    S.mat('dumpster', (34, 70, 52), namp=0.25, nscale=4, spec=0.3)
    S.mat('trashbag', (18, 18, 20), spec=0.35, shin=18, namp=0.3, nscale=6, bump=0.4, bscale=9)
    S.mat('hydrant', (150, 120, 40), namp=0.2, nscale=8, spec=0.4)
    S.mat('cable', (10, 10, 12))
    S.mat('lamp_head', (50, 50, 54), spec=0.3)
    S.mat('lamp_glass', (255, 190, 120), emis=(255, 170, 90), emis_mult=6)
    S.mat('poster1', (200, 200, 200), tex=tx.hires(tx.poster(1), 3), texmode=1)
    S.mat('poster2', (200, 200, 200), tex=tx.hires(tx.poster(2), 3), texmode=1)
    S.mat('poster3', (200, 200, 200), tex=tx.hires(tx.poster(5), 3), texmode=1)
    S.mat('alley_door', (200, 220, 200), emis=(180, 220, 190), emis_mult=1.2)
    S.mat('ac_unit', (110, 112, 108), namp=0.2, nscale=6)
    S.mat('newsbox', (120, 30, 30), spec=0.5)
    S.mat('notice', (220, 220, 210), tex=tx.hires(tx.rezoning_notice(), 3), texmode=1)

    # ---------------------------------------------------------------- ground
    S.wboxr(-40, -1, -60, 40, 0, 30, 'asphalt')
    S.tag('ground')
    S.wboxr(-40, 0, 0, 40, 0.15, 3.2, 'sidewalk')
    S.wboxr(-40, 0, 3.05, 40, 0.15, 3.32, 'curb')
    S.tag(None)
    for (x, z, rx, rz) in [(-5.2, 4.6, 1.6, 0.5), (0.8, 5.4, 1.1, 0.35), (-1.8, 1.9, 0.7, 0.3), (4.2, 4.2, 0.9, 0.3)]:
        S.ell(WORLD, (x, 0.005 if z > 3.2 else 0.155, z), (rx, 0.012, rz), 'puddle')
    # alley floor
    S.wboxr(-2.0, 0, -18, 1.0, 0.04, 0, 'asphalt')

    # ---------------------------------------------------------------- bar building (left)
    S.wboxr(-14, 0, -18, -2.0, 4.9, 0, 'brick')
    S.wboxr(-14, 4.9, -0.4, -2.0, 5.15, 0.15, 'trim')            # parapet cap
    S.wboxr(-14, 2.85, 0, -2.0, 3.0, 0.12, 'trim')              # storefront cornice
    # front window
    S.wboxr(-7.8, 0.75, -0.2, -4.9, 2.7, 0.06, 'wood_dk')
    S.wboxr(-7.65, 0.9, -0.25, -5.05, 2.55, 0.07, 'bar_window')
    S.tag('bar_window')
    S.wboxr(-7.75, 0.7, 0.0, -4.95, 0.78, 0.18, 'wood_dk')
    S.tag(None)
    # door
    with S.tag('bar_door'):
        S.wboxr(-4.5, 0.15, -0.2, -3.3, 2.45, 0.05, 'wood_dk')
        S.wboxr(-4.38, 0.15, -0.25, -3.42, 2.35, 0.06, 'backing')
        S.wboxr(-4.2, 1.5, -0.26, -3.6, 2.0, 0.08, 'door_glow')
        S.sph((-3.55, 1.15, 0.1), 0.04, 'chrome')
    S.wboxr(-3.2, 1.6, 0.0, -2.95, 2.5, 0.06, 'backing')
    S.wboxr(-3.18, 1.62, 0.04, -2.97, 2.48, 0.07, 'neon_bar')
    # city notice of a public hearing, taped up between the window and the door
    with S.tag('rezoning'):
        S.wboxr(-4.86, 1.12, 0.0, -4.54, 1.56, 0.015, 'notice')
    # BLUE NOTE neon sign on a backing board
    with S.tag('neon'):
        S.wboxr(-7.6, 3.15, 0.05, -3.4, 4.25, 0.18, 'backing')
        S.wboxr(-7.55, 3.2, 0.18, -3.45, 4.2, 0.2, 'neon_blue')
        for x in (-7.2, -3.8):
            S.cyl((x, 4.25, 0.1), (x, 5.0, 0.0), 0.02, 'metal_dk')
    S.wboxr(-6.9, 1.7, 0.07, -5.8, 2.3, 0.08, 'neon_open')
    # rooftop billboard
    with S.tag('billboard'):
        S.wboxr(-10.0, 5.6, -4.05, -5.4, 7.9, -3.95, 'billboard')
        for x in (-9.4, -7.7, -6.0):
            S.cyl((x, 4.9, -4.1), (x, 5.6, -4.1), 0.06, 'metal_dk')
        S.wboxr(-10.1, 5.5, -4.2, -5.3, 5.6, -3.6, 'metal_dk')
    for x in (-9.0, -6.4):
        S.cyl((x, 5.55, -3.6), (x, 5.55, -3.0), 0.03, 'metal_dk')
        S.ell(WORLD, (x, 5.55, -2.95), (0.1, 0.06, 0.06), 'lamp_glass')
    # posters, AC unit, newspaper box
    S.wboxr(-8.7, 1.0, 0.0, -8.0, 1.9, 0.02, 'poster1')
    S.wboxr(-2.75, 0.9, 0.0, -2.15, 1.7, 0.02, 'poster2')
    S.wboxr(-2.7, 0.2, 0.0, -2.2, 0.85, 0.02, 'poster3')
    S.wboxr(-9.9, 3.6, 0.0, -9.1, 4.05, 0.45, 'ac_unit')
    S.wboxr(-8.9, 0.15, 0.6, -8.4, 1.1, 1.05, 'newsbox')
    # fire hydrant
    if 'hydrant' not in hide:
        with S.tag('hydrant'):
            S.cyl((-5.6, 0.15, 2.75), (-5.6, 0.75, 2.75), 0.11, 'hydrant')
            S.sph((-5.6, 0.78, 2.75), 0.12, 'hydrant')
            S.cyl((-5.77, 0.5, 2.75), (-5.43, 0.5, 2.75), 0.06, 'hydrant')

    # ---------------------------------------------------------------- alley
    S.wboxr(-2.0, 0, -18, -1.9, 4.9, 0, 'brick')                       # bar side wall (inner face)
    S.wboxr(1.0, 0, -30, 14, 16, 0, 'concrete')                        # precinct block incl. alley side
    S.wboxr(-3, 0, -18.5, 2, 8, -17.5, 'brick_dk')                     # alley back wall
    with S.tag('alley'):
        S.wboxr(-0.9, 0.04, -17.55, 0.1, 2.3, -17.4, 'alley_door')
    S.wboxr(-1.1, 2.4, -17.6, 0.3, 2.55, -16.9, 'trim')
    # fire escape on bar side wall (inside alley)
    for k, y in enumerate((2.6, 4.6)):
        z0, z1 = -3.0 - k * 0.8, -9.0 - k * 0.8
        S.wboxr(-1.9, y, z1, -1.1, y + 0.05, z0, 'metal_dk')
        for z in np.linspace(z1, z0, 9):
            S.cyl((-1.1, y, z), (-1.1, y + 0.9, z), 0.015, 'metal_dk')
        S.cyl((-1.1, y + 0.9, z1), (-1.1, y + 0.9, z0), 0.02, 'metal_dk')
        # stairs
        S.cyl((-1.3, y, z0 - 0.3), (-1.3, y + 2.0, z0 - 2.8), 0.03, 'metal_dk')
    # dumpster + bags
    with S.tag('trash_can'):
        S.wboxr(-0.2, 0.1, -3.4, 0.95, 1.25, -1.6, 'dumpster', rnd=0.03)
        S.wboxr(-0.25, 1.22, -3.45, 1.0, 1.3, -1.55, 'dumpster', rnd=0.02)
        for (x, z, r) in [(-0.6, -1.1, 0.32), (-0.2, -0.7, 0.28), (-1.2, -1.8, 0.3)]:
            S.ell(WORLD, (x, r * 0.6, z), (r, r * 0.65, r * 0.9), 'trashbag', k=0.12)
            S.ell(WORLD, (x + r * 0.35, r * 0.75, z - r * 0.2), (r * 0.6, r * 0.55, r * 0.6), 'trashbag', k=0.15)
            S.ell(WORLD, (x - r * 0.3, r * 0.45, z + r * 0.3), (r * 0.55, r * 0.45, r * 0.5), 'trashbag', k=0.15)
    # steam / pipes
    S.cyl((0.9, 0, -6.0), (0.9, 7.0, -6.0), 0.08, 'metal_dk')
    S.wboxr(0.55, 3.1, -8.2, 1.0, 3.6, -7.2, 'ac_unit')

    # ---------------------------------------------------------------- precinct (right)
    S.wboxr(1.0, 0.0, 0.0, 14, 0.6, 0.12, 'trim')                       # plinth
    # entrance recess with glass doors
    with S.tag('precinct_door'):
        S.wboxr(4.5, 0.15, -1.2, 6.9, 3.0, 0.2, 'concrete', op=1)
        S.wboxr(4.6, 0.15, -1.2, 6.8, 2.9, -1.0, 'entrance_glass')
        S.wboxr(5.68, 0.15, -1.0, 5.72, 2.9, -0.95, 'metal_dk')
    S.wboxr(4.3, 3.0, -0.1, 7.1, 3.18, 1.4, 'trim')                     # canopy
    S.wboxr(4.6, 2.95, 0.4, 6.8, 3.0, 1.2, 'lamp_glass')                 # canopy light panel
    S.wboxr(4.3, 0.15, 0.0, 7.1, 0.3, 0.8, 'curb')                       # step
    with S.tag('precinct_sign'):
        S.wboxr(4.0, 3.45, 0.0, 7.4, 4.05, 0.06, 'police_letters')
    for x in (4.0, 7.4):
        S.cyl((x, 0.3, 0.9), (x, 2.2, 0.9), 0.04, 'metal_dk')
        S.sph((x, 2.35, 0.9), 0.16, 'blue_lamp')
    # ground floor windows (blinds) and upper storeys
    for x0, x1 in ((1.6, 3.9), (7.6, 9.9)):
        S.wboxr(x0 - 0.1, 0.9, -0.15, x1 + 0.1, 2.7, 0.03, 'trim')
        S.wboxr(x0, 1.0, -0.2, x1, 2.6, 0.04, 'win_ground')
    S.wboxr(1.4, 4.6, -0.2, 13.5, 11.0, 0.03, 'win_upper')
    for x in np.arange(1.4, 13.6, 1.5):
        S.wboxr(x - 0.06, 4.5, 0.0, x + 0.06, 11.0, 0.18, 'concrete')
    for y in (4.5, 6.6, 8.8):
        S.wboxr(1.3, y - 0.08, 0.0, 13.6, y + 0.08, 0.2, 'concrete')

    # ---------------------------------------------------------------- street furniture
    with S.tag('payphone'):
        S.cyl((-1.25, 0.15, 0.9), (-1.25, 2.1, 0.9), 0.05, 'metal_dk')
        S.wboxr(-1.6, 1.0, 0.75, -0.9, 1.9, 1.05, 'metal_dk', rnd=0.02)
        S.wboxr(-1.5, 1.1, 1.05, -1.0, 1.8, 1.07, 'trim')
        S.wboxr(-1.55, 2.05, 0.82, -0.95, 2.35, 0.98, 'phone_sign')
        S.ell(WORLD, (-1.12, 1.45, 1.1), (0.04, 0.12, 0.04), 'tire')
    if 'streetlamp' not in hide:
        with S.tag('streetlamp'):
            S.cone((3.3, 0.15, 2.9), (3.3, 7.4, 2.9), 0.08, 0.05, 'metal_dk')
            S.cone((3.3, 7.3, 2.9), (2.9, 7.6, 4.6), 0.05, 0.04, 'metal_dk')
            S.ell(WORLD, (2.85, 7.55, 4.9), (0.25, 0.1, 0.45), 'lamp_head')
            S.ell(WORLD, (2.85, 7.47, 4.9), (0.18, 0.04, 0.32), 'lamp_glass')

    # parked car (unmarked sedan) at the kerb, its back end just in frame at the bottom right
    if 'car' not in hide:
        with S.tag('car'):
            cx0, cx1, cz0, cz1 = 4.7, 9.25, 3.75, 5.55
            S.wboxr(cx0, 0.32, cz0, cx1, 0.92, cz1, 'car_paint', rnd=0.12)
            S.wboxr(cx0 + 1.1, 0.85, cz0 + 0.08, cx1 - 1.3, 1.42, cz1 - 0.08, 'car_paint', rnd=0.14)
            S.wboxr(cx0 + 1.2, 0.95, cz0 + 0.04, cx1 - 1.4, 1.36, cz1 - 0.04, 'car_glass', rnd=0.08)
            S.fcyl((cx0 + 0.85, 0.34, cz1 - 0.08), 0.34, 0.12, 'tire', axis='z')
            S.fcyl((cx0 + 0.85, 0.34, cz1 + 0.04), 0.18, 0.02, 'chrome', axis='z')
            S.wboxr(cx0 - 0.03, 0.62, cz0 + 0.2, cx0 + 0.02, 0.74, cz0 + 0.5, 'taillight')
            S.wboxr(cx0 - 0.03, 0.62, cz1 - 0.5, cx0 + 0.02, 0.74, cz1 - 0.2, 'taillight')
            S.wboxr(cx0 - 0.04, 0.4, cz0 + 0.65, cx0 + 0.01, 0.56, cz1 - 0.65, 'plate')
    # ---------------------------------------------------------------- distance: palms, wires, skyline
    for (x, z, h, lean) in [(-3.2, -22, 13, 1.5), (-1.0, -30, 16, -1.5), (-12, -30, 15, 2), (-7.5, -40, 18, 1)]:
        top = (x + lean, h, z)
        S.cone((x, 0, z), top, 0.32, 0.18, 'palm')
        for k in range(11):
            a = k / 11 * 2 * math.pi + rng.uniform(-0.2, 0.2)
            droop = rng.uniform(0.6, 1.4)
            dx, dz = math.cos(a), math.sin(a)
            p1 = (top[0] + dx * 1.6, h + 0.6, z + dz * 1.6)
            p2 = (top[0] + dx * 3.4, h - droop, z + dz * 3.4)
            S.cone(top, p1, 0.08, 0.22, 'palm'); S.cone(p1, p2, 0.22, 0.04, 'palm')
    for (y0, y1, zz) in [(5.6, 8.5, -0.5), (5.8, 9.0, -0.9)]:
        pts = [(-12, y0, zz), (-4, y0 - 0.7, zz), (4, (y0 + y1) / 2 - 0.9, zz), (12, y1, zz)]
        for a, b in zip(pts, pts[1:]):
            S.cyl(a, b, 0.015, 'cable')
    S.wboxr(-120, 0, -101, 120, 40, -100, 'sky')

    # ---------------------------------------------------------------- lights
    S.light((2.85, 7.3, 4.9), (255, 160, 80), power=75, range=18, vol=1.0, volshadow=True, soft=16,
            spot=((-0.12, -1, -0.3), 28, 58))
    for x in (-9.2, -5.8):
        S.light((x, 5.5, -2.8), (255, 220, 170), power=1.6, range=5, vol=0.3, shadow=False, spot=((0, 0.6, -1), 35, 70))
    S.light((-6.3, 1.7, -0.9), (255, 140, 70), power=10, range=8, vol=0.25)
    S.light((-5.5, 3.7, 0.9), (90, 150, 255), power=6, range=8, vol=0.7, shadow=False)
    S.light((-3.1, 2.1, 0.5), (255, 70, 160), power=2.5, range=6, vol=0.5, shadow=False)
    S.light((-3.9, 1.8, 0.4), (255, 150, 80), power=2.0, range=5, vol=0.2, shadow=False)
    S.light((5.7, 2.9, 0.8), (205, 222, 255), power=26, range=9, vol=0.9, spot=((0, -1, 0.15), 30, 70))
    for x in (4.0, 7.4):
        S.light((x, 2.35, 1.1), (70, 120, 255), power=2.0, range=5, shadow=False, vol=0.5)
    S.light((-0.4, 3.6, -14.5), (170, 220, 195), power=55, range=24, vol=1.8, volshadow=True, soft=20)
    S.light((-1.25, 2.6, 1.2), (120, 170, 255), power=1.2, range=4, shadow=False, vol=0.3)
    S.sun((0.35, -1, -0.5), (70, 80, 130), power=0.35, shadow=False)

    cam = Camera((0.4, 2.55, 13.6), (0.15, 2.25, 0), fov=38, W=3840, H=2160)
    env = dict(sky=(22, 22, 40), bounce=(14, 12, 18), fog_col=(22, 18, 36), fog=0.05, fog_h0=0.0, fog_hf=0.22,
               fog_max=120, vol_scale=4, vol_steps=40, reflections=True, grid=0.75, ao_scale=1.5)

    meta = dict(
        room='street',
        walk=[(-8.8, 0.6), (9.6, 0.6), (9.6, 1.25), (7.2, 1.25), (7.2, 3.4), (4.4, 3.4), (4.4, 4.8), (-8.8, 4.8)],
        walk_zmin=0.6, walk_zmax=4.8, scale_x=0.0,
        spawns={'squad_room': (5.7, 1.3), 'start': (0, 2.0)},
        hotspots={
            'bar_door': ('Blue Note door', (-3.9, 0.9), 'up'),
            'neon': ('neon sign', None, 'up'),
            'payphone': ('payphone', (-1.25, 1.55), 'up'),
            'trash_can': ('dumpster', (0.2, 0.75), 'up'),
            'alley': ('alley', None, 'up'),
            'streetlamp': ('streetlamp', None, 'up'),
            'billboard': ('billboard', None, 'up'),
            'hydrant': ('fire hydrant', (-5.0, 2.5), 'left'),
            'precinct_door': ('precinct', (5.7, 1.0), 'up'),
            'precinct_sign': ('POLICE sign', None, 'up'),
            'bar_window': ('bar window', (-6.3, 0.9), 'up'),
            'rezoning': ('notice', (-4.7, 0.9), 'up'),
            'car': ('car', (4.15, 4.4), 'right'),
        },
        hotspot_shapes={'alley': [(-1.9, 0, 0), (1.0, 0, 0), (1.0, 6.0, 0), (-1.9, 6.0, 0)],
                        'bar_window': [(-7.65, 0.9, 0.07), (-5.05, 0.9, 0.07), (-5.05, 2.55, 0.07), (-7.65, 2.55, 0.07)],
                        'rezoning': [(-4.95, 1.05, 0.03), (-4.47, 1.05, 0.03), (-4.47, 1.66, 0.03), (-4.95, 1.66, 0.03)]},
        hotspot_order=['billboard', 'alley', 'streetlamp', 'precinct_sign', 'bar_window', 'trash_can', 'neon',
                       'precinct_door', 'bar_door', 'rezoning', 'payphone', 'hydrant', 'car'],
        # walk-behind props: tag -> (x, z) floor point where the prop stands. The player is drawn behind
        # the prop while his feet are further away (higher on screen) than that point.
        occluders={'hydrant': (-5.6, 2.75), 'streetlamp': (3.3, 2.9), 'car': (4.9, 3.75)},
        # floor footprints the player walks around: (x, z, radius in metres)
        obstacles=[(-5.6, 2.75, 0.4), (3.3, 2.9, 0.32)],
        char_fill=((190, 196, 230), 0.06),
        tint=(0.7, 0.72, 0.88),
    )
    return S, cam, env, meta
