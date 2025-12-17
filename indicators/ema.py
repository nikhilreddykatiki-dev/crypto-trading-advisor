def add_ema(df, fast, slow):
    df["ema_fast"] = df["close"].ewm(span=fast).mean()
    df["ema_slow"] = df["close"].ewm(span=slow).mean()
    return df
