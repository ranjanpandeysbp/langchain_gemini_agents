"""
StockSage — AI Research Agent v5
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Full Nifty Index Suite (50+ indices)
✅ Real-time quotes, fundamentals, technicals via yfinance
✅ Multi-source news: DuckDuckGo + RSS (Economic Times, Moneycontrol)
✅ Analyst Consensus: Buy/Sell/Hold ratings + price targets (yfinance)
✅ PCR (Put-Call Ratio) + Options chain support/resistance levels
✅ Detailed Fundamental Report (scorecard + rating)
✅ Detailed Technical Report (multi-timeframe + pivot levels)
✅ Trade Setup Engine: Intraday & Swing setups with SL + RR
✅ Global Macro Dashboard: Crude Oil, Gold, Silver, DXY, US Futures
✅ US Market & Futures: S&P500, NASDAQ, Dow, ES/NQ/YM/RTY futures
✅ Macro Impact Analysis: How global factors affect Indian markets
✅ Enhanced ReAct agent with Gemini
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
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
# NIFTY INDEX MASTER MAP
# ─────────────────────────────────────────────────────────────────────────────

NIFTY_INDEX_MAP = {
    # Broad Market
    "NIFTY50":"^NSEI","NIFTY":"^NSEI","SENSEX":"^BSESN",
    "NIFTY100":"^CNX100","NIFTY200":"NIFTY200.NS","NIFTY500":"^CNX500",
    "NIFTYMIDCAP50":"^NSEMDCP50","NIFTYMIDCAP100":"^CNXMDCP100",
    "NIFTYMIDCAP150":"NIFTYMIDCAP150.NS","NIFTYSMALLCAP50":"^CNXSC",
    "NIFTYSMALLCAP100":"^CNXSMCP100","NIFTYSMALLCAP250":"NIFTYSMALLCAP250.NS",
    "NIFTYMICROCAP250":"NIFTYMICROCAP250.NS","NIFTYTOTALMARKET":"NIFTYTOTALMARKET.NS",
    "NIFTYLARGMID250":"NIFTYLARGMID250.NS","NIFTYMIDSELECT":"NIFTYMIDSELECT.NS",
    # Sectoral
    "BANKNIFTY":"^NSEBANK","NIFTYBANK":"^NSEBANK","NIFTYIT":"^CNXIT",
    "NIFTYFMCG":"^CNXFMCG","NIFTYAUTO":"^CNXAUTO","NIFTYPHARMA":"^CNXPHARMA",
    "NIFTYFINSERV":"^CNXFINANCE","NIFTYFINANCE":"^CNXFINANCE","NIFTYMETAL":"^CNXMETAL",
    "NIFTYREALTY":"^CNXREALTY","NIFTYENERGY":"^CNXENERGY","NIFTYINFRA":"^CNXINFRA",
    "NIFTYMEDIA":"^CNXMEDIA","NIFTYPSUBANK":"^CNXPSUBANK","NIFTYPSE":"^CNXPSE",
    "NIFTYCONSUMPTION":"NIFTYCONSUMPTION.NS","NIFTYOILGAS":"NIFTYOILGAS.NS",
    "NIFTYHEALTHCARE":"NIFTYHEALTHCARE.NS","NIFTYMFG":"NIFTYMFG.NS",
    "NIFTYINDIAMFG":"NIFTYINDIAMFG.NS","NIFTYCHEMICALS":"NIFTYCHEMICALS.NS",
    # Thematic
    "NIFTYINDIADIGITAL":"NIFTYINDIADIGITAL.NS","NIFTYMOBILITY":"NIFTYMOBILITY.NS",
    "NIFTYNEWENERGY":"NIFTYNEWENERGY.NS","NIFTYCPSE":"^CNXCPSE","NIFTYV20":"NIFTYV20.NS",
    "NIFTY100LOWVOL30":"NIFTY100LOWVOL30.NS","NIFTYALPHA50":"NIFTYALPHA50.NS",
    "NIFTYHIGHBETA50":"NIFTYHIGHBETA50.NS","NIFTY100QUALITY30":"NIFTY100QUALITY30.NS",
    "NIFTYDIVIDEND":"^CNXDIVID","NIFTYGROWTHSECT15":"NIFTYGROWTHSECT15.NS",
    # Volatility & US Indices
    "INDIAVIX":"^INDIAVIX","SP500":"^GSPC","SPX":"^GSPC",
    "NASDAQ":"^IXIC","DOW":"^DJI","RUSSELL2000":"^RUT","VIX":"^VIX",
    # US Futures
    "ES":"ES=F","SP500FUT":"ES=F","ESFUT":"ES=F",
    "NQ":"NQ=F","NASDAQFUT":"NQ=F","NQFUT":"NQ=F",
    "YM":"YM=F","DOWFUT":"YM=F","YMFUT":"YM=F",
    "RTY":"RTY=F","RUSSELLFUT":"RTY=F",
    # Commodities
    "GOLD":"GC=F","XAUUSD":"GC=F","GOLDSPOT":"GC=F",
    "SILVER":"SI=F","XAGUSD":"SI=F",
    "CRUDEOIL":"CL=F","WTI":"CL=F","CRUDE":"CL=F","OIL":"CL=F",
    "BRENT":"BZ=F","BRENTOIL":"BZ=F",
    "NATURALGAS":"NG=F","NATGAS":"NG=F",
    "COPPER":"HG=F",
    "PLATINUM":"PL=F",
    # Currencies / Dollar Index
    "DXY":"DX-Y.NYB","DOLLARINDEX":"DX-Y.NYB","DOLLAR":"DX-Y.NYB",
    "USDINR":"USDINR=X","INRUSD":"USDINR=X",
    "EURUSD":"EURUSD=X","GBPUSD":"GBPUSD=X",
    "USDJPY":"JPY=X","USDCNY":"CNY=X",
    # MCX India proxies
    "MCXGOLD":"GC=F","MCXSILVER":"SI=F","MCXCRUDE":"CL=F",
}

NIFTY_DISPLAY = {v: k for k, v in NIFTY_INDEX_MAP.items()}

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

SECTOR_INDICES = {
    "IT":"^CNXIT","Bank":"^NSEBANK","FMCG":"^CNXFMCG","Auto":"^CNXAUTO",
    "Pharma":"^CNXPHARMA","Metal":"^CNXMETAL","Realty":"^CNXREALTY",
    "Energy":"^CNXENERGY","Infra":"^CNXINFRA","PSU Bank":"^CNXPSUBANK",
    "Financial":"^CNXFINANCE","Media":"^CNXMEDIA",
    "Oil & Gas":"NIFTYOILGAS.NS","Healthcare":"NIFTYHEALTHCARE.NS",
}

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def resolve_ticker(raw: str) -> tuple:
    raw = raw.strip().upper()
    if raw in NIFTY_INDEX_MAP:
        return NIFTY_INDEX_MAP[raw], "INDEX 📊"
    if raw.endswith(".NS"): return raw, "NSE 🇮🇳"
    if raw.endswith(".BO"): return raw, "BSE 🇮🇳"
    if raw.isdigit():       return f"{raw}.BO", "BSE 🇮🇳"
    if raw in INDIAN_TICKERS: return f"{raw}.NS", "NSE 🇮🇳"
    return raw, "US 🇺🇸"

def fmt(val, decimals=2, prefix="", suffix=""):
    try:
        if val is None: return "N/A"
        if math.isnan(float(val)): return "N/A"
        return f"{prefix}{float(val):,.{decimals}f}{suffix}"
    except: return str(val) if val else "N/A"

def human_number(n):
    try:
        n = float(n)
        if abs(n) >= 1e12: return f"{n/1e12:.2f} T"
        if abs(n) >= 1e9:  return f"{n/1e9:.2f} B"
        if abs(n) >= 1e6:  return f"{n/1e6:.2f} M"
        if abs(n) >= 1e3:  return f"{n/1e3:.2f} K"
        return str(round(n, 2))
    except: return "N/A"

def currency_sym(symbol: str) -> str:
    return "₹" if (".NS" in symbol or ".BO" in symbol
                   or "^NSE" in symbol or "^CNX" in symbol or "^BSE" in symbol) else "$"

def arrow(chg): return "▲" if chg >= 0 else "▼"
def sign(chg):  return "+" if chg >= 0 else ""

def _compute_pivots(high, low, close):
    """Standard pivot point + S1/S2/S3 + R1/R2/R3"""
    pp = (high + low + close) / 3
    r1 = 2*pp - low;  s1 = 2*pp - high
    r2 = pp + (high - low); s2 = pp - (high - low)
    r3 = high + 2*(pp - low); s3 = low - 2*(high - pp)
    return pp, r1, r2, r3, s1, s2, s3

def _rsi_series(close, period=14):
    import numpy as np
    delta = close.diff()
    gain  = delta.clip(lower=0).rolling(period).mean()
    loss  = (-delta.clip(upper=0)).rolling(period).mean()
    rs    = gain / loss.replace(0, float("nan"))
    return 100 - 100 / (1 + rs)

def _compute_all_technicals(df):
    """Compute all technical indicators and return a dict."""
    import pandas as pd
    import numpy as np
    close  = df["Close"]
    high   = df["High"]
    low    = df["Low"]
    volume = df["Volume"]

    # RSI
    rsi14  = _rsi_series(close, 14).iloc[-1]
    rsi9   = _rsi_series(close, 9).iloc[-1]

    # Stochastic
    lo14   = low.rolling(14).min()
    hi14   = high.rolling(14).max()
    pctK   = ((close - lo14) / (hi14 - lo14).replace(0, float("nan")) * 100).rolling(3).mean()
    pctD   = pctK.rolling(3).mean()
    stoch_k, stoch_d = pctK.iloc[-1], pctD.iloc[-1]

    # MACD
    ema12    = close.ewm(span=12, adjust=False).mean()
    ema26    = close.ewm(span=26, adjust=False).mean()
    macd_l   = ema12 - ema26
    signal_l = macd_l.ewm(span=9, adjust=False).mean()
    hist_l   = macd_l - signal_l
    macd_v, sig_v, hist_v = macd_l.iloc[-1], signal_l.iloc[-1], hist_l.iloc[-1]

    # EMAs & SMAs
    ema9   = close.ewm(span=9).mean().iloc[-1]
    ema20  = close.ewm(span=20).mean().iloc[-1]
    ema50  = close.ewm(span=50).mean().iloc[-1]
    ema200 = close.ewm(span=200).mean().iloc[-1]
    sma20v = close.rolling(20).mean().iloc[-1]
    sma50v = close.rolling(50).mean().iloc[-1]

    # Bollinger Bands
    sma20  = close.rolling(20).mean()
    std20  = close.rolling(20).std()
    bb_up  = (sma20 + 2*std20).iloc[-1]
    bb_lo  = (sma20 - 2*std20).iloc[-1]
    bb_mid = sma20.iloc[-1]
    bb_bw  = (bb_up - bb_lo) / bb_mid * 100

    # ATR(14)
    tr    = pd.concat([high-low, (high-close.shift()).abs(), (low-close.shift()).abs()], axis=1).max(axis=1)
    atr   = tr.rolling(14).mean().iloc[-1]

    # Volume
    avg_vol  = volume.rolling(20).mean().iloc[-1]
    last_vol = volume.iloc[-1]
    obv      = (volume * close.diff().apply(lambda x: 1 if x>0 else (-1 if x<0 else 0))).cumsum()
    obv_trend = "Rising" if obv.iloc[-1] > obv.iloc[-5] else "Falling"

    # Support / Resistance (20d and 5d)
    r20   = df.tail(20)
    r5    = df.tail(5)
    sup20 = r20["Low"].min();  res20 = r20["High"].max()
    sup5  = r5["Low"].min();   res5  = r5["High"].max()

    # Pivot (yesterday's OHLC)
    prev_h = high.iloc[-2]; prev_l = low.iloc[-2]; prev_c = close.iloc[-2]
    pp, r1, r2, r3, s1, s2, s3 = _compute_pivots(prev_h, prev_l, prev_c)

    # Trend score (0-7)
    price = close.iloc[-1]
    bull  = sum([price > ema20, price > ema50, price > ema200,
                 hist_v > 0, rsi14 < 65, stoch_k < 70, last_vol > avg_vol*0.8])

    return {
        "price":price, "rsi14":rsi14, "rsi9":rsi9,
        "stoch_k":stoch_k, "stoch_d":stoch_d,
        "macd_v":macd_v, "sig_v":sig_v, "hist_v":hist_v,
        "ema9":ema9, "ema20":ema20, "ema50":ema50, "ema200":ema200,
        "sma20":sma20v, "sma50":sma50v,
        "bb_up":bb_up, "bb_lo":bb_lo, "bb_mid":bb_mid, "bb_bw":bb_bw,
        "atr":atr, "avg_vol":avg_vol, "last_vol":last_vol,
        "obv_trend":obv_trend,
        "sup20":sup20, "res20":res20, "sup5":sup5, "res5":res5,
        "pp":pp, "r1":r1, "r2":r2, "r3":r3, "s1":s1, "s2":s2, "s3":s3,
        "bull":bull,
    }

# ─────────────────────────────────────────────────────────────────────────────
# TOOLS
# ─────────────────────────────────────────────────────────────────────────────
from langchain.tools import tool


# ══════════════════════════════════════════════════════════════════════════════
# 1. QUOTE
# ══════════════════════════════════════════════════════════════════════════════
@tool
def get_stock_quote(ticker: str) -> str:
    """
    Real-time price quote for any Indian stock, US stock, OR Nifty index.
    Input: ticker (RELIANCE, TCS, BANKNIFTY, NIFTYIT, AAPL, NVDA …)
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
            return f"❌ No data for '{ticker}'."
        cur  = currency_sym(symbol)
        last = hist["Close"].iloc[-1]
        prev = hist["Close"].iloc[-2] if len(hist) > 1 else last
        chg  = last - prev; chgp = chg/prev*100 if prev else 0
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
        return f"Error: {e}"


# ══════════════════════════════════════════════════════════════════════════════
# 2. ANALYST CONSENSUS — BUY/SELL/HOLD + PRICE TARGETS
# ══════════════════════════════════════════════════════════════════════════════
@tool
def get_analyst_consensus(ticker: str) -> str:
    """
    Fetches analyst buy/sell/hold consensus, price targets (low/mean/high),
    and recent upgrades/downgrades from yfinance + DuckDuckGo.
    Works for Indian stocks (TCS, RELIANCE, INFY) and US stocks (AAPL, NVDA).
    Input: ticker symbol.
    """
    import yfinance as yf
    from duckduckgo_search import DDGS
    symbol, market = resolve_ticker(ticker)
    try:
        tk   = yf.Ticker(symbol)
        info = tk.info
        cur  = currency_sym(symbol)

        # yfinance analyst data
        rec_key   = info.get("recommendationKey", "N/A").upper()
        rec_mean  = info.get("recommendationMean")        # 1=Strong Buy, 5=Sell
        n_analyst = info.get("numberOfAnalystOpinions", 0)
        target_lo = info.get("targetLowPrice")
        target_hi = info.get("targetHighPrice")
        target_me = info.get("targetMeanPrice")
        target_md = info.get("targetMedianPrice")
        price_now = info.get("currentPrice") or info.get("regularMarketPrice")

        # Map mean to label
        def mean_to_label(m):
            if m is None: return "N/A"
            if m <= 1.5:  return "STRONG BUY 🟢🟢"
            if m <= 2.5:  return "BUY 🟢"
            if m <= 3.5:  return "HOLD ⚪"
            if m <= 4.5:  return "UNDERPERFORM 🔴"
            return "SELL 🔴🔴"

        # Upside / downside from mean target
        upside = ((target_me - price_now) / price_now * 100) if target_me and price_now else None

        # Try to get upgrades/downgrades
        upgrades_text = ""
        try:
            upg = tk.upgrades_downgrades
            if upg is not None and not upg.empty:
                recent = upg.head(5)
                upgrades_text = "\n  [RECENT UPGRADES / DOWNGRADES]\n"
                for idx, row in recent.iterrows():
                    date_str = idx.strftime("%d %b %Y") if hasattr(idx, 'strftime') else str(idx)
                    firm  = row.get("Firm", "N/A")
                    action= row.get("Action", "")
                    to_gr = row.get("ToGrade", "")
                    fr_gr = row.get("FromGrade", "")
                    upgrades_text += f"  {date_str}  {firm:<20} {action:<12} {fr_gr} → {to_gr}\n"
        except: pass

        out  = f"🎯 ANALYST CONSENSUS — {symbol} [{market}]\n{'═'*56}\n"
        out += f"  Recommendation  : {mean_to_label(rec_mean)}  ({rec_key})\n"
        out += f"  Consensus Score : {fmt(rec_mean)} / 5.0  (1=Strong Buy, 5=Sell)\n"
        out += f"  # Analysts      : {n_analyst}\n"
        out += f"\n  [PRICE TARGETS]\n"
        out += f"  Current Price   : {cur}{fmt(price_now)}\n"
        out += f"  Target Low      : {cur}{fmt(target_lo)}\n"
        out += f"  Target Mean     : {cur}{fmt(target_me)}\n"
        out += f"  Target Median   : {cur}{fmt(target_md)}\n"
        out += f"  Target High     : {cur}{fmt(target_hi)}\n"
        if upside is not None:
            out += f"  Implied Upside  : {sign(upside)}{upside:.1f}% {'🟢' if upside>0 else '🔴'}\n"
        out += upgrades_text

        # Supplement with DuckDuckGo for latest analyst calls
        try:
            name = info.get("shortName", ticker)
            results = DDGS().text(f"{name} {ticker} analyst rating target price 2025", max_results=4)
            if results:
                out += "\n  [WEB — LATEST ANALYST CALLS]\n"
                for i, r in enumerate(results, 1):
                    out += f"  {i}. {r.get('title','')}\n"
                    out += f"     📝 {r.get('body','')[:200]}\n\n"
        except: pass

        return out
    except Exception as e:
        return f"Error fetching analyst data for {symbol}: {e}"


