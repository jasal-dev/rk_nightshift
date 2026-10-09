"""Mulholland scenic overlook, 1:55 a.m.: a dirt pullout above the lit-up basin, a low stone wall, rain blowing sideways.
Kenji's white Prius sits nose to the view with the driver's door open and the dome light on, Kenji slumped behind the
wheel (seen, not shown: face to the window, eyes closed). Dr. Shah crouches at the door with a flashlight, Officer Park
holds the tape between two cones, the coroner's van idles at the right and Ray's car waits at the left."""
import math, random
import numpy as np
from scene3d import *
import textures as tx
import npc
import cars

CAR_O, CAR_YAW = (2.2, 0.0, 0.3), 25.0      # Kenji's Prius: floor centre and heading (nose toward the wall, a bit left)
DOOR_OPEN = 65.0


def car_frame():
    return Frame(CAR_O, Ry(CAR_YAW))


def car_pt(x, y, z):
    """Car-local point (x to the passenger side, y up, z toward the tail) -> world."""
    return tuple(car_frame().to((x, y, z)))


def quad(c, hw, hh):
    """A camera-facing-ish quad around car-local point c (for hotspot shapes)."""
    x, y, z = c
    return [car_pt(x, y - hh, z - hw), car_pt(x, y - hh, z + hw), car_pt(x, y + hh, z + hw), car_pt(x, y + hh, z - hw)]


