import time
from typing import List
import dqtrader_rs
from dqtrader.decorator import measure_time
from dqtrader.strategy import get_strategy
from dqtrader.common import frequency_to_int
from dqtrader.enums import Frequency
from dqtrader.backtest_environment import get_env
import numpy as np
import dqtrader.tframe.language.chinese.text as text
import pandas as pd

from dqtrader.utils import time_utils


def check_reg_kdata_precondition(frequency_i: int, frequency_num: int):
    """ 检查注册频率与频数，是否允许合法注册
    :param frequency_i: 频率的整数表示形式
    :param frequency_num: 频数
    :exception ValueError, 不支持的频率与频数组合
    """
    strategy = get_strategy()
    strategy_frequency_i = strategy.frequency_int()
    if frequency_i < Frequency.Day <= strategy_frequency_i:
        raise ValueError(text.ERROR_FREQ_NEED_GT_DAY)
    if frequency_i < strategy_frequency_i < Frequency.Day:
        raise ValueError(text.ERROR_FREQ_TOO_HIGH)
    if Frequency.Tick == frequency_i and frequency_num != 1:
        raise ValueError(text.ERROR_NOTSUPPORT_TICK_MULTI_FREQNUM)



def fetch_data(frequency: str, frequency_num: int, adjust=False):
    # 获取数据
    # 获取K线数据
    strategy = get_strategy()
    filled_up_zero = strategy.frequency_int() == Frequency.Day
    kdata_list = dqtrader_rs.get_kdata(
        strategy.target_list,
        frequency,
        frequency_num,
        strategy.begin_date,
        strategy.end_date,
        strategy.fq, True, filled_up_zero)
    # 在这里直接调调整数据
    if not adjust:
        return kdata_list
    # 判断是否有主力合约
    has_combind = False
    for target in strategy.target_list:
        is_combined = dqtrader_rs.is_future_combine(target)
        if is_combined:
            has_combind = True
            break
    if not has_combind:
        return kdata_list
    # 按照顺序
    adjust_kdata_list = []
    # 先判断是否有主力合约
    for i in range(len(strategy.target_list)):
        target = strategy.target_list[i]
        #  不是主力合约，则过滤掉
        if not dqtrader_rs.is_future_combine(target):
            adjust_kdata_list.append(kdata_list[i])
            continue
        # 获取主力合约信息
        combined_infos = dqtrader_rs.get_main_contract(target, strategy.begin_date, strategy.end_date)
        kdatas = kdata_list[i]
        adjust_kdatas = []

        divisor = 1
        dividend = 1
        # 这里的计算逻辑是
        # 切换标的时候
        # divisor 乘以上一个标的最后一个bar 的收盘价
        # 如：divisor *= last_target.close
        # dividend 乘以当前标的第一个bar 的开盘价
        # 如：dividend *= cur_target.open

        # kdatas 的长度和 combined_infos 的长度是一致的才对
        combined_info_index = 0
        cur_combined_info_code = combined_infos[combined_info_index].order_book_id
        # 对应 _regfuncs.py 中 648 行
        for kdata in kdatas:

            #  调整价格
            order_book_id = combined_infos[combined_info_index].order_book_id
            if cur_combined_info_code != order_book_id:
                # 日期更换，则认为是主力合约变换
                divisor *= adjust_kdatas[-1].close
                #
                dividend *= kdata.open
                cur_combined_info_code = order_book_id
            # 计算出调价因子
            kdata.open = divisor * kdata.open / dividend
            kdata.high = divisor * kdata.high / dividend
            kdata.low = divisor * kdata.low / dividend
            kdata.close = divisor * kdata.close / dividend
            adjust_kdatas.append(kdata)
            # 检查是否需要切换

            combined_info_index += 1
            if combined_info_index >= len(combined_infos):
                combined_info_index = len(combined_infos) - 1

        adjust_kdata_list.append(adjust_kdatas)
    return adjust_kdata_list


# 注册K线数据
# adjust 调整价格，主要是用于期货主力合约切换用的
def reg_kdata(frequency: str, frequency_num: int, adjust=False):
    # 转换频率
    frequency_i = frequency_to_int(frequency)
    check_reg_kdata_precondition(frequency_i, frequency_num)
    # 检查是否允许注册频率与频数
    env = get_env()
    # 注册数据，判断是不是新注册，不是新注册注册就跳过了
    is_new_reg = env.reg_kdata(frequency, frequency_i, frequency_num, adjust)
    if not is_new_reg:
        return
    kdata_list = fetch_data(frequency, frequency_num, adjust)
    env.store_reg_kdata(kdata_list)


def get_current_bar(target_list=None):
    if target_list is None:
        target_list = []
    strategy = get_strategy()
    env = get_env()
    if len(target_list) == 0:
        target_list = strategy.target_list
    else:
        target_list = [target.upper() for target in target_list]
    play_bar_index = env.play_bar_index
    kdata_array = []
    for target in target_list:
        target_index = strategy.target_index(target)
        kdata = env.get_driver_kdata(target_index)
        if kdata is None:
            kdata_array.append(
                [target, play_bar_index, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan])
        else:
            kdata_array.append([target, time_utils.ymd_hmss_to_datetime(kdata.datetime), play_bar_index, kdata.open,
                                kdata.high, kdata.low, kdata.close, kdata.volume, kdata.total_turnover,
                                kdata.open_interest])

    df = pd.DataFrame(kdata_array, columns=[
        'code', 'time_bar', "number_bar", "open", "high", "low", "close", "volume", "total_turnover", "open_interest"])

    return df


