"""
Assembles overleaf/main_single_paste.tex: one self-contained LaTeX file with
every chapter and the bibliography inlined, for pasting directly into
Overleaf's editor instead of uploading a multi-file project.
"""
import re
from pathlib import Path

ROOT = Path(__file__).parent
OVERLEAF = ROOT / "overleaf"

PREAMBLE = r"""\documentclass[12pt,oneside]{report}

% Compile this with XeLaTeX (Overleaf: Menu -> Compiler -> XeLaTeX), not pdfLaTeX:
% the thesis text uses Unicode characters directly (sigma, rho, the minus
% sign), which XeLaTeX's native Unicode handling renders with no extra
% packages or escaping; pdfLaTeX will error on them.

% ---- Page geometry (adjust to your university's required margins) ----
\usepackage[a4paper,margin=1in]{geometry}

% ---- Fonts and spacing ----
\usepackage{fontspec}
\setmainfont{TeX Gyre Termes}   % metric-compatible Times New Roman clone; free, bundled with TeX Live
\usepackage{setspace}
\onehalfspacing             % \doublespacing or \singlespacing to change

% ---- Tables, figures, links ----
\usepackage{calc}
\usepackage{array}
\usepackage{longtable}
\usepackage{booktabs}
\usepackage{graphicx}
\setkeys{Gin}{width=0.85\linewidth,keepaspectratio}
\usepackage[hyphens]{url}
\usepackage{microtype}
\usepackage[htt]{hyphenat}
\usepackage[colorlinks=true,linkcolor=blue,citecolor=blue,urlcolor=blue]{hyperref}

% ---- Bibliography: typed out by hand below (thebibliography), not natbib+.bib,
% so this one file is the whole project with no references.bib to upload
% separately. Each entry links to its real source (DOI or URL), verified
% individually before being added; nothing here is invented. ----
\usepackage{natbib}

\providecommand{\tightlist}{%
  \setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}

% ---- Front matter ----
\title{Predictive Market Intelligence for Engineering Proposals in the Video Game Co-Development Industry \\[0.5em]
\large A Design Science Research Study of a Bid-Competitiveness Prediction Pipeline for Virtuos' Engineering Business Unit}
\author{[Your full name]}
\date{[Submission date]}

\begin{document}

\maketitle
\tableofcontents
\listoffigures

"""

