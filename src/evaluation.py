import os
import sys
import json
import numpy as np
import pandas as pd

# Reconfigure stdout and stderr to use UTF-8 to prevent CP1252 terminal encoding errors on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# Add project path to sys.path
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))

from baseline_predictor import GenAIBaselinePredictor
from advanced_predictor import GenAIAdvancedPredictor


class ModelEvaluator:
    """
    Evaluates and compares:
    - Baseline Predictor (Linear Regression)
    - Advanced Predictor (XGBoost)
    
    GENAI FEATURES:
    - Compares RSI, MACD features
    - Tracks categorical feature usage
    - Saves GenAI-ready results
    - RAG-compatible comparison
    """

    def __init__(self):
        self.baseline_results = None
        self.advanced_results = None
        self.comparison_results = None

    # =========================================
    # LOAD DATASET
    # =========================================
    def load_dataset(
        self,
        path=None
    ):
        if path is None:
            _BASE = os.path.dirname(os.path.realpath(__file__))
            path = os.path.join(_BASE, "data", "stock_dataset.csv")
        if not os.path.exists(path):
            raise FileNotFoundError(f"❌ Dataset not found: {path}")

        try:
            df = pd.read_csv(path)
            print("\n✅ Dataset Loaded Successfully")
            print(f"   Shape: {df.shape}")
            print(f"   Columns: {list(df.columns)}")
            return df
        except Exception as e:
            raise Exception(f"❌ Error loading dataset: {str(e)}")

    # =========================================
    # RUN BASELINE MODEL
    # =========================================
    def evaluate_baseline(self, df, stock_symbol=None):
        """Evaluate baseline model on specified stock or all data"""
        
        print("\n" + "=" * 70)
        print("📈 EVALUATING BASELINE MODEL (Linear Regression)")
        print("=" * 70)

        try:
            baseline = GenAIBaselinePredictor()

            X_train, X_test, y_train, y_test = baseline.prepare_data(
                df,
                stock_symbol=stock_symbol
            )

            baseline.train(X_train, y_train)

            predictions = baseline.predict(X_test)

            results = baseline.evaluate(y_test, predictions)

            feature_importance = baseline.feature_importance()

            # Convert numpy arrays to lists for JSON serialization
            self.baseline_results = {
                "metrics": results,
                "feature_importance": self._serialize_importance(feature_importance),
                "predictions": predictions.tolist() if hasattr(predictions, 'tolist') else list(predictions),
                "actual": y_test.tolist() if hasattr(y_test, 'tolist') else list(y_test),
                "stock_symbol": stock_symbol,
                "genai_features": baseline.genai_features
            }

            print("\n✅ Baseline Evaluation Complete")
            return self.baseline_results

        except Exception as e:
            print(f"\n❌ Baseline evaluation failed: {str(e)}")
            raise

    # =========================================
    # RUN ADVANCED MODEL
    # =========================================
    def evaluate_advanced(self, df, stock_symbol=None):
        """Evaluate advanced model on specified stock or all data"""
        
        print("\n" + "=" * 70)
        print("🚀 EVALUATING ADVANCED MODEL (XGBoost)")
        print("=" * 70)

        try:
            advanced = GenAIAdvancedPredictor()

            # Pass stock_symbol to prepare_data if available
            if stock_symbol and "stock_symbol" in df.columns:
                X_train, X_test, y_train, y_test = advanced.prepare_data(
                    df[df["stock_symbol"] == stock_symbol] if stock_symbol else df
                )
            else:
                X_train, X_test, y_train, y_test = advanced.prepare_data(df)

            advanced.train(X_train, y_train)

            predictions = advanced.predict(X_test)

            results = advanced.evaluate(y_test, predictions)

            feature_importance = advanced.feature_importance()

            # Convert numpy arrays to lists for JSON serialization
            self.advanced_results = {
                "metrics": results,
                "feature_importance": self._serialize_importance(feature_importance),
                "predictions": predictions.tolist() if hasattr(predictions, 'tolist') else list(predictions),
                "actual": y_test.tolist() if hasattr(y_test, 'tolist') else list(y_test),
                "stock_symbol": stock_symbol,
                "genai_features": advanced.genai_features,
                "categorical_features": advanced.categorical_features
            }

            print("\n✅ Advanced Evaluation Complete")
            return self.advanced_results

        except Exception as e:
            print(f"\n❌ Advanced evaluation failed: {str(e)}")
            raise

    # =========================================
    # SERIALIZE FEATURE IMPORTANCE
    # =========================================
    def _serialize_importance(self, importance):
        """Convert feature importance to JSON-serializable format"""
        if importance is None:
            return None
        
        serialized = {}
        for feature, data in importance.items():
            if isinstance(data, dict):
                serialized[feature] = {
                    k: float(v) if isinstance(v, (np.floating, np.integer)) else v
                    for k, v in data.items()
                }
            else:
                serialized[feature] = float(data) if isinstance(data, (np.floating, np.integer)) else data
        
        return serialized

    # =========================================
    # COMPARE MODELS
    # =========================================
    def compare_models(self):
        """Compare baseline vs advanced models"""
        
        if self.baseline_results is None:
            raise ValueError("❌ Baseline results missing. Run evaluate_baseline() first.")

        if self.advanced_results is None:
            raise ValueError("❌ Advanced results missing. Run evaluate_advanced() first.")

        baseline = self.baseline_results["metrics"]
        advanced = self.advanced_results["metrics"]

        comparison = {}

        metrics = ["MAE", "MSE", "RMSE", "R2_Score", "MAPE_%"]

        for metric in metrics:
            baseline_val = baseline.get(metric, 0)
            advanced_val = advanced.get(metric, 0)

            # Lower is better except R2
            if metric == "R2_Score":
                if baseline_val != 0:
                    improvement = ((advanced_val - baseline_val) / abs(baseline_val)) * 100
                else:
                    improvement = np.nan
                better_model = "Advanced" if advanced_val > baseline_val else "Baseline"
            else:
                if baseline_val != 0:
                    improvement = ((baseline_val - advanced_val) / abs(baseline_val)) * 100
                else:
                    improvement = np.nan
                better_model = "Advanced" if advanced_val < baseline_val else "Baseline"

            comparison[metric] = {
                "Baseline": round(baseline_val, 4),
                "Advanced": round(advanced_val, 4),
                "Improvement_%": round(improvement, 4) if not np.isnan(improvement) else "N/A",
                "Better_Model": better_model
            }

        self.comparison_results = comparison

        return comparison

    # =========================================
    # DISPLAY COMPARISON
    # =========================================
    def print_comparison(self):
        """Print formatted comparison table"""
        
        if self.comparison_results is None:
            raise ValueError("❌ Run compare_models() first")

        print("\n" + "=" * 90)
        print("📊 MODEL COMPARISON REPORT")
        print("=" * 90)

        print(
            f"{'Metric':15s} | {'Baseline':12s} | {'Advanced':12s} | "
            f"{'Improvement %':15s} | {'Best Model':12s}"
        )

        print("-" * 90)

        for metric, values in self.comparison_results.items():
            print(
                f"{metric:15s} | "
                f"{values['Baseline']:12.4f} | "
                f"{values['Advanced']:12.4f} | "
                f"{str(values['Improvement_%']):15s} | "
                f"{values['Better_Model']:12s}"
            )

        print("=" * 90)

    # =========================================
    # SAVE RESULTS
    # =========================================
    def save_results(
        self,
        output_folder=None
    ):
        if output_folder is None:
            _BASE = os.path.dirname(os.path.realpath(__file__))
            output_folder = os.path.join(_BASE, "results")
        """Save all results as JSON files"""
        
        try:
            os.makedirs(output_folder, exist_ok=True)

            # Baseline
            if self.baseline_results:
                baseline_path = os.path.join(output_folder, "baseline_results.json")
                with open(baseline_path, "w") as f:
                    json.dump(self.baseline_results, f, indent=4)
                print(f"\n✅ Baseline results saved: {baseline_path}")

            # Advanced
            if self.advanced_results:
                advanced_path = os.path.join(output_folder, "advanced_results.json")
                with open(advanced_path, "w") as f:
                    json.dump(self.advanced_results, f, indent=4)
                print(f"✅ Advanced results saved: {advanced_path}")

            # Comparison
            if self.comparison_results:
                comparison_path = os.path.join(output_folder, "model_comparison.json")
                with open(comparison_path, "w") as f:
                    json.dump(self.comparison_results, f, indent=4)
                print(f"   [SUCCESS] Comparison saved: {comparison_path}")

                # GenAI Summary
                advanced_wins = 0
                baseline_wins = 0
                ties = 0

                for metric, values in self.comparison_results.items():
                    if values["Better_Model"] == "Advanced":
                        advanced_wins += 1
                    elif values["Better_Model"] == "Baseline":
                        baseline_wins += 1
                    else:
                        ties += 1

                if advanced_wins > baseline_wins:
                    winner = "Advanced"
                    nl_summary = f"The advanced predictor (XGBoost) outperformed the baseline model by winning {advanced_wins} out of {len(self.comparison_results)} metrics. It represents the best choice for deployment."
                elif baseline_wins > advanced_wins:
                    winner = "Baseline"
                    nl_summary = f"The baseline predictor (Linear Regression) outperformed the advanced model by winning {baseline_wins} out of {len(self.comparison_results)} metrics. Due to the high linearity and structure of this stock market dataset, the baseline model provides superior metrics."
                else:
                    winner = "Tie"
                    nl_summary = f"Both baseline and advanced predictors performed equally, each winning {baseline_wins} metrics."

                genai_summary = {
                    "winner": winner,
                    "advanced_wins": advanced_wins,
                    "baseline_wins": baseline_wins,
                    "ties": ties,
                    "natural_language_summary": nl_summary
                }

                genai_summary_path = os.path.join(output_folder, "genai_summary.json")
                with open(genai_summary_path, "w") as f:
                    json.dump(genai_summary, f, indent=4)
                print(f"   [SUCCESS] GenAI Summary saved: {genai_summary_path}")

            print(f"\n💾 All results saved in: {output_folder}")

        except Exception as e:
            print(f"\n❌ Error saving results: {str(e)}")
            raise

    # =========================================
    # GENERATE SUMMARY
    # =========================================
    def generate_summary(self):
        """Generate final evaluation summary"""
        
        if self.comparison_results is None:
            raise ValueError("❌ Comparison results missing. Run compare_models() first.")

        advanced_wins = 0
        baseline_wins = 0
        ties = 0

        for metric, values in self.comparison_results.items():
            if values["Better_Model"] == "Advanced":
                advanced_wins += 1
            elif values["Better_Model"] == "Baseline":
                baseline_wins += 1
            else:
                ties += 1

        print("\n" + "=" * 70)
        print("📌 FINAL EVALUATION SUMMARY")
        print("=" * 70)

        print(f"🎯 Advanced Model Wins : {advanced_wins}/{len(self.comparison_results)}")
        print(f"🎯 Baseline Model Wins : {baseline_wins}/{len(self.comparison_results)}")
        print(f"🎯 Ties               : {ties}/{len(self.comparison_results)}")

        if advanced_wins > baseline_wins:
            print("\n🏆 BEST OVERALL MODEL: ADVANCED PREDICTOR (XGBoost) ✅")
        elif baseline_wins > advanced_wins:
            print("\n🏆 BEST OVERALL MODEL: BASELINE PREDICTOR (Linear Regression) ✅")
        else:
            print("\n🏆 BOTH MODELS PERFORM EQUALLY ✅")

        print("=" * 70)

        # GenAI-specific summary
        print("\n🤖 GENAI FEATURES ANALYSIS")
        print("-" * 70)
        
        if self.baseline_results and self.advanced_results:
            baseline_genai = self.baseline_results.get("genai_features", [])
            advanced_genai = self.advanced_results.get("genai_features", [])
            
            print(f"   Baseline GenAI Features: {baseline_genai}")
            print(f"   Advanced GenAI Features: {advanced_genai}")
            
            if advanced_genai:
                print(f"\n   ✅ Advanced uses categorical features: {self.advanced_results.get('categorical_features', [])}")

        print("=" * 70)


