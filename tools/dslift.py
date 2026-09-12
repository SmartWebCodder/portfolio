# -*- coding: utf-8 -*-
"""Turn the lifted Devsync page into Nelson's portfolio.

Content is swapped by matching an element's visible text, so one rule covers
every breakpoint variant and works whether Framer left the text whole or split
it into one span per character.
"""
import html as H
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import services
import works
from htmlutil import element_at, children_of, plain, retext, strip_em_dashes

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DS = os.path.join(REPO, '.lift', 'ds')

GITHUB = 'https://github.com/SmartWebCodder'
LINKEDIN = 'https://www.linkedin.com/in/akintoye-ayomide-nelson/'
MAILTO = 'mailto:akintoyenelson@gmail.com'
X_URL = 'https://x.com/_NelsonAyo'
TEL = 'tel:+2348138412167'

# The stats are a Framer code component that counts up from its own runtime.
# Without it they sit at zero, so each is replaced with a target the page can
# animate itself (see components/Counters.tsx).
STATS = {
    'Years in Experience': 7,
    'Teams Worldwide': 8,
    'Completed Projects': 50,
}

# The template's logos are invented brands. These are the real ones, drawn as
# wordmarks so nothing claims a client that does not exist.
CLIENTS = ['Paysnap', 'Betro', 'Unispend', 'SynthrixAi',
           'RCCG KT', 'Ikebest', 'Afobaino', 'OBC Ibadan']
KEEP_CLIENTS = len(CLIENTS)
DROP_FOOTER_LINKS = {'404', 'PRIVACY POLICY', 'TERM & CONDITION',
                     'PRIVACYPOLICY', 'TERM&CONDITION'}

HERO_PORTRAIT = '/ds/e8w16q5wJI84smxcPUFYRRZmI.png'
PORTRAIT = '/nelson.webp'

MAIL_ICON = (
    '<svg class="hero-icon" viewBox="0 0 24 24" fill="none" aria-hidden="true">'
    '<rect x="2.5" y="4.5" width="19" height="15" rx="2.5"/>'
    '<path d="m3 7 9 6 9-6"/></svg>')
PHONE_ICON = (
    '<svg class="hero-icon" viewBox="0 0 24 24" fill="none" aria-hidden="true">'
    '<path d="M6.5 3h3l1.5 4-2 1.5a12 12 0 0 0 6.5 6.5L17 13l4 1.5v3a2 2 0 0 1'
    '-2.2 2A17 17 0 0 1 3 5.2 2 2 0 0 1 5 3Z"/></svg>')

ROLLING = {
    # hero social row
    'Twitter (X)': 'X',
    'CodePen': 'Email',
    # footer, Portfolio column
    'CONTRA': 'PROJECTS',
    'GITHUB': 'GITHUB',
    'CODEPEN': 'EMAIL',
    # footer, Social column
    'INSTAGRAM': 'GITHUB',
    'TWITTER “X”': 'X',
    # buttons
    'My Resume': 'Contact Me',
    'Start Project': 'Contact Me',
    'Hire Me': 'Contact Me',
}

TEXT = {
    'Buy Template For $49': '',

    'Bruno Simon': 'Akintoye Nelson',
    'I craft fast, scalable, and user-friendly web applications with modern '
    'JavaScript frameworks — combining React on the frontend with robust '
    'server-side solutions using Node.js.':
        'I craft fast, scalable, and user-friendly web applications with modern '
        'JavaScript frameworks — combining React and Next.js on the frontend '
        'with robust server-side systems in Node.js, NestJS and PostgreSQL.',
    'info@brunosimon.com': 'akintoyenelson@gmail.com',
    'brunosimon@gmail.com': 'akintoyenelson@gmail.com',
    '+39 03 463 853 02': '+234 813 841 2167',
    '(684) 555-0102': '+234 813 841 2167',

    'Tailwind CSS': 'Next.js',
    'Express.js': 'NestJS',
    'MongoDB': 'PostgreSQL',
    'PHP': 'MongoDB',
    'Laravel': 'Redis',
    'Github': 'GitHub',
    'Stack Overflow': 'Prisma',

    'Clients Worldwide': 'Teams Worldwide',
    'Start Project': 'Contact Me',
    'Hire Me ': 'Contact Me',
    'Hire Me': 'Contact Me',
    'Protfolio': 'Portfolio',

    'Working with Bruno Simon was one of the best decisions we made for our web '
    'platform. He understood our vision, delivered clean & scalable code, and '
    'communicated clearly throughout the project.':
        'Working with Nelson was one of the best decisions we made for our web '
        'platform. He understood our vision, delivered clean & scalable code, '
        'and communicated clearly throughout the project.',
}

