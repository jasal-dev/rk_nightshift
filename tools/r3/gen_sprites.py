"""Render the detective's relightable animation sheets for the game.
python gen_sprites.py [--only walk_right,...] [--preview]
Writes assets/characters/detective.png, detective_light.png and scripts/detective_anims.gd"""
import argparse, math, os, sys, time
import numpy as np
from PIL import Image
import detective
from scene3d import Camera, Rx, Ry, composite, srgb

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
FW, FH = 240, 372
PIVOT = (120, 360)
SPRITE_PX = 312           # 1.83 m tall figure -> pixels at 1920x1080 (keep in sync with render_room.py)
PX_PER_M = SPRITE_PX / 1.83
SS = 2
PITCH = 9


def g(x, c, w):  # wrapped gaussian bump on [0,1)
    d = (x - c + 0.5) % 1.0 - 0.5
    return math.exp(-d * d / (2 * w * w))

def walk_pose(i, n, yaw):
    p = i / n
    out = dict(yaw=yaw, lean=4)
    for k, ph in (('l', p), ('r', (p + 0.5) % 1)):
        a = 2 * math.pi * ph
        out[k + 'hp'] = 25 * math.sin(a)
        out[k + 'k'] = 5 + 42 * max(0.0, math.cos(a)) ** 1.3
        out[k + 'fp'] = 14 * g(ph, 0.25, 0.05) - 34 * g(ph, 0.84, 0.06) + 4 * g(ph, 0.05, 0.06)
    aL = 2 * math.pi * p
    out['lsp'] = -20 * math.sin(aL); out['rsp'] = 20 * math.sin(aL)
    out['le'] = 12 + 14 * max(0, -math.sin(aL)); out['re'] = 12 + 14 * max(0, math.sin(aL))
    out['pyaw'] = -6 * math.sin(aL); out['cyaw'] = 10 * math.sin(aL)
    out['hy'] = -(out['pyaw'] + out['cyaw'])
    out['dx'] = -0.014 * math.cos(aL)
    out['sway'] = 1.5 * math.cos(aL)
    return out

def idle(yaw, n=8):
    fr = []
    for i in range(n):
        b = (1 - math.cos(2 * math.pi * i / n)) / 2
        fr.append(dict(yaw=yaw, breath=0.006 * b, shrug=0.15 * b, hp=-1 * b,
                       blink={5: 1.0, 6: 0.4}.get(i, 0)))
    return fr

GEST = dict(rsp=22, re=78, rin=18, rhand='open', rroll=50)
def talk(yaw):
    seq = [(0.7, 6, 72, 2), (0.2, 12, 88, -1), (0.9, 4, 64, 3), (0.3, 10, 82, 0), (0.6, 6, 70, 2), (0.0, 8, 76, 0)]
    return [dict(yaw=yaw, mouth=m, rsp=sp, re=e, rin=26, rsa=12, rhand='open', rroll=40, hp=h) for m, sp, e, h in seq]

def pickup():
    st = dict(yaw=90)
    mid = dict(yaw=90, lean=18, rhp=32, rk=52, lhp=-4, lk=36, lfp=-8, rsp=24, re=24, hp=8)
    low = dict(yaw=90, lean=36, rhp=82, rk=122, lhp=22, lk=118, lfp=-38, rfp=0, rsp=56, re=10,
               rhand='open', hp=16, lsp=20, le=30)
    return [st, mid, low, {**low, 'rhand': 'hold', 'props': (('box', 'r'),)},
            {**mid, 'rsp': 24, 're': 62, 'rhand': 'hold', 'props': (('box', 'r'),)},
            dict(yaw=90, rsp=10, re=96, rin=12, rhand='hold', props=(('box', 'r'),)),
            dict(yaw=90, rsp=10, re=98, rin=12, rhand='hold', props=(('box', 'r'),), hp=14)]

