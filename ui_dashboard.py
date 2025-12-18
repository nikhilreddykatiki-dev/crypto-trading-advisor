import streamlit as st
from streamlit_autorefresh import st_autorefresh
import plotly.graph_objects as go
from datetime import datetime, timezone
from api.market_data import fetch_cryptocompare_candles
from indicators.ema import add_ema
from strategy.context import build_context, build_htf_context
from strategy.advisor import advisor
from utils.journal import log_trade

# ================= SIGNAL SETTINGS =================
SIGNAL_VALID_CANDLES = 1  # valid for 1 closed candle

def get_last_closed_candle_time(df):
    """
    Returns the timestamp of the last fully closed candle.
    """
    return df.iloc[-2]["time"]

def candle_close_countdown(df, interval):
    """
    Countdown until the currently forming candle closes.
    Robust for CryptoCompare timestamps.
    """
    TF_SECONDS = {
        "1m": 60,
        "3m": 180,
        "5m": 300,
        "15m": 900
    }

    tf_sec = TF_SECONDS[interval]

    # Last candle time from API (this is the OPEN time of the current candle)
    current_candle_open = df.iloc[-1]["time"].replace(tzinfo=timezone.utc)

    next_close_ts = current_candle_open.timestamp() + tf_sec
    now_ts = datetime.now(timezone.utc).timestamp()

    remaining = int(next_close_ts - now_ts)
    return max(0, remaining)

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

# ================= CANDLE COUNTDOWN =================
remaining_sec = candle_close_countdown(df, ltf_interval)

mm = remaining_sec // 60
ss = remaining_sec % 60


# ================= INDICATORS =================
df = add_ema(df)
htf_df = add_ema(htf_df)

# ================= SESSION STATE =================
if "last_candle_time" not in st.session_state:
    st.session_state.last_candle_time = None

if "frozen_signal" not in st.session_state:
    st.session_state.frozen_signal = None

if "last_signal_snapshot" not in st.session_state:
    st.session_state.last_signal_snapshot = None

if "signal_candle_index" not in st.session_state:
    st.session_state.signal_candle_index = None

if "signal_decision_time" not in st.session_state:
    st.session_state.signal_decision_time = None

if "signal_decision_time" not in st.session_state:
    st.session_state.signal_decision_time = None

if "last_action" not in st.session_state:
    st.session_state.last_action = None

# ================= CONTEXT & ADVISOR =================
ctx = build_context(df)
htf = build_htf_context(htf_df)

# ================= SIGNAL FREEZE (CORRECTED) =================
last_closed_time = get_last_closed_candle_time(df)
current_candle_index = df.index[-2]

# New candle closed → recompute advisor
if st.session_state.last_candle_time != last_closed_time:
    new_adv = advisor(ctx, htf, min_rr=min_rr)

    st.session_state.last_candle_time = last_closed_time
    st.session_state.signal_candle_index = current_candle_index

    # 🔒 LOCK decision time ONLY on NEW TAKE signal
    if (
        new_adv["action"].startswith("TAKE")
        and st.session_state.last_action != new_adv["action"]
    ):
        st.session_state.frozen_signal = new_adv
        st.session_state.signal_decision_time = last_closed_time
        st.session_state.last_action = new_adv["action"]

    # Otherwise keep previous frozen signal
else:
    new_adv = st.session_state.frozen_signal

adv = st.session_state.frozen_signal or new_adv    

# ----- EXPIRY CHECK -----
candles_passed = (
    df.index[-2] - st.session_state.signal_candle_index
    if st.session_state.signal_candle_index is not None
    else 0
)

if candles_passed >= SIGNAL_VALID_CANDLES:
    adv = {
        "action": "SIGNAL EXPIRED — WAIT",
        "notes": ["Signal expired after candle close", "Waiting for new setup"]
    }
# Update recap status if expired
if adv["action"].startswith("SIGNAL EXPIRED") and st.session_state.last_signal_snapshot:
    st.session_state.last_signal_snapshot["action"] = "EXPIRED"

# ----- EXPIRY CHECK (STATE-SAFE) -----
candles_passed = (
    df.index[-2] - st.session_state.signal_candle_index
    if st.session_state.signal_candle_index is not None
    else 0
)

# If signal expired, update the FROZEN signal (single source of truth)
if candles_passed >= SIGNAL_VALID_CANDLES:
    st.session_state.frozen_signal = {
        "action": "SIGNAL EXPIRED — WAIT",
        "notes": [
            "Signal expired after candle close",
            "Waiting for new setup"
        ]
    }

# Always read adv from frozen state
adv = st.session_state.frozen_signal or {"action": "WAIT", "notes": []}

# Update recap status if expired
if (
    adv["action"].startswith("SIGNAL EXPIRED")
    and st.session_state.last_signal_snapshot
):
    st.session_state.last_signal_snapshot["action"] = "EXPIRED"


# ================= STATUS BANNER =================
st.markdown("### 🧠 Advisor Status")

action = adv["action"]

if action.startswith("TAKE"):
    st.markdown(
        f"""
        <div style="
            background-color:#e6fffa;
            border-left:6px solid #2ecc71;
            padding:16px;
            border-radius:8px;
            font-size:18px;
            font-weight:600;">
            {action}
        </div>
        """,
        unsafe_allow_html=True
    )
elif action.startswith("NO TRADE") or action.startswith("SIGNAL EXPIRED"):
    st.markdown(
        f"""
        <div style="
            background-color:#fff5f5;
            border-left:6px solid #e74c3c;
            padding:16px;
            border-radius:8px;
            font-size:18px;
            font-weight:600;">
            {action}
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.markdown(
        f"""
        <div style="
            background-color:#fffbea;
            border-left:6px solid #f1c40f;
            padding:16px;
            border-radius:8px;
            font-size:18px;
            font-weight:600;">
            {action}
        </div>
        """,
        unsafe_allow_html=True
    )

st.caption(
    f"🔒 Signal locked @ {st.session_state.signal_decision_time.strftime('%H:%M:%S')}"
    if st.session_state.signal_decision_time else ""
)

# ================= TRADE RECAP =================
st.markdown("### 📘 Trade Recap")

snap = st.session_state.last_signal_snapshot

if snap:
    col1, col2, col3 = st.columns(3)

    with col1:
        st.write("**Symbol**:", snap["symbol"])
        st.write("**Timeframe**:", snap["timeframe"])
        st.write("**Time**:", snap["time"].strftime("%Y-%m-%d %H:%M:%S"))

    with col2:
        st.write("**Action**:", snap["action"])
        if snap["entry"]:
            st.write("**Entry**:", snap["entry"])
            st.write("**SL**:", snap["sl"])
            st.write("**TP**:", snap["tp"])

    with col3:
        if snap["rr"]:
            st.metric("RR", snap["rr"])

        if snap["action"] == "EXPIRED":
            st.warning("⏱️ Signal expired")
        elif snap["action"].startswith("TAKE"):
            st.success("✅ Signal was valid")
        else:
            st.info("ℹ️ No trade taken")

else:
    st.info("No signal recorded yet")

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
    height=620,
    margin=dict(l=20, r=20, t=40, b=20),
)

st.plotly_chart(fig, use_container_width=True)
