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

| Chapter | Status |
|---|---|
| 1. Introduction | Draft for review |
| 2. Literature Review | Not started |
| 3. Methodology | Not started |
| 4. Design and Implementation | Not started |
| 5. Evaluation | Not started |
| 6. Discussion | Not started |
| 7. Conclusion | Not started |
| Appendices | Not started |

## Known open items (need your input before later chapters)

- **Citation style**: see above.
- **University template**: if your program has a required thesis template
  (title page format, margins, font, required front-matter pages like a
  declaration of originality or ethics statement), send it and I'll match
  `build.sh`'s output to it rather than Pandoc's default styling.
- **Supervisor sign-off on scope deviations**: Chapter 1, Section 1.6 states
  plainly that the delivered artefact uses one GBM model (not a Random
  Forest/XGBoost comparison) and a web dashboard (not Power BI). Confirm this
  framing is acceptable to your supervisor before it propagates through the
  rest of the thesis.
