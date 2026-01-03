# conftest.py
from logging import DEBUG, INFO, WARNING, ERROR
import pytest
import os
import asyncio
import threading
import time

@pytest.fixture
def client(request, monkeypatch):
    # 设置环境变量 CONFIG 的值
    CONFIG_NAME = request.param['config_name']

    monkeypatch.setenv('CONFIG', CONFIG_NAME)
    assert(os.getenv('CONFIG') == CONFIG_NAME)

    from main import KsMarketApiServer
    from ks_trade_api.utility import get_file_path, load_json

    gateway_config_name = 'ks_setting.json'
    gateway_config_path = get_file_path(gateway_config_name)
    config = load_json(gateway_config_path)
    setting_client = config['ks_market_api']['setting']
    setting_server = setting_client.copy()
    setting_server['zmq'] = { 'sub_address': setting_client['zmq']['sub_address'], 'pub_address': setting_client['zmq']['pub_address']}
    # KsMarketApiServer(setting_server)
    
    server_thread = threading.Thread(
        target=KsMarketApiServer,
        kwargs={"setting": setting_server},
        daemon=True  # 让 pytest 结束时自动关闭服务器
    )
    server_thread.start()
    time.sleep(2)  # 确保服务器已启动

    class Client():
        async def async_sleep(self, seconds: int = 5, log: bool = True):
            count = seconds
            while count > 0:
                await asyncio.sleep(1)
                count -= 1
                log and self.log(f'--------async_sleep-------->: {count}')
    return Client()