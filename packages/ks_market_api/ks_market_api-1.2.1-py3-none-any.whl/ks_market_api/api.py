from ks_utility.zmqs import ZmqPublisher, ZmqSubscriber
from ks_trade_api.constant import SubscribeType, Indicator, Timing, RET_OK, Exchange, Interval
from ks_trade_api.object import IndicatorData
from dateutil.parser import parse
import json
import traceback

class KsMarketApi(ZmqPublisher, ZmqSubscriber):
    gateway_name: str = 'ks_market_api'
    
    def __init__(self, setting: dict = {}):
        self.gateway_name = setting.get('gateway_name', self.gateway_name)
        
        pub_address: str = setting.get('zmq', {}).get('pub_address')
        sub_address: str = setting.get('zmq', {}).get('sub_address')
        if not sub_address:
            from config import GATEWAY_CONFIG
            sub_address = GATEWAY_CONFIG['ks_market_api']['setting']['zmq']['sub_address']
        if not pub_address:
            pub_address = GATEWAY_CONFIG['ks_market_api']['setting']['zmq']['pub_address']
        ZmqPublisher.__init__(self, pub_address)
        ZmqSubscriber.__init__(self, sub_address)

    def subscribe(
            self,
            vt_symbols: list[str] = [], 
            types: list[SubscribeType] = [], 
            indicators: list[Indicator] = [],
            data_time_types: list[Timing] = []
        ):
        types = [x.value for x in types]
        indicators = [x.value for x in indicators]
        data_time_types = [x.value for x in data_time_types]
        self.send('subscribe', {'vt_symbols': vt_symbols, 'types': types, 'indicators': indicators, 'data_time_types': data_time_types})
        return RET_OK, None

    def on_indicator(self, indicator):
        pass
    
    def on_close(self, data: dict = {}):
        pass

    def on_message(self, topic: str, msg: str):
        msg_data = json.loads(msg)
        if topic == 'on_close':
            self.on_close(msg_data)
            ZmqPublisher.stop(self)
            ZmqSubscriber.stop(self)
            return
        
        try:
            indicator = IndicatorData(
                gateway_name=msg_data['gateway_name'],
                symbol=msg_data['symbol'],
                exchange=Exchange(msg_data['exchange']),
                datetime=parse(msg_data['datetime']),
                indicator=Indicator(msg_data['indicator']),
                interval=Interval(msg_data['interval']),
                timing=Timing(msg_data['timing']),
                data=msg_data['data']  
            )
            getattr(self, topic)(indicator)
        except:
            traceback.print_exc()
            
    def close(self):
        self.send('close', {})

if __name__ == '__main__':
    ks_market_api = KsMarketApi()
