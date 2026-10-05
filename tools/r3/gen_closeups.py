"""Close-up pictures shown full screen in the game (Case 3's UV lamp). Writes assets/ui/<name>.png.

python gen_closeups.py
  uv_wall.png      Gus's wall of signed photos under the UV lamp: three signatures glow gold (modern paint pen).
  uv_headshot.png  Pearl's headshot from her locker under the same lamp, her autograph glowing the same gold.
  invite_render.png  Pryce's invitation unfolded: a watercolour tower where the Blue Note stands (Case 4).
  headlight_hole.png, headlight_piece.png, headlight_shard.png  The headlight fit (Case 4): Crane's broken headlight
                     and the two pieces that go back into it."""
import math, os, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import textures as tx

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
W, H = 1120, 700


def violet_ground(w, h, seed):
    """The dark wall lit only by the lamp: a violet pool of light, falling off to black."""
    yy, xx = np.mgrid[0:h, 0:w]
    r = np.hypot((xx - w * 0.5) / (w * 0.55), (yy - h * 0.48) / (h * 0.6))
    fall = np.clip(1.1 - r, 0, 1) ** 1.4
    n = tx.noise(w, h, 40, seed)
    rgb = np.array([46, 18, 92])[None, None, :] * (fall[..., None] * (0.8 + 0.3 * n[..., None]))
    return Image.fromarray(np.dstack([rgb.clip(0, 255), np.full((h, w), 255)]).astype(np.uint8), 'RGBA')


def uv_wall():
    img = violet_ground(W, H, 1)
    wall = tx.signed_wall(1024, 640, uv=True)
    img.alpha_composite(wall, ((W - 1024) // 2, (H - 640) // 2))
    return img


def uv_headshot():
    """An 8 x 10 glossy of Pearl, signed across the bottom, on the open locker shelf, under the lamp."""
    img = violet_ground(W, H, 2)
    d = ImageDraw.Draw(img)
    pw, ph = 420, 540
    x0, y0 = (W - pw) // 2, (H - ph) // 2
    photo = Image.new('RGBA', (pw, ph), (40, 30, 70, 255)); g = ImageDraw.Draw(photo)
    g.rectangle([0, 0, pw - 1, ph - 1], outline=(150, 130, 210, 255), width=10)                 # the white border
    cx = pw * 0.52
    g.ellipse([cx - 150, 60, cx + 150, 520], fill=(70, 40, 110, 255))                          # hair, falling long
    g.chord([cx - 210, 400, cx + 210, 760], 180, 360, fill=(60, 34, 96, 255))                  # shoulders
    g.rectangle([cx - 34, 300, cx + 34, 420], fill=(112, 84, 160, 255))                       # neck
    g.ellipse([cx - 82, 120, cx + 82, 340], fill=(128, 98, 178, 255))                          # face
    g.chord([cx - 90, 100, cx + 96, 300], 190, 350, fill=(70, 40, 110, 255))                   # a sweep of hair
    g.pieslice([cx - 150, 90, cx + 20, 470], 100, 250, fill=(70, 40, 110, 255))                # over the left side
    for ex in (-30, 34):
        g.ellipse([cx + ex - 12, 205, cx + ex + 12, 219], fill=(40, 20, 60, 255))               # eyes
    g.ellipse([cx - 22, 280, cx + 26, 296], fill=(90, 50, 110, 255))                           # lips
    photo = photo.filter(ImageFilter.GaussianBlur(2.2))
    img.alpha_composite(photo, (x0, y0))
    glow = Image.new('RGBA', (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(glow)
    tx._signature(gd, x0 + 60, y0 + ph - 120, x0 + pw - 50, y0 + ph - 70, 77, (255, 214, 120, 255), 7)
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(10)))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(3)))
    img.alpha_composite(glow)
    return img


