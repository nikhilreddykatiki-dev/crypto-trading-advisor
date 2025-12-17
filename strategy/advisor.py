from strategy.risk import calculate_trade
from config import MIN_RR

def advisor(ctx, htf):
    notes = []

    if ctx["trend"] != htf["htf_trend"]:
        notes.append("HTF in control, LTF against → no trade")
        return {"action": "NO TRADE", "notes": notes}

    if not ctx["near_ema"]:
        notes.append("Price not in pullback zone")
        return {"action": "WAIT", "notes": notes}

    direction = "LONG" if ctx["trend"] == "bullish" else "SHORT"
    sl, tp, rr = calculate_trade(ctx["last_price"], direction)

    if rr < MIN_RR:
        notes.append("RR below threshold")
        return {"action": "WAIT", "notes": notes}

    notes.append("HTF + LTF aligned")
    notes.append("Valid pullback with RR")

    return {
        "action": f"TAKE {direction}",
        "entry": ctx["last_price"],
        "sl": sl,
        "tp": tp,
        "rr": rr,
        "notes": notes
    }