# ══════════════════════════════════════════════════════════════════════════════
# 3. PCR + OPTIONS CHAIN ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
@tool
def get_pcr_and_options_analysis(ticker: str) -> str:
    """
    Fetches Put-Call Ratio (PCR) from options chain and identifies max pain,
    key OI-based support and resistance levels. Best for Nifty indices and
    large-cap stocks with active options (RELIANCE, TCS, BANKNIFTY, NIFTY50).
    PCR > 1.2 = Bullish sentiment | PCR < 0.8 = Bearish | 0.8-1.2 = Neutral
    Input: ticker (NIFTY50, BANKNIFTY, RELIANCE, TCS, AAPL, etc.)
    """
    import yfinance as yf
    import numpy as np
    symbol, market = resolve_ticker(ticker)
    try:
        tk   = yf.Ticker(symbol)
        exps = tk.options
        if not exps:
            return f"⚠️ No options data for {symbol}. Options may not be listed for this ticker."

        # Use nearest expiry
        near_exp = exps[0]
        chain    = tk.option_chain(near_exp)
        calls    = chain.calls
        puts     = chain.puts
        cur      = currency_sym(symbol)

        # Current price
        hist  = tk.history(period="2d")
        price = hist["Close"].iloc[-1] if not hist.empty else 0

        # PCR by OI and by volume
        total_call_oi  = calls["openInterest"].sum()
        total_put_oi   = puts["openInterest"].sum()
        total_call_vol = calls["volume"].fillna(0).sum()
        total_put_vol  = puts["volume"].fillna(0).sum()

        pcr_oi  = total_put_oi  / total_call_oi  if total_call_oi  > 0 else 0
        pcr_vol = total_put_vol / total_call_vol if total_call_vol > 0 else 0

        # Max Pain — strike where total option buyer loss is maximum
        all_strikes = sorted(set(calls["strike"].tolist() + puts["strike"].tolist()))
        pain_vals   = {}
        for s in all_strikes:
            call_pain = ((calls["strike"] - s).clip(lower=0) * calls["openInterest"].fillna(0)).sum()
            put_pain  = ((s - puts["strike"]).clip(lower=0) * puts["openInterest"].fillna(0)).sum()
            pain_vals[s] = call_pain + put_pain
        max_pain_strike = min(pain_vals, key=pain_vals.get)

        # Highest OI strikes (key S/R from options market)
        # ATM region: ±10% of current price
        atm_calls = calls[(calls["strike"] >= price*0.90) & (calls["strike"] <= price*1.10)]
        atm_puts  = puts[(puts["strike"]  >= price*0.90) & (puts["strike"]  <= price*1.10)]

        top_call_strikes = atm_calls.nlargest(3, "openInterest")[["strike","openInterest","volume"]]
        top_put_strikes  = atm_puts.nlargest(3, "openInterest")[["strike","openInterest","volume"]]

        # Sentiment
        if pcr_oi > 1.3:   sent = "STRONG BULLISH 🟢🟢 — Heavy put writing; market expects upside"
        elif pcr_oi > 1.0: sent = "BULLISH 🟢 — More puts than calls; mild bullish bias"
        elif pcr_oi > 0.8: sent = "NEUTRAL ⚪ — Balanced positioning"
        elif pcr_oi > 0.6: sent = "BEARISH 🔴 — More calls than puts; mild bearish bias"
        else:              sent = "STRONG BEARISH 🔴🔴 — Heavy call writing; market expects downside"

        out  = f"📊 OPTIONS & PCR — {symbol} [{market}]\n{'═'*56}\n"
        out += f"  Nearest Expiry  : {near_exp}\n"
        out += f"  Current Price   : {cur}{price:,.2f}\n"
        out += f"\n  [PUT-CALL RATIO]\n"
        out += f"  PCR (OI)        : {pcr_oi:.3f}   →  {sent}\n"
        out += f"  PCR (Volume)    : {pcr_vol:.3f}\n"
        out += f"  Total Call OI   : {human_number(total_call_oi)}\n"
        out += f"  Total Put OI    : {human_number(total_put_oi)}\n"
        out += f"\n  [MAX PAIN]\n"
        out += f"  Max Pain Strike : {cur}{max_pain_strike:,.0f}\n"
        out += f"  Distance        : {((max_pain_strike - price)/price*100):+.2f}% from current price\n"
        out += f"  (Price tends to gravitate toward max pain near expiry)\n"
        out += f"\n  [KEY RESISTANCE — Top Call OI Strikes]\n"
        for _, row in top_call_strikes.iterrows():
            out += f"  Strike {cur}{row['strike']:>10,.0f}  OI: {human_number(row['openInterest'])}  Vol: {human_number(row['volume'])}\n"
        out += f"\n  [KEY SUPPORT — Top Put OI Strikes]\n"
        for _, row in top_put_strikes.iterrows():
            out += f"  Strike {cur}{row['strike']:>10,.0f}  OI: {human_number(row['openInterest'])}  Vol: {human_number(row['volume'])}\n"
        out += f"\n  PCR Interpretation Guide:\n"
        out += f"  > 1.3 = Strong Bullish  |  1.0–1.3 = Bullish  |  0.8–1.0 = Neutral\n"
        out += f"  0.6–0.8 = Bearish  |  < 0.6 = Strong Bearish\n"
        return out
    except Exception as e:
        return f"Error fetching options data for {symbol}: {e}"


# ══════════════════════════════════════════════════════════════════════════════
# 4. DETAILED FUNDAMENTAL REPORT
# ══════════════════════════════════════════════════════════════════════════════
@tool
def get_detailed_fundamental_report(ticker: str) -> str:
    """
    Generates a comprehensive fundamental analysis report with:
    - Full valuation metrics (P/E, P/B, PEG, EV/EBITDA)
    - Profitability scorecard (margins, ROE, ROA, ROCE proxy)
    - Balance sheet health (D/E, current ratio, interest coverage)
    - Growth metrics (revenue growth, earnings growth)
    - Dividend analysis
    - Fundamental strength rating (A/B/C/D/F)
    - Buy/Hold/Sell recommendation based on fundamentals
    Input: ticker (RELIANCE, TCS, HDFCBANK, AAPL …)
    """
    import yfinance as yf
    symbol, market = resolve_ticker(ticker)
    try:
        tk   = yf.Ticker(symbol)
        info = tk.info
        if not info.get("regularMarketPrice") and ".NS" in symbol:
            symbol = symbol.replace(".NS", ".BO")
            tk   = yf.Ticker(symbol); info = tk.info
        cur = currency_sym(symbol)

        # ── Collect raw values ────────────────────────────────────────────────
        pe_ttm   = info.get("trailingPE")
        pe_fwd   = info.get("forwardPE")
        pb       = info.get("priceToBook")
        peg      = info.get("pegRatio")
        ev_ebitda= info.get("enterpriseToEbitda")
        eps_ttm  = info.get("trailingEps")
        eps_fwd  = info.get("forwardEps")
        rev      = info.get("totalRevenue")
        net_inc  = info.get("netIncomeToCommon")
        ebitda   = info.get("ebitda")
        gross_m  = (info.get("grossMargins") or 0)*100
        oper_m   = (info.get("operatingMargins") or 0)*100
        net_m    = (info.get("profitMargins") or 0)*100
        roe      = (info.get("returnOnEquity") or 0)*100
        roa      = (info.get("returnOnAssets") or 0)*100
        de       = info.get("debtToEquity")
        cur_r    = info.get("currentRatio")
        book_v   = info.get("bookValue")
        div_y    = (info.get("dividendYield") or 0)*100
        div_r    = info.get("dividendRate")
        pay_r    = (info.get("payoutRatio") or 0)*100
        mkt_cap  = info.get("marketCap")
        rev_g    = (info.get("revenueGrowth") or 0)*100
        earn_g   = (info.get("earningsGrowth") or 0)*100
        price_n  = info.get("currentPrice") or info.get("regularMarketPrice")
        target_m = info.get("targetMeanPrice")
        n_anal   = info.get("numberOfAnalystOpinions", 0)
        rec_k    = info.get("recommendationKey","N/A").upper()
        rec_m    = info.get("recommendationMean")
        beta     = info.get("beta")
        sector   = info.get("sector","N/A")
        name     = info.get("longName","N/A")

        # ── Fundamental Scoring (0-100) ───────────────────────────────────────
        score = 0
        notes = []

        # Valuation (25 pts)
        if pe_ttm and pe_ttm < 15:        score += 25; notes.append("PE < 15 → Undervalued ✅")
        elif pe_ttm and pe_ttm < 25:      score += 15; notes.append("PE 15-25 → Fair value ✅")
        elif pe_ttm and pe_ttm < 40:      score += 8;  notes.append("PE 25-40 → Slightly expensive ⚠️")
        else:                             notes.append("PE > 40 or N/A → Expensive / no earnings ❌")

        # Profitability (25 pts)
        if roe > 20:                      score += 10; notes.append("ROE > 20% → Excellent ✅")
        elif roe > 12:                    score += 6;  notes.append("ROE 12-20% → Good ✅")
        else:                             notes.append("ROE < 12% → Weak ❌")
        if net_m > 15:                    score += 10; notes.append("Net Margin > 15% → Strong ✅")
        elif net_m > 8:                   score += 6;  notes.append("Net Margin 8-15% → Average ⚠️")
        else:                             notes.append("Net Margin < 8% → Thin ❌")
        if oper_m > 20:                   score += 5;  notes.append("Oper Margin > 20% → Excellent ✅")
        elif oper_m > 10:                 score += 3

        # Growth (25 pts)
        if earn_g > 20:                   score += 15; notes.append("Earnings Growth > 20% → High growth ✅")
        elif earn_g > 10:                 score += 10; notes.append("Earnings Growth 10-20% → Good ✅")
        elif earn_g > 0:                  score += 5;  notes.append("Earnings Growth > 0% → Positive ⚠️")
        else:                             notes.append("Earnings declining ❌")
        if rev_g > 15:                    score += 10; notes.append("Revenue Growth > 15% → Excellent ✅")
        elif rev_g > 5:                   score += 6;  notes.append("Revenue Growth 5-15% → Good ✅")
        else:                             notes.append("Revenue Growth < 5% ❌")

        # Balance Sheet (25 pts)
        if de and de < 0.5:               score += 15; notes.append("D/E < 0.5 → Low debt ✅")
        elif de and de < 1.5:             score += 10; notes.append("D/E 0.5-1.5 → Moderate debt ⚠️")
        elif de:                          score += 3;  notes.append("D/E > 1.5 → High debt ❌")
        if cur_r and cur_r > 2:           score += 10; notes.append("Current Ratio > 2 → Strong liquidity ✅")
        elif cur_r and cur_r > 1:         score += 6;  notes.append("Current Ratio 1-2 → Adequate ⚠️")
        else:                             notes.append("Current Ratio < 1 → Liquidity risk ❌")

        # Grade
        if score >= 80:   grade = "A+ 🏆 (Excellent)";     rec = "STRONG BUY 🟢🟢"
        elif score >= 65: grade = "A  🟢 (Very Good)";     rec = "BUY 🟢"
        elif score >= 50: grade = "B  ✅ (Good)";           rec = "BUY / HOLD 🟢"
        elif score >= 35: grade = "C  ⚠️  (Average)";      rec = "HOLD ⚪"
        elif score >= 20: grade = "D  🔴 (Below Average)"; rec = "REDUCE 🔴"
        else:             grade = "F  ❌ (Poor)";           rec = "SELL 🔴🔴"

        # Analyst consensus map
        def mean_lbl(m):
            if m is None: return "N/A"
            if m<=1.5: return "STRONG BUY 🟢🟢"
            if m<=2.5: return "BUY 🟢"
            if m<=3.5: return "HOLD ⚪"
            if m<=4.5: return "UNDERPERFORM 🔴"
            return "SELL 🔴🔴"

        upside = ((target_m - price_n)/price_n*100) if target_m and price_n else None

        out  = f"\n{'═'*62}\n"
        out += f"  📋 FUNDAMENTAL REPORT — {name}\n"
        out += f"  {symbol} | {market} | {sector}\n"
        out += f"{'═'*62}\n"
        out += f"\n  ┌─ FUNDAMENTAL SCORE ────────────────────────────────────\n"
        out += f"  │  Score  : {score}/100\n"
        out += f"  │  Grade  : {grade}\n"
        out += f"  │  Signal : {rec}\n"
        out += f"  └────────────────────────────────────────────────────────\n"

        out += f"\n  [VALUATION]\n"
        out += f"  P/E TTM       : {fmt(pe_ttm):>10}   {'✅ Cheap' if pe_ttm and pe_ttm<20 else ('⚠️ Fair' if pe_ttm and pe_ttm<35 else '❌ Expensive')}\n"
        out += f"  P/E Forward   : {fmt(pe_fwd):>10}\n"
        out += f"  P/B Ratio     : {fmt(pb):>10}   {'✅' if pb and pb<3 else '⚠️'}\n"
        out += f"  PEG Ratio     : {fmt(peg):>10}   {'✅ Undervalued' if peg and peg<1 else ('⚠️ Fair' if peg and peg<2 else '❌ Overvalued')}\n"
        out += f"  EV/EBITDA     : {fmt(ev_ebitda):>10}\n"
        out += f"  Market Cap    : {human_number(mkt_cap):>10}\n"
        out += f"  Beta          : {fmt(beta):>10}   {'Low risk' if beta and beta<0.8 else ('Moderate' if beta and beta<1.3 else 'High risk')}\n"

        out += f"\n  [PROFITABILITY]\n"
        out += f"  EPS (TTM)     : {cur}{fmt(eps_ttm):>9}\n"
        out += f"  EPS (Fwd)     : {cur}{fmt(eps_fwd):>9}\n"
        out += f"  Revenue       : {human_number(rev):>10}\n"
        out += f"  Net Income    : {human_number(net_inc):>10}\n"
        out += f"  EBITDA        : {human_number(ebitda):>10}\n"
        out += f"  Gross Margin  : {fmt(gross_m):>9}%\n"
        out += f"  Oper Margin   : {fmt(oper_m):>9}%\n"
        out += f"  Net Margin    : {fmt(net_m):>9}%\n"
        out += f"  ROE           : {fmt(roe):>9}%  {'🟢' if roe>15 else ('⚠️' if roe>8 else '🔴')}\n"
        out += f"  ROA           : {fmt(roa):>9}%\n"

        out += f"\n  [GROWTH]\n"
        out += f"  Revenue Growth: {fmt(rev_g):>9}%  {'🟢' if rev_g>10 else ('⚠️' if rev_g>0 else '🔴')}\n"
        out += f"  Earnings Growth:{fmt(earn_g):>9}%  {'🟢' if earn_g>15 else ('⚠️' if earn_g>0 else '🔴')}\n"

        out += f"\n  [BALANCE SHEET HEALTH]\n"
        out += f"  Debt/Equity   : {fmt(de):>10}  {'✅ Low' if de and de<0.5 else ('⚠️ Moderate' if de and de<1.5 else '❌ High')}\n"
        out += f"  Current Ratio : {fmt(cur_r):>10}  {'✅ Strong' if cur_r and cur_r>2 else ('⚠️ Adequate' if cur_r and cur_r>1 else '❌ Weak')}\n"
        out += f"  Book Value    : {cur}{fmt(book_v):>9}\n"

        out += f"\n  [DIVIDENDS]\n"
        out += f"  Div Yield     : {fmt(div_y):>9}%\n"
        out += f"  Div Rate      : {cur}{fmt(div_r):>9}\n"
        out += f"  Payout Ratio  : {fmt(pay_r):>9}%\n"

        out += f"\n  [ANALYST CONSENSUS]\n"
        out += f"  Wall St Rating: {mean_lbl(rec_m)} ({rec_k})\n"
        out += f"  # Analysts    : {n_anal}\n"
        out += f"  Target Price  : {cur}{fmt(target_m)}\n"
        if upside: out += f"  Upside        : {sign(upside)}{upside:.1f}%\n"

        out += f"\n  [SCORECARD BREAKDOWN]\n"
        for n in notes:
            out += f"  • {n}\n"

        return out
    except Exception as e:
        return f"Error in fundamental report for {symbol}: {e}"


