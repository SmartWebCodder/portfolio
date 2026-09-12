import re, os, json

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC=os.environ.get('FASTFOLIO_HTML', os.path.join(REPO, '.lift', 'src', 'fastfolio.html'))
OUT=os.path.join(REPO, '.lift', 'ff')
s=open(SRC,encoding='utf-8',errors='ignore').read()

# collect all style block contents
styles=re.findall(r'<style[^>]*>(.*?)</style>', s, flags=re.S)
allcss='\n'.join(styles)
open(os.path.join(OUT,'all.css'),'w').write(allcss)
print('total css bytes', len(allcss), 'blocks', len(styles))

# classes used in our sections
used=set()
presets=set()
for name in ['skills','experience','testimonials']:
    h=open(os.path.join(OUT,name+'.html')).read()
    for c in re.findall(r'class="([^"]*)"', h):
        for x in c.split(): used.add(x)
    for p in re.findall(r'data-styles-preset="([^"]*)"', h): presets.add(p)
print('classes', len(used), 'presets', len(presets))
json.dump(sorted(used), open(os.path.join(OUT,'classes.json'),'w'), indent=0)
json.dump(sorted(presets), open(os.path.join(OUT,'presets.json'),'w'), indent=0)
print(sorted(presets))
