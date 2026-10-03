"""Python side of the r3 renderer: build SDF scenes, render them, turn the result into pixel art.

Coordinates: metres, y up. Room cameras are perspective; sprites use an orthographic camera.
"""
import math, os, struct, subprocess, tempfile
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
R3 = os.path.join(HERE, 'r3')
TMP = os.environ.get('R3_TMP', tempfile.gettempdir())


# ------------------------------------------------------------------ math
def A(*v): return np.array(v, dtype=float)
def nrm(v): v = np.asarray(v, float); return v / np.linalg.norm(v)
def Rx(a):
    a = math.radians(a); c, s = math.cos(a), math.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
def Ry(a):
    a = math.radians(a); c, s = math.cos(a), math.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
def Rz(a):
    a = math.radians(a); c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
def swing(a): return Rx(-a)


class Frame:
    def __init__(self, o=(0, 0, 0), M=None, s=1.0):
        self.o = np.asarray(o, float); self.M = np.eye(3) if M is None else np.asarray(M, float); self.s = s
    def to(self, l): return self.o + self.M @ (np.asarray(l, float) * self.s)
    def plane(self, n, o):
        nm = self.M @ np.asarray(n, float)
        return nm, o * self.s + float(nm @ self.o)

WORLD = Frame()


def srgb(c): return [((v / 255.0) ** 2.2) for v in c]


