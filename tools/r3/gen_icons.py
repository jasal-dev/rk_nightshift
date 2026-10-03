"""Inventory icons rendered from small 3D props, so they match the rooms. Writes assets/items/<id>.png (84x84)."""
import math, os, sys
import numpy as np
from PIL import Image, ImageFilter
from scene3d import Scene, Camera, WORLD, Rx, Ry, Rz, aces, Frame

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
    S.transform(rot)
    S.light((-1.2, 1.6, 2.0), (255, 236, 210), power=7, range=10, soft=8)
    S.light((1.4, 0.6, -1.0), (140, 180, 255), power=4, range=10, shadow=False)
    S.light((1.0, -0.6, 2.0), (120, 120, 150), power=1.2, range=10, shadow=False)
    return S


def main():
    for item in (sys.argv[1:] or ('key', 'case_file', 'coffee', 'dime', 'matchbook', 'gaff', 'envelope', 'notebook')):
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
