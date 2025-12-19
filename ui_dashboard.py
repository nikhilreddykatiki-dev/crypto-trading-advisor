import streamlit as st
import plotly.graph_objects as go

from streamlit_autorefresh import st_autorefresh

from api.market_data import fetch_cryptocompare_candles
from indicators.ema import add_ema
from strategy.context import build_context
from strategy.advisor import advisor


# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Crypto Trading Advisor",
    layout="wide"
)

# Auto refresh every 5 seconds
st_autorefresh(interval=5000, key="auto_refresh")


# ================= SESSION STATE =================
if "locked_trade" not in st.session_state:
    st.session_state.locked_trade = None


# ================= CONFIG =================
SYMBOL = "BTC"
TIMEFRAME = "3m"


# ================= DATA =================
df = fetch_cryptocompare_candles(SYMBOL, TIMEFRAME)
df = add_ema(df)

ctx = build_context(df)
adv = advisor(ctx)


# ================= DISPLAY DECISION SOURCE =================
# If trade is locked → use locked trade everywhere
display_trade = (
    st.session_state.locked_trade
    if st.session_state.locked_trade
    else adv
)


# ================= HEADER =================
st.title("📊 Crypto Trading Advisor")
st.caption(f"{SYMBOL} · {TIMEFRAME} · Manual trade locking enabled")


# ================= LIVE METRICS =================
col1, col2, col3 = st.columns(3)
col1.metric("Live Price", ctx["price"])
col2.metric("EMA 21", ctx["ema_fast"])
col3.metric("EMA 34", ctx["ema_slow"])


# ================= ADVISOR DECISION =================
st.subheader("🧠 Advisor Decision")

action = display_trade["action"]

if action == "TAKE LONG":
    st.success("🟢 TAKE LONG (LOCKED)" if st.session_state.locked_trade else "🟢 TAKE LONG")

elif action == "TAKE SHORT":
    st.error("🔴 TAKE SHORT (LOCKED)" if st.session_state.locked_trade else "🔴 TAKE SHORT")

elif action == "WAIT":
    st.warning("🟡 WAIT")

else:
    st.info(action)


# ================= ADVISOR NOTES =================
st.subheader("📌 Advisor Notes")

notes = display_trade.get("notes", [])
if not notes:
    st.markdown("- No additional notes")
else:
    for n in notes:
        st.markdown(f"- {n}")


# ================= LOCK / CLEAR BUTTONS =================
if adv["action"].startswith("TAKE") and not st.session_state.locked_trade:
    if st.button("🔒 Lock this trade"):
        st.session_state.locked_trade = adv.copy()

if st.session_state.locked_trade:
    if st.button("❌ Clear locked trade"):
        st.session_state.locked_trade = None


# ================= TRADE LEVELS =================
if display_trade["action"].startswith("TAKE"):
    st.subheader("🎯 Trade Levels")

    entry = display_trade["entry"]
    sl = display_trade["sl"]
    tp = display_trade["tp"]

    c1, c2, c3 = st.columns(3)
    c1.metric("Entry", entry)
    c2.metric("Stop Loss", sl)
    c3.metric("Take Profit", tp)

    st.caption(
        f"Risk: {abs(entry - sl):.0f} pts | "
        f"Reward: {abs(tp - entry):.0f} pts"
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

# ----- LOCKED OR LIVE TRADE LEVELS -----
if display_trade["action"].startswith("TAKE"):
    fig.add_hline(y=display_trade["entry"], line_color="blue", annotation_text="Entry")
    fig.add_hline(y=display_trade["sl"], line_color="red", annotation_text="SL")
    fig.add_hline(y=display_trade["tp"], line_color="green", annotation_text="TP")

    # Ensure TP / SL always visible
    y_vals = list(df["low"]) + list(df["high"]) + [
        display_trade["entry"],
        display_trade["sl"],
        display_trade["tp"]
    ]
    fig.update_yaxes(range=[min(y_vals) * 0.999, max(y_vals) * 1.001])

fig.update_layout(
    height=620,
    margin=dict(l=20, r=20, t=40, b=20),
    xaxis_rangeslider_visible=False
)

st.plotly_chart(fig, use_container_width=True)
