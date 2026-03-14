"""
StockSage — AI Research Agent v2
Supports Indian (NSE/BSE) & US markets
Data: yfinance (real market data) + DuckDuckGo (news & web research)
LLM : Gemini via LangChain ReAct
"""

import os
import warnings
from datetime import datetime
from dotenv import load_dotenv

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

load_dotenv()
os.environ["LANGCHAIN_TRACING_V2"] = "false"

api_key = os.getenv("GEMINI_API_KEY")
model   = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

# ─────────────────────────────────────────────────────────────────────────────
# MARKET HELPERS
# ─────────────────────────────────────────────────────────────────────────────

INDIAN_TICKERS = {
    "RELIANCE","TCS","INFY","HDFCBANK","ICICIBANK","KOTAKBANK","HINDUNILVR",
    "BHARTIARTL","ITC","SBIN","BAJFINANCE","AXISBANK","WIPRO","HCLTECH",
    "MARUTI","TITAN","ULTRACEMCO","NESTLEIND","POWERGRID","NTPC","ONGC",
    "COALINDIA","TATAMOTORS","TATASTEEL","JSWSTEEL","SUNPHARMA","DRREDDY",
    "CIPLA","DIVISLAB","ADANIENT","ADANIPORTS","INDUSINDBANK","TECHM",
    "BAJAJFINSV","BAJAJ-AUTO","EICHERMOT","HEROMOTOCO","M&M","ASIANPAINT",
    "BRITANNIA","DABUR","MARICO","GODREJCP","PIDILITEIND","HAVELLS",
    "VOLTAS","TATACONSUM","ZOMATO","NYKAA","PAYTM","DMART","IRCTC",
    "LT","LTIM","LTTS","MPHASIS","PERSISTENT","COFORGE","NIFTY50","BANKNIFTY",
}

INDEX_MAP = {
    "NIFTY50": "^NSEI", "NIFTY": "^NSEI", "SENSEX": "^BSESN",
    "BANKNIFTY": "^NSEBANK", "SP500": "^GSPC", "SPX": "^GSPC",
    "NASDAQ": "^IXIC", "DOW": "^DJI",
}


def resolve_ticker(raw: str) -> tuple:
    raw = raw.strip().upper()
    if raw in INDEX_MAP:
        sym = INDEX_MAP[raw]
        return sym, "INDEX"
    if raw.endswith(".NS"):
        return raw, "NSE 🇮🇳"
    if raw.endswith(".BO"):
        return raw, "BSE 🇮🇳"
    if raw.isdigit():
        return f"{raw}.BO", "BSE 🇮🇳"
    if raw in INDIAN_TICKERS:
        return f"{raw}.NS", "NSE 🇮🇳"
    return raw, "US 🇺🇸"


def fmt(val, decimals=2, prefix="", suffix=""):
    try:
        if val is None:
            return "N/A"
        import math
        if math.isnan(float(val)):
            return "N/A"
        return f"{prefix}{float(val):,.{decimals}f}{suffix}"
    except Exception:
        return str(val) if val else "N/A"


def human_number(n):
    try:
        n = float(n)
        if abs(n) >= 1e12: return f"{n/1e12:.2f} T"
        if abs(n) >= 1e9:  return f"{n/1e9:.2f} B"
        if abs(n) >= 1e6:  return f"{n/1e6:.2f} M"
        if abs(n) >= 1e3:  return f"{n/1e3:.2f} K"
        return str(round(n, 2))
    except Exception:
        return "N/A"


def currency_sym(symbol: str) -> str:
    return "₹" if (".NS" in symbol or ".BO" in symbol) else "$"


# ─────────────────────────────────────────────────────────────────────────────
# YFINANCE TOOLS
# ─────────────────────────────────────────────────────────────────────────────

from langchain.tools import tool


