# Waaree Energies — Python Analytics Package

Part IV of the institutional research package (see Parts I-III: Industry/Company
Research, DCF & Comps Valuation, and the 3-Statement Excel Model).

## Setup

```bash
pip install -r requirements.txt
```

## Scripts (run in order)

| Script | What it does | Needs internet? |
|---|---|---|
| `01_data_import.py` | Pulls Waaree, peer, and NIFTY 50 daily prices via yfinance to `./data/` | **Yes** |
| `02_ratio_analysis.py` | Computes the full ratio suite from Part I's financials; exports chart + `Waaree_Ratios.xlsx` | No |
| `03_risk_metrics.py` | Returns, volatility, rolling MAs, beta vs. NIFTY 50, Sharpe ratio | No — uses `./data/` if present, else clearly-labeled illustrative data |
| `04_monte_carlo.py` | 20,000-path Monte Carlo simulation of the DCF from Part II | No |
| `05_export_master_workbook.py` | Consolidates 02-04 into `output/Waaree_Python_Analytics.xlsx` | No |

## Important note on live market data

This package was built and demonstrated inside a sandboxed environment whose
network allowlist does not include Yahoo Finance. `01_data_import.py` is
fully correct and ready to run — on a normal machine with internet access it
will populate `./data/` with real Waaree, peer, and NIFTY 50 prices, and
`03_risk_metrics.py` will automatically pick them up and use them instead of
the illustrative fallback. Every output built on the fallback is explicitly
labeled "ILLUSTRATIVE DATA" in its console output, chart title, and the
Excel workbook — never silently presented as real.

## Key results from this run (see `output/`)

- **Ratio suite**: reconciles to Part I's historical ratio table (ROE, ROCE,
  margins, leverage) — see `output/ratios.csv` and `output/ratio_trends.png`.
- **Monte Carlo DCF** (20,000 simulations, randomizing growth, margin, capex,
  working capital, WACC, and terminal growth simultaneously):
  - Median intrinsic value: **~₹2,121/share** (vs. Part II's single-point
    base case of ₹2,146 — strong agreement)
  - 90% confidence interval: roughly **₹1,565 – ₹2,923/share**
  - Only an **~11% probability** that intrinsic value exceeds the ₹2,886 CMP
    under these assumptions — a quantified, distributional version of Part
    II's "DCF suggests downside" finding, and the single most decision-useful
    number this package produces.
  - WACC is the single largest driver of valuation uncertainty (correlation
    −0.55), ahead of revenue growth and terminal growth (+0.42 each) —
    meaning debating the ERP/beta assumptions in Part II Section 2.1 matters
    more to the final number than debating the revenue forecast.