def use():
    return [dict(yaw=90), dict(yaw=90, rsp=40, re=40, lean=2),
            dict(yaw=90, rsp=74, re=14, rhand='open', lean=4, rhp=6, lhp=-2),
            dict(yaw=90, rsp=78, re=18, rw=-22, rhand='open', lean=5, rhp=6, lhp=-2),
            dict(yaw=90, rsp=74, re=14, rhand='open', lean=4, rhp=6, lhp=-2)]

def notebook():
    nb = (('notebook', 'r'),)
    a = dict(yaw=90, rsp=16, re=112, rin=45, hp=6)
    b = dict(yaw=90, rsp=22, re=96, rin=26, rhand='hold', props=nb, hp=18)
    w = dict(b, lsp=26, le=102, lin=36, lhand='hold', props=nb + (('pen', 'l'),))
    return [dict(yaw=90), a, b, w, dict(w, lw=10, lin=33), dict(w, lw=-6, lin=39), dict(w, lw=12, lin=35), b, a]

def look_around():
    return [dict(yaw=0, hy=h, hp=-2 if h else 0) for h in (0, -22, -40, -22, 0, 22, 40, 22)]

def shrug():
    s = lambda t: dict(yaw=0, shrug=t, lsa=8 + 5 * t, rsa=8 + 5 * t, le=12 + 66 * t, re=12 + 66 * t,
                       lin=-26 * t, rin=-26 * t, lsp=16 * t, rsp=16 * t,
                       lhand='open' if t > 0.3 else 'relaxed', rhand='open' if t > 0.3 else 'relaxed',
                       lroll=-70 * t, rroll=-70 * t, hp=7 * t, mouth=0.15 * t)
    return [s(0), s(0.45), s(0.85), s(1.0), s(1.0), s(0.5)]

def badge():
    bd = (('badge', 'r'),)
    return [dict(yaw=0), dict(yaw=0, rsp=14, re=108, rin=48),
            dict(yaw=0, rsp=30, re=100, rin=30, rhand='hold', props=bd),
            dict(yaw=0, rsp=46, re=92, rin=24, rhand='hold', props=bd),
            dict(yaw=0, rsp=46, re=92, rin=24, rhand='hold', props=bd, mouth=0.5),
            dict(yaw=0, rsp=46, re=92, rin=24, rhand='hold', props=bd)]

ANIMS = [
    ('idle_right', idle(90), 6, True),
    ('walk_right', [walk_pose(i, 12, 90) for i in range(12)], 12, True),
    ('idle_down', idle(0), 6, True),
    ('walk_down', [walk_pose(i, 12, 0) for i in range(12)], 12, True),
    ('idle_up', idle(180), 6, True),
    ('walk_up', [walk_pose(i, 12, 180) for i in range(12)], 12, True),
    ('talk_right', talk(90), 8, True),
    ('talk_down', talk(0), 8, True),
    ('pickup_right', pickup(), 8, False),
    ('use_right', use(), 8, False),
    ('notebook_right', notebook(), 6, False),
    ('look_around', look_around(), 4, True),
    ('shrug', shrug(), 8, False),
    ('show_badge', badge(), 6, False),
]



# Relightable sprites. Each frame is rendered as
#   albedo  : surface colour x ambient occlusion, no lights          -> detective.png (RGBA)
#   shading : white figure lit by one directional light per channel  -> detective_light.png (RGB, A = coverage)
# The game mixes the three shading channels with the room's lights at the detective's position (see
# light_probes.py and shaders/relight.gdshader), so he takes on the light and fog of wherever he stands.
# Light directions in view space (x right, y up, z toward the viewer). Must match light_probes.BASIS.
BASIS = [(-0.75, 0.5, 0.45), (0.75, 0.5, 0.45), (0.0, 0.7, -0.7)]    # left key, right key, top/back rim


def _setup(pose):
    S = detective.build(pose)
    S.transform(Rx(PITCH) @ Ry(pose.get('yaw', 90)))
    view_h = FH / PX_PER_M
    top = PIVOT[1] / PX_PER_M                      # metres above the feet at the top edge
    cy = top - view_h / 2
    cam = Camera((0, cy, 10), (0, cy, 0), W=FW * SS, H=FH * SS, ortho=True, ortho_h=view_h)
    return S, cam


