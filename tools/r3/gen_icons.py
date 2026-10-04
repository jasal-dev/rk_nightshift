"""Inventory icons rendered from small 3D props, so they match the rooms. Writes assets/items/<id>.png (84x84)."""
import math, os, sys
import numpy as np
from PIL import Image, ImageFilter
from scene3d import Scene, Camera, WORLD, Rx, Ry, Rz, aces, Frame
import textures as tx

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
SIZE, SS = 84, 4


def scene():
    S = Scene()
    S.mat('brass', (210, 168, 70), spec=1.4, shin=60, namp=0.08, nscale=60)
    S.mat('manila', (214, 178, 112), namp=0.06, nscale=30)
    S.mat('paper', (236, 232, 214))
    S.mat('red', (170, 36, 32), spec=0.3)
    S.mat('mug', (226, 220, 206), spec=0.6, shin=50)
    S.mat('coffee', (40, 22, 14), spec=1.2, shin=90)
    S.mat('silver', (188, 190, 198), spec=1.6, shin=70, namp=0.05, nscale=80)
    S.mat('blue', (34, 70, 150), spec=0.3)
    S.mat('ink', (230, 236, 250))
    S.mat('match', (190, 160, 110)); S.mat('matchhead', (150, 30, 24))
    S.mat('wood', (130, 100, 66), namp=0.2, nscale=30)
    S.mat('steel', (170, 172, 178), spec=1.4, shin=60)
    S.mat('envelope', (210, 214, 226), namp=0.15, nscale=20)
    S.mat('singe', (60, 40, 28), namp=0.4, nscale=30)
    S.mat('leather', (60, 40, 30), spec=0.3, shin=30, namp=0.1, nscale=40)
    S.mat('elastic', (20, 20, 22))
    # Case 2
    S.mat('glide', (220, 220, 220), tex=tx.glide_card(), texmode=1, spec=0.4, shin=40)
    S.mat('teal', (30, 150, 134), spec=0.3)
    S.mat('ink_dk', (30, 34, 70))
    S.mat('dodger', (30, 70, 160), spec=0.5)
    S.mat('plastic', (24, 24, 28), spec=0.8, shin=60)
    S.mat('lens', (10, 12, 20), spec=1.6, shin=90)
    S.mat('clear', (200, 210, 220), spec=1.2, shin=80)
    S.mat('sdcard', (40, 80, 160), spec=0.5)
    S.mat('peas', (110, 170, 70), spec=0.5, shin=40, namp=0.15, nscale=40)
    S.mat('tape', (220, 210, 170), spec=0.4)
    S.mat('screen_on', (20, 120, 110), emis=(40, 210, 180), emis_mult=1.2)
    # Case 3
    S.mat('gold', (226, 176, 64), spec=1.8, shin=80, namp=0.05, nscale=60)
    S.mat('gold_dk', (150, 110, 40), spec=1.2, shin=60)
    S.mat('uv', (150, 80, 255), emis=(150, 70, 255), emis_mult=1.6)
    S.mat('masking', (222, 206, 156))
    S.mat('catalogue', (20, 20, 24), tex=tx.catalogue_cover(), texmode=1, spec=1.0, shin=60)
    S.mat('brenner', (236, 228, 206), tex=tx.brenner_card(), texmode=1, spec=0.2)
    S.mat('water', (120, 160, 200), spec=1.6, shin=90)
    return S


