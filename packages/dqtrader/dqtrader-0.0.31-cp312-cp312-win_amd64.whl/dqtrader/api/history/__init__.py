from typing import List
import dqtrader_rs
import numpy as np

from dqtrader.decorator import measure_time
import dqtrader.enums as enums
import dqtrader.utils.time_utils as time_utils
import pandas as pd

__all__ = [
    'get_stock_info',
    'get_future_info',
    'get_target_info',
    'get_margin_and_commission',
    'get_kdata',
    "get_future_contracts",
    'get_history_instruments',
    'get_tick_data',
    'get_code_list',
    'get_trading_days',
    'get_trading_time',
    'get_main_contract',
    'get_factor_by_factor',
    'get_factor_by_day',
    'get_factor_by_code',
    'get_custom_factor_by_factor',
    'get_custom_factor_by_day',
    'get_custom_factor_by_code'
]


# 获取股票信息
def get_stock_info(target_list: List[str]):
    stock_infos = dqtrader_rs.get_stock_info(target_list)
    stock_info_array = []

    for stock_info in stock_infos:
        stock_info_array.append([stock_info.code, stock_info.market, stock_info.name,
                                 stock_info.abbrev_name, stock_info.round_lot, stock_info.listed_date,
                                 stock_info.de_listed_date,
                                 stock_info.type])

    df = pd.DataFrame(stock_info_array, columns=[
        'code', "market", 'name', "abbrev_name", "round_lot", "listed_date", "de_listed_date", "type"])

    return df


# 获取期货信息
def get_future_info(target_list: List[str]):
    future_infos = dqtrader_rs.get_future_info(target_list)
    future_info_array = []

    for future_info in future_infos:
        future_info_array.append([future_info.code, future_info.market, future_info.name, future_info.margin_rate,
                                  future_info.round_lot, future_info.listed_date, future_info.de_listed_date,
                                  future_info.type,
                                  future_info.multiplier, future_info.underlying_target, future_info.settlement,
                                  future_info.product, future_info.min_move, future_info.commission,
                                  future_info.commission_unit])

    df = pd.DataFrame(future_info_array, columns=[
        'code', "market", 'name', "ex_margin_rate", "round_lot", "listed_date", "de_listed_date", "type", "multiplier",
        "underlying_target",
        "settlement",
        "product", "min_move", "commission", "commission_unit"])

    return df


def get_future_contracts(date: str, market: str, varieties: str):
    contracts = dqtrader_rs.get_future_contracts(date, market, varieties)
    contracts_array = []
    for contract in contracts:
        contracts_array.append([f"{contract.market}.{contract.code}", contract.name])
    df = pd.DataFrame(contracts_array, columns=["code", "name"])

    df_sorted = df.sort_values(by='code')
    return df_sorted


# 获取目标信息
def get_target_info(target_list: List[str]):
    return dqtrader_rs.get_target_info(target_list)


def get_margin_and_commission(target_list: List[str]):
    margin_and_commission_datas = dqtrader_rs.get_margin_and_commission(target_list)
    margin_and_commission_array = []
    for ele in margin_and_commission_datas:
        margin_and_commission_array.append([f"{ele.market}.{ele.code}",
                                            ele.margin_rate.long_ratio_by_money,
                                            ele.margin_rate.long_ratio_by_volume,
                                            ele.margin_rate.short_ratio_by_money,
                                            ele.margin_rate.short_ratio_by_volume,
                                            ele.commission_rate.open_ratio_by_money,
                                            ele.commission_rate.open_ratio_by_volume,
                                            ele.commission_rate.close_ratio_by_money,
                                            ele.commission_rate.close_ratio_by_volume,
                                            ele.commission_rate.close_today_ratio_by_money,
                                            ele.commission_rate.close_today_ratio_by_volume])
    df = pd.DataFrame(margin_and_commission_array, columns=[
        'code', "margin_long_ratio_by_money", "margin_long_ratio_by_volume", "margin_short_ratio_by_money",
        "margin_short_ratio_by_volume",
        "commission_open_ratio_by_money", "commission_open_ratio_by_volume", "commission_close_ratio_by_money",
        "commission_close_ratio_by_volume", "commission_close_today_ratio_by_money",
        "commission_close_today_ratio_by_volume"])
    return df


