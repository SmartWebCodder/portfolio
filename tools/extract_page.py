# -*- coding: utf-8 -*-
"""Lift the whole Devsync page body + its stylesheet + its SVG sprite."""
import re, os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC=os.environ.get('DEVSYNC_HTML', os.path.join(REPO, '.lift', 'src', 'devsync.html'))
OUT=os.path.join(REPO, '.lift', 'ds')
os.makedirs(OUT, exist_ok=True)
s=open(SRC,encoding='utf-8',errors='ignore').read()

VOID={'area','base','br','col','embed','hr','img','input','link','meta','param',
      'source','track','wbr','use','path','circle','rect','polygon','stop','ellipse',
      'line','polyline'}
TAG=re.compile(r'<(/?)([a-zA-Z][a-zA-Z0-9:-]*)((?:[^>"\']|"[^"]*"|\'[^\']*\')*?)(/?)>')

def extract_at(html, start):
    i, depth = start, 0
    while True:
        t=TAG.search(html,i)
        if not t: return None
        closing,name,selfc=t.group(1),t.group(2).lower(),t.group(4)
        i=t.end()
        if name in VOID or selfc=='/': continue
        if closing:
            depth-=1
            if depth==0: return html[start:t.end()]
        else: depth+=1

# 1. the page root that holds nav + every section + footer
i=s.find('<div class="framer-R2Reu')
page=extract_at(s,i)
open(os.path.join(OUT,'page.html'),'w').write(page)
print('page.html', len(page))

# 2. the SVG sprite Framer ships inline for this page
i=s.find('<div id="svg-templates"')
sprite=extract_at(s,i) if i>=0 else ''
open(os.path.join(OUT,'sprite.html'),'w').write(sprite or '')
print('sprite.html', len(sprite or ''))

# 3. every stylesheet block
styles=re.findall(r'<style[^>]*>(.*?)</style>', s, flags=re.S)
open(os.path.join(OUT,'all.css'),'w').write('\n'.join(styles))
print('all.css', sum(len(x) for x in styles))
