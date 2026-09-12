# -*- coding: utf-8 -*-
"""Turn the lifted Devsync page into Nelson's portfolio.

Content is swapped by matching an element's *plain text*, so the same rule hits
every breakpoint variant and works whether Framer left the text whole or split
it into one span per character.
"""
import re, os, sys, html as H
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tojsx import convert

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DS = os.path.join(REPO, '.lift', 'ds')
page = open(os.path.join(DS, 'page.html'), encoding='utf-8').read()

VOID = {'area','base','br','col','embed','hr','img','input','link','meta','param',
        'source','track','wbr','use','path','circle','rect','polygon','stop',
        'ellipse','line','polyline'}
TAG = re.compile(r'<(/?)([a-zA-Z][a-zA-Z0-9:-]*)((?:[^>"\']|"[^"]*"|\'[^\']*\')*?)(/?)>')

def element_at(s, start):
    """Return (inner_start, inner_end, end) for the element opening at `start`."""
    m = TAG.match(s, start)
    if not m:
        return None
    if m.group(2).lower() in VOID or m.group(4):
        return (m.end(), m.end(), m.end())
    i, depth = m.end(), 1
    while depth:
        t = TAG.search(s, i)
        if not t:
            return None
        name, closing, selfc = t.group(2).lower(), t.group(1), t.group(4)
        i = t.end()
        if name in VOID or selfc:
            continue
        depth += -1 if closing else 1
        if depth == 0:
            return (m.end(), t.start(), t.end())
    return None

def plain(s):
    s = re.sub(r'<!--.*?-->', '', s, flags=re.S)
    s = re.sub(r'<[^>]+>', '', s)
    return H.unescape(s).strip()

# --------------------------------------------------------------------------
# 0. strip the template's own "Get this template" promo overlay
# --------------------------------------------------------------------------
i = page.find('<div class="framer-4b2use-container">')
if i > 0:
    span = element_at(page, i)
    removed = span[2] - i
    page = page[:i] + page[span[2]:]
    print('stripped promo overlay:', removed, 'chars')

# --------------------------------------------------------------------------
# 1. images -> local copies
# --------------------------------------------------------------------------
page = re.sub(r'\s(?:srcset|srcSet)="[^"]*"', '', page)
page = re.sub(r'\ssizes="[^"]*"', '', page)
page = re.sub(r'src="https://framerusercontent\.com/images/([^"?]+)[^"]*"',
              lambda m: 'src="/ds/%s"' % m.group(1), page)

# the hero portrait
page = page.replace('/ds/e8w16q5wJI84smxcPUFYRRZmI.png', '/nelson.png')
page = re.sub(r'alt="(a boy were hoodie)?"(?=[^>]*/nelson\.png)', '', page)
page = page.replace('src="/nelson.png" alt', 'src="/nelson.png" alt="Akintoye Ayomide Nelson" data-alt')

# The About band's Image Group is the scroll-jacked image stack. It goes; the
# ticker beside it stays, and the portrait now lives in the hero.
i = page.find('data-framer-name="Image Group"')
if i > 0:
    a = page.rfind('<div', 0, i)
    span = element_at(page, a)
    print('removed scroll-jack image group:', span[2] - a, 'chars')
    page = page[:a] + page[span[2]:]

# the wordmark: swap Framer's logo image for live text we can style
LOGO = re.compile(
    r'<div aria-label="Brand logo" class="framer-1azl6kd">.*?</div></div>', re.S)
page, n = LOGO.subn(
    '<div aria-label="Brand logo" class="framer-1azl6kd brand-mark">'
    '<span class="brand-mark__text">Akintoye Nelson</span></div>', page)
print('logo marks replaced:', n)


# --------------------------------------------------------------------------
# 2a. rolling text (nav, buttons, social + footer links)
#
# Framer renders these as <p class="rolling-text-inner-…"> with one
# <span style="display:block…">C</span> per character, and fakes the second
# copy with a text-shadow. Rebuild the characters, keeping the span style.
# --------------------------------------------------------------------------
ROLLING = {
    # hero social row
    "Twitter (X)": "Email",
    "CodePen": "Resume",
    # footer, Portfolio column
    "CONTRA": "RESUME",
    "GITHUB": "PROJECTS",
    "CODEPEN": "EMAIL",
    # footer, Social column
    "INSTAGRAM": "GITHUB",
    "TWITTER \u201cX\u201d": "X.COM",
}

