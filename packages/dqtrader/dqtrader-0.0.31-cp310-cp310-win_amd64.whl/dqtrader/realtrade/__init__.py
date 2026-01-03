import datetime
import time
from typing import Dict

import dqtrader_rs

from dqtrader import log
from dqtrader.common import check_begin_end_date
from dqtrader.context import Context
from dqtrader.enums import Frequency
from dqtrader.exception import NotSupportError
from dqtrader.real_environment import get_env, KDataInfo
from dqtrader.realtrade import real_account
from dqtrader.realtrade.api import _reg_driver_kdata
from dqtrader.realtrade.real_account import get_all_account_subscribe_tag
from dqtrader.strategy import get_strategy
from dqtrader.tframe.language.chinese import text
from dqtrader.utils import time_utils


# 初始化配置
def init_config(config):
    # 获取所有账号信息
    account_names = config["accounts"]
    if account_names is None:
        raise Exception("请设置账号: accounts")
    if len(account_names) == 0:
        raise Exception("请设置账号: accounts")
    # 初始化账号
    real_account.init_accounts(account_names)
    # 初始化策略信息
    config["strategy"]["end_date"] = time_utils.cur_date_str()
    get_strategy().init_from_config(config)


def _check_freq(frequency, frequency_num):
    """假设输入参数值都是对的, 检查支持情况,
    :return: 如果不支持的频率, raise NotSupportError
    """
    frequency = str.lower(frequency)
    if frequency == "tick" and frequency_num != 1:
        raise NotSupportError(text.ERROR_NOTSUPPORT_TICK_MULTI_FREQNUM)
    if frequency in ['sec']:
        raise NotSupportError(
            text.ERROR_NOTSUPPORT_FREQ.format(KFreq=frequency))



def _init_data():
    env = get_env()
    strategy = get_strategy()
    env.output_log(
        f"准备K线数据[{strategy.begin_date}--{strategy.end_date}][{strategy.frequency}_{strategy.frequency_num}][{strategy.target_list[0]}~{strategy.target_list[-1]}]...")
    _reg_driver_kdata(strategy.frequency, strategy.frequency_num, False)


# 注册数据
def _handle_data(push_target: str, min_data, kdata_info: KDataInfo):
    strategy = get_strategy()
    # 获取当前数据所在的时间点
    trading_point = kdata_info.find_real_trading_datetime(min_data.datetime)
    # 遍历当前标的
    # move_index = False
    for index, target_2 in enumerate(strategy.target_list):
        # 如何确保订阅的数据，全部处理完成
        # 获取数据
        target_2 = target_2.lower()
        kdatas = kdata_info.kdatas[index]
        # 判断推过来的数据，是不是当前目标数据
        if push_target == target_2:
            if len(kdatas) != 0:
                # 当前数据不为空
                # 当前时间线小等于，全部合成，说明是在当前的 bar 中
                if kdatas[-1].datetime >= trading_point:  # 合并
                    last_kdata = kdatas[-1]
                    # 上一跟是对其的时候，需要去判断
                    if last_kdata.open == 0:
                        last_kdata.open = min_data.open
                        last_kdata.high = min_data.high
                        last_kdata.low = min_data.low
                        last_kdata.volume = min_data.volume
                        last_kdata.total_turnover = min_data.total_turnover
                    else:
                        last_kdata.high = max(min_data.high, last_kdata.high)
                        last_kdata.low = min(min_data.low, last_kdata.low)
                        last_kdata.volume += min_data.volume
                        last_kdata.total_turnover += min_data.total_turnover
                    last_kdata.close = min_data.close
                    last_kdata.datetime = min_data.datetime  # 更新当前时间
                    last_kdata.open_interest = min_data.open_interest
                    # last_kdata.settlement = min_data.settlement
                # 当前 bar 的时间，大于最后一根时间，说明是新的时间点
                elif kdatas[-1].datetime < trading_point:
                    # 上一跟，需要时间对其
                    trading_point = kdata_info.find_real_trading_datetime(kdatas[-1].datetime)
                    #
                    kdatas[-1].datetime = trading_point
                    # 新增数据
                    kdatas.append(min_data)
                    # move_index = True
            else:
                kdatas.append(min_data)


def on_min_data():
    env = get_env()
    min_datas = dqtrader_rs.get_mink_data()
    if len(min_datas) == 0:
        return
    for min_data in min_datas:
        # print(f"===on_min_data===:{min_data.datetime}")
        # 分钟线数据
        push_target = f"{min_data.market}.{min_data.code}"
        # 记录当前驱动的时间
        driver_kdata_info = env.get_driver_kdata_info()
        _handle_data(push_target, min_data, driver_kdata_info)
        # 分钟线数据
        reg_index_arr = env.get_min_reg_index()
        # 要判断当前的 驱动数据，所有还是要合成驱动数据的
        for reg_index in reg_index_arr:
            kdata_info = env.get_reg_kdata(reg_index)
            _handle_data(push_target, min_data, kdata_info)


def on_day_data():
    strategy = get_strategy()
    env = get_env()
    day_datas = dqtrader_rs.get_dayk_data()
    if len(day_datas) == 0:
        return
    # print(f"===on_day_data===")
    # 判断驱动是不是日线
    for day_data in day_datas:
        push_target = f"{day_data.market}.{day_data.code}"
        if strategy.frequency_int() == Frequency.Day:
            driver_kdata_info = env.get_driver_kdata()
            _handle_data(push_target, day_data, driver_kdata_info)
        # 获取日线频率
        reg_index_arr = env.get_day_reg_index()
        # 要判断当前的 驱动数据，所有还是要合成驱动数据的
        for reg_index in reg_index_arr:
            kdata_info = env.get_reg_kdata(reg_index)
            _handle_data(push_target, day_data, kdata_info)


