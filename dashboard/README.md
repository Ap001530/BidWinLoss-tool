# Thesis artifact: results dashboard + interactive scorer

`index.html` is the page body published as a Claude Artifact (a "Dashboard" type
artifact, whose host wraps it in a `<style>`/`<script>` body fragment — not a
standalone HTML document). It is a snapshot of the dashboard's source at
publish time, kept here for the thesis repo's record; the live version is the
Artifact itself.

**Live artifact:** https://claude.ai/artifact/SbM2Nh2HSxJpnopa5ADTwG

## What it shows

Every number on the page is read from `outputs/model_results.json` (the single
data source attached to the dashboard) — nothing is hand-typed:

1. **Synthetic-data disclaimer** — up front, matching `data/methodology_synthetic_data.md`.
2. **Model performance** — 5-fold CV AUC, held-out test AUC, Brier score,
   ROC curve, confusion matrix.
3. **Global SHAP feature importance** — mean |SHAP value| per feature,
   collapsed from one-hot columns back to the business-readable feature.
4. **SHAP vs. BU hypothesis comparison** — the BU's documented hypothesis
   ranking against where SHAP actually places each feature, with the
   Spearman rank correlation and an explicit note that agreement is expected
   by construction (the synthetic data's weights come from the same
   hypotheses) and that divergences are the methodologically interesting part.
5. **Example bids** — eight sampled bids with predicted win probability and
   their top SHAP-attributed positive/negative factors.
6. **Interactive scorer** — lets a reader set a hypothetical bid's features
   and see an estimated win probability. It runs a logistic-regression
   surrogate (also trained in `src/train_model.py`, reported with its own
   AUC) rather than the gradient-boosted model, so its decision function can
   be evaluated exactly in the browser: every factor shown is an exact
   coefficient × standardized-value term, not an approximation of the GBM.

## Regenerating

```bash
python3 data/generate_synthetic_bids.py
python3 src/train_model.py          # writes outputs/model_results.json
```

Then re-publish `outputs/model_results.json` as the dashboard's attached
dataset file and republish `dashboard/index.html` as its page.