# ══════════════════════════════════════════════════════════════════════════════
# 5. DETAILED TECHNICAL REPORT
# ══════════════════════════════════════════════════════════════════════════════
@tool
def get_detailed_technical_report(ticker: str) -> str:
    """
    Comprehensive multi-timeframe technical analysis report including:
    - Trend analysis (EMA 9/20/50/200)
    - Momentum (RSI, Stochastic, MACD)
    - Volatility (Bollinger Bands, ATR)
    - Volume + OBV analysis
    - Daily pivot points (PP, R1/R2/R3, S1/S2/S3)
    - 5-day and 20-day support/resistance zones
    - Technical signal score + BUY/SELL rating
    Input: ticker or index name (RELIANCE, BANKNIFTY, TCS, AAPL …)
    """
    import yfinance as yf
    import numpy as np
    symbol, market = resolve_ticker(ticker)
    try:
        df6m = yf.Ticker(symbol).history(period="6mo", interval="1d")
        if df6m.empty and ".NS" in symbol:
            symbol = symbol.replace(".NS", ".BO"); market = "BSE 🇮🇳"
            df6m = yf.Ticker(symbol).history(period="6mo", interval="1d")
        if df6m.empty:
            return f"No data for '{ticker}'."

        cur = currency_sym(symbol)
        t   = _compute_all_technicals(df6m)
        p   = t["price"]
        atr = t["atr"]

        # Signal labels
        def rsi_lbl(r): return "OVERSOLD 🟢" if r<30 else ("OVERBOUGHT 🔴" if r>70 else "NEUTRAL ⚪")
        def stoch_lbl(k): return "OVERSOLD 🟢" if k<20 else ("OVERBOUGHT 🔴" if k>80 else "NEUTRAL ⚪")
        trend_lbl = ("STRONG UPTREND 🟢🟢" if p>t["ema50"]>t["ema200"] else
                     "UPTREND 🟢"          if p>t["ema50"] else
                     "STRONG DOWNTREND 🔴🔴" if p<t["ema50"]<t["ema200"] else
                     "DOWNTREND 🔴"        if p<t["ema50"] else "SIDEWAYS ⚪")
        macd_lbl  = "BULLISH CROSSOVER 🟢" if t["hist_v"]>0 else "BEARISH CROSSOVER 🔴"
        vol_lbl   = "HIGH 🔥" if t["last_vol"]>t["avg_vol"]*1.5 else ("LOW 📉" if t["last_vol"]<t["avg_vol"]*0.5 else "NORMAL ⚪")
        bb_lbl    = ("Near UPPER 🔴 Overbought" if p>t["bb_up"]*0.98 else
                     "Near LOWER 🟢 Oversold"   if p<t["bb_lo"]*1.02 else "Middle Zone ⚪")

        # Technical signal score (0-10)
        sc = 0
        sc += 2 if p > t["ema200"] else 0           # above 200 EMA
        sc += 1 if p > t["ema50"]  else 0           # above 50 EMA
        sc += 1 if p > t["ema20"]  else 0           # above 20 EMA
        sc += 1 if t["hist_v"] > 0 else 0           # MACD bullish
        sc += 1 if t["rsi14"] > 40 and t["rsi14"] < 70 else 0  # RSI healthy
        sc += 1 if t["stoch_k"] < 80 else 0         # stoch not overbought
        sc += 1 if t["obv_trend"] == "Rising" else 0# OBV rising
        sc += 1 if t["last_vol"] > t["avg_vol"]*0.7 else 0  # decent volume
        sc += 1 if t["bb_bw"] < 8 else 0            # not overextended

        if sc >= 8:   tech_rec = "STRONG BUY 🟢🟢";  tech_grade = "A+"
        elif sc >= 6: tech_rec = "BUY 🟢";            tech_grade = "A"
        elif sc >= 5: tech_rec = "MILD BUY 🟢";       tech_grade = "B"
        elif sc >= 4: tech_rec = "NEUTRAL ⚪";         tech_grade = "C"
        elif sc >= 3: tech_rec = "MILD SELL 🔴";       tech_grade = "D"
        else:         tech_rec = "SELL 🔴🔴";          tech_grade = "F"

        out  = f"\n{'═'*62}\n"
        out += f"  📈 TECHNICAL REPORT — {symbol} [{market}]\n"
        out += f"{'═'*62}\n"
        out += f"\n  ┌─ TECHNICAL SCORE ──────────────────────────────────────\n"
        out += f"  │  Score  : {sc}/10\n"
        out += f"  │  Grade  : {tech_grade}\n"
        out += f"  │  Signal : {tech_rec}\n"
        out += f"  └────────────────────────────────────────────────────────\n"

        out += f"\n  [PRICE ACTION]\n"
        out += f"  Current Price  : {cur}{p:,.2f}\n"
        out += f"  Trend          : {trend_lbl}\n"

        out += f"\n  [EMA CLOUD]\n"
        out += f"  EMA  9   : {cur}{t['ema9']:,.2f}   {'▲ Price above' if p>t['ema9'] else '▼ Price below'}\n"
        out += f"  EMA 20   : {cur}{t['ema20']:,.2f}   {'▲ Price above' if p>t['ema20'] else '▼ Price below'}\n"
        out += f"  EMA 50   : {cur}{t['ema50']:,.2f}   {'▲ Price above' if p>t['ema50'] else '▼ Price below'}\n"
        out += f"  EMA 200  : {cur}{t['ema200']:,.2f}   {'▲ Price above' if p>t['ema200'] else '▼ Price below'}\n"
        out += f"  EMA 9×20 : {'Golden Cross 🟢' if t['ema9']>t['ema20'] else 'Death Cross 🔴'}\n"
        out += f"  EMA50×200: {'Golden Cross 🟢' if t['ema50']>t['ema200'] else 'Death Cross 🔴'}\n"

        out += f"\n  [MOMENTUM INDICATORS]\n"
        out += f"  RSI(14)  : {t['rsi14']:.1f}  →  {rsi_lbl(t['rsi14'])}\n"
        out += f"  RSI(9)   : {t['rsi9']:.1f}   (short-term)\n"
        out += f"  Stoch %K : {t['stoch_k']:.1f}  %D: {t['stoch_d']:.1f}  →  {stoch_lbl(t['stoch_k'])}\n"
        out += f"  MACD     : {t['macd_v']:,.3f}  |  Signal: {t['sig_v']:,.3f}  |  Hist: {t['hist_v']:,.3f}\n"
        out += f"  MACD     : {macd_lbl}\n"

        out += f"\n  [VOLATILITY]\n"
        out += f"  BB Upper : {cur}{t['bb_up']:,.2f}\n"
        out += f"  BB Mid   : {cur}{t['bb_mid']:,.2f}\n"
        out += f"  BB Lower : {cur}{t['bb_lo']:,.2f}\n"
        out += f"  BB BW    : {t['bb_bw']:.1f}%  ({'Squeeze — breakout coming ⚡' if t['bb_bw']<4 else 'Wide — high volatility' if t['bb_bw']>12 else 'Normal'})\n"
        out += f"  BB Status: {bb_lbl}\n"
        out += f"  ATR(14)  : {cur}{atr:,.2f}  ({atr/p*100:.1f}% of price)\n"

        out += f"\n  [VOLUME ANALYSIS]\n"
        out += f"  Last Volume    : {human_number(t['last_vol'])}\n"
        out += f"  20D Avg Volume : {human_number(t['avg_vol'])}\n"
        out += f"  Volume Trend   : {vol_lbl}\n"
        out += f"  OBV Trend      : {t['obv_trend']} {'🟢' if t['obv_trend']=='Rising' else '🔴'}\n"

        out += f"\n  [PIVOT POINTS — Daily]\n"
        out += f"  Pivot (PP) : {cur}{t['pp']:,.2f}\n"
        out += f"  R1         : {cur}{t['r1']:,.2f}   S1: {cur}{t['s1']:,.2f}\n"
        out += f"  R2         : {cur}{t['r2']:,.2f}   S2: {cur}{t['s2']:,.2f}\n"
        out += f"  R3         : {cur}{t['r3']:,.2f}   S3: {cur}{t['s3']:,.2f}\n"

        out += f"\n  [SUPPORT / RESISTANCE ZONES]\n"
        out += f"  Immediate Support  (5d low) : {cur}{t['sup5']:,.2f}\n"
        out += f"  Immediate Resist   (5d high): {cur}{t['res5']:,.2f}\n"
        out += f"  Strong Support    (20d low) : {cur}{t['sup20']:,.2f}\n"
        out += f"  Strong Resistance (20d high): {cur}{t['res20']:,.2f}\n"

        return out
    except Exception as e:
        return f"Error in technical report for {symbol}: {e}"


# ══════════════════════════════════════════════════════════════════════════════
# 6. INTRADAY TRADE SETUP
# ══════════════════════════════════════════════════════════════════════════════
@tool
def get_intraday_trade_setup(ticker: str) -> str:
    """
    Generates a complete INTRADAY trade setup with:
    - Long (BUY) and Short (SELL) setups
    - Entry price zone, Stop-Loss, Target 1, Target 2, Target 3
    - Risk-Reward Ratio for each setup
    - Position sizing guidance (1% risk rule)
    - Setup quality rating
    Use for day traders. Works on stocks and indices.
    Input: ticker (RELIANCE, BANKNIFTY, TCS, NIFTY50 …)
    """
    import yfinance as yf
    import pandas as pd
    symbol, market = resolve_ticker(ticker)
    try:
        # Fetch 5-min data if available, else 15-min
        df15 = yf.Ticker(symbol).history(period="5d", interval="15m")
        df1d = yf.Ticker(symbol).history(period="30d", interval="1d")
        if df15.empty or df1d.empty:
            return f"Insufficient intraday data for '{ticker}'."

        cur = currency_sym(symbol)
        t   = _compute_all_technicals(df15)   # technicals on 15-min
        td  = _compute_all_technicals(df1d)   # technicals on daily (trend filter)

        price = t["price"]
        atr15 = t["atr"]     # 15-min ATR
        atr1d = td["atr"]    # daily ATR
        intra_atr = atr1d * 0.6   # typical intraday range ~ 60% of daily ATR

        # Daily trend context
        daily_trend = "UPTREND" if df1d["Close"].iloc[-1] > td["ema50"] else "DOWNTREND"

        # Intraday levels from 15-min data
        today_data = df15[df15.index.date == df15.index[-1].date()]
        if not today_data.empty:
            day_high = today_data["High"].max()
            day_low  = today_data["Low"].min()
            day_open = today_data["Open"].iloc[0]
        else:
            day_high = t["res5"];  day_low = t["sup5"];  day_open = price

        # Pivot (yesterday)
        prev = df1d.iloc[-2]
        pp, r1, r2, r3, s1, s2, s3 = _compute_pivots(prev["High"], prev["Low"], prev["Close"])

        # ── LONG SETUP ────────────────────────────────────────────────────────
        # Entry: above pivot / above day high breakout / near S1 support
        long_entry_zone_lo = max(pp, t["ema20"]) * 0.9985
        long_entry_zone_hi = max(pp, t["ema20"]) * 1.0015
        long_sl     = min(t["sup5"], s1) - atr15*0.3   # below immediate support
        long_sl     = min(long_sl, price - atr15*1.2)
        long_t1     = r1
        long_t2     = r2
        long_t3     = r2 + (r2 - r1)
        long_risk   = price - long_sl
        long_rr1    = (long_t1 - price) / long_risk if long_risk > 0 else 0
        long_rr2    = (long_t2 - price) / long_risk if long_risk > 0 else 0

        # ── SHORT SETUP ───────────────────────────────────────────────────────
        short_entry_zone_lo = min(pp, t["ema20"]) * 0.9985
        short_entry_zone_hi = min(pp, t["ema20"]) * 1.0015
        short_sl    = max(t["res5"], r1) + atr15*0.3
        short_sl    = max(short_sl, price + atr15*1.2)
        short_t1    = s1
        short_t2    = s2
        short_t3    = s2 - (s1 - s2)
        short_risk  = short_sl - price
        short_rr1   = (price - short_t1) / short_risk if short_risk > 0 else 0
        short_rr2   = (price - short_t2) / short_risk if short_risk > 0 else 0

        # Setup quality
        long_quality  = "STRONG ✅" if t["rsi14"]<60 and td["hist_v"]>0 and daily_trend=="UPTREND" else ("MODERATE ⚠️" if t["rsi14"]<70 else "WEAK ❌")
        short_quality = "STRONG ✅" if t["rsi14"]>40 and td["hist_v"]<0 and daily_trend=="DOWNTREND" else ("MODERATE ⚠️" if t["rsi14"]>30 else "WEAK ❌")

        # Position sizing (1% risk rule)
        capital_ex = 100000  # example ₹1 lakh
        qty_long   = int(capital_ex * 0.01 / long_risk) if long_risk > 0 else 0
        qty_short  = int(capital_ex * 0.01 / short_risk) if short_risk > 0 else 0

        out  = f"\n{'═'*64}\n"
        out += f"  ⚡ INTRADAY TRADE SETUP — {symbol} [{market}]\n"
        out += f"{'═'*64}\n"
        out += f"  Current Price   : {cur}{price:,.2f}\n"
        out += f"  Daily Trend     : {daily_trend} (Daily EMA50 filter)\n"
        out += f"  ATR(14) Daily   : {cur}{atr1d:,.2f}  |  ATR 15-min: {cur}{atr15:,.2f}\n"
        out += f"  Today Range     : H:{cur}{day_high:,.2f}  L:{cur}{day_low:,.2f}\n"
        out += f"\n  [PIVOT LEVELS]\n"
        out += f"  PP:{cur}{pp:,.2f}  R1:{cur}{r1:,.2f}  R2:{cur}{r2:,.2f}  R3:{cur}{r3:,.2f}\n"
        out += f"             S1:{cur}{s1:,.2f}  S2:{cur}{s2:,.2f}  S3:{cur}{s3:,.2f}\n"

        out += f"\n  ┌─ 📈 LONG (BUY) SETUP {'─'*38}\n"
        out += f"  │  Quality       : {long_quality}\n"
        out += f"  │  Entry Zone    : {cur}{long_entry_zone_lo:,.2f} – {cur}{long_entry_zone_hi:,.2f}\n"
        out += f"  │  Stop-Loss     : {cur}{long_sl:,.2f}  (Risk: {cur}{abs(price-long_sl):,.2f})\n"
        out += f"  │  Target 1 (R1) : {cur}{long_t1:,.2f}  →  RR {long_rr1:.1f}:1  🎯\n"
        out += f"  │  Target 2 (R2) : {cur}{long_t2:,.2f}  →  RR {long_rr2:.1f}:1  🎯🎯\n"
        out += f"  │  Target 3      : {cur}{long_t3:,.2f}  →  RR {((long_t3-price)/long_risk):.1f}:1  🎯🎯🎯\n"
        out += f"  │  Position Size : {qty_long} shares (1% risk on {cur}{capital_ex:,})\n"
        out += f"  └{'─'*62}\n"

        out += f"\n  ┌─ 📉 SHORT (SELL) SETUP {'─'*37}\n"
        out += f"  │  Quality       : {short_quality}\n"
        out += f"  │  Entry Zone    : {cur}{short_entry_zone_lo:,.2f} – {cur}{short_entry_zone_hi:,.2f}\n"
        out += f"  │  Stop-Loss     : {cur}{short_sl:,.2f}  (Risk: {cur}{abs(short_sl-price):,.2f})\n"
        out += f"  │  Target 1 (S1) : {cur}{short_t1:,.2f}  →  RR {short_rr1:.1f}:1  🎯\n"
        out += f"  │  Target 2 (S2) : {cur}{short_t2:,.2f}  →  RR {short_rr2:.1f}:1  🎯🎯\n"
        out += f"  │  Target 3      : {cur}{short_t3:,.2f}  →  RR {((price-short_t3)/short_risk):.1f}:1  🎯🎯🎯\n"
        out += f"  │  Position Size : {qty_short} shares (1% risk on {cur}{capital_ex:,})\n"
        out += f"  └{'─'*62}\n"

        out += f"\n  [INTRADAY RULES]\n"
        out += f"  • Trade LONG only if price > PP and daily trend is UP\n"
        out += f"  • Trade SHORT only if price < PP and daily trend is DOWN\n"
        out += f"  • Book 50% at T1, trail SL to entry for rest\n"
        out += f"  • Exit all positions 15 min before market close\n"
        out += f"  • Never risk more than 1-2% of capital per trade\n"
        out += f"  ⚠️  Educational only. Not financial advice.\n"
        return out
    except Exception as e:
        return f"Error generating intraday setup for {symbol}: {e}"


