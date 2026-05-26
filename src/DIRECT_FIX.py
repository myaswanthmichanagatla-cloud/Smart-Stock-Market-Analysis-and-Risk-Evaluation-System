"""
DIRECT_FIX.py
=============
Place this file in your src\ folder and run:
    python DIRECT_FIX.py

It will directly overwrite the broken sections in all 3 files.
"""

import os
import sys

HERE = os.path.dirname(os.path.realpath(__file__))
print(f"Working in: {HERE}")
print("=" * 60)

# ─────────────────────────────────────────────────────────────
# 1. Completely rewrite stock_data_pipeline.py
# ─────────────────────────────────────────────────────────────
pipeline_path = os.path.join(HERE, "stock_data_pipeline.py")
print(f"\n[1/3] Rewriting: {pipeline_path}")

new_pipeline = r'''
import os
import glob
import json
import numpy as np
import pandas as pd
import warnings

warnings.filterwarnings('ignore')

_BASE_DIR = os.path.dirname(os.path.realpath(__file__))


class StockDataPipeline:

    def __init__(self, data_folder=None, output_file=None):
        self.data_folder   = data_folder  or os.path.join(_BASE_DIR, "data")
        self.output_file   = output_file  or os.path.join(_BASE_DIR, "data", "stock_dataset.csv")
        self.combined_df   = None
        self.required_cols = ["open", "high", "low", "close", "volume"]

    def calculate_rsi(self, series, window=14):
        try:
            delta    = series.diff()
            gain     = np.where(delta > 0, delta, 0)
            loss     = np.where(delta < 0, -delta, 0)
            avg_gain = pd.Series(gain).rolling(window=window, min_periods=1).mean()
            avg_loss = pd.Series(loss).rolling(window=window, min_periods=1).mean()
            rs       = avg_gain / avg_loss.replace(0, np.nan)
            return 100 - (100 / (1 + rs))
        except Exception as e:
            print(f"   RSI warning: {e}")
            return pd.Series([50] * len(series), index=series.index)

    def calculate_macd(self, series):
        try:
            if len(series) < 26:
                z = pd.Series([0] * len(series), index=series.index)
                return z, z
            ema_12 = series.ewm(span=12, adjust=False).mean()
            ema_26 = series.ewm(span=26, adjust=False).mean()
            macd   = ema_12 - ema_26
            signal = macd.ewm(span=9, adjust=False).mean()
            return macd, signal
        except Exception as e:
            print(f"   MACD warning: {e}")
            z = pd.Series([0] * len(series), index=series.index)
            return z, z

    def calculate_bollinger_bands(self, series, window=20):
        try:
            sma = series.rolling(window=window, min_periods=1).mean()
            std = series.rolling(window=window, min_periods=1).std().replace(0, 1)
            return sma + (2 * std), sma - (2 * std)
        except Exception as e:
            return series, series

    def classify_risk(self, v):
        if pd.isna(v):   return "Unknown"
        elif v < 1:      return "Low Risk"
        elif v < 2:      return "Moderate Risk"
        else:            return "High Risk"

    def classify_trend(self, close, sma_20):
        if pd.isna(close) or pd.isna(sma_20): return "Unknown"
        elif close > sma_20: return "Bullish"
        elif close < sma_20: return "Bearish"
        else:                return "Neutral"

    def generate_text_summary(self, row):
        try:
            d = row.get("date", "N/A")
            d = d.date() if pd.notnull(d) else "N/A"
            return (
                f"{row.get('stock_symbol','N/A')} on {d} "
                f"had close price {row.get('close',0):.2f}, "
                f"daily return {row.get('daily_return_pct',0):.2f}%, "
                f"RSI {row.get('rsi',50):.2f}, MACD {row.get('macd',0):.2f}, "
                f"trend {row.get('trend_label','Unknown')}, "
                f"risk category {row.get('risk_category','Unknown')}."
            )
        except Exception as e:
            return f"Error: {e}"

    def process_single_stock(self, file_path):
        stock_symbol = os.path.basename(file_path).replace(".csv", "").upper()
        print(f"\n  Processing: {stock_symbol}")
        try:
            df = pd.read_csv(file_path)
            df.columns = [c.strip().lower().replace(" ","_").replace("%","pct") for c in df.columns]
            print(f"   Columns: {list(df.columns)}")

            rename_map = {
                "prevclose":"prev_close","pctdeliverble":"pct_deliverable",
                "%deliverble":"pct_deliverable","last":"last_price",
                "turnover (lacs)":"turnover"
            }
            df.rename(columns=rename_map, inplace=True)
            df["stock_symbol"] = stock_symbol

            if "date" not in df.columns:
                raise ValueError(f"Missing date column")
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
            df.dropna(subset=["date"], inplace=True)

            alt = {
                "open":["open","open_price"],"high":["high","high_price","day_high"],
                "low":["low","low_price","day_low"],"close":["close","close_price","last"],
                "volume":["volume","vol","trade_volume"]
            }
            for col in self.required_cols:
                if col not in df.columns:
                    for a in alt.get(col,[]):
                        if a in df.columns:
                            df.rename(columns={a:col}, inplace=True); break

            for col in self.required_cols + ["prev_close","volume","turnover","trades"]:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col].astype(str).str.replace(",",""), errors="coerce")

            n0 = len(df)
            df.dropna(subset=["date","open","high","low","close","volume"], inplace=True)
            r = n0 - len(df)
            if r > 0: print(f"   Removed {r} rows with missing values")
            if len(df) < 5: raise ValueError(f"Not enough data: {len(df)} rows")

            df.sort_values("date", inplace=True)

            df["daily_return"]     = df["close"].pct_change()
            df["daily_return_pct"] = df["daily_return"] * 100
            df["price_range"]      = df["high"] - df["low"]
            df["price_change"]     = df["close"] - df["open"]
            df["sma_5"]            = df["close"].rolling(5,  min_periods=1).mean()
            df["sma_20"]           = df["close"].rolling(20, min_periods=1).mean()
            df["ema_10"]           = df["close"].ewm(span=10, adjust=False).mean()
            df["volatility"]       = df["daily_return_pct"].rolling(10, min_periods=1).std()
            df["rsi"]                                     = self.calculate_rsi(df["close"])
            df["macd"], df["macd_signal"]                = self.calculate_macd(df["close"])
            df["bollinger_upper"], df["bollinger_lower"] = self.calculate_bollinger_bands(df["close"])
            df["momentum_3"]        = df["close"] - df["close"].shift(3)
            df["volume_ma_5"]       = df["volume"].rolling(5, min_periods=1).mean()
            df["risk_category"]     = df["volatility"].apply(self.classify_risk)
            df["trend_label"]       = df.apply(lambda r: self.classify_trend(r["close"], r["sma_20"]), axis=1)
            df["target_next_close"] = df["close"].shift(-1)

            # KEY FIX: only drop rows missing essential columns, not ALL columns
            n0 = len(df)
            key = ["open","high","low","close","volume","rsi","macd","sma_20","target_next_close"]
            df.dropna(subset=key, inplace=True)
            r = n0 - len(df)
            if r > 0: print(f"   Removed {r} rows after feature engineering")
            if len(df) < 5: raise ValueError(f"Not enough data after features: {len(df)} rows")

            df["text_summary"] = df.apply(self.generate_text_summary, axis=1)
            print(f"   OK {stock_symbol}: {len(df)} rows")
            return df

        except Exception as e:
            print(f"   FAILED {stock_symbol}: {e}")
            return None

    def load_all_stocks(self):
        files = glob.glob(os.path.join(self.data_folder, "*.csv"))
        if not files:
            raise FileNotFoundError(f"No CSV files found in {self.data_folder}")
        print(f"\nFound {len(files)} CSV files in {self.data_folder}")
        all_data, failed = [], []
        for fp in files:
            try:
                s = self.process_single_stock(fp)
                if s is not None and len(s) > 0:
                    all_data.append(s)
                else:
                    failed.append(os.path.basename(fp))
            except Exception as e:
                print(f"   Error: {e}"); failed.append(os.path.basename(fp))
        if not all_data:
            raise ValueError("No valid stock files processed")
        self.combined_df = pd.concat(all_data, ignore_index=True)
        self.combined_df.sort_values(["stock_symbol","date"], inplace=True)
        print(f"\nTotal rows: {len(self.combined_df)} | Stocks: {self.combined_df['stock_symbol'].nunique()}")
        if failed: print(f"Failed: {failed}")
        return self.combined_df

    def save_dataset(self):
        if self.combined_df is None: raise ValueError("Run load_all_stocks() first")
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        self.combined_df.sort_values("date").to_csv(self.output_file, index=False)
        print(f"\nDataset saved: {self.output_file}  ({len(self.combined_df)} rows)")

    def save_rag_knowledge_base(self, output_json=None):
        if self.combined_df is None: raise ValueError("Run load_all_stocks() first")
        if output_json is None:
            output_json = os.path.join(_BASE_DIR, "data", "rag_knowledge_base.json")
        os.makedirs(os.path.dirname(output_json), exist_ok=True)
        kb = self.combined_df[
            ["stock_symbol","date","close","text_summary","trend_label","risk_category","rsi"]
        ].to_dict(orient="records")
        with open(output_json, "w") as f:
            json.dump(kb, f, indent=4, default=str)
        print(f"RAG KB saved: {output_json}  ({len(kb)} records)")


if __name__ == "__main__":
    try:
        print("=" * 60)
        print("GENAI STOCK DATA PIPELINE")
        print("=" * 60)
        p = StockDataPipeline()
        p.load_all_stocks()
        p.save_dataset()
        p.save_rag_knowledge_base()
        print("\nPIPELINE COMPLETED SUCCESSFULLY")
    except FileNotFoundError as e:
        print(f"\nFILE ERROR: {e}")
    except ValueError as e:
        print(f"\nDATA ERROR: {e}")
    except Exception as e:
        import traceback; traceback.print_exc()
'''