HREFS = {
    'index.html': '#top',
    'about.html': '#about-us',
    'projects.html': '#explore',
    'blog.html': '#blogs',
    'contact-us.html': MAILTO,
    '404.html': '#top',
    'legal/privacy-policy.html': '#top',
    'legal/terms-conditions.html': '#top',

    'https://twitter.com/?lang=en': X_URL,
    'https://www.linkedin.com/': LINKEDIN,
    'https://github.com/': GITHUB,
    'https://codepen.io/': MAILTO,
    'https://contra.com/': '#explore',
    'https://stackoverflow.com/': GITHUB,
    'https://www.instagram.com/': GITHUB,
    'https://read.cv/explore': MAILTO,

    'mailto:brunosimon@gmail.com': MAILTO,
    'mailto:info@brunosimon.com': MAILTO,
    'tel:(684) 555-0102': TEL,
    'tel:+39 03 463 853 02': TEL,

    'blog/frontend-vs-backend-which-path-should-you-choose.html': '#blogs',
    'blog/11-seo-for-developers-optimizing-websites-for-better-rankings.html': '#blogs',
    'blog/working-remotely-as-a-full-stack-developer-my-workflow-tools.html': '#blogs',
}

ACCENT_SWAPS = [
    (r'rgb\(\s*122\s*,\s*242\s*,\s*152\s*\)', 'var(--accent)'),
    (r'#7af298', 'var(--accent)'),
    (r'rgba\(\s*153\s*,\s*247\s*,\s*177\s*,\s*([0-9.]+)\s*\)',
     r'rgba(255, 138, 71, \1)'),
    (r'rgba\(\s*83\s*,\s*137\s*,\s*114\s*,\s*([0-9.]+)\s*\)',
     r'rgba(137, 83, 39, \1)'),
]


def strip_promo(page):
    """Remove the template's own "Get this template" overlay."""
    i = page.find('<div class="framer-4b2use-container">')
    if i < 0:
        return page
    span = element_at(page, i)
    print('stripped promo overlay:', span[2] - i, 'chars')
    return page[:i] + page[span[2]:]


def localise_images(page):
    page = re.sub(r'\s(?:srcset|srcSet)="[^"]*"', '', page)
    page = re.sub(r'\ssizes="[^"]*"', '', page)
    page = re.sub(r'src="https://framerusercontent\.com/images/([^"?]+)[^"]*"',
                  lambda m: 'src="/%s"' % os.path.join('ds', m.group(1)), page)

    page = page.replace(HERO_PORTRAIT, PORTRAIT)
    # the template leaves a bare `alt` on its images, and its intrinsic
    # width/height no longer describe this file
    page = re.sub(
        r'<img\b[^>]*?%s[^>]*>' % re.escape(PORTRAIT),
        lambda m: re.sub(r'\s(?:alt(?:="[^"]*")?|width="[^"]*"|height="[^"]*")(?=[\s>])',
                         '', m.group(0)).replace(
            'src="%s"' % PORTRAIT,
            'src="%s" alt="Akintoye Ayomide Nelson"' % PORTRAIT),
        page)
    return page


