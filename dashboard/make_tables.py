"""
Flattens outputs/model_results.json into one small array-of-rows JSON file per
dashboard section. The dashboard Artifact type only loads tabular (row-array)
data from an attached file source, not an arbitrary nested JSON object, so
this split is required before each file can be attached as a dataset.
"""

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "outputs", "model_results.json")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tables")
os.makedirs(OUT, exist_ok=True)

r = json.load(open(SRC))


def dump(name, rows):
    with open(os.path.join(OUT, f"{name}.json"), "w") as f:
        json.dump(rows, f)
    print(name, len(rows), "rows")


# summary (1 row)
cm = r["performance"]["confusion_matrix"]
dump("summary", [{
    "n_rows": r["meta"]["n_rows"],
    "win_rate": r["meta"]["win_rate"],
    "model": r["meta"]["model"],
    "n_train": r["meta"]["n_train"],
    "n_test": r["meta"]["n_test"],
    "test_auc": r["performance"]["test_auc"],
    "cv_auc_mean": r["performance"]["cv_auc_mean"],
    "cv_auc_std": r["performance"]["cv_auc_std"],
    "brier_score": r["performance"]["brier_score"],
    "spearman": r["spearman_rank_correlation"],
    "tn": cm["tn"], "fp": cm["fp"], "fn": cm["fn"], "tp": cm["tp"],
}])

dump("roc_curve", r["performance"]["roc_curve"])
dump("calibration", r["performance"]["calibration_bins"])
dump("shap_importance", r["shap_global_importance"])
dump("hypothesis_comparison", r["hypothesis_comparison"])

ex_rows = []
for i, ex in enumerate(r["example_bids"]):
    row = {
        "bid_id": i + 1,
        "client_segment": ex["client_segment"],
        "project_type": ex["project_type"],
        "win_probability": ex["win_probability"],
        "actual_outcome": ex["actual_outcome"],
    }
    for j, f in enumerate(ex["top_positive_factors"][:3]):
        row[f"pos{j+1}_feature"] = f["feature"]
        row[f"pos{j+1}_value"] = f["contribution"]
    for j, f in enumerate(ex["top_negative_factors"][:3]):
        row[f"neg{j+1}_feature"] = f["feature"]
        row[f"neg{j+1}_value"] = f["contribution"]
    for feat, val in ex.get("features", {}).items():
        row[f"feat_{feat}"] = val
    ex_rows.append(row)
dump("examples", ex_rows)

sm = r["scorer_model"]
num_rows = []
for i, f in enumerate(sm["num_features"]):
    num_rows.append({
        "feature": f,
        "mean": sm["num_means"][i],
        "scale": sm["num_scales"][i],
        "coef": sm["num_coefs"][i],
        "default": sm["num_medians_for_defaults"][i],
    })
dump("scorer_num", num_rows)

cat_rows = []
for cat in sm["cat_features"]:
    default_val = sm["cat_mode_for_defaults"][cat]
    for category in sm["cat_categories"][cat]:
        key = f"{cat}_{category}"
        cat_rows.append({
            "feature": cat,
            "category": category,
            "coef": sm["cat_coefs"].get(key, 0.0),
            "is_default": category == default_val,
        })
dump("scorer_cat", cat_rows)

dump("scorer_meta", [{
    "intercept": sm["intercept"],
    "auc_on_full_data": sm["auc_on_full_data"],
    "cv_auc_mean": sm["cv_auc_mean"],
    "cv_auc_std": sm["cv_auc_std"],
}])

print("done ->", OUT)
