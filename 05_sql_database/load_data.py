"""
load_data.py
=============
Builds waaree_research.db from schema.sql and populates it with the
financial data from Part I (historicals), Part II (DCF sensitivity),
and Part IV (Monte Carlo percentiles).

Usage:
    python load_data.py
"""
import sqlite3
import os
import json

HERE = os.path.dirname(__file__)
DB_PATH = os.path.join(HERE, "waaree_research.db")
SCHEMA_PATH = os.path.join(HERE, "schema.sql")

if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

with open(SCHEMA_PATH) as f:
    cur.executescript(f.read())

# ---------------------------------------------------------------------
# 1. Companies
# ---------------------------------------------------------------------
companies = [
    ("Waaree Energies Limited", "WAAREEENER", "Solar PV Manufacturing", "2024-10-28", 1, "Primary subject of this research package"),
    ("Premier Energies Limited", "PREMIERENE", "Solar PV Manufacturing", "2024-09-03", 0, "Cell+module integrated peer; best-in-class margins"),
    ("Vikram Solar Limited", "VIKRAMSOLAR", "Solar PV Manufacturing", "2025-08-19", 0, "Newest listed peer; highest growth multiple at IPO"),
    ("Websol Energy System Limited", "WEBELSOLAR", "Solar PV Manufacturing", None, 0, "Niche/small-scale peer; highest EBITDA margin in peer set"),
]
cur.executemany(
    "INSERT INTO companies (name, ticker, sector, listed_date, is_primary_subject, notes) VALUES (?,?,?,?,?,?)",
    companies,
)
conn.commit()

def cid(name):
    cur.execute("SELECT company_id FROM companies WHERE name = ?", (name,))
    return cur.fetchone()[0]

WAAREE = cid("Waaree Energies Limited")
PREMIER = cid("Premier Energies Limited")
VIKRAM = cid("Vikram Solar Limited")
WEBSOL = cid("Websol Energy System Limited")

# ---------------------------------------------------------------------
# 2. Income Statement — Waaree FY20-FY26 (₹ Cr), Source: Part I
# ---------------------------------------------------------------------
years = ["FY20","FY21","FY22","FY23","FY24","FY25","FY26"]
fy_end = ["2020-03-31","2021-03-31","2022-03-31","2023-03-31","2024-03-31","2025-03-31","2026-03-31"]
revenue    = [1996,1953,2854,6751,11398,14444,26537]
ebitda     = [93,85,106,836,1574,2722,5909]
depn       = [27,29,43,164,277,402,990]
interest   = [34,31,41,82,140,152,280]
other_inc  = [25,45,97,88,576,398,413]
tax_rate   = [0.31,0.31,0.33,0.26,0.27,0.25,0.23]
net_profit = [39,48,80,500,1274,1928,3884]
eps        = [2.12,2.50,3.84,24.49,62.76,65.00,129.02]
pbt        = [round((ebitda[i]-depn[i])+other_inc[i]-interest[i],2) for i in range(7)]

for i in range(7):
    cur.execute("""INSERT INTO income_statement
        (company_id, fiscal_year, fiscal_year_end, revenue, ebitda, depreciation, interest, other_income, pbt, tax_rate, net_profit, eps)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
        (WAAREE, years[i], fy_end[i], revenue[i], ebitda[i], depn[i], interest[i], other_inc[i], pbt[i], tax_rate[i], net_profit[i], eps[i]))

# ---------------------------------------------------------------------
# 3. Balance Sheet — Waaree FY20-FY26
# ---------------------------------------------------------------------
equity_cap  = [197,197,197,243,263,287,288]
reserves    = [101,148,231,1595,3825,9192,14150]
borrowings  = [157,340,363,320,553,1199,3213]
other_liab  = [483,596,1362,5247,6635,9028,12465]
nfa         = [152,285,625,1105,1450,4051,7329]
cwip        = [40,3,124,537,1341,1884,3476]
investments = [85,115,143,31,71,65,953]
other_assets= [661,878,1262,5732,8414,13706,18358]

for i in range(7):
    cur.execute("""INSERT INTO balance_sheet
        (company_id, fiscal_year, equity_capital, reserves, borrowings, other_liabilities, net_fixed_assets, cwip, investments, other_assets)
        VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (WAAREE, years[i], equity_cap[i], reserves[i], borrowings[i], other_liab[i], nfa[i], cwip[i], investments[i], other_assets[i]))

# ---------------------------------------------------------------------
# 4. Cash Flow — Waaree FY20-FY26
# ---------------------------------------------------------------------
cfo = [83,67,698,1560,2305,3158,1627]
cfi = [-22,-250,-673,-2088,-3346,-6806,-3953]
cff = [-50,161,101,642,909,4036,2573]
fcf = [32,-35,202,698,968,-114,-3209]

for i in range(7):
    cur.execute("""INSERT INTO cash_flow (company_id, fiscal_year, cfo, cfi, cff, free_cash_flow) VALUES (?,?,?,?,?,?)""",
        (WAAREE, years[i], cfo[i], cfi[i], cff[i], fcf[i]))

# ---------------------------------------------------------------------
# 5. Working Capital Days — Waaree FY20-FY26 (Source: Part I Section 4.3)
# ---------------------------------------------------------------------
debtor_days = [26,22,12,17,31,30,34]
inventory_days = [54,83,85,192,108,96,118]
payable_days = [67,99,83,143,84,91,63]
ccc = [13,6,14,66,55,35,90]

