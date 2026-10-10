"""Pier 9, Port of Los Angeles, one in the morning: rain, sodium light, stacked containers, a salvage warehouse with a
green door, Tiny under the awning, a burn barrel, and a boat hook on a piling at the water's edge."""
import math, random
import numpy as np
from scene3d import *
import textures as tx
import npc
import cars


def build(hide=(), time='night'):
    """time: 'night' (Case 1), 'dawn' (Case 5, scene 8: the rain over, the sky going pink behind the crane, the barrel
    cold, Vance in his doorway, Brenner's gray Lincoln and Brenner himself as overlays) or 'sunrise' (scenes 9 and 10:
    the sun up over the port, the Lincoln left for the lab, and whoever Ray called, as overlays)."""
    day = time != 'night'
    S = Scene()
    rng = random.Random(9)
    # ---------------------------------------------------------------- materials
    S.mat('deck', (255, 255, 255), tex=tx.hires(tx.concrete(seed=51, base=(104, 104, 102)), 2), texmode=4, texmap=1,
          texscale=3.0, refl=0.42, ripple=0.14, spec=0.45, shin=50)
    S.mat('puddle', (26, 26, 30), refl=0.95, ripple=0.06, spec=0.9, shin=120)
    S.mat('water', (8, 12, 16), refl=0.9, ripple=0.22, spec=1.0, shin=90)
    S.mat('edge', (90, 86, 78), namp=0.25, nscale=6, refl=0.1)
    S.mat('timber', (64, 46, 34), namp=0.3, nscale=10, bump=0.2, bscale=12)
    S.mat('bollard', (30, 30, 32), spec=0.6, shin=40)
    S.mat('bollard_y', (170, 140, 30), spec=0.4)
    S.mat('shed', (255, 255, 255), tex=tx.hires(tx.corrugated(seed=52, base=(118, 124, 126)), 2), texmode=4, texmap=1,
          texscale=2.4, spec=0.35, shin=30)
    S.mat('shed_dk', (255, 255, 255), tex=tx.hires(tx.corrugated(seed=53, base=(78, 82, 84), rust=0.5), 2), texmode=4,
          texmap=1, texscale=2.4, spec=0.3, shin=30)
    S.mat('roof', (70, 72, 74), spec=0.4, shin=30, refl=0.2)
    S.mat('green_door', (38, 92, 62), namp=0.25, nscale=7, spec=0.35, shin=30)
    S.mat('green_dk', (24, 60, 40), namp=0.2, nscale=7)
    S.mat('steel', (120, 122, 126), spec=0.8, shin=50)
    S.mat('metal_dk', (36, 38, 42), spec=0.5, shin=40)
    S.mat('sign', (200, 200, 200), tex=tx.hires(tx.salvage_sign(), 2), texmode=1)
    S.mat('awning', (52, 70, 66), spec=0.5, shin=40, refl=0.15)
    S.mat('bulb', (255, 200, 130), emis=(255, 190, 110), emis_mult=6)
    S.mat('cage', (30, 30, 30))
    for i, (col, label) in enumerate([((150, 46, 36), 'HANJIN'), ((40, 74, 120), 'COSCO'), ((60, 112, 70), 'EVERGREEN'),
                                      ((170, 120, 40), 'MAERSK')]):
        S.mat(f'cont{i}', (255, 255, 255), tex=tx.container_side(col, label, seed=60 + i), texmode=1, spec=0.3, shin=30)
        S.mat(f'cont{i}_end', (255, 255, 255), tex=tx.container_end(col, seed=70 + i), texmode=1, spec=0.3, shin=30)
        S.mat(f'cont{i}_top', col, namp=0.3, nscale=5, spec=0.2)
    S.mat('barrel', (70, 46, 34), namp=0.4, nscale=9, bump=0.3, bscale=10, spec=0.2)
    S.mat('ash', (40, 36, 34), namp=0.5, nscale=20)
    S.mat('ember', (120, 40, 10), emis=(255, 110, 40), emis_mult=2.5, namp=0.6, nscale=30)
    S.mat('nav_light', (60, 255, 120), emis=(60, 255, 120), emis_mult=4)
    S.mat('pole', (110, 92, 66), namp=0.2, nscale=30)
    S.mat('hook', (150, 150, 156), spec=1.0, shin=60)
    S.mat('chair', (60, 62, 66), spec=0.5, shin=30)
    S.mat('crate', (120, 96, 66), namp=0.35, nscale=8)
    S.mat('radio', (40, 38, 36), spec=0.5, shin=40)
    S.mat('radio_dial', (200, 150, 60), emis=(255, 180, 80), emis_mult=2.0)
    S.mat('car_paint', (34, 38, 44), spec=1.4, shin=90, refl=0.45)
    S.mat('car_glass', (8, 10, 14), spec=1.5, shin=120, refl=0.6)
    S.mat('chrome', (150, 150, 156), spec=1.6, shin=80, refl=0.5)
    S.mat('tire', (16, 16, 18))
    S.mat('taillight', (120, 10, 10), emis=(220, 30, 30), emis_mult=1.2)
    S.mat('lamp_head', (50, 50, 54), spec=0.3)
    S.mat('lamp_glass', (255, 190, 120), emis=(255, 170, 90), emis_mult=0.0 if time == 'sunrise' else 6)
    S.mat('crane', (150, 60, 40), namp=0.2, nscale=4)
    S.mat('red_lamp', (255, 40, 30), emis=(255, 30, 20), emis_mult=8)
    S.mat('hull', (22, 24, 30), spec=0.2)
    S.mat('ship_light', (255, 230, 180), emis=(255, 220, 160), emis_mult=5)
    if day:
        S.mat('sky', (40, 40, 60), tex=tx.dawn_sky(sun=time == 'sunrise'), texmode=3, texemis=1.25 if time == 'sunrise' else 1.0)
    else:
        S.mat('sky', (16, 12, 24), tex=tx.skyline(15, 1024, 256, k=3), texmode=3, texemis=1.0)
    S.mat('backing', (16, 14, 20), spec=0.2)

    # ---------------------------------------------------------------- pier deck and water
    EDGE = 5.4
    S.wboxr(-40, -1, -60, EDGE, 0, 30, 'deck')
    for (x, z, rx, rz) in [(-2.4, 3.9, 1.0, 0.3), (2.6, 2.2, 0.6, 0.2)]:
        S.ell(WORLD, (x, 0.004, z), (rx, 0.012, rz), 'puddle')
    S.wboxr(EDGE - 0.25, 0, -60, EDGE + 0.05, 0.18, 30, 'edge')                   # cap timber
    S.wboxr(EDGE, -1.6, -60, EDGE + 0.06, 0.0, 30, 'timber')                      # fender board
    S.wboxr(EDGE, -60, -400, 400, -1.1, 60, 'water')
    for z in (-6.0, 4.4):
        S.cyl((EDGE - 0.35, 0, z), (EDGE - 0.35, 0.5, z), 0.16, 'bollard')
        S.sph((EDGE - 0.35, 0.5, z), 0.2, 'bollard')
        S.cyl((EDGE - 0.35, 0.3, z), (EDGE - 0.35, 0.36, z), 0.165, 'bollard_y')
    # pilings along the edge (one carries the boat hook)
    for z in (-12.0, -3.0):
        S.cyl((EDGE + 0.25, -2.0, z), (EDGE + 0.25, 0.9, z), 0.17, 'timber')

    # ---------------------------------------------------------------- warehouse (Harbor Marine Salvage)
    WZ = -2.2
    S.wboxr(-2.6, 0, -14, 4.9, 6.2, WZ, 'shed')
    S.wboxr(-2.8, 6.2, -14.2, 5.1, 6.45, WZ + 0.25, 'roof')
    S.wboxr(-2.6, 0, WZ, 4.9, 0.35, WZ + 0.05, 'shed_dk')                        # kick plate
    S.wboxr(-2.2, 0.0, WZ, -0.4, 2.9, WZ + 0.04, 'shed_dk')                       # roller door, shut
    for y in np.arange(0.2, 2.9, 0.3):
        S.wboxr(-2.2, y, WZ + 0.04, -0.4, y + 0.03, WZ + 0.06, 'metal_dk')
    with S.tag('green_door'):
        S.wboxr(0.85, 0, WZ - 0.1, 2.15, 2.35, WZ + 0.04, 'green_dk')
        S.wboxr(0.92, 0.02, WZ, 2.08, 2.28, WZ + 0.08, 'green_door', rnd=0.01)
        S.wboxr(1.05, 1.55, WZ + 0.08, 1.95, 2.1, WZ + 0.09, 'green_dk')          # peep panel
        S.wboxr(1.85, 1.0, WZ + 0.08, 1.95, 1.2, WZ + 0.14, 'steel')              # handle
    with S.tag('warehouse_sign'):
        S.wboxr(0.0, 3.3, WZ, 4.4, 3.95, WZ + 0.08, 'sign')
    # awning over the door and Tiny's chair
    S.wbox((2.3, 2.72, -1.45), (1.9, 0.035, 0.8), 'awning', rot=Rx(-8))
    for x in (0.45, 4.15):
        S.cyl((x, 0, -0.78), (x, 2.62, -0.78), 0.045, 'metal_dk')
    S.cyl((1.5, 2.65, WZ + 0.05), (1.5, 2.5, WZ + 0.25), 0.012, 'cage')
    S.sph((1.5, 2.45, WZ + 0.27), 0.07, 'bulb')
    # left corner: a lamp post against the warehouse
    S.cone((-3.0, 0, -2.4), (-3.0, 6.8, -2.4), 0.09, 0.06, 'metal_dk')
    S.cone((-3.0, 6.7, -2.4), (-3.0, 7.0, -0.8), 0.05, 0.04, 'metal_dk')
    S.ell(WORLD, (-3.0, 6.95, -0.6), (0.25, 0.1, 0.42), 'lamp_head')
    S.ell(WORLD, (-3.0, 6.87, -0.6), (0.18, 0.04, 0.3), 'lamp_glass')

    # ---------------------------------------------------------------- Tiny, his chair, the radio
    tx_, tz_ = 2.85, -1.35
    with S.tag('tiny'):
        for sx in (-1, 1):
            S.cyl((tx_ + sx * 0.22, 0, tz_ - 0.22), (tx_ - sx * 0.22, 0.4, tz_ + 0.22), 0.015, 'chair')
            S.cyl((tx_ + sx * 0.22, 0, tz_ + 0.22), (tx_ - sx * 0.22, 0.4, tz_ - 0.22), 0.015, 'chair')
        S.wboxr(tx_ - 0.26, 0.36, tz_ - 0.25, tx_ + 0.26, 0.4, tz_ + 0.24, 'chair')
        S.wboxr(tx_ - 0.24, 0.6, tz_ - 0.32, tx_ + 0.24, 0.98, tz_ - 0.28, 'chair')
    npc.place(S, 'tiny', dict(npc.SEATED, yaw=0, lsp=26, le=58, lin=10, rsp=26, re=56, rin=12, hp=6, hy=-14,
                              coatlen=0.12),
              (tx_, -0.06, tz_ - 0.08), yaw=-12, scale=1.16, tag='tiny',
              colors=dict(coat=(44, 48, 62), coat_dk=(30, 32, 42), lining=(40, 40, 46), shirt=(70, 70, 76),
                          pants=(52, 54, 60), skin=(132, 92, 70), skin_dk=(108, 74, 58), stubble=(116, 82, 64),
                          lips=(120, 80, 66), hair=(26, 24, 24), hairgrey=(40, 38, 38), brow=(24, 22, 22)))
    # Blue Note napkin folded in his breast pocket
    S.wbox((tx_ + 0.12, 1.0, tz_ + 0.1), (0.035, 0.03, 0.006), 'radio_dial', rot=Ry(-12))
    with S.tag('radio'):
        S.wboxr(tx_ + 0.6, 0, tz_ - 0.25, tx_ + 1.15, 0.5, tz_ + 0.25, 'crate')
        S.wboxr(tx_ + 0.7, 0.5, tz_ - 0.05, tx_ + 1.02, 0.68, tz_ + 0.06, 'radio', rnd=0.01)
        S.wboxr(tx_ + 0.74, 0.55, tz_ + 0.06, tx_ + 0.86, 0.63, tz_ + 0.065, 'radio_dial')
        S.cyl((tx_ + 0.98, 0.68, tz_), (tx_ + 1.1, 1.05, tz_), 0.006, 'steel')

    # ---------------------------------------------------------------- burn barrel
    bx, bz = -0.9, 1.3
    if 'barrel' not in hide:
        with S.tag('barrel'):
            S.tcyl(Frame((bx, 0.45, bz)), (0, 0, 0), (0.3, 0.3), (0.3, 0.3), 0.45, 'barrel', shell=0.012)
            for y in (0.2, 0.62):
                S.tcyl(Frame((bx, y, bz)), (0, 0, 0), (0.31, 0.31), (0.31, 0.31), 0.015, 'barrel')
            S.tcyl(Frame((bx, 0.78, bz)), (0, 0, 0), (0.285, 0.285), (0.285, 0.285), 0.02, 'ash')
            for k in range(6):
                a = k * 1.1
                S.ell(WORLD, (bx + 0.16 * math.cos(a), 0.81, bz + 0.16 * math.sin(a)), (0.07, 0.03, 0.06),
                      'ash' if day else 'ember', k=0.02)

    # ---------------------------------------------------------------- piling with the boat hook
    px, pz = EDGE + 0.05, 3.1
    with S.tag('piling'):
        S.cyl((px, -2.0, pz), (px, 1.15, pz), 0.18, 'timber')
        S.sph((px, 1.15, pz), 0.18, 'timber')
        S.cyl((px - 0.17, 0.95, pz + 0.05), (px - 0.24, 0.95, pz + 0.08), 0.012, 'steel')   # the nail it hangs on
        S.cyl((px, 1.3, pz), (px, 1.45, pz), 0.05, 'nav_light')                          # harbour marker lamp
    if 'hook' not in hide:
        with S.tag('hook'):
            S.cyl((px - 0.3, 0.02, pz + 0.18), (px - 0.24, 2.25, pz + 0.12), 0.034, 'pole')
            S.cyl((px - 0.24, 2.25, pz + 0.12), (px - 0.24, 2.42, pz + 0.12), 0.016, 'hook')
            S.cone((px - 0.24, 2.32, pz + 0.12), (px - 0.12, 2.24, pz + 0.12), 0.014, 0.008, 'hook')

    # ---------------------------------------------------------------- containers (left, behind the car)
    def container(x0, y0, z0, i, L=6.1):
        S.wboxr(x0, y0, z0, x0 + L, y0 + 2.59, z0 + 2.44, f'cont{i}_top')
        S.wboxr(x0 + 0.05, y0 + 0.05, z0 + 2.44, x0 + L - 0.05, y0 + 2.54, z0 + 2.46, f'cont{i}')
        S.wboxr(x0 + L, y0 + 0.05, z0 + 0.05, x0 + L + 0.02, y0 + 2.54, z0 + 2.39, f'cont{i}_end')
    with S.tag('containers'):
        container(-9.8, 0, -6.4, 0)
        container(-9.2, 2.59, -6.2, 1)
        container(-10.5, 0, -10.2, 2)
        container(-10.0, 2.59, -10.0, 3)
        container(-9.0, 5.18, -10.4, 0)

    # ---------------------------------------------------------------- Ray's car, parked at the left, nose to the right
    with S.tag('car'):
        cars.car(S, 'ray', (-6.75, 0.0, 2.65), -90, (34, 38, 44), L=4.8, W=1.88, H=1.42, lights=False,
                 tag='car')

    # ---------------------------------------------------------------- the harbour beyond: crane, a ship, the lights
    with S.tag('crane'):
        for x in (14.0, 24.0):
            for z in (-30.0, -38.0):
                S.wboxr(x - 0.5, -1, z - 0.5, x + 0.5, 18, z + 0.5, 'crane')
        S.wboxr(13.0, 17.0, -39, 25.0, 18.6, -29, 'crane')
        S.wboxr(18.0, 17.4, -60, 20.0, 18.4, -16, 'crane')                       # boom over the water
        S.wboxr(16.5, 18.6, -36, 21.5, 21.0, -31, 'crane')                       # machinery house
        for (x, y, z) in [(14.0, 18.9, -30.0), (24.0, 18.9, -30.0), (19.0, 21.3, -33.5), (19.0, 18.5, -16.5)]:
            S.sph((x, y, z), 0.35, 'red_lamp')
    S.wboxr(28, -1.2, -70, 120, 6.0, -52, 'hull')
    S.wboxr(60, 6.0, -66, 76, 14.0, -56, 'hull')
    for k in range(24):
        S.sph((30 + k * 3.7, 5.2 + (k % 3) * 0.4, -52.0), 0.12, 'ship_light')
    S.wboxr(-200, -2, -201, 300, 140 if day else 60, -200, 'sky')

    # ---------------------------------------------------------------- lights
    if day:
        dawn_lights(S, hide, time, bx, bz, tx_, tz_, px, pz, WZ)
    else:
        S.light((-3.0, 6.7, -0.6), (255, 160, 80), power=60, range=18, vol=0.45, volshadow=True, soft=16,
                spot=((0.25, -1, 0.35), 32, 62))                                       # sodium lamp
        S.light((1.5, 2.35, WZ + 0.35), (255, 190, 120), power=9, range=8, vol=0.3, soft=10)   # caged bulb over the door
        S.light((px - 0.1, 1.5, pz + 0.1), (90, 255, 140), power=1.6, range=5, vol=0.25, soft=8)   # marker lamp on the piling
        S.light((-9.5, 6.0, 4.5), (255, 165, 90), power=22, range=14, vol=0.15, soft=16,
                spot=((0.3, -1, -0.2), 35, 70))                                         # another lamp, off to the left
        S.light((bx, 0.95, bz), (255, 120, 50), power=2.2, range=4, vol=0.35, soft=8)            # burn barrel embers
        S.light((tx_ + 0.86, 0.75, tz_ + 0.2), (255, 170, 80), power=0.25, range=2, shadow=False)
        S.light((16.0, 9.0, -6.0), (150, 175, 255), power=70, range=45, vol=0.4, shadow=False)  # harbour floodlights
        S.light((19.0, 18.0, -16.0), (255, 40, 30), power=4, range=26, vol=0.5, shadow=False)
        S.sun((0.35, -1, -0.5), (70, 82, 130), power=0.35, shadow=False)

    cam = Camera((0.4, 2.55, 13.6), (0.15, 2.25, 0), fov=38, W=3840, H=2160)
    env = dict(sky=(20, 22, 38), bounce=(14, 12, 16), fog_col=(22, 22, 34), fog=0.035, fog_h0=0.0, fog_hf=0.2,
               fog_max=140, vol_scale=4, vol_steps=40, reflections=True, grid=0.75, ao_scale=1.5)

    if day:
        dawn_extras(S, hide, time, EDGE)
        return S, cam, dawn_env(time), dawn_meta(time, EDGE, bx, bz, px, pz)
    meta = dict(
        room='pier9_dock',
        walk=[(-4.0, -0.5), (4.5, -0.5), (4.5, 4.8), (-4.0, 4.8)],
        walk_zmin=-0.5, walk_zmax=4.8, scale_x=0.0,
        spawns={'street': (-3.4, 2.6), 'vance_office': (1.5, -0.25), 'start': (0.0, 2.0)},
        hotspots={
            'tiny': ('Tiny', (1.95, -0.25), 'right'),
            'green_door': ('green door', (1.5, -0.35), 'up'),
            'radio': ('radio', (3.7, -0.3), 'up'),
            'barrel': ('burn barrel', (-0.05, 1.35), 'left'),
            'piling': ('boat hook', (4.4, 3.1), 'right'),
            'containers': ('containers', None, 'up'),
            'crane': ('crane', None, 'up'),
            'water': ('water', None, 'right'),
            'warehouse_sign': ('sign', None, 'up'),
            'car': ('car', (-3.6, 2.5), 'left'),
        },
        hotspot_shapes={'water': [(EDGE + 0.1, -1.1, 12), (EDGE + 0.1, -1.1, -45), (90, -1.1, -45), (90, -1.1, 12)]},
        hotspot_order=['crane', 'water', 'containers', 'warehouse_sign', 'car', 'green_door', 'radio', 'tiny', 'barrel',
                       'piling'],
        overlays=['hook'],
        occluders={'barrel': (bx, bz)},
        obstacles=[(bx, bz, 0.45)],
        char_fill=((196, 196, 226), 0.08),
        tint=(0.72, 0.72, 0.86),
    )
    return S, cam, env, meta


