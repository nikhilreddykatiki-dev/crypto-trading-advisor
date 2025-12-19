import streamlit as st
import plotly.graph_objects as go

from api.market_data import fetch_cryptocompare_candles
from strategy.context import build_context, build_htf_context
from strategy.advisor import advisor


# ================= CONFIG =================
st.set_page_config(
    page_title="Crypto Trading Advisor",
    layout="wide"
)

AUTO_REFRESH_SECONDS = 5


# ================= SIDEBAR =================
st.sidebar.title("⚙️ Controls")

symbol = st.sidebar.selectbox("Symbol", ["BTC"])
ltf_interval = st.sidebar.selectbox("Lower Timeframe", ["1m", "3m", "5m"], index=1)
min_rr = st.sidebar.slider("Minimum RR", 1.5, 3.0, 2.0, 0.1)


# ================= DATA =================
df = fetch_cryptocompare_candles(symbol, ltf_interval)

if df is None or df.empty:
    st.error("Market data unavailable")
    st.stop()

ctx = build_context(df)
htf = build_htf_context(symbol)


# ================= ADVISOR (PURE) =================
adv = advisor(ctx, htf, min_rr=min_rr)


# ================= HEADER =================
st.title("📈 Crypto Trading Advisor")
st.caption(f"LTF: {ltf_interval} · Auto-refresh every {AUTO_REFRESH_SECONDS}s")


# ================= ACTION =================
st.subheader("🧠 Advisor Decision")

if adv["action"].startswith("TAKE"):
    st.success(adv["action"])
elif adv["action"] == "WAIT":
    st.warning("WAIT")
else:
    st.info(adv["action"])


# ================= NOTES =================
st.subheader("📌 Advisor Notes")

for note in adv["notes"]:
    st.markdown(f"- {note}")


# ================= CHART =================
fig = go.Figure()

fig.add_trace(go.Candlestick(
    x=df["time"],
    open=df["open"],
    high=df["high"],
    low=df["low"],
    close=df["close"],
    name="Price"
))

fig.add_trace(go.Scatter(
    x=df["time"],
    y=df["ema_fast"],
    line=dict(color="orange"),
    name="EMA Fast"
))

fig.add_trace(go.Scatter(
    x=df["time"],
    y=df["ema_slow"],
    line=dict(color="blue"),
    name="EMA Slow"
))

# Entry / SL / TP (ONLY IF TAKE)
if adv["action"].startswith("TAKE"):
    fig.add_hline(y=adv["entry"], line_dash="dot", annotation_text="Entry")
    fig.add_hline(y=adv["sl"], line_dash="dash", line_color="red", annotation_text="SL")
    fig.add_hline(y=adv["tp"], line_dash="dash", line_color="green", annotation_text="TP")

fig.update_layout(
    height=600,
    margin=dict(l=20, r=20, t=40, b=20),
    xaxis_rangeslider_visible=False
)

st.plotly_chart(fig, use_container_width=True)


# ================= AUTO REFRESH =================
st.experimental_autorefresh(
    interval=AUTO_REFRESH_SECONDS * 1000,
    key="auto_refresh"
)
