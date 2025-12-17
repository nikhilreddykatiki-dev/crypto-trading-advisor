def build_context(df):
    last = df.iloc[-1]
    prev = df.iloc[-2]

    trend = "bullish" if last.ema_fast > last.ema_slow else "bearish"

    price_position = (
        "above_both"
        if last.close > last.ema_fast and last.close > last.ema_slow
        else "below_both"
    )

    ema_gap = abs(last.ema_fast - last.ema_slow)
    prev_gap = abs(prev.ema_fast - prev.ema_slow)

    momentum = "strengthening" if ema_gap > prev_gap else "weakening"

    pullback_zone = (
        abs(last.close - last.ema_fast) / last.close < 0.002
    )

    return {
        "trend": trend,
        "price_position": price_position,
        "ema_fast": round(last.ema_fast, 2),
        "ema_slow": round(last.ema_slow, 2),
        "ema_gap": round(ema_gap, 2),
        "momentum": momentum,
        "near_ema_fast": pullback_zone,
        "last_price": round(last.close, 2)
    }

def build_htf_context(df):
    last = df.iloc[-1]

    trend = "bullish" if last.ema_fast > last.ema_slow else "bearish"

    return {
        "htf_trend": trend,
        "ema_fast": round(last.ema_fast, 2),
        "ema_slow": round(last.ema_slow, 2),
    }
