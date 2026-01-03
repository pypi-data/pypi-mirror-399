from ks_futu_market_api import KsFutuMarketApi
from ks_trade_api.constant import SubscribeType, RET_OK, RET_ERROR, Interval, Adjustment

symbol = '00700.SEHK'
symbol1 = '09988.SEHK'
interval = Interval.MONTH

api = KsFutuMarketApi({"security_firm": "FUTUSG", "port": 11112})
api.subscribe(symbol, [SubscribeType.BOOK, SubscribeType.K_MONTH])
api.subscribe(symbol1, [SubscribeType.BOOK, SubscribeType.K_MONTH])

ret_k, data_k = api.query_history_n(symbol, 20, interval=interval, adjustment=Adjustment.BACKWARD_ADJUSTMENT, extended_time=False)
ret_k1, data_k1 = api.query_history_n(symbol1, 20, interval=interval, adjustment=Adjustment.BACKWARD_ADJUSTMENT, extended_time=False)
if ret_k == RET_OK:
    print(data_k)
api.close()

