-- =====================================================================
-- Waaree Energies — Research Database: Query Library
-- Part V of the institutional research package.
-- Run against waaree_research.db (SQLite). Each query is labeled with
-- its analytical purpose, matching the categories requested in the
-- original project brief.
-- =====================================================================


-- ---------------------------------------------------------------------
-- A. TREND ANALYSIS
-- A1. Revenue, EBITDA, and Net Profit trend for Waaree, FY20-FY26
-- ---------------------------------------------------------------------
SELECT
    fiscal_year,
    revenue,
    ebitda,
    ROUND(ebitda * 100.0 / revenue, 1) AS ebitda_margin_pct,
    net_profit,
    ROUND(net_profit * 100.0 / revenue, 1) AS net_margin_pct
FROM income_statement
WHERE company_id = (SELECT company_id FROM companies WHERE name = 'Waaree Energies Limited')
ORDER BY fiscal_year;

-- A2. Free cash flow trend alongside net profit — surfaces the FY25-FY26
--     "profit up, cash down" divergence flagged throughout Parts I-II
SELECT
    i.fiscal_year,
    i.net_profit,
    cf.free_cash_flow,
    ROUND(cf.cfo * 100.0 / i.ebitda, 1) AS cfo_to_ebitda_pct
FROM income_statement i
JOIN cash_flow cf ON cf.company_id = i.company_id AND cf.fiscal_year = i.fiscal_year
WHERE i.company_id = (SELECT company_id FROM companies WHERE name = 'Waaree Energies Limited')
ORDER BY i.fiscal_year;


-- ---------------------------------------------------------------------
-- B. GROWTH ANALYSIS
-- B1. Year-over-year growth (via the vw_yoy_growth view / window functions)
-- ---------------------------------------------------------------------
SELECT * FROM vw_yoy_growth
WHERE company_name = 'Waaree Energies Limited'
ORDER BY fiscal_year;

-- B2. CAGR calculation: 5-year and 3-year revenue & net profit CAGR,
--     computed directly in SQL using first/last values via subqueries
WITH bounds AS (
    SELECT
        (SELECT revenue FROM income_statement WHERE company_id=1 AND fiscal_year='FY21') AS rev_fy21,
        (SELECT revenue FROM income_statement WHERE company_id=1 AND fiscal_year='FY23') AS rev_fy23,
        (SELECT revenue FROM income_statement WHERE company_id=1 AND fiscal_year='FY26') AS rev_fy26,
        (SELECT net_profit FROM income_statement WHERE company_id=1 AND fiscal_year='FY21') AS np_fy21,
        (SELECT net_profit FROM income_statement WHERE company_id=1 AND fiscal_year='FY23') AS np_fy23,
        (SELECT net_profit FROM income_statement WHERE company_id=1 AND fiscal_year='FY26') AS np_fy26
)
SELECT
    ROUND((POWER(rev_fy26 / rev_fy21, 1.0/5) - 1) * 100, 1) AS revenue_cagr_5yr_pct,
    ROUND((POWER(rev_fy26 / rev_fy23, 1.0/3) - 1) * 100, 1) AS revenue_cagr_3yr_pct,
    ROUND((POWER(np_fy26 / np_fy21, 1.0/5) - 1) * 100, 1)  AS net_profit_cagr_5yr_pct,
    ROUND((POWER(np_fy26 / np_fy23, 1.0/3) - 1) * 100, 1)  AS net_profit_cagr_3yr_pct
FROM bounds;
-- Note: SQLite's POWER() requires the math functions extension, which
-- recalc.py / most modern SQLite builds (3.35+) enable by default. If
-- POWER is unavailable, use: EXP(LN(rev_fy26/rev_fy21)/5) instead.


-- ---------------------------------------------------------------------
-- C. RATIO COMPARISON
-- C1. Full ratio suite across all years (via vw_ratios view)
-- ---------------------------------------------------------------------
SELECT * FROM vw_ratios
WHERE company_name = 'Waaree Energies Limited'
ORDER BY fiscal_year;

-- C2. Working-capital ratios alongside the cash conversion cycle —
--     the single most important qualifying data point from Part I
SELECT
    fiscal_year,
    debtor_days,
    inventory_days,
    payable_days,
    cash_conversion_cycle,
    cash_conversion_cycle - LAG(cash_conversion_cycle) OVER (ORDER BY fiscal_year) AS ccc_change_days
FROM working_capital_days
WHERE company_id = 1
ORDER BY fiscal_year;


