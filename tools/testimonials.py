# -*- coding: utf-8 -*-
"""Swap the template's testimonials for Nelson's clients.

The section renders each card once per breakpoint, and only one of those
variants is wrapped in a ticker list, so the cards are matched on their text
rather than located structurally: one rule then covers every variant.
"""
import json
import os
import re

from htmlutil import element_at, children_of, retext

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# the people the template ships, in the order its cards appear
TEMPLATE = [
    ('Daniel Carter', 'Product Designer, Stripe',
     'Working with Snilloc was seamless. His attention to detail and ability '
     'to translate design into smooth, functional interfaces really stood out.'),
    ('Michael Brown', 'UI/UX Designer, Adobe',
     'He has a strong eye for design and knows how to bring ideas to life on '
     'the web. Collaboration with him is always easy and productive.'),
    ('Emily Watson', 'Frontend Developer, Shopify',
     'Snilloc writes some of the cleanest code I’ve seen. He’s '
     'thoughtful, consistent, and always focused on performance and user '
     'experience.'),
    ('Sarah Johnson', 'Software Engineer, Microsoft',
     'Snilloc is reliable and detail-oriented. He takes feedback well and '
     'continuously improves both the product and his workflow.'),
    ('James Wilson', 'Product Manager, Atlassian',
     'He understands product thinking, not just code. That makes a big '
     'difference when building features that actually matter to users.'),
    ('Olivia Martinez', 'Creative Developer, Webflow',
     'His work is clean, modern, and polished. He consistently delivers '
     'interfaces that feel intuitive and well-crafted.'),
]

AVATARS = ['0t1mAkMD8DjLQwkEPKvWPvRdw', 'BIKrk2jNPbjgqk1KIiOt21i28c',
           'Ir7RsDIGqdl9NXRsjqxfC8LSeI', 'fSilKlVeMn7BTOvTYqgkAXZeq8',
           'plfPyU9U9DxoD47TDqzj1bNU0', 'wud5asxR22rV2WSRb526VDJgk']


def load_people():
    with open(os.path.join(REPO, 'content', 'testimonials.json')) as f:
        return json.load(f)


def _card_groups(html):
    """Every element whose direct children are testimonial cards.

    The section renders the row once per breakpoint and only one of those is
    wrapped in a ticker list, so the groups are found by structure instead.
    """
    groups, seen = [], set()
    for m in re.finditer(r'data-framer-name="testimonial card"', html):
        node = m.start()
        while True:
            node = html.rfind('<div', 0, node)
            if node < 0:
                break
            span = element_at(html, node)
            if not span or span[2] < m.start():
                continue
            if html[span[0]:span[1]].count('data-framer-name="testimonial card"') > 1:
                if node not in seen:
                    seen.add(node)
                    groups.append(node)
                break
    return groups


def rebuild(html):
    people = load_people()
    mapping = {}
    for (name, role, quote), person in zip(TEMPLATE, people):
        mapping[name] = person['name']
        mapping[role] = person['role']
        mapping[quote] = person['quote']

    html, hits = retext(html, mapping)
    missed = [k for k, v in hits.items() if not v]
    if missed:
        print('  !! testimonial text not found:', missed[0][:60])

    # each card keeps its slot's avatar; the template's stock portraits are
    # replaced with lettermarks, since these people did not pose for them
    for i, asset in enumerate(AVATARS, start=1):
        if i > len(people):
            break
        html = re.sub(
            r'src="https://framerusercontent\.com/images/%s[^"]*"' % re.escape(asset),
            'src="/avatars/a%d.png"' % i, html)
    html = re.sub(r'\salt="[^"]*"', '', html)

    print('  testimonials: %d fields swapped'
          % sum(1 for v in hits.values() if v))
    return html