@tool
def get_stock_quote(ticker: str) -> str:
    """
    Get real-time price quote and key stats for any Indian or US stock.
    Indian: RELIANCE, TCS, INFY, HDFCBANK, TATAMOTORS, or TCS.NS / RELIANCE.BO
    US    : AAPL, MSFT, TSLA, NVDA, AMZN, GOOGL
    Input : ticker symbol.
    """
    import yfinance as yf
    symbol, market = resolve_ticker(ticker)
    try:
        tk   = yf.Ticker(symbol)
        hist = tk.history(period="5d")
        if hist.empty and ".NS" in symbol:
            symbol = symbol.replace(".NS", ".BO")
            market = "BSE 🇮🇳"
            tk     = yf.Ticker(symbol)
            hist   = tk.history(period="5d")
        if hist.empty:
            return f"No data for '{ticker}'. Verify the symbol."

        cur  = currency_sym(symbol)
        last = hist["Close"].iloc[-1]
        prev = hist["Close"].iloc[-2] if len(hist) > 1 else last
        chg  = last - prev
        chgp = chg / prev * 100 if prev else 0
        vol  = hist["Volume"].iloc[-1]
        info = tk.fast_info

        out  = f"📊 QUOTE — {symbol} [{market}]\n{'─'*50}\n"
        out += f"  Price     : {cur}{last:,.2f}  {'▲' if chg>=0 else '▼'} {'+' if chg>=0 else ''}{chg:.2f} ({'+' if chgp>=0 else ''}{chgp:.2f}%)\n"
        out += f"  Volume    : {human_number(vol)}\n"
        out += f"  52W High  : {cur}{fmt(getattr(info,'year_high',None))}\n"
        out += f"  52W Low   : {cur}{fmt(getattr(info,'year_low',None))}\n"
        out += f"  Mkt Cap   : {human_number(getattr(info,'market_cap',None))}\n"
        out += f"  As of     : {hist.index[-1].strftime('%d %b %Y')}\n"
        return out
    except Exception as e:
        return f"Error fetching quote for {symbol}: {e}"


@tool
def get_stock_fundamentals(ticker: str) -> str:
    """
    Fetch real fundamental data: P/E, EPS, revenue, margins, ROE, debt-to-equity,
    dividends, book value for any Indian or US stock via yfinance.
    Indian: RELIANCE, TCS, HDFCBANK, INFY
    US    : AAPL, MSFT, GOOGL, NVDA
    Input : ticker symbol.
    """
    import yfinance as yf
    symbol, market = resolve_ticker(ticker)
    try:
        info = yf.Ticker(symbol).info
        if not info.get("regularMarketPrice") and ".NS" in symbol:
            symbol = symbol.replace(".NS", ".BO")
            info   = yf.Ticker(symbol).info
        cur = currency_sym(symbol)
        out  = f"📊 FUNDAMENTALS — {symbol} [{market}]\n{'─'*50}\n"
        out += f"  Company      : {info.get('longName','N/A')}\n"
        out += f"  Sector       : {info.get('sector','N/A')}\n"
        out += f"  Industry     : {info.get('industry','N/A')}\n"
        out += f"\n  [VALUATION]\n"
        out += f"  P/E (TTM)    : {fmt(info.get('trailingPE'))}\n"
        out += f"  P/E (Fwd)    : {fmt(info.get('forwardPE'))}\n"
        out += f"  P/B Ratio    : {fmt(info.get('priceToBook'))}\n"
        out += f"  PEG Ratio    : {fmt(info.get('pegRatio'))}\n"
        out += f"  EV/EBITDA    : {fmt(info.get('enterpriseToEbitda'))}\n"
        out += f"\n  [EARNINGS]\n"
        out += f"  EPS (TTM)    : {cur}{fmt(info.get('trailingEps'))}\n"
        out += f"  EPS (Fwd)    : {cur}{fmt(info.get('forwardEps'))}\n"
        out += f"  Revenue      : {human_number(info.get('totalRevenue'))}\n"
        out += f"  Net Income   : {human_number(info.get('netIncomeToCommon'))}\n"
        out += f"  EBITDA       : {human_number(info.get('ebitda'))}\n"
        out += f"\n  [MARGINS & RETURNS]\n"
        out += f"  Gross Margin : {fmt((info.get('grossMargins') or 0)*100)}%\n"
        out += f"  Oper Margin  : {fmt((info.get('operatingMargins') or 0)*100)}%\n"
        out += f"  Net Margin   : {fmt((info.get('profitMargins') or 0)*100)}%\n"
        out += f"  ROE          : {fmt((info.get('returnOnEquity') or 0)*100)}%\n"
        out += f"  ROA          : {fmt((info.get('returnOnAssets') or 0)*100)}%\n"
        out += f"\n  [BALANCE SHEET]\n"
        out += f"  Debt/Equity  : {fmt(info.get('debtToEquity'))}\n"
        out += f"  Current Ratio: {fmt(info.get('currentRatio'))}\n"
        out += f"  Book Value   : {cur}{fmt(info.get('bookValue'))}\n"
        out += f"\n  [DIVIDENDS]\n"
        out += f"  Div Yield    : {fmt((info.get('dividendYield') or 0)*100)}%\n"
        out += f"  Div Rate     : {cur}{fmt(info.get('dividendRate'))}\n"
        out += f"  Payout Ratio : {fmt((info.get('payoutRatio') or 0)*100)}%\n"
        return out
    except Exception as e:
        return f"Error fetching fundamentals for {symbol}: {e}"