with open(pipeline_path, "w", encoding="utf-8") as f:
    f.write(new_pipeline)
print(f"   Written {len(new_pipeline)} bytes")

# Verify the fix is present
with open(pipeline_path, encoding="utf-8") as f:
    content = f.read()
if 'dropna(subset=key, inplace=True)' in content:
    print("   VERIFIED: dropna fix is present")
else:
    print("   ERROR: fix not found!")

# ─────────────────────────────────────────────────────────────
# 2. Fix baseline_predictor.py
# ─────────────────────────────────────────────────────────────
baseline_path = os.path.join(HERE, "baseline_predictor.py")
print(f"\n[2/3] Fixing: {baseline_path}")

if not os.path.exists(baseline_path):
    print("   NOT FOUND — skipping")
else:
    with open(baseline_path, encoding="utf-8") as f:
        txt = f.read()

    # Find the __main__ block and replace the path lines
    fixed = False
    lines = txt.splitlines()
    out   = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # Detect the hardcoded Colab path lines
        if ('DATA_PATH' in line and '/content/' in line) or \
           ('MODEL_PATH' in line and '/content/' in line and 'baseline' in line.lower()):
            # Skip until we've consumed both DATA_PATH and MODEL_PATH lines
            consumed = 0
            while i < len(lines) and consumed < 2:
                if 'DATA_PATH' in lines[i] or 'MODEL_PATH' in lines[i]:
                    consumed += 1
                i += 1
            # Insert the fixed paths
            out.append('    _BASE      = os.path.dirname(os.path.realpath(__file__))')
            out.append('    DATA_PATH  = os.path.join(_BASE, "data",   "stock_dataset.csv")')
            out.append('    MODEL_PATH = os.path.join(_BASE, "models", "baseline_model.pkl")')
            out.append('    os.makedirs(os.path.join(_BASE, "models"), exist_ok=True)')
            fixed = True
            continue
        out.append(line)
        i += 1

    if fixed:
        with open(baseline_path, "w", encoding="utf-8") as f:
            f.write("\n".join(out))
        print("   Fixed hardcoded Colab path")
    else:
        print("   Path already fixed or pattern not found — checking...")
        if '_BASE' in txt:
            print("   Already contains _BASE — looks good")
        else:
            print("   WARNING: Could not fix automatically")

