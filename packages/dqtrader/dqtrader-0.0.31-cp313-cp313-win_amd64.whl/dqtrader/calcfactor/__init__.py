from typing import Dict

import dqtrader_rs

from dqtrader import enums
from dqtrader.account import get_account, reset_account
from dqtrader.backtest.api import reg_driver_kdata
from dqtrader.common import check_begin_end_date
from dqtrader.backtest_environment import get_env, reset_env
from dqtrader.context import Context
from dqtrader.strategy import get_strategy, reset_strategy
from dqtrader.utils import time_utils


def init_config(config):
    # 初始化账号信息
    get_account().init_from_config(config)
    # 初始化策略信息
    if "strategy" in config:
        # 默认为日线
        config["strategy"]["frequency"] = "day"
        config["strategy"]["frequency_num"] = 1

        if "fq" not in config["strategy"]:
            config["strategy"]["fq"] = enums.FQType.FORWARD

        get_strategy().init_from_config(config)


def _init_data():
    # 获取驱动轴数据
    strategy = get_strategy()
    reg_driver_kdata(strategy.frequency, strategy.frequency_num, False)
    # 获取涨跌停数据
    history_instruments = dqtrader_rs.get_history_instrument(
        strategy.target_list, "day", 1, strategy.begin_date, strategy.end_date)
    env = get_env()
    env.set_history_instruments(history_instruments)


def run_factor(config: Dict, init, calc_factor) -> int:
    reset_account()
    reset_strategy()
    reset_env()
    #
    init_func = init
    calc_factor_func = calc_factor

    # 全局变量
    _context = Context()
    # 1. 初始化配置信息
    init_config(config)
    # 2. 检查开始时间和结束时间
    check_begin_end_date(get_strategy().begin_date, get_strategy().end_date)
    # 初始化标的信息
    env = get_env()
    env.init_target_info()
    account = get_account()
    strategy = get_strategy()
    # 初始化账号信息
    # 检查频率与标的个数是否允许
    # 创建回测任务信息，用于绩效分析

    # 记录回测使开始时间，用于输出回测耗时
    _context.record_start_time()
    # 重置每日平仓的时间
    account.reset_daily_close_time()
    factor_id = dqtrader_rs.get_factor_id(strategy.name)

    task_id = dqtrader_rs.create_factor_task(factor_id, strategy.name)
    dqtrader_rs.set_task_id(task_id)
    env.set_task_id(task_id)
    # 2. 初始化数据
    _init_data()

    init_func(_context)

    # 推送数据
    driver_time_line = env.get_driver_time_line()
    data_len = len(driver_time_line)

    # 保存计算结果
    calc_factor_array = []
    date_array = []
    # 推送数据
    last_bar_date = int(driver_time_line[0] / 1_00_00_00_000)
    env.output_log(f"Test Day {time_utils.ymd_to_str(last_bar_date)}...")
    for play_index in range(data_len):
        env.play_bar_index = play_index
        # 当前交易时间
        bar_time = driver_time_line[play_index]
        _context.now = time_utils.ymd_hmss_to_datetime(bar_time)
        bar_date = int(bar_time / 1_00_00_00_000)
        if bar_date != last_bar_date:
            last_bar_date = bar_date
            env.output_log(f"Test Day {time_utils.ymd_to_str(bar_date)}...")

        # 获取当前交易日
        env.date_index = play_index
        # 处理返回值
        result = calc_factor_func(_context)
        calc_factor_array.append(result)
        date_array.append(bar_date)

    env.output_log("回测完毕, 正在处理绩效报告, 请稍等...")
    env.output_log(f"回测总耗时 {_context.execute_time()} 秒")

    py_params = dqtrader_rs.PyFactorTaskParams()
    py_benchmark_market_code = dqtrader_rs.PyMarketCode()
    words = strategy.benchmark.split(".")
    py_benchmark_market_code.market = words[0]
    py_benchmark_market_code.code = words[1]
    py_params.benchmark = py_benchmark_market_code
    py_params.team_num = 5
    py_params.begin_date = strategy.begin_date_int()
    py_params.end_date = strategy.end_date_int()
    py_params.holding_adjust_fre = 1  # day
    py_params.factor_direct = 1
    py_params.attenuation_cycle = 5
    py_params.portfolio_way = 1
    py_params.industry_class = "申万1级"
    py_params.signal_list = []

    py_factor_value_list = []
    target_list = get_strategy().target_list
    for target_index, target in enumerate(target_list):
        py_market_code = dqtrader_rs.PyMarketCode()
        words = target.split(".")
        py_market_code.market = words[0]
        py_market_code.code = words[1]
        py_factor_value = dqtrader_rs.PyFactorValue()
        py_factor_value.market_code = py_market_code
        values = []
        for calc_factor in calc_factor_array:
            factor_value = calc_factor[target_index]
            values.append(factor_value)
        py_factor_value.values = values
        py_factor_value_list.append(py_factor_value)
    # 因子存在时，保存
    if factor_id != 0:
        dqtrader_rs.save_custom_value(factor_id, date_array, py_factor_value_list)
    # 增加一个接口，存储因子值得
    dqtrader_rs.analysis_factor(
        task_id, py_params, date_array, py_factor_value_list)

    return task_id
