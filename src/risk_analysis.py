
import os
import json
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings("ignore")

from datetime import datetime
from scipy import stats


class RiskAnalyzer:
    """
    GenAI-Enhanced Risk Analysis System
    
    Features:
    - Value at Risk (VaR)
    - Conditional VaR (CVaR/Expected Shortfall)
    - Maximum Drawdown
    - Sharpe Ratio
    - Sortino Ratio
    - Beta calculation
    - Volatility analysis
    - Risk categorization
    - GenAI-ready insights
    """

    def __init__(self, confidence_level=0.95, risk_free_rate=0.02):
        """
        Initialize Risk Analyzer
        
        Args:
            confidence_level: VaR confidence level (default 95%)
            risk_free_rate: Annual risk-free rate (default 2%)
        """
        self.confidence_level = confidence_level
        self.risk_free_rate = risk_free_rate
        self.stocks = []
        self.returns = None
        self.price_data = None
        self.risk_metrics = {}

    # =========================================
    # LOAD DATA
    # =========================================
    def load_data(self, df):
        """
        Load stock data and calculate returns
        
        Args:
            df: DataFrame with [date, stock_symbol, close] columns
        """
        try:
            print("\n" + "=" * 70)
            print("📊 LOADING DATA FOR RISK ANALYSIS")
            print("=" * 70)

            df = df.copy()

            # Validate columns
            if "stock_symbol" not in df.columns:
                raise ValueError("Missing stock_symbol column")
            if "close" not in df.columns:
                raise ValueError("Missing close column")

            # Get stocks
            self.stocks = sorted(df["stock_symbol"].unique())
            print(f"✅ Stocks: {', '.join(self.stocks)} ({len(self.stocks)} total)")

            # Handle date
            if "date" not in df.columns:
                df["date"] = range(len(df))
            
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
            df = df.dropna(subset=["date", "close"])
            df = df.sort_values(["stock_symbol", "date"])

            # Pivot to price matrix
            self.price_data = df.pivot_table(
                index="date",
                columns="stock_symbol",
                values="close",
                aggfunc="last"
            ).dropna()

            if len(self.price_data) < 30:
                raise ValueError(f"Need 30+ periods, found {len(self.price_data)}")

            # Calculate returns
            self.returns = self.price_data.pct_change().dropna()

            print(f"✅ Data loaded: {len(self.price_data)} periods")
            print(f"   Date range: {self.price_data.index.min()} to {self.price_data.index.max()}")
            print(f"   Returns calculated: {len(self.returns)} periods")

            return True

        except Exception as e:
            print(f"❌ Error loading data: {str(e)}")
            raise

    # =========================================
    # VALUE AT RISK (VaR)
    # =========================================
    def calculate_var(self, stock=None, portfolio_weights=None, method="historical"):
        """
        Calculate Value at Risk
        
        Args:
            stock: Stock symbol (None for portfolio)
            portfolio_weights: Portfolio weights (if stock is None)
            method: "historical" or "parametric"
            
        Returns:
            VaR value (negative number representing potential loss)
        """
        try:
            if stock:
                # Single stock VaR
                returns_data = self.returns[stock]
            elif portfolio_weights is not None:
                # Portfolio VaR
                weights = np.array(portfolio_weights)
                returns_data = (self.returns * weights).sum(axis=1)
            else:
                raise ValueError("Specify either stock or portfolio_weights")

            if method == "historical":
                # Historical VaR
                var = np.percentile(returns_data, (1 - self.confidence_level) * 100)
            else:
                # Parametric VaR (assumes normal distribution)
                mean = returns_data.mean()
                std = returns_data.std()
                var = stats.norm.ppf(1 - self.confidence_level, mean, std)

            return float(var)

        except Exception as e:
            print(f"❌ VaR calculation error: {str(e)}")
            raise

    # =========================================
    # CONDITIONAL VaR (CVaR / Expected Shortfall)
    # =========================================
    def calculate_cvar(self, stock=None, portfolio_weights=None):
        """
        Calculate Conditional VaR (Expected Shortfall)
        Average loss beyond VaR threshold
        
        Returns:
            CVaR value
        """
        try:
            if stock:
                returns_data = self.returns[stock]
            elif portfolio_weights is not None:
                weights = np.array(portfolio_weights)
                returns_data = (self.returns * weights).sum(axis=1)
            else:
                raise ValueError("Specify either stock or portfolio_weights")

            var = self.calculate_var(stock, portfolio_weights)
            cvar = returns_data[returns_data <= var].mean()

            return float(cvar)

        except Exception as e:
            print(f"❌ CVaR calculation error: {str(e)}")
            raise

    # =========================================
    # MAXIMUM DRAWDOWN
    # =========================================
    def calculate_max_drawdown(self, stock=None, portfolio_weights=None):
        """
        Calculate maximum drawdown (largest peak-to-trough decline)
        
        Returns:
            (max_drawdown, drawdown_duration_days, recovery_time_days)
        """
        try:
            if stock:
                prices = self.price_data[stock]
            elif portfolio_weights is not None:
                weights = np.array(portfolio_weights)
                prices = (self.price_data * weights).sum(axis=1)
            else:
                raise ValueError("Specify either stock or portfolio_weights")

            # Calculate cumulative returns
            cumulative = (1 + self.returns[stock] if stock else (self.returns * weights).sum(axis=1)).cumprod()
            running_max = cumulative.expanding().max()
            drawdown = (cumulative - running_max) / running_max

            max_dd = drawdown.min()
            
            # Find drawdown period
            max_dd_idx = drawdown.idxmin()
            peak_idx = running_max[:max_dd_idx].idxmax()
            
            # Calculate recovery
            recovery_idx = cumulative[max_dd_idx:][cumulative[max_dd_idx:] >= running_max[max_dd_idx]].first_valid_index()
            
            drawdown_duration = (max_dd_idx - peak_idx).days if hasattr(max_dd_idx - peak_idx, 'days') else len(cumulative[peak_idx:max_dd_idx])
            recovery_time = (recovery_idx - max_dd_idx).days if recovery_idx and hasattr(recovery_idx - max_dd_idx, 'days') else None

            return float(max_dd), int(drawdown_duration), recovery_time

        except Exception as e:
            print(f"❌ Max drawdown calculation error: {str(e)}")
            return 0.0, 0, None

    # =========================================
    # SHARPE RATIO
    # =========================================
    def calculate_sharpe_ratio(self, stock=None, portfolio_weights=None):
        """
        Calculate Sharpe Ratio (risk-adjusted return)
        
        Returns:
            Sharpe ratio
        """
        try:
            if stock:
                returns_data = self.returns[stock]
            elif portfolio_weights is not None:
                weights = np.array(portfolio_weights)
                returns_data = (self.returns * weights).sum(axis=1)
            else:
                raise ValueError("Specify either stock or portfolio_weights")

            # Annualize
            mean_return = returns_data.mean() * 252
            std_return = returns_data.std() * np.sqrt(252)

            sharpe = (mean_return - self.risk_free_rate) / std_return if std_return > 0 else 0

            return float(sharpe)

        except Exception as e:
            print(f"❌ Sharpe ratio error: {str(e)}")
            raise

    # =========================================
    # SORTINO RATIO
    # =========================================
    def calculate_sortino_ratio(self, stock=None, portfolio_weights=None):
        """
        Calculate Sortino Ratio (downside risk-adjusted return)
        Only considers downside volatility
        
        Returns:
            Sortino ratio
        """
        try:
            if stock:
                returns_data = self.returns[stock]
            elif portfolio_weights is not None:
                weights = np.array(portfolio_weights)
                returns_data = (self.returns * weights).sum(axis=1)
            else:
                raise ValueError("Specify either stock or portfolio_weights")

            # Annualize
            mean_return = returns_data.mean() * 252
            
            # Downside deviation (only negative returns)
            downside_returns = returns_data[returns_data < 0]
            downside_std = downside_returns.std() * np.sqrt(252)

            sortino = (mean_return - self.risk_free_rate) / downside_std if downside_std > 0 else 0

            return float(sortino)

        except Exception as e:
            print(f"❌ Sortino ratio error: {str(e)}")
            raise

    # =========================================
    # BETA (vs Market/Benchmark)
    # =========================================
    def calculate_beta(self, stock, benchmark_stock=None):
        """
        Calculate beta (systematic risk relative to benchmark)
        
        Args:
            stock: Stock symbol
            benchmark_stock: Benchmark stock (None = equal-weighted portfolio)
            
        Returns:
            Beta value
        """
        try:
            stock_returns = self.returns[stock]

            if benchmark_stock:
                market_returns = self.returns[benchmark_stock]
            else:
                # Use equal-weighted portfolio as benchmark
                market_returns = self.returns.mean(axis=1)

            # Calculate covariance and variance
            covariance = np.cov(stock_returns, market_returns)[0][1]
            market_variance = np.var(market_returns)

            beta = covariance / market_variance if market_variance > 0 else 1.0

            return float(beta)

        except Exception as e:
            print(f"❌ Beta calculation error: {str(e)}")
            return 1.0

    # =========================================
    # VOLATILITY METRICS
    # =========================================
    def calculate_volatility(self, stock=None, portfolio_weights=None, window=30):
        """
        Calculate rolling volatility
        
        Returns:
            (current_volatility, average_volatility, max_volatility)
        """
        try:
            if stock:
                returns_data = self.returns[stock]
            elif portfolio_weights is not None:
                weights = np.array(portfolio_weights)
                returns_data = (self.returns * weights).sum(axis=1)
            else:
                raise ValueError("Specify either stock or portfolio_weights")

            # Calculate rolling volatility (annualized)
            rolling_vol = returns_data.rolling(window=window).std() * np.sqrt(252)

            current_vol = rolling_vol.iloc[-1]
            avg_vol = rolling_vol.mean()
            max_vol = rolling_vol.max()

            return float(current_vol), float(avg_vol), float(max_vol)

        except Exception as e:
            print(f"❌ Volatility calculation error: {str(e)}")
            return 0.0, 0.0, 0.0

    # =========================================
    # RISK CATEGORIZATION
    # =========================================
    def categorize_risk(self, volatility):
        """
        Categorize risk based on volatility
        
        Returns:
            Risk category string
        """
        vol_pct = volatility * 100

        if vol_pct < 15:
            return "Low Risk"
        elif vol_pct < 25:
            return "Moderate Risk"
        elif vol_pct < 35:
            return "High Risk"
        else:
            return "Very High Risk"

    # =========================================
    # COMPREHENSIVE RISK ANALYSIS
    # =========================================
    def analyze_stock(self, stock):
        """
        Perform comprehensive risk analysis for a single stock
        
        Returns:
            Dictionary with all risk metrics
        """
        try:
            print(f"\n{'='*70}")
            print(f"🔍 RISK ANALYSIS: {stock}")
            print(f"{'='*70}")

            # Calculate all metrics
            var_95 = self.calculate_var(stock=stock)
            cvar_95 = self.calculate_cvar(stock=stock)
            max_dd, dd_duration, recovery = self.calculate_max_drawdown(stock=stock)
            sharpe = self.calculate_sharpe_ratio(stock=stock)
            sortino = self.calculate_sortino_ratio(stock=stock)
            beta = self.calculate_beta(stock=stock)
            curr_vol, avg_vol, max_vol = self.calculate_volatility(stock=stock)

            # Returns statistics
            stock_returns = self.returns[stock]
            mean_return = stock_returns.mean() * 252
            std_return = stock_returns.std() * np.sqrt(252)

            risk_category = self.categorize_risk(curr_vol)

            metrics = {
                "stock": stock,
                "returns": {
                    "mean_annual": float(mean_return * 100),
                    "volatility_annual": float(std_return * 100)
                },
                "var_metrics": {
                    "var_95": float(var_95 * 100),
                    "cvar_95": float(cvar_95 * 100),
                    "confidence_level": self.confidence_level * 100
                },
                "drawdown": {
                    "max_drawdown": float(max_dd * 100),
                    "duration_days": dd_duration,
                    "recovery_days": recovery
                },
                "risk_adjusted": {
                    "sharpe_ratio": float(sharpe),
                    "sortino_ratio": float(sortino),
                    "beta": float(beta)
                },
                "volatility": {
                    "current": float(curr_vol * 100),
                    "average": float(avg_vol * 100),
                    "maximum": float(max_vol * 100)
                },
                "risk_category": risk_category
            }

            # Print summary
            print(f"\n📈 Returns:")
            print(f"   Mean Annual Return: {metrics['returns']['mean_annual']:.2f}%")
            print(f"   Annual Volatility:  {metrics['returns']['volatility_annual']:.2f}%")

            print(f"\n⚠️  Risk Metrics:")
            print(f"   VaR (95%):     {metrics['var_metrics']['var_95']:.2f}%")
            print(f"   CVaR (95%):    {metrics['var_metrics']['cvar_95']:.2f}%")
            print(f"   Max Drawdown:  {metrics['drawdown']['max_drawdown']:.2f}%")

            print(f"\n📊 Risk-Adjusted Returns:")
            print(f"   Sharpe Ratio:  {metrics['risk_adjusted']['sharpe_ratio']:.4f}")
            print(f"   Sortino Ratio: {metrics['risk_adjusted']['sortino_ratio']:.4f}")
            print(f"   Beta:          {metrics['risk_adjusted']['beta']:.4f}")

            print(f"\n🎯 Risk Category: {risk_category}")
            print(f"{'='*70}")

            return metrics

        except Exception as e:
            print(f"❌ Analysis error for {stock}: {str(e)}")
            raise

    # =========================================
    # ANALYZE ALL STOCKS
    # =========================================
    def analyze_all_stocks(self):
        """
        Analyze all stocks and generate comparative report
        
        Returns:
            Dictionary with all stock metrics
        """
        try:
            print("\n" + "=" * 70)
            print("🔍 COMPREHENSIVE RISK ANALYSIS - ALL STOCKS")
            print("=" * 70)

            all_metrics = {}

            for stock in self.stocks:
                metrics = self.analyze_stock(stock)
                all_metrics[stock] = metrics

            # Generate comparison
            self._print_comparison(all_metrics)

            self.risk_metrics = all_metrics

            return all_metrics

        except Exception as e:
            print(f"❌ Error analyzing stocks: {str(e)}")
            raise

    # =========================================
    # PRINT COMPARISON TABLE
    # =========================================
    def _print_comparison(self, all_metrics):
        """Print comparison table for all stocks"""
        print("\n" + "=" * 100)
        print("📊 RISK COMPARISON TABLE")
        print("=" * 100)
        print(f"{'Stock':12s} | {'Return%':>8s} | {'Vol%':>7s} | {'VaR%':>7s} | {'MaxDD%':>8s} | {'Sharpe':>7s} | {'Risk':>15s}")
        print("-" * 100)

        for stock, metrics in all_metrics.items():
            print(
                f"{stock:12s} | "
                f"{metrics['returns']['mean_annual']:>8.2f} | "
                f"{metrics['returns']['volatility_annual']:>7.2f} | "
                f"{metrics['var_metrics']['var_95']:>7.2f} | "
                f"{metrics['drawdown']['max_drawdown']:>8.2f} | "
                f"{metrics['risk_adjusted']['sharpe_ratio']:>7.4f} | "
                f"{metrics['risk_category']:>15s}"
            )

        print("=" * 100)

    # =========================================
    # GENERATE GENAI SUMMARY
    # =========================================
    def generate_genai_summary(self):
        """Generate natural language risk summary"""
        if not self.risk_metrics:
            raise ValueError("Run analyze_all_stocks() first")

        # Find best/worst stocks
        sharpe_sorted = sorted(
            self.risk_metrics.items(),
            key=lambda x: x[1]["risk_adjusted"]["sharpe_ratio"],
            reverse=True
        )

        best_stock = sharpe_sorted[0][0]
        worst_stock = sharpe_sorted[-1][0]

        best_metrics = self.risk_metrics[best_stock]
        worst_metrics = self.risk_metrics[worst_stock]

        # Risk distribution
        risk_dist = {}
        for stock, metrics in self.risk_metrics.items():
            category = metrics["risk_category"]
            risk_dist[category] = risk_dist.get(category, 0) + 1

        summary = {
            "analysis_date": datetime.now().isoformat(),
            "num_stocks": len(self.stocks),
            "stocks_analyzed": self.stocks,
            "best_risk_adjusted": {
                "stock": best_stock,
                "sharpe_ratio": best_metrics["risk_adjusted"]["sharpe_ratio"],
                "return": best_metrics["returns"]["mean_annual"],
                "volatility": best_metrics["returns"]["volatility_annual"]
            },
            "highest_risk": {
                "stock": worst_stock,
                "sharpe_ratio": worst_metrics["risk_adjusted"]["sharpe_ratio"],
                "return": worst_metrics["returns"]["mean_annual"],
                "volatility": worst_metrics["returns"]["volatility_annual"]
            },
            "risk_distribution": risk_dist,
            "natural_language_summary": (
                f"Risk analysis of {len(self.stocks)} stocks completed. "
                f"{best_stock} shows the best risk-adjusted returns with Sharpe ratio {best_metrics['risk_adjusted']['sharpe_ratio']:.3f}, "
                f"offering {best_metrics['returns']['mean_annual']:.2f}% annual return with {best_metrics['returns']['volatility_annual']:.2f}% volatility. "
                f"{worst_stock} has the highest risk profile with Sharpe ratio {worst_metrics['risk_adjusted']['sharpe_ratio']:.3f}. "
                f"Risk distribution: {', '.join([f'{k}: {v}' for k, v in risk_dist.items()])}. "
                f"Maximum drawdowns range from {min([m['drawdown']['max_drawdown'] for m in self.risk_metrics.values()]):.2f}% "
                f"to {max([m['drawdown']['max_drawdown'] for m in self.risk_metrics.values()]):.2f}%."
            )
        }

        return summary

    # =========================================
    # SAVE RESULTS
    # =========================================
    def save_results(self, output_path=None):
        if output_path is None:
            _BASE = os.path.dirname(os.path.realpath(__file__))
            output_path = os.path.join(_BASE, "results", "risk_analysis.json")
        """Save risk analysis results to JSON"""
        try:
            if not self.risk_metrics:
                raise ValueError("No metrics to save. Run analyze_all_stocks() first")

            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            summary = self.generate_genai_summary()

            results = {
                "risk_metrics": self.risk_metrics,
                "summary": summary,
                "parameters": {
                    "confidence_level": self.confidence_level,
                    "risk_free_rate": self.risk_free_rate
                }
            }

            with open(output_path, "w") as f:
                json.dump(results, f, indent=4)

            size = os.path.getsize(output_path) / 1024
            print(f"\n✅ Results saved: {output_path}")
            print(f"   File size: {size:.2f} KB")

        except Exception as e:
            print(f"❌ Save error: {str(e)}")
            raise