BIBLIOGRAPHY = r"""
\begin{thebibliography}{}

\bibitem[Breiman, 2001]{breiman2001random}
Breiman, L. (2001).
\newblock Random forests.
\newblock {\em Machine Learning}, 45(1):5--32.
\newblock \href{https://doi.org/10.1023/A:1010933404324}{doi.org/10.1023/A:1010933404324}

\bibitem[Chapman et~al., 2000]{chapman2000crispdm}
Chapman, P., Clinton, J., Kerber, R., Khabaza, T., Reinartz, T., Shearer, C.,
  and Wirth, R. (2000).
\newblock {CRISP-DM} 1.0: Step-by-step data mining guide.
\newblock Technical report, The CRISP-DM Consortium.

\bibitem[Chen and Guestrin, 2016]{chen2016xgboost}
Chen, T. and Guestrin, C. (2016).
\newblock {XGBoost}: A scalable tree boosting system.
\newblock In {\em Proceedings of the 22nd ACM SIGKDD International Conference
  on Knowledge Discovery and Data Mining (KDD '16)}, San Francisco, CA.
\newblock \href{https://doi.org/10.1145/2939672.2939785}{doi.org/10.1145/2939672.2939785}

\bibitem[Friedman, 2001]{friedman2001greedy}
Friedman, J.~H. (2001).
\newblock Greedy function approximation: A gradient boosting machine.
\newblock {\em The Annals of Statistics}, 29(5):1189--1232.

\bibitem[He and Garcia, 2009]{he2009learning}
He, H. and Garcia, E.~A. (2009).
\newblock Learning from imbalanced data.
\newblock {\em IEEE Transactions on Knowledge and Data Engineering},
  21(9):1263--1284.
\newblock \href{https://doi.org/10.1109/TKDE.2008.239}{doi.org/10.1109/TKDE.2008.239}

\bibitem[Hevner et~al., 2004]{hevner2004design}
Hevner, A.~R., March, S.~T., Park, J., and Ram, S. (2004).
\newblock Design science in information systems research.
\newblock {\em MIS Quarterly}, 28(1):75--105.
\newblock \href{https://aisel.aisnet.org/misq/vol28/iss1/6/}{aisel.aisnet.org/misq/vol28/iss1/6}

\bibitem[Lundberg and Lee, 2017]{lundberg2017unified}
Lundberg, S.~M. and Lee, S.-I. (2017).
\newblock A unified approach to interpreting model predictions.
\newblock In {\em Advances in Neural Information Processing Systems 30 (NeurIPS
  2017)}, pages 4765--4774.
\newblock \href{https://arxiv.org/abs/1705.07874}{arxiv.org/abs/1705.07874}

\bibitem[{MarketIntelo}, 2025]{marketintelo2025gamecodev}
{MarketIntelo} (2025).
\newblock Game co-development services market size, share and trends analysis
  report 2025--2034.
\newblock Industry market research report, MarketIntelo. Vendor
  market-research estimate, not peer reviewed; accessed October 2026.
\newblock \href{https://marketintelo.com/report/game-co-development-services-market/}{marketintelo.com/report/game-co-development-services-market}

\bibitem[Olan et~al., 2024]{olan2024enabling}
Olan, F., Spanaki, K., Ahmed, W., and Zhao, G. (2024).
\newblock Enabling explainable artificial intelligence capabilities in supply
  chain decision support making.
\newblock {\em Production Planning \& Control}, 36(6):808--819.
\newblock \href{https://doi.org/10.1080/09537287.2024.2313514}{doi.org/10.1080/09537287.2024.2313514}

\bibitem[Peffers et~al., 2007]{peffers2007design}
Peffers, K., Tuunanen, T., Rothenberger, M.~A., and Chatterjee, S. (2007).
\newblock A design science research methodology for information systems
  research.
\newblock {\em Journal of Management Information Systems}, 24(3):45--77.
\newblock \href{https://doi.org/10.2753/MIS0742-1222240302}{doi.org/10.2753/MIS0742-1222240302}

\bibitem[Rezazadeh, 2020]{rezazadeh2020generalized}
Rezazadeh, A. (2020).
\newblock A generalized flow for {B2B} sales predictive modeling: An {Azure}
  machine-learning approach.
\newblock {\em Forecasting}, 2(3):267--283.
\newblock \href{https://doi.org/10.3390/forecast2030015}{doi.org/10.3390/forecast2030015}

\bibitem[Schr{\"o}er et~al., 2021]{schroer2021systematic}
Schr{\"o}er, C., Kruse, F., and Marx~G{\'o}mez, J. (2021).
\newblock A systematic literature review on applying {CRISP-DM} process model.
\newblock {\em Procedia Computer Science}, 181:526--534.
\newblock \href{https://doi.org/10.1016/j.procs.2021.01.199}{doi.org/10.1016/j.procs.2021.01.199}

\bibitem[Yan et~al., 2015]{yan2015sales}
Yan, J., Gong, M., Sun, C., Huang, J., and Chu, S.~M. (2015).
\newblock Sales pipeline win propensity prediction: A regression approach.
\newblock In {\em 2015 IFIP/IEEE International Symposium on Integrated Network
  Management (IM)}, Ottawa, Canada. IEEE.
\newblock \href{https://arxiv.org/abs/1502.06229}{arxiv.org/abs/1502.06229}

\bibitem[Zahid et~al., 2021]{zahid2021predicting}
Zahid, E., Ong, Y.~J., Megahed, A., and Nakamura, T. (2021).
\newblock Predicting loss risks for b2b tendering processes.
\newblock {\em arXiv preprint arXiv:2109.06815}.
\newblock \href{https://arxiv.org/abs/2109.06815}{arxiv.org/abs/2109.06815}

\end{thebibliography}
"""

CHAPTER_ORDER = [
    "01-introduction",
    "02-literature-review",
    "03-methodology",
    "04-design-implementation",
    "05-evaluation",
    "06-discussion",
    "07-conclusion",
]
APPENDIX = "08-appendices"

parts = [PREAMBLE]
for name in CHAPTER_ORDER:
    text = (OVERLEAF / "chapters" / f"{name}.tex").read_text()
    parts.append(text.strip())
    parts.append("\n\n")

parts.append(BIBLIOGRAPHY)
parts.append("\n")
parts.append((OVERLEAF / "chapters" / f"{APPENDIX}.tex").read_text().strip())
parts.append("\n\n\\end{document}\n")

out = "".join(parts)
out_path = OVERLEAF / "main_single_paste.tex"
out_path.write_text(out)
print(f"Wrote {out_path} ({len(out):,} chars, {len(out.split()):,} words)")