# ══════════════════════════════════════════════════════════════════════════════
# 7. SWING TRADE SETUP
# ══════════════════════════════════════════════════════════════════════════════
@tool
def get_swing_trade_setup(ticker: str) -> str:
    """
    Generates a complete SWING trade setup (2–15 days holding) with:
    - Trend-based Long and Short setups
    - Entry price, Stop-Loss, Target 1/2/3
    - Risk-Reward Ratios
    - Position sizing guidance
    - Setup quality score
    - Ideal holding period estimate
    Input: ticker (RELIANCE, TCS, BANKNIFTY, NIFTY50, AAPL …)
    """
    import yfinance as yf
    import numpy as np
    symbol, market = resolve_ticker(ticker)
    try:
        df   = yf.Ticker(symbol).history(period="6mo", interval="1d")
        if df.empty and ".NS" in symbol:
            symbol = symbol.replace(".NS", ".BO"); market = "BSE 🇮🇳"
            df = yf.Ticker(symbol).history(period="6mo", interval="1d")
        if df.empty:
            return f"No data for '{ticker}'."

        cur = currency_sym(symbol)
        t   = _compute_all_technicals(df)
        p   = t["price"]
        atr = t["atr"]

        close = df["Close"]
        high  = df["High"]
        low   = df["Low"]

        # Weekly trend
        ema21w = close.ewm(span=21).mean().iloc[-1]
        ema55  = close.ewm(span=55).mean().iloc[-1]
        weekly_trend = "UPTREND 🟢" if p > ema21w > ema55 else ("DOWNTREND 🔴" if p < ema21w < ema55 else "SIDEWAYS ⚪")

        # Swing S/R based on recent 10 and 20 candle pivots
        rec10 = df.tail(10)
        s10   = rec10["Low"].min();  r10 = rec10["High"].max()
        s20   = t["sup20"];          r20 = t["res20"]

        # Fibonacci retracement from 20-day swing
        fib_range  = r20 - s20
        fib_382    = r20 - 0.382 * fib_range
        fib_500    = r20 - 0.500 * fib_range
        fib_618    = r20 - 0.618 * fib_range
        fib_ext127 = r20 + 0.272 * fib_range   # extension target
        fib_ext162 = r20 + 0.618 * fib_range

        # ── LONG SETUP ────────────────────────────────────────────────────────
        # Entry near fib 38.2 or 50% if in uptrend; or above recent high breakout
        if p > t["ema50"]:  # uptrend — buy dip
            long_entry  = max(fib_382, t["ema20"]) if abs(p - fib_382)/p < 0.03 else p
            long_entry_type = "Fib 38.2% Retracement / EMA20 Support"
        else:  # breakout
            long_entry  = r20 * 1.005
            long_entry_type = "Breakout above 20d High"
        long_sl   = min(s10, fib_618) - atr*0.2
        long_sl   = min(long_sl, p - atr*2)
        long_t1   = r10
        long_t2   = fib_ext127
        long_t3   = fib_ext162
        long_risk = p - long_sl
        long_rr1  = (long_t1 - p) / long_risk if long_risk > 0 else 0
        long_rr2  = (long_t2 - p) / long_risk if long_risk > 0 else 0
        long_rr3  = (long_t3 - p) / long_risk if long_risk > 0 else 0

        # ── SHORT SETUP ───────────────────────────────────────────────────────
        if p < t["ema50"]:  # downtrend — short rally
            short_entry = min(fib_382, t["ema20"]) if abs(p - fib_382)/p < 0.05 else p
            short_entry_type = "Fib 38.2% Bounce / EMA20 Resistance"
        else:  # breakdown
            short_entry = s20 * 0.995
            short_entry_type = "Breakdown below 20d Low"
        short_sl   = max(r10, fib_382) + atr*0.2
        short_sl   = max(short_sl, p + atr*2)
        short_t1   = s10
        short_t2   = r20 - 0.618 * fib_range
        short_t3   = s20
        short_risk = short_sl - p
        short_rr1  = (p - short_t1) / short_risk if short_risk > 0 else 0
        short_rr2  = (p - short_t2) / short_risk if short_risk > 0 else 0
        short_rr3  = (p - short_t3) / short_risk if short_risk > 0 else 0

        # Quality scoring
        long_sc  = sum([t["rsi14"]<65, t["hist_v"]>0, p>t["ema50"], t["obv_trend"]=="Rising", t["stoch_k"]<70])
        short_sc = sum([t["rsi14"]>35, t["hist_v"]<0, p<t["ema50"], t["obv_trend"]=="Falling", t["stoch_k"]>30])

        def ql(s): return "EXCELLENT ✅✅" if s>=4 else ("GOOD ✅" if s>=3 else ("MODERATE ⚠️" if s>=2 else "WEAK ❌"))

        # Position sizing
        capital_ex = 100000
        qty_long  = int(capital_ex * 0.02 / long_risk)  if long_risk > 0 else 0  # 2% risk for swing
        qty_short = int(capital_ex * 0.02 / short_risk) if short_risk > 0 else 0

        out  = f"\n{'═'*64}\n"
        out += f"  🔄 SWING TRADE SETUP — {symbol} [{market}]\n"
        out += f"{'═'*64}\n"
        out += f"  Current Price    : {cur}{p:,.2f}\n"
        out += f"  Trend (Daily)    : {weekly_trend}\n"
        out += f"  ATR(14) Daily    : {cur}{atr:,.2f}  (~{atr/p*100:.1f}% daily range)\n"
        out += f"  EMA 21           : {cur}{ema21w:,.2f}  |  EMA 55: {cur}{ema55:,.2f}\n"

        out += f"\n  [FIBONACCI LEVELS — 20d Swing]\n"
        out += f"  Swing High       : {cur}{r20:,.2f}\n"
        out += f"  Fib 38.2%        : {cur}{fib_382:,.2f}\n"
        out += f"  Fib 50.0%        : {cur}{fib_500:,.2f}\n"
        out += f"  Fib 61.8%        : {cur}{fib_618:,.2f}\n"
        out += f"  Swing Low        : {cur}{s20:,.2f}\n"
        out += f"  Fib Ext 127.2%   : {cur}{fib_ext127:,.2f}\n"
        out += f"  Fib Ext 161.8%   : {cur}{fib_ext162:,.2f}\n"

        out += f"\n  ┌─ 📈 SWING LONG SETUP {'─'*40}\n"
        out += f"  │  Quality        : {ql(long_sc)} (score {long_sc}/5)\n"
        out += f"  │  Setup Type     : {long_entry_type}\n"
        out += f"  │  Entry          : {cur}{long_entry:,.2f}\n"
        out += f"  │  Stop-Loss      : {cur}{long_sl:,.2f}  (Risk: {cur}{abs(p-long_sl):,.2f} | {abs(p-long_sl)/p*100:.1f}%)\n"
        out += f"  │  Target 1       : {cur}{long_t1:,.2f}  →  RR {long_rr1:.1f}:1  🎯  (Book 40%)\n"
        out += f"  │  Target 2       : {cur}{long_t2:,.2f}  →  RR {long_rr2:.1f}:1  🎯🎯 (Book 40%)\n"
        out += f"  │  Target 3       : {cur}{long_t3:,.2f}  →  RR {long_rr3:.1f}:1  🎯🎯🎯 (Book 20%)\n"
        out += f"  │  Hold Period    : 3–10 trading days\n"
        out += f"  │  Position Size  : {qty_long} shares (2% risk on {cur}{capital_ex:,})\n"
        out += f"  └{'─'*62}\n"

        out += f"\n  ┌─ 📉 SWING SHORT SETUP {'─'*39}\n"
        out += f"  │  Quality        : {ql(short_sc)} (score {short_sc}/5)\n"
        out += f"  │  Setup Type     : {short_entry_type}\n"
        out += f"  │  Entry          : {cur}{short_entry:,.2f}\n"
        out += f"  │  Stop-Loss      : {cur}{short_sl:,.2f}  (Risk: {cur}{abs(short_sl-p):,.2f} | {abs(short_sl-p)/p*100:.1f}%)\n"
        out += f"  │  Target 1       : {cur}{short_t1:,.2f}  →  RR {short_rr1:.1f}:1  🎯  (Book 40%)\n"
        out += f"  │  Target 2       : {cur}{short_t2:,.2f}  →  RR {short_rr2:.1f}:1  🎯🎯 (Book 40%)\n"
        out += f"  │  Target 3       : {cur}{short_t3:,.2f}  →  RR {short_rr3:.1f}:1  🎯🎯🎯 (Book 20%)\n"
        out += f"  │  Hold Period    : 3–10 trading days\n"
        out += f"  │  Position Size  : {qty_short} shares (2% risk on {cur}{capital_ex:,})\n"
        out += f"  └{'─'*62}\n"

        out += f"\n  [SWING TRADING RULES]\n"
        out += f"  • Only trade setups with RR ≥ 2:1\n"
        out += f"  • Book 40% at T1, move SL to breakeven\n"
        out += f"  • Book another 40% at T2, trail remaining with ATR stop\n"
        out += f"  • Discard setup if RSI > 75 (long) or < 25 (short)\n"
        out += f"  • Confirm entry with volume spike (> 1.5x avg)\n"
        out += f"  ⚠️  Educational only. Not financial advice.\n"
        return out
    except Exception as e:
        return f"Error generating swing setup for {symbol}: {e}"


# ══════════════════════════════════════════════════════════════════════════════
# 8–14. RETAINED + IMPROVED TOOLS FROM v3
# ══════════════════════════════════════════════════════════════════════════════

@tool
def get_nifty_index_analysis(index_name: str) -> str:
    """
    Deep analysis of any Nifty index with technicals, returns, pivot points.
    Inputs: NIFTY50, BANKNIFTY, NIFTYIT, NIFTYFMCG, NIFTYAUTO, NIFTYPHARMA,
            NIFTYMETAL, NIFTYREALTY, NIFTYENERGY, NIFTYPSUBANK, INDIAVIX,
            NIFTYMIDCAP100, NIFTYSMALLCAP100, NIFTYCPSE … (50+ indices)
    Input: index name.
    """
    import yfinance as yf
    import numpy as np
    key = index_name.strip().upper().replace(" ","").replace("-","")
    if key not in NIFTY_INDEX_MAP:
        matches = [k for k in NIFTY_INDEX_MAP if key in k]
        if not matches: return f"❌ Unknown index '{index_name}'. Available: {', '.join(sorted(NIFTY_INDEX_MAP.keys()))}"
        key = matches[0]
    symbol = NIFTY_INDEX_MAP[key]
    try:
        df = yf.Ticker(symbol).history(period="1y", interval="1d")
        if df.empty: return f"⚠️ No data for {key} ({symbol})."
        t     = _compute_all_technicals(df)
        close = df["Close"]
        now   = t["price"]
        prev  = close.iloc[-2]
        chg   = now - prev; chgp = chg/prev*100

        def ret(d):
            try:
                p = close.iloc[-d] if d<len(close) else close.iloc[0]
                r = (now-p)/p*100; return f"{sign(r)}{r:.2f}%"
            except: return "N/A"

        ytd = df[df.index.year==datetime.now().year]["Close"]
        ytd_r = ((now-ytd.iloc[0])/ytd.iloc[0]*100) if not ytd.empty else 0
        ann_v = close.pct_change().dropna().std()*(252**0.5)*100

        rsi_s = "OVERSOLD 🟢" if t["rsi14"]<30 else ("OVERBOUGHT 🔴" if t["rsi14"]>70 else "NEUTRAL ⚪")
        trend = ("STRONG UPTREND 🟢" if now>t["ema50"]>t["ema200"] else "STRONG DOWNTREND 🔴" if now<t["ema50"]<t["ema200"] else "MIXED ⚪")

        out  = f"📊 INDEX ANALYSIS — {key} ({symbol})\n{'═'*56}\n"
        out += f"  Value    : ₹{now:,.2f}  {arrow(chg)} {sign(chg)}{chg:.2f} ({sign(chgp)}{chgp:.2f}%)\n"
        out += f"  52W H/L  : ₹{close.max():,.2f} / ₹{close.min():,.2f}\n"
        out += f"\n  [RETURNS]\n"
        out += f"  1W:{ret(5)}  1M:{ret(21)}  3M:{ret(63)}  6M:{ret(126)}  YTD:{sign(ytd_r)}{ytd_r:.2f}%  1Y:{ret(252)}\n"
        out += f"\n  [TECHNICALS]\n"
        out += f"  EMA20:₹{t['ema20']:,.0f}  EMA50:₹{t['ema50']:,.0f}  EMA200:₹{t['ema200']:,.0f}\n"
        out += f"  Trend : {trend}\n"
        out += f"  RSI(14): {t['rsi14']:.1f} → {rsi_s}  |  MACD Hist: {t['hist_v']:.2f} {'🟢' if t['hist_v']>0 else '🔴'}\n"
        out += f"  BB: Up:₹{t['bb_up']:,.0f}  Lo:₹{t['bb_lo']:,.0f}  BW:{t['bb_bw']:.1f}%\n"
        out += f"\n  [PIVOT LEVELS]\n"
        out += f"  PP:₹{t['pp']:,.2f}  R1:₹{t['r1']:,.2f}  R2:₹{t['r2']:,.2f}\n"
        out += f"          S1:₹{t['s1']:,.2f}  S2:₹{t['s2']:,.2f}\n"
        out += f"\n  [S/R ZONES]\n"
        out += f"  Immediate Support : ₹{t['sup5']:,.2f}  |  Resistance: ₹{t['res5']:,.2f}\n"
        out += f"  Strong Support    : ₹{t['sup20']:,.2f}  |  Resistance: ₹{t['res20']:,.2f}\n"
        out += f"\n  [RISK]  Ann.Vol: {ann_v:.1f}%\n"
        return out
    except Exception as e: return f"Error: {e}"


@tool
def get_sectoral_momentum(period: str = "1M") -> str:
    """Sectoral momentum scorecard. Input: '1W','1M','3M','6M','1Y'"""
    import yfinance as yf
    period_map = {"1W":5,"1M":21,"3M":63,"6M":126,"1Y":252}
    p    = period.strip().upper()
    days = period_map.get(p, 21)
    results = []
    for name, sym in SECTOR_INDICES.items():
        try:
            hist  = yf.Ticker(sym).history(period="1y",interval="1d")
            if hist.empty or len(hist)<days: continue
            close = hist["Close"]
            now, past = close.iloc[-1], close.iloc[-days]
            ret = (now-past)/past*100
            rsi = _rsi_series(close,14).iloc[-1]
            results.append((name, sym, now, ret, rsi))
        except: pass
    if not results: return "⚠️ Could not fetch sectoral data."
    results.sort(key=lambda x: x[3], reverse=True)
    out  = f"🏭 SECTORAL MOMENTUM — {p}\n{'═'*56}\n"
    out += f"  {'Sector':<16} {'Price':>10} {'Return':>9} {'RSI':>7}  Signal\n"
    out += f"  {'─'*14} {'─'*10} {'─'*9} {'─'*7}  {'─'*12}\n"
    for name, sym, price, ret, rsi in results:
        rsi_s = "Overbought🔴" if rsi>70 else ("Oversold🟢" if rsi<30 else "Neutral⚪")
        out  += f"  {name:<16} {price:>10,.0f} {sign(ret)}{ret:>7.2f}% {rsi:>7.1f}  {rsi_s}\n"
    out += f"\n  🏆 Top Gainer : {results[0][0]}  ({sign(results[0][3])}{results[0][3]:.2f}%)\n"
    out += f"  📉 Top Laggard: {results[-1][0]}  ({sign(results[-1][3])}{results[-1][3]:.2f}%)\n"
    return out


@tool
def get_nifty_dashboard(category: str = "sector") -> str:
    """Live Nifty index dashboard. category: 'broad','sector','thematic','all'"""
    import yfinance as yf
    groups = {
        "broad"   : {"Nifty 50":"^NSEI","Nifty 100":"^CNX100","Nifty 500":"^CNX500",
                     "Midcap 50":"^NSEMDCP50","Midcap 100":"^CNXMDCP100",
                     "Smallcap 50":"^CNXSC","Smallcap 100":"^CNXSMCP100",
                     "Sensex":"^BSESN","India VIX":"^INDIAVIX"},
        "sector"  : {"Bank Nifty":"^NSEBANK","Nifty IT":"^CNXIT","Nifty FMCG":"^CNXFMCG",
                     "Nifty Auto":"^CNXAUTO","Nifty Pharma":"^CNXPHARMA","Nifty Metal":"^CNXMETAL",
                     "Nifty Realty":"^CNXREALTY","Nifty Energy":"^CNXENERGY",
                     "Nifty Infra":"^CNXINFRA","PSU Bank":"^CNXPSUBANK",
                     "Nifty Fin Serv":"^CNXFINANCE","Nifty Media":"^CNXMEDIA",
                     "Oil & Gas":"NIFTYOILGAS.NS","Healthcare":"NIFTYHEALTHCARE.NS"},
        "thematic": {"Nifty CPSE":"^CNXCPSE","Nifty Dividend":"^CNXDIVID",
                     "Nifty Alpha50":"NIFTYALPHA50.NS","Nifty HiBeta50":"NIFTYHIGHBETA50.NS",
                     "Nifty Value20":"NIFTYV20.NS","Nifty Quality30":"NIFTY100QUALITY30.NS",
                     "Nifty LowVol30":"NIFTY100LOWVOL30.NS"},
    }
    cat      = category.strip().lower()
    selected = {**groups["broad"],**groups["sector"],**groups["thematic"]} if cat=="all" else groups.get(cat, groups["sector"])
    header   = f"NIFTY — {cat.upper()}"
    out  = f"🇮🇳 {header}\n{'═'*60}\n"
    out += f"  {'Index':<24} {'Value':>10} {'Change':>10} {'%Chg':>8}\n"
    out += f"  {'─'*22} {'─'*10} {'─'*10} {'─'*8}\n"
    for name, sym in selected.items():
        try:
            hist = yf.Ticker(sym).history(period="5d")
            if hist.empty: out += f"  {name:<24} {'N/A':>10}\n"; continue
            last = hist["Close"].iloc[-1]
            prev = hist["Close"].iloc[-2] if len(hist)>1 else last
            ch   = last-prev; chp = ch/prev*100 if prev else 0
            out += f"  {name:<24} {last:>10,.2f} {sign(ch)}{ch:>9.2f} {sign(chp)}{chp:>6.2f}%  {arrow(ch)}\n"
        except: out += f"  {name:<24} {'Error':>10}\n"
    out += f"\n  {datetime.now().strftime('%d %b %Y %H:%M')} | Source: yfinance\n"
    return out


@tool
def get_stock_fundamentals(ticker: str) -> str:
    """Quick fundamental summary (P/E, EPS, margins, ROE, debt). Input: ticker."""
    import yfinance as yf
    symbol, market = resolve_ticker(ticker)
    try:
        info = yf.Ticker(symbol).info
        if not info.get("regularMarketPrice") and ".NS" in symbol:
            symbol=symbol.replace(".NS",".BO"); info=yf.Ticker(symbol).info
        cur = currency_sym(symbol)
        out  = f"📊 FUNDAMENTALS — {symbol} [{market}]\n{'═'*52}\n"
        out += f"  Company   : {info.get('longName','N/A')}\n  Sector    : {info.get('sector','N/A')}\n"
        out += f"  P/E TTM   : {fmt(info.get('trailingPE'))}  |  P/E Fwd: {fmt(info.get('forwardPE'))}\n"
        out += f"  P/B       : {fmt(info.get('priceToBook'))}  |  PEG: {fmt(info.get('pegRatio'))}\n"
        out += f"  EPS TTM   : {cur}{fmt(info.get('trailingEps'))}  |  EPS Fwd: {cur}{fmt(info.get('forwardEps'))}\n"
        out += f"  Revenue   : {human_number(info.get('totalRevenue'))}  |  EBITDA: {human_number(info.get('ebitda'))}\n"
        out += f"  Net Margin: {fmt((info.get('profitMargins') or 0)*100)}%  |  ROE: {fmt((info.get('returnOnEquity') or 0)*100)}%\n"
        out += f"  D/E Ratio : {fmt(info.get('debtToEquity'))}  |  Curr Ratio: {fmt(info.get('currentRatio'))}\n"
        out += f"  Div Yield : {fmt((info.get('dividendYield') or 0)*100)}%  |  Mkt Cap: {human_number(info.get('marketCap'))}\n"
        return out
    except Exception as e: return f"Error: {e}"


@tool
def get_price_history(ticker: str) -> str:
    """Multi-period returns and risk metrics (Sharpe, Max DD). Input: ticker."""
    import yfinance as yf
    import numpy as np
    symbol, market = resolve_ticker(ticker)
    try:
        df  = yf.Ticker(symbol).history(period="1y",interval="1d")
        if df.empty and ".NS" in symbol:
            symbol=symbol.replace(".NS",".BO"); df=yf.Ticker(symbol).history(period="1y",interval="1d")
        if df.empty: return f"No data for '{ticker}'."
        cur=currency_sym(symbol); close=df["Close"]; now=close.iloc[-1]
        def ret(d):
            try: p=close.iloc[-d] if d<len(close) else close.iloc[0]; r=(now-p)/p*100; return f"{sign(r)}{r:.2f}%"
            except: return "N/A"
        ytd=df[df.index.year==datetime.now().year]["Close"]
        ytd_r=((now-ytd.iloc[0])/ytd.iloc[0]*100) if not ytd.empty else 0
        rets=close.pct_change().dropna()
        ann_v=rets.std()*(252**0.5)*100
        sharp=(rets.mean()/rets.std())*(252**0.5) if rets.std()>0 else 0
        dd=(close/close.cummax()-1).min()*100
        out  = f"📅 PERFORMANCE — {symbol}\n{'═'*52}\n"
        out += f"  Current : {cur}{now:,.2f}\n"
        out += f"  1W:{ret(5)}  1M:{ret(21)}  3M:{ret(63)}  6M:{ret(126)}  YTD:{sign(ytd_r)}{ytd_r:.2f}%  1Y:{ret(252)}\n"
        out += f"  Range   : H:{cur}{close.max():,.2f}  L:{cur}{close.min():,.2f}  Avg:{cur}{close.mean():,.2f}\n"
        out += f"  Ann.Vol : {ann_v:.1f}%  Sharpe:{sharp:.2f}  Max DD:{dd:.2f}%\n"
        return out
    except Exception as e: return f"Error: {e}"


