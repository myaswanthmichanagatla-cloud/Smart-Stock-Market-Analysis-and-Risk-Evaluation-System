
#!/usr/bin/env python3
"""
Master Runner for Smart Stock Market Analysis System

This script orchestrates the complete pipeline:
1. Data Pipeline
2. Model Training (Baseline & Advanced)
3. Model Evaluation
4. Portfolio Optimization
5. RAG System Initialization
6. Report Generation

Usage:
    python master_runner.py [options]

Options:
    --full          Run complete pipeline (default)
    --skip-data     Skip data processing
    --skip-models   Skip model training
    --quick         Run essential components only
    --report        Generate final report only
    --interactive   Enable interactive RAG mode
"""

import os
import sys
import time
import json
import argparse
from datetime import datetime
from typing import Dict, List, Tuple


class MasterRunner:
    """
    Master orchestrator for Smart Stock Market Analysis System
    """

    def __init__(self, base_dir=None):
        if base_dir is None:
            base_dir = os.path.dirname(os.path.realpath(__file__))
        self.base_dir = base_dir
        self.start_time = None
        self.execution_log = []
        self.components_status = {}
        
        # Define component order
        self.components = [
            ("Data Pipeline", "stock_data_pipeline.py", "Process stock data and generate features"),
            ("Baseline Predictor", "baseline_predictor.py", "Train Linear Regression model"),
            ("Advanced Predictor", "advanced_predictor.py", "Train XGBoost model"),
            ("Model Evaluation", "evaluation.py", "Compare model performance"),
            ("Portfolio Optimizer", "portfolio_optimizer.py", "Generate optimal allocation"),
            ("RAG System", "smart_stock_market_rag.py", "Initialize knowledge system")
        ]

    def print_banner(self):
        """Print system banner"""
        print("\n" + "=" * 80)
        print(" " * 15 + "🤖 SMART STOCK MARKET ANALYSIS SYSTEM")
        print(" " * 20 + "GenAI-Enhanced | End-to-End ML Pipeline")
        print("=" * 80)
        print(f"\n📍 Base Directory: {self.base_dir}")
        print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)

    def log(self, message: str, level: str = "INFO"):
        """Log execution events"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        log_entry = {
            "timestamp": timestamp,
            "level": level,
            "message": message
        }
        self.execution_log.append(log_entry)
        
        # Color-coded output
        icons = {
            "INFO": "ℹ️ ",
            "SUCCESS": "✅",
            "ERROR": "❌",
            "WARNING": "⚠️ ",
            "RUNNING": "🔄"
        }
        
        icon = icons.get(level, "  ")
        print(f"{icon} [{timestamp}] {message}")

    def print_section(self, title: str, step: int = 0):
        """Print section header"""
        print("\n" + "-" * 80)
        if step > 0:
            print(f"STEP {step}: {title}")
        else:
            print(f"{title}")
        print("-" * 80)

    def check_prerequisites(self) -> bool:
        """Check if all component files exist"""
        self.print_section("CHECKING PREREQUISITES")
        
        all_exist = True
        
        for name, filename, _ in self.components:
            filepath = os.path.join(self.base_dir, filename)
            if os.path.exists(filepath):
                size = os.path.getsize(filepath) / 1024
                self.log(f"{filename:35s} ✅ ({size:.1f} KB)", "SUCCESS")
            else:
                self.log(f"{filename:35s} ❌ Missing", "ERROR")
                all_exist = False
        
        return all_exist

    def run_component(
        self, 
        name: str, 
        script: str, 
        description: str,
        critical: bool = True
    ) -> bool:
        """
        Run a single component
        
        Args:
            name: Component name
            script: Script filename
            description: Component description
            critical: Whether failure should stop pipeline
            
        Returns:
            Success status
        """
        try:
            self.log(f"Starting: {description}", "RUNNING")
            
            script_path = os.path.join(self.base_dir, script)
            
            if not os.path.exists(script_path):
                raise FileNotFoundError(f"Script not found: {script_path}")
            
            # Execute script
            import subprocess
            start = time.time()
            result = subprocess.run(
                [sys.executable, script_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd=self.base_dir
            )
            exit_code = result.returncode
            duration = time.time() - start
            
            if exit_code == 0:
                self.log(f"Completed: {name} ({duration:.1f}s)", "SUCCESS")
                self.components_status[name] = {"status": "SUCCESS", "duration": duration}
                return True
            else:
                msg = f"Failed: {name} (exit code {exit_code})"
                if critical:
                    self.log(msg, "ERROR")
                    self.components_status[name] = {"status": "ERROR", "duration": duration}
                    return False
                else:
                    self.log(msg, "WARNING")
                    self.components_status[name] = {"status": "WARNING", "duration": duration}
                    return True  # Continue anyway
                    
        except Exception as e:
            self.log(f"Exception in {name}: {str(e)}", "ERROR")
            self.components_status[name] = {"status": "ERROR", "error": str(e)}
            return not critical

    def run_full_pipeline(self, skip_data: bool = False, skip_models: bool = False):
        """Run complete pipeline"""
        self.start_time = time.time()
        
        # Step 1: Check prerequisites
        if not self.check_prerequisites():
            self.log("Prerequisites check failed. Some components missing.", "ERROR")
            return False
        
        success = True
        step = 1
        
        # Step 2: Data Pipeline
        if not skip_data:
            self.print_section(self.components[0][2], step)
            step += 1
            if not self.run_component(*self.components[0], critical=True):
                self.log("Data pipeline failed. Aborting.", "ERROR")
                return False
        else:
            self.log("Skipping data pipeline (using existing data)", "WARNING")
            self.components_status["Data Pipeline"] = {"status": "SKIPPED"}
        
        # Step 3: Model Training
        if not skip_models:
            for i in range(1, 3):  # Baseline and Advanced
                self.print_section(self.components[i][2], step)
                step += 1
                self.run_component(*self.components[i], critical=False)
        else:
            self.log("Skipping model training (using existing models)", "WARNING")
            self.components_status["Baseline Predictor"] = {"status": "SKIPPED"}
            self.components_status["Advanced Predictor"] = {"status": "SKIPPED"}
        
        # Step 4: Evaluation
        self.print_section(self.components[3][2], step)
        step += 1
        self.run_component(*self.components[3], critical=False)
        
        # Step 5: Portfolio Optimization
        self.print_section(self.components[4][2], step)
        step += 1
        self.run_component(*self.components[4], critical=False)
        
        # Step 6: RAG System
        self.print_section(self.components[5][2], step)
        step += 1
        self.run_component(*self.components[5], critical=False)
        
        return True

    def run_quick_mode(self):
        """Run essential components only"""
        self.start_time = time.time()
        
        self.log("Running in QUICK mode (essential components only)", "INFO")
        
        essential = [0, 3, 4]  # Data, Evaluation, Portfolio
        
        for idx in essential:
            name, script, desc = self.components[idx]
            self.print_section(desc)
            self.run_component(name, script, desc, critical=False)

    def verify_outputs(self) -> Dict[str, bool]:
        """Verify all expected outputs exist"""
        self.print_section("VERIFYING OUTPUTS")
        
        expected_files = {
            "data/stock_dataset.csv": "Stock dataset",
            "data/rag_knowledge_base.json": "RAG knowledge base",
            "models/baseline_model.pkl": "Baseline model",
            "models/xgboost_model.pkl": "XGBoost model",
            "results/baseline_results.json": "Baseline results",
            "results/advanced_results.json": "Advanced results",
            "results/model_comparison.json": "Model comparison",
            "results/genai_summary.json": "GenAI summary",
            "results/portfolio_optimization.json": "Portfolio allocation",
            "results/rag_report.json": "RAG report"
        }
        
        verification = {}
        exists_count = 0
        
        for rel_path, description in expected_files.items():
            full_path = os.path.join(self.base_dir, rel_path)
            exists = os.path.exists(full_path)
            verification[rel_path] = exists
            
            if exists:
                size = os.path.getsize(full_path) / 1024
                self.log(f"{description:30s} ✅ ({size:>8.2f} KB)", "SUCCESS")
                exists_count += 1
            else:
                self.log(f"{description:30s} ❌ Missing", "ERROR")
        
        completion = (exists_count / len(expected_files)) * 100
        
        print("\n" + "=" * 80)
        print(f"📊 COMPLETION: {exists_count}/{len(expected_files)} files ({completion:.1f}%)")
        print("=" * 80)
        
        return verification

    def generate_final_report(self):
        """Generate comprehensive final report"""
        self.print_section("GENERATING FINAL REPORT")
        
        total_duration = time.time() - self.start_time if self.start_time else 0
        
        report = {
            "system_name": "Smart Stock Market Analysis System",
            "execution_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_duration_seconds": round(total_duration, 2),
            "base_directory": self.base_dir,
            "components_status": self.components_status,
            "execution_log": self.execution_log[-50:],  # Last 50 entries
            "outputs_verification": self.verify_outputs()
        }
        
        # Add summary statistics
        successful = sum(1 for v in self.components_status.values() if v.get("status") == "SUCCESS")
        failed = sum(1 for v in self.components_status.values() if v.get("status") == "ERROR")
        skipped = sum(1 for v in self.components_status.values() if v.get("status") == "SKIPPED")
        
        report["summary"] = {
            "total_components": len(self.components_status),
            "successful": successful,
            "failed": failed,
            "skipped": skipped,
            "success_rate": f"{(successful/(successful+failed)*100):.1f}%" if (successful+failed) > 0 else "N/A"
        }
        
        # Save report
        report_path = os.path.join(self.base_dir, "results", "master_execution_report.json")
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        
        with open(report_path, "w") as f:
            json.dump(report, f, indent=4)
        
        self.log(f"Report saved: {report_path}", "SUCCESS")
        
        return report

    def print_final_summary(self, report: Dict):
        """Print final execution summary"""
        print("\n" + "=" * 80)
        print(" " * 25 + "📊 EXECUTION SUMMARY")
        print("=" * 80)
        
        summary = report["summary"]
        
        print(f"\n⏱️  Total Duration: {report['total_duration_seconds']:.1f} seconds")
        print(f"✅ Successful: {summary['successful']}")
        print(f"❌ Failed: {summary['failed']}")
        print(f"⏭️  Skipped: {summary['skipped']}")
        print(f"📈 Success Rate: {summary['success_rate']}")
        
        print("\n" + "-" * 80)
        print("COMPONENT STATUS:")
        print("-" * 80)
        
        for component, status in self.components_status.items():
            status_icon = {
                "SUCCESS": "✅",
                "ERROR": "❌",
                "WARNING": "⚠️ ",
                "SKIPPED": "⏭️ "
            }.get(status.get("status"), "❓")
            
            duration = status.get("duration", 0)
            print(f"{status_icon} {component:30s} ({duration:.1f}s)")
        
        print("\n" + "=" * 80)
        
        # Check if all critical components succeeded
        critical_success = all(
            self.components_status.get(name, {}).get("status") in ["SUCCESS", "SKIPPED"]
            for name, _, _ in self.components[:4]  # First 4 are critical
        )
        
        if critical_success:
            print("🎉 PIPELINE COMPLETED SUCCESSFULLY!")
        else:
            print("⚠️  PIPELINE COMPLETED WITH ERRORS")
        
        print("=" * 80)
        
        print("\n📁 Generated Files:")
        print("   📊 Stock dataset & RAG knowledge base")
        print("   🤖 Trained ML models (Baseline & XGBoost)")
        print("   📈 Model evaluation & comparison")
        print("   💼 Portfolio optimization strategies")
        print("   🧠 RAG system initialized")
        
        print("\n💡 Next Steps:")
        print("   1. Review results in: /results/")
        print("   2. Load models for predictions")
        print("   3. Use RAG system for Q&A")
        print("   4. Deploy for production")
        
        print("\n🔗 Quick Access:")
        print(f"   Master Report: {self.base_dir}/results/master_execution_report.json")
        print(f"   GenAI Summary: {self.base_dir}/results/genai_summary.json")
        print(f"   Portfolio: {self.base_dir}/results/portfolio_optimization.json")
        
        print("\n" + "=" * 80)

    def run_interactive_rag(self):
        """Launch interactive RAG session"""
        try:
            self.print_section("LAUNCHING INTERACTIVE RAG")
            
            sys.path.append(self.base_dir)
            from smart_stock_market_rag import StockMarketRAG
            
            rag = StockMarketRAG()
            rag.load_knowledge_base()
            rag.load_model_results()
            rag.load_portfolio_data()
            
            rag.interactive_qa()
            
        except Exception as e:
            self.log(f"RAG session error: {str(e)}", "ERROR")


# =========================================
# MAIN EXECUTION
# =========================================
def main():
    """Main entry point"""
    
    parser = argparse.ArgumentParser(
        description="Smart Stock Market Analysis System - Master Runner"
    )
    
    parser.add_argument(
        "--mode",
        choices=["full", "quick", "report"],
        default="full",
        help="Execution mode (default: full)"
    )
    
    parser.add_argument(
        "--skip-data",
        action="store_true",
        help="Skip data pipeline (use existing data)"
    )
    
    parser.add_argument(
        "--skip-models",
        action="store_true",
        help="Skip model training (use existing models)"
    )
    
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Enable interactive RAG mode after execution"
    )
    
    parser.add_argument(
        "--base-dir",
        default=os.path.dirname(os.path.realpath(__file__)),
        help="Base directory for the project"
    )
    
    args = parser.parse_args()
    
    # Initialize runner
    runner = MasterRunner(base_dir=args.base_dir)
    runner.print_banner()
    
    try:
        # Execute based on mode
        if args.mode == "report":
            # Report only
            runner.verify_outputs()
            report = runner.generate_final_report()
            runner.print_final_summary(report)
            
        elif args.mode == "quick":
            # Quick mode
            runner.run_quick_mode()
            report = runner.generate_final_report()
            runner.print_final_summary(report)
            
        else:
            # Full mode
            success = runner.run_full_pipeline(
                skip_data=args.skip_data,
                skip_models=args.skip_models
            )
            
            report = runner.generate_final_report()
            runner.print_final_summary(report)
        
        # Interactive RAG (if requested)
        if args.interactive:
            runner.run_interactive_rag()
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Execution interrupted by user")
        return 1
        
    except Exception as e:
        print(f"\n\n❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