def invite_render():
    """Pryce's invitation, unfolded: an architect's watercolour of a glass tower on Hollywood Boulevard, across from the
    Chinese Theatre's pagoda roof. Where the Blue Note stands today, a lobby."""
    w, h = 1000, 640
    rng = random.Random(7)
    paper = np.ones((h, w, 3)) * np.array([236, 230, 214], float)
    paper *= (0.94 + 0.08 * tx.noise(w, h, 30, 3)[..., None])
    img = Image.fromarray(paper.astype(np.uint8)).convert('RGBA')
    wash = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(wash)
    d.rectangle([0, 0, w, 330], fill=(150, 186, 220, 120))                                  # a washed blue sky
    d.ellipse([-200, 180, 700, 520], fill=(240, 190, 140, 70))                              # sunset glow
    d.rectangle([0, 470, w, h], fill=(130, 126, 120, 150))                                  # the boulevard
    for x in range(0, w, 70):                                                               # the stars in the sidewalk
        d.polygon([(x + 20, 560), (x + 26, 574), (x + 40, 574), (x + 29, 582), (x + 33, 596), (x + 20, 588),
                   (x + 7, 596), (x + 11, 582), (x, 574), (x + 14, 574)], fill=(200, 130, 140, 140))
    # the Chinese Theatre's pagoda roof, left
    d.polygon([(30, 360), (260, 360), (230, 300), (60, 300)], fill=(70, 130, 110, 190))
    d.polygon([(80, 300), (210, 300), (190, 250), (100, 250)], fill=(70, 130, 110, 190))
    d.rectangle([60, 360, 230, 470], fill=(170, 50, 40, 180))
    # the tower, right of centre: glass, forty floors of it, going off the top of the page
    tx0, tx1 = 520, 760
    d.polygon([(tx0, 470), (tx1, 470), (tx1 - 20, -10), (tx0 + 30, -10)], fill=(110, 160, 200, 170))
    for y in range(0, 470, 18):
        d.line([tx0 + 10, y, tx1 - 10, y], fill=(230, 240, 250, 120), width=2)
    for x in range(tx0 + 30, tx1, 40):
        d.line([x, 0, x - 6, 470], fill=(80, 110, 150, 120), width=2)
    # the lobby at street level: glowing, people drawn as dabs
    d.rectangle([tx0 - 40, 390, tx1 + 40, 470], fill=(250, 220, 150, 190))
    for k in range(9):
        x = tx0 - 20 + k * 32
        d.ellipse([x, 430 + rng.randint(-4, 4), x + 10, 468], fill=(60, 50, 60, 170))
    img.alpha_composite(wash.filter(ImageFilter.GaussianBlur(3)))
    pen = Image.new('RGBA', (w, h), (0, 0, 0, 0)); g = ImageDraw.Draw(pen)
    g.text((tx0 - 20, 396), 'PRYCE TOWER  HOLLYWOOD CORE', font=tx.font('DejaVuSans-Bold.ttf', 18), fill=(90, 70, 40, 230))
    g.text((40, 600), 'Hollywood Core. The future has a skyline.', font=tx.font('DejaVuSerif-Italic.ttf', 22),
           fill=(60, 50, 60, 230))
    g.rectangle([4, 4, w - 5, h - 5], outline=(190, 180, 160, 255), width=3)
    img.alpha_composite(pen)
    return img


# ---------------------------------------------------------------- the headlight fit (Case 4, puzzle 5.1)
HL_W, HL_H = 1120, 700
LENS = (300, 230, 820, 470)                 # the lens's box in the close-up
# the missing parts of the lens: the big piece from the reeds (left), the sliver from Owen's bike (lower right)
P1 = [(300, 300), (340, 240), (430, 230), (520, 232), (548, 280), (530, 330), (566, 372), (540, 420), (558, 470),
      (360, 470), (310, 430)]
P2 = [(558, 470), (540, 420), (566, 372), (620, 396), (700, 420), (760, 452), (700, 470)]


def _lens(w, h):
    """The whole headlight lens, as it was: clear plastic over a chrome reflector, four rings moulded across it."""
    x0, y0, x1, y1 = LENS
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    d.rounded_rectangle([x0, y0, x1, y1], radius=70, fill=(170, 186, 200, 255))
    d.rounded_rectangle([x0 + 30, y0 + 30, x1 - 30, y1 - 30], radius=50, fill=(120, 130, 140, 255))
    for cx in (430, 640):                                                                    # the reflectors
        d.ellipse([cx - 70, 280, cx + 70, 420], fill=(210, 214, 220, 255))
        d.ellipse([cx - 30, 320, cx + 30, 380], fill=(250, 250, 246, 255))
    for k in range(4):                                                                       # the four rings
        cx = 470 + k * 52
        d.ellipse([cx - 34, 316, cx + 34, 384], outline=(236, 240, 246, 255), width=7)
    d.line([x0 + 40, y0 + 22, x1 - 80, y0 + 22], fill=(255, 255, 255, 200), width=6)       # a highlight
    return img.filter(ImageFilter.GaussianBlur(0.8))


