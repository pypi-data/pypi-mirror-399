import multiprocessing
import threading
import numpy as np
import talib
from ks_trade_api.constant import Adjustment, RET_OK, SUBSCRIBE_TYPE2INTERVAL, IndicatorColumn, Interval, Indicator, Timing, SubscribeType
from ks_trade_api.object import BarData
from ks_futu_market_api import KsFutuMarketApi
from ks_utility.zmqs import ZmqPublisher, ZmqSubscriber
from logger import Logger
import time
from pathlib import Path
import json
import os
from setting import SETTINGS
from ks_trade_api.utility import TEMP_DIR, extract_vt_symbol
import sys
import pandas as pd

PARAMS2ENUM: dict = {
    'types': SubscribeType,
    'indicators': Indicator
}

def process_b(bar: BarData, close_shared_dict: dict, datetime_shared_dict: dict, indicator_shared_queue: multiprocessing.Queue):
    """ 计算不同周期的 price 均值 """
    vt_symbol = bar.vt_symbol
    interval = bar.interval  # 取出当前数据的周期
    
    history_updated = False
    history_datetime = None
    empty = not len(datetime_shared_dict[vt_symbol][interval])
    if empty or datetime_shared_dict[vt_symbol][interval][-1] < bar.datetime:
        if not empty:
            history_datetime = datetime_shared_dict[vt_symbol][interval][-1]
            print(f'[{vt_symbol},{interval}]history_updated!!!!!!!!!!!!!!@{history_datetime}')
        close_shared_dict[vt_symbol][interval]._callmethod("append", (float(bar.close),))
        datetime_shared_dict[vt_symbol][interval]._callmethod("append", (bar.datetime,))
        close_shared_dict[vt_symbol][interval][:] = close_shared_dict[vt_symbol][interval][-21:]
        datetime_shared_dict[vt_symbol][interval][:] = datetime_shared_dict[vt_symbol][interval][-21:]
        history_updated = True
    else:
        close_shared_dict[-1] = float(bar.close)

    close_prices = np.array(close_shared_dict[vt_symbol][interval])
    bars = []
    boll_band = talib.BBANDS(close_prices[-20:], timeperiod=20)

    # 没有够20跟bar，不计算
    if len(close_prices) < 20:
        return
    
    if history_updated:
        # todo! 为了性能考虑，先不要广播realtime_bar了
        # realtime_bar = {
        #     'symbol': bar.symbol, 
        #     'exchange': bar.exchange.value,
        #     'datetime': str(bar.datetime),
        #     'interval': interval.value, 
        #     'indicator': Indicator.BAR.value,
        #     'timing': Timing.REALTIME.value, 
        #     'data': {
        #         IndicatorColumn.BARCLOSE.name: close_prices[-1]
        #     }
        # }
        
        history_bar = {
            'symbol': bar.symbol, 
            'exchange': bar.exchange.value,
            'datetime': str(history_datetime),
            'interval': interval.value, 
            'indicator': Indicator.BAR.value,
            'timing': Timing.HISTORY.value, 
            'data': {
                IndicatorColumn.BARCLOSE.name: close_prices[-2]
            }
        }
        bars.append(history_bar)
        
        # pdb.set_trace()
        boll_band = talib.BBANDS(close_prices, timeperiod=20)
        realtime_boll = {
            'symbol': bar.symbol, 
            'exchange': bar.exchange.value,
            'datetime': str(bar.datetime),
            'interval': interval.value, 
            'indicator': Indicator.BOLL.value,
            'timing': Timing.REALTIME.value, 
            'data': {
                IndicatorColumn.BOLLUPPER.name: boll_band[0][-1], 
                IndicatorColumn.BOLLMIDDLE.name: boll_band[1][-1], 
                IndicatorColumn.BOLLLOWER.name: boll_band[2][-1]
            }
        }
        history_boll = {
            'symbol': bar.symbol, 
            
            'exchange': bar.exchange.value,
            'datetime': str(history_datetime),
            'interval': interval.value, 
            'indicator': Indicator.BOLL.value,
            'timing': Timing.HISTORY.value, 
            'data': {
                IndicatorColumn.BOLLUPPER.name: boll_band[0][-2],
                IndicatorColumn.BOLLMIDDLE.name: boll_band[1][-2], 
                IndicatorColumn.BOLLLOWER.name: boll_band[2][-2]
            }
        }
        bars.append(realtime_boll)
        bars.append(history_boll)
    else:
        # pdb.set_trace()
        boll_band = talib.BBANDS(close_prices[-20:], timeperiod=20)
        realtime_boll = {
            'symbol': bar.symbol, 
            'exchange': bar.exchange.value,
            'datetime': str(bar.datetime),
            'interval': interval.value, 
            'indicator': Indicator.BOLL.value,
            'timing': Timing.REALTIME.value, 
            'data': {
                IndicatorColumn.BOLLUPPER.name: boll_band[0][-1],
                IndicatorColumn.BOLLMIDDLE.name: boll_band[1][-1],
                IndicatorColumn.BOLLLOWER.name: boll_band[2][-1]
            }
        }
        bars.append(realtime_boll)
    
    if bars:
        indicator_shared_queue.put(bars)

    # pid = os.getpid()  # 获取当前进程 ID
    # print(f"[进程 {pid}] 股票: {vt_symbol} | 周期: {interval}")


