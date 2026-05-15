
#!/usr/bin/env python3
"""
Smart Stock Market Analysis System - Main Entry Point

This is the primary interface for the entire system.
Simple, clean, and user-friendly.

Quick Start:
    python main.py
"""

import os
import sys
import json
from datetime import datetime


# =========================================
# SYSTEM CONFIGURATION
# =========================================

class Config:
    """System configuration"""
    BASE_DIR = "/content/smart_stock_market_project"
    DATA_DIR = os.path.join(BASE_DIR, "data")
    MODELS_DIR = os.path.join(BASE_DIR, "models")
    RESULTS_DIR = os.path.join(BASE_DIR, "results")
    
    # File paths
    DATASET = os.path.join(DATA_DIR, "stock_dataset.csv")
    RAG_KB = os.path.join(DATA_DIR, "rag_knowledge_base.json")
    BASELINE_MODEL = os.path.join(MODELS_DIR, "baseline_model.pkl")
    XGBOOST_MODEL = os.path.join(MODELS_DIR, "xgboost_model.pkl")
    
    # Component scripts
    COMPONENTS = {
        "data": "stock_data_pipeline.py",
        "baseline": "baseline_predictor.py",
        "advanced": "advanced_predictor.py",
        "evaluation": "evaluation.py",
        "portfolio": "portfolio_optimizer.py",
        "rag": "smart_stock_market_rag.py"
    }


# =========================================
# UTILITIES
# =========================================

def print_header():
    """Print system header"""
    print("\n" + "=" * 80)
    print("""
    ╔═══════════════════════════════════════════════════════════════════════╗
    ║                                                                       ║
    ║        🤖 SMART STOCK MARKET ANALYSIS SYSTEM 🤖                      ║
    ║                                                                       ║
    ║              GenAI-Enhanced | ML-Powered | End-to-End                ║
    ║                                                                       ║
    ╚═══════════════════════════════════════════════════════════════════════╝
    """)
    print("=" * 80)


def print_menu():
    """Print main menu"""
    print("\n" + "=" * 80)
    print("📋 MAIN MENU")
    print("=" * 80)
    print("""
    1️⃣   RUN COMPLETE PIPELINE
         Execute all components from data processing to RAG system
    
    2️⃣   RUN INDIVIDUAL COMPONENTS
         Choose specific components to run
    
    3️⃣   VIEW SYSTEM STATUS
         Check what has been generated and system health
    
    4️⃣   QUERY RAG SYSTEM
         Ask questions about your stock data
    
    5️⃣   VIEW RESULTS
         See model performance, portfolio allocation, summaries
    
    6️⃣   GENERATE REPORT
         Create comprehensive analysis report
    
    7️⃣   HELP & DOCUMENTATION
         Learn how to use the system
    
    0️⃣   EXIT
         Close the application
    """)
    print("=" * 80)


def check_system_status():
    """Check which components have been run"""
    print("\n" + "=" * 80)
    print("🔍 SYSTEM STATUS CHECK")
    print("=" * 80)
    
    files = {
        "📊 Stock Dataset": Config.DATASET,
        "🧠 RAG Knowledge Base": Config.RAG_KB,
        "🤖 Baseline Model": Config.BASELINE_MODEL,
        "🚀 XGBoost Model": Config.XGBOOST_MODEL,
        "📈 Baseline Results": os.path.join(Config.RESULTS_DIR, "baseline_results.json"),
        "📊 Advanced Results": os.path.join(Config.RESULTS_DIR, "advanced_results.json"),
        "🔀 Model Comparison": os.path.join(Config.RESULTS_DIR, "model_comparison.json"),
        "🤖 GenAI Summary": os.path.join(Config.RESULTS_DIR, "genai_summary.json"),
        "💼 Portfolio Optimization": os.path.join(Config.RESULTS_DIR, "portfolio_optimization.json")
    }
    
    exists_count = 0
    total = len(files)
    
    print(f"\n{'Component':40s} {'Status':10s} {'Size':15s}")
    print("-" * 80)
    
    for name, path in files.items():
        if os.path.exists(path):
            size = os.path.getsize(path) / 1024
            print(f"{name:40s} {'✅':10s} {size:>10.2f} KB")
            exists_count += 1
        else:
            print(f"{name:40s} {'❌':10s} {'Not found':>15s}")
    
    print("-" * 80)
    completion = (exists_count / total) * 100
    print(f"\n📊 System Completion: {exists_count}/{total} ({completion:.1f}%)")
    
    if completion == 100:
        print("\n✅ All components generated! System ready.")
    elif completion >= 50:
        print("\n⚠️  Partial completion. Some components missing.")
    else:
        print("\n❌ Most components missing. Run pipeline first.")
    
    print("=" * 80)
    
    return completion