@tool
def compare_stocks_yf(tickers: str) -> str:
    """Side-by-side comparison of 2-4 stocks. Input: 'TCS, INFY, WIPRO' or 'AAPL vs MSFT'."""
    import yfinance as yf
    raw_list = [t.strip() for t in tickers.replace(" vs ",",").replace(" VS ",",").split(",") if t.strip()]
    if len(raw_list)<2: return "Provide at least 2 tickers."
    rows=[]
    for raw in raw_list[:4]:
        symbol, market = resolve_ticker(raw)
        try:
            info=yf.Ticker(symbol).info; cur=currency_sym(symbol)
            rows.append({"sym":symbol,"mkt":market,"cur":cur,
                "name":(info.get("shortName","") or symbol)[:20],
                "price":info.get("currentPrice") or info.get("regularMarketPrice"),
                "pe":info.get("trailingPE"),"fpe":info.get("forwardPE"),
                "pb":info.get("priceToBook"),"peg":info.get("pegRatio"),
                "eps":info.get("trailingEps"),"rev":info.get("totalRevenue"),
                "margin":info.get("profitMargins"),"roe":info.get("returnOnEquity"),
                "de":info.get("debtToEquity"),"mktcap":info.get("marketCap"),
                "div":info.get("dividendYield"),"52wh":info.get("fiftyTwoWeekHigh"),
                "52wl":info.get("fiftyTwoWeekLow"),"evebitda":info.get("enterpriseToEbitda"),
                "target":info.get("targetMeanPrice"),"rec":info.get("recommendationKey","N/A")})
        except Exception as e: rows.append({"sym":symbol,"mkt":market,"cur":"₹","error":str(e)})
    metrics=[("Price",      lambda r:f"{r['cur']}{fmt(r.get('price'))}"),
             ("Mkt Cap",    lambda r:human_number(r.get("mktcap"))),
             ("P/E TTM",    lambda r:fmt(r.get("pe"))),("P/E Fwd",  lambda r:fmt(r.get("fpe"))),
             ("PEG",        lambda r:fmt(r.get("peg"))),("P/B",     lambda r:fmt(r.get("pb"))),
             ("EV/EBITDA",  lambda r:fmt(r.get("evebitda"))),
             ("EPS TTM",    lambda r:f"{r['cur']}{fmt(r.get('eps'))}"),
             ("Revenue",    lambda r:human_number(r.get("rev"))),
             ("Net Margin", lambda r:f"{fmt((r.get('margin') or 0)*100)}%"),
             ("ROE",        lambda r:f"{fmt((r.get('roe') or 0)*100)}%"),
             ("Debt/Equity",lambda r:fmt(r.get("de"))),
             ("Div Yield",  lambda r:f"{fmt((r.get('div') or 0)*100)}%"),
             ("52W High",   lambda r:f"{r['cur']}{fmt(r.get('52wh'))}"),
             ("52W Low",    lambda r:f"{r['cur']}{fmt(r.get('52wl'))}"),
             ("Analyst",    lambda r:r.get("rec","N/A").upper()),
             ("Target",     lambda r:f"{r['cur']}{fmt(r.get('target'))}")]
    out  = f"⚖️  COMPARISON — {' | '.join(r['sym'] for r in rows)}\n{'═'*64}\n"
    out += f"  {'Metric':<14}" + "".join(f"{r['sym']:<18}" for r in rows) + "\n"
    out += f"  {'─'*14}" + "─"*18*len(rows) + "\n"
    for label, fn in metrics:
        line = f"  {label:<14}"
        for r in rows:
            if "error" in r: line += f"{'ERR':<18}"
            else:
                try: line += f"{fn(r):<18}"
                except: line += f"{'N/A':<18}"
        out += line+"\n"
    return out


@tool
def get_market_overview(market: str) -> str:
    """Live market overview. Input: india, nse, us, global, vix"""
    import yfinance as yf
    INDICES={
        "india":[("^NSEI","Nifty 50"),("^BSESN","Sensex"),("^NSEBANK","Bank Nifty"),
                 ("^CNXIT","Nifty IT"),("^CNXAUTO","Nifty Auto"),("^CNXFMCG","Nifty FMCG"),
                 ("^CNXPHARMA","Nifty Pharma"),("^INDIAVIX","India VIX")],
        "nse"  :[("^NSEI","Nifty 50"),("^BSESN","Sensex"),("^NSEBANK","Bank Nifty"),
                 ("^CNXIT","Nifty IT"),("^INDIAVIX","India VIX")],
        "us"   :[("^GSPC","S&P 500"),("^IXIC","NASDAQ"),("^DJI","Dow Jones"),("^RUT","Russell 2000"),("^VIX","CBOE VIX")],
        "global":[("^NSEI","Nifty 50"),("^BSESN","Sensex"),("^GSPC","S&P 500"),("^IXIC","NASDAQ"),("^INDIAVIX","India VIX"),("^VIX","US VIX")],
        "vix"  :[("^INDIAVIX","India VIX"),("^VIX","CBOE VIX")],
    }
    key=market.lower().strip(); pairs=INDICES.get(key, INDICES["global"])
    out=f"🌐 MARKET OVERVIEW — {market.upper()}\n{'═'*52}\n"
    out+=f"  {'Index':<22} {'Value':>10} {'Chg':>10} {'%Chg':>8}\n"
    out+=f"  {'─'*20} {'─'*10} {'─'*10} {'─'*8}\n"
    for sym, name in pairs:
        try:
            hist=yf.Ticker(sym).history(period="5d")
            if hist.empty: out+=f"  {name:<22} {'N/A':>10}\n"; continue
            last=hist["Close"].iloc[-1]; prev=hist["Close"].iloc[-2] if len(hist)>1 else last
            ch=last-prev; chp=ch/prev*100 if prev else 0
            out+=f"  {name:<22} {last:>10,.2f} {sign(ch)}{ch:>9.2f} {sign(chp)}{chp:>6.2f}%  {arrow(ch)}\n"
        except: out+=f"  {name:<22} {'Error':>10}\n"
    out+=f"\n  {datetime.now().strftime('%d %b %Y %H:%M')} | yfinance\n"
    return out


@tool
def search_stock_news(query: str) -> str:
    """
    Latest stock/market news via DuckDuckGo + ET/Moneycontrol RSS.
    Input: query (e.g. 'RELIANCE news', 'Nifty IT outlook', 'RBI policy impact')
    """
    try:
        from duckduckgo_search import DDGS
        import urllib.request, xml.etree.ElementTree as ET
        results = DDGS().text(f"{query} India stock market 2025", max_results=5)
        out = f"📰 NEWS — '{query}'\n{'═'*56}\n\n"
        if results:
            out += "🔎 [Web Results]\n"
            for i, r in enumerate(results, 1):
                out += f"  {i}. {r.get('title','')}\n     🔗 {r.get('href','')}\n     📝 {r.get('body','')[:200]}\n\n"
        for feed_name, url in [("Economic Times","https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms"),
                                 ("Moneycontrol","https://www.moneycontrol.com/rss/latestnews.xml")]:
            try:
                req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"})
                with urllib.request.urlopen(req,timeout=5) as resp: tree=ET.parse(resp)
                items=tree.getroot().findall(".//item")[:3]
                if items:
                    out+=f"\n📡 [{feed_name} RSS]\n"
                    for item in items:
                        out+=f"  • {(item.findtext('title') or '').strip()}\n    {(item.findtext('description') or '')[:150].strip()}\n\n"
            except: pass
        return out
    except Exception as e: return f"Error: {e}"


@tool
def search_macro_news(topic: str) -> str:
    """Macro news: RBI, FII/DII flows, inflation, budget, USD/INR, crude oil."""
    try:
        from duckduckgo_search import DDGS
        results = DDGS().text(f"{topic} India economy 2025", max_results=6)
        out = f"🌏 MACRO — '{topic}'\n{'═'*52}\n\n"
        for i, r in enumerate(results, 1):
            out += f"  {i}. {r.get('title','')}\n     📝 {r.get('body','')[:250]}\n\n"
        return out
    except Exception as e: return f"Error: {e}"


@tool
def search_sector_analysis(sector: str) -> str:
    """Sector research and industry outlook. Input: sector name."""
    try:
        from duckduckgo_search import DDGS
        results = DDGS().text(f"{sector} sector India analysis outlook 2025", max_results=6)
        out = f"🏭 SECTOR — '{sector}'\n{'═'*52}\n\n"
        for i, r in enumerate(results, 1):
            out += f"  {i}. {r.get('title','')}\n     📝 {r.get('body','')[:250]}\n\n"
        return out
    except Exception as e: return f"Error: {e}"


@tool
def search_ipo_and_corporate_actions(query: str) -> str:
    """IPO news, dividends, buybacks, bonus, stock splits. Input: query."""
    try:
        from duckduckgo_search import DDGS
        results = DDGS().text(f"{query} NSE BSE India 2025", max_results=6)
        out = f"🏢 CORPORATE — '{query}'\n{'═'*52}\n\n"
        for i, r in enumerate(results, 1):
            out += f"  {i}. {r.get('title','')}\n     📝 {r.get('body','')[:250]}\n\n"
        return out
    except Exception as e: return f"Error: {e}"


# ══════════════════════════════════════════════════════════════════════════════
# GLOBAL MACRO DASHBOARD — Crude Oil, Gold, Silver, DXY, Currencies
# ══════════════════════════════════════════════════════════════════════════════
@tool
def get_global_macro_dashboard(category: str = "all") -> str:
    """
    Live dashboard of global macro indicators that directly impact Indian markets:
    Crude Oil (WTI + Brent), Gold, Silver, Copper, Dollar Index (DXY),
    USD/INR, EUR/USD, USD/JPY, Natural Gas.
    Categories: 'commodities', 'currencies', 'energy', 'metals', 'all'
    Input: category string (default: 'all')

    How these affect Indian markets:
    - Crude Oil ↑ → Inflation ↑, CAD widens, ONGC/BPCL/IOC impacted
    - Gold ↑     → Safe-haven demand, Titan/Kalyan/jewellery stocks
    - DXY ↑      → INR weakens, FII outflows, IT stocks (hedge) benefit
    - USD/INR ↑  → Import costs ↑, exporters (IT, Pharma) benefit
    - Copper ↑   → Industrial demand signal, Metal/Infra stocks
    """
    import yfinance as yf

    MACRO_GROUPS = {
        "energy": {
            "Crude Oil WTI ($/bbl)" : "CL=F",
            "Crude Oil Brent ($/bbl)": "BZ=F",
            "Natural Gas ($/MMBtu)"  : "NG=F",
        },
        "metals": {
            "Gold ($/oz)"            : "GC=F",
            "Silver ($/oz)"          : "SI=F",
            "Copper ($/lb)"          : "HG=F",
            "Platinum ($/oz)"        : "PL=F",
        },
        "currencies": {
            "Dollar Index (DXY)"     : "DX-Y.NYB",
            "USD/INR"                : "USDINR=X",
            "EUR/USD"                : "EURUSD=X",
            "GBP/USD"                : "GBPUSD=X",
            "USD/JPY"                : "JPY=X",
            "USD/CNY"                : "CNY=X",
        },
    }

    cat = category.strip().lower()
    if cat == "commodities":
        selected = {**MACRO_GROUPS["energy"], **MACRO_GROUPS["metals"]}
        header = "COMMODITIES"
    elif cat in MACRO_GROUPS:
        selected = MACRO_GROUPS[cat]
        header = cat.upper()
    else:
        selected = {**MACRO_GROUPS["energy"], **MACRO_GROUPS["metals"], **MACRO_GROUPS["currencies"]}
        header = "ALL MACRO INDICATORS"

    out  = f"\n🌍 GLOBAL MACRO DASHBOARD — {header}\n{'═'*62}\n"
    out += f"  {'Instrument':<28} {'Price':>12} {'Change':>10} {'%Chg':>8}  Trend\n"
    out += f"  {'─'*26} {'─'*12} {'─'*10} {'─'*8}  {'─'*8}\n"

    for name, sym in selected.items():
        try:
            hist = yf.Ticker(sym).history(period="5d")
            if hist.empty:
                out += f"  {name:<28} {'N/A':>12}\n"
                continue
            last = hist["Close"].iloc[-1]
            prev = hist["Close"].iloc[-2] if len(hist) > 1 else last
            ch   = last - prev
            chp  = ch / prev * 100 if prev else 0
            week_ago = hist["Close"].iloc[0]
            wret = (last - week_ago) / week_ago * 100
            trend = "▲" if ch >= 0 else "▼"
            out  += f"  {name:<28} {last:>12,.3f} {sign(ch)}{ch:>9.3f} {sign(chp)}{chp:>6.2f}%  {trend} W:{sign(wret)}{wret:.1f}%\n"
        except:
            out += f"  {name:<28} {'Error':>12}\n"

    # Contextual interpretation
    out += f"\n  {'═'*60}\n"
    out += f"  📌 MARKET IMPACT GUIDE\n"
    out += f"  {'─'*60}\n"

    # Fetch crude and DXY for live interpretation
    try:
        crude_hist = yf.Ticker("CL=F").history(period="5d")
        dxy_hist   = yf.Ticker("DX-Y.NYB").history(period="5d")
        usdinr_h   = yf.Ticker("USDINR=X").history(period="5d")
        gold_hist  = yf.Ticker("GC=F").history(period="5d")

        crude = crude_hist["Close"].iloc[-1] if not crude_hist.empty else 0
        dxy   = dxy_hist["Close"].iloc[-1]   if not dxy_hist.empty   else 0
        usdinr= usdinr_h["Close"].iloc[-1]   if not usdinr_h.empty   else 0
        gold  = gold_hist["Close"].iloc[-1]  if not gold_hist.empty  else 0

        crude_chgp = (crude_hist["Close"].iloc[-1] - crude_hist["Close"].iloc[-2]) / crude_hist["Close"].iloc[-2] * 100 if len(crude_hist) > 1 else 0
        dxy_chgp   = (dxy_hist["Close"].iloc[-1]   - dxy_hist["Close"].iloc[-2])   / dxy_hist["Close"].iloc[-2]   * 100 if len(dxy_hist)   > 1 else 0

        out += f"\n  🛢️  CRUDE OIL @ ${crude:.2f}/bbl  ({sign(crude_chgp)}{crude_chgp:.2f}% today)\n"
        if crude < 70:
            out += f"     → LOW crude: Inflation relief 🟢 | OMC (BPCL/IOC/HPCL) margins improve 🟢\n"
            out += f"     → CAD pressure eases 🟢 | Freight/logistics costs fall 🟢\n"
        elif crude < 85:
            out += f"     → MODERATE crude: Neutral for India 🟡 | Watch for OMC under-recoveries\n"
        else:
            out += f"     → HIGH crude: Inflation risk 🔴 | OMC under-recovery risk 🔴\n"
            out += f"     → CAD widens 🔴 | INR depreciation pressure 🔴 | ONGC/OIL India benefit 🟢\n"

        out += f"\n  💰 GOLD @ ${gold:.0f}/oz\n"
        if gold > 2400:
            out += f"     → HIGH gold: Safe-haven demand 🔴 global risk-off | Titan/Kalyan/jewellery\n"
        elif gold > 1900:
            out += f"     → ELEVATED gold: Mild safe-haven | Positive for gold ETFs and jewellers\n"
        else:
            out += f"     → MODERATE gold: Risk-on environment 🟢 | Equities preferred over gold\n"

        out += f"\n  💵 DOLLAR INDEX @ {dxy:.2f}  ({sign(dxy_chgp)}{dxy_chgp:.2f}% today)\n"
        if dxy > 105:
            out += f"     → STRONG DXY: FII outflow pressure on India 🔴 | INR weakness 🔴\n"
            out += f"     → IT/Pharma exporters benefit from INR depreciation 🟢\n"
        elif dxy > 100:
            out += f"     → FIRM DXY: Moderate FII pressure | Watch USD/INR closely\n"
        else:
            out += f"     → WEAK DXY: FII inflows into EMs including India 🟢 | INR supportive 🟢\n"

        out += f"\n  🇮🇳 USD/INR @ ₹{usdinr:.2f}\n"
        if usdinr > 86:
            out += f"     → WEAK INR: Import inflation 🔴 | IT/Pharma exporters benefit 🟢\n"
        elif usdinr > 83:
            out += f"     → STABLE INR: Balanced macro environment 🟡\n"
        else:
            out += f"     → STRONG INR: Import costs lower 🟢 | FII inflows supportive 🟢\n"

    except:
        out += f"  (Live interpretation unavailable)\n"

    out += f"\n  Data: yfinance | {datetime.now().strftime('%d %b %Y %H:%M IST')}\n"
    return out


