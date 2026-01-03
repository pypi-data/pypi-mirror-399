from threading import RLock, Thread
from datetime import datetime
from time import sleep
from futu import OpenQuoteContext
from futu.common.open_context_base import OpenContextBase, ContextStatus
from futu.common.callback_executor import CallbackExecutor, CallbackItem
from futu.common.network_manager import NetManager, PacketErr, ConnectErr, CloseReason
from futu.common.handler_context import HandlerContext
from futu.common.sys_config import SysConfig
from futu.common.err import Err
from futu.common.constant import RET_OK
from futu.quote.open_quote_context import SubRecord

class KsOpenContextBase(OpenContextBase):
    def __init__(self, host, port, is_encrypt=None, is_async_connect=False):
        self.__host = host
        self.__port = port
        self._callback_executor = CallbackExecutor()
        self._net_mgr = NetManager.default()
        self._handler_ctx = HandlerContext(self._is_proc_run)
        self._lock = RLock()
        self._status = ContextStatus.START
        self._connect_err = None  # rsa加密失败时为Err.RsaErr, 否则为str
        self._proc_run = True
        self._sync_conn_id = 0
        self._conn_id = 0
        self._keep_alive_interval = 10
        self._last_keep_alive_time = datetime.now()
        self._reconnect_timer = None
        self._reconnect_interval = 8  # 重试连接的间隔
        self._sync_query_connect_timeout = None
        self._keep_alive_fail_count = 0
        self._last_recv_time = datetime.now()
        self._is_encrypt = is_encrypt
        if self.is_encrypt():
            assert SysConfig.INIT_RSA_FILE != '', Err.NotSetRSAFile.text
        self._net_mgr.start()

        if is_async_connect:
            self._wait_reconnect(0)
        else:
            while True:
                ret = self._init_connect_sync()
                if ret == RET_OK:
                    return
                else:
                    if self.status == ContextStatus.CLOSED:
                        return
                sleep(self._reconnect_interval)
    
class KsOpenQuoteContext(KsOpenContextBase):
    def __init__(self, host='127.0.0.1', port=11111, is_encrypt=None, is_async_connect=False):
        """
        初始化Context对象
        :param host: host地址
        :param port: 端口
        """
        self._ctx_subscribe = {}
        self._sub_record = SubRecord()
        super(KsOpenContextBase, self).__init__(
            host, port, is_encrypt=is_encrypt, is_async_connect=is_async_connect)