def run_component(component_name):
    """Run a specific component"""
    if component_name not in Config.COMPONENTS:
        print(f"❌ Unknown component: {component_name}")
        return False
    
    script = Config.COMPONENTS[component_name]
    script_path = os.path.join(Config.BASE_DIR, script)
    
    if not os.path.exists(script_path):
        print(f"❌ Script not found: {script_path}")
        return False
    
    print(f"\n🔄 Running {component_name}...")
    print("-" * 80)
    
    result = os.system(f"python {script_path}")
    
    if result == 0:
        print(f"\n✅ {component_name} completed successfully")
        return True
    else:
        print(f"\n❌ {component_name} failed (exit code: {result})")
        return False


def run_full_pipeline():
    """Run complete pipeline"""
    print("\n" + "=" * 80)
    print("🚀 RUNNING COMPLETE PIPELINE")
    print("=" * 80)
    
    components = [
        ("data", "📊 Data Pipeline"),
        ("baseline", "🤖 Baseline Model"),
        ("advanced", "🚀 Advanced Model"),
        ("evaluation", "📈 Model Evaluation"),
        ("portfolio", "💼 Portfolio Optimization"),
        ("rag", "🧠 RAG System")
    ]
    
    results = {}
    
    for comp_key, comp_name in components:
        print(f"\n{'='*80}")
        print(f"Running: {comp_name}")
        print("=" * 80)
        
        success = run_component(comp_key)
        results[comp_name] = "✅ Success" if success else "❌ Failed"
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 PIPELINE EXECUTION SUMMARY")
    print("=" * 80)
    
    for comp, status in results.items():
        print(f"{comp:40s} {status}")
    
    successful = sum(1 for s in results.values() if "Success" in s)
    print(f"\n✅ Success Rate: {successful}/{len(results)} ({successful/len(results)*100:.1f}%)")
    print("=" * 80)


def run_individual_components():
    """Menu for running individual components"""
    print("\n" + "=" * 80)
    print("🎯 INDIVIDUAL COMPONENTS")
    print("=" * 80)
    print("""
    1. Data Pipeline (Process stock data)
    2. Baseline Model (Linear Regression)
    3. Advanced Model (XGBoost)
    4. Model Evaluation (Compare models)
    5. Portfolio Optimization (Asset allocation)
    6. RAG System (Knowledge Q&A)
    
    0. Back to main menu
    """)
    print("=" * 80)
    
    choice = input("\n👉 Select component (0-6): ").strip()
    
    component_map = {
        "1": "data",
        "2": "baseline",
        "3": "advanced",
        "4": "evaluation",
        "5": "portfolio",
        "6": "rag"
    }
    
    if choice in component_map:
        run_component(component_map[choice])
    elif choice == "0":
        return
    else:
        print("❌ Invalid choice")


def view_results():
    """Display key results"""
    print("\n" + "=" * 80)
    print("📊 RESULTS VIEWER")
    print("=" * 80)
    print("""
    1. Model Comparison
    2. GenAI Summary
    3. Portfolio Allocation
    4. All Results
    
    0. Back to main menu
    """)
    print("=" * 80)
    
    choice = input("\n👉 Select (0-4): ").strip()
    
    if choice == "1":
        show_model_comparison()
    elif choice == "2":
        show_genai_summary()
    elif choice == "3":
        show_portfolio()
    elif choice == "4":
        show_all_results()
    elif choice == "0":
        return
    else:
        print("❌ Invalid choice")


def show_model_comparison():
    """Show model comparison"""
    path = os.path.join(Config.RESULTS_DIR, "model_comparison.json")
    
    if not os.path.exists(path):
        print("\n❌ Model comparison not available. Run evaluation first.")
        return
    
    with open(path, "r") as f:
        comparison = json.load(f)
    
    print("\n" + "=" * 80)
    print("🔀 MODEL COMPARISON")
    print("=" * 80)
    
    print(f"\n{'Metric':15s} {'Baseline':>12s} {'Advanced':>12s} {'Better':>12s} {'Improvement':>12s}")
    print("-" * 80)
    
    for metric, data in comparison.items():
        print(
            f"{metric:15s} "
            f"{data.get('Baseline', 0):>12.4f} "
            f"{data.get('Advanced', 0):>12.4f} "
            f"{data.get('Better_Model', 'N/A'):>12s} "
            f"{data.get('Improvement_%', 0):>11.2f}%"
        )
    
    print("=" * 80)


def show_genai_summary():
    """Show GenAI summary"""
    path = os.path.join(Config.RESULTS_DIR, "genai_summary.json")
    
    if not os.path.exists(path):
        print("\n❌ GenAI summary not available.")
        return
    
    with open(path, "r") as f:
        summary = json.load(f)
    
    print("\n" + "=" * 80)
    print("🤖 GENAI SUMMARY")
    print("=" * 80)
    
    if "natural_language_summary" in summary:
        print(f"\n{summary['natural_language_summary']}")
    
    if "winner" in summary:
        print(f"\n🏆 Winner: {summary['winner']}")
        print(f"📊 Advanced Wins: {summary.get('advanced_wins', 0)}")
        print(f"📊 Baseline Wins: {summary.get('baseline_wins', 0)}")
    
    print("=" * 80)