# =========================================
# MAIN EXECUTION
# =========================================
if __name__ == "__main__":

    try:
        print("=" * 70)
        print("🤖 SMART STOCK MARKET MODEL EVALUATION")
        print("=" * 70)

        evaluator = ModelEvaluator()

        # -------------------------------
        # Load Dataset
        # -------------------------------
        df = evaluator.load_dataset()

        # -------------------------------
        # Evaluate Baseline (Multi-Stock)
        # -------------------------------
        evaluator.evaluate_baseline(df, stock_symbol=None)

        # -------------------------------
        # Evaluate Advanced (Multi-Stock)
        # -------------------------------
        evaluator.evaluate_advanced(df, stock_symbol=None)

        # -------------------------------
        # Compare Models
        # -------------------------------
        evaluator.compare_models()

        # -------------------------------
        # Print Comparison
        # -------------------------------
        evaluator.print_comparison()

        # -------------------------------
        # Summary
        # -------------------------------
        evaluator.generate_summary()

        # -------------------------------
        # Save Results
        # -------------------------------
        evaluator.save_results()

        print("\n" + "=" * 70)
        print("✅ EVALUATION COMPLETED SUCCESSFULLY")
        print("=" * 70)
        print(f"\n📁 Results saved in: {os.path.join(os.path.dirname(os.path.realpath(__file__)), 'results')}/")
        print("\n💡 Files created:")
        print("   1. baseline_results.json")
        print("   2. advanced_results.json")
        print("   3. model_comparison.json")
        print("\n🚀 Next Steps:")
        print("   - Check results/ folder for JSON files")
        print("   - Use GenAI features for RAG queries")
        print("   - Deploy best model for predictions")
        print("=" * 70 + "\n")

    except FileNotFoundError as e:
        print(f"\n❌ FILE ERROR: {e}")
        print(f"\n💡 SOLUTION:")
        print(f"   1. Run pipeline first: python stock_data_pipeline.py")
        print(f"   2. Run baseline: python baseline_predictor.py")
        print(f"   3. Run advanced: python advanced_predictor.py")

    except ValueError as e:
        print(f"\n❌ VALUE ERROR: {e}")

    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
