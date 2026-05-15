
#!/usr/bin/env python3
"""
Master Stock Market Analysis Pipeline
Orchestrates all components of the system
"""

import os
import sys
import time
import json
from datetime import datetime


class StockPipeline:
    """
    Master pipeline orchestrator for stock market analysis system
    
    Components:
    1. Data Pipeline - Load and process stock data
    2. Baseline Predictor - Linear regression model
    3. Advanced Predictor - XGBoost model
    4. Model Evaluation - Compare models
    5. Portfolio Optimizer - Optimal allocation
    """

    def __init__(self, base_dir="/content/smart_stock_market_project"):
        self.base_dir = base_dir
        self.data_dir = os.path.join(base_dir, "data")
        self.models_dir = os.path.join(base_dir, "models")
        self.results_dir = os.path.join(base_dir, "results")
        
        # Create directories
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.models_dir, exist_ok=True)
        os.makedirs(self.results_dir, exist_ok=True)
        
        self.start_time = None
        self.pipeline_log = []

    def log(self, message, level="INFO"):
        """Log pipeline events"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = {
            "timestamp": timestamp,
            "level": level,
            "message": message
        }
        self.pipeline_log.append(log_entry)
        
        # Print with color coding
        if level == "ERROR":
            print(f"❌ [{timestamp}] {message}")
        elif level == "SUCCESS":
            print(f"✅ [{timestamp}] {message}")
        elif level == "WARNING":
            print(f"⚠️  [{timestamp}] {message}")
        else:
            print(f"ℹ️  [{timestamp}] {message}")

    def print_header(self, title):
        """Print section header"""
        print("\n" + "=" * 70)
        print(f"  {title}")
        print("=" * 70)

    def run_step(self, step_name, script_name, description):
        """Run a pipeline step"""
        self.print_header(f"STEP: {step_name}")
        self.log(f"Starting: {description}", "INFO")
        
        script_path = os.path.join(self.base_dir, script_name)
        
        try:
            # Check if script exists
            if not os.path.exists(script_path):
                raise FileNotFoundError(f"Script not found: {script_path}")
            
            # Run the script
            start = time.time()
            result = os.system(f"python {script_path}")
            duration = time.time() - start
            
            if result == 0:
                self.log(f"Completed: {step_name} ({duration:.2f}s)", "SUCCESS")
                return True
            else:
                self.log(f"Failed: {step_name} (exit code {result})", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Error in {step_name}: {str(e)}", "ERROR")
            return False

    def check_prerequisites(self):
        """Check if all required files exist"""
        self.print_header("CHECKING PREREQUISITES")
        
        required_scripts = [
            "stock_data_pipeline.py",
            "baseline_predictor.py",
            "advanced_predictor.py",
            "evaluation.py",
            "portfolio_optimizer.py"
        ]
        
        all_exist = True
        for script in required_scripts:
            path = os.path.join(self.base_dir, script)
            if os.path.exists(path):
                self.log(f"Found: {script}", "SUCCESS")
            else:
                self.log(f"Missing: {script}", "ERROR")
                all_exist = False
        
        return all_exist

    def run_full_pipeline(self, skip_data=False):
        """Run complete pipeline"""
        self.start_time = time.time()
        
        self.print_header("🤖 STOCK MARKET ANALYSIS PIPELINE")
        print(f"Base Directory: {self.base_dir}")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Check prerequisites
        if not self.check_prerequisites():
            self.log("Prerequisites check failed. Pipeline aborted.", "ERROR")
            return False
        
        # Step 1: Data Pipeline
        if not skip_data:
            if not self.run_step(
                "1. Data Pipeline",
                "stock_data_pipeline.py",
                "Load and process stock data with technical indicators"
            ):
                self.log("Data pipeline failed. Aborting.", "ERROR")
                return False
        else:
            self.log("Skipping data pipeline (using existing data)", "WARNING")
        
        # Step 2: Baseline Predictor
        if not self.run_step(
            "2. Baseline Predictor",
            "baseline_predictor.py",
            "Train Linear Regression model"
        ):
            self.log("Baseline predictor failed. Continuing anyway.", "WARNING")
        
        # Step 3: Advanced Predictor
        if not self.run_step(
            "3. Advanced Predictor",
            "advanced_predictor.py",
            "Train XGBoost model"
        ):
            self.log("Advanced predictor failed. Continuing anyway.", "WARNING")
        
        # Step 4: Model Evaluation
        if not self.run_step(
            "4. Model Evaluation",
            "evaluation.py",
            "Compare baseline vs advanced models"
        ):
            self.log("Evaluation failed. Continuing anyway.", "WARNING")
        
        # Step 5: Portfolio Optimization
        if not self.run_step(
            "5. Portfolio Optimizer",
            "portfolio_optimizer.py",
            "Generate optimal portfolio allocation"
        ):
            self.log("Portfolio optimization failed.", "WARNING")
        
        # Pipeline complete
        total_time = time.time() - self.start_time
        
        self.print_header("PIPELINE SUMMARY")
        self.log(f"Pipeline completed in {total_time:.2f} seconds", "SUCCESS")
        
        return True

    def generate_report(self):
        """Generate pipeline execution report"""
        self.print_header("EXECUTION REPORT")
        
        report = {
            "pipeline_name": "Stock Market Analysis Pipeline",
            "execution_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_duration": time.time() - self.start_time if self.start_time else 0,
            "base_directory": self.base_dir,
            "logs": self.pipeline_log,
            "outputs": self.check_outputs()
        }
        
        # Save report
        report_path = os.path.join(self.results_dir, "pipeline_report.json")
        with open(report_path, "w") as f:
            json.dump(report, f, indent=4)
        
        self.log(f"Report saved: {report_path}", "SUCCESS")
        
        # Print summary
        print("\nGenerated Files:")
        for file_info in report["outputs"]:
            status = "✅" if file_info["exists"] else "❌"
            print(f"{status} {file_info['name']} ({file_info['size']})")
        
        return report

    def check_outputs(self):
        """Check which output files were generated"""
        expected_outputs = [
            ("data/stock_dataset.csv", "ML-ready dataset"),
            ("data/rag_knowledge_base.json", "GenAI knowledge base"),
            ("models/baseline_model.pkl", "Baseline model"),
            ("models/xgboost_model.pkl", "XGBoost model"),
            ("results/baseline_results.json", "Baseline metrics"),
            ("results/advanced_results.json", "Advanced metrics"),
            ("results/model_comparison.json", "Model comparison"),
            ("results/genai_summary.json", "GenAI summary"),
            ("results/portfolio_optimization.json", "Portfolio allocation")
        ]
        
        outputs = []
        for rel_path, description in expected_outputs:
            full_path = os.path.join(self.base_dir, rel_path)
            exists = os.path.exists(full_path)
            size = f"{os.path.getsize(full_path) / 1024:.2f} KB" if exists else "N/A"
            
            outputs.append({
                "name": rel_path,
                "description": description,
                "exists": exists,
                "size": size
            })
        
        return outputs

    def quick_status(self):
        """Quick status check of the system"""
        self.print_header("SYSTEM STATUS")
        
        outputs = self.check_outputs()
        
        total = len(outputs)
        exists = sum(1 for o in outputs if o["exists"])
        
        print(f"\nFiles Generated: {exists}/{total}")
        print(f"Completion: {exists/total*100:.1f}%")
        
        print("\nDetailed Status:")
        for output in outputs:
            status = "✅" if output["exists"] else "❌"
            print(f"{status} {output['description']:30s} ({output['size']})")


# =========================================
# COMMAND LINE INTERFACE
# =========================================
def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Stock Market Analysis Pipeline Orchestrator"
    )
    parser.add_argument(
        "--skip-data",
        action="store_true",
        help="Skip data pipeline (use existing data)"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show pipeline status only"
    )
    parser.add_argument(
        "--base-dir",
        default="/content/smart_stock_market_project",
        help="Base directory for the project"
    )
    
    args = parser.parse_args()
    
    # Initialize pipeline
    pipeline = StockPipeline(base_dir=args.base_dir)
    
    try:
        if args.status:
            # Just show status
            pipeline.quick_status()
        else:
            # Run full pipeline
            print("=" * 70)
            print("🚀 STARTING STOCK MARKET ANALYSIS PIPELINE")
            print("=" * 70)
            
            success = pipeline.run_full_pipeline(skip_data=args.skip_data)
            
            # Generate report
            pipeline.generate_report()
            
            if success:
                print("\n" + "=" * 70)
                print("✅ PIPELINE COMPLETED SUCCESSFULLY")
                print("=" * 70)
                print("\nNext Steps:")
                print("  1. Check results/ directory for outputs")
                print("  2. Review pipeline_report.json for details")
                print("  3. Use GenAI summaries for integration")
                print("=" * 70)
            else:
                print("\n" + "=" * 70)
                print("⚠️  PIPELINE COMPLETED WITH ERRORS")
                print("=" * 70)
                print("Check pipeline_report.json for details")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Pipeline failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
