"""Generates Nightshift's mouse cursors and the raindrop texture (1920x1080 UI scale).
Room backgrounds, the detective and the item icons are rendered by tools/r3 - see README.
Run from anywhere:  python tools/gen_art.py   (needs Pillow)"""
import os
from PIL import Image, ImageDraw

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')


def out(p):
    path = os.path.join(ROOT, p); os.makedirs(os.path.dirname(path), exist_ok=True); return path


def cursor(col, name, size=48, k=4):
    """Crosshair with a dark outline, drawn at k x and downsampled for smooth edges."""
    S = size * k
    im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    c = S // 2; gap = 7 * k; arm = 22 * k
    for width, colour in ((7 * k, (0, 0, 0, 200)), (3 * k, col + (255,))):
        for (x0, y0, x1, y1) in ((c, c - arm, c, c - gap), (c, c + gap, c, c + arm),
                                 (c - arm, c, c - gap, c), (c + gap, c, c + arm, c)):
            d.line([x0, y0, x1, y1], fill=colour, width=width)
    d.ellipse([c - 2 * k, c - 2 * k, c + 2 * k, c + 2 * k], fill=col + (255,))
    im.resize((size, size), Image.LANCZOS).save(out(f'assets/ui/{name}.png'))


def main():
    cursor((236, 232, 214), 'cursor')
    cursor((255, 196, 90), 'cursor_hot')
    drop = Image.new('RGBA', (2, 28), (0, 0, 0, 0)); d = ImageDraw.Draw(drop)
    for y in range(28):
        d.point((0, y), fill=(190, 210, 240, int(40 + 70 * y / 27)))
        d.point((1, y), fill=(190, 210, 240, int(20 + 40 * y / 27)))
    drop.save(out('assets/rooms/raindrop.png'))
    print('cursors + raindrop done')


if __name__ == '__main__':
    main()
