# -*- coding: utf-8 -*-
"""Draw an initials avatar per testimonial.

Stock portraits of people who did not say these things would be misleading, so
each card carries a lettermark in the site's palette instead.
"""
import json
import os

from PIL import Image, ImageDraw, ImageFont

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, 'public', 'avatars')
SIZE = 192

TONES = [
    ((255, 122, 47), (120, 44, 10)),
    ((255, 168, 94), (110, 52, 16)),
    ((232, 96, 32), (96, 34, 6)),
    ((255, 196, 140), (128, 62, 22)),
]

FONTS = [
    '/System/Library/Fonts/Supplemental/Futura.ttc',
    '/System/Library/Fonts/HelveticaNeue.ttc',
    '/System/Library/Fonts/Helvetica.ttc',
]


def font(size):
    for path in FONTS:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size, index=0)
            except OSError:
                continue
    return ImageFont.load_default()


def initials(name):
    parts = [p for p in name.replace("'", ' ').split() if p[:1].isalpha()]
    return (parts[0][0] + (parts[-1][0] if len(parts) > 1 else '')).upper()


def draw(text, tone):
    fg, bg = tone
    img = Image.new('RGB', (SIZE, SIZE), bg)
    d = ImageDraw.Draw(img)
    d.ellipse([0, 0, SIZE - 1, SIZE - 1], fill=bg)
    f = font(round(SIZE * 0.42))
    box = d.textbbox((0, 0), text, font=f)
    d.text(((SIZE - box[2] + box[0]) / 2 - box[0],
            (SIZE - box[3] + box[1]) / 2 - box[1]),
           text, font=f, fill=fg)
    return img


def main():
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(REPO, 'content', 'testimonials.json')) as f:
        people = json.load(f)

    for n, person in enumerate(people, start=1):
        img = draw(initials(person['name']), TONES[n % len(TONES)])
        img.save(os.path.join(OUT, 'a%d.png' % n), 'PNG', optimize=True)
    print('avatars written:', len(people))


if __name__ == '__main__':
    main()
