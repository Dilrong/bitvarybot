import pyupbit
import numpy as np

# CONST
TIKER="KRW-BTC"
k = 0.5

# Function

# 상위 수익 코인 탐색
def get_hpr(ticker):
    try:
        df = pyupbit.get_ohlcv(ticker)
        df = df['2018']

        df['ma5'] = df['close'].rolling(window=5).mean().shift(1)
        df['range'] = (df['high'] - df['low']) * 0.5
        df['target'] = df['open'] + df['range'].shift(1)
        df['bull'] = df['open'] > df['ma5']

        fee = 0.0032
        df['ror'] = np.where(df['high'] > df['target'], df['close'] / df['target'], 1)

        df['hpr'] = df['ror'].cumprod()
        df['dd'] = (df['hpr'].cummax() - df['hpr']) / df['hpr'].cummax() * 100
        return df['hpr'][-2]
    except:
        return 1

# 변동성 돌파 전략 백테스트
def get_VolatilityTest(k):    
    df = pyupbit.get_ohlcv(TIKER)
    df['range'] = (df['high'] - df['low']) * k
    df['target'] = df['open'] + df['range'].shift(1)

    fee = 0.0032
    df['ror'] = np.where(df['high'] > df['target'], df['close'] / df['target'], 1)

    df['hpr'] = df['ror'].cumprod()
    df['dd'] = (df['hpr'].cummax() - df['hpr']) / df['hpr'].cummax() * 100

    print("Volatility Breakthrough")
    print("K: ", k)
    print("MDD: ", df['dd'].max())
    print("HPR: ", df['hpr'][-2])

# 변동성 돌파+상승장 전략 백테스트
def get_VolatilityRisingTest(k):
    df = pyupbit.get_ohlcv(TIKER)

    df['ma5'] = df['close'].rolling(window=5).mean().shift(1)
    df['range'] = (df['high'] - df['low']) * k
    df['target'] = df['open'] + df['range'].shift(1)
    df['bull'] = df['open'] > df['ma5']

    fee = 0.0032
    df['ror'] = np.where(df['high'] > df['target'], df['close'] / df['target'], 1)

    df['hpr'] = df['ror'].cumprod()
    df['dd'] = (df['hpr'].cummax() - df['hpr']) / df['hpr'].cummax() * 100

    print("Volatility Breakthrough And Rising")
    print("K: ", k)
    print("MDD: ", df['dd'].max())
    print("HPR: ", df['hpr'][-2])

for k in np.arange(0.1, 1.0, 0.1):
    get_VolatilityTest(k)
    get_VolatilityRisingTest(k)

    print(pyupbit.get_ohlcv(TIKER))
    # tickers = pyupbit.get_tickers()
    # hprs=[]
    # for ticker in tickers:
    #     hprs = get_hpr(ticker)
    #     hprs.append((ticker, hpr))

    # sorted_hprs = sorted(hprs, key=lambda x:x[1], reverse=True)
    # print(sorted_hprs[:5])