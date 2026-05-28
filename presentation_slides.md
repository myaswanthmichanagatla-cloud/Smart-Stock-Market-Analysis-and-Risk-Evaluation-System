# Stock Market Analysis & Risk Evaluation System (StockRAG)
## Project Presentation Slide Guide

This document contains the visual layout design, slide notes, and exact content copy for the 10-slide presentation. It is designed around a premium **dark mode theme** with **electric teal, lavender, and warm amber** accents.

---

### Slide 1: Title & Gateway (The Pitch)
*   **Visual Layout**: Minimalist, high-impact centered design. Slate-black background with a thin glowing teal neon horizontal line separating the title and subtitle.
*   **Aesthetic**: Large bold typography, plenty of breathing room (whitespace).
*   **Slide Content**:
    *   **Title**: SMART STOCK MARKET ANALYSIS & RISK EVALUATION SYSTEM
    *   **Subtitle**: *An AI-Powered Semantic RAG Pipeline & Machine Learning Prediction Platform*
    *   **Team IDs**: SE25MAID035, SE25MAID014, SE25MAID016, SE25MAID021
    *   **Context**: Academic Research & Financial System Implementation

---

### Slide 2: The Core Problem (Traditional vs. Semantic)
*   **Visual Layout**: Split-screen two-column card comparison.
*   **Left Column (The Legacy - Red/Gray Accent)**:
    *   *Header*: TRADITIONAL STOCK SCREENERS
    *   *Body*:
        *   Relies strictly on hardcoded filters, tickers, and direct keywords.
        *   Fails to capture semantic investor intent.
        *   *Example*: Searching for "safe long-term banking stocks with stable returns" returns zero matches if the exact text isn't in the database.
*   **Right Column (The Solution - Electric Teal Accent)**:
    *   *Header*: SEMANTIC STOCK RAG
    *   *Body*:
        *   Processes natural-language queries into rich semantic embeddings.
        *   Recognizes the *context* and *intent* behind the user's investment goals.
        *   *Result*: Matches queries with stock metadata, fundamentals, risk profiles, and expected performance.

---

### Slide 3: End-to-End System Architecture
*   **Visual Layout**: Connected process flow blocks. A horizontal timeline of 5 styled boxes with arrows linking them together.
*   **Steps**:
    1.  **Natural Query Input** → "Low-risk tech stocks with high PE ratios"
    2.  **Financial Text Encoder** → Sentences tokenized and mapped via FinBERT / SentenceTransformers
    3.  **Semantic Search Index** → Cosine similarity lookup against the pre-computed Vector Index (`stock_index.pkl`)
    4.  **Top-K Retrieval** → Returns company names, risk levels, and fundamental metrics
    5.  **Downstream Action** → Populates the Interactive Dashboard and feeds predictive models

---

### Slide 4: The Financial RAG Pipeline
*   **Visual Layout**: "Interactive Terminal" box mock-up on a dark card.
*   **Mock-up Screen**:
    *   *User Query*: `"safe long-term technology stocks"`
    *   *Semantic Embedding Map*: `[0.124, -0.482, 0.891, ...]` (FinBERT Space)
    *   *Retrieved Results (Top-1)*:
        *   **Infosys (Technology)** | Similarity: `0.9123`
        *   *Retrieved Context*: "Technology company with positive returns, stable growth, and moderate PE ratio."
        *   *Risk Level*: `Low Risk` | *Close*: `₹1540.20`
*   **Key Feature**: Matches words like "safe" to "Low Risk" and "growth" to positive performance labels automatically.

---

### Slide 5: Predictive Modeling (Baseline vs. Advanced)
*   **Visual Layout**: Split layout with a detailed performance table. Highlighted "Winner" badge on the Baseline card.
*   **Performance Comparison Table**:

