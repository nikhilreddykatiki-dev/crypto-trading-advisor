def advisor(ctx, min_rr=2.0):
    notes = []

    if ctx["trend"] == "bullish":
        bias = "LONG"
    else:
        bias = "SHORT"

    notes.append(f"Trend bias: {bias}")

    if not ctx["near_ema"]:
        notes.append("Price not near EMA pullback zone")
        return {
            "action": "WAIT",
            "notes": notes
        }

    if ctx["momentum"] == "weakening":
        notes.append("Momentum weakening near EMA")
    else:
        notes.append("Momentum supportive")

    entry = ctx["price"]

    if bias == "LONG":
        sl = entry * 0.995
        tp = entry * 1.01
    else:
        sl = entry * 1.005
        tp = entry * 0.99

    rr = abs(tp - entry) / abs(entry - sl)

    notes.append(f"RR ≈ {round(rr,2)}")

    if rr < min_rr:
        notes.append("RR below acceptable threshold")
        return {
            "action": "WAIT",
            "notes": notes
        }

    return {
        "action": f"TAKE {bias}",
        "notes": notes,
        "entry": round(entry, 2),
        "sl": round(sl, 2),
        "tp": round(tp, 2),
        "rr": round(rr, 2)
    }
