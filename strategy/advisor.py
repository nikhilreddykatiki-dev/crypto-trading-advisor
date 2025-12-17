from config import MIN_EMA_GAP, MAX_EMA_GAP, MIN_RR, SL_BUFFER_PCT
from strategy.risk import calculate_rr

def advisor_logic(ctx, htf):
    notes = []
    bias = "LONG ONLY" if ctx["trend"] == "bullish" else "SHORT ONLY"
    action = "WAIT"

    # Always show HTF bias
    notes.append(f"HTF (15m) bias: {htf['htf_trend'].upper()}")

    # HTF alignment
    if ctx["trend"] != htf["htf_trend"]:
        notes.append(f"HTF ({htf['htf_trend'].upper()}) in control")
        notes.append("Waiting for LTF to align with HTF")
        return {
            "bias": bias,
            "action": "NO TRADE",
            "notes": notes
    }


    # Chop / late trend
    if ctx["ema_gap"] < MIN_EMA_GAP:
        notes.append("EMA gap small -> choppy market")
        return {"bias": bias, "action": "NO TRADE", "notes": notes}

    if ctx["ema_gap"] > MAX_EMA_GAP:
        notes.append("EMA gap large -> late trend")
        return {"bias": bias, "action": "WAIT", "notes": notes}

    # Momentum note
    if ctx["momentum"] == "weakening":
        notes.append("Momentum weakening -> caution")

    # ----- ENTRY LOGIC -----
    if not ctx["near_ema_fast"]:
        return {"bias": bias, "action": "WAIT", "notes": notes}

    entry = ctx["last_price"]

    if ctx["trend"] == "bullish" and ctx["price_position"] == "above_both":
        action = "TAKE LONG"
        sl = ctx["ema_fast"] * (1 - SL_BUFFER_PCT)
        tp = entry + (entry - sl) * MIN_RR

    elif ctx["trend"] == "bearish" and ctx["price_position"] == "below_both":
        action = "TAKE SHORT"
        sl = ctx["ema_fast"] * (1 + SL_BUFFER_PCT)
        tp = entry - (sl - entry) * MIN_RR

    else:
        return {"bias": bias, "action": "WAIT", "notes": notes}

    rr = calculate_rr(entry, sl, tp)

    if rr < MIN_RR:
        notes.append(f"RR {rr} < {MIN_RR} -> trade blocked")
        return {"bias": bias, "action": "WAIT", "notes": notes}

    # Approved trade
    notes.extend([
        f"Entry: {round(entry, 2)}",
        f"SL: {round(sl, 2)}",
        f"TP: {round(tp, 2)}",
        f"RR: {rr}"
    ])

    return {
        "bias": bias,
        "action": action,
        "notes": notes,
        "entry": round(entry, 2),
        "sl": round(sl, 2),
        "tp": round(tp, 2),
        "rr": rr
    }
