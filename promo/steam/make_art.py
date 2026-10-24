"""Builds the Steam store art into promo/steam/images from the title-screen background and neon signs.
python promo/steam/make_art.py   (run from the repo root; needs Pillow + numpy)"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
OUT = os.path.join(ROOT, 'promo', 'steam', 'images')
SHOTS = os.path.join(OUT, 'screenshots')
os.makedirs(SHOTS, exist_ok=True)
FONT = 'C:/Windows/Fonts/DejaVuSansCondensed-Bold.ttf'
if not os.path.exists(FONT):
    FONT = os.path.join(ROOT, 'assets/fonts/DejaVuSansCondensed-Bold.ttf')


def P(*a):
    return os.path.join(ROOT, *a)


def background():
    b = Image.open(P('assets/rooms/title.png')).convert('RGBA')
    b.alpha_composite(Image.open(P('assets/rooms/title_bar_red.png')), (8, 0))
    b.alpha_composite(Image.open(P('assets/rooms/title_bar_blue.png')), (0, 0))
    return b.convert('RGB')


def cover(img, size, cx=0.5, cy=0.5):
    w, h = size
    s = max(w / img.width, h / img.height)
    im = img.resize((round(img.width * s) + 1, round(img.height * s) + 1), Image.LANCZOS)
    x = int((im.width - w) * cx)
    y = int((im.height - h) * cy)
    return im.crop((x, y, x + w, y + h))


def tagline_img(width, spacing):
    f = ImageFont.truetype(FONT, 100)
    txt = 'FIVE CASES.  ONE NIGHT.'
    xs, x = [], 0
    for ch in txt:
        xs.append(x); x += f.getlength(ch) + spacing
    im = Image.new('L', (int(x) + 20, 140), 0)
    d = ImageDraw.Draw(im)
    for ch, px in zip(txt, xs):
        d.text((px + 10, 10), ch, font=f, fill=255)
    im = im.crop(im.getbbox())
    r = width / im.width
    return im.resize((width, round(im.height * r)), Image.LANCZOS)


def logo_rgba(width, tagline=True):
    """Neon logo (RAY KESSLER, NIGHTSHIFT, tagline) as RGBA with unpremultiplied glow."""
    L = Image.open(P('assets/ui/title_logo.png')).convert('RGBA')
    S = Image.open(P('assets/ui/title_sub.png')).convert('RGBA')
    sw = round(L.width * 0.42)
    S = S.resize((sw, round(S.height * sw / S.width)), Image.LANCZOS)
    gap = -10
    th = 0
    tag = None
    if tagline:
        tag = tagline_img(round(L.width * 0.3), 14)
        th = tag.height + 30
    H = L.height + gap + S.height + th
    c = Image.new('RGBA', (L.width, H), (0, 0, 0, 0))
    c.alpha_composite(L, (0, 0))
    c.alpha_composite(S, ((L.width - S.width) // 2, L.height + gap))
    if tag is not None:
        col = Image.new('RGBA', tag.size, (232, 220, 196, 255))
        col.putalpha(tag)
        c.alpha_composite(col, ((L.width - tag.width) // 2, H - tag.height))
    # the neon art is additive-light on transparent: make alpha = brightness so it stands alone
    a = np.asarray(c).astype(np.float32) / 255
    rgb, al = a[..., :3], a[..., 3:]
    lit = rgb * al
    alpha = np.clip(lit.max(axis=2, keepdims=True) * 1.4, 0, 1)
    alpha = np.maximum(alpha, al * 0.0)
    col = np.where(alpha > 0.004, np.clip(lit / np.maximum(alpha, 1e-4), 0, 1), 0)
    out = np.concatenate([col, alpha], axis=2)
    im = Image.fromarray((out * 255).astype(np.uint8), 'RGBA')
    im = im.crop(im.getbbox())
    return im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)


def darken(img, bottom=0.0, top=0.0, amt=0.0):
    a = np.asarray(img).astype(np.float32)
    h = a.shape[0]
    y = np.linspace(0, 1, h)[:, None, None]
    k = 1 - amt - top * (1 - y) ** 2 - bottom * y ** 2
    return Image.fromarray(np.clip(a * k, 0, 255).astype(np.uint8))


def place(bg, logo, cx, cy):
    out = bg.convert('RGBA')
    # soft dark pool behind the sign so the neon reads on any background
    pad = Image.new('L', out.size, 0)
    ImageDraw.Draw(pad).ellipse([cx - logo.width * .62, cy - logo.height * .8, cx + logo.width * .62, cy + logo.height * .8], fill=150)
    pad = pad.filter(ImageFilter.GaussianBlur(logo.height * .35))
    out = Image.composite(Image.new('RGBA', out.size, (4, 2, 10, 255)), out, pad)
    out.alpha_composite(logo, (round(cx - logo.width / 2), round(cy - logo.height / 2)))
    return out.convert('RGB')


def save(im, name, jpg=False):
    p = os.path.join(OUT, name)
    if jpg:
        im.convert('RGB').save(p, quality=95)
    else:
        im.save(p)
    print(name, im.size)


bg = background()
dark = darken(bg, bottom=0.35, top=0.25, amt=0.1)

# capsules (logo included)
def capsule(name, size, logo_w, cx, cy, focus):
    base = cover(dark, size, *focus)
    save(place(base, logo_rgba(logo_w), size[0] * cx, size[1] * cy), name)

capsule('header_capsule_920x430.png', (920, 430), 560, .5, .5, (.55, .5))
capsule('small_capsule_462x174.png', (462, 174), 380, .5, .5, (.5, .45))
capsule('main_capsule_1232x706.png', (1232, 706), 960, .5, .40, (.55, .5))
capsule('vertical_capsule_748x896.png', (748, 896), 700, .5, .25, (.30, .5))
capsule('library_capsule_600x900.png', (600, 900), 560, .5, .25, (.30, .5))

# library hero (no text), logo (transparent), page background
save(cover(bg, (3840, 1240), .5, .55), 'library_hero_3840x1240.jpg', jpg=True)
save(cover(darken(bg, bottom=.5, top=.3, amt=.25), (1438, 810)), 'page_background_1438x810.jpg', jpg=True)
save(logo_rgba(1280, tagline=False), 'library_logo_1280.png')

# clean title screenshot (no menu) and picks from docs/screenshots
t = place(dark, logo_rgba(1300), 960, 330)
save(t, 'screenshots/01_title.png')
picks = ['01_case1_squad_room', '02_case1_payphone_call', '06_case1_murder_board', '07_case2_mulholland_shah',
         '08_case2_prius_glide_app', '09_case2_norms_rosa', '11_case3_stardust_pearl', '12_case3_uv_lamp',
         '13_case3_roof_charlie', '15_case4_reeds_headlight', '16_case4_gate_camera', '21_case4_notebook',
         '23_case5_blue_note_bar']
for i, n in enumerate(picks, 2):
    Image.open(P('docs/screenshots', n + '.png')).convert('RGB').save(os.path.join(SHOTS, '%02d_%s.png' % (i, n[3:])))
