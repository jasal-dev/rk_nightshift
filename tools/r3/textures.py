"""Procedural textures for the Nightshift sets (PIL). All return RGBA PIL images."""
import math, os, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FONT_DIR = '/usr/share/fonts/truetype/dejavu/'
def _font_dirs():
    yield FONT_DIR
    try:   # matplotlib ships the DejaVu family, which makes this work on Windows too
        import matplotlib
        yield os.path.join(os.path.dirname(matplotlib.__file__), 'mpl-data', 'fonts', 'ttf') + os.sep
    except ImportError:
        pass

def font(name='DejaVuSans-Bold.ttf', size=40):
    for d in _font_dirs():
        try: return ImageFont.truetype(d + name, size)
        except Exception: pass
    return ImageFont.load_default()

def noise(w, h, scale, seed=0, octaves=4):
    rng = np.random.default_rng(seed)
    out = np.zeros((h, w))
    amp, tot = 1.0, 0
    for o in range(octaves):
        s = max(1, int(scale / (2 ** o)))
        g = rng.random((h // s + 2, w // s + 2))
        im = Image.fromarray((g * 255).astype(np.uint8)).resize(((w // s + 2) * s, (h // s + 2) * s), Image.BICUBIC)
        out += np.asarray(im, float)[:h, :w] / 255 * amp
        tot += amp; amp *= 0.5
    return out / tot

def to_img(rgb, a=None):
    rgb = np.clip(rgb, 0, 255).astype(np.uint8)
    if a is None: a = np.full(rgb.shape[:2], 255, np.uint8)
    return Image.fromarray(np.dstack([rgb, np.clip(a, 0, 255).astype(np.uint8)]), 'RGBA')

def brick(seed=1, w=256, h=256, base=(118, 62, 48), mortar=(70, 62, 58), rows=16, cols=4):
    rng = random.Random(seed)
    img = Image.new('RGB', (w, h), mortar); d = ImageDraw.Draw(img)
    bh = h / rows; bw = w / cols
    for r in range(rows):
        off = (bw / 2) if r % 2 else 0
        for c in range(-1, cols + 1):
            x0 = c * bw + off + 1; y0 = r * bh + 1
            k = rng.uniform(0.7, 1.15)
            col = tuple(int(v * k + rng.uniform(-6, 6)) for v in base)
            d.rectangle([x0, y0, x0 + bw - 3, y0 + bh - 3], fill=col)
    a = np.asarray(img, float)
    n = noise(w, h, 24, seed)[..., None]
    grime = noise(w, h, 64, seed + 7)[..., None]
    a = a * (0.8 + 0.4 * n) * (0.75 + 0.35 * grime)
    return to_img(a)

def concrete(seed=2, w=256, h=256, base=(120, 122, 124), panel=128):
    n = noise(w, h, 40, seed); n2 = noise(w, h, 4, seed + 1, 2)
    a = np.ones((h, w, 3)) * np.array(base, float)
    a *= (0.9 + 0.12 * n[..., None]) * (0.88 + 0.2 * n2[..., None])
    # panel seams + rain streaks
    a[::panel, :] *= 0.55; a[:, ::panel] *= 0.55
    streak = noise(w, h, 3, seed + 3)
    st = np.asarray(Image.fromarray((streak * 255).astype(np.uint8)).resize((w, h // 8)).resize((w, h)), float) / 255
    a *= (0.85 + 0.2 * st[..., None])
    return to_img(a)

def asphalt(seed=3, w=256, h=256):
    n = noise(w, h, 32, seed); n2 = np.random.default_rng(seed).random((h, w))
    a = np.ones((h, w, 3)) * 46 * (0.75 + 0.45 * n[..., None]) * (0.85 + 0.3 * n2[..., None])
    img = to_img(a); d = ImageDraw.Draw(img)
    rng = random.Random(seed)
    for _ in range(14):   # cracks / tar seams
        x, y = rng.uniform(0, w), rng.uniform(0, h)
        for _ in range(30):
            nx, ny = x + rng.uniform(-6, 6), y + rng.uniform(-6, 6)
            d.line([x, y, nx, ny], fill=(26, 26, 28, 255)); x, y = nx, ny
    return img

def sidewalk(seed=4, w=256, h=256, slab=128):
    n = noise(w, h, 30, seed); n2 = np.random.default_rng(seed).random((h, w))
    a = np.ones((h, w, 3)) * np.array([104, 102, 100], float) * (0.75 + 0.35 * n[..., None]) * (0.9 + 0.15 * n2[..., None])
    a[::slab, :] *= 0.5; a[:, ::slab] *= 0.5
    return to_img(a)

def linoleum(seed=5, w=256, h=256, tile=64):
    a = np.zeros((h, w, 3))
    rng = np.random.default_rng(seed)
    for ty in range(h // tile):
        for tx in range(w // tile):
            k = rng.uniform(0.85, 1.1)
            a[ty * tile:(ty + 1) * tile, tx * tile:(tx + 1) * tile] = np.array([118, 114, 104]) * k
    n = noise(w, h, 8, seed)
    a *= (0.85 + 0.25 * n[..., None]); a[::tile, :] *= 0.7; a[:, ::tile] *= 0.7
    return to_img(a)

def carpet(seed=6, w=256, h=256):
    n = noise(w, h, 4, seed, 2); n2 = noise(w, h, 50, seed + 1)
    a = np.ones((h, w, 3)) * np.array([62, 66, 74], float) * (0.8 + 0.3 * n[..., None]) * (0.85 + 0.25 * n2[..., None])
    return to_img(a)

def ceiling_tiles(seed=7, w=256, h=256, tile=64):
    n = noise(w, h, 3, seed, 2)
    a = np.ones((h, w, 3)) * 168 * (0.85 + 0.2 * n[..., None])
    a[::tile, :] = 90; a[:, ::tile] = 90
    return to_img(a)

def windows_grid(seed, cols, rows, lit=0.3, w=None, h=None, frame=(40, 40, 46), warm=True, blinds=True, k=4):
    """Facade window sheet. RGB albedo = glass/frames, alpha = emission mask for lit windows."""
    cw, ch = 24 * k, 32 * k
    W, H = cols * cw, rows * ch
    rng = random.Random(seed)
    img = Image.new('RGBA', (W, H), frame + (0,)); d = ImageDraw.Draw(img)
    for r in range(rows):
        for c in range(cols):
            x0, y0 = c * cw + 3 * k, r * ch + 4 * k
            on = rng.random() < lit
            if on:
                col = rng.choice([(255, 196, 120), (255, 214, 150), (200, 220, 255), (255, 180, 110)] if warm else
                                 [(190, 210, 240), (220, 230, 255)])
                d.rectangle([x0, y0, x0 + cw - 7 * k, y0 + ch - 9 * k], fill=col + (255,))
                if blinds and rng.random() < 0.6:
                    for yy in range(y0, y0 + ch - 9 * k, 3 * k):
                        d.rectangle([x0, yy, x0 + cw - 7 * k, yy + k - 1], fill=tuple(int(v * 0.55) for v in col) + (255,))
                if rng.random() < 0.35:   # a hint of the room: darker lower half (furniture, shadow)
                    d.rectangle([x0, y0 + (ch - 9 * k) * 2 // 3, x0 + cw - 7 * k, y0 + ch - 9 * k],
                                fill=tuple(int(v * 0.45) for v in col) + (255,))
            else:
                d.rectangle([x0, y0, x0 + cw - 7 * k, y0 + ch - 9 * k], fill=(22, 24, 34, 0))
    return img

def neon_text(text, color, size=64, fnt='DejaVuSans-Bold.ttf', pad=24, vertical=False, tube=4):
    """Emissive neon lettering: alpha marks the glowing tube, with a soft halo."""
    f = font(fnt, size)
    if vertical:
        lines = list(text)
        widths = [f.getbbox(ch)[2] for ch in lines]
        W = max(widths) + pad * 2; H = int(len(lines) * size * 1.02) + pad * 2
    else:
        bb = f.getbbox(text); W = bb[2] + pad * 2; H = size + pad * 2
    m = Image.new('L', (W, H), 0); d = ImageDraw.Draw(m)
    if vertical:
        for i, ch in enumerate(lines):
            cw = f.getbbox(ch)[2]
            d.text(((W - cw) // 2, pad + i * size * 1.02), ch, font=f, fill=255)
    else:
        d.text((pad, pad - size * 0.1), text, font=f, fill=255)
    # tube = outline of glyphs
    edge = m.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.MaxFilter(tube | 1))
    tubem = np.asarray(edge, float) / 255
    halo = np.asarray(m.filter(ImageFilter.GaussianBlur(size * 0.12)), float) / 255
    a = np.clip(tubem * 1.0 + halo * 0.35, 0, 1)
    core = np.clip(tubem, 0, 1)[..., None]
    rgb = np.array(color, float) * (1 - core * 0.45) + 255 * core * 0.45
    return to_img(np.broadcast_to(rgb, (H, W, 3)), a * 255)

def sign_board(text, fg, bg, w=512, h=128, fnt='DejaVuSans-Bold.ttf', size=None, alpha_bg=255):
    img = Image.new('RGBA', (w, h), bg + (alpha_bg,)); d = ImageDraw.Draw(img)
    f = font(fnt, size or int(h * 0.62))
    bb = d.textbbox((0, 0), text, font=f)
    d.text(((w - bb[2]) // 2, (h - bb[3]) // 2 - bb[1] // 2), text, font=f, fill=fg + (255,))
    return img

def skyline(seed=9, w=1024, h=256, k=1):
    """Distant city: albedo dark silhouettes, alpha = emissive windows + haze glow at the horizon."""
    w, h = w * k, h * k
    rng = random.Random(seed)
    sky = np.zeros((h, w, 3)); a = np.zeros((h, w))
    yy = np.linspace(0, 1, h)[:, None]
    sky[:] = (np.array([46, 30, 60]) * (1 - yy) + np.array([150, 80, 70]) * yy)[:, None, :][:, 0, :][:, None, :]
    a[:] = (0.25 + 0.75 * yy ** 2)
    img = to_img(sky, a * 255); d = ImageDraw.Draw(img)
    x = 0
    while x < w:
        bw = rng.randint(14, 60) * k; bh = rng.randint(30, 200) * k
        top = h - bh
        d.rectangle([x, top, x + bw, h], fill=(14, 12, 22, 0))
        if rng.random() < 0.25:
            d.rectangle([x + bw // 2 - k, top - rng.randint(6, 30) * k, x + bw // 2, top], fill=(14, 12, 22, 0))
            d.rectangle([x + bw // 2 - k, top - 6 * k, x + bw // 2, top - 5 * k], fill=(255, 60, 50, 255))
        for wy in range(top + 4 * k, h - 2 * k, 5 * k):
            for wx in range(x + 2 * k, x + bw - 2 * k, 4 * k):
                if rng.random() < 0.18:
                    d.rectangle([wx, wy, wx + k - 1, wy + k - 1],
                                fill=rng.choice([(255, 200, 120, 255), (230, 220, 200, 255), (160, 190, 255, 255)]))
        x += bw + rng.randint(-4, 3) * k
    return img

def poster(seed, w=96, h=128):
    rng = random.Random(seed)
    bg = rng.choice([(200, 190, 160), (40, 40, 50), (160, 40, 40), (230, 220, 200)])
    img = Image.new('RGBA', (w, h), bg + (255,)); d = ImageDraw.Draw(img)
    fg = (20, 20, 20) if sum(bg) > 400 else (230, 220, 200)
    d.rectangle([8, 10, w - 8, h * 0.55], fill=rng.choice([(90, 60, 50), (40, 60, 90), (30, 30, 30)]) + (255,))
    for i in range(4):
        y = h * 0.6 + i * 10
        d.rectangle([8, y, rng.randint(w // 2, w - 8), y + 5], fill=fg + (255,))
    # torn / weathered
    n = noise(w, h, 10, seed)
    arr = np.asarray(img).copy(); arr[..., :3] = (arr[..., :3] * (0.7 + 0.4 * n[..., None])).clip(0, 255)
    return Image.fromarray(arr)

def murder_board(seed=11, w=512, h=256):
    rng = random.Random(seed)
    img = Image.new('RGBA', (w, h), (218, 220, 214, 255)); d = ImageDraw.Draw(img)
    pins = []
    for i in range(14):
        pw, ph = rng.randint(36, 64), rng.randint(44, 70)
        x, y = rng.randint(10, w - pw - 10), rng.randint(10, h - ph - 10)
        photo = rng.random() < 0.5
        d.rectangle([x, y, x + pw, y + ph], fill=(240, 238, 228, 255) if not photo else (70, 66, 64, 255))
        if photo:
            d.rectangle([x + 3, y + 3, x + pw - 3, y + ph - 14], fill=rng.choice([(120, 110, 100), (90, 96, 104), (140, 120, 100)]) + (255,))
            d.ellipse([x + pw // 2 - 8, y + 10, x + pw // 2 + 8, y + 28], fill=(170, 150, 130, 255))
        else:
            for ly in range(y + 6, y + ph - 4, 5):
                d.line([x + 4, ly, x + pw - rng.randint(5, 20), ly], fill=(90, 90, 100, 255))
        pins.append((x + pw // 2, y + 3))
    for _ in range(9):
        a, b = rng.sample(pins, 2); d.line([a, b], fill=(200, 30, 30, 255), width=2)
    for p in pins: d.ellipse([p[0] - 3, p[1] - 3, p[0] + 3, p[1] + 3], fill=(220, 40, 40, 255))
    # marker scribbles
    f = font('DejaVuSans-Bold.ttf', 20)
    d.text((14, h - 30), 'REYES, D.  - 2 days', font=f, fill=(30, 40, 120, 255))
    d.text((w - 180, 10), 'BLUE NOTE ?', font=f, fill=(160, 20, 20, 255))
    return img

def monitor(seed, w=128, h=80, kind='code'):
    rng = random.Random(seed)
    img = Image.new('RGBA', (w, h), (14, 22, 34, 255)); d = ImageDraw.Draw(img)
    if kind == 'off':
        return Image.new('RGBA', (w, h), (8, 9, 12, 0))
    d.rectangle([0, 0, w, 9], fill=(40, 70, 120, 255))
    for i in range(8):
        y = 14 + i * 8
        d.rectangle([6, y, rng.randint(30, w - 8), y + 3], fill=rng.choice([(150, 190, 230), (120, 160, 200), (200, 200, 210)]) + (255,))
    if kind == 'mug':
        d.rectangle([w - 46, 14, w - 8, 60], fill=(90, 90, 96, 255)); d.ellipse([w - 36, 20, w - 18, 38], fill=(170, 150, 130, 255))
    return img

def blinds_window(seed=12, w=256, h=192, city=True):
    """Window with half-open blinds: albedo blinds, emission from the night city between slats."""
    rng = random.Random(seed)
    sky = skyline(seed, w, h)
    arr = np.asarray(sky).astype(float).copy()
    for y in range(h):
        if (y % 8) < 5:  # slat
            arr[y, :, :3] = np.array([150, 146, 130]) * (0.8 + 0.2 * (y % 8) / 5)
            arr[y, :, 3] = 0
    return Image.fromarray(arr.clip(0, 255).astype(np.uint8), 'RGBA')

def car_plate(w=64, h=32):
    img = Image.new('RGBA', (w, h), (230, 230, 230, 255)); d = ImageDraw.Draw(img)
    d.text((6, 6), '8NSH214', font=font('DejaVuSans-Bold.ttf', 14), fill=(30, 40, 120, 255))
    return img


def bar_interior(seed=13, w=256, h=160):
    """Warm, smoky bar interior seen through the front window."""
    rng = random.Random(seed)
    yy = np.linspace(0, 1, h)[:, None, None]
    a = np.array([150, 80, 40], float) * (1 - yy) + np.array([70, 30, 20], float) * yy
    a = np.broadcast_to(a, (h, w, 3)).copy()
    img = to_img(a); d = ImageDraw.Draw(img)
    # back-bar shelves with bottles
    for sy in (40, 70):
        d.rectangle([20, sy, w - 20, sy + 3], fill=(60, 30, 20, 255))
        x = 24
        while x < w - 24:
            bw = rng.randint(4, 7); bh = rng.randint(12, 22)
            col = rng.choice([(120, 160, 90), (200, 140, 60), (230, 210, 170), (90, 120, 160), (170, 60, 40)])
            d.rectangle([x, sy - bh, x + bw, sy], fill=col + (255,))
            d.rectangle([x + bw // 2 - 1, sy - bh - 5, x + bw // 2 + 1, sy - bh], fill=col + (255,))
            x += bw + rng.randint(2, 5)
    # pendant lamps
    for lx in (50, 128, 206):
        d.line([lx, 0, lx, 14], fill=(30, 20, 15, 255))
        d.ellipse([lx - 10, 12, lx + 10, 24], fill=(255, 220, 150, 255))
    # bar counter + a silhouette on a stool
    d.rectangle([0, 104, w, 160], fill=(40, 18, 12, 255)); d.rectangle([0, 100, w, 106], fill=(110, 60, 30, 255))
    d.ellipse([168, 58, 186, 78], fill=(26, 14, 12, 255)); d.rectangle([162, 76, 194, 112], fill=(26, 14, 12, 255))
    d.line([150, 112, 205, 112], fill=(26, 14, 12, 255), width=3)
    arr = np.asarray(img.filter(ImageFilter.GaussianBlur(1.2))).copy()
    return Image.fromarray(arr)

def billboard(w=320, h=160):
    img = Image.new('RGBA', (w, h), (200, 190, 170, 255)); d = ImageDraw.Draw(img)
    d.rectangle([0, 0, w, h * 0.62], fill=(40, 90, 140, 255))
    d.ellipse([w * 0.62, h * 0.08, w * 0.95, h * 0.58], fill=(230, 200, 120, 255))
    f = font('DejaVuSans-Bold.ttf', 30)
    d.text((14, 18), 'SUNSET', font=f, fill=(250, 240, 220, 255))
    d.text((14, 54), 'INJURY LAW', font=font('DejaVuSans-Bold.ttf', 22), fill=(250, 240, 220, 255))
    d.text((14, h * 0.68), '1-800-555-0199', font=font('DejaVuSans-Bold.ttf', 26), fill=(160, 30, 30, 255))
    n = noise(w, h, 12, 3)
    arr = np.asarray(img).astype(float); arr[..., :3] *= (0.65 + 0.45 * n[..., None])
    return to_img(arr[..., :3])


def hires(img, k=2):
    """Smooth upscale for textures that are drawn small but seen large."""
    return img.resize((img.width * k, img.height * k), Image.LANCZOS)


def lobby(seed=21, w=384, h=256):
    """Precinct lobby seen through the glass doors: cool light, a front desk, a flag, a bench."""
    yy = np.linspace(0, 1, h)[:, None, None]
    a = np.array([150, 170, 180], float) * (1 - yy) * 0.9 + np.array([70, 80, 88], float) * yy
    a = np.broadcast_to(a, (h, w, 3)).copy()
    img = to_img(a); d = ImageDraw.Draw(img)
    for lx in range(30, w, 90):
        d.rectangle([lx, 6, lx + 50, 12], fill=(235, 245, 245, 255))
    d.rectangle([w * 0.25, h * 0.55, w * 0.8, h * 0.78], fill=(70, 60, 54, 255))           # front desk
    d.rectangle([w * 0.25, h * 0.53, w * 0.8, h * 0.56], fill=(120, 110, 100, 255))
    d.rectangle([w * 0.55, h * 0.36, w * 0.6, h * 0.53], fill=(40, 40, 46, 255))            # officer silhouette
    d.ellipse([w * 0.545, h * 0.28, w * 0.605, h * 0.38], fill=(40, 40, 46, 255))
    d.rectangle([w * 0.06, h * 0.2, w * 0.07, h * 0.8], fill=(160, 140, 80, 255))           # flag pole
    d.rectangle([w * 0.07, h * 0.22, w * 0.17, h * 0.36], fill=(40, 50, 90, 255))
    d.rectangle([w * 0.86, h * 0.66, w * 0.98, h * 0.72], fill=(60, 60, 64, 255))           # bench
    return to_img(np.asarray(img.filter(ImageFilter.GaussianBlur(1.0)))[..., :3].astype(float))

def bar_door_glass(w=128, h=96):
    img = to_img(np.broadcast_to(np.array([200, 120, 60], float), (h, w, 3)).copy()); d = ImageDraw.Draw(img)
    for x in range(0, w, 8):   # gathered curtain
        d.rectangle([x, 0, x + 3, h], fill=(150, 80, 40, 255))
    d.ellipse([w * 0.6, h * 0.25, w * 0.8, h * 0.6], fill=(70, 30, 20, 255))
    return to_img(np.asarray(img.filter(ImageFilter.GaussianBlur(1.5)))[..., :3].astype(float))


# ---------------------------------------------------------------- Case 1: Pier 9 and Vance's office
def corrugated(seed=31, w=256, h=256, base=(120, 124, 120), ribs=16, rust=0.35):
    """Ribbed sheet metal (tiling): vertical ribs with streaks of rust and grime."""
    xx = np.linspace(0, 1, w)[None, :]
    rib = 0.75 + 0.25 * np.cos(xx * ribs * 2 * math.pi)
    n = noise(w, h, 24, seed)
    streak = noise(w, h, 6, seed + 1)
    streak = np.clip((noise(w, 4, 3, seed + 2)[1:2, :] - 0.5) * 3, 0, 1) * (0.6 + 0.4 * streak)
    rgb = np.array(base, float)[None, None, :] * (rib * (0.8 + 0.35 * n))[..., None]
    rust_col = np.array([120, 64, 36], float)
    k = np.clip(streak * rust * 1.4, 0, 0.8)[..., None]
    rgb = rgb * (1 - k) + rust_col * k
    return to_img(rgb)

def container_side(color, label, seed=32, w=512, h=192):
    """Side of a shipping container: ribbed paint, a stencilled company name, rust at the seams."""
    base = np.array(color, float)
    rib = 0.78 + 0.22 * np.cos(np.linspace(0, 1, w)[None, :] * 34 * 2 * math.pi)
    n = noise(w, h, 30, seed)
    rgb = base[None, None, :] * (rib * (0.75 + 0.4 * n))[..., None]
    rust = np.clip((noise(w, h, 8, seed + 3) - 0.62) * 4, 0, 1)
    rgb = rgb * (1 - rust[..., None] * 0.6) + np.array([110, 58, 34]) * rust[..., None] * 0.6
    img = to_img(rgb); d = ImageDraw.Draw(img)
    f = font('DejaVuSans-Bold.ttf', 46)
    d.text((40, 54), label, font=f, fill=(226, 222, 210, 230))
    d.rectangle([0, 0, w, 6], fill=(40, 34, 30, 255)); d.rectangle([0, h - 8, w, h], fill=(40, 34, 30, 255))
    return img

def container_end(color, seed=33, w=128, h=128):
    """Container doors: two panels, vertical lock bars."""
    base = np.array(color, float)
    n = noise(w, h, 16, seed)
    img = to_img(base[None, None, :] * (0.7 + 0.4 * n[..., None])); d = ImageDraw.Draw(img)
    d.line([w // 2, 0, w // 2, h], fill=(30, 26, 24, 255), width=3)
    for x in (w * 0.2, w * 0.38, w * 0.62, w * 0.8):
        d.line([x, 6, x, h - 6], fill=(150, 150, 150, 255), width=2)
    return img

def salvage_sign(w=512, h=96):
    img = Image.new('RGBA', (w, h), (214, 206, 186, 255)); d = ImageDraw.Draw(img)
    d.rectangle([4, 4, w - 5, h - 5], outline=(40, 70, 60, 255), width=4)
    f = font('DejaVuSans-Bold.ttf', 34)
    bb = d.textbbox((0, 0), 'HARBOR MARINE SALVAGE', font=f)
    d.text(((w - bb[2]) // 2, (h - bb[3]) // 2 - 4), 'HARBOR MARINE SALVAGE', font=f, fill=(40, 70, 60, 255))
    n = noise(w, h, 10, 5)
    arr = np.asarray(img).astype(float); arr[..., :3] *= (0.6 + 0.5 * n[..., None])
    return to_img(arr[..., :3])

def rezoning_notice(w=120, h=160):
    """A city notice of public hearing, taped to the Blue Note's wall."""
    img = Image.new('RGBA', (w, h), (236, 232, 214, 255)); d = ImageDraw.Draw(img)
    d.rectangle([0, 0, w, 26], fill=(30, 50, 110, 255))
    d.text((8, 4), 'NOTICE', font=font('DejaVuSans-Bold.ttf', 17), fill=(240, 240, 240, 255))
    d.text((8, 32), 'PUBLIC', font=font('DejaVuSans-Bold.ttf', 14), fill=(20, 20, 20, 255))
    d.text((8, 48), 'HEARING', font=font('DejaVuSans-Bold.ttf', 14), fill=(20, 20, 20, 255))
    for i in range(7):
        y = 72 + i * 10
        d.rectangle([8, y, w - 8 - (i % 3) * 14, y + 4], fill=(70, 70, 76, 255))
    d.text((8, h - 22), 'PRYCE DEV.', font=font('DejaVuSans-Bold.ttf', 12), fill=(150, 20, 20, 255))
    n = noise(w, h, 9, 41)
    arr = np.asarray(img).astype(float); arr[..., :3] *= (0.75 + 0.3 * n[..., None])
    return to_img(arr[..., :3])

def markers_wall(seed=34, w=512, h=256):
    """Vance's wall of IOUs: rows of handwritten cards on cork. One, third row fourth from the left, is stamped PAID."""
    rng = random.Random(seed)
    n = noise(w, h, 8, seed)
    cork = np.array([150, 112, 72], float)[None, None, :] * (0.75 + 0.35 * n[..., None])
    img = to_img(cork); d = ImageDraw.Draw(img)
    rows, cols = 4, 9
    cw, ch = 44, 50
    for r in range(rows):
        for c in range(cols):
            x = 14 + c * (cw + 10) + rng.randint(-3, 3)
            y = 12 + r * (ch + 12) + rng.randint(-3, 3)
            paper = rng.choice([(236, 230, 210), (226, 222, 196), (240, 236, 222)])
            d.rectangle([x, y, x + cw, y + ch], fill=paper + (255,))
            for ly in range(y + 8, y + ch - 6, 7):
                d.line([x + 4, ly, x + cw - rng.randint(4, 16), ly], fill=(40, 50, 90, 255), width=1)
            d.ellipse([x + cw // 2 - 3, y - 2, x + cw // 2 + 3, y + 4], fill=(200, 40, 40, 255))
            if (r, c) == (2, 3):
                d.rectangle([x + 3, y + 16, x + cw - 3, y + 34], outline=(200, 20, 20, 255), width=2)
                d.text((x + 6, y + 17), 'PAID', font=font('DejaVuSans-Bold.ttf', 13), fill=(200, 20, 20, 255))
    return img

def boat_photo(w=128, h=96):
    """Framed photo of a sport-fishing boat at sea."""
    img = Image.new('RGBA', (w, h), (40, 30, 20, 255)); d = ImageDraw.Draw(img)
    d.rectangle([8, 8, w - 9, h - 9], fill=(150, 190, 220, 255))
    d.rectangle([8, h * 0.55, w - 9, h - 9], fill=(40, 90, 130, 255))
    d.polygon([(24, h * 0.58), (98, h * 0.58), (88, h * 0.7), (30, h * 0.7)], fill=(236, 236, 230, 255))
    d.rectangle([44, h * 0.38, 76, h * 0.58], fill=(236, 236, 230, 255))
    d.line([60, h * 0.18, 60, h * 0.38], fill=(60, 60, 60, 255), width=2)
    return img

def ledger_cover(w=128, h=96):
    img = Image.new('RGBA', (w, h), (36, 80, 52, 255)); d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 18, h], fill=(26, 56, 36, 255))
    d.rectangle([40, 30, 100, 50], outline=(200, 170, 90, 255), width=2)
    return img