# ---------------------------------------------------------------- Case 5: dawn and sunrise
LINCOLN = (-6.15, -0.75)      # Brenner's gray Lincoln Town Car, nose to the right, behind Ray's car
BOLLARD = (5.05, 4.4)         # the iron bollard at the end of the pier, where Ray sets down Danny's phone
BRENNER = (3.05, 3.65)        # where Brenner stands to talk, facing Ray at the bollard
HOOD = (-2.95, -0.55)         # Brenner bent over the Lincoln's hood, cuffed
VANCE = (1.5, -1.85)          # Vance in his doorway
DOYLE = (-3.55, 2.25)         # by the hood of Ray's car, where the box is laid out
OKAFOR = (-3.45, 2.2)
MARA = (-3.5, 2.3)

VANCE_COLORS = dict(coat=(52, 52, 58), coat_dk=(38, 38, 42), lining=(60, 56, 70), shirt=(104, 96, 118),
                    pants=(44, 44, 50), hair=(190, 188, 184), hairgrey=(214, 212, 208), brow=(170, 168, 164),
                    stubble=(166, 124, 104), skin=(170, 128, 106), skin_dk=(140, 102, 86))


def dawn_env(time):
    if time == 'sunrise':
        return dict(sky=(120, 126, 150), bounce=(70, 58, 52), fog_col=(170, 140, 120), fog=0.008, fog_h0=0.0, fog_hf=0.12,
                    fog_max=260, vol_scale=4, vol_steps=40, reflections=True, grid=0.75, ao_scale=1.4)
    return dict(sky=(70, 70, 104), bounce=(42, 34, 44), fog_col=(120, 90, 110), fog=0.01, fog_h0=0.0, fog_hf=0.14,
                fog_max=260, vol_scale=4, vol_steps=40, reflections=True, grid=0.75, ao_scale=1.4)


