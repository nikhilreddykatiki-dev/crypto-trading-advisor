def advisor(ctx):
    notes = []

    # Trend bias
    if ctx["trend"] == "bullish":
        bias = "LONG"
    else:
        bias = "SHORT"

    notes.append(f"Trend bias: {bias}")

    # Pullback check
    if not ctx["near_ema"]:
        notes.append("Price not near EMA pullback zone")
        return {
            "action": "WAIT",
            "notes": notes
        }

    # Momentum context
    if ctx["momentum"] == "weakening":
        notes.append("Momentum weakening near EMA")
    else:
        notes.append("Momentum supportive")

    entry = ctx["price"]

    # Simple structure-based SL/TP (no RR logic)
    if bias == "LONG":
        sl = entry * 0.995
        tp = entry * 1.01
    else:
        sl = entry * 1.005
        tp = entry * 0.99

    notes.append("Conditions met for pullback continuation")

    return {
        "action": f"TAKE {bias}",
        "notes": notes,
        "entry": round(entry, 2),
        "sl": round(sl, 2),
        "tp": round(tp, 2)
    }
