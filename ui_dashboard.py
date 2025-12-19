import streamlit as st
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
from api.market_data import fetch_cryptocompare_candles
from indicators.ema import add_ema
from strategy.context import build_context
from strategy.advisor import advisor

st.set_page_config(page_title="Crypto Trading Advisor", layout="wide")
# Auto refresh every 5 seconds
st_autorefresh(interval=5000, key="refresh")

if "locked_trade" not in st.session_state:
    st.session_state.locked_trade = None


# ================= CONFIG =================
SYMBOL = "BTC"
TIMEFRAME = "3m"
REFRESH_SECONDS = 5

# ================= DATA =================
df = fetch_cryptocompare_candles(SYMBOL, TIMEFRAME)
df = add_ema(df)

ctx = build_context(df)
adv = advisor(ctx)

col1, col2, col3 = st.columns(3)

col1.metric("Live Price", ctx["price"])
col2.metric("EMA 21", ctx["ema_fast"])
col3.metric("EMA 34", ctx["ema_slow"])


# ================= UI =================
st.title("📊 Crypto Trading Advisor")
st.caption(f"{SYMBOL} · {TIMEFRAME} · Auto refresh {REFRESH_SECONDS}s")

st.subheader("🧠 Advisor Decision")

if adv["action"].startswith("TAKE"):
    st.success(adv["action"])
else:
    st.warning("WAIT")

st.subheader("📌 Advisor Notes")
for n in adv["notes"]:
    st.markdown(f"- {n}")

if adv["action"].startswith("TAKE"):
    if st.button("🔒 Lock this trade"):
        st.session_state.locked_trade = adv.copy()

if st.session_state.locked_trade:
    lt = st.session_state.locked_trade

    st.subheader("🔐 Locked Trade")

    col1, col2, col3 = st.columns(3)
    col1.metric("Entry", lt["entry"])
    col2.metric("Stop Loss", lt["sl"])
    col3.metric("Take Profit", lt["tp"])

    st.caption("These values are frozen and will not change")

if st.session_state.locked_trade:
    if st.button("❌ Clear locked trade"):
        st.session_state.locked_trade = None


# ================= TRADE LEVELS =================
if adv["action"].startswith("TAKE"):
    st.subheader("🎯 Trade Levels")

    col1, col2, col3 = st.columns(3)

    entry = adv["entry"]
    sl = adv["sl"]
    tp = adv["tp"]

    with col1:
        st.metric("Entry", entry)

    with col2:
        st.metric("Stop Loss", sl)

    with col3:
        st.metric("Take Profit", tp)

    # Optional: distance info (very useful)
    st.caption(
        f"Risk: {abs(entry - sl):.0f} points | "
        f"Reward: {abs(tp - entry):.0f} points"
    )


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

fig.add_scatter(x=df["time"], y=df["ema_fast"], name="EMA 21")
fig.add_scatter(x=df["time"], y=df["ema_slow"], name="EMA 34")

if adv["action"].startswith("TAKE"):
    fig.add_hline(y=adv["entry"], line_color="blue", annotation_text="Entry")
    fig.add_hline(y=adv["sl"], line_color="red", annotation_text="SL")
    fig.add_hline(y=adv["tp"], line_color="green", annotation_text="TP")

fig.update_layout(
    height=600,
    xaxis_rangeslider_visible=False
)

st.plotly_chart(fig, use_container_width=True)

