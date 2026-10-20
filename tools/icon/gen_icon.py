"""Generates the Nightshift game icon (two candidate designs) with Pillow.
  python tools/icon/gen_icon.py [out_dir]   ->  icon_a.png, icon_b.png (1024 px)
tools/icon/build_icon.py turns the chosen design into icon.svg/.png, the .ico and the Steam sizes."""
import os, sys, random, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

S = 1024
PINK = (255, 70, 140)
HOT = (255, 225, 235)
BLUE = (70, 130, 255)
SERIF = 'C:/Windows/Fonts/georgiaz.ttf'


def vgrad(top, bot):
    im = Image.new('RGB', (S, S))
    d = ImageDraw.Draw(im)
    for y in range(S):
        t = y / (S - 1)
        d.line([(0, y), (S, y)], fill=tuple(int(a + (b - a) * t) for a, b in zip(top, bot)))
    return im


def glow(mask, color, radius, strength=1.0):
    g = mask.filter(ImageFilter.GaussianBlur(radius))
    return Image.merge('RGB', [g.point(lambda v, c=c: int(v * c / 255 * strength)) for c in color])


def add(a, b):
    return ImageChops.add(a, b)


def neon(base, mask, color, tube=7):
    """mask: L image of the neon line. Adds halo + coloured tube + white-hot core."""
    out = add(base, glow(mask, color, 46, 1.1))
    out = add(out, glow(mask, color, 18, 1.0))
    out = add(out, glow(mask, color, 6, 0.9))
    out.paste(Image.new('RGB', (S, S), color), mask=mask.filter(ImageFilter.GaussianBlur(1.2)))
    core = mask.filter(ImageFilter.MinFilter(tube | 1))
    out.paste(Image.new('RGB', (S, S), HOT), mask=core.filter(ImageFilter.GaussianBlur(1.5)))
    return out


def rain(img, n=70, seed=3):
    r = random.Random(seed)
    lay = Image.new('L', (S, S), 0)
    d = ImageDraw.Draw(lay)
    for _ in range(n):
        x, y = r.randrange(S), r.randrange(-100, S)
        l = r.randrange(60, 200)
        d.line([(x, y), (x - l * 0.18, y + l)], fill=r.randrange(25, 70), width=r.choice([2, 3]))
    return add(img, Image.merge('RGB', [lay.point(lambda v, k=k: int(v * k)) for k in (0.7, 0.8, 1.0)]))


def rounded(img, r=190):
    m = Image.new('L', (S, S), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, S - 1, S - 1], r, fill=255)
    out = img.convert('RGBA')
    out.putalpha(m)
    return out


def tube_text(text, font, xy, anchor='mm'):
    m = Image.new('L', (S, S), 0)
    d = ImageDraw.Draw(m)
    d.text(xy, text, font=font, fill=255, anchor=anchor, stroke_width=0)
    outer = m
    inner = m.filter(ImageFilter.MinFilter(21))
    return ImageChops.subtract(outer, inner)       # outline only = neon tube


def design_a():
    """RK monogram: pink neon tube letters in a blue neon frame, rainy night wall."""
    img = vgrad((14, 10, 28), (30, 14, 36))
    img = rain(img)
    # wet street glow at the bottom
    street = Image.new('L', (S, S), 0)
    ImageDraw.Draw(street).rectangle([0, 860, S, S], fill=255)
    img = add(img, glow(street.filter(ImageFilter.GaussianBlur(40)), (40, 60, 160), 30, 0.35))
    fr = Image.new('L', (S, S), 0)
    ImageDraw.Draw(fr).rounded_rectangle([96, 96, S - 97, S - 97], 120, outline=255, width=14)
    img = neon(img, fr, BLUE, 5)
    font = ImageFont.truetype(SERIF, 520)
    m = tube_text('RK', font, (S // 2 - 6, S // 2 - 10))
    img = neon(img, m, PINK, 5)
    # reflection on the wet street under the letters
    refl = ImageChops.offset(m.transpose(Image.FLIP_TOP_BOTTOM), 0, 360)
    fade = Image.linear_gradient('L').resize((S, S)).transpose(Image.FLIP_TOP_BOTTOM).point(lambda v: v // 6)
    refl = ImageChops.multiply(refl, fade)
    img = add(img, glow(refl.filter(ImageFilter.GaussianBlur(4)), PINK, 6, 0.6))
    return rounded(img)


def design_b():
    """Fedora detective silhouette in a venetian-blind window, pink/blue night light."""
    img = vgrad((16, 20, 52), (60, 16, 56))
    # window light: soft pink/blue wash with blind slats
    wash = Image.new('RGB', (S, S), (0, 0, 0))
    wash = add(wash, glow(Image.new('L', (S, S), 0).point(lambda v: 0), BLUE, 1))
    light = Image.new('L', (S, S), 0)
    ld = ImageDraw.Draw(light)
    ld.ellipse([160, 120, 864, 824], fill=255)
    img = add(img, glow(light.filter(ImageFilter.GaussianBlur(120)), (120, 60, 170), 1, 0.9))
    slats = Image.new('L', (S, S), 0)
    sd = ImageDraw.Draw(slats)
    for y in range(40, S, 74):
        sd.rectangle([0, y, S, y + 26], fill=255)
    slat_shadow = slats.filter(ImageFilter.GaussianBlur(3)).point(lambda v: int(v * 0.55))
    img.paste((8, 6, 18), mask=slat_shadow)
    # silhouette: head, hat, coat shoulders
    sil = Image.new('L', (S * 2, S * 2), 0)
    d = ImageDraw.Draw(sil)
    c = S  # centre in 2x space
    d.polygon([(c - 700, 2 * S), (c - 620, 1530), (c - 360, 1400), (c - 150, 1330), (c + 150, 1330),
               (c + 360, 1400), (c + 620, 1530), (c + 700, 2 * S)], fill=255)        # shoulders
    d.rectangle([c - 90, 1180, c + 90, 1360], fill=255)                              # neck
    d.ellipse([c - 190, 880, c + 190, 1290], fill=255)                               # head
    d.polygon([(c - 215, 940), (c - 205, 700), (c - 100, 640), (c + 100, 640), (c + 205, 700), (c + 215, 940)], fill=255)  # crown
    d.ellipse([c - 520, 880, c + 520, 1010], fill=255)                               # brim
    sil = sil.resize((S, S), Image.LANCZOS)
    img.paste((6, 4, 14), mask=sil)
    # pink neon rim on the right edge, blue on the left
    edge = ImageChops.subtract(sil, sil.filter(ImageFilter.MinFilter(15)))
    right = ImageChops.offset(sil, -14, 0)
    rim_r = ImageChops.subtract(sil, right)
    left = ImageChops.offset(sil, 14, 0)
    rim_l = ImageChops.subtract(sil, left)
    img = add(img, glow(rim_r.filter(ImageFilter.GaussianBlur(5)), PINK, 5, 2.4))
    img = add(img, glow(rim_l.filter(ImageFilter.GaussianBlur(5)), BLUE, 5, 2.4))
    img = add(img, glow(edge, (255, 110, 170), 22, 0.35))
    # hat band
    band = Image.new('L', (S, S), 0)
    ImageDraw.Draw(band).line([(S // 2 - 208, 478), (S // 2 + 208, 478)], fill=255, width=6)
    img = neon(img, band, PINK, 3)
    img = rain(img, 40, 9)
    return rounded(img)


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else '.'
    os.makedirs(out, exist_ok=True)
    design_a().save(os.path.join(out, 'icon_a.png'))
    design_b().save(os.path.join(out, 'icon_b.png'))