def strip_scroll_jack(page):
    """Remove the scroll-jacked image band from the About section.

    Two parts: the image stack itself, and the three empty "scroll animation
    layer" divs that gave the scrub its travel. The layers are 556px of nothing
    once the pin is gone, which is what left the gap above the skills.
    """
    i = page.find('data-framer-name="Image Group"')
    if i >= 0:
        a = page.rfind('<div', 0, i)
        span = element_at(page, a)
        print('removed scroll-jack image group:', span[2] - a, 'chars')
        page = page[:a] + page[span[2]:]

    removed = 0
    for n in (1, 2, 3):
        marker = 'id="scroll-animation-layer%d"' % n
        j = page.find(marker)
        if j < 0:
            continue
        a = page.rfind('<div', 0, j)
        span = element_at(page, a)
        removed += span[2] - a
        page = page[:a] + page[span[2]:]
    print('removed scroll animation layers:', removed, 'chars')
    return page


def swap_wordmark(page):
    """The logo is a fixed-size image asset; live text can carry any name."""
    page, n = re.subn(
        r'<div aria-label="Brand logo" class="framer-1azl6kd">.*?</div></div>',
        '<div aria-label="Brand logo" class="framer-1azl6kd brand-mark">'
        '<span class="brand-mark__text">Akintoye Nelson</span></div>',
        page, flags=re.S)
    print('logo marks replaced:', n)
    return page


def rewrite_rolling_text(page):
    """Framer renders hover-roll text as one <span> per character."""
    span_re = re.compile(r'<span style="([^"]*)">([^<]*)</span>', re.S)
    hits = {}

    def one(m):
        spans = span_re.findall(m.group(2))
        if not spans:
            return m.group(0)
        text = H.unescape(''.join(c for _, c in spans)).replace(' ', ' ')
        new = ROLLING.get(text.strip())
        if new is None:
            return m.group(0)
        hits[text.strip()] = hits.get(text.strip(), 0) + 1
        style = spans[0][0]
        # Framer separates words with NBSP so a roll keeps them on one line.
        body = ''.join('<span style="%s">%s</span>'
                       % (style, H.escape(c if c != ' ' else ' '))
                       for c in new)
        # Framer emits a per-instance <style> keyed to this exact class name;
        # keep the hash or the block loses its layout and colour.
        return '<p class="%s">%s</p>' % (m.group(1), body)

    page = re.sub(r'<p class="(rolling-text-inner-[A-Za-z0-9]+)">(.*?)</p>',
                  one, page, flags=re.S)
    print('rolling text rewritten:', hits)
    return page


def tag_tickers(page):
    """Give each Ticker/Slider track a class and a duplicated run.

    Framer animates these from its runtime, which is not shipped; CSS drives
    them instead, translating by half a track that holds its items twice.
    """
    section_re = re.compile(r'<section style="display:flex[^"]*">')
    out, i, kinds = [], 0, []
    while True:
        m = section_re.search(page, i)
        if not m:
            out.append(page[i:])
            break
        span = element_at(page, m.start())
        block = page[m.start():span[2]]

        enclosing = page.rfind('<section class=', 0, m.start())
        name = re.search(r'data-framer-name="([^"]*)"',
                         page[enclosing:enclosing + 300])
        kind = 'marquee' if (name and name.group(1).strip() == 'About us') else 'slider'
        kinds.append(kind)

        block = block.replace(
            m.group(0),
            m.group(0).replace('opacity:0;', '').replace('opacity:0.001;', ''), 1)

        ul = re.search(r'<ul style="([^"]*)"', block)
        if ul:
            ul_span = element_at(block, ul.start())
            items = block[ul_span[0]:ul_span[1]]
            style = (ul.group(1)
                     .replace('width:100%;', 'width:max-content;')
                     .replace('transform:translateX(-0px)', 'transform:none'))
            block = (block[:ul.start()]
                     + '<ul class="ds-%s__track" style="%s">%s%s</ul>'
                       % (kind, style, items, items)
                     + block[ul_span[2]:])

        out.append(page[i:m.start()])
        out.append(block)
        i = span[2]

    print('tickers tagged:', len(kinds), kinds)
    return ''.join(out)