def on_order_change(on_order_status_func):
    order_infos = dqtrader_rs.get_order_change_list()
    #
    # print("===on_order_change===")
    # 更新持仓
    for order_info in order_infos:
        account = real_account.get_account_by_id(order_info.account_id)
        if account is None:
            return
        # 更新持仓
        account.update_position()
        order = account.update_order(order_info.client_id)
        if order is None or on_order_status_func is None:
            return
        on_order_status_func(order)


def on_equity_change():
    equity_infos = dqtrader_rs.get_equity_list()
    for equity_info in equity_infos:
        account = real_account.get_account_by_id(equity_info.id)
        if account is None:
            return
        account.update_equity(equity_info)


def on_update_time_line():
    # print("===on_update_time_line===")
    strategy = get_strategy()
    env = get_env()
    # _frequency_int = strategy.frequency_int()
    # 获取交易时间轴
    trading_scope = dqtrader_rs.get_trading_time(
        strategy.target_list,
        strategy.frequency,
        strategy.frequency_num,
        "", "")
    _drive_kdata_info = env.get_driver_kdata_info()
    _drive_kdata_info.update_time_scope(trading_scope)
    # 更新所有注册数据交易日
    _reg_keys = env.get_all_reg_keys()
    for _reg_key in _reg_keys:
        #
        trading_scope = dqtrader_rs.get_trading_time(
            strategy.target_list,
            _reg_key.frequency,
            _reg_key.frequency_num,
            "", "")
        reg_index = env.get_reg_index(_reg_key)
        reg_kdata_info = env.get_reg_kdata(reg_index)
        reg_kdata_info.update_time_scope(trading_scope)


def run_realtrade(config: Dict, init, on_bar, on_order_status=None):

    log.init()
    init_func = init
    on_bar_func = on_bar
    on_order_status_func = on_order_status
    # 全局变量
    _context = Context()

    # 1. 初始化配置信息
    init_config(config)
    # 回测频率检查
    _check_freq(get_strategy().frequency, get_strategy().frequency_num)
    # 检查开始时间和结束时间
    check_begin_end_date(get_strategy().begin_date, get_strategy().end_date)
    # 初始化标的信息
    env = get_env()
    env.init_target_info()
    # 初始化账号信息
    # 检查频率与标的个数是否允许
    # 创建回测任务信息，用于绩效分析
    # 记录回测使开始时间，用于输出回测耗时
    _context.record_start_time()
    # 获取策略信息，创建回测任务
    strategy = get_strategy()
    #
    strategy_id = dqtrader_rs.get_strategy_id(strategy.name)
    account_ids = real_account.get_all_account_id()

    task_id = dqtrader_rs.create_realtrade_task(
        strategy_id,
        strategy.name,
        strategy.frequency_int(),
        strategy.frequency_num,
        strategy.begin_date_int(),
        strategy.target_list,
        account_ids
    )
    dqtrader_rs.set_task_id(task_id)
    env.set_task_id(task_id)
    env.output_log("策略模拟实盘启动...")
    # 2. 初始化数据
    _init_data()

    # 3. 调用 on_init 函数
    init_func(_context)

    # 这里要订阅id
    subscribe_tags = get_all_account_subscribe_tag()
    for subscribe_tag in subscribe_tags:
        dqtrader_rs.subscribe_topic("OneAccountEquityChange", subscribe_tag)
        dqtrader_rs.subscribe_topic("OneOrderStatusChange", subscribe_tag)

    # 订阅更新时间轴的数据
    dqtrader_rs.subscribe_topic("NoticeUpdateTimeLine", "")

    for target in strategy.target_list:
        lower_target = target.lower()
        dqtrader_rs.subscribe_topic("RtMinData", lower_target)
        dqtrader_rs.subscribe_topic("RtDayData", lower_target)

    try:

        driver_kdata_info = env.get_driver_kdata_info()
        play_bar_index = len(driver_kdata_info.kdatas[0])
        env.play_bar_index = play_bar_index
        cur_time = time_utils.cur_ymd_hmss()
        last_time_point = driver_kdata_info.find_real_trading_datetime(cur_time)

        while True:
            # 沉睡 0.5 s
            time.sleep(0.5)  # 沉睡 0.5 s
            signal = dqtrader_rs.get_signal()
            _context.now = datetime.datetime.now()
            if signal == 1:
                # 分钟
                on_min_data()
            elif signal == 2:
                # 更新时间轴
                on_update_time_line()
            elif signal == 3:
                # 日线
                on_day_data()
            elif signal == 4:
                on_order_change(on_order_status_func)
            elif signal == 5:
                on_equity_change()

            cur_time = time_utils.cur_ymd_hmss()
            cur_time_point = driver_kdata_info.find_real_trading_datetime(cur_time)
            if last_time_point == cur_time_point:
                continue
            on_bar_func(_context)
            env.play_bar_index = play_bar_index
            last_time_point = cur_time_point
            play_bar_index += 1
    except KeyboardInterrupt:
        print("程序终止")
