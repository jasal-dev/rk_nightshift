"""Vance's office: a pair of shipping containers inside the salvage warehouse, fitted out with a desk, a space heater,
a green banker's lamp and a wall of IOUs. Vance sits behind the desk and does not get up."""
import math, random
import numpy as np
from scene3d import *
import textures as tx
import npc


def build(hide=()):
    S = Scene()
    rng = random.Random(31)
    # ---------------------------------------------------------------- materials
    S.mat('wall', (255, 255, 255), tex=tx.hires(tx.corrugated(seed=81, base=(132, 120, 96), ribs=14, rust=0.25), 2),
          texmode=4, texmap=1, texscale=1.6, spec=0.3, shin=30)
    S.mat('ceiling', (255, 255, 255), tex=tx.corrugated(seed=82, base=(90, 86, 76), ribs=10, rust=0.2), texmode=4,
          texmap=1, texscale=1.6)
    S.mat('floor', (96, 74, 56), namp=0.3, nscale=6, spec=0.2, shin=20)
    S.mat('rug', (110, 40, 34), namp=0.35, nscale=14)
    S.mat('rug_edge', (170, 140, 90), namp=0.2, nscale=14)
    S.mat('door', (70, 76, 80), spec=0.5, shin=30, namp=0.15, nscale=6)
    S.mat('door_glass', (30, 30, 30), emis=(180, 140, 90), emis_mult=0.6)
    S.mat('steel', (140, 140, 144), spec=0.9, shin=50)
    S.mat('cork', (200, 200, 200), tex=tx.hires(tx.markers_wall(), 2), texmode=1, spec=0.1)
    S.mat('frame', (60, 40, 24), spec=0.4, shin=30)
    S.mat('photo', (200, 200, 200), tex=tx.hires(tx.boat_photo(), 2), texmode=1, spec=0.6, shin=60)
    S.mat('desk', (74, 46, 30), namp=0.15, nscale=6, spec=0.45, shin=40)
    S.mat('blotter', (30, 60, 44), spec=0.2)
    S.mat('lamp_shade', (40, 110, 76), spec=0.9, shin=60)
    S.mat('brass', (176, 140, 60), spec=1.2, shin=50)
    S.mat('bulb', (255, 220, 160), emis=(255, 210, 150), emis_mult=5)
    S.mat('gun', (34, 34, 38), spec=1.2, shin=70)
    S.mat('grip', (70, 46, 30), spec=0.4)
    S.mat('china', (226, 222, 210), spec=0.7, shin=60)
    S.mat('tea', (150, 110, 40), spec=1.0, shin=90)
    S.mat('ledger', (200, 200, 200), tex=tx.ledger_cover(), texmode=1, spec=0.3)
    S.mat('paper', (226, 222, 206))
    S.mat('leather', (36, 26, 22), spec=0.5, shin=40, namp=0.1, nscale=20)
    S.mat('chair_wood', (88, 62, 40), namp=0.2, nscale=8, spec=0.3)
    S.mat('heater', (60, 58, 56), spec=0.5, shin=30)
    S.mat('coil', (255, 120, 40), emis=(255, 110, 30), emis_mult=4)
    S.mat('fixture', (50, 52, 54))
    S.mat('tube', (230, 240, 236), emis=(200, 225, 220), emis_mult=1.2)
    S.mat('safe', (52, 58, 52), spec=0.6, shin=40)
    S.mat('kettle', (150, 150, 150), spec=1.2, shin=60)

    X0, X1, ZB, H = -5.0, 5.0, -2.4, 2.7
    # ---------------------------------------------------------------- the box
    S.wboxr(X0 - 1, -0.3, ZB - 1, X1 + 1, 0.0, 8, 'floor')
    S.wboxr(X0 - 0.2, 0, ZB - 0.2, X1 + 0.2, H, ZB, 'wall')               # back wall
    S.wboxr(X0 - 0.2, 0, ZB, X0, H, 4, 'wall')                            # left wall
    S.wboxr(X1, 0, ZB, X1 + 0.2, H, 4, 'wall')                            # right wall
    S.wboxr(X0 - 0.2, H, ZB - 0.2, X1 + 0.2, H + 0.2, 4, 'ceiling')
    S.wboxr(-0.15, 0, ZB, 0.15, H, ZB + 0.12, 'door')                     # seam where the two boxes were welded
    S.wboxr(-3.0, 0.0, -2.0, 4.2, 0.012, 1.4, 'rug_edge')
    S.wboxr(-2.85, 0.0, -1.85, 4.05, 0.016, 1.25, 'rug')

    # ---------------------------------------------------------------- door back to the warehouse
    with S.tag('door'):
        S.wboxr(-4.45, 0, ZB - 0.05, -3.25, 2.15, ZB + 0.06, 'door')
        S.wboxr(-4.1, 1.45, ZB + 0.06, -3.6, 1.85, ZB + 0.07, 'door_glass')
        S.wboxr(-3.45, 0.95, ZB + 0.06, -3.35, 1.1, ZB + 0.14, 'steel')

    # ---------------------------------------------------------------- wall of markers, boat photo
    with S.tag('markers'):
        S.wboxr(-2.8, 0.82, ZB, -0.35, 2.08, ZB + 0.04, 'frame')
        S.wboxr(-2.75, 0.86, ZB + 0.04, -0.4, 2.04, ZB + 0.05, 'cork')
    with S.tag('boat_photo'):
        S.wboxr(0.35, 1.4, ZB, 1.0, 1.9, ZB + 0.04, 'frame')
        S.wboxr(0.4, 1.44, ZB + 0.04, 0.95, 1.86, ZB + 0.05, 'photo')

    # a squat safe and an old filing cabinet in the corner
    S.wboxr(4.0, 0, ZB + 0.05, 4.85, 1.0, ZB + 0.8, 'safe', rnd=0.03)
    S.sph((4.4, 0.6, ZB + 0.82), 0.06, 'steel')
    S.wboxr(-4.85, 0, -1.6, -4.25, 1.35, -0.9, 'door', rnd=0.01)

    # ---------------------------------------------------------------- Vance and his desk
    vx, vz = 2.0, -2.0
    # high-backed leather chair behind him
    S.wboxr(vx - 0.32, 0.4, vz - 0.3, vx + 0.32, 0.5, vz + 0.25, 'leather', rnd=0.04)
    S.wboxr(vx - 0.32, 0.5, vz - 0.32, vx + 0.32, 1.45, vz - 0.2, 'leather', rnd=0.06)
    npc.place(S, 'vance', dict(npc.SEATED, yaw=0, lsp=46, le=68, lin=34, rsp=44, re=70, rin=36, hp=-3, hy=8,
                               coatlen=0.06, lean=6),
              (vx, -0.02, vz + 0.05), yaw=0, scale=0.98, tag='vance',
              colors=dict(coat=(104, 96, 118), coat_dk=(80, 74, 92), lining=(90, 84, 100), shirt=(196, 194, 186),
                          pants=(44, 44, 50), hair=(190, 188, 184), hairgrey=(214, 212, 208), brow=(170, 168, 164),
                          stubble=(166, 124, 104), skin=(170, 128, 106), skin_dk=(140, 102, 86)))
    dx0, dx1, dz0, dz1 = 0.9, 3.1, -1.55, -0.65
    S.wboxr(dx0, 0.72, dz0, dx1, 0.78, dz1, 'desk')
    S.wboxr(dx0 + 0.05, 0.02, dz1 - 0.06, dx1 - 0.05, 0.72, dz1 - 0.02, 'desk')            # modesty panel
    S.wboxr(dx0 + 0.05, 0.0, dz0 + 0.05, dx0 + 0.6, 0.72, dz1 - 0.05, 'desk')               # drawers
    S.wboxr(dx1 - 0.6, 0.0, dz0 + 0.05, dx1 - 0.05, 0.72, dz1 - 0.05, 'desk')
    for y in (0.2, 0.42, 0.62):
        S.wboxr(dx0 + 0.25, y, dz1 - 0.02, dx0 + 0.4, y + 0.025, dz1, 'brass')
        S.wboxr(dx1 - 0.4, y, dz1 - 0.02, dx1 - 0.25, y + 0.025, dz1, 'brass')
    S.wboxr(1.3, 0.78, -1.35, 2.7, 0.79, -0.8, 'blotter')
    with S.tag('lamp'):
        lx, lz = 2.8, -1.3
        S.cyl((lx, 0.78, lz), (lx, 0.81, lz), 0.11, 'brass')
        S.cyl((lx, 0.81, lz), (lx, 1.08, lz), 0.014, 'brass')
        S.ell(WORLD, (lx - 0.04, 1.12, lz + 0.04), (0.19, 0.065, 0.095), 'lamp_shade', rot=Ry(30))
        S.ell(WORLD, (lx - 0.04, 1.07, lz + 0.04), (0.11, 0.02, 0.05), 'bulb', rot=Ry(30))
    with S.tag('gun'):
        gx, gz = 1.6, -0.98
        S.wbox((gx, 0.805, gz), (0.11, 0.018, 0.016), 'gun', rot=Ry(18))
        S.wbox((gx - 0.1, 0.8, gz + 0.04), (0.03, 0.014, 0.05), 'grip', rot=Ry(18))
    with S.tag('tea'):
        cx, cz = 1.22, -1.05
        S.cyl((cx, 0.78, cz), (cx, 0.79, cz), 0.07, 'china')
        S.cyl((cx, 0.79, cz), (cx, 0.87, cz), 0.04, 'china')
        S.cyl((cx, 0.862, cz), (cx, 0.866, cz), 0.034, 'tea')
    with S.tag('ledger'):
        S.wbox((2.3, 0.81, -1.0), (0.17, 0.025, 0.12), 'ledger', rot=Ry(-8))
        S.wbox((2.31, 0.81, -1.0), (0.16, 0.02, 0.115), 'paper', rot=Ry(-8))
    # papers
    for k in range(3):
        S.wbox((1.85 + k * 0.05, 0.795 + k * 0.004, -1.15), (0.1, 0.002, 0.14), 'paper', rot=Ry(rng.uniform(-15, 15)))

    # ---------------------------------------------------------------- the hard chair for visitors
    if 'chair' not in hide:
        with S.tag('chair'):
            hx, hz = 1.0, -0.15
            S.wboxr(hx - 0.22, 0.43, hz - 0.2, hx + 0.22, 0.47, hz + 0.2, 'chair_wood')
            S.wboxr(hx - 0.22, 0.47, hz + 0.16, hx + 0.22, 0.95, hz + 0.2, 'chair_wood')
            for sx in (-1, 1):
                for sz in (-1, 1):
                    S.cyl((hx + sx * 0.19, 0, hz + sz * 0.17), (hx + sx * 0.19, 0.43, hz + sz * 0.17), 0.018, 'chair_wood')

    # ---------------------------------------------------------------- space heater, kettle
    with S.tag('heater'):
        hx2, hz2 = 3.55, -1.95
        S.wboxr(hx2 - 0.25, 0.05, hz2 - 0.12, hx2 + 0.25, 0.62, hz2 + 0.12, 'heater', rnd=0.03)
        for y in (0.18, 0.3, 0.42, 0.54):
            S.cyl((hx2 - 0.18, y, hz2 + 0.13), (hx2 + 0.18, y, hz2 + 0.13), 0.018, 'coil')
        S.wboxr(hx2 - 0.2, 0.0, hz2 - 0.15, hx2 + 0.2, 0.05, hz2 + 0.15, 'heater')
    S.cyl((4.4, 1.0, ZB + 0.45), (4.4, 1.18, ZB + 0.45), 0.09, 'kettle')

    # ---------------------------------------------------------------- ceiling tube
    S.wboxr(-2.0, H - 0.08, -0.9, 0.6, H, -0.7, 'fixture')
    S.wboxr(-1.95, H - 0.11, -0.86, 0.55, H - 0.08, -0.74, 'tube')

    # ---------------------------------------------------------------- lights
    S.light((2.76, 1.04, -1.26), (255, 196, 120), power=6, range=6, soft=10, vol=0.4, spot=((0.0, -1, 0.15), 50, 82))
    S.light((2.76, 1.2, -1.26), (255, 190, 120), power=0.8, range=6, shadow=False, vol=0.1)
    S.light((3.55, 0.4, -1.65), (255, 110, 40), power=3.0, range=4.5, vol=0.25, soft=10)
    S.light((-0.7, H - 0.2, -0.8), (200, 225, 220), power=2.4, range=7, vol=0.15, soft=12, spot=((0, -1, 0.1), 60, 88))
    S.light((-3.85, 1.65, ZB + 0.3), (255, 170, 110), power=0.5, range=3, shadow=False)
    S.light((1.7, 1.55, -0.85), (255, 200, 150), power=0.9, range=2.2, shadow=False)          # lamp bounce on Vance
    S.light((0.0, 2.0, 5.0), (120, 130, 170), power=1.2, range=12, shadow=False)            # spill from the warehouse

    cam = Camera((0.3, 2.2, 5.9), (0.4, 1.05, -1.2), fov=40, W=3840, H=2160)
    env = dict(sky=(26, 26, 32), bounce=(26, 20, 16), fog_col=(26, 22, 20), fog=0.04, fog_h0=0.0, fog_hf=0.05,
               fog_max=40, vol_scale=4, vol_steps=40, reflections=False, grid=0.5, ao_scale=0.8)
    meta = dict(
        room='vance_office',
        walk=[(-4.6, -1.95), (-3.0, -1.95), (-3.0, -0.45), (4.4, -0.45), (4.4, 1.7), (-4.6, 1.7)],
        walk_zmin=-1.95, walk_zmax=1.7, scale_x=-1.0,
        spawns={'pier9_dock': (-3.85, -1.75), 'start': (0.0, 1.0)},
        hotspots={
            'vance': ('Vance', (2.15, -0.2), 'up'),
            'markers': ('wall of IOUs', (-1.55, -0.6), 'up'),
            'gun': ('.45 on the desk', (1.75, -0.25), 'up'),
            'tea': ('tea cup', (1.45, -0.3), 'up'),
            'ledger': ('ledger', (2.5, -0.2), 'up'),
            'boat_photo': ('photo', None, 'up'),
            'lamp': ('desk lamp', (2.9, -0.2), 'up'),
            'heater': ('space heater', (3.6, -0.55), 'up'),
            'door': ('door', (-3.85, -1.85), 'up'),
        },
        hotspot_shapes={'vance': [(vx - 0.33, 0.78, vz + 0.2), (vx + 0.33, 0.78, vz + 0.2),
                                  (vx + 0.33, 1.5, vz + 0.2), (vx - 0.33, 1.5, vz + 0.2)]},
        hotspot_order=['markers', 'boat_photo', 'door', 'heater', 'vance', 'lamp', 'ledger', 'tea', 'gun'],
        occluders={'chair': (1.0, 0.05)},
        obstacles=[(1.0, -0.15, 0.32)],
        char_fill=((236, 214, 190), 0.25),
        tint=(0.86, 0.76, 0.66),
        exposure=1.4,
    )
    return S, cam, env, meta