# ─────────────────────────────────────────────────────────────
# 3. Fix advanced_predictor.py
# ─────────────────────────────────────────────────────────────
advanced_path = os.path.join(HERE, "advanced_predictor.py")
print(f"\n[3/3] Fixing: {advanced_path}")

if not os.path.exists(advanced_path):
    print("   NOT FOUND — skipping")
else:
    with open(advanced_path, encoding="utf-8") as f:
        txt = f.read()

    lines = txt.splitlines()
    out   = []
    i     = 0
    fixed = False
    while i < len(lines):
        line = lines[i]
        if ('DATA_PATH' in line and '/content/' in line) or \
           ('MODEL_PATH' in line and '/content/' in line and 'advanced' in line.lower()):
            consumed = 0
            while i < len(lines) and consumed < 2:
                if 'DATA_PATH' in lines[i] or 'MODEL_PATH' in lines[i]:
                    consumed += 1
                i += 1
            out.append('    _BASE      = os.path.dirname(os.path.realpath(__file__))')
            out.append('    DATA_PATH  = os.path.join(_BASE, "data",   "stock_dataset.csv")')
            out.append('    MODEL_PATH = os.path.join(_BASE, "models", "advanced_model.pkl")')
            out.append('    os.makedirs(os.path.join(_BASE, "models"), exist_ok=True)')
            fixed = True
            continue
        out.append(line)
        i += 1

    if fixed:
        with open(advanced_path, "w", encoding="utf-8") as f:
            f.write("\n".join(out))
        print("   Fixed hardcoded Colab path")
    else:
        if '_BASE' in txt:
            print("   Already contains _BASE — looks good")
        else:
            print("   WARNING: Could not fix automatically")

# ─────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("ALL DONE — now run:")
print("   python main.py")
print("   Choose Option 1")
print("=" * 60)