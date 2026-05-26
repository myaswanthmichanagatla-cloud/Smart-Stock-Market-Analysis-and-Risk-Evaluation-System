import os
import glob
import json
import numpy as np
import pandas as pd
import warnings

warnings.filterwarnings('ignore')

# Resolve base directory relative to THIS file — works on any OS
_BASE_DIR = os.path.dirname(os.path.realpath(__file__))


class StockDataPipeline:
    """
    GenAI-Enhanced Stock Data Pipeline:
    - Load multiple NSE CSV files
    - Clean NSE-specific format
    - Merge all stocks
    - Feature engineering
    - Technical indicators (RSI, MACD, Bollinger)
    - Risk labels
    - Trend labels
    - Retrieval-ready text summaries

    FIXES APPLIED:
    - __init__ paths now dynamic (relative to script, not cwd)
    - save_rag_knowledge_base path now dynamic
    - dropna() changed to subset-only (was wiping all rows)
    - RSI division by zero handled
    - MACD edge cases handled
    """

<<<<<<< HEAD
    def __init__(self, data_folder=None, output_file=None):
        self.data_folder = data_folder or os.path.join(_BASE_DIR, "data")
        self.output_file = output_file or os.path.join(_BASE_DIR, "data", "stock_dataset.csv")
        self.combined_df  = None
=======
    def __init__(
        self,
        data_folder="data",
        output_file="data/stock_dataset.csv"
    ):
        self.data_folder = data_folder
        self.output_file = output_file
        self.combined_df = None
