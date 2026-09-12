# -*- coding: utf-8 -*-
"""Lift the three Fastfolio sections, swap the template's copy for Nelson's."""
import re, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import skills
import testimonials
from htmlutil import element_at, strip_em_dashes
from tojsx import convert

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FF = os.path.join(REPO, '.lift', 'ff')
OUT = os.path.join(REPO, 'components', 'lifted')
os.makedirs(OUT, exist_ok=True)

def read(n):
    return open(os.path.join(FF, n + '.html'), encoding='utf-8').read()

def sub(html, pairs):
    """Ordered, whole-string replacements applied to every breakpoint variant."""
    for old, new in pairs:
        if old not in html:
            print('  !! not found:', old[:70])
        html = html.replace(old, new)
    return html

# --------------------------------------------------------------------------
# Skills / "Tools I Build With"
# --------------------------------------------------------------------------
TECH = [
    ('QUMZjLBEaefCugbhkaTAFcprOWQ.svg', 'html logo',       'HTML5',       '/tech/html.svg'),
    ('CPCoZIHh5IhKplr3oPeQOTLRy4A.svg', 'css logo',        'CSS3',        '/tech/css.svg'),
    ('U4WwaSswiaWDacNalJbEKDXNj7w.png', 'Javascript logo', 'JavaScript',  '/tech/javascript.png'),
    ('1XkLbWWmnowcE9PvrezLNvsFZw.png',  'react logo',      'React',       '/tech/react.png'),
    ('fS4jIkPM7ZdAr12rAtjx7LIbPjg.webp','nextjs logo',     'Next.js',     '/tech/nextjs.webp'),
    ('dMTyUNYFKn4FNDoOM2XVPeWLI.png',   'redux logo',      'TypeScript',  '/tech/typescript.png'),
    ('ntr6KUGqNxMQW1AP6w7IPChNIM.png',  'tailwindcss logo','TailwindCSS', '/tech/tailwindcss.png'),
    ('v4EhMXccLQv14F1b1SCORd1fGck.webp','sass logo',       'Node.js',     '/tech/nodejs.svg'),
    ('JcVzC5vItQ6wJkBzEGg0u5viZyw.png', 'GSAP logo',       'NestJS',      '/tech/nestjs.svg'),
    ('wfmZJb4V5pKZfdVVDZx1fggVXU.png',  'typescript logo', 'PostgreSQL',  '/tech/postgresql.svg'),
    ('7ke3hIoqfWHE2POE0JDsQleVfbI.svg', 'netlify logo',    'Docker',      '/tech/docker.svg'),
    ('RMsp0LaPuNuXwPhZgGHJWTPZWLY.svg', 'git logo',        'Git',         '/tech/git.svg'),
]
# the labels the template ships with, in the same slot order
OLD_LABELS = ['HTML5','CSS3','JavaScript','React','Nextjs','Redux','TailwindCSS',
              'Sass','GSAP','TypeScript','Netlify','Git']

def build_skills():
    h = read('skills')
    # Framer emits srcset + src with sizing query params; rewrite the whole attr.
    for asset, alt, label, local in TECH:
        h = re.sub(r'srcSet="[^"]*%s[^"]*"' % re.escape(asset), '', h)
        h = re.sub(r'srcset="[^"]*%s[^"]*"' % re.escape(asset), '', h)
        h = re.sub(r'src="https://framerusercontent\.com/images/%s[^"]*"' % re.escape(asset),
                   'src="%s"' % local, h)
        h = h.replace('alt="%s"' % alt, 'alt="%s"' % label)
    # labels sit in <p ...>LABEL</p>; replace longest-first so "Git" doesn't hit "GitHub"
    order = sorted(range(len(OLD_LABELS)), key=lambda i: -len(OLD_LABELS[i]))
    for i in order:
        old, new = OLD_LABELS[i], TECH[i][2]
        h = re.sub(r'(>)%s(</p>)' % re.escape(old), r'\g<1>%s\g<2>' % new, h)
    h = h.replace(
        'A curated set of technologies I rely on to build modern web experiences',
        'The stack I reach for across the whole product: interface, API and data layer')
    return skills.rebuild(h)

# --------------------------------------------------------------------------
# Experience / "Where I've Worked"
# --------------------------------------------------------------------------
SUBTITLE = ('Seven years of shipping production systems, and the interfaces '
            'on top of them')

