import pandas as pd
from math import nan
import numpy as np
from typing import Dict, List
import dqtrader_rs
from pandas import DataFrame

from dqtrader.backtest_environment import get_env
from dqtrader.strategy import get_strategy
from dqtrader.tframe.language.chinese import text
from dqtrader.utils import time_utils

__all__ = [
    "reg_factor",
    # "get_backtest_reg_factor",
    # "get_realtrade_reg_factor",
    "reg_custom_factor",
    # "get_backtest_reg_custom_factor"
]


def reg_factor(factors: List[str]):
    if isinstance(factors, str):
        factors = [factors]
    else:
        factors = list(factors)
    if len(factors) < 1:
        raise ValueError(text.ERROR_INPUT_FACTOR_TOTAL)
    strategy = get_strategy()
    env = get_env()

    env.store_reg_factor_idx(factors)

    for factor in factors:
        # 因子是否存在，存在不在获取
        if env.exist_factor_data(factor):
            continue
        factor_data = dqtrader_rs.get_factor(
            factor, strategy.target_list, strategy.begin_date, strategy.end_date)
        env.store_reg_factor(factor, factor_data)


def get_backtest_reg_factor(reg_idx: int, target_list: List[str] = [], length: int = 1) -> DataFrame:
    #
    env = get_env()
    strategy = get_strategy()
    # 如果输入的标的为空，那么默认获取所有的标的
    if len(target_list) == 0:
        target_list = strategy.target_list
    #

    factor_names = env.get_reg_factor_by_idx(reg_idx)
    factor_array = []  # 要增加

    for factor_name in factor_names:
        factor_info = env.get_reg_factor(factor_name)
        if factor_info is None:
            return None
        # 标的
        # 当前推送到的索引
        play_bar_index = env.play_bar_index
        real_kdata_index = factor_info.get_factor_index(play_bar_index)
        start_pos = max(real_kdata_index - length + 1, 0)
        last_arr_size = len(factor_array)

        for target in target_list:
            target_index = strategy.target_index(target)
            for i in range(length):
                factor_array.append([target_index, pd.NaT, "", np.nan])

        for target in target_list:
            target_index = strategy.target_index(target)
            target_factor_data = factor_info.factor_datas[target_index]
            array_index = length - 1
            target_play_index = 0
            for i in range(start_pos, real_kdata_index + 1):
                #
                factor_array[target_index * length + array_index + last_arr_size] = [
                    int(target_index),
                    time_utils.ymd_to_date(int(factor_info.dates[real_kdata_index - target_play_index])),
                    factor_name,
                    target_factor_data[real_kdata_index - target_play_index]
                ]
                array_index -= 1
                target_play_index += 1

    df = pd.DataFrame(factor_array, columns=[
        'target_index', 'date', "factor", "value"])
    return df.round(5)


def get_realtrade_reg_factor(reg_idx: int, target_list: List[str] = [], length: int = 1) -> DataFrame:
    env = get_env()
    strategy = get_strategy()
    # 如果输入的标的为空，那么默认获取所有的标的
    if len(target_list) == 0:
        target_list = strategy.target_list
    #
    factor_names = env.get_reg_factor_by_idx(reg_idx)
    factor_array = []  # 要增加

    array_index = 0
    for factor_name in factor_names:
        factor_info = env.get_reg_factor(factor_name)
        if factor_info is None:
            return None

        for target in target_list:
            target_index = strategy.target_index(target)
            for i in range(length):
                factor_array.append([target_index, pd.NaT, "", np.nan])

        for target in target_list:
            target_index = strategy.target_index(target)
            target_factor_data = factor_info.factor_datas[target_index]
            real_kdata_index = len(target_factor_data)
            start_pos = real_kdata_index - length


            for i in range(start_pos, real_kdata_index):
                #
                factor_array[target_index * length + array_index] = [
                    int(target_index),
                    time_utils.ymd_to_date(int(factor_info.dates[i])),
                    factor_name,
                    target_factor_data[i]
                ]
                array_index += 1
                # target_play_index += 1

    df = pd.DataFrame(factor_array, columns=[
        'target_index', 'date', "factor", "value"])
    return df.round(5)


