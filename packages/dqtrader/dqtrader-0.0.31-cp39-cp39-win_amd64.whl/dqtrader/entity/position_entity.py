from math import nan

from dqtrader.backtest_environment import get_env
from dqtrader.enums import PositionChangeReason, PositionSide, TargetType


PRECISION_MUL = 10 ** 3


class PositioinSnapshot:
    # 代码
    code: str
    # 目标索引
    target_index: int
    # 多头持仓数量
    volume_long: int
    # 空头持仓数量
    volume_short: int
    # 多头持仓数量(今仓)
    volume_today_long: int
    # 空头持仓数量(今仓)
    volume_today_short: int
    # 多头持仓的浮动盈亏（Floating Profit and Loss for Long Positions）
    fpnl_long: float
    # 空头持仓的浮动盈亏（Floating Profit and Loss for Long Positions）
    fpnl_short: float
    # 多头持仓的零基准盈亏（Zero-based Profit and Loss）
    zpnl_long: float
    # 空头持仓的零基准盈亏（Zero-based Profit and Loss）
    zpnl_short: float
    # 多头持仓成本(昨仓)
    holding_cost_long: float
    # 空头持仓成本(昨仓)
    holding_cost_short: float
    # 多头开仓均价(昨仓)
    cost_long: float
    # 空头开仓均价(昨仓)
    cost_short: float
    # 多头持仓的数量
    amount_long: float
    # 空头持仓的数量
    amount_short: float
    # 多头持仓的价值
    holding_value_long: float
    # 空头持仓的价值
    holding_value_short: float
    # 可平仓位【总】
    available_long: int
    available_short: int
    # 可平今多头仓位【今日】
    available_today_long: float
    # 可平今空头仓位【今日】
    available_today_short: float
    # 价格
    price: float
    # 多头建仓时间
    created_long: int
    # 空头建仓时间
    created_short: int
    # 仓位变更时间
    updated: int
    # 挂单冻结多头仓位: 股票当天买入的不能卖出
    order_frozen_long: int
    # 挂单冻结空头仓位: 股票当天买入的不能卖出
    order_frozen_short: int
    # 挂单冻结多头仓位(今仓)
    order_frozen_today_long: int
    # 挂单冻结空头仓位(今仓)
    order_frozen_today_short: int
    # 多头保证金
    margin_long: float
    # 空头保证金
    margin_short: float
    # 变更理由
    change_reason: int

    def __init__(self) -> None:
        # 代码
        self.code = ""
        # 目标索引
        self.target_index = 0
        # 多头持仓数量
        self.volume_long = 0
        # 空头持仓数量
        self.volume_short = 0
        # 多头持仓数量(今仓)
        self.volume_today_long = 0
        # 空头持仓数量(今仓)
        self.volume_today_short = 0
        # 多头持仓的浮动盈亏（Floating Profit and Loss for Long Positions）
        self.fpnl_long = 0.0
        # 空头持仓的浮动盈亏（Floating Profit and Loss for Long Positions）
        self.fpnl_short = 0.0
        # 多头持仓的零基准盈亏（Zero-based Profit and Loss）
        self.zpnl_long = 0.0
        # 空头持仓的零基准盈亏（Zero-based Profit and Loss）
        self.zpnl_short = 0.0
        # 多头持仓成本(昨仓)
        self.holding_cost_long = 0.0
        # 空头持仓成本(昨仓)
        self.holding_cost_short = 0.0
        # 多头开仓均价(昨仓)
        self.cost_long = 0.0
        # 空头开仓均价(昨仓)
        self.cost_short = 0.0
        # 多头持仓的数量
        self.amount_long = 0.0
        # 空头持仓的数量
        self.amount_shor = 0.0
        # 多头持仓的价值
        self.holding_value_long = 0.0
        # 空头持仓的价值
        self.holding_value_short = 0.0
        # 可平仓位【总】
        self.available_long = 0
        self.available_short = 0
        # 可平今多头仓位【今日】
        self.available_today_long = 0.0
        # 可平今空头仓位【今日】
        self.available_today_short = 0.0
        # 价格
        self.price = 0.0
        # 多头建仓时间
        self.created_long = nan
        # 空头建仓时间
        self.created_short = nan
        # 仓位变更时间
        self.updated = nan
        # 挂单冻结多头仓位: 股票当天买入的不能卖出
        self.order_frozen_long = 0
        # 挂单冻结空头仓位: 股票当天买入的不能卖出
        self.order_frozen_short = 0
        # 挂单冻结多头仓位(今仓)
        self.order_frozen_today_long = 0
        # 挂单冻结空头仓位(今仓)
        self.order_frozen_today_short = 0
        # 多头保证金
        self.margin_long = 0.0
        # 空头保证金
        self.margin_short = 0.0
        # 变更理由
        self.change_reason = 0


