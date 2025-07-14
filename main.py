import ccxt
import time
import ta
import pandas as pd

# اطلاعات API خودت رو از Gate.io اینجا وارد کن
api_key = 'GATE_IO_API_KEY'
api_secret = 'GATE_IO_SECRET_KEY'

exchange = ccxt.gate({
    'apiKey': api_key,
    'secret': api_secret,
    'enableRateLimit': True,
})

symbol = 'DOGE5L/USDT'
usdt_amount = 100

def fetch_data():
    bars = exchange.fetch_ohlcv(symbol, timeframe='5m', limit=100)
    df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['ema9'] = ta.trend.ema_indicator(df['close'], window=9)
    df['ema21'] = ta.trend.ema_indicator(df['close'], window=21)
    df['rsi'] = ta.momentum.rsi(df['close'], window=14)
    return df

def should_buy(df):
    if (
        df['ema9'].iloc[-2] < df['ema21'].iloc[-2] and
        df['ema9'].iloc[-1] > df['ema21'].iloc[-1] and
        df['rsi'].iloc[-1] > 50
    ):
        return True
    return False

def should_sell(df, entry_price):
    current_price = df['close'].iloc[-1]
    profit = (current_price - entry_price) / entry_price
    if profit >= 0.04 or (df['ema9'].iloc[-1] < df['ema21'].iloc[-1]):
        return True
    return False

in_position = False
entry_price = 0

while True:
    df = fetch_data()
    if not in_position and should_buy(df):
        price = df['close'].iloc[-1]
        order = exchange.create_market_buy_order(symbol, usdt_amount / price)
        entry_price = price
        in_position = True
        print("خرید انجام شد:", entry_price)
    elif in_position and should_sell(df, entry_price):
        price = df['close'].iloc[-1]
        amount = usdt_amount / entry_price
        order = exchange.create_market_sell_order(symbol, amount)
        print("فروش انجام شد:", price)
        in_position = False
    time.sleep(60)
