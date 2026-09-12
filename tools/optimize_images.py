# -*- coding: utf-8 -*-
"""Compress the project screenshots into web-sized WebP.

Each source is a ~3584x2240 PNG of several megabytes. The Works cards render
them at roughly 640px wide, so they are resized to a 2x-retina width and
re-encoded; a small blurred placeholder is written alongside each for the
loading shimmer.
"""
import os
from PIL import Image

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, 'projects')
OUT = os.path.join(REPO, 'public', 'projects')

WIDTH = 1280
QUALITY = 82
PORTRAIT_WIDTH = 1100

os.makedirs(OUT, exist_ok=True)


def slug(name):
    return os.path.splitext(name)[0].lower().replace('.', '-').replace('_', '-')


def convert(path, name):
    img = Image.open(path).convert('RGB')
    ratio = WIDTH / img.width
    img = img.resize((WIDTH, round(img.height * ratio)), Image.LANCZOS)

    full = os.path.join(OUT, name + '.webp')
    img.save(full, 'WEBP', quality=QUALITY, method=6)
    return os.path.getsize(path), os.path.getsize(full)


def trim_portrait():
    """Trim the hero cutout to its subject.

    The export carries wide transparent margins and is landscape, so it was
    being cropped oddly inside the hero's portrait frame.
    """
    src = os.path.join(SRC, 'nelson.png')
    if not os.path.exists(src):
        return
    img = Image.open(src)
    if img.mode not in ('RGBA', 'LA'):
        return
    box = img.getchannel('A').getbbox()
    if not box:
        return
    before = os.path.getsize(src)
    img = img.crop(box)
    if img.width > PORTRAIT_WIDTH:
        img = img.resize(
            (PORTRAIT_WIDTH, round(img.height * PORTRAIT_WIDTH / img.width)),
            Image.LANCZOS)
    out = os.path.join(REPO, 'public', 'nelson.webp')
    img.save(out, 'WEBP', quality=88, method=6)
    print('%-34s %7.1f MB -> %6.0f KB' % (
        'nelson.webp', before / 1e6, os.path.getsize(out) / 1e3))


trim_portrait()

total_in = total_out = 0
for f in sorted(os.listdir(SRC)):
    if not f.lower().endswith(('.png', '.jpg', '.jpeg')) or f == 'nelson.png':
        continue
    a, b = convert(os.path.join(SRC, f), slug(f))
    total_in += a
    total_out += b
    print('%-34s %7.1f MB -> %6.0f KB' % (slug(f), a / 1e6, b / 1e3))

print('total %.1f MB -> %.0f KB' % (total_in / 1e6, total_out / 1e3))


def recolour_footer_glow():
    """Shift the footer backdrop from the template's green to this site's orange.

    The glow is baked into a photo, so no CSS token reaches it; the hue is
    rotated in place instead.
    """
    import colorsys

    src = os.path.join(REPO, 'public', 'ds', 'YAiWqmJ1DFGxCJ93IHzGFZr2Yak.png')
    if not os.path.exists(src):
        return

    img = Image.open(src).convert('RGB')
    shift = (25 - 150) / 360.0          # green 150deg -> orange 25deg
    px = img.load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y]
            hue, light, sat = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
            if sat < 0.05:
                continue
            r, g, b = colorsys.hls_to_rgb((hue + shift) % 1.0, light, sat)
            px[x, y] = (round(r * 255), round(g * 255), round(b * 255))

    before = os.path.getsize(src)
    img.save(src, 'PNG', optimize=True)
    print('%-34s %7.0f KB -> %6.0f KB' % (
        'footer glow (recoloured)', before / 1e3, os.path.getsize(src) / 1e3))


recolour_footer_glow()