ROLL_P = re.compile(r'<p class="rolling-text-inner-[A-Za-z0-9]+">(.*?)</p>', re.S)
ROLL_SPAN = re.compile(r'<span style="([^"]*)">([^<]*)</span>', re.S)

def roll(m):
    inner = m.group(1)
    spans = ROLL_SPAN.findall(inner)
    if not spans:
        return m.group(0)
    text = H.unescape(''.join(c for _, c in spans)).replace('\u00a0', ' ')
    new = ROLLING.get(text.strip())
    if new is None:
        return m.group(0)
    roll.hits[text.strip()] = roll.hits.get(text.strip(), 0) + 1
    style = spans[0][0]
    # Framer separates words with NBSP so the roll keeps them on one line.
    body = ''.join('<span style="%s">%s</span>'
                   % (style, H.escape(c if c != ' ' else '\u00a0')) for c in new)
    return m.group(0)[:m.group(0).index('>') + 1] + body + '</p>'

roll.hits = {}
page = ROLL_P.sub(roll, page)
print('rolling text rewritten:', roll.hits)

# --------------------------------------------------------------------------
# 2. text content
# --------------------------------------------------------------------------
TEXT = {
    "Buy Template For $49": "",
    # hero
    "Bruno Simon": "Akintoye Nelson",
    "I craft fast, scalable, and user-friendly web applications with modern JavaScript frameworks — combining React on the frontend with robust server-side solutions using Node.js.":
        "I craft fast, scalable, and user-friendly web applications with modern JavaScript frameworks — combining React and Next.js on the frontend with robust server-side systems in Node.js, NestJS and PostgreSQL.",
    "info@brunosimon.com": "akintoyenelson@gmail.com",
    "+39 03 463 853 02": "+234 813 841 2167",
    "brunosimon@gmail.com": "akintoyenelson@gmail.com",
    "(684) 555-0102": "+234 813 841 2167",

    # socials
    "/ Twitter (X)": "/ GitHub",
    "/ LinkedIn": "/ LinkedIn",
    "/ GitHub": "/ GitHub",
    "/ CodePen": "/ Email",

    # about
    "I thrive on solving real-world problems, turning ideas into clean, maintainable code, and learning through experimentation.  You’ll find me building side projects, diving into new tech stacks, or simply exploring what’s next in the world of web development.":
        "I thrive on solving real-world problems, turning ideas into clean, maintainable code, and learning through experimentation. You’ll find me building side projects, diving into new tech stacks, or simply exploring what’s next in the world of web development.",

    # skills
    "HTML": "HTML", "CSS": "CSS", "JavaScript": "JavaScript", "React": "React",
    "Tailwind CSS": "Next.js",
    "Node.js": "Node.js", "Express.js": "NestJS", "MongoDB": "PostgreSQL",
    "PHP": "MongoDB", "Laravel": "Redis",
    "Git": "Git", "Github": "GitHub", "Stack Overflow": "Prisma",
    "AWS": "AWS", "Docker": "Docker",

    # stats
    "Clients Worldwide": "Teams Worldwide",

    # services
    "Build complete web applications from scratch — frontend to backend — optimized for speed, security, and scalability.":
        "Build complete web applications from scratch — frontend to backend — optimized for speed, security, and scalability.",

    # testimonial attributions that name the template author
    "Working with Bruno Simon was one of the best decisions we made for our web platform. He understood our vision, delivered clean & scalable code, and communicated clearly throughout the project.":
        "Working with Nelson was one of the best decisions we made for our web platform. He understood our vision, delivered clean & scalable code, and communicated clearly throughout the project.",
    "Bruno immediately understood our product goals and translated them into a beautifully optimized web experience. His technical expertise and collaborative spirit made a complex project feel effortless.":
        "Nelson immediately understood our product goals and translated them into a beautifully optimized web experience. His technical expertise and collaborative spirit made a complex project feel effortless.",
    "Working with Bruno was a game-changer for our e-commerce revamp. He not only delivered scalable, high-quality code but also brought clarity and structure to the entire process. Communication was seamless from start to finish.":
        "Working with Nelson was a game-changer for our e-commerce revamp. He not only delivered scalable, high-quality code but also brought clarity and structure to the entire process. Communication was seamless from start to finish.",

    # footer
    "Protfolio": "Portfolio",
    "CONTRA": "RESUME",
    "CODEPEN": "EMAIL",
    "INSTAGRAM": "GITHUB",
    "TWITER “X”": "LINKEDIN",
}

