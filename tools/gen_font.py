"""Builds a crisp 1-bit bitmap font (BMFont text format) for the UI.
Glyphs come from Pillow's built-in bitmap font. Run: python tools/gen_font.py"""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
OUT = os.path.join(ROOT, 'assets', 'fonts'); os.makedirs(OUT, exist_ok=True)
font = ImageFont.load_default_imagefont()
chars = [chr(c) for c in range(32, 127)] + list('’…—éäö')
CW, CH = 8, 13
cols = 16
rows = (len(chars) + cols - 1) // cols
sheet = Image.new('RGBA', (cols * CW, rows * CH), (0, 0, 0, 0))
lines = []
asc = 10
glyphs = []
for i, ch in enumerate(chars):
    g = Image.new('L', (CW, CH), 0)
    try:
        ImageDraw.Draw(g).text((0, 0), ch, fill=255, font=font)
    except Exception:
        continue
    g = g.point(lambda v: 255 if v > 100 else 0)
    bbox = g.getbbox()
    adv = (bbox[2] + 1) if bbox else 4
    if ch == ' ': adv = 4
    x, y = (i % cols) * CW, (i // cols) * CH
    sheet.paste(Image.new('RGBA', (CW, CH), (255, 255, 255, 255)), (x, y), g)
    glyphs.append(f'char id={ord(ch)} x={x} y={y} width={CW} height={CH} xoffset=0 yoffset=0 xadvance={max(adv, 3)} page=0 chnl=15')
sheet.save(os.path.join(OUT, 'pixel.png'))
with open(os.path.join(OUT, 'pixel.fnt'), 'w') as f:
    f.write(f'info face="NightshiftPixel" size={CH} bold=0 italic=0 charset="" unicode=1 stretchH=100 smooth=0 aa=1 padding=0,0,0,0 spacing=0,0\n')
    f.write(f'common lineHeight={CH} base={asc} scaleW={sheet.width} scaleH={sheet.height} pages=1 packed=0\n')
    f.write('page id=0 file="pixel.png"\n')
    f.write(f'chars count={len(glyphs)}\n')
    f.write('\n'.join(glyphs) + '\n')
print('font done', len(glyphs))
