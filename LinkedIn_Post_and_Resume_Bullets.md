# LinkedIn Post

*Post this as a text update with an attached PDF carousel (see "Carousel" note below). Copy the text as-is or lightly personalize the opening line.*

---

I built a full DCF model for India's largest solar manufacturer — and it disagrees with the market by 60 percentage points. Here's what I found, and why I think that disagreement is the actually interesting part.

Over the past few weeks I put together an end-to-end institutional equity research package on **Waaree Energies** (NSE: WAAREEENER), India's largest non-Chinese solar PV module manufacturer:

→ Industry & company research (Porter's Five Forces, SWOT, policy landscape — the ALMM/PLI/BCD stack driving Indian solar manufacturing)
→ A DCF valuation (WACC build-up, 5-year FCFF forecast, terminal value) and a comparable-company analysis against Premier Energies, Vikram Solar, and Websol
→ A fully dynamic 3-statement Excel model — 529 live formulas, every forecast assumption editable, zero balance-sheet errors
→ A 20,000-path Monte Carlo simulation in Python to stress-test the valuation instead of relying on one point estimate
→ A SQL database and a Power BI data model + DAX measures for the whole thing

**The finding that mattered most:** Waaree's FY26 net profit grew 101% year-over-year — but free cash flow swung to -₹3,209 Cr, as the cash conversion cycle widened from 35 days to 90 days. CFO/EBITDA fell from 143% to just 47%. The P&L looked great. The cash flow statement told a very different story.

That single fact is why my DCF (₹2,146/share) and my peer-multiple comps (₹3,900/share) landed so far apart, and why the Monte Carlo simulation puts only an ~11% probability on the stock's intrinsic value exceeding today's market price. I didn't average the two methods together and call it a day — I weighted the DCF more heavily (65/35) because the cash-flow deterioration is company-specific and disclosed, not something peer multiples obviously price in, and I said so explicitly rather than hiding the judgment call.

Final call: **HOLD, 12-month target ₹2,760/share.**

Full writeup, the model, the Python code, and the SQL/Power BI layers are all on GitHub: [link]

This was built as an independent learning project, not investment advice — but I'd genuinely like to hear pushback on the DCF/comps weighting from anyone who's done sell-side or buy-side work. That's the one judgment call in this whole project I'm least certain about.

#EquityResearch #FinancialModeling #DCF #Python #PowerBI #IndianStockMarket

---

**Carousel note:** LinkedIn's PDF-carousel format outperforms plain text+link posts. Turn these 4 images into a single PDF (any of the docx/pptx viewers, or just paste them into one Word doc and export as PDF) and attach it instead of / alongside the link:
1. The rating box (screenshots/01_rating_box.jpg)
2. The Monte Carlo histogram (screenshots/02_monte_carlo.png)
3. The DCF sensitivity table (screenshots/04_dcf_table.jpg)
4. The Power BI dashboard preview (screenshot of Waaree_Dashboard_Preview.html)

Post the link to the repo in the first comment rather than the post body if you notice LinkedIn suppressing reach on posts with outbound links — test both and see what performs better for your audience.

---

# Resume Bullets

*Add under a "Projects" section, not buried inside "Skills."*

**Independent Equity Research — Waaree Energies Ltd. (NSE-listed solar PV manufacturer)**
*[github.com/your-username/waaree-energies-equity-research]* · [Month] 2026

- Built an end-to-end institutional equity research package spanning industry/company research, DCF and comparable-company valuation, a dynamic 3-statement Excel model, Python analytics, a SQL database, and a Power BI dashboard
- Ran a 20,000-simulation Monte Carlo valuation in Python (NumPy), quantifying an 11% probability that intrinsic value exceeds the market price and identifying WACC — not revenue growth — as the dominant driver of valuation uncertainty
- Identified and quantified a company-specific cash-conversion deterioration (CFO/EBITDA 143%→47% YoY) missed by a pure comps-based valuation, and reconciled a 60-percentage-point DCF-vs-comps gap into a single weighted price target with an explicitly stated rationale
- Built a fully dynamic 3-statement financial model in Excel (529 live formulas across 10 linked tabs) with zero balance-sheet integrity errors and a live WACC/terminal-growth sensitivity grid
- Designed a normalized SQL schema (8 tables, 2 views) and a Power BI star-schema data model with a full DAX measures library for ratio, valuation, and peer-comparison analysis

**Tools:** Excel (dynamic financial modeling, sensitivity analysis) · Python (pandas, NumPy, statsmodels, Monte Carlo simulation) · SQL (SQLite, window functions, CAGR/ranking queries) · Power BI (DAX, star schema design)

---

## Interview prep — the 3 questions to have crisp answers for

1. **"Walk me through why you weighted DCF 65% and comps 35%."**
   Answer: the FY26 cash-conversion deterioration (CFO/EBITDA to 47%, FCF to -₹3,209 Cr) is Waaree-specific and disclosed; it's directly modeled in the DCF's working-capital assumptions but not obviously reflected in Premier Energies' or Websol's current trading multiples, which may themselves carry sector-wide optimism about the ALMM List-II transition. State plainly that a 50/50 blend would give a mildly bullish view instead (+4.7%) — showing you know it's a judgment call, not a formula.

2. **"What would change your mind — bullish or bearish?"**
   Bullish: 1H-FY27 results showing the cash conversion cycle normalizing back toward 35 days, or confirmed cell-capacity progress materially ahead of the 2.3 GW FY26 base. Bearish: the working-capital deterioration proving structural rather than transitory, or the ALMM List-II cost pass-through running larger/longer than modeled.

3. **"What's the weakest assumption in your model?"**
   Be ready to name the ERP/beta choice in the WACC build (Section 2.1 of the valuation doc) — you flagged this yourself as the single largest driver of valuation uncertainty in the Monte Carlo sensitivity ranking, ahead of revenue growth. Knowing your own model's weak point cold is the fastest way to look credible in this kind of interview.
