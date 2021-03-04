import pyupbit
import pprint
import time
import datetime

# Const
TIKER="KRW-BTC"
SPREAD_GAP = 1
k = 0.5

# Load API Key
f = open("key.txt")
lines = f.readlines()
access = lines[0].strip()
secret = lines[1].strip()
f.close()

# Load Upbit API
upbit = pyupbit.Upbit(access, secret)

# function

# 목표가
def get_target_price():
    df = pyupbit.get_ohlcv(TIKER)
    yesterday = df.iloc[-2]

    today_open = yesterday['close']
    yesterday_high = yesterday['high']
    yesterday_low = yesterday['low']

    # 목표가(당일 시가+레인지*0.5)
    target = today_open + (yesterday_high - yesterday_low) * k
    return target

# 매수
def buy_crypto_currency():
    krw = upbit.get_balance(TIKER)[2]
    orderbook = pyupbit.get_orderbook(TIKER)
    print(orderbook)
    sell_price = orderbook['asks'][0]['price']   
    unit = krw/float(sell_price)
    upbit.buy_market_order(TIKER, unit)

# 매도
def sell_crypto_currency():
    unit = upbit.get_balance(TIKER)[0]
    upbit.sell_market_order(TIKER, unit)

# 5일 이동평균 확인
def get_yesterday_ma5():
    df = pyupbit.get_ohlcv(TIKER)
    close = df['close']
    ma = close.rolling(window=5).mean()
    return ma[-2]

now = datetime.datetime.now()
mid = datetime.datetime(now.year, now.month, now.day) + datetime.timedelta(1)
ma5 = get_yesterday_ma5()
target_price = get_target_price()

# 매도
while True:
    try:
        now = datetime.datetime.now()
        mid = datetime.datetime(now.year, now.month, now.day) + datetime.timedelta(1)
        if mid < now < mid + datetime.delta(seconds=10):
            target_price = get_target_price()
            mid = datetime.datetime(now.year, now.month, now.day) + datetime.timedelta(1)
            ma5 = get_yesterday_ma5()
            sell_crypto_currency

        current_price = pyupbit.get_current_price()
        if (current_price > target_price) and (current_price > ma5):
            buy_crypto_currency()
        print("Time: {now} Target Price: {target_price} Current_Price{current_price}")
    except:
        print("Error")
    time.sleep(SPREAD_GAP)