@tool
def get_technical_indicators(ticker: str) -> str:
    """
    Compute real technical indicators from live OHLCV data via yfinance:
    RSI(14), MACD(12,26,9), EMA20/50/200, Bollinger Bands(20,2), ATR(14),
    volume trend, support & resistance. Works for Indian and US stocks.
    Indian: RELIANCE, TCS, INFY.NS, WIPRO
    US    : TSLA, NVDA, AAPL, SPY
    Input : ticker symbol.
    """
    import yfinance as yf
    import pandas as pd
    import numpy as np
    symbol, market = resolve_ticker(ticker)
    try:
        df = yf.Ticker(symbol).history(period="6mo", interval="1d")
        if df.empty and ".NS" in symbol:
            symbol = symbol.replace(".NS", ".BO")
            market = "BSE 🇮🇳"
            df     = yf.Ticker(symbol).history(period="6mo", interval="1d")
        if df.empty:
            return f"No price history for '{ticker}'."

        close  = df["Close"]
        volume = df["Volume"]
        high   = df["High"]
        low    = df["Low"]
        cur    = currency_sym(symbol)

        # RSI(14)
        delta = close.diff()
        gain  = delta.clip(lower=0).rolling(14).mean()
        loss  = (-delta.clip(upper=0)).rolling(14).mean()
        rs    = gain / loss.replace(0, np.nan)
        rsi   = (100 - 100 / (1 + rs)).iloc[-1]

        # MACD(12,26,9)
        ema12    = close.ewm(span=12, adjust=False).mean()
        ema26    = close.ewm(span=26, adjust=False).mean()
        macd_l   = ema12 - ema26
        signal_l = macd_l.ewm(span=9, adjust=False).mean()
        hist_l   = macd_l - signal_l
        macd_v, sig_v, hist_v = macd_l.iloc[-1], signal_l.iloc[-1], hist_l.iloc[-1]

        # EMAs
        ema20  = close.ewm(span=20).mean().iloc[-1]
        ema50  = close.ewm(span=50).mean().iloc[-1]
        ema200 = close.ewm(span=200).mean().iloc[-1]

        # Bollinger Bands(20,2)
        sma20 = close.rolling(20).mean()
        std20 = close.rolling(20).std()
        bb_up = (sma20 + 2*std20).iloc[-1]
        bb_lo = (sma20 - 2*std20).iloc[-1]

        # ATR(14)
        tr  = pd.concat([high-low, (high-close.shift()).abs(), (low-close.shift()).abs()], axis=1).max(axis=1)
        atr = tr.rolling(14).mean().iloc[-1]

        # Volume
        avg_vol  = volume.rolling(20).mean().iloc[-1]
        last_vol = volume.iloc[-1]
        vol_tr   = "HIGH 🔥" if last_vol > avg_vol*1.5 else ("LOW 📉" if last_vol < avg_vol*0.5 else "NORMAL ⚪")

        # Support / Resistance
        recent     = df.tail(20)
        support    = recent["Low"].min()
        resistance = recent["High"].max()

        price = close.iloc[-1]
        rsi_sig  = "OVERSOLD 🟢 (potential buy zone)" if rsi<30 else ("OVERBOUGHT 🔴 (potential sell zone)" if rsi>70 else "NEUTRAL ⚪")
        macd_sig = "BULLISH 🟢 (histogram positive)" if hist_v>0 else "BEARISH 🔴 (histogram negative)"
        trend    = ("STRONG UPTREND 🟢" if price>ema50>ema200 else
                    "STRONG DOWNTREND 🔴" if price<ema50<ema200 else "MIXED / SIDEWAYS ⚪")
        bb_sig   = ("Near UPPER band 🔴 overbought" if price>bb_up*0.98 else
                    "Near LOWER band 🟢 oversold"   if price<bb_lo*1.02 else "Inside Bands ⚪")

        out  = f"📈 TECHNICALS — {symbol} [{market}]\n{'─'*50}\n"
        out += f"  Current Price : {cur}{price:,.2f}\n"
        out += f"\n  [TREND & EMAs]\n"
        out += f"  EMA 20   : {cur}{ema20:,.2f}  {'▲ above' if price>ema20 else '▼ below'}\n"
        out += f"  EMA 50   : {cur}{ema50:,.2f}  {'▲ above' if price>ema50 else '▼ below'}\n"
        out += f"  EMA 200  : {cur}{ema200:,.2f}  {'▲ above' if price>ema200 else '▼ below'}\n"
        out += f"  Trend    : {trend}\n"
        out += f"\n  [MOMENTUM]\n"
        out += f"  RSI(14)  : {rsi:.1f}  →  {rsi_sig}\n"
        out += f"  MACD     : {macd_v:.3f} | Signal: {sig_v:.3f} | Hist: {hist_v:.3f}\n"
        out += f"  MACD Sig : {macd_sig}\n"
        out += f"\n  [VOLATILITY]\n"
        out += f"  BB Upper : {cur}{bb_up:,.2f}\n"
        out += f"  BB Lower : {cur}{bb_lo:,.2f}\n"
        out += f"  BB Signal: {bb_sig}\n"
        out += f"  ATR(14)  : {cur}{atr:,.2f}\n"
        out += f"\n  [VOLUME]\n"
        out += f"  Last Vol : {human_number(last_vol)}\n"
        out += f"  Avg(20d) : {human_number(avg_vol)}\n"
        out += f"  Trend    : {vol_tr}\n"
        out += f"\n  [SUPPORT / RESISTANCE — 20d pivot]\n"
        out += f"  Support  : {cur}{support:,.2f}\n"
        out += f"  Resist.  : {cur}{resistance:,.2f}\n"
        return out
    except Exception as e:
        return f"Error computing technicals for {symbol}: {e}"