SPLIT_SPAN = re.compile(r'^<span style="[^"]*display:inline-block[^"]*">.</span>$')

def split_like(sample_style, text):
    """Rebuild split text using the same per-character span style Framer used."""
    out = []
    for word in text.split(' '):
        chars = ''.join('<span style="%s">%s</span>' % (sample_style, H.escape(c))
                        for c in word)
        out.append('<span style="white-space:nowrap">%s</span>' % chars)
    return ' '.join(out)

def retext(page, mapping):
    """Rewrite any element whose plain text matches a key."""
    hits = {k: 0 for k in mapping}
    out, i = [], 0
    while True:
        m = re.compile(r'<(h1|h2|h3|h4|p|span|a|div)\b').search(page, i)
        if not m:
            out.append(page[i:]); break
        span = element_at(page, m.start())
        if not span:
            out.append(page[i:m.end()]); i = m.end(); continue
        inner_s, inner_e, end = span
        inner = page[inner_s:inner_e]
        key = plain(inner)
        # Only rewrite a leaf text element. If the inner HTML still contains a
        # structural child, the real text node lives deeper and replacing here
        # would delete that child (it did: it ate the hero <h1>).
        nested = re.search(
            r'<(?:h[1-6]|p|div|ul|ol|li|a|section|nav|figure|blockquote)\b', inner)
        if key in mapping and mapping[key] != key and not nested:
            new = mapping[key]
            chars = re.findall(r'<span style="([^"]*display:inline-block[^"]*)">', inner)
            body = split_like(chars[0], new) if chars else H.escape(new)
            out.append(page[i:inner_s]); out.append(body)
            hits[key] += 1
            i = inner_e
            continue
        out.append(page[i:m.end()]); i = m.end()
    return ''.join(out), hits

page, hits = retext(page, TEXT)
for k, v in sorted(hits.items(), key=lambda kv: -kv[1]):
    print('  %3d  %s' % (v, k[:64]))


# --------------------------------------------------------------------------
# 2c. project cards
#
# Tags like "Vite" repeat across cards, so these are applied per card: find the
# card by the project link the template gave it, then rewrite inside that slice.
# --------------------------------------------------------------------------
PROJECTS = {
    'techzo': [
        ('Techzo', 'PlantRight AI'),
        ('Techzo is a cutting-edge design agency template built to showcase innovation, digital expertise, and a bold creative presence online',
         'A full-stack spatial AI platform for reforestation — site selection, design and monitoring, with ArcGIS/QGIS integration that cut manual work for forestry teams by 65–80%.'),
        ('HTML5  &  CSS', 'Next.js & React'), ('Framer Motion', 'NestJS'), ('Vite', 'PostgreSQL'),
    ],
    'lumin-studio': [
        ('Lumin Studio', 'Selar Clone'),
        ('LuminStudio blends elegance and clarity — a modern design agency template crafted to highlight creative work and impress potential clients',
         'A production-ready commerce platform for African digital creators — digital product sales, memberships, bundles and creator analytics, end to end.'),
        ('HTML5 & Tailwind CSS', 'TypeScript'), ('React', 'Express & NestJS'), ('Vite', 'Prisma'),
    ],
    'nubuilt': [
        ('Nubuilt', 'Unispend'),
        ('Crafted with clean, semantic code — Nubuilt is a sleek architecture template built for performance, responsiveness, and timeless design.',
         'A campus payments ecosystem: real-time student wallet top-ups, QR-code payments and transaction tracking, with dashboards for revenue-sharing models.'),
        ('HTML5', 'React'), ('CSS', 'NestJS'), ('GSAP', 'MongoDB'),
    ],
    'design-orbit': [
        ('Design orbit', 'ChopExpress'),
        ('Bold, creative, and conversion-focused — DesignOrbit is a sleek portfolio website template made for design agencies to showcase their work and attract clients.',
         'A multi-tenant food delivery platform handling high-concurrency rider, business and order workflows — transaction lookups cut by 50–60%.'),
        ('HTML5 & CSS', 'Node.js'), ('GSAP', 'PostgreSQL'), ('Vite', 'Prisma'),
    ],
    'formation-time': [
        ('Formation time', 'FastPay Webhooks'),
        ('Professional and polished — FormationTime is a clean consultant website template designed to build trust, highlight services, and convert leads.',
         'A real-time webhook system for payment notifications with delivery guarantees, reducing manual reconciliation by 40% across high-volume traffic.'),
        ('HTML5', 'Express'), ('Tailwind CSS', 'PostgreSQL'), ('Alpine.js', 'AWS'),
    ],
    'laundrybee': [
        ('LaundryBee', 'Pandar Pipelines'),
        ('Fresh, fast, and user-friendly — Laundrybee is a clean and modern website template built to promote laundry services and boost online bookings',
         'API integrations and data pipelines rebuilt around connection pooling and query optimisation, bringing average response times down by 60%.'),
        ('Tailwind CSS', 'TypeScript'), ('Alpine.js', 'NestJS'), ('Formspree', 'MongoDB'),
    ],
}

