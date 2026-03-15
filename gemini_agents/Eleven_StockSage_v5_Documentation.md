# 📊 StockSage v5 — Complete Documentation

> **AI-Powered Stock Research & Trade Setup Agent**
> Indian Markets (NSE/BSE) · US Markets (NYSE/NASDAQ) · Global Macro

---

## Table of Contents

1. [Overview](#1-overview)
2. [Architecture](#2-architecture)
3. [Installation & Setup](#3-installation--setup)
4. [Configuration](#4-configuration)
5. [Data Sources](#5-data-sources)
6. [Core Data Structures](#6-core-data-structures)
7. [Helper Functions](#7-helper-functions)
8. [Tool Reference — All 21 Tools](#8-tool-reference--all-21-tools)
   - [Market Data Tools](#81-market-data-tools)
   - [Analysis & Report Tools](#82-analysis--report-tools)
   - [Trade Setup Tools](#83-trade-setup-tools)
   - [Global Macro Tools](#84-global-macro-tools)
   - [Index & Sector Tools](#85-index--sector-tools)
   - [News & Research Tools](#86-news--research-tools)
9. [The ReAct Agent](#9-the-react-agent)
10. [System Prompt Design](#10-system-prompt-design)
11. [Interactive Shell](#11-interactive-shell)
12. [Quick Shortcuts Reference](#12-quick-shortcuts-reference)
13. [Example Queries & Expected Output](#13-example-queries--expected-output)
14. [Technical Indicators Explained](#14-technical-indicators-explained)
15. [Trade Setup Framework](#15-trade-setup-framework)
16. [Global Macro Framework](#16-global-macro-framework)
17. [Extending & Customising](#17-extending--customising)
18. [Troubleshooting](#18-troubleshooting)
19. [Limitations & Disclaimer](#19-limitations--disclaimer)

---

## 1. Overview

StockSage v5 is a **fully autonomous AI research agent** built on Google Gemini's LLM using the **LangChain ReAct (Reasoning + Acting)** pattern. It combines live market data, options chain analysis, technical indicators, fundamental analysis, analyst consensus, and global macro factors into a single conversational interface.

### What Makes It Different

| Feature | StockSage v5 |
|---|---|
| Indian market coverage | NSE + BSE + 50+ Nifty indices |
| US market coverage | NYSE + NASDAQ + pre-market futures |
| Global macro | Crude Oil, Gold, Silver, DXY, USD/INR, US Yields |
| Trade setups | Intraday (pivot-based) + Swing (Fibonacci-based) |
| Options analysis | Live PCR, Max Pain, OI-based S/R |
| Analyst data | Buy/Sell/Hold consensus + price targets |
| LLM reasoning | Gemini ReAct agent chains tools autonomously |
| Pre-open signal | Gap-up/gap-down indicator from US futures |

### Version History

| Version | Key Additions |
|---|---|
| v1 | Basic yfinance quotes + Gemini |
| v2 | Indian market support (NSE/BSE), DuckDuckGo news |
| v3 | 50+ Nifty indices, sectoral momentum, RSS news |
| v4 | Analyst consensus, PCR/options, detailed reports, trade setups |
| **v5** | **Crude oil, gold, DXY, US futures, macro impact analysis** |

---

## 2. Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER (CLI / Terminal)                        │
└──────────────────────────────┬──────────────────────────────────┘
                               │ natural language query
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    INTERACTIVE SHELL (main)                      │
│  • Quick shortcut parser (bypasses LLM for speed)               │
│  • History, help, clear commands                                 │
└──────────────────────────────┬──────────────────────────────────┘
                               │ complex queries
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│              LANGCHAIN ReAct AGENT (Gemini LLM)                 │
│                                                                  │
│  Thought → Action → Observation → Thought → ... → Final Answer │
│                                                                  │
│  System Prompt: market knowledge + tool routing + analysis rules│
└──────────────────────────────┬──────────────────────────────────┘
                               │ selects & calls tools
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                      TOOL LAYER (21 tools)                       │
├───────────────┬──────────────┬───────────────┬──────────────────┤
│  Market Data  │  Analysis    │  Trade Setup  │  Macro / News    │
│  ─────────── │  ─────────── │  ──────────── │  ─────────────── │
│  get_quote    │  fundamental │  intraday     │  macro_dashboard  │
│  nifty_index  │  technical   │  swing        │  us_futures       │
│  pcr_options  │  analyst     │               │  macro_impact     │
│  price_hist   │  compare     │               │  news / RSS       │
└───────────────┴──────┬───────┴───────────────┴──────────────────┘
                       │ data requests
          ┌────────────┼───────────────┐
          ▼            ▼               ▼
    ┌──────────┐  ┌──────────┐  ┌──────────────┐
    │ yfinance │  │DuckDuckGo│  │  RSS Feeds   │
    │ (OHLCV,  │  │ Web Search│  │ (ET Markets, │
    │  options,│  │          │  │  Moneycontrol)│
    │  info)   │  │          │  │              │
    └──────────┘  └──────────┘  └──────────────┘
```

### ReAct Loop Explained

The LangChain **ReAct** pattern lets the LLM reason step-by-step before acting:

```
Thought:  "The user wants to analyse RELIANCE. I should first get 
           the live quote, then fundamentals, then technicals..."
Action:   get_stock_quote("RELIANCE")
Observation: "📊 QUOTE — RELIANCE.NS [NSE] Price: ₹2,847..."
Thought:  "Now I have the price. Let me get fundamentals..."
Action:   get_detailed_fundamental_report("RELIANCE")
Observation: "...P/E: 24.5, ROE: 18.2%..."
...continues until enough data is gathered...
Final Answer: [complete structured analysis]
```

---

## 3. Installation & Setup

### Prerequisites

- Python 3.9 or higher
- A Google Gemini API key (free tier available)
- Internet connection for live data

### Step 1 — Clone / Download

```bash
# Save stocksage_v5.py to your project directory
mkdir stocksage && cd stocksage
# Place stocksage_v5.py here
```

### Step 2 — Create Virtual Environment (Recommended)

```bash
python -m venv venv

# Activate:
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

Create `requirements.txt` with:

```text
yfinance>=0.2.40
langchain>=0.2.0
langchain-google-genai>=1.0.0
langchainhub>=0.1.15
duckduckgo-search>=6.0.0
python-dotenv>=1.0.0
pandas>=2.0.0
numpy>=1.24.0
```

Or install directly:

```bash
pip install yfinance langchain langchain-google-genai langchainhub \
            duckduckgo-search python-dotenv pandas numpy
```

### Step 4 — Get Gemini API Key

1. Go to [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2. Click **Create API key**
3. Copy the key

### Step 5 — Create `.env` File

In the same directory as `stocksage_v5.py`, create a `.env` file:

```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-flash
```

> **Model options:**
> - `gemini-1.5-flash` — Fast, good for most queries (default, free tier)
> - `gemini-1.5-pro` — Slower but more thorough analysis
> - `gemini-2.0-flash` — Latest and fastest

### Step 6 — Run

```bash
python stocksage_v5.py
```

You should see the banner and the `🔍 StockSage v5>` prompt.

---

## 4. Configuration

All configuration is via environment variables in `.env`:

| Variable | Default | Description |
|---|---|---|
| `GEMINI_API_KEY` | *(required)* | Your Google Gemini API key |
| `GEMINI_MODEL` | `gemini-1.5-flash` | Gemini model to use |

### Agent Tuning (in code)

These are set directly in the code and can be adjusted:

```python
# LLM temperature — lower = more precise/deterministic
llm = ChatGoogleGenerativeAI(model=model, temperature=0.15, ...)

# Max tool calls per query (increase for complex multi-step analysis)
max_iterations=15

# Max time per query in seconds
max_execution_time=150
```

---

## 5. Data Sources

### yfinance (Primary)
- **What it provides:** Real-time and historical OHLCV prices, company fundamentals (P/E, EPS, revenue, margins, etc.), options chains, analyst recommendations, upgrades/downgrades
- **Coverage:** NSE/BSE Indian stocks, US stocks, global indices, commodities futures, currency pairs
- **Latency:** ~15-minute delayed for free (real-time for most indices)
- **Cost:** Free

### DuckDuckGo Search (News & Research)
- **What it provides:** Latest news articles, analyst reports, sector outlooks
- **Used for:** `search_stock_news`, `search_macro_news`, `search_sector_analysis`, `search_analyst_ratings`, `search_ipo_and_corporate_actions`
- **Cost:** Free (rate-limited)

### RSS Feeds (Breaking News)
- **Economic Times Markets:** `https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms`
- **Moneycontrol:** `https://www.moneycontrol.com/rss/latestnews.xml`
- **Fetched with:** Python `urllib` + `xml.etree.ElementTree`

---

## 6. Core Data Structures

### `NIFTY_INDEX_MAP`
Maps human-readable index names to yfinance symbols:

```python
NIFTY_INDEX_MAP = {
    # Broad Market
    "NIFTY50"   : "^NSEI",       # Nifty 50 Index
    "SENSEX"    : "^BSESN",      # BSE Sensex
    "BANKNIFTY" : "^NSEBANK",    # Bank Nifty
    "NIFTYIT"   : "^CNXIT",      # Nifty IT Sector
    # ... 50+ more indices
    
    # US Futures
    "ES"  : "ES=F",   # S&P 500 Futures
    "NQ"  : "NQ=F",   # NASDAQ Futures
    "YM"  : "YM=F",   # Dow Futures
    
    # Commodities
    "GOLD"     : "GC=F",      # Gold Futures
    "CRUDEOIL" : "CL=F",      # WTI Crude Futures
    "SILVER"   : "SI=F",      # Silver Futures
    
    # Currencies
    "DXY"    : "DX-Y.NYB",   # Dollar Index
    "USDINR" : "USDINR=X",   # USD/INR rate
}
```

### `INDIAN_TICKERS`
A Python `set` of ~120 known Indian stock symbols (without `.NS`/`.BO` suffix). Used by `resolve_ticker()` to auto-detect Indian stocks.

### `SECTOR_INDICES`
Maps sector names to yfinance symbols for the momentum scanner:

```python
SECTOR_INDICES = {
    "IT"      : "^CNXIT",
    "Bank"    : "^NSEBANK",
    "FMCG"    : "^CNXFMCG",
    # ... 14 sectors total
}
```

---

## 7. Helper Functions

These private utility functions are used internally by all tools.

### `resolve_ticker(raw: str) → tuple`
Auto-detects the correct yfinance symbol and market for any input:

```python
resolve_ticker("RELIANCE")   # → ("RELIANCE.NS", "NSE 🇮🇳")
resolve_ticker("TCS.NS")     # → ("TCS.NS",      "NSE 🇮🇳")
resolve_ticker("AAPL")       # → ("AAPL",         "US 🇺🇸")
resolve_ticker("NIFTY50")    # → ("^NSEI",         "INDEX 📊")
resolve_ticker("GOLD")       # → ("GC=F",          "INDEX 📊")
resolve_ticker("ES")         # → ("ES=F",           "INDEX 📊")
resolve_ticker("500325")     # → ("500325.BO",      "BSE 🇮🇳")
```

**Detection priority:**
1. Check `NIFTY_INDEX_MAP` (covers indices, futures, commodities, FX)
2. Check `.NS` / `.BO` suffix
3. Check if numeric (→ BSE code)
4. Check `INDIAN_TICKERS` set
5. Default to US ticker

### `fmt(val, decimals=2, prefix="", suffix="") → str`
Safe number formatter that handles `None` and `NaN`:

```python
fmt(24.567)           # → "24.57"
fmt(None)             # → "N/A"
fmt(float('nan'))     # → "N/A"
fmt(0.1853, suffix="%")  # → "0.19%"
```

### `human_number(n) → str`
Converts large numbers to readable format:

```python
human_number(1_250_000_000_000)  # → "1.25 T"
human_number(8_500_000_000)      # → "8.50 B"
human_number(450_000_000)        # → "450.00 M"
human_number(125_000)            # → "125.00 K"
```

### `currency_sym(symbol: str) → str`
Returns `₹` for Indian assets, `$` for everything else:

```python
currency_sym("RELIANCE.NS")  # → "₹"
currency_sym("^NSEI")        # → "₹"
currency_sym("AAPL")         # → "$"
currency_sym("GC=F")         # → "$"
```

### `_compute_pivots(high, low, close) → tuple`
Computes standard pivot points from yesterday's OHLC:

```
PP = (High + Low + Close) / 3
R1 = 2×PP − Low       S1 = 2×PP − High
R2 = PP + (High−Low)  S2 = PP − (High−Low)
R3 = High + 2×(PP−Low) S3 = Low − 2×(High−PP)
```

Returns `(pp, r1, r2, r3, s1, s2, s3)`.

### `_rsi_series(close, period=14) → pd.Series`
Computes RSI for a full price series using Wilder's smoothing (EMA-based rolling averages). Used for both RSI(14) and RSI(9).

### `_compute_all_technicals(df) → dict`
The **central technical analysis engine**. Takes a DataFrame of OHLCV data and returns a dictionary of 30+ computed values:

```python
{
    "price": float,          # Latest close
    "rsi14": float,          # RSI(14)
    "rsi9": float,           # RSI(9) — short-term
    "stoch_k": float,        # Stochastic %K
    "stoch_d": float,        # Stochastic %D
    "macd_v": float,         # MACD line value
    "sig_v": float,          # Signal line value
    "hist_v": float,         # MACD histogram (positive = bullish)
    "ema9": float,           # EMA(9)
    "ema20": float,          # EMA(20)
    "ema50": float,          # EMA(50)
    "ema200": float,         # EMA(200)
    "sma20": float,          # SMA(20)
    "sma50": float,          # SMA(50)
    "bb_up": float,          # Bollinger Upper Band
    "bb_lo": float,          # Bollinger Lower Band
    "bb_mid": float,         # Bollinger Middle (SMA20)
    "bb_bw": float,          # Bandwidth % — squeeze detector
    "atr": float,            # ATR(14) — daily range estimate
    "avg_vol": float,        # 20-day average volume
    "last_vol": float,       # Latest day's volume
    "obv_trend": str,        # "Rising" or "Falling"
    "sup20": float,          # 20-day low (strong support)
    "res20": float,          # 20-day high (strong resistance)
    "sup5": float,           # 5-day low (immediate support)
    "res5": float,           # 5-day high (immediate resistance)
    "pp": float,             # Pivot Point
    "r1": float,             # Resistance 1
    "r2": float,             # Resistance 2
    "r3": float,             # Resistance 3
    "s1": float,             # Support 1
    "s2": float,             # Support 2
    "s3": float,             # Support 3
    "bull": int,             # Bullish signal count (0–7)
}
```

---

## 8. Tool Reference — All 21 Tools

### 8.1 Market Data Tools

---

#### `get_stock_quote(ticker)`
**Purpose:** Instant real-time price quote for any stock, index, or commodity.

**Inputs:** Any ticker — `RELIANCE`, `TCS.NS`, `AAPL`, `NIFTY50`, `GOLD`, `ES`

**Output:**
```
📊 QUOTE — RELIANCE.NS [NSE 🇮🇳]
────────────────────────────────────────────────────
  Price    : ₹2,847.30  ▲ +34.20 (+1.22%)
  Volume   : 12.45 M
  52W High : ₹3,217.90
  52W Low  : ₹2,180.50
  Mkt Cap  : 19.28 T
  Date     : 15 Mar 2026
```

**How it works:**
1. Calls `resolve_ticker()` to get the correct yfinance symbol
2. Fetches 5 days of history with `tk.history(period="5d")`
3. If NSE data is empty, automatically falls back to BSE (`.NS` → `.BO`)
4. Computes day change from previous close
5. Fetches 52W High/Low and market cap from `tk.fast_info`

---

#### `get_price_history(ticker)`
**Purpose:** Multi-period returns analysis with risk metrics.

**Output includes:**
- Returns: 1W, 1M, 3M, 6M, YTD, 1Y
- 1-Year price range (High, Low, Average)
- **Annualised Volatility** (standard deviation of daily returns × √252)
- **Sharpe Ratio** (annualised return ÷ annualised std dev)
- **Maximum Drawdown** (worst peak-to-trough decline over the year)

---

#### `compare_stocks_yf(tickers)`
**Purpose:** Side-by-side fundamental comparison of 2–4 stocks.

**Input:** Comma-separated or "A vs B" format — `"TCS, INFY, WIPRO"` or `"AAPL vs MSFT"`

**Compares 17 metrics including:**
- Price, Market Cap, P/E (TTM & Forward), PEG, P/B, EV/EBITDA
- EPS, Revenue, Net Margin, ROE, Debt/Equity
- Dividend Yield, 52W High/Low
- **Analyst consensus + Target price** (v5 addition)

---

#### `get_market_overview(market)`
**Purpose:** Quick live snapshot of major indices.

**Inputs:** `india` | `nse` | `us` | `global` | `vix`

**India mode shows:** Nifty 50, Sensex, Bank Nifty, Nifty IT, Auto, FMCG, Pharma, India VIX

---

### 8.2 Analysis & Report Tools

---

#### `get_analyst_consensus(ticker)`
**Purpose:** Fetches Wall Street / institutional analyst buy/sell/hold consensus and price targets.

**Data pulled from yfinance:**
- Recommendation key (BUY, HOLD, SELL, STRONG_BUY, etc.)
- Consensus score: 1.0 (Strong Buy) → 5.0 (Sell)
- Number of analysts covering the stock
- Target price: Low / Mean / Median / High
- Implied upside % from current price
- Recent upgrades/downgrades with firm name and date

**Supplemented with DuckDuckGo** for latest analyst calls not yet in yfinance.

**Score interpretation:**
```
1.0–1.5  → STRONG BUY 🟢🟢
1.5–2.5  → BUY 🟢
2.5–3.5  → HOLD ⚪
3.5–4.5  → UNDERPERFORM 🔴
4.5–5.0  → SELL 🔴🔴
```

---

#### `get_pcr_and_options_analysis(ticker)`
**Purpose:** Analyses the live options chain to compute PCR and identify options-derived support/resistance.

**How PCR is computed:**
```
PCR (OI)     = Total Put Open Interest ÷ Total Call Open Interest
PCR (Volume) = Total Put Volume ÷ Total Call Volume
```

**PCR Interpretation:**
```
PCR > 1.3   → STRONG BULLISH — heavy put writing; market expects upside
PCR 1.0–1.3 → BULLISH
PCR 0.8–1.0 → NEUTRAL
PCR 0.6–0.8 → BEARISH
PCR < 0.6   → STRONG BEARISH — heavy call writing
```

**Max Pain calculation:**
For each strike price, the total option buyer loss is calculated:
```
Pain at strike S = Σ(call_OI × max(0, S − call_strike))
                 + Σ(put_OI × max(0, put_strike − S))
Max Pain = strike with minimum total pain value
```
Price tends to gravitate toward max pain near expiry (option seller advantage).

**Key support/resistance:** Top 3 Put OI strikes = support zones; Top 3 Call OI strikes = resistance zones.

---

#### `get_detailed_fundamental_report(ticker)`
**Purpose:** Comprehensive fundamental analysis with a scored report card.

**Scoring System (0–100 points across 4 pillars):**

| Pillar | Points | Key Metrics |
|---|---|---|
| Valuation | 25 | P/E TTM relative to market |
| Profitability | 25 | ROE, Net Margin, Operating Margin |
| Growth | 25 | Revenue Growth YoY, Earnings Growth YoY |
| Balance Sheet | 25 | Debt/Equity, Current Ratio |

**Grade Scale:**
```
80–100 → A+ 🏆 STRONG BUY
65–79  → A  🟢 BUY
50–64  → B  ✅ BUY/HOLD
35–49  → C  ⚠️ HOLD
20–34  → D  🔴 REDUCE
0–19   → F  ❌ SELL
```

---

#### `get_detailed_technical_report(ticker)`
**Purpose:** Multi-indicator technical analysis with a scored grade.

**Technical Score (0–10 points):**
```
+2  Price above EMA200 (primary trend filter)
+1  Price above EMA50
+1  Price above EMA20
+1  MACD histogram positive (bullish momentum)
+1  RSI(14) between 40–70 (healthy, not overbought)
+1  Stochastic %K below 80 (not overbought)
+1  OBV Rising (volume confirming price)
+1  Volume ≥ 70% of 20-day average (adequate participation)
+1  BB Bandwidth < 8% (not overextended)
```

**Grade:**
```
8–10 → STRONG BUY 🟢🟢  (A+)
6–7  → BUY 🟢           (A)
5    → MILD BUY 🟢       (B)
4    → NEUTRAL ⚪         (C)
3    → MILD SELL 🔴       (D)
0–2  → SELL 🔴🔴         (F)
```

**Output sections:**
- EMA Cloud (9/20/50/200) with Golden/Death Cross status
- Momentum: RSI(14), RSI(9), Stochastic %K/%D, MACD
- Volatility: Bollinger Bands + Bandwidth, ATR
- Volume: raw volume, 20-day average, OBV trend
- Daily Pivot Points: PP, R1/R2/R3, S1/S2/S3
- Support/Resistance: 5-day zones (immediate) + 20-day zones (strong)

---

#### `get_nifty_index_analysis(index_name)`
**Purpose:** Deep analysis of any of the 50+ supported Nifty indices.

**Supported inputs (examples):**
```
Broad:    NIFTY50, NIFTY100, NIFTY500, NIFTYMIDCAP100, NIFTYSMALLCAP100
Sector:   BANKNIFTY, NIFTYIT, NIFTYFMCG, NIFTYAUTO, NIFTYPHARMA,
          NIFTYMETAL, NIFTYREALTY, NIFTYENERGY, NIFTYPSUBANK,
          NIFTYFINSERV, NIFTYOILGAS, NIFTYHEALTHCARE, NIFTYMEDIA
Thematic: NIFTYCPSE, NIFTYALPHA50, NIFTYDIVIDEND, NIFTYV20
Volatility: INDIAVIX
```

**Output:** 1Y price history, multi-period returns, full technicals, pivot points, support/resistance zones.

---

### 8.3 Trade Setup Tools

---

#### `get_intraday_trade_setup(ticker)`
**Purpose:** Generates a complete intraday (day trading) setup using pivot analysis on 15-minute data.

**Data used:**
- **15-minute candles** (last 5 days) for intraday technicals
- **Daily candles** (last 30 days) as the trend filter

**Setup methodology:**

```
LONG SETUP:
  Entry Zone  = around Pivot Point (PP) or EMA20 on 15-min
  Stop-Loss   = below nearest 5-day support or S1 pivot − (0.3 × ATR15)
                (also: min of entry − 1.2 × ATR15)
  Target 1    = R1 (Resistance 1)
  Target 2    = R2 (Resistance 2)
  Target 3    = R2 + (R2 − R1) extension

SHORT SETUP:
  Entry Zone  = around PP or EMA20 resistance
  Stop-Loss   = above nearest 5-day resistance or R1 + (0.3 × ATR15)
  Target 1    = S1 (Support 1)
  Target 2    = S2 (Support 2)
  Target 3    = S2 − (S1 − S2) extension
```

**Position sizing (1% risk rule):**
```
Quantity = (Capital × 1%) ÷ (Entry Price − Stop-Loss)
Example:  Capital ₹1,00,000 | Risk ₹50/share → Qty = 20 shares
```

**Quality rating:**
- `STRONG ✅` — RSI healthy + MACD aligned + daily trend confirmed
- `MODERATE ⚠️` — 2 of 3 conditions met
- `WEAK ❌` — poor alignment

**Intraday rules embedded in output:**
- Trade LONG only above PP in uptrend; SHORT only below PP in downtrend
- Book 50% at T1, trail SL to entry for remainder
- Exit all positions 15 min before market close (3:15 PM IST)

---

#### `get_swing_trade_setup(ticker)`
**Purpose:** Generates a swing trade setup (2–15 days) using Fibonacci retracement/extension.

**Data used:** 6 months of daily candles

**Setup methodology:**

```
Swing Range = 20-day High (R20) − 20-day Low (S20)

LONG SETUP (Uptrend / Pullback):
  Entry  = Fib 38.2% retracement OR above R20 breakout
  SL     = below Fib 61.8% OR 2 × daily ATR below entry
  T1     = 10-day High
  T2     = Fib 127.2% extension
  T3     = Fib 161.8% extension

SHORT SETUP (Downtrend / Bounce):
  Entry  = Fib 38.2% bounce resistance OR below S20 breakdown
  SL     = above Fib 38.2% OR 2 × daily ATR above entry
  T1     = 10-day Low
  T2     = Fib 50% support
  T3     = 20-day Low
```

**Fibonacci levels computed:**
```
Swing High  = R20
Fib 38.2%   = R20 − 0.382 × (R20 − S20)
Fib 50.0%   = R20 − 0.500 × (R20 − S20)
Fib 61.8%   = R20 − 0.618 × (R20 − S20)  ← Golden Ratio SL level
Fib 127.2%  = R20 + 0.272 × (R20 − S20)  ← T2 target
Fib 161.8%  = R20 + 0.618 × (R20 − S20)  ← T3 target
```

**Position sizing (2% risk rule for swing):**
```
Quantity = (Capital × 2%) ÷ (Entry Price − Stop-Loss)
```

**Quality scoring (0–5):**
```
+1  RSI < 65 (not overbought for long)
+1  MACD histogram positive
+1  Price above EMA50
+1  OBV Rising
+1  Stochastic < 70
```

**Booking strategy:**
- T1 → Book 40%, move SL to breakeven
- T2 → Book 40%, trail remaining with ATR-based stop
- T3 → Book final 20% (runners)

---

### 8.4 Global Macro Tools

---

#### `get_global_macro_dashboard(category)`
**Purpose:** Live dashboard of all global macro indicators that move Indian markets.

**Categories:** `commodities` | `currencies` | `energy` | `metals` | `all`

**Instruments covered:**

| Category | Instruments |
|---|---|
| Energy | WTI Crude, Brent Crude, Natural Gas |
| Metals | Gold, Silver, Copper, Platinum |
| Currencies | DXY, USD/INR, EUR/USD, GBP/USD, USD/JPY, USD/CNY |

**Output includes:**
- Live price, 1-day change %, 1-week change % for every instrument
- **Live contextual interpretation block** that reads current values and explains:
  - Crude Oil impact on India (inflation, CAD, OMC margins, ONGC)
  - Gold level (safe-haven signal, jewellery sector)
  - DXY direction (FII flow indicator)
  - USD/INR level (importers vs exporters)

**Example interpretation:**
```
🛢️  CRUDE OIL @ $88.50/bbl (+1.2% today)
    → HIGH crude: Inflation risk 🔴 | OMC under-recovery risk 🔴
    → CAD widens 🔴 | INR depreciation pressure 🔴 | ONGC/OIL India benefit 🟢

💵 DOLLAR INDEX @ 106.3 (+0.3% today)
    → STRONG DXY: FII outflow pressure on India 🔴 | INR weakness 🔴
    → IT/Pharma exporters benefit from INR depreciation 🟢
```

---

#### `get_us_markets_and_futures(mode)`
**Purpose:** Live US equity markets + overnight futures + sector ETF dashboard with pre-open gap signal for Indian markets.

**Modes:** `indices` | `futures` | `sectors` | `all`

**Cash Indices tracked:** S&P 500, NASDAQ Composite, NASDAQ-100, Dow Jones, Russell 2000, CBOE VIX (with 52-week position %)

**Futures tracked:**
| Contract | Symbol | Represents |
|---|---|---|
| ES | ES=F | S&P 500 Futures |
| NQ | NQ=F | NASDAQ 100 Futures |
| YM | YM=F | Dow Jones Futures |
| RTY | RTY=F | Russell 2000 Futures |
| VX | VX=F | VIX Futures |
| ZB | ZB=F | 30-Year T-Bond Futures |
| ZN | ZN=F | 10-Year T-Note Futures |

**15 Sector ETFs tracked:** XLK (Tech), XLF (Financials), XLE (Energy), XLV (Healthcare), XLI (Industrials), XLY (Cons. Disc.), XLP (Cons. Staples), XLU (Utilities), XLB (Materials), XLRE (Real Estate), XLC (Comm. Svcs), GLD (Gold ETF), SLV (Silver ETF), USO (Oil ETF), TLT (20Y Bond ETF)

**Pre-open Gap Indicator** — combines 4 factors:

```
Factor                 Bullish Threshold    Weight
─────────────────────  ──────────────────   ──────
S&P Futures            > +0.3%              2 pts
US VIX                 < 15                 1 pt
Dollar Index           falling              1 pt
Crude Oil              falling              1 pt

Final Signal:
  Bull% ≥ 70% → BULLISH OPEN LIKELY 🟢🟢
  Bull% 55–70% → MILD BULLISH OPEN 🟢
  Bull% 45–55% → NEUTRAL / FLAT ⚪
  Bull% 30–45% → MILD BEARISH OPEN 🔴
  Bull% < 30%  → BEARISH OPEN LIKELY 🔴🔴
```

---

#### `get_macro_impact_analysis(ticker)`
**Purpose:** Sector-specific analysis of how current global macro conditions affect a given stock or sector.

**How it works:**
1. Fetches all 10 macro instruments live (crude, brent, gold, silver, DXY, USD/INR, S&P500, VIX, US10Y yield, Natural Gas)
2. Auto-detects the sector from a built-in mapping of ~80 tickers/indices
3. Delivers sector-specific narrative with real numbers

**Sector detection examples:**
```python
"TCS", "INFY", "WIPRO"     → IT sector
"ONGC", "GAIL"             → OilGas sector
"BPCL", "IOC", "HINDPETRO" → OMC (Oil Marketing Companies) sector
"TATASTEEL", "JSWSTEEL"    → Metal sector
"HDFCBANK", "ICICIBANK"    → Banking sector
"SUNPHARMA", "DRREDDY"     → Pharma sector
"MARUTI", "M&M"            → Auto sector
"HINDUNILVR", "ITC"        → FMCG sector
"TITAN", "KALYANKJIL"      → Gold/Jewellery sector
```

**Sector-specific narratives:**

| Sector | Key Macro Drivers |
|---|---|
| IT | USD/INR (revenue multiplier), DXY (FII flows), US 10Y yield, US tech spend |
| OMC | Crude oil (under-recovery), USD/INR (import cost) |
| E&P (ONGC) | Crude oil (realisation), Natural Gas prices |
| Metal | S&P500 (demand signal), Copper, USD/INR (export competitiveness) |
| Pharma | USD/INR (export revenue ~60-70% USD), US Healthcare ETF |
| Banking | US 10Y yield (bond MTM, FII flows), VIX (credit risk), INR |
| Auto | Crude (fuel cost / EV shift), USD/INR (imported parts), S&P |
| FMCG | Crude (packaging/palm oil costs), USD/INR (imports), VIX |
| Gold/Jewellery | Gold price (revenue), USD/INR (domestic gold price) |

**Final macro score:**
```
5/5 positive factors → ✅ MACRO TAILWIND
3–4/5               → 🟡 MACRO NEUTRAL
0–2/5               → 🔴 MACRO HEADWIND
```

---

### 8.5 Index & Sector Tools

---

#### `get_nifty_dashboard(category)`
**Purpose:** Live snapshot table of all Nifty indices grouped by category.

**Categories:**
- `broad` — Nifty 50/100/500, Midcap, Smallcap, Sensex, India VIX
- `sector` — All 14 sector indices (Bank, IT, FMCG, Auto, Pharma, Metal, Realty, Energy, Infra, PSU Bank, Financial Services, Media, Oil & Gas, Healthcare)
- `thematic` — CPSE, Dividend, Alpha50, HiBeta50, Value20, Quality30, LowVol30
- `all` — Everything combined (~28 indices)

---

#### `get_sectoral_momentum(period)`
**Purpose:** Ranks all 14 Nifty sector indices by performance over a chosen period.

**Input:** `1W` | `1M` | `3M` | `6M` | `1Y`

**Output:** Sorted table with price, return %, RSI, and overbought/oversold signal for each sector. Highlights top gainer and top laggard.

---

### 8.6 News & Research Tools

---

#### `search_stock_news(query)`
**Purpose:** Fetches latest news from 3 sources simultaneously.

**Sources:**
1. DuckDuckGo web search (5 results)
2. Economic Times Markets RSS feed (top 3 headlines)
3. Moneycontrol RSS feed (top 3 headlines)

**Best for:** Earnings results, corporate announcements, management commentary, regulatory news.

---

#### `search_macro_news(topic)`
**Purpose:** Macro-economic news search via DuckDuckGo.

**Best for:** RBI policy decisions, FII/DII flow data, CPI/WPI inflation, budget impact, USD/INR movements, crude oil geopolitics.

---

#### `search_sector_analysis(sector)`
**Purpose:** Research sector trends, industry outlook, competitive landscape.

**Best for:** "Indian IT sector H2 2025 outlook", "PSU banks NPA trends", "EV industry India 2025".

---

#### `search_analyst_ratings(query)`
**Purpose:** Searches for latest analyst research reports, price targets, and rating changes via DuckDuckGo.

---

#### `search_ipo_and_corporate_actions(query)`
**Purpose:** IPO news, upcoming listings, dividends, buybacks, bonus shares, stock splits, rights issues.

---

## 9. The ReAct Agent

### How the Agent Decides What to Do

The agent uses the **ReAct (Reason + Act)** framework where the LLM alternates between:
1. **Thought** — reasoning about what information is needed
2. **Action** — selecting and calling a tool
3. **Observation** — reading the tool's output
4. **Repeat** until enough information is gathered
5. **Final Answer** — synthesising all observations

### AgentExecutor Configuration

```python
executor = AgentExecutor(
    agent=agent,
    tools=ALL_TOOLS,
    verbose=True,           # Shows Thought/Action/Observation in terminal
    handle_parsing_errors=True,  # Recovers from LLM formatting mistakes
    max_iterations=15,      # Max tool calls per query
    max_execution_time=150, # Timeout in seconds
)
```

### How the System Prompt Guides Tool Routing

The `SYSTEM_PROMPT` includes explicit routing rules that tell the agent which tools to call for each query type:

```
STOCK QUERY    → quote + fundamental report + technical report 
                 + analyst consensus + macro impact + news
INDEX QUERY    → index analysis + PCR + US futures + news
INTRADAY SETUP → intraday setup + technical report + PCR + US futures
MACRO QUERY    → macro dashboard + US futures + macro news
```

This dramatically reduces tool selection errors and ensures comprehensive coverage.

---

## 10. System Prompt Design

The `SYSTEM_PROMPT` is a carefully engineered multi-section prompt:

### Section 1: Identity + Market Knowledge
Tells the LLM it is an expert analyst covering Indian and US markets, with knowledge of ticker conventions (.NS = NSE, .BO = BSE, ^NSEI = Nifty 50, etc.)

### Section 2: Tool Routing Guide
Maps query types to specific tool sequences. This is the most critical section for agent performance.

### Section 3: Response Structure
Mandates labelled output sections: `[QUOTE]`, `[FUNDAMENTAL REPORT]`, `[TECHNICAL REPORT]`, `[PCR/OPTIONS]`, `[ANALYST CONSENSUS]`, `[GLOBAL MACRO]`, `[MACRO IMPACT]`, `[NEWS]`, `[TRADE SETUP]`, `[VERDICT]`

### Section 4: Macro Interpretation Cheatsheet
Hardcoded macro thresholds that the LLM uses when interpreting macro data:

```
Crude Oil > $85/bbl  → inflation risk, CAD pressure
DXY > 105            → FII outflows, IT benefits
USD/INR > 86         → exporters benefit, import inflation
US VIX > 20          → global risk-off
S&P Futures +0.5%+   → India likely gaps up
US 10Y Yield > 4.5%  → FII outflows, growth stocks hurt
```

### Section 5: Trade Setup Framework
Documents the exact SL/target calculation methodology so the LLM explains setups correctly.

### Temperature Setting
`temperature=0.15` — very low, making responses precise and consistent (not creative). Ideal for financial analysis where accuracy matters more than creativity.

---

## 11. Interactive Shell

The `main()` function provides a command-line interface with two modes:

### Mode 1: Quick Shortcuts (No LLM — Instant Response)
Direct function calls that bypass the LLM for speed:

```bash
StockSage v5> quote RELIANCE
StockSage v5> macro all
StockSage v5> usfut
StockSage v5> intraday BANKNIFTY
StockSage v5> swing TCS
```

### Mode 2: Natural Language (Full LLM + ReAct Chain)
Any query that doesn't match a shortcut pattern goes to the full agent:

```bash
StockSage v5> Give me a complete analysis of Reliance Industries with trade setup
StockSage v5> Is Bank Nifty oversold? Compare with India VIX
StockSage v5> How will rising crude oil impact Indian IT sector?
```

### Session History
The shell maintains an in-memory `history` list of `(question, answer)` tuples. Type `history` to review past queries in the session.

---

## 12. Quick Shortcuts Reference

| Command | Example | Calls |
|---|---|---|
| `quote <ticker>` | `quote RELIANCE` | `get_stock_quote` |
| `market <region>` | `market india` | `get_market_overview` |
| `macro [category]` | `macro` / `macro energy` | `get_global_macro_dashboard` |
| `usfut [mode]` | `usfut` / `usfut futures` | `get_us_markets_and_futures` |
| `impact <ticker>` | `impact INFY` | `get_macro_impact_analysis` |
| `dashboard <cat>` | `dashboard sector` | `get_nifty_dashboard` |
| `momentum <period>` | `momentum 1M` | `get_sectoral_momentum` |
| `index <name>` | `index BANKNIFTY` | `get_nifty_index_analysis` |
| `pcr <ticker>` | `pcr NIFTY50` | `get_pcr_and_options_analysis` |
| `intraday <ticker>` | `intraday TATAMOTORS` | `get_intraday_trade_setup` |
| `swing <ticker>` | `swing TCS` | `get_swing_trade_setup` |
| `analyst <ticker>` | `analyst HDFCBANK` | `get_analyst_consensus` |
| `help` | `help` | Prints help text |
| `history` | `history` | Shows session history |
| `clear` | `clear` | Clears session history |
| `exit` / `quit` | `exit` | Exits the program |

---

## 13. Example Queries & Expected Output

### Example 1: Full Stock Analysis

```
🔍 StockSage v5> Full analysis of TCS with trade setup
```

**Agent calls (in order):**
1. `get_stock_quote("TCS")`
2. `get_detailed_fundamental_report("TCS")`
3. `get_detailed_technical_report("TCS")`
4. `get_analyst_consensus("TCS")`
5. `get_macro_impact_analysis("TCS")`
6. `search_stock_news("TCS")`
7. `get_swing_trade_setup("TCS")` *(if swing is implied)*

**Final answer structure:**
```
[QUOTE]              Current price, change, volume
[FUNDAMENTAL REPORT] Score/100, grade, valuation, profitability, growth, B/S
[TECHNICAL REPORT]   Score/10, grade, EMAs, momentum, volatility, pivots
[ANALYST CONSENSUS]  Buy/Hold/Sell, target price, upside %
[MACRO IMPACT]       USD/INR effect on IT revenues, DXY/FII flows
[NEWS]               Latest 5 news items
[TRADE SETUP]        Intraday and/or swing setup with SL/T1/T2/T3/RR
[VERDICT]
  📈 Bull Case: ...
  📉 Bear Case: ...
  🎯 Key Levels: Support | Resistance | Max Pain | Target
  📊 Analyst View: BUY | Target ₹X | Upside Y%
  🌍 Macro Signal: Tailwind/Neutral/Headwind
```

---

### Example 2: Intraday Trade Setup

```
🔍 StockSage v5> Intraday trade setup for BANKNIFTY
```
OR use shortcut:
```
🔍 StockSage v5> intraday BANKNIFTY
```

**Output (abridged):**
```
⚡ INTRADAY TRADE SETUP — ^NSEBANK [INDEX 📊]
════════════════════════════════════════════════════════════
  Current Price   : ₹51,247.35
  Daily Trend     : UPTREND (Daily EMA50 filter)
  ATR(14) Daily   : ₹412.50  |  ATR 15-min: ₹85.30
  Today Range     : H:₹51,520  L:₹50,980

  [PIVOT LEVELS]
  PP:₹51,125  R1:₹51,435  R2:₹51,825  R3:₹52,135
              S1:₹50,735  S2:₹50,425  S3:₹50,035

  ┌─ 📈 LONG (BUY) SETUP ─────────────────────────────
  │  Quality       : STRONG ✅
  │  Entry Zone    : ₹51,100 – ₹51,175
  │  Stop-Loss     : ₹50,710  (Risk: ₹435.00)
  │  Target 1 (R1) : ₹51,435  →  RR 0.8:1  🎯
  │  Target 2 (R2) : ₹51,825  →  RR 1.7:1  🎯🎯
  │  Target 3      : ₹52,215  →  RR 2.6:1  🎯🎯🎯
  │  Position Size : 2 lots (1% risk on ₹1,00,000)
  └──────────────────────────────────────────────────
```

---

### Example 3: Global Macro Dashboard

```
🔍 StockSage v5> macro
```

**Output:**
```
🌍 GLOBAL MACRO DASHBOARD — ALL MACRO INDICATORS
══════════════════════════════════════════════════════════════
  Instrument                   Price     Change    %Chg  Trend
  ─────────────────────────── ─────────  ──────── ──────  ───────
  Crude Oil WTI ($/bbl)           88.420    +0.920  +1.05%  ▲ W:+2.1%
  Crude Oil Brent ($/bbl)         91.150    +0.880  +0.97%  ▲ W:+1.8%
  Natural Gas ($/MMBtu)            2.840    -0.020  -0.70%  ▼ W:-1.2%
  Gold ($/oz)                   2,356.200   +8.400  +0.36%  ▲ W:+0.8%
  Silver ($/oz)                   28.450    +0.230  +0.82%  ▲ W:+1.4%
  Dollar Index (DXY)             106.240    +0.150  +0.14%  ▲ W:+0.4%
  USD/INR                         86.320    +0.180  +0.21%  ▲ W:+0.3%
  ...

  📌 MARKET IMPACT GUIDE
  🛢️  CRUDE OIL @ $88.42/bbl  (+1.05% today)
     → HIGH crude: Inflation risk 🔴 | OMC under-recovery risk 🔴
     → CAD widens 🔴 | ONGC/OIL India benefit 🟢

  💵 DOLLAR INDEX @ 106.24  (+0.14% today)
     → STRONG DXY: FII outflow pressure on India 🔴
     → IT/Pharma exporters benefit from INR depreciation 🟢

  🇮🇳 USD/INR @ ₹86.32
     → WEAK INR: Import costs higher 🔴 | IT/Pharma exporters benefit 🟢
```

---

### Example 4: Pre-Open Gap Check

```
🔍 StockSage v5> usfut
```

**Output (key section):**
```
  S&P Futures : +0.42%  |  VIX: 14.8  |  DXY: +0.14%  |  Crude: +1.05%
  ┌──────────────────────────────────────────────────────────┐
  │  Indian Market Pre-Open Signal : MILD BULLISH OPEN 🟢    │
  │  Bull Score: 3  Bear Score: 2  Confidence: 60%           │
  └──────────────────────────────────────────────────────────┘
```

---

## 14. Technical Indicators Explained

### RSI (Relative Strength Index)
- Period: 14 days (also 9 days for short-term)
- Formula: `RSI = 100 − 100 / (1 + RS)` where `RS = Avg Gain / Avg Loss`
- Signals: < 30 = Oversold (buy zone); > 70 = Overbought (sell zone); 40–60 = Neutral

### MACD (Moving Average Convergence Divergence)
- Parameters: (12, 26, 9)
- Formula: `MACD Line = EMA(12) − EMA(26)` | `Signal = EMA(9) of MACD`
- Histogram: `MACD − Signal` — positive = bullish momentum; negative = bearish

### Stochastic Oscillator
- Parameters: %K(14,3), %D(3)
- Formula: `%K = (Close − Low14) / (High14 − Low14) × 100` smoothed over 3 days
- Signals: < 20 = Oversold; > 80 = Overbought

### Bollinger Bands
- Parameters: SMA(20) ± 2×StdDev
- Bandwidth: `(Upper − Lower) / Middle × 100%`
- Bandwidth < 4% = **Squeeze** (breakout imminent); > 12% = overextended
- Price near Upper band → overbought; near Lower → oversold

### ATR (Average True Range)
- Period: 14 days
- Formula: `TR = max(H−L, |H−PrevClose|, |L−PrevClose|)` averaged over 14 days
- Use: Stop-loss sizing (1× ATR = normal SL; 2× ATR = wider SL for swing trades)

### OBV (On-Balance Volume)
- Formula: Running cumulative sum; +volume on up days, −volume on down days
- Rising OBV + rising price = confirmed uptrend
- Divergence (price up, OBV down) = distribution / weak hands

### Pivot Points (Standard)
- Computed from **yesterday's** High, Low, Close
- PP = (H + L + C) / 3 — the central pivot, acts as bias line
- Above PP = bullish bias; Below PP = bearish bias
- R1/R2/R3 = resistance levels; S1/S2/S3 = support levels

---

## 15. Trade Setup Framework

### Risk Management Principles Built In

**1% Risk Rule (Intraday):**
> Never risk more than 1% of capital on a single intraday trade.
> `Position Size = (Capital × 1%) ÷ Per-Share Risk`

**2% Risk Rule (Swing):**
> Never risk more than 2% of capital on a single swing trade.
> `Position Size = (Capital × 2%) ÷ Per-Share Risk`

**Booking Strategy:**
```
Intraday:
  At T1 → Book 50% of position
  Move SL to entry (breakeven)
  Let rest run to T2/T3

Swing:
  At T1 → Book 40%
  At T2 → Book 40%, trail remaining with ATR stop
  At T3 → Book final 20% (runners)
```

### Minimum RR (Risk-Reward) Requirements
- Intraday: Minimum **1.5:1** (prefer 2:1)
- Swing: Minimum **2:1** (prefer 3:1)

> A setup with RR < 1.5:1 should generally be skipped even if technically perfect, because one losing trade erases more than one winning trade.

### Stop-Loss Placement Logic

**Intraday SL:** Below the nearest of:
- 5-day low (immediate support)
- S1 pivot level
- 1.2 × 15-min ATR below entry
With a buffer of 0.3 × 15-min ATR beyond the level.

**Swing SL:** Below the nearest of:
- Fibonacci 61.8% retracement (golden ratio — most important Fib level)
- 10-day low
- 2 × daily ATR below entry

---

## 16. Global Macro Framework

### Why Global Macro Matters for Indian Markets

Indian equity markets are deeply interconnected with global macro factors. Understanding these correlations is critical for both intraday and positional trading.

### The 6 Key Macro Drivers

| Factor | Bullish for India | Bearish for India |
|---|---|---|
| **Crude Oil (WTI)** | Below $70/bbl | Above $85/bbl |
| **Gold** | Stable $1,800–$2,200 (risk-on) | Spike above $2,500 (risk-off signal) |
| **Dollar Index (DXY)** | Falling / Below 100 | Rising / Above 105 |
| **USD/INR** | Below ₹83 (stable INR) | Above ₹86 (weak INR) |
| **US VIX** | Below 15 (calm) | Above 20 (fear) |
| **US S&P Futures** | Rising (+0.5%+) | Falling (-0.5%-) |

### Sector Sensitivity Matrix

| Sector | Crude ↑ | Gold ↑ | DXY ↑ | INR Weak | VIX ↑ | US Mkts ↑ |
|---|---|---|---|---|---|---|
| IT / Pharma | Neutral | Bearish | Positive | Positive | Bearish | Positive |
| OMC (BPCL/IOC) | Very Bearish | Neutral | Bearish | Bearish | Neutral | Neutral |
| ONGC / Oil E&P | Very Positive | Neutral | Neutral | Bearish | Neutral | Neutral |
| Metal | Neutral | Neutral | Bearish | Positive | Bearish | Positive |
| Banking | Bearish | Negative | Bearish | Bearish | Very Bearish | Positive |
| Auto | Bearish | Neutral | Bearish | Bearish | Bearish | Neutral |
| FMCG | Bearish | Neutral | Bearish | Bearish | Positive | Neutral |
| Jewellery/Gold | Neutral | Very Positive | Neutral | Positive | Positive | Neutral |
| Realty | Bearish | Neutral | Bearish | Bearish | Bearish | Neutral |

---

## 17. Extending & Customising

### Adding a New Indian Stock

Simply add the ticker to `INDIAN_TICKERS`:

```python
INDIAN_TICKERS = {
    # ... existing tickers ...
    "ZYDUSLIFE",      # Add any NSE symbol
    "MOTHERSON",
    "SUNTV",
}
```

### Adding a New Nifty Index

Add to `NIFTY_INDEX_MAP`:

```python
NIFTY_INDEX_MAP = {
    # ... existing entries ...
    "NIFTYDEFENCE" : "NIFTYDEFENCE.NS",   # Example new index
}
```

### Adding a New Commodity or Currency

```python
NIFTY_INDEX_MAP = {
    # ... existing entries ...
    "LITHIUM" : "LIT",        # ETF proxy
    "PALLADIUM" : "PA=F",     # Palladium futures
    "USDSGD" : "SGDUSD=X",   # SGD/USD
}
```

### Changing the LLM Model

In `.env`:

```env
GEMINI_MODEL=gemini-1.5-pro        # More powerful, slower
GEMINI_MODEL=gemini-2.0-flash      # Latest Gemini
```

Or switch to a different LLM provider entirely by replacing:

```python
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4o", temperature=0.15)
```

### Adding a New Tool

```python
@tool
def get_my_new_tool(input_param: str) -> str:
    """
    One-line description of what this tool does.
    Be specific — the LLM reads this to decide when to call the tool.
    Input: describe what input_param should be.
    """
    # Your implementation here
    return "formatted output string"

# Then add to ALL_TOOLS:
ALL_TOOLS = [
    ...
    get_my_new_tool,
]
```

### Adjusting Agent Aggressiveness

For more thorough analysis (more tool calls):

```python
executor = AgentExecutor(
    max_iterations=20,       # Allow more tool calls
    max_execution_time=240,  # Allow more time
)
```

For faster but shallower analysis:

```python
executor = AgentExecutor(
    max_iterations=8,
    max_execution_time=60,
)
```

---

## 18. Troubleshooting

### `No data for 'TICKER'`
- Verify the ticker symbol is correct
- For Indian stocks, try appending `.NS` (NSE) or `.BO` (BSE)
- yfinance occasionally has data gaps; try again after a few seconds
- Some small-cap Indian stocks may not be in yfinance's database

### `No options data for SYMBOL`
- Options data is only available for optionable securities
- Indian indices (NIFTY50, BANKNIFTY) and large caps have options
- Penny stocks, small caps, and some ETFs have no options data

### `Agent error: ...` / Tool calling loops
- Usually caused by the LLM getting confused by complex queries
- Try simplifying the query or using a quick shortcut instead
- Increase `max_iterations` if the agent is cutting off mid-analysis

### Slow performance
- DuckDuckGo searches can be slow (1-3 seconds each)
- Use quick shortcuts (`macro`, `usfut`, `intraday`) to bypass the LLM
- Switch to `gemini-1.5-flash` (default) instead of pro models
- Reduce `max_iterations` for faster but less thorough responses

### `GEMINI_API_KEY not found`
- Ensure `.env` file is in the same directory as `stocksage_v5.py`
- Check for typos in the `.env` file — no spaces around `=`
- Verify the API key is valid at [https://aistudio.google.com](https://aistudio.google.com)

### RSS feed errors
- RSS failures are silently suppressed — the tool still works with DuckDuckGo results
- Some corporate firewalls block external RSS feeds
- This is non-critical; news still comes from DuckDuckGo

### ImportError for `duckduckgo_search`
```bash
pip install duckduckgo-search --upgrade
```

### ImportError for `langchainhub`
```bash
pip install langchainhub
```

---

## 19. Limitations & Disclaimer

### Data Limitations
- **yfinance data is delayed** by ~15 minutes for most instruments (not true real-time)
- Options data may be incomplete for less liquid instruments
- Analyst consensus data in yfinance lags behind Bloomberg/Refinitiv
- Some Nifty thematic indices have limited or no data in yfinance
- Historical data for some Indian indices goes back only 1–3 years

### Model Limitations
- The LLM can misinterpret ambiguous queries
- At `temperature=0.15`, responses are precise but may occasionally be repetitive
- The agent may call more tools than necessary for simple queries (use shortcuts instead)
- LLM-generated trade analysis should never replace professional financial advice

### Technical Analysis Limitations
- All technical indicators are **lagging** (they describe past price action, not predict future)
- Pivot points work best in liquid, trending markets and less so in thin or sideways markets
- PCR is a sentiment indicator, not a directional predictor — it can stay extreme for extended periods
- Fibonacci levels are subjective (based on which swing high/low you choose)

### Legal Disclaimer

> ⚠️ **IMPORTANT: This tool is for EDUCATIONAL and RESEARCH purposes ONLY.**
>
> - StockSage v5 does NOT constitute financial advice
> - All trade setups, recommendations, and analysis are illustrative only
> - Past performance does not guarantee future results
> - Always consult a SEBI-registered investment advisor before making investment decisions
> - The developer is NOT responsible for any financial losses arising from use of this tool
> - Trading in equities, derivatives, and commodities involves substantial risk of loss

---

## Appendix A — Complete Ticker Symbol Reference

### Indian Stocks (NSE — auto-detected, no suffix needed)

```
Large Cap:  RELIANCE, TCS, INFY, HDFCBANK, ICICIBANK, KOTAKBANK,
            HINDUNILVR, BHARTIARTL, ITC, SBIN, BAJFINANCE, AXISBANK,
            WIPRO, HCLTECH, MARUTI, TITAN, ULTRACEMCO, NESTLEIND,
            TATAMOTORS, TATASTEEL, JSWSTEEL, SUNPHARMA, DRREDDY,
            ADANIENT, ADANIPORTS, LT, M&M, ASIANPAINT ...

Mid Cap:    ZOMATO, NYKAA, DMART, IRCTC, LTIM, LTTS, MPHASIS,
            PERSISTENT, COFORGE, POLYCAB, DIXON, TRENT ...

PSU:        ONGC, COALINDIA, NTPC, POWERGRID, BEL, HAL, BHEL,
            BPCL, IOC, HINDPETRO, GAIL, RECLTD, PFC, NHPC ...
```

### Nifty Indices

```
Broad:     NIFTY50, NIFTY100, NIFTY200, NIFTY500
           NIFTYMIDCAP50, NIFTYMIDCAP100, NIFTYMIDCAP150
           NIFTYSMALLCAP50, NIFTYSMALLCAP100, NIFTYSMALLCAP250
           SENSEX

Sector:    BANKNIFTY, NIFTYIT, NIFTYFMCG, NIFTYAUTO, NIFTYPHARMA
           NIFTYMETAL, NIFTYREALTY, NIFTYENERGY, NIFTYINFRA
           NIFTYPSUBANK, NIFTYFINSERV, NIFTYMEDIA
           NIFTYOILGAS, NIFTYHEALTHCARE, NIFTYMFG

Thematic:  NIFTYCPSE, NIFTYDIVIDEND, NIFTYALPHA50, NIFTYHIGHBETA50
           NIFTYV20, NIFTY100QUALITY30, NIFTY100LOWVOL30

Volatility: INDIAVIX
```

### US Stocks (plain ticker)
`AAPL, MSFT, NVDA, TSLA, AMZN, GOOGL, META, JPM, BAC, V, UNH, WMT ...`

### US Indices
`SP500 (^GSPC), NASDAQ (^IXIC), DOW (^DJI), RUSSELL2000 (^RUT), VIX (^VIX)`

### US Futures
`ES (S&P500), NQ (NASDAQ), YM (Dow), RTY (Russell)`

### Commodities
`GOLD, SILVER, CRUDEOIL/WTI, BRENT, NATURALGAS, COPPER, PLATINUM`

### Currencies
`DXY/DOLLARINDEX, USDINR, EURUSD, GBPUSD, USDJPY`

---

## Appendix B — Full Tool List Summary

| # | Tool Name | Category | Key Output |
|---|---|---|---|
| 1 | `get_stock_quote` | Market Data | Price, change, volume, 52W H/L |
| 2 | `get_analyst_consensus` | Analysis | Buy/Sell/Hold, targets, upgrades |
| 3 | `get_pcr_and_options_analysis` | Analysis | PCR, Max Pain, OI support/resistance |
| 4 | `get_detailed_fundamental_report` | Analysis | Score/100, grade, full financials |
| 5 | `get_detailed_technical_report` | Analysis | Score/10, grade, all indicators, pivots |
| 6 | `get_intraday_trade_setup` | Trade Setup | Entry, SL, T1/T2/T3, RR, position size |
| 7 | `get_swing_trade_setup` | Trade Setup | Fib levels, Entry, SL, targets, RR |
| 8 | `get_global_macro_dashboard` | Macro | Crude, Gold, Silver, DXY, currencies |
| 9 | `get_us_markets_and_futures` | Macro | US indices, futures, ETFs, gap signal |
| 10 | `get_macro_impact_analysis` | Macro | Sector-specific macro sensitivity |
| 11 | `get_nifty_index_analysis` | Index | Full technical analysis for any index |
| 12 | `get_nifty_dashboard` | Index | Snapshot table of Nifty indices |
| 13 | `get_sectoral_momentum` | Index | Sector returns ranked table |
| 14 | `get_stock_fundamentals` | Analysis | Quick fundamental summary |
| 15 | `get_price_history` | Market Data | Multi-period returns, Sharpe, Max DD |
| 16 | `compare_stocks_yf` | Analysis | Side-by-side 17-metric comparison |
| 17 | `get_market_overview` | Market Data | Index-level overview |
| 18 | `search_stock_news` | News | DuckDuckGo + ET/MC RSS |
| 19 | `search_macro_news` | News | Macro-economic news |
| 20 | `search_sector_analysis` | Research | Sector outlook research |
| 21 | `search_ipo_and_corporate_actions` | Research | IPO, dividends, buybacks |

---

*StockSage v5 — Built with ❤️ using LangChain, Google Gemini, yfinance, and DuckDuckGo*

*⚠️ For educational purposes only. Not financial advice.*
