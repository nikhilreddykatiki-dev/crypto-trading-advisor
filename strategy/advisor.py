from strategy.risk import calculate_trade

def advisor(ctx, htf, min_rr=2.0):
    notes = []

    # 1️⃣ HTF conflict
    if ctx["trend"] != htf["htf_trend"]:
        notes.append(f"HTF ({htf['htf_trend'].upper()}) is in control")
        notes.append("Lower timeframe is against HTF")
        return {
            "action": "NO TRADE — HTF CONFLICT",
            "notes": notes
        }

    # 2️⃣ No pullback
    if not ctx["near_ema"]:
        notes.append("HTF and LTF aligned")
        notes.append("Price not in EMA pullback zone")
        return {
            "action": "WAIT — NO PULLBACK",
            "notes": notes
        }

    # 3️⃣ Direction
    direction = "LONG" if ctx["trend"] == "bullish" else "SHORT"
    sl, tp, rr = calculate_trade(ctx["last_price"], direction)

    # 4️⃣ RR filter
    if rr < min_rr:
        notes.append("Valid pullback detected")
        notes.append(f"RR too low ({rr} < {min_rr})")
        return {
            "action": "WAIT — RR TOO LOW",
            "notes": notes
        }

    # 5️⃣ Valid trade
    notes.append("HTF and LTF aligned")
    notes.append("Price in pullback zone")
    notes.append(f"RR acceptable ({rr})")

    return {
        "action": f"TAKE {direction}",
        "entry": ctx["last_price"],
        "sl": sl,
        "tp": tp,
        "rr": rr,
        "notes": notes
    }
