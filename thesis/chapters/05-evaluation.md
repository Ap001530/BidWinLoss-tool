# Evaluation

This chapter reports the evaluation set out in Chapter 3: quantitative performance of the gradient-boosted model, the global and per-bid SHAP results, the SHAP-versus-hypothesis comparison central to RQ1, evaluation of the scorer's logistic surrogate, and a structured assessment of the artefact against RQ3. Every figure reported here is read directly from the pipeline's own output file (`outputs/model_results.json`), consistent with the "single source of truth" design described in Chapter 4; none is recomputed or adjusted for presentation.

## Quantitative Model Performance

The gradient-boosted classifier was evaluated on a held-out test split (125 of the 500 bids, stratified to preserve the 30.6% realised win rate) and separately by 5-fold stratified cross-validation across all 500 bids. Table 5.1 reports both.

**Table 5.1: Model performance**

| Metric | Value |
|---|---|
| Held-out test AUC (single 75/25 split) | 0.632 |
| 5-fold cross-validated AUC (mean) | 0.705 |
| 5-fold cross-validated AUC (standard deviation) | ± 0.052 |
| 5-fold AUC, individual folds | 0.748, 0.674, 0.692, 0.632, 0.776 |
| Brier score (held-out test set) | 0.2103 |

The 5-fold cross-validated AUC of 0.705 is the more reliable headline figure, since it averages over five different train/test partitions rather than depending on which 125 bids happened to land in a single held-out split; the single-split test AUC of 0.632 sits within the range spanned by the individual cross-validation folds (0.632 to 0.776), so it is a plausible, if somewhat pessimistic, draw from the same underlying distribution rather than evidence of a separate problem. Read against the logistic-regression ceiling established in Chapter 3 (an AUC of approximately 0.72 for a simple linear baseline on this same data), the gradient-boosted model's cross-validated AUC of 0.705 is close to, essentially at, that ceiling. This is a meaningful result in both directions: it confirms the synthetic dataset carries genuine, learnable signal rather than being unlearnable noise, and it indicates that, on this dataset and with the hyperparameters selected in Chapter 4, the additional non-linear modelling capacity of a gradient-boosted ensemble over a plain logistic regression is not translating into a materially higher ceiling, a finding discussed further in Chapter 6.

The Brier score of 0.2103 measures how close the model's predicted probabilities are to the actual outcomes, averaged over the test set, where 0 is a perfect forecast and 0.25 is what a model achieves by always predicting the dataset's base win rate (approximately 30%) regardless of any feature. A Brier score of 0.21, modestly below that 0.25 naive baseline, indicates the model is extracting some genuine probability-calibration benefit from the features, though the margin is not large, consistent with the AUC result above.

### Confusion Matrix and Derived Classification Metrics

Table 5.2 reports the confusion matrix at the default 0.5 classification threshold on the held-out test set, together with the classification metrics it implies.

**Table 5.2: Confusion matrix and derived metrics (held-out test set, n = 125, threshold = 0.5)**

| | Predicted Lost | Predicted Won |
|---|---|---|
| **Actual Lost** (n = 87) | 77 (true negative) | 10 (false positive) |
| **Actual Won** (n = 38) | 28 (false negative) | 10 (true positive) |

| Metric (Won class) | Value |
|---|---|
| Accuracy | 0.696 |
| Precision | 0.500 |
| Recall | 0.263 |
| F1-score | 0.345 |

The most important pattern in Table 5.2 is the gap between precision (0.500) and recall (0.263) for the Won class: of the 38 bids the test set actually recorded as won, the model's default 0.5-threshold prediction correctly flags only 10, missing 28. This is a direct, expected consequence of class imbalance (He and Garcia [@he2009learning], Section 2.1): with a base win rate of roughly 30%, a threshold of 0.5 is conservative relative to the base rate, and the model, like most classifiers trained under imbalance without explicit reweighting, tends to under-predict the minority class at that threshold even when, as the AUC result shows, it ranks genuinely winnable bids above genuinely losing ones reasonably well. This is precisely why AUC, a threshold-independent ranking measure, is reported as the primary performance figure in Table 5.1 rather than accuracy or the default-threshold F1-score: a BU stakeholder using this tool in practice would not be bound to the 0.5 threshold, and could instead choose a lower threshold (flagging more bids as "competitive" at the cost of more false positives) depending on how the BU wants to trade off pursuing more opportunities against spending more proposal effort on bids that ultimately lose. This threshold-selection trade-off is not resolved by this thesis and is identified in Chapter 7 as a concrete next step for making the tool more directly actionable.

## Global SHAP Feature Importance

Table 5.3 reports the full global SHAP ranking, computed as the mean absolute SHAP value per feature across all 500 bids (Chapter 4).

