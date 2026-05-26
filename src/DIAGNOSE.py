"""
DIAGNOSE.py - Run this from your src\ folder to see exactly what's happening
    python DIAGNOSE.py
"""
import os, pandas as pd, numpy as np

HERE = os.path.dirname(os.path.realpath(__file__))
DATA = os.path.join(HERE, "data")

# Pick first CSV
import glob
files = glob.glob(os.path.join(DATA, "*.csv"))
if not files:
    print("No CSV files found in", DATA); exit()

fp = files[0]
sym = os.path.basename(fp).replace(".csv","")
print(f"Diagnosing: {fp}")
print("="*60)

df = pd.read_csv(fp)
print(f"Shape: {df.shape}")
print(f"Columns: {list(df.columns)}")
print(f"\nFirst 3 rows:")
print(df.head(3).to_string())
print(f"\nData types:")
print(df.dtypes)
print(f"\nNull counts:")
print(df.isnull().sum())

# Simulate what the pipeline does
df.columns = [c.strip().lower().replace(" ","_").replace("%","pct") for c in df.columns]
df["date"] = pd.to_datetime(df["date"], errors="coerce")
df.dropna(subset=["date"], inplace=True)
for col in ["open","high","low","close","volume"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace(",",""), errors="coerce")

df.dropna(subset=["date","open","high","low","close","volume"], inplace=True)
df.sort_values("date", inplace=True)
print(f"\nAfter cleaning: {len(df)} rows")

# Feature engineering
df["daily_return"]     = df["close"].pct_change()
df["daily_return_pct"] = df["daily_return"] * 100
df["sma_20"]           = df["close"].rolling(20, min_periods=1).mean()

# RSI FIXED
delta = df["close"].diff()

gain = np.where(delta > 0, delta, 0)
loss = np.where(delta < 0, -delta, 0)

gain = pd.Series(gain, index=df.index)
loss = pd.Series(loss, index=df.index)

avg_gain = gain.rolling(window=14, min_periods=14).mean()
avg_loss = loss.rolling(window=14, min_periods=14).mean()

# Avoid divide-by-zero
avg_loss = avg_loss.replace(0, 0.0001)

rs = avg_gain / avg_loss

df["rsi"] = 100 - (100 / (1 + rs))

# MACD
df["macd"] = df["close"].ewm(span=12,adjust=False).mean() - df["close"].ewm(span=26,adjust=False).mean()
df["volatility"] = df["daily_return_pct"].rolling(10, min_periods=1).std()
df["target_next_close"] = df["close"].shift(-1)

print(f"\nAfter features: {len(df)} rows")
print(f"\nNull counts after features:")
key = ["open","high","low","close","volume","rsi","macd","sma_20","target_next_close"]
for c in key:
    if c in df.columns:
        print(f"  {c}: {df[c].isnull().sum()} nulls")

print(f"\nAfter dropna(subset=key): {df.dropna(subset=key).shape[0]} rows remain")
print(f"After dropna(all): {df.dropna().shape[0]} rows remain")

print("\n" + "="*60)
print("RSI sample (first 5):", df['rsi'].head().values)
print("MACD sample (first 5):", df['macd'].head().values)