-- ---------------------------------------------------------------------
-- D. INDUSTRY / PEER COMPARISON
-- D1. Latest multiples across the peer set (Waaree vs. Premier, Vikram, Websol)
-- ---------------------------------------------------------------------
SELECT
    c.name,
    p.as_of_date,
    p.market_cap_cr,
    p.pe_ratio,
    p.ev_ebitda,
    p.price_to_book,
    ROUND(p.ebitda_margin * 100, 1) AS ebitda_margin_pct,
    p.source_note
FROM peer_snapshot p
JOIN companies c ON c.company_id = p.company_id
ORDER BY p.pe_ratio;

-- D2. How Waaree's own historical EBITDA margin compares to the current
--     peer set's snapshot margins (industry comparison across time AND peers)
SELECT 'Waaree FY26 (own history)' AS label, ROUND(ebitda*100.0/revenue,1) AS ebitda_margin_pct
FROM income_statement WHERE company_id = 1 AND fiscal_year = 'FY26'
UNION ALL
SELECT c.name || ' (snapshot)', ROUND(p.ebitda_margin*100,1)
FROM peer_snapshot p JOIN companies c ON c.company_id = p.company_id
WHERE c.company_id != 1
ORDER BY ebitda_margin_pct DESC;


-- ---------------------------------------------------------------------
-- E. TOP / WORST PERFORMERS
-- E1. Top-performing fiscal years for Waaree by ROE (uses vw_ratios)
-- ---------------------------------------------------------------------
SELECT fiscal_year, net_margin_pct, debt_to_equity, interest_coverage_x
FROM vw_ratios
WHERE company_name = 'Waaree Energies Limited'
ORDER BY net_margin_pct DESC
LIMIT 3;

-- E2. Worst-performing fiscal years for Waaree by free cash flow —
--     surfaces FY26 and FY25 as the two cash-conversion-stress years
SELECT
    i.fiscal_year,
    cf.free_cash_flow,
    i.net_profit,
    RANK() OVER (ORDER BY cf.free_cash_flow ASC) AS fcf_rank_worst_first
FROM cash_flow cf
JOIN income_statement i ON i.company_id = cf.company_id AND i.fiscal_year = cf.fiscal_year
WHERE cf.company_id = 1
ORDER BY cf.free_cash_flow ASC;

-- E3. Peer ranking by cheapest-to-most-expensive on EV/EBITDA (where available)
SELECT c.name, p.ev_ebitda,
       RANK() OVER (ORDER BY p.ev_ebitda ASC) AS cheapest_rank
FROM peer_snapshot p
JOIN companies c ON c.company_id = p.company_id
WHERE p.ev_ebitda IS NOT NULL
ORDER BY p.ev_ebitda ASC;


-- ---------------------------------------------------------------------
-- F. VALUATION QUERIES — querying the DCF sensitivity grid & Monte Carlo
--    output stored in dcf_scenarios (bridges Parts II and IV into SQL)
-- ---------------------------------------------------------------------

-- F1. Full DCF sensitivity grid, pivoted-style (WACC rows, g reads across)
SELECT
    wacc,
    MAX(CASE WHEN terminal_growth = 0.03 THEN intrinsic_value_per_share END) AS g_3pct,
    MAX(CASE WHEN terminal_growth = 0.04 THEN intrinsic_value_per_share END) AS g_4pct,
    MAX(CASE WHEN terminal_growth = 0.05 THEN intrinsic_value_per_share END) AS g_5pct,
    MAX(CASE WHEN terminal_growth = 0.06 THEN intrinsic_value_per_share END) AS g_6pct,
    MAX(CASE WHEN terminal_growth = 0.07 THEN intrinsic_value_per_share END) AS g_7pct
FROM dcf_scenarios
WHERE scenario_type = 'Sensitivity Grid'
GROUP BY wacc
ORDER BY wacc;

-- F2. Monte Carlo percentile distribution vs. CMP (₹2,886) — how much of
--     the distribution sits above/below the current market price
SELECT
    scenario_label,
    intrinsic_value_per_share,
    CASE WHEN intrinsic_value_per_share > 2886 THEN 'Above CMP' ELSE 'Below CMP' END AS vs_cmp
FROM dcf_scenarios
WHERE scenario_type = 'Monte Carlo Percentile'
ORDER BY intrinsic_value_per_share;

-- F3. Base case vs. current market price — one-line valuation summary
SELECT
    scenario_label,
    intrinsic_value_per_share,
    2886 AS cmp,
    ROUND((intrinsic_value_per_share / 2886.0 - 1) * 100, 1) AS upside_downside_pct
FROM dcf_scenarios
WHERE scenario_type = 'Base Case';
