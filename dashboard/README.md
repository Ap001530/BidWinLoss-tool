# Thesis artifact: results dashboard + interactive scorer

`index.html` is the page body published as a Claude Artifact (a "Dashboard" type
artifact, whose host wraps it in a `<style>`/`<script>` body fragment — not a
standalone HTML document). It is a snapshot of the dashboard's source at
publish time, kept here for the thesis repo's record; the live version is the
Artifact itself.

**Live artifact:** https://claude.ai/artifact/SbM2Nh2HSxJpnopa5ADTwG

## Why `tables/*.json` instead of `outputs/model_results.json` directly

The dashboard type only loads **tabular** data (an array of row objects) from
an attached file source — it refused `outputs/model_results.json` as-is
("the file has no rows this dashboard can read") because that file is one
nested JSON object, not a flat table. `make_tables.py` flattens it into nine
small row-array files, one per dashboard section, each attached as its own
dataset:

| Dataset | Rows | Feeds |
|---|---|---|
| `summary` | 1 | headline AUC/Brier/Spearman stats, confusion matrix |
| `roc_curve` | 60 | ROC curve |
| `calibration` | 5 | (reserved — calibration bins, not currently drawn) |
| `shap_importance` | 13 | global SHAP bar chart |
| `hypothesis_comparison` | 13 | SHAP-vs-BU-hypothesis table |
| `examples` | 8 | example bid cards |
| `scorer_num` | 10 | scorer: numeric coefficients |
| `scorer_cat` | 12 | scorer: categorical coefficients |
| `scorer_meta` | 1 | scorer: intercept + AUC |

## What it shows

Every number on the page is read from one of the datasets above (ultimately
derived from `outputs/model_results.json`) — nothing is hand-typed:

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
python3 dashboard/make_tables.py    # writes dashboard/tables/*.json
```

Then re-upload each file in `dashboard/tables/` as an asset on the dashboard
Artifact, point each `datasets/<id>` document at its new asset url, and
republish `dashboard/index.html` as its page.
