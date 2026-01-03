# 全局环境
from math import isnan
from typing import Callable, Dict, List, Optional
import sys
import dqtrader_rs
import numpy as np

from dqtrader.entity import DQTBackTrade, SnapOrder
from dqtrader.enums import Frequency, TargetType
from dqtrader.strategy import get_strategy
from dqtrader.utils import time_utils


class KDataInfo:
    # 对应当前 play_bar_index 下，要推送的 K线数据
    left_bar_pos: List[int]
    # 是去掉线丢应下划线的
    right_bar_pos: List[int]
    # 存储所有的 K线数据
    kdatas: List[List[dqtrader_rs.PyMinOrDayData]]

    # 合成缓存的
    last_start_indexs: List[int]
    last_merge_indexs: List[int]
    last_merge_kdatas: List[dqtrader_rs.PyMinOrDayData | None]

    def __init__(self, left_bar_pos: List[int], right_bar_pos: List[int],
                 kdatas: List[List[dqtrader_rs.PyMinOrDayData]]) -> None:
        #
        self.left_bar_pos = left_bar_pos
        self.right_bar_pos = right_bar_pos
        self.kdatas = kdatas
        #
        self.last_start_indexs = []
        self.last_merge_kdatas = []
        self.last_merge_indexs = []
        for i in range(0, len(self.kdatas)):
            self.last_start_indexs.append(-1)
            self.last_merge_indexs.append(-1)
            self.last_merge_kdatas.append(None)

    def set_last_kdata(self, target_index: int, last_start_index: int, last_merge_index: int,
                       last_kdata: dqtrader_rs.PyMinOrDayData):
        self.last_start_indexs[target_index] = last_start_index
        self.last_merge_kdatas[target_index] = last_kdata
        self.last_merge_indexs[target_index] = last_merge_index

    def get_last_kdata(self, target_index: int, last_start_index: int):
        if self.last_start_indexs[target_index] != last_start_index:
            return None
        return self.last_merge_kdatas[target_index]

    def get_last_merge_index(self, target_index: int, last_start_index: int):
        if self.last_merge_indexs[target_index] != last_start_index:
            return last_start_index
        return self.last_merge_indexs[target_index]

    def get_kdata_index(self, play_index: int) -> int:
        return self.left_bar_pos[play_index]

    def get_kdata(self, target_index: int, data_index: int) -> dqtrader_rs.PyMinOrDayData:
        # 返回数据
        return self.kdatas[target_index][data_index]

    def get_play_start_index(self, play_index: int) -> int:
        kdata_index = self.get_kdata_index(play_index)
        if kdata_index == 0:
            return 0
        return self.right_bar_pos[kdata_index - 1] + 1

    def get_play_last_index(self, play_index: int) -> int:
        kdata_index = self.get_kdata_index(play_index)
        return self.right_bar_pos[kdata_index]


class RegKdataInfo:
    frequency: str
    frequency_i: int
    frequency_num: int
    adjust: bool

    def __init__(self, frequency: str, frequency_i: int, frequency_num: int, adjust: bool) -> None:
        self.frequency = frequency
        self.frequency_i = frequency_i
        self.frequency_num = frequency_num
        self.adjust = adjust

    def __hash__(self) -> int:
        return hash((self.frequency_i, self.frequency_num))

    def __eq__(self, other: object) -> bool:
        if isinstance(other, RegKdataInfo):
            return self.frequency_i == other.frequency_i and self.frequency_num == other.frequency_num
        return False

    def __repr__(self) -> str:
        return f"Person(frequency_i={self.frequency_i}, frequency_num={self.frequency_num}, adjust={self.adjust})"


class FactorInfo:
    dates: List[int]
    # 对应的是标的的因子
    factor_datas: List[List[float]]

    # 对应当前 play_bar_index 下，要推送的 K线数据
    left_bar_pos: List[int]
    # 是去掉线丢应下划线的
    right_bar_pos: List[int]

    def __init__(self, left_bar_pos: List[int], right_bar_pos: List[int], dates: List[int],
                 factor_datas: List[List[float]]) -> None:
        self.left_bar_pos = left_bar_pos
        self.right_bar_pos = right_bar_pos
        self.dates = dates
        self.factor_datas = factor_datas

    def get_factor_index(self, play_index: int) -> int:
        return self.left_bar_pos[play_index]