# =========================================
# MAIN EXECUTION
# =========================================
if __name__ == "__main__":
    
    _BASE      = os.path.dirname(os.path.realpath(__file__))
    DATA_PATH  = os.path.join(_BASE, "data", "stock_dataset.csv")
    
    try:
        print("=" * 70)
        print("🤖 GENAI-ENHANCED RISK ANALYSIS SYSTEM")
        print("=" * 70)

        # Load data
        if not os.path.exists(DATA_PATH):
            raise FileNotFoundError(f"Dataset not found: {DATA_PATH}")

        df = pd.read_csv(DATA_PATH)
        print(f"\nDataset loaded: {df.shape}")

        # Initialize analyzer
        analyzer = RiskAnalyzer(confidence_level=0.95, risk_free_rate=0.02)

        # Load data
        analyzer.load_data(df)

        # Analyze all stocks
        all_metrics = analyzer.analyze_all_stocks()

        # Generate summary
        summary = analyzer.generate_genai_summary()

        print("\n" + "=" * 70)
        print("🎯 GENAI RISK SUMMARY")
        print("=" * 70)
        print(summary["natural_language_summary"])
        print("=" * 70)

        # Save results
        analyzer.save_results()

        print("\n" + "=" * 70)
        print("✅ RISK ANALYSIS COMPLETE")
        print("=" * 70)
        print("\nOutput: risk_analysis.json")
        print("=" * 70 + "\n")

    except FileNotFoundError as e:
        print(f"\n❌ FILE ERROR: {str(e)}")
    except ValueError as e:
        print(f"\n❌ VALUE ERROR: {str(e)}")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
