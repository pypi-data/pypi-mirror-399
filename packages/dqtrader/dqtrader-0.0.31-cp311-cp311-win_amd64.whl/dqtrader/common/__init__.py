import bisect
from datetime import datetime
from typing import Union, Iterable

from dqtrader.enums import  Frequency
from dqtrader.utils.time_utils import to_datetime


_frequency_str_to_int_dict = {
    'tick': Frequency.Tick,
    'sec': Frequency.Second,
    'min': Frequency.Min,
    'day': Frequency.Day,
    'week': Frequency.Week,
    'month': Frequency.Month,
    'year': Frequency.Year,
}


def frequency_to_int(frequency: str) -> int | None:
    return _frequency_str_to_int_dict.get(str.lower(frequency))



def check_begin_end_date(begin_date, end_date):
    """
    一、输入的整形数据是否符合datatime的要求
    二、判断输入的时间是否在可控区间内
    三、结束时间不能小于开始时间

    :param begin: int/str, like: 20120119
    :param end: int/str, like:20120120
    :return: None
    """
    _b = to_datetime(begin_date)
    _e = to_datetime(end_date)
    min_time = datetime(1900, 1, 1)
    now_time = datetime.now()
    if min_time < _b < now_time and min_time < _e < now_time:
        if _b > _e:
            raise ValueError('start date {} > stop date {}'.format(_b, _e))
    else:
        raise ValueError('Expect date from 1900 to now')


def market_str_to_int(market: str) -> int:
    market = market.lower()
    if market == "szse":
        return 1
    elif market == 2:
        return 2
    elif market == "shfe":
        return 3
    elif market == "dce":
        return 4
    elif market == "czce":
        return 5
    elif market == "cffex":
        return 6
    elif market == "ine":
        return 7
    elif market == "gfex":
        return 8
    else:
        return 0


class SortedIntSet:
    def __init__(self):
        self.data = []

    def add(self, value: Union[int, Iterable[int]]):
        """可以添加单个整数或多个整数"""
        if isinstance(value, int):
            self._add_one(value)
        else:
            for v in value:
                self._add_one(v)

    def _add_one(self, value: int):
        idx = bisect.bisect_left(self.data, value)
        # 只有当该值不存在时才插入（确保去重）
        if idx == len(self.data) or self.data[idx] != value:
            self.data.insert(idx, value)
    def get_ge(self, value: int):
        """如果存在该值，返回该值；否则返回第一个大于该值的元素；如果没有更大元素，返回 None"""
        idx = bisect.bisect_left(self.data, value)
        if idx < len(self.data):
            return self.data[idx]
        return None