>>>>>>> 61548e8b50024a25c8c25fef6b487fbb4b8af334
        self.required_cols = ["open", "high", "low", "close", "volume"]

    # =========================================
    # RSI (FIXED: Handle division by zero)
    # =========================================
    def calculate_rsi(self, series, window=14):
        try:
            delta = series.diff()
            gain = np.where(delta > 0, delta, 0)
            loss = np.where(delta < 0, -delta, 0)
            avg_gain = pd.Series(gain).rolling(window=window, min_periods=1).mean()
            avg_loss = pd.Series(loss).rolling(window=window, min_periods=1).mean()
            rs  = avg_gain / avg_loss.replace(0, np.nan)
            rsi = 100 - (100 / (1 + rs))
            return rsi
        except Exception as e:
            print(f"   ⚠️  RSI calculation warning: {str(e)}")
            return pd.Series([50] * len(series), index=series.index)

    # =========================================
    # MACD (FIXED: Handle edge cases)
    # =========================================
    def calculate_macd(self, series):
        try:
            if len(series) < 26:
                print(f"   ⚠️  MACD requires 26+ data points, returning zeros")
                z = pd.Series([0] * len(series), index=series.index)
                return z, z
            ema_12  = series.ewm(span=12, adjust=False).mean()
            ema_26  = series.ewm(span=26, adjust=False).mean()
            macd    = ema_12 - ema_26
            signal  = macd.ewm(span=9, adjust=False).mean()
            return macd, signal
        except Exception as e:
            print(f"   ⚠️  MACD calculation warning: {str(e)}")
            z = pd.Series([0] * len(series), index=series.index)
            return z, z

    # =========================================
    # BOLLINGER BANDS (FIXED: Handle std=0)
    # =========================================
    def calculate_bollinger_bands(self, series, window=20):
        try:
            sma = series.rolling(window=window, min_periods=1).mean()
            std = series.rolling(window=window, min_periods=1).std().replace(0, 1)
            return sma + (2 * std), sma - (2 * std)
        except Exception as e:
            print(f"   ⚠️  Bollinger Bands warning: {str(e)}")
            return series, series

    # =========================================
    # RISK LABEL
    # =========================================
    def classify_risk(self, volatility):
        if pd.isna(volatility):
            return "Unknown"
        elif volatility < 1:
            return "Low Risk"
        elif volatility < 2:
            return "Moderate Risk"
        else:
            return "High Risk"

    # =========================================
    # TREND LABEL
    # =========================================
    def classify_trend(self, close, sma_20):
        if pd.isna(close) or pd.isna(sma_20):
            return "Unknown"
        elif close > sma_20:
            return "Bullish"
        elif close < sma_20:
            return "Bearish"
        else:
            return "Neutral"

    # =========================================
    # GENERATE RETRIEVAL TEXT
    # =========================================
    def generate_text_summary(self, row):
        try:
            date_val = row.get('date', 'N/A')
            date_str = date_val.date() if pd.notnull(date_val) else 'N/A'
            return (
                f"{row.get('stock_symbol','N/A')} on {date_str} "
                f"had close price {row.get('close',0):.2f}, "
                f"daily return {row.get('daily_return_pct',0):.2f}%, "
                f"RSI {row.get('rsi',50):.2f}, "
                f"MACD {row.get('macd',0):.2f}, "
                f"trend {row.get('trend_label','Unknown')}, "
                f"risk category {row.get('risk_category','Unknown')}."
            )
        except Exception as e:
            return f"Error generating summary: {str(e)}"

    # =========================================
    # PROCESS SINGLE FILE
    # =========================================
    def process_single_stock(self, file_path):
        stock_symbol = os.path.basename(file_path).replace(".csv", "").upper()
        print(f"\n📥 Processing: {stock_symbol}")

        try:
            df = pd.read_csv(file_path)

            # Standardize column names
            df.columns = [
                col.strip().lower().replace(" ", "_").replace("%", "pct")
                for col in df.columns
            ]
            print(f"   Original columns: {list(df.columns)}")

            # Rename common NSE columns
            rename_map = {
                "prevclose": "prev_close",
                "pctdeliverble": "pct_deliverable",
                "%deliverble": "pct_deliverable",
                "deliverable_volume": "deliverable_volume",
                "last": "last_price",
                "turnover (lacs)": "turnover"
            }
            df.rename(columns=rename_map, inplace=True)
            df["stock_symbol"] = stock_symbol

            # Date validation
            if "date" not in df.columns:
                raise ValueError(f"❌ Missing 'date' column in {stock_symbol}")
            # Handle multiple date formats including DD-Mon-YYYY (NSE format)
            for fmt in ["%d-%b-%Y", "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", None]:
                try:
                    if fmt:
                        parsed = pd.to_datetime(df["date"], format=fmt, errors="coerce")
                    else:
                        parsed = pd.to_datetime(df["date"], dayfirst=True, errors="coerce")
                    valid = parsed.notna().sum()
                    if valid > len(df) * 0.8:  # 80%+ rows parsed OK
                        df["date"] = parsed
                        break
                except Exception:
                    continue
            df.dropna(subset=["date"], inplace=True)

            # Column fallbacks
            alt_names = {
                "open":   ["open", "open_price"],
                "high":   ["high", "high_price", "day_high"],
                "low":    ["low",  "low_price",  "day_low"],
                "close":  ["close","close_price","last"],
                "volume": ["volume","vol","trade_volume"]
            }
            for col in self.required_cols:
                if col not in df.columns:
                    for alt in alt_names.get(col, []):
                        if alt in df.columns:
                            df.rename(columns={alt: col}, inplace=True)
                            break

            # Numeric conversion
            numeric_cols = self.required_cols + [
                "prev_close","volume","turnover","trades",
                "deliverable_volume","pct_deliverable"
            ]
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(
                        df[col].astype(str).str.replace(",", ""),
                        errors="coerce"
                    )

            # Drop rows missing essential price/volume columns
            initial_rows = len(df)
            df.dropna(subset=["date","open","high","low","close","volume"], inplace=True)
            removed = initial_rows - len(df)
            if removed > 0:
                print(f"   🧹 Removed {removed} rows with missing values")

            if len(df) < 5:
                raise ValueError(f"Not enough data after cleaning: {len(df)} rows")

            df.sort_values("date", inplace=True)

            # ── Feature Engineering ────────────────────────────────────────
            df["daily_return"]     = df["close"].pct_change()
            df["daily_return_pct"] = df["daily_return"] * 100
            df["price_range"]      = df["high"] - df["low"]
            df["price_change"]     = df["close"] - df["open"]
            df["sma_5"]            = df["close"].rolling(5,  min_periods=1).mean()
            df["sma_20"]           = df["close"].rolling(20, min_periods=1).mean()
            df["ema_10"]           = df["close"].ewm(span=10, adjust=False).mean()
            df["volatility"]       = df["daily_return_pct"].rolling(10, min_periods=1).std()

            df["rsi"]                                    = self.calculate_rsi(df["close"])
            df["rsi"] = df["rsi"].fillna(50)  # Fill leading NaNs
            df["macd"], df["macd_signal"]               = self.calculate_macd(df["close"])
            df["bollinger_upper"], df["bollinger_lower"] = self.calculate_bollinger_bands(df["close"])

            df["momentum_3"]   = df["close"] - df["close"].shift(3)
            df["volume_ma_5"]  = df["volume"].rolling(5, min_periods=1).mean()
            df["risk_category"]= df["volatility"].apply(self.classify_risk)
            df["trend_label"]  = df.apply(
                lambda row: self.classify_trend(row["close"], row["sma_20"]), axis=1
            )
            df["target_next_close"] = df["close"].shift(-1)

            # ── FIX: only drop rows missing KEY columns, not ALL columns ──
            initial_rows = len(df)
            key_cols = ["open","high","low","close","volume",
                        "rsi","macd","sma_20","target_next_close"]
            df.dropna(subset=key_cols, inplace=True)
            removed = initial_rows - len(df)
            if removed > 0:
                print(f"   🧹 Removed {removed} rows after feature engineering")

            if len(df) < 5:
                raise ValueError(f"Not enough data after feature engineering: {len(df)} rows")

            df["text_summary"] = df.apply(self.generate_text_summary, axis=1)
            print(f"   ✅ Final rows for {stock_symbol}: {len(df)}")
            return df

        except Exception as e:
            print(f"   ❌ Failed to process {stock_symbol}: {str(e)}")
            return None

    # =========================================
    # LOAD ALL STOCKS
    # =========================================
    def load_all_stocks(self):
        all_files = glob.glob(os.path.join(self.data_folder, "*.csv"))

        if len(all_files) == 0:
            raise FileNotFoundError(f"❌ No CSV files found in {self.data_folder}")

        print(f"\n🔍 Found {len(all_files)} CSV files")

        all_data, failed_files = [], []

        for file_path in all_files:
            try:
                stock_df = self.process_single_stock(file_path)
                if stock_df is not None and len(stock_df) > 0:
                    all_data.append(stock_df)
                else:
                    failed_files.append(os.path.basename(file_path))
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
                failed_files.append(os.path.basename(file_path))

        if len(all_data) == 0:
            raise ValueError("❌ No valid stock files processed")

        self.combined_df = pd.concat(all_data, ignore_index=True)
        self.combined_df.sort_values(by=["stock_symbol","date"], inplace=True)

        print("\n" + "=" * 70)
        print("📊 FINAL DATASET SUMMARY")
        print("=" * 70)
        print(f"✅ Total Rows      : {len(self.combined_df)}")
        print(f"✅ Stocks Covered  : {self.combined_df['stock_symbol'].nunique()}")
        print(f"✅ Columns         : {len(self.combined_df.columns)}")
        print(f"✅ Date Range      : {self.combined_df['date'].min().date()} to {self.combined_df['date'].max().date()}")

        if failed_files:
            print(f"\n⚠️  Failed files ({len(failed_files)}):")
            for f in failed_files[:5]:
                print(f"   - {f}")
        print("=" * 70)
        return self.combined_df

    # =========================================
    # SAVE DATASET
    # =========================================
    def save_dataset(self):
        if self.combined_df is None:
            raise ValueError("❌ Run load_all_stocks() first")
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        df_sorted = self.combined_df.sort_values("date")
        df_sorted.to_csv(self.output_file, index=False)
        print(f"\n✅ Dataset saved at: {self.output_file}")
        print(f"   Rows: {len(df_sorted)}")
        print(f"   Size: {os.path.getsize(self.output_file)/1024:.2f} KB")

    # =========================================
    # SAVE RAG KNOWLEDGE BASE (path now dynamic)
    # =========================================
