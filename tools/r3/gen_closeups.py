"""Close-up pictures shown full screen in the game (Case 3's UV lamp). Writes assets/ui/<name>.png.

python gen_closeups.py
  uv_wall.png      Gus's wall of signed photos under the UV lamp: three signatures glow gold (modern paint pen).
  uv_headshot.png  Pearl's headshot from her locker under the same lamp, her autograph glowing the same gold."""
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


def main():
    out = os.path.join(ROOT, 'assets', 'ui')
    uv_wall().save(os.path.join(out, 'uv_wall.png'))
    uv_headshot().save(os.path.join(out, 'uv_headshot.png'))
    print('uv_wall, uv_headshot')


if __name__ == '__main__':
    main()
