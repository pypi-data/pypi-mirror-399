from decimal import Decimal
from datetime import datetime
import math

import pytest
import asyncio
from .config import CONFIGS



@pytest.mark.asyncio
@pytest.mark.parametrize("client", CONFIGS, indirect=True)
async def test_css(client):
    # res_cn = fundamental_api.css(
    #     vt_symbols=['600519.SSE', '000001.SZSE'],
    #     indicators='ROE,ROETTM,BPS,DIVIDENDYIELDY,LIBILITYTOASSET',
    #     options='ReportDate=MRQ,TradeDate=2024-12-05'
    # )
    from ks_trade_api.constant import SubscribeType, Indicator
    from ks_trade_api.utility import get_file_path, load_json
    from api import KsMarketApi
    from ks_utility.zmqs import zmq
    
    gateway_config_name = 'ks_setting.json'
    gateway_config_path = get_file_path(gateway_config_name)
    config = load_json(gateway_config_path)
    setting_server = config['ks_market_api']['setting']
    setting_client = setting_server.copy()
    setting_client['zmq'] = { 'sub_address': setting_server['zmq']['pub_address'], 'pub_address': setting_server['zmq']['sub_address']}
    
    ks_market_api = KsMarketApi(setting_client)
    def on_indicator(data):
        print(data)
    ks_market_api.on_indicator = on_indicator

    # import time
    # time.sleep(3) # todo!!! 为什么需要这个睡眠时间呢？
    # print('tttttttttttttttttttttttttt')
    ks_market_api.subscribe(
        vt_symbols=['00700.SEHK'],
        types=[SubscribeType.K_HOUR],
        indicators=[Indicator.BOLL]
    )
    
    await client.async_sleep(1000000, log=False)