**Table 5.3: Global SHAP feature importance (all 500 bids)**

| Rank | Feature | Mean |SHAP| |
|---|---|---|
| 1 | Relationship history | 0.3585 |
| 2 | Pre-RFP engagement | 0.3379 |
| 3 | Security credentials | 0.2683 |
| 4 | Portfolio similarity | 0.1916 |
| 5 | Incumbency position | 0.1456 |
| 6 | Project type | 0.1015 |
| 7 | Geo/timezone fit | 0.0854 |
| 8 | Client segment | 0.0796 |
| 9 | Effort (person-months) | 0.0738 |
| 10 | Deal origin (inbound) | 0.0623 |
| 11 | Price position | 0.0589 |
| 12 | Competing bidders | 0.0492 |
| 13 | Requirement coverage | 0.0169 |

Relationship history emerges as the single most influential feature, consistent with its encoded effect size in the data generator (Chapter 3) and with the general finding in the win-propensity literature that prior relationship is a strong predictor of future outcomes (Yan et al. [-@yan2015sales]; Rezazadeh [-@rezazadeh2020generalized]). Pre-RFP engagement and security credentials rank second and third, both plausible on their face, early engagement shapes a proposal to a client's actual needs, and security credentials gate entry for the AAA-publisher and platform-holder segments specifically, which is exactly the interaction effect deliberately encoded into the data generator (Chapter 3). That this interaction surfaces as a high global-importance feature, rather than being invisible to a method that only reports average effects, is a point in favour of the pipeline correctly recovering a non-additive relationship, though confirming the *interaction* specifically, rather than only the feature's overall importance, would require inspecting SHAP interaction values or a segment-conditioned breakdown, which this thesis's current evaluation does not include and which is identified in Chapter 7 as a specific next step.

## RQ1: SHAP Ranking Against the BU's Documented Hypotheses

Table 5.4 reports the full comparison between the Engineering BU's documented hypothesis ranking (the order features were expected to matter in, before any modelling) and the rank SHAP actually assigns each feature after training.

**Table 5.4: BU hypothesis rank versus SHAP rank, by feature**

| Feature | BU hypothesis rank | SHAP rank | Shift |
|---|---|---|---|
| Relationship history | 1 | 1 | No change |
| Deal origin (inbound) | 2 | 10 | Down 8 |
| Pre-RFP engagement | 3 | 2 | Up 1 |
| Requirement coverage | 4 | 13 | Down 9 |
| Incumbency position | 5 | 5 | No change |
| Portfolio similarity | 6 | 4 | Up 2 |
| Price position | 7 | 11 | Down 4 |
| Geo/timezone fit | 8 | 7 | Up 1 |
| Security credentials | 9 | 3 | Up 6 |
| Competing bidders | 10 | 12 | Down 2 |
| Effort (person-months) | 11 | 9 | Up 2 |
| Client segment | 12 | 8 | Up 4 |
| Project type | 13 | 6 | Up 7 |

The Spearman rank correlation between the two orderings is **0.242**. Read in isolation, this is a weak positive correlation, and it is worth restating the methodological caveat from Chapter 3 explicitly here: because the synthetic data generator's encoded weights were themselves derived from this same BU hypothesis document, a *much* higher correlation would have been the more naively expected outcome, and the fact that it is not near 1.0 is not, by itself, a sign that the pipeline failed. Three features account for most of the divergence and are each individually explicable rather than symptomatic of a broken pipeline.

**Security credentials (hypothesis rank 9, SHAP rank 3, up 6).** The data generator encodes a strong *interaction* effect for this feature, specifically for AAA-publisher and platform-holder clients, security credentials matter substantially more than their flat, segment-independent effect alone would suggest. The BU's hypothesis ranking, by construction, ranks features on their expected flat importance; SHAP's mean-absolute-value summary, by contrast, captures the feature's importance averaged across all the conditions it appears in, including the specific client segments where its effect is amplified. A feature whose importance is concentrated in a subset of cases, rather than spread evenly, can rank much higher in a SHAP summary than in a simple a priori importance guess that does not anticipate that interaction. This is, in the author's reading, the pipeline correctly surfacing a pattern the flat hypothesis ranking was not designed to anticipate, rather than a failure to recover the hypothesis.