def render_pose(pose, name='spr', mode='albedo'):
    """mode: 'albedo' or an index into BASIS."""
    S, cam = _setup(pose)
    for m in S.mats:
        m[3] = 0.0                                   # no specular: matte, relit in the game
        m[11] = m[12] = m[13] = 0.0                  # no emission
        if mode != 'albedo':
            m[0] = m[1] = m[2] = 1.0                 # white: pure shading
            m[5] = 0.0                               # no albedo noise (normals keep their bump)
            m[17] = 0                                # no texture
            if mode == 2:
                m[9] = max(m[9], 0.45)               # rim: let the back light wrap round the silhouette
    if mode == 'albedo':
        env = dict(sky=(255, 255, 255), bounce=(255, 255, 255), fog=0.0, reflections=False, vol_scale=0,
                   grid=0.25, ao_scale=0.35)
    else:
        d = np.array(BASIS[mode], float); d /= np.linalg.norm(d)
        S.sun(tuple(-d), (255, 255, 255), power=1.0, shadow=True, soft=10)
        env = dict(sky=(0, 0, 0), bounce=(0, 0, 0), fog=0.0, reflections=False, vol_scale=0,
                   grid=0.25, ao_scale=0.35)
    surf, depth, vol = S.render(cam, env, name)
    return surf


def to_pixels(surf, gamma=1 / 2.2):
    """Supersampled linear render -> straight-alpha RGBA uint8 at final size (soft, anti-aliased edges).
    Values are stored gamma-encoded (not tone-mapped): the game shader decodes, relights and tone-maps."""
    h, w = FH, FW
    s = surf.reshape(h, SS, w, SS, 4)
    a = s[..., 3].mean(axis=(1, 3))
    rgb = (s[..., :3] * s[..., 3:4]).sum(axis=(1, 3)) / np.maximum(s[..., 3].sum(axis=(1, 3))[..., None], 1e-6)
    out = np.clip(rgb, 0, 1) ** gamma
    rgba = np.zeros((h, w, 4), np.uint8)
    rgba[..., :3] = (out * 255 + 0.5).astype(np.uint8)
    rgba[..., 3] = (np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8)
    return rgba


def render_frame(pose, tag):
    alb = to_pixels(render_pose(pose, tag, 'albedo'))
    sh = np.zeros_like(alb)
    for k in range(3):
        sh[..., k] = to_pixels(render_pose(pose, tag, k))[..., 0]
    sh[..., 3] = alb[..., 3]
    # transparent pixels: copy the nearest shading so linear filtering doesn't darken the edges
    return alb, sh