for i in range(7):
    cur.execute("""INSERT INTO working_capital_days (company_id, fiscal_year, debtor_days, inventory_days, payable_days, cash_conversion_cycle)
        VALUES (?,?,?,?,?,?)""", (WAAREE, years[i], debtor_days[i], inventory_days[i], payable_days[i], ccc[i]))

# ---------------------------------------------------------------------
# 6. Peer Snapshot — cross-sectional comps (Source: Part I Section 1.5 / Part II Section 3.1)
# ---------------------------------------------------------------------
peer_rows = [
    (WAAREE,  "2026-06-30", 83000, 25.0, 14.4, 5.7,  0.220, "Own current multiples, late Jun 2026"),
    (PREMIER, "2026-07-01", 46544, 30.8, 20.2, 15.8, 0.275, "Aug 2025 peer comparison + Jul 2026 current multiples (mixed vintage, see Part II 3.1 note)"),
    (VIKRAM,  "2025-08-19", 7000,  70.0, None, 8.4,  0.144, "IPO-era multiple (Aug 2025); price down ~22.5% YTD through Jul 2026 — not refreshed, flagged in Part II"),
    (WEBSOL,  "2025-08-01", None,  29.7, None, 21.3, 0.440, "Aug 2025 peer comparison; market cap not captured in source"),
]
cur.executemany("""INSERT INTO peer_snapshot (company_id, as_of_date, market_cap_cr, pe_ratio, ev_ebitda, price_to_book, ebitda_margin, source_note)
    VALUES (?,?,?,?,?,?,?,?)""", peer_rows)

# ---------------------------------------------------------------------
# 7. Stock prices — monthly-resampled illustrative series (see Python Part IV)
#    Flagged is_illustrative = 1. Real daily data can be loaded by re-running
#    01_data_import.py (Part IV) and importing its CSVs here instead.
# ---------------------------------------------------------------------
import random
random.seed(7)
base = 1503.0
cur_price = base
price_rows = []
d = 2024
import datetime
dt = datetime.date(2024, 10, 31)
end_dt = datetime.date(2026, 6, 30)
while dt <= end_dt:
    drift = random.gauss(0.01, 0.06)
    cur_price = max(500, cur_price * (1 + drift))
    price_rows.append((WAAREE, dt.isoformat(), round(cur_price, 2), 1))
    # move to next month end (approx)
    month = dt.month + 1
    year = dt.year + (1 if month > 12 else 0)
    month = 1 if month > 12 else month
    day = 28
    dt = datetime.date(year, month, day)
# rescale last point toward disclosed CMP for realism
scale = 2886.0 / price_rows[-1][2]
price_rows = [(r[0], r[1], round(r[2]*scale, 2), r[3]) for r in price_rows]
cur.executemany("INSERT INTO stock_prices (company_id, price_date, close_price, is_illustrative) VALUES (?,?,?,?)", price_rows)

# ---------------------------------------------------------------------
# 8. DCF Scenarios — Part II sensitivity grid + Part IV Monte Carlo percentiles
# ---------------------------------------------------------------------
sensitivity = [
    (0.118, 0.03, 2291), (0.118, 0.04, 2546), (0.118, 0.05, 2876), (0.118, 0.06, 3319), (0.118, 0.07, 3947),
    (0.128, 0.03, 2017), (0.128, 0.04, 2212), (0.128, 0.05, 2458), (0.128, 0.06, 2776), (0.128, 0.07, 3204),
    (0.138, 0.03, 1794), (0.138, 0.04, 1947), (0.138, 0.05, 2136), (0.138, 0.06, 2374), (0.138, 0.07, 2681),
    (0.148, 0.03, 1609), (0.148, 0.04, 1733), (0.148, 0.05, 1881), (0.148, 0.06, 2064), (0.148, 0.07, 2293),
    (0.158, 0.03, 1455), (0.158, 0.04, 1555), (0.158, 0.05, 1674), (0.158, 0.06, 1818), (0.158, 0.07, 1994),
]
for wacc, g, val in sensitivity:
    cur.execute("""INSERT INTO dcf_scenarios (company_id, scenario_type, scenario_label, wacc, terminal_growth, intrinsic_value_per_share)
        VALUES (?,?,?,?,?,?)""", (WAAREE, "Sensitivity Grid", f"WACC {wacc:.1%} / g {g:.1%}", wacc, g, val))

mc_json_path = os.path.join(HERE, "..", "python", "output", "mc_summary.json")
if os.path.exists(mc_json_path):
    with open(mc_json_path) as f:
        mc = json.load(f)
    for pct, val in mc["percentiles"].items():
        cur.execute("""INSERT INTO dcf_scenarios (company_id, scenario_type, scenario_label, wacc, terminal_growth, intrinsic_value_per_share)
            VALUES (?,?,?,?,?,?)""", (WAAREE, "Monte Carlo Percentile", f"P{pct}", None, None, round(val)))
else:
    # fallback values matching the Part IV run in this package
    for pct, val in [(5,1264),(10,1424),(25,1745),(50,2121),(75,2565),(90,3097),(95,3499)]:
        cur.execute("""INSERT INTO dcf_scenarios (company_id, scenario_type, scenario_label, wacc, terminal_growth, intrinsic_value_per_share)
            VALUES (?,?,?,?,?,?)""", (WAAREE, "Monte Carlo Percentile", f"P{pct}", None, None, val))

cur.execute("""INSERT INTO dcf_scenarios (company_id, scenario_type, scenario_label, wacc, terminal_growth, intrinsic_value_per_share)
    VALUES (?,?,?,?,?,?)""", (WAAREE, "Base Case", "Part II Base Case", 0.138, 0.05, 2146))

conn.commit()
conn.close()
print(f"Database built -> {DB_PATH}")
