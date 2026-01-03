from typing import List, Dict, Optional
import dqtrader_rs
from dqtrader.enums import Frequency, TargetType
from dqtrader.backtest_environment import RegKdataInfo
from dqtrader.strategy import get_strategy


class KDataInfo:
    kdatas: List[List[dqtrader_rs.PyMinOrDayData]]
    trading_scope: List[int]

    def __init__(self, trading_scope: List[int], kdatas: List[List[dqtrader_rs.PyMinOrDayData]]) -> None:
        self.kdatas = kdatas
        self.trading_scope = trading_scope

    def find_real_trading_datetime(self, kdata_datetime: int):
        for trading_point in self.trading_scope:
            if trading_point.datetime >= kdata_datetime:
                return trading_point.datetime
        return self.trading_scope[-1].datetime

    def update_time_scope(self, trading_scope: List[int]):
        self.trading_scope = trading_scope


class Environment:
    task_id: int
    # 注册数据的索引
    reg_kdata_index_dict: Dict[RegKdataInfo, int]
    # 通过索引获取注册频率
    reg_kdata_index_reg_info_dict: Dict[int, RegKdataInfo]
    # 第一个数组 为 reg_kdata_index_dict 对应的索引
    # 第二个是所有 targets
    # 第三个是所有的 target 对应所有的K线数据
    reg_kdata_list: List[KDataInfo]

    driver_kdata: KDataInfo
    # 标的信息
    target_info_dict: Dict[str, dqtrader_rs.PyTargetInfo]



    def __init__(self) -> None:
        self.task_id = 0
        self.reg_kdata_list = []
        self.target_info_dict = {}
        self.reg_kdata_index_dict = {}
        self.reg_kdata_index_reg_info_dict = {}

        # 驱动时间轴
        self.driver_kdata = KDataInfo([], [])

    def init_target_info(self):
        targets = get_strategy().target_list
        target_info_list = dqtrader_rs.get_target_info(targets)

        strategy = get_strategy()
        # 判断是不是主链，是的话则获取获取真实的
        for target_info in target_info_list:
            order_book_id = f"{target_info.market}.{target_info.code}"
            #
            is_future_combine = dqtrader_rs.is_future_combine(order_book_id)
            if is_future_combine:

              real_code = dqtrader_rs.get_future_real_code_by_main_contract(order_book_id)
              strategy.set_real_order_book_id(order_book_id, f"{target_info.market}.{real_code.code}")

            self.target_info_dict[
                str.upper(order_book_id)] = target_info

    #
    def reg_kdata(self, frequency: str, frequency_i: int, frequency_num: int, adjust: bool) -> bool:
        reg_info = RegKdataInfo(frequency=frequency, frequency_i=frequency_i, frequency_num=frequency_num,
                                adjust=adjust)
        reg_idx = self.reg_kdata_index_dict.get(reg_info)
        if reg_idx is not None:
            return False
        index = len(self.reg_kdata_index_dict)
        self.reg_kdata_index_dict[reg_info] = index
        self.reg_kdata_index_reg_info_dict[index] = reg_info
        return True

    def get_reg_index(self, reg_key: RegKdataInfo) -> int:
        return self.reg_kdata_index_dict[reg_key]

    def get_all_reg_keys(self) -> List[RegKdataInfo]:
        keys = self.reg_kdata_index_dict.keys()
        return list(keys)

    def set_task_id(self, task_id: int):
        self.task_id = task_id

    def get_task_id(self):
        return self.task_id

    def output_log(self, log: str):
        dqtrader_rs.output_log(self.task_id, log)
        print(log)

    def get_min_reg_index(self):
        index_arr = []
        for index, reg_info in enumerate(self.reg_kdata_index_dict.keys()):
            if reg_info.frequency_i == Frequency.Min:
                index_arr.append(index)
        return index_arr

    def get_day_reg_index(self):
        index_arr = []
        for index, reg_info in enumerate(self.reg_kdata_index_dict.keys()):
            if reg_info.frequency_i == Frequency.Day:
                index_arr.append(index)
        return index_arr

    def store_reg_kdata(self, trading_scope: List[int], kdatas: List[List[dqtrader_rs.PyMinOrDayData]]):
        kdata_info = KDataInfo(trading_scope, kdatas)
        self.reg_kdata_list.append(kdata_info)

    def get_reg_kdata(self, reg_idx: int) -> KDataInfo:
        return self.reg_kdata_list[reg_idx]

    def set_driver_kdata(self, trading_scope: List[int], driver_kdata_list: List[List[dqtrader_rs.PyMinOrDayData]]):
        self.driver_kdata.trading_scope = trading_scope
        self.driver_kdata.kdatas = driver_kdata_list

    def get_driver_kdata_info(self) -> KDataInfo:
        return self.driver_kdata

    def get_driver_kdatas(self, target_index: int) -> List[dqtrader_rs.PyMinOrDayData]:
        return self.driver_kdata.kdatas[target_index]

    # 获取市价
    # 市价默认为 1，下一个 bar 的开盘价
    #  -1 当前刷新Bar的上一Bar收盘价, 0 当前刷新Bar的收盘价, 1 下一个Bar的开盘价, offset>2 表示第n 个tick
    def market_price(self, target_index: int, offset: int = 1) -> Optional[float]:
        kdatas = self.get_driver_kdatas(target_index)
        # 当前刷新Bar的收盘价
        if offset == 0:
            # 最后 一根 bar
            return kdatas[-1].close
        if offset <= -1:
            if offset < -len(kdatas):
                offset = -len(kdatas)
            return kdatas[offset].open

        # 获取当前的 实时行情
        strategy = get_strategy()
        target = strategy.target(target_index)

        cur_tick_data = dqtrader_rs.get_cur_rt_tick_data(target)
        return cur_tick_data.last

    def get_multiple(self, target_index: int, default: float = 1.0) -> float:
        strategy = get_strategy()
        target = strategy.target(target_index)
        target_info = self.target_info_dict.get(target)
        if target_info is None:
            return default
        return target_info.multiple


_env = None


def get_env():
    global _env
    if _env is None:
        _env = Environment()
    return _env
