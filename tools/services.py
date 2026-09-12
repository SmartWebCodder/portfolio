# -*- coding: utf-8 -*-
"""Rebuild the services list from content/services.json.

Framer only renders the body of whichever item is open, so the closed ones
ship empty and cannot be expanded. Every item is cloned from the open one
instead, and the collapse is handled by styles/overrides.css.
"""
import json
import os
import re

from htmlutil import element_at, retext, plain

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ITEM = re.compile(r'class="framer-DsE1D[^"]*"')
OPEN_VARIANT = 'framer-v-ig0c81'
CLOSED_VARIANT = 'framer-v-1xjxd8z'


def load_services():
    with open(os.path.join(REPO, 'content', 'services.json')) as f:
        return json.load(f)


def rebuild(page):
    """Replace each run of service items with one clone per service."""
    services = load_services()
    rebuilt = 0
    cursor = 0

    while True:
        m = ITEM.search(page, cursor)
        if not m:
            break
        if OPEN_VARIANT not in page[m.start():m.start() + 200]:
            cursor = m.end()
            continue

        start = page.rfind('<div', 0, m.start() + 1)
        span = element_at(page, start)
        template = page[start:span[2]]

        # the run of sibling items this open one belongs to
        end = span[2]
        while True:
            nxt = ITEM.search(page, end)
            if not nxt or nxt.start() - end > 400:
                break
            a = page.rfind('<div', 0, nxt.start() + 1)
            s2 = element_at(page, a)
            if not s2:
                break
            end = s2[2]

        old_title = plain(re.search(r'<h3[^>]*>(.*?)</h3>', template, re.S).group(1))
        paragraphs = [plain(p.group(1)) for p in
                      re.finditer(r'<p[^>]*>(.*?)</p>', template, re.S)]
        old_number = paragraphs[0]
        old_body = max(paragraphs, key=len)

        out = []
        for n, svc in enumerate(services):
            item, _ = retext(template, {
                old_title: svc['title'],
                old_number: svc['number'],
                old_body: svc['body'],
            })
            if n:
                item = item.replace(OPEN_VARIANT, CLOSED_VARIANT, 1)
            out.append(item)

        block = ''.join(out)
        page = page[:start] + block + page[end:]
        cursor = start + len(block)
        rebuilt += 1

    print('service lists rebuilt:', rebuilt, 'with', len(services), 'items')
    return page