def build_palette(samples, n=48):
    px = np.concatenate([(img[m] * 255).astype(np.uint8) for img, m in samples])
    side = int(math.ceil(math.sqrt(len(px))))
    pad = np.repeat(px[:1], side * side - len(px), axis=0)
    im = Image.fromarray(np.concatenate([px, pad]).reshape(side, side, 3))
    q = im.quantize(colors=n, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    return np.array(q.getpalette()[:n * 3], float).reshape(-1, 3) / 255.0


def quantize(img, mask, pal):
    flat = img.reshape(-1, 3)
    wts = np.array([0.3, 0.59, 0.11]) * 3
    d = (((flat[:, None, :] - pal[None]) ** 2) * wts).sum(-1)
    idx = d.argmin(1)
    out = (pal[idx].reshape(img.shape) * 255 + 0.5).astype(np.uint8)
    rgba = np.zeros((img.shape[0], img.shape[1], 4), np.uint8)
    rgba[..., :3] = out; rgba[..., 3] = mask * 255
    # selective outline: dark, tinted by the neighbouring colour
    m = mask
    edge = np.zeros_like(m)
    edge[1:] |= m[:-1]; edge[:-1] |= m[1:]; edge[:, 1:] |= m[:, :-1]; edge[:, :-1] |= m[:, 1:]
    edge &= ~m
    ys, xs = np.nonzero(edge)
    for y, x in zip(ys, xs):
        nb = [(y + dy, x + dx) for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)) if 0 <= y + dy < m.shape[0] and 0 <= x + dx < m.shape[1] and m[y + dy, x + dx]]
        c = np.mean([out[p] for p in nb], axis=0) * 0.28 + np.array([6, 6, 10])
        rgba[y, x, :3] = c.astype(np.uint8); rgba[y, x, 3] = 255
    return rgba


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--only', default=''); ap.add_argument('--preview', action='store_true')
    a = ap.parse_args()
    only = set(a.only.split(',')) if a.only else None
    anims = [x for x in ANIMS if not only or x[0] in only]
    t = time.time()
    rendered = []
    for name, poses, fps, loop in anims:
        frames = [render_frame(p, 'spr') for p in poses]
        rendered.append((name, frames, fps, loop))
        print(name, len(frames), f'{time.time() - t:.0f}s', flush=True)
    sheet_rows = []
    for name, frames, fps, loop in rendered:
        alb = [Image.fromarray(f[0], 'RGBA') for f in frames]
        sh = [Image.fromarray(f[1], 'RGBA') for f in frames]
        sheet_rows.append((name, alb, sh, fps, loop))
        if name.endswith('_right'):
            # mirrored frames: flip the image and swap the left/right key channels
            msh = []
            for im in sh:
                r, g, b, al = im.transpose(Image.FLIP_LEFT_RIGHT).split()
                msh.append(Image.merge('RGBA', (g, r, b, al)))
            sheet_rows.append((name.replace('_right', '_left'), [im.transpose(Image.FLIP_LEFT_RIGHT) for im in alb],
                               msh, fps, loop))
    order = ['idle_right', 'walk_right', 'idle_down', 'walk_down', 'idle_up', 'walk_up', 'talk_right', 'talk_down',
             'pickup_right', 'use_right', 'notebook_right', 'look_around', 'shrug', 'show_badge']
    sheet_rows.sort(key=lambda r: (r[0].endswith('_left'), order.index(r[0].replace('_left', '_right')) if r[0].replace('_left', '_right') in order else 99))
    cols = max(len(r[1]) for r in sheet_rows)
    sheet = Image.new('RGBA', (cols * FW, len(sheet_rows) * FH), (0, 0, 0, 0))
    lsheet = Image.new('RGBA', (cols * FW, len(sheet_rows) * FH), (0, 0, 0, 0))
    table = []
    for r, (name, alb, sh, fps, loop) in enumerate(sheet_rows):
        for c, (im, li) in enumerate(zip(alb, sh)):
            sheet.paste(im, (c * FW, r * FH))
            lsheet.paste(li, (c * FW, r * FH))
        table.append((name, r, len(alb), fps, loop))
    if a.preview:
        sheet.save(os.path.join(HERE, 'out', 'detective_sheet.png'))
        lsheet.save(os.path.join(HERE, 'out', 'detective_light_sheet.png'))
        return
    sheet.save(os.path.join(ROOT, 'assets', 'characters', 'detective.png'))
    lsheet.save(os.path.join(ROOT, 'assets', 'characters', 'detective_light.png'))
    lines = ['# Generated by tools/r3/gen_sprites.py - row/frame layout of assets/characters/detective.png',
             '# (detective_light.png has the same layout: R/G/B = shading from the left key, right key and back rim)',
             'extends RefCounted', '', f'const FRAME_SIZE := Vector2i({FW}, {FH})', f'const PIVOT := Vector2({PIVOT[0]}, {PIVOT[1]})',
             f'const HEIGHT := {SPRITE_PX}.0', '', '## name: [row, frame_count, fps, loop]', 'const ANIMS := {']
    for name, r, n, fps, loop in table:
        lines.append(f'\t"{name}": [{r}, {n}, {fps}, {str(loop).lower()}],')
    lines.append('}')
    open(os.path.join(ROOT, 'scripts', 'detective_anims.gd'), 'w').write('\n'.join(lines) + '\n')
    print('sheet', sheet.size, f'{time.time() - t:.0f}s')


if __name__ == '__main__':
    main()