# 注册驱动的数据线
def reg_driver_kdata(frequency: str, frequency_num: int, adjust=False):
    kdata_list = fetch_data(frequency, frequency_num, adjust)
    env = get_env()
    env.set_driver_kdata(kdata_list)


def get_reg_kdata(reg_idx: int, target_list: List[str] = [], length: int = 1, fill_up: bool = False, df=False):
    strategy = get_strategy()
    env = get_env()
    # 如果输入的标的为空，那么默认获取所有的标的
    if len(target_list) == 0:
        target_list = strategy.target_list
    # 行情的 dict
    kdata_dict = {}
    # 获取 reg_kdata 所注册的索引
    kdata_info = env.get_reg_kdata(reg_idx)
    # 获取注册信息
    reg_info = env.get_reg_kdata_info(reg_idx)
    # 获取注册频率
    strategy_frequency_int = strategy.frequency_int()
    # 当前推送到的索引
    play_bar_index = env.play_bar_index
    # 填充
    # 往前推数据获取索引 + 1 是为了能获取到当前的
    # 遍历标的列表
    for target in target_list:
        # 构建指定长度的数组
        kdata_dict[target] = [None for _ in range(length)]
        # 获取标的的索引
        target_index = strategy.target_index(target)
        # 根据索引获取对应的 K线 数据
        kdatas = kdata_info.kdatas[target_index]
        # 过滤掉数字为空的标的
        if len(kdatas) == 0:
            continue
        if fill_up:
            # 将数组填充进来
            # 注意，这里到时候要测试数据的下标是否正确
            # last_data_index = -1
            # 数据的位置
            # data_pos = 0
            # 将数据填满
            # 先拿当前数据填满
            # 获取真实的索引
            real_kdata_index = kdata_info.get_kdata_index(play_bar_index)
            # 然后从后往前填写
            if real_kdata_index - length < 0:
                end_index = 0
            else:
                end_index = real_kdata_index - length

            data_pos = length - 1
            for i in range(real_kdata_index, end_index - 1, -1):
                kdata_dict[target][data_pos] = kdatas[i]
                data_pos -= 1
                if data_pos < 0:
                    break

            # 获取当前驱动轴的数据，然后更新
            # 频率不相同，那么则拿当前的频率更新
            if reg_info.frequency_i != strategy_frequency_int:
                last_index = kdata_info.get_play_last_index(play_bar_index)
                if last_index == play_bar_index:
                    continue
                start_index = kdata_info.get_play_start_index(play_bar_index)
                # 因为在上面 + 1 了，所以这里要 -1
                # 目标是要最新一根数据
                #  这里要合成数据，合成当开始，到现在的数据
                # 从开始到现在
                # 合成数据
                kdata_dict[target][length - 1] = env.get_merge_driver_kdata(reg_idx, target_index, start_index)
        else:
            has_volume_data_index = []
            last_data_index = -1
            for i in range(play_bar_index, -1, -1):
                cur_kdata_index = kdata_info.get_kdata_index(i)
                if cur_kdata_index == last_data_index:
                    continue
                kdata = kdatas[cur_kdata_index]
                last_data_index = cur_kdata_index
                if kdata.volume == 0:
                    continue
                has_volume_data_index.append(cur_kdata_index)
                # 填满数据，退出
                if len(has_volume_data_index) >= length:
                    break
            # 反转数组，因为是倒叙获取的，要变成正序
            has_volume_data_index.reverse()
            # print(f"--has_volume_data_index = {has_volume_data_index}")
            # 遍历取出数据，填充
            for i in range(0, len(has_volume_data_index)):
                kdata = kdatas[has_volume_data_index[i]]
                kdata_dict[target][i] = kdata
            #
            if reg_info.frequency_i != strategy_frequency_int:
                # 填充驱动轴数据
                driver_kdata = env.get_driver_kdata(target_index)
                if driver_kdata.volume != 0:
                    kdata_dict[target][len(has_volume_data_index) - 1] = driver_kdata

    if not df:
        return kdata_dict
    kdata_array = []
    target_index = 0
    for target in target_list:
        kdatas = kdata_dict[target]
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


def get_tab_strategy_id():
    base_infos = dqtrader_rs.get_tab_strategy_id()

    ids = []

    for base_info in base_infos:
        ids.append({
            "id": base_info.id,
            "name": base_info.name
        })

    return ids


def get_tab_factor_id():
    base_infos = dqtrader_rs.get_tab_factor_id()

    ids = []

    for base_info in base_infos:
        ids.append({
            "id": base_info.id,
            "name": base_info.name
        })

    return ids


def get_performance(task_id: int):
    performace = dqtrader_rs.get_performance(task_id)
    return performace.to_dict()
