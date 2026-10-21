"""
Synthetic bid dataset generator — Virtuos Engineering BU bid competitiveness model
==================================================================================

PURPOSE
-------
Generate a realistic synthetic dataset of resolved (Won/Lost) game-development bids
for an end-to-end ML pipeline whose goal is to RECOVER known feature->outcome
relationships. The embedded relationships are NOT real findings — they are encoded
here, derived from the supervisor-reviewed feature hypotheses document. The pipeline's
job is to recover them; this validates the method, it does not discover what wins bids.

PROVENANCE OF WEIGHTS (important for the thesis)
-----------------------------------------------
No empirical survey results were available. Feature influence weights below are set
from the DOCUMENTED HYPOTHESES in the feature definition document (relative strength
and expected direction), not from the author's ad-hoc preference and not from real
practitioner data. This is stated as a limitation in methodology.md.

DESIGN PRINCIPLES (to avoid trivial circularity)
------------------------------------------------
1. Outcome is a NOISY logistic function of features, not a clean rule (label noise +
   latent Gaussian noise) -> model cannot hit ~100% accuracy.
2. Features are CORRELATED where reality demands (Effort<->Price, Relationship<->Pre-RFP).
3. INTERACTION effects exist (weak portfolio hurts new clients more; IP matters more
   for AAA/platform clients).
4. CLASS IMBALANCE: base win rate ~30%.
5. MISSING values injected in a few fields.
6. Marginals chosen to look like a real BU bid log.

OUTPUT
------
data/synthetic_bids.csv  (one row per bid)
Console diagnostics (win rate, AUC achievable, correlations).
"""

import os

import numpy as np
import pandas as pd

RNG = np.random.default_rng(42)
N = 500
TARGET_WIN_RATE = 0.30

# ----------------------------------------------------------------------------
# 1. CATEGORICAL FEATURE UNIVERSES + marginal probabilities (look like a real log)
# ----------------------------------------------------------------------------
CLIENT_SEGMENTS = ["AAA_publisher", "Midsize_publisher", "Indie_studio", "Platform_holder"]
CLIENT_SEG_P    = [0.30, 0.32, 0.28, 0.10]

PROJECT_TYPES   = ["Full_development", "Co_development", "Porting", "Live_ops", "Art_services"]
PROJECT_TYPE_P  = [0.18, 0.34, 0.20, 0.16, 0.12]

# Relationship History folds in Prior Delivery Outcome (ordinal, higher = better)
#   0 = New client, 1 = Prior but poor delivery, 2 = Prior neutral, 3 = Prior & went well
RELATIONSHIP_LEVELS = [0, 1, 2, 3]
RELATIONSHIP_P      = [0.45, 0.10, 0.22, 0.23]

# Incumbency: greenfield / defending our own work / displacing a competitor
INCUMBENCY = ["Greenfield", "Incumbent_defend", "Displacement"]
INCUMBENCY_P = [0.55, 0.22, 0.23]

def draw_categorical(levels, p, n):
    return RNG.choice(levels, size=n, p=p)

# ----------------------------------------------------------------------------
# 2. DRAW BASE FEATURES
# ----------------------------------------------------------------------------
client_segment = draw_categorical(CLIENT_SEGMENTS, CLIENT_SEG_P, N)
project_type   = draw_categorical(PROJECT_TYPES, PROJECT_TYPE_P, N)
relationship   = draw_categorical(RELATIONSHIP_LEVELS, RELATIONSHIP_P, N)
incumbency     = draw_categorical(INCUMBENCY, INCUMBENCY_P, N)

# Deal Origin: inbound more likely when there's a prior good relationship (correlation)
inbound_prob = 0.25 + 0.15 * (relationship >= 2)
deal_inbound = (RNG.random(N) < inbound_prob).astype(int)   # 1 = inbound

# Pre-RFP engagement: correlated with inbound AND relationship
prerfp_prob = 0.20 + 0.35 * deal_inbound + 0.10 * (relationship >= 2)
prerfp_prob = np.clip(prerfp_prob, 0, 0.9)
pre_rfp = (RNG.random(N) < prerfp_prob).astype(int)         # 1 = engaged before RFP

# Effort (person-months): lognormal, varies by project type
base_effort = {"Full_development": 180, "Co_development": 90, "Porting": 35,
               "Live_ops": 60, "Art_services": 40}