@tool
def get_price_history(ticker: str) -> str:
    """
    Show recent performance: 1W/1M/3M/6M/YTD/1Y returns, annualised volatility,
    and 1-year price range for any Indian or US stock.
    Indian: RELIANCE, TCS, NIFTY50
    US    : AAPL, SPY, QQQ
    Input : ticker symbol.
    """
    import yfinance as yf
    import numpy as np
    symbol, market = resolve_ticker(ticker)
    try:
        df = yf.Ticker(symbol).history(period="1y", interval="1d")
        if df.empty and ".NS" in symbol:
            symbol = symbol.replace(".NS", ".BO")
            df     = yf.Ticker(symbol).history(period="1y", interval="1d")
        if df.empty:
            return f"No price history for '{ticker}'."
        cur   = currency_sym(symbol)
        close = df["Close"]
        now   = close.iloc[-1]

        def ret(days):
            try:
                p = close.iloc[-days] if days < len(close) else close.iloc[0]
                r = (now - p) / p * 100
                return f"{'+' if r>=0 else ''}{r:.2f}%"
            except Exception:
                return "N/A"

        ytd_start = df[df.index.year == datetime.now().year]["Close"]
        ytd_ret   = ((now - ytd_start.iloc[0]) / ytd_start.iloc[0] * 100) if not ytd_start.empty else 0
        ann_vol   = close.pct_change().dropna().std() * (252**0.5) * 100

        out  = f"📅 PERFORMANCE — {symbol} [{market}]\n{'─'*50}\n"
        out += f"  Current : {cur}{now:,.2f}\n\n"
        out += f"  [RETURNS]\n"
        out += f"  1 Week  : {ret(5)}\n"
        out += f"  1 Month : {ret(21)}\n"
        out += f"  3 Month : {ret(63)}\n"
        out += f"  6 Month : {ret(126)}\n"
        out += f"  YTD     : {'+' if ytd_ret>=0 else ''}{ytd_ret:.2f}%\n"
        out += f"  1 Year  : {ret(252)}\n"
        out += f"\n  [1-YEAR RANGE]\n"
        out += f"  High    : {cur}{close.max():,.2f}\n"
        out += f"  Low     : {cur}{close.min():,.2f}\n"
        out += f"  Avg     : {cur}{close.mean():,.2f}\n"
        out += f"\n  [RISK]\n"
        out += f"  Ann. Vol: {ann_vol:.1f}%  — {'High' if ann_vol>40 else 'Moderate' if ann_vol>20 else 'Low'} risk\n"
        return out
    except Exception as e:
        return f"Error fetching history for {symbol}: {e}"


