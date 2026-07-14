"""
01_data_import.py
==================
Pulls daily OHLCV price history for Waaree Energies, its peer set, and the
NIFTY 50 index via yfinance, and saves clean CSVs to ./data/.

NOTE ON THIS SANDBOX: this script requires outbound internet access to
Yahoo Finance (query1/query2.finance.yahoo.com), which is not on this
environment's network allowlist. Run this script on your own machine
(`pip install -r requirements.txt` first) to populate ./data/ with real
prices. Scripts 03-05 will automatically detect and use ./data/*.csv if
present, and fall back to clearly-labeled synthetic/illustrative data
if not — so the rest of the pipeline runs either way.

Usage:
    python 01_data_import.py
"""
import os
import pandas as pd
import yfinance as yf

OUT_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(OUT_DIR, exist_ok=True)

TICKERS = {
    "WAAREE": "WAAREEENER.NS",
    "PREMIER_ENERGIES": "PREMIERENE.NS",
    "TATA_POWER": "TATAPOWER.NS",
    "WEBSOL": "WEBELSOLAR.NS",
    "NIFTY50": "^NSEI",
}

START = "2024-10-28"   # Waaree's listing date
END = None              # None = up to today


def fetch_and_save():
    frames = {}
    for name, ticker in TICKERS.items():
        print(f"Fetching {name} ({ticker}) ...")
        df = yf.download(ticker, start=START, end=END, progress=False, auto_adjust=True)
        if df.empty:
            print(f"  WARNING: no data returned for {ticker}")
            continue
        df = df[["Open", "High", "Low", "Close", "Volume"]].copy()
        df.index.name = "Date"
        out_path = os.path.join(OUT_DIR, f"{name}.csv")
        df.to_csv(out_path)
        print(f"  Saved {len(df)} rows -> {out_path}")
        frames[name] = df
    return frames


if __name__ == "__main__":
    fetch_and_save()
    print("\nDone. Re-run 03_risk_metrics.py and 05_export_master_workbook.py to refresh downstream outputs with real prices.")
