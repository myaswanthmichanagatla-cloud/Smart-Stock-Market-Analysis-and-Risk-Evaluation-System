#!/usr/bin/env python3
"""
Smart Stock Market RAG System
Retrieval-Augmented Generation for Stock Market Insights

Features:
- Query stock market knowledge base
- Semantic search with embeddings
- Context-aware responses
- Integration with GenAI models
- Natural language Q&A
"""

import os
import sys
import json
import numpy as np
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional
import warnings
warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------------
# BUG FIXED: Derive project paths from this script's own location instead of
# hardcoding the Google-Colab-only path '/content/smart_stock_market_project'.
# This makes the module importable from any directory on any OS.
# ---------------------------------------------------------------------------
_SCRIPT_DIR  = os.path.dirname(os.path.realpath(__file__))
_DEFAULT_KB   = os.path.join(_SCRIPT_DIR, "data",    "rag_knowledge_base.json")
_DEFAULT_RES  = os.path.join(_SCRIPT_DIR, "results")


class StockMarketRAG:
    """
    RAG System for Stock Market Analysis

    Components:
    1. Knowledge Base Loader
    2. Semantic Search
    3. Context Retrieval
    4. Answer Generation
    """

    def __init__(
        self,
        kb_path: str   = _DEFAULT_KB,   # BUG FIXED: was hardcoded Colab path
        results_path: str = _DEFAULT_RES # BUG FIXED: was hardcoded Colab path
    ):
        self.kb_path      = kb_path
        self.results_path = results_path
        self.knowledge_base: List[Dict] = []
        self.stock_data   = None
        self.model_results: Dict = {}
        self.portfolio_data: Dict = {}

    # =========================================
    # LOAD KNOWLEDGE BASE
    # =========================================
    def load_knowledge_base(self) -> bool:
        """Load RAG knowledge base"""
        try:
            print("\n" + "=" * 70)
            print("📚 LOADING KNOWLEDGE BASE")
            print("=" * 70)

            if not os.path.exists(self.kb_path):
                raise FileNotFoundError(
                    f"Knowledge base not found: {self.kb_path}\n"
                    "  → Run the Data Pipeline first (Option 1 in main menu)."
                )

            with open(self.kb_path, "r") as f:
                self.knowledge_base = json.load(f)

            print(f"✅ Loaded {len(self.knowledge_base)} knowledge entries")

            # Load the complete stock dataset if available for advanced aggregations
            csv_path = os.path.join(os.path.dirname(self.kb_path), "stock_dataset.csv")
            if os.path.exists(csv_path):
                self.stock_data = pd.read_csv(csv_path)
                print(f"   ✅ Loaded stock dataset: {self.stock_data.shape}")
            else:
                self.stock_data = pd.DataFrame(self.knowledge_base)

            # Extract and display unique stocks
            if self.knowledge_base and isinstance(self.knowledge_base, list):
                stocks = set()
                for entry in self.knowledge_base:
                    if "stock_symbol" in entry:
                        stocks.add(entry["stock_symbol"])
                print(f"   Stocks: {', '.join(sorted(stocks))}")

            return True

        except Exception as e:
            print(f"❌ Error loading knowledge base: {str(e)}")
            return False

    # =========================================
    # LOAD MODEL RESULTS
    # =========================================
    def load_model_results(self) -> bool:
        """Load model evaluation results"""
        try:
            print("\n📊 Loading Model Results...")

            files = {
                "baseline":    "baseline_results.json",
                "advanced":    "advanced_results.json",
                "comparison":  "model_comparison.json",
                "genai_summary": "genai_summary.json"
            }

            for key, filename in files.items():
                filepath = os.path.join(self.results_path, filename)
                if os.path.exists(filepath):
                    with open(filepath, "r") as f:
                        self.model_results[key] = json.load(f)
                    print(f"   ✅ {filename}")
                else:
                    print(f"   ⚠️  {filename} not found")

            return len(self.model_results) > 0

        except Exception as e:
            print(f"❌ Error loading model results: {str(e)}")
            return False

    # =========================================
    # LOAD PORTFOLIO DATA
    # =========================================
    def load_portfolio_data(self) -> bool:
        """Load portfolio optimization results"""
        try:
            print("\n💼 Loading Portfolio Data...")

            portfolio_path = os.path.join(
                self.results_path, "portfolio_optimization.json"
            )

            if os.path.exists(portfolio_path):
                with open(portfolio_path, "r") as f:
                    self.portfolio_data = json.load(f)
                print("   ✅ Portfolio optimization loaded")
                return True
            else:
                print("   ⚠️  Portfolio data not found")
                return False

        except Exception as e:
            print(f"❌ Error loading portfolio data: {str(e)}")
            return False

    # =========================================
    # SEMANTIC SEARCH (keyword / TF-IDF style)
    # =========================================
    def search_knowledge_base(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Search knowledge base using keyword matching.

        Args:
            query:  Search query string
            top_k:  Maximum number of results to return

        Returns:
            List of relevant knowledge-base entries
        """
        try:
            query_lower  = query.lower()
            query_terms  = set(query_lower.split())

            results = []
            for entry in self.knowledge_base:
                text = entry.get("text_summary", str(entry)).lower()

                score = sum(text.count(term) for term in query_terms if term in text)

                if score > 0:
                    results.append({"entry": entry, "score": score})

            results.sort(key=lambda x: x["score"], reverse=True)
            return [r["entry"] for r in results[:top_k]]

        except Exception as e:
            print(f"❌ Search error: {str(e)}")
            return []

    # =========================================
    # QUERY STOCK INFORMATION
    # =========================================
    def query_stock(self, stock_symbol: str) -> Dict[str, Any]:
        """Get information about a specific stock"""
        try:
            stock_symbol  = stock_symbol.upper()
            stock_entries = [
                entry for entry in self.knowledge_base
                if entry.get("stock_symbol", "").upper() == stock_symbol
            ]

            if not stock_entries:
                return {
                    "stock":   stock_symbol,
                    "found":   False,
                    "message": f"No data found for {stock_symbol}"
                }

            closes = [e["close"] for e in stock_entries if "close" in e]

            return {
                "stock":       stock_symbol,
                "found":       True,
                "data_points": len(stock_entries),
                "statistics": {
                    "avg_price": round(float(np.mean(closes)),  2) if closes else 0,
                    "min_price": round(float(np.min(closes)),   2) if closes else 0,
                    "max_price": round(float(np.max(closes)),   2) if closes else 0,
                },
                "trend": stock_entries[-1].get("trend_label",    "Unknown"),
                "risk":  stock_entries[-1].get("risk_category",  "Unknown"),
                "latest_entry": stock_entries[-1]
            }

        except Exception as e:
            return {"error": str(e)}

    # =========================================
    # QUERY MODEL PERFORMANCE
    # =========================================
    def query_model_performance(self, model_type: str = "comparison") -> Dict[str, Any]:
        """Get model performance information"""
        try:
            if model_type == "comparison" and "comparison" in self.model_results:
                comparison    = self.model_results["comparison"]
                advanced_wins = sum(
                    1 for data in comparison.values()
                    if data.get("Better_Model") == "Advanced"
                )
                baseline_wins = len(comparison) - advanced_wins
                return {
                    "comparison":    comparison,
                    "winner":        "Advanced" if advanced_wins > baseline_wins else "Baseline",
                    "advanced_wins": advanced_wins,
                    "baseline_wins": baseline_wins,
                    "total_metrics": len(comparison)
                }

            if model_type == "baseline" and "baseline" in self.model_results:
                return self.model_results["baseline"]

            if model_type == "advanced" and "advanced" in self.model_results:
                return self.model_results["advanced"]

            if "genai_summary" in self.model_results:
                return self.model_results["genai_summary"]

            return {"error": "Model results not available"}

        except Exception as e:
            return {"error": str(e)}

    # =========================================
    # QUERY PORTFOLIO
    # =========================================
    def query_portfolio(self) -> Dict[str, Any]:
        """Get portfolio optimization information"""
        try:
            if not self.portfolio_data:
                return {"error": "Portfolio data not available"}

            if "summary" in self.portfolio_data:
                summary = self.portfolio_data["summary"]
                return {
                    "best_strategy":   summary.get("best_strategy",       "Unknown"),
                    "expected_return": summary.get("best_expected_return", 0),
                    "volatility":      summary.get("best_volatility",      0),
                    "sharpe_ratio":    summary.get("best_sharpe_ratio",    0),
                    "allocation":      summary.get("best_weights",         {}),
                    "recommendation":  summary.get("natural_language_summary", "")
                }

            return self.portfolio_data

        except Exception as e:
            return {"error": str(e)}

    # =========================================
    # ANSWER QUESTION
    # =========================================
    def answer_question(self, question: str) -> str:
        """
        Answer a natural language question using RAG.

        BUG FIXED: stock-name detection previously checked only four hardcoded
        names ("reliance", "tcs", "infy", "hdfc").  Now it dynamically builds
        the symbol list from whatever is actually in the loaded knowledge base,
        so any stock present in the data is recognised.
        """
        try:
            question_lower = question.lower()

            # ── Build a dynamic set of known stock symbols from KB ──────────
            known_symbols = {
                entry.get("stock_symbol", "").lower()
                for entry in self.knowledge_base
                if entry.get("stock_symbol")
            }

            # ── Stock-specific questions ────────────────────────────────────
            stock_question = (
                "stock" in question_lower
                or any(sym in question_lower for sym in known_symbols)
            )

            if stock_question:
                # Find the first symbol mentioned in the question
                matched_stock = next(
                    (sym.upper() for sym in known_symbols if sym in question_lower),
                    None
                )
                if matched_stock:
                    info = self.query_stock(matched_stock)
                    if info.get("found"):
                        return (
                            f"**{matched_stock} Information:**\n"
                            f"- Data Points: {info['data_points']}\n"
                            f"- Average Price: ₹{info['statistics']['avg_price']}\n"
                            f"- Price Range: "
                            f"₹{info['statistics']['min_price']} – "
                            f"₹{info['statistics']['max_price']}\n"
                            f"- Latest Trend: {info['trend']}\n"
                            f"- Risk Level:   {info['risk']}"
                        )

            # ── Model performance questions ─────────────────────────────────
            if any(kw in question_lower for kw in ["model", "prediction", "accuracy"]):
                perf = self.query_model_performance()
                if "winner" in perf:
                    return (
                        f"**Model Performance Comparison:**\n"
                        f"- Winner: {perf['winner']} Model\n"
                        f"- Advanced Wins: {perf['advanced_wins']}/{perf['total_metrics']} metrics\n"
                        f"- Baseline Wins: {perf['baseline_wins']}/{perf['total_metrics']} metrics\n\n"
                        f"The {perf['winner']} model performs better overall."
                    )

            # ── Portfolio questions ─────────────────────────────────────────
            if any(kw in question_lower for kw in ["portfolio", "allocation", "invest"]):
                portfolio = self.query_portfolio()
                if "best_strategy" in portfolio:
                    alloc_text = ", ".join(
                        f"{stock}: {weight:.1f}%"
                        for stock, weight in list(portfolio["allocation"].items())[:3]
                    )
                    return (
                        f"**Portfolio Recommendation:**\n"
                        f"- Strategy: {portfolio['best_strategy']}\n"
                        f"- Expected Return: {portfolio['expected_return']:.2f}%\n"
                        f"- Risk (Volatility): {portfolio['volatility']:.2f}%\n"
                        f"- Sharpe Ratio: {portfolio['sharpe_ratio']:.4f}\n"
                        f"- Top Allocations: {alloc_text}\n\n"
                        f"{portfolio['recommendation']}"
                    )

            # ── General semantic search ─────────────────────────────────────
            results = self.search_knowledge_base(question, top_k=3)
            if results:
                context = "\n".join(
                    r.get("text_summary", str(r)) for r in results
                )
                return (
                    f"**Based on available data:**\n\n"
                    f"{context}\n\n"
                    f"*Retrieved from {len(results)} relevant entries*"
                )

            return (
                "I don't have enough information to answer that question. "
                "Try asking about:\n"
                "- Specific stocks (e.g., 'Tell me about RELIANCE')\n"
                "- Model performance (e.g., 'Which model is better?')\n"
                "- Portfolio allocation (e.g., 'How should I invest?')"
            )

        except Exception as e:
            return f"Error processing question: {str(e)}"

    # =========================================
    # INTERACTIVE Q&A
    # =========================================
    def interactive_qa(self):
        """Interactive question-answering session"""
        print("\n" + "=" * 70)
        print("🤖 SMART STOCK MARKET RAG - INTERACTIVE Q&A")
        print("=" * 70)
        print("\nAsk questions about stocks, models, or portfolios.")
        print("Type 'exit' or 'quit' to end the session.\n")

        while True:
            try:
                question = input("❓ Question: ").strip()

                if question.lower() in ("exit", "quit", "q"):
                    print("\n👋 Goodbye!")
                    break

                if not question:
                    continue

                print("\n💭 Thinking...")
                answer = self.answer_question(question)
                print(f"\n✅ Answer:\n{answer}\n")
                print("-" * 70)

            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}\n")

    # =========================================
    # GENERATE REPORT
    # =========================================
    def generate_report(self, output_path: Optional[str] = None):
        """Generate comprehensive RAG report"""
        try:
            if output_path is None:
                output_path = os.path.join(self.results_path, "rag_report.json")

            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            report = {
                "generated_at":              datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "knowledge_base_size":        len(self.knowledge_base),
                "model_results_available":    list(self.model_results.keys()),
                "portfolio_data_available":   bool(self.portfolio_data),
                "sample_queries": [
                    "Which model performs better?",
                    "What is the portfolio recommendation?",
                    "Tell me about RELIANCE",
                    "Tell me about TCS"
                ],
                "capabilities": [
                    "Stock information lookup",
                    "Model performance comparison",
                    "Portfolio allocation advice",
                    "Semantic knowledge search",
                    "Natural language Q&A"
                ]
            }

            with open(output_path, "w") as f:
                json.dump(report, f, indent=4)

            print(f"\n✅ RAG report saved: {output_path}")
            return report

        except Exception as e:
            print(f"❌ Error generating report: {str(e)}")
            return None


# =========================================
# PREDEFINED SAMPLE QUERIES
# =========================================
def run_sample_queries(rag: StockMarketRAG):
    """Run sample queries to demonstrate RAG capabilities"""
    print("\n" + "=" * 70)
    print("📋 SAMPLE QUERIES")
    print("=" * 70)

    queries = [
        "Which model performs better?",
        "What is the recommended portfolio allocation?",
        "What are the risk levels of different stocks?",
    ]

    for i, query in enumerate(queries, 1):
        print(f"\n{i}. Query: {query}")
        print("-" * 70)
        print(rag.answer_question(query))
        print()


# =========================================
# MAIN EXECUTION
# =========================================
def main():
    """
    Main execution.

    BUG FIXED: interactive_qa() was commented out with no way to reach it.
    Now the user is properly asked whether to enter interactive mode and the
    input() call is active (not commented out).
    """
    try:
        print("=" * 70)
        print("🤖 SMART STOCK MARKET RAG SYSTEM")
        print("=" * 70)

        # Initialise RAG (paths resolved from script location — no Colab dependency)
        rag = StockMarketRAG()

        # Load all available data
        kb_loaded        = rag.load_knowledge_base()
        model_loaded     = rag.load_model_results()    # noqa: F841
        portfolio_loaded = rag.load_portfolio_data()   # noqa: F841

        if not kb_loaded:
            print(
                "\n⚠️  Knowledge base not loaded — run the Data Pipeline first.\n"
                "   From main menu: choose Option 1 → Run Complete Pipeline.\n"
            )
            return

        # Run sample queries to show capabilities
        run_sample_queries(rag)

        # Generate a report
        rag.generate_report()

        # ── Interactive mode ────────────────────────────────────────────────
        # BUG FIXED: the input() call was commented out, making interactive
        # mode completely unreachable.  It is now active.
        print("\n" + "=" * 70)
        print("💡 INTERACTIVE MODE")
        print("=" * 70)
        print("\nWould you like to ask your own questions? (y/n): ", end="", flush=True)
        response = input().strip().lower()
        if response == "y":
            rag.interactive_qa()

        print("\n" + "=" * 70)
        print("✅ RAG SYSTEM COMPLETE")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