class KsMarketApiServer(ZmqPublisher, ZmqSubscriber, Logger):
    gateway_name: str = 'ks_market_api'
    
    def __init__(self, setting: dict):
        ZmqPublisher.__init__(self, setting['zmq']['pub_address'], server=True)
        ZmqSubscriber.__init__(self, setting['zmq']['sub_address'], server=True)
        
        log_path = TEMP_DIR.joinpath('logs').joinpath('ks_trader_api')
        Logger.__init__(self, path=log_path, name='ks_market_api')
        
        self.log(setting)
        
        self.log('KsMarketApiServer初始化...')

        self.gateway_name = setting.get('gateway_name', self.gateway_name)
        self.market_api = KsFutuMarketApi(setting)

        self.running = True
        self.pool = multiprocessing.Pool(processes=setting.get('pool_size', 1))
        self.manager = multiprocessing.Manager()
        self.close_shared_dict = self.manager.dict() # 储存股票数据 股票->周期->收盘价
        self.datetime_shared_dict = self.manager.dict() # 储存股票数据 股票->周期->时间
        self.indicator_shared_queue = self.manager.Queue() # 储存计算好的布林带值
        self.bar_shared_queue = self.manager.Queue() # 储存计算好的布林带值

        def on_bar_rt(bar: BarData):
            self.bar_shared_queue.put(bar)

        self.market_api.on_bar_rt = on_bar_rt
        
        # 启动后台线程运行主循环
        self.indicator_thread = threading.Thread(target=self.process_indicator)
        self.indicator_thread.start()
        
        self.log('KsMarketApiServer初始化完成.')
        
        self.process_bar()
        
    def update_shared_dict(self, vt_symbol: str, interval: Interval):
        if not vt_symbol in self.close_shared_dict:
            self.close_shared_dict[vt_symbol] = self.manager.dict()
        self.close_shared_dict[vt_symbol][interval] = self.manager.list()
            
        if not vt_symbol in self.datetime_shared_dict:
            self.datetime_shared_dict[vt_symbol] = self.manager.dict()
        self.datetime_shared_dict[vt_symbol][interval] = self.manager.list()

    def on_message(self, topic, msg):
        msg_data = json.loads(msg)
        # todo 以后可能不是都传入list
        for param, value_list in msg_data.items():
            if param in PARAMS2ENUM:
                msg_data[param] = [PARAMS2ENUM[param](x) for x in value_list]
        if topic == 'close':
            self.close()
        elif topic == 'subscribe':
            self.subscribe(**msg_data)

    def subscribe(
            self,
            vt_symbols: list[str] = [], 
            types: list[SubscribeType] = [], 
            indicators: list[Indicator] = [],
            data_time_types: list[Timing] = []
        ):
        api = self.market_api
        # 订阅市场数据
        api.subscribe(vt_symbols, types)
        for subscribe_type in types:
            for vt_symbol in vt_symbols:
                interval = SUBSCRIBE_TYPE2INTERVAL.get(subscribe_type)
                if not interval == Interval.TICK:
                    ret_k, data_k = api.query_history_n(vt_symbol, 20, interval=interval, adjustment=Adjustment.BACKWARD_ADJUSTMENT)
                    if ret_k == RET_OK:
                        self.log(f'{vt_symbol},{interval.value}历史bars查询成功')
                        if not len(data_k):
                            self.log(f'{vt_symbol}的历史K线长度为0')
                            continue
                        
                        # 字符串转为enum
                        data_k['interval'] = data_k['interval'].transform(Interval)
                        data_k[['symbol', 'exchange']] = data_k['vt_symbol'].apply(lambda x: pd.Series(extract_vt_symbol(x)))
                        
                        self.update_shared_dict(vt_symbol, interval)
                        self.close_shared_dict[vt_symbol][interval]._callmethod('extend', (data_k.close.tolist(),))
                        self.datetime_shared_dict[vt_symbol][interval]._callmethod('extend', (data_k.datetime.tolist(),))


    def process_bar(self):
        """ 处理布林带计算结果 """
        
        while self.running:
            bar = self.bar_shared_queue.get()
            if bar is None:
                break
            
            self.pool.apply_async(process_b, (bar, self.close_shared_dict, self.datetime_shared_dict, self.indicator_shared_queue))  # 提交任务到进程池

    def process_indicator(self):
        """ 处理布林带计算结果 """
        while self.running:
            bars = self.indicator_shared_queue.get()
            if bars is None:
                break
            
            for bar in bars:
                bar['gateway_name'] = self.gateway_name
                # print(bar) # todo
                self.send('on_indicator', bar)

    def close(self):
        """ 关闭所有进程 """
        
        self.market_api.close()
        
        self.bar_shared_queue.put(None)
        self.indicator_shared_queue.put(None)
        self.indicator_thread.join()
        
        self.running = False
        self.pool.close()
        self.pool.join()
        
        self.send('on_close', {})
        
        ZmqPublisher.stop(self)
        ZmqSubscriber.stop(self)
        
        self.log('全部线程进程已经关闭.')
        sys.exit(0)
        


if __name__ == '__main__':
    multiprocessing.freeze_support() # 支持pyinstaller打包多进程

    api_setting = SETTINGS['ks_market_api']['setting']
    KsMarketApiServer(api_setting)
    