@tool
def compare_stocks_yf(tickers: str) -> str:
    """
    Side-by-side fundamental comparison of 2-4 stocks using live yfinance data.
    Supports mixed markets: Indian + US.
    Examples:
      "RELIANCE, TCS, INFY"        (Indian)
      "AAPL, MSFT, GOOGL"          (US)
      "RELIANCE.NS, AAPL, TSLA"    (mixed)
    Input: comma-separated tickers (or use ' vs ' as separator).
    """
    import yfinance as yf
    raw_list = [t.strip() for t in tickers.replace(" vs ", ",").replace(" VS ", ",").split(",") if t.strip()]
    if len(raw_list) < 2:
        return "Provide at least 2 tickers to compare, e.g. 'RELIANCE, TCS, INFY'"

    rows = []
    for raw in raw_list[:4]:
        symbol, market = resolve_ticker(raw)
        try:
            info = yf.Ticker(symbol).info
            cur  = currency_sym(symbol)
            rows.append({
                "sym": symbol, "mkt": market, "cur": cur,
                "name"   : (info.get("shortName","") or symbol)[:22],
                "price"  : info.get("currentPrice") or info.get("regularMarketPrice"),
                "pe"     : info.get("trailingPE"),
                "fpe"    : info.get("forwardPE"),
                "pb"     : info.get("priceToBook"),
                "eps"    : info.get("trailingEps"),
                "rev"    : info.get("totalRevenue"),
                "margin" : info.get("profitMargins"),
                "roe"    : info.get("returnOnEquity"),
                "de"     : info.get("debtToEquity"),
                "mktcap" : info.get("marketCap"),
                "div"    : info.get("dividendYield"),
                "52wh"   : info.get("fiftyTwoWeekHigh"),
                "52wl"   : info.get("fiftyTwoWeekLow"),
            })
        except Exception as e:
            rows.append({"sym": symbol, "mkt": market, "cur": "$", "error": str(e)})

    metrics = [
        ("Price",       lambda r: f"{r['cur']}{fmt(r.get('price'))}"),
        ("Mkt Cap",     lambda r: human_number(r.get("mktcap"))),
        ("P/E (TTM)",   lambda r: fmt(r.get("pe"))),
        ("P/E (Fwd)",   lambda r: fmt(r.get("fpe"))),
        ("P/B",         lambda r: fmt(r.get("pb"))),
        ("EPS (TTM)",   lambda r: f"{r['cur']}{fmt(r.get('eps'))}"),
        ("Revenue",     lambda r: human_number(r.get("rev"))),
        ("Net Margin",  lambda r: f"{fmt((r.get('margin') or 0)*100)}%"),
        ("ROE",         lambda r: f"{fmt((r.get('roe') or 0)*100)}%"),
        ("Debt/Equity", lambda r: fmt(r.get("de"))),
        ("Div Yield",   lambda r: f"{fmt((r.get('div') or 0)*100)}%"),
        ("52W High",    lambda r: f"{r['cur']}{fmt(r.get('52wh'))}"),
        ("52W Low",     lambda r: f"{r['cur']}{fmt(r.get('52wl'))}"),
    ]

    out  = f"⚖️  COMPARISON — {' | '.join(r['sym'] for r in rows)}\n{'─'*60}\n"
    out += f"  {'Metric':<16}" + "".join(f"{r['sym']:<20}" for r in rows) + "\n"
    out += f"  {'─'*14}" + ("─"*20)*len(rows) + "\n"
    for label, fn in metrics:
        line = f"  {label:<16}"
        for r in rows:
            if "error" in r:
                line += f"{'ERR':<20}"
            else:
                try:
                    line += f"{fn(r):<20}"
                except Exception:
                    line += f"{'N/A':<20}"
        out += line + "\n"
    out += f"\n  Markets: {', '.join(r['sym']+'('+r['mkt']+')' for r in rows if 'error' not in r)}\n"
    return out


