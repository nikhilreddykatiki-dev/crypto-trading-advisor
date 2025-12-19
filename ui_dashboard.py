import streamlit as st
import plotly.graph_objects as go

from api.market_data import fetch_cryptocompare_candles
from indicators.ema import add_ema
from strategy.context import build_context
from strategy.advisor import advisor

st.set_page_config(page_title="Crypto Trading Advisor", layout="wide")

# ================= CONFIG =================
SYMBOL = "BTC"
TIMEFRAME = "3m"
REFRESH_SECONDS = 5

# ================= DATA =================
df = fetch_cryptocompare_candles(SYMBOL, TIMEFRAME)
df = add_ema(df)

ctx = build_context(df)
adv = advisor(ctx)

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

