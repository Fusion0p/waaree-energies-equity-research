# Waaree Energies — SQL Research Database

Part V of the institutional research package.

## Contents

| File | Purpose |
|---|---|
| `schema.sql` | Full DDL: 8 tables + 2 views (SQLite dialect, portable to Postgres/MySQL) |
| `load_data.py` | Builds `waaree_research.db` and populates it from Parts I, II, and IV |
| `queries.sql` | 14 labeled, tested queries: trend, growth (CAGR via window functions), ratio, industry/peer comparison, top/worst performers, and DCF/Monte Carlo queries |
| `waaree_research.db` | The populated SQLite database (run `load_data.py` to regenerate) |

## Quick start

```bash
python load_data.py                     # (re)builds waaree_research.db
python3 -c "
import sqlite3
conn = sqlite3.connect('waaree_research.db')
for row in conn.execute(open('queries.sql').read().split(';')[0]):
    print(row)
"
# Or open waaree_research.db in any SQLite browser (DB Browser for SQLite, DBeaver, etc.)
# and run queries.sql directly.
```

## Schema design notes

- **companies**: Waaree (`is_primary_subject=1`) plus the three clean pure-play
  peers used in Part II's comps analysis (Premier Energies, Vikram Solar,
  Websol Energy).
- **income_statement / balance_sheet / cash_flow**: fully populated for
  Waaree FY20-FY26 (Part I data). Peers only have cross-sectional data
  (see `peer_snapshot`) since standalone multi-year peer financials were
  outside this project's research scope — a limitation stated explicitly
  rather than papered over with invented numbers.
- **working_capital_days**: supports the cash-conversion-cycle analysis
  that is the central analytical thread of Parts I-IV.
- **peer_snapshot**: cross-sectional comps (P/E, EV/EBITDA, P/B, margin) at
  a point in time — mixed data vintages are preserved and flagged in
  `source_note` rather than silently blended, consistent with Part II
  Section 3.1's limitation note.
- **stock_prices**: `is_illustrative=1` flags every row, since this
  environment has no live market-data network access (see Part IV README)
  — swap in real data from `01_data_import.py`'s CSVs at any time.
- **dcf_scenarios**: stores both the Part II/III sensitivity grid (25 rows)
  and the Part IV Monte Carlo percentile output (7 rows) as queryable data,
  bridging the Excel/Python deliverables into SQL.
- **vw_ratios / vw_yoy_growth**: ratios are views, not stored tables — they
  recompute from the underlying financials every time they're queried,
  which is the correct pattern for derived data (matches the "Ratios" tab
  design in the Excel model, which uses live formulas for the same reason).

## Validated

All 14 queries in `queries.sql` were executed against the populated database
and cross-checked against Parts I, II, and IV — e.g. the CAGR query returns
68.5% (5-yr revenue CAGR) matching Part I's narrative, and the sensitivity
grid pivot query reproduces the Excel model's 5×5 grid exactly.