# 获取K线数据
# @measure_time
# def get_kdata(
#         target_list: List[str],  # 标的列表
#         frequency: str,  # 频率
#         fre_num: int,
#         begin_date: str,
#         end_date: str,
#         fq: int = enums.FQType.NA,
#         fill_up: bool = False
# ):
#     kdatas = dqtrader_rs.get_kdata(target_list, frequency, fre_num, begin_date, end_date, fq, fill_up, False)
#     kdata_array = []
#     for target_index, kdatas in enumerate(kdatas):
#         target = target_list[target_index]
#         for kdata in kdatas:
#             kdata_array.append(
#                 [time_utils.ymd_hmss_to_datetime(kdata.datetime), target, kdata.open, kdata.high, kdata.low,
#                  kdata.close, kdata.volume,
#                  kdata.total_turnover, kdata.open_interest])
#
#     df = pd.DataFrame(kdata_array, columns=[
#         'datetime', 'code', "open", "high", "low", "close", "volume", "total_turnover", "open_interest"])
#
#     return df
@measure_time
def get_kdata(
        target_list: List[str],  # 标的列表
        frequency: str,  # 频率
        fre_num: int,
        begin_date: str,
        end_date: str,
        fq: int = enums.FQType.NA,
        fill_up: bool = False
):
    kdatas = dqtrader_rs.get_kdata(target_list, frequency, fre_num, begin_date, end_date, fq, fill_up, False)
    columns = ['datetime', 'code', "open", "high", "low", "close", "volume", "total_turnover", "open_interest"]
    kdata_array = [
        [
            time_utils.ymd_hmss_to_datetime(kdata.datetime),
            target,
            kdata.open,
            kdata.high,
            kdata.low,
            kdata.close,
            kdata.volume,
            kdata.total_turnover,
            kdata.open_interest
        ]
        for target, target_kdatas in zip(target_list, kdatas)
        for kdata in target_kdatas
    ]

    return pd.DataFrame(kdata_array, columns=columns)


def get_history_instruments(
        target_list: List[str],  # 标的列表
        begin_date: str,
        end_date: str,
        df: bool = False
):
    history_instruments = dqtrader_rs.get_history_instrument(target_list, "DAY", 1, begin_date, end_date)

    # 定义 columns，避免重复创建
    columns = ['trade_date', 'code', 'settle_price', "open_interest", "prev_close", "prev_settle",
               "delisted", "st", "suspended", "up_limit_price", "down_limit_price"]

    if not df:
        return history_instruments

    # 使用列表推导式构造 data_array
    data_array = [
        [
            time_utils.ymd_hmss_to_datetime(data.datetime).date(),
            target,
            data.settlement,
            data.open_interest,
            data.prev_close,
            data.prev_settlement,
            data.is_delisted,
            data.is_st,
            data.is_suspended,
            data.up_limit_price,
            data.down_limit_price
        ]
        for target, history_instrument in zip(target_list, history_instruments)
        for data in history_instrument
    ]

    return pd.DataFrame(data_array, columns=columns)


# 获取 tick 先数据
def get_tick_data(target: str, date: str, fq: int = enums.FQType.NA):
    tick_datas = dqtrader_rs.get_tick(target, date, 0, fq)

    tick_data_array = []

    for tick_data in tick_datas:
        tick_data_array.append([time_utils.ymd_hmss_to_datetime(tick_data.datetime),
                                tick_data.volume,
                                tick_data.bid,
                                tick_data.bid_vol,
                                tick_data.ask,
                                tick_data.ask_vol,
                                tick_data.open_interest,
                                tick_data.last,
                                tick_data.total_turnover
                                ])

    df = pd.DataFrame(tick_data_array, columns=[
        'datetime', 'volume', "bid_price", "bid_volume", "ask_price", "ask_volume", "open_interest", "price",
        "total_turnover"])

    return df


# 获取代码表
def get_code_list(block: str, date: str = None):
    # //
    if date is None:
        date = time_utils.cur_date_str()

    code_array = [
        [
            f"{ci.market}.{ci.code}" if ci.market else ci.code,
            ci.name,
            ci.block_name,
            ci.weight,
            time_utils.ymd_to_date(ci.date),
        ]
        for ci in dqtrader_rs.get_code_list(block, date)
    ]

    return pd.DataFrame(code_array, columns=["code", "name", "block_name", "weight", "date"])


# 获取交易日历
def get_trading_days(market: str, begin_date: str, end_date: str):
    trading_days = dqtrader_rs.get_trading_days(market, begin_date, end_date)
    trading_day_arr = []
    for trading_day in trading_days:
        trading_day_arr.append(time_utils.ymd_to_date(trading_day))
    return np.array(trading_day_arr)


# 获取交易时间段
def get_trading_time(
        target_list: List[str],
        frequency: str,  # 频率
        fre_num: int,
        begin_date: str,
        end_date: str):
    trading_times = dqtrader_rs.get_trading_time(target_list, frequency, fre_num, begin_date, end_date)

    trading_time_array = []

    for trading_time in trading_times:
        trading_time_array.append([time_utils.ymd_hmss_to_datetime(trading_time.datetime), trading_time.num])

    df = pd.DataFrame(trading_time_array, columns=['time', 'nums'])

    return df


# 获取主力合约
def get_main_contract(target: str, begin_date: str, end_date: str):
    main_contract_array = []
    main_contracts = dqtrader_rs.get_main_contract(target, begin_date, end_date)

    for main_contract in main_contracts:
        main_contract_array.append([main_contract.order_book_id.upper(), time_utils.ymd_to_date(main_contract.date)])
    df = pd.DataFrame(main_contract_array, columns=["code", "date"])
    return df


