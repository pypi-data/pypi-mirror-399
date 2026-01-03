import multiprocessing
import time
import random
import os


class BarData:
    """ 保存股票数据 """
    def __init__(self, price, volume, symbol, period):
        self.price = price
        self.volume = volume
        self.symbol = symbol
        self.period = period  # ✅ 每条数据带上周期

    def __repr__(self):
        return f"BarData(price={self.price}, volume={self.volume}, symbol={self.symbol}, period={self.period})"


def process_b(bar_data, shared_dict):
    """ 计算不同周期的 price 均值 """
    pid = os.getpid()  # 获取当前进程 ID
    symbol = bar_data.symbol
    period = bar_data.period  # ✅ 取出当前数据的周期

    # ✅ 确保 symbol 在共享数据中
    if symbol not in shared_dict:
        print(f"[进程 {pid}] {symbol} 不在 shared_dict 中，数据丢失！")
        return

    # ✅ 确保 symbol 下有该周期的价格列表
    if period not in shared_dict[symbol]:
        shared_dict[symbol][period] = multiprocessing.Manager().list()

    price_list = shared_dict[symbol][period]
    price_list.append(bar_data.price)

    if len(price_list) > period:
        price_list.pop(0)  # 只保留最近 `period` 个价格

    avg_price = sum(price_list) / len(price_list)

    print(f"[进程 {pid}] 股票: {symbol} | 周期: {period} | 最近 {period} 个 price: {list(price_list)} | 均值: {avg_price:.2f}")




if __name__ == "__main__":
    stock_symbols = ["AAPL", "TSLA", "AMZN", "MSFT"]
    periods = [3, 5, 10]  # ✅ 支持多个周期
    pool_size = 4  

    manager = multiprocessing.Manager()
    shared_dict = manager.dict()  # 使用共享字典存储 {symbol: {周期1: [最近N个price], 周期2: [...]}}
    
    # ✅ 初始化 shared_dict
    for symbol in stock_symbols:
        shared_dict[symbol] = manager.dict()  
        for period in periods:
            shared_dict[symbol][period] = manager.list()  # 每个周期都有自己的价格列表

    pool = multiprocessing.Pool(processes=pool_size)

    try:
        while True:
            # 生成随机股票数据
            symbol = random.choice(stock_symbols)
            price = random.randint(100, 500)
            volume = random.randint(10, 100)
            period = random.choice(periods)  # ✅ 随机选择一个周期

            bar_data = BarData(price, volume, symbol, period)
            pool.apply_async(process_b, (bar_data, shared_dict))  # 提交任务到进程池

            time.sleep(0.5)  # 模拟 on_bar 调用频率

    except KeyboardInterrupt:
        print("主进程退出，关闭进程池...")
        pool.close()
        pool.join()
        