def show_portfolio():
    """Show portfolio allocation"""
    path = os.path.join(Config.RESULTS_DIR, "portfolio_optimization.json")
    
    if not os.path.exists(path):
        print("\n❌ Portfolio data not available.")
        return
    
    with open(path, "r") as f:
        portfolio = json.load(f)
    
    print("\n" + "=" * 80)
    print("💼 PORTFOLIO ALLOCATION")
    print("=" * 80)
    
    if "summary" in portfolio:
        summary = portfolio["summary"]
        print(f"\n🎯 Best Strategy: {summary.get('best_strategy', 'N/A')}")
        print(f"📈 Expected Return: {summary.get('best_expected_return', 0):.2f}%")
        print(f"📊 Volatility: {summary.get('best_volatility', 0):.2f}%")
        print(f"⚡ Sharpe Ratio: {summary.get('best_sharpe_ratio', 0):.4f}")
        
        if "best_weights" in summary:
            print("\n💰 Allocation:")
            for stock, weight in summary["best_weights"].items():
                print(f"   {stock:15s}: {weight:>6.2f}%")
    
    print("=" * 80)


def show_all_results():
    """Show all available results"""
    show_model_comparison()
    input("\nPress Enter to continue...")
    show_genai_summary()
    input("\nPress Enter to continue...")
    show_portfolio()


def generate_report():
    """Generate comprehensive report"""
    print("\n" + "=" * 80)
    print("📄 GENERATING COMPREHENSIVE REPORT")
    print("=" * 80)
    
    completion = check_system_status()
    
    report = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "system_completion": f"{completion:.1f}%",
        "recommendation": "System ready!" if completion == 100 else "Run missing components"
    }
    
    report_path = os.path.join(Config.RESULTS_DIR, "system_report.json")
    os.makedirs(Config.RESULTS_DIR, exist_ok=True)
    
    with open(report_path, "w") as f:
        json.dump(report, f, indent=4)
    
    print(f"\n✅ Report saved: {report_path}")
    print("=" * 80)


def show_help():
    """Show help and documentation"""
    print("\n" + "=" * 80)
    print("📖 HELP & DOCUMENTATION")
    print("=" * 80)
    print("""
    QUICK START:
    ============
    1. Run Complete Pipeline (Option 1)
    2. View Results (Option 5)
    3. Query RAG System (Option 4)
    
    SYSTEM COMPONENTS:
    ==================
    • Data Pipeline: Processes stock data with 40+ features
    • Baseline Model: Linear Regression predictor
    • Advanced Model: XGBoost for better accuracy
    • Evaluation: Compares both models
    • Portfolio: Optimizes asset allocation
    • RAG System: Natural language Q&A
    
    TYPICAL WORKFLOW:
    =================
    First Time:
      → Run Complete Pipeline (Option 1)
      → Wait for completion
      → View Results (Option 5)
    
    Subsequent Use:
      → Check Status (Option 3)
      → Query RAG (Option 4)
      → View specific results (Option 5)
    
    TIPS:
    =====
    ✓ Always run complete pipeline first
    ✓ Check system status to verify completion
    ✓ Use RAG for intelligent queries
    ✓ Generate report for comprehensive overview
    """)
    print("=" * 80)


# =========================================
# MAIN FUNCTION
# =========================================

def main():
    """Main application loop"""
    
    # Ensure directories exist
    for directory in [Config.DATA_DIR, Config.MODELS_DIR, Config.RESULTS_DIR]:
        os.makedirs(directory, exist_ok=True)
    
    print_header()
    
    while True:
        print_menu()
        
        choice = input("\n👉 Enter your choice (0-7): ").strip()
        
        if choice == "1":
            run_full_pipeline()
        
        elif choice == "2":
            run_individual_components()
        
        elif choice == "3":
            check_system_status()
        
        elif choice == "4":
            print("\n💡 RAG System requires interactive terminal.")
            print("   Run: python -c 'from smart_stock_market_rag import *; rag = StockMarketRAG(); rag.load_knowledge_base(); rag.interactive_qa()'")
        
        elif choice == "5":
            view_results()
        
        elif choice == "6":
            generate_report()
        
        elif choice == "7":
            show_help()
        
        elif choice == "0":
            print("\n" + "=" * 80)
            print("👋 Thank you for using Smart Stock Market Analysis System!")
            print("=" * 80)
            print()
            break
        
        else:
            print("\n❌ Invalid choice. Please select 0-7.")
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 System interrupted. Goodbye!")
    except Exception as e:
        print(f"\n\n❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