def build(hide=()):
    S = Scene()
    rng = random.Random(41)
    # ---------------------------------------------------------------- materials
    S.mat('dirt', (255, 255, 255), tex=tx.hires(tx.decomposed_granite(), 2), texmode=4, texmap=1, texscale=5.0, refl=0.1,
          ripple=0.05, spec=0.35, shin=40)
    S.mat('puddle', (26, 24, 26), refl=0.92, ripple=0.08, spec=0.9, shin=120)
    S.mat('slope', (46, 38, 32), namp=0.4, nscale=3)
    S.mat('wall', (255, 255, 255), tex=tx.stone_wall(), texmode=4, texmap=1, texscale=1.6, refl=0.1, spec=0.3, shin=30)
    S.mat('wall_cap', (120, 112, 100), namp=0.3, nscale=8, refl=0.15, spec=0.4, shin=40)
    S.mat('brush', (24, 30, 22), namp=0.5, nscale=5, bump=0.4, bscale=6)
    S.mat('brush_lt', (40, 46, 32), namp=0.5, nscale=6, bump=0.4, bscale=6)
    S.mat('basin', (0, 0, 0), tex=tx.city_basin(w=3072, h=384), texmode=3, texemis=2.2)
    S.mat('clouds', (0, 0, 0), tex=tx.night_clouds(), texmode=3, texemis=0.55)
    S.mat('sign', (200, 200, 200), tex=tx.hires(tx.overlook_sign(), 2), texmode=1, spec=0.3)
    S.mat('post', (70, 52, 38), namp=0.3, nscale=10)
    # Kenji's Prius
    S.mat('paint', (214, 216, 214), spec=1.3, shin=90, refl=0.35)
    S.mat('glass', (12, 14, 18), spec=1.5, shin=120, refl=0.55)
    S.mat('trim', (22, 22, 24), spec=0.4, shin=30)
    S.mat('tire', (16, 16, 18))
    S.mat('rim', (150, 150, 156), spec=1.2, shin=60, refl=0.3)
    S.mat('headlight', (240, 240, 230), emis=(255, 250, 235), emis_mult=4)
    S.mat('taillight', (130, 10, 10), emis=(255, 30, 30), emis_mult=2.2)
    S.mat('interior', (34, 34, 38), namp=0.2, nscale=30)
    S.mat('headliner', (120, 116, 108), namp=0.1, nscale=30)
    S.mat('seat', (46, 46, 52), namp=0.25, nscale=24, spec=0.2)
    S.mat('dash', (30, 30, 34), spec=0.3, shin=30)
    S.mat('dash_lt', (70, 70, 76), spec=0.3, shin=30)
    S.mat('radio', (10, 14, 30), tex=tx.device_screen('radio'), texmode=3, texemis=1.6)
    S.mat('phone', (8, 20, 22), tex=tx.device_screen('glide'), texmode=3, texemis=1.8)
    S.mat('cup', (232, 226, 210), spec=0.3)
    S.mat('lid', (200, 70, 40))
    S.mat('chrome', (170, 170, 176), spec=1.6, shin=80, refl=0.5)
    S.mat('card', (220, 220, 220), tex=tx.glide_card(), texmode=1)
    S.mat('dome', (255, 230, 190), emis=(255, 220, 170), emis_mult=3)
    S.mat('scratch', (214, 216, 214), tex=tx.keyed_scratch('RAT'), texmode=1, spec=1.3, shin=90, refl=0.35)
    # cones, tape, the van, Ray's car
    S.mat('cone', (240, 100, 20), spec=0.4, shin=30)
    S.mat('cone_band', (230, 230, 220), spec=0.4)
    S.mat('tape', (240, 200, 30), emis=(60, 50, 0), spec=0.5)
    S.mat('van', (210, 212, 214), spec=1.0, shin=60, refl=0.25)
    S.mat('van_side', (210, 212, 214), tex=tx.hires(tx.van_side(), 2), texmode=1, spec=1.0, shin=60, refl=0.2)
    S.mat('amber', (200, 120, 20), emis=(255, 150, 30), emis_mult=2.5)
    S.mat('car_paint', (34, 38, 44), spec=1.4, shin=90, refl=0.45)
    S.mat('car_glass', (8, 10, 14), spec=1.5, shin=120, refl=0.6)

    # ---------------------------------------------------------------- the pullout, the wall, the drop
    S.wboxr(-30, -1, -4.3, 30, 0, 30, 'dirt')
    for (x, z, rx, rz) in [(3.4, 4.0, 0.7, 0.18), (-3.2, 1.2, 0.6, 0.16)]:
        S.ell(WORLD, (x, 0.004, z), (rx, 0.01, rz), 'puddle')
    WZ = -4.0
    with S.tag('wall'):
        S.wboxr(-14, 0, WZ - 0.25, 14, 0.72, WZ + 0.25, 'wall')
        S.wboxr(-14, 0.72, WZ - 0.3, 14, 0.8, WZ + 0.3, 'wall_cap', rnd=0.02)
    # the hillside falls away beyond the wall; brush along the crest breaks up the skyline
    S.wbox((0, -15, -12), (40, 0.4, 13), 'slope', rot=Rx(-62))
    for k in range(26):
        x = -15 + k * 1.2 + rng.uniform(-0.4, 0.4)
        if -9.5 < x < 10.5:
            continue
        r = rng.uniform(0.5, 1.1)
        S.ell(WORLD, (x, r * 0.5, WZ - 0.9 - rng.uniform(0, 1.2)), (r * 1.2, r * 0.8, r), rng.choice(['brush', 'brush_lt']), k=0.2)
    for (x, z, r) in [(-11.5, 1.0, 1.4), (-10.0, -2.0, 1.1), (11.0, -2.5, 1.3), (12.2, 1.8, 1.6), (-12.5, 5.0, 1.5)]:
        S.ell(WORLD, (x, r * 0.55, z), (r * 1.3, r * 0.9, r), 'brush', k=0.2)
        S.ell(WORLD, (x + r * 0.6, r * 0.8, z - 0.3), (r * 0.8, r * 0.7, r * 0.7), 'brush_lt', k=0.2)
    # the basin, far below, and the cloud deck lit orange from underneath
    S.wboxr(-80, -17, -91, 90, 2.3, -90, 'basin')
    S.wboxr(-100, 1.6, -111, 110, 45, -110, 'clouds')
    # scenic overlook sign
    with S.tag('sign'):
        S.wboxr(-6.4, 0, -3.35, -6.28, 1.2, -3.23, 'post')
        S.wboxr(-5.2, 0, -3.35, -5.08, 1.2, -3.23, 'post')
        S.wboxr(-6.6, 1.0, -3.3, -4.9, 1.75, -3.24, 'sign')

    # ---------------------------------------------------------------- Kenji's Prius
    F = car_frame()
    def box(c, half, m, rnd=0.0, rot=None, op=0, k=0):
        return S.box(F, c, half, rnd, m, rot=rot, op=op, k=k)
    with S.tag('prius'):
        box((0, 0.62, 0.0), (0.88, 0.3, 2.27), 'paint', rnd=0.14)                  # body
        box((0, 0.86, -1.8), (0.84, 0.08, 0.5), 'paint', rnd=0.08, rot=Rx(6))      # low nose
    box((0, 1.0, 0.35), (0.76, 0.52, 1.08), 'paint', op=1)                       # cabin well
    box((-0.9, 0.7, 0.07), (0.2, 0.27, 0.52), 'paint', op=1)                     # driver's door opening
    with S.tag('prius'):
        box((0, 1.47, 0.4), (0.8, 0.025, 0.76), 'paint', rnd=0.02)                 # roof
        box((-0.82, 1.2, -0.92), (0.04, 0.3, 0.035), 'paint', rot=Rx(-62))         # A pillars
        box((0.82, 1.2, -0.92), (0.04, 0.3, 0.035), 'paint', rot=Rx(-62))
        box((-0.83, 1.2, 0.63), (0.03, 0.28, 0.05), 'paint')                       # B pillars
        box((0.83, 1.2, 0.63), (0.03, 0.28, 0.05), 'paint')
        if 'windshield' not in hide:                                               # (the close-up looks out through it)
            box((0, 1.21, -0.93), (0.8, 0.012, 0.6), 'glass', rot=Rx(-28))         # windshield
        # sloped hatch: glass from the roof's back edge down to the tail deck, C pillars closing the sides under it
        (hy0, hz0), (hy1, hz1) = (1.46, 1.12), (0.93, 2.04)
        hl, ha = math.hypot(hy0 - hy1, hz1 - hz0) / 2, math.degrees(math.atan2(hy0 - hy1, hz1 - hz0))
        hc, hn = np.array([(hy0 + hy1) / 2, (hz0 + hz1) / 2]), np.array([math.cos(math.radians(ha)), math.sin(math.radians(ha))])
        box((0, *hc), (0.74, 0.012, hl), 'glass', rot=Rx(ha))
        for sx in (-0.82, 0.82):
            box((sx, *(hc - 0.25 * hn)), (0.05, 0.25, hl), 'paint', rnd=0.03, rot=Rx(ha))
        box((0.84, 1.18, 0.245), (0.012, 0.25, 0.875), 'glass')                    # passenger-side windows (to the C pillar)
        box((-0.84, 1.18, 0.895), (0.012, 0.25, 0.225), 'glass')                   # rear driver-side window (to the C pillar)
        box((0, 0.66, 2.24), (0.8, 0.22, 0.04), 'paint', rnd=0.04)                 # Kamm tail
        box((-0.62, 0.78, 2.27), (0.16, 0.05, 0.02), 'taillight')
        box((0.62, 0.78, 2.27), (0.16, 0.05, 0.02), 'taillight')
        box((0, 0.84, 2.27), (0.46, 0.012, 0.015), 'taillight')
        box((-0.6, 0.72, -2.24), (0.18, 0.05, 0.05), 'headlight', rot=Ry(10))
        box((0.6, 0.72, -2.24), (0.18, 0.05, 0.05), 'headlight', rot=Ry(-10))
        box((0, 0.36, 2.29), (0.7, 0.05, 0.03), 'trim')
        box((-0.881, 0.66, 1.1), (0.34, 0.085, 0.002), 'scratch', rot=Ry(-90))                 # RAT, keyed into the paint
        for (wx, wz) in ((-0.82, -1.45), (0.82, -1.45), (-0.82, 1.45), (0.82, 1.45)):
            wf = Frame(car_pt(wx, 0.32, wz), Ry(CAR_YAW) @ Rz(90))
            S.tcyl(wf, (0, 0, 0), (0.32, 0.32), (0.32, 0.32), 0.1, 'tire')
            S.tcyl(wf, (0, -0.1 * np.sign(wx), 0), (0.19, 0.19), (0.19, 0.19), 0.012, 'rim')
    # interior
    box((0, 0.46, 0.35), (0.76, 0.04, 1.08), 'interior')
    with S.tag('back_seat'):
        box((0, 0.58, 1.15), (0.74, 0.08, 0.28), 'seat', rnd=0.04)
        box((0, 0.88, 1.44), (0.74, 0.3, 0.07), 'seat', rnd=0.05, rot=Rx(-12))     # (top clears the hatch glass)
    for sx in (-0.38, 0.38):
        box((sx, 0.6, 0.12), (0.25, 0.08, 0.26), 'seat', rnd=0.05)
        box((sx, 0.94, 0.44), (0.25, 0.31, 0.07), 'seat', rnd=0.05, rot=Rx(-14))
        box((sx, 1.33, 0.5), (0.13, 0.06, 0.05), 'seat', rnd=0.03)
    box((0, 1.43, 0.39), (0.76, 0.012, 0.73), 'headliner')
    box((0, 0.88, -0.98), (0.78, 0.14, 0.24), 'dash', rnd=0.04)
    with S.tag('head_unit'):
        box((0, 1.0, -0.74), (0.1, 0.065, 0.006), 'radio', rot=Rx(-18))
    with S.tag('glovebox'):
        box((0.42, 0.8, -0.735), (0.22, 0.08, 0.008), 'dash_lt', rnd=0.01)
    with S.tag('cups'):
        box((0, 0.58, -0.2), (0.12, 0.13, 0.36), 'dash', rnd=0.03)                # console
        for cz in (-0.32, -0.14):
            S.cone(car_pt(0, 0.7, cz), car_pt(0, 0.86, cz), 0.035, 0.045, 'cup')
            S.fcyl(car_pt(0, 0.868, cz), 0.047, 0.008, 'lid')
    # steering wheel and column (Kenji's hands are on it)
    wc = np.array(car_pt(-0.38, 0.98, -0.6)); ax = F.M @ nrm((0, 0.45, 1))
    u = F.M @ np.array([1.0, 0, 0]); v = np.cross(ax, u)
    ring = [wc + 0.17 * (math.cos(a) * u + math.sin(a) * v) for a in np.linspace(0, 2 * math.pi, 15)]
    for a, b in zip(ring, ring[1:]):
        S.cyl(a, b, 0.016, 'dash')
    S.cyl(wc, car_pt(-0.38, 0.9, -0.82), 0.03, 'dash')
    with S.tag('ignition'):
        S.cyl(car_pt(-0.18, 0.9, -0.76), car_pt(-0.18, 0.9, -0.71), 0.012, 'chrome')
        S.sph(car_pt(-0.17, 0.85, -0.7), 0.025, 'chrome')
    with S.tag('phone_mount'):
        box((-0.16, 1.08, -0.79), (0.04, 0.075, 0.006), 'phone', rot=Rx(-20))
        box((-0.16, 1.08, -0.8), (0.046, 0.082, 0.004), 'trim', rot=Rx(-20))
    with S.tag('dashcam'):
        S.cyl(car_pt(0.0, 1.37, -0.66), car_pt(0.0, 1.36, -0.63), 0.03, 'trim')    # empty suction mount
        for k in range(3):                                                         # the cable, coiled neat on the dash
            S.cyl(car_pt(0.12 + 0.03 * k, 1.03, -0.86), car_pt(0.12 + 0.03 * k, 1.03, -0.8), 0.006, 'trim')
    with S.tag('visor'):
        box((-0.38, 1.4, -0.38), (0.2, 0.012, 0.09), 'dash_lt', rot=Rx(-60))
        box((-0.38, 1.39, -0.36), (0.07, 0.008, 0.045), 'card', rot=Rx(-60) @ Rx(90))
    box((-0.05, 1.445, 0.2), (0.12, 0.008, 0.06), 'dome')
    # the open driver's door, hinged at its front edge
    hinge = np.array(car_pt(-0.88, 0, -0.45))
    D = Frame(hinge, Ry(CAR_YAW) @ Ry(-DOOR_OPEN))
    with S.tag('door_pocket'):
        S.box(D, (0.07, 0.5, 0.52), (0.03, 0.09, 0.36), 0.01, 'interior')
        S.box(D, (0.1, 0.56, 0.4), (0.005, 0.03, 0.08), 0.0, 'cup')
    with S.tag('prius'):
        S.box(D, (0, 0.66, 0.52), (0.05, 0.3, 0.52), 0.04, 'paint')
        S.box(D, (0.05, 0.7, 0.52), (0.01, 0.26, 0.48), 0.01, 'interior')
        S.box(D, (0, 1.17, 0.5), (0.015, 0.22, 0.44), 0.01, 'glass')

    # Kenji, slumped behind the wheel, his face turned to the window. Eyes closed, nothing else shown.
    npc.cast(S, 'kenji', dict(npc.SEATED, lsp=56, le=34, lin=10, rsp=58, re=36, rin=12, lean=10, hp=12, hy=48, hr=14,
                              lhand='hold', rhand='hold'),
             car_pt(-0.38, 0.12, 0.08), yaw=CAR_YAW + 180, scale=0.93, tag='kenji')

    # ---------------------------------------------------------------- Dr. Shah at the door, Officer Park at the tape
    npc.cast(S, 'shah', dict(npc.CROUCH, rsp=70, re=28, rin=14, lsp=30, le=60, hp=10, hy=-10,
                             props=(('torch', 'r'),)),
             car_pt(-1.36, 0, 0.18), yaw=CAR_YAW + 90, scale=0.95, tag='shah')
    PARK = (5.05, 0, 2.9)
    npc.cast(S, 'park', dict(npc.STAND, lsp=28, le=40, lin=24, rsp=4, re=18, hp=4, hy=-16), PARK, yaw=-28, scale=0.94,
             tag='park')
    # cones and tape
    cones = [(4.35, 4.3), (5.95, 1.65)]
    for (x, z) in cones:
        S.wboxr(x - 0.2, 0, z - 0.2, x + 0.2, 0.04, z + 0.2, 'cone')
        S.cone((x, 0.04, z), (x, 0.72, z), 0.15, 0.03, 'cone')
        S.cone((x, 0.38, z), (x, 0.5, z), 0.1, 0.08, 'cone_band')
    (ax_, az_), (bx_, bz_) = cones
    for t0, t1 in ((0, 0.25), (0.25, 0.5), (0.5, 0.75), (0.75, 1.0)):
        def tp(t): return (ax_ + (bx_ - ax_) * t, 0.7 - 0.12 * math.sin(math.pi * t), az_ + (bz_ - az_) * t)
        S.cyl(tp(t0), tp(t1), 0.012, 'tape')
    S.cyl((5.95, 0.7, 1.65), (8.3, 0.62, 0.2), 0.012, 'tape')

    # ---------------------------------------------------------------- the coroner's van, idling (nose to the wall)
    vx0, vx1, vz0, vz1 = 6.4, 8.5, -3.3, 2.3
    with S.tag('van'):
        S.wboxr(vx0, 0.35, vz0, vx1, 2.55, vz1, 'van', rnd=0.12)
        S.wbox((vx0 - 0.005, 1.3, (vz0 + vz1) / 2 + 0.6), (1.6, 0.6, 0.01), 'van_side', rot=Ry(-90))
        S.wboxr(vx0 - 0.01, 1.55, vz0 + 0.25, vx0 + 0.02, 2.2, vz0 + 1.1, 'car_glass')
        S.wboxr(vx0 + 0.15, 0.45, vz1 - 0.01, vx0 + 0.45, 0.8, vz1 + 0.02, 'taillight')
        S.wboxr(vx1 - 0.45, 0.45, vz1 - 0.01, vx1 - 0.15, 0.8, vz1 + 0.02, 'taillight')
        S.wboxr(vx0 + 0.2, 1.1, vz1 - 0.01, vx1 - 0.2, 2.35, vz1 + 0.015, 'car_glass')
        S.wboxr(vx0 + 0.6, 2.56, vz0 + 0.5, vx1 - 0.6, 2.66, vz0 + 0.8, 'amber')
        for (wz) in (vz0 + 0.8, vz1 - 0.9):
            S.fcyl((vx0 + 0.04, 0.38, wz), 0.38, 0.12, 'tire', axis='x')

    # ---------------------------------------------------------------- Ray's car, parked at the left (nose to the wall)
    with S.tag('car'):
        cars.car(S, 'ray', (-5.0, 0.0, 1.6), 0, (34, 38, 44), L=4.8, W=1.88, H=1.42, lights=False,
                 tag='car')

    # ---------------------------------------------------------------- lights
    for sx in (-0.6, 0.6):                                                     # Prius headlights into the rain
        S.light(car_pt(sx, 0.72, -2.4), (255, 246, 226), power=26, range=16, vol=0.35, volshadow=True, soft=10,
                spot=(F.M @ np.array([0.0, -0.12, -1.0]), 14, 32))
    S.light(car_pt(-0.05, 1.36, 0.2), (255, 214, 160), power=1.8, range=3.2, vol=0.15, soft=14)   # dome light
    S.light(car_pt(-1.05, 0.95, 0.15), (240, 244, 255), power=4, range=5, vol=0.4, soft=8,
            spot=(F.M @ np.array([1.0, 0.15, -0.1]), 12, 30))                      # Shah's flashlight
    if 'tail_glow' not in hide:                                               # (red glow behind the car; not inside it)
        S.light(car_pt(0, 0.8, 2.6), (255, 40, 30), power=1.4, range=3, shadow=False, vol=0.2)      # tail lights
    S.light((7.35, 2.75, -2.4), (255, 150, 40), power=2.4, range=7, vol=0.4, shadow=False)          # van roof light
    S.light((7.35, 0.7, 2.8), (255, 40, 30), power=1.2, range=3, shadow=False, vol=0.2)
    S.light((0.0, -40.0, -120.0), (255, 150, 90), power=900, range=200, shadow=False)              # the city's glow
    S.light((-3.0, 9.0, 8.0), (120, 140, 200), power=14, range=26, soft=30)              # hazy moon behind cloud
    S.light((7.6, 3.4, 3.8), (236, 240, 255), power=60, range=16, vol=0.5, volshadow=True, soft=20,
            spot=((-1.0, -0.55, -0.55), 24, 50))                                 # the van's scene light on the car
    S.sun((0.3, -1, -0.4), (70, 80, 120), power=0.3, shadow=False)

    cam = Camera((0.6, 3.1, 11.0), (1.2, 0.9, -2.0), fov=44, W=3840, H=2160)
    env = dict(sky=(26, 24, 40), bounce=(22, 16, 14), fog_col=(40, 30, 40), fog=0.012, fog_h0=0.0, fog_hf=0.15,
               fog_max=230, vol_scale=4, vol_steps=40, reflections=True, grid=0.75, ao_scale=1.4)
    meta = dict(
        room='mulholland_overlook',
        walk=[(-3.6, -1.8), (-0.5, -1.8), (0.0, 1.4), (1.8, 3.15), (4.2, 2.6), (4.6, -0.5), (5.4, -0.5), (5.4, 1.4),
              (4.15, 3.6), (4.15, 5.0), (-3.6, 5.0)],
        walk_zmin=-1.8, walk_zmax=5.0, scale_x=0.0,
        spawns={'drive': (-3.2, 3.4), 'prius_interior': (0.0, 1.45), 'start': (-1.0, 3.0)},
        hotspots={
            'kenji': ('Kenji', (0.25, 1.9), 'right'),
            'shah': ('Dr. Shah', (0.25, 1.9), 'right'),
            'park': ('Officer Park', (4.1, 3.2), 'right'),
            'inside': ('inside the car', (0.0, 1.4), 'right'),
            'prius': ('white Prius', (1.9, 3.0), 'up'),
            'ground': ('ground', (-1.0, 2.6), 'down'),
            'wall': ('low wall', (-2.2, -1.6), 'up'),
            'view': ('the city', None, 'up'),
            'van': ("coroner's van", (5.1, 0.0), 'right'),
            'sign': ('sign', (-3.3, -1.6), 'up'),
            'car': ('my car', (-3.3, 3.0), 'left'),
        },
        hotspot_shapes={
            'kenji': quad((-0.4, 1.12, 0.12), 0.22, 0.3),
            'inside': [car_pt(-0.95, 0.45, -0.45), car_pt(-0.95, 0.45, 0.65), car_pt(-0.95, 1.45, 0.65),
                       car_pt(-0.95, 1.45, -0.45)],
            'ground': [(-1.4, 0.0, -3.3), (0.4, 0.0, -3.3), (0.6, 0.0, -2.0), (-1.4, 0.0, -2.0)],
            'view': [(-40, 0.85, -60), (60, 0.85, -60), (60, 30, -60), (-40, 30, -60)],
        },
        hotspot_order=['view', 'wall', 'sign', 'ground', 'van', 'car', 'park', 'prius', 'inside', 'shah', 'kenji'],
        obstacles=[],
        char_fill=((200, 196, 220), 0.12),
        tint=(0.76, 0.72, 0.84),
        exposure=1.6,
    )
    return S, cam, env, meta
