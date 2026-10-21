# Synthetic Data — Methodology & Honest Framing

## What this experiment demonstrates (and what it does not)

This study uses **synthetically generated bid data**. The claim being made is narrow and
deliberate:

> **A working end-to-end pipeline, validated by its ability to recover feature–outcome
> relationships grounded in the documented feature hypotheses.**

This is a **validation of method**, not a discovery about what wins real bids. Because the
relationships between features and the Win/Lost outcome are *encoded by the author* in the
data generator, any importance the trained model and SHAP later report is — by construction —
a recovery of those encoded relationships. It is therefore **not evidence** about the true
drivers of Virtuos' bid success. Stating this plainly is what protects the result in a
defence: the contribution is the pipeline (data → model → SHAP → dashboard) and the
demonstration that it correctly surfaces known signal under realistic noise.

## Provenance of the encoded relationships

No empirical practitioner survey results were available at generation time. The direction and
*relative* strength of each feature's effect were therefore set from the **supervisor-reviewed
feature hypotheses document** (the Engineering BU's stated assumptions about what should drive
competitiveness). This is the most defensible anchor available short of real data, and it keeps
the later "SHAP vs. BU assumptions" comparison meaningful: the pipeline is being asked to
recover the BU's own stated hypotheses from noisy data, which is a genuine test of the method.

**Limitation:** because the generator's weights come from the same hypotheses the model is
later compared against, alignment between SHAP and hypotheses is expected and must not be read
as independent confirmation. Divergences that arise are attributable to noise, interactions, or
class imbalance interacting with the learner — which is itself the interesting methodological
content.

## Design choices that keep the data non-trivial

The generator deliberately avoids a clean, trivially-learnable rule:

1. **Noisy logistic outcome** — win probability is a logistic function of a latent score with
   added Gaussian noise (σ≈1.25), not a deterministic threshold.
2. **Label noise** — ~5% of outcomes are flipped, mimicking mislabeled or genuinely surprising
   results in real bid logs.
3. **Correlated features** — e.g. inbound deals correlate with prior good relationships;
   pre-RFP engagement correlates with both; price position correlates with effort.
4. **Interaction effects** — a weak portfolio penalises *new* clients far more than repeat ones;
   IP-security credentials matter much more for AAA/platform clients; indies are more
   price-sensitive. These make the problem non-additive, so a linear model alone cannot fully
   capture it (motivating tree-based models + SHAP).
5. **Class imbalance** — base win rate calibrated to ~30%, matching a realistic bid log rather
   than a balanced 50/50.
6. **Missing values** — injected into a few fields to exercise the imputation step.

The result is a dataset a model can learn well but **not perfectly** — the 5-fold logistic CV
AUC lands around 0.72, confirming strong-but-imperfect recoverable signal. A near-1.0 AUC would
be a red flag that the data is trivially circular; this is not that.

## A deliberately noteworthy encoded pattern

One encoded relationship is intentionally counter-intuitive so the pipeline has something
non-obvious to recover: a **prior relationship that delivered poorly** (`relationship_history = 1`)
is encoded as *worse* than a brand-new client, not better. If SHAP later separates "prior-good"
from "prior-poor" rather than treating all repeat business as positive, that demonstrates the
pipeline captures nuance a naïve binary "repeat client?" feature would miss.

## Feature set used

Because synthetic generation removes the "was it ever logged?" constraint, the richer feature
set is used: client_segment, project_type, relationship_history (with prior-delivery outcome
folded in as an ordinal), deal_origin_inbound, pre_rfp_engagement, incumbency,
effort_person_months, price_position_pct, requirement_coverage, portfolio_similarity,
geo_timezone_fit, ip_security_credentials, competing_bidders, and the win target.

**competing_bidders caveat:** in a *real* deployment this value is often known only after the
decision, making it a leakage risk. It is retained here for completeness but flagged; with real
data it should be verified as known-at-bid-time or demoted to analysis-only.
