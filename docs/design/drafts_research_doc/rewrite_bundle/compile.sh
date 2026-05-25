#!/usr/bin/env bash
set -euo pipefail
MAIN="state_collapser_mathematical_model_rewrite_first_draft"
pdflatex -interaction=nonstopmode -halt-on-error "${MAIN}.tex"
if command -v bibtex >/dev/null 2>&1; then
  bibtex "${MAIN}"
elif command -v bibtex8 >/dev/null 2>&1; then
  bibtex8 "${MAIN}"
else
  echo "No bibtex/bibtex8 found; continuing with any existing ${MAIN}.bbl" >&2
fi
pdflatex -interaction=nonstopmode -halt-on-error "${MAIN}.tex"
pdflatex -interaction=nonstopmode -halt-on-error "${MAIN}.tex"
echo "Built ${MAIN}.pdf"
