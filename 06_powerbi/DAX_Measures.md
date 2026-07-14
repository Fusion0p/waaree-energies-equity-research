# Waaree Energies — Power BI DAX Measures Library

Part VI of the institutional research package. Import `Waaree_PowerBI_DataModel.xlsx`
into Power BI Desktop (Get Data → Excel Workbook → select all 10 tables), then
build these relationships and measures.

## 1. Data Model Relationships

Set these up in Model View after import:

| From | To | Cardinality |
|---|---|---|
| `Fact_IncomeStatement[company]` | `Dim_Company[name]` | Many-to-one |
| `Fact_IncomeStatement[fiscal_year]` | `Dim_FiscalYear[fiscal_year]` | Many-to-one |
| `Fact_BalanceSheet[company]` / `[fiscal_year]` | `Dim_Company` / `Dim_FiscalYear` | Many-to-one |
| `Fact_CashFlow[company]` / `[fiscal_year]` | `Dim_Company` / `Dim_FiscalYear` | Many-to-one |
| `Fact_Ratios[company_name]` / `[fiscal_year]` | `Dim_Company[name]` / `Dim_FiscalYear` | Many-to-one |
| `Fact_WorkingCapital[company]` / `[fiscal_year]` | `Dim_Company` / `Dim_FiscalYear` | Many-to-one |
| `Fact_PeerSnapshot[company]` | `Dim_Company[name]` | Many-to-one |
| `Fact_StockPrice[company]` | `Dim_Company[name]` | Many-to-one |
| `Fact_DCFScenarios[company]` | `Dim_Company[name]` | Many-to-one |

Mark `Dim_FiscalYear` as a Date Table proxy: sort `Fact_IncomeStatement[fiscal_year]`
column by `Dim_FiscalYear[fy_order]` (Column tool → Sort by Column) so charts
render FY20→FY31E in the correct order rather than alphabetically.

## 2. Core KPI Measures

```dax
Total Revenue = SUM(Fact_IncomeStatement[revenue])

Total EBITDA = SUM(Fact_IncomeStatement[ebitda])

EBITDA Margin % =
DIVIDE([Total EBITDA], [Total Revenue], 0)

Net Profit = SUM(Fact_IncomeStatement[net_profit])

Net Margin % =
DIVIDE([Net Profit], [Total Revenue], 0)

EPS (Rs) = AVERAGE(Fact_IncomeStatement[eps])

Revenue YoY Growth % =
VAR CurrentRev = [Total Revenue]
VAR PriorRev =
    CALCULATE(
        [Total Revenue],
        DATEADD(Dim_FiscalYear[calendar_year_end], -1, YEAR)
    )
RETURN DIVIDE(CurrentRev - PriorRev, PriorRev, BLANK())
-- Note: since Dim_FiscalYear isn't a true date table, the more robust
-- pattern in this model is the explicit-index version below:

Revenue YoY Growth % (fy_order) =
VAR CurrentOrder = SELECTEDVALUE(Dim_FiscalYear[fy_order])
VAR CurrentRev = [Total Revenue]
VAR PriorRev =
    CALCULATE(
        [Total Revenue],
        FILTER(ALL(Dim_FiscalYear), Dim_FiscalYear[fy_order] = CurrentOrder - 1)
    )
RETURN DIVIDE(CurrentRev - PriorRev, PriorRev, BLANK())
```

## 3. Cash Flow Measures

```dax
CFO = SUM(Fact_CashFlow[cfo])
CFI = SUM(Fact_CashFlow[cfi])
CFF = SUM(Fact_CashFlow[cff])
Free Cash Flow = SUM(Fact_CashFlow[free_cash_flow])

CFO to EBITDA % =
DIVIDE([CFO], [Total EBITDA], 0)   -- the key "quality of earnings" KPI from Part I
```

## 4. Return & Leverage Measures