def build(item):
    S = scene()
    if item == 'key':
        S.fcyl((-0.28, 0, 0.02), 0.14, 0.02, 'brass', axis='z')
        S.fcyl((-0.28, 0, 0.02), 0.06, 0.1, 'brass', axis='z', op=1)
        S.wbox((0.08, 0, 0.02), (0.24, 0.035, 0.02), 'brass')
        for x, h in ((0.2, 0.07), (0.27, 0.05), (0.13, 0.06)):
            S.wbox((x, -0.04 - h / 2, 0.02), (0.025, h / 2, 0.02), 'brass')
        rot = Rz(25)
    elif item == 'case_file':
        S.wbox((0, 0, 0), (0.36, 0.26, 0.02), 'manila', rnd=0.01)
        S.wbox((-0.2, 0.28, 0), (0.12, 0.03, 0.02), 'manila', rnd=0.01)
        S.wbox((0.02, 0.02, 0.025), (0.3, 0.2, 0.005), 'paper')
        S.wbox((0.22, -0.16, 0.035), (0.09, 0.03, 0.006), 'red')
        rot = Rz(-6) @ Rx(-20)
    elif item == 'coffee':
        S.fcyl((0, 0, 0), 0.2, 0.22, 'mug')
        S.fcyl((0, 0.2, 0), 0.17, 0.06, 'mug', op=1)
        S.fcyl((0, 0.13, 0), 0.17, 0.01, 'coffee')
        S.fcyl((0, -0.02, 0), 0.204, 0.04, 'red')
        S.ell(WORLD, (0.24, 0.0, 0), (0.08, 0.13, 0.035), 'mug')
        S.ell(WORLD, (0.24, 0.0, 0), (0.045, 0.085, 0.06), 'mug', op=1)
        rot = Rx(-22) @ Ry(-25)
    elif item == 'dime':
        S.fcyl((0, 0, 0), 0.22, 0.02, 'silver', axis='z')
        S.fcyl((0, 0, 0.02), 0.18, 0.006, 'silver', axis='z', op=1)
        S.ell(WORLD, (-0.02, 0.02, 0.018), (0.07, 0.09, 0.01), 'silver')
        rot = Rx(-30) @ Ry(20)
    elif item == 'matchbook':
        S.wbox((0, 0, 0), (0.22, 0.32, 0.03), 'blue', rnd=0.01)
        S.wbox((0, -0.22, 0.034), (0.2, 0.05, 0.006), 'match')
        S.wbox((0.02, 0.08, 0.034), (0.13, 0.1, 0.004), 'ink')
        rot = Rz(12) @ Rx(-15)
    elif item == 'gaff':
        S.cyl((-0.4, -0.38, 0), (0.28, 0.3, 0), 0.03, 'wood')
        S.cyl((0.28, 0.3, 0), (0.38, 0.4, 0), 0.022, 'steel')
        S.cone((0.33, 0.35, 0), (0.42, 0.24, 0), 0.02, 0.008, 'steel')
        rot = Rx(-10)
    elif item == 'envelope':
        S.wbox((0, 0, 0), (0.36, 0.22, 0.012), 'envelope', rnd=0.005)
        S.wbox((0, 0.1, 0.016), (0.3, 0.1, 0.004), 'envelope', rot=Rx(-6))
        S.wbox((0.06, -0.02, 0.016), (0.18, 0.025, 0.003), 'blue')          # "1 of 3" on the back
        S.ell(WORLD, (0.33, 0.19, 0.012), (0.09, 0.07, 0.004), 'singe')     # singed corner
        rot = Rz(-8) @ Rx(-18)
    elif item == 'notebook':
        S.wbox((0, 0, 0), (0.24, 0.33, 0.04), 'leather', rnd=0.02)
        S.wbox((0.02, 0, -0.008), (0.23, 0.31, 0.026), 'paper')
        S.wbox((0.16, 0, 0.042), (0.012, 0.335, 0.006), 'elastic')
        rot = Rz(-10) @ Rx(-20)
    elif item == 'driver_card':
        S.wbox((0, 0, 0), (0.36, 0.23, 0.012), 'glide', rnd=0.01)
        rot = Rz(-8) @ Rx(-20)
    elif item == 'norms_receipt':
        S.wbox((0, 0, 0), (0.16, 0.36, 0.006), 'paper', rnd=0.003)
        S.wbox((0, 0.29, 0.008), (0.12, 0.035, 0.003), 'red')
        for k in range(6):
            S.wbox((-0.02 + (k % 2) * 0.03, 0.17 - k * 0.075, 0.008), (0.1 - (k % 2) * 0.03, 0.012, 0.002), 'ink_dk')
        rot = Rz(12) @ Rx(-20)
    elif item == 'kenji_keys':
        for k in range(14):
            a0, a1 = k / 14 * 2 * math.pi, (k + 1) / 14 * 2 * math.pi
            S.cyl((0.13 * math.cos(a0) - 0.15, 0.13 * math.sin(a0) + 0.15, 0),
                  (0.13 * math.cos(a1) - 0.15, 0.13 * math.sin(a1) + 0.15, 0), 0.014, 'steel')
        S.wbox((0.1, -0.05, 0), (0.08, 0.11, 0.035), 'plastic', rnd=0.03, rot=Rz(-40))           # the car fob
        S.wbox((-0.2, -0.16, 0), (0.035, 0.15, 0.01), 'brass', rot=Rz(10))                     # house key
        S.fcyl((-0.23, 0.02, 0), 0.06, 0.012, 'brass', axis='z')
        S.cone((0.06, 0.2, 0), (0.34, 0.36, 0), 0.025, 0.045, 'dodger')                       # little plastic bat
        rot = Rx(-20)
    elif item == 'card_slip':
        S.wbox((0, 0, 0), (0.24, 0.34, 0.006), 'paper', rnd=0.003)
        for k in range(4):
            S.wbox((-0.04, 0.22 - k * 0.07, 0.008), (0.15, 0.01, 0.002), 'ink_dk')
        pts = [(-0.16, -0.16), (-0.1, -0.08), (-0.05, -0.2), (0.0, -0.09), (0.05, -0.21), (0.1, -0.1), (0.16, -0.18)]
        for a, b in zip(pts, pts[1:]):
            S.cyl((a[0], a[1], 0.01), (b[0], b[1], 0.01), 0.008, 'ink_dk')
        rot = Rz(-10) @ Rx(-20)
    elif item == 'frozen_peas':
        S.ell(WORLD, (0, 0, 0), (0.3, 0.36, 0.08), 'peas', k=0.05)
        S.ell(WORLD, (0, 0.33, 0), (0.24, 0.06, 0.04), 'peas')
        S.wbox((0, 0.02, 0.07), (0.14, 0.1, 0.012), 'paper', rot=Rx(-5))
        S.wbox((0, 0.2, 0.0), (0.33, 0.035, 0.09), 'tape')
        rot = Rz(10) @ Rx(-20)
    elif item == 'sd_cards':
        S.wbox((-0.12, 0.12, 0), (0.2, 0.1, 0.07), 'plastic', rnd=0.03)                         # the dashcam
        S.fcyl((-0.2, 0.12, 0.08), 0.055, 0.02, 'lens', axis='z')
        S.fcyl((-0.04, 0.12, 0.08), 0.045, 0.02, 'lens', axis='z')
        S.wbox((0.1, -0.16, 0), (0.24, 0.13, 0.03), 'clear', rnd=0.02)                         # the card case
        for k in range(5):
            S.wbox((-0.06 + k * 0.08, -0.16, 0.035), (0.028, 0.04, 0.004), 'sdcard')
        rot = Rz(-6) @ Rx(-24)
    elif item == 'ride_receipt':
        S.wbox((0, 0, 0), (0.2, 0.38, 0.025), 'plastic', rnd=0.04)
        S.wbox((0, 0.0, 0.026), (0.17, 0.33, 0.003), 'screen_on')
        S.wbox((0, 0.24, 0.03), (0.13, 0.03, 0.002), 'teal')
        for k in range(4):
            S.wbox((-0.02, 0.12 - k * 0.09, 0.03), (0.11, 0.015, 0.002), 'ink')
        rot = Rz(-12) @ Rx(-18)
    elif item == 'gus_keys':
        for k in range(16):                                                                  # the ring
            a0, a1 = k / 16 * 2 * math.pi, (k + 1) / 16 * 2 * math.pi
            S.cyl((0.12 * math.cos(a0) - 0.12, 0.12 * math.sin(a0) + 0.18, 0),
                  (0.12 * math.cos(a1) - 0.12, 0.12 * math.sin(a1) + 0.18, 0), 0.013, 'steel')
        for ang, m, ln in ((-60, 'brass', 0.32), (-95, 'steel', 0.36), (-130, 'brass', 0.2)):
            a = math.radians(ang)
            c = (-0.12 + 0.12 * math.cos(a), 0.18 + 0.12 * math.sin(a))
            R = Rz(ang + 90)
            fr = Frame((c[0], c[1], 0), R)
            S.fcyl(fr.to((0, -0.05, 0)), 0.05, 0.012, m, axis='z')
            S.box(fr, (0, -0.05 - ln / 2, 0), (0.022, ln / 2, 0.012), 0.004, m)
            S.box(fr, (0.025, -0.05 - ln * 0.8, 0), (0.012, 0.03, 0.012), 0.003, m)
        rot = Rx(-20)
    elif item == 'uv_lamp':
        S.wbox((0, 0, 0), (0.12, 0.38, 0.06), 'plastic', rnd=0.04)                           # handheld body
        S.wbox((0, 0.12, 0.062), (0.07, 0.2, 0.004), 'uv')                                    # the violet tube
        S.wbox((0, -0.22, 0.065), (0.13, 0.05, 0.004), 'masking', rot=Rz(4))                  # Gus's tape note
        for k in range(3):
            S.wbox((-0.05 + k * 0.05, -0.22, 0.07), (0.018, 0.012, 0.002), 'ink_dk')
        rot = Rz(-28) @ Rx(-20)
    elif item == 'catalogue':
        S.wbox((0, 0, 0), (0.28, 0.37, 0.03), 'catalogue', rnd=0.01)
        S.wbox((0.0, 0.0, -0.005), (0.27, 0.36, 0.026), 'paper')
        S.wbox((0.25, 0.3, 0.032), (0.04, 0.06, 0.002), 'paper', rot=Rz(45))                  # a corner turned down
        rot = Rz(8) @ Rx(-20)
    elif item == 'star_earring':
        for k in range(5):
            t = math.radians(k * 72)
            S.cone((0, 0, 0), (0.3 * math.sin(t), 0.3 * math.cos(t), 0), 0.1, 0.02, 'gold')
        S.sph((0, 0, 0.02), 0.09, 'gold')
        S.cyl((0.0, -0.05, -0.04), (0.16, -0.32, -0.08), 0.018, 'gold_dk')                    # the post, bent back
        rot = Rz(10) @ Rx(-15)
    elif item == 'fake_oscar':
        S.fcyl((0, -0.34, 0), 0.13, 0.06, 'gold_dk')                                          # the base
        S.fcyl((0, -0.25, 0), 0.08, 0.03, 'gold')
        S.cone((0, -0.22, 0), (0, 0.14, 0), 0.04, 0.065, 'gold', k=0.02)                    # a slim gold figure
        S.ell(WORLD, (0, 0.17, 0), (0.07, 0.06, 0.05), 'gold', k=0.02)
        S.sph((0, 0.27, 0), 0.045, 'gold', k=0.01)
        S.cone((0.0, 0.1, 0.03), (0.0, -0.08, 0.05), 0.02, 0.015, 'gold')                    # arms folded on a sword
        S.sph((0.08, -0.05, 0.08), 0.025, 'water')                                            # still dripping
        S.sph((-0.06, -0.3, 0.12), 0.02, 'water')
        rot = Ry(-20) @ Rx(-8)
    elif item == 'brenner_card':
        S.wbox((0, 0, 0), (0.37, 0.22, 0.008), 'brenner', rnd=0.005)
        rot = Rz(-6) @ Rx(-22)
    S.transform(rot)
    S.light((-1.2, 1.6, 2.0), (255, 236, 210), power=7, range=10, soft=8)
    S.light((1.4, 0.6, -1.0), (140, 180, 255), power=4, range=10, shadow=False)
    S.light((1.0, -0.6, 2.0), (120, 120, 150), power=1.2, range=10, shadow=False)
    return S