# 获取因子数据

# def get_factor_by_factor(
#         factor: str,
#         target_list: List[str],
#         begin_date: str,
#         end_date: str):
#     factor_datas = dqtrader_rs.get_factor(
#         factor, target_list, begin_date, end_date)
#     factor_array = []
#     for (index, date) in enumerate(factor_datas.dates):
#         date_factor_array = [time_utils.ymd_to_date(date)]
#         for i in range(len(target_list)):
#             date_factor_array.append(factor_datas.values[i][index])
#         factor_array.append(date_factor_array)
#     df = pd.DataFrame(factor_array, columns=['date'] + target_list).round(5)
#     return df

def get_factor_by_factor(
        factor: str,
        target_list: List[str],
        begin_date: str,
        end_date: str):
    # 获取因子数据
    factor_datas = dqtrader_rs.get_factor(factor, target_list, begin_date, end_date)
    # 使用zip优化数据组合
    factor_array = [
        [time_utils.ymd_to_date(date)] + list(values)
        for date, values in zip(factor_datas.dates, zip(*factor_datas.values))
    ]

    # 创建DataFrame并设置列名
    df = pd.DataFrame(factor_array, columns=['date'] + target_list).round(5)
    return df


def get_factor_by_day(
        factor_list: List[str],
        target_list: List[str],
        date: str):
    factor_array = []
    for target in target_list:
        factor_array.append([target])

    for factor in factor_list:
        factor_value = dqtrader_rs.get_factor(factor, target_list, date, date)
        for (index, values) in enumerate(factor_value.values):
            if len(values) == 0:
                factor_array[index].append(np.nan)
            else:
                factor_array[index].append(values[0])
    df = pd.DataFrame(factor_array, columns=['code'] + factor_list).round(5)
    return df


# 通过代码获取
# def get_factor_by_code(
#         factor_list: List[str],
#         target: str,
#         begin_date: str,
#         end_date: str):
#     factor_array = []
#     target_list = [target]
#     factor_value_array = []
#     for factor in factor_list:
#         factor_value = dqtrader_rs.get_factor(factor, target_list, begin_date, end_date)
#         factor_value_array.append()
#
#
#     for (index, date) in enumerate(factor_value.dates):
#
#             factor_array.append([time_utils.ymd_to_date(date), factor_value.values[0][index]])
#
#     df = pd.DataFrame(factor_array, columns=['date'] + factor_list).round(5)
#     return df

def get_factor_by_code(
        factor_list: List[str],
        target: str,
        begin_date: str,
        end_date: str):
    factor_array = []
    target_list = [target]
    factor_value_array = []
    for factor in factor_list:
        factor_value = dqtrader_rs.get_factor(factor, target_list, begin_date, end_date)
        factor_value_array.append(factor_value)

    first_factor_value = factor_value_array[0]
    factor_len = len(first_factor_value.dates)
    for i in range(0, factor_len):
        data_arr = [time_utils.ymd_to_date(first_factor_value.dates[i])]
        for j in range(0, len(factor_list)):
            factor_value = factor_value_array[j]
            data_arr.append(factor_value.values[0][i])

        factor_array.append(data_arr)

    df = pd.DataFrame(factor_array, columns=['date'] + factor_list).round(5)
    return df


# 获取因子数据

def get_custom_factor_by_factor(
        factor: str,
        target_list: List[str],
        begin_date: str,
        end_date: str):
    factor_datas = dqtrader_rs.get_local_factor(
        factor, target_list, begin_date, end_date)

    factor_array = [
        [time_utils.ymd_to_date(date)] + list(values)
        for date, values in zip(factor_datas.dates, zip(*factor_datas.values))
    ]

    # 创建DataFrame并设置列名
    df = pd.DataFrame(factor_array, columns=['date'] + target_list).round(5)
    return df


def get_custom_factor_by_day(
        factor_list: List[str],
        target_list: List[str],
        date: str):
    factor_array = []
    for target in target_list:
        factor_array.append([target])
    for factor in factor_list:
        factor_value = dqtrader_rs.get_local_factor(factor, target_list, date, date)
        for (index, values) in enumerate(factor_value.values):
            factor_array[index].append(values[0])
    df = pd.DataFrame(factor_array, columns=['code'] + factor_list).round(5)
    return df


# 通过代码获取
def get_custom_factor_by_code(
        factor_list: List[str],
        target: str,
        begin_date: str,
        end_date: str):
    factor_array = []
    target_list = [target]
    for factor in factor_list:
        factor_value = dqtrader_rs.get_local_factor(factor, target_list, begin_date, end_date)
        for (index, date) in enumerate(factor_value.dates):
            factor_array.append([time_utils.ymd_to_date(date), factor_value.values[0][index]])
    df = pd.DataFrame(factor_array, columns=['date'] + factor_list).round(5)
    return df
