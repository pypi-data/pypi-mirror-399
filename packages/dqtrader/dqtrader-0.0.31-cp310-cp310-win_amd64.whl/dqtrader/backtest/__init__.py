from typing import Dict

import dqtrader_rs
import dqtrader.tframe.language.chinese.text as text
from dqtrader.account import get_account, reset_account
from dqtrader.backtest.api import reg_driver_kdata
from dqtrader.backtest.domain import clear_unfilled_order, deal_trade
from dqtrader.backtest_environment import get_env, reset_env
from dqtrader.backtest.order_var import OrderVar
from dqtrader.common import check_begin_end_date, SortedIntSet
from dqtrader.context import Context
from dqtrader.decorator import measure_time
from dqtrader.enums import Frequency
from dqtrader.exception import NotSupportError
from dqtrader.strategy import get_strategy, reset_strategy
from dqtrader.utils import time_utils


def init_config(config):
    # 初始化账号信息
    get_account().init_from_config(config)
    # 初始化策略信息
    get_strategy().init_from_config(config)


# 回测频率检查


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


# 回测日期检查



def _init_data():
    env = get_env()
    strategy = get_strategy()
    env.output_log(
        f"准备K线数据[{strategy.begin_date}--{strategy.end_date}][{strategy.frequency}_{strategy.frequency_num}][{strategy.target_list[0]}~{strategy.target_list[-1]}]...")
    # 获取驱动轴数据
    reg_driver_kdata(strategy.frequency, strategy.frequency_num, False)
    # 获取涨跌停数据
    history_instruments = dqtrader_rs.get_history_instrument(
        strategy.target_list, "day", 1, strategy.begin_date, strategy.end_date)
    env.set_history_instruments(history_instruments)


def init_trading_days():
    trading_day_set = SortedIntSet()
    strategy = get_strategy()
    for target in strategy.target_list:
        words = target.split(".")
        trading_days = dqtrader_rs.get_trading_days(words[0], strategy.begin_date, strategy.end_date)
        trading_day_set.add(trading_days)
    return trading_day_set





