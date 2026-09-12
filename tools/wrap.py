# -*- coding: utf-8 -*-
"""Wrap each lifted JSX fragment in a React component file."""
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FF=os.path.join(REPO, '.lift', 'ff')
OUT=os.path.join(REPO, 'components', 'lifted')

HEAD = '''/* eslint-disable @next/next/no-img-element */
/**
 * Lifted verbatim from the Fastfolio template: the same markup and the same
 * class names, so `styles/fastfolio.css` (also taken from the template) lays it
 * out identically. Only the copy, the images and the accent colour differ.
 *
 * Generated — see the lift script in the project notes; edit the data, not this.
 */
export default function %s() {
  return (
    %s
  );
}
'''

for comp, name in [('SkillsSection','skills'),
                   ('ExperienceSection','experience'),
                   ('TestimonialsSection','testimonials')]:
    jsx = open(os.path.join(FF, name+'.built.jsx')).read().strip()
    src = HEAD % (comp, jsx)
    open(os.path.join(OUT, comp+'.tsx'),'w').write(src)
    print(comp, len(src))