# ══════════════════════════════════════════════════════════════════════════════
# US MARKETS & FUTURES DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
@tool
def get_us_markets_and_futures(mode: str = "all") -> str:
    """
    Live US equity markets + pre-market/after-hours futures dashboard.
    Shows S&P 500, NASDAQ, Dow Jones, Russell 2000 with technicals +
    ES (S&P Futures), NQ (NASDAQ Futures), YM (Dow Futures), RTY (Russell Futures).
    Also shows US sector ETFs and key stocks.
    Modes: 'indices', 'futures', 'sectors', 'all'
    Input: mode string (default: 'all')

    Critical for Indian market pre-opening context:
    - US futures UP → Indian markets likely to open GAP UP
    - US futures DOWN → Indian markets likely to open GAP DOWN
    - VIX spike → Risk-off globally, Indian markets fall
    """
    import yfinance as yf

    out = f"\n🇺🇸 US MARKETS & FUTURES\n{'═'*64}\n"
    out += f"  {datetime.now().strftime('%d %b %Y %H:%M UTC')}\n\n"

    if mode in ("indices", "all"):
        out += f"  [CASH INDICES]\n"
        out += f"  {'Index':<22} {'Last':>10} {'Chg':>10} {'%Chg':>8}  52W Pos\n"
        out += f"  {'─'*20} {'─'*10} {'─'*10} {'─'*8}  {'─'*10}\n"
        US_INDICES = {
            "S&P 500"       : "^GSPC",
            "NASDAQ Comp"   : "^IXIC",
            "NASDAQ-100"    : "^NDX",
            "Dow Jones"     : "^DJI",
            "Russell 2000"  : "^RUT",
            "CBOE VIX"      : "^VIX",
        }
        for name, sym in US_INDICES.items():
            try:
                tk   = yf.Ticker(sym)
                hist = tk.history(period="1y")
                if hist.empty: out += f"  {name:<22} {'N/A':>10}\n"; continue
                last = hist["Close"].iloc[-1]
                prev = hist["Close"].iloc[-2]
                ch   = last - prev; chp = ch / prev * 100
                hi52 = hist["Close"].max(); lo52 = hist["Close"].min()
                pos  = (last - lo52) / (hi52 - lo52) * 100 if hi52 != lo52 else 50
                out += f"  {name:<22} {last:>10,.2f} {sign(ch)}{ch:>9.2f} {sign(chp)}{chp:>6.2f}%  {pos:4.0f}% of 52W\n"
            except:
                out += f"  {name:<22} {'Error':>10}\n"

    if mode in ("futures", "all"):
        out += f"\n  [US FUTURES  — Pre-market / Overnight]\n"
        out += f"  {'Contract':<24} {'Last':>10} {'Chg':>10} {'%Chg':>8}  Signal\n"
        out += f"  {'─'*22} {'─'*10} {'─'*10} {'─'*8}  {'─'*12}\n"
        FUTURES = {
            "ES (S&P500 Fut)"   : "ES=F",
            "NQ (NASDAQ Fut)"   : "NQ=F",
            "YM (Dow Fut)"      : "YM=F",
            "RTY (Russell Fut)" : "RTY=F",
            "VX (VIX Fut)"      : "VX=F",
            "ZB (30Y T-Bond)"   : "ZB=F",
            "ZN (10Y T-Note)"   : "ZN=F",
        }
        for name, sym in FUTURES.items():
            try:
                hist = yf.Ticker(sym).history(period="5d")
                if hist.empty: out += f"  {name:<24} {'N/A':>10}\n"; continue
                last = hist["Close"].iloc[-1]
                prev = hist["Close"].iloc[-2] if len(hist) > 1 else last
                ch   = last - prev; chp = ch / prev * 100
                sig  = "GAP UP likely 🟢" if chp > 0.5 else ("GAP DOWN likely 🔴" if chp < -0.5 else "Flat open ⚪")
                out += f"  {name:<24} {last:>10,.2f} {sign(ch)}{ch:>9.2f} {sign(chp)}{chp:>6.2f}%  {sig}\n"
            except:
                out += f"  {name:<24} {'Error':>10}\n"

    if mode in ("sectors", "all"):
        out += f"\n  [US SECTOR ETFs]\n"
        out += f"  {'ETF':<24} {'Name':<22} {'Last':>8} {'1D%':>7}  {'1W%':>7}\n"
        out += f"  {'─'*22} {'─'*20} {'─'*8} {'─'*7}  {'─'*7}\n"
        SECTOR_ETFS = {
            "XLK" : "Technology",  "XLF" : "Financials",  "XLE" : "Energy",
            "XLV" : "Healthcare",  "XLI" : "Industrials", "XLY" : "Cons. Discret",
            "XLP" : "Cons. Staples","XLU" : "Utilities",   "XLB" : "Materials",
            "XLRE": "Real Estate",  "XLC" : "Comm. Svcs",  "GLD" : "Gold ETF",
            "SLV" : "Silver ETF",   "USO" : "Oil ETF",     "TLT" : "20Y Bond ETF",
        }
        for sym, name in SECTOR_ETFS.items():
            try:
                hist = yf.Ticker(sym).history(period="10d")
                if hist.empty or len(hist) < 2: out += f"  {sym:<24} {name:<22} {'N/A':>8}\n"; continue
                last = hist["Close"].iloc[-1]; prev = hist["Close"].iloc[-2]
                week = hist["Close"].iloc[0]
                d1 = (last - prev) / prev * 100; w1 = (last - week) / week * 100
                out += f"  {sym:<24} {name:<22} {last:>8,.2f} {sign(d1)}{d1:>5.2f}%  {sign(w1)}{w1:>5.2f}%\n"
            except:
                out += f"  {sym:<24} {name:<22} {'Error':>8}\n"

    # Indian market pre-open context
    out += f"\n  {'═'*62}\n"
    out += f"  📌 INDIAN MARKET PRE-OPEN CONTEXT\n"
    out += f"  {'─'*62}\n"
    try:
        es_h   = yf.Ticker("ES=F").history(period="5d")
        vix_h  = yf.Ticker("^VIX").history(period="5d")
        dxy_h  = yf.Ticker("DX-Y.NYB").history(period="5d")
        cl_h   = yf.Ticker("CL=F").history(period="5d")

        es_chgp  = (es_h["Close"].iloc[-1]  - es_h["Close"].iloc[-2])  / es_h["Close"].iloc[-2]  * 100 if len(es_h)  > 1 else 0
        vix_val  = vix_h["Close"].iloc[-1]  if not vix_h.empty  else 0
        dxy_chgp = (dxy_h["Close"].iloc[-1] - dxy_h["Close"].iloc[-2]) / dxy_h["Close"].iloc[-2] * 100 if len(dxy_h) > 1 else 0
        cl_chgp  = (cl_h["Close"].iloc[-1]  - cl_h["Close"].iloc[-2])  / cl_h["Close"].iloc[-2]  * 100 if len(cl_h)  > 1 else 0

        # Overall signal
        bull_signals = 0
        bear_signals = 0

        if es_chgp > 0.3:   bull_signals += 2
        elif es_chgp < -0.3: bear_signals += 2

        if vix_val < 15:    bull_signals += 1
        elif vix_val > 20:  bear_signals += 2
        elif vix_val > 25:  bear_signals += 3

        if dxy_chgp > 0.3:  bear_signals += 1
        elif dxy_chgp < -0.3: bull_signals += 1

        if cl_chgp < -2:    bull_signals += 1
        elif cl_chgp > 3:   bear_signals += 1

        total = bull_signals + bear_signals
        if total > 0:
            bull_pct = bull_signals / total * 100
        else:
            bull_pct = 50

        if bull_pct >= 70:   overall = "BULLISH OPEN LIKELY 🟢🟢"
        elif bull_pct >= 55: overall = "MILD BULLISH OPEN 🟢"
        elif bull_pct >= 45: overall = "NEUTRAL / FLAT OPEN ⚪"
        elif bull_pct >= 30: overall = "MILD BEARISH OPEN 🔴"
        else:                overall = "BEARISH OPEN LIKELY 🔴🔴"

        out += f"\n  S&P Futures : {sign(es_chgp)}{es_chgp:.2f}%  |  VIX: {vix_val:.2f}  |  DXY: {sign(dxy_chgp)}{dxy_chgp:.2f}%  |  Crude: {sign(cl_chgp)}{cl_chgp:.2f}%\n"
        out += f"  ┌─────────────────────────────────────────────────────────┐\n"
        out += f"  │  Indian Market Pre-Open Signal : {overall:<26}│\n"
        out += f"  │  Bull Score: {bull_signals}  Bear Score: {bear_signals}  Confidence: {bull_pct:.0f}%       │\n"
        out += f"  └─────────────────────────────────────────────────────────┘\n"

        out += f"\n  Factor Analysis:\n"
        out += f"  {'Factor':<25} {'Value':>10}  Impact on India\n"
        out += f"  {'─'*23} {'─'*10}  {'─'*25}\n"
        out += f"  {'S&P500 Futures':<25} {sign(es_chgp)}{es_chgp:>8.2f}%  {'Positive 🟢' if es_chgp>0 else 'Negative 🔴'} (sentiment)\n"
        out += f"  {'CBOE VIX':<25} {vix_val:>10.2f}  {'High fear 🔴' if vix_val>20 else ('Elevated ⚠️' if vix_val>15 else 'Calm 🟢')}\n"
        out += f"  {'Dollar Index':<25} {sign(dxy_chgp)}{dxy_chgp:>8.2f}%  {'FII outflow risk 🔴' if dxy_chgp>0.3 else ('FII inflow 🟢' if dxy_chgp<-0.3 else 'Neutral ⚪')}\n"
        out += f"  {'Crude Oil WTI':<25} {sign(cl_chgp)}{cl_chgp:>8.2f}%  {'Inflation risk 🔴' if cl_chgp>2 else ('CAD relief 🟢' if cl_chgp<-2 else 'Neutral ⚪')}\n"
    except:
        out += f"  (Pre-open context unavailable)\n"

    return out


# ══════════════════════════════════════════════════════════════════════════════
# MACRO IMPACT ANALYSIS — How global factors affect a specific stock/sector
# ══════════════════════════════════════════════════════════════════════════════
@tool
def get_macro_impact_analysis(ticker: str) -> str:
    """
    Analyses how current global macro factors (crude oil, gold, DXY, US markets,
    bond yields, USD/INR) specifically impact a given Indian stock or sector.
    Provides sensitivity analysis and what to watch.
    Input: ticker or sector name (RELIANCE, ONGC, INFY, TCS, TATASTEEL,
           SUNPHARMA, HDFCBANK, BANKNIFTY, NIFTYIT, NIFTYENERGY …)
    """
    import yfinance as yf

    raw = ticker.strip().upper()
    symbol, market = resolve_ticker(ticker)

    # Fetch all macro factors
    macro = {}
    macro_syms = {
        "crude" : "CL=F",  "brent"  : "BZ=F",
        "gold"  : "GC=F",  "silver" : "SI=F",
        "dxy"   : "DX-Y.NYB", "usdinr": "USDINR=X",
        "sp500" : "^GSPC",    "vix"   : "^VIX",
        "us10yr": "^TNX",     "natgas": "NG=F",
    }
    for key, sym in macro_syms.items():
        try:
            h = yf.Ticker(sym).history(period="5d")
            if not h.empty:
                last = h["Close"].iloc[-1]
                prev = h["Close"].iloc[-2] if len(h) > 1 else last
                macro[key] = {"val": last, "chgp": (last - prev) / prev * 100 if prev else 0}
        except:
            macro[key] = {"val": 0, "chgp": 0}

    def mv(k): return macro.get(k, {}).get("val", 0)
    def mc(k): return macro.get(k, {}).get("chgp", 0)

    # Determine sector sensitivity based on ticker
    sector_map = {
        # Oil & Gas
        "ONGC":"OilGas","BPCL":"OMC","IOC":"OMC","HINDPETRO":"OMC","GAIL":"OilGas",
        "RELIANCE":"Conglomerate","PETRONET":"OilGas","MGL":"OilGas",
        # IT / Tech
        "TCS":"IT","INFY":"IT","WIPRO":"IT","HCLTECH":"IT","TECHM":"IT",
        "LTIM":"IT","MPHASIS":"IT","PERSISTENT":"IT","COFORGE":"IT",
        # Pharma
        "SUNPHARMA":"Pharma","DRREDDY":"Pharma","CIPLA":"Pharma",
        "DIVISLAB":"Pharma","LUPIN":"Pharma","AUROPHARMA":"Pharma",
        # Banking
        "HDFCBANK":"Banking","ICICIBANK":"Banking","SBIN":"PSUBank",
        "AXISBANK":"Banking","KOTAKBANK":"Banking","BANKNIFTY":"Banking",
        "INDUSINDBANK":"Banking","BANKBARODA":"PSUBank","PNB":"PSUBank",
        # Metal
        "TATASTEEL":"Metal","JSWSTEEL":"Metal","HINDALCO":"Metal",
        "VEDL":"Metal","COALINDIA":"Metal","NIFTYMETAL":"Metal",
        # Auto
        "MARUTI":"Auto","TATAMOTORS":"Auto","M&M":"Auto","BAJAJ-AUTO":"Auto",
        "EICHERMOT":"Auto","HEROMOTOCO":"Auto","NIFTYAUTO":"Auto",
        # FMCG
        "HINDUNILVR":"FMCG","ITC":"FMCG","NESTLE":"FMCG","BRITANNIA":"FMCG",
        "DABUR":"FMCG","MARICO":"FMCG","NIFTYFMCG":"FMCG",
        # Jewellery/Gold
        "TITAN":"Gold","KALYANKJIL":"Gold","SENCO":"Gold","RAJESHEXPO":"Gold",
        # Realty
        "NIFTYREALTY":"Realty","DLF":"Realty","GODREJPROP":"Realty",
    }

    # Determine sector
    sec = "General"
    for k, v in sector_map.items():
        if k in raw or raw in k:
            sec = v; break
    # Also check index map
    if "IT" in raw or raw in ("NIFTYIT",): sec = "IT"
    if "ENERGY" in raw: sec = "OilGas"
    if "BANK" in raw:   sec = "Banking"
    if "METAL" in raw:  sec = "Metal"
    if "PHARMA" in raw: sec = "Pharma"
    if "AUTO" in raw:   sec = "Auto"
    if "FMCG" in raw:   sec = "FMCG"

    out  = f"\n🌍 MACRO IMPACT ANALYSIS — {raw} ({sec} Sector)\n{'═'*64}\n"
    out += f"\n  [CURRENT MACRO SNAPSHOT]\n"
    out += f"  {'Factor':<22} {'Value':>10} {'1D Chg':>9}  Status\n"
    out += f"  {'─'*20} {'─'*10} {'─'*9}  {'─'*20}\n"

    macro_display = [
        ("Crude Oil WTI",   "crude",  "$/bbl"),
        ("Brent Crude",     "brent",  "$/bbl"),
        ("Gold",            "gold",   "$/oz"),
        ("Silver",          "silver", "$/oz"),
        ("Dollar Index",    "dxy",    "pts"),
        ("USD/INR",         "usdinr", "₹"),
        ("S&P 500",         "sp500",  "pts"),
        ("US VIX",          "vix",    "pts"),
        ("US 10Y Yield",    "us10yr", "%"),
        ("Natural Gas",     "natgas", "$/MMBtu"),
    ]
    for label, key, unit in macro_display:
        v = mv(key); c = mc(key)
        status = "▲ Rising" if c > 0.3 else ("▼ Falling" if c < -0.3 else "── Stable")
        out += f"  {label:<22} {v:>10.3f} {sign(c)}{c:>7.2f}%  {status}\n"

    # Sector-specific sensitivity analysis
    out += f"\n  {'═'*62}\n"
    out += f"  📊 SECTOR SENSITIVITY — {sec}\n"
    out += f"  {'─'*62}\n"

    crude  = mv("crude"); crude_c = mc("crude")
    gold   = mv("gold");  gold_c  = mc("gold")
    dxy    = mv("dxy");   dxy_c   = mc("dxy")
    usdinr = mv("usdinr"); usdinr_c = mc("usdinr")
    sp500  = mv("sp500"); sp500_c = mc("sp500")
    vix    = mv("vix")
    us10yr = mv("us10yr")

    if sec == "IT":
        out += f"\n  IT sector has HIGH sensitivity to USD/INR and US tech demand.\n"
        out += f"\n  USD/INR @ ₹{usdinr:.2f} ({sign(usdinr_c)}{usdinr_c:.2f}%)\n"
        if usdinr_c > 0.3:
            out += f"    → INR weakening 🟢 POSITIVE: Boosts IT revenue in INR terms\n"
            out += f"    → Every 1% INR depreciation adds ~1-1.5% to IT revenue\n"
        else:
            out += f"    → INR strengthening 🔴 NEGATIVE: Reduces IT revenue in INR terms\n"
        out += f"\n  S&P 500 / NASDAQ ({sign(sp500_c)}{sp500_c:.2f}%)\n"
        if sp500_c > 0:
            out += f"    → US markets up 🟢: IT discretionary spending expected to hold\n"
        else:
            out += f"    → US markets down 🔴: Risk of IT deal delays / budget cuts\n"
        out += f"\n  US 10Y Yield @ {us10yr:.2f}%\n"
        if us10yr > 4.5:
            out += f"    → HIGH US yields 🔴: FII selling pressure, growth stock valuation hit\n"
        else:
            out += f"    → MODERATE yields 🟢: FII flows supportive\n"
        out += f"\n  DXY @ {dxy:.2f} ({sign(dxy_c)}{dxy_c:.2f}%)\n"
        if dxy_c > 0.3:
            out += f"    → Strong USD 🔴: FII outflow risk from India | INR depreciation\n"
        else:
            out += f"    → Weak USD 🟢: FII inflows into EM; INR strengthens\n"

    elif sec in ("OilGas", "OMC"):
        out += f"\n  Oil & Gas sector has VERY HIGH sensitivity to crude oil prices.\n"
        out += f"\n  WTI Crude @ ${crude:.2f}/bbl ({sign(crude_c)}{crude_c:.2f}%)\n"
        if sec == "OMC":
            if crude_c > 2:
                out += f"    → Crude RISING 🔴: Under-recovery risk for OMCs (BPCL/IOC/HPCL)\n"
                out += f"    → Margin compression unless retail fuel prices hiked\n"
            elif crude_c < -2:
                out += f"    → Crude FALLING 🟢: Under-recovery eases for OMCs\n"
                out += f"    → Marketing margins improve; positive for BPCL/IOC\n"
        else:
            if crude_c > 0:
                out += f"    → Crude RISING 🟢: Direct revenue benefit for ONGC/OIL India\n"
                out += f"    → E&P companies benefit from higher realisation\n"
            else:
                out += f"    → Crude FALLING 🔴: Realisation pressure on E&P companies\n"
        out += f"\n  USD/INR @ ₹{usdinr:.2f}: {'Crude imports costlier 🔴' if usdinr_c>0 else 'Import cost relief 🟢'}\n"
        out += f"\n  Natural Gas ({sign(mc('natgas'))}{mc('natgas'):.2f}%): {'Higher input cost 🔴' if mc('natgas')>2 else ('Input cost relief 🟢' if mc('natgas')<-2 else 'Stable ⚪')}\n"

    elif sec == "Metal":
        out += f"\n  Metal sector has HIGH sensitivity to global industrial demand.\n"
        out += f"\n  Copper ({sign(mc('silver'))}{mc('silver'):.2f}%): Leading industrial demand indicator\n"
        if sp500_c > 0:
            out += f"    → US markets UP 🟢: Global growth expectations supportive for metals\n"
        else:
            out += f"    → US markets DOWN 🔴: Demand destruction fears; metal prices at risk\n"
        out += f"\n  Gold @ ${gold:.0f}/oz ({sign(gold_c)}{gold_c:.2f}%)\n"
        if gold_c > 1:
            out += f"    → Gold RISING: Safe-haven bid; often inversely correlated with base metals\n"
        out += f"\n  USD/INR ({sign(usdinr_c)}{usdinr_c:.2f}%): {'Import cost relief 🟢 for steel' if usdinr_c<0 else 'Export competitiveness 🟢' if usdinr_c>0 else 'Neutral ⚪'}\n"
        out += f"\n  China demand proxy via Copper + Shanghai PMI key watch factor\n"

    elif sec == "Pharma":
        out += f"\n  Pharma sector has MODERATE sensitivity to USD/INR (export focus).\n"
        out += f"\n  USD/INR @ ₹{usdinr:.2f} ({sign(usdinr_c)}{usdinr_c:.2f}%)\n"
        if usdinr_c > 0.3:
            out += f"    → INR weakening 🟢: Revenue boost for pharma exporters (US generic biz)\n"
            out += f"    → ~60-70% of Indian pharma revenues are USD-denominated\n"
        else:
            out += f"    → INR strengthening 🔴: Export revenue headwind\n"
        out += f"\n  US Healthcare ETF (XLV) performance key for sentiment\n"
        out += f"\n  US VIX @ {vix:.2f}: {'Risk-off; defensive pharma may outperform 🟢' if vix>20 else 'Risk-on; cyclicals preferred 🟡'}\n"

    elif sec == "Banking":
        out += f"\n  Banking sector has HIGH sensitivity to yields, liquidity, and macro.\n"
        out += f"\n  US 10Y Yield @ {us10yr:.2f}%\n"
        if us10yr > 4.5:
            out += f"    → HIGH yields: Bond mark-to-market losses; FII outflows 🔴\n"
            out += f"    → Domestic NIM pressure if RBI follows global tightening\n"
        else:
            out += f"    → LOW yields: FII inflows; banking sector attractive 🟢\n"
        out += f"\n  VIX @ {vix:.2f}: {'Risk-off 🔴 — Loan growth concerns, NPA risks' if vix>20 else 'Calm 🟢 — Credit growth positive'}\n"
        out += f"\n  USD/INR ({sign(usdinr_c)}{usdinr_c:.2f}%): {'INR weakness may prompt RBI intervention; liquidity tightening risk 🔴' if usdinr_c>0.5 else 'Stable INR supportive for banking 🟢'}\n"
        out += f"\n  DXY ({sign(dxy_c)}{dxy_c:.2f}%): {'FII selling risk 🔴' if dxy_c>0.3 else 'FII buying supportive 🟢'}\n"

    elif sec in ("Auto",):
        out += f"\n  Auto sector sensitive to crude oil, currency, and consumer sentiment.\n"
        out += f"\n  Crude Oil ({sign(crude_c)}{crude_c:.2f}%): {'High fuel cost → EV shift, lower ICE demand 🔴' if crude_c>2 else ('Fuel cost relief 🟢 → supports ICE demand' if crude_c<-2 else 'Neutral ⚪')}\n"
        out += f"\n  USD/INR ({sign(usdinr_c)}{usdinr_c:.2f}%): {'Import parts costlier 🔴 — semicond., EV batteries' if usdinr_c>0 else 'Import cost relief 🟢'}\n"
        out += f"\n  S&P 500 ({sign(sp500_c)}{sp500_c:.2f}%): {'Global risk-on 🟢 — export-oriented autos (JLR-Tata) benefit' if sp500_c>0 else 'Global slowdown risk 🔴'}\n"

    elif sec == "FMCG":
        out += f"\n  FMCG sector sensitive to input costs (crude derivatives, gold) and INR.\n"
        out += f"\n  Crude Oil ({sign(crude_c)}{crude_c:.2f}%): {'Input cost pressure 🔴 — packaging, palm oil' if crude_c>2 else ('Input cost relief 🟢' if crude_c<-2 else 'Neutral ⚪')}\n"
        out += f"\n  USD/INR ({sign(usdinr_c)}{usdinr_c:.2f}%): {'Imported inputs costlier 🔴' if usdinr_c>0 else 'Import cost savings 🟢'}\n"
        out += f"\n  VIX @ {vix:.2f}: {'Defensive FMCG outperforms in risk-off 🟢' if vix>20 else 'Cyclicals preferred over FMCG 🔴'}\n"

    elif sec == "Gold":
        out += f"\n  Gold & Jewellery sector highly sensitive to gold prices and consumer spending.\n"
        out += f"\n  Gold @ ${gold:.0f}/oz ({sign(gold_c)}{gold_c:.2f}%)\n"
        if gold_c > 1:
            out += f"    → Gold RISING 🟢: Revenue boost for jewellers (Titan/Kalyan)\n"
            out += f"    → Gold ETFs and sovereign gold bonds in demand\n"
        else:
            out += f"    → Gold FALLING 🔴: Jewellery discretionary demand may soften\n"
        out += f"\n  USD/INR ({sign(usdinr_c)}{usdinr_c:.2f}%): {'INR weakness raises domestic gold price 🟢 for jewellers' if usdinr_c>0 else 'INR strength lowers domestic gold price 🔴'}\n"

    else:  # General
        out += f"\n  [GENERAL MARKET SENSITIVITY]\n"
        out += f"\n  S&P 500 ({sign(sp500_c)}{sp500_c:.2f}%): {'Global risk-on 🟢 supports Indian equities' if sp500_c>0 else 'Global risk-off 🔴 pressures Indian equities'}\n"
        out += f"  VIX @ {vix:.2f}: {'Elevated fear 🔴' if vix>20 else ('Moderate 🟡' if vix>15 else 'Calm 🟢')}\n"
        out += f"  DXY ({sign(dxy_c)}{dxy_c:.2f}%): {'FII outflow risk 🔴' if dxy_c>0.3 else ('FII inflow supportive 🟢' if dxy_c<-0.3 else 'Neutral ⚪')}\n"
        out += f"  Crude ({sign(crude_c)}{crude_c:.2f}%): {'Inflation risk 🔴' if crude_c>2 else ('Macro relief 🟢' if crude_c<-2 else 'Neutral ⚪')}\n"
        out += f"  Gold ({sign(gold_c)}{gold_c:.2f}%): {'Safe-haven bid 🔴 risk-off signal' if gold_c>1 else 'Risk-on ⚪'}\n"
        out += f"  US 10Y Yield @ {us10yr:.2f}%: {'High — FII pressure 🔴' if us10yr>4.5 else 'Moderate 🟢'}\n"

    # Overall macro verdict
    out += f"\n  {'═'*62}\n"
    out += f"  🎯 OVERALL MACRO VERDICT for {raw}\n"
    out += f"  {'─'*62}\n"
    positive = sum([sp500_c > 0, dxy_c < 0, vix < 15,
                    crude_c < 0 if sec not in ("OilGas","OMC") else crude_c > 0,
                    us10yr < 4.5])
    out += f"  Macro Score: {positive}/5 positive factors\n"
    if positive >= 4:   out += f"  ✅ MACRO TAILWIND — Favourable global conditions for {raw}\n"
    elif positive >= 3: out += f"  🟡 MACRO NEUTRAL — Mixed signals; stock-specific factors dominate\n"
    else:               out += f"  🔴 MACRO HEADWIND — Global conditions unfavourable; extra caution\n"
    out += f"\n  Data: yfinance | {datetime.now().strftime('%d %b %Y %H:%M')}\n"
    return out


