import streamlit as st
from streamlit_autorefresh import st_autorefresh
import plotly.graph_objects as go
from api.market_data import fetch_cryptocompare_candles
from indicators.ema import add_ema
from strategy.context import build_context, build_htf_context
from strategy.advisor import advisor
from utils.journal import log_trade
from config import LTF_INTERVAL, HTF_INTERVAL

st.set_page_config(page_title="Crypto Trading Advisor", layout="wide")
st_autorefresh(interval=20_000, key="refresh")

st.title("📊 Crypto Trading Advisor")
st.caption("LTF: 3m • HTF: 15m • Data: CryptoCompare")

df = fetch_cryptocompare_candles("BTC", LTF_INTERVAL)
htf_df = fetch_cryptocompare_candles("BTC", HTF_INTERVAL)

if df is None or htf_df is None:
    st.stop()


if df is None or htf_df is None:
    st.stop()

df = add_ema(df)
htf_df = add_ema(htf_df)

ctx = build_context(df)
htf = build_htf_context(htf_df)
adv = advisor(ctx, htf)

# ================= ADVISOR PANEL (TOP) =================

st.subheader("🧠 Advisor Status")

col1, col2 = st.columns([1, 3])

# Action badge
with col1:
    action = adv["action"]

    if action.startswith("TAKE"):
        st.success(action)
    elif action.startswith("NO TRADE"):
        st.error(action)
    else:
        st.warning(action)

# Advisor notes
with col2:
    for n in adv["notes"]:
        st.write("•", n)

st.divider()

fig = go.Figure()
fig.add_candlestick(
    x=df["time"],
    open=df["open"],
    high=df["high"],
    low=df["low"],
    close=df["close"]
)
fig.add_scatter(x=df["time"], y=df["ema_fast"], name="EMA 21")
fig.add_scatter(x=df["time"], y=df["ema_slow"], name="EMA 34")
# ===== Pullback zone (EMA21 band) =====
ema = ctx["ema_fast"]

fig.add_hrect(
    y0=ema * 0.998,
    y1=ema * 1.002,
    fillcolor="rgba(255, 165, 0, 0.18)",
    line_width=0,
    layer="below"
)


# ===== Trade levels =====
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
# ===== HTF conflict overlay =====
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

st.plotly_chart(fig, use_container_width=True)
