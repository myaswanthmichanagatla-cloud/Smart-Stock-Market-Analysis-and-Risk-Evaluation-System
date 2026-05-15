
import os
import joblib
import numpy as np
import pandas as pd
import json
import warnings

warnings.filterwarnings('ignore')

from sklearn.linear_model import LinearRegression
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)
from sklearn.model_selection import train_test_split


class GenAIBaselinePredictor:
    """
    GenAI-Enhanced Baseline Predictor using Linear Regression
    
    FIX: Categorical columns (trend_label, risk_category) are NOT used as features
    They are only kept for RAG text summaries and context
    """

    def __init__(self):
        self.model = LinearRegression()
        self.feature_names = None
        self.stock_symbol = None
        self.is_multi_stock = False
        self.genai_features = ["rsi", "macd"]  # Only numeric GenAI features

    # =========================================
    # DATA PREPARATION - GENAI ENHANCED
    # =========================================
    def prepare_data(self, df, stock_symbol=None):
        """
        Prepares data with all GenAI features
        FIX: Exclude categorical columns from features
        """
        df = df.copy()

        print(f"\n🤖 GENAI DATA PREPARATION STARTED")
        print(f"   Initial shape: {df.shape}")

        # -------------------------------
        # Check if stock_symbol column exists
        # -------------------------------
        if "stock_symbol" not in df.columns:
            if stock_symbol:
                raise ValueError("Column 'stock_symbol' not found in dataset")
            else:
                print(f"   ⚠️  No 'stock_symbol' column. Using multi-stock mode.")
                self.is_multi_stock = True
        else:
            if stock_symbol:
                df = df[df["stock_symbol"] == stock_symbol].copy()
                self.stock_symbol = stock_symbol
                self.is_multi_stock = False

                if len(df) == 0:
                    raise ValueError(f"No data for stock: {stock_symbol}")

                print(f"   📈 Filtered: {stock_symbol} ({len(df)} rows)")

        # -------------------------------
        # Date handling
        # -------------------------------
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
            df.dropna(subset=["date"], inplace=True)
            df.sort_values("date", inplace=True)

        # -------------------------------
        # Required columns
        # -------------------------------
        required_cols = ["open", "high", "low", "close", "volume"]
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            raise ValueError(f"Missing columns: {missing}")

        # Numeric conversion
        for col in required_cols + ["prev_close"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # Clean
        df.dropna(subset=required_cols, inplace=True)
        if len(df) < 20:
            raise ValueError(f"Not enough data: {len(df)} rows")

        print(f"   ✅ Cleaned rows: {len(df)}")

        # -------------------------------
        # GENAI FEATURE ENGINEERING (25+ features)
        # -------------------------------
        
        # Basic features
        df["prev_close"] = df["close"].shift(1)
        df["price_range"] = df["high"] - df["low"]
        df["price_change"] = df["close"] - df["open"]
        df["return_pct"] = ((df["close"] - df["open"]) / df["open"]) * 100

        # Moving averages
        df["sma_3"] = df["close"].rolling(3, min_periods=1).mean()
        df["sma_5"] = df["close"].rolling(5, min_periods=1).mean()
        df["sma_20"] = df["close"].rolling(20, min_periods=1).mean()
        df["ema_10"] = df["close"].ewm(span=10, adjust=False, min_periods=1).mean()
        df["volume_ma_5"] = df["volume"].rolling(5, min_periods=1).mean()

        # Volatility
        df["volatility"] = df["return_pct"].rolling(10, min_periods=1).std()

        # Momentum
        df["momentum_3"] = df["close"] - df["close"].shift(3)
        df["momentum_5"] = df["close"] - df["close"].shift(5)

        # =========================================
        # GENAI TECHNICAL INDICATORS (NUMERIC ONLY)
        # =========================================
        
        # RSI
        delta = df["close"].diff()
        gain = np.where(delta > 0, delta, 0)
        loss = np.where(delta < 0, -delta, 0)
        avg_gain = pd.Series(gain).rolling(14, min_periods=1).mean()
        avg_loss = pd.Series(loss).rolling(14, min_periods=1).mean()
        rs = avg_gain / avg_loss.replace(0, np.nan)
        df["rsi"] = 100 - (100 / (1 + rs))

        # MACD
        ema_12 = df["close"].ewm(span=12, adjust=False, min_periods=1).mean()
        ema_26 = df["close"].ewm(span=26, adjust=False, min_periods=1).mean()
        df["macd"] = ema_12 - ema_26
        df["macd_signal"] = df["macd"].ewm(span=9, adjust=False, min_periods=1).mean()

        # Bollinger Bands
        sma = df["close"].rolling(20, min_periods=1).mean()
        std = df["close"].rolling(20, min_periods=1).std().replace(0, 1)
        df["bollinger_upper"] = sma + (2 * std)
        df["bollinger_lower"] = sma - (2 * std)
        df["bollinger_width"] = df["bollinger_upper"] - df["bollinger_lower"]

        # =========================================
        # GENAI LABELS (KEEP FOR CONTEXT, NOT FEATURES)
        # =========================================
        
        # Trend (categorical - for RAG only)
        df["trend_label"] = df.apply(
            lambda row: "Bullish" if row["close"] > row["sma_20"] 
                      else "Bearish" if row["close"] < row["sma_20"] 
                      else "Neutral",
            axis=1
        )

        # Risk (categorical - for RAG only)
        df["risk_category"] = df["volatility"].apply(
            lambda x: "Low Risk" if pd.notnull(x) and x < 1 
                      else "Moderate Risk" if pd.notnull(x) and x < 2 
                      else "High Risk" if pd.notnull(x) 
                      else "Unknown"
        )

        # =========================================
        # GENAI TEXT SUMMARY (USES CATEGORICAL COLUMNS)
        # =========================================
        df["text_summary"] = df.apply(
            lambda row: (
                f"{row.get('stock_symbol', 'N/A')} on {pd.to_datetime(row.get('date')).date() if pd.notnull(row.get('date')) else 'N/A'} "
                f"closed at {row.get('close', 0):.2f}. "
                f"RSI: {row.get('rsi', 50):.2f}, "
                f"MACD: {row.get('macd', 0):.2f}, "
                f"Trend: {row.get('trend_label', 'Unknown')}, "
                f"Risk: {row.get('risk_category', 'Unknown')}."
            ),
            axis=1
        )

        # Target
        df["target"] = df["close"].shift(-1)

        # Drop NaNs
        df.dropna(inplace=True)

        if len(df) < 20:
            raise ValueError(f"Not enough data after features: {len(df)} rows")

        print(f"   ✅ Features engineered: {len(df)} rows")

        # -------------------------------
        # FEATURE SELECTION (NUMERIC ONLY - FIX)
        # -------------------------------
        features = [
            # Basic OHLCV
            "open", "high", "low", "close", "volume",
            "prev_close",
            
            # Derived
            "price_range", "price_change", "return_pct",
            
            # Moving Averages
            "sma_3", "sma_5", "sma_20", "ema_10",
            "volume_ma_5",
            
            # Momentum
            "momentum_3", "momentum_5",
            
            # Volatility
            "volatility",
            
            # GENAI Technical Indicators (NUMERIC ONLY)
            "rsi", "macd", "macd_signal",
            "bollinger_upper", "bollinger_lower", "bollinger_width"
        ]

        # Filter only existing columns
        features = [f for f in features if f in df.columns]

        # ⚠️ EXCLUDE categorical columns from features
        categorical_cols = ["trend_label", "risk_category", "text_summary", "date", "stock_symbol"]
        features = [f for f in features if f not in categorical_cols]

        self.feature_names = features

        X = df[features].copy()
        y = df["target"].copy()

        print(f"   ✅ Numeric Features: {len(features)}")
        print(f"   ✅ Shape: {X.shape}")
        print(f"   ⚠️  Excluded (categorical): trend_label, risk_category")

        # Train/Test Split (NO SHUFFLE for time series)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, shuffle=False
        )

        print(f"\n{'='*60}")
        print(f"✅ GENAI DATA PREPARATION COMPLETE")
        print(f"{'='*60}")
        print(f"📊 Total Samples  : {len(df)}")
        print(f"🏋️  Train         : {len(X_train)}")
        print(f"🧪  Test          : {len(X_test)}")
        print(f"🔧 Features      : {len(features)}")
        if self.stock_symbol:
            print(f"📈 Stock         : {self.stock_symbol}")
        else:
            print(f"📊 Mode          : Multi-Stock")
        print(f"🤖 GenAI Features: RSI, MACD (numeric only)")
        print(f"📝 Context Only  : trend_label, risk_category (for RAG)")
        print(f"{'='*60}\n")

        return X_train, X_test, y_train, y_test

    # =========================================
    # TRAIN MODEL
    # =========================================
    def train(self, X_train, y_train):
        try:
            self.model.fit(X_train, y_train)
            print(f"✅ Baseline Model Trained")
            print(f"   Samples: {len(X_train)} | Features: {len(X_train.columns)}")
        except Exception as e:
            print(f"❌ Training failed: {str(e)}")
            raise

    # =========================================
    # PREDICT
    # =========================================
    def predict(self, X_test):
        try:
            predictions = self.model.predict(X_test)
            print(f"✅ Predictions: {len(predictions)} samples")
            return predictions
        except Exception as e:
            print(f"❌ Prediction failed: {str(e)}")
            raise

    # =========================================
    # EVALUATE
    # =========================================
    def evaluate(self, y_test, predictions):
        try:
            mae = mean_absolute_error(y_test, predictions)
            mse = mean_squared_error(y_test, predictions)
            rmse = np.sqrt(mse)
            r2 = r2_score(y_test, predictions)

            y_test_safe = np.where(y_test == 0, 1e-8, y_test)
            mape = np.mean(np.abs((y_test - predictions) / y_test_safe)) * 100

            results = {
                "MAE": round(mae, 4),
                "MSE": round(mse, 4),
                "RMSE": round(rmse, 4),
                "R2_Score": round(r2, 4),
                "MAPE_%": round(mape, 4)
            }

            return results
        except Exception as e:
            print(f"❌ Evaluation failed: {str(e)}")
            raise

    # =========================================
    # FEATURE IMPORTANCE (GENAI ENHANCED)
    # =========================================
    def feature_importance(self):
        try:
            if not self.feature_names:
                return None

            coefficients = self.model.coef_

            importance = {}
            for name, coef in zip(self.feature_names, coefficients):
                importance[name] = {
                    "coefficient": float(coef),
                    "abs_value": float(abs(coef)),
                    "is_genai": name in self.genai_features
                }

            sorted_imp = dict(
                sorted(importance.items(), key=lambda x: x[1]["abs_value"], reverse=True)
            )

            return sorted_imp

        except Exception as e:
            print(f"❌ Feature importance failed: {str(e)}")
            raise

    # =========================================
    # SAVE MODEL (GENAI READY)
    # =========================================
    def save_model(self, path="/content/smart_stock_market_project/models/baseline_model.pkl"):
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)

            model_package = {
                "model": self.model,
                "feature_names": self.feature_names,
                "stock_symbol": self.stock_symbol,
                "is_multi_stock": self.is_multi_stock,
                "genai_features": self.genai_features,
                "categorical_context": ["trend_label", "risk_category"]  # For RAG
            }

            joblib.dump(model_package, path)
            print(f"\n✅ Model saved: {path}")
            print(f"   🤖 GenAI Features: {self.genai_features}")
            print(f"   📝 Context Fields: trend_label, risk_category")

        except Exception as e:
            print(f"❌ Save failed: {str(e)}")
            raise

    # =========================================
    # LOAD MODEL
    # =========================================
    def load_model(self, path="/content/smart_stock_market_project/models/baseline_model.pkl"):
        try:
            if not os.path.exists(path):
                raise FileNotFoundError(f"Model not found: {path}")

            package = joblib.load(path)
            self.model = package["model"]
            self.feature_names = package["feature_names"]
            self.stock_symbol = package.get("stock_symbol")
            self.is_multi_stock = package.get("is_multi_stock", False)
            self.genai_features = package.get("genai_features", [])

            print(f"\n✅ Model loaded: {path}")

        except Exception as e:
            print(f"❌ Load failed: {str(e)}")
            raise

    # =========================================
    # MODEL SUMMARY
    # =========================================
    def get_model_summary(self):
        return {
            "Model Type": "Linear Regression (GenAI Baseline)",
            "Features": len(self.feature_names) if self.feature_names else 0,
            "GenAI Features": len(self.genai_features),
            "Target": "Next-Day Close",
            "Stock": self.stock_symbol if self.stock_symbol else "Multi-Stock",
            "Mode": "GenAI Enhanced"
        }


