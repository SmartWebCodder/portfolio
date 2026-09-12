# -*- coding: utf-8 -*-
"""Prepare the hero portrait and the footer backdrop.

Project screenshots are handled by tools/mockups.py. Reads its originals from
projects/, which is not committed.
"""
import os
from PIL import Image, ImageDraw

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, 'projects')
OUT = os.path.join(REPO, 'public', 'projects')

PORTRAIT_WIDTH = 1100

os.makedirs(OUT, exist_ok=True)


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

    # idempotent: a second pass would rotate the hue past orange
    probe = img.copy()
    probe.thumbnail((120, 120))
    greens = 0
    for r, g, b in probe.convert('RGB').getdata():
        if max(r, g, b) < 40:
            continue
        hue, _, sat = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
        if sat > 0.15 and 0.28 < hue < 0.55:
            greens += 1
    if greens < 50:
        print('%-34s already orange, skipped' % 'footer glow')
        return

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


def prepare_loader():
    """Size the loader artwork for the web. It already ships without a bar; the
    page draws a real one underneath it."""
    src = os.path.join(SRC, 'load.png')
    if not os.path.exists(src):
        return
    # the artwork is transparent; flattening it onto a colour draws a box
    img = Image.open(src).convert('RGBA')
    if img.width > 900:
        img = img.resize((900, round(img.height * 900 / img.width)), Image.LANCZOS)
    out = os.path.join(REPO, 'public', 'loader.webp')
    img.save(out, 'WEBP', quality=88, method=6, lossless=False)
    print('%-34s %7.1f MB -> %6.0f KB' % (
        'loader.webp', os.path.getsize(src) / 1e6, os.path.getsize(out) / 1e3))


prepare_loader()


def prepare_social_card():
    """Build the 1200x630 card link previews use."""
    src = os.path.join(SRC, 'seo.png')
    if not os.path.exists(src):
        return
    img = Image.open(src).convert('RGB')

    target = 1200 / 630
    if img.width / img.height > target:
        w = round(img.height * target)
        img = img.crop(((img.width - w) // 2, 0, (img.width - w) // 2 + w, img.height))
    else:
        h = round(img.width / target)
        img = img.crop((0, 0, img.width, h))

    img = img.resize((1200, 630), Image.LANCZOS)
    out = os.path.join(REPO, 'public', 'og.jpg')
    img.save(out, 'JPEG', quality=86, optimize=True, progressive=True)
    print('%-34s %7.1f MB -> %6.0f KB' % (
        'og.jpg', os.path.getsize(src) / 1e6, os.path.getsize(out) / 1e3))


prepare_social_card()


def peace_favicon():
    """A peace sign, drawn rather than cropped from a photo."""
    size = 512
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    accent = (255, 122, 47, 255)
    pad = round(size * 0.06)
    stroke = round(size * 0.075)

    d.ellipse([pad, pad, size - pad, size - pad], fill=(17, 17, 17, 255))
    d.ellipse([pad, pad, size - pad, size - pad], outline=accent, width=stroke)

    cx = cy = size / 2
    r = (size - pad * 2) / 2 - stroke / 2
    d.line([(cx, cy - r), (cx, cy + r)], fill=accent, width=stroke)
    for dx in (-1, 1):
        d.line([(cx, cy), (cx + dx * r * 0.7071, cy + r * 0.7071)],
               fill=accent, width=stroke)

    out = os.path.join(REPO, 'public', 'favicon.png')
    img.save(out, 'PNG', optimize=True)
    print('%-34s %6.0f KB' % ('favicon.png (peace)', os.path.getsize(out) / 1e3))


peace_favicon()


def compress_template_images():
    """Re-encode the template photographs as WebP.

    They ship as full-size PNGs of photographs, which is the worst case for
    PNG; the cards render them a few hundred pixels wide. dslift rewrites the
    references to .webp to match.
    """
    src_dir = os.path.join(REPO, 'public', 'ds')
    if not os.path.isdir(src_dir):
        return

    before = after = 0
    converted = 0
    for name in sorted(os.listdir(src_dir)):
        if not name.lower().endswith(('.png', '.jpg', '.jpeg')):
            continue
        path = os.path.join(src_dir, name)
        size = os.path.getsize(path)
        if size < 40_000:
            continue

        img = Image.open(path)
        mode = 'RGBA' if img.mode in ('RGBA', 'LA', 'P') else 'RGB'
        img = img.convert(mode)
        if img.width > 1200:
            img = img.resize((1200, round(img.height * 1200 / img.width)),
                             Image.LANCZOS)

        out = os.path.splitext(path)[0] + '.webp'
        img.save(out, 'WEBP', quality=80, method=6)
        os.remove(path)
        before += size
        after += os.path.getsize(out)
        converted += 1

    if converted:
        print('%-34s %6.0f KB -> %6.0f KB  (%d files)' % (
            'template photos', before / 1e3, after / 1e3, converted))


compress_template_images()
