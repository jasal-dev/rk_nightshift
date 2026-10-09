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

def noise_wrap(w, h, scale, seed=0, octaves=4):
    """Like noise(), but it tiles seamlessly: white noise blurred in the frequency domain, which wraps by nature.
    Use it for textures that repeat over a large surface (triplanar ground), where noise() leaves straight seams."""
    rng = np.random.default_rng(seed)
    fy, fx = np.fft.fftfreq(h)[:, None], np.fft.fftfreq(w)[None, :]
    out = np.zeros((h, w))
    amp, tot = 1.0, 0
    for o in range(octaves):
        sig = max(0.5, scale / (2 ** o) / 2.5)
        n = np.real(np.fft.ifft2(np.fft.fft2(rng.random((h, w))) * np.exp(-2 * (np.pi * sig) ** 2 * (fx ** 2 + fy ** 2))))
        out += np.clip(0.5 + (n - n.mean()) / (n.std() + 1e-9) * 0.18, 0, 1) * amp
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


# ---------------------------------------------------------------- Case 2: Mulholland overlook
def city_basin(seed=81, w=2048, h=512):
    """The LA basin at night seen from the hills: a grid of street lights thinning toward the horizon, boulevards
    converging on it, a freeway, a cluster of downtown towers. Emissive (alpha = light), drawn in perspective."""
    rng = random.Random(seed)
    yy = np.linspace(0, 1, h)[:, None]
    haze = np.clip(1 - yy * 6.0, 0, 1) ** 2                                  # thin glow at the horizon (top)
    rgb = np.zeros((h, w, 3)); rgb[:] = np.array([255, 150, 90])
    a = haze * 0.3 * np.ones((1, w))
    img = to_img(rgb, a * 255); d = ImageDraw.Draw(img)
    hz = 6                                                                    # horizon row
    def row_y(t):                                                             # t: 0 far .. 1 near
        return hz + (h - hz) * t ** 2.2
    for i in range(1, 140):                                                   # rows of street lamps
        t = i / 140
        y = int(row_y(t))
        step = max(2, int(3 + 26 * t))
        size = 1 if t < 0.5 else 2
        bright = rng.random() < 0.12
        for x in range(rng.randint(0, step), w, step):
            if rng.random() < (0.55 if not bright else 0.9):
                col = rng.choice([(255, 190, 110), (255, 170, 90), (230, 230, 255), (255, 220, 160)])
                al = int(150 + 105 * rng.random())
                d.rectangle([x, y, x + size - 1, y + size - 1], fill=col + (al,))
    vx = w * 0.46
    for k in range(-14, 15):                                                  # boulevards
        x1 = vx + k * w * 0.11
        col = rng.choice([(255, 200, 120), (255, 150, 80)])
        for t in np.linspace(0.02, 1, 160):
            x = vx + (x1 - vx) * t ** 2.2 + rng.uniform(-1, 1)
            if rng.random() < 0.6:
                d.point((x, row_y(t)), fill=col + (230,))
    for t in np.linspace(0.15, 1, 70):                                        # a freeway: tail and head lights
        x = w * 0.18 + (w * 0.05) * t ** 2 * 10
        y = row_y(t)
        d.point((x, y), fill=(255, 40, 30, 255)); d.point((x + 3, y), fill=(255, 250, 230, 255))
    x = int(w * 0.62)                                                         # downtown on the horizon
    for _ in range(9):
        bw, bh = rng.randint(6, 16), rng.randint(14, 46)
        d.rectangle([x, hz - bh + 10, x + bw, hz + 10], fill=(20, 16, 24, 255))
        for wy in range(hz - bh + 12, hz + 8, 3):
            for wx in range(x + 1, x + bw - 1, 2):
                if rng.random() < 0.35:
                    d.point((wx, wy), fill=(255, 230, 180, 255))
        x += bw + rng.randint(0, 4)
    # neighbourhoods: lights cluster, hills and parks stay dark
    arr = np.asarray(img).astype(float)
    hood = np.clip((noise(w, h, 140, seed + 5, octaves=3) - 0.32) * 2.2, 0.08, 1.0)
    arr[..., 3] *= np.maximum(hood, (np.linspace(0, 1, h)[:, None] < 0.08))
    return Image.fromarray(arr.clip(0, 255).astype(np.uint8), 'RGBA').filter(ImageFilter.GaussianBlur(0.6))

def night_clouds(seed=82, w=1024, h=256):
    """Low cloud lit orange from underneath by the city. Emissive."""
    n = noise(w, h, 90, seed, octaves=5)
    yy = np.linspace(0, 1, h)[:, None]
    glow = 0.15 + 0.85 * yy ** 2
    rgb = np.dstack([0 * n + 150, 0 * n + 80, 0 * n + 70]) * (0.4 + 0.8 * n[..., None])
    rgb = rgb * glow[..., None] + np.array([30, 24, 50]) * (1 - glow[..., None])
    return to_img(rgb, np.clip(0.35 + 0.65 * glow * (0.6 + 0.6 * n), 0, 1) * 255)

def decomposed_granite(seed=83, w=256, h=256):
    """Pale orange crushed-granite pullout, wet: grit and darker damp patches. Tiles seamlessly."""
    n = noise_wrap(w, h, 40, seed); g = np.random.default_rng(seed).random((h, w))
    rgb = np.array([164, 118, 80], float)[None, None, :] * (0.72 + 0.4 * n[..., None]) * (0.85 + 0.25 * g[..., None])
    damp = np.clip((noise_wrap(w, h, 70, seed + 1) - 0.5) * 3, 0, 1)
    rgb = rgb * (1 - 0.35 * damp[..., None])
    return to_img(rgb)

def stone_wall(seed=84, w=256, h=128):
    """Low wall of rough fieldstone set in mortar."""
    rng = random.Random(seed)
    img = Image.new('RGB', (w, h), (78, 72, 64)); d = ImageDraw.Draw(img)
    y = 0
    while y < h:
        rh = rng.randint(18, 30); x = -rng.randint(0, 30)
        while x < w:
            sw = rng.randint(26, 52)
            c = rng.randint(96, 136)
            d.rounded_rectangle([x + 2, y + 2, x + sw - 2, y + rh - 2], 6, fill=(c, c - 8, c - 20))
            x += sw
        y += rh
    n = noise(w, h, 8, seed)
    arr = np.asarray(img).astype(float) * (0.75 + 0.4 * n[..., None])
    return to_img(arr)

def van_side(w=512, h=192):
    """Coroner's van side panel: white with a blue stripe and the county lettering."""
    img = Image.new('RGBA', (w, h), (214, 216, 218, 255)); d = ImageDraw.Draw(img)
    d.rectangle([0, h * 0.62, w, h * 0.7], fill=(30, 60, 130, 255))
    d.text((40, 40), 'CORONER', font=font('DejaVuSans-Bold.ttf', 52), fill=(30, 40, 70, 255))
    d.text((44, 104), 'COUNTY OF LOS ANGELES', font=font('DejaVuSans-Bold.ttf', 18), fill=(30, 40, 70, 255))
    d.ellipse([w - 120, 30, w - 40, 110], outline=(150, 120, 40, 255), width=6)
    return img

