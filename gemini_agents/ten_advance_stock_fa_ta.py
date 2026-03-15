"""
StockSage — AI Research Agent v3
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Full Nifty Index Suite (50+ indices: Nifty 50, Bank, IT, FMCG, Auto, etc.)
✅ Real-time quotes, fundamentals, technicals via yfinance
✅ Multi-source news: DuckDuckGo + RSS feeds (Economic Times, Moneycontrol)
✅ Analyst ratings & price targets
✅ FII/DII flow proxy, sectoral momentum scan
✅ Enhanced ReAct agent with Gemini — tuned for deeper analysis
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import os
import warnings
import math
from datetime import datetime, timedelta
from dotenv import load_dotenv

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

load_dotenv()
os.environ["LANGCHAIN_TRACING_V2"] = "false"

api_key = os.getenv("GEMINI_API_KEY")
model   = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

# ─────────────────────────────────────────────────────────────────────────────
# NIFTY INDEX MASTER MAP  (name → yfinance symbol)
# ─────────────────────────────────────────────────────────────────────────────

NIFTY_INDEX_MAP = {
    # ── Broad Market ──────────────────────────────────────────────────────────
    "NIFTY50"            : "^NSEI",
    "NIFTY"              : "^NSEI",
    "SENSEX"             : "^BSESN",
    "NIFTY100"           : "^CNX100",
    "NIFTY200"           : "NIFTY200.NS",
    "NIFTY500"           : "^CNX500",
    "NIFTYMIDCAP50"      : "^NSEMDCP50",
    "NIFTYMIDCAP100"     : "^CNXMDCP100",
    "NIFTYMIDCAP150"     : "NIFTYMIDCAP150.NS",
    "NIFTYSMALLCAP50"    : "^CNXSC",
    "NIFTYSMALLCAP100"   : "^CNXSMCP100",
    "NIFTYSMALLCAP250"   : "NIFTYSMALLCAP250.NS",
    "NIFTYMICROCAP250"   : "NIFTYMICROCAP250.NS",
    "NIFTYTOTALMARKET"   : "NIFTYTOTALMARKET.NS",
    "NIFTYLARGMID250"    : "NIFTYLARGMID250.NS",
    "NIFTYMIDSELECT"     : "NIFTYMIDSELECT.NS",

    # ── Sectoral ─────────────────────────────────────────────────────────────
    "BANKNIFTY"          : "^NSEBANK",
    "NIFTYBANK"          : "^NSEBANK",
    "NIFTYIT"            : "^CNXIT",
    "NIFTYFMCG"          : "^CNXFMCG",
    "NIFTYAUTO"          : "^CNXAUTO",
    "NIFTYPHARMA"        : "^CNXPHARMA",
    "NIFTYFINSERV"       : "^CNXFINANCE",     # Nifty Financial Services
    "NIFTYFINANCE"       : "^CNXFINANCE",
    "NIFTYMETAL"         : "^CNXMETAL",
    "NIFTYREALTY"        : "^CNXREALTY",
    "NIFTYENERGY"        : "^CNXENERGY",
    "NIFTYINFRA"         : "^CNXINFRA",
    "NIFTYMEDIA"         : "^CNXMEDIA",
    "NIFTYPSUBANK"       : "^CNXPSUBANK",
    "NIFTYPSE"           : "^CNXPSE",
    "NIFTYCONSUMPTION"   : "NIFTYCONSUMPTION.NS",
    "NIFTYOILGAS"        : "NIFTYOILGAS.NS",
    "NIFTYHEALTHCARE"    : "NIFTYHEALTHCARE.NS",
    "NIFTYMFG"           : "NIFTYMFG.NS",
    "NIFTYINDIAMFG"      : "NIFTYINDIAMFG.NS",
    "NIFTYCHEMICALS"     : "NIFTYCHEMICALS.NS",

    # ── Thematic ──────────────────────────────────────────────────────────────
    "NIFTYINDIADIGITAL"  : "NIFTYINDIADIGITAL.NS",
    "NIFTYMOBILITY"      : "NIFTYMOBILITY.NS",
    "NIFTYNEWENERGY"     : "NIFTYNEWENERGY.NS",
    "NIFTYCPSE"          : "^CNXCPSE",
    "NIFTYV20"           : "NIFTYV20.NS",
    "NIFTY100LOWVOL30"   : "NIFTY100LOWVOL30.NS",
    "NIFTYALPHA50"       : "NIFTYALPHA50.NS",
    "NIFTYHIGHBETA50"    : "NIFTYHIGHBETA50.NS",
    "NIFTY100QUALITY30"  : "NIFTY100QUALITY30.NS",
    "NIFTYDIVIDEND"      : "^CNXDIVID",
    "NIFTYGROWTHSECT15"  : "NIFTYGROWTHSECT15.NS",

    # ── Fixed Income / Hybrid ─────────────────────────────────────────────────
    "NIFTY10YR"          : "^NSEFI10",        # Nifty 10 yr benchmark G-Sec (proxy)

    # ── US Indices (keep for global context) ──────────────────────────────────
    "SP500"              : "^GSPC",
    "SPX"                : "^GSPC",
    "NASDAQ"             : "^IXIC",
    "DOW"                : "^DJI",
    "RUSSELL2000"        : "^RUT",
    "VIX"                : "^VIX",
    "INDIAVIX"           : "^INDIAVIX",
}

# Human-friendly display names
NIFTY_DISPLAY = {v: k for k, v in NIFTY_INDEX_MAP.items()}

# ─────────────────────────────────────────────────────────────────────────────
# STOCK TICKER UNIVERSE
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
    "LT","LTIM","LTTS","MPHASIS","PERSISTENT","COFORGE","INDIAMART",
    "POLYCAB","DIXON","TRENT","JUBLFOOD","METROPOLIS","LALPATHLAB",
    "ASTRAL","AIAENG","GMRINFRA","CONCOR","CANBK","BANKBARODA","PNB",
    "RECLTD","PFC","NHPC","SJVN","IRFC","RVNL","RAILTEL","HAL",
    "BEL","BHEL","BPCL","IOC","HINDPETRO","GAIL","MGL","PETRONET",
    "OFSS","KPITTECH","TATAELXSI","INTELLECT","MASTEK","NIITTECH",
    "SYNGENE","AUROPHARMA","TORNTPHARM","ALKEM","BIOCON","LUPIN",
    "BALKRISIND","CEAT","MRF","APOLLOTYRE","EXIDEIND","AMARARAJA",
    "WHIRLPOOL","BLUESTAR","CROMPTON","ORIENTELEC","BAJAJELEC",
    "KALYANKJIL","SENCO","PCJEWELLER","RAJESHEXPO",
}

# ─────────────────────────────────────────────────────────────────────────────
# SECTOR GROUPS — for momentum scan
# ─────────────────────────────────────────────────────────────────────────────

SECTOR_INDICES = {
    "IT"         : "^CNXIT",
    "Bank"       : "^NSEBANK",
    "FMCG"       : "^CNXFMCG",
    "Auto"       : "^CNXAUTO",
    "Pharma"     : "^CNXPHARMA",
    "Metal"      : "^CNXMETAL",
    "Realty"     : "^CNXREALTY",
    "Energy"     : "^CNXENERGY",
    "Infra"      : "^CNXINFRA",
    "PSU Bank"   : "^CNXPSUBANK",
    "Financial"  : "^CNXFINANCE",
    "Media"      : "^CNXMEDIA",
    "Oil & Gas"  : "NIFTYOILGAS.NS",
    "Healthcare" : "NIFTYHEALTHCARE.NS",
}

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def resolve_ticker(raw: str) -> tuple:
    raw = raw.strip().upper()
    if raw in NIFTY_INDEX_MAP:
        return NIFTY_INDEX_MAP[raw], "INDEX 📊"
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
        if val is None: return "N/A"
        if math.isnan(float(val)): return "N/A"
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
    return "₹" if (".NS" in symbol or ".BO" in symbol or "^NSE" in symbol or "^CNX" in symbol or "^BSE" in symbol) else "$"


def arrow(chg): return "▲" if chg >= 0 else "▼"
def sign(chg):  return "+" if chg >= 0 else ""


# ─────────────────────────────────────────────────────────────────────────────
# TOOLS
# ─────────────────────────────────────────────────────────────────────────────

from langchain.tools import tool


# ── 1. STOCK / INDEX QUOTE ───────────────────────────────────────────────────

@tool
def get_stock_quote(ticker: str) -> str:
    """
    Real-time price quote for any Indian stock, US stock, OR Nifty index.
    Indian stocks : RELIANCE, TCS, INFY, HDFCBANK, TATAMOTORS
    Nifty indices : NIFTY50, BANKNIFTY, NIFTYIT, NIFTYFMCG, NIFTYAUTO,
                    NIFTYPHARMA, NIFTYMETAL, NIFTYREALTY, NIFTYMIDCAP100,
                    NIFTYSMALLCAP100, NIFTYPSUBANK, NIFTYFINSERV, INDIAVIX
    US stocks     : AAPL, MSFT, NVDA, TSLA
    Input: ticker symbol.
    """
    import yfinance as yf
    symbol, market = resolve_ticker(ticker)
    try:
        tk   = yf.Ticker(symbol)
        hist = tk.history(period="5d")
        if hist.empty and ".NS" in symbol:
            symbol = symbol.replace(".NS", ".BO"); market = "BSE 🇮🇳"
            tk = yf.Ticker(symbol); hist = tk.history(period="5d")
        if hist.empty:
            return f"❌ No data for '{ticker}'. Verify the symbol."

        cur  = currency_sym(symbol)
        last = hist["Close"].iloc[-1]
        prev = hist["Close"].iloc[-2] if len(hist) > 1 else last
        chg  = last - prev
        chgp = chg / prev * 100 if prev else 0
        vol  = hist["Volume"].iloc[-1]
        info = tk.fast_info
        disp = NIFTY_DISPLAY.get(symbol, symbol)

        out  = f"📊 QUOTE — {disp} [{market}]\n{'─'*52}\n"
        out += f"  Price    : {cur}{last:,.2f}  {arrow(chg)} {sign(chg)}{chg:.2f} ({sign(chgp)}{chgp:.2f}%)\n"
        out += f"  Volume   : {human_number(vol)}\n"
        out += f"  52W High : {cur}{fmt(getattr(info,'year_high',None))}\n"
        out += f"  52W Low  : {cur}{fmt(getattr(info,'year_low',None))}\n"
        out += f"  Mkt Cap  : {human_number(getattr(info,'market_cap',None))}\n"
        out += f"  Date     : {hist.index[-1].strftime('%d %b %Y')}\n"
        return out
    except Exception as e:
        return f"Error fetching quote for {symbol}: {e}"


# ── 2. INDEX ANALYSIS ────────────────────────────────────────────────────────

@tool
def get_nifty_index_analysis(index_name: str) -> str:
    """
    Deep analysis of ANY Nifty index: price, returns, technicals, and trend.
    Supported inputs (case-insensitive):
      Broad  : NIFTY50, NIFTY100, NIFTY500, NIFTYMIDCAP100, NIFTYSMALLCAP100
      Sector : BANKNIFTY, NIFTYIT, NIFTYFMCG, NIFTYAUTO, NIFTYPHARMA,
               NIFTYMETAL, NIFTYREALTY, NIFTYENERGY, NIFTYPSUBANK,
               NIFTYFINSERV, NIFTYOILGAS, NIFTYHEALTHCARE, NIFTYMEDIA
      Thematic: NIFTYCPSE, NIFTYALPHA50, NIFTYDIVIDEND, NIFTYV20
      Volatility: INDIAVIX
    Input: index name (e.g. "NIFTYIT" or "BANKNIFTY").
    """
    import yfinance as yf
    import pandas as pd
    import numpy as np

    key = index_name.strip().upper().replace(" ", "").replace("-", "")
    if key not in NIFTY_INDEX_MAP:
        # fuzzy: partial match
        matches = [k for k in NIFTY_INDEX_MAP if key in k]
        if not matches:
            all_keys = ", ".join(sorted(NIFTY_INDEX_MAP.keys()))
            return f"❌ Unknown index '{index_name}'.\nAvailable: {all_keys}"
        key = matches[0]

    symbol = NIFTY_INDEX_MAP[key]
    try:
        df = yf.Ticker(symbol).history(period="1y", interval="1d")
        if df.empty:
            return f"⚠️ No data for {key} ({symbol}). NSE may not publish intraday for this index."

        close = df["Close"]
        high  = df["High"]
        low   = df["Low"]
        now   = close.iloc[-1]
        prev  = close.iloc[-2] if len(df) > 1 else now
        chg   = now - prev
        chgp  = chg / prev * 100

        def ret(days):
            try:
                p = close.iloc[-days] if days < len(close) else close.iloc[0]
                r = (now - p) / p * 100
                return f"{sign(r)}{r:.2f}%"
            except: return "N/A"

        ytd   = df[df.index.year == datetime.now().year]["Close"]
        ytd_r = ((now - ytd.iloc[0]) / ytd.iloc[0] * 100) if not ytd.empty else 0
        ann_v = close.pct_change().dropna().std() * (252**0.5) * 100

        # RSI
        delta = close.diff()
        gain  = delta.clip(lower=0).rolling(14).mean()
        loss  = (-delta.clip(upper=0)).rolling(14).mean()
        rs    = gain / loss.replace(0, np.nan)
        rsi   = (100 - 100 / (1 + rs)).iloc[-1]

        # EMA
        ema20  = close.ewm(span=20).mean().iloc[-1]
        ema50  = close.ewm(span=50).mean().iloc[-1]
        ema200 = close.ewm(span=200).mean().iloc[-1]

        # MACD
        ema12    = close.ewm(span=12, adjust=False).mean()
        ema26    = close.ewm(span=26, adjust=False).mean()
        macd_l   = ema12 - ema26
        signal_l = macd_l.ewm(span=9, adjust=False).mean()
        hist_v   = (macd_l - signal_l).iloc[-1]
        macd_v   = macd_l.iloc[-1]

        # Bollinger
        sma20  = close.rolling(20).mean()
        std20  = close.rolling(20).std()
        bb_up  = (sma20 + 2*std20).iloc[-1]
        bb_lo  = (sma20 - 2*std20).iloc[-1]

        # Support / Resistance (20d)
        rec   = df.tail(20)
        supp  = rec["Low"].min()
        res   = rec["High"].max()

        rsi_s  = "OVERSOLD 🟢" if rsi < 30 else ("OVERBOUGHT 🔴" if rsi > 70 else "NEUTRAL ⚪")
        trend  = ("STRONG UPTREND 🟢" if now > ema50 > ema200 else
                  "STRONG DOWNTREND 🔴" if now < ema50 < ema200 else "MIXED / SIDEWAYS ⚪")
        macd_s = "BULLISH 🟢" if hist_v > 0 else "BEARISH 🔴"

        out  = f"📊 INDEX ANALYSIS — {key}  ({symbol})\n{'═'*56}\n"
        out += f"  Value      : ₹{now:,.2f}  {arrow(chg)} {sign(chg)}{chg:.2f} ({sign(chgp)}{chgp:.2f}%)\n"
        out += f"  52W High   : ₹{close.max():,.2f}\n"
        out += f"  52W Low    : ₹{close.min():,.2f}\n"
        out += f"\n  [RETURNS]\n"
        out += f"  1W  : {ret(5)}   1M  : {ret(21)}\n"
        out += f"  3M  : {ret(63)}  6M  : {ret(126)}\n"
        out += f"  YTD : {sign(ytd_r)}{ytd_r:.2f}%   1Y  : {ret(252)}\n"
        out += f"\n  [TECHNICALS]\n"
        out += f"  EMA20  : ₹{ema20:,.2f}  {'▲' if now>ema20 else '▼'}\n"
        out += f"  EMA50  : ₹{ema50:,.2f}  {'▲' if now>ema50 else '▼'}\n"
        out += f"  EMA200 : ₹{ema200:,.2f}  {'▲' if now>ema200 else '▼'}\n"
        out += f"  Trend  : {trend}\n"
        out += f"  RSI(14): {rsi:.1f}  →  {rsi_s}\n"
        out += f"  MACD   : {macd_v:.2f} | Signal: {signal_l.iloc[-1]:.2f} | Hist: {hist_v:.2f}  → {macd_s}\n"
        out += f"  BB Up  : ₹{bb_up:,.2f}  |  BB Lo: ₹{bb_lo:,.2f}\n"
        out += f"\n  [SUPPORT / RESISTANCE — 20d]\n"
        out += f"  Support    : ₹{supp:,.2f}\n"
        out += f"  Resistance : ₹{res:,.2f}\n"
        out += f"\n  [RISK]\n"
        out += f"  Ann. Vol   : {ann_v:.1f}%  ({'High' if ann_v>30 else 'Moderate' if ann_v>15 else 'Low'})\n"
        out += f"  Data as of : {df.index[-1].strftime('%d %b %Y')}\n"
        return out
    except Exception as e:
        return f"Error analysing {key}: {e}"


# ── 3. SECTORAL MOMENTUM DASHBOARD ──────────────────────────────────────────

@tool
def get_sectoral_momentum(period: str = "1M") -> str:
    """
    Live sectoral momentum scorecard — ranks all major Nifty sector indices
    by performance over a chosen period. Highlights top gainers and laggards.
    Input: period — '1W', '1M', '3M', '6M', or '1Y'  (default: '1M')
    """
    import yfinance as yf
    period_map = {"1W": 5, "1M": 21, "3M": 63, "6M": 126, "1Y": 252}
    p = period.strip().upper()
    days = period_map.get(p, 21)

    results = []
    for name, sym in SECTOR_INDICES.items():
        try:
            hist = yf.Ticker(sym).history(period="1y", interval="1d")
            if hist.empty or len(hist) < days: continue
            close = hist["Close"]
            now, past = close.iloc[-1], close.iloc[-days]
            ret = (now - past) / past * 100
            rsi_raw = close.diff().clip(lower=0).rolling(14).mean() / \
                      (-close.diff().clip(upper=0).rolling(14).mean().replace(0, float('nan')))
            rsi = float(100 - 100 / (1 + rsi_raw.iloc[-1]))
            results.append((name, sym, now, ret, rsi))
        except: pass

    if not results:
        return "⚠️ Could not fetch sectoral data."

    results.sort(key=lambda x: x[3], reverse=True)
    out  = f"🏭 SECTORAL MOMENTUM — {p} Period\n{'═'*56}\n"
    out += f"  {'Sector':<16} {'Price':>10} {'Return':>9} {'RSI':>7}  Signal\n"
    out += f"  {'─'*14} {'─'*10} {'─'*9} {'─'*7}  {'─'*10}\n"
    for name, sym, price, ret, rsi in results:
        rsi_s = "Overbought🔴" if rsi > 70 else ("Oversold🟢" if rsi < 30 else "Neutral⚪")
        bar   = "🟩" * min(int(abs(ret)//3), 5) if ret > 0 else "🟥" * min(int(abs(ret)//3), 5)
        out  += f"  {name:<16} {price:>10,.0f} {sign(ret)}{ret:>7.2f}% {rsi:>7.1f}  {rsi_s}\n"
    out += f"\n  Top Gainer : {results[0][0]}  ({sign(results[0][3])}{results[0][3]:.2f}%)\n"
    out += f"  Top Laggard: {results[-1][0]}  ({sign(results[-1][3])}{results[-1][3]:.2f}%)\n"
    out += f"\n  Data: yfinance | {datetime.now().strftime('%d %b %Y %H:%M')}\n"
    return out


# ── 4. FULL NIFTY INDEX DASHBOARD ────────────────────────────────────────────

@tool
def get_nifty_dashboard(category: str = "all") -> str:
    """
    Live dashboard of ALL major Nifty indices grouped by category.
    Categories:
      'broad'     → Nifty 50, 100, 200, 500, Midcap, Smallcap
      'sector'    → IT, Bank, FMCG, Auto, Pharma, Metal, Realty, etc.
      'thematic'  → CPSE, Alpha, Dividend, V20, Quality, etc.
      'all'       → Everything (may take ~30s)
    Input: category string.
    """
    import yfinance as yf
    cat = category.strip().lower()

    groups = {
        "broad": {
            "Nifty 50"         : "^NSEI",
            "Nifty 100"        : "^CNX100",
            "Nifty 500"        : "^CNX500",
            "Nifty Midcap 50"  : "^NSEMDCP50",
            "Nifty Midcap 100" : "^CNXMDCP100",
            "Nifty Smallcap 50": "^CNXSC",
            "Nifty Smallcap 100":"^CNXSMCP100",
            "Sensex"           : "^BSESN",
            "India VIX"        : "^INDIAVIX",
        },
        "sector": {
            "Bank Nifty"       : "^NSEBANK",
            "Nifty IT"         : "^CNXIT",
            "Nifty FMCG"       : "^CNXFMCG",
            "Nifty Auto"       : "^CNXAUTO",
            "Nifty Pharma"     : "^CNXPHARMA",
            "Nifty Metal"      : "^CNXMETAL",
            "Nifty Realty"     : "^CNXREALTY",
            "Nifty Energy"     : "^CNXENERGY",
            "Nifty Infra"      : "^CNXINFRA",
            "Nifty PSU Bank"   : "^CNXPSUBANK",
            "Nifty Financial"  : "^CNXFINANCE",
            "Nifty Media"      : "^CNXMEDIA",
            "Nifty PSE"        : "^CNXPSE",
            "Nifty Oil & Gas"  : "NIFTYOILGAS.NS",
            "Nifty Healthcare" : "NIFTYHEALTHCARE.NS",
        },
        "thematic": {
            "Nifty CPSE"       : "^CNXCPSE",
            "Nifty Dividend"   : "^CNXDIVID",
            "Nifty Alpha 50"   : "NIFTYALPHA50.NS",
            "Nifty HiBeta 50"  : "NIFTYHIGHBETA50.NS",
            "Nifty Value 20"   : "NIFTYV20.NS",
            "Nifty Quality 30" : "NIFTY100QUALITY30.NS",
            "Nifty LowVol 30"  : "NIFTY100LOWVOL30.NS",
        },
    }

    if cat == "all":
        selected = {**groups["broad"], **groups["sector"], **groups["thematic"]}
        header   = "ALL NIFTY INDICES"
    elif cat in groups:
        selected = groups[cat]
        header   = f"NIFTY — {cat.upper()}"
    else:
        selected = groups["broad"]
        header   = "NIFTY BROAD MARKET"

    out = f"🇮🇳 {header}\n{'═'*60}\n"
    out += f"  {'Index':<24} {'Value':>10} {'Change':>10} {'%Chg':>8}\n"
    out += f"  {'─'*22} {'─'*10} {'─'*10} {'─'*8}\n"
    for name, sym in selected.items():
        try:
            hist = yf.Ticker(sym).history(period="5d")
            if hist.empty:
                out += f"  {name:<24} {'N/A':>10}\n"; continue
            last = hist["Close"].iloc[-1]
            prev = hist["Close"].iloc[-2] if len(hist) > 1 else last
            ch   = last - prev
            chp  = ch / prev * 100 if prev else 0
            out += f"  {name:<24} {last:>10,.2f} {sign(ch)}{ch:>9.2f} {sign(chp)}{chp:>6.2f}%  {arrow(ch)}\n"
        except:
            out += f"  {name:<24} {'Error':>10}\n"
    out += f"\n  {datetime.now().strftime('%d %b %Y %H:%M')} | Source: yfinance\n"
    return out


# ── 5. STOCK FUNDAMENTALS ────────────────────────────────────────────────────

@tool
def get_stock_fundamentals(ticker: str) -> str:
    """
    Detailed fundamental analysis: P/E, EPS, revenue, margins, ROE, debt ratios,
    dividends, book value. Works for any Indian or US stock.
    Input: ticker (RELIANCE, TCS, AAPL, NVDA …)
    """
    import yfinance as yf
    symbol, market = resolve_ticker(ticker)
    try:
        info = yf.Ticker(symbol).info
        if not info.get("regularMarketPrice") and ".NS" in symbol:
            symbol = symbol.replace(".NS", ".BO")
            info   = yf.Ticker(symbol).info
        cur = currency_sym(symbol)
        out  = f"📊 FUNDAMENTALS — {symbol} [{market}]\n{'═'*52}\n"
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


# ── 6. TECHNICAL INDICATORS ──────────────────────────────────────────────────

@tool
def get_technical_indicators(ticker: str) -> str:
    """
    Full technical analysis: RSI, MACD, EMA 20/50/200, Bollinger Bands, ATR,
    Stochastic oscillator, volume analysis, support & resistance.
    Works for Indian stocks, Nifty indices, and US stocks.
    Input: ticker or index name (RELIANCE, BANKNIFTY, AAPL, NVDA …)
    """
    import yfinance as yf
    import pandas as pd
    import numpy as np
    symbol, market = resolve_ticker(ticker)
    try:
        df = yf.Ticker(symbol).history(period="6mo", interval="1d")
        if df.empty and ".NS" in symbol:
            symbol = symbol.replace(".NS", ".BO"); market = "BSE 🇮🇳"
            df = yf.Ticker(symbol).history(period="6mo", interval="1d")
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

        # Stochastic %K %D
        lo14 = low.rolling(14).min()
        hi14 = high.rolling(14).max()
        pctK = ((close - lo14) / (hi14 - lo14) * 100).rolling(3).mean()
        pctD = pctK.rolling(3).mean()
        stoch_k, stoch_d = pctK.iloc[-1], pctD.iloc[-1]

        # MACD(12,26,9)
        ema12    = close.ewm(span=12, adjust=False).mean()
        ema26    = close.ewm(span=26, adjust=False).mean()
        macd_l   = ema12 - ema26
        signal_l = macd_l.ewm(span=9, adjust=False).mean()
        hist_l   = macd_l - signal_l
        macd_v, sig_v, hist_v = macd_l.iloc[-1], signal_l.iloc[-1], hist_l.iloc[-1]

        # EMAs
        ema9   = close.ewm(span=9).mean().iloc[-1]
        ema20  = close.ewm(span=20).mean().iloc[-1]
        ema50  = close.ewm(span=50).mean().iloc[-1]
        ema200 = close.ewm(span=200).mean().iloc[-1]

        # Bollinger Bands(20,2)
        sma20  = close.rolling(20).mean()
        std20  = close.rolling(20).std()
        bb_up  = (sma20 + 2*std20).iloc[-1]
        bb_lo  = (sma20 - 2*std20).iloc[-1]
        bb_mid = sma20.iloc[-1]
        bb_bw  = (bb_up - bb_lo) / bb_mid * 100  # bandwidth %

        # ATR(14)
        tr    = pd.concat([high-low, (high-close.shift()).abs(), (low-close.shift()).abs()], axis=1).max(axis=1)
        atr   = tr.rolling(14).mean().iloc[-1]
        atr_p = atr / close.iloc[-1] * 100  # ATR as % of price

        # Volume analysis
        avg_vol  = volume.rolling(20).mean().iloc[-1]
        last_vol = volume.iloc[-1]
        vol_tr   = "HIGH 🔥" if last_vol > avg_vol*1.5 else ("LOW 📉" if last_vol < avg_vol*0.5 else "NORMAL ⚪")
        obv      = (volume * close.diff().apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0))).cumsum()
        obv_trend = "Rising 🟢" if obv.iloc[-1] > obv.iloc[-5] else "Falling 🔴"

        # Support / Resistance
        recent     = df.tail(20)
        support    = recent["Low"].min()
        resistance = recent["High"].max()

        price    = close.iloc[-1]
        rsi_sig  = "OVERSOLD 🟢" if rsi < 30 else ("OVERBOUGHT 🔴" if rsi > 70 else "NEUTRAL ⚪")
        stoch_s  = "OVERSOLD 🟢" if stoch_k < 20 else ("OVERBOUGHT 🔴" if stoch_k > 80 else "NEUTRAL ⚪")
        macd_sig = "BULLISH 🟢 (histogram positive)" if hist_v > 0 else "BEARISH 🔴 (histogram negative)"
        trend    = ("STRONG UPTREND 🟢" if price > ema50 > ema200 else
                    "STRONG DOWNTREND 🔴" if price < ema50 < ema200 else "MIXED / SIDEWAYS ⚪")
        bb_sig   = ("Near UPPER band 🔴 — overbought" if price > bb_up*0.98 else
                    "Near LOWER band 🟢 — oversold"   if price < bb_lo*1.02 else "Inside Bands ⚪")

        # Overall signal score (0-5)
        bull = sum([rsi < 50, hist_v > 0, price > ema50, price > ema200, stoch_k < 50])
        signal_txt = "STRONG BUY 🟢🟢" if bull >= 4 else ("BUY 🟢" if bull == 3 else ("SELL 🔴" if bull <= 1 else "NEUTRAL ⚪"))

        out  = f"📈 TECHNICALS — {symbol} [{market}]\n{'═'*56}\n"
        out += f"  Current Price  : {cur}{price:,.2f}\n"
        out += f"  Overall Signal : {signal_txt}  (score {bull}/5)\n"
        out += f"\n  [TREND & EMAs]\n"
        out += f"  EMA 9    : {cur}{ema9:,.2f}  {'▲' if price>ema9 else '▼'}\n"
        out += f"  EMA 20   : {cur}{ema20:,.2f}  {'▲' if price>ema20 else '▼'}\n"
        out += f"  EMA 50   : {cur}{ema50:,.2f}  {'▲' if price>ema50 else '▼'}\n"
        out += f"  EMA 200  : {cur}{ema200:,.2f}  {'▲' if price>ema200 else '▼'}\n"
        out += f"  Trend    : {trend}\n"
        out += f"\n  [MOMENTUM]\n"
        out += f"  RSI(14)  : {rsi:.1f}  →  {rsi_sig}\n"
        out += f"  Stoch %K : {stoch_k:.1f}  %D: {stoch_d:.1f}  → {stoch_s}\n"
        out += f"  MACD     : {macd_v:.3f} | Signal: {sig_v:.3f} | Hist: {hist_v:.3f}\n"
        out += f"  MACD Sig : {macd_sig}\n"
        out += f"\n  [VOLATILITY]\n"
        out += f"  BB Upper : {cur}{bb_up:,.2f}\n"
        out += f"  BB Mid   : {cur}{bb_mid:,.2f}\n"
        out += f"  BB Lower : {cur}{bb_lo:,.2f}\n"
        out += f"  BB BW    : {bb_bw:.1f}% ({'Wide — high vol' if bb_bw>10 else 'Narrow — low vol'})\n"
        out += f"  BB Signal: {bb_sig}\n"
        out += f"  ATR(14)  : {cur}{atr:,.2f}  ({atr_p:.1f}% of price)\n"
        out += f"\n  [VOLUME & OBV]\n"
        out += f"  Last Vol : {human_number(last_vol)}\n"
        out += f"  Avg(20d) : {human_number(avg_vol)}\n"
        out += f"  Vol Trend: {vol_tr}\n"
        out += f"  OBV Trend: {obv_trend}\n"
        out += f"\n  [SUPPORT / RESISTANCE — 20d pivot]\n"
        out += f"  Support  : {cur}{support:,.2f}\n"
        out += f"  Resist.  : {cur}{resistance:,.2f}\n"
        return out
    except Exception as e:
        return f"Error computing technicals for {symbol}: {e}"


# ── 7. PRICE HISTORY ─────────────────────────────────────────────────────────

@tool
def get_price_history(ticker: str) -> str:
    """
    Multi-period return analysis and risk metrics for any stock or index.
    Input: ticker or index name.
    """
    import yfinance as yf
    import numpy as np
    symbol, market = resolve_ticker(ticker)
    try:
        df = yf.Ticker(symbol).history(period="1y", interval="1d")
        if df.empty and ".NS" in symbol:
            symbol = symbol.replace(".NS", ".BO")
            df = yf.Ticker(symbol).history(period="1y", interval="1d")
        if df.empty:
            return f"No price history for '{ticker}'."
        cur   = currency_sym(symbol)
        close = df["Close"]
        now   = close.iloc[-1]

        def ret(days):
            try:
                p = close.iloc[-days] if days < len(close) else close.iloc[0]
                r = (now - p) / p * 100
                return f"{sign(r)}{r:.2f}%"
            except: return "N/A"

        ytd_s = df[df.index.year == datetime.now().year]["Close"]
        ytd_r = ((now - ytd_s.iloc[0]) / ytd_s.iloc[0] * 100) if not ytd_s.empty else 0
        ann_v = close.pct_change().dropna().std() * (252**0.5) * 100
        rets  = close.pct_change().dropna()
        sharp = (rets.mean() / rets.std()) * (252**0.5) if rets.std() > 0 else 0
        dd    = (close / close.cummax() - 1).min() * 100  # max drawdown

        out  = f"📅 PERFORMANCE — {symbol} [{market}]\n{'═'*52}\n"
        out += f"  Current  : {cur}{now:,.2f}\n\n"
        out += f"  [RETURNS]\n"
        out += f"  1 Week   : {ret(5)}\n"
        out += f"  1 Month  : {ret(21)}\n"
        out += f"  3 Month  : {ret(63)}\n"
        out += f"  6 Month  : {ret(126)}\n"
        out += f"  YTD      : {sign(ytd_r)}{ytd_r:.2f}%\n"
        out += f"  1 Year   : {ret(252)}\n"
        out += f"\n  [1-YEAR RANGE]\n"
        out += f"  High     : {cur}{close.max():,.2f}\n"
        out += f"  Low      : {cur}{close.min():,.2f}\n"
        out += f"  Avg      : {cur}{close.mean():,.2f}\n"
        out += f"\n  [RISK METRICS]\n"
        out += f"  Ann. Vol : {ann_v:.1f}%  ({'High' if ann_v>40 else 'Moderate' if ann_v>20 else 'Low'})\n"
        out += f"  Sharpe   : {sharp:.2f}  ({'Good' if sharp>1 else 'Average' if sharp>0 else 'Poor'})\n"
        out += f"  Max DD   : {dd:.2f}%\n"
        return out
    except Exception as e:
        return f"Error fetching history for {symbol}: {e}"


# ── 8. COMPARE STOCKS ────────────────────────────────────────────────────────

@tool
def compare_stocks_yf(tickers: str) -> str:
    """
    Side-by-side fundamental comparison of 2-4 stocks (Indian + US mixed).
    Examples: "RELIANCE, TCS, INFY" | "AAPL, MSFT, GOOGL" | "RELIANCE.NS, AAPL"
    Input: comma-separated tickers (or 'A vs B').
    """
    import yfinance as yf
    raw_list = [t.strip() for t in tickers.replace(" vs ", ",").replace(" VS ", ",").split(",") if t.strip()]
    if len(raw_list) < 2:
        return "Provide at least 2 tickers, e.g. 'RELIANCE, TCS, INFY'"

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
                "peg"    : info.get("pegRatio"),
                "evebitda": info.get("enterpriseToEbitda"),
            })
        except Exception as e:
            rows.append({"sym": symbol, "mkt": market, "cur": "$", "error": str(e)})

    metrics = [
        ("Price",       lambda r: f"{r['cur']}{fmt(r.get('price'))}"),
        ("Mkt Cap",     lambda r: human_number(r.get("mktcap"))),
        ("P/E (TTM)",   lambda r: fmt(r.get("pe"))),
        ("P/E (Fwd)",   lambda r: fmt(r.get("fpe"))),
        ("PEG",         lambda r: fmt(r.get("peg"))),
        ("P/B",         lambda r: fmt(r.get("pb"))),
        ("EV/EBITDA",   lambda r: fmt(r.get("evebitda"))),
        ("EPS (TTM)",   lambda r: f"{r['cur']}{fmt(r.get('eps'))}"),
        ("Revenue",     lambda r: human_number(r.get("rev"))),
        ("Net Margin",  lambda r: f"{fmt((r.get('margin') or 0)*100)}%"),
        ("ROE",         lambda r: f"{fmt((r.get('roe') or 0)*100)}%"),
        ("Debt/Equity", lambda r: fmt(r.get("de"))),
        ("Div Yield",   lambda r: f"{fmt((r.get('div') or 0)*100)}%"),
        ("52W High",    lambda r: f"{r['cur']}{fmt(r.get('52wh'))}"),
        ("52W Low",     lambda r: f"{r['cur']}{fmt(r.get('52wl'))}"),
    ]

    out  = f"⚖️  COMPARISON — {' | '.join(r['sym'] for r in rows)}\n{'═'*64}\n"
    out += f"  {'Metric':<14}" + "".join(f"{r['sym']:<18}" for r in rows) + "\n"
    out += f"  {'─'*14}" + ("─"*18)*len(rows) + "\n"
    for label, fn in metrics:
        line = f"  {label:<14}"
        for r in rows:
            if "error" in r: line += f"{'ERR':<18}"
            else:
                try:    line += f"{fn(r):<18}"
                except: line += f"{'N/A':<18}"
        out += line + "\n"
    out += f"\n  Markets: {', '.join(r['sym']+'('+r['mkt']+')' for r in rows if 'error' not in r)}\n"
    return out


# ── 9. MARKET OVERVIEW ───────────────────────────────────────────────────────

@tool
def get_market_overview(market: str) -> str:
    """
    Live overview of major market indices.
    Inputs: india, nse, us, usa, nasdaq, global, vix
    """
    import yfinance as yf
    INDICES = {
        "india" : [("^NSEI","Nifty 50"),("^BSESN","Sensex"),("^NSEBANK","Bank Nifty"),
                   ("^CNXIT","Nifty IT"),("^CNXAUTO","Nifty Auto"),("^CNXFMCG","Nifty FMCG"),
                   ("^CNXPHARMA","Nifty Pharma"),("^INDIAVIX","India VIX")],
        "nse"   : [("^NSEI","Nifty 50"),("^BSESN","Sensex"),("^NSEBANK","Bank Nifty"),
                   ("^CNXIT","Nifty IT"),("^CNXAUTO","Nifty Auto"),("^CNXFMCG","Nifty FMCG"),
                   ("^CNXPHARMA","Nifty Pharma"),("^INDIAVIX","India VIX")],
        "us"    : [("^GSPC","S&P 500"),("^IXIC","NASDAQ"),("^DJI","Dow Jones"),
                   ("^RUT","Russell 2000"),("^VIX","CBOE VIX")],
        "usa"   : [("^GSPC","S&P 500"),("^IXIC","NASDAQ"),("^DJI","Dow Jones"),
                   ("^RUT","Russell 2000"),("^VIX","CBOE VIX")],
        "global": [("^NSEI","Nifty 50"),("^BSESN","Sensex"),("^GSPC","S&P 500"),
                   ("^IXIC","NASDAQ"),("^DJI","Dow Jones"),("^INDIAVIX","India VIX"),("^VIX","US VIX")],
        "vix"   : [("^INDIAVIX","India VIX"),("^VIX","CBOE VIX")],
    }
    key   = market.lower().strip()
    pairs = INDICES.get(key, INDICES["global"])
    out   = f"🌐 MARKET OVERVIEW — {market.upper()}\n{'═'*52}\n"
    out += f"  {'Index':<24} {'Value':>10} {'Chg':>10} {'%Chg':>8}\n"
    out += f"  {'─'*22} {'─'*10} {'─'*10} {'─'*8}\n"
    for sym, name in pairs:
        try:
            hist = yf.Ticker(sym).history(period="5d")
            if hist.empty:
                out += f"  {name:<24} {'N/A':>10}\n"; continue
            last = hist["Close"].iloc[-1]
            prev = hist["Close"].iloc[-2] if len(hist) > 1 else last
            ch   = last - prev
            chp  = ch / prev * 100 if prev else 0
            out += f"  {name:<24} {last:>10,.2f} {sign(ch)}{ch:>9.2f} {sign(chp)}{chp:>6.2f}%  {arrow(ch)}\n"
        except:
            out += f"  {name:<24} {'Error':>10}\n"
    out += f"\n  {datetime.now().strftime('%d %b %Y %H:%M')} | Source: yfinance\n"
    return out


# ── 10. NEWS — Multi-source ──────────────────────────────────────────────────

@tool
def search_stock_news(query: str) -> str:
    """
    Search latest stock/market news via DuckDuckGo + Economic Times RSS.
    Use for earnings, corporate events, macro news, regulatory updates.
    Examples: "RELIANCE news today", "Nifty IT sector outlook 2025",
              "RBI rate decision impact markets", "TCS Q4 results"
    Input: query string.
    """
    try:
        from duckduckgo_search import DDGS
        import urllib.request
        import xml.etree.ElementTree as ET

        results_ddg = DDGS().text(f"{query} India stock market 2025", max_results=5)
        out = f"📰 LATEST NEWS — '{query}'\n{'═'*56}\n\n"

        if results_ddg:
            out += "🔎 [DuckDuckGo Web Results]\n"
            for i, r in enumerate(results_ddg, 1):
                out += f"  {i}. {r.get('title','N/A')}\n"
                out += f"     🔗 {r.get('href','N/A')}\n"
                out += f"     📝 {r.get('body','N/A')[:200]}\n\n"

        # Economic Times RSS
        rss_feeds = [
            ("Economic Times Markets", "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms"),
            ("Moneycontrol Top News",  "https://www.moneycontrol.com/rss/latestnews.xml"),
        ]
        for feed_name, url in rss_feeds:
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=5) as resp:
                    tree = ET.parse(resp)
                root = tree.getroot()
                items = root.findall(".//item")[:3]
                if items:
                    out += f"\n📡 [{feed_name} — RSS]\n"
                    for item in items:
                        title = (item.findtext("title") or "").strip()
                        link  = (item.findtext("link")  or "").strip()
                        desc  = (item.findtext("description") or "")[:180].strip()
                        if query.split()[0].lower() in title.lower() or True:  # always show top 3
                            out += f"  • {title}\n    🔗 {link}\n    📝 {desc}\n\n"
            except: pass

        return out if len(out) > 200 else f"No news found for '{query}'."
    except Exception as e:
        return f"Error fetching news: {e}"


# ── 11. ANALYST RATINGS ──────────────────────────────────────────────────────

@tool
def search_analyst_ratings(query: str) -> str:
    """
    Search analyst buy/sell/hold ratings and price targets via DuckDuckGo.
    Examples: "TCS analyst target price 2025", "AAPL Wall Street consensus"
    Input: stock name or ticker.
    """
    try:
        from duckduckgo_search import DDGS
        results = DDGS().text(f"{query} analyst rating price target 2025 buy sell hold", max_results=6)
        if not results:
            return "No analyst data found."
        out = f"🎯 ANALYST RATINGS — '{query}'\n{'═'*52}\n\n"
        for i, r in enumerate(results, 1):
            out += f"  {i}. {r.get('title','N/A')}\n"
            out += f"     🔗 {r.get('href','N/A')}\n"
            out += f"     📝 {r.get('body','N/A')[:250]}\n\n"
        return out
    except Exception as e:
        return f"Error fetching analyst data: {e}"


# ── 12. SECTOR RESEARCH ──────────────────────────────────────────────────────

@tool
def search_sector_analysis(sector: str) -> str:
    """
    Deep sector/industry research via DuckDuckGo.
    Examples: "Indian IT sector H2 2025", "EV industry India", "PSU banks outlook"
    Input: sector or industry name.
    """
    try:
        from duckduckgo_search import DDGS
        results = DDGS().text(f"{sector} sector India analysis outlook 2025", max_results=6)
        if not results:
            return "No sector data found."
        out = f"🏭 SECTOR RESEARCH — '{sector}'\n{'═'*52}\n\n"
        for i, r in enumerate(results, 1):
            out += f"  {i}. {r.get('title','N/A')}\n"
            out += f"     🔗 {r.get('href','N/A')}\n"
            out += f"     📝 {r.get('body','N/A')[:250]}\n\n"
        return out
    except Exception as e:
        return f"Error in sector search: {e}"


# ── 13. MACRO / ECONOMY NEWS ─────────────────────────────────────────────────

@tool
def search_macro_news(topic: str) -> str:
    """
    Search macro-economic news: RBI policy, inflation, FII/DII flows, budget,
    USD/INR, crude oil, global events impacting Indian markets.
    Examples: "RBI monetary policy 2025", "FII DII flows India June 2025",
              "India inflation CPI", "crude oil impact Indian market"
    Input: macro topic.
    """
    try:
        from duckduckgo_search import DDGS
        results = DDGS().text(f"{topic} India economy 2025", max_results=6)
        if not results:
            return "No macro data found."
        out = f"🌏 MACRO NEWS — '{topic}'\n{'═'*52}\n\n"
        for i, r in enumerate(results, 1):
            out += f"  {i}. {r.get('title','N/A')}\n"
            out += f"     🔗 {r.get('href','N/A')}\n"
            out += f"     📝 {r.get('body','N/A')[:250]}\n\n"
        return out
    except Exception as e:
        return f"Error in macro search: {e}"


# ── 14. IPO / CORPORATE ACTIONS ──────────────────────────────────────────────

@tool
def search_ipo_and_corporate_actions(query: str) -> str:
    """
    Search IPO news, upcoming listings, dividends, bonus, stock splits,
    rights issues, buybacks, and other corporate actions in India.
    Examples: "upcoming IPO India 2025", "TCS buyback", "Infosys dividend 2025"
    Input: query string.
    """
    try:
        from duckduckgo_search import DDGS
        results = DDGS().text(f"{query} NSE BSE India 2025", max_results=6)
        if not results:
            return "No data found."
        out = f"🏢 CORPORATE ACTIONS — '{query}'\n{'═'*52}\n\n"
        for i, r in enumerate(results, 1):
            out += f"  {i}. {r.get('title','N/A')}\n"
            out += f"     🔗 {r.get('href','N/A')}\n"
            out += f"     📝 {r.get('body','N/A')[:250]}\n\n"
        return out
    except Exception as e:
        return f"Error fetching IPO/corporate actions: {e}"


# ─────────────────────────────────────────────────────────────────────────────
# AGENT SETUP
# ─────────────────────────────────────────────────────────────────────────────

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_react_agent
from langchain.agents.agent import AgentExecutor
from langchain import hub

SYSTEM_PROMPT = """You are StockSage v3, an expert AI equity research analyst covering
Indian (NSE/BSE) and US (NYSE/NASDAQ) markets with deep specialisation in
Nifty indices and Indian macro-economics.

