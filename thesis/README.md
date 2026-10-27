# Thesis

Source for the master's thesis. Chapters are written as Markdown (one file per
chapter, `chapters/NN-name.md`), citations as BibTeX (`references.bib`), and
`build.sh` assembles everything into `thesis.docx` with Pandoc.

## Why Markdown + Pandoc instead of writing directly in Word

- Chapters are plain text: easy to diff, review, and version in this git repo
  alongside the rest of the thesis project.
- Citations are real BibTeX entries, each sourced and checked against a search
  result or publisher page before being added (see each chapter for in-text
  citations; nothing is invented). `--citeproc` resolves them and builds the
  reference list automatically, so the list can never drift from what's
  actually cited.
- Pandoc's `--number-sections` auto-numbers headings, so chapter/section
  numbers never need manual upkeep as sections are added, removed or reordered.

## Building

```bash
cd thesis
./build.sh      # writes thesis.docx
```

Requires `pandoc` (already installed in this environment).

## Current citation style

Pandoc's default (a Chicago author-date style) is used for now. If your
program requires APA, Harvard, or IEEE, that's a one-line change: drop a
`.csl` file for the required style next to `references.bib` and add
`--csl=<file>.csl` to `build.sh`. Flag this once you know your program's
required style so it isn't reformatted chapter by chapter after the fact.

## Status

All chapters drafted: ~17,500 words, 54 pages at 1.5 line spacing (Times New
Roman 12pt; see "Formatting" below).

| Chapter | Status | Words |
|---|---|---|
| 1. Introduction | Draft for review | 2,265 |
| 2. Literature Review | Draft for review | 2,491 |
| 3. Methodology | Draft for review | 3,137 |
| 4. Design and Implementation | Draft for review | 2,172 |
| 5. Evaluation | Draft for review | 3,433 |
| 6. Discussion | Draft for review | 1,655 |
| 7. Conclusion | Draft for review | 1,105 |
| Appendices (A-D) | Draft for review | 1,226 |

Every citation in every chapter (14 total, listed in `references.bib`) was
individually looked up and verified against a search result or publisher page
before being added; none is invented. Every figure in Chapters 4 and 5 (model
performance, SHAP rankings, the hypothesis comparison) is read directly from
`outputs/model_results.json`, the same file the dashboard artefact itself
reads from, so the thesis and the artefact cannot drift out of sync.

## Formatting

Currently 1.5 line spacing, Times New Roman 12pt, via `thesis/reference.docx`
(a Pandoc reference template, edited with python-docx). This produced 54
pages against your ~60-page target without padding the text; double-spacing
instead gives 70 pages, single-spacing gives 38. To change it:

```bash
python3 -c "
from docx import Document
from docx.enum.text import WD_LINE_SPACING
doc = Document('thesis/reference.docx')
doc.styles['Normal'].paragraph_format.line_spacing_rule = WD_LINE_SPACING.DOUBLE  # or .SINGLE
doc.save('thesis/reference.docx')
"
./thesis/build.sh
```

## Known open items (need your input)

- **Citation style**: see above. Pandoc's default (Chicago author-date) is
  used for now; swapping to APA/Harvard/IEEE is a one-line change (a `.csl`
  file + `--csl=<file>.csl` in `build.sh`) once you know your program's
  required style.
- **University template**: if your program has a required thesis template
  (title page format, margins, required front-matter pages like a
  declaration of originality or an ethics statement, a specific line-spacing
  and font requirement), send it and I'll match `reference.docx` to it
  exactly rather than the current generic academic styling.
- **Supervisor sign-off on scope deviations**: Chapter 1 Section 1.6 and
  Chapter 3 Section 3.4 state plainly, and in detail, that the delivered
  artefact uses one GBM model (not a Random Forest/XGBoost comparison) and a
  web dashboard (not Power BI), with Appendix B setting out what porting to
  Power BI would involve. Confirm this framing is acceptable to your
  supervisor before your defence.
- **The relationship-history non-monotonicity check** (Chapter 5, Section
  5.4; Chapter 7's third recommendation): a known, flagged gap in the
  current evaluation, not yet fixed. Worth closing before a defence if time
  allows, since it is the one deliberately designed test case in the
  synthetic data this thesis's evaluation does not yet directly confirm.
