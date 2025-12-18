import requests
import pandas as pd
import streamlit as st
from datetime import datetime
import pytz

def fetch_cryptocompare_candles(symbol="BTC", interval="3m", limit=200):
    TF_MAP = {
        "1m": ("histominute", 1),
        "3m": ("histominute", 3),
        "5m": ("histominute", 5),
        "15m": ("histominute", 15),
    }

    endpoint, aggregate = TF_MAP[interval]

    url = f"https://min-api.cryptocompare.com/data/v2/{endpoint}"
    params = {
        "fsym": symbol,
        "tsym": "USD",
        "limit": limit,
        "aggregate": aggregate
    }

    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()

        if data["Response"] != "Success":
            raise ValueError("Bad response")

        rows = data["Data"]["Data"]

        df = pd.DataFrame(rows)
        # Convert to UTC first
        df["time"] = pd.to_datetime(df["time"], unit="s", utc=True)

        # Convert to IST for display
        ist = pytz.timezone("Asia/Kolkata")
        df["time"] = df["time"].dt.tz_convert(ist)

        df["close"] = df["close"].astype(float)

        return df[["time", "open", "high", "low", "close", "volumefrom"]]

    except Exception:
        st.error("⚠️ Market data unavailable (CryptoCompare)")
        return None
