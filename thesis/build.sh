#!/usr/bin/env bash
# Builds thesis/thesis.docx from metadata.yaml + chapters/*.md + references.bib.
# Chapters are concatenated in filename order (01-, 02-, ... prefixes control order).
set -euo pipefail
cd "$(dirname "$0")"

CHAPTERS=$(ls chapters/*.md | sort)

pandoc metadata.yaml $CHAPTERS \
  --citeproc \
  --bibliography references.bib \
  --toc --toc-depth=3 \
  --number-sections \
  --reference-doc=reference.docx \
  -o thesis.docx

echo "Built thesis/thesis.docx"
