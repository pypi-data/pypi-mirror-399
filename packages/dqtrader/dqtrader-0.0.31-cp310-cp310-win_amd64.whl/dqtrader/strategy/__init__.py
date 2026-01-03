# 策略信息
from typing import Dict, List

import dqtrader_rs
from dqtrader import enums
from dqtrader.common import frequency_to_int
from dqtrader.tframe.udefs import ONE_YEAR_AGO, ZERO_YEAR_AGO
from dqtrader.utils import time_utils


class Strategy:
    name: str
    target_list: List[str]
    frequency: str
    begin_date: str
    end_date: str
    fq: int
    frequency_num: int
    benchmark: str
    target_index_dict: Dict[str, int]
    future_combine_dict: Dict[str, str]

    def __init__(self):
        self.target_list = []
        self.name = ""
        self.frequency = "day"
        self.begin_date = ONE_YEAR_AGO.strftime("%Y-%m-%d")
        self.end_date = ZERO_YEAR_AGO.strftime("%Y-%m-%d")
        self.frequency_num = 1
        self.fq = enums.FQType.NA
        self.target_index_dict = {}
        self.future_combine_dict = {}
        self.benchmark = "sse.000300"

    def init_from_config(self, config):
        if "strategy" in config:
            strategy_config = config["strategy"]
            if "name" in strategy_config:
                self.name = strategy_config["name"]
            if "target_list" in strategy_config:
                self.set_target_list(strategy_config["target_list"])
            if "frequency" in strategy_config:
                self.frequency = strategy_config["frequency"]
            if "frequency_num" in strategy_config:
                self.frequency_num = strategy_config["frequency_num"]
            if "begin_date" in strategy_config:
                self.begin_date = strategy_config["begin_date"]
            if "end_date" in strategy_config:
                self.end_date = strategy_config["end_date"]
            if "fq" in strategy_config:
                self.fq = strategy_config["fq"]
            if "benchmark" in strategy_config:
                self.benchmark = strategy_config["benchmark"]

    def set_name(self, name: str):
        self.name = name

    def set_target_list(self, target_list: List[str]):
        self.target_list = [code.upper() for code in target_list]
        self.target_index_dict = {}
        for target in self.target_list:
            self.target_index_dict[target] = len(self.target_index_dict)

    def set_frequency(self, frequency: str):
        self.frequency = frequency

    def frequency_int(self) -> enums.Frequency:
        return frequency_to_int(self.frequency)

    def set_begin_date(self, begin_date: str):
        self.begin_date = begin_date

    def set_end_date(self, end_date: str):
        self.end_date = end_date

    def set_fq(self, fq: int):
        self.fq = fq

    def set_benchmark(self, benchmark: str):
        self.benchmark = benchmark

    def target_index(self, target: str) -> int:
        return self.target_index_dict[target]

    def target(self, target_index: int) -> str:
        return self.target_list[target_index]

    # 是否是股票
    def is_stock(self, target_index: int) -> bool:
        target = self.target_list[target_index]
        return dqtrader_rs.is_stock(target)

    def begin_date_int(self) -> int:
        return time_utils.str_to_ymd(self.begin_date)

    def end_date_int(self) -> int:
        return time_utils.str_to_ymd(self.end_date)

    # 是否是期货
    def is_future(self, target_index: int) -> bool:
        target = self.target_list[target_index]
        return dqtrader_rs.is_future(target)

    def get_type(self, target_index: int) -> int:
        if self.is_stock(target_index):
            return enums.TargetType.STOCK
        elif self.is_future(target_index):
            return enums.TargetType.FUTURE
        else:
            raise NotImplementedError

    def set_real_order_book_id(self, combine_order_book_id: str, real_order_book_id: str):
        self.future_combine_dict[combine_order_book_id.lower()] = real_order_book_id.lower()

    # def target(self, target_index: int) -> str:
    #     return self.target_list[target_index]
    #
    def get_real_target(self, target_index: int) -> str:
        target = self.target_list[target_index]
        real_target = self.future_combine_dict.get(target, None)
        if real_target is None:
            return target
        return real_target
    def get_all_real_target(self) -> List[str]:
        real_targets = []
        for index, target in enumerate(self.target_list):
            real_target = self.future_combine_dict.get(target.lower(), None)
            if real_target is None:
                real_targets.append(target)
            else:
                real_targets.append(real_target)
        return real_targets

_strategy = None


def get_strategy():
    global _strategy
    if _strategy is None:
        _strategy = Strategy()
    return _strategy


def reset_strategy():
    global _strategy
    _strategy = None
