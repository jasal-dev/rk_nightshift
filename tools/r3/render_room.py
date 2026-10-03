"""Render a room set, convert it to pixel art and export the data Godot needs.

python render_room.py street [--preview] [--colors 112]
Writes  assets/rooms/<room>.png  and  tools/r3/out/<room>.json (hotspot polygons, walk area, spawns, scaling).
"""
import argparse, importlib, json, math, os, sys, time
import numpy as np
from PIL import Image
from scene3d import composite, palette_quantize, Camera

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
OUTW, OUTH = 1920, 1080
PERSON_M = 1.83
SPRITE_PX = 312          # detective height in pixels at scale 1.0 (see gen_sprites.py)


def hull(points):
    pts = sorted(set((round(x, 1), round(y, 1)) for x, y in points))
    if len(pts) < 3: return pts
    def cross(o, a, b): return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, hi = [], []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0: lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(hi) >= 2 and cross(hi[-2], hi[-1], p) <= 0: hi.pop()
        hi.append(p)
    return lo[:-1] + hi[:-1]


def clip_poly(poly, x0=0.0, y0=0.0, x1=OUTW, y1=OUTH):
    """Sutherland-Hodgman clip of a polygon to a rectangle."""
    def clip(pts, inside, inter):
        out = []
        for i in range(len(pts)):
            a, b = pts[i - 1], pts[i]
            if inside(b):
                if not inside(a): out.append(inter(a, b))
                out.append(b)
            elif inside(a):
                out.append(inter(a, b))
        return out
    def ix(xc):
        return lambda a, b: (xc, a[1] + (b[1] - a[1]) * (xc - a[0]) / (b[0] - a[0]))
    def iy(yc):
        return lambda a, b: (a[0] + (b[0] - a[0]) * (yc - a[1]) / (b[1] - a[1]), yc)
    pts = list(poly)
    for inside, inter in ((lambda p: p[0] >= x0, ix(x0)), (lambda p: p[0] <= x1, ix(x1)),
                          (lambda p: p[1] >= y0, iy(y0)), (lambda p: p[1] <= y1, iy(y1))):
        if not pts: break
        pts = clip(pts, inside, inter)
    return [(round(x, 1), round(y, 1)) for x, y in pts]


def clip_screen(poly):
    return clip_poly(poly)


def export_meta(S, cam, meta, floor_y=0.1):
    P = lambda p: cam.project(p, OUTW, OUTH)
    hs = {}
    for tag, (name, walk, face) in meta['hotspots'].items():
        if tag in meta.get('hotspot_shapes', {}):
            pts = [P(p)[:2] for p in meta['hotspot_shapes'][tag]]
        else:
            pts = []
            for i in S.tags.get(tag, []):
                pts += [P(c)[:2] for c in S.corners(i)]
        if not pts:
            print('WARNING: hotspot without geometry', tag); continue
        poly = clip_screen(hull(pts))
        w2 = None
        if walk is not None:
            x, y, _ = P((walk[0], floor_y, walk[1])); w2 = (round(x), round(y))
        hs[tag] = dict(name=name, polygon=poly, walk_to=w2, face=face)
    walk = [tuple(round(v, 1) for v in P((x, floor_y, z))[:2]) for x, z in meta['walk']]
    walk = clip_poly(walk, 6, 0, OUTW - 6, OUTH - 2)
    spawns = {k: tuple(round(v) for v in P((x, floor_y, z))[:2]) for k, (x, z) in meta['spawns'].items()}
    # depth scaling: person height in px is linear in screen y on a flat floor
    samples = []
    for z in (meta['walk_zmin'], meta['walk_zmax']):
        x = meta.get('scale_x', 0.0)
        fx, fy, _ = P((x, floor_y, z)); hx, hy, _ = P((x, floor_y + PERSON_M, z))
        samples.append((fy, (fy - hy) / SPRITE_PX))
    (fy0, s0), (fy1, s1) = samples
    obstacles = []
    for (x, z, r) in meta.get('obstacles', []):
        ring = [P((x + r * math.cos(a), floor_y, z + r * math.sin(a)))[:2]
                for a in np.linspace(0, 2 * math.pi, 12, endpoint=False)]
        obstacles.append([(round(px, 1), round(py, 1)) for px, py in ring])
    return dict(room=meta['room'], hotspots=hs, order=meta['hotspot_order'], walk=walk, spawns=spawns,
                obstacles=obstacles,
                far_y=round(fy0, 1), far_scale=round(s0, 3), near_y=round(fy1, 1), near_scale=round(s1, 3),
                tint=meta.get('tint', (1, 1, 1)), extra=meta.get('extra', {}))


def drop_specks(mask, r=2, min_sum=3.0):
    """Zero out isolated mask pixels (depth noise far from the prop)."""
    p = np.pad(mask, r + 1)
    c = p.cumsum(0).cumsum(1)
    k = 2 * r + 1
    box = c[k:, k:] - c[:-k, k:] - c[k:, :-k] + c[:-k, :-k]
    return np.where(box[:mask.shape[0], :mask.shape[1]] >= min_sum, mask, 0)


