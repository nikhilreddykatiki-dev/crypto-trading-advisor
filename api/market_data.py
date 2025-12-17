import requests
import pandas as pd
import streamlit as st

def fetch_coinbase_candles(symbol="BTC-USD", interval="3m", limit=200):
    GRANULARITY = {
        "1m": 60,
        "3m": 180,
        "5m": 300,
        "15m": 900
    }

    url = f"https://api.exchange.coinbase.com/products/{symbol}/candles"
    params = {"granularity": GRANULARITY[interval]}

    try:
        r = requests.get(
            url,
            params=params,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10
        )
        r.raise_for_status()
        data = r.json()

        if not data:
            raise ValueError("Empty data")

        df = pd.DataFrame(
            data,
            columns=["time", "low", "high", "open", "close", "volume"]
        )

        df["close"] = df["close"].astype(float)
        df["time"] = pd.to_datetime(df["time"], unit="s")
        df = df.sort_values("time").tail(limit)

        return df

    except Exception:
        st.error("⚠️ Coinbase market data unavailable")
        return None