def contact_icons(page):
    """The template labels the hero contact rows with a bare "E" and "T"."""
    for cls, icon in (('framer-15utcab', MAIL_ICON),
                      ('framer-1avki3e', PHONE_ICON)):
        page, n = re.subn(
            r'(<div class="%s"[^>]*>)<p class="framer-text[^"]*"[^>]*>[^<]*</p>' % cls,
            lambda m: m.group(1) + icon, page)
        print('  %s -> icon x%d' % (cls, n))

    # the separator's space is a plain space the browser collapses away
    page, n = re.subn(r'(>/<span class="framer-text"[^>]*>)\s*(</span>)',
                      r'\1&nbsp;\2', page)
    print('  social separators spaced:', n)
    return page


def wire_counters(page):
    """Swap Framer's counter component for a span the page can animate.

    Each metric is one child of the Progress Metrics block, so the target is
    matched on the label the child renders.
    """
    wired = 0
    start = 0
    while True:
        i = page.find('data-framer-name="Progress Metrics ', start)
        if i < 0:
            break
        block = page.rfind('<div', 0, i)
        span = element_at(page, block)
        if not span:
            break
        start = span[2]

        for a, b in reversed(list(children_of(page, block))):
            text = plain(page[a:b])
            target = next((v for k, v in STATS.items() if text.endswith(k)), None)
            if target is None:
                continue
            child = page[a:b]
            m = re.search(r'<span style="display:inline-flex[^"]*">', child)
            if not m:
                continue
            # replace the span's contents, not a guessed run of closing tags:
            # matching '</span></span>' left the outermost one unbalanced and
            # silently truncated the document.
            inner = element_at(child, m.start())
            child = (child[:inner[0]]
                     + '<span data-count="%d">0</span>' % target
                     + child[inner[1]:])
            page = page[:a] + child + page[b:]
            wired += 1

    print('counters wired:', wired)
    return page


