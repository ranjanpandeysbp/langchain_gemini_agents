"""
StockSage — AI Research Agent v5 (Streamlit UI)
"""

import os
import warnings
import math
from datetime import datetime, timedelta

import streamlit as st

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="StockSage v5 — AI Research Agent",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .stTextInput>div>div>input { background-color: #1e2130; color: #f0f0f0; border: 1px solid #3d4f7c; border-radius: 8px; }
    .stButton>button { background: linear-gradient(135deg, #1a56db, #0a3fa0); color: white; border: none; border-radius: 8px; padding: 0.5rem 1.5rem; font-weight: 600; transition: all 0.2s; }
    .stButton>button:hover { background: linear-gradient(135deg, #2563eb, #1e40af); transform: translateY(-1px); }
    .result-box { background-color: #1e2130; border: 1px solid #3d4f7c; border-radius: 10px; padding: 1.2rem; font-family: 'Courier New', monospace; font-size: 0.82rem; color: #e2e8f0; white-space: pre-wrap; overflow-x: auto; max-height: 70vh; overflow-y: auto; }
    .shortcut-btn>button { background: #1e2130 !important; border: 1px solid #3d4f7c !important; color: #94a3b8 !important; font-size: 0.78rem !important; padding: 0.3rem 0.6rem !important; border-radius: 6px !important; }
    .shortcut-btn>button:hover { border-color: #1a56db !important; color: #60a5fa !important; }
    .badge { display: inline-block; background: #1e3a5f; color: #60a5fa; border-radius: 20px; padding: 2px 10px; font-size: 0.75rem; margin: 2px; }
    h1 { color: #f0f4ff !important; }
    .sidebar-section { background: #1e2130; border-radius: 8px; padding: 0.8rem; margin-bottom: 0.8rem; border: 1px solid #2d3748; }
    .stSelectbox>div>div { background-color: #1e2130; border: 1px solid #3d4f7c; }
    .history-item { background: #161b2e; border-left: 3px solid #1a56db; padding: 0.5rem 0.8rem; margin-bottom: 0.4rem; border-radius: 0 6px 6px 0; font-size: 0.82rem; color: #94a3b8; cursor: pointer; }
    .history-item:hover { background: #1e2a45; color: #60a5fa; }
    .status-running { color: #f59e0b; }
    .status-done { color: #22c55e; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# NIFTY INDEX MAP & HELPERS (same as original)
# ─────────────────────────────────────────────────────────────────────────────

NIFTY_INDEX_MAP = {
    "NIFTY50":"^NSEI","NIFTY":"^NSEI","SENSEX":"^BSESN",
    "NIFTY100":"^CNX100","NIFTY200":"NIFTY200.NS","NIFTY500":"^CNX500",
    "NIFTYMIDCAP50":"^NSEMDCP50","NIFTYMIDCAP100":"^CNXMDCP100",
    "NIFTYMIDCAP150":"NIFTYMIDCAP150.NS","NIFTYSMALLCAP50":"^CNXSC",
    "NIFTYSMALLCAP100":"^CNXSMCP100","NIFTYSMALLCAP250":"NIFTYSMALLCAP250.NS",
    "NIFTYMICROCAP250":"NIFTYMICROCAP250.NS","NIFTYTOTALMARKET":"NIFTYTOTALMARKET.NS",
    "NIFTYLARGMID250":"NIFTYLARGMID250.NS","NIFTYMIDSELECT":"NIFTYMIDSELECT.NS",
    "BANKNIFTY":"^NSEBANK","NIFTYBANK":"^NSEBANK","NIFTYIT":"^CNXIT",
    "NIFTYFMCG":"^CNXFMCG","NIFTYAUTO":"^CNXAUTO","NIFTYPHARMA":"^CNXPHARMA",
    "NIFTYFINSERV":"NIFTY_FIN_SERVICE.NS","NIFTYFINANCE":"NIFTY_FIN_SERVICE.NS","NIFTYMETAL":"^CNXMETAL",
    "NIFTYREALTY":"^CNXREALTY","NIFTYENERGY":"^CNXENERGY","NIFTYINFRA":"^CNXINFRA",
    "NIFTYMEDIA":"^CNXMEDIA","NIFTYPSUBANK":"^CNXPSUBANK","NIFTYPSE":"^CNXPSE",
    "NIFTYCONSUMPTION":"NIFTYCONSUMPTION.NS","NIFTYOILGAS":"NIFTYOILGAS.NS",
    "NIFTYHEALTHCARE":"NIFTYHEALTHCARE.NS","NIFTYMFG":"NIFTYMFG.NS",
    "NIFTYINDIAMFG":"NIFTYINDIAMFG.NS","NIFTYCHEMICALS":"NIFTYCHEMICALS.NS",
    "NIFTYINDIADIGITAL":"NIFTYINDIADIGITAL.NS","NIFTYMOBILITY":"NIFTYMOBILITY.NS",
    "NIFTYNEWENERGY":"NIFTYNEWENERGY.NS","NIFTYCPSE":"^CNXCPSE","NIFTYV20":"NIFTYV20.NS",
    "NIFTY100LOWVOL30":"NIFTY100LOWVOL30.NS","NIFTYALPHA50":"NIFTYALPHA50.NS",
    "NIFTYHIGHBETA50":"NIFTYHIGHBETA50.NS","NIFTY100QUALITY30":"NIFTY100QUALITY30.NS",
    "NIFTYDIVIDEND":"^CNXDIVID","NIFTYGROWTHSECT15":"NIFTYGROWTHSECT15.NS",
    "INDIAVIX":"^INDIAVIX","SP500":"^GSPC","SPX":"^GSPC",
    "NASDAQ":"^IXIC","DOW":"^DJI","RUSSELL2000":"^RUT","VIX":"^VIX",
    "ES":"ES=F","SP500FUT":"ES=F","ESFUT":"ES=F",
    "NQ":"NQ=F","NASDAQFUT":"NQ=F","NQFUT":"NQ=F",
    "YM":"YM=F","DOWFUT":"YM=F","YMFUT":"YM=F",
    "RTY":"RTY=F","RUSSELLFUT":"RTY=F",
    "GOLD":"GC=F","XAUUSD":"GC=F","GOLDSPOT":"GC=F",
    "SILVER":"SI=F","XAGUSD":"SI=F",
    "CRUDEOIL":"CL=F","WTI":"CL=F","CRUDE":"CL=F","OIL":"CL=F",
    "BRENT":"BZ=F","BRENTOIL":"BZ=F",
    "NATURALGAS":"NG=F","NATGAS":"NG=F",
    "COPPER":"HG=F","PLATINUM":"PL=F",
    "DXY":"DX-Y.NYB","DOLLARINDEX":"DX-Y.NYB","DOLLAR":"DX-Y.NYB",
    "USDINR":"USDINR=X","INRUSD":"USDINR=X",
    "EURUSD":"EURUSD=X","GBPUSD":"GBPUSD=X",
    "USDJPY":"JPY=X","USDCNY":"CNY=X",
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
    "Oil & Gas":"NIFTY_OIL_AND_GAS.NS","Healthcare":"NIFTY_HEALTHCARE.NS",
}


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
    import pandas as pd
    import numpy as np
    close  = df["Close"]
    high   = df["High"]
    low    = df["Low"]
    volume = df["Volume"]

    rsi14  = _rsi_series(close, 14).iloc[-1]
    rsi9   = _rsi_series(close, 9).iloc[-1]

    lo14   = low.rolling(14).min()
    hi14   = high.rolling(14).max()
    pctK   = ((close - lo14) / (hi14 - lo14).replace(0, float("nan")) * 100).rolling(3).mean()
    pctD   = pctK.rolling(3).mean()
    stoch_k, stoch_d = pctK.iloc[-1], pctD.iloc[-1]

    ema12    = close.ewm(span=12, adjust=False).mean()
    ema26    = close.ewm(span=26, adjust=False).mean()
    macd_l   = ema12 - ema26
    signal_l = macd_l.ewm(span=9, adjust=False).mean()
    hist_l   = macd_l - signal_l
    macd_v, sig_v, hist_v = macd_l.iloc[-1], signal_l.iloc[-1], hist_l.iloc[-1]

    ema9   = close.ewm(span=9).mean().iloc[-1]
    ema20  = close.ewm(span=20).mean().iloc[-1]
    ema50  = close.ewm(span=50).mean().iloc[-1]
    ema200 = close.ewm(span=200).mean().iloc[-1]
    sma20v = close.rolling(20).mean().iloc[-1]
    sma50v = close.rolling(50).mean().iloc[-1]

    sma20  = close.rolling(20).mean()
    std20  = close.rolling(20).std()
    bb_up  = (sma20 + 2*std20).iloc[-1]
    bb_lo  = (sma20 - 2*std20).iloc[-1]
    bb_mid = sma20.iloc[-1]
    bb_bw  = (bb_up - bb_lo) / bb_mid * 100

    tr    = pd.concat([high-low, (high-close.shift()).abs(), (low-close.shift()).abs()], axis=1).max(axis=1)
    atr   = tr.rolling(14).mean().iloc[-1]

    avg_vol  = volume.rolling(20).mean().iloc[-1]
    last_vol = volume.iloc[-1]
    obv      = (volume * close.diff().apply(lambda x: 1 if x>0 else (-1 if x<0 else 0))).cumsum()
    obv_trend = "Rising" if obv.iloc[-1] > obv.iloc[-5] else "Falling"

    r20   = df.tail(20)
    r5    = df.tail(5)
    sup20 = r20["Low"].min();  res20 = r20["High"].max()
    sup5  = r5["Low"].min();   res5  = r5["High"].max()

    prev_h = high.iloc[-2]; prev_l = low.iloc[-2]; prev_c = close.iloc[-2]
    pp, r1, r2, r3, s1, s2, s3 = _compute_pivots(prev_h, prev_l, prev_c)

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
# TOOL FUNCTIONS (non-decorator versions for direct use)
# ─────────────────────────────────────────────────────────────────────────────

def get_stock_quote(ticker: str) -> str:
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


def get_analyst_consensus(ticker: str) -> str:
    import yfinance as yf
    symbol, market = resolve_ticker(ticker)
    try:
        tk   = yf.Ticker(symbol)
        info = tk.info
        cur  = currency_sym(symbol)
        rec_key   = info.get("recommendationKey", "N/A").upper()
        rec_mean  = info.get("recommendationMean")
        n_analyst = info.get("numberOfAnalystOpinions", 0)
        target_lo = info.get("targetLowPrice")
        target_hi = info.get("targetHighPrice")
        target_me = info.get("targetMeanPrice")
        target_md = info.get("targetMedianPrice")
        price_now = info.get("currentPrice") or info.get("regularMarketPrice")

        def mean_to_label(m):
            if m is None: return "N/A"
            if m <= 1.5:  return "STRONG BUY 🟢🟢"
            if m <= 2.5:  return "BUY 🟢"
            if m <= 3.5:  return "HOLD ⚪"
            if m <= 4.5:  return "UNDERPERFORM 🔴"
            return "SELL 🔴🔴"

        upside = ((target_me - price_now) / price_now * 100) if target_me and price_now else None

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
        return out
    except Exception as e:
        return f"Error fetching analyst data for {symbol}: {e}"


def get_pcr_and_options_analysis(ticker: str) -> str:
    import yfinance as yf
    import numpy as np
    symbol, market = resolve_ticker(ticker)
    try:
        tk   = yf.Ticker(symbol)
        exps = tk.options
        if not exps:
            return f"⚠️ No options data for {symbol}."

        near_exp = exps[0]
        chain    = tk.option_chain(near_exp)
        calls    = chain.calls
        puts     = chain.puts
        cur      = currency_sym(symbol)

        hist  = tk.history(period="2d")
        price = hist["Close"].iloc[-1] if not hist.empty else 0

        total_call_oi  = calls["openInterest"].sum()
        total_put_oi   = puts["openInterest"].sum()
        total_call_vol = calls["volume"].fillna(0).sum()
        total_put_vol  = puts["volume"].fillna(0).sum()

        pcr_oi  = total_put_oi  / total_call_oi  if total_call_oi  > 0 else 0
        pcr_vol = total_put_vol / total_call_vol if total_call_vol > 0 else 0

        all_strikes = sorted(set(calls["strike"].tolist() + puts["strike"].tolist()))
        pain_vals   = {}
        for s in all_strikes:
            call_pain = ((calls["strike"] - s).clip(lower=0) * calls["openInterest"].fillna(0)).sum()
            put_pain  = ((s - puts["strike"]).clip(lower=0) * puts["openInterest"].fillna(0)).sum()
            pain_vals[s] = call_pain + put_pain
        max_pain_strike = min(pain_vals, key=pain_vals.get)

        atm_calls = calls[(calls["strike"] >= price*0.90) & (calls["strike"] <= price*1.10)]
        atm_puts  = puts[(puts["strike"]  >= price*0.90) & (puts["strike"]  <= price*1.10)]
        top_call_strikes = atm_calls.nlargest(3, "openInterest")[["strike","openInterest","volume"]]
        top_put_strikes  = atm_puts.nlargest(3, "openInterest")[["strike","openInterest","volume"]]

        if pcr_oi > 1.3:   sent = "STRONG BULLISH 🟢🟢"
        elif pcr_oi > 1.0: sent = "BULLISH 🟢"
        elif pcr_oi > 0.8: sent = "NEUTRAL ⚪"
        elif pcr_oi > 0.6: sent = "BEARISH 🔴"
        else:              sent = "STRONG BEARISH 🔴🔴"

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
        out += f"\n  [KEY RESISTANCE — Top Call OI Strikes]\n"
        for _, row in top_call_strikes.iterrows():
            out += f"  Strike {cur}{row['strike']:>10,.0f}  OI: {human_number(row['openInterest'])}  Vol: {human_number(row['volume'])}\n"
        out += f"\n  [KEY SUPPORT — Top Put OI Strikes]\n"
        for _, row in top_put_strikes.iterrows():
            out += f"  Strike {cur}{row['strike']:>10,.0f}  OI: {human_number(row['openInterest'])}  Vol: {human_number(row['volume'])}\n"
        out += f"\n  PCR Guide: >1.3 Strong Bullish | 1.0-1.3 Bullish | 0.8-1.0 Neutral\n"
        out += f"             0.6-0.8 Bearish | <0.6 Strong Bearish\n"
        return out
    except Exception as e:
        return f"Error fetching options data for {symbol}: {e}"


def get_detailed_fundamental_report(ticker: str) -> str:
    import yfinance as yf
    symbol, market = resolve_ticker(ticker)
    try:
        tk   = yf.Ticker(symbol)
        info = tk.info
        if not info.get("regularMarketPrice") and ".NS" in symbol:
            symbol = symbol.replace(".NS", ".BO")
            tk   = yf.Ticker(symbol); info = tk.info
        cur = currency_sym(symbol)

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

        score = 0; notes = []

        if pe_ttm and pe_ttm < 15:        score += 25; notes.append("PE < 15 → Undervalued ✅")
        elif pe_ttm and pe_ttm < 25:      score += 15; notes.append("PE 15-25 → Fair value ✅")
        elif pe_ttm and pe_ttm < 40:      score += 8;  notes.append("PE 25-40 → Slightly expensive ⚠️")
        else:                             notes.append("PE > 40 or N/A → Expensive / no earnings ❌")

        if roe > 20:                      score += 10; notes.append("ROE > 20% → Excellent ✅")
        elif roe > 12:                    score += 6;  notes.append("ROE 12-20% → Good ✅")
        else:                             notes.append("ROE < 12% → Weak ❌")
        if net_m > 15:                    score += 10; notes.append("Net Margin > 15% → Strong ✅")
        elif net_m > 8:                   score += 6;  notes.append("Net Margin 8-15% → Average ⚠️")
        else:                             notes.append("Net Margin < 8% → Thin ❌")
        if oper_m > 20:                   score += 5;  notes.append("Oper Margin > 20% → Excellent ✅")
        elif oper_m > 10:                 score += 3

        if earn_g > 20:                   score += 15; notes.append("Earnings Growth > 20% → High growth ✅")
        elif earn_g > 10:                 score += 10; notes.append("Earnings Growth 10-20% → Good ✅")
        elif earn_g > 0:                  score += 5;  notes.append("Earnings Growth > 0% → Positive ⚠️")
        else:                             notes.append("Earnings declining ❌")
        if rev_g > 15:                    score += 10; notes.append("Revenue Growth > 15% → Excellent ✅")
        elif rev_g > 5:                   score += 6;  notes.append("Revenue Growth 5-15% → Good ✅")
        else:                             notes.append("Revenue Growth < 5% ❌")

        if de and de < 0.5:               score += 15; notes.append("D/E < 0.5 → Low debt ✅")
        elif de and de < 1.5:             score += 10; notes.append("D/E 0.5-1.5 → Moderate debt ⚠️")
        elif de:                          score += 3;  notes.append("D/E > 1.5 → High debt ❌")
        if cur_r and cur_r > 2:           score += 10; notes.append("Current Ratio > 2 → Strong liquidity ✅")
        elif cur_r and cur_r > 1:         score += 6;  notes.append("Current Ratio 1-2 → Adequate ⚠️")
        else:                             notes.append("Current Ratio < 1 → Liquidity risk ❌")

        if score >= 80:   grade = "A+ 🏆 (Excellent)";     rec = "STRONG BUY 🟢🟢"
        elif score >= 65: grade = "A  🟢 (Very Good)";     rec = "BUY 🟢"
        elif score >= 50: grade = "B  ✅ (Good)";           rec = "BUY / HOLD 🟢"
        elif score >= 35: grade = "C  ⚠️  (Average)";      rec = "HOLD ⚪"
        elif score >= 20: grade = "D  🔴 (Below Average)"; rec = "REDUCE 🔴"
        else:             grade = "F  ❌ (Poor)";           rec = "SELL 🔴🔴"

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
        out += f"  P/B Ratio     : {fmt(pb):>10}\n"
        out += f"  PEG Ratio     : {fmt(peg):>10}   {'✅ Undervalued' if peg and peg<1 else ('⚠️ Fair' if peg and peg<2 else '❌ Overvalued')}\n"
        out += f"  EV/EBITDA     : {fmt(ev_ebitda):>10}\n"
        out += f"  Market Cap    : {human_number(mkt_cap):>10}\n"
        out += f"  Beta          : {fmt(beta):>10}\n"
        out += f"\n  [PROFITABILITY]\n"
        out += f"  Gross Margin  : {fmt(gross_m):>9}%\n"
        out += f"  Oper Margin   : {fmt(oper_m):>9}%\n"
        out += f"  Net Margin    : {fmt(net_m):>9}%\n"
        out += f"  ROE           : {fmt(roe):>9}%  {'🟢' if roe>15 else ('⚠️' if roe>8 else '🔴')}\n"
        out += f"  ROA           : {fmt(roa):>9}%\n"
        out += f"\n  [GROWTH]\n"
        out += f"  Revenue Growth: {fmt(rev_g):>9}%  {'🟢' if rev_g>10 else ('⚠️' if rev_g>0 else '🔴')}\n"
        out += f"  Earnings Growth:{fmt(earn_g):>9}%  {'🟢' if earn_g>15 else ('⚠️' if earn_g>0 else '🔴')}\n"
        out += f"\n  [BALANCE SHEET]\n"
        out += f"  Debt/Equity   : {fmt(de):>10}  {'✅ Low' if de and de<0.5 else ('⚠️ Moderate' if de and de<1.5 else '❌ High')}\n"
        out += f"  Current Ratio : {fmt(cur_r):>10}\n"
        out += f"\n  [DIVIDENDS]\n"
        out += f"  Div Yield     : {fmt(div_y):>9}%\n"
        out += f"  Payout Ratio  : {fmt(pay_r):>9}%\n"
        out += f"\n  [ANALYST CONSENSUS]\n"
        out += f"  Wall St Rating: {mean_lbl(rec_m)} ({rec_k})\n"
        out += f"  # Analysts    : {n_anal}\n"
        out += f"  Target Price  : {cur}{fmt(target_m)}\n"
        if upside: out += f"  Upside        : {sign(upside)}{upside:.1f}%\n"
        out += f"\n  [SCORECARD]\n"
        for n in notes:
            out += f"  • {n}\n"
        return out
    except Exception as e:
        return f"Error in fundamental report for {symbol}: {e}"


def get_detailed_technical_report(ticker: str) -> str:
    import yfinance as yf
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

        sc = 0
        sc += 2 if p > t["ema200"] else 0
        sc += 1 if p > t["ema50"]  else 0
        sc += 1 if p > t["ema20"]  else 0
        sc += 1 if t["hist_v"] > 0 else 0
        sc += 1 if t["rsi14"] > 40 and t["rsi14"] < 70 else 0
        sc += 1 if t["stoch_k"] < 80 else 0
        sc += 1 if t["obv_trend"] == "Rising" else 0
        sc += 1 if t["last_vol"] > t["avg_vol"]*0.7 else 0
        sc += 1 if t["bb_bw"] < 8 else 0

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
        out += f"  EMA  9   : {cur}{t['ema9']:,.2f}   {'▲' if p>t['ema9'] else '▼'}\n"
        out += f"  EMA 20   : {cur}{t['ema20']:,.2f}   {'▲' if p>t['ema20'] else '▼'}\n"
        out += f"  EMA 50   : {cur}{t['ema50']:,.2f}   {'▲' if p>t['ema50'] else '▼'}\n"
        out += f"  EMA 200  : {cur}{t['ema200']:,.2f}   {'▲' if p>t['ema200'] else '▼'}\n"
        out += f"  EMA 9×20 : {'Golden Cross 🟢' if t['ema9']>t['ema20'] else 'Death Cross 🔴'}\n"
        out += f"  EMA50×200: {'Golden Cross 🟢' if t['ema50']>t['ema200'] else 'Death Cross 🔴'}\n"
        out += f"\n  [MOMENTUM]\n"
        out += f"  RSI(14)  : {t['rsi14']:.1f}  →  {rsi_lbl(t['rsi14'])}\n"
        out += f"  RSI(9)   : {t['rsi9']:.1f}\n"
        out += f"  Stoch %K : {t['stoch_k']:.1f}  %D: {t['stoch_d']:.1f}  →  {stoch_lbl(t['stoch_k'])}\n"
        out += f"  MACD     : {t['macd_v']:,.3f}  Signal: {t['sig_v']:,.3f}  Hist: {t['hist_v']:,.3f}\n"
        out += f"  MACD     : {macd_lbl}\n"
        out += f"\n  [VOLATILITY]\n"
        out += f"  BB Upper : {cur}{t['bb_up']:,.2f}\n"
        out += f"  BB Mid   : {cur}{t['bb_mid']:,.2f}\n"
        out += f"  BB Lower : {cur}{t['bb_lo']:,.2f}\n"
        out += f"  BB BW    : {t['bb_bw']:.1f}%  ({'Squeeze ⚡' if t['bb_bw']<4 else 'Wide — high vol' if t['bb_bw']>12 else 'Normal'})\n"
        out += f"  BB Status: {bb_lbl}\n"
        out += f"  ATR(14)  : {cur}{atr:,.2f}  ({atr/p*100:.1f}% of price)\n"
        out += f"\n  [VOLUME]\n"
        out += f"  Last Volume    : {human_number(t['last_vol'])}\n"
        out += f"  20D Avg Volume : {human_number(t['avg_vol'])}\n"
        out += f"  Volume Trend   : {vol_lbl}\n"
        out += f"  OBV Trend      : {t['obv_trend']} {'🟢' if t['obv_trend']=='Rising' else '🔴'}\n"
        out += f"\n  [PIVOT POINTS]\n"
        out += f"  Pivot (PP) : {cur}{t['pp']:,.2f}\n"
        out += f"  R1:{cur}{t['r1']:,.2f}  R2:{cur}{t['r2']:,.2f}  R3:{cur}{t['r3']:,.2f}\n"
        out += f"  S1:{cur}{t['s1']:,.2f}  S2:{cur}{t['s2']:,.2f}  S3:{cur}{t['s3']:,.2f}\n"
        out += f"\n  [S/R ZONES]\n"
        out += f"  5d Support  : {cur}{t['sup5']:,.2f}  |  5d Resistance : {cur}{t['res5']:,.2f}\n"
        out += f"  20d Support : {cur}{t['sup20']:,.2f}  |  20d Resistance: {cur}{t['res20']:,.2f}\n"
        return out
    except Exception as e:
        return f"Error in technical report for {symbol}: {e}"


def get_market_overview(market_name: str) -> str:
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
    key=market_name.lower().strip(); pairs=INDICES.get(key, INDICES["global"])
    out=f"🌐 MARKET OVERVIEW — {market_name.upper()}\n{'═'*52}\n"
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


def get_global_macro_dashboard(category: str = "all") -> str:
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
        selected = {**MACRO_GROUPS["energy"], **MACRO_GROUPS["metals"]}; header = "COMMODITIES"
    elif cat in MACRO_GROUPS:
        selected = MACRO_GROUPS[cat]; header = cat.upper()
    else:
        selected = {**MACRO_GROUPS["energy"], **MACRO_GROUPS["metals"], **MACRO_GROUPS["currencies"]}; header = "ALL MACRO INDICATORS"

    out  = f"\n🌍 GLOBAL MACRO DASHBOARD — {header}\n{'═'*62}\n"
    out += f"  {'Instrument':<28} {'Price':>12} {'Change':>10} {'%Chg':>8}  Trend\n"
    out += f"  {'─'*26} {'─'*12} {'─'*10} {'─'*8}  {'─'*8}\n"
    for name, sym in selected.items():
        try:
            hist = yf.Ticker(sym).history(period="5d")
            if hist.empty: out += f"  {name:<28} {'N/A':>12}\n"; continue
            last = hist["Close"].iloc[-1]; prev = hist["Close"].iloc[-2] if len(hist) > 1 else last
            ch = last - prev; chp = ch / prev * 100 if prev else 0
            week_ago = hist["Close"].iloc[0]; wret = (last - week_ago) / week_ago * 100
            trend = "▲" if ch >= 0 else "▼"
            out  += f"  {name:<28} {last:>12,.3f} {sign(ch)}{ch:>9.3f} {sign(chp)}{chp:>6.2f}%  {trend} W:{sign(wret)}{wret:.1f}%\n"
        except: out += f"  {name:<28} {'Error':>12}\n"
    out += f"\n  Data: yfinance | {datetime.now().strftime('%d %b %Y %H:%M IST')}\n"
    return out


def get_sectoral_momentum(period: str = "1M") -> str:
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


def get_nifty_index_analysis(index_name: str) -> str:
    import yfinance as yf
    key = index_name.strip().upper().replace(" ","").replace("-","")
    if key not in NIFTY_INDEX_MAP:
        matches = [k for k in NIFTY_INDEX_MAP if key in k]
        if not matches: return f"❌ Unknown index '{index_name}'."
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

        trend = ("STRONG UPTREND 🟢" if now>t["ema50"]>t["ema200"] else
                 "STRONG DOWNTREND 🔴" if now<t["ema50"]<t["ema200"] else "MIXED ⚪")

        out  = f"📊 INDEX ANALYSIS — {key} ({symbol})\n{'═'*56}\n"
        out += f"  Value    : ₹{now:,.2f}  {arrow(chg)} {sign(chg)}{chg:.2f} ({sign(chgp)}{chgp:.2f}%)\n"
        out += f"  52W H/L  : ₹{close.max():,.2f} / ₹{close.min():,.2f}\n"
        out += f"\n  [RETURNS]\n"
        out += f"  1W:{ret(5)}  1M:{ret(21)}  3M:{ret(63)}  6M:{ret(126)}  YTD:{sign(ytd_r)}{ytd_r:.2f}%  1Y:{ret(252)}\n"
        out += f"\n  [TECHNICALS]\n"
        out += f"  EMA20:₹{t['ema20']:,.0f}  EMA50:₹{t['ema50']:,.0f}  EMA200:₹{t['ema200']:,.0f}\n"
        out += f"  Trend : {trend}\n"
        out += f"  RSI(14): {t['rsi14']:.1f}  |  MACD Hist: {t['hist_v']:.2f}\n"
        out += f"\n  [PIVOT LEVELS]\n"
        out += f"  PP:₹{t['pp']:,.2f}  R1:₹{t['r1']:,.2f}  R2:₹{t['r2']:,.2f}\n"
        out += f"          S1:₹{t['s1']:,.2f}  S2:₹{t['s2']:,.2f}\n"
        out += f"\n  [RISK]  Ann.Vol: {ann_v:.1f}%\n"
        return out
    except Exception as e: return f"Error: {e}"


def get_intraday_trade_setup(ticker: str) -> str:
    import yfinance as yf
    symbol, market = resolve_ticker(ticker)
    try:
        df15 = yf.Ticker(symbol).history(period="5d", interval="15m")
        df1d = yf.Ticker(symbol).history(period="30d", interval="1d")
        if df15.empty or df1d.empty:
            return f"Insufficient intraday data for '{ticker}'."

        cur = currency_sym(symbol)
        t   = _compute_all_technicals(df15)
        td  = _compute_all_technicals(df1d)
        price = t["price"]
        atr15 = t["atr"]
        atr1d = td["atr"]
        daily_trend = "UPTREND" if df1d["Close"].iloc[-1] > td["ema50"] else "DOWNTREND"

        today_data = df15[df15.index.date == df15.index[-1].date()]
        if not today_data.empty:
            day_high = today_data["High"].max()
            day_low  = today_data["Low"].min()
        else:
            day_high = t["res5"];  day_low = t["sup5"]

        prev = df1d.iloc[-2]
        pp, r1, r2, r3, s1, s2, s3 = _compute_pivots(prev["High"], prev["Low"], prev["Close"])

        long_entry_zone_lo = max(pp, t["ema20"]) * 0.9985
        long_entry_zone_hi = max(pp, t["ema20"]) * 1.0015
        long_sl     = min(t["sup5"], s1) - atr15*0.3
        long_sl     = min(long_sl, price - atr15*1.2)
        long_t1     = r1; long_t2 = r2; long_t3 = r2 + (r2 - r1)
        long_risk   = price - long_sl
        long_rr1    = (long_t1 - price) / long_risk if long_risk > 0 else 0
        long_rr2    = (long_t2 - price) / long_risk if long_risk > 0 else 0

        short_entry_zone_lo = min(pp, t["ema20"]) * 0.9985
        short_entry_zone_hi = min(pp, t["ema20"]) * 1.0015
        short_sl    = max(t["res5"], r1) + atr15*0.3
        short_sl    = max(short_sl, price + atr15*1.2)
        short_t1    = s1; short_t2 = s2; short_t3 = s2 - (s1 - s2)
        short_risk  = short_sl - price
        short_rr1   = (price - short_t1) / short_risk if short_risk > 0 else 0
        short_rr2   = (price - short_t2) / short_risk if short_risk > 0 else 0

        long_quality  = "STRONG ✅" if t["rsi14"]<60 and td["hist_v"]>0 and daily_trend=="UPTREND" else ("MODERATE ⚠️" if t["rsi14"]<70 else "WEAK ❌")
        short_quality = "STRONG ✅" if t["rsi14"]>40 and td["hist_v"]<0 and daily_trend=="DOWNTREND" else ("MODERATE ⚠️" if t["rsi14"]>30 else "WEAK ❌")

        capital_ex = 100000
        qty_long   = int(capital_ex * 0.01 / long_risk) if long_risk > 0 else 0
        qty_short  = int(capital_ex * 0.01 / short_risk) if short_risk > 0 else 0

        out  = f"\n{'═'*64}\n"
        out += f"  ⚡ INTRADAY TRADE SETUP — {symbol} [{market}]\n"
        out += f"{'═'*64}\n"
        out += f"  Current Price   : {cur}{price:,.2f}\n"
        out += f"  Daily Trend     : {daily_trend}\n"
        out += f"  ATR Daily       : {cur}{atr1d:,.2f}  |  ATR 15-min: {cur}{atr15:,.2f}\n"
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
        out += f"  │  Target 3      : {cur}{long_t3:,.2f}  🎯🎯🎯\n"
        out += f"  │  Position Size : {qty_long} units (1% risk on {cur}{capital_ex:,})\n"
        out += f"  └{'─'*62}\n"
        out += f"\n  ┌─ 📉 SHORT (SELL) SETUP {'─'*37}\n"
        out += f"  │  Quality       : {short_quality}\n"
        out += f"  │  Entry Zone    : {cur}{short_entry_zone_lo:,.2f} – {cur}{short_entry_zone_hi:,.2f}\n"
        out += f"  │  Stop-Loss     : {cur}{short_sl:,.2f}  (Risk: {cur}{abs(short_sl-price):,.2f})\n"
        out += f"  │  Target 1 (S1) : {cur}{short_t1:,.2f}  →  RR {short_rr1:.1f}:1  🎯\n"
        out += f"  │  Target 2 (S2) : {cur}{short_t2:,.2f}  →  RR {short_rr2:.1f}:1  🎯🎯\n"
        out += f"  │  Target 3      : {cur}{short_t3:,.2f}  🎯🎯🎯\n"
        out += f"  │  Position Size : {qty_short} units (1% risk on {cur}{capital_ex:,})\n"
        out += f"  └{'─'*62}\n"
        out += f"\n  ⚠️  Educational only. Not financial advice.\n"
        return out
    except Exception as e:
        return f"Error generating intraday setup for {symbol}: {e}"


def get_swing_trade_setup(ticker: str) -> str:
    import yfinance as yf
    symbol, market = resolve_ticker(ticker)
    try:
        df   = yf.Ticker(symbol).history(period="6mo", interval="1d")
        if df.empty and ".NS" in symbol:
            symbol = symbol.replace(".NS", ".BO"); market = "BSE 🇮🇳"
            df = yf.Ticker(symbol).history(period="6mo", interval="1d")
        if df.empty: return f"No data for '{ticker}'."

        cur = currency_sym(symbol)
        t   = _compute_all_technicals(df)
        p   = t["price"]; atr = t["atr"]
        close = df["Close"]; high = df["High"]; low = df["Low"]

        ema21w = close.ewm(span=21).mean().iloc[-1]
        ema55  = close.ewm(span=55).mean().iloc[-1]
        weekly_trend = "UPTREND 🟢" if p > ema21w > ema55 else ("DOWNTREND 🔴" if p < ema21w < ema55 else "SIDEWAYS ⚪")

        rec10 = df.tail(10)
        s10 = rec10["Low"].min(); r10 = rec10["High"].max()
        s20 = t["sup20"]; r20 = t["res20"]

        fib_range  = r20 - s20
        fib_382    = r20 - 0.382 * fib_range
        fib_500    = r20 - 0.500 * fib_range
        fib_618    = r20 - 0.618 * fib_range
        fib_ext127 = r20 + 0.272 * fib_range
        fib_ext162 = r20 + 0.618 * fib_range

        if p > t["ema50"]:
            long_entry = max(fib_382, t["ema20"]) if abs(p - fib_382)/p < 0.03 else p
            long_entry_type = "Fib 38.2% Retracement / EMA20 Support"
        else:
            long_entry = r20 * 1.005
            long_entry_type = "Breakout above 20d High"
        long_sl   = min(s10, fib_618) - atr*0.2; long_sl = min(long_sl, p - atr*2)
        long_t1   = r10; long_t2 = fib_ext127; long_t3 = fib_ext162
        long_risk = p - long_sl
        long_rr1  = (long_t1 - p) / long_risk if long_risk > 0 else 0
        long_rr2  = (long_t2 - p) / long_risk if long_risk > 0 else 0
        long_rr3  = (long_t3 - p) / long_risk if long_risk > 0 else 0

        if p < t["ema50"]:
            short_entry = min(fib_382, t["ema20"]) if abs(p - fib_382)/p < 0.05 else p
            short_entry_type = "Fib 38.2% Bounce / EMA20 Resistance"
        else:
            short_entry = s20 * 0.995
            short_entry_type = "Breakdown below 20d Low"
        short_sl   = max(r10, fib_382) + atr*0.2; short_sl = max(short_sl, p + atr*2)
        short_t1   = s10; short_t2 = r20 - 0.618 * fib_range; short_t3 = s20
        short_risk = short_sl - p
        short_rr1  = (p - short_t1) / short_risk if short_risk > 0 else 0
        short_rr2  = (p - short_t2) / short_risk if short_risk > 0 else 0
        short_rr3  = (p - short_t3) / short_risk if short_risk > 0 else 0

        long_sc  = sum([t["rsi14"]<65, t["hist_v"]>0, p>t["ema50"], t["obv_trend"]=="Rising", t["stoch_k"]<70])
        short_sc = sum([t["rsi14"]>35, t["hist_v"]<0, p<t["ema50"], t["obv_trend"]=="Falling", t["stoch_k"]>30])
        def ql(s): return "EXCELLENT ✅✅" if s>=4 else ("GOOD ✅" if s>=3 else ("MODERATE ⚠️" if s>=2 else "WEAK ❌"))

        capital_ex = 100000
        qty_long  = int(capital_ex * 0.02 / long_risk)  if long_risk > 0 else 0
        qty_short = int(capital_ex * 0.02 / short_risk) if short_risk > 0 else 0

        out  = f"\n{'═'*64}\n"
        out += f"  🔄 SWING TRADE SETUP — {symbol} [{market}]\n"
        out += f"{'═'*64}\n"
        out += f"  Current Price    : {cur}{p:,.2f}\n"
        out += f"  Trend (Daily)    : {weekly_trend}\n"
        out += f"  ATR(14) Daily    : {cur}{atr:,.2f}  (~{atr/p*100:.1f}% daily range)\n"
        out += f"\n  [FIBONACCI LEVELS]\n"
        out += f"  Swing High (20d) : {cur}{r20:,.2f}\n"
        out += f"  Fib 38.2%        : {cur}{fib_382:,.2f}\n"
        out += f"  Fib 50.0%        : {cur}{fib_500:,.2f}\n"
        out += f"  Fib 61.8%        : {cur}{fib_618:,.2f}\n"
        out += f"  Swing Low  (20d) : {cur}{s20:,.2f}\n"
        out += f"  Ext 127.2%       : {cur}{fib_ext127:,.2f}\n"
        out += f"  Ext 161.8%       : {cur}{fib_ext162:,.2f}\n"
        out += f"\n  ┌─ 📈 SWING LONG SETUP {'─'*40}\n"
        out += f"  │  Quality        : {ql(long_sc)} (score {long_sc}/5)\n"
        out += f"  │  Setup Type     : {long_entry_type}\n"
        out += f"  │  Entry          : {cur}{long_entry:,.2f}\n"
        out += f"  │  Stop-Loss      : {cur}{long_sl:,.2f}  (Risk: {cur}{abs(p-long_sl):,.2f})\n"
        out += f"  │  Target 1       : {cur}{long_t1:,.2f}  →  RR {long_rr1:.1f}:1  🎯\n"
        out += f"  │  Target 2       : {cur}{long_t2:,.2f}  →  RR {long_rr2:.1f}:1  🎯🎯\n"
        out += f"  │  Target 3       : {cur}{long_t3:,.2f}  →  RR {long_rr3:.1f}:1  🎯🎯🎯\n"
        out += f"  │  Hold Period    : 3–10 trading days\n"
        out += f"  └{'─'*62}\n"
        out += f"\n  ┌─ 📉 SWING SHORT SETUP {'─'*39}\n"
        out += f"  │  Quality        : {ql(short_sc)} (score {short_sc}/5)\n"
        out += f"  │  Setup Type     : {short_entry_type}\n"
        out += f"  │  Entry          : {cur}{short_entry:,.2f}\n"
        out += f"  │  Stop-Loss      : {cur}{short_sl:,.2f}  (Risk: {cur}{abs(short_sl-p):,.2f})\n"
        out += f"  │  Target 1       : {cur}{short_t1:,.2f}  →  RR {short_rr1:.1f}:1  🎯\n"
        out += f"  │  Target 2       : {cur}{short_t2:,.2f}  →  RR {short_rr2:.1f}:1  🎯🎯\n"
        out += f"  │  Target 3       : {cur}{short_t3:,.2f}  →  RR {short_rr3:.1f}:1  🎯🎯🎯\n"
        out += f"  │  Hold Period    : 3–10 trading days\n"
        out += f"  └{'─'*62}\n"
        out += f"\n  ⚠️  Educational only. Not financial advice.\n"
        return out
    except Exception as e:
        return f"Error generating swing setup for {symbol}: {e}"


def search_stock_news(query: str) -> str:
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


def compare_stocks(tickers: str) -> str:
    import yfinance as yf
    raw_list = [t.strip() for t in tickers.replace(" vs ",",").replace(" VS ",",").split(",") if t.strip()]
    if len(raw_list) < 2: return "Provide at least 2 tickers separated by commas."
    rows = []
    for raw in raw_list[:4]:
        symbol, market = resolve_ticker(raw)
        try:
            info = yf.Ticker(symbol).info; cur = currency_sym(symbol)
            rows.append({"sym":symbol,"mkt":market,"cur":cur,
                "name":(info.get("shortName","") or symbol)[:20],
                "price":info.get("currentPrice") or info.get("regularMarketPrice"),
                "pe":info.get("trailingPE"),"fpe":info.get("forwardPE"),
                "pb":info.get("priceToBook"),"peg":info.get("pegRatio"),
                "margin":info.get("profitMargins"),"roe":info.get("returnOnEquity"),
                "de":info.get("debtToEquity"),"mktcap":info.get("marketCap"),
                "div":info.get("dividendYield"),"52wh":info.get("fiftyTwoWeekHigh"),
                "52wl":info.get("fiftyTwoWeekLow"),"evebitda":info.get("enterpriseToEbitda"),
                "target":info.get("targetMeanPrice"),"rec":info.get("recommendationKey","N/A")})
        except Exception as e:
            rows.append({"sym":symbol,"mkt":market,"cur":"₹","error":str(e)})

    metrics=[("Price",      lambda r:f"{r['cur']}{fmt(r.get('price'))}"),
             ("Mkt Cap",    lambda r:human_number(r.get("mktcap"))),
             ("P/E TTM",    lambda r:fmt(r.get("pe"))),
             ("P/E Fwd",    lambda r:fmt(r.get("fpe"))),
             ("PEG",        lambda r:fmt(r.get("peg"))),
             ("P/B",        lambda r:fmt(r.get("pb"))),
             ("EV/EBITDA",  lambda r:fmt(r.get("evebitda"))),
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
        out += line + "\n"
    return out


# ─────────────────────────────────────────────────────────────────────────────
# AGENT (LangChain + Gemini) — only if API key is available
# ─────────────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are StockSage v5, an expert AI equity research analyst for Indian (NSE/BSE + 50+ Nifty indices) and US (NYSE/NASDAQ) markets.

For stock queries: provide full analysis including quote, fundamentals, technicals, and analyst consensus.
For indices: include PCR, pivot levels, and sector context.
For trade setups: ALWAYS show Entry, SL, T1/T2/T3, and RR ratio.
For macro queries: include crude oil, gold, DXY, USD/INR, US futures context.

Always end with:
📈 BULL CASE (3 reasons)
📉 BEAR CASE (3 reasons)
🎯 KEY LEVELS: Support | Resistance | Target
📊 ANALYST VIEW: consensus + target + upside%
🌍 MACRO SIGNAL: tailwind/headwind
⚠️ Educational only. Not financial advice."""


def run_agent_query(query: str, api_key: str, model: str = "gemini-1.5-flash") -> str:
    """Run query via LangChain ReAct agent with Gemini."""
    import os
    os.environ["LANGCHAIN_TRACING_V2"] = "false"

    from langchain.tools import tool as lc_tool
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain.agents import create_react_agent
    from langchain.agents.agent import AgentExecutor
    from langchain import hub

    # Wrap functions as tools
    @lc_tool
    def quote_tool(ticker: str) -> str:
        """Get real-time price quote for any stock or index."""
        return get_stock_quote(ticker)

    @lc_tool
    def fundamental_tool(ticker: str) -> str:
        """Get detailed fundamental analysis report."""
        return get_detailed_fundamental_report(ticker)

    @lc_tool
    def technical_tool(ticker: str) -> str:
        """Get detailed technical analysis report."""
        return get_detailed_technical_report(ticker)

    @lc_tool
    def analyst_tool(ticker: str) -> str:
        """Get analyst consensus, ratings, and price targets."""
        return get_analyst_consensus(ticker)

    @lc_tool
    def pcr_tool(ticker: str) -> str:
        """Get PCR and options chain analysis."""
        return get_pcr_and_options_analysis(ticker)

    @lc_tool
    def intraday_tool(ticker: str) -> str:
        """Get intraday trade setup with entry, SL, targets."""
        return get_intraday_trade_setup(ticker)

    @lc_tool
    def swing_tool(ticker: str) -> str:
        """Get swing trade setup with entry, SL, targets."""
        return get_swing_trade_setup(ticker)

    @lc_tool
    def macro_tool(category: str) -> str:
        """Get global macro dashboard — crude, gold, DXY, currencies."""
        return get_global_macro_dashboard(category)

    @lc_tool
    def market_tool(market_name: str) -> str:
        """Get live market overview for india, us, global, vix."""
        return get_market_overview(market_name)

    @lc_tool
    def sector_tool(period: str) -> str:
        """Get sectoral momentum scorecard."""
        return get_sectoral_momentum(period)

    @lc_tool
    def index_tool(index_name: str) -> str:
        """Analyse any Nifty index."""
        return get_nifty_index_analysis(index_name)

    @lc_tool
    def news_tool(query: str) -> str:
        """Search latest stock and market news."""
        return search_stock_news(query)

    @lc_tool
    def compare_tool(tickers: str) -> str:
        """Compare multiple stocks side by side."""
        return compare_stocks(tickers)

    all_tools = [quote_tool, fundamental_tool, technical_tool, analyst_tool,
                 pcr_tool, intraday_tool, swing_tool, macro_tool, market_tool,
                 sector_tool, index_tool, news_tool, compare_tool]

    llm = ChatGoogleGenerativeAI(model=model, temperature=0.15, google_api_key=api_key)
    base_prompt = hub.pull("hwchase17/react")
    agent       = create_react_agent(llm=llm, tools=all_tools, prompt=base_prompt)
    executor    = AgentExecutor(
        agent=agent, tools=all_tools,
        verbose=False, handle_parsing_errors=True,
        max_iterations=12, max_execution_time=120,
    )

    enriched = f"{SYSTEM_PROMPT}\n\nUser Question: {query}"
    result = executor.invoke({"input": enriched})
    return result.get("output", "No response generated.")


# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []
if "result" not in st.session_state:
    st.session_state.result = ""
if "query_input" not in st.session_state:
    st.session_state.query_input = ""


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Configuration")

    with st.expander("🔑 API Keys", expanded=True):
        gemini_key = st.text_input(
            "Gemini API Key (for AI analysis)",
            type="password",
            placeholder="AIza...",
            help="Required only for AI-powered free-text queries. Quick tools work without it."
        )
        gemini_model = st.selectbox(
            "Gemini Model",
            ["gemini-3.1-flash-lite-preview", "gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash"],
            index=0
        )

    st.markdown("---")
    st.markdown("## ⚡ Quick Tools")
    st.markdown("*No API key needed*")

    with st.expander("📊 Market Overview", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🇮🇳 India", use_container_width=True):
                with st.spinner("Loading..."):
                    st.session_state.result = get_market_overview("india")
            if st.button("🇺🇸 US", use_container_width=True):
                with st.spinner("Loading..."):
                    st.session_state.result = get_market_overview("us")
        with col2:
            if st.button("🌐 Global", use_container_width=True):
                with st.spinner("Loading..."):
                    st.session_state.result = get_market_overview("global")
            if st.button("📉 VIX", use_container_width=True):
                with st.spinner("Loading..."):
                    st.session_state.result = get_market_overview("vix")

    with st.expander("🌍 Macro Dashboard"):
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🛢️ All Macro", use_container_width=True):
                with st.spinner("Loading..."):
                    st.session_state.result = get_global_macro_dashboard("all")
            if st.button("⚡ Energy", use_container_width=True):
                with st.spinner("Loading..."):
                    st.session_state.result = get_global_macro_dashboard("energy")
        with col2:
            if st.button("🥇 Metals", use_container_width=True):
                with st.spinner("Loading..."):
                    st.session_state.result = get_global_macro_dashboard("metals")
            if st.button("💵 FX", use_container_width=True):
                with st.spinner("Loading..."):
                    st.session_state.result = get_global_macro_dashboard("currencies")

    with st.expander("🏭 Sector Momentum"):
        period_sel = st.selectbox("Period", ["1W","1M","3M","6M","1Y"], index=1)
        if st.button("📈 Get Momentum", use_container_width=True):
            with st.spinner("Fetching sector data..."):
                st.session_state.result = get_sectoral_momentum(period_sel)

    with st.expander("🔍 Quick Lookup"):
        quick_ticker = st.text_input("Ticker", placeholder="RELIANCE, TCS, GOLD...")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💰 Quote", use_container_width=True) and quick_ticker:
                with st.spinner("Fetching..."):
                    st.session_state.result = get_stock_quote(quick_ticker)
            if st.button("📋 Fundamental", use_container_width=True) and quick_ticker:
                with st.spinner("Analysing..."):
                    st.session_state.result = get_detailed_fundamental_report(quick_ticker)
            if st.button("⚡ Intraday", use_container_width=True) and quick_ticker:
                with st.spinner("Generating setup..."):
                    st.session_state.result = get_intraday_trade_setup(quick_ticker)
        with col2:
            if st.button("📈 Technical", use_container_width=True) and quick_ticker:
                with st.spinner("Analysing..."):
                    st.session_state.result = get_detailed_technical_report(quick_ticker)
            if st.button("🎯 Analyst", use_container_width=True) and quick_ticker:
                with st.spinner("Fetching..."):
                    st.session_state.result = get_analyst_consensus(quick_ticker)
            if st.button("🔄 Swing", use_container_width=True) and quick_ticker:
                with st.spinner("Generating setup..."):
                    st.session_state.result = get_swing_trade_setup(quick_ticker)

        if st.button("📊 PCR / Options", use_container_width=True) and quick_ticker:
            with st.spinner("Fetching options chain..."):
                st.session_state.result = get_pcr_and_options_analysis(quick_ticker)
        if st.button("📰 News", use_container_width=True) and quick_ticker:
            with st.spinner("Searching news..."):
                st.session_state.result = search_stock_news(quick_ticker)

    with st.expander("🔢 Compare Stocks"):
        compare_input = st.text_input("Tickers (comma-separated)", placeholder="TCS, INFY, WIPRO")
        if st.button("⚖️ Compare", use_container_width=True) and compare_input:
            with st.spinner("Comparing..."):
                st.session_state.result = compare_stocks(compare_input)

    with st.expander("📊 Nifty Index"):
        idx_options = sorted(NIFTY_INDEX_MAP.keys())
        sel_idx = st.selectbox("Select Index", idx_options, index=idx_options.index("NIFTY50"))
        if st.button("🔍 Analyse Index", use_container_width=True):
            with st.spinner("Analysing..."):
                st.session_state.result = get_nifty_index_analysis(sel_idx)

    st.markdown("---")
    if st.session_state.history:
        st.markdown("## 📜 History")
        for i, (q, _) in enumerate(reversed(st.session_state.history[-8:])):
            if st.button(f"↩ {q[:35]}...", key=f"hist_{i}", use_container_width=True):
                st.session_state.result = st.session_state.history[-(i+1)][1]
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.history = []
            st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# MAIN AREA
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding: 1rem 0 0.5rem 0;">
  <h1 style="font-size:2.2rem; font-weight:800; background: linear-gradient(135deg, #60a5fa, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
    📊 StockSage v5
  </h1>
  <p style="color:#94a3b8; font-size:0.95rem; margin-top:-0.5rem;">
    AI Research Agent · Indian (NSE/BSE/Nifty) + US Markets · Global Macro
  </p>
</div>
""", unsafe_allow_html=True)

# Feature badges
st.markdown("""
<div style="text-align:center; margin-bottom:1.5rem;">
  <span class="badge">📈 Technicals</span>
  <span class="badge">📋 Fundamentals</span>
  <span class="badge">🎯 Trade Setups</span>
  <span class="badge">🌍 Global Macro</span>
  <span class="badge">📊 PCR/Options</span>
  <span class="badge">🤖 AI Analysis</span>
</div>
""", unsafe_allow_html=True)

# ── AI Query Box ──────────────────────────────────────────────────────────────
with st.container():
    st.markdown("### 🤖 AI-Powered Analysis")
    st.caption("Uses Gemini AI + all tools. Requires Gemini API key in sidebar.")

    example_queries = [
        "Select an example query...",
        "Full analysis of RELIANCE with intraday trade setup",
        "Swing trade setup for TCS with macro context",
        "How does crude oil impact ONGC and BPCL today?",
        "Global macro dashboard — crude, gold, DXY impact on India",
        "PCR analysis and intraday setup for BANKNIFTY",
        "Compare TCS, INFY, WIPRO with analyst ratings",
        "Detailed fundamental report for HDFCBANK",
        "Nifty IT technical analysis and sector outlook",
        "Which sectors are outperforming this month?",
    ]

    col_q, col_btn = st.columns([5, 1])
    with col_q:
        selected_example = st.selectbox("📌 Example queries", example_queries, label_visibility="collapsed")
        if selected_example != "Select an example query...":
            st.session_state.query_input = selected_example

        user_query = st.text_area(
            "Your question",
            value=st.session_state.query_input,
            placeholder="e.g. Full analysis of RELIANCE with intraday setup...",
            height=80,
            label_visibility="collapsed"
        )

    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        run_ai = st.button("🚀 Analyse", use_container_width=True, type="primary")

    if run_ai:
        if not user_query.strip():
            st.warning("Please enter a query.")
        elif not gemini_key:
            st.error("Please enter your Gemini API key in the sidebar to use AI analysis.")
        else:
            with st.spinner("🤖 StockSage is researching... (may take 30-60s)"):
                try:
                    result = run_agent_query(user_query, gemini_key, gemini_model)
                    st.session_state.result = result
                    st.session_state.history.append((user_query, result))
                    st.session_state.query_input = ""
                except Exception as e:
                    st.session_state.result = f"❌ Agent error: {str(e)}\n\nTip: Check your Gemini API key or try a quick tool from the sidebar."

st.markdown("---")

# ── Results Display ───────────────────────────────────────────────────────────
if st.session_state.result:
    col_hdr, col_copy = st.columns([6, 1])
    with col_hdr:
        st.markdown("### 📋 Results")
    with col_copy:
        st.download_button(
            "⬇️ Export",
            data=st.session_state.result,
            file_name=f"stocksage_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain",
            use_container_width=True
        )

    st.markdown(f'<div class="result-box">{st.session_state.result}</div>', unsafe_allow_html=True)
else:
    # Welcome screen
    st.markdown("""
    <div style="background: #1e2130; border: 1px dashed #3d4f7c; border-radius:10px; padding:2rem; text-align:center; margin-top:1rem;">
      <p style="color:#60a5fa; font-size:1.1rem; font-weight:600;">👋 Welcome to StockSage v5</p>
      <p style="color:#94a3b8;">
        Use the <strong>Quick Tools</strong> in the sidebar for instant data (no API key needed),
        or type a question above for AI-powered analysis (requires Gemini API key).
      </p>
      <br>
      <p style="color:#64748b; font-size:0.85rem;">
        📌 Try: Market Overview → 🇮🇳 India &nbsp;|&nbsp; Quick Lookup → RELIANCE → Quote
        &nbsp;|&nbsp; Macro Dashboard → 🛢️ All Macro
      </p>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align:center; margin-top:2rem; padding: 1rem; border-top: 1px solid #2d3748;">
  <p style="color:#475569; font-size:0.8rem;">
    ⚠️ <strong>Educational purposes only. Not financial advice.</strong>
    Data via yfinance. AI via Google Gemini. &nbsp;|&nbsp;
    StockSage v5 © 2025
  </p>
</div>
""", unsafe_allow_html=True)