def overlook_sign(w=384, h=128):
    img = Image.new('RGBA', (w, h), (90, 62, 40, 255)); d = ImageDraw.Draw(img)
    d.rectangle([5, 5, w - 6, h - 6], outline=(222, 206, 170, 255), width=3)
    f = font('DejaVuSans-Bold.ttf', 30)
    for i, line in enumerate(('MULHOLLAND', 'SCENIC OVERLOOK')):
        bb = d.textbbox((0, 0), line, font=f)
        d.text(((w - bb[2]) // 2, 18 + i * 46), line, font=f, fill=(232, 218, 184, 255))
    return img

def device_screen(kind, w=128, h=96):
    """Small glowing screens: 'glide' (driver app on a phone), 'radio' (car head unit)."""
    if kind == 'glide':
        img = Image.new('RGBA', (w, h), (10, 24, 26, 255)); d = ImageDraw.Draw(img)
        d.rectangle([0, 0, w, 16], fill=(30, 170, 150, 255))
        for i in range(5):
            d.rectangle([8, 24 + i * 13, w - 20 - (i % 2) * 20, 30 + i * 13], fill=(170, 220, 210, 255))
        return img
    img = Image.new('RGBA', (w, h), (6, 12, 30, 255)); d = ImageDraw.Draw(img)
    d.text((10, 26), '88.1 FM', font=font('DejaVuSans-Bold.ttf', 24), fill=(120, 190, 255, 255))
    d.rectangle([10, 66, w - 10, 70], fill=(60, 110, 200, 255))
    return img

def keyed_scratch(text='RAT', w=384, h=96, seed=7):
    """Letters gouged into car paint with a key: shaky single strokes, dark primer edges, a rust line in the groove.
    Transparent around the strokes so the paint shows through."""
    rng = random.Random(seed)
    strokes = {'R': [[(0, 1), (0, 0), (0.62, 0.02), (0.7, 0.24), (0.55, 0.46), (0, 0.48)], [(0.22, 0.48), (0.75, 1)]],
               'A': [[(0, 1), (0.4, 0), (0.8, 1)], [(0.16, 0.62), (0.66, 0.6)]],
               'T': [[(-0.05, 0.02), (0.85, 0)], [(0.4, 0.0), (0.42, 1)]]}
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    lw, lh, x0, y0 = w * 0.2, h * 0.7, w * 0.08, h * 0.15
    lines = []
    for i, ch in enumerate(text):
        ox = x0 + i * w * 0.3
        for st in strokes[ch]:
            pts = []
            for (a, b), (c, e) in zip(st, st[1:]):
                for t in np.linspace(0, 1, 6)[:-1] if pts else np.linspace(0, 1, 6):
                    x, y = a + (c - a) * t, b + (e - b) * t
                    pts.append((ox + x * lw + (1 - y) * lh * 0.12 + rng.uniform(-1.5, 1.5), y0 + y * lh + rng.uniform(-1.5, 1.5)))
            pts.append((pts[-1][0] + rng.uniform(4, 12), pts[-1][1] + rng.uniform(-3, 3)))       # the key skids on
            lines.append(pts)
    for pts in lines:
        d.line(pts, fill=(88, 86, 84, 255), width=6, joint='curve')
    for pts in lines:
        d.line(pts, fill=(150, 78, 40, 255), width=2, joint='curve')
    return img


def glide_card(w=128, h=80):
    """Kenji's Glide driver card: teal band, photo, five stars."""
    img = Image.new('RGBA', (w, h), (236, 240, 238, 255)); d = ImageDraw.Draw(img)
    d.rectangle([0, 0, w, 18], fill=(30, 150, 134, 255))
    d.text((6, 1), 'GLIDE', font=font('DejaVuSans-Bold.ttf', 14), fill=(255, 255, 255, 255))
    d.rectangle([8, 24, 44, 70], fill=(120, 110, 104, 255))
    d.ellipse([16, 30, 36, 50], fill=(196, 160, 130, 255))
    d.text((52, 26), 'K. OTA', font=font('DejaVuSans-Bold.ttf', 13), fill=(20, 30, 40, 255))
    d.text((52, 46), '4.98 *****', font=font('DejaVuSans-Bold.ttf', 11), fill=(200, 140, 20, 255))
    return img


# ---------------------------------------------------------------- Case 2: Norm's on Sunset
def terrazzo(seed=85, w=256, h=256):
    rng = np.random.default_rng(seed)
    n = noise(w, h, 30, seed)
    rgb = np.array([196, 176, 150], float)[None, None, :] * (0.88 + 0.15 * n[..., None])
    img = to_img(rgb); d = ImageDraw.Draw(img)
    for _ in range(1400):
        x, y = int(rng.integers(0, w)), int(rng.integers(0, h)); r = int(rng.integers(1, 3))
        c = [(150, 60, 40), (60, 60, 64), (230, 226, 214), (190, 120, 60)][int(rng.integers(0, 4))]
        d.ellipse([x, y, x + r, y + r], fill=c + (255,))
    return img

def sunset_street(seed=86, w=512, h=192):
    """Sunset Boulevard through the diner's windows: wet street, car lights, signs across the road. Emissive."""
    rng = random.Random(seed)
    yy = np.linspace(0, 1, h)[:, None, None]
    rgb = np.array([40, 30, 60], float) * (1 - yy) + np.array([60, 40, 40], float) * yy
    rgb = np.broadcast_to(rgb, (h, w, 3)).copy()
    img = to_img(rgb, np.full((h, w), 150)); d = ImageDraw.Draw(img)
    for x in range(0, w, 60):                                                  # buildings across the street
        bh = rng.randint(50, 110)
        d.rectangle([x, h * 0.55 - bh, x + rng.randint(40, 58), h * 0.55], fill=(18, 16, 24, 255))
        if rng.random() < 0.5:
            d.rectangle([x + 6, h * 0.55 - bh + 10, x + 40, h * 0.55 - bh + 22],
                        fill=rng.choice([(255, 80, 120), (90, 200, 255), (255, 200, 90)]) + (255,))
    d.rectangle([0, h * 0.55, w, h], fill=(26, 24, 30, 255))                    # wet street
    for _ in range(14):                                                        # headlights and their reflections
        x = rng.randint(0, w); c = rng.choice([(255, 240, 210), (255, 50, 40), (255, 170, 80)])
        d.ellipse([x, h * 0.62, x + 8, h * 0.62 + 5], fill=c + (255,))
        d.rectangle([x + 2, h * 0.66, x + 5, h * 0.95], fill=c + (90,))
    for x in range(30, w, 140):                                                 # street lamps
        d.rectangle([x, h * 0.1, x + 2, h * 0.55], fill=(30, 30, 36, 255))
        d.ellipse([x - 5, h * 0.08, x + 7, h * 0.13], fill=(255, 190, 120, 255))
    return img.filter(ImageFilter.GaussianBlur(1.2))

def pie_case(w=256, h=192):
    """The lit pie case: three glass shelves of pies."""
    img = Image.new('RGBA', (w, h), (250, 244, 226, 255)); d = ImageDraw.Draw(img)
    for r in range(3):
        y = 20 + r * 60
        d.rectangle([0, y + 40, w, y + 44], fill=(200, 200, 196, 255))
        for c in range(4):
            x = 12 + c * 62
            col = [(150, 30, 40), (200, 150, 80), (240, 220, 120), (120, 70, 40)][(c + r) % 4]
            d.ellipse([x, y + 10, x + 48, y + 40], fill=(190, 140, 80, 255))
            d.ellipse([x + 4, y + 12, x + 44, y + 32], fill=col + (255,))
            if (c + r) % 4 == 2:                                                  # meringue
                d.ellipse([x + 6, y + 2, x + 42, y + 24], fill=(250, 248, 236, 255))
    return img

def jukebox_front(w=96, h=160):
    img = Image.new('RGBA', (w, h), (60, 20, 30, 255)); d = ImageDraw.Draw(img)
    d.pieslice([4, 2, w - 4, 80], 180, 360, fill=(255, 140, 60, 255))
    d.rectangle([4, 40, w - 4, 70], fill=(255, 200, 120, 255))
    for i in range(6):
        d.rectangle([10, 80 + i * 10, w - 10, 85 + i * 10], fill=(255, 230, 190, 255))
    d.rectangle([20, h - 30, w - 20, h - 10], fill=(120, 180, 255, 255))
    return img

def norms_sign(w=512, h=160):
    """Googie sign: NORM'S in red on a white starburst board. Emissive."""
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    d.polygon([(10, h * 0.5), (w * 0.2, 6), (w * 0.85, 14), (w - 6, h * 0.55), (w * 0.8, h - 8), (w * 0.15, h - 14)],
              fill=(250, 240, 220, 200))
    f = font('DejaVuSans-Bold.ttf', 92)
    bb = d.textbbox((0, 0), "NORM'S", font=f)
    d.text(((w - bb[2]) // 2, (h - bb[3]) // 2 - 12), "NORM'S", font=f, fill=(230, 30, 40, 255))
    return img

def menu_board(w=384, h=96):
    img = Image.new('RGBA', (w, h), (30, 26, 24, 255)); d = ImageDraw.Draw(img)
    f = font('DejaVuSans-Bold.ttf', 18)
    for i, t in enumerate(('COFFEE 2.00   PIE 4.75   A LA MODE +1.50', 'OPEN 24 HOURS SINCE 1957')):
        d.text((14, 16 + i * 38), t, font=f, fill=(250, 230, 180, 255))
    return img


# ---------------------------------------------------------------- Case 2: Kenji and Devin's apartment
def floorboards(seed=87, w=256, h=256, base=(120, 84, 54)):
    rng = random.Random(seed)
    img = Image.new('RGB', (w, h), base); d = ImageDraw.Draw(img)
    for i in range(0, w, 32):
        c = tuple(int(v * rng.uniform(0.9, 1.06)) for v in base)
        d.rectangle([i, 0, i + 31, h], fill=c)
        d.line([i, 0, i, h], fill=(60, 40, 26), width=2)
        y = rng.randint(0, h); d.line([i, y, i + 31, y], fill=(70, 48, 30), width=2)
    n = noise(w, h, 6, seed)
    return to_img(np.asarray(img).astype(float) * (0.8 + 0.3 * n[..., None]))

def night_photo(kind, w=192, h=128):
    """Devin's framed night photos of LA: 'freeway', 'bowl', 'overlook'."""
    img = Image.new('RGBA', (w, h), (14, 12, 22, 255)); d = ImageDraw.Draw(img)
    if kind == 'freeway':
        for k in range(40):
            t = k / 40
            d.line([w * 0.1, h, w * (0.3 + t * 0.6), h * 0.35], fill=(255, int(80 + 150 * t), 60, 255), width=1)
            d.line([w * 0.3, h, w * (0.35 + t * 0.6), h * 0.38], fill=(250, 240, 220, 255), width=1)
    elif kind == 'bowl':
        d.pieslice([w * 0.2, h * 0.3, w * 0.8, h * 0.95], 180, 360, fill=(240, 236, 220, 255))
        for i in range(5):
            d.arc([w * (0.22 + i * 0.03), h * (0.33 + i * 0.03), w * (0.78 - i * 0.03), h * 0.95], 180, 360,
                  fill=(160, 150, 200, 255), width=1)
        d.rectangle([0, h * 0.9, w, h], fill=(30, 26, 40, 255))
    else:                                                                       # the overlook: wall, city below
        sub = city_basin(seed=88, w=w * 4, h=h * 2).resize((w, h // 2))
        img.paste(sub, (0, h // 3), sub)
        d.rectangle([0, h * 0.8, w, h], fill=(70, 60, 50, 255))
    return img

def hushhush_printout(w=128, h=160):
    img = Image.new('RGBA', (w, h), (240, 238, 232, 255)); d = ImageDraw.Draw(img)
    d.rectangle([0, 0, w, 24], fill=(220, 30, 120, 255))
    d.text((6, 3), 'HushHush', font=font('DejaVuSans-Bold.ttf', 16), fill=(255, 255, 255, 255))
    d.text((6, 30), "STUDIO ASSISTANT'S", font=font('DejaVuSans-Bold.ttf', 9), fill=(20, 20, 20, 255))
    d.text((6, 42), 'BACK-SEAT MELTDOWN', font=font('DejaVuSans-Bold.ttf', 9), fill=(20, 20, 20, 255))
    d.rectangle([6, 58, w - 6, 118], fill=(70, 80, 90, 255))                   # cabin-camera still
    d.ellipse([46, 70, 76, 100], fill=(170, 140, 120, 255))
    for i in range(4):
        d.rectangle([6, 126 + i * 8, w - 20, 129 + i * 8], fill=(90, 90, 96, 255))
    d.rectangle([w - 46, 6, w - 8, 18], fill=(255, 230, 80, 255))               # yellow sticky note
    return img

def certificate(w=192, h=128):
    img = Image.new('RGBA', (w, h), (240, 236, 222, 255)); d = ImageDraw.Draw(img)
    d.rectangle([6, 6, w - 7, h - 7], outline=(30, 150, 134, 255), width=4)
    d.text((24, 18), 'GLIDE', font=font('DejaVuSans-Bold.ttf', 22), fill=(30, 150, 134, 255))
    d.text((24, 50), 'DRIVER OF THE MONTH', font=font('DejaVuSans-Bold.ttf', 13), fill=(40, 40, 50, 255))
    d.text((24, 76), '* * * * *', font=font('DejaVuSans-Bold.ttf', 18), fill=(210, 160, 30, 255))
    return img

def pennant(w=192, h=64):
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    d.polygon([(0, 0), (w, h // 2), (0, h)], fill=(20, 60, 150, 255))
    d.text((12, h // 2 - 12), 'DODGERS', font=font('DejaVuSerif-BoldItalic.ttf', 20), fill=(250, 250, 250, 255))
    return img

def fridge_door(seed=89, w=128, h=256):
    """An old round-cornered fridge, covered in magnets and takeout menus, Kenji's note in the middle."""
    rng = random.Random(seed)
    img = Image.new('RGBA', (w, h), (222, 218, 200, 255)); d = ImageDraw.Draw(img)
    d.line([0, h * 0.32, w, h * 0.32], fill=(150, 146, 130, 255), width=3)    # freezer seam
    d.rectangle([w - 14, h * 0.1, w - 8, h * 0.26], fill=(180, 180, 176, 255))
    d.rectangle([w - 14, h * 0.4, w - 8, h * 0.6], fill=(180, 180, 176, 255))
    for _ in range(9):
        x, y = rng.randint(6, w - 50), rng.randint(int(h * 0.36), h - 50)
        d.rectangle([x, y, x + rng.randint(26, 40), y + rng.randint(30, 44)],
                    fill=rng.choice([(250, 250, 240), (250, 220, 120), (240, 170, 160), (190, 220, 250)]) + (255,))
        d.ellipse([x + 8, y - 3, x + 16, y + 5], fill=rng.choice([(200, 40, 40), (40, 120, 200), (40, 160, 70)]) + (255,))
    d.rectangle([36, h * 0.5, 92, h * 0.62], fill=(255, 240, 120, 255))       # Kenji's note
    for i in range(3):
        d.line([40, h * 0.52 + 8 + i * 7, 86, h * 0.52 + 8 + i * 7], fill=(40, 40, 90, 255), width=1)
    return img

def dashcam_box(w=96, h=96):
    img = Image.new('RGBA', (w, h), (30, 32, 36, 255)); d = ImageDraw.Draw(img)
    d.text((8, 10), 'DuoCam 2', font=font('DejaVuSans-Bold.ttf', 15), fill=(240, 240, 240, 255))
    d.rectangle([14, 40, 82, 80], fill=(60, 64, 72, 255)); d.ellipse([30, 46, 58, 74], fill=(10, 10, 14, 255))
    return img

def laptop_screen(w=128, h=80):
    img = Image.new('RGBA', (w, h), (30, 30, 34, 255)); d = ImageDraw.Draw(img)
    d.rectangle([0, 0, w, 8], fill=(60, 60, 66, 255))
    for i in range(3):
        for j in range(2):
            d.rectangle([24 + i * 34, 14 + j * 32, 52 + i * 34, 40 + j * 32],
                        fill=[(230, 220, 200), (200, 170, 150), (240, 236, 230)][(i + j) % 3] + (255,))
    d.rectangle([2, 12, 18, h - 4], fill=(44, 44, 50, 255))
    return img


# ---------------------------------------------------------------- Case 2: squad room board pins
def board_pins(kind, w=96, h=128):
    """Pinned paper for the murder board: 'kenji' (Glide card, card slip, Polaroid of the cards, a marker line
    through it all), 'envelope' (Danny's '1 of 3'), 'receipt' (print of Walt B.'s ride)."""
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    if kind == 'kenji':
        img.paste(glide_card().resize((w - 10, 46)), (2, 4))
        d.rectangle([8, 54, 46, 120], fill=(240, 238, 228, 255))               # card slip
        for i in range(5):
            d.line([12, 62 + i * 9, 40, 62 + i * 9], fill=(90, 90, 110, 255))
        d.rectangle([52, 58, 92, 110], fill=(246, 246, 240, 255))              # Polaroid of the cards
        d.rectangle([56, 62, 88, 94], fill=(40, 50, 60, 255))
        for i in range(4):
            d.rectangle([59 + i * 7, 70, 63 + i * 7, 80], fill=(200, 60, 60, 255))
        d.line([0, h - 4, w, 6], fill=(30, 30, 30, 255), width=3)
        pins = ((w // 2, 6), (26, 56), (72, 60))
    elif kind == 'envelope':
        d.rectangle([6, 30, w - 6, 90], fill=(206, 212, 226, 255))
        d.polygon([(6, 30), (w // 2, 62), (w - 6, 30)], outline=(150, 156, 170, 255))
        d.text((24, 66), '1 of 3', font=font('DejaVuSans-Bold.ttf', 14), fill=(30, 40, 120, 255))
        d.ellipse([w - 30, 26, w - 2, 46], fill=(60, 40, 28, 255))
        pins = ((w // 2, 34),)
    elif kind == 'gus':
        d.rectangle([6, 6, 50, 62], fill=(246, 246, 240, 255))                     # Polaroid of the dripping prop
        d.rectangle([10, 10, 46, 48], fill=(30, 34, 44, 255))
        d.rectangle([25, 18, 31, 42], fill=(220, 176, 70, 255))
        d.ellipse([23, 13, 33, 21], fill=(220, 176, 70, 255))
        d.rectangle([21, 42, 35, 46], fill=(150, 110, 40, 255))
        d.rectangle([56, 10, 90, 54], fill=(210, 220, 226, 200))                  # the earring in its evidence bag
        d.rectangle([56, 10, 90, 16], fill=(200, 40, 40, 255))
        cx, cy = 73, 36
        star = [(cx + (9 if i % 2 == 0 else 4) * math.sin(i * math.pi / 5), cy - (9 if i % 2 == 0 else 4) * math.cos(i * math.pi / 5))
                for i in range(10)]
        d.polygon(star, fill=(226, 180, 70, 255))
        d.rectangle([14, 68, 84, 122], fill=(240, 238, 230, 255))                 # the catalogue page, Gus's red ink
        d.rectangle([20, 74, 46, 100], fill=(60, 50, 40, 255))
        for i in range(3):
            d.rectangle([50, 76 + i * 8, 80, 79 + i * 8], fill=(90, 90, 100, 255))
        d.text((20, 104), '734??', font=font('DejaVuSans-Bold.ttf', 12), fill=(190, 20, 20, 255))
        d.line([0, 8, w, h - 6], fill=(30, 30, 30, 255), width=3)                 # a line through the case
        pins = ((28, 8), (73, 12), (49, 70))
    elif kind == 'brenner':
        d.rectangle([8, 40, w - 8, 92], fill=(236, 228, 206, 255))                 # Walter Brenner's card
        d.text((14, 46), 'WALTER BRENNER', font=font('DejaVuSerif-Bold.ttf', 10), fill=(30, 50, 120, 255))
        d.text((14, 62), 'LAPD (Ret.)', font=font('DejaVuSerif.ttf', 9), fill=(30, 50, 120, 255))
        d.text((14, 74), 'Pryce Development', font=font('DejaVuSerif.ttf', 8), fill=(30, 50, 120, 255))
        pins = ((w // 2, 44),)
    elif kind == 'owen':
        d.rectangle([6, 8, 58, 66], fill=(246, 246, 240, 255))                     # Polaroid of the fitted headlight
        d.rectangle([10, 12, 54, 52], fill=(70, 82, 96, 255))
        d.rounded_rectangle([14, 24, 50, 42], radius=6, fill=(190, 200, 210, 255))
        for k in range(4):
            d.ellipse([18 + k * 7, 29, 26 + k * 7, 37], outline=(250, 250, 250, 255))
        d.line([24, 24, 30, 33, 26, 42], fill=(240, 240, 240, 255))               # the crack where the pieces join
        d.rectangle([62, 14, 90, 70], fill=(236, 232, 214, 255))                    # valet ticket No. 47
        d.rectangle([62, 14, 90, 22], fill=(150, 30, 36, 255))
        d.text((66, 26), '47', font=font('DejaVuSans-Bold.ttf', 12), fill=(30, 30, 40, 255))
        for i in range(3):
            d.rectangle([66, 44 + i * 7, 86, 46 + i * 7], fill=(90, 90, 110, 255))
        d.rectangle([16, 76, 80, 120], fill=(240, 196, 30, 255))                    # a Chomp receipt, yellow
        for i in range(4):
            d.rectangle([22, 84 + i * 8, 72 - (i % 2) * 12, 87 + i * 8], fill=(40, 34, 20, 255))
        d.line([0, 6, w, h - 8], fill=(30, 30, 30, 255), width=3)                   # a line through the case
        pins = ((32, 10), (76, 16), (48, 78))
    elif kind == 'phone':
        d.rectangle([10, 14, w - 10, h - 14], fill=(244, 244, 240, 255))           # the lab's evidence receipt
        d.rectangle([10, 14, w - 10, 30], fill=(30, 50, 110, 255))
        d.text((16, 36), 'ITEM 1', font=font('DejaVuSans-Bold.ttf', 11), fill=(30, 30, 40, 255))
        for i in range(5):
            d.rectangle([16, 56 + i * 9, w - 18 - (i % 3) * 10, 59 + i * 9], fill=(80, 80, 96, 255))
        d.text((16, 100), 'I. Feld', font=font('DejaVuSerif-Italic.ttf', 11), fill=(30, 50, 120, 255))
        pins = ((w // 2, 18),)
    elif kind == 'invite':
        d.rectangle([6, 20, w - 6, h - 20], fill=(236, 230, 214, 255))             # folded open on the watercolour
        d.rectangle([10, 24, w - 10, 70], fill=(170, 200, 226, 255))
        d.polygon([(44, 100), (70, 100), (66, 24), (48, 24)], fill=(110, 160, 200, 255))   # the tower
        d.polygon([(14, 86), (40, 86), (36, 76), (18, 76)], fill=(70, 130, 110, 255))      # the theatre's pagoda
        d.rectangle([38, 92, 76, 102], fill=(250, 220, 150, 255))                         # the lobby
        d.line([w // 2, 20, w // 2, h - 20], fill=(200, 190, 170, 255), width=1)            # the fold
        pins = ((w // 2, 24),)
    elif kind == 'walt':
        d.rectangle([4, 6, w - 4, 50], fill=(246, 244, 236, 255))                    # the index card, turned over
        d.line([4, 16, w - 4, 16], fill=(200, 80, 80, 255))
        d.text((8, 20), 'WALT BRENNER', font=font('DejaVuSans-Bold.ttf', 11), fill=(20, 24, 60, 255))
        d.text((8, 36), 'for H. PRYCE, T. HASKELL', font=font('DejaVuSans.ttf', 7), fill=(20, 24, 60, 255))
        d.rectangle([6, 58, 52, 112], fill=(246, 246, 240, 255))                     # photo of the tab book page
        d.rectangle([10, 62, 48, 100], fill=(60, 96, 70, 255))
        for i in range(4):
            d.rectangle([13, 66 + i * 8, 44, 68 + i * 8], fill=(230, 226, 210, 255))
        d.text((12, 100), '3:20 W.B.', font=font('DejaVuSans-Bold.ttf', 8), fill=(30, 30, 40, 255))
        d.rectangle([58, 64, 92, 96], fill=(30, 34, 60, 255))                        # Sal's bar card: a cocktail glass
        d.polygon([(66, 70), (84, 70), (75, 80)], fill=(220, 190, 110, 255))
        d.line([75, 80, 75, 88], fill=(220, 190, 110, 255)); d.line([70, 88, 80, 88], fill=(220, 190, 110, 255))
        pins = ((w // 2, 10), (29, 60), (75, 66))
    elif kind == 'bare':
        img = Image.new('RGBA', (w, h), (214, 216, 208, 255)); d = ImageDraw.Draw(img)
        rng = random.Random(5)
        for _ in range(14):                                                        # the holes where the pins were
            x, y = rng.randint(6, w - 6), rng.randint(6, h - 6)
            d.ellipse([x - 1, y - 1, x + 1, y + 1], fill=(120, 116, 110, 255))
        for _ in range(5):                                                         # lighter squares where paper hung
            x, y = rng.randint(4, w - 40), rng.randint(4, h - 50)
            d.rectangle([x, y, x + rng.randint(20, 36), y + rng.randint(26, 44)], fill=(226, 228, 222, 255))
        pins = ()
    else:
        d.rectangle([14, 10, w - 14, h - 10], fill=(244, 244, 240, 255))
        d.rectangle([20, 16, w - 20, 34], fill=(30, 150, 134, 255))
        for i in range(4):
            d.rectangle([22, 44 + i * 11, w - 24 - (i % 2) * 12, 48 + i * 11], fill=(70, 70, 80, 255))
        d.text((20, 88), 'BILLED TO', font=font('DejaVuSans-Bold.ttf', 9), fill=(40, 40, 50, 255))
        d.text((20, 100), 'PRYCE DEV.', font=font('DejaVuSans-Bold.ttf', 11), fill=(150, 20, 20, 255))
        pins = ((w // 2, 14),)
    for x, y in pins:
        d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=(220, 40, 40, 255))
    return img


# ---------------------------------------------------------------- Case 3: Stardust Memorabilia, Hollywood Boulevard
def checker_floor(seed=91, w=256, h=256, tile=64):
    """Old shop floor: black and cream linoleum squares, worn and scuffed."""
    a = np.zeros((h, w, 3))
    rng = np.random.default_rng(seed)
    for ty in range(h // tile):
        for tx_ in range(w // tile):
            base = np.array([214, 204, 180]) if (tx_ + ty) % 2 == 0 else np.array([34, 32, 34])
            a[ty * tile:(ty + 1) * tile, tx_ * tile:(tx_ + 1) * tile] = base * rng.uniform(0.9, 1.05)
    n = noise(w, h, 12, seed)
    a *= (0.82 + 0.3 * n[..., None]); a[::tile, :] *= 0.75; a[:, ::tile] *= 0.75
    return to_img(a)


def walk_star(seed=92, w=256, h=256):
    """A Walk of Fame square on the sidewalk: charcoal terrazzo around a coral-pink star with a brass rim and a little
    brass emblem. One star per tile; the sidewalk repeats it."""
    n = noise(w, h, 3, seed, 2); g = np.random.default_rng(seed).random((h, w))
    a = np.array([52, 50, 54], float)[None, None, :] * (0.8 + 0.3 * n[..., None]) * (0.9 + 0.2 * g[..., None])
    m = int(w * 0.14)
    a[m:h - m, m:w - m] = (np.array([150, 66, 68]) * (0.85 + 0.25 * n[m:h - m, m:w - m, None])
                           * (0.92 + 0.15 * g[m:h - m, m:w - m, None]))
    img = to_img(a); d = ImageDraw.Draw(img)
    cx, cy, R, r = w / 2, h / 2 - 8, w * 0.27, w * 0.11
    pts = [(cx + (R if i % 2 == 0 else r) * math.sin(i * math.pi / 5),
            cy - (R if i % 2 == 0 else r) * math.cos(i * math.pi / 5)) for i in range(10)]
    d.polygon(pts, fill=(196, 104, 104, 255))
    d.line(pts + [pts[0]], fill=(206, 168, 90, 255), width=4)
    d.ellipse([cx - 16, cy - 10, cx + 16, cy + 16], fill=(200, 160, 84, 255))
    for k in range(2):
        d.rectangle([cx - 46, h - m - 40 + k * 14, cx + 46, h - m - 34 + k * 14], fill=(196, 160, 86, 255))
    d.line([0, 1, w, 1], fill=(26, 24, 26, 255), width=3)
    d.line([1, 0, 1, h], fill=(26, 24, 26, 255), width=3)
    return img


# the wall of fame, 4 x 3; the named ones are the three fakes that glow under UV
SIGNED = [('Bogart', (40, 40, 44)), ('Lyle Brandt', (46, 40, 36)), ('Monroe', (60, 56, 56)), ('', (34, 36, 40)),
          ('', (50, 46, 42)), ('', (38, 38, 46)), ('', (48, 44, 44)), ('', (40, 44, 40)),
          ('', (44, 40, 40)), ('', (36, 34, 38)), ('', (52, 48, 46)), ('', (40, 40, 40))]


def _portrait(d, x0, y0, x1, y1, seed, bg, hat=False):
    """A black-and-white studio portrait: a soft-lit head and shoulders on a dark ground (drawn into its own small
    image, softened, and pasted, so it reads as a photograph rather than a drawing)."""
    rng = random.Random(seed)
    w, h = int(x1 - x0), int(y1 - y0)
    im = Image.new('RGBA', (w, h), bg + (255,)); g = ImageDraw.Draw(im)
    g.ellipse([w * 0.1, -h * 0.1, w * 0.9, h * 0.7], fill=tuple(min(255, c + 26) for c in bg) + (255,))   # backlight
    cx = w / 2 + rng.uniform(-w * 0.08, w * 0.08)
    tone = rng.randint(160, 210)
    sy = h * 0.7
    suit = (int(tone * 0.5),) * 3 + (255,)
    g.chord([cx - w * 0.46, sy, cx + w * 0.46, sy + 2 * (h - sy)], 180, 360, fill=suit)                # suit
    g.polygon([(cx - w * 0.08, sy), (cx + w * 0.08, sy), (cx, h)], fill=(tone - 20,) * 3 + (255,))        # collar
    g.rectangle([cx - w * 0.1, h * 0.55, cx + w * 0.1, sy + 4], fill=(tone - 40,) * 3 + (255,))            # neck
    hw, ht = w * rng.uniform(0.17, 0.21), h * 0.2
    g.ellipse([cx - hw, ht, cx + hw, h * 0.62], fill=(tone,) * 3 + (255,))                                 # face
    g.chord([cx - hw, ht, cx + hw, h * 0.62], 300, 60, fill=(tone - 30,) * 3 + (255,))                       # shadow side
    hair = rng.choice([(24, 24, 24), (214, 210, 196), (64, 60, 56)])
    g.chord([cx - hw * 1.1, ht - h * 0.05, cx + hw * 1.1, h * 0.46], 180, 360, fill=hair + (255,))
    if hat:                                                                       # a fedora
        g.rectangle([cx - hw * 1.0, ht - h * 0.12, cx + hw * 1.0, ht + h * 0.04], fill=(30, 30, 30, 255))
        g.ellipse([cx - hw * 1.7, ht + h * 0.0, cx + hw * 1.7, ht + h * 0.09], fill=(24, 24, 24, 255))
    im = im.filter(ImageFilter.GaussianBlur(max(0.8, w / 90)))
    d._image.paste(im, (int(x0), int(y0)))


def _signature(d, x0, y0, x1, y1, seed, color, width=2):
    """A slanted autograph across the bottom of a photo: two words of uneven cursive loops (a tall capital, then
    smaller letters), and a flourish underneath."""
    rng = random.Random(seed)
    H = y1 - y0
    words = [rng.randint(3, 5), rng.randint(4, 7)]
    total = sum(words) + 1.5
    unit = (x1 - x0) / total
    x, pts_all = x0, []
    for wi, letters in enumerate(words):
        pts = []
        for li in range(letters):
            lw = unit * rng.uniform(0.7, 1.2)
            tall = H * (1.1 if li == 0 else rng.uniform(0.35, 0.7))
            for j in range(10):
                t = j / 9
                f = t * 2 * math.pi
                px = x + lw * t - lw * 0.35 * math.sin(f)
                py = y1 - H * 0.2 - tall * (0.5 - 0.5 * math.cos(f)) - (px - x0) * 0.12
                pts.append((px + (y1 - py) * 0.25, py))
            x += lw
        pts_all.append(pts)
        x += unit * 1.2
    for pts in pts_all:
        d.line(pts, fill=color, width=width, joint='curve')
    d.line([(x0 + (x1 - x0) * 0.1, y1 + H * 0.05), (x1, y1 - H * 0.25)], fill=color, width=max(1, width - 1))


def _frames(w, h):
    cols, rows = 4, 3
    fw, fh, k = w / cols, h / rows, w / 512
    for i in range(cols * rows):
        c, r = i % cols, i // cols
        x0, y0 = c * fw + (10 + (r % 2) * 4) * k, r * fh + 8 * k
        yield i, x0, y0, x0 + fw - 24 * k, y0 + fh - 18 * k


def signed_wall(w=512, h=320, uv=False):
    """Gus's wall of fame: twelve signed studio portraits in cheap gold frames, 4 x 3, on a transparent ground.
    With uv=True, the same wall under the UV lamp: violet and dark, and the three fakes (Bogart, Lyle Brandt, Monroe)
    glowing gold, the modern paint pen lighting up like a premiere."""
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    for i, x0, y0, x1, y1 in _frames(w, h):
        k = w / 512
        d.rectangle([x0, y0, x1, y1], fill=(176, 140, 60, 255))                    # gold frame
        d.rectangle([x0 + 3 * k, y0 + 3 * k, x1 - 3 * k, y1 - 3 * k], fill=(120, 92, 40, 255))
        _portrait(d, x0 + 7 * k, y0 + 7 * k, x1 - 7 * k, y1 - 7 * k, 100 + i, SIGNED[i][1], hat=SIGNED[i][0] == 'Bogart')
        _signature(d, x0 + 14 * k, y1 - 30 * k, x1 - 14 * k, y1 - 12 * k, 300 + i, (236, 232, 220, 255), int(2 * k))
    if not uv:
        return img
    a = np.asarray(img).astype(float)
    lum = a[..., :3].mean(-1, keepdims=True)
    a[..., :3] = lum * np.array([0.32, 0.18, 0.62]) + np.array([8, 0, 24])
    img = Image.fromarray(a.clip(0, 255).astype(np.uint8))
    glow = Image.new('RGBA', (w, h), (0, 0, 0, 0)); gd = ImageDraw.Draw(glow)
    for i, x0, y0, x1, y1 in _frames(w, h):
        if SIGNED[i][0]:
            k = w / 512
            _signature(gd, x0 + 14 * k, y1 - 30 * k, x1 - 14 * k, y1 - 12 * k, 300 + i, (255, 214, 120, 255), int(4 * k))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(6 * w / 512)))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(2 * w / 512)))
    img.alpha_composite(glow)
    return img


def academy_certificate(w=192, h=256):
    img = Image.new('RGBA', (w, h), (232, 222, 196, 255)); d = ImageDraw.Draw(img)
    d.rectangle([5, 5, w - 6, h - 6], outline=(150, 120, 60, 255), width=3)
    d.rectangle([11, 11, w - 12, h - 12], outline=(150, 120, 60, 255), width=1)
    f, fb = font('DejaVuSerif.ttf', 11), font('DejaVuSerif-Bold.ttf', 14)
    lines = [('CERTIFICATE', fb, 24), ('OF PROVENANCE', f, 44), ('Academy Award statuette', f, 74),
             ('Best Supporting Actor, 1954', f, 92), ('LYLE BRANDT', fb, 116), ('Harbor Lights', f, 138),
             ('Base serial No. 734', fb, 166), ('From the Brandt estate, 1988', f, 192)]
    for text, fn, y in lines:
        bb = d.textbbox((0, 0), text, font=fn)
        d.text(((w - bb[2]) / 2, y), text, font=fn, fill=(50, 40, 30, 255))
    d.ellipse([w / 2 - 14, h - 46, w / 2 + 14, h - 18], fill=(160, 40, 40, 255))  # wax seal
    return img


def brass_plate(w=256, h=72):
    img = Image.new('RGBA', (w, h), (190, 150, 72, 255)); d = ImageDraw.Draw(img)
    d.rectangle([3, 3, w - 4, h - 4], outline=(120, 90, 40, 255), width=2)
    for text, y, sz in (('LYLE BRANDT', 8, 18), ('BEST SUPPORTING ACTOR, 1954', 32, 12), ('HARBOR LIGHTS', 48, 12)):
        fn = font('DejaVuSerif-Bold.ttf', sz)
        bb = d.textbbox((0, 0), text, font=fn)
        d.text(((w - bb[2]) / 2, y), text, font=fn, fill=(60, 40, 16, 255))
    return img


def chair_back(w=256, h=72):
    """Director's chair canvas: STARDUST stencilled in white."""
    img = Image.new('RGBA', (w, h), (30, 30, 34, 255)); d = ImageDraw.Draw(img)
    fn = font('DejaVuSans-Bold.ttf', 40)
    bb = d.textbbox((0, 0), 'STARDUST', font=fn)
    d.text(((w - bb[2]) / 2, (h - bb[3]) / 2 - 4), 'STARDUST', font=fn, fill=(226, 222, 210, 255))
    return img


def movie_poster(title, sub, colors, seed=0, w=128, h=192):
    """A one-sheet: a painted scene in two colours, the title in big letters, small credits."""
    rng = random.Random(seed)
    bg, fg = colors
    img = Image.new('RGBA', (w, h), bg + (255,)); d = ImageDraw.Draw(img)
    for i in range(6):
        y = h * 0.1 + i * 12
        x0 = rng.uniform(-30, w - 40)
        d.ellipse([x0, y, x0 + rng.uniform(50, 110), y + rng.uniform(30, 70)], fill=tuple(int(c * 0.7) for c in bg) + (255,))
    d.ellipse([w * 0.3, h * 0.18, w * 0.7, h * 0.48], fill=(220, 190, 160, 255))
    d.ellipse([w * 0.18, h * 0.42, w * 0.82, h * 0.82], fill=tuple(int(c * 0.4) for c in bg) + (255,))
    for size in range(18, 8, -1):
        fn = font('DejaVuSerif-Bold.ttf', size)
        bb = d.textbbox((0, 0), title, font=fn)
        if bb[2] < w - 10:
            break
    d.text(((w - bb[2]) / 2, h * 0.8), title, font=fn, fill=fg + (255,))
    fs = font('DejaVuSans.ttf', 9)
    bb = d.textbbox((0, 0), sub, font=fs)
    d.text(((w - bb[2]) / 2, h * 0.92), sub, font=fs, fill=fg + (255,))
    return img


def theatre_front(seed=93, w=512, h=256):
    """The Chinese Theatre across the boulevard after hours: a deep red facade, faintly floodlit, over the big dark
    entrance (alpha marks how much of it glows)."""
    yy = np.linspace(0, 1, h)[:, None, None]
    a = np.zeros((h, w, 3)) + np.array([110, 34, 26]) * (0.35 + 0.8 * yy)
    glow = (20 + 50 * yy[..., 0]) * np.ones((1, w))
    img = to_img(a, glow); d = ImageDraw.Draw(img)
    d.rectangle([w * 0.36, h * 0.34, w * 0.64, h], fill=(14, 8, 8, 0))               # the entrance, dark
    d.polygon([(w * 0.36, h * 0.34), (w * 0.5, h * 0.2), (w * 0.64, h * 0.34)], fill=(40, 90, 70, 60))
    return img


def tape_band(w=256, h=32):
    img = Image.new('RGBA', (w, h), (230, 196, 30, 255)); d = ImageDraw.Draw(img)
    fn = font('DejaVuSans-Bold.ttf', 18)
    for x in range(0, w, 128):
        d.text((x + 6, 6), 'POLICE LINE', font=fn, fill=(20, 20, 20, 255))
    return img


# ---------------------------------------------------------------- Case 3: the back office and the roof
def fuse_panel(w=192, h=256):
    """Gus's old fuse panel: grey steel, a row of black breakers with masking-tape labels in his capitals, and a
    clockwork timer dial on the ROOF SIGN circuit."""
    img = Image.new('RGBA', (w, h), (120, 124, 128, 255)); d = ImageDraw.Draw(img)
    d.rectangle([4, 4, w - 5, h - 5], outline=(70, 72, 76, 255), width=3)
    f = font('DejaVuSans-Bold.ttf', 11)
    for i, label in enumerate(('SHOP', 'OFFICE', 'FRIDGE (NEVER)', 'ROOF SIGN')):
        y = 24 + i * 52
        d.rectangle([16, y, 40, y + 30], fill=(24, 24, 26, 255))                   # breaker
        d.rectangle([22, y + 4, 34, y + 14], fill=(200, 200, 196, 255))
        d.rectangle([50, y + 6, w - 14, y + 24], fill=(226, 212, 160, 255))        # masking tape
        d.text((54, y + 8), label, font=f, fill=(30, 30, 40, 255))
    d.text((54, 24 + 3 * 52 + 26), 'TIMER OFF AT 1', font=font('DejaVuSans-Bold.ttf', 9), fill=(30, 30, 40, 255))
    d.text((54, 24 + 3 * 52 + 38), '($$$!)', font=font('DejaVuSans-Bold.ttf', 9), fill=(160, 30, 30, 255))
    cx, cy = w - 40, h - 32
    d.ellipse([cx - 20, cy - 20, cx + 20, cy + 20], fill=(230, 226, 214, 255), outline=(40, 40, 40, 255), width=2)
    d.line([cx, cy, cx - 6, cy - 16], fill=(160, 30, 30, 255), width=3)          # set to 1:00
    return img


def tape_label(text, w=128, h=32):
    """A strip of masking tape with a name on it in black marker."""
    img = Image.new('RGBA', (w, h), (222, 206, 156, 255)); d = ImageDraw.Draw(img)
    fn = font('DejaVuSans-Bold.ttf', 20)
    bb = d.textbbox((0, 0), text, font=fn)
    d.text(((w - bb[2]) / 2, (h - bb[3]) / 2 - 3), text, font=fn, fill=(24, 24, 28, 255))
    return img


def pryce_letter(w=128, h=168):
    """Pryce Development's final notice: letterhead, a red FINAL NOTICE, lines of type, a certified-mail stamp."""
    img = Image.new('RGBA', (w, h), (240, 238, 230, 255)); d = ImageDraw.Draw(img)
    d.text((8, 6), 'PRYCE', font=font('DejaVuSans-Bold.ttf', 14), fill=(40, 50, 80, 255))
    d.text((8, 22), 'DEVELOPMENT', font=font('DejaVuSans.ttf', 8), fill=(40, 50, 80, 255))
    d.line([8, 34, w - 8, 34], fill=(40, 50, 80, 255), width=1)
    d.text((8, 42), 'FINAL NOTICE', font=font('DejaVuSans-Bold.ttf', 11), fill=(170, 30, 30, 255))
    d.text((8, 55), 'TO VACATE', font=font('DejaVuSans-Bold.ttf', 11), fill=(170, 30, 30, 255))
    for i in range(9):
        d.rectangle([8, 74 + i * 8, w - 8 - (i % 3) * 14, 77 + i * 8], fill=(90, 90, 100, 255))
    d.rectangle([w - 50, h - 34, w - 8, h - 10], outline=(60, 60, 150, 255), width=2)  # certified mail stamp
    return img


def catalogue_cover(w=128, h=168):
    img = Image.new('RGBA', (w, h), (20, 20, 24, 255)); d = ImageDraw.Draw(img)
    d.text((10, 10), "CALLOWAY'S", font=font('DejaVuSerif-Bold.ttf', 15), fill=(212, 180, 100, 255))
    d.text((10, 30), 'Beverly Hills', font=font('DejaVuSerif.ttf', 9), fill=(212, 180, 100, 255))
    d.rectangle([20, 50, w - 20, h - 40], fill=(60, 50, 40, 255))
    d.ellipse([w / 2 - 8, 62, w / 2 + 8, 78], fill=(220, 180, 80, 255))         # a gold statuette on the cover
    d.rectangle([w / 2 - 5, 78, w / 2 + 5, 112], fill=(220, 180, 80, 255))
    d.rectangle([w / 2 - 12, 112, w / 2 + 12, 120], fill=(30, 26, 22, 255))
    d.text((10, h - 32), 'HOLLYWOOD LEGENDS', font=font('DejaVuSerif-Bold.ttf', 10), fill=(212, 180, 100, 255))
    return img


def stardust_letter(ch, color=(255, 110, 60), w=192, h=256):
    """One six-foot neon letter for the roof sign: a red-gold tube on a black steel backing."""
    m = Image.new('L', (w, h), 0); d = ImageDraw.Draw(m)
    f = font('DejaVuSans-Bold.ttf', int(h * 0.92))
    bb = d.textbbox((0, 0), ch, font=f)
    d.text(((w - bb[2] - bb[0]) / 2, (h - bb[3] - bb[1]) / 2), ch, font=f, fill=255)
    edge = m.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.MaxFilter(9))
    tube = np.asarray(edge, float) / 255
    halo = np.asarray(m.filter(ImageFilter.GaussianBlur(10)), float) / 255
    a = np.clip(tube + halo * 0.3, 0, 1)
    rgb = np.array(color, float) * (1 - tube[..., None] * 0.4) + 255 * tube[..., None] * 0.4
    return to_img(rgb, a * 255)


def tar_gravel(seed=95, w=256, h=256):
    """A tar-and-gravel roof, wet: dark pea gravel with lighter stones, bare black tar where it has worn thin."""
    rng = np.random.default_rng(seed)
    n = noise(w, h, 24, seed)
    a = np.ones((h, w, 3)) * np.array([70, 66, 62], float) * (0.75 + 0.4 * n[..., None])
    stones = rng.random((h, w))
    a[stones > 0.82] *= 1.5
    a[stones < 0.12] *= 0.55
    bare = np.clip((noise(w, h, 60, seed + 1) - 0.62) * 6, 0, 1)
    a = a * (1 - bare[..., None]) + np.array([20, 20, 22]) * bare[..., None]
    return to_img(a)


def tank_staves(seed=96, w=256, h=256):
    """The old wooden water tank: weathered vertical staves, rust streaks under the iron hoops."""
    rng = random.Random(seed)
    img = Image.new('RGB', (w, h)); d = ImageDraw.Draw(img)
    for i in range(0, w, 16):
        c = rng.randint(70, 100)
        d.rectangle([i, 0, i + 15, h], fill=(c, int(c * 0.72), int(c * 0.5)))
        d.line([i, 0, i, h], fill=(36, 26, 20), width=2)
    n = noise(w, h, 8, seed)
    a = np.asarray(img, float) * (0.75 + 0.4 * n[..., None])
    for y in (0.2, 0.55, 0.88):                                          # rust running down from the hoops
        yy = int(h * y)
        a[yy:yy + 30] = a[yy:yy + 30] * 0.75 + np.array([110, 50, 24]) * 0.25
    return to_img(a)


def brenner_card(w=192, h=112, back=False):
    """Walter Brenner's business card: cream stock, raised blue type. The back has his note in ballpoint."""
    img = Image.new('RGBA', (w, h), (236, 228, 206, 255)); d = ImageDraw.Draw(img)
    blue = (30, 50, 120, 255)
    if back:
        f = font('DejaVuSerif-Italic.ttf', 12)
        for i, line in enumerate(('Gus.', 'Think it over. Nobody else', 'is going to offer.', '        W.')):
            d.text((12, 14 + i * 20), line, font=f, fill=(40, 50, 110, 255))
        return img
    d.text((12, 12), 'WALTER BRENNER', font=font('DejaVuSerif-Bold.ttf', 16), fill=blue)
    d.text((12, 34), 'LAPD (Ret.)', font=font('DejaVuSerif.ttf', 11), fill=blue)
    d.line([12, 52, w - 12, 52], fill=blue, width=1)
    d.text((12, 60), 'Security Consultant', font=font('DejaVuSerif.ttf', 11), fill=blue)
    d.text((12, 76), 'Pryce Development', font=font('DejaVuSerif-Bold.ttf', 11), fill=blue)
    return img


# ---------------------------------------------------------------- Case 4: Low Water
def bike_lane(w=256, h=512):
    """A painted bike-lane stencil, seen from above: a white bicycle over a chevron, on transparent ground."""
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    white = (226, 226, 220, 235)
    cx = w // 2
    for (x, y) in ((cx - 58, 150), (cx + 58, 150)):                    # wheels
        d.ellipse([x - 40, y - 40, x + 40, y + 40], outline=white, width=9)
    d.line([cx - 58, 150, cx - 10, 96, cx + 40, 96, cx + 58, 150], fill=white, width=8)
    d.line([cx - 10, 96, cx + 4, 150, cx + 40, 96], fill=white, width=8)
    d.line([cx - 16, 84, cx + 2, 84], fill=white, width=8)
    d.line([cx + 40, 96, cx + 46, 74, cx + 62, 74], fill=white, width=7)
    for k in range(2):                                                  # the chevrons
        y = 280 + k * 70
        d.line([cx - 70, y + 40, cx, y, cx + 70, y + 40], fill=white, width=16)
    a = np.asarray(img).astype(float)
    a[..., 3] *= 0.6 + 0.4 * noise(w, h, 10, 7)                         # worn paint
    return Image.fromarray(a.astype(np.uint8), 'RGBA')


def storm_grate(w=128, h=64):
    """A curb-side storm drain grate: iron bars over black, with plastic glitter caught in them."""
    img = Image.new('RGBA', (w, h), (8, 8, 10, 255)); d = ImageDraw.Draw(img)
    for x in range(4, w, 12):
        d.rectangle([x, 2, x + 5, h - 3], fill=(58, 54, 52, 255))
    d.rectangle([0, 0, w - 1, h - 1], outline=(70, 66, 62, 255), width=4)
    rng = random.Random(4)
    for _ in range(14):
        x, y = rng.randint(6, w - 6), rng.randint(6, h - 6)
        d.rectangle([x, y, x + 2, y + 1], fill=(230, 236, 240, 255))
    return img


def channel_concrete(seed=101, w=256, h=256, algae=0.6):
    """The river channel's poured concrete, slick with green algae toward the water, panel seams, stains."""
    n = noise(w, h, 40, seed); n2 = noise(w, h, 6, seed + 1, 2)
    a = np.ones((h, w, 3)) * np.array([112, 110, 102], float) * (0.85 + 0.2 * n[..., None]) * (0.9 + 0.15 * n2[..., None])
    g = np.clip((noise(w, h, 50, seed + 2) - 0.5 + algae * 0.5) * 2.2, 0, 1)
    a = a * (1 - g[..., None] * 0.7) + np.array([46, 66, 34]) * g[..., None] * 0.7
    a[::128, :] *= 0.6; a[:, ::128] *= 0.6
    return to_img(a)


def graffiti_wall(seed=102, w=512, h=128):
    """Faded tags on the channel wall."""
    img = channel_concrete(seed, w, h, algae=0.2); d = ImageDraw.Draw(img)
    rng = random.Random(seed)
    for t, col in (('NV13', (150, 60, 140)), ('EVLA', (60, 120, 180)), ('RIP', (200, 200, 190)), ('KZ', (190, 90, 40))):
        x, y = rng.randint(0, w - 160), rng.randint(10, h - 60)
        d.text((x, y), t, font=font('DejaVuSans-Bold.ttf', rng.randint(34, 52)), fill=col + (140,))
    return img


def chomp_box(w=128, h=128):
    """The yellow Chomp delivery box: a bite taken out of a circle, CHOMP under it."""
    img = Image.new('RGBA', (w, h), (240, 196, 30, 255)); d = ImageDraw.Draw(img)
    d.ellipse([34, 18, 94, 78], fill=(30, 26, 22, 255))
    d.ellipse([74, 14, 104, 44], fill=(240, 196, 30, 255))
    d.text((22, 86), 'CHOMP', font=font('DejaVuSans-Bold.ttf', 22), fill=(30, 26, 22, 255))
    return img


def tent_tarp(seed=103, w=256, h=256):
    """A blue-grey tarp, faded, with grommets and creases."""
    n = noise(w, h, 30, seed)
    a = np.ones((h, w, 3)) * np.array([70, 92, 116], float) * (0.75 + 0.35 * n[..., None])
    a[::64, :] *= 0.8
    return to_img(a)


def flag_folded(w=64, h=64):
    img = Image.new('RGBA', (w, h), (30, 40, 90, 255)); d = ImageDraw.Draw(img)
    for i in range(5):
        d.ellipse([8 + i * 10, 10 + (i % 2) * 14, 13 + i * 10, 15 + (i % 2) * 14], fill=(230, 230, 230, 255))
    return img


def us_flag(w=380, h=200):
    """The Stars and Stripes, hoist on the left: 13 stripes, a blue canton with 50 stars in rows of 6 and 5."""
    img = Image.new('RGBA', (w, h), (232, 228, 216, 255)); d = ImageDraw.Draw(img)
    sh = h / 13
    for i in range(0, 13, 2):
        d.rectangle([0, round(i * sh), w, round((i + 1) * sh) - 1], fill=(170, 30, 42, 255))
    cw, ch = round(w * 0.4), round(sh * 7)
    d.rectangle([0, 0, cw - 1, ch - 1], fill=(36, 44, 96, 255))
    r = max(1.2, h / 110)
    for row in range(9):
        cols = 6 if row % 2 == 0 else 5
        for c in range(cols):
            x = cw * (2 * c + 1 + (row % 2)) / 12
            y = ch * (row + 1) / 10
            d.ellipse([x - r, y - r, x + r, y + r], fill=(236, 234, 226, 255))
    return img


def night_hills(seed=104, w=2048, h=384):
    """Dark hills with scattered house lights and a freeway's ribbon of headlights along the bottom (emission in alpha)."""
    rng = np.random.default_rng(seed)
    a = np.zeros((h, w, 3)); em = np.zeros((h, w))
    x = np.arange(w)
    ridge = h * (0.35 + 0.18 * np.sin(x / w * 7.0 + 1.0) + 0.08 * np.sin(x / w * 23.0) + 0.05 * (noise(w, 1, 60, seed)[0] - 0.5))
    yy = np.arange(h)[:, None]
    hill = yy > ridge[None, :]
    a[hill] = (16, 16, 20)
    a[~hill] = 0
    a += (~hill)[..., None] * (np.array([30, 22, 40])[None, None, :] + np.array([60, 34, 30])[None, None, :] * (yy / h)[..., None] * 1.6)
    em[~hill] = 0.5
    for _ in range(260):                                                # house lights on the slopes
        px = rng.integers(0, w); py = int(ridge[px] + rng.integers(4, int(h - ridge[px]) - 20))
        if py < h - 30:
            c = (255, 190, 110) if rng.random() < 0.8 else (200, 220, 255)
            a[py:py + 3, px:px + 4] = c; em[py:py + 3, px:px + 4] = rng.uniform(0.3, 0.8)
    fy = h - 26                                                         # the freeway along the bottom
    for k in range(0, w, 3):
        if rng.random() < 0.6:
            red = rng.random() < 0.5
            a[fy + (0 if red else 5):fy + (2 if red else 7), k:k + 2] = (255, 40, 30) if red else (255, 240, 200)
            em[fy + (0 if red else 5):fy + (2 if red else 7), k:k + 2] = 1.0
    a[fy - 3:fy - 1, :] = (255, 150, 70); em[fy - 3:fy - 1, :] = 0.5     # sodium lamps
    return to_img(a, em * 255)


def haskell_easel(w=256, h=352):
    """The easel sign at the gate: navy board, gold type, a little skyline."""
    img = Image.new('RGBA', (w, h), (24, 34, 70, 255)); d = ImageDraw.Draw(img)
    gold = (226, 190, 110, 255)
    d.rectangle([8, 8, w - 9, h - 9], outline=gold, width=3)
    d.text((24, 26), 'FRIENDS OF', font=font('DejaVuSerif.ttf', 26), fill=gold)
    d.text((24, 58), 'TED HASKELL', font=font('DejaVuSerif-Bold.ttf', 32), fill=(240, 236, 226, 255))
    d.line([24, 104, w - 24, 104], fill=gold, width=2)
    for i, (x, bh) in enumerate(((40, 70), (70, 120), (104, 96), (140, 150), (176, 86), (204, 110))):
        d.rectangle([x, 250 - bh, x + 24, 250], fill=(200, 210, 230, 255) if i == 3 else (120, 136, 170, 255))
    d.text((24, 268), 'HOLLYWOOD CORE', font=font('DejaVuSans-Bold.ttf', 22), fill=gold)
    d.text((24, 298), 'The future has a skyline.', font=font('DejaVuSerif-Italic.ttf', 18), fill=(220, 220, 230, 255))
    return img


def giftbag_side(w=192, h=96):
    """A cardboard box of gift bags: navy bags with gold rope handles, 'HOLLYWOOD CORE' on the box."""
    img = Image.new('RGBA', (w, h), (150, 116, 76, 255)); d = ImageDraw.Draw(img)
    d.text((12, 36), 'HOLLYWOOD CORE', font=font('DejaVuSans-Bold.ttf', 18), fill=(40, 40, 70, 255))
    d.line([0, 4, w, 4], fill=(110, 84, 54, 255), width=4)
    return img


def starline_podium(w=192, h=256):
    img = Image.new('RGBA', (w, h), (20, 20, 24, 255)); d = ImageDraw.Draw(img)
    d.rectangle([0, 0, w, 60], fill=(150, 30, 36, 255))
    d.text((18, 12), 'STARLINE', font=font('DejaVuSans-Bold.ttf', 30), fill=(250, 240, 230, 255))
    d.text((18, 80), 'VALET', font=font('DejaVuSans-Bold.ttf', 34), fill=(220, 210, 200, 255))
    for i in range(5):
        x, y = 30 + i * 30, 160
        d.polygon([(x, y - 12), (x + 4, y - 3), (x + 13, y - 3), (x + 6, y + 3), (x + 9, y + 12), (x, y + 6),
                   (x - 9, y + 12), (x - 6, y + 3), (x - 13, y - 3), (x - 4, y - 3)], fill=(220, 180, 80, 255))
    return img


def key_board(w=160, h=200):
    """The valet's key board: a pegboard, rows of empty hooks, one fob left."""
    img = Image.new('RGBA', (w, h), (120, 96, 66, 255)); d = ImageDraw.Draw(img)
    for r in range(5):
        for c in range(4):
            x, y = 22 + c * 38, 24 + r * 36
            d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=(60, 50, 40, 255))
            d.line([x, y, x, y + 8], fill=(180, 180, 186, 255), width=2)
    d.rectangle([94, 152, 108, 176], fill=(20, 20, 24, 255))            # the Range Rover's fob
    d.rectangle([94, 172, 108, 180], fill=(200, 200, 204, 255))
    return img


def tarp_blue(seed=107, w=256, h=256):
    """A brand-new blue tarp: bright, still creased in squares from the package."""
    a = np.ones((h, w, 3)) * np.array([30, 90, 190], float)
    n = noise(w, h, 40, seed)
    a *= (0.88 + 0.18 * n[..., None])
    for k in range(0, w, 64):
        a[:, k:k + 2] *= 0.72; a[k:k + 2, :] *= 0.72
        a[:, k + 2:k + 4] *= 1.15; a[k + 2:k + 4, :] *= 1.15
    return to_img(a)


def newspaper(w=128, h=96):
    img = Image.new('RGBA', (w, h), (214, 210, 196, 255)); d = ImageDraw.Draw(img)
    d.text((6, 4), 'LOS ANGELES', font=font('DejaVuSerif-Bold.ttf', 12), fill=(30, 30, 30, 255))
    for c in range(3):
        for r in range(9):
            d.line([6 + c * 40, 26 + r * 7, 40 + c * 40, 26 + r * 7], fill=(120, 118, 110, 255), width=2)
    return img


def lab_sign(w=256, h=128):
    img = Image.new('RGBA', (w, h), (238, 236, 226, 255)); d = ImageDraw.Draw(img)
    d.text((14, 10), 'NIGHT INTAKE', font=font('DejaVuSans-Bold.ttf', 28), fill=(160, 20, 20, 255))
    d.text((14, 50), 'RING ONCE.', font=font('DejaVuSans-Bold.ttf', 20), fill=(30, 30, 30, 255))
    d.text((14, 78), 'RINGING TWICE WILL NOT', font=font('DejaVuSans.ttf', 15), fill=(30, 30, 30, 255))
    d.text((14, 98), 'MAKE IT FASTER.', font=font('DejaVuSans.ttf', 15), fill=(30, 30, 30, 255))
    for (x, y) in ((4, 4), (w - 20, 4), (4, h - 14), (w - 20, h - 14)):              # tape
        d.rectangle([x, y, x + 16, y + 10], fill=(220, 210, 160, 200))
    return img


def lab_monitor(kind, w=128, h=80):
    img = Image.new('RGBA', (w, h), (8, 14, 20, 255)); d = ImageDraw.Draw(img)
    rng = random.Random(len(kind))
    if kind == 'graph':
        pts = [(x, 40 + int(18 * math.sin(x / 9.0) + rng.uniform(-4, 4))) for x in range(0, w, 4)]
        d.line(pts, fill=(90, 230, 140, 255), width=2)
    else:
        for i in range(8):
            d.rectangle([6, 6 + i * 9, 20 + rng.randint(20, w - 30), 9 + i * 9], fill=(120, 190, 240, 255))
    return img


def dodgers_mug(w=64, h=64):
    img = Image.new('RGBA', (w, h), (236, 236, 236, 255)); d = ImageDraw.Draw(img)
    d.text((10, 20), 'LA', font=font('DejaVuSerif-BoldItalic.ttf', 24), fill=(20, 60, 150, 255))
    return img


# ---------------------------------------------------------------- Case 5: the Blue Note, its back room, the pier at dawn
def danny_poster(w=128, h=192):
    """DANNY REYES, PIANO, THURSDAYS: a gig poster, a piano player's silhouette, a small eyeliner heart in the corner."""
    img = Image.new('RGBA', (w, h), (22, 30, 58, 255)); d = ImageDraw.Draw(img)
    d.rectangle([4, 4, w - 5, h - 5], outline=(210, 170, 80, 255), width=2)
    d.ellipse([w // 2 - 40, 30, w // 2 + 40, 110], fill=(46, 70, 130, 255))
    d.ellipse([w // 2 - 12, 44, w // 2 + 8, 64], fill=(14, 16, 24, 255))                # the player's head
    d.polygon([(w // 2 - 22, 108), (w // 2 - 14, 66), (w // 2 + 10, 66), (w // 2 + 22, 108)], fill=(14, 16, 24, 255))
    d.rectangle([w // 2 + 4, 84, w // 2 + 44, 92], fill=(236, 232, 220, 255))           # the keys
    for x in range(w // 2 + 8, w // 2 + 44, 6):
        d.rectangle([x, 84, x + 2, 88], fill=(14, 16, 24, 255))
    f = font('DejaVuSans-Bold.ttf', 16); f2 = font('DejaVuSerif-BoldItalic.ttf', 14)
    d.text((10, 118), 'DANNY', font=f, fill=(236, 220, 180, 255))
    d.text((10, 136), 'REYES', font=f, fill=(236, 220, 180, 255))
    d.text((10, 158), 'piano  THURSDAYS', font=f2, fill=(210, 170, 80, 255))
    d.text((w - 22, h - 26), '♥', font=font('DejaVuSans.ttf', 14), fill=(20, 18, 22, 255))   # eyeliner heart
    return img


def reserved_card(w=96, h=48):
    img = Image.new('RGBA', (w, h), (226, 216, 190, 255)); d = ImageDraw.Draw(img)
    d.rectangle([2, 2, w - 3, h - 3], outline=(150, 120, 60, 255), width=2)
    d.text((10, 14), 'RESERVED', font=font('DejaVuSerif-Bold.ttf', 14), fill=(110, 20, 24, 255))
    return img


def piano_keys(w=512, h=64, tape=True):
    """A keyboard seen from above: white keys with black ones, Nina's masking-tape letters on the octave from middle C."""
    img = Image.new('RGBA', (w, h), (232, 226, 210, 255)); d = ImageDraw.Draw(img)
    n = 26
    kw = w / n
    for i in range(n):
        d.line([i * kw, 0, i * kw, h], fill=(120, 116, 106, 255), width=1)
    for i in range(n - 1):
        if i % 7 in (0, 1, 3, 4, 5):
            d.rectangle([i * kw + kw * 0.62, 0, i * kw + kw * 1.38, h * 0.6], fill=(16, 14, 16, 255))
    if tape:
        for i in range(7, 14):
            d.rectangle([i * kw + 3, h * 0.72, i * kw + kw - 3, h - 4], fill=(214, 196, 140, 255))
    return img


def bar_wallpaper(seed=111, w=256, h=256):
    """Deep blue flock paper with a faded gold diamond pattern, smoke-darkened toward the top."""
    img = Image.new('RGB', (w, h), (26, 34, 58)); d = ImageDraw.Draw(img)
    for y in range(0, h, 32):
        for x in range(0, w, 32):
            ox = 16 if (y // 32) % 2 else 0
            d.polygon([(x + ox, y + 4), (x + ox + 10, y + 16), (x + ox, y + 28), (x + ox - 10, y + 16)], outline=(96, 80, 46))
    n = noise(w, h, 8, seed)
    return to_img(np.asarray(img).astype(float) * (0.8 + 0.35 * n[..., None]))


def liquor_case(seed, w=128, h=96):
    rng = random.Random(seed)
    base = rng.choice([(176, 140, 96), (160, 126, 84), (186, 156, 110)])
    img = Image.new('RGBA', (w, h), base + (255,)); d = ImageDraw.Draw(img)
    label = rng.choice(['RYE', 'CAMPARI', 'GIN', 'BOURBON', 'VERMOUTH', 'TONIC'])
    d.rectangle([10, 30, w - 10, 64], outline=(70, 40, 30, 255), width=2)
    d.text((16, 36), label, font=font('DejaVuSans-Bold.ttf', 18), fill=(80, 30, 24, 255))
    d.line([0, h // 2 - 30, w, h // 2 - 30], fill=(120, 90, 60, 255), width=3)
    return img


def locker_label(text, w=128, h=32):
    img = Image.new('RGBA', (w, h), (226, 222, 200, 255)); d = ImageDraw.Draw(img)
    d.text((8, 5), text, font=font('DejaVuSans-Bold.ttf', 18), fill=(30, 30, 36, 255))
    return img


def pryce_lease_letter(w=128, h=168):
    """A lawyer's letter on Pryce Development's letterhead, NO across it in red, underlined three times."""
    img = Image.new('RGBA', (w, h), (240, 238, 230, 255)); d = ImageDraw.Draw(img)
    d.rectangle([8, 8, 60, 20], fill=(40, 50, 90, 255))
    for i in range(12):
        d.line([10, 34 + i * 9, w - 10 - (i * 7) % 30, 34 + i * 9], fill=(110, 110, 120, 255))
    d.text((28, 52), 'NO', font=font('DejaVuSans-Bold.ttf', 48), fill=(196, 20, 20, 255))
    for k in range(3):
        d.line([24, 108 + k * 6, 100, 106 + k * 6], fill=(196, 20, 20, 255), width=3)
    return img


def dawn_sky(w=1024, h=256, sun=False):
    """Navy at the top going to rose and gold at the horizon (sun=True: the sun is up, a hot band at the bottom)."""
    yy = np.linspace(0, 1, h)[:, None]
    if sun:
        stops = [(0.0, (70, 110, 170)), (0.45, (190, 160, 160)), (0.8, (255, 190, 120)), (1.0, (255, 220, 160))]
    else:
        stops = [(0.0, (24, 30, 64)), (0.5, (90, 70, 110)), (0.8, (220, 120, 120)), (1.0, (250, 170, 130))]
    ts = [t for t, _ in stops]
    col = np.stack([np.interp(yy[:, 0], ts, [c[k] for _, c in stops]) for k in range(3)], -1)[:, None, :]
    arr = np.broadcast_to(col, (h, w, 3)).copy()
    n = noise(w, h, 5, 121)
    arr *= (0.94 + 0.1 * n[..., None])
    return to_img(arr)
