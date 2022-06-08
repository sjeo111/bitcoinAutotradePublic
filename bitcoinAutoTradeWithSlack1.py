from sre_constants import IN
import time
import pyupbit
import datetime
import requests

access = "ugLNltzWr2PkVhRAOochX3quMIAZZMJR6kCPnT7M111"
secret = "irxncjuwYrTdvdB8SSvAMxFUVuNa9PKX9a97hB4f111"
myToken = "xoxb-3276158219075-3278526728804-GBMVDUOkwaCE1ztoEUgCNYUv111"

"""슬랙 메시지 전송"""
def post_message(token, channel, text):
    response = requests.post("https://slack.com/api/chat.postMessage",
        headers={"Authorization": "Bearer "+token},
        data={"channel": channel,"text": text}
    )

# Not in Use
def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    """ohlcv는 고가/시가/저가/종가/거래량을 DataFrame으로 반환"""
    """iloc -  행번호로 선택 row / loc - label, 조건표현으로 선택하는 방법"""
    df = pyupbit.get_ohlcv(ticker, interval="day1", count=15)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
   
    return target_price

# Not in Use
def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

# Not in Use
def get_ma15(ticker):
    """15일 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="minute5", count=5)
    ma15 = df['close'].rolling(5).mean().iloc[-1]
    
    return ma15

# Searching for Account Balance
def get_balance(ticker):
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

# Searching for buying price in average
def get_avg_buy_price(ticker):
    # Searching for Account Balance
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['avg_buy_price'] is not None:
                return float(b['avg_buy_price'])
            else:
                return 0
    return 0

# Searching for Current Price
def get_current_price(ticker):
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]

# Getting High price
def get_high_price(ticker):
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    high = df.iloc[0]['high']
    return high

# Getting Low price
def get_low_price(ticker):
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    low = round(df.iloc[0]['low'])
    return low



#코인별로 1시간봉 데이터 베이스 생성
def tickers_db(ticker):
    df = pyupbit.get_ohlcv(ticker, interval='minute60', count=120)
    return df

# Fast %K = ((현재가 - n기간 중 최저가) / (n기간 중 최고가 - n기간 중 최저가)) * 100
def get_stochastic_fast_k(close_price, low, high, n):
    fast_k = ((close_price - low.rolling(n).min()) / (high.rolling(n).max() - low.rolling(n).min())) * 100
    return fast_k

# Slow %K = Fast %K의 m기간 이동평균(SMA)
def get_stochastic_slow_k(fast_k, n):
    slow_k = fast_k.rolling(n).mean()
    return slow_k

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")
# 시작 메세지 슬랙 전송
# post_message(myToken,"#coin", "autotrade start")

while True:
    try:   
        
        """if start_time < now < end_time - datetime.timedelta(seconds=10): """
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-BTC")
        end_time = start_time + datetime.timedelta(days=1)
        low_price = get_low_price("KRW-BTC")
        current_price = get_current_price("KRW-BTC")
        avg_buy_price = get_avg_buy_price("KRW-BTC")

        # Stochastic 설정 (fast 14일, slow 3일)
        df = tickers_db('KRW-BTC')  
        df['fast_k'] = get_stochastic_fast_k(df['close'], df['low'], df['high'], 14)
        df['slow_k'] = get_stochastic_slow_k(df['fast_k'], 3)
        stochastict_fast = df['fast_k'][-1]
        stochastict_slow = df['slow_k'][-1]

        # MACD 구하기 
        df['ma12'] = df['close'].rolling(window=12).mean() 
        #12일 이동평균 
        df['ma26'] = df['close'].rolling(window=26).mean() 
        #26일 이동평균 
        df['MACD'] = df['ma12'] - df['ma26'] 
        #MACD 
        df['MACD_Signal'] = df['MACD'].rolling(window=9).mean() 
        # MACD Signal(MACD 9일 이동평균) 
        df['MACD_Oscil'] = df['MACD'] - df['MACD_Signal'] 
        #MACD 오실레이터

        print(df['ma12'])

        # 출력 (25분에 진행)
        # if now.minute == 25 :
            # post_message(myToken, "#coin", "--------------------------------")
            # post_message(myToken, "#coin", "fast : " + str(stochastict_fast))
            # post_message(myToken, "#coin", "slow : " + str(stochastict_slow))
            # post_message(myToken, "#coin", "현재가  : "+ str(current_price))
            # post_message(myToken, "#coin", "최저가 : " + str(low_price))
           
        print("------------------------------------")
        print("fast   : " + str(stochastict_fast))
        print("slow   : " + str(stochastict_slow))
        print("현재가 : "+ str(current_price))
        print("최저가 : " + str(low_price))
        print("구매가 : "+str(avg_buy_price))

        #buy for profit
        if 30.0 > stochastict_fast > 22.0 and stochastict_fast > stochastict_slow :
                krw = get_balance("KRW")
                print("I need to buy")

                if krw > 5000:
                 #post_message(myToken,"#coin", "let me buy")
                 buy_result = upbit.buy_market_order("KRW-BTC", krw*0.9995)
                 #post_message(myToken,"#coin", "BTC buy : " +str(buy_result))

        #sell for profit / fast > 55 & slow+1 > fast
        elif stochastict_fast > 55.0 and stochastict_slow + 1 > stochastict_fast :
                btc = get_balance("BTC")             
                print("I need to sell")

                if btc >0.0001:
                 #post_message(myToken,"#coin", "let me sell")
                 sell_result = upbit.sell_market_order("KRW-BTC", btc*0.9995)
                 #post_message(myToken,"#coin", "BTC sell : " +str(sell_result))

        #sell for profit / fast > 75
        elif stochastict_fast > 75.0 :
                btc = get_balance("BTC")             
                print("I need to sell")

                if btc >0.0001:
                 #post_message(myToken,"#coin", "let me sell")
                 sell_result = upbit.sell_market_order("KRW-BTC", btc*0.9995)
                 #post_message(myToken,"#coin", "BTC sell : " +str(sell_result))


        #sell for profit / fast & slow get together && fast > 65
        elif stochastict_fast - stochastict_slow > 5 and stochastict_fast >65:
                btc = get_balance("BTC")             
                print("I need to sell")

                if btc >0.0001:
                 #post_message(myToken,"#coin", "let me sell")
                 sell_result = upbit.sell_market_order("KRW-BTC", btc*0.9995)
                 #post_message(myToken,"#coin", "BTC sell : " +str(sell_result))

        
        #sell for profit / slow > fast (5) && fast > 65 
        elif stochastict_slow - stochastict_fast > 4 and stochastict_fast >65:
                btc = get_balance("BTC")             
                print("I need to sell")

                if btc >0.0001:
                 #post_message(myToken,"#coin", "let me sell")
                 sell_result = upbit.sell_market_order("KRW-BTC", btc*0.9995)
                 #post_message(myToken,"#coin", "BTC sell : " +str(sell_result))


        #sell for escape / fast < 8 && slow > fast (5)
        elif 8 > stochastict_fast and stochastict_slow + 5 > stochastict_fast :
                btc = get_balance("BTC")
                print("I need to sell")

                if btc >0.0001:  
                 #post_message(myToken,"#coin", "let me sell")
                 sell_result = upbit.sell_market_order("KRW-BTC", btc*0.9995)
                 #post_message(myToken,"#coin", "BTC sell : " +str(sell_result))
       
        #Doing Nothing, reported on every 25
        else:
            print("I am just watching")
            # if now.minute == 25 :
              #  post_message(myToken,"#coin", "I am just watching")
        """    btc = get_balance("btc") """
        """    if BTC > 0.00008: """
        """        sell_result = upbit.sell_market_order("KRW-ETC", BTC*0.9995) """
        """        post_message(myToken,"#coin", "ETC buy : " +str(sell_result)) """

        time.sleep(5)
        
    except Exception as e:
        print(e)
        post_message(myToken,"#coin", e)
        time.sleep(1)