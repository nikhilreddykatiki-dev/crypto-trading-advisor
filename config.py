# ===== MARKET =====
SYMBOL = "BTCUSDT"
INTERVAL = "3m"
CANDLE_LIMIT = 120

# ===== INDICATORS =====
EMA_FAST = 21
EMA_SLOW = 34

# ===== RULE THRESHOLDS =====
MIN_EMA_GAP = 25      # too small = chop
MAX_EMA_GAP = 200     # too large = late trend

HTF_INTERVAL = "15m"
HTF_EMA_FAST = 21
HTF_EMA_SLOW = 34

MIN_RR = 2.0          # minimum acceptable risk:reward
SL_BUFFER_PCT = 0.001 # 0.1% buffer beyond EMA/swing
