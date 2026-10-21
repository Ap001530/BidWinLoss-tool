"""
Bid competitiveness model — training, evaluation, and SHAP explanation pipeline.

Trains a gradient-boosted classifier on the synthetic bid dataset, evaluates it,
computes SHAP values for global and per-bid explanation, and writes every number the
dashboard needs to outputs/model_results.json. No numbers are hand-typed into the
dashboard — this script is the single source of truth for them.
"""

import json
import os

import numpy as np
import pandas as pd
import shap
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    RocCurveDisplay,
    brier_score_loss,
    confusion_matrix,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(ROOT, "data", "synthetic_bids.csv")
OUT_PATH = os.path.join(ROOT, "outputs", "model_results.json")

RANDOM_STATE = 42

# BU's documented hypotheses about relative feature importance (from the feature
# hypotheses document), used ONLY for the SHAP-vs-hypotheses comparison in the
# dashboard -- never fed into the model.
BU_HYPOTHESES_RANK = [
    "relationship_history",
    "deal_origin_inbound",
    "pre_rfp_engagement",
    "requirement_coverage",
    "incumbency",
    "portfolio_similarity",
    "price_position_pct",
    "geo_timezone_fit",
    "ip_security_credentials",
    "competing_bidders",
    "effort_person_months",
    "client_segment",
    "project_type",
]

CAT_FEATURES = ["client_segment", "project_type", "incumbency"]
NUM_FEATURES = [
    "relationship_history",
    "deal_origin_inbound",
    "pre_rfp_engagement",
    "effort_person_months",
    "price_position_pct",
    "requirement_coverage",
    "portfolio_similarity",
    "geo_timezone_fit",
    "ip_security_credentials",
    "competing_bidders",
]
FEATURE_ORDER = NUM_FEATURES + CAT_FEATURES


def build_preprocessor():
    return ColumnTransformer(
        [
            ("num", SimpleImputer(strategy="median"), NUM_FEATURES),
            (
                "cat",
                Pipeline(
                    [
                        ("imp", SimpleImputer(strategy="most_frequent")),
                        ("ohe", OneHotEncoder(handle_unknown="ignore")),
                    ]
                ),
                CAT_FEATURES,
            ),
        ]
    )


