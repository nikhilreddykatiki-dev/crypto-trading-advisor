def advisor(ctx):
    """
    Simple, local-style trading advisor.
    Decides based on:
    - EMA trend
    - EMA pullback
    - Momentum
    Uses EMA structure for SL/TP (no RR, no percentages).
    """

    notes = []

    # ---------------- TREND BIAS ----------------
    if ctx["trend"] == "bullish":
        bias = "LONG"
        notes.append("Higher probability trend is BULLISH (EMA fast > EMA slow)")
    else:
        bias = "SHORT"
        notes.append("Higher probability trend is BEARISH (EMA fast < EMA slow)")

    # ---------------- PULLBACK CHECK ----------------
    if not ctx["near_ema"]:
        notes.append("Price is not near EMA pullback zone")
        notes.append("Waiting for price to retrace closer to EMA")
        return {
            "action": "WAIT",
            "notes": notes
        }

    notes.append("Price is near EMA pullback zone")

    # ---------------- MOMENTUM CONTEXT ----------------
    if ctx["momentum"] == "weakening":
        notes.append("Momentum is weakening → pullback likely ending")
    else:
        notes.append("Momentum still strong → pullback may be shallow")

    # ---------------- TRADE STRUCTURE ----------------
    entry = ctx["price"]
    ema = ctx["ema_fast"]

    if bias == "LONG":
        sl = ema * 0.998              # slightly below EMA
        tp = entry + (entry - sl) * 1.5

        notes.append("SL placed slightly below EMA (structure-based)")
        notes.append("TP set using risk-based extension above entry")

    else:  # SHORT
        sl = ema * 1.002              # slightly above EMA
        tp = entry - (sl - entry) * 1.5

        notes.append("SL placed slightly above EMA (structure-based)")
        notes.append("TP set using risk-based extension below entry")

    # ---------------- FINAL DECISION ----------------
    notes.append("Trend + pullback conditions satisfied")
    notes.append("Waiting for price reaction confirmation on chart")

    return {
        "action": f"TAKE {bias}",
        "notes": notes,
        "entry": round(entry, 2),
        "sl": round(sl, 2),
        "tp": round(tp, 2)
    }