class Environment:
    task_id: int
    #  手续费倍数(相对于交易所)
    future_cost_fee: float
    # 股票手续费(单位万分之一)
    stock_cost_fee: float
    # 注册数据的索引
    reg_kdata_index_dict: Dict[RegKdataInfo, int]
    # 通过索引获取注册频率
    reg_kdata_index_reg_info_dict: Dict[int, RegKdataInfo]
    # 回放到得索引
    play_bar_index: int
    # 第一个数组 为 reg_kdata_index_dict 对应的索引
    # 第二个是所有 targets
    # 第三个是所有的 target 对应所有的K线数据
    reg_kdata_list: List[KDataInfo]
    # 标的信息
    target_info_dict: Dict[str, dqtrader_rs.PyTargetInfo]
    # 注册因子数据的索引
    # reg_factor_index_dict: Dict[str, int]
    # 隐私索引
    # reg_factor_index_reg_info_dict: Dict[int, List[str]]
    # 因子信息
    reg_factor_data_dict: Dict[str, FactorInfo]
    #
    reg_custom_factor_data_dict: Dict[str, FactorInfo]

    # 存储注册顺序的
    reg_factor_idx_list: [List[str]]
    reg_custom_factor_idx_list: [List[str]]

    target_type_list: List[int]

    # 驱动数据的时间轴
    driver_time_line: List[int]
    # 用于驱动的数据，也会推送到模拟交易所
    driver_kdata_list: KDataInfo
    # 涨跌停数据
    # history_instruments: List[Dict[int, dqtrader_rs.PyHistoryInstrumentData]]
    history_instruments: List[List[dqtrader_rs.PyHistoryInstrumentData]]
    # min频回测中为获取正确的换日市价设置的标志位
    min_freq_turn_pos: bool
    # 当天第一根 bar 的时间
    day_begin_time_rb: int
    # 日索引,用于获取结算价
    date_index: int
    # True, 下一根bar没有开盘价时 order 单 不取消
    market_order_holding: bool
    # LimitType: 限价单成交方式: 默认为 False
    #         False-直接成交
    #         True-下根 bar 内没有该价格时, 撤单处
    limit_type: bool
    # 订单状态回调
    on_order_status: Optional[Callable[[SnapOrder], None]]

    on_order_execution: Optional[Callable[[DQTBackTrade], None]]

    def __init__(self) -> None:
        #  手续费倍数(相对于交易所)
        self.trade_fee = 0.0
        self.future_cost_fee = 1.1
        # 股票手续费(单位万分之一)
        self.stock_cost_fee = 2.5
        self.target_info_dict = {}
        self.reg_kdata_index_dict = {}
        self.reg_kdata_index_reg_info_dict = {}
        self.reg_kdata_list = []
        self.play_bar_index = 0
        self.min_freq_turn_pos = False
        self.driver_time_line = []
        self.driver_kdata_list = KDataInfo([], [], [])
        self.reg_factor_idx_list = []
        self.target_type_list = []

        self.reg_custom_factor_idx_list = []

        self.day_begin_time_rb = -1
        self.date_index = 0
        self.market_order_holding = True
        self.limit_type = False
        self.on_order_status = None
        self.on_order_execution = None
        # 因子数据
        self.reg_factor_data_dict = {}
        self.reg_custom_factor_data_dict = {}

    # 初始化回测标的对象信息

    def init_target_info(self):
        targets = get_strategy().target_list
        target_info_list = dqtrader_rs.get_target_info(targets)
        self.target_type_list = []

        for target_info in target_info_list:
            cost_fee = self.cost_fee_rate(target_info.target_type)

            self.target_type_list.append(target_info.target_type)
            if target_info.trading_fee_unit == "per_value":
                target_info.trading_fee_open = target_info.trading_fee_open * 0.01
                target_info.trading_fee_close = target_info.trading_fee_close * 0.01
                target_info.trading_fee_close_today = target_info.trading_fee_close_today * 0.01
            if target_info.target_type == TargetType.STOCK:
                # 股票
                target_info.trading_fee_open = cost_fee
                target_info.trading_fee_close = cost_fee
                target_info.trading_fee_close_today = cost_fee
            elif target_info.target_type == TargetType.FUTURE:
                # 期货
                target_info.trading_fee_open = target_info.trading_fee_open * cost_fee
                target_info.trading_fee_close = target_info.trading_fee_close * cost_fee
                target_info.trading_fee_close_today = target_info.trading_fee_close_today * cost_fee
            self.target_info_dict[
                str.upper(f"{target_info.market}.{target_info.code}")] = target_info

    def set_task_id(self, task_id: int):
        self.task_id = task_id

    def output_log(self, log: str):
        dqtrader_rs.output_log(self.task_id, log)
        buf = getattr(sys.stdout, "buffer", None)

        if buf is not None:
            buf.write(log.encode('utf-8') + b'\n')
            buf.flush()
        else:
            print(log)

    def set_future_cost_fee(self, future_cost_fee: float):
        self.future_cost_fee = future_cost_fee

    def set_stock_cost_fee(self, stock_cost_fee: float):
        self.stock_cost_fee = stock_cost_fee
        self.trade_fee = self.stock_cost_fee / 10000

    # 获取合约乘数
    def get_multiple(self, target_index: int, default: float = 1.0) -> float:
        strategy = get_strategy()
        target = strategy.target(target_index)
        target_info = self.target_info_dict.get(target)
        if target_info is None:
            return default
        return target_info.multiple

    #
    def get_minmove(self, target_index: int) -> float:
        strategy = get_strategy()
        target = strategy.target(target_index)
        target_info = self.target_info_dict.get(target)
        if target_info is None:
            return 0
        return target_info.min_move

    # 获取
    # def get_long_margin(self, target_index: int, default: float = 1.0) -> float:
    #     account = get_account()
    #     strategy = get_strategy()
    #     target = strategy.target(target_index)
    #     target_info = self.target_info_dict.get(target)
    #     if target_info is None:
    #         return default
    #     return target_info.long_margin * account.margin_rate

    def get_target_info(self, target_index: int) -> dqtrader_rs.PyTargetInfo:
        strategy = get_strategy()
        target = strategy.target(target_index)
        return self.target_info_dict.get(target)

    #

    # def get_short_margin(self, target_index: int, default: float = 1.0) -> float:
    #     strategy = get_strategy()
    #     account = get_account()
    #     target = strategy.target(target_index)
    #     target_info = self.target_info_dict.get(target)
    #     if target_info is None:
    #         return default
    #     return target_info.short_margin * account.margin_rate
    # 获取保证金率

    # def get_margin_rate(self, target_index: int,  side: OrderSide, default: float = 1.0) -> float:
    #     if side == OrderSide.BUY:
    #         return self.get_long_margin(target_index, default)
    #     elif side == OrderSide.SELL:
    #         return self.get_short_margin(target_index, default)
    #     else:
    #         return default

    def cost_fee_rate(self, target_type: TargetType) -> float:
        if target_type == 2:
            # 期货
            return self.future_cost_fee
        elif target_type == 1:
            # 股票
            return self.stock_cost_fee / 1e4
        else:
            return 0

    # 注册数据
    def reg_kdata(self, frequency: str, frequency_i: int, frequency_num: int, adjust: bool) -> bool:
        reg_info = RegKdataInfo(frequency=frequency, frequency_i=frequency_i,
                                frequency_num=frequency_num, adjust=adjust)
        reg_idx = self.reg_kdata_index_dict.get(reg_info)
        if reg_idx is not None:
            return False
        index = len(self.reg_kdata_index_dict)
        self.reg_kdata_index_dict[reg_info] = index
        self.reg_kdata_index_reg_info_dict[index] = reg_info
        return True

    # 获取注册数据的索引
    def reg_kdata_idx(self, frequency_i: int, frequency_num: int, adjust: bool) -> int:
        reg_info = RegKdataInfo(frequency_i=frequency_i,
                                frequency_num=frequency_num, adjust=adjust)
        return self.reg_kdata_index_dict.get(reg_info)

    def store_reg_kdata(self, kdatas: List[List[dqtrader_rs.PyMinOrDayData]]):
        time_line = []
        for kdata in kdatas[0]:
            time_line.append(kdata.datetime)
        #
        left_bar_pos = np.searchsorted(
            time_line, self.driver_time_line, side="left")
        right_bar_pos = np.searchsorted(
            self.driver_time_line, time_line, side="left")
        kdata_info = KDataInfo(left_bar_pos, right_bar_pos, kdatas)
        self.reg_kdata_list.append(kdata_info)

    # 获取注册的 k线 数据
    def get_reg_kdata(self, reg_idx: int) -> KDataInfo:
        return self.reg_kdata_list[reg_idx]

    # 获取注册的频率

    def get_reg_kdata_info(self, reg_idx: int) -> RegKdataInfo:
        return self.reg_kdata_index_reg_info_dict.get(reg_idx)

    # 设置驱动的时间

    def set_driver_kdata(self, driver_kdata_list: List[List[dqtrader_rs.PyMinOrDayData]]):
        time_line = []
        # 获取时间轴
        for kdatas in driver_kdata_list:
            for kdata in kdatas:
                time_line.append(kdata.datetime)
            break
        # 驱动的数据
        self.driver_kdata_list.kdatas = driver_kdata_list
        self.driver_time_line = time_line

    def get_driver_kdata(self, target_index: int) -> dqtrader_rs.PyMinOrDayData:
        return self.driver_kdata_list.kdatas[target_index][self.play_bar_index]

    def get_merge_driver_kdata(self, reg_idx: int, target_index: int, start_index: int) -> dqtrader_rs.PyMinOrDayData:
        target_kdatas = self.driver_kdata_list.kdatas[target_index]
        kdata_info = self.get_reg_kdata(reg_idx)
        last_merge_kdata = kdata_info.get_last_kdata(target_index, start_index)
        if last_merge_kdata is None:
            last_merge_kdata = dqtrader_rs.PyMinOrDayData()
            first_data = target_kdatas[start_index]
            last_merge_kdata.datetime = first_data.datetime
            last_merge_kdata.open = first_data.open
            last_merge_kdata.high = first_data.high
            last_merge_kdata.low = first_data.low
            last_merge_kdata.close = first_data.close
            last_merge_kdata.volume = first_data.volume
            last_merge_kdata.total_turnover = first_data.total_turnover
            last_merge_kdata.open_interest = first_data.open_interest

        play_start_index = kdata_info.get_last_merge_index(target_index, start_index)
        play_bar_index = self.play_bar_index
        for i in range(play_start_index + 1, play_bar_index + 1):
            cur_data = target_kdatas[i]
            last_merge_kdata.high = max(last_merge_kdata.high, cur_data.high)
            last_merge_kdata.low = min(last_merge_kdata.low, cur_data.low)
            last_merge_kdata.total_turnover += cur_data.total_turnover
            last_merge_kdata.open_interest = cur_data.open_interest
            last_merge_kdata.volume += cur_data.volume
            last_merge_kdata.close = cur_data.close
            last_merge_kdata.datetime = cur_data.datetime

        kdata_info.set_last_kdata(target_index, start_index, play_bar_index, last_merge_kdata)
        return last_merge_kdata

    def get_driver_kdatas(self, target_index: int) -> List[dqtrader_rs.PyMinOrDayData]:
        return self.driver_kdata_list.kdatas[target_index]

    def get_driver_time_line(self) -> List[int]:
        return self.driver_time_line

    def is_index(self, target_index: int) -> bool:
        return self.target_type_list[target_index] == TargetType.INDEX

    def is_stock(self, target_index: int) -> bool:
        return self.target_type_list[target_index] == TargetType.STOCK

    def get_target_type(self, target_index: int) -> TargetType:
        return self.target_type_list[target_index]

    # 是否是期货
    def is_future(self, target_index: int) -> bool:
        return self.target_type_list[target_index] == TargetType.FUTURE

    # 存储因子数据
    def store_reg_factor(self, factor: str, factors: dqtrader_rs.PyFactorData):

        driver_time_line = [x // 1_00_00_00_000 for x in self.driver_time_line]

        if len(driver_time_line) == 0:
            driver_time_line = factors.dates

        time_line = factors.dates

        left_bar_pos = np.searchsorted(
            time_line, driver_time_line, side="left")
        right_bar_pos = np.searchsorted(
            driver_time_line, time_line, side="left")

        factor_info = FactorInfo(left_bar_pos, right_bar_pos, factors.dates, factors.values)
        self.reg_factor_data_dict[factor] = factor_info

    # 获取注册的 因子 数据
    def get_reg_factor(self, factor: str) -> FactorInfo:
        return self.reg_factor_data_dict[factor]

    def store_reg_factor_idx(self, factors: List[str]):
        self.reg_factor_idx_list.append(factors)

    def get_reg_factor_by_idx(self, index: int):
        return self.reg_factor_idx_list[index]

    def store_reg_custom_factor_idx(self, factors: List[str]):
        self.reg_custom_factor_idx_list.append(factors)

    def get_reg_custom_factor_by_idx(self, index: int):
        return self.reg_custom_factor_idx_list[index]

    def exist_factor_data(self, factor: str) -> bool:
        factor_info = self.reg_factor_data_dict.get(factor, None)
        return factor_info is not None

    def store_reg_custom_factor(self, factor: str, factors: dqtrader_rs.PyFactorData):

        driver_time_line = [x // 1_00_00_00_000 for x in self.driver_time_line]

        if len(driver_time_line) == 0:
            driver_time_line = factors.dates

        time_line = factors.dates
        left_bar_pos = np.searchsorted(
            time_line, driver_time_line, side="left")
        right_bar_pos = np.searchsorted(
            driver_time_line, time_line, side="left")

        factor_info = FactorInfo(left_bar_pos, right_bar_pos, factors.dates, factors.values)
        self.reg_custom_factor_data_dict[factor] = factor_info

    # 获取注册的 因子 数据
    def get_reg_custom_factor(self, factor: str) -> FactorInfo:
        return self.reg_custom_factor_data_dict[factor]

    def exist_custom_factor_data(self, factor: str) -> bool:
        factor_info = self.reg_custom_factor_data_dict.get(factor, None)
        return factor_info is not None

    # # 获取注册的 因子 数据
    # def get_reg_factor_info(self, reg_idx: int) -> List[str]:
    #   return self.reg_factor_index_reg_info_dict[reg_idx]
    # 设置涨跌停数据

    def set_history_instruments(self, all_history_instruments: List[List[dqtrader_rs.PyHistoryInstrumentData]]):
        self.history_instruments = all_history_instruments

    # 获取涨跌停数据
    # 根据回放推送数据
    def get_history_instruments(self, target_index: int, data_index: int) -> dqtrader_rs.PyHistoryInstrumentData:
        if data_index < 0:
            return None
        return self.history_instruments[target_index][data_index]

    def cur_bar_time(self) -> int:
        for kdatas in self.driver_kdata_list.kdatas:
            if len(kdatas) == 0:
                continue
            return kdatas[self.play_bar_index].datetime

    def get_filled_time(self, target_index: int, reference_time: int) -> int:
        strategy = get_strategy()
        frequency_i = strategy.frequency_int()
        frequency_num = strategy.frequency_num
        if frequency_i == Frequency.Min and frequency_num == 1:
            return time_utils.ymd_hmss_add_minutes(reference_time, -1)

        if frequency_i == Frequency.Day and frequency_num == 1:
            return self.cur_bar_time()

        if (frequency_i in [Frequency.Min, Frequency.Day] and frequency_num > 1) or (
                frequency_num == 1 and frequency_i > Frequency.Day):
            # 取合成bar的第一个原始数据且成交量大于0的时间点
            kdatas = self.get_driver_kdatas(target_index)
            play_bar_index = self.play_bar_index
            for i in range(play_bar_index - 1, -1, -1):
                kdata = kdatas[i]
                if kdata.volume > 0:
                    if frequency_i == Frequency.Min:
                        return time_utils.ymd_hmss_add_minutes(kdata.datetime, -1)
                    else:
                        return kdata.datetime
        return reference_time

    # 获取到，用于驱动的数据

    # def reset_daily_close_time(self):
    #     """将当天停止交易时间设置为0"""
    #     get_account().daily_close_time = None

    # def exist_daily_close_time(self):
    #     """判断用户是否设置当天停止交易时间"""
    #     return get_account().daily_close_time is not None

    # 获取市价
    # 市价默认为 1，下一个 bar 的开盘价
    #  -1 当前刷新Bar的上一Bar收盘价, 0 当前刷新Bar的收盘价, 1 下一个Bar的开盘价, offset>2 表示第n 个tick
    def market_price(self, target_index: int, offset: int = 1) -> Optional[float]:
        #
        kdatas = self.get_driver_kdatas(target_index)
        # kdata_index = self.play_bar_index + offset
        # 当前刷新Bar的收盘价
        if offset == 0:
            return kdatas[self.play_bar_index].close
            # 当前刷新bar的下一个 bar 开盘价
        if offset == 1:
            # 下一个 bar 的开盘价
            next_bar_index = self.play_bar_index + offset
            if next_bar_index >= len(self.driver_time_line):
                next_bar_index = self.play_bar_index
            return kdatas[next_bar_index].open
        if offset <= -1:
            # 当前刷新bar的上一个bar的收盘价(price_loc = 0 时需要使用下单的bar的收盘价作为市价单成交位置）
            pre_bar_index = self.play_bar_index + offset
            if pre_bar_index < 0:
                pre_bar_index = 0
            return kdatas[pre_bar_index].close

        strategy = get_strategy()
        target = strategy.target(target_index)
        cur_bar_time = self.driver_time_line[self.play_bar_index]
        tick_datas = dqtrader_rs.get_tick(target, "", cur_bar_time, 0)
        tick_data_len = len(tick_datas)
        if tick_data_len >= 1:
            pos = tick_data_len - 1 if tick_data_len < offset else offset - 1
            return tick_datas[pos].last
        return np.nan

    # 获取结算价
    # :param target_index: int, 标的索引
    # :param pos: int, -1表示昨,0表示今
    # :return: price: float
    def settle_price(self, target_index: int, offset: int = -1) -> float:
        day_offset = self.date_index + offset
        # 结算价是按天的
        history_instrument = self.get_history_instruments(
            target_index, day_offset)
        if history_instrument is None:
            return self.market_price(target_index)

        return history_instrument.settlement

    # 判断普通单是昨还是今
    def is_old_order_rb(self, order_updated_time: int) -> bool:
        strategy = get_strategy()
        strategy_frequency_i = strategy.frequency_int()
        if strategy_frequency_i < Frequency.Min:
            raise NotImplementedError
        elif strategy_frequency_i == Frequency.Min:
            return order_updated_time < self.day_begin_time_rb
        return True

    #  当前价格是涨停价
    def at_limit_up_price(self, target_index: int) -> bool:
        history_instrument = self.get_history_instruments(
            target_index, self.date_index)
        if history_instrument is None:
            return False
        kdata = self.get_driver_kdata(target_index)

        return kdata.high == kdata.low == history_instrument.up_limit_price

    # 当前价格是跌停价
    def at_limit_down_price(self, target_index: int) -> bool:
        history_instrument = self.get_history_instruments(
            target_index, self.date_index)
        if history_instrument is None:
            return False
        kdata = self.get_driver_kdata(target_index)

        return kdata.high == kdata.low == history_instrument.down_limit_price

    @staticmethod
    def is_valid_order_id(order_id: int) -> bool:
        return not (isnan(order_id) or order_id is None)


_env = None


def get_env():
    global _env
    if _env is None:
        _env = Environment()
    return _env


def reset_env():
    global _env
    _env = None
