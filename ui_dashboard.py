import streamlit as st
from datetime import datetime
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
from api.market_data import fetch_candles, fetch_candles_htf
from indicators.ema import add_ema
from strategy.context import build_context, build_htf_context
from strategy.advisor import advisor_logic
from utils.journal import log_trade
from config import (
    EMA_FAST,
    EMA_SLOW,
    INTERVAL,
    HTF_INTERVAL,
    HTF_EMA_FAST,
    HTF_EMA_SLOW
)

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Trading Advisor",
    page_icon="📊",
    layout="wide",
)

# ---------------- AUTO REFRESH ----------------
# 20 seconds = 20000 ms (you can change this)
st_autorefresh(interval=20_000, key="refresh")

# ---------------- STYLE ----------------
st.markdown(
    """
    <style>
    .big-font {
        font-size:36px !important;
        font-weight:700;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------- HEADER ----------------
st.markdown("<div class='big-font'>📊 Crypto Trading Advisor</div>", unsafe_allow_html=True)
st.caption(f"LTF: {INTERVAL} • HTF: {HTF_INTERVAL} • Auto-refresh enabled")

# ---------------- FETCH LTF DATA ----------------
df = fetch_candles()

if df is None or df.empty:
    st.stop()

df = add_ema(df, EMA_FAST, EMA_SLOW)
ctx = build_context(df)

# ---------------- FETCH HTF DATA ----------------
df_htf = fetch_candles_htf("BTCUSDT", HTF_INTERVAL)
df_htf = add_ema(df_htf, HTF_EMA_FAST, HTF_EMA_SLOW)
htf = build_htf_context(df_htf)

# ---------------- ADVISOR LOGIC ----------------
adv = advisor_logic(ctx, htf)

last_price = df.iloc[-1]["close"]

# ================= TRADE JOURNAL ONLY =================
if adv["action"].startswith("TAKE"):
    direction = "LONG" if "LONG" in adv["action"] else "SHORT"

    log_trade(
        symbol="BTCUSDT",
        ltf=INTERVAL,
        htf=HTF_INTERVAL,
        direction=direction,
        entry=adv["entry"],
        sl=adv["sl"],
        tp=adv["tp"],
        rr=adv["rr"],
    )


# ================= TOP STATUS BAR =================
col1, col2, col3, col4 = st.columns(4)

# HTF Bias
if htf["htf_trend"] == "bullish":
    col1.success("🟢 HTF BULLISH (15m)")
else:
    col1.error("🔴 HTF BEARISH (15m)")

# LTF State (contextual, not directional)
if ctx["trend"] == htf["htf_trend"]:
    col2.success("🟢 LTF ALIGNED WITH HTF")
else:
    col2.warning("🟡 LTF PULLBACK AGAINST HTF")

col3.metric("Last Price", f"{last_price:,.2f}")
if adv["action"].startswith("TAKE"):
    col4.success(adv["action"])
elif "NO TRADE" in adv["action"]:
    col4.error(adv["action"])
else:
    col4.info(adv["action"])


# ================= ADVISOR NOTES (ON TOP) =================
st.divider()
st.subheader("🧠 Advisor Notes")

if adv["notes"]:
    for note in adv["notes"]:
        st.warning(note)
else:
    st.success("Market structure is clean. No warnings.")

# ================= MARKET METRICS =================
st.divider()
m1, m2, m3 = st.columns(3)

m1.metric("EMA Fast (LTF)", ctx["ema_fast"])
m2.metric("EMA Slow (LTF)", ctx["ema_slow"])
m3.metric("EMA Gap", ctx["ema_gap"])

# ================= PRICE CHART =================
st.divider()
st.subheader("📈 Price Chart (LTF)")

fig = go.Figure()

fig.add_trace(go.Candlestick(
    x=df.index,
    open=df["open"],
    high=df["high"],
    low=df["low"],
    close=df["close"],
    name="Price"
))

fig.add_trace(go.Scatter(
    x=df.index,
    y=df["ema_fast"],
    line=dict(color="orange", width=2),
    name="EMA Fast"
))

fig.add_trace(go.Scatter(
    x=df.index,
    y=df["ema_slow"],
    line=dict(color="cyan", width=2),
    name="EMA Slow"
))

fig.update_layout(
    height=500,
    margin=dict(l=10, r=10, t=30, b=10),
    xaxis_rangeslider_visible=False,
    template="plotly_dark"
)

# ================= VISUAL ANNOTATIONS =================

# HTF conflict shading
if ctx["trend"] != htf["htf_trend"]:
    fig.add_shape(
        type="rect",
        xref="paper",
        yref="paper",
        x0=0,
        y0=0,
        x1=1,
        y1=1,
        fillcolor="rgba(255, 0, 0, 0.08)",
        line_width=0,
        layer="below"
    )

# Pullback zone highlight (EMA21 band)
ema = ctx["ema_fast"]
fig.add_hrect(
    y0=ema * 0.998,
    y1=ema * 1.002,
    fillcolor="rgba(255, 165, 0, 0.15)",
    line_width=0
)

# Entry / SL / TP lines (only when TAKE TRADE)
if adv["action"].startswith("TAKE"):
    fig.add_hline(y=adv["entry"], line_color="blue", line_width=2, annotation_text="Entry")
    fig.add_hline(y=adv["sl"], line_color="red", line_width=2, annotation_text="SL")
    fig.add_hline(y=adv["tp"], line_color="green", line_width=2, annotation_text="TP")


st.plotly_chart(fig, use_container_width=True)

# ================= FOOTER =================
st.caption(f"Last update: {datetime.now().strftime('%H:%M:%S')}")
