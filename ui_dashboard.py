import streamlit as st
from streamlit_autorefresh import st_autorefresh
import plotly.graph_objects as go

from api.market_data import fetch_coinbase_candles
from indicators.ema import add_ema
from strategy.context import build_context, build_htf_context
from strategy.advisor import advisor
from utils.journal import log_trade
from config import LTF_INTERVAL, HTF_INTERVAL

st.set_page_config(page_title="Crypto Trading Advisor", layout="wide")
st_autorefresh(interval=20_000, key="refresh")

st.title("📊 Crypto Trading Advisor")
st.caption("LTF: 3m • HTF: 15m • Data: Coinbase")

df = fetch_coinbase_candles("BTC-USD", LTF_INTERVAL)
htf_df = fetch_coinbase_candles("BTC-USD", HTF_INTERVAL)

if df is None or htf_df is None:
    st.stop()

df = add_ema(df)
htf_df = add_ema(htf_df)

ctx = build_context(df)
htf = build_htf_context(htf_df)
adv = advisor(ctx, htf)

st.subheader("Advisor Notes")
for n in adv["notes"]:
    st.write("•", n)

st.metric("Last Price", ctx["last_price"])
st.metric("Action", adv["action"])

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

if adv["action"].startswith("TAKE"):
    fig.add_hline(y=adv["entry"], line_color="blue")
    fig.add_hline(y=adv["sl"], line_color="red")
    fig.add_hline(y=adv["tp"], line_color="green")

    log_trade(
        "BTC-USD",
        adv["action"],
        adv["entry"],
        adv["sl"],
        adv["tp"],
        adv["rr"]
    )

st.plotly_chart(fig, use_container_width=True)
