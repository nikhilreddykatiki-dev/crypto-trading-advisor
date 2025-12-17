import requests
import pandas as pd
from config import SYMBOL, INTERVAL, CANDLE_LIMIT

BINANCE_URL = "https://api.binance.com/api/v3/klines"

def fetch_candles():
    params = {
        "symbol": SYMBOL,
        "interval": INTERVAL,
        "limit": CANDLE_LIMIT
    }

    r = requests.get(BINANCE_URL, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()

    df = pd.DataFrame(data, columns=[
        "time","open","high","low","close","volume",
        "ct","qav","trades","tb","tq","ignore"
    ])

    for col in ["open","high","low","close","volume"]:
        df[col] = df[col].astype(float)

    return df

def fetch_candles_htf(symbol, interval, limit=200):
    import requests
    import pandas as pd

    BINANCE_URL = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }

    r = requests.get(BINANCE_URL, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()

    df = pd.DataFrame(data, columns=[
        "time","open","high","low","close","volume",
        "ct","qav","trades","tb","tq","ignore"
    ])

    for col in ["open","high","low","close","volume"]:
        df[col] = df[col].astype(float)

    return df