══════════════════════════════════════════════════════════════
MARKET KNOWLEDGE
══════════════════════════════════════════════════════════════
Indian NSE stocks     : append .NS  (e.g. RELIANCE.NS, TCS.NS)
Indian BSE stocks     : append .BO  (e.g. RELIANCE.BO)
US stocks             : plain ticker (AAPL, NVDA, MSFT)
Nifty indices         : NIFTY50, BANKNIFTY, NIFTYIT, NIFTYFMCG, NIFTYAUTO,
                        NIFTYPHARMA, NIFTYMETAL, NIFTYREALTY, NIFTYENERGY,
                        NIFTYPSUBANK, NIFTYFINSERV, NIFTYMIDCAP100, NIFTYSMALLCAP100,
                        NIFTYCPSE, NIFTYALPHA50, NIFTYHEALTHCARE, NIFTYOILGAS,
                        INDIAVIX … (50+ indices available)
US indices            : SP500, NASDAQ, DOW, VIX

══════════════════════════════════════════════════════════════
TOOL PRIORITY & USAGE
══════════════════════════════════════════════════════════════
1. For any STOCK query          → get_stock_quote FIRST
2. For any INDEX query          → get_nifty_index_analysis
3. For full market snapshot     → get_nifty_dashboard (category: broad/sector/all)
4. For sector momentum          → get_sectoral_momentum
5. For valuation/financials     → get_stock_fundamentals
6. For chart/momentum analysis  → get_technical_indicators
7. For multi-stock comparison   → compare_stocks_yf
8. For latest news & events     → search_stock_news + search_macro_news
9. For analyst targets          → search_analyst_ratings
10. For IPO/corporate actions   → search_ipo_and_corporate_actions
11. For sector deep dive        → search_sector_analysis

