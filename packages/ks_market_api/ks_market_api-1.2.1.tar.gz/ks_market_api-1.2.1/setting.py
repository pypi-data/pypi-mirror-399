from ks_trade_api.utility import load_json, TEMP_NAME
from typing import Dict, Any
from logging import INFO
from pathlib import Path
import os
import sys

SETTINGS: Dict[str, Any] = {
    "ks_market_api": {
        "name": "ks_market_api",
        "setting": {
            "security_firm": "FUTUSG",
            "port": 11111,
            "zmq": {
                "pub_address": "tcp://127.0.0.1:2000",
                "sub_address": "tcp://127.0.0.1:2001"
            }
        }
    }
}


# Load global setting from json file.
SETTING_FILENAME: str = "ks_setting.json"
SETTINGS.update(load_json(SETTING_FILENAME))
