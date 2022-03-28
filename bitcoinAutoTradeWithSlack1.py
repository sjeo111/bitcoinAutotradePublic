import time
import pyupbit
import datetime
import requests

access = "ugLNltzWr2PkVhRAOochX3quMIAZZMJR6kCPnT7M"
secret = "irxncjuwYrTdvdB8SSvAMxFUVuNa9PKX9a97hB4f"
myToken = "xoxb-3276158219075-3278526728804-dyDURQa73fpL1zPvmhkMjegz"

def post_message(token, channel, text):
    """슬랙 메시지 전송"""
    response = requests.post("https://slack.com/api/chat.postMessage",
        headers={"Authorization": "Bearer "+token},
        data={"channel": channel,"text": text}
    )

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    """ohlcv는 고가/시가/저가/종가/거래량을 DataFrame으로 반환"""
    """iloc -  행번호로 선택 row / loc - label, 조건표현으로 선택하는 방법"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    post_message(myToken, "#coin", "Target Price is "+str(target_price))
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_ma15(ticker):
    """15일 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=5)
    ma15 = df['close'].rolling(5).mean().iloc[-1]
    post_message(myToken, "#coin", "Average line is " +str(ma15))
    return ma15

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")
# 시작 메세지 슬랙 전송
post_message(myToken,"#coin", "autotrade start")

while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-ETC")
        end_time = start_time + datetime.timedelta(days=1)

        """if start_time < now < end_time - datetime.timedelta(seconds=10): """
        target_price = get_target_price("KRW-ETC", 0.2)
        ma15 = get_ma15("KRW-ETC")
        current_price = get_current_price("KRW-ETC")
        post_message(myToken, "#coin", "Current price is "+str(current_price))

        if target_price < current_price and ma15 < current_price:
                krw = get_balance("KRW")
                post_message(myToken,"#coin", "let me buy")
                if krw > 5000:
                   buy_result = upbit.buy_market_order("KRW-ETC", krw*0.9995)
                   post_message(myToken,"#coin", "ETC buy : " +str(buy_result))
        
        elif target_price > current_price and ma15 > current_price :
                btc = get_balance("ETC")
                post_message(myToken,"#coin", "Coin Balance is : "+ str(btc))
                
                if btc > 0.1:
                 post_message(myToken,"#coin", "let me sell")
                
                 sell_result = upbit.sell_market_order("KRW-ETC", btc*0.9995)
                 post_message(myToken,"#coin", "ETC sell : " +str(sell_result))
        
        else:
               post_message(myToken,"#coin", "I don't know")
        """    btc = get_balance("ETC") """
        """    if btc > 0.00008: """
        """        sell_result = upbit.sell_market_order("KRW-ETC", btc*0.9995) """
        """        post_message(myToken,"#coin", "ETC buy : " +str(sell_result)) """
        time.sleep(30)
    except Exception as e:
        print(e)
        post_message(myToken,"#coin", e)
        time.sleep(1)