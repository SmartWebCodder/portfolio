# -*- coding: utf-8 -*-
"""Convert lifted Framer HTML into JSX that renders without the Framer runtime."""
import re, json, sys

# SVG elements React spells in camelCase (HTML parsing lowercases them).
SVG_TAGS = {
    'lineargradient':'linearGradient','radialgradient':'radialGradient',
    'clippath':'clipPath','feblend':'feBlend','fecolormatrix':'feColorMatrix',
    'fecomponenttransfer':'feComponentTransfer','fecomposite':'feComposite',
    'feconvolvematrix':'feConvolveMatrix','fediffuselighting':'feDiffuseLighting',
    'fedisplacementmap':'feDisplacementMap','fedistantlight':'feDistantLight',
    'fedropshadow':'feDropShadow','feflood':'feFlood','fefunca':'feFuncA',
    'fefuncb':'feFuncB','fefuncg':'feFuncG','fefuncr':'feFuncR',
    'fegaussianblur':'feGaussianBlur','feimage':'feImage','femerge':'feMerge',
    'femergenode':'feMergeNode','femorphology':'feMorphology','feoffset':'feOffset',
    'fepointlight':'fePointLight','fespecularlighting':'feSpecularLighting',
    'fespotlight':'feSpotLight','fetile':'feTile','feturbulence':'feTurbulence',
    'foreignobject':'foreignObject','textpath':'textPath',
}

VOID = {'area','base','br','col','embed','hr','img','input','link','meta','param',
        'source','track','wbr'}
SVG_SELF = {'use','path','circle','rect','polygon','stop','ellipse','line','polyline'}

# HTML attribute -> JSX prop
ATTR_MAP = {
    'class':'className','for':'htmlFor','tabindex':'tabIndex','colspan':'colSpan',
    'rowspan':'rowSpan','maxlength':'maxLength','readonly':'readOnly',
    'autoplay':'autoPlay','autofocus':'autoFocus','srcset':'srcSet',
    'crossorigin':'crossOrigin','playsinline':'playsInline','novalidate':'noValidate',
    'enctype':'encType','usemap':'useMap','contenteditable':'contentEditable',
    'spellcheck':'spellCheck','viewbox':'viewBox','stroke-width':'strokeWidth',
    'stroke-linecap':'strokeLinecap','stroke-linejoin':'strokeLinejoin',
    'stroke-dasharray':'strokeDasharray','stroke-dashoffset':'strokeDashoffset',
    'fill-rule':'fillRule','clip-rule':'clipRule','clip-path':'clipPath',
    'stop-color':'stopColor','stop-opacity':'stopOpacity','text-anchor':'textAnchor',
    'font-family':'fontFamily','font-size':'fontSize','font-weight':'fontWeight',
    'letter-spacing':'letterSpacing','vector-effect':'vectorEffect',
    'shape-rendering':'shapeRendering','preserveaspectratio':'preserveAspectRatio',
    'gradientunits':'gradientUnits','gradienttransform':'gradientTransform',
    'patternunits':'patternUnits','maskunits':'maskUnits','xlink:href':'xlinkHref',
    'srclang':'srcLang','frameborder':'frameBorder','allowfullscreen':'allowFullScreen',
    'marker-end':'markerEnd','marker-start':'markerStart','paint-order':'paintOrder',
    'dominant-baseline':'dominantBaseline','mask-type':'maskType',
}
# React types these as numbers, so they must be emitted as {n} not "n".
NUM_ATTRS = {'tabIndex', 'rowSpan', 'colSpan', 'span', 'start', 'size',
             'rows', 'cols', 'maxLength', 'minLength', 'step',
             'aria-posinset', 'aria-setsize', 'aria-level', 'aria-valuemin',
             'aria-valuemax', 'aria-valuenow', 'aria-colcount', 'aria-colindex',
             'aria-colspan', 'aria-rowcount', 'aria-rowindex', 'aria-rowspan'}
BOOL_ATTRS = {'hidden','disabled','checked','readonly','autoplay','muted','loop',
              'controls','selected','required','allowfullscreen','playsinline',
              'autofocus','novalidate','defer','async','open','inert'}

def css_prop_to_js(p):
    p = p.strip()
    if p.startswith('--'):
        return p          # custom property -> keep, must be quoted key
    # React spells vendor prefixes WebkitFoo / MozFoo / msFoo (-ms- is the odd
    # one out and stays lowercase).
    prefixed = None
    for pre, js in (('-webkit-', 'Webkit'), ('-moz-', 'Moz'), ('-o-', 'O'),
                    ('-ms-', 'ms')):
        if p.startswith(pre):
            prefixed, p = js, p[len(pre):]
            break
    parts = p.lstrip('-').split('-')
    name = parts[0] + ''.join(w[:1].upper() + w[1:] for w in parts[1:])
    if prefixed:
        return prefixed + name[:1].upper() + name[1:]
    return name

