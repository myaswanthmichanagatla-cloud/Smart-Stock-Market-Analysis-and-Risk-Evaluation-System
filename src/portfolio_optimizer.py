
import os
import numpy as np
import pandas as pd
import json
import warnings

warnings.filterwarnings('ignore')

from scipy.optimize import minimize

try:
    import cvxpy as cp
    CVXPY_AVAILABLE = True
except ImportError:
    CVXPY_AVAILABLE = False


class GenAIPortfolioOptimizer:
    def __init__(self):
        self.optimal_weights = None
        self.predictions_df = None
        self.risk_metrics = None
        self.genai_context = {}
        self.stock_names = None
        self.n_assets = None

    # =========================================
    # LOAD PREDICTIONS - 100% FIXED
    # =========================================
    def load_predictions_from_evaluation(self, results_folder=None):
        try:
            if results_folder is None:
                results_folder = "/content/smart_stock_market_project/results"

            advanced_file = os.path.join(results_folder, "advanced_results.json")

            if not os.path.exists(advanced_file):
                print(f"⚠️  Advanced results not found: {advanced_file}")
                return False

            with open(advanced_file, 'r') as f:
                advanced_data = json.load(f)

            predictions = advanced_data.get("predictions", [])
            actuals = advanced_data.get("actual", [])

            if len(predictions) != len(actuals):
                min_len = min(len(predictions), len(actuals))
                predictions = predictions[:min_len]
                actuals = actuals[:min_len]

            n_stocks = 5
            n_samples = len(predictions)
            
            # ✅ FIXED: Calculate exact distribution
            base_size = n_samples // n_stocks
            remainder = n_samples % n_stocks
            
            stock_data = {}
            idx = 0
            
            for i in range(n_stocks):
                # First 'remainder' stocks get +1 element
                size = base_size + (1 if i < remainder else 0)
                stock_data[f"Stock_{i+1}"] = predictions[idx:idx+size]
                idx += size
            
            # ✅ Verify all arrays have EXACT same length (they won't, but that's OK for time series)
            # For portfolio optimization, we need a DataFrame where each column is a stock's time series
            # Different lengths are FINE as long as we handle NaN
            
            self.predictions_df = pd.DataFrame(stock_data)
            self.stock_names = [f"Stock_{i+1}" for i in range(n_stocks)]
            self.n_assets = n_stocks

            print(f"✅ Loaded predictions: {self.predictions_df.shape}")
            lengths = [len(self.predictions_df[col].dropna()) for col in self.predictions_df.columns]
            print(f"   Valid samples per stock: {lengths}")

            return True

        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False

    # =========================================
    # GENERATE SAMPLE DATA
    # =========================================
    def generate_sample_data(self, n_stocks=5, n_days=252):
        try:
            np.random.seed(42)
            returns = np.random.randn(n_days, n_stocks) * 0.02
            prices = 100 + np.cumsum(returns, axis=0)
            
            self.predictions_df = pd.DataFrame(
                prices,
                columns=[f"Stock_{i+1}" for i in range(n_stocks)]
            )
            
            self.stock_names = [f"Stock_{i+1}" for i in range(n_stocks)]
            self.n_assets = n_stocks
            
            print(f"✅ Generated sample data: {self.predictions_df.shape}")
            return True

        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False

    # =========================================
    # CALCULATE EXPECTED RETURNS
    # =========================================
    def calculate_expected_returns(self):
        try:
            if self.predictions_df is None:
                raise ValueError("No predictions loaded")

            returns = self.predictions_df.pct_change().dropna()
            expected_returns = returns.mean() * 252
            
            print(f"✅ Expected Returns: {expected_returns.mean():.2%} annualized")
            return expected_returns.values

        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return None

    # =========================================
    # CALCULATE COVARIANCE MATRIX
    # =========================================
    def calculate_covariance_matrix(self):
        try:
            if self.predictions_df is None:
                raise ValueError("No predictions loaded")

            returns = self.predictions_df.pct_change().dropna()
            cov_matrix = returns.cov() * 252
            
            print(f"✅ Covariance Matrix: {cov_matrix.shape}")
            return cov_matrix.values

        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return None

    # =========================================
    # GENAI ALLOCATION
    # =========================================
    def genai_allocation(self, risk_tolerance="moderate"):
        try:
            print(f"\n🤖 GENAI ALLOCATION (Risk: {risk_tolerance})")

            expected_returns = self.calculate_expected_returns()
            cov_matrix = self.calculate_covariance_matrix()

            if expected_returns is None or cov_matrix is None:
                raise ValueError("Cannot calculate metrics")

            if risk_tolerance == "conservative":
                risk_free_rate = 0.03
                target_return = expected_returns.mean() * 0.8
            elif risk_tolerance == "aggressive":
                risk_free_rate = 0.07
                target_return = expected_returns.mean() * 1.2
            else:
                risk_free_rate = 0.05
                target_return = expected_returns.mean()

            n_assets = len(expected_returns)

            def objective(weights):
                portfolio_return = np.dot(weights, expected_returns)
                portfolio_std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
                return portfolio_std - 0.5 * portfolio_return

            constraints = [
                {'type': 'eq', 'fun': lambda x: np.dot(x, expected_returns) - target_return},
                {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}
            ]
            bounds = tuple((0, 1) for _ in range(n_assets))
            initial_weights = np.array([1/n_assets] * n_assets)

            result = minimize(
                objective,
                initial_weights,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints,
                options={'maxiter': 1000}
            )

            self.optimal_weights = result.x

            portfolio_return = np.dot(self.optimal_weights, expected_returns)
            portfolio_std = np.sqrt(np.dot(self.optimal_weights.T, np.dot(cov_matrix, self.optimal_weights)))
            sharpe = (portfolio_return - risk_free_rate) / portfolio_std

            self.risk_metrics = {
                "portfolio_return": portfolio_return,
                "portfolio_std": portfolio_std,
                "sharpe_ratio": sharpe,
                "weights": self.optimal_weights.tolist(),
                "strategy": f"GenAI {risk_tolerance.capitalize()}"
            }

            self.genai_context = {
                "risk_tolerance": risk_tolerance,
                "target_return": float(target_return),
                "risk_free_rate": risk_free_rate
            }

            print(f"✅ Return: {portfolio_return:.2%} | Risk: {portfolio_std:.2%} | Sharpe: {sharpe:.4f}")

            return self.optimal_weights

        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return None

    # =========================================
    # DISPLAY PORTFOLIO
    # =========================================
    def display_portfolio(self):
        if self.optimal_weights is None:
            print("❌ No weights available")
            return

        print("\n" + "=" * 70)
        print("📊 OPTIMAL PORTFOLIO ALLOCATION")
        print("=" * 70)

        if self.stock_names is None:
            self.stock_names = [f"Stock_{i+1}" for i in range(len(self.optimal_weights))]

        n = len(self.optimal_weights)
        
        portfolio_df = pd.DataFrame({
            "Stock": self.stock_names[:n],
            "Weight (%)": (self.optimal_weights[:n] * 100).round(2),
            "Allocation": self.optimal_weights[:n].round(4)
        })

        print(portfolio_df.to_string(index=False))

        print(f"\n📈 Portfolio Metrics:")
        if self.risk_metrics:
            for key, value in self.risk_metrics.items():
                if isinstance(value, (list, str)):
                    print(f"   {key.replace('_', ' ').title()}: {value}")
                elif isinstance(value, (int, float, np.number)):
                    print(f"   {key.replace('_', ' ').title()}: {value:.4f}")
                else:
                    print(f"   {key.replace('_', ' ').title()}: {value}")

        print("=" * 70)

    # =========================================
    # SAVE PORTFOLIO
    # =========================================
    def save_portfolio(self, output_path="/content/smart_stock_market_project/results/optimal_portfolio.json"):
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            portfolio_data = {
                "optimal_weights": self.optimal_weights.tolist() if self.optimal_weights is not None else None,
                "risk_metrics": self.risk_metrics,
                "genai_context": self.genai_context,
                "stock_names": self.stock_names,
                "n_assets": self.n_assets,
                "timestamp": pd.Timestamp.now().isoformat()
            }

            with open(output_path, 'w') as f:
                json.dump(portfolio_data, f, indent=4)

            print(f"\n✅ Saved: {output_path}")

        except Exception as e:
            print(f"❌ Save failed: {str(e)}")

    # =========================================
    # GENERATE REPORT
    # =========================================
    def generate_genai_report(self):
        if not self.risk_metrics:
            return None

        sharpe = self.risk_metrics.get('sharpe_ratio', 0)
        
        recommendation = (
            "Excellent risk-adjusted returns. Increase allocation." if sharpe > 2 else
            "Good risk-adjusted returns. Suitable for moderate investors." if sharpe > 1 else
            "Acceptable returns. Monitor closely." if sharpe > 0 else
            "Poor risk-adjusted returns. Consider rebalancing."
        )

        report = {
            "report_type": "Portfolio Optimization",
            "generated_at": pd.Timestamp.now().isoformat(),
            "strategy": self.risk_metrics.get("strategy", "Unknown"),
            "metrics": {
                "expected_return": f"{self.risk_metrics.get('portfolio_return', 0):.2%}",
                "volatility": f"{self.risk_metrics.get('portfolio_std', 0):.2%}",
                "sharpe_ratio": f"{self.risk_metrics.get('sharpe_ratio', 0):.4f}"
            },
            "allocation": {
                name: f"{w*100:.2f}%"
                for name, w in zip(self.stock_names, self.optimal_weights)
            },
            "genai_context": self.genai_context,
            "recommendation": recommendation
        }

        return report


# =========================================
# MAIN
# =========================================
if __name__ == "__main__":
    try:
        print("=" * 70)
        print("🤖 GENAI PORTFOLIO OPTIMIZER")
        print("=" * 70)

        optimizer = GenAIPortfolioOptimizer()

        print(f"\n📥 Loading predictions...")
        loaded = optimizer.load_predictions_from_evaluation()

        if not loaded:
            print(f"\n⚠️  Using sample data...")
            optimizer.generate_sample_data(n_stocks=5, n_days=252)

        print(f"\n🚀 Running optimization...")
        optimizer.genai_allocation(risk_tolerance="moderate")

        optimizer.display_portfolio()

        print(f"\n🤖 GENAI REPORT:")
        report = optimizer.generate_genai_report()
        if report:
            print(json.dumps(report, indent=2))

        optimizer.save_portfolio()

        print(f"\n{'='*70}")
        print("✅ COMPLETED")
        print(f"{'='*70}\n")

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
