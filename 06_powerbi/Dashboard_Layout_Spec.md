# Waaree Energies — Power BI Dashboard: Layout Specification

Part VI of the institutional research package. Build this as a 3-page
Power BI report on top of `Waaree_PowerBI_DataModel.xlsx` + `DAX_Measures.md`.
A working visual preview of Page 1 is in `Waaree_Dashboard_Preview.html`.

## Page 1 — Executive Overview

**Top strip — 6 KPI cards** (Card visual, one measure each):
`Total Revenue` | `EBITDA Margin %` | `Net Profit` | `EPS (Rs)` | `ROE %` | `Debt to Equity`
Each card: main number + a small YoY delta using the built-in "trend" indicator.

**Row 2, left (60% width) — Revenue & EBITDA Trend**
Clustered column + line combo chart: `Total Revenue` (columns) and
`EBITDA Margin %` (line, secondary axis) by `Dim_FiscalYear[fiscal_year]`
(sorted by fy_order). This is the single most important chart in the
deck — it's the visual for the "operating leverage" story from Part I.

**Row 2, right (40% width) — Free Cash Flow Waterfall**
Waterfall or column chart of `Free Cash Flow` by fiscal year, colored
red/green by sign. Add a text callout box: "FY26 CFO/EBITDA fell to 47%"
(static text box, since this is the flagged analytical finding).

**Row 3, left — ROE vs ROCE**
Line chart, two series (`ROE %`, `ROCE %`) by fiscal year.

**Row 3, right — Leverage Trend**
Column chart of `Debt to Equity` by fiscal year, with a reference line
at a chosen comfort threshold (e.g., 0.5x) using an Analytics pane
constant line.

**Slicers (top of page, applies to whole page)**:
- Fiscal Year (multi-select, from `Dim_FiscalYear[fiscal_year]`)
- Company (single-select, from `Dim_Company[name]`, default = Waaree)

## Page 2 — Valuation & Peer Comparison

**Left — DCF Sensitivity Heatmap**
Matrix visual: rows = `Fact_DCFScenarios[wacc]` (filtered to `scenario_type
= "Sensitivity Grid"`), columns = `terminal_growth`, values =
`intrinsic_value_per_share`, with conditional-formatting color scale
(red low → green high). This directly reproduces the Excel Sensitivity
tab and Part II Section 2.4's table as an interactive Power BI visual.

**Right, top — Monte Carlo Percentile Bar**
Bar chart: `Fact_DCFScenarios[scenario_label]` (P5, P10, P25, P50, P75,
P90, P95) vs. `intrinsic_value_per_share`, with a constant reference
line at CMP (₹2,886) via the Analytics pane. Color bars red if below
CMP, green if above (conditional formatting rule).

**Right, bottom — Peer Multiple Comparison**
Clustered bar chart: `Dim_Company[name]` vs. `pe_ratio` and `ev_ebitda`
(two measures), filtered to the peer_snapshot table. Include a text box
noting the mixed data-vintage caveat from Part II Section 3.1.

**Bottom strip — KPI cards**: `Base Case Intrinsic Value`, `CMP`,
`Upside Downside %`, `Monte Carlo Median`, `Probability Value Exceeds CMP`.

## Page 3 — Forecast & Cash Flow Detail

**Top — Revenue: Actual vs. Forecast**
Column chart, `Dim_FiscalYear[fiscal_year]` on the axis, with two
measures (`Revenue (Actual Only)`, `Revenue (Forecast Only)`) stacked,
colored differently (navy for actual, gold for forecast) so the FY26/FY27E
boundary is visually obvious.

**Middle-left — Working Capital Days**
Line chart: `Debtor Days`, `Inventory Days`, `Payable Days` by fiscal
year — the chart that visualizes the FY26 cash-conversion-cycle stress.

**Middle-right — Cash Conversion Cycle**
Column chart: `Cash Conversion Cycle (days)` by fiscal year, single
series, with a data label callout on FY26 (the 90-day spike).

**Bottom — Stock Price Trend** *(flagged illustrative until real data loaded)*
Line chart: `Fact_StockPrice[close_price]` by `price_date`, with a text
banner: "Illustrative data — see Part IV README" bound to
`Fact_StockPrice[is_illustrative] = 1`, using a page-level visual-header
warning icon or a persistent text box (Power BI can't conditionally hide
text boxes without a measure-driven bookmark, so a static banner is the
pragmatic choice here given the data's current status).

## Formatting & Theme

- Import a custom theme JSON (View → Themes → Browse for themes) using
  this palette to match Parts I-V:
  - Primary (navy): `#1F2A44`
  - Accent (gold): `#B08D57`
  - Positive (green): `#1E6B3C`
  - Negative (red): `#A32424`
  - Background: `#FFFFFF` / light grey `#F2F2F2` for card backgrounds
- Font: Segoe UI (Power BI default) at 10-11pt for body, 14-16pt bold for
  titles, consistent with the Word/Excel deliverables' Calibri/Arial choice.
