import re, sys, os, json

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC=os.environ.get('FASTFOLIO_HTML', os.path.join(REPO, '.lift', 'src', 'fastfolio.html'))
OUT=os.path.join(REPO, '.lift', 'ff')
os.makedirs(OUT, exist_ok=True)
s=open(SRC,encoding='utf-8',errors='ignore').read()

VOID={'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr','use','path','circle','rect','polygon','stop'}

def extract_section(html, idname):
    m=re.search(r'<section[^>]*id="%s"'%idname, html)
    if not m: return None
    start=html.rfind('<section', 0, m.end())
    # walk
    i=start; depth=0
    tagre=re.compile(r'<(/?)([a-zA-Z][a-zA-Z0-9-]*)([^>]*?)(/?)>')
    while True:
        t=tagre.search(html, i)
        if not t: break
        closing, name, attrs, selfc = t.group(1), t.group(2).lower(), t.group(3), t.group(4)
        i=t.end()
        if name in VOID or selfc=='/': continue
        if closing: 
            depth-=1
            if depth==0: return html[start:t.end()]
        else: depth+=1
    return None

secs={}
for name in ['skills','experience','testimonials']:
    h=extract_section(s,name)
    secs[name]=h
    open(os.path.join(OUT,name+'.html'),'w').write(h or '')
    print(name, len(h or ''))