# ------------------------------------------------------------------ scene
class Scene:
    def __init__(self):
        self.prims, self.decals, self.lights, self.textures = [], [], [], []
        self.mats, self.mat_index = [], {}
        self.tex_index = {}
        self.tags = {}            # tag -> list of prim indices (for hotspot projection)
        self._tag = None
        self.mat('default', (128, 128, 128))

    # -- materials -------------------------------------------------------
    def mat(self, name, rgb=(128, 128, 128), spec=0.0, shin=20, namp=0.0, nscale=10, bump=0.0, bscale=10,
            wrap=0.0, aniso=0, emis=(0, 0, 0), emis_mult=1.0, refl=0.0, rough=0.0, tex=None, texmode=0,
            texmap=0, texscale=1.0, texemis=1.0, ripple=0.0, linear=False):
        col = list(rgb) if linear else srgb(rgb)
        e = [c * emis_mult for c in (emis if linear else srgb(emis))]
        ti = self.texture(tex) if tex is not None else -1
        vals = col + [spec, shin, namp, nscale, bump, bscale, wrap, aniso] + e + [refl, rough, ti, texmode,
                texmap, texscale, texemis, ripple]
        if name in self.mat_index:
            self.mats[self.mat_index[name]] = vals
        else:
            self.mat_index[name] = len(self.mats); self.mats.append(vals)
        return name

    def texture(self, img):
        if isinstance(img, str):
            key = img
            if key in self.tex_index: return self.tex_index[key]
            img = Image.open(img)
            im = img.convert('RGBA')
            self.tex_index[key] = len(self.textures); self.textures.append(im)
            return self.tex_index[key]
        self.textures.append(img.convert('RGBA'))
        return len(self.textures) - 1

    def M(self, name): return self.mat_index[name]

    # -- tagging -----------------------------------------------------------
    def tag(self, name):
        self._tag = name
        return self
    def __enter__(self): return self
    def __exit__(self, *a): self._tag = None

    # -- primitives ----------------------------------------------------------
    def _add(self, typ, m, op, k, a=None, b=None, ra=0, rb=0, R=None, c=None, r=None, clip=None, shell=0,
             clip2=None, inmat=None):
        self.prims.append(dict(type=typ, mat=self.M(m), op=op, k=k,
                               a=A(0, 0, 0) if a is None else np.asarray(a, float),
                               b=A(0, 0, 0) if b is None else np.asarray(b, float), ra=ra, rb=rb,
                               R=np.eye(3) if R is None else np.asarray(R, float),
                               c=A(0, 0, 0) if c is None else np.asarray(c, float),
                               r=A(1, 1, 1) if r is None else np.asarray(r, float), clip=clip, shell=shell,
                               clip2=clip2, inmat=inmat))
        if self._tag:
            self.tags.setdefault(self._tag, []).append(len(self.prims) - 1)
        return len(self.prims) - 1

    def cone(self, a, b, ra, rb, m, k=0, op=0, clip=None):
        a, b = np.asarray(a, float), np.asarray(b, float)
        if np.linalg.norm(b - a) <= abs(ra - rb) + 1e-5:
            return self.sph(a if ra >= rb else b, max(ra, rb), m, k, op)
        return self._add(0, m, op, k, a=a, b=b, ra=ra, rb=rb, clip=clip)
    def cyl(self, a, b, r, m, k=0, op=0): return self.cone(a, b, r, r, m, k, op)
    def sph(self, c, r, m, k=0, op=0): return self._add(3, m, op, k, a=c, ra=r)
    def ell(self, fr, c, r, m, k=0, op=0, rot=None, clip=None):
        Mx = fr.M if rot is None else fr.M @ rot
        return self._add(1, m, op, k, R=Mx.T, c=fr.to(c), r=np.asarray(r, float) * fr.s, clip=clip)
    def box(self, fr, c, half, rnd, m, k=0, op=0, rot=None):
        Mx = fr.M if rot is None else fr.M @ rot
        return self._add(2, m, op, k, R=Mx.T, c=fr.to(c), r=np.asarray(half, float) * fr.s, ra=rnd * fr.s)
    def wbox(self, c, half, m, rnd=0.0, rot=None, k=0, op=0):
        """World-space box. rot: 3x3 rotation (e.g. Ry(30))."""
        return self.box(WORLD, c, half, rnd, m, k=k, op=op, rot=rot)
    def wboxr(self, x0, y0, z0, x1, y1, z1, m, rnd=0.0, k=0, op=0):
        """Axis-aligned box from min/max corners."""
        return self.wbox(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2),
                         (abs(x1 - x0) / 2, abs(y1 - y0) / 2, abs(z1 - z0) / 2), m, rnd=rnd, k=k, op=op)
    def fcyl(self, c, r, half_h, m, axis='y', op=0, k=0):
        """Flat-capped cylinder centred at c along a world axis."""
        R = {'y': np.eye(3), 'z': Rx(90), 'x': Rz(90)}[axis]
        return self.tcyl(Frame(c, R), (0, 0, 0), (r, r), (r, r), half_h, m, k=k, op=op)

    def tcyl(self, fr, c, top, bot, h, m, shell=0, clip=None, clip2=None, k=0, rot=None, inmat=None, op=0):
        Mx = fr.M if rot is None else fr.M @ rot
        sc = fr.s
        i = self._add(4, m, op, k, a=A(bot[0] * sc, bot[1] * sc, 0), R=Mx.T, c=fr.to(c),
                      r=A(top[0] * sc, top[1] * sc, h * sc), shell=shell,
                      clip=None if clip is None else fr.plane(*clip),
                      clip2=None if clip2 is None else fr.plane(*clip2))
        self.prims[i]['inmat'] = self.M(inmat) if inmat else None
        return i
    def decal(self, fr, frm, to, planes, feather=0.0):
        self.decals.append((self.M(frm), self.M(to), [fr.plane(n, o) for n, o in planes], feather))

    # -- lights ----------------------------------------------------------------
    def light(self, pos, col, power=1.0, range=12.0, shadow=True, vol=0.0, volshadow=False, soft=12.0,
              spot=None, linear=False):
        """Point light (or spot when spot=(direction, inner_deg, outer_deg)). col is sRGB 0-255."""
        c = list(col) if linear else srgb(col)
        c = [v * power for v in c]
        if spot:
            d, ai, ao = spot
            self.lights.append([1, *pos, *nrm(d), *c, range, math.cos(math.radians(ai)), math.cos(math.radians(ao)),
                                1 if shadow else 0, vol, 1 if volshadow else 0, soft])
        else:
            self.lights.append([0, *pos, 0, -1, 0, *c, range, 0, 0, 1 if shadow else 0, vol,
                                1 if volshadow else 0, soft])
    def sun(self, direction, col, power=1.0, shadow=True, vol=0.0, soft=12.0):
        c = [v * power for v in srgb(col)]
        self.lights.append([2, 0, 0, 0, *nrm(direction), *c, 1e4, 0, 0, 1 if shadow else 0, vol, 0, soft])

    # -- transform (used by sprite rigs) ---------------------------------------
    def transform(self, Wm):
        for p in self.prims:
            if p['type'] != 4: p['a'] = Wm @ p['a']; p['b'] = Wm @ p['b']
            p['c'] = Wm @ p['c']
            p['R'] = p['R'] @ Wm.T
            if p['clip'] is not None: p['clip'] = (Wm @ p['clip'][0], p['clip'][1])
            if p['clip2'] is not None: p['clip2'] = (Wm @ p['clip2'][0], p['clip2'][1])
        self.decals = [(f, t, [(Wm @ n, o) for n, o in pl], fe) for f, t, pl, fe in self.decals]

    @staticmethod
    def bounds(p):
        t = p['type']
        if t == 0: return (p['a'] + p['b']) / 2, np.linalg.norm(p['b'] - p['a']) / 2 + max(p['ra'], p['rb'])
        if t == 1: return p['c'], max(p['r'])
        if t == 2: return p['c'], float(np.linalg.norm(p['r'])) + p['ra']
        if t == 4: return p['c'], math.hypot(max(p['r'][0], p['r'][1], p['a'][0], p['a'][1]), p['r'][2]) + p['shell']
        return p['a'], p['ra']

    def corners(self, i):
        """Approximate 3D corner points of a prim (for projecting hotspots)."""
        p = self.prims[i]
        if p['type'] == 2:
            Rt = p['R'].T
            out = []
            for sx in (-1, 1):
                for sy in (-1, 1):
                    for sz in (-1, 1):
                        out.append(p['c'] + Rt @ (p['r'] * A(sx, sy, sz)))
            return out
        c, r = self.bounds(p)
        if p['type'] in (1, 4):
            Rt = p['R'].T
            ext = p['r'] if p['type'] == 1 else A(max(p['r'][0], p['a'][0]), p['r'][2], max(p['r'][1], p['a'][1]))
            if p['type'] == 4:
                ext = A(max(p['r'][0], p['a'][0]), p['r'][2], max(p['r'][1], p['a'][1]))
            return [p['c'] + Rt @ (ext * A(sx, sy, sz)) for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)]
        if p['type'] == 0:
            pts = []
            for e, rr in ((p['a'], p['ra']), (p['b'], p['rb'])):
                for d in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)):
                    pts.append(e + rr * A(*d))
            return pts
        return [c + r * A(*d) for d in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))]

    # -- output ------------------------------------------------------------------
    def write(self, path, cam, env):
        with open(path, 'wb') as f:
            hdr = [cam.W, cam.H, 1 if cam.ortho else 0, *cam.pos, *cam.target, math.radians(cam.fov), cam.ortho_h,
                   *srgb(env.get('sky', (40, 44, 60))), *srgb(env.get('bounce', (20, 18, 22))),
                   *srgb(env.get('fog_col', (20, 22, 30))), env.get('fog', 0.0), env.get('fog_h0', 0.0),
                   env.get('fog_hf', 0.0), env.get('fog_max', 80.0),
                   len(self.prims), len(self.decals), len(self.mats), len(self.lights), len(self.textures),
                   1 if env.get('reflections', True) else 0, 1 if env.get('shadows', True) else 0,
                   env.get('vol_scale', 0), env.get('grid', 0.6), env.get('ao_scale', 1.0), *cam.up,
                   env.get('vol_steps', 40)]
            hdr += [0] * (64 - len(hdr))
            f.write(struct.pack('64f', *hdr))
            for p in self.prims:
                c, r = self.bounds(p)
                cl, c2 = p['clip'], p['clip2']
                v = [p['type'], p['mat'], p['op'], p['k'], *p['a'], *p['b'], p['ra'], p['rb'],
                     *p['R'].flatten(), *p['c'], *p['r'],
                     1 if cl is not None else 0, *(cl[0] if cl is not None else (0, 0, 0)), cl[1] if cl is not None else 0,
                     *c, r, p['shell'], 1 if c2 is not None else 0, *(c2[0] if c2 is not None else (0, 0, 0)),
                     c2[1] if c2 is not None else 0, (p['inmat'] + 1) if p.get('inmat') is not None else 0]
                v += [0] * (48 - len(v)); f.write(struct.pack('48f', *v))
            for frm, to, pl, fe in self.decals:
                v = [frm, to, len(pl)]
                for n, o in pl: v += [*n, o]
                v += [0] * (27 - len(v)) + [fe]; f.write(struct.pack('28f', *v))
            for m in self.mats:
                v = list(m) + [0] * (32 - len(m)); f.write(struct.pack('32f', *v))
            for l in self.lights:
                v = list(l) + [0] * (20 - len(l)); f.write(struct.pack('20f', *v))
            for im in self.textures:
                f.write(struct.pack('2i', im.width, im.height)); f.write(im.tobytes())

    def render(self, cam, env, name='scene'):
        base = os.path.join(TMP, f'r3_{name}')
        self.write(base + '.bin', cam, env)
        subprocess.run([R3, base + '.bin', base], check=True)
        surf = np.fromfile(base + '.surf', np.float32).reshape(cam.H, cam.W, 4)
        depth = np.fromfile(base + '.depth', np.float32).reshape(cam.H, cam.W)
        vol = None
        vs = env.get('vol_scale', 0)
        if vs and env.get('fog', 0) > 0:
            vol = np.fromfile(base + '.vol', np.float32).reshape(cam.H // vs, cam.W // vs, 4)
        return surf, depth, vol


class Camera:
    def __init__(self, pos, target, fov=50.0, W=1280, H=720, ortho=False, ortho_h=2.0, up=(0, 1, 0)):
        self.pos, self.target, self.fov, self.W, self.H = list(pos), list(target), fov, W, H
        self.ortho, self.ortho_h, self.up = ortho, ortho_h, list(up)
        f = nrm(A(*target) - A(*pos)); r = nrm(np.cross(f, A(*up))); u = np.cross(r, f)
        self.f, self.r, self.u = f, r, u

    def project(self, p, out_w=640, out_h=360):
        """World point -> pixel coords in an out_w x out_h image."""
        d = A(*p) - A(*self.pos)
        z = d @ self.f
        x, y = d @ self.r, d @ self.u
        aspect = self.W / self.H
        if self.ortho:
            nx, ny = x / (self.ortho_h * 0.5 * aspect), y / (self.ortho_h * 0.5)
        else:
            th = math.tan(math.radians(self.fov) * 0.5)
            nx, ny = x / (z * th * aspect), y / (z * th)
        return ((nx + 1) * 0.5 * out_w, (1 - ny) * 0.5 * out_h, z)


# ------------------------------------------------------------------ post: pixel art
BAYER8 = np.array([[0, 32, 8, 40, 2, 34, 10, 42], [48, 16, 56, 24, 50, 18, 58, 26], [12, 44, 4, 36, 14, 46, 6, 38],
                   [60, 28, 52, 20, 62, 30, 54, 22], [3, 35, 11, 43, 1, 33, 9, 41], [51, 19, 59, 27, 49, 17, 57, 25],
                   [15, 47, 7, 39, 13, 45, 5, 37], [63, 31, 55, 23, 61, 29, 53, 21]], float) / 64.0


def aces(x):
    return np.clip((x * (2.51 * x + 0.03)) / (x * (2.43 * x + 0.59) + 0.14), 0, 1)


def downsample(a, f):
    h, w = a.shape[0] // f, a.shape[1] // f
    return a[:h * f, :w * f].reshape(h, f, w, f, -1).mean(axis=(1, 3))


def composite(surf, vol, ss, exposure=1.0, grade=None):
    """Linear surf (H,W,4) rendered at ss x supersample + volumetric pass (rendered at vol_scale == ss)
    -> sRGB float image at target resolution, plus coverage alpha."""
    low = downsample(surf[..., :3], ss)
    alpha = downsample(surf[..., 3:4], ss)[..., 0]
    if vol is not None:
        if vol.shape[:2] != low.shape[:2]:
            vol = np.stack([np.asarray(Image.fromarray(np.ascontiguousarray(vol[..., k])).resize(
                (low.shape[1], low.shape[0]), Image.BICUBIC)) for k in range(4)], -1)
        low = low * np.clip(vol[..., 3:4], 0, 1) + np.maximum(vol[..., :3], 0)
    low = low * exposure
    if grade: low = grade(low)
    out = aces(low) ** (1 / 2.2)
    return out, alpha


def palette_quantize(img, n_colors=96, dither=0.06, sharpen=0.0, seed_img=None):
    """sRGB float image -> palettised uint8 RGB with ordered dithering."""
    h, w = img.shape[:2]
    src = (np.clip(img, 0, 1) * 255).astype(np.uint8)
    if seed_img is None:
        # oversample saturated / bright pixels so neon and highlights keep their own palette entries
        f = img.reshape(-1, 3)
        mx, mn = f.max(1), f.min(1)
        score = (mx - mn) * (0.3 + mx)
        k = max(64, len(f) // 25)
        top = np.argsort(score)[-k:]
        extra = (np.clip(f[top], 0, 1) * 255).astype(np.uint8)
        extra = np.repeat(extra, 6, axis=0)
        allpx = np.concatenate([src.reshape(-1, 3), extra])
        side = int(math.ceil(math.sqrt(len(allpx))))
        pad = np.zeros((side * side - len(allpx), 3), np.uint8) + allpx[:1]
        seed_img = np.concatenate([allpx, pad]).reshape(side, side, 3)
    pal_src = Image.fromarray(seed_img)
    pal_img = pal_src.quantize(colors=n_colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    pal = np.array(pal_img.getpalette()[:n_colors * 3], float).reshape(-1, 3) / 255.0
    th = np.tile(BAYER8, (h // 8 + 1, w // 8 + 1))[:h, :w] - 0.5
    x = img + th[..., None] * dither
    flat = x.reshape(-1, 3)
    # nearest palette entry (perceptual-ish weights)
    wts = np.array([0.30, 0.59, 0.11]) * 3
    best = np.zeros(len(flat), int); bd = np.full(len(flat), 1e9)
    for i, c in enumerate(pal):
        d = (((flat - c) ** 2) * wts).sum(1)
        m = d < bd; bd[m] = d[m]; best[m] = i
    out = (pal[best].reshape(h, w, 3) * 255 + 0.5).astype(np.uint8)
    return out, pal


def painterly(img, radius=1):
    """Light Kuwahara-style smoothing so renders read as painted rather than noisy."""
    from PIL import ImageFilter
    im = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))
    im = im.filter(ImageFilter.ModeFilter(3)) if radius else im
    return np.asarray(im).astype(float) / 255.0
