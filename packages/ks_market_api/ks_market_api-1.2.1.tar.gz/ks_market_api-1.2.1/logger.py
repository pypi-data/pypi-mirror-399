from ks_utility.logs import LoggerBase
from pathlib import Path

class Logger(LoggerBase):
    def __init__(self, path=None, name=None):
        if not path:
            path = Path('data/logs')
        if not name:
            name = 'ks_market_engine'
        super().__init__(path, name)