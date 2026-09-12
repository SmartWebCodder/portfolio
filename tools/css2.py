import re, os, json

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT=os.path.join(REPO, '.lift', 'ff')
css=open(os.path.join(OUT,'all.css')).read()
used=set(json.load(open(os.path.join(OUT,'classes.json'))))
presets=set(json.load(open(os.path.join(OUT,'presets.json'))))

# tokenize top-level blocks
def split_blocks(text):
    out=[]; depth=0; buf=''; i=0
    while i < len(text):
        ch=text[i]
        buf+=ch
        if ch=='{': depth+=1
        elif ch=='}':
            depth-=1
            if depth==0:
                out.append(buf.strip()); buf=''
        i+=1
    if buf.strip(): out.append(buf.strip())
    return out

blocks=split_blocks(css)
print('top blocks', len(blocks))

def sel_of(b):
    return b[:b.index('{')].strip() if '{' in b else b

kept=[]
keyframes=set()
for b in blocks:
    sel=sel_of(b)
    low=sel.lower()
    if low.startswith('@font-face') or low.startswith('@import'):
        kept.append(b); continue
    if low.startswith('@keyframes') or low.startswith('@-webkit-keyframes'):
        continue  # handled later
    if low.startswith('@media') or low.startswith('@supports'):
        # recurse into inner
        inner=b[b.index('{')+1:b.rindex('}')]
        sub=split_blocks(inner)
        keep_sub=[]
        for sb in sub:
            ss=sel_of(sb)
            if any(('.'+c) in ss for c in used) or any(('.'+p) in ss for p in presets) or ':root' in ss or 'body' == ss.strip():
                keep_sub.append(sb)
        if keep_sub:
            kept.append(sel+'{\n'+'\n'.join(keep_sub)+'\n}')
        continue
    if any(('.'+c) in sel for c in used) or any(('.'+p) in sel for p in presets):
        kept.append(b)
        continue
    if ':root' in sel or sel.strip() in ('body','html','*','html, body'):
        kept.append(b); continue

out='\n'.join(kept)
# find animation names referenced
for n in re.findall(r'animation(?:-name)?\s*:\s*([^;}]+)', out):
    for tok in re.split(r'[ ,]+', n.strip()):
        if re.match(r'^[a-zA-Z_-][\w-]*$', tok) and tok not in ('none','infinite','linear','ease','ease-in','ease-out','ease-in-out','normal','forwards','backwards','both','alternate','reverse','running','paused','alternate-reverse'):
            keyframes.add(tok)
kf=[]
for b in blocks:
    sel=sel_of(b)
    m=re.match(r'@(?:-webkit-)?keyframes\s+([\w-]+)', sel)
    if m and m.group(1) in keyframes:
        kf.append(b)
out=out+'\n'+'\n'.join(kf)
open(os.path.join(OUT,'sections.css'),'w').write(out)
print('kept bytes', len(out), 'rules', len(kept), 'keyframes', len(kf), keyframes)