@tool
def get_market_overview(market: str) -> str:
    """
    Live overview of major market indices.
    Accepted inputs: india, nse, us, usa, nasdaq, nyse, global
    Examples: "india", "us", "global"
    Input: market name.
    """
    import yfinance as yf
    INDICES = {
        "india" : [("^NSEI","NIFTY 50"),("^BSESN","SENSEX"),("^NSEBANK","BANK NIFTY")],
        "nse"   : [("^NSEI","NIFTY 50"),("^BSESN","SENSEX"),("^NSEBANK","BANK NIFTY")],
        "us"    : [("^GSPC","S&P 500"),("^IXIC","NASDAQ"),("^DJI","DOW JONES"),("^RUT","RUSSELL 2000")],
        "usa"   : [("^GSPC","S&P 500"),("^IXIC","NASDAQ"),("^DJI","DOW JONES"),("^RUT","RUSSELL 2000")],
        "nasdaq": [("^IXIC","NASDAQ Composite"),("^NDX","NASDAQ-100")],
        "nyse"  : [("^GSPC","S&P 500"),("^DJI","DOW JONES")],
        "global": [("^NSEI","NIFTY 50"),("^BSESN","SENSEX"),("^GSPC","S&P 500"),("^IXIC","NASDAQ"),("^DJI","DOW JONES")],
    }
    key   = market.lower().strip()
    pairs = INDICES.get(key, INDICES["global"])
    out   = f"🌐 MARKET OVERVIEW — {market.upper()}\n{'─'*50}\n"
    for sym, name in pairs:
        try:
            hist = yf.Ticker(sym).history(period="5d")
            if hist.empty:
                out += f"  {name:<22}: N/A\n"; continue
            last = hist["Close"].iloc[-1]
            prev = hist["Close"].iloc[-2] if len(hist) > 1 else last
            ch   = last - prev
            chp  = ch / prev * 100 if prev else 0
            out += f"  {name:<22}: {last:>10,.2f}  {'▲' if ch>=0 else '▼'} {chp:+.2f}%\n"
        except Exception as e:
            out += f"  {name:<22}: Error\n"
    out += f"\n  {datetime.now().strftime('%d %b %Y %H:%M')} | Source: yfinance\n"
    return out


# ─────────────────────────────────────────────────────────────────────────────
# DUCKDUCKGO TOOLS
# ─────────────────────────────────────────────────────────────────────────────

@tool
def search_stock_news(query: str) -> str:
    """
    Search latest stock news and market sentiment via DuckDuckGo.
    Use for news, earnings updates, macro events that yfinance can't provide.
    Examples: "RELIANCE Industries news", "Apple AAPL earnings 2025"
    Input: stock name/ticker + topic.
    """
    try:
        from duckduckgo_search import DDGS
        results = DDGS().text(f"{query} stock news 2025", max_results=5)
        if not results:
            return "No news found."
        out = f"📰 NEWS — '{query}':\n\n"
        for i, r in enumerate(results, 1):
            out += f"{i}. {r.get('title','N/A')}\n"
            out += f"   🔗 {r.get('href','N/A')}\n"
            out += f"   📝 {r.get('body','N/A')}\n\n"
        return out
    except Exception as e:
        return f"Error fetching news: {e}"