<<<<<<< HEAD
    def save_rag_knowledge_base(self, output_json=None):
=======
    def save_rag_knowledge_base(
        self,
        output_json="data/rag_knowledge_base.json"
    ):
>>>>>>> 61548e8b50024a25c8c25fef6b487fbb4b8af334
        if self.combined_df is None:
            raise ValueError("❌ Run load_all_stocks() first")
        if output_json is None:
            output_json = os.path.join(_BASE_DIR, "data", "rag_knowledge_base.json")
        knowledge_base = self.combined_df[
            ["stock_symbol","date","close","text_summary","trend_label","risk_category","rsi"]
        ].to_dict(orient="records")
        os.makedirs(os.path.dirname(output_json), exist_ok=True)
        with open(output_json, "w") as f:
            json.dump(knowledge_base, f, indent=4, default=str)
        print(f"✅ RAG knowledge base saved at: {output_json}")
        print(f"   Records: {len(knowledge_base)}")


# =========================================
# MAIN EXECUTION
# =========================================
if __name__ == "__main__":
    try:
        print("=" * 70)
        print("🤖 GENAI STOCK DATA PIPELINE - PRODUCTION READY")
        print("=" * 70)

        pipeline = StockDataPipeline()
        pipeline.load_all_stocks()
        pipeline.save_dataset()
        pipeline.save_rag_knowledge_base()

        print("\n" + "=" * 70)
        print("✅ GENAI DATA PIPELINE COMPLETED SUCCESSFULLY")
        print("=" * 70)
        print("\n📁 Files created:")
        print(f"   1. {pipeline.output_file}")
        print(f"   2. {os.path.join(_BASE_DIR, 'data', 'rag_knowledge_base.json')}")
        print("=" * 70 + "\n")

    except FileNotFoundError as e:
        print(f"\n❌ FILE ERROR: {e}")
        print(f"\n💡 SOLUTION: Place CSV files in the 'data' folder next to this script.")
    except ValueError as e:
        print(f"\n❌ DATA ERROR: {e}")
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {str(e)}")
        import traceback
        traceback.print_exc()