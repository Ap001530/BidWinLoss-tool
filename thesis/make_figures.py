"""
Generates thesis figures directly from outputs/model_results.json, so every
plotted number traces back to the same pipeline run the thesis text cites.
No figure here is illustrative or invented; each is a direct rendering of a
field in that file.
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures")
os.makedirs(OUT, exist_ok=True)

r = json.load(open(os.path.join(ROOT, "outputs", "model_results.json")))

plt.rcParams.update({
    "font.family": "serif",
    "font.size": 11,
    "axes.edgecolor": "#444444",
    "axes.labelcolor": "#222222",
    "text.color": "#222222",
    "xtick.color": "#333333",
    "ytick.color": "#333333",
})

ACCENT = "#b5692a"
MUTED = "#8a8275"
GRID = "#e4ddd0"

# ---------------------------------------------------------------------------
# Figure 5.1: ROC curve
# ---------------------------------------------------------------------------
roc = sorted(r["performance"]["roc_curve"], key=lambda d: (d["fpr"], d["tpr"]))
fpr = [d["fpr"] for d in roc]
tpr = [d["tpr"] for d in roc]

fig, ax = plt.subplots(figsize=(5.5, 5))
ax.plot([0, 1], [0, 1], linestyle="--", color=GRID, linewidth=1.2, label="Random classifier")
ax.plot(fpr, tpr, color=ACCENT, linewidth=2.2, label="Gradient-boosted model")
ax.set_xlabel("False positive rate")
ax.set_ylabel("True positive rate")
ax.set_title(f"ROC curve, held-out test set (AUC = {r['performance']['test_auc']:.3f})")
ax.set_xlim(-0.02, 1.02)
ax.set_ylim(-0.02, 1.02)
ax.legend(loc="lower right", frameon=False)
ax.grid(color=GRID, linewidth=0.6)
ax.set_axisbelow(True)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "fig5-1-roc-curve.png"), dpi=200)
plt.close(fig)

# ---------------------------------------------------------------------------
# Figure 5.2: Global SHAP importance
# ---------------------------------------------------------------------------
LABELS = {
    "relationship_history": "Relationship history",
    "pre_rfp_engagement": "Pre-RFP engagement",
    "ip_security_credentials": "Security credentials",
    "portfolio_similarity": "Portfolio similarity",
    "incumbency": "Incumbency position",
    "project_type": "Project type",
    "geo_timezone_fit": "Geo/timezone fit",
    "client_segment": "Client segment",
    "effort_person_months": "Effort (person-months)",
    "deal_origin_inbound": "Deal origin (inbound)",
    "price_position_pct": "Price position",
    "competing_bidders": "Competing bidders",
    "requirement_coverage": "Requirement coverage",
}
shap_rows = sorted(r["shap_global_importance"], key=lambda d: d["mean_abs_shap"])
feat_names = [LABELS.get(d["feature"], d["feature"]) for d in shap_rows]
feat_vals = [d["mean_abs_shap"] for d in shap_rows]

fig, ax = plt.subplots(figsize=(7, 5.5))
bars = ax.barh(feat_names, feat_vals, color=ACCENT, height=0.65)
ax.set_xlabel("Mean |SHAP value|")
ax.set_title("Global SHAP feature importance (all 500 bids)")
ax.grid(axis="x", color=GRID, linewidth=0.6)
ax.set_axisbelow(True)
for spine in ["top", "right"]:
    ax.spines[spine].set_visible(False)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "fig5-2-shap-importance.png"), dpi=200)
plt.close(fig)

# ---------------------------------------------------------------------------
# Figure 5.3: Confusion matrix heatmap
# ---------------------------------------------------------------------------
cm = r["performance"]["confusion_matrix"]
matrix = [[cm["tn"], cm["fp"]], [cm["fn"], cm["tp"]]]

fig, ax = plt.subplots(figsize=(4.5, 4.2))
im = ax.imshow(matrix, cmap="Oranges", vmin=0, vmax=max(max(row) for row in matrix))
ax.set_xticks([0, 1])
ax.set_yticks([0, 1])
ax.set_xticklabels(["Predicted Lost", "Predicted Won"])
ax.set_yticklabels(["Actual Lost", "Actual Won"])
for i in range(2):
    for j in range(2):
        ax.text(j, i, str(matrix[i][j]), ha="center", va="center",
                fontsize=16, color="#222222" if matrix[i][j] < 50 else "white")
ax.set_title("Confusion matrix, held-out test set\n(threshold = 0.5, n = 125)")
fig.tight_layout()
fig.savefig(os.path.join(OUT, "fig5-3-confusion-matrix.png"), dpi=200)
plt.close(fig)

# ---------------------------------------------------------------------------
# Figure 4.1: Pipeline architecture diagram (schematic, hand-drawn boxes)
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(9, 3.4))
ax.set_xlim(0, 10)
ax.set_ylim(0, 3)
ax.axis("off")

stages = [
    ("Synthetic data\ngenerator", "data/generate_\nsynthetic_bids.py"),
    ("Model training\n+ SHAP", "src/train_\nmodel.py"),
    ("Results\nflattening", "dashboard/make_\ntables.py"),
    ("Dashboard\n+ scorer", "index.html\n(Artifact / Pages)"),
]
box_w, box_h = 1.9, 1.5
gap = 0.55
x = 0.3
for i, (title, sub) in enumerate(stages):
    box = FancyBboxPatch((x, 0.75), box_w, box_h, boxstyle="round,pad=0.06,rounding_size=0.08",
                          linewidth=1.3, edgecolor="#444444", facecolor="#fbeedb" if i % 2 == 0 else "#ffffff")
    ax.add_patch(box)
    ax.text(x + box_w / 2, 0.75 + box_h * 0.66, title, ha="center", va="center", fontsize=10.5, fontweight="bold")
    ax.text(x + box_w / 2, 0.75 + box_h * 0.28, sub, ha="center", va="center", fontsize=8.5, color=MUTED, family="monospace")
    if i < len(stages) - 1:
        arrow = FancyArrowPatch((x + box_w + 0.03, 0.75 + box_h / 2),
                                (x + box_w + gap - 0.03, 0.75 + box_h / 2),
                                arrowstyle="-|>", mutation_scale=16, color=ACCENT, linewidth=1.6)
        ax.add_patch(arrow)
    x += box_w + gap

ax.text(5, 0.25, "Each stage reads only the previous stage's output file; outputs/model_results.json is the single\n"
                  "source of truth every dashboard figure and this thesis's Chapter 5 numbers are read from.",
        ha="center", va="center", fontsize=8.5, color=MUTED, style="italic")
fig.tight_layout()
fig.savefig(os.path.join(OUT, "fig4-1-pipeline-architecture.png"), dpi=200)
plt.close(fig)

print("Wrote figures to", OUT)
for f in sorted(os.listdir(OUT)):
    print(" -", f)