# =========================================
# MAIN EXECUTION
# =========================================
if __name__ == "__main__":
    DATA_PATH = "/content/smart_stock_market_project/data/stock_dataset.csv"
    MODEL_PATH = "/content/smart_stock_market_project/models/baseline_model.pkl"

    try:
        print("=" * 70)
        print("🤖 GENAI BASELINE PREDICTOR - FIXED VERSION")
        print("=" * 70)

        if not os.path.exists(DATA_PATH):
            raise FileNotFoundError(f"❌ Dataset not found: {DATA_PATH}")

        print(f"\n📥 Loading dataset...")
        df = pd.read_csv(DATA_PATH)
        print(f"✅ Loaded: {df.shape}")

        predictor = GenAIBaselinePredictor()

        # Prepare data (multi-stock or specific stock)
        X_train, X_test, y_train, y_test = predictor.prepare_data(df, stock_symbol=None)

        # Train
        print(f"\n🏋️  Training...")
        predictor.train(X_train, y_train)

        # Predict
        print(f"\n🧪 Predicting...")
        predictions = predictor.predict(X_test)

        # Evaluate
        print(f"\n📊 Evaluating...")
        results = predictor.evaluate(y_test, predictions)

        # Update model with metrics
        predictor.save_model(MODEL_PATH)

        # Display results
        print(f"\n{'='*70}")
        print(f"📊 GENAI BASELINE PERFORMANCE")
        print(f"{'='*70}")
        for metric, value in results.items():
            print(f"  {metric:15s}: {value}")

        # Feature importance
        print(f"\n{'='*70}")
        print(f"📌 FEATURE IMPORTANCE (Top 15)")
        print(f"{'='*70}")
        importance = predictor.feature_importance()

        if importance:
            for idx, (feature, data) in enumerate(list(importance.items())[:15], 1):
                is_genai = "🤖" if data.get("is_genai") else "   "
                print(f"{is_genai} {idx:2d}. {feature:18s}: {data['coefficient']:10.4f} (|{data['abs_value']:8.4f}|)")

        # Summary
        print(f"\n{'='*70}")
        print(f"📋 MODEL SUMMARY")
        print(f"{'='*70}")
        summary = predictor.get_model_summary()
        for key, value in summary.items():
            print(f"  {key:25s}: {value}")

        # Sample predictions
        print(f"\n{'='*70}")
        print(f"🎯 SAMPLE PREDICTIONS")
        print(f"{'='*70}")
        print(f"{'Actual':>12} | {'Predicted':>12} | {'Error%':>10}")
        print("-" * 45)

        for i in range(min(10, len(y_test))):
            actual = y_test.iloc[i]
            pred = predictions[i]
            error = (abs(actual - pred) / actual * 100) if actual != 0 else 0
            print(f"{actual:12.2f} | {pred:12.2f} | {error:9.2f}%")

        print(f"\n{'='*70}")
        print(f"✅ GENAI BASELINE COMPLETED - FIXED!")
        print(f"{'='*70}")
        print(f"\n💡 Next: Run Advanced Predictor")
        print(f"   !python /content/smart_stock_market_project/advanced_predictor.py")
        print(f"\n💡 Run Evaluation")
        print(f"   !python /content/smart_stock_market_project/evaluation.py")
        print(f"{'='*70}\n")

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