effort = np.array([RNG.lognormal(mean=np.log(base_effort[pt]), sigma=0.45)
                   for pt in project_type])
effort = np.round(effort, 1)

# Price Position: % deviation from benchmark. Correlated with effort (bigger jobs get
# discounted slightly) + noise. Negative = below benchmark (cheaper).
price_position = -0.04 * (np.log(effort) - np.log(80)) * 10 + RNG.normal(0, 9, N)
price_position = np.round(price_position, 1)

# Requirement Coverage: proportion of RFP requirements fully met (0.5–1.0), higher when
# relationship/pre-RFP engagement let us shape the spec.
req_cov = 0.72 + 0.05 * pre_rfp + 0.03 * (relationship >= 2) + RNG.normal(0, 0.09, N)
req_cov = np.clip(np.round(req_cov, 2), 0.45, 1.0)

# Portfolio Similarity: 0–1, mild lift for co-dev/porting (common, well-evidenced work)
port_base = np.where(np.isin(project_type, ["Co_development", "Porting"]), 0.58, 0.48)
portfolio_sim = np.clip(port_base + RNG.normal(0, 0.18, N), 0, 1).round(2)

# Geographic / Timezone Fit: 0–1 overlap fraction
geo_fit = np.clip(RNG.beta(5, 3, N), 0, 1).round(2)

# IP Security credentials present (1/0); more common when we chase AAA/platform
ip_prob = 0.35 + 0.25 * np.isin(client_segment, ["AAA_publisher", "Platform_holder"])
ip_security = (RNG.random(N) < ip_prob).astype(int)

# Competing Bidders: count. NOTE: flagged as possible leakage in real data (often only
# known post-hoc). Kept here for completeness; treat as analysis-only if reviewing real data.
competing_bidders = RNG.poisson(lam=3.2, size=N) + 1

# ----------------------------------------------------------------------------
# 3. LATENT WIN PROPENSITY (log-odds) — weights from hypothesis document
#    Direction and RELATIVE magnitude encode the documented hypotheses.
# ----------------------------------------------------------------------------
logit = np.zeros(N)

# Relationship (strong, per doc: repeat business easier to secure)
logit += np.select([relationship == 0, relationship == 1, relationship == 2, relationship == 3],
                   [-0.35, -0.55, 0.35, 0.95])   # prior-but-poor is WORSE than new (deliberate, noteworthy)

# Deal origin: inbound strongly favorable
logit += 0.75 * deal_inbound

# Pre-RFP engagement: strong (shaping the spec)
logit += 0.65 * pre_rfp

# Incumbency: defending easy-ish, displacement hard
logit += np.select([incumbency == "Greenfield", incumbency == "Incumbent_defend", incumbency == "Displacement"],
                   [0.0, 0.55, -0.60])

# Price position: overpricing hurts ~2.6x more than underpricing helps/hurts
logit += -0.045 * np.clip(price_position, 0, None) - 0.017 * np.clip(-price_position, 0, None)

# Requirement coverage (centered at 0.75)
logit += 2.4 * (req_cov - 0.75)

# Portfolio similarity (centered)
logit += 1.3 * (portfolio_sim - 0.5)

# Effort: very large engagements slightly harder to win
logit += -0.0012 * (effort - 90)

# Geo/timezone fit
logit += 0.9 * (geo_fit - 0.6)

# IP security — base small effect, big interaction below
logit += 0.20 * ip_security

# Competing bidders: more rivals -> lower odds
logit += -0.12 * (competing_bidders - 3)

# ---- INTERACTIONS (make it non-additive, more realistic & interesting) ----
# Weak portfolio hurts NEW clients far more than repeat clients
logit += -1.1 * ((relationship == 0) & (portfolio_sim < 0.45))
# IP security matters much more for AAA/platform clients
logit += 0.85 * (ip_security & np.isin(client_segment, ["AAA_publisher", "Platform_holder"]))
# Indies are more price-sensitive: extra penalty for overpricing them
logit += -0.03 * np.clip(price_position, 0, None) * (client_segment == "Indie_studio")

# ---- LATENT NOISE (so relationships are recoverable but not perfect) ----
logit += RNG.normal(0, 1.25, N)