def dawn_lights(S, hide, time, bx, bz, tx_, tz_, px, pz, WZ):
    if time == 'sunrise':
        S.sun((-0.8, -0.3, 0.52), (255, 200, 140), power=2.4, shadow=True, soft=6)        # the sun over the port
        S.sun((0.3, -1, 0.2), (150, 170, 220), power=0.35, shadow=False)                  # the sky
    else:
        S.sun((-0.75, -0.22, 0.6), (255, 150, 150), power=0.7, shadow=True, soft=14)      # pink, before the sun
        S.sun((0.3, -1, 0.2), (110, 120, 180), power=0.45, shadow=False)
        S.light((-3.0, 6.7, -0.6), (255, 160, 80), power=30, range=18, vol=0.2, soft=16,
                spot=((0.25, -1, 0.35), 32, 62))                                           # the sodium lamp, still on
    S.light((1.5, 2.35, WZ + 0.35), (255, 190, 120), power=4, range=6, vol=0.1, soft=10)  # the caged bulb
    S.light((1.5, 1.6, WZ - 0.6), (255, 200, 140), power=2.5, range=4, soft=10)          # Vance's office, through the door
    S.light((px - 0.1, 1.5, pz + 0.1), (90, 255, 140), power=0.8, range=4, soft=8)       # the marker lamp on the piling
    S.light((tx_ + 0.86, 0.75, tz_ + 0.2), (255, 170, 80), power=0.25, range=2, shadow=False)


