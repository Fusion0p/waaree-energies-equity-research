"""
04_monte_carlo.py
==================
Monte Carlo simulation on the Waaree Energies DCF built in Part II /
the Excel model. Instead of a single point estimate, this randomizes the
key uncertain drivers 20,000 times and produces a full distribution of
intrinsic value per share.

Randomized inputs (all independent, chosen to reflect genuine uncertainty
ranges discussed in Part I/II, not arbitrary):
  - Revenue growth path (FY27E-FY31E)   : each year ~ Normal(base, sd), floored at 0
  - EBITDA margin path (FY27E-FY31E)    : each year ~ Normal(base, sd), clipped [10%, 30%]
  - Capex % of revenue (FY27E-FY31E)    : ~ Normal(base, sd), floored at 2%
  - Δ NWC % of Δ revenue (FY27E-FY31E)  : ~ Normal(base, sd), floored at 0
  - WACC                                : ~ Normal(13.8%, 1.0%), floored at 8%
  - Terminal growth rate (g)            : ~ Normal(5.0%, 1.0%), clipped [1%, WACC-0.5%]

No internet required — pure numpy simulation.

Usage:
    python 04_monte_carlo.py
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(__file__)
OUT_DIR = os.path.join(HERE, "output")
os.makedirs(OUT_DIR, exist_ok=True)

np.random.seed(42)
N = 20000

# ---- Base case (Part II) ----
REV0 = 26537.0
growth_base = np.array([0.35, 0.25, 0.20, 0.15, 0.12])
growth_sd   = np.array([0.08, 0.08, 0.07, 0.06, 0.05])

margin_base = np.array([0.200, 0.205, 0.210, 0.215, 0.220])
margin_sd   = np.array([0.020, 0.020, 0.020, 0.020, 0.020])

da_pct = np.array([0.045, 0.045, 0.043, 0.040, 0.038])   # held fixed — mechanical, low uncertainty

capex_base = np.array([0.080, 0.070, 0.060, 0.050, 0.045])
capex_sd   = np.array([0.015, 0.015, 0.012, 0.010, 0.010])

nwc_base = np.array([0.15, 0.14, 0.12, 0.10, 0.10])
nwc_sd   = np.array([0.04, 0.04, 0.03, 0.03, 0.03])

tax = 0.25
net_debt = 2260.0
shares = 30.1

# ---- Draw random inputs ----
growth = np.clip(np.random.normal(growth_base, growth_sd, size=(N, 5)), -0.05, None)
margin = np.clip(np.random.normal(margin_base, margin_sd, size=(N, 5)), 0.10, 0.30)
capex_pct = np.clip(np.random.normal(capex_base, capex_sd, size=(N, 5)), 0.02, None)
nwc_pct = np.clip(np.random.normal(nwc_base, nwc_sd, size=(N, 5)), 0.0, None)
wacc = np.clip(np.random.normal(0.138, 0.010, size=N), 0.08, None)
g = np.clip(np.random.normal(0.050, 0.010, size=N), 0.01, None)
g = np.minimum(g, wacc - 0.005)   # enforce WACC > g always

# ---- Build revenue path ----
revenue = np.zeros((N, 5))
prev = np.full(N, REV0)
for t in range(5):
    prev = prev * (1 + growth[:, t])
    revenue[:, t] = prev

ebitda = revenue * margin
da = revenue * da_pct
ebit = ebitda - da
nopat = ebit * (1 - tax)
capex = revenue * capex_pct

delta_rev = np.diff(np.hstack([np.full((N, 1), REV0), revenue]), axis=1)
nwc_inv = delta_rev * nwc_pct

fcff = nopat + da - capex - nwc_inv  # shape (N, 5)

# ---- Discount ----
periods = np.arange(1, 6)
disc = 1 / (1 + wacc[:, None]) ** periods[None, :]
pv_fcff = (fcff * disc).sum(axis=1)

tv = fcff[:, -1] * (1 + g) / (wacc - g)
pv_tv = tv * disc[:, -1]

ev = pv_fcff + pv_tv
equity_value = ev - net_debt
value_per_share = equity_value / shares

# ---- Results ----
CMP = 2886.0
p = np.percentile(value_per_share, [5, 10, 25, 50, 75, 90, 95])
prob_above_cmp = (value_per_share > CMP).mean()

print("=" * 60)
print("MONTE CARLO DCF — WAAREE ENERGIES (N = {:,} simulations)".format(N))
print("=" * 60)
print(f"Mean intrinsic value/share      : Rs {value_per_share.mean():,.0f}")
print(f"Median intrinsic value/share    : Rs {np.median(value_per_share):,.0f}")
print(f"Std deviation                   : Rs {value_per_share.std():,.0f}")
print()
print("Percentiles:")
for pct, val in zip([5, 10, 25, 50, 75, 90, 95], p):
    print(f"  P{pct:<3}: Rs {val:,.0f}")
print()
print(f"CMP (late Jun 2026)              : Rs {CMP:,.0f}")
print(f"P(intrinsic value > CMP)         : {prob_above_cmp*100:.1f}%")
print(f"P(intrinsic value < CMP)         : {(1-prob_above_cmp)*100:.1f}%")

# ---- Sensitivity: correlation of each input with output (simple driver ranking) ----
drivers = {
    "WACC": wacc,
    "Terminal growth (g)": g,
    "Avg revenue growth (FY27-31)": growth.mean(axis=1),
    "Avg EBITDA margin (FY27-31)": margin.mean(axis=1),
    "Avg Capex % (FY27-31)": capex_pct.mean(axis=1),
    "Avg ΔNWC % (FY27-31)": nwc_pct.mean(axis=1),
}
corrs = {k: np.corrcoef(v, value_per_share)[0, 1] for k, v in drivers.items()}
corrs_sorted = dict(sorted(corrs.items(), key=lambda x: abs(x[1]), reverse=True))
print("\nDriver sensitivity (correlation with intrinsic value/share):")
for k, v in corrs_sorted.items():
    print(f"  {k:<32s}: {v:+.2f}")

# ---- Charts ----
fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))
fig.suptitle("Waaree Energies — Monte Carlo DCF (20,000 simulations)", fontsize=13, fontweight="bold", color="#1F2A44")

ax = axes[0]
ax.hist(value_per_share, bins=100, color="#1F2A44", alpha=0.85)
ax.axvline(CMP, color="#A32424", linewidth=2, linestyle="--", label=f"CMP = Rs{CMP:,.0f}")
ax.axvline(np.median(value_per_share), color="#B08D57", linewidth=2, label=f"Median = Rs{np.median(value_per_share):,.0f}")
ax.set_title("Distribution of Intrinsic Value per Share")
ax.set_xlabel("Rs per share")
ax.set_ylabel("Frequency")
ax.legend()

ax = axes[1]
labels = list(corrs_sorted.keys())
vals = list(corrs_sorted.values())
colors = ["#1E6B3C" if v > 0 else "#A32424" for v in vals]
ax.barh(labels, vals, color=colors)
ax.axvline(0, color="black", linewidth=0.8)
ax.set_title("Driver Sensitivity (correlation to value/share)")
ax.set_xlabel("Correlation coefficient")

plt.tight_layout(rect=[0, 0, 1, 0.94])
chart_path = os.path.join(OUT_DIR, "monte_carlo.png")
plt.savefig(chart_path, dpi=150)
plt.close()
print(f"\nSaved chart -> {chart_path}")

# Save raw results for the Excel export step
np.save(os.path.join(OUT_DIR, "mc_value_per_share.npy"), value_per_share)
import json
summary = {
    "n_simulations": N,
    "mean": float(value_per_share.mean()),
    "median": float(np.median(value_per_share)),
    "std": float(value_per_share.std()),
    "percentiles": {str(k): float(v) for k, v in zip([5,10,25,50,75,90,95], p)},
    "prob_above_cmp": float(prob_above_cmp),
    "cmp": CMP,
    "driver_sensitivity": {k: float(v) for k, v in corrs_sorted.items()},
}
with open(os.path.join(OUT_DIR, "mc_summary.json"), "w") as f:
    json.dump(summary, f, indent=2)
print(f"Saved summary -> {os.path.join(OUT_DIR, 'mc_summary.json')}")
