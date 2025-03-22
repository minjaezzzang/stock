import yaml
import requests as req
import json

# 설정 파일 불러오기
with open('config.yaml') as f:
    cfg = yaml.load(f, Loader=yaml.FullLoader)

APP_KEY = cfg['APP_KEY']
APP_SECRET = cfg['APP_SECRET']
CANO = cfg['Cano']
ACNT_PRDT_CD = cfg['ACNT_PRDT_CD']
BASE_URL = cfg['URL_BASE']

def hash_key(body):
    """
    API 요청에 필요한 hashkey를 생성하는 함수
    :param body: 요청 본문
    :return: 해시값
    """
    url = f'{BASE_URL}/uapi/hashkey'
    headers = {"content-type": "application/json"}
    return req.post(url, headers=headers, data=json.dumps(body)).json()['HASH']

def get_access_token():
    """
    액세스 토큰을 가져오는 함수
    :return: 액세스 토큰
    """
    url = f'{BASE_URL}/oauth2/tokenP'
    headers = {'Content-Type': "application/json"}
    body = {
        "grant_type": "client_credentials",  # 인증 방식
        "appkey": APP_KEY,
        "appsecret": APP_SECRET
    }
    res = req.post(url, headers=headers, json=body)  # json=body 사용
    res_json = res.json()
    return res_json.get('access_token')

def get_current_price(code: str):
    """
    종목 코드를 입력받아 현재 주가를 조회하는 함수
    :param code: 종목 코드
    :return: 현재 주가
    """
    access_token = get_access_token()
    url = f'{BASE_URL}/uapi/domestic-stock/v1/quotations/inquire-price'
    headers = {
        "Content-Type": "application/json",
        "authorization": f'Bearer {access_token}',
        "appkey": APP_KEY,
        "appsecret": APP_SECRET,
        "tr_id": "FHKST01010100"
    }
    params = {
        "fid_cond_mrkt_div_code": 'J',
        "fid_input_iscd": code
    }
    res = req.get(url=url, params=params, headers=headers)
    res_json = res.json()
    return int(res_json['output']['stck_prpr'])

def get_cash_balance() -> int:
    """
    계좌의 현금 잔고를 조회하는 함수
    :return: 현금 잔고
    """
    access_token = get_access_token()
    url = f'{BASE_URL}/uapi/domestic-stock/v1/trading/inquire-psbl-order'
    headers = {
        'Content-Type': "application/json",
        'authorization': f'Bearer {access_token}',
        'appkey': APP_KEY
    }
    params = {
        'cano': CANO,
        'acnt_prdt_cd': ACNT_PRDT_CD,
        'pdno': "005935",
        'ord_unpr': '50000',
        'ord_dvsn': '01',
        'cma_evlu_amt_acld_yn': 'Y',
        'ovrs_icld_yn': 'Y'
    }
    res = req.get(url, params=params, headers=headers)
    res_json = res.json()
    return int(res_json['output']['ord_psbl_cash'])

def buy(code: str, qty: int) -> None:
    """
    주식을 매수하는 함수
    :param code: 종목 코드
    :param qty: 매수 수량
    :return: 매수 결과
    """
    access_token = get_access_token()
    url = f'{BASE_URL}/uapi/domestic-stock/v1/trading/order-cash'
    body = {
        "CANO": CANO,
        "ACNT_PRDT_CD": ACNT_PRDT_CD,
        "PDNO": code,
        "ORD_DVSN": "01",  # 매수 주문은 "01"
        'ORD_QTY': str(qty),
        'ORD_UNPR': "0"  # 시장가로 매수
    }
    headers = {
        "Content-Type": 'application/json',
        'authorization': f'Bearer {access_token}',
        'appKey': APP_KEY,
        'appSecret': APP_SECRET,
        'tr_id': 'TTTC0802U',
        'custtype': 'P',
        'hashkey': hash_key(body)
    }
    res = req.post(url, headers=headers, data=json.dumps(body))
    res_json = res.json()
    success = res_json['rt_cd']
    print(f'{res_json["msg1"]}')
    return success == 0

def sell(code: str, qty: int) -> None:
    """
    주식을 매도하는 함수
    :param code: 종목 코드
    :param qty: 매도 수량
    :return: 매도 결과
    """
    access_token = get_access_token()
    url = f'{BASE_URL}/uapi/domestic-stock/v1/trading/order-cash'
    body = {
        "CANO": CANO,
        "ACNT_PRDT_CD": ACNT_PRDT_CD,
        "PDNO": code,
        "ORD_DVSN": "02",  # 매도 주문은 "02"
        'ORD_QTY': str(qty),
        'ORD_UNPR': "0"  # 시장가로 매도
    }
    headers = {
        "Content-Type": 'application/json',
        'authorization': f'Bearer {access_token}',
        'appKey': APP_KEY,
        'appSecret': APP_SECRET,
        'tr_id': 'TTTC0802U',
        'custtype': 'P',
        'hashkey': hash_key(body)
    }
    res = req.post(url, headers=headers, data=json.dumps(body))
    res_json = res.json()
    success = res_json['rt_cd']
    print(f'{res_json["msg1"]}')
    return success == 0
def get_stock_balance(code: str):
    """현재 보유하고 있는 특정 주식의 수량을 조회하는 함수"""
    access_token = get_access_token()
    url = f'{BASE_URL}/uapi/domestic-stock/v1/trading/inquire-psbl-order'
    
    # 요청 헤더
    headers = {
        "Content-Type": "application/json",
        "authorization": f'Bearer {access_token}',
        "appkey": APP_KEY,
        "appsecret": APP_SECRET,
        "tr_id": "FHKST01010100"
    }
    
    # 파라미터: 종목 코드(code)에 대해 보유 수량을 조회
    params = {
        'cano': CANO,
        'acnt_prdt_cd': ACNT_PRDT_CD,
        'pdno': code,  # 종목 코드
    }
    
    # API 호출
    res = req.get(url, params=params, headers=headers)
    res_json = res.json()
    
    # 응답 결과에서 보유 수량 추출
    if res_json['rt_cd'] == '0000':
        stock_qty = res_json['output'][0].get('qty', 0)  # 보유 수량
        return stock_qty
    else:
        print(f"에러 발생: {res_json['msg1']}")
        return 0


