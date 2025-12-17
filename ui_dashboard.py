import streamlit as st
from streamlit_autorefresh import st_autorefresh
import plotly.graph_objects as go

from api.market_data import fetch_cryptocompare_candles
from indicators.ema import add_ema
from strategy.context import build_context, build_htf_context
from strategy.advisor import advisor
from utils.journal import log_trade

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Crypto Trading Advisor",
    layout="wide"
)

# ================= AUTO REFRESH =================
# Fixed to 5 seconds as requested
st_autorefresh(interval=5_000, key="auto_refresh")

# ================= SIDEBAR CONTROLS =================
with st.sidebar:
    st.header("⚙️ Controls")

    symbol = st.selectbox(
        "Symbol",
        options=["BTC", "ETH", "SOL"],
        index=0
    )

    ltf_interval = st.selectbox(
        "Lower Timeframe",
        options=["1m", "3m", "5m"],
        index=1  # default = 3m
    )

    min_rr = st.slider(
        "Minimum RR",
        min_value=1.0,
        max_value=3.0,
        step=0.1,
        value=2.0
    )
# ================= TITLE =================
st.title(f"📊 Crypto Trading Advisor — {symbol}")
st.caption("HTF: 15m • Data: CryptoCompare • Auto refresh: 5s")

# ================= DATA FETCH =================
df = fetch_cryptocompare_candles(symbol, ltf_interval)
htf_df = fetch_cryptocompare_candles(symbol, "15m")

if df is None or htf_df is None:
    st.stop()

# ================= INDICATORS =================
df = add_ema(df)
htf_df = add_ema(htf_df)

# ================= CONTEXT & ADVISOR =================
ctx = build_context(df)
htf = build_htf_context(htf_df)
adv = advisor(ctx, htf, min_rr=min_rr)

# ================= ADVISOR PANEL (TOP) =================
st.subheader("🧠 Advisor Status")

col1, col2 = st.columns([1, 3])

with col1:
    action = adv["action"]

    if action.startswith("TAKE"):
        st.success(action)
    elif action.startswith("NO TRADE"):
        st.error(action)
    else:
        st.warning(action)

with col2:
    for note in adv["notes"]:
        st.write("•", note)

st.divider()

# ================= CHART =================
fig = go.Figure()

fig.add_candlestick(
    x=df["time"],
    open=df["open"],
    high=df["high"],
    low=df["low"],
    close=df["close"],
    name="Price"
)

fig.add_scatter(
    x=df["time"],
    y=df["ema_fast"],
    name="EMA 21",
    line=dict(color="orange")
)

fig.add_scatter(
    x=df["time"],
    y=df["ema_slow"],
    name="EMA 34",
    line=dict(color="blue")
)

# ================= PULLBACK ZONE =================
ema = ctx["ema_fast"]

fig.add_hrect(
    y0=ema * 0.998,
    y1=ema * 1.002,
    fillcolor="rgba(255, 165, 0, 0.18)",
    line_width=0,
    layer="below"
)

# ================= TRADE LEVELS =================
if adv["action"].startswith("TAKE"):
    fig.add_hline(
        y=adv["entry"],
        line_color="blue",
        line_width=2,
        annotation_text="Entry",
        annotation_position="right"
    )

    fig.add_hline(
        y=adv["sl"],
        line_color="red",
        line_width=2,
        annotation_text="SL",
        annotation_position="right"
    )

    fig.add_hline(
        y=adv["tp"],
        line_color="green",
        line_width=2,
        annotation_text="TP",
        annotation_position="right"
    )

    log_trade(
        symbol=symbol,
        direction=adv["action"],
        entry=adv["entry"],
        sl=adv["sl"],
        tp=adv["tp"],
        rr=adv["rr"]
    )


# ================= HTF BLOCK OVERLAY =================
if adv["action"].startswith("NO TRADE"):
    fig.add_shape(
        type="rect",
        xref="paper",
        yref="paper",
        x0=0,
        y0=0,
        x1=1,
        y1=1,
        fillcolor="rgba(200, 200, 200, 0.15)",
        line_width=0,
        layer="above"
    )

# ================= FINAL CHART RENDER =================
fig.update_layout(
    height=600,
    margin=dict(l=20, r=20, t=30, b=20),
    xaxis_rangeslider_visible=False
)

st.plotly_chart(fig, use_container_width=True)