def split_decls(style):
    """Split a CSS declaration list on top-level semicolons (respecting parens/quotes)."""
    out, buf, depth, quote = [], '', 0, None
    for ch in style:
        if quote:
            buf += ch
            if ch == quote:
                quote = None
            continue
        if ch in '"\'':
            quote = ch; buf += ch; continue
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
        if ch == ';' and depth == 0:
            out.append(buf); buf = ''
        else:
            buf += ch
    if buf.strip():
        out.append(buf)
    return out

def split_decl(d):
    """Split one declaration into (prop, value) at the first top-level colon."""
    depth, quote = 0, None
    for i, ch in enumerate(d):
        if quote:
            if ch == quote: quote = None
            continue
        if ch in '"\'':
            quote = ch; continue
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
        elif ch == ':' and depth == 0:
            return d[:i], d[i+1:]
    return None, None

def style_to_obj(style, strip_hidden=True):
    """Convert an inline style to a JSX style object.

    Framer's runtime animates elements in from a hidden state. Without it those
    inline values would stick, so a hidden element is reported back to the
    caller and its entrance offset dropped.

    An element counts as hidden only when it is actually invisible: opacity at
    zero, or a blur filter. A bare transform is layout (translateY(-50%) to
    centre a number, translate(-50%) to centre a portrait) and must be kept.
    """
    decls = []
    for d in split_decls(style):
        if not d.strip():
            continue
        prop, val = split_decl(d)
        if prop is None:
            continue
        prop, val = prop.strip().lower(), val.strip()
        val = re.sub(r'/\*.*?\*/', '', val, flags=re.S).strip()
        if val:
            decls.append((prop, val))

    hidden = False
    if strip_hidden:
        for prop, val in decls:
            if prop == 'opacity':
                try:
                    if float(val) < 0.05:
                        hidden = True
                except ValueError:
                    pass
            elif prop == 'filter' and 'blur' in val:
                hidden = True
            elif prop == 'visibility' and val == 'hidden':
                hidden = True

    obj = {}
    for prop, val in decls:
        if strip_hidden:
            if prop == 'will-change':
                continue
            if hidden and prop in ('opacity', 'transform', 'filter', 'visibility'):
                continue
        obj[css_prop_to_js(prop)] = val
    return obj, hidden


def obj_to_jsx(obj):
    parts = []
    for k, v in obj.items():
        key = '"%s"' % k if (k.startswith('--') or not re.match(r'^[A-Za-z_$][\w$]*$', k)) else k
        parts.append('%s: %s' % (key, json.dumps(v)))
    return '{' + ', '.join(parts) + '}'

# Attributes React will pass through to the DOM. Anything else Framer emits is
# a prop for its own runtime (tickereffectvelocity, parentsize, …); those are
# re-prefixed as data-* so they stay readable without tripping React's types.
SAFE_ATTRS = {
    'id','class','style','title','role','dir','lang','slot','translate','hidden',
    'href','src','alt','target','rel','download','type','value','name','media',
    'width','height','loading','decoding','sizes','srcset','poster','preload',
    'viewbox','fill','stroke','d','x','y','x1','y1','x2','y2','cx','cy','r','rx','ry',
    'points','opacity','transform','offset','mask','filter','clip-path','overflow',
    'gradientunits','gradienttransform','patternunits','maskunits','result','in',
    'stddeviation','operator','k1','k2','k3','k4','xlink:href','preserveaspectratio',
    'stop-color','stop-opacity','fill-rule','clip-rule','fill-opacity','stroke-opacity',
    'stroke-width','stroke-linecap','stroke-linejoin','stroke-dasharray','stroke-dashoffset',
    'vector-effect','shape-rendering','text-anchor','dominant-baseline','paint-order',
    'font-family','font-size','font-weight','letter-spacing','marker-end','marker-start',
    'mask-type','for','tabindex','colspan','rowspan','span','start','size','rows','cols',
    'maxlength','minlength','step','placeholder','disabled','checked','selected',
    'required','readonly','multiple','autoplay','muted','loop','controls','playsinline',
    'crossorigin','referrerpolicy','autocomplete','autofocus','novalidate','enctype',
    'method','action','usemap','contenteditable','spellcheck','draggable','inert',
    'itemprop','itemscope','itemtype','datetime','cite','open','reversed','wrap',
    'frameborder','allowfullscreen','allow','sandbox','srcdoc','srclang','kind','default',
}

ATTR_RE = re.compile(
    r'''([:a-zA-Z_][-:.\w]*)\s*(?:=\s*(?:"([^"]*)"|'([^']*)'|([^\s"'=<>`]+)))?''')

