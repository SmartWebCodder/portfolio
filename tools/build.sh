#!/usr/bin/env bash
# Regenerate every lifted component and stylesheet from the template exports.
set -euo pipefail
cd "$(dirname "$0")/.."

python3 tools/extract_page.py   # Devsync   -> .lift/ds
python3 tools/extract.py        # Fastfolio -> .lift/ff
python3 tools/css.py            # Fastfolio stylesheet + class inventory
python3 tools/css2.py           # filter it to the three lifted sections

python3 tools/dslift.py         # Devsync content, links, accent, tickers
python3 tools/dscss.py          # -> styles/devsync.css
python3 tools/dssplit.py        # -> components/devsync/*.tsx

python3 tools/lift.py           # Fastfolio content
python3 tools/wrap.py           # -> components/lifted/*.tsx
python3 tools/ffcss.py          # -> styles/fastfolio.css

echo "done"
