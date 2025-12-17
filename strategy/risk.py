def calculate_trade(price, direction):
    if direction == "LONG":
        sl = price * 0.995
        tp = price * 1.01
    else:
        sl = price * 1.005
        tp = price * 0.99

    rr = abs(tp - price) / abs(price - sl)
    return round(sl, 2), round(tp, 2), round(rr, 2)