def trim_clients(page):
    """Keep four of the template's eight client logos, in every breakpoint grid.

    Each grid holds a logo once per breakpoint, so the children come in
    consecutive pairs; dropping the tail keeps the pairs intact.
    """
    section = page.find('id="my-client"')
    if section < 0:
        return page

    trimmed = 0
    cursor = section
    while True:
        i = page.find('data-framer-name="Logo Wrapper"', cursor)
        if i < 0:
            break

        grid = i
        while True:
            grid = page.rfind('<div', 0, grid)
            if grid < 0 or grid < section:
                grid = None
                break
            span = element_at(page, grid)
            if span and page[span[0]:span[1]].count('data-framer-name="Logo Wrapper"') > 1:
                break
        if grid is None:
            break

        kids = list(children_of(page, grid))
        per_logo = 2 if len(kids) % 2 == 0 else 1
        keep = KEEP_CLIENTS * per_logo
        if len(kids) > keep:
            page = page[:kids[keep][0]] + page[kids[-1][1]:]

        # swap each logo's stack of images for the client's name
        kids = list(children_of(page, grid))
        out = []
        for n, (a, b) in enumerate(kids):
            name = CLIENTS[(n // per_logo) % len(CLIENTS)]
            cell = page[a:b]
            w = cell.find('data-framer-name="Logo Wrapper"')
            if w >= 0:
                start = cell.rfind('<div', 0, w)
                span = element_at(cell, start)
                cell = (cell[:span[0]]
                        + '<span class="client-mark">%s</span>' % name
                        + cell[span[1]:])
            out.append(cell)
        page = page[:kids[0][0]] + ''.join(out) + page[kids[-1][1]:]
        trimmed += 1
        cursor = element_at(page, grid)[2]

    print('client grids trimmed:', trimmed, 'to', KEEP_CLIENTS, 'logos each')
    return page


def trim_footer_links(page):
    """Drop the template's 404, privacy policy and terms links."""
    removed = 0
    while True:
        for m in re.finditer(r'<a\b', page):
            span = element_at(page, m.start())
            if not span:
                continue
            text = plain(page[span[0]:span[1]]).replace('\u00a0', ' ').upper()
            if text in DROP_FOOTER_LINKS:
                page = page[:m.start()] + page[span[2]:]
                removed += 1
                break
        else:
            break
    print('footer legal links removed:', removed)
    return page


def match_footer_glow(page):
    """The footer backdrop is a photo; the hero glow is a blurred token colour.

    Dropping the photo and reusing the hero's element makes the two match.
    """
    removed = 0
    for m in list(re.finditer(r'<img[^>]*YAiWqmJ1DFGxCJ93IHzGFZr2Yak[^>]*>', page)):
        wrapper = page.rfind('<div', 0, m.start())
        span = element_at(page, wrapper)
        if span and span[2] > m.end():
            page = page[:wrapper] + '<div class="footer-glow"></div>' + page[span[2]:]
            removed += 1
    print('footer backdrop replaced:', removed)
    return page


def rewrite_links(page):
    page, n = re.subn(
        r'href="([^"#][^"]*)"',
        lambda m: 'href="%s"' % HREFS.get(m.group(1), m.group(1)), page)
    print('hrefs rewritten:', n)
    page = page.replace('id="explore "', 'id="explore"')

    # the CV is not published, so nothing should link to it
    page, dropped = re.subn(r'href="/Akintoye_Ayomide_Nelson_CV\.pdf"',
                            'href="%s"' % MAILTO, page)
    if dropped:
        print('resume links repointed:', dropped)
    return page


def recolour(page):
    total = 0
    for pat, rep in ACCENT_SWAPS:
        page, n = re.subn(pat, rep, page, flags=re.I)
        total += n
    print('accent swaps in markup:', total)
    return page


def rename_labels(page):
    """data-framer-name is Framer's design-tool label; nothing reads it, but it
    still names the template's author in the page source."""
    def one(m):
        return 'data-framer-name="%s"' % (
            m.group(1)
            .replace('Bruno Simon', 'Akintoye Nelson')
            .replace('Bruno', 'Nelson')
            .replace('brunosimon@gmail.com', 'akintoyenelson@gmail.com')
            .replace('info@brunosimon.com', 'akintoyenelson@gmail.com'))

    page, n = re.subn(r'data-framer-name="([^"]*)"', one, page)
    print('framer-name labels scanned:', n)
    return page


def block_count(page):
    """Direct children of the page root, as a structural fingerprint."""
    root = page.find('<div class="framer-R2Reu')
    return len(list(children_of(page, root))) if root >= 0 else -1


def main():
    page = open(os.path.join(DS, 'page.html'), encoding='utf-8').read()

    page = strip_promo(page)
    expected_blocks = block_count(page)
    page = localise_images(page)
    page = strip_scroll_jack(page)
    page = swap_wordmark(page)
    page = rewrite_rolling_text(page)

    page, hits = retext(page, TEXT)
    for key, n in sorted(hits.items(), key=lambda kv: -kv[1]):
        print('  %3d  %s' % (n, key[:64]))

    page = works.rebuild(page)
    page = services.rebuild(page)
    page = wire_counters(page)
    page = trim_clients(page)
    page = trim_footer_links(page)
    page = match_footer_glow(page)
    page = tag_tickers(page)
    page = contact_icons(page)
    page = rewrite_links(page)
    page = recolour(page)
    page = rename_labels(page)
    page = strip_em_dashes(page)

    # A step that leaves unbalanced tags truncates the tree silently, so the
    # page's own shape is checked before anything is written.
    if block_count(page) != expected_blocks:
        raise SystemExit(
            'page structure changed: %d top-level blocks, expected %d'
            % (block_count(page), expected_blocks))

    out = os.path.join(DS, 'page.built.html')
    open(out, 'w').write(page)
    print('page.built.html', len(page))


if __name__ == '__main__':
    main()
