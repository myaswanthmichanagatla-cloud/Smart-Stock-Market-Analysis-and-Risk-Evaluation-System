#!/usr/bin/env python3
"""
Smart Stock Market RAG System
Retrieval-Augmented Generation for Stock Market Insights
"""

import os
import sys
import re
import json
import numpy as np
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional
import warnings
warnings.filterwarnings("ignore")

_SCRIPT_DIR  = os.path.dirname(os.path.realpath(__file__))
_DEFAULT_KB   = os.path.join(_SCRIPT_DIR, "data",    "rag_knowledge_base.json")
_DEFAULT_RES  = os.path.join(_SCRIPT_DIR, "results")


class StockMarketRAG:
    def __init__(
        self,
        kb_path: str   = _DEFAULT_KB,
        results_path: str = _DEFAULT_RES
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

            csv_path = os.path.join(os.path.dirname(self.kb_path), "stock_dataset.csv")
            if os.path.exists(csv_path):
                self.stock_data = pd.read_csv(csv_path)
                print(f"   ✅ Loaded stock dataset: {self.stock_data.shape}")
            else:
                self.stock_data = pd.DataFrame(self.knowledge_base)

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
        try:
            print("\n📊 Loading Model Results...")

            files = {
                "baseline":      "baseline_results.json",
                "advanced":      "advanced_results.json",
                "comparison":    "model_comparison.json",
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
    # SEMANTIC SEARCH — FIXED
    # =========================================
    def search_knowledge_base(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Search knowledge base.
        Now handles numeric filters like 'RSI above 65' or 'price below 500'
        before falling back to keyword matching.
        """
        try:
            query_lower = query.lower()
            query_terms = set(query_lower.split())

            # ── STEP 1: Numeric filter detection ────────────────────────────
            # Catches: "rsi above 65", "close below 500", "volatility over 0.3"
            num_match = re.search(
                r'(rsi|macd|close|return|price|volatility)\s*(above|below|over|under|>|<)\s*([\d.]+)',
                query_lower
            )

            if num_match:
                field = num_match.group(1)
                op    = num_match.group(2)
                val   = float(num_match.group(3))

                # Map plain words to actual column names
                field_map = {"price": "close", "return": "daily_return_pct"}
                field = field_map.get(field, field)

                gt = op in ("above", "over", ">")

                # Filter entries by actual numeric value
                filtered = [
                    e for e in self.knowledge_base
                    if field in e and e[field] is not None
                    and (float(e[field]) > val if gt else float(e[field]) < val)
                ]

                # Return ONE row per stock (most recent date)
                seen = {}
                for e in sorted(filtered, key=lambda x: x.get("date", ""), reverse=True):
                    sym = e.get("stock_symbol", "")
                    if sym not in seen:
                        seen[sym] = e

                return list(seen.values())[:top_k]

            # ── STEP 2: Keyword fallback ─────────────────────────────────────
            results = []
            for entry in self.knowledge_base:
                text  = entry.get("text_summary", str(entry)).lower()
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
                "trend": stock_entries[-1].get("trend_label",   "Unknown"),
                "risk":  stock_entries[-1].get("risk_category", "Unknown"),
                "latest_entry": stock_entries[-1]
            }

        except Exception as e:
            return {"error": str(e)}

    # =========================================
    # QUERY MODEL PERFORMANCE
    # =========================================
    def query_model_performance(self, model_type: str = "comparison") -> Dict[str, Any]:
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
    # ANSWER QUESTION — FIXED
    # =========================================
    def answer_question(self, question: str) -> str:
        """
        Answer a natural language question using RAG.
        Now handles:
          - RSI / MACD numeric filters  ("RSI above 65")
          - Risk category filters       ("high risk stocks")
          - Stock-specific queries      ("tell me about TCS")
          - Model performance queries   ("which model is better")
          - Portfolio queries           ("how should I invest")
          - General keyword fallback
        """
        try:
            question_lower = question.lower()

            # Build dynamic symbol list from KB
            known_symbols = {
                entry.get("stock_symbol", "").lower()
                for entry in self.knowledge_base
                if entry.get("stock_symbol")
            }

            # ── 1. Stock-specific question ───────────────────────────────────
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
                        f"- Price Range: ₹{info['statistics']['min_price']} – ₹{info['statistics']['max_price']}\n"
                        f"- Latest Trend: {info['trend']}\n"
                        f"- Risk Level: {info['risk']}"
                    )

            # ── 2. Model performance ─────────────────────────────────────────
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

            # ── 3. Portfolio ─────────────────────────────────────────────────
            if any(kw in question_lower for kw in ["portfolio", "allocation", "invest"]):
                portfolio = self.query_portfolio()
                if "best_strategy" in portfolio:
                    alloc_text = ", ".join(
                        f"{s}: {w:.1f}%"
                        for s, w in list(portfolio["allocation"].items())[:5]
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

            # ── 4. RSI / MACD technical queries ─────────────────────────────
            # Examples: "RSI above 65", "stocks with high RSI", "MACD positive"
            if "rsi" in question_lower or "macd" in question_lower:
                results = self.search_knowledge_base(question, top_k=16)
                if results:
                    lines = ["**Stocks matching your query (latest entry per stock):**\n"]
                    for r in results:
                        lines.append(
                            f"- {r.get('stock_symbol', '?')}: "
                            f"RSI={float(r.get('rsi', 0)):.1f}, "
                            f"MACD={float(r.get('macd', 0)):.2f}, "
                            f"Trend={r.get('trend_label', '?')}, "
                            f"Close=₹{float(r.get('close', 0)):.2f} "
                            f"({r.get('date', '?')})"
                        )
                    return "\n".join(lines)
                return "No stocks matched that RSI/MACD filter in the knowledge base."

            # ── 5. Risk category queries ─────────────────────────────────────
            # Examples: "high risk stocks", "which stocks are low risk"
            if "risk" in question_lower:
                target = (
                    "High Risk"     if "high"     in question_lower else
                    "Low Risk"      if "low"      in question_lower else
                    "Moderate Risk" if "moderate" in question_lower else None
                )

                seen = {}
                for e in sorted(self.knowledge_base, key=lambda x: x.get("date", ""), reverse=True):
                    sym = e.get("stock_symbol", "")
                    if sym in seen:
                        continue
                    if target is None or e.get("risk_category") == target:
                        seen[sym] = e

                label = target if target else "All stocks by risk category"
                lines = [f"**{label} (latest data per stock):**\n"]
                for sym, e in sorted(seen.items()):
                    lines.append(
                        f"- {sym}: {e.get('risk_category', '?')}, "
                        f"RSI={float(e.get('rsi', 0)):.1f}, "
                        f"Close=₹{float(e.get('close', 0)):.2f}"
                    )
                return "\n".join(lines) if len(lines) > 1 else "No matching stocks found."

            # ── 6. General keyword fallback ──────────────────────────────────
            results = self.search_knowledge_base(question, top_k=10)
            if results:
                # Deduplicate: one row per stock
                seen = {}
                for r in results:
                    sym = r.get("stock_symbol", "??")
                    if sym not in seen:
                        seen[sym] = r
                lines = ["**Based on available data (one entry per stock):**\n"]
                for sym, r in seen.items():
                    lines.append(f"- {sym}: {r.get('text_summary', str(r))}")
                return "\n".join(lines)

            return (
                "I don't have enough information to answer that question.\n"
                "Try asking:\n"
                "- 'Which stocks have RSI above 65?'\n"
                "- 'Show me high risk stocks'\n"
                "- 'Tell me about RELIANCE'\n"
                "- 'Which model performs better?'\n"
                "- 'What is the portfolio allocation?'"
            )

        except Exception as e:
            return f"Error processing question: {str(e)}"

    # =========================================
    # INTERACTIVE Q&A
    # =========================================
    def interactive_qa(self):
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
        try:
            if output_path is None:
                output_path = os.path.join(self.results_path, "rag_report.json")

            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            report = {
                "generated_at":            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "knowledge_base_size":      len(self.knowledge_base),
                "model_results_available":  list(self.model_results.keys()),
                "portfolio_data_available": bool(self.portfolio_data),
                "sample_queries": [
                    "Which stocks have RSI above 65?",
                    "Show me high risk stocks",
                    "Which model performs better?",
                    "What is the portfolio allocation?",
                    "Tell me about RELIANCE"
                ],
                "capabilities": [
                    "Stock information lookup",
                    "Model performance comparison",
                    "Portfolio allocation advice",
                    "Numeric filter search (RSI, MACD, price)",
                    "Risk category filtering",
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
# SAMPLE QUERIES
# =========================================
def run_sample_queries(rag: StockMarketRAG):
    print("\n" + "=" * 70)
    print("📋 SAMPLE QUERIES")
    print("=" * 70)

    queries = [
        "Which model performs better?",
        "What is the recommended portfolio allocation?",
        "Which stocks have RSI above 65?",
        "Show me high risk stocks",
    ]

    for i, query in enumerate(queries, 1):
        print(f"\n{i}. Query: {query}")
        print("-" * 70)
        print(rag.answer_question(query))
        print()


# =========================================
# MAIN
# =========================================
def main():
    try:
        print("=" * 70)
        print("🤖 SMART STOCK MARKET RAG SYSTEM")
        print("=" * 70)

        rag = StockMarketRAG()

        kb_loaded        = rag.load_knowledge_base()
        model_loaded     = rag.load_model_results()
        portfolio_loaded = rag.load_portfolio_data()

        if not kb_loaded:
            print(
                "\n⚠️  Knowledge base not loaded — run the Data Pipeline first.\n"
                "   From main menu: choose Option 1 → Run Complete Pipeline.\n"
            )
            return

        run_sample_queries(rag)
        rag.generate_report()

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