```dax
Total Equity = SUM(Fact_BalanceSheet[equity_capital]) + SUM(Fact_BalanceSheet[reserves])

Total Borrowings = SUM(Fact_BalanceSheet[borrowings])

Debt to Equity =
DIVIDE([Total Borrowings], [Total Equity], 0)

ROE % =
VAR NP = [Net Profit]
VAR AvgEquity =
    AVERAGEX(
        VALUES(Dim_FiscalYear[fy_order]),
        CALCULATE([Total Equity])
    )
RETURN DIVIDE(NP, AvgEquity, 0)

ROCE % =
VAR EBIT = [Total EBITDA] - SUM(Fact_IncomeStatement[depreciation])
VAR CapitalEmployed = [Total Equity] + [Total Borrowings]
RETURN DIVIDE(EBIT, CapitalEmployed, 0)

Interest Coverage (x) =
VAR EBIT = [Total EBITDA] - SUM(Fact_IncomeStatement[depreciation])
RETURN DIVIDE(EBIT, SUM(Fact_IncomeStatement[interest]), 0)
```

## 5. Working Capital Measures

```dax
Cash Conversion Cycle (days) = AVERAGE(Fact_WorkingCapital[cash_conversion_cycle])
Debtor Days = AVERAGE(Fact_WorkingCapital[debtor_days])
Inventory Days = AVERAGE(Fact_WorkingCapital[inventory_days])
Payable Days = AVERAGE(Fact_WorkingCapital[payable_days])
```

## 6. Valuation / DCF Measures

```dax
Base Case Intrinsic Value =
CALCULATE(
    AVERAGE(Fact_DCFScenarios[intrinsic_value_per_share]),
    Fact_DCFScenarios[scenario_type] = "Base Case"
)

CMP = 2886   -- hardcoded constant; replace with a live Fact_StockPrice lookup once real data is loaded

Upside Downside % =
DIVIDE([Base Case Intrinsic Value] - [CMP], [CMP], 0)

Monte Carlo Median =
CALCULATE(
    AVERAGE(Fact_DCFScenarios[intrinsic_value_per_share]),
    Fact_DCFScenarios[scenario_type] = "Monte Carlo Percentile",
    Fact_DCFScenarios[scenario_label] = "P50"
)

Probability Value Exceeds CMP =
VAR AboveCount =
    CALCULATE(
        COUNTROWS(Fact_DCFScenarios),
        Fact_DCFScenarios[scenario_type] = "Monte Carlo Percentile",
        Fact_DCFScenarios[intrinsic_value_per_share] > [CMP]
    )
VAR TotalCount =
    CALCULATE(
        COUNTROWS(Fact_DCFScenarios),
        Fact_DCFScenarios[scenario_type] = "Monte Carlo Percentile"
    )
RETURN DIVIDE(AboveCount, TotalCount, 0)
-- Note: for a true probability (not just percentile-bucket count), pull
-- the full 20,000-row Monte Carlo output (Part IV) into a new fact table
-- rather than just the 7 summary percentiles included here.
```

## 7. Peer Comparison Measures

```dax
Peer Avg PE = AVERAGEX(FILTER(Fact_PeerSnapshot, Fact_PeerSnapshot[company] <> "Waaree Energies Limited"), Fact_PeerSnapshot[pe_ratio])

Waaree PE = CALCULATE(AVERAGE(Fact_PeerSnapshot[pe_ratio]), Fact_PeerSnapshot[company] = "Waaree Energies Limited")

PE Discount to Peers % =
DIVIDE([Waaree PE] - [Peer Avg PE], [Peer Avg PE], 0)
```

## 8. Forecast vs. Actual Flag (for conditional formatting)

```dax
Is Forecast = SELECTEDVALUE(Dim_FiscalYear[is_forecast])

Revenue (Actual Only) =
CALCULATE([Total Revenue], Dim_FiscalYear[is_forecast] = 0)

Revenue (Forecast Only) =
CALCULATE([Total Revenue], Dim_FiscalYear[is_forecast] = 1)
```
