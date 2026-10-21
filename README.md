# BidWinLoss-tool

Thesis project: a bid-competitiveness prediction pipeline for Virtuos' Engineering BU — a
machine-learning tool that predicts how likely a game-development proposal is to win a bid,
and uses SHAP to check which features actually drive the prediction against the BU's
documented hypotheses about what makes a bid competitive.

**This repository uses synthetic data.** See `data/methodology_synthetic_data.md` for the full,
honest framing: the pipeline is validated on data where feature→outcome relationships were
encoded from the BU's own documented hypotheses, so the claim here is "the pipeline recovers
known signal correctly," not "this is what wins real Virtuos bids."

## Pipeline

```
data/generate_synthetic_bids.py   -> data/synthetic_bids.csv
src/train_model.py                -> outputs/model_results.json
```

1. **`data/generate_synthetic_bids.py`** generates 500 synthetic resolved bids (Won/Lost) with
   realistic correlation, interaction effects, class imbalance, label noise, and missing values.
2. **`src/train_model.py`** trains a `GradientBoostingClassifier`, evaluates it (AUC, confusion
   matrix, ROC, calibration), runs `shap.TreeExplainer` for global and per-bid feature
   attribution, compares the SHAP ranking against the BU's documented hypothesis ranking, and
   also fits a logistic-regression surrogate (reported with its own AUC) so the dashboard's
   interactive scorer can compute an exact, transparent win-probability decomposition
   client-side without porting a tree ensemble into JavaScript.

Run both in order:

```bash
pip install -r requirements.txt
python3 data/generate_synthetic_bids.py
python3 src/train_model.py
```

This writes `outputs/model_results.json`, which is the single source of truth for every number
shown in the results dashboard — nothing in the dashboard is hand-typed.

## Dashboard + scorer

The thesis artifact (results dashboard with an embedded interactive bid scorer) is built from
`outputs/model_results.json` and published as a Claude Artifact.
