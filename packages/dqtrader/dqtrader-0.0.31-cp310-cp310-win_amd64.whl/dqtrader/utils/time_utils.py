from collections.abc import Iterable
from datetime import datetime, date, timedelta
import pandas as pd


def to_datetime(ts: str | Iterable, fmt: str = '%Y-%m-%d'):
    """
    将整形转变为datetime类型
    :param ts: int/str, 形如：2012-01-01
    :param fmt: 格式化字符串
    :return: datetime
    """
    ls = ts
    is_iterable = not isinstance(ts, str) and isinstance(ts, Iterable)
    if not is_iterable:
        ls = [ts]
    result = [datetime.strptime(str(dt), fmt) for dt in ls]
    return result if is_iterable else result[0]


def cur_time_str():
    current_time = datetime.now()
    return current_time.strftime("%Y-%m-%d %H:%M:%S")


def cur_date_str():
    current_time = datetime.now()
    return current_time.strftime("%Y-%m-%d")


def ymd_hmss_to_str(value: int) -> str:
    str_time = str(value)
    # 提取年、月、日、时、分、秒
    year = str_time[:4]
    month = str_time[4:6]
    day = str_time[6:8]
    hour = str_time[8:10]
    minute = str_time[10:12]
    second = str_time[12:14]
    return f"{year}-{month}-{day} {hour}:{minute}:{second}"


def ymd_to_str(value: int) -> str:
    str_time = str(value)
    # 提取年、月、日、时、分、秒
    year = str_time[:4]
    month = str_time[4:6]
    day = str_time[6:8]
    return f"{year}-{month}-{day}"


def str_to_ymd(value: str) -> int:
    new_date = value.replace("-", "")
    return int(new_date)


def ymd_to_date(int_date):
    if int_date == 0:
        return pd.NaT
    year = int_date // 10000
    month = int_date // 100 % 100
    day = int_date % 100
    return date(year, month, day)


def ymd_hmss_to_datetime(value: int):
    if value == 0:
        return pd.NaT
    year = value // 1_00_00_00_00_00_000
    month = value // 1_00_00_00_00_000 % 100
    day = value // 1_00_00_00_000 % 100
    hour = value // 1_00_00_000 % 100
    minute = value // 1_00_000 % 100
    second = value // 1000 % 100

    ms = value % 1000


    return datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=second, microsecond=ms*1000)


def datetime_to_ymd_hmss(obj: datetime) -> int:
    return obj.year * 1_00_00_00_00_00_000 + obj.month * 1_00_00_00_00_000 + obj.day * 1_00_00_00_000 + obj.hour * 1_00_00_000 + obj.minute * 1_00_000 + obj.second * 1000


def cur_ymd_hmss() -> int:
    obj = datetime.now()
    return obj.year * 1_00_00_00_00_00_000 + obj.month * 1_00_00_00_00_000 + obj.day * 1_00_00_00_000 + obj.hour * 1_00_00_000 + obj.minute * 1_00_000 + obj.second * 1000


def ymd_hmss_add_minutes(value: int, minutes: int):
    datetime_obj = ymd_hmss_to_datetime(value)
    datetime_obj = datetime_obj + timedelta(minutes=minutes)
    return datetime_to_ymd_hmss(datetime_obj)
