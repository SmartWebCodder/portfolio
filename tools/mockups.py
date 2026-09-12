# -*- coding: utf-8 -*-
"""Render each project screenshot into a laptop mockup on a branded backdrop.

The Works cards mix full-page screenshots of very different proportions, which
reads as inconsistent. Each one is composited into the same laptop frame over
an orange gradient so the grid is uniform and on-brand.
"""
import math
import os

from PIL import Image, ImageDraw, ImageFilter

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, 'projects')
OUT = os.path.join(REPO, 'public', 'projects')

CANVAS = (1600, 1000)
QUALITY = 82

# backdrop, deep to light orange
DEEP = (74, 22, 2)
MID = (214, 92, 20)
LIGHT = (255, 205, 165)

BEZEL = (28, 28, 30)
BODY = (176, 178, 184)
BODY_EDGE = (128, 130, 136)


def _ramp(t):
    """Deep orange through mid to a light tint."""
    if t < 0.55:
        a, b, k = DEEP, MID, t / 0.55
    else:
        a, b, k = MID, LIGHT, (t - 0.55) / 0.45
    k = k * k * (3 - 2 * k)
    return tuple(round(a[i] + (b[i] - a[i]) * k) for i in range(3))


def backdrop(size):
    """A diagonal orange gradient, deep in one corner and light in the other."""
    w, h = size
    base = Image.new('RGB', (w, h))
    px = base.load()
    for y in range(h):
        for x in range(0, w, 3):
            t = min(1.0, (x / w) * 0.6 + (1 - y / h) * 0.4)
            c = _ramp(t)
            for dx in range(min(3, w - x)):
                px[x + dx, y] = c

    glow = Image.new('L', (w, h), 0)
    ImageDraw.Draw(glow).ellipse(
        [w * 0.45, -h * 0.45, w * 1.25, h * 0.75], fill=150)
    glow = glow.filter(ImageFilter.GaussianBlur(w // 7))
    return Image.composite(Image.new('RGB', (w, h), LIGHT), base, glow)


def rounded(size, radius, fill):
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    ImageDraw.Draw(img).rounded_rectangle(
        [0, 0, size[0] - 1, size[1] - 1], radius=radius, fill=fill)
    return img


def laptop(shot, canvas=CANVAS):
    """Composite one screenshot into a laptop over the backdrop."""
    w, h = canvas
    scene = backdrop(canvas).convert('RGBA')

    lid_w = round(w * 0.66)
    lid_h = round(lid_w * 0.625)            # 16:10
    lid_x = (w - lid_w) // 2
    lid_y = round(h * 0.13)

    shadow = Image.new('RGBA', canvas, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle(
        [lid_x + 18, lid_y + 34, lid_x + lid_w + 18, lid_y + lid_h + 70],
        radius=28, fill=(20, 8, 0, 110))
    scene.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(26)))

    scene.alpha_composite(rounded((lid_w, lid_h), 18, BEZEL + (255,)), (lid_x, lid_y))

    pad = round(lid_w * 0.013)
    screen_w, screen_h = lid_w - pad * 2, lid_h - pad * 2

    # cover-crop the screenshot to the screen, anchored at the top
    ratio = max(screen_w / shot.width, screen_h / shot.height)
    fitted = shot.resize(
        (math.ceil(shot.width * ratio), math.ceil(shot.height * ratio)),
        Image.LANCZOS)
    fitted = fitted.crop((
        (fitted.width - screen_w) // 2, 0,
        (fitted.width - screen_w) // 2 + screen_w, screen_h))

    mask = rounded((screen_w, screen_h), 10, (255, 255, 255, 255)).getchannel('A')
    scene.paste(fitted.convert('RGB'), (lid_x + pad, lid_y + pad), mask)

    # base: a shallow trapezoid under the lid, plus the notch
    base_y = lid_y + lid_h
    base_w = round(lid_w * 1.13)
    base_x = (w - base_w) // 2
    base_h = round(lid_h * 0.028)
    deck = Image.new('RGBA', canvas, (0, 0, 0, 0))
    d = ImageDraw.Draw(deck)
    d.polygon([(lid_x - 6, base_y), (lid_x + lid_w + 6, base_y),
               (base_x + base_w, base_y + base_h), (base_x, base_y + base_h)],
              fill=BODY + (255,))
    d.rounded_rectangle(
        [base_x, base_y + base_h - 2, base_x + base_w, base_y + base_h + 10],
        radius=6, fill=BODY_EDGE + (255,))
    d.rounded_rectangle(
        [w // 2 - round(lid_w * 0.07), base_y + base_h - 1,
         w // 2 + round(lid_w * 0.07), base_y + base_h + 6],
        radius=4, fill=(150, 152, 158, 255))
    scene.alpha_composite(deck)

    return scene.convert('RGB')


def main():
    os.makedirs(OUT, exist_ok=True)
    total = 0
    for name in sorted(os.listdir(SRC)):
        if not name.lower().endswith(('.png', '.jpg', '.jpeg')) or name == 'nelson.png':
            continue
        slug = os.path.splitext(name)[0].lower().replace('.', '-').replace('_', '-')
        shot = Image.open(os.path.join(SRC, name)).convert('RGB')
        out = os.path.join(OUT, slug + '.webp')
        laptop(shot).save(out, 'WEBP', quality=QUALITY, method=6)
        size = os.path.getsize(out)
        total += size
        print('%-34s %6.0f KB' % (slug, size / 1e3))
    print('total %.0f KB' % (total / 1e3))


if __name__ == '__main__':
    main()