# ─────────────────────────────────────────────────────────────────────────────
# AGENT SETUP
# ─────────────────────────────────────────────────────────────────────────────
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_react_agent
from langchain.agents.agent import AgentExecutor
from langchain import hub
import time

# ── Fix: Patch the broken FinishReason enum in google-generativeai / proto ──
# Gemini returns FinishReason code 10 ("MALFORMED_FUNCTION_CALL") which older
# versions of the proto-plus / langchain-google-genai library don't recognise.
# The library then calls `.name` on the raw int, raising:
#   'int' object has no attribute 'name'
# We fix this by monkey-patching the enum to handle unknown values gracefully.
def _patch_finish_reason():
    try:
        import google.generativeai.types as gtypes

        original_init = None

        # Attempt 1: patch the protos FinishReason enum
        try:
            from google.ai.generativelanguage_v1beta.types.generative_service import (
                Candidate,
            )
            original_fr = Candidate.FinishReason

            class _SafeFinishReason(int):
                """Wraps an integer finish-reason so .name always works."""
                _names = {
                    0: "FINISH_REASON_UNSPECIFIED",
                    1: "STOP",
                    2: "MAX_TOKENS",
                    3: "SAFETY",
                    4: "RECITATION",
                    5: "OTHER",
                    8: "BLOCKLIST",
                    9: "PROHIBITED_CONTENT",
                    10: "MALFORMED_FUNCTION_CALL",
                    11: "IMAGE_SAFETY",
                }
                @property
                def name(self):
                    return self._names.get(int(self), f"UNKNOWN_{int(self)}")
                def __str__(self):
                    return self.name

            # Wrap the original enum __getitem__ to return safe objects
            _orig_getattr = original_fr.__class__.__getattribute__

            def _safe_getitem(cls, val):
                try:
                    return original_fr(val)
                except Exception:
                    safe = _SafeFinishReason(val)
                    return safe

            Candidate.FinishReason.__class__.__call__ = lambda cls, val: _safe_getitem(cls, val)
        except Exception:
            pass

        # Attempt 2: patch langchain_google_genai's conversion helper
        try:
            import langchain_google_genai._common as _common

            _orig_convert = getattr(_common, "_get_finish_reason", None)

            def _safe_finish_reason(candidate):
                try:
                    fr = candidate.finish_reason
                    if hasattr(fr, "name"):
                        return fr.name
                    # fr is a raw int
                    _map = {
                        0: "FINISH_REASON_UNSPECIFIED", 1: "STOP",
                        2: "MAX_TOKENS", 3: "SAFETY", 4: "RECITATION",
                        5: "OTHER", 8: "BLOCKLIST", 9: "PROHIBITED_CONTENT",
                        10: "MALFORMED_FUNCTION_CALL", 11: "IMAGE_SAFETY",
                    }
                    return _map.get(int(fr), f"UNKNOWN_{fr}")
                except Exception:
                    return "STOP"

            if _orig_convert:
                _common._get_finish_reason = _safe_finish_reason
        except Exception:
            pass

        # Attempt 3: patch the chat model's _generate to swallow the error
        try:
            import langchain_google_genai.chat_models as _cm

            _orig_generate = _cm.ChatGoogleGenerativeAI._generate

            def _safe_generate(self, *args, **kwargs):
                try:
                    return _orig_generate(self, *args, **kwargs)
                except AttributeError as e:
                    if "'int' object has no attribute 'name'" in str(e):
                        # Re-invoke with a direct fallback: return whatever
                        # partial response the model produced
                        import google.generativeai as genai
                        # Already raised — we can't recover the partial result,
                        # so raise a cleaner error that the retry loop handles
                        raise RuntimeError(
                            f"Gemini FinishReason parse error (code 10). "
                            f"Retrying with simplified prompt..."
                        ) from e
                    raise

            _cm.ChatGoogleGenerativeAI._generate = _safe_generate
        except Exception:
            pass

    except Exception as e:
        # Patching failed silently — the retry wrapper below still protects us
        pass

_patch_finish_reason()


# ── Safer LLM wrapper that retries on the FinishReason crash ────────────────
class _RobustGemini(ChatGoogleGenerativeAI):
    """
    Subclass that catches the 'int has no attribute name' FinishReason bug
    and retries up to 3 times with exponential back-off before giving up.
    Also suppresses the UserWarning about unrecognized FinishReason enums.
    """
    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        import warnings
        last_exc = None
        for attempt in range(3):
            try:
                with warnings.catch_warnings():
                    warnings.filterwarnings(
                        "ignore",
                        message=".*FinishReason.*",
                        category=UserWarning,
                    )
                    warnings.filterwarnings(
                        "ignore",
                        message=".*Unrecognized.*",
                        category=UserWarning,
                    )
                    return super()._generate(
                        messages, stop=stop, run_manager=run_manager, **kwargs
                    )
            except AttributeError as e:
                if "'int' object has no attribute 'name'" in str(e):
                    last_exc = e
                    wait = 2 ** attempt        # 1s, 2s, 4s
                    time.sleep(wait)
                    continue
                raise
            except Exception as e:
                # Any other error — surface it immediately
                raise
        # All retries exhausted
        raise RuntimeError(
            f"Gemini API returned an unrecognised FinishReason (code 10) "
            f"after 3 attempts. This usually means the model tried to call "
            f"a tool with malformed arguments. "
            f"Original error: {last_exc}"
        )


# ── Build LLM + Agent ────────────────────────────────────────────────────────

# Build safety_settings — handle both old SDK (string keys) and new SDK (int keys)
def _build_safety_settings():
    """
    Returns safety_settings dict compatible with whatever version of
    google-generativeai is installed.  The dict tells Gemini not to
    block responses for any harm category, which prevents false-positive
    FinishReason=SAFETY blocks (code 10) on financial content.
    """
    try:
        # Modern SDK — HarmCategory is an IntEnum; use the enum members directly
        from google.generativeai.types import HarmCategory, HarmBlockThreshold
        return {
            HarmCategory.HARM_CATEGORY_HARASSMENT        : HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH       : HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT : HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT : HarmBlockThreshold.BLOCK_NONE,
        }
    except Exception:
        pass

    try:
        # Fallback — integer keys that map to the same enum values
        from google.generativeai.types import HarmBlockThreshold
        return {
            1: HarmBlockThreshold.BLOCK_NONE,   # HARASSMENT
            2: HarmBlockThreshold.BLOCK_NONE,   # HATE_SPEECH
            3: HarmBlockThreshold.BLOCK_NONE,   # SEXUALLY_EXPLICIT
            4: HarmBlockThreshold.BLOCK_NONE,   # DANGEROUS_CONTENT
        }
    except Exception:
        pass

    # Last resort — return empty dict (default safety settings)
    return {}

llm = _RobustGemini(
    model=model,
    temperature=0.15,
    google_api_key=api_key,
    convert_system_message_to_human=True,   # Required for Gemini ReAct
    safety_settings=_build_safety_settings(),
)

ALL_TOOLS = [
    get_stock_quote,
    get_analyst_consensus,
    get_pcr_and_options_analysis,
    get_detailed_fundamental_report,
    get_detailed_technical_report,
    get_intraday_trade_setup,
    get_swing_trade_setup,
    get_global_macro_dashboard,
    get_us_markets_and_futures,
    get_macro_impact_analysis,
    get_nifty_index_analysis,
    get_nifty_dashboard,
    get_sectoral_momentum,
    get_stock_fundamentals,
    get_price_history,
    compare_stocks_yf,
    get_market_overview,
    search_stock_news,
    search_macro_news,
    search_sector_analysis,
    search_ipo_and_corporate_actions,
]