def dawn_extras(S, hide, time, EDGE):
    S.mat('lincoln_dk', (20, 20, 24), spec=0.6)
    S.mat('doorway', (30, 24, 20), emis=(110, 80, 50), emis_mult=0.25)
    S.mat('phone_case', (16, 16, 18), spec=0.8, shin=50)
    S.mat('sticker', (40, 80, 170), spec=0.4)
    S.mat('cup_w', (232, 226, 210), spec=0.3)
    S.mat('box', (176, 146, 100), namp=0.2, nscale=20)
    S.mat('laptop', (60, 62, 66), spec=1.0, shin=60)
    S.mat('laptop_lit', (40, 60, 90), emis=(140, 180, 230), emis_mult=1.2)
    S.mat('paper_w', (236, 232, 220))
    # Vance's door stands open; Vance in it, an overcoat over the cardigan, his tea
    with S.tag('vance'):
        S.wboxr(0.93, 0.02, -2.2 + 0.085, 2.07, 2.27, -2.2 + 0.1, 'doorway')
        S.wbox((0.86, 1.15, -2.2 + 0.6), (0.04, 1.14, 0.56), 'green_door', rot=Ry(0))
    npc.place(S, 'vance', dict(npc.STAND, props=(('teacup', 'l'),), lsp=30, le=92, lin=34, rsp=-2, re=16, hp=2,
                               hy=24, coatlen=0.48),
              (VANCE[0], 0.0, VANCE[1]), yaw=12, scale=0.98, tag='vance', colors=VANCE_COLORS)
    # the bollard's things (overlays): Danny's dead phone, Brenner's coffee
    bx, bz = BOLLARD
    if time == 'dawn' and 'bollard_phone' not in hide:
        with S.tag('bollard_phone'):
            S.wbox((bx - 0.02, 0.715, bz), (0.04, 0.008, 0.075), 'phone_case', rot=Ry(20))
            S.wbox((bx - 0.02, 0.724, bz + 0.02), (0.015, 0.002, 0.015), 'sticker', rot=Ry(20))
    if time == 'dawn' and 'bollard_cup' not in hide:
        with S.tag('bollard_cup'):
            S.tcyl(Frame((bx + 0.1, 0.77, bz - 0.06)), (0, 0, 0), (0.044, 0.044), (0.034, 0.034), 0.065, 'cup_w')
            S.tcyl(Frame((bx + 0.1, 0.84, bz - 0.06)), (0, 0, 0), (0.046, 0.046), (0.046, 0.046), 0.008, 'lincoln_dk')
    # Brenner's gray Lincoln: an overlay at dawn (it arrives), part of the set at sunrise (left for the lab)
    if time == 'sunrise' or 'lincoln' not in hide:
        cars.car(S, 'lincoln', (LINCOLN[0], 0.0, LINCOLN[1]), -90, (118, 122, 128), L=5.5, W=1.95, H=1.45,
                 lights=False, tag='lincoln_car')
    if time == 'dawn':
        stand = dict(npc.STAND, hp=4, hy=-6)
        if 'brenner' not in hide:
            npc.cast(S, 'brenner', dict(stand, props=(('cup', 'l'),), lsp=32, le=82, lin=26, rsp=-2, re=14),
                     (BRENNER[0], 0.0, BRENNER[1]), yaw=58, scale=1.07, tag='brenner')
        if 'brenner_gun' not in hide:
            npc.cast(S, 'brenner', dict(stand, props=(('revolver', 'r'),), rsp=30, rsa=6, re=34, rin=10, rhand='fist',
                                        lsp=-4, le=12, hp=6, hy=-2),
                     (BRENNER[0], 0.0, BRENNER[1]), yaw=58, scale=1.07, tag='brenner_gun')
        if 'brenner_cuffed' not in hide:
            npc.cast(S, 'brenner', dict(npc.STAND, lean=66, lhp=30, rhp=26, lk=8, rk=6, lsp=-22, lsa=10, le=96, lin=96,
                                        rsp=-22, rsa=10, re=96, rin=96, hp=-36, hy=34, coatlen=0.24),
                     (HOOD[0], 0.0, HOOD[1]), yaw=-90, scale=1.07, tag='brenner_cuffed')
    if time == 'sunrise':
        # Danny's box laid open on the hood of Ray's car, for Doyle (with her), the drive for Okafor, Mara's laptop
        if 'doyle' not in hide:
            with S.tag('doyle_box'):
                S.wboxr(-4.95, 0.88, 2.2, -4.5, 1.12, 2.75, 'box')                  # sitting on the hood, not in it
                S.wboxr(-4.92, 0.94, 2.23, -4.53, 1.14, 2.72, 'box', op=1)          # open: no lid
                for k in range(4):
                    S.wbox((-5.35 + k * 0.02, 0.855, 2.0 + k * 0.28), (0.1, 0.004, 0.12), 'paper_w', rot=Ry(10 * k))
            npc.cast(S, 'doyle', dict(npc.STAND, lsp=26, le=70, lin=40, rsp=24, re=74, rin=42, hp=12, hy=-30),
                     (DOYLE[0], 0.0, DOYLE[1]), yaw=-70, scale=0.95, tag='doyle')
        if 'okafor' not in hide:
            npc.cast(S, 'okafor', dict(npc.STAND, props=(('clipboard', 'r'),), rsp=30, re=86, rin=30, lsp=4, le=16,
                                       hp=8, hy=20), (OKAFOR[0], 0.0, OKAFOR[1]), yaw=70, scale=0.94, tag='okafor')
        if 'mara' not in hide:
            with S.tag('mara_laptop'):
                S.wbox((-4.75, 0.86, 2.55), (0.17, 0.01, 0.12), 'laptop', rot=Ry(-70))
                S.wbox((-4.68, 0.97, 2.48), (0.17, 0.11, 0.008), 'laptop_lit', rot=Ry(-70) @ Rx(-12))
            npc.cast(S, 'mara', dict(npc.STAND, headset=True, lsp=30, le=74, lin=20, rsp=30, re=78, rin=22, hp=18,
                                     hy=-10), (MARA[0], 0.0, MARA[1]), yaw=-75, scale=0.94, tag='mara')


