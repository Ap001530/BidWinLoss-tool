# Appendices {-}

## Appendix A: Synthetic Data Generation, Full Parameters {-}

This appendix gives the generator's exact parameters, complementing the methodology and justification given in Chapter 3. The full generator source is `data/generate_synthetic_bids.py`.

**Table A.1: Feature marginal distributions**

| Feature | Values and probabilities |
|---|---|
| Client segment | AAA publisher 30%, mid-size publisher 32%, indie studio 28%, platform holder 10% |
| Project type | Full development 18%, co-development 34%, porting 20%, live operations 16%, art services 12% |
| Relationship history | New client 45%, prior/poor delivery 10%, prior/neutral delivery 22%, prior/good delivery 23% |
| Incumbency position | Greenfield 55%, defending existing work 22%, displacing a competitor 23% |

Deal origin, pre-RFP engagement, effort, price position, requirement coverage, portfolio similarity, geo/timezone fit, security credentials, and competing-bidder count are each drawn conditionally or from continuous distributions (lognormal for effort; Beta for geo/timezone fit; Poisson for competing bidders) as described in Chapter 3; exact distributional parameters are given in the generator source.

**Table A.2: Encoded log-odds weights (relative effect on win propensity)**

| Feature / level | Encoded effect |
|---|---|
| Relationship history: new / poor prior / neutral prior / good prior | −0.35 / −0.55 / +0.35 / +0.95 |
| Deal origin: inbound | +0.75 |
| Pre-RFP engagement | +0.65 |
| Incumbency: greenfield / defending / displacing | 0 / +0.55 / −0.60 |
| Price position | −0.045 per point above benchmark; −0.017 per point below |
| Requirement coverage | +2.4 × (coverage − 0.75) |
| Portfolio similarity | +1.3 × (similarity − 0.5) |
| Effort | −0.0012 × (person-months − 90) |
| Geo/timezone fit | +0.9 × (fit − 0.6) |
| Security credentials | +0.20 (base; see interaction below) |
| Competing bidders | −0.12 × (count − 3) |
| Interaction: weak portfolio (< 0.45) × new client | −1.1 |
| Interaction: security credentials × AAA/platform segment | +0.85 |
| Interaction: price overage × indie-studio segment | −0.03 per point |
| Latent noise | Gaussian, σ = 1.25 |
| Label noise | 5% of outcomes flipped post-draw |

The intercept is calibrated by binary search so the realised win rate lands close to 30%; on the run this thesis reports, the realised win rate was 30.6% across 500 bids.

## Appendix B: Power BI Migration Plan {-}

This appendix sets out concretely what porting the delivered pipeline's output to Power BI, the originally proposed delivery mechanism (Section 1.6, Section 3.4), would involve, since the pipeline was deliberately built to make this a presentation-layer addition rather than a rebuild.

1. **Data import.** `outputs/model_results.json`, or the nine flattened per-section tables already generated for the Claude Artifact dashboard (`dashboard/tables/*.json`, Chapter 4), would be imported via Power Query as Power BI tables; the flattened tables are directly usable as-is, since Power BI, like the Claude Artifact platform, works natively with tabular data.
2. **Report pages.** Each dashboard section described in Chapter 4 maps to one Power BI report page: a performance-summary page (card visuals for AUC, Brier score, and the Spearman correlation, plus a line chart for the ROC curve and a matrix visual for the confusion matrix); a SHAP importance page (a horizontal bar chart); a hypothesis-comparison page (a table visual with conditional formatting on the rank-shift column); and an example-bids page (a table with drill-through to a detail page per bid).
3. **The scorer.** This is the one component that cannot be ported directly, since Power BI's native interactivity does not support a live, client-side arithmetic scorer in the way the web artefact's JavaScript implementation does (Section 4.4). The closest native equivalent is a set of Power BI "What if" parameters, one slider per numeric feature and one dropdown per categorical feature, feeding a DAX measure that replicates the logistic surrogate's exact computation (intercept plus the sum of each standardised feature times its coefficient, passed through a logistic transform), using the coefficients already exported in `outputs/model_results.json`'s `scorer_model` object. This is a direct, mechanical translation of existing, already-computed numbers into DAX, not new modelling work.
4. **Refresh.** A scheduled Power BI refresh, pulling an updated `model_results.json` each time the underlying pipeline is re-run (for example, on a periodic schedule once real bid data accumulates, Chapter 7), would restore the MLOps-style automated refresh specified in the original proposal, implemented as a scheduled task that re-runs `src/train_model.py` and republishes its output file to wherever Power BI's refresh step reads from.

## Appendix C: Repository and Pipeline Structure {-}

**Table C.1: Pipeline scripts, their CRISP-DM stage (Chapter 3), and how to run them**

| Script | CRISP-DM stage | Output | Run |
|---|---|---|---|
| `data/generate_synthetic_bids.py` | Data understanding, data preparation | `data/synthetic_bids.csv` | `python3 data/generate_synthetic_bids.py` |
| `src/train_model.py` | Modelling, evaluation | `outputs/model_results.json` | `python3 src/train_model.py` |
| `dashboard/make_tables.py` | Deployment | `dashboard/tables/*.json`, `docs/data/*.json` | `python3 dashboard/make_tables.py` |
| `dashboard/index.html` | Deployment | Claude Artifact dashboard | Published as a hosted Artifact |
| `docs/index.html` | Deployment | Static GitHub Pages site | Served from the repository's `docs/` folder |

`data/methodology_synthetic_data.md` gives the synthetic-data methodology in its original, standalone form, written before this thesis and incorporated into Chapter 3. All code is version-controlled in the project's Git repository alongside this thesis document, consistent with Hevner et al.'s [-@hevner2004design] requirement that the research process be rigorously and repeatably documented (Chapter 3).

## Appendix D: Feature Glossary {-}

This glossary reproduces, for reference, the plain-language feature definitions built into the artefact's clickable glossary (Chapter 4), covering every feature used in modelling.

| Feature | Definition |
|---|---|
| History with this client | Whether this client is new to Virtuos, or a repeat client, and if a repeat client, how the last project went: poorly, fine, or well. |
| Who started the conversation | Whether the client approached Virtuos about this opportunity (inbound), or Virtuos pursued the client (outbound). |
| Talked before the formal bid | Whether Virtuos had conversations with the client about the project before the official request for proposal went out. |
| Starting position on this deal | Whether this is a brand-new opportunity with no prior vendor, work Virtuos is already doing that it is defending, or work currently done by a competitor that Virtuos is trying to win away. |
| Project size | The estimated effort for the project, in person-months. |
| Price vs. the market rate | How Virtuos's quoted price compares to the typical rate for similar work; positive means priced above that benchmark. |
| How much of the brief we covered | The share of the client's stated requirements that the proposal fully addresses. |
| Relevant past work | How closely Virtuos's existing portfolio matches the kind of work this project needs. |
| Time zone overlap | How much the working hours of Virtuos's team overlap with the client's. |
| Security credentials in place | Whether Virtuos already holds the data and IP security certifications this client's industry typically requires. |
| Number of competing bidders | How many other studios were bidding for the same project (flagged in Chapter 3 as a possible real-world leakage risk, since it is often only known after the decision is made). |
| Type of client | AAA publisher, mid-size publisher, indie studio, or platform holder. |
| Type of project | Full development, co-development, porting, live operations, or art services. |