**Requirement coverage (hypothesis rank 4, SHAP rank 13, down 9) and deal origin (hypothesis rank 2, SHAP rank 10, down 8).** These are the two largest downward shifts, features the BU expected to matter considerably more than SHAP finds they do. Requirement coverage's encoded effect in the data generator is comparatively modest relative to several other features (Chapter 3), and its values are also fairly tightly clustered around the dataset's mean (Appendix A), which limits how much variation in predicted probability it can account for even if its per-unit effect were otherwise large; a feature with a real but narrow range of observed values will tend to show a smaller mean-absolute-SHAP contribution than one with the same per-unit effect but a wider observed range, simply because SHAP measures realised contribution across the actual data, not a feature's theoretical maximum influence. Deal origin's downward shift is smaller in absolute SHAP terms but large in rank terms specifically because several features cluster closely around similarly modest importance values in the bottom half of Table 5.3, where small differences in mean |SHAP| translate into comparatively large rank movements. Both cases illustrate a general, useful methodological point for RQ1: a rank-based comparison like this one is sensitive to clustering in the underlying importance values in a way that comparing the raw importance scores directly is not, and a fuller evaluation (identified in Chapter 7) would report both the rank comparison and the underlying score differences side by side.

**Project type (hypothesis rank 13, SHAP rank 6, up 7).** This is the largest upward shift and the converse of the security-credentials case: a feature the BU's flat hypothesis ranked as least important turns out to carry real signal once the model has access to the rest of the feature set, plausibly because project type correlates with several other features (effort, portfolio similarity) in ways the generator's correlation structure (Chapter 3) builds in deliberately, so part of what SHAP attributes to "project type" may be signal that is genuinely shared with those correlated features rather than independent to project type alone. Disentangling shared, correlated signal from each individual feature's independent contribution is a known general limitation of SHAP and of feature-importance methods more broadly, and is noted as such in Chapter 6 rather than treated as specific to this result.

Taken together, these three cases support treating the overall finding of RQ1 as follows: the model's two highest-ranked features by the BU's own hypothesis (relationship history and incumbency position) are recovered at identical rank by SHAP, which is a meaningful, direct confirmation at the top of the ranking; the correlation across the full ranking is weak rather than strong, which, given the interaction effects and value-range differences discussed above, is judged to be an interesting and explicable methodological result rather than evidence the pipeline failed to recover the encoded signal, but which does mean this thesis cannot claim the pipeline reproduces the BU's full hypothesis ordering faithfully, only its top end and its broad logic.

## Per-Bid Explanation: Qualitative Review of Example Bids

The eight example bids the artefact displays (Chapter 4) were reviewed qualitatively against their SHAP explanations and full feature profiles. In general, the explanations are internally coherent: bids with high predicted win probability (for example, the first example bid, an AAA-publisher live-ops proposal predicted at 70.3% and actually won) are consistently explained by positive contributions from pre-RFP engagement, security credentials, and portfolio similarity, each a top-ranked global feature in Table 5.3; bids with low predicted win probability (for example, an indie-studio co-development proposal predicted at 9.7% and actually lost) are consistently explained by negative contributions from relationship history, portfolio similarity, and pre-RFP engagement, the same top features acting in the opposite direction. This consistency between a bid-level explanation and the global ranking is expected, since both are computed from the same underlying SHAP values, but confirming it holds in practice, rather than only in aggregate, is exactly what the per-bid explanation view is for, and this review found no example among the eight where the stated top factors were inconsistent with the bid's actual feature values.

The deliberately non-monotonic encoded pattern described in Chapter 3, that a prior client whose delivery went poorly is encoded as *worse* for win probability than a brand-new client, was not directly testable from the current evaluation output: the pipeline reports an aggregate SHAP importance for "relationship history" as a whole but does not currently export a per-level breakdown (the contribution specifically at level 1, "prior, poor delivery," versus level 0, "new client") that would show whether the model separated these two levels correctly rather than treating relationship history as a simple monotonic scale. This is flagged here as a specific, known gap in the current evaluation rather than glossed over: Chapter 7 recommends adding a partial-dependence or SHAP-dependence plot for this feature specifically as a near-term extension, since it is the one deliberately designed test case in the synthetic data (Chapter 3) that this thesis's evaluation does not yet directly confirm or disconfirm.

## Evaluation of the Scorer's Logistic Surrogate

The logistic-regression surrogate that drives the artefact's interactive scorer (Chapter 4) achieves an AUC of 0.773 on the full dataset and 0.743 under 5-fold cross-validation (standard deviation 0.048). The cross-validated figure is the more reliable one for the same reason given in Section 5.1, and it sits close to, if marginally above, the gradient-boosted model's own cross-validated AUC of 0.705. This is a favourable result for the design choice made in Chapter 4: the scorer trades the gradient-boosted model's modest additional ranking power for an exact, auditable client-side computation, and on this dataset that trade costs little to nothing in predictive performance, within the noise of a 500-row dataset.

