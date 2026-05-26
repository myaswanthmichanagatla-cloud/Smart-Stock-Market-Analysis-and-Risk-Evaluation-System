"""
ONE-TIME PATCH SCRIPT
Run this once from your src\ folder:
    python patch_fix.py
 
It will directly edit stock_data_pipeline.py, baseline_predictor.py,
and advanced_predictor.py in-place with all required fixes.
"""
 
import os
import re
 
BASE = os.path.dirname(os.path.realpath(__file__))
print(f"📁 Patching files in: {BASE}")
print("=" * 60)
 
# ── Helper ────────────────────────────────────────────────────────────────────
def patch_file(filename, replacements):
    path = os.path.join(BASE, filename)
    if not os.path.exists(path):
        print(f"❌ Not found: {path}")
        return False
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    original = content
    for old, new in replacements:
        if old in content:
            content = content.replace(old, new)
            print(f"   ✅ Fixed: {repr(old[:60])}...")
        else:
            print(f"   ⚠️  Already patched or not found: {repr(old[:60])}...")
    if content != original:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ Saved: {filename}")
    else:
        print(f"ℹ️  No changes needed: {filename}")
    return True
 
# ── 1. stock_data_pipeline.py ─────────────────────────────────────────────────
print("\n[1/3] Patching stock_data_pipeline.py ...")
 
patch_file("stock_data_pipeline.py", [
    # Fix __init__ relative paths
    (
        '''    def __init__(
    self,
    data_folder="data",
    output_file="data/stock_dataset.csv"
):
        self.data_folder = data_folder
        self.output_file = output_file''',
        '''    def __init__(
    self,
    data_folder=None,
    output_file=None
):
        _base = os.path.dirname(os.path.realpath(__file__))
        self.data_folder = data_folder or os.path.join(_base, "data")
        self.output_file = output_file or os.path.join(_base, "data", "stock_dataset.csv")'''
    ),
    # Fix save_rag_knowledge_base default path
    (
        '        output_json="data/rag_knowledge_base.json"\n    ):',
        '        output_json=None\n    ):\n        if output_json is None:\n            _base = os.path.dirname(os.path.realpath(__file__))\n            output_json = os.path.join(_base, "data", "rag_knowledge_base.json")'
    ),
    # Fix dropna wiping all rows
    (
        '            # Drop NaNs from indicators\n            initial_rows = len(df)\n            df.dropna(inplace=True)',
        '            # Drop NaNs from indicators — only on essential columns\n            initial_rows = len(df)\n            key_cols = ["open", "high", "low", "close", "volume",\n                        "rsi", "macd", "sma_20", "target_next_close"]\n            df.dropna(subset=key_cols, inplace=True)'
    ),
])
 
# ── 2. baseline_predictor.py ──────────────────────────────────────────────────
print("\n[2/3] Patching baseline_predictor.py ...")
 
patch_file("baseline_predictor.py", [
    (
        'if __name__ == "__main__":\n    DATA_PATH = "/content/smart_stock_market_project/data/stock_dataset.csv"\n    MODEL_PATH = "/content/smart_stock_market_project/models/baseline_model.pkl"',
        'if __name__ == "__main__":\n    _BASE      = os.path.dirname(os.path.realpath(__file__))\n    DATA_PATH  = os.path.join(_BASE, "data",   "stock_dataset.csv")\n    MODEL_PATH = os.path.join(_BASE, "models", "baseline_model.pkl")\n    os.makedirs(os.path.join(_BASE, "models"), exist_ok=True)'
    ),
])
 
# ── 3. advanced_predictor.py ──────────────────────────────────────────────────
print("\n[3/3] Patching advanced_predictor.py ...")
 
patch_file("advanced_predictor.py", [
    (
        'if __name__ == "__main__":\n    DATA_PATH = "/content/smart_stock_market_project/data/stock_dataset.csv"\n    MODEL_PATH = "/content/smart_stock_market_project/models/advanced_model.pkl"',
        'if __name__ == "__main__":\n    _BASE      = os.path.dirname(os.path.realpath(__file__))\n    DATA_PATH  = os.path.join(_BASE, "data",   "stock_dataset.csv")\n    MODEL_PATH = os.path.join(_BASE, "models", "advanced_model.pkl")\n    os.makedirs(os.path.join(_BASE, "models"), exist_ok=True)'
    ),
])
 
# ── Done ──────────────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("✅ PATCH COMPLETE — now delete __pycache__ and run main.py")
print("=" * 60)
print("\nRun these commands:")
print('   rmdir /s /q __pycache__')
print('   python main.py')
 