# -*- coding: utf-8 -*-
import pyupbit
import pprint
import time
import datetime

# API Login
f = open("key.txt")
lines = f.readlines()
access = lines[0].strip()
secret = lines[1].strip()
f.close()

SELECTED_COINS = ['BTC', 'ETH', 'XRP', 'ETC', 'OMG', 'ZEC', 'XMR', 'XLM', 'ADA', 'EOS', 'ONT', 'MFT', 'BAT', 'LOOM', 'BCH', 'ZIL', 'IOST']
# 5 days
GROWING_PERIOD = 5
# 코인별 예산
BETTING_BUDGET = 100000
# 하루 최대 코인 갯수
MAX_NUM_COIN = 50 
SPREAD_GAP = 0.002
input_ticker="KRW-ETH"

# Load Upbit API
upbit = pyupbit.Upbit(access, secret)

# 코인 선택
def candidate_coins():
    if SELECTED_COINS:
        return map(lambda x: 'KRW-{0}'.format(x), SELECTED_COINS)
    candidate_coins = map(lambda x: x['market'], upbit.get_markets())
    return filter(lambda x: x.startswitch('KRW'), candidate_coins)

# 상승장 확인
def is_growing_market(market):
    prices = upbit.get_ohlcv(market, "day", count=GROWING_PERIOD)
    return prices[0]['trade_price'] > prices[-1]['trade_price']

# k 값 계산
def get_market_noise(market):
    prices = upbit.get_ohlcv(market, "day", count=20)[1:]
    price_noise = list(map(lambda p: 1 - abs(p['trade_price'] - p['opening_price']) / (p['high_price'] - p['low_price']), prices))
    return sum(price_noise) / len(price_noise)

def get_betting_ratio(market):
    '''
    3일~20일의 18개의 이동 평균선을 계산
    이동평균선 스코어 = 각 이동평균선을 넘은 개수/18
    e.g., 3일의 이동 평균선 = (1일전 종가 + 2일전 종가 + 3일전 종가)/3
          => 만약 현재 가격이 3일의 이동 평균 가격 보다 높으면 score 1/18 더한다
    '''
    prices = upbit.get_ohlcv(market, "day", count=21)
    score = 0
    if len(prices) < 21:
        return 0

    for period in range(3, 20):
        sum_prices = 0
        for j in range(0, period):
            sum_prices += prices[j+1]['trade_price']

        if sum_prices/period < prices[0]['opening_price']:
            score += 1/18.0
    return score

def fix_price(price):
    _unit = {
        10: 0.01,
        10**1: 0.1,
        10**2: 1,
        10**3: 5,
        10**4: 10,
        5*10**4: 50,
        10**5: 100,
        10**6: 500,
        2*10**6: 1000
    }

    for p in _unit:
        if price > p:
            price = (price // _unit[p]) * _unit[p]
    return price

def buy(market, budget):
    for retry in range(3):
        ticker = upbit.get_ticker(market)
        last_price = fix_price(ticker[0]['trade_price'] * (1 + SPREAD_GAP))
        amount = budget / last_price

        result = upbit.place_order(market, 'bid', amount, last_price)
        if result and result['uuid']:
            for i in range(5):
                order_info = upbit.get_order(result['uuid'])
                if order_info and float(order_info['remaining_volume']) <= 0.0:
                    return
                time.sleep(1)

            upbit.cancel_order(result['uuid'])


def sell(market, amount):
    for retry in range(3):
        ticker = upbit.get_ticker(market)
        if not ticker:
            return

        total_price = float(amount) * float(ticker[0]['trade_price'])
        if total_price < 10000:
            return

        last_price = fix_price(ticker[0]['trade_price'] * (1 - SPREAD_GAP))
        result = upbit.place_order(market, 'ask', amount, last_price)

        if result and result['uuid']:
            for i in range(5):
                order_info = upbit.get_order(result['uuid'])
                if order_info and float(order_info['remaining_volume']) <= 0.0:
                    return
                time.sleep(1)

            upbit.cancel_order(result['uuid'])


def dump_all():
    accounts_list = upbit.get_accounts()
    accounts_list = filter(lambda z: z['currency'] != 'KRW', accounts_list)
    for wallet in accounts_list:
        sell('KRW-{0}'.format(wallet['currency']), wallet['balance'])


if __name__ == '__main__':
    trade_markets = list(candidate_coins())
    already_buy = {}
    coin_noise = {}
    coin_betting_ratio = {}
    coin_investable = MAX_NUM_COIN

    for market in trade_markets:
        coin_noise[market] = get_market_noise(market)
        coin_betting_ratio[market] = get_betting_ratio(market)

    trade_markets = list(filter(lambda m: coin_betting_ratio[m] > 0, trade_markets))

    while True:
        for market in trade_markets:
            if market in already_buy:
                continue

            if coin_investable <= 0:
                break

            candles = upbit.get_ohlcv(market, "day", count=2)  # Today, Yesterday

            _range = candles[1]['high_price'] - candles[1]['low_price']

            today_opening = candles[0]['opening_price']
            today_current = candles[0]['trade_price']

            k = _range * coin_noise[market] * 0.5

            over_ratio = today_current / (today_opening + k)

            if over_ratio > 1.0:
                buy(market, BETTING_BUDGET * coin_betting_ratio[market])
                already_buy[market] = True
                coin_investable -= 1
                # 만약 현재 시가 기준으로 전날 등락폭 대비해서 올랐으면 사자

        time.sleep(1)

        t = datetime.now(timezone('Asia/Seoul'))
        if t.hour == 23 and t.minute > 45:  # 저녁 12시 전에 판매 한다.
            dump_all()
            exit(0)