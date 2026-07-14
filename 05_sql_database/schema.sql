-- =====================================================================
-- Waaree Energies — Equity Research Database Schema
-- Part V of the institutional research package.
-- Dialect: SQLite (chosen for portability/zero-setup). Column types and
-- syntax are close enough to standard SQL to port to Postgres/MySQL with
-- minor edits (e.g. AUTOINCREMENT -> SERIAL, adding explicit FK actions).
-- =====================================================================

PRAGMA foreign_keys = ON;

-- ---------------------------------------------------------------------
-- 1. COMPANIES — master list: Waaree (primary subject) + peer set
-- ---------------------------------------------------------------------
CREATE TABLE companies (
    company_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL UNIQUE,
    ticker          TEXT,
    sector          TEXT NOT NULL,
    listed_date     DATE,
    is_primary_subject INTEGER NOT NULL DEFAULT 0,  -- 1 = Waaree, 0 = peer
    notes           TEXT
);

-- ---------------------------------------------------------------------
-- 2. INCOME STATEMENT — annual, ₹ Crore, consolidated
--    Fully populated for Waaree (FY20-FY26); peers only have single-period
--    snapshot data (see peer_snapshot table) since standalone multi-year
--    financials for the smaller peers weren't part of this research scope.
-- ---------------------------------------------------------------------
CREATE TABLE income_statement (
    company_id      INTEGER NOT NULL REFERENCES companies(company_id),
    fiscal_year     TEXT NOT NULL,      -- e.g. 'FY26'
    fiscal_year_end DATE,               -- e.g. '2026-03-31'
    revenue         REAL,
    ebitda          REAL,
    depreciation    REAL,
    interest        REAL,
    other_income    REAL,
    pbt             REAL,
    tax_rate        REAL,               -- as decimal, e.g. 0.23
    net_profit      REAL,
    eps             REAL,
    PRIMARY KEY (company_id, fiscal_year)
);

-- ---------------------------------------------------------------------
-- 3. BALANCE SHEET — annual, ₹ Crore, consolidated
-- ---------------------------------------------------------------------
CREATE TABLE balance_sheet (
    company_id       INTEGER NOT NULL REFERENCES companies(company_id),
    fiscal_year      TEXT NOT NULL,
    equity_capital   REAL,
    reserves         REAL,
    borrowings       REAL,
    other_liabilities REAL,
    net_fixed_assets REAL,
    cwip             REAL,
    investments      REAL,
    other_assets     REAL,
    PRIMARY KEY (company_id, fiscal_year)
);

-- ---------------------------------------------------------------------
-- 4. CASH FLOW — annual, ₹ Crore, consolidated
-- ---------------------------------------------------------------------
CREATE TABLE cash_flow (
    company_id       INTEGER NOT NULL REFERENCES companies(company_id),
    fiscal_year      TEXT NOT NULL,
    cfo              REAL,
    cfi              REAL,
    cff              REAL,
    free_cash_flow   REAL,
    PRIMARY KEY (company_id, fiscal_year)
);

-- ---------------------------------------------------------------------
-- 5. WORKING CAPITAL DAYS — supports cash-conversion-cycle analysis
-- ---------------------------------------------------------------------
CREATE TABLE working_capital_days (
    company_id            INTEGER NOT NULL REFERENCES companies(company_id),
    fiscal_year           TEXT NOT NULL,
    debtor_days           REAL,
    inventory_days        REAL,
    payable_days          REAL,
    cash_conversion_cycle REAL,
    PRIMARY KEY (company_id, fiscal_year)
);

-- ---------------------------------------------------------------------
-- 6. PEER SNAPSHOT — cross-sectional comps (single as-of date), used for
--    relative valuation / industry comparison queries (Part II Section 3)
-- ---------------------------------------------------------------------
CREATE TABLE peer_snapshot (
    company_id      INTEGER NOT NULL REFERENCES companies(company_id),
    as_of_date      DATE NOT NULL,
    market_cap_cr   REAL,
    pe_ratio        REAL,
    ev_ebitda       REAL,
    price_to_book   REAL,
    ebitda_margin   REAL,               -- as decimal
    source_note     TEXT,
    PRIMARY KEY (company_id, as_of_date)
);

