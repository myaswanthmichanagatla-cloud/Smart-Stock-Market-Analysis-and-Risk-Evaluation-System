#!/usr/bin/env python3
"""
Generate Presentation Script for StockMarketRAG
Uses python-pptx to programmatically construct a premium, creative, dark-themed 16:9 slide deck.
"""

import sys
import os

# Define color palette (RGB)
BG_DEEP_NAVY = (10, 25, 47)      # #0A192F (Slide background)
BG_CARD_NAVY = (23, 42, 69)      # #172A45 (Card background)
ACCENT_TEAL  = (20, 233, 192)    # #14E9C0 (Semantic highlights)
ACCENT_AMBER = (245, 158, 11)    # #F59E0B (Risk/Warning)
TEXT_WHITE   = (248, 250, 252)   # #F8FAFC (Primary headers/body)
TEXT_MUTED   = (148, 163, 184)   # #94A3B8 (Subtext)
BORDER_SLATE = (51, 65, 85)      # #334155 (Borders/lines)
CARD_RED     = (45, 27, 30)       # #2D1B1E (Red card)
CARD_GREEN   = (16, 44, 37)       # #102C25 (Teal card)

def main():
    try:
        from pptx import Presentation
        from pptx.util import Inches, Pt
        from pptx.dml.color import RGBColor
        from pptx.enum.text import PP_ALIGN
        from pptx.enum.shapes import MSO_SHAPE
    except ImportError:
        print("[ERROR] python-pptx is not installed.")
        print("[INFO] Run: pip install python-pptx")
        sys.exit(1)

    prs = Presentation()
    
    # Set to widescreen 16:9 layout
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    
    blank_layout = prs.slide_layouts[6] # Blank slide layout

    # Helper function to add slide background
    def apply_background(slide, color):
        rect = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), prs.slide_width, prs.slide_height
        )
        rect.fill.solid()
        rect.fill.fore_color.rgb = RGBColor(*color)
        rect.line.fill.background() # No border
        return rect

    # Helper function to create standard text boxes
    def add_textbox(slide, left, top, width, height, text, font_size=14, bold=False, color=TEXT_WHITE, font_name="Calibri", align=PP_ALIGN.LEFT):
        tx_box = slide.shapes.add_textbox(left, top, width, height)
        tf = tx_box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_bottom = tf.margin_right = 0
        p = tf.paragraphs[0]
        p.text = text
        p.alignment = align
        p.font.name = font_name
        p.font.size = Pt(font_size)
        p.font.bold = bold
        p.font.color.rgb = RGBColor(*color)
        return tx_box, tf

    # Helper function to create a stylized card
    def add_card(slide, left, top, width, height, bg_color=BG_CARD_NAVY, border_color=None, border_width=1):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = RGBColor(*bg_color)
        if border_color:
            card.line.color.rgb = RGBColor(*border_color)
            card.line.width = Pt(border_width)
        else:
            card.line.fill.background()
        return card

    # Helper function to build a standard slide header
    def add_slide_header(slide, title, category="STOCK MARKET RAG SYSTEM"):
        # Category label (tiny, uppercase teal)
        add_textbox(
            slide, Inches(0.75), Inches(0.4), Inches(11.83), Inches(0.3),
            category.upper(), font_size=10, bold=True, color=ACCENT_TEAL, font_name="Trebuchet MS"
        )
        # Title
        add_textbox(
            slide, Inches(0.75), Inches(0.7), Inches(11.83), Inches(0.7),
            title, font_size=28, bold=True, color=TEXT_WHITE, font_name="Trebuchet MS"
        )
        # Horizontal rule
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.75), Inches(1.4), Inches(11.83), Inches(0.02))
        line.fill.solid()
        line.fill.fore_color.rgb = RGBColor(*BORDER_SLATE)
        line.line.fill.background()

    # =========================================================================
    # SLIDE 1: Title Slide (The Gateway)
    # =========================================================================
    slide1 = prs.slides.add_slide(blank_layout)
    apply_background(slide1, BG_DEEP_NAVY)

    # Decorative abstract layout shapes (background accent)
    bg_shape = slide1.shapes.add_shape(MSO_SHAPE.ISOSCELES_TRIANGLE, Inches(9.5), Inches(0.5), Inches(3.5), Inches(6.5))
    bg_shape.rotation = 90
    bg_shape.fill.solid()
    bg_shape.fill.fore_color.rgb = RGBColor(*BG_CARD_NAVY)
    bg_shape.line.fill.background()

    # Centered Title Card
    add_textbox(
        slide1, Inches(0.75), Inches(2.2), Inches(10.0), Inches(1.8),
        "SMART STOCK MARKET ANALYSIS\n& RISK EVALUATION SYSTEM",
        font_size=40, bold=True, color=TEXT_WHITE, font_name="Trebuchet MS"
    )
    
    # Subtitle
    add_textbox(
        slide1, Inches(0.75), Inches(4.1), Inches(10.0), Inches(0.6),
        "An AI-Powered Semantic RAG Pipeline & Machine Learning Prediction Platform",
        font_size=18, bold=False, color=ACCENT_TEAL, font_name="Calibri"
    )
    
    # Line
    accent_bar = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.75), Inches(4.9), Inches(5.0), Inches(0.05))
    accent_bar.fill.solid()
    accent_bar.fill.fore_color.rgb = RGBColor(*ACCENT_TEAL)
    accent_bar.line.fill.background()

    # Team & Academic project notes
    team_text = "DEVELOPED BY: SE25MAID035 | SE25MAID014 | SE25MAID016 | SE25MAID021\nDEPARTMENT OF DATA SCIENCE & AI"
    add_textbox(
        slide1, Inches(0.75), Inches(5.3), Inches(8.0), Inches(0.8),
        team_text, font_size=11, bold=True, color=TEXT_MUTED, font_name="Calibri"
    )

    # =========================================================================
    # SLIDE 2: Problem Statement (The Core Need)
    # =========================================================================
    slide2 = prs.slides.add_slide(blank_layout)
    apply_background(slide2, BG_DEEP_NAVY)
    add_slide_header(slide2, "The Core Problem: Standard vs. Semantic Screening")

    # Left Card: Traditional Screeners (Red tint)
    add_card(slide2, Inches(0.75), Inches(1.8), Inches(5.6), Inches(4.8), bg_color=CARD_RED, border_color=BORDER_SLATE)
    add_textbox(
        slide2, Inches(1.1), Inches(2.1), Inches(4.9), Inches(0.5),
        "TRADITIONAL STOCK SCREENERS", font_size=18, bold=True, color=ACCENT_AMBER, font_name="Trebuchet MS"
    )
    add_textbox(
        slide2, Inches(1.1), Inches(2.8), Inches(4.9), Inches(3.2),
        "• Rigid filters (only PE < 15, Close Price, Sector).\n"
        "• No semantic understanding: Searching for 'safe dividend banking stock with long-term growth' fails to execute.\n"
        "• Pure keyword matching ignores context, intent, and company sentiment.\n"
        "• Demands excessive technical stock-market jargon from retail investors.",
        font_size=14, color=TEXT_WHITE
    )

    # Right Card: Semantic RAG System (Green tint)
    add_card(slide2, Inches(6.98), Inches(1.8), Inches(5.6), Inches(4.8), bg_color=CARD_GREEN, border_color=ACCENT_TEAL)
    add_textbox(
        slide2, Inches(7.33), Inches(2.1), Inches(4.9), Inches(0.5),
        "OUR RETRIEVAL-AUGMENTED PIPELINE", font_size=18, bold=True, color=ACCENT_TEAL, font_name="Trebuchet MS"
    )
    add_textbox(
        slide2, Inches(7.33), Inches(2.8), Inches(4.9), Inches(3.2),
        "• Intent Recognition: Automatically maps natural query parameters to numeric features & labels.\n"
        "• Context-Aware Embeddings: Employs FinBERT and sentence transformers to evaluate company descriptions.\n"
        "• Grounded Insights: Enriches retrieval with risk scores, sentiment weights, and performance forecasts.\n"
        "• Conversational Access: Empowers any investor to chat directly with market data.",
        font_size=14, color=TEXT_WHITE
    )

    # =========================================================================
    # SLIDE 3: System Architecture
    # =========================================================================
    slide3 = prs.slides.add_slide(blank_layout)
    apply_background(slide3, BG_DEEP_NAVY)
    add_slide_header(slide3, "System Architecture: End-to-End Execution")

    steps = [
        ("1. USER INPUT", "Natural language investment query is sent to system."),
        ("2. ENCODER", "Query converted to vector space using FinBERT embeddings."),
        ("3. CO-SIM INDEX", "Cosine similarity search against vector index (`pkl` DB)."),
        ("4. RAG RETRIEVAL", "Top-K stocks matched with metadata, risk levels, and news."),
        ("5. DASHBOARD", "Visual recommendations and ML price forecasts rendered.")
    ]

    card_w = Inches(2.12)
    card_h = Inches(4.0)
    gap = Inches(0.3)
    start_x = Inches(0.75)
    top_y = Inches(2.2)

    for idx, (title, desc) in enumerate(steps):
        x = start_x + idx * (card_w + gap)
        # Background card
        add_card(slide3, x, top_y, card_w, card_h, bg_color=BG_CARD_NAVY, border_color=ACCENT_TEAL if idx == 3 else BORDER_SLATE)
        
        # Step Number bubble
        num_box = slide3.shapes.add_shape(MSO_SHAPE.OVAL, x + Inches(0.2), top_y + Inches(0.2), Inches(0.4), Inches(0.4))
        num_box.fill.solid()
        num_box.fill.fore_color.rgb = RGBColor(*(ACCENT_TEAL if idx == 3 else BORDER_SLATE))
        num_box.line.fill.background()
        
        # Write number inside bubble
        p = num_box.text_frame.paragraphs[0]
        p.text = str(idx + 1)
        p.alignment = PP_ALIGN.CENTER
        p.font.name = "Trebuchet MS"
        p.font.bold = True
        p.font.size = Pt(12)
        p.font.color.rgb = RGBColor(*TEXT_WHITE)

        # Title
        add_textbox(
            slide3, x + Inches(0.2), top_y + Inches(0.9), card_w - Inches(0.4), Inches(0.6),
            title, font_size=12, bold=True, color=ACCENT_TEAL if idx == 3 else TEXT_WHITE, font_name="Trebuchet MS"
        )
        # Description
        add_textbox(
            slide3, x + Inches(0.2), top_y + Inches(1.6), card_w - Inches(0.4), Inches(2.0),
            desc, font_size=11, color=TEXT_MUTED
        )
        
        # Connection chevron arrows (except last card)
        if idx < len(steps) - 1:
            arrow = slide3.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, x + card_w + Inches(0.05), top_y + Inches(1.8), Inches(0.2), Inches(0.25))
            arrow.fill.solid()
            arrow.fill.fore_color.rgb = RGBColor(*BORDER_SLATE)
            arrow.line.fill.background()

    # =========================================================================
    # SLIDE 4: The Financial RAG Pipeline
    # =========================================================================
    slide4 = prs.slides.add_slide(blank_layout)
    apply_background(slide4, BG_DEEP_NAVY)
    add_slide_header(slide4, "Financial RAG: Semantic Stock Mapping")

    # Terminal header
    term_x = Inches(0.75)
    term_y = Inches(1.8)
    term_w = Inches(11.83)
    term_h = Inches(4.8)

    # Main Card
    add_card(slide4, term_x, term_y, term_w, term_h, bg_color=BG_CARD_NAVY, border_color=ACCENT_TEAL, border_width=1.5)
    
    # Terminal mock controls (3 colored circles)
    colors = [(255, 95, 87), (254, 188, 46), (40, 200, 64)] # red, yellow, green
    for idx, col in enumerate(colors):
        dot = slide4.shapes.add_shape(MSO_SHAPE.OVAL, term_x + Inches(0.25) + idx*Inches(0.3), term_y + Inches(0.2), Inches(0.18), Inches(0.18))
        dot.fill.solid()
        dot.fill.fore_color.rgb = RGBColor(*col)
        dot.line.fill.background()

    # Terminal code display
    content_box = slide4.shapes.add_textbox(term_x + Inches(0.4), term_y + Inches(0.6), term_w - Inches(0.8), term_h - Inches(0.8))
    tf = content_box.text_frame
    tf.word_wrap = True

    def add_terminal_line(tf, prefix, text, color, pref_color=ACCENT_TEAL, bold=False):
        p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
        p.text = ""
        r1 = p.add_run()
        r1.text = prefix
        r1.font.name = "Consolas"
        r1.font.bold = True
        r1.font.size = Pt(13)
        r1.font.color.rgb = RGBColor(*pref_color)

        r2 = p.add_run()
        r2.text = text
        r2.font.name = "Consolas"
        r2.font.bold = bold
        r2.font.size = Pt(13)
        r2.font.color.rgb = RGBColor(*color)

    add_terminal_line(tf, "investor@stockrag:~$ ", "python stock_retrieval.py --mode query --query \"safe long-term tech stocks\"", TEXT_WHITE, pref_color=(148, 163, 184))
    add_terminal_line(tf, "[INFO] ", "Initializing SentenceTransformer/FinBERT model encoder...", TEXT_MUTED)
    add_terminal_line(tf, "[INFO] ", "Computing similarity index lookup in data/stock_index.pkl...", TEXT_MUTED)
    add_terminal_line(tf, "[SUCCESS] ", "Retrieved Top-1 relevant match with cosine score 0.9123:", ACCENT_TEAL)
    add_terminal_line(tf, "\n", "", TEXT_WHITE)
    add_terminal_line(tf, "Rank 1: ", "INFOSYS (TICKER: INFY) | Similarity Score: 0.9123", TEXT_WHITE, bold=True)
    add_terminal_line(tf, "   ├─ Sector:      ", "Technology", ACCENT_TEAL)
    add_terminal_line(tf, "   ├─ Risk Level:  ", "Low Risk", ACCENT_TEAL)
    add_terminal_line(tf, "   ├─ Current Close: ", "₹1540.20", ACCENT_TEAL)
    add_terminal_line(tf, "   └─ Context:     ", "Technology company with positive returns, stable growth, and moderate PE ratio.", ACCENT_AMBER)
    add_terminal_line(tf, "\n", "", TEXT_WHITE)
    add_terminal_line(tf, "investor@stockrag:~$ ", "█", TEXT_WHITE, pref_color=(148, 163, 184))

    # =========================================================================
    # SLIDE 5: Predictive Modeling (Baseline vs. Advanced)
    # =========================================================================
    slide5 = prs.slides.add_slide(blank_layout)
    apply_background(slide5, BG_DEEP_NAVY)
    add_slide_header(slide5, "Predictive Modeling: Baseline vs. Advanced ML")

    # Add summary text above table
    add_textbox(
        slide5, Inches(0.75), Inches(1.6), Inches(11.83), Inches(0.6),
        "Evaluating predictions of future stock closes. Baseline (Linear Regression) significantly outperformed the Advanced (XGBoost/Neural Network) configurations due to the linear features of the dataset.",
        font_size=13, color=TEXT_MUTED
    )

    # Insert Table
    rows = 6
    cols = 4
    left = Inches(0.75)
    top = Inches(2.3)
    width = Inches(11.83)
    height = Inches(3.8)

    table_shape = slide5.shapes.add_table(rows, cols, left, top, width, height)
    table = table_shape.table

    # Format column widths
    table.columns[0].width = Inches(3.0)
    table.columns[1].width = Inches(2.94)
    table.columns[2].width = Inches(2.94)
    table.columns[3].width = Inches(2.95)

    headers = ["Evaluation Metric", "Baseline (Linear Regression)", "Advanced (XGBoost/NN)", "Performance Winner"]
    data = [
        ["Mean Absolute Error (MAE)", "1.5318", "136.3857", "Baseline (+98.8%)"],
        ["Mean Squared Error (MSE)", "3.7425", "22,804.59", "Baseline (+99.9%)"],
        ["Root Mean Squared Error (RMSE)", "1.9345", "151.0119", "Baseline (+98.7%)"],
        ["R-Squared Score (R²)", "0.9991", "-4.4594", "Baseline (+122.4%)"],
        ["Mean Absolute Percentage Error (MAPE)", "0.13%", "11.46%", "Baseline (+98.8%)"]
    ]

    # Write Headers
    for col_idx, text in enumerate(headers):
        cell = table.cell(0, col_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(*BG_CARD_NAVY)
        cell.text = text
        p = cell.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        p.font.name = "Trebuchet MS"
        p.font.bold = True
        p.font.size = Pt(13)
        p.font.color.rgb = RGBColor(*ACCENT_TEAL)

    # Write Data
    for row_idx, row_data in enumerate(data, start=1):
        for col_idx, val in enumerate(row_data):
            cell = table.cell(row_idx, col_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(*(18, 30, 49) if row_idx % 2 == 0 else (23, 42, 69))
            cell.text = val
            p = cell.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER if col_idx > 0 else PP_ALIGN.LEFT
            p.font.name = "Calibri"
            p.font.size = Pt(12)
            
            # Color Winner text teal
            if col_idx == 3:
                p.font.bold = True
                p.font.color.rgb = RGBColor(*ACCENT_TEAL)
            else:
                p.font.color.rgb = RGBColor(*TEXT_WHITE)

    # Bottom notes
    add_textbox(
        slide5, Inches(0.75), Inches(6.25), Inches(11.83), Inches(0.4),
        "💡 Insight: The Baseline model captures linear trends perfectly. XGBoost overfitted background fluctuations, yielding negative R².",
        font_size=11, bold=True, color=ACCENT_AMBER
    )

    # =========================================================================
    # SLIDE 6: Risk Analysis & Portfolio Optimization
    # =========================================================================
    slide6 = prs.slides.add_slide(blank_layout)
    apply_background(slide6, BG_DEEP_NAVY)
    add_slide_header(slide6, "Risk Analysis & Portfolio Optimization")

    strategies = [
        {
            "title": "CONSERVATIVE PROFILE",
            "border": BORDER_SLATE,
            "expected_return": "25.66%",
            "volatility": "7.59%",
            "sharpe": "2.8543",
            "weights": "80% Stock | 20% Cash",
            "advice": "Designed for stable growth. Mitigates downside risk with a cash buffer."
        },
        {
            "title": "MODERATE PROFILE",
            "border": ACCENT_TEAL,
            "expected_return": "28.86%",
            "volatility": "8.53%",
            "sharpe": "3.0128",
            "weights": "90% Stock | 10% Cash",
            "advice": "Balanced asset allocation. Captures standard market trends with controlled risk."
        },
        {
            "title": "AGGRESSIVE PROFILE",
            "border": ACCENT_AMBER,
            "expected_return": "32.07%",
            "volatility": "9.48%",
            "sharpe": "3.1714",
            "weights": "100% Stock Allocation",
            "advice": "Full allocation strategy. High single-stock concentration. Best potential returns."
        }
    ]

    card_w = Inches(3.6)
    card_h = Inches(4.5)
    gap = Inches(0.5)
    start_x = Inches(0.75)
    top_y = Inches(1.9)

    for idx, strat in enumerate(strategies):
        x = start_x + idx * (card_w + gap)
        add_card(slide6, x, top_y, card_w, card_h, bg_color=BG_CARD_NAVY, border_color=strat["border"], border_width=1.5)
        
        # Header inside card
        add_textbox(
            slide6, x + Inches(0.25), top_y + Inches(0.3), card_w - Inches(0.5), Inches(0.5),
            strat["title"], font_size=15, bold=True, color=strat["border"], font_name="Trebuchet MS", align=PP_ALIGN.CENTER
        )
        
        # Stat grid
        stat_y = top_y + Inches(1.0)
        metrics = [
            ("Expected Return", strat["expected_return"]),
            ("Volatility Score", strat["volatility"]),
            ("Sharpe Ratio", strat["sharpe"]),
            ("Asset Weights", strat["weights"])
        ]
        
        for midx, (label, val) in enumerate(metrics):
            y_offset = stat_y + midx * Inches(0.65)
            # Label
            add_textbox(
                slide6, x + Inches(0.25), y_offset, card_w - Inches(0.5), Inches(0.25),
                label, font_size=10, color=TEXT_MUTED
            ),
            # Value
            add_textbox(
                slide6, x + Inches(0.25), y_offset + Inches(0.22), card_w - Inches(0.5), Inches(0.35),
                val, font_size=14, bold=True, color=TEXT_WHITE
            )

        # Bottom Advice line
        divider = slide6.shapes.add_shape(MSO_SHAPE.RECTANGLE, x + Inches(0.25), top_y + Inches(3.5), card_w - Inches(0.5), Inches(0.01))
        divider.fill.solid()
        divider.fill.fore_color.rgb = RGBColor(*BORDER_SLATE)
        divider.line.fill.background()

        add_textbox(
            slide6, x + Inches(0.25), top_y + Inches(3.6), card_w - Inches(0.5), Inches(0.8),
            strat["advice"], font_size=11, color=TEXT_MUTED
        )

    # =========================================================================
    # SLIDE 7: Live RAG Dashboard Interface
    # =========================================================================
    slide7 = prs.slides.add_slide(blank_layout)
    apply_background(slide7, BG_DEEP_NAVY)
    add_slide_header(slide7, "Interactive StockRAG Dashboard")

    # Left: Wireframe mock of the dashboard UI
    mock_x = Inches(0.75)
    mock_y = Inches(1.8)
    mock_w = Inches(6.5)
    mock_h = Inches(4.5)

    add_card(slide7, mock_x, mock_y, mock_w, mock_h, bg_color=(15, 23, 42), border_color=BORDER_SLATE)
    
    # Dashboard Header Bar
    bar = slide7.shapes.add_shape(MSO_SHAPE.RECTANGLE, mock_x, mock_y, mock_w, Inches(0.5))
    bar.fill.solid()
    bar.fill.fore_color.rgb = RGBColor(*BG_CARD_NAVY)
    bar.line.fill.background()
    add_textbox(slide7, mock_x + Inches(0.2), mock_y + Inches(0.12), mock_w, Inches(0.3), "📊 StockRAG Live Investor Portal", font_size=11, bold=True, color=ACCENT_TEAL, font_name="Trebuchet MS")

    # Search panel mock
    add_card(slide7, mock_x + Inches(0.3), mock_y + Inches(0.7), mock_w - Inches(0.6), Inches(0.7), bg_color=BG_CARD_NAVY)
    add_textbox(slide7, mock_x + Inches(0.5), mock_y + Inches(0.8), mock_w - Inches(1.0), Inches(0.5), "🔍 Search stocks semantically (e.g. high-yield energy shares)...", font_size=10, color=TEXT_MUTED)

    # Two columns in mockup: charts & stats
    add_card(slide7, mock_x + Inches(0.3), mock_y + Inches(1.6), mock_w * 0.55, Inches(2.6), bg_color=BG_CARD_NAVY) # chart
    # draw a mini mockup chart path (zigzag lines)
    for i in range(4):
        segment = slide7.shapes.add_shape(MSO_SHAPE.RECTANGLE, mock_x + Inches(0.6) + idx*Inches(0.6), mock_y + Inches(3.2) - (i%2)*Inches(0.4), Inches(0.4), Inches(0.1))
        segment.fill.solid()
        segment.fill.fore_color.rgb = RGBColor(*ACCENT_TEAL)
        segment.line.fill.background()
    add_textbox(slide7, mock_x + Inches(0.5), mock_y + Inches(1.8), Inches(3.0), Inches(0.3), "Historical Trend & Prediction", font_size=9, bold=True, color=TEXT_WHITE)

    add_card(slide7, mock_x + Inches(4.1), mock_y + Inches(1.6), Inches(2.1), Inches(2.6), bg_color=BG_CARD_NAVY) # side stats
    add_textbox(slide7, mock_x + Inches(4.25), mock_y + Inches(1.8), Inches(1.8), Inches(2.0), 
                "RELIANCE\nClose: ₹2450\nRisk: Low\n\nTCS\nClose: ₹3400\nRisk: Low\n\nINFY\nClose: ₹1540\nRisk: Low", font_size=9, color=TEXT_WHITE)

    # Right Column: Narrative describing features
    right_x = Inches(7.6)
    right_y = Inches(1.8)
    right_w = Inches(4.98)

    add_textbox(
        slide7, right_x, right_y, right_w, Inches(0.5),
        "DASHBOARD ARCHITECTURE", font_size=18, bold=True, color=ACCENT_TEAL, font_name="Trebuchet MS"
    )
    
    features = [
        ("Twelve Data Live Proxy", "Queries stock prices dynamically through local server proxy (`server.py`) to bypass CORS and hide API credentials."),
        ("Natural Language Interface", "Users enter complex investment questions and receive instant contextual RAG answers parsed by our semantic engine."),
        ("Responsive Layout", "Built with lightweight HTML/CSS structure to load under 300ms. No bulky frameworks required.")
    ]

    feat_y = right_y + Inches(0.8)
    for idx, (title, fdesc) in enumerate(features):
        y_offset = feat_y + idx * Inches(1.2)
        # Bullet/dot
        dot = slide7.shapes.add_shape(MSO_SHAPE.OVAL, right_x, y_offset + Inches(0.05), Inches(0.12), Inches(0.12))
        dot.fill.solid()
        dot.fill.fore_color.rgb = RGBColor(*ACCENT_TEAL)
        dot.line.fill.background()
        
        add_textbox(slide7, right_x + Inches(0.25), y_offset, right_w - Inches(0.3), Inches(0.3), title, font_size=13, bold=True, color=TEXT_WHITE)
        add_textbox(slide7, right_x + Inches(0.25), y_offset + Inches(0.28), right_w - Inches(0.3), Inches(0.8), fdesc, font_size=11, color=TEXT_MUTED)

    # =========================================================================
    # SLIDE 8: Ablation Study & Core Metrics
    # =========================================================================
    slide8 = prs.slides.add_slide(blank_layout)
    apply_background(slide8, BG_DEEP_NAVY)
    add_slide_header(slide8, "Ablation Study & Evaluation Metrics")

    # Grid of two big stats cards
    card_w = Inches(5.6)
    card_h = Inches(4.5)
    
    # Left Card: Semantic Retrieval
    add_card(slide8, Inches(0.75), Inches(1.8), card_w, card_h, bg_color=BG_CARD_NAVY, border_color=ACCENT_TEAL, border_width=1.5)
    add_textbox(slide8, Inches(1.1), Inches(2.2), card_w - Inches(0.7), Inches(1.2), "0.90+", font_size=60, bold=True, color=ACCENT_TEAL, font_name="Trebuchet MS", align=PP_ALIGN.CENTER)
    add_textbox(slide8, Inches(1.1), Inches(3.6), card_w - Inches(0.7), Inches(0.4), "RETRIEVAL RELEVANCE@5", font_size=14, bold=True, color=TEXT_WHITE, font_name="Trebuchet MS", align=PP_ALIGN.CENTER)
    
    divider1 = slide8.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.5), Inches(4.1), card_w - Inches(1.5), Inches(0.01))
    divider1.fill.solid()
    divider1.fill.fore_color.rgb = RGBColor(*BORDER_SLATE)
    divider1.line.fill.background()
    
    add_textbox(slide8, Inches(1.1), Inches(4.3), card_w - Inches(0.7), Inches(1.5), 
                "• Measures relevance of retrieved stocks against semantic query context.\n"
                "• Increased from 0.70+ in Milestone 1 to 0.90+ using advanced embedding matching.\n"
                "• Sentence-Transformers accurately capture sector & risk intent.", font_size=12, color=TEXT_MUTED)

    # Right Card: Risk Classification
    add_card(slide8, Inches(6.98), Inches(1.8), card_w, card_h, bg_color=BG_CARD_NAVY, border_color=ACCENT_AMBER, border_width=1.5)
    add_textbox(slide8, Inches(7.33), Inches(2.2), card_w - Inches(0.7), Inches(1.2), "0.90+", font_size=60, bold=True, color=ACCENT_AMBER, font_name="Trebuchet MS", align=PP_ALIGN.CENTER)
    add_textbox(slide8, Inches(7.33), Inches(3.6), card_w - Inches(0.7), Inches(0.4), "RISK CLASSIFICATION ACCURACY", font_size=14, bold=True, color=TEXT_WHITE, font_name="Trebuchet MS", align=PP_ALIGN.CENTER)
    
    divider2 = slide8.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(7.73), Inches(4.1), card_w - Inches(1.5), Inches(0.01))
    divider2.fill.solid()
    divider2.fill.fore_color.rgb = RGBColor(*BORDER_SLATE)
    divider2.line.fill.background()
    
    add_textbox(slide8, Inches(7.33), Inches(4.3), card_w - Inches(0.7), Inches(1.5), 
                "• Measures correct categorization of stocks into Low, Moderate, and High Risk.\n"
                "• Evaluates asset volatility metrics over the full historic training distribution.\n"
                "• Crucial step for downstream asset weights allocation inside portfolios.", font_size=12, color=TEXT_MUTED)

    # =========================================================================
    # SLIDE 9: Future Scope & Roadmap
    # =========================================================================
    slide9 = prs.slides.add_slide(blank_layout)
    apply_background(slide9, BG_DEEP_NAVY)
    add_slide_header(slide9, "Future Scope & Project Roadmap")

    # Roadmap horizontal timeline
    roadmaps = [
        ("PHASE 1: NEWS INTEGRATION", "Incorporate live scraped news articles. Perform sentiment analysis on headlines via FinBERT to dynamically adjust stock risk parameters based on market events."),
        ("PHASE 2: LLM GENERATION", "Connect retrieval contexts to local Large Language Models (LLMs) like Llama-3 or Gemini. Generate personalized paragraphs explaining recommendations to investors."),
        ("PHASE 3: ONE-CLICK TRADE", "Establish brokerage integrations via REST APIs to translate portfolio allocation suggestions directly into executable market trades with automated rebalancing.")
    ]

    width_box = Inches(3.6)
    height_box = Inches(4.0)
    start_x = Inches(0.75)
    top_y = Inches(2.2)
    gap = Inches(0.5)

    for idx, (p_title, p_desc) in enumerate(roadmaps):
        x = start_x + idx * (width_box + gap)
        add_card(slide9, x, top_y, width_box, height_box, bg_color=BG_CARD_NAVY, border_color=BORDER_SLATE)
        
        # Horizontal highlight line on card top
        top_bar = slide9.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, top_y, width_box, Inches(0.12))
        top_bar.fill.solid()
        top_bar.fill.fore_color.rgb = RGBColor(*ACCENT_TEAL)
        top_bar.line.fill.background()

        # Step Node
        node = slide9.shapes.add_shape(MSO_SHAPE.OVAL, x + Inches(0.3), top_y + Inches(0.4), Inches(0.5), Inches(0.5))
        node.fill.solid()
        node.fill.fore_color.rgb = RGBColor(*ACCENT_TEAL)
        node.line.fill.background()
        p = node.text_frame.paragraphs[0]
        p.text = f"P{idx+1}"
        p.alignment = PP_ALIGN.CENTER
        p.font.name = "Trebuchet MS"
        p.font.bold = True
        p.font.size = Pt(11)
        p.font.color.rgb = RGBColor(*BG_DEEP_NAVY)

        add_textbox(slide9, x + Inches(0.3), top_y + Inches(1.1), width_box - Inches(0.6), Inches(0.8), p_title, font_size=13, bold=True, color=TEXT_WHITE, font_name="Trebuchet MS")
        add_textbox(slide9, x + Inches(0.3), top_y + Inches(1.8), width_box - Inches(0.6), Inches(2.0), p_desc, font_size=11, color=TEXT_MUTED)

    # =========================================================================
    # SLIDE 10: Conclusion & Thank You
    # =========================================================================
    slide10 = prs.slides.add_slide(blank_layout)
    apply_background(slide10, BG_DEEP_NAVY)

    # Background design element
    bg_circle = slide10.shapes.add_shape(MSO_SHAPE.OVAL, Inches(4.5), Inches(-1.5), Inches(10.0), Inches(10.0))
    bg_circle.fill.solid()
    bg_circle.fill.fore_color.rgb = RGBColor(*BG_CARD_NAVY)
    bg_circle.line.fill.background()

    # Large Center Card
    main_w = Inches(8.5)
    main_h = Inches(4.5)
    main_x = Inches(2.4)
    main_y = Inches(1.5)

    add_card(slide10, main_x, main_y, main_w, main_h, bg_color=BG_DEEP_NAVY, border_color=ACCENT_TEAL, border_width=2.5)

    add_textbox(
        slide10, main_x + Inches(0.5), main_y + Inches(0.5), main_w - Inches(1.0), Inches(0.5),
        "PROJECT CONCLUSION", font_size=14, bold=True, color=ACCENT_TEAL, font_name="Trebuchet MS", align=PP_ALIGN.CENTER
    )
    
    add_textbox(
        slide10, main_x + Inches(0.5), main_y + Inches(1.1), main_w - Inches(1.0), Inches(1.2),
        "By replacing rigid keywords with a semantic RAG pipeline, the system unlocks natural-language investment screens. Combined with robust baseline predictors and Modern Portfolio Theory allocation models, StockRAG delivers high-integrity, risk-aware investment recommendations.",
        font_size=13, color=TEXT_WHITE, align=PP_ALIGN.CENTER
    )

    # Metrics row
    metrics_y = main_y + Inches(2.6)
    add_textbox(slide10, main_x + Inches(1.0), metrics_y, Inches(2.0), Inches(0.8), "5,000\nData Points", font_size=16, bold=True, color=ACCENT_TEAL, font_name="Trebuchet MS", align=PP_ALIGN.CENTER)
    add_textbox(slide10, main_x + Inches(3.25), metrics_y, Inches(2.0), Inches(0.8), "12\nIndexed Sectors", font_size=16, bold=True, color=ACCENT_TEAL, font_name="Trebuchet MS", align=PP_ALIGN.CENTER)
    add_textbox(slide10, main_x + Inches(5.5), metrics_y, Inches(2.0), Inches(0.8), "90%+\nRet. Relevance", font_size=16, bold=True, color=ACCENT_TEAL, font_name="Trebuchet MS", align=PP_ALIGN.CENTER)

    # Thank you
    add_textbox(
        slide10, main_x + Inches(0.5), main_y + Inches(3.7), main_w - Inches(1.0), Inches(0.5),
        "Thank You! Questions?", font_size=20, bold=True, color=TEXT_WHITE, font_name="Trebuchet MS", align=PP_ALIGN.CENTER
    )

    # Output generation
    output_dir = os.path.dirname(os.path.realpath(__file__))
    output_path = os.path.join(os.path.dirname(output_dir), "Stock_Market_RAG_Presentation.pptx")
    prs.save(output_path)
    print(f"[SUCCESS] Widescreen PowerPoint Presentation generated successfully:\n   File: {output_path}")

if __name__ == "__main__":
    main()