JOBS = [
    ('Frontend Engineer — Paystack', 'Senior Software Engineer, Pandar Resources',
     '2023 — Present', '2026 - Present',
     ['Built and maintained responsive user interfaces using modern JavaScript frameworks',
      'Collaborated with designers to deliver clean, user-focused experiences',
      'Optimized performance and improved page load times across key products'],
     ['Built the dashboards and the APIs behind them in TypeScript, React and NestJS',
      'Cut average response times by 60% through connection pooling and query optimisation',
      'Added structured logging and metrics, speeding up debugging of high-throughput services']),
    ('Frontend Engineer — Hubtel', 'Full Stack Engineer, ODJTech Multimedia',
     '2022 — 2023', '2025 - 2026',
     ['Built responsive customer-facing interfaces for web products',
      'Worked closely with product and design teams to improve usability',
      'Optimized UI performance and reusable component structure'],
     ['Shipped customer-facing interfaces in React alongside the event-driven services behind them',
      'Implemented Redis caching that held response times steady under concurrent load',
      'Drove reliability work: failure-mode handling and autoscaling for production stability']),
    ('UI Engineer — Meta', 'Product Engineer, Unispend',
     '2021 — 2022', '2025 - 2026',
     ['Developed polished interface components for internal tools and product experiences',
      'Improved design consistency across multiple user flows',
      'Collaborated with cross-functional teams to ship high-quality features'],
     ['Built the student wallet UI, QR-code payment flow and transaction history end to end',
      'Designed the analytics dashboards revenue-sharing partners use day to day',
      'Wired JWT auth and rate limiting across the campus payments ecosystem']),
    ('Frontend Lead — Google', 'Full Stack Engineer, FastPay Tech',
     '2020 — 2021', '2023 - 2024',
     ['Crafted scalable web interfaces with a focus on speed and accessibility',
      'Contributed to clean component systems and maintainable codebases',
      'Helped refine user experiences through testing and iteration'],
     ['Built payment interfaces and the APIs behind them, owning both ends of the flow',
      'Designed a real-time webhook system with delivery guarantees for payment notifications',
      'Reduced manual reconciliation by 40% across high-volume transaction traffic']),
]

def build_experience():
    h = read('experience')
    pairs = []
    for old_t, new_t, old_d, new_d, old_bs, new_bs in JOBS:
        pairs.append((old_t, new_t))
        pairs += list(zip(old_bs, new_bs))
    # dates repeat across cards, so replace them together with their card title
    h = sub(h, pairs)
    for old_t, new_t, old_d, new_d, _, _ in JOBS:
        # the date follows its (already renamed) title within the same card
        h = re.sub(r'(%s.{0,4000}?)>%s<' % (re.escape(new_t), re.escape(old_d)),
                   lambda m: m.group(1) + '>' + new_d + '<', h, count=6, flags=re.S)
    h = h.replace('Download My CV', 'Contact Me')
    for variant in ("A summary of my professional journey and the impact I've made",
                    'A summary of my professional journey and the impact I&#x27;ve made',
                    'A summary of my professional journey and the impact I\u2019ve made'):
        h = h.replace(variant, SUBTITLE)
    return h

# --------------------------------------------------------------------------
# Testimonials / "Don't just take my words for it"
# --------------------------------------------------------------------------
def build_testimonials():
    h = read('testimonials')
    h = re.sub(r'\s(?:srcset|srcSet)="[^"]*"', '', h)
    h = testimonials.rebuild(h)
    return tag_tickers(h)

def tag_tickers(html):
    """Drive the testimonial rows from CSS.

    Framer's Ticker is animated by its runtime. The markup stays; each track
    gets a class and a duplicated run so CSS can translate it by exactly half
    its width, and the row the template marks "reverse" runs the other way.
    """
    reverse = set(re.findall(
        r'class="(framer-[a-z0-9]+)"(?=(?:(?!class=)[\s\S]){0,600}?'
        r'tickereffectdirectionmodifier="reverse")', html))

    out, i, n = [], 0, 0
    for m in re.finditer(r'<ul role="group" style="([^"]*)">', html):
        span = element_at(html, m.start())
        items = html[span[0]:span[1]]
        owner = re.findall(r'class="(framer-[a-z0-9]+)"', html[:m.start()])
        direction = 'reverse' if owner and owner[-1] in reverse else 'forward'
        style = (m.group(1)
                 .replace('opacity:0;', '')
                 .replace('width:100%;', 'width:max-content;')
                 .replace('transform:translateX(-20px)', 'transform:none'))
        out.append(html[i:m.start()])
        # A single duplicated run is narrower than a wide viewport, so the
        # loop point shows as a gap. Four runs keep the half-track wider than
        # the screen at every breakpoint.
        out.append('<ul role="group" class="ff-ticker__track ff-ticker__track--%s" '
                   'style="%s">%s</ul>' % (direction, style, items * 4))
        i = span[2]
        n += 1
    out.append(html[i:])
    print('  testimonial tickers tagged:', n)
    return ''.join(out)


BUILDERS = {
    'SkillsSection': ('skills', build_skills),
    'ExperienceSection': ('experience', build_experience),
    'TestimonialsSection': ('testimonials', build_testimonials),
}

for comp, (name, fn) in BUILDERS.items():
    print('==', comp)
    html = fn()
    html = strip_em_dashes(html)
    jsx = convert(html)
    open(os.path.join(FF, name + '.built.html'), 'w').write(html)
    open(os.path.join(FF, name + '.built.jsx'), 'w').write(jsx)
    print('  ->', len(jsx), 'chars jsx')
