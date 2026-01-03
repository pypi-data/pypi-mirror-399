from ks_trade_api.utility import get_file_path, load_json

gateway_config_path = get_file_path('gateway_config.json')
GATEWAY_CONFIG = load_json(gateway_config_path)