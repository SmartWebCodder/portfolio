# -*- coding: utf-8 -*-
"""Small HTML helpers shared by the lift scripts.

The template exports are well-formed enough to walk with a tag scanner, which
keeps the pipeline dependency-free.
"""
import re
import html as H

VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link',
        'meta', 'param', 'source', 'track', 'wbr', 'use', 'path', 'circle',
        'rect', 'polygon', 'stop', 'ellipse', 'line', 'polyline'}

TAG = re.compile(r'<(/?)([a-zA-Z][a-zA-Z0-9:-]*)((?:[^>"\']|"[^"]*"|\'[^\']*\')*?)(/?)>')

STRUCTURAL = re.compile(
    r'<(?:h[1-6]|p|div|ul|ol|li|a|section|nav|figure|blockquote)\b')

SPLIT_CHAR = re.compile(r'<span style="([^"]*display:inline-block[^"]*)">')


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


def children_of(s, start):
    """Yield (start, end) for each direct child element of the element at `start`."""
    m = TAG.match(s, start)
    i, depth, child = m.end(), 1, None
    while True:
        t = TAG.search(s, i)
        if not t:
            return
        name, closing, selfc = t.group(2).lower(), t.group(1), t.group(4)
        if name in VOID or selfc:
            if depth == 1:
                yield (t.start(), t.end())
            i = t.end()
            continue
        if closing:
            depth -= 1
            if depth == 0:
                return
            if depth == 1 and child is not None:
                yield (child, t.end())
                child = None
        else:
            if depth == 1 and child is None:
                child = t.start()
            depth += 1
        i = t.end()


def plain(s):
    """The visible text of a fragment.

    Framer inlines a <style> block next to some components; its rules are not
    text, so strip those elements whole rather than just their tags.
    """
    s = re.sub(r'<!--.*?-->', '', s, flags=re.S)
    s = re.sub(r'<(style|script)\b[^>]*>.*?</\1>', '', s, flags=re.S | re.I)
    return H.unescape(re.sub(r'<[^>]+>', '', s)).strip()


def split_like(style, text):
    """Rebuild split text using the per-character span style Framer used."""
    words = []
    for word in text.split(' '):
        chars = ''.join('<span style="%s">%s</span>' % (style, H.escape(c))
                        for c in word)
        words.append('<span style="white-space:nowrap">%s</span>' % chars)
    return ' '.join(words)


def retext(page, mapping):
    """Rewrite every leaf element whose visible text matches a key.

    Matching on text rather than position means one rule covers all of Framer's
    breakpoint variants, and works whether the text is whole or split into one
    span per character.
    """
    hits = {k: 0 for k in mapping}
    out, i = [], 0
    tag_start = re.compile(r'<(h1|h2|h3|h4|p|span|a|div)\b')
    while True:
        m = tag_start.search(page, i)
        if not m:
            out.append(page[i:])
            break
        span = element_at(page, m.start())
        if not span:
            out.append(page[i:m.end()])
            i = m.end()
            continue
        inner_s, inner_e, _ = span
        inner = page[inner_s:inner_e]
        key = plain(inner)
        # Only a leaf may be rewritten: a structural child means the real text
        # node lives deeper, and replacing here would delete that child.
        if key in mapping and mapping[key] != key and not STRUCTURAL.search(inner):
            chars = SPLIT_CHAR.findall(inner)
            body = (split_like(chars[0], mapping[key]) if chars
                    else H.escape(mapping[key]))
            out.append(page[i:inner_s])
            out.append(body)
            hits[key] += 1
            i = inner_e
            continue
        out.append(page[i:m.end()])
        i = m.end()
    return ''.join(out), hits


def strip_em_dashes(html):
    """Replace em dashes in text nodes only, leaving attributes and CSS alone."""
    def one(m):
        text = m.group(1)
        if '\u2014' not in text:
            return m.group(0)
        # " — " joins clauses and reads better as a comma; a bare em dash
        # between words is a hyphen.
        text = re.sub(r' \u2014 ', ', ', text)
        text = text.replace('\u2014', '-')
        return '>' + text + '<'

    return re.sub(r'>([^<]*)<', one, html)