class BasePosition:
    # 目标索引
    target_index: int
    # szse.000001
    target: str
    # 下单类型
    type: TargetType
    # 建仓时间
    create_long_time: int
    # 仓位变更时间
    update_time: int
    # 今开价格和数量: list of list[[price,volume]]
    holding_cost_today_long_list: list[tuple[float, int]]
    # 挂单冻结仓位: 股票当天买入的不能卖出
    order_frozen_long: int
    # 持仓数量(昨仓)
    volume_long_yd: int
    # 多头冻结仓位(今仓)
    order_frozen_today_long: int
    # 持仓成本(昨仓)
    holding_cost_long: int
    # 可平仓位【总】
    available_long: int
    # 变更理由
    change_reason: PositionChangeReason

    def __init__(self, target_index: int, target: str, type: TargetType) -> None:
        self.target_index = target_index
        self.target = target
        self.type = type
        self.holding_cost_today_long_list = []
        # 建仓时间（datetime类型）
        self.create_long_time = nan
        # 仓位变更时间
        self.update_time = nan
        # 挂单冻结仓位: 股票当天买入的不能卖出
        self.order_frozen_long = 0
        # 持仓数量(昨仓)
        self.volume_long_yd = 0
        # 多头冻结仓位(今仓)
        self.order_frozen_today_long = 0
        # 持仓成本(昨仓)
        self.holding_cost_long = 0
        # 可平仓位【总】
        self.available_long = 0
        # 变更理由
        self.change_reason = 0

    def total_volume_long(self):
        raise NotImplementedError

    def total_volume_short(self):
        raise NotImplementedError

    # 保持一致接口, 返回所有可用多头仓位
    @property
    def position_available_long(self):
        raise NotImplementedError

    # 保持一致接口, 返回所有可用空头仓位

    @property
    def position_available_short(self):
        raise NotImplementedError

    @property
    def position_available_today_long(self):
        raise NotImplementedError

    @property
    def position_available_today_short(self):
        raise NotImplementedError

    #   生成账户快照
    # :return: dict 结构
    #
    def snapshot(self):
        raise NotImplementedError

    def volume(self, side: PositionSide):
        raise NotImplementedError

    def market_value(self, side):
        raise NotImplementedError

    # 标的多头持仓量(单位：股)
    # :param target_index: 标的索引
    # :return: int 标的仓位
    def volume_long(self) -> int:
        value = self.volume_long_yd
        for _, v in self.holding_cost_today_long_list:
            value += v
        return value

    # 返回今仓多头持仓仓位
    # 股票单位 股
    # param target_index: int 标的索引
    # return: int 仓位信息
    def volume_long_today(self) -> int:
        value = 0
        for _, v in self.holding_cost_today_long_list:
            value += v
        return value