Always call AT LEAST 2 tools for any substantive question.
For index queries, call get_nifty_index_analysis + search_stock_news.
For stock queries, call get_stock_quote + get_stock_fundamentals + get_technical_indicators + search_stock_news.

══════════════════════════════════════════════════════════════
RESPONSE STRUCTURE
══════════════════════════════════════════════════════════════
Label each section clearly:
[QUOTE/INDEX]  [FUNDAMENTAL]  [TECHNICAL]  [NEWS]  [MACRO]  [VERDICT]

• Use ₹ for Indian stocks/indices, $ for US.
• Always state the exchange (NSE / BSE / NYSE / NASDAQ).
• Cite specific numbers (EMA values, RSI, PE ratios).
• For indices: interpret India VIX level (< 15 calm, 15-20 moderate, > 20 elevated fear).
• END with VERDICT block:
    📈 Bull Case: <3 bullet reasons>
    📉 Bear Case: <3 bullet reasons>
    🎯 Key Levels: Support ₹X | Resistance ₹Y | Target ₹Z
• Always append: "⚠ Educational purposes only. Not financial advice."

══════════════════════════════════════════════════════════════
ANALYSIS FRAMEWORK
══════════════════════════════════════════════════════════════
• Blend fundamental + technical + news catalysts.
• Compare index PE vs historical average (Nifty 50 avg PE ~20-22x).
• Flag if India VIX > 20 as caution signal.
• For sectoral queries: mention FII vs DII flows context if available.
• For individual stocks: check if price is above/below 200 EMA as primary trend filter.
"""

llm = ChatGoogleGenerativeAI(model=model, temperature=0.2, google_api_key=api_key)

ALL_TOOLS = [
    get_stock_quote,
    get_nifty_index_analysis,
    get_nifty_dashboard,
    get_sectoral_momentum,
    get_stock_fundamentals,
    get_technical_indicators,
    get_price_history,
    compare_stocks_yf,
    get_market_overview,
    search_stock_news,
    search_macro_news,
    search_analyst_ratings,
    search_sector_analysis,
    search_ipo_and_corporate_actions,
]

base_prompt = hub.pull("hwchase17/react")
agent       = create_react_agent(llm=llm, tools=ALL_TOOLS, prompt=base_prompt)
executor    = AgentExecutor(
    agent=agent, tools=ALL_TOOLS,
    verbose=True, handle_parsing_errors=True,
    max_iterations=12, max_execution_time=120,
)


# ─────────────────────────────────────────────────────────────────────────────
# INTERACTIVE SHELL
# ─────────────────────────────────────────────────────────────────────────────

BANNER = """
╔══════════════════════════════════════════════════════════════════════╗
║   📊  S T O C K S A G E  v3  —  AI Research Agent                   ║
║   Indian (NSE/BSE/50+ Nifty Indices) · US (NYSE/NASDAQ)             ║
╚══════════════════════════════════════════════════════════════════════╝

  Live Data   : yfinance  (prices · fundamentals · technicals · indices)
  Web Search  : DuckDuckGo + ET/Moneycontrol RSS  (news · analyst views)
  Indices     : 50+ Nifty indices (Broad · Sector · Thematic)
  LLM Engine  : Google Gemini (ReAct Agent, enhanced prompting)

  ⚠️  Educational use only — NOT financial advice

