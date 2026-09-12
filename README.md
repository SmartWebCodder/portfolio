# Portfolio — Akintoye Ayomide Nelson

A single-page portfolio built with Next.js (App Router) and TypeScript.

The design is a port of two Framer templates rather than an original build:

- **Devsync** supplies the page — nav, hero, about, works, services, process,
  clients, blog and footer.
- **Fastfolio** supplies three sections — *Tools I Build With*,
  *Where I've Worked* and *Don't just take my words for it*. Fastfolio's
  testimonials section replaces Devsync's own.

Both are ported by lifting the templates' real markup and stylesheets, not by
rebuilding the designs by hand.

## Running

```bash
npm install
npm run dev      # http://localhost:3111
npm run build
```

## Layout

```
app/                    layout, page, base stylesheet
components/devsync/     generated — one component per Devsync section
components/lifted/      generated — the three Fastfolio sections
components/             Reveal, Accordion (behaviour Framer's runtime provided)
styles/devsync.css      generated from the Devsync stylesheet
styles/fastfolio.css    generated from the Fastfolio stylesheet
styles/overrides.css    hand-written; the only stylesheet meant to be edited
tools/                  the lift pipeline
lib/data.ts             profile, projects, skills
public/ds/              template images, pulled local
.lift/src/              the two template exports the pipeline reads
```

## Regenerating the lifted code

Everything under `components/devsync/`, `components/lifted/`,
`styles/devsync.css` and `styles/fastfolio.css` is generated. Edit the scripts
in `tools/`, not those files, then:

```bash
./tools/build.sh
```

The pipeline reads the template exports from `.lift/src/`. Override either path
with `DEVSYNC_HTML` / `FASTFOLIO_HTML`.

## Deliberate changes to the templates

- The green accent (`rgb(122, 242, 152)`) is remapped to orange (`#ff7a2f`).
- Devsync's About band pinned itself to the viewport and scrubbed a stack of
  images as you scrolled. The pin and the image stack are both removed; the
  name marquee stays and the portrait moved to the hero.
- Framer's runtime is not shipped, so the tickers, scroll reveals and the
  experience accordion are re-implemented in `styles/overrides.css`,
  `components/Reveal.tsx` and `components/Accordion.tsx`.
- The template's own promo overlay and "Buy Template" button are stripped.

## Known gaps

- The blog section still carries the template's three article titles; there are
  no posts behind them.
- The client logos are still the template's, not actual employers.
- Testimonials are the Fastfolio template's placeholder quotes and people.