def run_backtest(config: Dict, init, on_bar, on_order_status=None, on_order_execution=None)->int:
    reset_account()
    reset_strategy()
    reset_env()
    OrderVar.clear_data()

    init_func = init
    on_bar_func = on_bar
    on_order_status_func = on_order_status
    on_order_execution_func = on_order_execution
    # 全局变量
    _context = Context()
    # 1. 初始化配置信息
    init_config(config)
    #
    trading_day_set = init_trading_days()
    # 回测频率检查
    _check_freq(get_strategy().frequency, get_strategy().frequency_num)
    # 检查开始时间和结束时间
    check_begin_end_date(get_strategy().begin_date, get_strategy().end_date)

    # 初始化标的信息
    env = get_env()
    env.init_target_info()

    if on_order_status_func is not None:
        env.on_order_status = lambda order_inner: on_order_status_func(_context, order_inner)

    if on_order_execution_func is not None:
        env.on_order_execution = lambda order_inner: on_order_execution_func(
            _context, order_inner)
    # 初始化账号信息
    # 检查频率与标的个数是否允许
    # 创建回测任务信息，用于绩效分析
    # 记录回测使开始时间，用于输出回测耗时
    _context.record_start_time()
    account = get_account()
    # 获取策略信息，创建回测任务
    strategy = get_strategy()
    # 重置每日平仓的时间
    account.reset_daily_close_time()

    strategy_id = dqtrader_rs.get_strategy_id(strategy.name)

    task_id = dqtrader_rs.create_strategy_task(
        strategy_id,
        strategy.name,
        strategy.frequency_int(),
        strategy.frequency_num,
        strategy.begin_date_int(),
        strategy.end_date_int()
    )
    # 设置
    dqtrader_rs.set_task_id(task_id)
    env.set_task_id(task_id)
    env.output_log("策略启动...")
    # 2. 初始化数据
    _init_data()
    # env.output_log("数据准备完成，开始回测...")
    # 3. 调用 on_init 函数
    init_func(_context)
    # 4. 循环调用数据
    # 判断频率是不是小于日频
    is_less_min_frequency = strategy.frequency_int() < Frequency.Day
    # 推送数据
    driver_time_line = env.get_driver_time_line()
    data_len = len(driver_time_line)
    # 当前的交易日
    last_trading_date = int(driver_time_line[0] / 1_00_00_00_000)
    last_trading_date = trading_day_set.get_ge(last_trading_date)
    date_index = 0
    # day_begin_time_rb = -1
    # begin_date = int(driver_time_line[0] / 1_00_00_00_000)
    clear_unfilled = True
    env.output_log(f"Test Day {time_utils.ymd_to_str(last_trading_date)}...")
    last_bar_date = last_trading_date
    for play_index in range(data_len):
        # 推送到的数据
        env.play_bar_index = play_index
        # 当前交易时间
        bar_time = driver_time_line[play_index]

        _context.now = time_utils.ymd_hmss_to_datetime(bar_time)
        # 获取当前交易日
        bar_date = int(bar_time / 1_00_00_00_000)
        # 获取时分秒
        hm = bar_time / 1_00_000 - bar_date * 1_00_00
        # 判断两个日期
        if bar_date > last_bar_date:
            trading_bar_date = trading_day_set.get_ge(bar_date)
            if last_trading_date != trading_bar_date:
                # 要判断是不是交易日才行
                date_index += 1
            # 判断该当天是不是 是不是交易日
            env.output_log(f"Test Day {time_utils.ymd_to_str(bar_date)}...")
            last_trading_date = trading_bar_date
            last_bar_date = bar_date
            # 日期更新索引变换
            env.date_index = date_index

        if clear_unfilled:
            # 记录每一个交易日第一根bar的交易时间
            env.day_begin_time_rb = bar_time

        # 要判断是不是当前最后一根，就是判断 是不是 15:00 即可
        if is_less_min_frequency:
            # 判断是不是最后当天的最后一根了
            clear_unfilled = hm == 1500
            # done_daily_close = clear_unfilled
        else:
            clear_unfilled = False
            # done_daily_close = True

        # 第一根不驱动，模拟交易市场，因为第一根不会下单
        if clear_unfilled:
            env.min_freq_turn_pos = True
            # 收盘，删除没有成交的订单, 删除当天创建的订单
            clear_unfilled_order(bar_date)
            # 每一天起始bar的时候先进行结算再处理未完成订单，目前设定中上一天最后一个bar的订单未处理，所以需要接下来调用 deal_trade
            account.on_settlement(True)
            # 处理未完成订单
            deal_trade()
        elif not is_less_min_frequency:
            # 处理未完成订单
            deal_trade()
            # 回测目前支持 min day week month,当频率大于min的时候，每一个周期都需要做今昨转换但不清订单
            account.on_settlement(False)
        else:
            # if play_index ==3208: #3106:
            #     asdasd = 0
            deal_trade()
        # 调用数据
        on_bar_func(_context)

    env.output_log("回测完毕, 正在处理绩效报告, 请稍等...")
    env.output_log(f"回测总耗时 {_context.execute_time()} 秒")

    # 处理完成后，将交割单，发送给绩效分析引擎
    #
    py_account = dqtrader_rs.PyAccountInfo()
    py_account.valid_cash = account.initial_cash
    py_account.init_cash = account.initial_cash
    py_account.frequency = strategy.frequency_int()
    py_account.fq = strategy.fq
    py_account.fre_num = strategy.frequency_num
    py_account.benchmark = strategy.benchmark
    py_account.begin_date = strategy.begin_date
    py_account.order_mode = 1  # 交易模式
    py_account.end_date = strategy.end_date

    py_account.cost_fee_stock = env.stock_cost_fee / 1e4
    py_account.cost_fee_future = env.future_cost_fee
    py_account.slide_price = account.slide_price
    py_account.rate = account.risk_free_rate
    py_account.margin_multiply = account.margin_rate

    py_account.margin = account.get_long_margin(0, 1.0)
    py_account.multiple = env.get_multiple(0)

    py_trade_list = []

    for trade in OrderVar.trade_list:
        order = OrderVar.order_dict.get(trade.order_id, None)
        if order is None:
            continue
        target_info = env.get_target_info(order.target_index)
        py_trade = dqtrader_rs.PyOrder()
        py_trade.atm_order_id = trade.trade_id
        py_trade.client_order_id = trade.trade_id
        words = order.code.split(".")
        py_trade.market = words[0]
        py_trade.name = target_info.name
        py_trade.code = words[1]

        py_trade.order_act = trade.side
        py_trade.order_ctg = trade.ctg
        py_trade.offset_flag = trade.position_effect
        py_trade.create_time = time_utils.ymd_hmss_to_str(order.created_time)
        py_trade.filled_time = time_utils.ymd_hmss_to_str(trade.created)
        py_trade.price = trade.price
        py_trade.volume = int(trade.volume)
        py_trade.order_status = 1  # 全部成交
        py_trade_list.append(py_trade)
    #

    py_order_list = []
    for order in OrderVar.order_list:
        py_order = dqtrader_rs.PyOrder()
        target_info = env.get_target_info(order.target_index)
        py_order.atm_order_id = order.order_id
        py_order.client_order_id = order.order_id
        words = order.code.split(".")
        py_order.market = words[0]
        py_order.code = words[1]
        py_order.name = target_info.name
        py_order.order_act = order.side
        py_order.order_ctg = order.ctg
        py_order.offset_flag = order.position_effect
        py_order.create_time = time_utils.ymd_hmss_to_str(order.created_time)
        py_order.filled_time = time_utils.ymd_hmss_to_str(order.updated_time)
        py_order.price = order.price
        py_order.filled_price = order.filled_average
        py_order.volume_traded = int(order.filled_volume)
        py_order.volume = int(order.volume)
        py_order.order_status = order.status  # 全部成交
        py_order_list.append(py_order)
    py_updown_list = []
    for target_index in range(len(strategy.target_list)):
        target_info = env.get_target_info(target_index)
        kdatas = env.get_driver_kdatas(target_index)
        py_updown = dqtrader_rs.PyTargetUpdownInfo()
        py_updown.market = target_info.market
        py_updown.code = target_info.code
        py_updown.name = target_info.name

        if kdatas[0].open != 0:
            py_updown.updown = (kdatas[-1].close - kdatas[0].open) / kdatas[0].open

        py_updown.last_price = kdatas[-1].close
        py_updown_list.append(py_updown)

    # print(f"order size = {len(OrderVar.order_list)} trade size = {len(OrderVar.trade_list)}")
    dqtrader_rs.analysis_order(
        task_id, py_account, py_order_list, py_trade_list, py_updown_list, [])

    return task_id