class StockPosition(BasePosition):
    # 可平今仓位【今日】
    available_today_long: int

    def __init__(self, target_index: int, target: str) -> None:
        super(StockPosition, self).__init__(
            target_index, target, TargetType.STOCK)
        self.available_today_long = 0
        # 今开价格和数量: list of list[[price,volume]]

    def volume(self, side: PositionSide) -> int:
        if side == PositionSide.LONG:
            return self.volume_long_yd + sum((v for _, v in self.holding_cost_today_long_list))
        return 0

    # 保持一致接口, 返回所有可用多头仓位
    @property
    def position_available_long(self):
        return self.available_today_long

    # 保持一致接口, 返回所有可用空头仓位
    @property
    def position_available_short(self):
        return 0

    @property
    def position_available_today_long(self):
        return 0

    @property
    def position_available_today_short(self):
        return 0

    @property
    def total_volume_long(self):
        volume = self.volume_long_yd
        volume += sum((v for _, v in self.holding_cost_today_long_list))
        volume += self.order_frozen_long
        return volume

    @property
    def total_volume_short(self):
        return 0

    # 执行快照
    def snapshot(self) -> PositioinSnapshot:
        #
        env = get_env()
        market_price = env.market_price(self.target_index, 0)
        holding_cost: float = 0.0
        volume_today: int = 0
        #
        for c, v in self.holding_cost_today_long_list:
            holding_cost += c
            volume_today += v

        position_snapshot = PositioinSnapshot()
        position_snapshot.code = self.target
        position_snapshot.target_index = self.target_index
        position_snapshot.volume_long = int(self.volume_long_yd + volume_today)
        position_snapshot.volume_short = 0
        position_snapshot.volume_today_long = 0
        position_snapshot.volume_today_short = 0
        position_snapshot.fpnl_long = (((market_price * self.volume_long_yd - self.holding_cost_long) + (
                market_price * volume_today - holding_cost)) * PRECISION_MUL + 0.5) // 1 / PRECISION_MUL
        position_snapshot.fpnl_short = 0.0
        position_snapshot.zpnl_long = position_snapshot.fpnl_long
        position_snapshot.zpnl_short = 0.0
        position_snapshot.holding_cost_long = (((holding_cost + self.holding_cost_long) /
                                                position_snapshot.volume_long if position_snapshot.volume_long != 0 else 0.0) * PRECISION_MUL + 0.5) // 1 / PRECISION_MUL
        position_snapshot.holding_cost_short = 0.0
        position_snapshot.cost_long = position_snapshot.holding_cost_long
        position_snapshot.cost_short = 0.0
        position_snapshot.amount_long = ((holding_cost + self.holding_cost_long)
                                         * PRECISION_MUL + 0.5) // 1 / PRECISION_MUL
        position_snapshot.amount_short = 0.0
        position_snapshot.holding_value_long = (
                                                       market_price * position_snapshot.volume_long * PRECISION_MUL + 0.5) // 1 / PRECISION_MUL
        position_snapshot.holding_value_short = 0.0
        position_snapshot.available_long = int(self.available_long)
        position_snapshot.available_short = 0
        position_snapshot.available_today_long = 0
        position_snapshot.available_today_short = 0
        position_snapshot.price = market_price
        position_snapshot.created_long = self.create_long_time
        position_snapshot.created_short = nan
        position_snapshot.updated = self.update_time
        position_snapshot.order_frozen_long = self.order_frozen_long
        position_snapshot.order_frozen_short = 0
        position_snapshot.order_frozen_today_long = self.order_frozen_today_long
        position_snapshot.order_frozen_today_short = 0
        position_snapshot.margin_long = 0.0
        position_snapshot.margin_short = 0.0
        position_snapshot.change_reason = self.change_reason

        return position_snapshot