def convert_attrs(raw, tag):
    """Return (jsx_attr_string, was_hidden)."""
    out, hidden = [], False
    for m in ATTR_RE.finditer(raw):
        name = m.group(1)
        val = m.group(2)
        if val is None: val = m.group(3)
        if val is None: val = m.group(4)
        low = name.lower()
        if low in ('xmlns', 'xmlns:xlink'):
            continue
        if low.startswith('data-framer-appear-id'):
            continue
        if val is None:
            if low in BOOL_ATTRS:
                out.append('%s={true}' % ATTR_MAP.get(low, low))
            elif low in SAFE_ATTRS or low.startswith(('data-', 'aria-')):
                out.append('%s=""' % ATTR_MAP.get(low, low))
            else:
                # a bare Framer prop (shadows, …) — keep it, but as data-*
                out.append('data-%s=""' % low.replace(':', '-'))
            continue
        import html as _h
        val = _h.unescape(val)
        if low == 'style':
            obj, hid = style_to_obj(val)
            hidden = hidden or hid
            if obj:
                # Custom properties and newer CSS features (corner-shape, …)
                # are not in React's CSSProperties type; cast rather than drop.
                out.append('style={%s as React.CSSProperties}' % obj_to_jsx(obj))
            continue
        # Framer puts a `name` on layout divs; React only allows it on form
        # elements, so drop it there (data-framer-name still carries the label).
        if low == 'name' and tag not in ('input', 'select', 'textarea', 'button',
                                         'form', 'iframe', 'object', 'param',
                                         'map', 'meta', 'output', 'fieldset'):
            continue
        if not low.startswith(('data-', 'aria-')) and low not in SAFE_ATTRS:
            name, low = 'data-' + low.replace(':', '-'), 'data-' + low
        jsx_name = ATTR_MAP.get(low, name if low.startswith('data-') else low)
        if not low.startswith(('data-', 'aria-')) and ':' in jsx_name:
            continue
        if jsx_name in NUM_ATTRS and re.match(r'^-?\d+$', val.strip()):
            out.append('%s={%s}' % (jsx_name, val.strip()))
        elif '"' in val:
            # JSX string attributes take no backslash escapes; use an expression.
            out.append('%s={%s}' % (jsx_name, json.dumps(val)))
        else:
            out.append('%s=%s' % (jsx_name, json.dumps(val)))
    return (' ' + ' '.join(out) if out else ''), hidden

TAG_RE = re.compile(r'<(/?)([a-zA-Z][a-zA-Z0-9:-]*)((?:[^>"\']|"[^"]*"|\'[^\']*\')*?)(/?)>')
COMMENT_RE = re.compile(r'<!--.*?-->', re.S)

def escape_text(t):
    import html as _h
    t = _h.unescape(t)
    if not t.strip():
        # A space between two elements is meaningful text (it is what separates
        # the words of split headings); JSX drops it unless it is explicit.
        return '{" "}' if ' ' in t else ''
    # JSX-safe: braces must be escaped
    if '{' in t or '}' in t or '<' in t or '>' in t:
        return '{' + json.dumps(t) + '}'
    return t

def convert(html, reveal=True):
    html = COMMENT_RE.sub('', html)
    out, pos, char_i = [], 0, [0]
    for m in TAG_RE.finditer(html):
        text = html[pos:m.start()]
        if text:
            out.append(escape_text(text))
        pos = m.end()
        closing, tag, attrs, selfc = m.group(1), m.group(2), m.group(3), m.group(4)
        tl = tag.lower()
        if closing:
            out.append('</%s>' % SVG_TAGS.get(tl, tl))
            continue
        jsx_attrs, hidden = convert_attrs(attrs, tl)
        if hidden and reveal:
            # A single-character inline span is one glyph of Framer's split text;
            # give it an index so CSS can stagger the blur-in.
            nxt = html[m.end():m.end() + 40]
            if tl == 'span' and re.match(r'^[^<]</span>', nxt):
                jsx_attrs += ' data-char={%d}' % char_i[0]
                char_i[0] += 1
            else:
                jsx_attrs += ' data-reveal="true"'
        name_out = SVG_TAGS.get(tl, tl)
        if tl in VOID or tl in SVG_SELF or selfc:
            out.append('<%s%s />' % (name_out, jsx_attrs))
        else:
            out.append('<%s%s>' % (name_out, jsx_attrs))
        if len(out) > 1 and len(''.join(out[-2:])) > 160:
            out.append('\n')
    tail = html[pos:]
    if tail:
        out.append(escape_text(tail))
    return ''.join(out)

if __name__ == '__main__':
    src, dst = sys.argv[1], sys.argv[2]
    open(dst, 'w').write(convert(open(src, encoding='utf-8', errors='ignore').read()))
    print('wrote', dst)
