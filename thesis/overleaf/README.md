# Overleaf project

This is the LaTeX version of the thesis: same 7 chapters, appendices,
figures, and 14 verified citations as `thesis/thesis.docx`, converted so you
can edit and compile it directly on Overleaf. Two ways to get it in:

### Option A: copy-paste a single file (easiest, no upload)

`main_single_paste.tex` is the whole thesis as one file, every chapter and
the bibliography (with its clickable source links) inlined, no separate
`.bib` or chapter files needed.

1. Open a new blank project on Overleaf (or open your existing project's
   `main.tex`).
2. Open `main_single_paste.tex` here, select all, copy, and paste it in,
   replacing whatever was there. It renders as soon as Overleaf recompiles
   (autocompile, or press Ctrl/Cmd+Enter).
3. Set the compiler to **XeLaTeX**: Menu (top left) -> **Compiler** ->
   XeLaTeX. Required: the text uses Unicode characters directly (sigma, rho,
   the minus sign) that plain pdfLaTeX can't typeset without extra escaping,
   and XeLaTeX handles them natively.
4. Upload the 4 figures: drag the 4 PNGs from the `figures/` folder here
   into Overleaf's file tree (left panel), into a `figures/` folder there
   too. This is the one thing that can't be pasted as text (they're images);
   everything else is in the one file.

Verified locally before handoff: compiles clean with XeLaTeX in two passes,
zero errors, all 14 citations resolved, 57 pages (matches the multi-file
version below exactly, since it's the same content, just concatenated).

### Option B: upload the full project (closer to normal LaTeX project layout)

1. On Overleaf: **New Project -> Upload Project**, and upload this whole
   `overleaf/` folder as a zip (`../overleaf-thesis.zip` already has it
   packaged), or `git push` it to a new Overleaf Git project if you're on a
   paid plan.
2. Same compiler step as above: Menu -> Compiler -> XeLaTeX.
3. Compile. Overleaf runs XeLaTeX -> BibTeX -> XeLaTeX -> XeLaTeX
   automatically on every compile, which is what citations and
   cross-references need; you don't need to trigger that sequence by hand.

This version keeps `references.bib` separate (so you get natbib's
one-line citation-style swap described below) and chapters as separate
files (closer to how `thesis/chapters/*.md` is organized, if you want to
keep editing per-chapter). The single-paste file in Option A has the
bibliography hand-typed inline instead, so it loses that one-line style
swap; if you want both the paste convenience and the style flexibility,
paste Option A in first, then split the bibliography back out to a
`references.bib` + `\bibliography{references}` yourself later.

Both were verified locally before handoff: XeLaTeX + BibTeX + two more
XeLaTeX passes, zero errors, all 14 citations resolved, 57 pages, `main.pdf`
included here so you can compare against what Overleaf produces.

## Structure

```
main.tex              Preamble, title page, chapter order, bibliography placement
chapters/*.tex         One file per chapter (converted from thesis/chapters/*.md)
figures/*.png          The same 4 figures as the Word version
references.bib         Same 14 verified citations as thesis/references.bib
```

## What's different from the Word version

- **Citations**: natbib + `\bibliographystyle{apalike}` instead of Pandoc
  citeproc. This is the one deliberate improvement LaTeX gives you over
  Word here: to change citation style, change one line,
  `\bibliographystyle{apalike}` in `main.tex`, to `plainnat`, `ieeetr`,
  `unsrtnat`, or any other natbib-compatible style, no CSL file needed, no
  rebuild script to re-run. (If your program specifically requires APA 7th
  with its exact formatting rules, `apalike` is close but not identical;
  the `apacite` package is the precise APA7 implementation if needed.)
- **Spacing/fonts**: `\onehalfspacing` (setspace package) and TeX Gyre Termes
  (a free, metric-compatible Times New Roman clone) in `main.tex`, matching
  the Word draft's 1.5-spacing, Times New Roman 12pt choice. Change
  `\onehalfspacing` to `\doublespacing` or `\singlespacing` to adjust, same
  as the Word version's options.
- **Two small LaTeX-only touch-ups** that only exist in the `.tex` files, not
  mirrored back to the `.md` source in `thesis/chapters/`: the Appendix C
  repository-structure table has rebalanced column widths and a smaller font
  (the original even 25/25/25/25 split overflowed the page margin with long
  file paths in a LaTeX table in a way Word's table didn't), and every
  figure's manual "Figure N.N:" caption prefix was removed, since LaTeX's
  `\caption{}` numbers figures automatically and the two together produced
  "Figure 5.1: Figure 5.1: ...". If you regenerate `chapters/*.tex` from the
  Markdown source (see below), you'll need to reapply both by hand, or just
  keep editing the `.tex` directly going forward.

## Regenerating a chapter from the Markdown source

The `thesis/chapters/*.md` files (one directory up) remain the original
source if you'd rather keep editing Markdown and regenerate both the Word
and LaTeX output from it:

```bash
cd thesis
pandoc chapters/01-introduction.md --natbib --top-level-division=chapter \
  -o overleaf/chapters/01-introduction.tex
```

Repeat per chapter (not for `075-references.md` — LaTeX places the
bibliography itself via `\bibliography{references}` in `main.tex`, with no
equivalent file needed). Reapply the two touch-ups above afterward if you
regenerate Chapter 5 or the Appendices specifically.

## Compiling locally (optional)

If you have a local TeX distribution instead of using Overleaf:

```bash
cd overleaf
xelatex main.tex
bibtex main
xelatex main.tex
xelatex main.tex   # second re-run resolves cross-references and the figure list
```