📌 Example queries:
  🇮🇳  "Analyse RELIANCE fundamentals and technicals"
  🇮🇳  "Nifty IT index analysis — bullish or bearish?"
  🇮🇳  "Show me Nifty sector dashboard"
  🇮🇳  "Which Nifty sectors are outperforming this month?"
  🇮🇳  "Compare INFY, TCS, WIPRO side by side"
  🇮🇳  "Is Bank Nifty overbought? RSI and MACD"
  🇮🇳  "India VIX analysis — fear or greed?"
  🇮🇳  "Upcoming IPOs and corporate actions India"
  🇺🇸  "NVDA technical analysis"
  🌐  "Global market overview"

  ⚡ Quick shortcuts (no LLM):
    quote RELIANCE         → instant quote
    market india           → market overview
    dashboard sector       → Nifty sector dashboard
    momentum 1M            → sectoral momentum (1M)
    index BANKNIFTY        → Nifty index deep analysis

  Commands: help | history | clear | exit
"""

HELP_TEXT = """
📖  HELP — StockSage v3
────────────────────────────────────────────────────────────────────
[QUOTE]          "Quote for RELIANCE" / "TSLA current price"
[INDEX]          "Nifty IT analysis" / "Bank Nifty RSI MACD"
[DASHBOARD]      "Nifty sector dashboard" / "All Nifty indices today"
[MOMENTUM]       "Which sectors are outperforming this month?"
[FUNDAMENTALS]   "HDFC Bank fundamentals" / "AAPL PE EPS"
[TECHNICALS]     "TCS RSI MACD stochastic" / "Is NVDA overbought?"
[PERFORMANCE]    "INFY 1 year returns" / "Nifty 50 YTD performance"
[COMPARISON]     "Compare INFY, TCS, WIPRO" / "AAPL vs MSFT"
[NEWS]           "Zomato news today" / "Nifty market latest news"
[MACRO]          "RBI rate decision impact" / "FII flows India"
[ANALYST]        "TCS analyst target" / "AAPL price target"
[SECTOR]         "Indian IT sector outlook" / "PSU banks 2025"
[IPO]            "Upcoming IPO India 2025" / "TCS buyback"

