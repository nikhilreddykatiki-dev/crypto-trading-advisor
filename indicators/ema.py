def add_ema(df, fast=21, slow=34):
    df["ema_fast"] = df["close"].ewm(span=fast).mean()
    df["ema_slow"] = df["close"].ewm(span=slow).mean()
    return df