@tool
def search_analyst_ratings(query: str) -> str:
    """
    Search analyst buy/sell/hold ratings and price targets via DuckDuckGo.
    Examples: "TCS analyst target price", "AAPL analyst rating 2025"
    Input: stock name/ticker.
    """
    try:
        from duckduckgo_search import DDGS
        results = DDGS().text(f"{query} analyst rating price target 2025", max_results=5)
        if not results:
            return "No analyst data found."
        out = f"🎯 ANALYST RATINGS — '{query}':\n\n"
        for i, r in enumerate(results, 1):
            out += f"{i}. {r.get('title','N/A')}\n"
            out += f"   🔗 {r.get('href','N/A')}\n"
            out += f"   📝 {r.get('body','N/A')}\n\n"
        return out
    except Exception as e:
        return f"Error fetching analyst data: {e}"


@tool
def search_sector_analysis(sector: str) -> str:
    """
    Research sector/industry trends, macro outlook, and top stocks via DuckDuckGo.
    Examples: "Indian IT sector 2025", "US semiconductor outlook", "EV industry India"
    Input: sector or industry name.
    """
    try:
        from duckduckgo_search import DDGS
        results = DDGS().text(f"{sector} sector analysis outlook 2025", max_results=5)
        if not results:
            return "No sector data found."
        out = f"🏭 SECTOR — '{sector}':\n\n"
        for i, r in enumerate(results, 1):
            out += f"{i}. {r.get('title','N/A')}\n"
            out += f"   🔗 {r.get('href','N/A')}\n"
            out += f"   📝 {r.get('body','N/A')}\n\n"
        return out
    except Exception as e:
        return f"Error in sector search: {e}"


# ─────────────────────────────────────────────────────────────────────────────
# AGENT SETUP
# ─────────────────────────────────────────────────────────────────────────────

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_react_agent
from langchain.agents.agent import AgentExecutor
from langchain import hub

SYSTEM_PROMPT = """You are StockSage, an expert AI research analyst covering both
Indian (NSE/BSE) and US (NYSE/NASDAQ) equity markets.

MARKET KNOWLEDGE:
- Indian NSE stocks append .NS  (e.g. RELIANCE.NS, TCS.NS)
- Indian BSE stocks append .BO  (e.g. RELIANCE.BO)
- US stocks use plain tickers    (e.g. AAPL, NVDA, MSFT)
- Indian indices: NIFTY50 → ^NSEI, SENSEX → ^BSESN, BANKNIFTY → ^NSEBANK
- US indices   : SP500 → ^GSPC, NASDAQ → ^IXIC, DOW → ^DJI

TOOL PRIORITY:
1. Call get_stock_quote FIRST for any stock query.
2. Call get_stock_fundamentals for valuation/financial analysis.
3. Call get_technical_indicators for chart/momentum analysis.
4. Call search_stock_news for latest developments (yfinance has no news).
5. Call compare_stocks_yf when user wants side-by-side analysis.
6. Call get_market_overview for index-level queries.

RESPONSE FORMAT:
- Label each section: [QUOTE] [FUNDAMENTAL] [TECHNICAL] [NEWS] [VERDICT]
- Use ₹ for Indian stocks, $ for US stocks.
- Always state the exchange (NSE/BSE/NYSE/NASDAQ).
- End with a brief VERDICT with Bull Case and Bear Case.
- Add: "⚠ For educational purposes only. Not financial advice."
"""

llm = ChatGoogleGenerativeAI(model=model, temperature=0.3, google_api_key=api_key)

ALL_TOOLS = [
    get_stock_quote,
    get_stock_fundamentals,
    get_technical_indicators,
    get_price_history,
    compare_stocks_yf,
    get_market_overview,
    search_stock_news,
    search_analyst_ratings,
    search_sector_analysis,
]

base_prompt = hub.pull("hwchase17/react")
agent       = create_react_agent(llm=llm, tools=ALL_TOOLS, prompt=base_prompt)
executor    = AgentExecutor(
    agent=agent, tools=ALL_TOOLS,
    verbose=True, handle_parsing_errors=True,
    max_iterations=10, max_execution_time=90,
)

# ─────────────────────────────────────────────────────────────────────────────
# INTERACTIVE Q&A
# ─────────────────────────────────────────────────────────────────────────────

