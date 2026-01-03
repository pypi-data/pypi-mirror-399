from typing import List

import dqtrader_rs
import numpy as np
import pandas as pd
from dqtrader.common import frequency_to_int
from dqtrader.enums import Frequency
from dqtrader.backtest.api import check_reg_kdata_precondition, fetch_data
from dqtrader.realtrade import get_env
from dqtrader.strategy import get_strategy
from dqtrader.utils import time_utils


def _reg_driver_kdata(frequency: str, frequency_num: int, adjust=False):
    kdata_list = fetch_data(frequency, frequency_num, adjust)
    env = get_env()
    strategy = get_strategy()
    trading_scope = []
    frequency = strategy.frequency
    # 获取
    # if strategy.frequency_int() == Frequency.Min:
    trading_scope = dqtrader_rs.get_trading_time(strategy.target_list, frequency, frequency_num, "", "")
    env.set_driver_kdata(trading_scope, kdata_list)
    dqtrader_rs.real_trade_subscribe(env.get_task_id(), strategy.target_list, frequency)


def reg_kdata(frequency: str, frequency_num: int, adjust=False):
    frequency_i = frequency_to_int(frequency)
    check_reg_kdata_precondition(frequency_i, frequency_num)
    env = get_env()
    # 注册数据，判断是不是新注册，不是新注册注册就跳过了
    is_new_reg = env.reg_kdata(frequency, frequency_i, frequency_num, adjust)
    if not is_new_reg:
        return
    # 获取当天的时间轴
    strategy = get_strategy()
    # 获取当前交易日的时间轴
    trading_scope = []
    # if frequency_i == Frequency.Min:
    trading_scope = dqtrader_rs.get_trading_time(strategy.target_list, frequency, frequency_num, "", "")
    kdata_list = fetch_data(frequency, frequency_num, adjust)
    env.store_reg_kdata(trading_scope, kdata_list)
    dqtrader_rs.real_trade_subscribe(env.get_task_id(), strategy.target_list, frequency)


def get_reg_kdata(reg_idx: int, target_list=None, length: int = 1, fill_up: bool = False, df=False):
    if target_list is None:
        target_list = []
    if length <= 0:
        raise Exception("length 只能大于等于 1")
    # 分钟线，对比最后一根就好了
    # 合成数据就好了
    strategy = get_strategy()
    env = get_env()
    # 如果输入的标的为空，那么默认获取所有的标的
    if len(target_list) == 0:
        target_list = strategy.target_list
    # 行情的 dict
    kdata_dict = {}
    # 获取 reg_kdata 所注册的索引
    kdata_info = env.get_reg_kdata(reg_idx)
    # 从当前往前合成
    for target in target_list:
        # 构建指定长度的数组
        kdata_dict[target] = [None for _ in range(length)]
        # 获取标的的索引
        target_index = strategy.target_index(target)
        # 根据索引获取对应的 K线 数据
        kdatas = kdata_info.kdatas[target_index]
        kdata_len = len(kdatas)
        # 过滤掉数字为空的标的
        if kdata_len == 0:
            continue
        data_pos = length - 1
        start_index = kdata_len - 1
        if fill_up:
            end_index = kdata_len - 1 - length - 1
            for i in range(start_index, end_index, -1):
                kdata_dict[target][data_pos] = kdatas[i]
                data_pos -= 1
                if data_pos < 0:
                    break
        else:
            for i in range(start_index, -1, -1):
                kdata = kdatas[i]
                if kdata.volume == 0:
                    continue
                kdata_dict[target][data_pos] = kdata
                data_pos -= 1
                if data_pos < 0:
                    break
    if not df:
        return kdata_dict
    kdata_array = []
    target_index = 0
    for target in target_list:
        kdatas = kdata_dict[target]
        #
        for kdata in kdatas:
            if kdata is None:
                kdata_array.append(
                    [target_index, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan])
            else:
                kdata_array.append([target_index, time_utils.ymd_hmss_to_datetime(kdata.datetime), kdata.open,
                                    kdata.high, kdata.low, kdata.close, kdata.volume, kdata.total_turnover,
                                    kdata.open_interest])
        target_index += 1
    df = pd.DataFrame(kdata_array, columns=[
        'target_index', 'time', "open", "high", "low", "close", "volume", "total_turnover", "open_interest"])
    return df


def get_current_bar(target_list=None):
    if target_list is None:
        target_list = []
    strategy = get_strategy()
    env = get_env()
    if len(target_list) == 0:
        target_list = strategy.target_list
    else:
        target_list = [target.upper() for target in target_list]

    kdata_array = []
    kdata_info = env.get_driver_kdata_info()
    for target in target_list:
        target_index = strategy.target_index(target)
        kdatas = kdata_info.kdatas[target_index]
        kdata = kdatas[-1]

        kdata_array.append([target, time_utils.ymd_hmss_to_datetime(kdata.datetime), env.play_bar_index, kdata.open,
                            kdata.high, kdata.low, kdata.close, kdata.volume, kdata.total_turnover,
                            kdata.open_interest])

    df = pd.DataFrame(kdata_array, columns=[
        'code', 'time_bar', "number_bar", "open", "high", "low", "close", "volume", "total_turnover", "open_interest"])

    return df