def main():
    for item in (sys.argv[1:] or ('key', 'case_file', 'coffee', 'dime', 'matchbook', 'gaff', 'envelope', 'notebook',
                                  'driver_card', 'norms_receipt', 'kenji_keys', 'card_slip', 'frozen_peas', 'sd_cards',
                                  'ride_receipt', 'gus_keys', 'uv_lamp', 'catalogue', 'star_earring', 'fake_oscar',
                                  'brenner_card')):
        S = build(item)
        cam = Camera((0, 0, 5), (0, 0, 0), W=SIZE * SS, H=SIZE * SS, ortho=True, ortho_h=0.95)
        env = dict(sky=(60, 60, 70), bounce=(30, 26, 26), fog=0, reflections=False, vol_scale=0, grid=0.12, ao_scale=0.3)
        surf, _, _ = S.render(cam, env, 'icon')
        s = surf.reshape(SIZE, SS, SIZE, SS, 4)
        a = s[..., 3].mean(axis=(1, 3))
        rgb = (s[..., :3] * s[..., 3:4]).sum(axis=(1, 3)) / np.maximum(s[..., 3].sum(axis=(1, 3))[..., None], 1e-6)
        rgb = aces(rgb * 1.4) ** (1 / 2.2)
        im = np.zeros((SIZE, SIZE, 4), np.uint8)
        im[..., :3] = (rgb * 255).clip(0, 255); im[..., 3] = (a * 255).clip(0, 255)
        icon = Image.fromarray(im, 'RGBA')
        # soft dark halo so icons read on any background
        halo = icon.split()[3].filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(2))
        out = Image.new('RGBA', icon.size, (0, 0, 0, 0))
        out.paste((8, 6, 10, 255), (0, 0), halo.point(lambda v: int(v * 0.7)))
        out.alpha_composite(icon)
        out.save(os.path.join(ROOT, 'assets', 'items', f'{item}.png'))
        print(item)


if __name__ == '__main__':
    main()
