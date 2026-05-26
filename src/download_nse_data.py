import os
import pandas as pd
import yfinance as yf

NSE_STOCKS = {
    "RELIANCE":   "RELIANCE.NS",
    "TCS":        "TCS.NS",
    "HDFCBANK":   "HDFCBANK.NS",
    "INFY":       "INFY.NS",
    "ICICIBANK":  "ICICIBANK.NS",
    "WIPRO":      "WIPRO.NS",
    "BHARTIARTL": "BHARTIARTL.NS",
    "SBIN":       "SBIN.NS",
    "HCLTECH":    "HCLTECH.NS",
    "BAJFINANCE": "BAJFINANCE.NS",
    "KOTAKBANK":  "KOTAKBANK.NS",
    "AXISBANK":   "AXISBANK.NS",
    "MARUTI":     "MARUTI.NS",
    "SUNPHARMA":  "SUNPHARMA.NS",
    "TITAN":      "TITAN.NS",
}

DATA_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)

print("=" * 60)
print("📥  NSE STOCK DATA DOWNLOADER")
print("=" * 60)

success, failed = [], []

for symbol, ticker in NSE_STOCKS.items():
    try:
        print(f"\n⬇  Downloading {symbol} ({ticker}) ...")
        raw = yf.download(ticker, period="3y", auto_adjust=True, progress=False)

        if raw.empty:
            print(f"   ⚠️  No data for {symbol}")
            failed.append(symbol)
            continue

        if isinstance(raw.columns, pd.MultiIndex):
            raw.columns = raw.columns.get_level_values(0)

        raw = raw.rename(columns={
            "Open": "open", "High": "high",
            "Low":  "low",  "Close": "close", "Volume": "volume"
        })

        raw.index.name = "date"
        raw = raw.reset_index()
        raw["date"] = pd.to_datetime(raw["date"]).dt.strftime("%d-%b-%Y")

        cols = ["date", "open", "high", "low", "close", "volume"]
        raw = raw[[c for c in cols if c in raw.columns]]

        out = os.path.join(DATA_DIR, f"{symbol}.csv")
        raw.to_csv(out, index=False)
        print(f"   ✅ {len(raw)} rows → {out}")
        success.append(symbol)

    except Exception as e:
        print(f"   ❌ Failed: {e}")
        failed.append(symbol)

print("\n" + "=" * 60)
print(f"✅  Downloaded : {len(success)} stocks → {success}")
if failed:
    print(f"❌  Failed     : {failed}")
print(f"📁  Saved to   : {DATA_DIR}")
print("\n💡 Next: python main.py → Option 1")