import csv
import os
from datetime import datetime

FILE_NAME = "trade_journal.csv"

HEADERS = [
    "timestamp",
    "symbol",
    "ltf",
    "htf",
    "direction",
    "entry",
    "sl",
    "tp",
    "rr",
]

def log_trade(symbol, ltf, htf, direction, entry, sl, tp, rr):
    file_exists = os.path.isfile(FILE_NAME)

    with open(FILE_NAME, mode="a", newline="") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow(HEADERS)

        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            symbol,
            ltf,
            htf,
            direction,
            entry,
            sl,
            tp,
            rr,
        ])
