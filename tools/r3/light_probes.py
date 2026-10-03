"""Bake a grid of light probes for a room so the game can relight the detective wherever he stands.

python light_probes.py street          (render_room.py also runs this after a full render)
Writes assets/rooms/<room>_light.json.

For every 32x32-pixel cell of the 1920x1080 screen, the cell centre is taken as the detective's feet on the
floor. At three heights on his body the renderer (r3 probe mode) measures each room light's attenuation, cone
and soft shadow, and the fog between the camera and him. Each light is then split over the three shading
directions the sprite sheet was rendered with (gen_sprites.BASIS), in the room camera's view space.
Per cell: ambient rgb, left key rgb, right key rgb, rim rgb, fog inscatter rgb, fog transmittance (16 floats).
"""
import importlib, json, math, os, struct, subprocess, sys
import numpy as np
from scene3d import Camera, srgb, TMP, R3, nrm

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
OUTW, OUTH = 1920, 1080
CELL = 32
FLOOR_Y = 0.1
HEIGHTS = (0.35, 0.95, 1.55)
BASIS = [(-0.75, 0.5, 0.45), (0.75, 0.5, 0.45), (0.0, 0.7, -0.7)]     # keep in sync with gen_sprites.BASIS


def floor_point(cam, sx, sy):
    nx, ny = sx / OUTW * 2 - 1, 1 - sy / OUTH * 2
    th = math.tan(math.radians(cam.fov) * 0.5); aspect = cam.W / cam.H
    d = cam.f + cam.r * nx * th * aspect + cam.u * ny * th
    p0 = np.array(cam.pos, float)
    if d[1] > -1e-3:                                   # at or above the horizon: far away
        return p0 + nrm(d * np.array([1, 0, 1])) * 40 + np.array([0, FLOOR_Y - p0[1], 0])
    t = (FLOOR_Y - p0[1]) / d[1]
    return p0 + d * min(t, 60.0)


def point_in_poly(x, y, poly):
    ins = False
    for i in range(len(poly)):
        (x1, y1), (x2, y2) = poly[i - 1], poly[i]
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            ins = not ins
    return ins


def bake(room, S, cam, env, meta, walk_poly):
    cam = Camera(cam.pos, cam.target, cam.fov, cam.W, cam.H)
    gw, gh = OUTW // CELL, (OUTH + CELL - 1) // CELL
    feet = np.array([[floor_point(cam, (i + 0.5) * CELL, (j + 0.5) * CELL) for i in range(gw)] for j in range(gh)])
    pts = []
    for j in range(gh):
        for i in range(gw):
            for h in HEIGHTS:
                pts.append(feet[j, i] + np.array([0, h, 0]))
    pts = np.array(pts, np.float32)
    base = os.path.join(TMP, f'r3_{room}_probe')
    S.write(base + '.bin', cam, env)
    with open(base + '.pts', 'wb') as f:
        f.write(struct.pack('i', len(pts))); f.write(pts.tobytes())
    subprocess.run([R3, base + '.bin', base, base + '.pts'], check=True)
    nl = len(S.lights)
    raw = np.fromfile(base + '.probe', np.float32).reshape(gh, gw, len(HEIGHTS), nl + 4)
    vis = raw[..., :nl].mean(2)                          # (gh, gw, nl)
    fog = raw[..., nl:].mean(2)                          # inscatter rgb + T
    basis = np.array([nrm(b) for b in BASIS])
    sky, bounce = np.array(srgb(env.get('sky', (40, 44, 60)))), np.array(srgb(env.get('bounce', (20, 18, 22))))
    amb = (sky + bounce) * 0.5
    keys = np.zeros((gh, gw, 3, 3))
    body = feet + np.array([0, 0.95, 0])
    for k, l in enumerate(S.lights):
        col = np.array(l[7:10])
        if l[0] == 2:
            ld = np.broadcast_to(-np.array(l[4:7]), body.shape)
        else:
            dv = np.array(l[1:4]) - body
            ld = dv / np.maximum(np.linalg.norm(dv, axis=-1, keepdims=True), 1e-6)
        v = np.stack([ld @ cam.r, ld @ cam.u, -(ld @ cam.f)], -1)          # light direction in view space
        w = np.maximum(v @ basis.T, 0) ** 2
        w = w / np.maximum(w.sum(-1, keepdims=True), 1e-6)
        keys += vis[..., k, None, None] * w[..., :, None] * col
    # character fill: a soft light from the camera side (an actor's eye light) so the detective stays
    # readable in back-lit rooms. meta['char_fill'] = ((r, g, b) sRGB, power)
    fc, fp = meta.get('char_fill', ((255, 255, 255), 0.0))
    fw = np.maximum(nrm((0, 0.35, 1)) @ basis.T, 0) ** 2; fw /= fw.sum()
    keys += fw[:, None] * np.array(srgb(fc)) * fp
    # cells whose feet are off the walkable floor copy the nearest walkable cell (clean bilinear edges)
    inside = np.array([[point_in_poly((i + 0.5) * CELL, (j + 0.5) * CELL, walk_poly) for i in range(gw)] for j in range(gh)])
    data = np.concatenate([np.broadcast_to(amb, (gh, gw, 3)), keys.reshape(gh, gw, 9), fog], -1)
    if inside.any():
        ij = np.argwhere(inside)
        for j in range(gh):
            for i in range(gw):
                if not inside[j, i]:
                    d = ((ij - (j, i)) ** 2).sum(1)
                    jj, ii = ij[d.argmin()]
                    data[j, i] = data[jj, ii]
    out = dict(cell=CELL, gw=gw, gh=gh, exposure=meta.get('exposure', 1.0),
               data=[round(float(x), 5) for x in data.reshape(-1)])
    path = os.path.join(ROOT, 'assets', 'rooms', f'{room}_light.json')
    json.dump(out, open(path, 'w'), separators=(',', ':'))
    print('light probes ->', path)
    return data


if __name__ == '__main__':
    room = sys.argv[1]
    mod = importlib.import_module(room)
    S, cam, env, meta = mod.build()
    info = json.load(open(os.path.join(HERE, 'out', f'{room}.json')))
    bake(room, S, cam, env, meta, info['walk'])
