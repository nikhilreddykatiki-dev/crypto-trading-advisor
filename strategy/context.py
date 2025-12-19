def build_context(df):
    last = df.iloc[-1]
    prev = df.iloc[-2]

    trend = "bullish" if last.ema_fast > last.ema_slow else "bearish"

    ema_gap = abs(last.ema_fast - last.ema_slow)
    prev_gap = abs(prev.ema_fast - prev.ema_slow)

    momentum = "strengthening" if ema_gap > prev_gap else "weakening"

    near_ema = abs(last.close - last.ema_fast) / last.close < 0.002

    return {
        "trend": trend,
        "price": round(last.close, 2),
        "near_ema": near_ema,
        "momentum": momentum,
        "ema_fast": round(last.ema_fast, 2),
        "ema_slow": round(last.ema_slow, 2),
    }
