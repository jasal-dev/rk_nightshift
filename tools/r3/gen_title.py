"""The title screen's neon signs. Writes assets/ui/title_logo.png, title_logo_dim.png and title_sub.png.

python gen_title.py
  title_logo.png      RAY KESSLER in red-pink neon tubes (the Blue Note's serif italic), on transparent: the colour is
                      the light, so the game draws it with additive blending.
  title_logo_dim.png  The same with one tube (the second S) nearly dead, swapped in now and then for a flicker.
  title_sub.png       NIGHTSHIFT, smaller and letter-spaced, in the Blue Note's blue."""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import textures as tx

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
SS = 2               # supersampling


def masks(text, fnt, size, pad, spacing=0, flicker=None):
    """Glyph masks (supersampled): the whole text, and the one letter at index `flicker` (or None)."""
    f = tx.font(fnt, size * SS)
    sp = spacing * SS
    xs, x = [], 0.0
    for ch in text:
        xs.append(x)
        x += f.getlength(ch) + sp
    bb = f.getbbox(text)
    tw = bb[2] - bb[0] if spacing == 0 else int(x - sp - bb[0])
    w, h = tw + pad * 2 * SS, bb[3] - bb[1] + pad * 2 * SS
    w, h = (w + SS - 1) // SS * SS, (h + SS - 1) // SS * SS
    ox, oy = pad * SS - bb[0], pad * SS - bb[1]
    full = Image.new('L', (w, h), 0)
    d = ImageDraw.Draw(full)
    if spacing == 0:
        d.text((ox, oy), text, font=f, fill=255)                # keeps the font's kerning
    else:
        for ch, cx in zip(text, xs):
            d.text((ox + cx, oy), ch, font=f, fill=255)
    one = Image.new('L', (w, h), 0)
    if flicker is not None:
        cx = f.getlength(text[:flicker]) if spacing == 0 else xs[flicker]
        ImageDraw.Draw(one).text((ox + cx, oy), text[flicker], font=f, fill=255)
    return full, one


def tube(m, width):
    """A glass tube bent along each glyph's outline: the band between a grown and a shrunk glyph."""
    grow = m.filter(ImageFilter.MaxFilter((width + 1) * SS + 1))
    shrink = m.filter(ImageFilter.MinFilter(width * SS + 1))
    band = np.asarray(grow, float) / 255 - np.asarray(shrink, float) / 255
    return np.asarray(Image.fromarray((band * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(SS * 0.8)),
                      float) / 255


def light(t, k, color, halo_px):
    """Light from the tube mask t (0..1 array) at strength k: a white-hot core, the coloured tube and three halos."""
    def blur(a, r):
        return np.asarray(Image.fromarray((a * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r)), float) / 255
    core = np.clip((t - 0.55) / 0.45, 0, 1)
    halo = (blur(t, halo_px * SS / 8) * 0.9 + blur(t, halo_px * SS * 3 / 8) * 0.65
            + blur(t, halo_px * SS) * 0.6)
    col = (t[..., None] * 1.1 + halo[..., None]) * np.array(color, float)[None, None, :] / 255 + core[..., None] * 0.75
    return col * k


def save(rgb, name):
    a = np.clip(rgb.max(-1), 0, 1)
    out = np.clip(rgb / np.maximum(a, 1e-4)[..., None], 0, 1)      # straight alpha: colour, and how much of it
    img = Image.fromarray(np.dstack([out * 255, a * 255]).astype(np.uint8), 'RGBA')
    img = img.resize((img.width // SS, img.height // SS), Image.LANCZOS)
    img.save(os.path.join(ROOT, 'assets', 'ui', name + '.png'))
    print(name, img.size)


def main():
    pink = (255, 52, 104)
    full, one = masks('RAY KESSLER', 'DejaVuSerif-BoldItalic.ttf', 160, 90, flicker=7)
    tf, to = tube(full, 5), tube(one, 5)
    rest = np.clip(tf - to, 0, 1)
    for name, k in (('title_logo', 1.0), ('title_logo_dim', 0.12)):
        rgb = light(rest, 1.0, pink, 48) + light(to, k, pink, 48)
        # the unlit glass still catches a little light where the tube is dark
        rgb += (to * (1 - k) * 0.12)[..., None] * np.array([0.6, 0.5, 0.55])
        save(rgb, name)
    full, _ = masks('NIGHTSHIFT', 'DejaVuSans-Bold.ttf', 64, 50, spacing=18)
    save(light(tube(full, 3), 1.0, (80, 150, 255), 28), 'title_sub')


if __name__ == '__main__':
    main()
