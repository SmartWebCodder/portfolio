# -*- coding: utf-8 -*-
"""Delete images no component references.

Most of public/ds came from the template and has since been replaced (the
scroll-jack stack, the client logos, the old project thumbnails).
"""
import glob
import os
import re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOTS = ['public/ds', 'public/avatars', 'public/tech', 'public/projects']
EXT = ('.png', '.jpg', '.jpeg', '.webp', '.svg')


def main():
    referenced = set()
    for path in glob.glob(os.path.join(REPO, 'components', '**', '*.tsx'),
                          recursive=True):
        referenced.update(re.findall(r'src="(/[^"]+)"', open(path).read()))
    for path in glob.glob(os.path.join(REPO, 'styles', '*.css')):
        referenced.update(re.findall(r'url\("(/[^"]+)"\)', open(path).read()))

    freed = removed = 0
    for root in ROOTS:
        full = os.path.join(REPO, root)
        if not os.path.isdir(full):
            continue
        for name in sorted(os.listdir(full)):
            if not name.lower().endswith(EXT):
                continue
            rel = '/' + os.path.relpath(os.path.join(full, name),
                                        os.path.join(REPO, 'public'))
            if rel in referenced:
                continue
            freed += os.path.getsize(os.path.join(full, name))
            os.remove(os.path.join(full, name))
            removed += 1

    print('pruned %d unreferenced images, %.1f MB' % (removed, freed / 1e6))


if __name__ == '__main__':
    main()
