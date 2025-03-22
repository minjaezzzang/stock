import threading as trd
import time
import functools
from funcs import *  # 종목 가격을 가져오는 함수
start = get_cash_balance()
# 종목 코드 입력받기
a = input('종목 코드를 공백 또는 쉼표로 구분하시오: ')
codes = [code.strip() for code in a.replace(',', ' ').split()]
profit_target = int(input('한 번 팔 때 목표 이득 (한 주 기준): '))
profit_goal = int(input('최종 목표 이득: '))

# 공유 딕셔너리 생성 (쓰레드 간 안전하게 데이터를 공유)
pricedict = {}

# 최근 n일 간의 주식 가격 변화율 계산 함수
def calculate_momentum(code, days=5):
    """주어진 기간(days) 동안의 주식 가격 변화율을 계산"""
    prices = [get_current_price(code) for _ in range(days)]
    if len(prices) < days:
        return 0
    price_change = (prices[-1] - prices[0]) / prices[0] * 100  # 변화율(%)
    return price_change

def loop_inf(func):
    """
    함수를 무한히 반복 실행하는 데코레이터
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        while True:
            result = func(*args, **kwargs)
            time.sleep(0.5)  # 너무 빠른 요청 방지, 적절한 딜레이 조정
    return wrapper

@loop_inf
def save_price_dict():
    global pricedict
    prices = [get_current_price(code) for code in codes]
    pricedict = dict(zip(codes, prices))
    print("현재 가격:", pricedict)  # 현재 가격 출력

# 쓰레드로 가격 저장을 반복적으로 실행
thread = trd.Thread(target=save_price_dict)
thread.start()

@loop_inf
def do_algolizm(code, first_price):
    """
    모멘텀 전략을 기반으로 매매하는 알고리즘 함수:
    - 상승 모멘텀(변화율 > 0)일 때 매수
    - 하락 모멘텀(변화율 < 0)일 때 매도
    - 목표 이득에 도달하면 매도
    """
    print(f'잔액:{get_cash_balance()} \n현재 이익:{abs(start-get_cash_balance)},{code} 주식 {get_stock_balance(code)}')
    # 최근 5일 간의 가격 변화율 계산
    momentum = calculate_momentum(code, days=5)

    if momentum > 0:  # 상승 모멘텀
        print(f'{code} 종목 상승 모멘텀 감지! 변화율: {momentum}%')
        current_price = get_current_price(code)
        if first_price is None:  # 첫 매수 시점이 없으면 매수
            first_price = current_price
            print(f'{code} 종목 매수! 첫 가격: {first_price}')

    elif momentum < 0:  # 하락 모멘텀
        print(f'{code} 종목 하락 모멘텀 감지! 변화율: {momentum}%')
        current_price = get_current_price(code)
        if first_price is not None and current_price < first_price:  # 매수 후 가격이 하락하면 매도
            print(f'{code} 종목 매도! 현재 가격: {current_price}, 첫 가격: {first_price}')
            sell(code, 1)  # 예시로 1주를 팔기
            first_price = None  # 매도 후 첫 가격 초기화

    # 목표 이득에 도달하면 매도
    current_price = get_current_price(code)
    price_diff = current_price - first_price if first_price else 0
    if price_diff >= profit_target:
        print(f'{code} 종목, 목표 이득 도달! 현재 가격: {current_price}, 첫 가격: {first_price}')
        sell(code, 1)  # 예시로 1주를 팔기
        first_price = None  # 매도 후 첫 가격 초기화

    # 최종 목표 이득에 도달했으면 종료
    if price_diff >= profit_goal:
        print(f'{code} 종목, 최종 목표 이득 도달! 현재 가격: {current_price}, 첫 가격: {first_price}')
        sell(code, 1)  # 예시로 1주를 팔기  # 종료 상태를 반환하여 알고리즘 종료

    print(f'{code} 종목, 현재 가격: {current_price}, 모멘텀: {momentum}%')
threads = []
for code in codes:
    threads.append(trd.Thread(target=do_algolizm,args=(code,get_current_price(code))))
for thread in threads:
    thread.start()
    

