import csv
from datetime import datetime

def log_trade(symbol, direction, entry, sl, tp, rr):
    with open("trade_journal.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            symbol, direction, entry, sl, tp, rr
        ])