BANNER = """
╔══════════════════════════════════════════════════════════════════╗
║     📊  S T O C K S A G E  v2  —  AI Research Agent             ║
║     Indian Markets (NSE/BSE) · US Markets (NYSE/NASDAQ)          ║
╚══════════════════════════════════════════════════════════════════╝

  Live Data  : yfinance  (prices · fundamentals · technicals)
  Web Search : DuckDuckGo (news · analyst views · sector trends)
  LLM Engine : Google Gemini (ReAct Agent)

  ⚠️  Educational use only — NOT financial advice

📌 Example queries:
  🇮🇳  "Analyze RELIANCE fundamentals and technicals"
  🇮🇳  "Is TCS overbought? Show RSI and MACD"
  🇮🇳  "Compare INFY, TCS, WIPRO side by side"
  🇮🇳  "India market overview today"
  🇺🇸  "NVDA technical analysis — bullish or bearish?"
  🇺🇸  "Compare AAPL vs MSFT vs GOOGL fundamentals"
  🌐  "Compare RELIANCE.NS vs AAPL"
  🌐  "Global market overview"

  Quick commands (no LLM):
    quote RELIANCE        → instant price quote
    market india          → index overview

  Commands: help | history | clear | exit
"""

HELP_TEXT = """
📖  HELP — Supported Queries
────────────────────────────────────────────────────────────────
[LIVE QUOTE]       "Quote for RELIANCE" / "TSLA current price"
[FUNDAMENTALS]     "HDFC Bank fundamentals" / "AAPL P/E EPS"
[TECHNICALS]       "TCS RSI MACD" / "Is NVDA overbought?"
[PRICE HISTORY]    "INFY 1 year returns" / "MSFT performance"
[COMPARISON]       "Compare INFY, TCS, WIPRO" / "AAPL vs MSFT"
[MARKET OVERVIEW]  "India market" / "US market overview"
[NEWS]             "Zomato news" / "Tesla earnings update"
[ANALYST RATINGS]  "TCS analyst target" / "AAPL price target"
[SECTOR]           "Indian IT sector" / "US semiconductor outlook"

📌  Indian Tickers (NSE):
    RELIANCE, TCS, INFY, HDFCBANK, ICICIBANK, WIPRO,
    TATAMOTORS, BAJFINANCE, ADANIENT, ZOMATO, IRCTC ...
    → Suffix .NS for NSE, .BO for BSE, or plain name (auto-resolved)

📌  US Tickers:
    AAPL, MSFT, NVDA, TSLA, AMZN, GOOGL, META, JPM ...

📌  Indices:
    NIFTY50, SENSEX, BANKNIFTY    ← Indian
    SP500, NASDAQ, DOW            ← US
────────────────────────────────────────────────────────────────
"""


def run_agent(question: str) -> str:
    enriched = (
        f"{SYSTEM_PROMPT}\n\n"
        f"User Question: {question}\n\n"
        "Use yfinance tools first for real data, then DuckDuckGo for news/context."
    )
    try:
        result = executor.invoke({"input": enriched})
        return result.get("output", "No response generated.")
    except Exception as e:
        return f"Agent error: {e}"


def main():
    print(BANNER)
    history = []

    while True:
        try:
            q = input("\n🔍 StockSage> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n👋 Goodbye! Invest wisely."); break

        if not q: continue
        if q.lower() in ("exit","quit","bye","q"):
            print("\n👋 Goodbye! Invest wisely."); break
        if q.lower() == "help":
            print(HELP_TEXT); continue
        if q.lower() == "history":
            [print(f"  {i+1}. {h}") for i, (h,_) in enumerate(history)] if history else print("  No history.")
            continue
        if q.lower() == "clear":
            history.clear(); print("🗑️  History cleared."); continue

        # ── Quick shortcuts bypass the LLM ───────────────────────────────────
        if q.lower().startswith("quote "):
            print(get_stock_quote.invoke(q[6:].strip())); continue
        if q.lower().startswith("market "):
            print(get_market_overview.invoke(q[7:].strip())); continue

        print(f"\n⏳ Researching '{q}'...\n{'─'*60}")
        answer = run_agent(q)
        history.append((q, answer))

        print(f"\n{'═'*60}\n📋 STOCKSAGE ANALYSIS\n{'═'*60}")
        print(answer)
        print(f"{'─'*60}")
        print("⚠️  For educational purposes only. Not financial advice.")


if __name__ == "__main__":
    main()