def finish(img, seed=1):
    """Filmic finish for full-resolution art: soft vignette and fine grain (also hides banding)."""
    h, w = img.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    r = np.hypot((xx - w / 2) / (w / 2), (yy - h / 2) / (h / 2))
    vig = 1 - 0.28 * np.clip(r - 0.45, 0, 1) ** 1.6
    grain = np.random.default_rng(seed).normal(0, 0.012, (h, w, 1))
    out = np.clip(img * vig[..., None] + grain, 0, 1)
    return (out * 255 + 0.5).astype(np.uint8)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('room'); ap.add_argument('--preview', action='store_true')
    ap.add_argument('--colors', type=int, default=0); ap.add_argument('--exposure', type=float, default=0)
    ap.add_argument('--meta-only', action='store_true')
    a = ap.parse_args()
    mod = importlib.import_module(a.room)
    S, cam, env, meta = mod.build()
    if a.meta_only:
        path = os.path.join(HERE, 'out', f'{a.room}.json')
        old = json.load(open(path)) if os.path.exists(path) else {}
        info = export_meta(S, Camera(cam.pos, cam.target, cam.fov, cam.W, cam.H), meta)
        info['overlays'] = old.get('overlays', {})
        info['occluders'] = old.get('occluders', {})
        json.dump(info, open(path, 'w'), indent=1)
        print('meta written'); return
    if a.preview:
        cam = Camera(cam.pos, cam.target, cam.fov, 960, 540)
        env = dict(env); env['vol_scale'] = 2
    ss = max(1, cam.W // OUTW)
    t = time.time()
    surf, depth, vol = S.render(cam, env, a.room)
    depth = np.nan_to_num(depth, nan=1e6, posinf=1e6)
    print(f'render {time.time() - t:.1f}s, {len(S.prims)} prims')
    img, alpha = composite(surf, vol, ss, exposure=a.exposure or meta.get('exposure', 1.0), grade=meta.get('grade'))
    overlays = {}
    for tag in meta.get('overlays', []):
        # render again without the prop; the difference becomes a sprite the game can hide
        S2, _, _, _ = mod.build(hide={tag})
        s2, _, v2 = S2.render(cam, env, a.room + '_no_' + tag)
        img2, _ = composite(s2, v2, ss, exposure=a.exposure or meta.get('exposure', 1.0), grade=meta.get('grade'))
        overlays[tag] = img
        diff = np.clip((np.abs(img - img2).max(-1) - 0.01) / 0.03, 0, 1)
        overlays[tag] = (img.copy(), diff)
        img = img2
    occ_masks = {}
    for tag in meta.get('occluders', {}):
        # render again without the prop; wherever the prop was the nearest surface, it covers the player
        S2, _, _, _ = mod.build(hide={tag})
        _, d2, _ = S2.render(cam, dict(env, vol_scale=0, reflections=False), a.room + '_occ_' + tag)
        d2 = np.nan_to_num(d2, nan=1e6, posinf=1e6)
        hit = (d2 - depth > np.maximum(0.03, 0.01 * depth)).astype(np.float32)
        h, w = hit.shape
        occ_masks[tag] = drop_specks(hit.reshape(h // ss, ss, w // ss, ss).mean((1, 3)))   # anti-aliased coverage
    os.makedirs(os.path.join(HERE, 'out'), exist_ok=True)
    Image.fromarray((img * 255).astype(np.uint8)).save(os.path.join(HERE, 'out', f'{a.room}_raw.png'))
    out = Image.fromarray(finish(img, seed=1))
    out.save(os.path.join(HERE, 'out', f'{a.room}_final.png'))
    if not a.preview:
        out.save(os.path.join(ROOT, 'assets', 'rooms', f'{a.room}.png'))
        info = export_meta(S, Camera(cam.pos, cam.target, cam.fov, cam.W, cam.H), meta)
        info['overlays'] = {}
        for tag, (full, mask) in overlays.items():
            # quantise the "with prop" frame to the same palette, cut out the changed pixels
            fq = finish(full, seed=1)
            ys, xs = np.nonzero(mask > 0)
            x0, y0, x1, y1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
            rgba = np.zeros((y1 - y0, x1 - x0, 4), np.uint8)
            rgba[..., :3] = fq[y0:y1, x0:x1]
            rgba[..., 3] = (mask[y0:y1, x0:x1] * 255).astype(np.uint8)
            Image.fromarray(rgba, 'RGBA').save(os.path.join(ROOT, 'assets', 'rooms', f'{a.room}_{tag}.png'))
            info['overlays'][tag] = [int(x0), int(y0)]
        info['occluders'] = {}
        fin = np.asarray(out)
        for tag, mask in occ_masks.items():
            # same pixels as the background, so the cut-out is invisible until someone walks behind it
            ys, xs = np.nonzero(mask > 0)
            x0, y0, x1, y1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
            rgba = np.zeros((y1 - y0, x1 - x0, 4), np.uint8)
            rgba[..., :3] = fin[y0:y1, x0:x1]
            rgba[..., 3] = (mask[y0:y1, x0:x1] * 255 + 0.5).astype(np.uint8)
            Image.fromarray(rgba, 'RGBA').save(os.path.join(ROOT, 'assets', 'rooms', f'{a.room}_{tag}.png'))
            bx, by, _ = Camera(cam.pos, cam.target, cam.fov, cam.W, cam.H).project(
                (meta['occluders'][tag][0], 0.1, meta['occluders'][tag][1]), OUTW, OUTH)
            info['occluders'][tag] = dict(pos=[int(x0), int(y0)], base=[round(bx), round(by)])
        with open(os.path.join(HERE, 'out', f'{a.room}.json'), 'w') as f:
            json.dump(info, f, indent=1)
        import light_probes
        light_probes.bake(a.room, S, cam, env, meta, info['walk'])
    print('done')


if __name__ == '__main__':
    main()
