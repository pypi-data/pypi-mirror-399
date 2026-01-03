from typing import List
import time
from dqtrader.strategy import get_strategy


class Context:
    start_time: float

    def __init__(self):
        self.start_time = 0

    def record_start_time(self):
        self.start_time = time.time()

    # 获取开始时间
    @property
    def begin_date(self) -> str:
        strategy = get_strategy()
        return strategy.begin_date

    # 获取结束时间
    @property
    def end_date(self) -> str:
        strategy = get_strategy()
        return strategy.end_date

    # 获取标的列表
    @property
    def target_list(self) -> List[str]:
        strategy = get_strategy()
        return strategy.target_list

    def execute_time(self):
        return time.time() - self.start_time
