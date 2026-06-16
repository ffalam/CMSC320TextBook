#!/usr/bin/env bash
# Merge all TOC-listed content into pdf/CMSC320TextBook.ipynb and export a PDF.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

if [[ -d "$ROOT/venv/bin" ]]; then
  # shellcheck disable=SC1091
  source "$ROOT/venv/bin/activate"
fi

echo "==> Merging notebooks from _toc.yml..."
python3 merge_for_pdf.py

echo "==> Converting to LaTeX (requires Pandoc + LaTeX)..."
jupyter nbconvert \
  --to latex \
  --no-input \
  --no-prompt \
  "$ROOT/pdf/CMSC320TextBook.ipynb" \
  --output CMSC320TextBook \
  --output-dir "$ROOT/pdf"

echo "==> Building PDF with xelatex..."
(
  cd "$ROOT/pdf"
  for _ in 1 2 3; do
    xelatex -interaction=nonstopmode CMSC320TextBook.tex >/dev/null || true
  done
)

if [[ ! -f "$ROOT/pdf/CMSC320TextBook.pdf" ]]; then
  echo "PDF build failed; see $ROOT/pdf/CMSC320TextBook.log" >&2
  exit 1
fi

echo "==> Validating PDF..."
python3 "$ROOT/validate_pdf.py"

if command -v convert >/dev/null 2>&1 && [[ -f "$ROOT/pdf/cover.png" ]]; then
  echo "==> Updating cover.pdf from cover.png..."
  convert "$ROOT/pdf/cover.png" "$ROOT/pdf/cover.pdf"
fi

echo "Done: $ROOT/pdf/CMSC320TextBook.pdf"