def per_card(page, href_pat, pairs_by_slug):
    total = 0
    for slug, pairs in pairs_by_slug.items():
        target = href_pat % slug
        i = 0
        while True:
            j = page.find('href="%s"' % target, i)
            if j < 0:
                break
            a = page.rfind('<a', 0, j)
            span = element_at(page, a)
            if not span:
                i = j + 1; continue
            card = page[a:span[2]]
            new, hits = retext(card, dict(pairs))
            total += sum(hits.values())
            page = page[:a] + new + page[span[2]:]
            i = a + len(new)
    print('project-card replacements:', total)
    return page

page = per_card(page, 'projects/%s.html', PROJECTS)

# --------------------------------------------------------------------------
# 2b. tickers
#
# Framer's Ticker/Slider components are animated by its runtime, which we are
# not shipping. The markup stays; each track gets a class, its items are
# duplicated, and CSS translates it by exactly half its width so the loop is
# seamless. The name band is the marquee the brief asked to keep.
# --------------------------------------------------------------------------
TICKER_SECTION = re.compile(r'<section style="display:flex[^"]*">')

def tag_tickers(page):
    out, i, n = [], 0, 0
    names = []
    while True:
        m = TICKER_SECTION.search(page, i)
        if not m:
            out.append(page[i:]); break
        span = element_at(page, m.start())
        block = page[m.start():span[2]]
        # which section is it in? the name band sits in "About us"
        j = page.rfind('<section class=', 0, m.start())
        ctx = re.search(r'data-framer-name="([^"]*)"', page[j:j + 300])
        kind = 'marquee' if (ctx and ctx.group(1).strip() == 'About us') else 'slider'
        names.append(kind)

        block = block.replace(m.group(0),
            m.group(0).replace('opacity:0;', '').replace('opacity:0.001;', ''), 1)
        # the <ul> is the track
        um = re.search(r'<ul style="([^"]*)"', block)
        if um:
            ul_span = element_at(block, um.start())
            items = block[ul_span[0]:ul_span[1]]
            style = (um.group(1)
                     .replace('width:100%;', 'width:max-content;')
                     .replace('transform:translateX(-0px)', 'transform:none'))
            new_ul = ('<ul class="ds-%s__track" style="%s">%s%s</ul>'
                      % (kind, style, items, items))
            block = block[:um.start()] + new_ul + block[ul_span[2]:]
        out.append(page[i:m.start()]); out.append(block)
        i = span[2]; n += 1
    print('tickers tagged:', n, names)
    return ''.join(out)

page = tag_tickers(page)

# --------------------------------------------------------------------------
# 2d. hero contact labels and social separators
# --------------------------------------------------------------------------
MAIL_ICON = ('<svg class="hero-icon" viewBox="0 0 24 24" fill="none" aria-hidden="true">'
             '<rect x="2.5" y="4.5" width="19" height="15" rx="2.5"/>'
             '<path d="m3 7 9 6 9-6"/></svg>')
PHONE_ICON = ('<svg class="hero-icon" viewBox="0 0 24 24" fill="none" aria-hidden="true">'
              '<path d="M6.5 3h3l1.5 4-2 1.5a12 12 0 0 0 6.5 6.5L17 13l4 1.5v3a2 2 0 0 1-2.2 2'
              'A17 17 0 0 1 3 5.2 2 2 0 0 1 5 3Z"/></svg>')

