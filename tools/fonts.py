# -*- coding: utf-8 -*-
"""Self-host the webfonts the templates load from third-party CDNs.

Both stylesheets point @font-face at framerusercontent.com and fonts.gstatic.com,
which puts two extra origins on the critical path. The files are pulled into
public/fonts and the rules rewritten to match.

Blocks for scripts the site never renders (Cyrillic, Greek, Vietnamese) are
dropped, so neither the CSS nor the font directory carries them.
"""
import hashlib
import os
import re
import urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, 'public', 'fonts')
SHEETS = ['styles/devsync.css', 'styles/fastfolio.css']

# the ranges an English page actually uses
KEEP_RANGES = ('U+0000', 'U+0100', 'U+0001', 'U+2000')

FACE = re.compile(r'@font-face\s*\{[^}]*\}', re.S)
URL = re.compile(r'url\("(https://[^"]+\.woff2?)"\)')


def wanted(block):
    m = re.search(r'unicode-range:\s*([^;}]+)', block)
    if not m:
        return True
    return any(r in m.group(1) for r in KEEP_RANGES)


def main():
    os.makedirs(OUT, exist_ok=True)
    kept_urls = set()
    dropped = 0

    for sheet in SHEETS:
        path = os.path.join(REPO, sheet)
        css = open(path).read()

        def face(m):
            nonlocal dropped
            if not wanted(m.group(0)):
                dropped += 1
                return ''
            return m.group(0)

        css = FACE.sub(face, css)
        kept_urls |= set(URL.findall(css))
        open(path, 'w').write(css)

    local = {}
    for url in sorted(kept_urls):
        name = hashlib.sha1(url.encode()).hexdigest()[:12] + '.woff2'
        dest = os.path.join(OUT, name)
        if not os.path.exists(dest):
            try:
                urllib.request.urlretrieve(url, dest)
            except Exception as exc:
                print('  could not fetch', url[:60], exc)
                continue
        local[url] = '/fonts/' + name

    for sheet in SHEETS:
        path = os.path.join(REPO, sheet)
        css = open(path).read()
        css = URL.sub(
            lambda m: 'url("%s")' % local.get(m.group(1), m.group(1)), css)
        open(path, 'w').write(css)

    # remove any file no longer referenced
    for name in os.listdir(OUT):
        if '/fonts/' + name not in local.values():
            os.remove(os.path.join(OUT, name))

    size = sum(os.path.getsize(os.path.join(OUT, f)) for f in os.listdir(OUT))
    print('fonts self-hosted: %d files, %.0f KB (%d non-Latin faces dropped)'
          % (len(local), size / 1e3, dropped))


if __name__ == '__main__':
    main()