def reg_custom_factor(factors: List[str]):
    if isinstance(factors, str):
        factors = [factors]
    else:
        factors = list(factors)
    if len(factors) < 1:
        raise ValueError(text.ERROR_INPUT_FACTOR_TOTAL)
    strategy = get_strategy()
    env = get_env()

    env.store_reg_custom_factor_idx(factors)
    for factor in factors:
        # 因子是否存在，存在不在获取
        if env.exist_custom_factor_data(factor):
            continue
        factor_data = dqtrader_rs.get_local_factor(
            factor, strategy.target_list, strategy.begin_date, strategy.end_date)
        env.store_reg_custom_factor(factor, factor_data)


def get_backtest_reg_custom_factor(reg_idx: int, target_list: List[str] = [], length: int = 1) -> DataFrame:
    env = get_env()
    strategy = get_strategy()
    # 如果输入的标的为空，那么默认获取所有的标的
    if len(target_list) == 0:
        target_list = strategy.target_list
    #
    factor_names = env.get_reg_custom_factor_by_idx(reg_idx)
    factor_array = []  # 要增加

    for factor_name in factor_names:
        factor_info = env.get_reg_custom_factor(factor_name)
        if factor_info is None:
            return None
        #
        # 标的
        # 当前推送到的索引
        play_bar_index = env.play_bar_index
        real_kdata_index = factor_info.get_factor_index(play_bar_index)
        start_pos = max(real_kdata_index - length + 1, 0)
        last_arr_size = len(factor_array)
        for target in target_list:
            target_index = strategy.target_index(target)
            for i in range(length):
                factor_array.append([target_index, pd.NaT, "", np.nan])

        for target in target_list:
            target_index = strategy.target_index(target)
            target_factor_data = factor_info.factor_datas[target_index]
            array_index = length - 1
            target_play_index = 0

            for i in range(start_pos, real_kdata_index + 1):
                factor_array[target_index * length + array_index + last_arr_size] = [
                    int(target_index),
                    time_utils.ymd_to_date(int(factor_info.dates[real_kdata_index - target_play_index])),
                    factor_name,
                    target_factor_data[real_kdata_index - target_play_index]
                ]
                array_index -= 1
                target_play_index += 1

    df = pd.DataFrame(factor_array, columns=[
        'target_index', 'date', "factor", "value"])
    return df.round(5)


def get_realtrade_reg_custom_factor(reg_idx: int, target_list: List[str] = [], length: int = 1) -> DataFrame:
    env = get_env()
    strategy = get_strategy()
    # 如果输入的标的为空，那么默认获取所有的标的
    if len(target_list) == 0:
        target_list = strategy.target_list
    #
    factor_names = env.get_reg_custom_factor_by_idx(reg_idx)
    factor_array = []  # 要增加

    array_index = 0
    for factor_name in factor_names:
        factor_info = env.get_reg_custom_factor(factor_name)
        if factor_info is None:
            return None

        for target in target_list:
            target_index = strategy.target_index(target)
            for i in range(length):
                factor_array.append([target_index, pd.NaT, "", np.nan])

        for target in target_list:
            target_index = strategy.target_index(target)
            target_factor_data = factor_info.factor_datas[target_index]
            real_kdata_index = len(target_factor_data)
            start_pos = real_kdata_index - length

            for i in range(start_pos, real_kdata_index):
                factor_array[target_index * length + array_index] = [
                    int(target_index),
                    time_utils.ymd_to_date(int(factor_info.dates[i])),
                    factor_name,
                    target_factor_data[i]
                ]
                array_index += 1

    df = pd.DataFrame(factor_array, columns=[
        'target_index', 'date', "factor", "value"])
    return df.round(5)