def label_icon(cls, icon):
    global page
    page, n = re.subn(
        r'(<div class="%s"[^>]*>)<p class="framer-text[^"]*"[^>]*>[^<]*</p>' % cls,
        lambda m: m.group(1) + icon, page)
    print('  %s -> icon x%d' % (cls, n))

label_icon('framer-15utcab', MAIL_ICON)   # E
label_icon('framer-1avki3e', PHONE_ICON)  # T

# "/ GitHub" — the separator's space is a plain space Framer collapses away
page, ns = re.subn(r'(>/<span class="framer-text"[^>]*>)\s*(</span>)',
                   r'\1&nbsp;\2', page)
print('  social separators spaced:', ns)

# --------------------------------------------------------------------------
# 3. links — the template is a multi-page site; this is one page
# --------------------------------------------------------------------------
GH = 'https://github.com/SmartWebCodder'
LI = 'https://www.linkedin.com/in/akintoye-ayomide-nelson/'
MAIL = 'mailto:akintoyenelson@gmail.com'
CV = '/Akintoye_Ayomide_Nelson_CV.pdf'

HREFS = {
    'index.html': '#top',
    'about.html': '#about-us',
    'projects.html': '#explore',
    'blog.html': '#blogs',
    'contact-us.html': MAIL,
    '404.html': '#top',
    'legal/privacy-policy.html': '#top',
    'legal/terms-conditions.html': '#top',

    'https://twitter.com/?lang=en': MAIL,
    'https://www.linkedin.com/': LI,
    'https://github.com/': GH,
    'https://codepen.io/': CV,
    'https://contra.com/': CV,
    'https://stackoverflow.com/': GH,
    'https://www.instagram.com/': GH,
    'https://read.cv/explore': CV,

    'mailto:brunosimon@gmail.com': MAIL,
    'mailto:info@brunosimon.com': MAIL,
    'tel:(684) 555-0102': 'tel:+2348138412167',
    'tel:+39 03 463 853 02': 'tel:+2348138412167',

    'projects/techzo.html': GH + '/plantright-ai',
    'projects/lumin-studio.html': GH + '/selar-clone',
    'projects/nubuilt.html': GH,
    'projects/design-orbit.html': GH,
    'projects/formation-time.html': GH,
    'projects/laundrybee.html': GH,

    'blog/frontend-vs-backend-which-path-should-you-choose.html': '#blogs',
    'blog/11-seo-for-developers-optimizing-websites-for-better-rankings.html': '#blogs',
    'blog/working-remotely-as-a-full-stack-developer-my-workflow-tools.html': '#blogs',
}
def fix_href(m):
    return 'href="%s"' % HREFS.get(m.group(1), m.group(1))
page, nh = re.subn(r'href="([^"#][^"]*)"', fix_href, page)
print('hrefs rewritten:', nh)

# the Works section id carries a stray trailing space in the template
page = page.replace('id="explore "', 'id="explore"')

# --------------------------------------------------------------------------
# 4. accent — the template's green becomes orange, in inline styles too
# --------------------------------------------------------------------------
acc = 0
for pat, rep in [
    (r'rgb\(\s*122\s*,\s*242\s*,\s*152\s*\)', 'var(--accent)'),
    (r'#7af298', 'var(--accent)'),
    (r'rgba\(\s*153\s*,\s*247\s*,\s*177\s*,\s*([0-9.]+)\s*\)', r'rgba(255, 138, 71, \1)'),
    (r'rgba\(\s*83\s*,\s*137\s*,\s*114\s*,\s*([0-9.]+)\s*\)', r'rgba(137, 83, 39, \1)'),
]:
    page, c = re.subn(pat, rep, page, flags=re.I)
    acc += c
print('accent swaps in markup:', acc)

# data-framer-name is the design-tool label Framer leaves behind. Nothing reads
# it, but it still names the template's author in the page source.
def rename_label(m):
    v = (m.group(1).replace('Bruno Simon', 'Akintoye Nelson')
                   .replace('Bruno', 'Nelson')
                   .replace('brunosimon@gmail.com', 'akintoyenelson@gmail.com')
                   .replace('info@brunosimon.com', 'akintoyenelson@gmail.com'))
    return 'data-framer-name="%s"' % v
page, nl = re.subn(r'data-framer-name="([^"]*)"', rename_label, page)
print('framer-name labels scanned:', nl)

open(os.path.join(DS, 'page.built.html'), 'w').write(page)
print('page.built.html', len(page))