class FuturePosition(BasePosition):
    # 多头开仓均价(昨仓)
    cost_long: float

    # 总多头持仓金额， 每一次调用on_trade,on_settlement的时候更新
    long_holding_total: float

    # 空头开仓均价(昨仓)
    cost_short: float

    # 空头仓位持仓(昨仓)
    volume_short_yd: int

    # 空头持仓均价(昨仓)
    holding_cost_short: float

    # 今开空头均价和数量: list of list [[price,volume]]
    holding_cost_today_short_list: list[tuple[float, int]]

    # 空头冻结仓位
    order_frozen_short: int

    # 空头冻结仓位（今仓）
    order_frozen_today_short: int

    # 可平空头仓位【总】
    available_short: int

    # 空头建仓时间
    create_short_time: int

    # 总空头持仓金额， 每一次调用on_trade,on_settlement的时候更新
    short_holding_total: float = 0.0

    def __init__(self, target_index: int, target: str) -> None:
        super(FuturePosition, self).__init__(
            target_index, target, TargetType.FUTURE)

        self.holding_cost_today_short_list = []

        # 多头开仓均价(昨仓)
        self.cost_long = 0.0

        # 总多头持仓金额， 每一次调用on_trade,on_settlement的时候更新
        self.long_holding_total = 0.0

        # 空头开仓均价(昨仓)
        self.cost_short = 0.0

        # 空头仓位持仓(昨仓)
        self.volume_short_yd = 0

        # 空头持仓均价(昨仓)
        self.holding_cost_short = 0.0

        # 空头冻结仓位
        self.order_frozen_short = 0

        # 空头冻结仓位（今仓）
        self.order_frozen_today_short = 0

        # 可平空头仓位【总】
        self.available_short = 0

        # 空头建仓时间(datetime类型)
        self.create_short_time = nan

        # 总空头持仓金额， 每一次调用on_trade,on_settlement的时候更新
        self.short_holding_total = 0.0

    def volume(self, side: PositionSide) -> int:
        if side == PositionSide.SHORT:
            return self.volume_short_yd + sum(v for _, v in self.holding_cost_today_short_list)

        return self.volume_long_yd + sum(v for _, v in self.holding_cost_today_long_list)

    # 保持一致接口, 返回所有可用多头仓位

    @property
    def position_available_long(self):
        return self.available_long

    # 保持一致接口, 返回所有可用空头仓位

    @property
    def position_available_short(self):
        return self.available_short

    @property
    def position_available_today_long(self):
        volume_today_long = 0
        for p, v in self.holding_cost_today_long_list:
            volume_today_long += v
        return volume_today_long

    @property
    def position_available_today_short(self):
        volume_today_short = 0
        for p, v in self.holding_cost_today_short_list:
            volume_today_short += v
        return volume_today_short

    @property
    def total_volume_long(self):
        volume = self.volume_long_yd
        volume += sum((v for _, v in self.holding_cost_today_long_list))
        return volume

    @property
    def total_volume_short(self):
        volume = self.volume_short_yd
        volume += sum((v for _, v in self.holding_cost_today_short_list))
        return volume

    def volume_short(self) -> int:
        value = self.volume_short_yd
        for _, v in self.holding_cost_today_short_list:
            value += v
        return value

    def volume_short_today(self) -> int:
        value = 0
        for _, v in self.holding_cost_today_short_list:
            value += v
        return value

    # 期货账户的持仓市值
    # :param side: 持仓方向
    # :return: 期货账户总市值
    def market_value(self, side):
        env = get_env()
        total_market_value = 0.0
        multiple = env.get_multiple(self.target_index)
        m_price = env.market_price(self.target_index, 0)

        if side == PositionSide.LONG:
            total_volume = self.volume_long_yd
            total_volume += sum((v for _,
                                       v in self.holding_cost_today_long_list))
        else:
            total_volume = self.volume_short_yd
            total_volume += sum((v for _,
                                       v in self.holding_cost_today_short_list))
        total_market_value += total_volume * m_price * multiple
        return total_market_value

    # def get_long_margin(self, target_index: int, default: float = 1.0) -> float:
    #     env = get_env()
    #     strategy = get_strategy()
    #     target = strategy.target(target_index)
    #     target_info = env.target_info_dict.get(target)
    #     if target_info is None:
    #         return default
    #     return target_info.long_margin * self.margin_rate

    # def get_short_margin(self, target_index: int, default: float = 1.0) -> float:
    #     strategy = get_strategy()
    #     env = get_env()
    #     target = strategy.target(target_index)
    #     target_info = env.target_info_dict.get(target)
    #     if target_info is None:
    #         return default
    #     return target_info.short_margin * self.margin_rate

    # def cost_fee_rate(self, target_type: TargetType) -> float:
    #     if target_type == 2:
    #         # 期货
    #         return self.future_cost_fee
    #     elif target_type == 1:
    #         # 股票
    #         return self.stock_cost_fee / 1e4
    #     else:
    #         return 0

    # 生成快照
    def snapshot(self) -> PositioinSnapshot:
        env = get_env()
        market_price = env.market_price(self.target_index, 0)

        multiple = env.get_multiple(self.target_index)
        # 这里要考虑
        margin_rate_long = env.get_long_margin(self.target_index, 1)
        margin_rate_short = env.get_short_margin(self.target_index, 1)

        holding_cost_long_today = 0.0
        volume_today_long = 0
        holding_cost_short_today = 0.0
        volume_today_short = 0
        for p, v in self.holding_cost_today_long_list:
            holding_cost_long_today += p * v * multiple
            volume_today_long += v
        for p, v in self.holding_cost_today_short_list:
            holding_cost_short_today += p * v * multiple
            volume_today_short += v

        market_value_long = (self.volume_long_yd +
                             volume_today_long) * market_price * multiple
        market_value_short = (self.volume_short_yd +
                              volume_today_short) * market_price * multiple
        position_snapshot = PositioinSnapshot()
        position_snapshot.code = self.target
        position_snapshot.target_index = self.target_index
        position_snapshot.volume_long = int(
            self.volume_long_yd + volume_today_long)
        position_snapshot.volume_short = int(
            self.volume_short_yd + volume_today_short)
        position_snapshot.volume_today_long = int(volume_today_long)
        position_snapshot.volume_today_short = int(volume_today_short)
        position_snapshot.fpnl_long = ((market_value_long - self.holding_cost_long * self.volume_long_yd *
                                        multiple - holding_cost_long_today) * PRECISION_MUL + 0.5) // 1 / PRECISION_MUL
        position_snapshot.fpnl_short = ((self.holding_cost_short * self.volume_short_yd * multiple +
                                         holding_cost_short_today - market_value_short) * PRECISION_MUL + 0.5) // 1 / PRECISION_MUL
        position_snapshot.zpnl_long = ((market_price * (
                    self.volume_long_yd + volume_today_long) * multiple - self.cost_long *
                                        self.volume_long_yd * multiple - holding_cost_long_today) * PRECISION_MUL + 0.5) // 1 / PRECISION_MUL
        position_snapshot.zpnl_short = ((
                                                    self.cost_short * self.volume_short_yd * multiple + holding_cost_short_today - market_price * (
                                                    self.volume_short_yd + volume_today_short) * multiple) * PRECISION_MUL + 0.5) // 1 / PRECISION_MUL
        position_snapshot.holding_cost_long = (((
                                                            self.holding_cost_long * self.volume_long_yd * multiple + holding_cost_long_today) / (
                                                            (self.volume_long_yd +
                                                             volume_today_long) * multiple) if (
                                                                                                           self.volume_long_yd + volume_today_long) != 0 else 0.0) * PRECISION_MUL + 0.5) // 1 / PRECISION_MUL
        position_snapshot.holding_cost_short = (((
                                                             self.holding_cost_short * self.volume_short_yd * multiple + holding_cost_short_today) / (
                                                             (self.volume_short_yd +
                                                              volume_today_short) * multiple) if (
                    self.volume_short_yd + volume_today_short != 0) else 0.0) * PRECISION_MUL + 0.5) // 1 / PRECISION_MUL
        position_snapshot.cost_long = (((self.cost_long * self.volume_long_yd * multiple + holding_cost_long_today) / (
                    (self.volume_long_yd + volume_today_long)
                    * multiple) if (
                    self.volume_long_yd + volume_today_long != 0) else 0.0) * PRECISION_MUL + 0.5) // 1 / PRECISION_MUL
        position_snapshot.cost_short = (((
                                                     self.cost_short * self.volume_short_yd * multiple + holding_cost_short_today) / (
                                                     (self.volume_short_yd + volume_today_short)
                                                     * multiple) if (
                    self.volume_short_yd + volume_today_short != 0) else 0.0) * PRECISION_MUL + 0.5) // 1 / PRECISION_MUL
        position_snapshot.amount_long = ((holding_cost_long_today + self.volume_long_yd *
                                          self.holding_cost_long * multiple) * PRECISION_MUL + 0.5) // 1 / PRECISION_MUL
        position_snapshot.amount_short = ((holding_cost_short_today + self.volume_short_yd *
                                           self.holding_cost_short * multiple) * PRECISION_MUL + 0.5) // 1 / PRECISION_MUL
        position_snapshot.holding_value_long = (
                                                       market_value_long * PRECISION_MUL + 0.5) // 1 // PRECISION_MUL
        position_snapshot.holding_value_short = (
                                                        market_value_short * PRECISION_MUL + 0.5) // 1 / PRECISION_MUL
        position_snapshot.available_long = int(self.available_long)
        position_snapshot.available_short = int(self.available_short)
        position_snapshot.available_today_long = volume_today_long
        position_snapshot.available_today_short = volume_today_short
        position_snapshot.price = market_price
        position_snapshot.created_long = self.create_long_time
        position_snapshot.created_short = self.create_short_time
        position_snapshot.updated = self.update_time
        position_snapshot.order_frozen_long = self.order_frozen_long
        position_snapshot.order_frozen_short = self.order_frozen_short
        position_snapshot.order_frozen_today_long = self.order_frozen_today_long
        position_snapshot.order_frozen_today_short = self.order_frozen_today_short
        position_snapshot.margin_long = ((self.holding_cost_long * self.volume_long_yd * margin_rate_long * multiple +
                                          holding_cost_long_today * margin_rate_long) * PRECISION_MUL + 0.5) // 1 / PRECISION_MUL
        position_snapshot.margin_short = ((
                                                      self.holding_cost_short * self.volume_short_yd * margin_rate_short * multiple +
                                                      holding_cost_short_today * margin_rate_short) * PRECISION_MUL + 0.5) // 1 / PRECISION_MUL
        position_snapshot.change_reason = self.change_reason
        return position_snapshot


class StockCommissionRate:
    open_tax: float  # 开仓印花税
    close_tax: float  # 平仓印花税
    trade_fee: float  # 佣金
    min_trade_fee: float  # 最小佣金
    trans_fee: float

    def __init__(self) -> None:
        self.open_tax = 0.0  # 开仓印花税
        self.close_tax = 0.001  # 平仓印花税
        self.trade_fee = 0.0002  # 佣金
        self.min_trade_fee = 5.0  # 最小佣金
        self.trans_fee = 0.00002
