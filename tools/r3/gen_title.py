"""The title screen's neon logo. Writes assets/ui/title_logo.png and title_logo_dim.png.

python gen_title.py
  title_logo.png      NIGHTSHIFT in red-pink neon tubes (the Blue Note's serif italic), on transparent: the colour is the
                      light, so the game draws it with additive blending.
  title_logo_dim.png  The same with one tube (the second I) nearly dead, swapped in now and then for a flicker."""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import textures as tx

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
TEXT = 'NIGHTSHIFT'
COLOR = np.array([255, 52, 104], float)
SIZE = 160           # glyph size in output pixels
PAD = 90             # room for the halo
SS = 2               # supersampling
FLICKER = 7          # index of the tube that buzzes (the second I)


def masks():
    f = tx.font('DejaVuSerif-BoldItalic.ttf', SIZE * SS)
    bb = f.getbbox(TEXT)
    w, h = bb[2] - bb[0] + PAD * 2 * SS, bb[3] - bb[1] + PAD * 2 * SS
    w, h = (w + SS - 1) // SS * SS, (h + SS - 1) // SS * SS
    ox, oy = PAD * SS - bb[0], PAD * SS - bb[1]
    full = Image.new('L', (w, h), 0)
    ImageDraw.Draw(full).text((ox, oy), TEXT, font=f, fill=255)
    one = Image.new('L', (w, h), 0)
    ImageDraw.Draw(one).text((ox + f.getlength(TEXT[:FLICKER]), oy), TEXT[FLICKER], font=f, fill=255)
    return full, one


def tube(m):
    """A glass tube bent along each glyph's outline: the band between a grown and a shrunk glyph."""
    grow = m.filter(ImageFilter.MaxFilter(6 * SS + 1))
    shrink = m.filter(ImageFilter.MinFilter(5 * SS + 1))
    band = np.asarray(grow, float) / 255 - np.asarray(shrink, float) / 255
    return Image.fromarray((band * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(SS * 0.8))


def light(t, k):
    """Light from the tube mask t (0..1 array) at strength k: a white-hot core, the coloured tube and three halos."""
    def blur(a, r):
        return np.asarray(Image.fromarray((a * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r)), float) / 255
    core = np.clip((t - 0.55) / 0.45, 0, 1)
    halo = blur(t, 6 * SS) * 0.9 + blur(t, 18 * SS) * 0.65 + blur(t, 48 * SS) * 0.6
    col = (t[..., None] * 1.1 + halo[..., None]) * COLOR[None, None, :] / 255 + core[..., None] * 0.75
    return col * k


def main():
    full, one = masks()
    tf = np.asarray(tube(full), float) / 255
    to = np.asarray(tube(one), float) / 255
    rest = np.clip(tf - to, 0, 1)
    for name, k_flicker in (('title_logo', 1.0), ('title_logo_dim', 0.12)):
        rgb = light(rest, 1.0) + light(to, k_flicker)
        # the unlit glass still catches a little light where the tube is dark
        rgb += (to * (1 - k_flicker) * 0.12)[..., None] * np.array([0.6, 0.5, 0.55])
        a = np.clip(rgb.max(-1), 0, 1)
        out = np.clip(rgb / np.maximum(a, 1e-4)[..., None], 0, 1)      # straight alpha: colour, and how much of it
        img = Image.fromarray(np.dstack([out * 255, a * 255]).astype(np.uint8), 'RGBA')
        img = img.resize((img.width // SS, img.height // SS), Image.LANCZOS)
        img.save(os.path.join(ROOT, 'assets', 'ui', name + '.png'))
        print(name, img.size)


if __name__ == '__main__':
    main()
