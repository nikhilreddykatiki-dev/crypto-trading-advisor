import requests
import pandas as pd
import pytz

def fetch_cryptocompare_candles(symbol="BTC", interval="3m", limit=200):
    TF_MAP = {
        "1m": ("histominute", 1),
        "3m": ("histominute", 3),
        "5m": ("histominute", 5),
    }

    endpoint, aggregate = TF_MAP[interval]

    url = f"https://min-api.cryptocompare.com/data/v2/{endpoint}"
    params = {
        "fsym": symbol,
        "tsym": "USD",
        "limit": limit,
        "aggregate": aggregate
    }

    r = requests.get(url, params=params, timeout=10)
    data = r.json()["Data"]["Data"]

    df = pd.DataFrame(data)
    df["time"] = pd.to_datetime(df["time"], unit="s", utc=True)
    df["time"] = df["time"].dt.tz_convert(pytz.timezone("Asia/Kolkata"))

    return df[["time", "open", "high", "low", "close"]]
