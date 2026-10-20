"""Builds the shipped icon files from design A of gen_icon.py:
  icon.png (project icon), icon.ico (Windows exe, 16..256), tools/steam/icons/ (client .ico 32 px, community jpg 184 px)."""
import os, sys
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
import gen_icon

root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
src = gen_icon.design_a()
src.resize((512, 512), Image.LANCZOS).save(os.path.join(root, 'icon.png'))
sizes = [16, 24, 32, 48, 64, 128, 256]
src.save(os.path.join(root, 'icon.ico'), sizes=[(s, s) for s in sizes])
sd = os.path.join(root, 'tools', 'steam', 'icons')
os.makedirs(sd, exist_ok=True)
src.save(os.path.join(sd, 'nightshift_client.ico'), sizes=[(32, 32)])
bg = Image.new('RGB', (1024, 1024), (14, 10, 28))       # jpg has no alpha: flatten the rounded corners onto the night colour
bg.paste(src, mask=src.getchannel('A'))
bg.resize((184, 184), Image.LANCZOS).save(os.path.join(sd, 'nightshift_community_184.jpg'), quality=95)