def headlight():
    """Background (the hole in Crane's headlight) and the two pieces, each with its target centre."""
    yy, xx = np.mgrid[0:HL_H, 0:HL_W]
    paint = np.ones((HL_H, HL_W, 3)) * np.array([96, 110, 126], float)                       # blue-gray paint
    paint *= (0.7 + 0.5 * np.clip(1 - np.hypot((xx - 560) / 700, (yy - 200) / 500), 0, 1)[..., None])
    bg = Image.fromarray(paint.clip(0, 255).astype(np.uint8)).convert('RGBA')
    d = ImageDraw.Draw(bg)
    x0, y0, x1, y1 = LENS
    d.rounded_rectangle([x0 - 24, y0 - 24, x1 + 24, y1 + 24], radius=86, fill=(30, 32, 36, 255))   # the housing
    lens = _lens(HL_W, HL_H)
    mask = Image.new('L', (HL_W, HL_H), 255); md = ImageDraw.Draw(mask)
    md.polygon(P1, fill=0); md.polygon(P2, fill=0)
    bg.alpha_composite(Image.composite(lens, Image.new('RGBA', (HL_W, HL_H), (0, 0, 0, 0)), mask))
    lens_mask = Image.new('L', (HL_W, HL_H), 0)
    ImageDraw.Draw(lens_mask).rounded_rectangle([x0, y0, x1, y1], radius=70, fill=255)
    hole = Image.new('RGBA', (HL_W, HL_H), (0, 0, 0, 0)); hd = ImageDraw.Draw(hole)
    for poly in (P1, P2):
        hd.polygon(poly, fill=(6, 6, 8, 255))
    bg.alpha_composite(Image.composite(hole, Image.new('RGBA', (HL_W, HL_H), (0, 0, 0, 0)), lens_mask))
    d = ImageDraw.Draw(bg)
    for poly in (P1, P2):                                                                     # dashed outlines
        for a, b in zip(poly, poly[1:] + poly[:1]):
            n = max(1, int(math.hypot(b[0] - a[0], b[1] - a[1]) / 12))
            for k in range(0, n, 2):
                t0, t1 = k / n, min(1, (k + 1) / n)
                d.line([a[0] + (b[0] - a[0]) * t0, a[1] + (b[1] - a[1]) * t0, a[0] + (b[0] - a[0]) * t1,
                        a[1] + (b[1] - a[1]) * t1], fill=(240, 220, 150, 200), width=3)
    pieces = []
    for name, poly in (('headlight_piece', P1), ('headlight_shard', P2)):
        m = Image.new('L', (HL_W, HL_H), 0); ImageDraw.Draw(m).polygon(poly, fill=255)
        m = Image.composite(m, Image.new('L', (HL_W, HL_H), 0), lens_mask)
        cut = Image.new('RGBA', (HL_W, HL_H), (0, 0, 0, 0)); cut.paste(lens, (0, 0), m)
        edge = m.filter(ImageFilter.FIND_EDGES)
        cut.paste((250, 252, 255, 255), (0, 0), edge)                                         # a bright broken edge
        bb = m.getbbox()
        pieces.append((name, cut.crop(bb), ((bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2)))
    return bg, pieces


def main():
    out = os.path.join(ROOT, 'assets', 'ui')
    uv_wall().save(os.path.join(out, 'uv_wall.png'))
    uv_headshot().save(os.path.join(out, 'uv_headshot.png'))
    invite_render().save(os.path.join(out, 'invite_render.png'))
    bg, pieces = headlight()
    bg.save(os.path.join(out, 'headlight_hole.png'))
    for name, im, c in pieces:
        im.save(os.path.join(out, name + '.png'))
        print(name, 'target centre', c, 'size', im.size)      # -> Case4.PIECES
    print('uv_wall, uv_headshot, invite_render, headlight_hole')


if __name__ == '__main__':
    main()