📌  Nifty Indices Supported:
    Broad   : NIFTY50, NIFTY100, NIFTY500, NIFTYMIDCAP100, NIFTYSMALLCAP100
    Sector  : BANKNIFTY, NIFTYIT, NIFTYFMCG, NIFTYAUTO, NIFTYPHARMA,
              NIFTYMETAL, NIFTYREALTY, NIFTYENERGY, NIFTYPSUBANK,
              NIFTYFINSERV, NIFTYOILGAS, NIFTYHEALTHCARE, NIFTYMEDIA
    Thematic: NIFTYCPSE, NIFTYALPHA50, NIFTYDIVIDEND, NIFTYV20
    Volatility: INDIAVIX

📌  Quick Commands:
    quote <TICKER>     → real-time price
    market india/us    → index overview
    dashboard broad    → broad market indices
    dashboard sector   → all sector indices
    momentum 1M        → sector momentum table
    index <NAME>       → deep index analysis
────────────────────────────────────────────────────────────────────
"""


def run_agent(question: str) -> str:
    enriched = (
        f"{SYSTEM_PROMPT}\n\n"
        f"User Question: {question}\n\n"
        "Instructions:\n"
        "1. Use yfinance tools first for real data.\n"
        "2. Use DuckDuckGo for latest news and context.\n"
        "3. For any Nifty index query, use get_nifty_index_analysis.\n"
        "4. Always end with a structured VERDICT.\n"
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
            q = input("\n🔍 StockSage v3> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n👋 Goodbye! Invest wisely."); break

        if not q: continue
        if q.lower() in ("exit","quit","bye","q"):
            print("\n👋 Goodbye! Invest wisely."); break
        if q.lower() == "help":
            print(HELP_TEXT); continue
        if q.lower() == "history":
            [print(f"  {i+1}. {h}") for i, (h, _) in enumerate(history)] if history else print("  No history.")
            continue
        if q.lower() == "clear":
            history.clear(); print("🗑️  History cleared."); continue

        # ── Quick shortcuts (bypass LLM) ─────────────────────────────────────
        if q.lower().startswith("quote "):
            print(get_stock_quote.invoke(q[6:].strip())); continue
        if q.lower().startswith("market "):
            print(get_market_overview.invoke(q[7:].strip())); continue
        if q.lower().startswith("dashboard"):
            cat = q[9:].strip() or "sector"
            print(get_nifty_dashboard.invoke(cat)); continue
        if q.lower().startswith("momentum"):
            p = q[8:].strip() or "1M"
            print(get_sectoral_momentum.invoke(p)); continue
        if q.lower().startswith("index "):
            print(get_nifty_index_analysis.invoke(q[6:].strip())); continue

        print(f"\n⏳ Researching '{q}'...\n{'─'*64}")
        answer = run_agent(q)
        history.append((q, answer))

        print(f"\n{'═'*64}\n📋 STOCKSAGE v3 ANALYSIS\n{'═'*64}")
        print(answer)
        print(f"{'─'*64}")
        print("⚠️  For educational purposes only. Not financial advice.")


if __name__ == "__main__":
    main()