# ----------------------------------------------------------------------------
# 4. CALIBRATE INTERCEPT TO HIT TARGET WIN RATE, then draw outcomes
# ----------------------------------------------------------------------------
def win_rate_for_intercept(c):
    p = 1 / (1 + np.exp(-(logit + c)))
    return p.mean()

lo, hi = -10, 10
for _ in range(60):
    mid = (lo + hi) / 2
    if win_rate_for_intercept(mid) < TARGET_WIN_RATE:
        lo = mid
    else:
        hi = mid
intercept = (lo + hi) / 2

p_win = 1 / (1 + np.exp(-(logit + intercept)))
win = (RNG.random(N) < p_win).astype(int)

# Label noise: flip ~5% of outcomes (real logs have mislabeled/odd results)
flip = RNG.random(N) < 0.05
win = np.where(flip, 1 - win, win)

# ----------------------------------------------------------------------------
# 5. ASSEMBLE DATAFRAME + inject missingness
# ----------------------------------------------------------------------------
df = pd.DataFrame({
    "client_segment": client_segment,
    "project_type": project_type,
    "relationship_history": relationship,          # 0=new,1=prior_poor,2=prior_neutral,3=prior_good
    "deal_origin_inbound": deal_inbound,           # 1=inbound,0=outbound
    "pre_rfp_engagement": pre_rfp,                 # 1=yes
    "incumbency": incumbency,
    "effort_person_months": effort,
    "price_position_pct": price_position,          # % dev from benchmark (+ = above)
    "requirement_coverage": req_cov,               # 0..1
    "portfolio_similarity": portfolio_sim,         # 0..1
    "geo_timezone_fit": geo_fit,                   # 0..1
    "ip_security_credentials": ip_security,        # 1=yes
    "competing_bidders": competing_bidders,        # count (leakage caveat)
    "win": win,                                    # TARGET: 1=Won,0=Lost
})

# Realistic missingness
for col, rate in [("pre_rfp_engagement", 0.06), ("requirement_coverage", 0.05),
                  ("competing_bidders", 0.08)]:
    mask = RNG.random(N) < rate
    df.loc[mask, col] = np.nan

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
df.to_csv(os.path.join(OUT_DIR, "synthetic_bids.csv"), index=False)

# ----------------------------------------------------------------------------
# 6. DIAGNOSTICS
# ----------------------------------------------------------------------------
print(f"Rows: {len(df)}")
print(f"Win rate: {df['win'].mean():.3f} (target {TARGET_WIN_RATE})")
print(f"Calibrated intercept: {intercept:.3f}")
print("\nWin rate by relationship level (0=new .. 3=prior_good):")
print(df.groupby('relationship_history')['win'].mean().round(3).to_string())
print("\nWin rate by deal origin (0=outbound,1=inbound):")
print(df.groupby('deal_origin_inbound')['win'].mean().round(3).to_string())
print("\nWin rate by incumbency:")
print(df.groupby('incumbency')['win'].mean().round(3).to_string())

# Best-achievable separation (ceiling check — should be good, not perfect)
try:
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import roc_auc_score
    from sklearn.model_selection import cross_val_predict
    from sklearn.pipeline import Pipeline
    from sklearn.compose import ColumnTransformer
    from sklearn.preprocessing import OneHotEncoder, StandardScaler
    from sklearn.impute import SimpleImputer

    X = df.drop(columns="win")
    y = df["win"]
    cat = ["client_segment", "project_type", "incumbency"]
    num = [c for c in X.columns if c not in cat]
    pre = ColumnTransformer([
        ("num", Pipeline([("imp", SimpleImputer(strategy="median")), ("sc", StandardScaler())]), num),
        ("cat", OneHotEncoder(handle_unknown="ignore"), cat),
    ])
    clf = Pipeline([("pre", pre), ("lr", LogisticRegression(max_iter=1000))])
    proba = cross_val_predict(clf, X, y, cv=5, method="predict_proba")[:, 1]
    print(f"\n5-fold CV AUC (logistic ceiling): {roc_auc_score(y, proba):.3f}")
    print("  -> expect ~0.75-0.85: strong but not perfect = healthy synthetic signal.")
except Exception as e:
    print(f"\n(Skipped AUC check: {e})")