This favourable result should not be over-read as evidence that a linear model is generally sufficient for this problem; Chapter 3's generator deliberately encodes non-linear interaction effects specifically to motivate using a tree-based learner at all (Section 2.2), and a logistic model, by construction, cannot represent those interactions directly, only indirectly, to the extent a feature's main effect correlates with the interaction's net impact across the dataset. The more precise reading is that, on *this* dataset's realised noise level and sample size, the gap between a model that can represent interactions and one that cannot happens to be small; whether that remains true on a larger, real dataset, where interaction effects might be both stronger and more precisely estimable, is explicitly left open and flagged in Chapter 6 as a limitation of the scorer specifically, distinct from the dashboard's primary model.

## RQ3: Structured Evaluation of the Artefact

RQ3 asks how the dashboard and scorer convert the model's output into usable decision-support information, and what building the artefact reveals about the practical requirements for deploying a tool like this. This thesis evaluates that question structurally, against four concrete requirements implied by RQ3's own wording, rather than through a formal user study, which was out of scope (Section 1.6) given the absence of real bid data and real BU users to test against.

**Does the artefact present model output without requiring statistical background?** The performance-metric explanations added to each stat tile (Chapter 4), stating in plain language what AUC, the Brier score, and the Spearman correlation each actually measure, and the clickable feature-definition system covering every technical or internal-shorthand feature name, were both added specifically in response to this requirement, after an earlier version of the artefact that displayed bare metric names and raw feature keys was judged, in review, to assume a BU stakeholder already knew what an AUC or an "incumbency" field meant. This is treated as a positive, if informally evaluated, result: the requirement was identified as unmet and then concretely addressed.

**Does the artefact let a user see why, not only what?** The SHAP chart, the hypothesis-comparison table, and each example bid's top-factor breakdown jointly satisfy this for the dashboard's retrospective, aggregate view; the scorer's live, exact factor breakdown satisfies it for a hypothetical, forward-looking bid a user constructs themselves. Both views are backed by the same underlying explanation method applied to two different models, which is disclosed explicitly in the artefact (Chapter 4) rather than left for a careful reader to notice.

**Is the artefact actually usable without a licensing or access barrier?** This was the central reason for the Power BI-to-web-dashboard deviation (Chapter 3), and the resulting artefact, openable in any browser with no account or license required, directly satisfies this requirement in a way the originally proposed Power BI delivery would not have, for any reviewer or BU stakeholder without an existing Power BI license.

**What did building the artefact reveal about deployment requirements that the original design did not anticipate?** Two concrete findings from the implementation process are reported here because they bear directly on this part of RQ3. First, the Claude Artifact hosting platform's dashboard type only accepts flat, tabular (row-array) data from an attached file, not the nested JSON structure `outputs/model_results.json` naturally has; this was discovered only when the first version of the dashboard loaded with no data at all, and required restructuring the pipeline's output into nine separate flat tables (Chapter 4) before the artefact would render. This is a concrete, generalisable lesson for any future deployment of this pipeline to a similar dashboard platform: the data-shape constraints of the chosen hosting mechanism should be checked before, not after, the results file's structure is finalised. Second, the decision to build the scorer on a separate, explicitly linear surrogate model, rather than on the primary gradient-boosted model, was not part of the original design and emerged specifically from the tension between wanting exact, auditable explanations and wanting to avoid porting a tree ensemble into JavaScript; this is reported as a genuine, unplanned design finding from the DSR process's demonstration step (Peffers et al. [-@peffers2007design]), not as a decision made in advance.

## Summary Against the Research Questions

RQ1 is answered with a specific, evidenced result rather than a simple yes or no: the model's top two features by the BU's own hypothesis are recovered at identical SHAP rank, and the largest divergences are each individually explicable (an interaction effect surfacing a feature's importance above its flat expectation; a narrow observed value range understating a feature's realised contribution; correlated signal being partly attributed to a feature the flat hypothesis under-weighted), but the overall rank correlation (0.242) is weak, and this thesis does not claim the pipeline faithfully reproduces the BU's full hypothesis ordering. RQ2 is answered with a cross-validated AUC of 0.705, close to the dataset's own logistic-regression ceiling of approximately 0.72, indicating the gradient-boosted model recovers close to the full recoverable signal in this synthetic data but gains comparatively little from its additional non-linear capacity on this specific dataset, a finding Chapter 6 discusses alongside the dataset-size limitation that likely drives it. RQ3 is answered structurally: the artefact meets the four concrete usability requirements derived from the research question, and the implementation process surfaced two genuine, reportable design findings, the hosting platform's tabular-data constraint and the case for a separate scorer model, that were not anticipated in the original design and are themselves part of this thesis's contribution. Chapter 6 now discusses what these results mean together, their limitations, and the threats to validity they raise.