| Metric | Baseline (Linear Regression) | Advanced (XGBoost/NN) | Winner |
| :--- | :---: | :---: | :---: |
| **MAE** | **1.53** | 136.39 | **Baseline** |
| **MSE** | **3.74** | 22,804.59 | **Baseline** |
| **RMSE** | **1.93** | 151.01 | **Baseline** |
| **R² Score** | **0.9991** | -4.4594 | **Baseline** |
| **MAPE %** | **0.13%** | 11.46% | **Baseline** |

*   **Key Insight**: Baseline performs exceptionally well due to the clean linear nature of the core dataset, preventing Advanced models from overfitting or suffering from gradient noise. Use Baseline for rapid, low-overhead deployments.

---

### Slide 6: Risk Analysis & Portfolio Optimization
*   **Visual Layout**: Three vertical column cards representing investor portfolios.
*   **Cards**:
    *   **Conservative Profile (Amber Accent)**:
        *   *Allocation*: 80% Stocks, 20% Cash Reserve
        *   *Expected Return*: **25.66%** | *Volatility*: **7.59%**
        *   *Sharpe Ratio*: **2.85**
    *   **Moderate Profile (Teal Accent)**:
        *   *Allocation*: 90% Stocks, 10% Cash Reserve
        *   *Expected Return*: **28.86%** | *Volatility*: **8.53%**
        *   *Sharpe Ratio*: **3.01**
    *   **Aggressive Profile (Gold Accent)**:
        *   *Allocation*: 100% Stock Portfolio
        *   *Expected Return*: **32.07%** | *Volatility*: **9.48%**
        *   *Sharpe Ratio*: **3.17**
*   **System Action**: Evaluates stock volatility over historical timelines to recommend optimal allocations based on Modern Portfolio Theory (MPT).

---

### Slide 7: Interactive Live Dashboard
*   **Visual Layout**: Wireframe dashboard mock-up with callouts.
*   **Dashboard Features**:
    *   **Live Twelve Data Integration**: Proxiable backend architecture (`server.py`) serving live prices.
    *   **Dynamic Visualizations**: Real-time stock charting, price range visualizers, and moving averages.
    *   **On-the-fly RAG Q&A**: Let users type natural questions directly into the browser and see model explanations immediately.
    *   **Clean Static HTML/CSS Frontend**: Ultra-responsive styling, bypasses standard rendering latency.

---

### Slide 8: Ablation Study & Core Metrics
*   **Visual Layout**: Two large stat callout panels side-by-side.
*   **Panel 1: Semantic Relevance**:
    *   *Metric*: **0.90+ Retrieval Relevance@5**
    *   *Context*: Up from 0.70+ in Milestone 1. Verified semantic match alignment against financial analysts' recommendations.
*   **Panel 2: Classification Accuracy**:
    *   *Metric*: **0.90+ Risk Accuracy**
    *   *Context*: Classification model successfully maps complex volatility data to correct risk profiles (Low/Moderate/High).

---

### Slide 9: Future Scope & Roadmap
*   **Visual Layout**: Horizontal timeline timeline with 3 nodes.
*   **Roadmap Nodes**:
    *   **Phase 1: Real-time News Integration**
        *   Augment the RAG knowledge base with active scraping of financial headlines for sentiment analysis.
    *   **Phase 2: LLM-Driven Insights**
        *   Plug in local/cloud LLMs (e.g., Llama-3, Gemini) to write fully conversational financial narratives explaining *why* a stock was chosen.
    *   **Phase 3: Automated Rebalancing**
        *   Connect portfolio recommendations directly to retail broker APIs for automated, one-click execution.

---

### Slide 10: Conclusion & Q&A
*   **Visual Layout**: Centered elegant sign-off card.
*   **Content**:
    *   **Project Goal Achieved**: Successfully bypassed traditional rigid screeners in favor of an intuitive, semantic stock retrieval pipeline.
    *   **System Integrity**: Tested end-to-end with high retrieval relevance and highly optimized linear prediction models.
    *   **GitHub/Resource Tickers**:
        *   *Knowledge Base Size*: 5,000 processed data records
        *   *Unique Sectors*: 12 industries indexed
    *   **Thank You!** (Open for Questions)