def dawn_meta(time, EDGE, bx, bz, px, pz):
    def rect(p, w, h):
        x, z = p
        return [(x - w, 0.0, z), (x + w, 0.0, z), (x + w, h, z), (x - w, h, z)]
    lx, lz = LINCOLN
    hs = {
        'tiny': ('Tiny', (1.95, -0.25), 'right'),
        'vance': ('Vance', (1.5, -0.35), 'up'),
        'radio': ('radio', (3.7, -0.3), 'up'),
        'barrel': ('burn barrel', (-0.05, 1.35), 'left'),
        'piling': ('boat hook', (4.4, 3.1), 'right'),
        'containers': ('containers', None, 'up'),
        'crane': ('crane', None, 'up'),
        'water': ('water', None, 'right'),
        'warehouse_sign': ('sign', None, 'up'),
        'car': ('car', (-3.6, 2.5), 'left'),
        'bollard': ('bollard', (4.35, 4.25), 'right'),
        'lincoln': ('gray Lincoln', (-2.9, 0.75), 'left'),
    }
    shapes = {'water': [(EDGE + 0.1, -1.1, 12), (EDGE + 0.1, -1.1, -45), (90, -1.1, -45), (90, -1.1, 12)],
              'vance': rect((VANCE[0], VANCE[1]), 0.36, 1.8),
              'bollard': [(BOLLARD[0] - 0.3, 0.0, BOLLARD[1]), (BOLLARD[0] + 0.3, 0.0, BOLLARD[1]),
                          (BOLLARD[0] + 0.3, 0.95, BOLLARD[1]), (BOLLARD[0] - 0.3, 0.95, BOLLARD[1])],
              'lincoln': [(lx - 2.75, 0.0, lz + 1.0), (lx + 2.75, 0.0, lz + 1.0), (lx + 2.75, 1.45, lz + 1.0),
                          (lx - 2.75, 1.45, lz + 1.0), (lx - 2.0, 1.45, lz - 1.0), (lx + 2.0, 1.45, lz - 1.0)]}
    order = ['crane', 'water', 'containers', 'warehouse_sign', 'lincoln', 'car', 'vance', 'radio', 'tiny', 'barrel',
             'piling', 'bollard']
    if time == 'dawn':
        hs['brenner'] = ('Brenner', (4.2, 4.15), 'left')
        hs['brenner_cuffed'] = ('Brenner', (-1.9, 0.75), 'left')
        shapes['brenner'] = rect(BRENNER, 0.36, 1.95)
        shapes['brenner_cuffed'] = [(HOOD[0] - 0.9, 0.0, HOOD[1]), (HOOD[0] + 0.4, 0.0, HOOD[1]),
                                    (HOOD[0] + 0.4, 1.5, HOOD[1]), (HOOD[0] - 0.9, 1.5, HOOD[1])]
        order += ['brenner_cuffed', 'brenner']
        overlays = ['brenner', 'brenner_gun', 'brenner_cuffed', 'bollard_phone', 'bollard_cup', 'lincoln']
        bases = {'brenner': BRENNER, 'brenner_gun': BRENNER, 'brenner_cuffed': HOOD}
        exclusive = ['brenner', 'brenner_gun', 'brenner_cuffed']
    else:
        for k, p in (('doyle', DOYLE), ('okafor', OKAFOR), ('mara', MARA)):
            hs[k] = ({'doyle': 'Lt. Doyle', 'okafor': 'Okafor', 'mara': 'Mara Quist'}[k], (-2.7, 2.6), 'left')
            shapes[k] = rect(p, 0.34, 1.75)
            order.append(k)
        overlays = ['doyle', 'okafor', 'mara']
        bases = {'doyle': DOYLE, 'okafor': OKAFOR, 'mara': MARA}
        exclusive = ['doyle', 'okafor', 'mara']
    return dict(
        room='pier9_' + time,
        walk=[(-3.0, -0.5), (4.5, -0.5), (4.5, 4.8), (-4.0, 4.8), (-4.0, 0.7), (-3.0, 0.7)],
        walk_zmin=-0.5, walk_zmax=4.8, scale_x=0.0,
        spawns={'drive': (-3.4, 2.6), 'night_lab': (-3.4, 2.6), 'pier9_dawn': (4.0, 4.1), 'start': (0.0, 2.0)},
        hotspots=hs,
        hotspot_shapes=shapes,
        hotspot_order=order,
        overlays=overlays,
        overlay_bases=bases,
        exclusive_overlays=exclusive,
        occluders={'barrel': (bx, bz)},
        obstacles=[(bx, bz, 0.45)],
        char_fill=((236, 210, 210), 0.1) if time == 'dawn' else ((255, 236, 210), 0.08),
        tint=(0.9, 0.82, 0.86) if time == 'dawn' else (1.0, 0.92, 0.84),
        exposure=1.2 if time == 'dawn' else 1.05,
    )
