import json, pickle, argparse
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"

def load_model():
    print(f"Loading model: {MODEL_NAME} ...")
    return SentenceTransformer(MODEL_NAME)

def build_index(data_path, index_path):
    with open(data_path, "r") as f:
        stocks = json.load(f)
    print(f"Total records: {len(stocks)}")
    model = load_model()
    texts = [s.get("text_summary", "") for s in stocks]
    print("Building embeddings...")
    embeddings = model.encode(texts, show_progress_bar=True, batch_size=64)
    with open(index_path, "wb") as f:
        pickle.dump({"stocks": stocks, "embeddings": embeddings}, f)
    print(f"Index saved to: {index_path}")

def query_stocks(query, index_path, topk=5):
    with open(index_path, "rb") as f:
        index = pickle.load(f)
    stocks, embeddings = index["stocks"], index["embeddings"]
    model = load_model()
    scores = cosine_similarity(model.encode([query]), embeddings)[0]
    top_indices = np.argsort(scores)[::-1][:topk]
    print(f'\nQuery: "{query}"\n')
    print(f"{'Rank':<6}{'Score':<8}{'Symbol':<20}{'Close':<10}{'Trend':<12}{'Risk':<18}{'RSI'}")
    print("-"*80)
    for rank, idx in enumerate(top_indices, 1):
        s = stocks[idx]
        print(f"{rank:<6}{scores[idx]:<8.4f}{str(s.get('stock_symbol','N/A')):<20}{s.get('close',0):<10.2f}{s.get('trend_label','N/A'):<12}{s.get('risk_category','N/A'):<18}{s.get('rsi',0):.1f}")
        print(f"       {s.get('text_summary','')[:110]}...")
        print()

def run_ablation(index_path):
    queries = [
        "safe long-term banking stocks with stable returns",
        "high growth technology sector stocks",
        "low volatility bullish trend stocks",
        "moderate risk bearish stocks with low RSI",
        "high RSI momentum stocks",
    ]
    with open(index_path, "rb") as f:
        index = pickle.load(f)
    stocks, embeddings = index["stocks"], index["embeddings"]
    model = load_model()
    print("\n" + "="*85)
    print("ABLATION STUDY")
    print("="*85)
    print(f"\n{'Query':<50}{'Top Match':<20}{'Score':<8}{'Risk':<18}{'Trend'}")
    print("-"*100)
    for q in queries:
        scores = cosine_similarity(model.encode([q]), embeddings)[0]
        idx = np.argmax(scores)
        s = stocks[idx]
        print(f"{q[:48]:<50}{str(s.get('stock_symbol','N/A')):<20}{scores[idx]:<8.4f}{s.get('risk_category','N/A'):<18}{s.get('trend_label','N/A')}")
    print("\nDone.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["index","query","ablation"], required=True)
    parser.add_argument("--data", default="data/rag_knowledge_base.json")
    parser.add_argument("--index", default="data/stock_index.pkl")
    parser.add_argument("--query", default="safe long-term growth stocks")
    parser.add_argument("--topk", type=int, default=5)
    args = parser.parse_args()
    if args.mode == "index": build_index(args.data, args.index)
    elif args.mode == "query": query_stocks(args.query, args.index, args.topk)
    elif args.mode == "ablation": run_ablation(args.index)