-- ---------------------------------------------------------------------
-- 7. STOCK PRICES — daily/periodic close price. is_illustrative flags
--    any row generated as a methodology stand-in rather than pulled from
--    a live market-data feed (see Python Part IV README for why).
-- ---------------------------------------------------------------------
CREATE TABLE stock_prices (
    company_id      INTEGER NOT NULL REFERENCES companies(company_id),
    price_date      DATE NOT NULL,
    close_price     REAL,
    is_illustrative INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (company_id, price_date)
);

-- ---------------------------------------------------------------------
-- 8. DCF SCENARIOS — stores the Part II/III sensitivity grid and the
--    Part IV Monte Carlo percentile output, so both are SQL-queryable.
-- ---------------------------------------------------------------------
CREATE TABLE dcf_scenarios (
    scenario_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id      INTEGER NOT NULL REFERENCES companies(company_id),
    scenario_type   TEXT NOT NULL,        -- 'Sensitivity Grid' | 'Monte Carlo Percentile' | 'Base Case'
    scenario_label  TEXT NOT NULL,        -- e.g. 'WACC 13.8% / g 5.0%' or 'P50'
    wacc            REAL,
    terminal_growth REAL,
    intrinsic_value_per_share REAL,
    created_at      TEXT DEFAULT (datetime('now'))
);

-- ---------------------------------------------------------------------
-- Indexes to support the trend/growth queries in queries.sql
-- ---------------------------------------------------------------------
CREATE INDEX idx_is_company_year ON income_statement(company_id, fiscal_year);
CREATE INDEX idx_bs_company_year ON balance_sheet(company_id, fiscal_year);
CREATE INDEX idx_cf_company_year ON cash_flow(company_id, fiscal_year);
CREATE INDEX idx_prices_company_date ON stock_prices(company_id, price_date);

-- =====================================================================
-- VIEWS — computed ratios, kept as views (not materialized tables) so
-- they always reflect the latest underlying data — standard practice
-- for derived/calculated fields in a research database.
-- =====================================================================

-- vw_ratios: full ratio suite per company per year
CREATE VIEW vw_ratios AS
SELECT
    c.name                                             AS company_name,
    i.fiscal_year,
    i.revenue,
    i.ebitda,
    ROUND(i.ebitda / NULLIF(i.revenue,0) * 100, 1)     AS ebitda_margin_pct,
    ROUND(i.net_profit / NULLIF(i.revenue,0) * 100, 1) AS net_margin_pct,
    ROUND((b.equity_capital + b.reserves), 1)          AS total_equity,
    b.borrowings,
    ROUND(b.borrowings / NULLIF((b.equity_capital + b.reserves),0), 2) AS debt_to_equity,
    ROUND((i.ebitda - i.depreciation) / NULLIF(i.interest,0), 1)       AS interest_coverage_x,
    i.eps
FROM income_statement i
JOIN companies c        ON c.company_id = i.company_id
JOIN balance_sheet b     ON b.company_id = i.company_id AND b.fiscal_year = i.fiscal_year;

-- vw_yoy_growth: year-over-year growth in revenue and net profit, via
-- window function LAG (SQLite >= 3.25 supports window functions)
CREATE VIEW vw_yoy_growth AS
SELECT
    c.name AS company_name,
    i.fiscal_year,
    i.revenue,
    ROUND(
        (i.revenue - LAG(i.revenue) OVER (PARTITION BY i.company_id ORDER BY i.fiscal_year))
        / NULLIF(LAG(i.revenue) OVER (PARTITION BY i.company_id ORDER BY i.fiscal_year), 0) * 100
    , 1) AS revenue_growth_pct,
    i.net_profit,
    ROUND(
        (i.net_profit - LAG(i.net_profit) OVER (PARTITION BY i.company_id ORDER BY i.fiscal_year))
        / NULLIF(LAG(i.net_profit) OVER (PARTITION BY i.company_id ORDER BY i.fiscal_year), 0) * 100
    , 1) AS net_profit_growth_pct
FROM income_statement i
JOIN companies c ON c.company_id = i.company_id;