def main():
    df = pd.read_csv(DATA_PATH)
    X = df[FEATURE_ORDER].copy()
    y = df["win"].copy()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, stratify=y, random_state=RANDOM_STATE
    )

    pre = build_preprocessor()
    X_train_t = pre.fit_transform(X_train)
    X_test_t = pre.transform(X_test)
    feature_names = list(pre.get_feature_names_out())

    model = GradientBoostingClassifier(
        n_estimators=100,
        learning_rate=0.04,
        max_depth=2,
        min_samples_leaf=20,
        subsample=0.8,
        random_state=RANDOM_STATE,
    )
    model.fit(X_train_t, y_train)

    # ---- Evaluation on held-out test set ----
    proba_test = model.predict_proba(X_test_t)[:, 1]
    pred_test = (proba_test >= 0.5).astype(int)

    auc = roc_auc_score(y_test, proba_test)
    brier = brier_score_loss(y_test, proba_test)
    cm = confusion_matrix(y_test, pred_test).tolist()  # [[TN, FP], [FN, TP]]
    fpr, tpr, _ = roc_curve(y_test, proba_test)
    roc_points = [
        {"fpr": round(float(f), 4), "tpr": round(float(t), 4)}
        for f, t in zip(fpr[::max(1, len(fpr) // 60)], tpr[::max(1, len(tpr) // 60)])
    ]

    # ---- Cross-validated AUC for a more stable headline number ----
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    cv_aucs = []
    X_full_t = None
    for tr_idx, va_idx in skf.split(X, y):
        pre_cv = build_preprocessor()
        Xtr = pre_cv.fit_transform(X.iloc[tr_idx])
        Xva = pre_cv.transform(X.iloc[va_idx])
        m = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.04,
            max_depth=2,
            min_samples_leaf=20,
            subsample=0.8,
            random_state=RANDOM_STATE,
        )
        m.fit(Xtr, y.iloc[tr_idx])
        p = m.predict_proba(Xva)[:, 1]
        cv_aucs.append(roc_auc_score(y.iloc[va_idx], p))

    # ---- Calibration bins (predicted vs observed win rate) ----
    cal_df = pd.DataFrame({"p": proba_test, "y": y_test.values})
    cal_df["bin"] = pd.qcut(cal_df["p"], q=5, duplicates="drop")
    calibration = (
        cal_df.groupby("bin", observed=True)
        .agg(predicted=("p", "mean"), observed=("y", "mean"), n=("y", "size"))
        .round(3)
        .reset_index(drop=True)
        .to_dict(orient="records")
    )

    # ---- SHAP: global importance on the FULL dataset (refit on all data for the
    #      explanation + scorer, since the thesis artifact is about explanation, not
    #      further held-out evaluation) ----
    pre_full = build_preprocessor()
    X_full_t = pre_full.fit_transform(X)
    full_feature_names = list(pre_full.get_feature_names_out())
    model_full = GradientBoostingClassifier(
        n_estimators=100,
        learning_rate=0.04,
        max_depth=2,
        min_samples_leaf=20,
        subsample=0.8,
        random_state=RANDOM_STATE,
    )
    model_full.fit(X_full_t, y)

    explainer = shap.TreeExplainer(model_full)
    shap_values = explainer.shap_values(X_full_t)

    mean_abs_shap = np.abs(shap_values).mean(axis=0)

    # Collapse one-hot columns back to their parent categorical feature for a
    # business-readable global ranking.
    def parent_feature(col_name):
        for cat in CAT_FEATURES:
            if col_name.startswith(f"cat__{cat}_"):
                return cat
        return col_name.replace("num__", "")

    importance_by_parent = {}
    for name, val in zip(full_feature_names, mean_abs_shap):
        parent = parent_feature(name)
        importance_by_parent[parent] = importance_by_parent.get(parent, 0.0) + float(val)

    global_importance = sorted(
        [{"feature": k, "mean_abs_shap": round(v, 4)} for k, v in importance_by_parent.items()],
        key=lambda r: -r["mean_abs_shap"],
    )

    shap_rank = [r["feature"] for r in global_importance]
    hypothesis_rank_map = {f: i + 1 for i, f in enumerate(BU_HYPOTHESES_RANK)}
    shap_rank_map = {f: i + 1 for i, f in enumerate(shap_rank)}

    comparison = []
    for feat in BU_HYPOTHESES_RANK:
        comparison.append(
            {
                "feature": feat,
                "bu_hypothesis_rank": hypothesis_rank_map[feat],
                "shap_rank": shap_rank_map.get(feat),
                "delta": (shap_rank_map.get(feat, 0) - hypothesis_rank_map[feat]),
            }
        )

    # Spearman rank correlation between BU hypothesis rank and SHAP rank
    ranks_a = [hypothesis_rank_map[f] for f in BU_HYPOTHESES_RANK]
    ranks_b = [shap_rank_map.get(f, len(BU_HYPOTHESES_RANK)) for f in BU_HYPOTHESES_RANK]
    spearman = pd.Series(ranks_a).corr(pd.Series(ranks_b), method="spearman")

    # ---- Per-bid explanations for a sample (for "example bids" in dashboard) ----
    sample_idx = list(X.sample(n=8, random_state=RANDOM_STATE).index)
    examples = []
    for idx in sample_idx:
        pos = X.index.get_loc(idx)
        row = X.loc[idx]
        row_shap = shap_values[pos]
        row_contribs = {}
        for name, val in zip(full_feature_names, row_shap):
            parent = parent_feature(name)
            row_contribs[parent] = row_contribs.get(parent, 0.0) + float(val)
        top_pos = sorted(row_contribs.items(), key=lambda kv: -kv[1])[:3]
        top_neg = sorted(row_contribs.items(), key=lambda kv: kv[1])[:3]

        def nn(v):  # NaN -> None, so every value round-trips through JSON cleanly
            return None if pd.isna(v) else v

        examples.append(
            {
                "client_segment": row["client_segment"],
                "project_type": row["project_type"],
                "win_probability": round(float(model_full.predict_proba(X_full_t[pos : pos + 1])[0, 1]), 3),
                "actual_outcome": "Won" if int(df.loc[idx, "win"]) == 1 else "Lost",
                "top_positive_factors": [{"feature": f, "contribution": round(v, 3)} for f, v in top_pos],
                "top_negative_factors": [{"feature": f, "contribution": round(v, 3)} for f, v in top_neg],
                "features": {
                    "relationship_history": int(row["relationship_history"]),
                    "deal_origin_inbound": int(row["deal_origin_inbound"]),
                    "pre_rfp_engagement": nn(row["pre_rfp_engagement"]) if pd.isna(row["pre_rfp_engagement"]) else int(row["pre_rfp_engagement"]),
                    "incumbency": row["incumbency"],
                    "effort_person_months": round(float(row["effort_person_months"]), 1),
                    "price_position_pct": round(float(row["price_position_pct"]), 1),
                    "requirement_coverage": nn(row["requirement_coverage"]) if pd.isna(row["requirement_coverage"]) else round(float(row["requirement_coverage"]), 2),
                    "portfolio_similarity": round(float(row["portfolio_similarity"]), 2),
                    "geo_timezone_fit": round(float(row["geo_timezone_fit"]), 2),
                    "ip_security_credentials": int(row["ip_security_credentials"]),
                    "competing_bidders": nn(row["competing_bidders"]) if pd.isna(row["competing_bidders"]) else int(row["competing_bidders"]),
                },
            }
        )

    # ---- Save model artifacts needed by the standalone scorer logic ----
    # Baseline (expected value) for the scorer's waterfall framing
    ev = explainer.expected_value
    base_value = float(np.ravel(ev)[0])

    # ---- Interactive scorer: logistic-regression surrogate ----
    # The dashboard's headline results (performance + SHAP) come from the GBM above.
    # For a browser-side interactive scorer we need a model whose decision function
    # can be evaluated client-side without porting a 100-tree ensemble. A logistic
    # regression trained on the SAME data gives an EXACT, honest linear decomposition
    # (coefficient x standardized value = that feature's log-odds contribution) --
    # nothing approximated, just a simpler, fully transparent model. Its own AUC is
    # reported in the dashboard so this simplification is never hidden.
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler

    num_imputer = SimpleImputer(strategy="median")
    X_num = num_imputer.fit_transform(X[NUM_FEATURES])
    scaler = StandardScaler()
    X_num_scaled = scaler.fit_transform(X_num)

    cat_imputer = SimpleImputer(strategy="most_frequent")
    X_cat_imp = cat_imputer.fit_transform(X[CAT_FEATURES])
    ohe = OneHotEncoder(handle_unknown="ignore", drop=None)
    X_cat_ohe = ohe.fit_transform(X_cat_imp).toarray()
    cat_feature_names = list(ohe.get_feature_names_out(CAT_FEATURES))

    X_lr = np.hstack([X_num_scaled, X_cat_ohe])
    lr_feature_names = NUM_FEATURES + cat_feature_names

    lr = LogisticRegression(max_iter=2000, C=1.0)
    lr.fit(X_lr, y)
    lr_proba = lr.predict_proba(X_lr)[:, 1]
    lr_auc = roc_auc_score(y, lr_proba)

    lr_skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    lr_cv_aucs = []
    for tr_idx, va_idx in lr_skf.split(X_lr, y):
        m = LogisticRegression(max_iter=2000, C=1.0)
        m.fit(X_lr[tr_idx], y.iloc[tr_idx])
        p = m.predict_proba(X_lr[va_idx])[:, 1]
        lr_cv_aucs.append(roc_auc_score(y.iloc[va_idx], p))

    scorer_model = {
        "intercept": float(lr.intercept_[0]),
        "num_features": NUM_FEATURES,
        "num_means": [float(v) for v in scaler.mean_],
        "num_scales": [float(v) for v in scaler.scale_],
        "num_coefs": [float(v) for v in lr.coef_[0][: len(NUM_FEATURES)]],
        "cat_features": CAT_FEATURES,
        "cat_categories": {
            cat: [str(v) for v in cats] for cat, cats in zip(CAT_FEATURES, ohe.categories_)
        },
        "cat_coefs": {
            name: float(coef)
            for name, coef in zip(cat_feature_names, lr.coef_[0][len(NUM_FEATURES) :])
        },
        "num_medians_for_defaults": [float(v) for v in num_imputer.statistics_],
        "cat_mode_for_defaults": {
            cat: str(cat_imputer.statistics_[i]) for i, cat in enumerate(CAT_FEATURES)
        },
        "auc_on_full_data": round(float(lr_auc), 3),
        "cv_auc_mean": round(float(np.mean(lr_cv_aucs)), 3),
        "cv_auc_std": round(float(np.std(lr_cv_aucs)), 3),
    }

    results = {
        "meta": {
            "n_rows": int(len(df)),
            "win_rate": round(float(y.mean()), 3),
            "model": "GradientBoostingClassifier (scikit-learn)",
            "n_train": int(len(X_train)),
            "n_test": int(len(X_test)),
            "random_state": RANDOM_STATE,
            "feature_order": FEATURE_ORDER,
            "cat_features": CAT_FEATURES,
            "num_features": NUM_FEATURES,
        },
        "performance": {
            "test_auc": round(float(auc), 3),
            "cv_auc_mean": round(float(np.mean(cv_aucs)), 3),
            "cv_auc_std": round(float(np.std(cv_aucs)), 3),
            "cv_auc_folds": [round(float(a), 3) for a in cv_aucs],
            "brier_score": round(float(brier), 4),
            "confusion_matrix": {"tn": cm[0][0], "fp": cm[0][1], "fn": cm[1][0], "tp": cm[1][1]},
            "roc_curve": roc_points,
            "calibration_bins": calibration,
        },
        "shap_global_importance": global_importance,
        "hypothesis_comparison": comparison,
        "spearman_rank_correlation": round(float(spearman), 3),
        "example_bids": examples,
        "scorer_base_value": base_value,
        "scorer_model": scorer_model,
    }

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump(results, f, indent=2)

    print(f"Wrote {OUT_PATH}")
    print(f"Test AUC: {auc:.3f} | 5-fold CV AUC: {np.mean(cv_aucs):.3f} (+/- {np.std(cv_aucs):.3f})")
    print(f"Brier score: {brier:.4f}")
    print(f"Spearman(BU hypothesis rank, SHAP rank) = {spearman:.3f}")
    print("\nTop 5 SHAP features:")
    for r in global_importance[:5]:
        print(f"  {r['feature']}: {r['mean_abs_shap']}")


if __name__ == "__main__":
    main()