# ── SYSTEM_PROMPT must be defined BEFORE the agent/prompt is built ───────────
SYSTEM_PROMPT = """You are StockSage v5, an expert AI equity research analyst for
Indian (NSE/BSE + 50+ Nifty indices) and US (NYSE/NASDAQ) markets, with deep
expertise in global macro analysis and its impact on Indian equities.

══════════════════════════════════════════════════════════════
TOOL ROUTING GUIDE
══════════════════════════════════════════════════════════════
STOCK QUERY          → get_stock_quote + get_detailed_fundamental_report
                       + get_detailed_technical_report + get_analyst_consensus
                       + get_macro_impact_analysis + search_stock_news
INDEX QUERY          → get_nifty_index_analysis + get_pcr_and_options_analysis
                       + get_us_markets_and_futures + search_stock_news
INTRADAY TRADE SETUP → get_intraday_trade_setup + get_detailed_technical_report
                       + get_pcr_and_options_analysis + get_us_markets_and_futures
SWING TRADE SETUP    → get_swing_trade_setup + get_detailed_technical_report
                       + get_analyst_consensus + get_macro_impact_analysis
FUNDAMENTAL ONLY     → get_detailed_fundamental_report + get_analyst_consensus
TECHNICAL ONLY       → get_detailed_technical_report + get_pcr_and_options_analysis
PCR/OPTIONS          → get_pcr_and_options_analysis
MACRO/GLOBAL         → get_global_macro_dashboard + get_us_markets_and_futures
                       + search_macro_news
MACRO IMPACT         → get_macro_impact_analysis + get_global_macro_dashboard
US MARKETS/FUTURES   → get_us_markets_and_futures
CRUDE/GOLD/DXY QUERY → get_global_macro_dashboard + get_macro_impact_analysis
SECTOR MOMENTUM      → get_sectoral_momentum + search_sector_analysis
                       + get_global_macro_dashboard
MARKET OVERVIEW      → get_market_overview + get_nifty_dashboard
                       + get_us_markets_and_futures
COMPARISON           → compare_stocks_yf + get_analyst_consensus

══════════════════════════════════════════════════════════════
RESPONSE STRUCTURE
══════════════════════════════════════════════════════════════
Always structure output with clearly labelled sections:
[QUOTE] [FUNDAMENTAL REPORT] [TECHNICAL REPORT] [PCR/OPTIONS]
[ANALYST CONSENSUS] [GLOBAL MACRO] [MACRO IMPACT] [NEWS] [TRADE SETUP] [VERDICT]

Rules:
• Use ₹ for Indian assets, $ for US / commodities.
• Always cite specific numbers (not vague statements).
• For trade setups: ALWAYS show Entry, SL, T1, T2, T3 and RR ratio.
• PCR > 1.2 = bullish; < 0.8 = bearish — always interpret.
• India VIX > 20 = elevated fear → caution on longs.
• Always include macro context in any Indian stock/index analysis:
  - Crude oil impact (especially for OMC, Energy, FMCG, Auto)
  - USD/INR level (especially for IT, Pharma, importers/exporters)
  - DXY direction (FII flows indicator)
  - US futures direction (pre-open gap indicator for Indian markets)
  - Gold price (safe-haven vs risk-on signal)
  - US 10Y yield (FII flow driver)
• End every analysis with:
    📈 BULL CASE (3 reasons — include 1 macro reason)
    📉 BEAR CASE (3 reasons — include 1 macro reason)
    🎯 KEY LEVELS: Imm. Support | Imm. Resistance | Max Pain | Target
    📊 ANALYST VIEW: consensus + target price + upside%
    🌍 MACRO SIGNAL: Overall macro tailwind/headwind
    ⚠️ Educational only. Not financial advice.

══════════════════════════════════════════════════════════════
MACRO INTERPRETATION CHEATSHEET
══════════════════════════════════════════════════════════════
Crude Oil > $85/bbl   → Inflation risk, CAD widens, OMC pain, ONGC gains
Crude Oil < $70/bbl   → Relief rally, OMC margins improve, lower inflation
Gold > $2400/oz       → Risk-off/safe-haven, Jewellery stocks benefit
DXY > 105             → FII outflows from India, INR weakens, IT benefits
DXY < 100             → FII inflows, INR strengthens, importers benefit
USD/INR > 86          → IT/Pharma exporters benefit; import inflation risk
USD/INR < 83          → Import cost savings; FII inflows
US VIX > 20           → Global risk-off, Indian markets under pressure
US VIX < 15           → Global calm, Indian markets supported
S&P Futures +0.5%+    → Indian markets likely GAP UP open
S&P Futures -0.5%+    → Indian markets likely GAP DOWN open
US 10Y Yield > 4.5%   → FII outflows, growth stock valuation compression
US 10Y Yield < 4%     → FII inflows, EM equities attractive

══════════════════════════════════════════════════════════════
TRADE SETUP FRAMEWORK
══════════════════════════════════════════════════════════════
Intraday:
  • Entries near pivot (PP), S1, or R1 breakouts
  • SL = 0.3×ATR beyond nearest support/resistance
  • Target 1 = R1/S1; T2 = R2/S2; T3 = extension
  • Minimum RR = 1.5:1; ideal = 2:1 or better
  • Book 50% at T1, trail rest
  • Check US futures direction before intraday entry

Swing:
  • Entry at Fib retracements (38.2%, 50%) or breakouts
  • SL = below Fib 61.8% or recent swing low
  • Targets = Fib extensions (127.2%, 161.8%)
  • Minimum RR = 2:1; ideal = 3:1 or better
  • Hold 3–10 trading days
  • Book 40% at T1, 40% at T2, trail 20% with ATR stop
  • Always consider macro tailwind/headwind for swing direction
"""

# ── Build agent AFTER SYSTEM_PROMPT is defined ───────────────────────────────
# Try the newer tool-calling agent first (more stable with Gemini);
# fall back to classic ReAct if the import isn't available.
try:
    from langchain.agents import create_tool_calling_agent
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

    tool_calling_prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human",  "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    agent = create_tool_calling_agent(llm=llm, tools=ALL_TOOLS, prompt=tool_calling_prompt)
    _agent_type = "tool_calling"
except ImportError:
    base_prompt = hub.pull("hwchase17/react")
    agent = create_react_agent(llm=llm, tools=ALL_TOOLS, prompt=base_prompt)
    _agent_type = "react"

executor = AgentExecutor(
    agent=agent,
    tools=ALL_TOOLS,
    verbose=True,
    handle_parsing_errors=True,
    return_intermediate_steps=False,
    max_iterations=15,
    max_execution_time=150,
)

# ─────────────────────────────────────────────────────────────────────────────
# INTERACTIVE SHELL
# ─────────────────────────────────────────────────────────────────────────────

BANNER = """
╔════════════════════════════════════════════════════════════════════════╗
║   📊  S T O C K S A G E  v5  —  AI Research & Trade Setup Agent       ║
║   Indian (NSE/BSE/50+ Nifty) · US Markets · Global Macro              ║
╚════════════════════════════════════════════════════════════════════════╝

  Live Data    : yfinance  (stocks · indices · futures · commodities · FX)
  Web Search   : DuckDuckGo + ET/Moneycontrol RSS
  NEW in v5    : 🛢️ Crude Oil · 🥇 Gold · 💵 DXY · 🇺🇸 US Futures
                 Macro Impact Analysis · Pre-open Gap Indicator
                 Sector Sensitivity to Global Macro
  LLM Engine   : Google Gemini (ReAct, temp=0.15)

  ⚠️  Educational use only — NOT financial advice

📌 Example queries:
  🌍  "Global macro dashboard — crude, gold, DXY today"
  🇺🇸  "US markets and futures — will India open gap up?"
  🇮🇳  "How does crude oil impact ONGC and BPCL?"
  🇮🇳  "Macro impact analysis for Nifty IT sector"
  🇮🇳  "Full analysis of RELIANCE with trade setup"
  🇮🇳  "Give me intraday trade setup for BANKNIFTY"
  🇮🇳  "Swing trade setup for TCS"
  🇮🇳  "PCR analysis of Nifty 50"
  🇮🇳  "Detailed fundamental report for HDFCBANK"
  🇮🇳  "Analyst consensus and target for INFY"
  🌐  "Compare TCS, INFY, WIPRO with analyst ratings"

  ⚡ Quick shortcuts (instant, no LLM):
    quote    <TICKER>      → real-time price
    market   india/us      → market overview
    macro                  → full macro dashboard (crude/gold/DXY/FX)
    usfut                  → US markets + futures pre-open signal
    impact   <TICKER>      → macro impact analysis for stock/sector
    dashboard sector       → Nifty sector dashboard
    momentum 1M            → sector momentum table
    index    <INDEXNAME>   → Nifty index analysis
    pcr      <TICKER>      → PCR + options analysis
    intraday <TICKER>      → intraday trade setup
    swing    <TICKER>      → swing trade setup
    analyst  <TICKER>      → analyst consensus

  Commands: help | history | clear | exit
"""

HELP_TEXT = """
📖  HELP — StockSage v5
───────────────────────────────────────────────────────────────────────
[QUOTE]           "Quote for RELIANCE" / "TSLA price" / "Gold price"
[ANALYST]         "TCS analyst target" / "AAPL buy or sell rating"
[PCR]             "Nifty PCR today" / "BANKNIFTY put-call ratio"
[FUNDAMENTAL]     "HDFCBANK detailed fundamental report"
[TECHNICAL]       "RELIANCE detailed technical report"
[INTRADAY SETUP]  "Intraday trade setup for NIFTY50"
[SWING SETUP]     "Swing trade setup for TCS"
[MACRO DASHBOARD] "Show global macro dashboard" / "Crude oil gold DXY today"
[US FUTURES]      "US markets and futures" / "Will India gap up tomorrow?"
[MACRO IMPACT]    "How does DXY affect Nifty IT?" / "Crude impact on ONGC"
[INDEX]           "Bank Nifty analysis" / "Nifty IT RSI MACD"
[DASHBOARD]       "Nifty sector dashboard" / "All Nifty indices"
[MOMENTUM]        "Which sectors outperforming this month?"
[COMPARISON]      "Compare INFY, TCS, WIPRO with analyst ratings"
[NEWS]            "Zomato news today" / "RELIANCE latest news"
[MACRO NEWS]      "RBI rate decision impact" / "FII flows India"
[SECTOR]          "Indian IT sector outlook 2025"
[IPO]             "Upcoming IPO India 2025"

📌 Global Macro Assets Supported:
    GOLD SILVER CRUDEOIL WTI BRENT NATURALGAS COPPER PLATINUM
    DXY DOLLARINDEX USDINR EURUSD GBPUSD USDJPY
    ES NQ YM RTY  (US Futures: S&P, NASDAQ, Dow, Russell)

📌 Nifty Indices (50+):
    NIFTY50 BANKNIFTY NIFTYIT NIFTYFMCG NIFTYAUTO NIFTYPHARMA
    NIFTYMETAL NIFTYREALTY NIFTYENERGY NIFTYPSUBANK NIFTYFINSERV
    NIFTYMIDCAP100 NIFTYSMALLCAP100 NIFTYCPSE INDIAVIX …

📌 Quick shortcuts:
    macro            → full macro dashboard (crude/gold/DXY/currencies)
    usfut            → US markets + futures pre-open signal
    impact RELIANCE  → macro impact analysis for stock
    quote GOLD       → gold price
    quote ES         → S&P500 futures
    intraday BANKNIFTY   swing TCS   pcr NIFTY50   analyst HDFCBANK
───────────────────────────────────────────────────────────────────────
"""


def run_agent(question: str) -> str:
    import warnings
    enriched = (
        f"{SYSTEM_PROMPT}\n\n"
        f"User Question: {question}\n\n"
        "Instructions:\n"
        "1. Use yfinance tools first. Use news tools for context.\n"
        "2. For trade setups: ALWAYS provide Entry, SL, T1/T2/T3, RR ratio.\n"
        "3. For full analysis: use fundamental + technical + analyst + PCR.\n"
        "4. Always end with structured VERDICT block.\n"
    )

    # Build the input dict based on which agent type is active
    agent_input = (
        {"input": enriched, "agent_scratchpad": []}
        if _agent_type == "tool_calling"
        else {"input": enriched}
    )

    # ── Attempt 1: Full agent run ────────────────────────────────────────────
    try:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message=".*FinishReason.*")
            warnings.filterwarnings("ignore", message=".*Unrecognized.*")
            result = executor.invoke(agent_input)
        return result.get("output", "No response.")

    except (AttributeError, RuntimeError) as e:
        err_str = str(e)
        if "'int' object has no attribute 'name'" in err_str or "FinishReason" in err_str:
            print(f"\n  ⚠️  Gemini FinishReason issue detected — retrying with simplified query...")

            # ── Attempt 2: Simplified single-step query ──────────────────────
            # Strip the long system prompt to reduce token count / complexity
            simple_input = (
                {"input": f"Answer briefly: {question}\nUse 1-2 tools maximum. "
                           f"Give a concise analysis with key numbers.",
                 "agent_scratchpad": []}
                if _agent_type == "tool_calling"
                else {"input": f"Answer briefly: {question}\nUse 1-2 tools maximum."}
            )
            try:
                time.sleep(2)
                with warnings.catch_warnings():
                    warnings.filterwarnings("ignore", message=".*FinishReason.*")
                    warnings.filterwarnings("ignore", message=".*Unrecognized.*")
                    result = executor.invoke(simple_input)
                return result.get("output", "No response.")
            except Exception as e2:
                # ── Attempt 3: Direct LLM call without tools ─────────────────
                print(f"  ⚠️  Agent failed again — falling back to direct LLM...")
                return _direct_llm_fallback(question)
        raise

    except Exception as e:
        err_str = str(e)
        if "429" in err_str or "quota" in err_str.lower():
            return ("⚠️ Gemini API rate limit reached. Please wait 60 seconds and try again.\n"
                    "Tip: Use quick shortcuts (quote, macro, intraday) which don't use the LLM.")
        if "API_KEY" in err_str or "credentials" in err_str.lower():
            return "❌ API key error. Check your GEMINI_API_KEY in .env file."
        return f"Agent error: {e}"


def _direct_llm_fallback(question: str) -> str:
    """
    When the ReAct agent crashes, call the LLM directly without tools
    and ask it to tell us WHICH tools to run, then run them manually.
    """
    import warnings
    try:
        # Ask LLM to identify the 2-3 most relevant tools for this query
        ticker_hint = ""
        words = question.upper().split()
        for w in words:
            cleaned = w.strip(".,?!")
            if cleaned in INDIAN_TICKERS or cleaned in NIFTY_INDEX_MAP:
                ticker_hint = cleaned
                break

        results = []

        # Run the most likely tools based on keywords in the question
        q_lower = question.lower()

        if ticker_hint:
            # Always get a quote first
            try:
                results.append(get_stock_quote.invoke(ticker_hint))
            except: pass

        if any(w in q_lower for w in ["technical","rsi","macd","chart","indicator","trend"]):
            t = ticker_hint or "NIFTY50"
            try: results.append(get_detailed_technical_report.invoke(t))
            except: pass

        if any(w in q_lower for w in ["fundamental","pe ratio","eps","revenue","margin","valuation"]):
            t = ticker_hint or "NIFTY50"
            try: results.append(get_detailed_fundamental_report.invoke(t))
            except: pass

        if any(w in q_lower for w in ["intraday","day trade","scalp"]):
            t = ticker_hint or "NIFTY50"
            try: results.append(get_intraday_trade_setup.invoke(t))
            except: pass

        if any(w in q_lower for w in ["swing","positional","2-15 day"]):
            t = ticker_hint or "NIFTY50"
            try: results.append(get_swing_trade_setup.invoke(t))
            except: pass

        if any(w in q_lower for w in ["pcr","put call","options","open interest"]):
            t = ticker_hint or "NIFTY50"
            try: results.append(get_pcr_and_options_analysis.invoke(t))
            except: pass

        if any(w in q_lower for w in ["analyst","target price","buy sell","recommendation","rating"]):
            t = ticker_hint or ""
            if t:
                try: results.append(get_analyst_consensus.invoke(t))
                except: pass

        if any(w in q_lower for w in ["crude","oil","gold","silver","dxy","dollar","macro","commodity"]):
            try: results.append(get_global_macro_dashboard.invoke("all"))
            except: pass

        if any(w in q_lower for w in ["us market","futures","s&p","nasdaq","gap up","gap down","pre-market"]):
            try: results.append(get_us_markets_and_futures.invoke("all"))
            except: pass

        if any(w in q_lower for w in ["news","latest","update","earnings","result"]):
            q_news = ticker_hint or question[:50]
            try: results.append(search_stock_news.invoke(q_news))
            except: pass

        if not results:
            # Generic fallback: market overview
            try: results.append(get_market_overview.invoke("india"))
            except: pass

        # Now ask the LLM to synthesise the tool outputs
        if results:
            combined_data = "\n\n---\n\n".join(results)
            synthesis_prompt = (
                f"Based on the following live market data, answer this question:\n"
                f"Question: {question}\n\n"
                f"Live Data:\n{combined_data}\n\n"
                f"Provide a concise, structured analysis. "
                f"Include key numbers. End with a brief VERDICT.\n"
                f"⚠️ Educational only. Not financial advice."
            )
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", message=".*FinishReason.*")
                warnings.filterwarnings("ignore", message=".*Unrecognized.*")
                response = llm.invoke(synthesis_prompt)
            answer = response.content if hasattr(response, "content") else str(response)
            return (
                f"[Note: Agent used direct tool execution due to API compatibility issue]\n\n"
                f"{answer}"
            )
        else:
            return (
                "⚠️ Could not fetch live data. Please try a quick shortcut instead:\n"
                "  quote RELIANCE | macro | usfut | intraday BANKNIFTY | swing TCS"
            )
    except Exception as e:
        return (
            f"⚠️ All fallback methods failed: {e}\n"
            f"Please use quick shortcuts: quote, macro, usfut, intraday, swing, index, pcr"
        )


def main():
    print(BANNER)
    history = []
    while True:
        try:
            q = input("\n🔍 StockSage v5> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n👋 Goodbye! Invest wisely."); break
        if not q: continue
        if q.lower() in ("exit","quit","bye","q"):
            print("\n👋 Goodbye! Invest wisely."); break
        if q.lower() == "help":    print(HELP_TEXT); continue
        if q.lower() == "history":
            [print(f"  {i+1}. {h}") for i,(h,_) in enumerate(history)] if history else print("  No history."); continue
        if q.lower() == "clear":   history.clear(); print("🗑️  Cleared."); continue

        # Quick shortcuts
        if q.lower().startswith("quote "):     print(get_stock_quote.invoke(q[6:].strip()));                     continue
        if q.lower().startswith("market "):    print(get_market_overview.invoke(q[7:].strip()));                 continue
        if q.lower() == "macro" or q.lower().startswith("macro "):
            cat = q[5:].strip() or "all"
            print(get_global_macro_dashboard.invoke(cat)); continue
        if q.lower() in ("usfut", "usfutures", "us futures", "us fut"):
            print(get_us_markets_and_futures.invoke("all")); continue
        if q.lower().startswith("usfut "):     print(get_us_markets_and_futures.invoke(q[6:].strip()));          continue
        if q.lower().startswith("impact "):    print(get_macro_impact_analysis.invoke(q[7:].strip()));           continue
        if q.lower().startswith("dashboard"):  print(get_nifty_dashboard.invoke(q[9:].strip() or "sector"));     continue
        if q.lower().startswith("momentum"):   print(get_sectoral_momentum.invoke(q[8:].strip() or "1M"));       continue
        if q.lower().startswith("index "):     print(get_nifty_index_analysis.invoke(q[6:].strip()));            continue
        if q.lower().startswith("pcr "):       print(get_pcr_and_options_analysis.invoke(q[4:].strip()));        continue
        if q.lower().startswith("intraday "):  print(get_intraday_trade_setup.invoke(q[9:].strip()));            continue
        if q.lower().startswith("swing "):     print(get_swing_trade_setup.invoke(q[6:].strip()));               continue
        if q.lower().startswith("analyst "):   print(get_analyst_consensus.invoke(q[8:].strip()));               continue

        print(f"\n⏳ Researching '{q}'...\n{'─'*64}")
        answer = run_agent(q)
        history.append((q, answer))
        print(f"\n{'═'*64}\n📋 STOCKSAGE v5 ANALYSIS\n{'═'*64}")
        print(answer)
        print(f"{'─'*64}\n⚠️  For educational purposes only. Not financial advice.")


if __name__ == "__main__":
    main()