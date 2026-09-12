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

# app screenshots, two per project
MOBILE = {
    'paysnap-app': ('paysnap2.jpeg', 'paysnap1.jpeg'),
    'chopexpress-app': ('chopexpress1.png', 'chopexpress-2.png'),
    'kimo-games': ('kimo-1.jpeg', 'kimo2.jpeg'),
}

# sources that are not standalone project screenshots
SKIP = {'nelson.png', 'load.png', 'seo.png'} | {
    n for names in MOBILE.values() for n in names}

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


def placeholder_screen(size):
    """The screen for the open slot: a terminal prompt, not a screenshot."""
    w, h = size
    img = Image.new('RGB', (w, h), (18, 18, 20))
    d = ImageDraw.Draw(img)

    from PIL import ImageFont
    def font(px, bold=False):
        for path in ('/System/Library/Fonts/Menlo.ttc',
                     '/System/Library/Fonts/Monaco.ttf',
                     '/System/Library/Fonts/Supplemental/Courier New.ttf'):
            if os.path.exists(path):
                try:
                    return ImageFont.truetype(path, px)
                except OSError:
                    continue
        return ImageFont.load_default()

    bar = round(h * 0.075)
    d.rectangle([0, 0, w, bar], fill=(32, 32, 36))
    for i, tone in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        cx = round(bar * 0.55) + i * round(bar * 0.5)
        r = round(bar * 0.14)
        d.ellipse([cx - r, bar / 2 - r, cx + r, bar / 2 + r], fill=tone)

    x, y = round(w * 0.07), round(h * 0.22)
    size_l = round(h * 0.055)
    d.text((x, y), '> awaiting brief...', font=font(size_l), fill=(255, 122, 47))
    d.text((x, y + size_l * 2.0), 'YOUR NEXT', font=font(round(h * 0.13)),
           fill=(245, 245, 245))
    d.text((x, y + size_l * 2.0 + round(h * 0.145)), 'PROJECT',
           font=font(round(h * 0.13)), fill=(255, 122, 47))
    d.text((x, y + size_l * 2.0 + round(h * 0.33)),
           'schema  ->  api  ->  interface  ->  shipped',
           font=font(round(h * 0.042)), fill=(150, 150, 155))
    return img


def phone(shot, height):
    """One phone, drawn around a screenshot, on transparency."""
    screen_w = round(height * 0.455)
    screen_h = round(height * 0.955)
    bezel = max(6, round(height * 0.011))
    w = screen_w + bezel * 2
    h = screen_h + bezel * 2
    radius = round(w * 0.13)

    body = rounded((w, h), radius, (24, 24, 27, 255))
    d = ImageDraw.Draw(body)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=radius,
                        outline=(58, 58, 64, 255), width=max(2, bezel // 3))

    ratio = max(screen_w / shot.width, screen_h / shot.height)
    fitted = shot.resize(
        (math.ceil(shot.width * ratio), math.ceil(shot.height * ratio)),
        Image.LANCZOS)
    fitted = fitted.crop((
        (fitted.width - screen_w) // 2, 0,
        (fitted.width - screen_w) // 2 + screen_w, screen_h))

    mask = rounded((screen_w, screen_h), round(radius * 0.8),
                   (255, 255, 255, 255)).getchannel('A')
    body.paste(fitted.convert('RGB'), (bezel, bezel), mask)

    # dynamic island
    island_w, island_h = round(screen_w * 0.3), round(screen_h * 0.022)
    ImageDraw.Draw(body).rounded_rectangle(
        [(w - island_w) / 2, bezel + island_h * 0.5,
         (w + island_w) / 2, bezel + island_h * 1.5],
        radius=island_h, fill=(12, 12, 14, 255))

    return body


def phones(shots, canvas=CANVAS):
    """Two app screens, angled, on the same backdrop the laptops use."""
    w, h = canvas
    scene = backdrop(canvas).convert('RGBA')

    height = round(h * 0.86)
    angles = (-9, 9)
    offsets = (-0.155, 0.155)
    lifts = (0.04, -0.02)

    for shot, angle, dx, lift in zip(shots, angles, offsets, lifts):
        device = phone(shot, height).rotate(angle, resample=Image.BICUBIC,
                                            expand=True)
        x = round(w / 2 + w * dx - device.width / 2)
        y = round(h / 2 + h * lift - device.height / 2)

        shadow = Image.new('RGBA', canvas, (0, 0, 0, 0))
        shadow.paste(Image.new('RGBA', device.size, (20, 8, 0, 120)),
                     (x + 14, y + 26), device.getchannel('A'))
        scene.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(24)))
        scene.alpha_composite(device, (x, y))

    return scene.convert('RGB')


def main():
    os.makedirs(OUT, exist_ok=True)
    total = 0
    for name in sorted(os.listdir(SRC)):
        if (not name.lower().endswith(('.png', '.jpg', '.jpeg'))
                or name in SKIP):
            continue
        slug = os.path.splitext(name)[0].lower().replace('.', '-').replace('_', '-')
        shot = Image.open(os.path.join(SRC, name)).convert('RGB')
        out = os.path.join(OUT, slug + '.webp')
        laptop(shot).save(out, 'WEBP', quality=QUALITY, method=6)
        size = os.path.getsize(out)
        total += size
        print('%-34s %6.0f KB' % (slug, size / 1e3))
    for slug, names in MOBILE.items():
        shots = [Image.open(os.path.join(SRC, n)).convert('RGB') for n in names]
        out = os.path.join(OUT, slug + '.webp')
        phones(shots).save(out, 'WEBP', quality=QUALITY, method=6)
        total += os.path.getsize(out)
        print('%-34s %6.0f KB' % (slug, os.path.getsize(out) / 1e3))

    slot = laptop(placeholder_screen((2560, 1600)))
    out = os.path.join(OUT, 'your-next-project.webp')
    slot.save(out, 'WEBP', quality=QUALITY, method=6)
    total += os.path.getsize(out)
    print('%-34s %6.0f KB' % ('your-next-project', os.path.getsize(out) / 1e3))

    print('total %.0f KB' % (total / 1e3))


if __name__ == '__main__':
    main()
