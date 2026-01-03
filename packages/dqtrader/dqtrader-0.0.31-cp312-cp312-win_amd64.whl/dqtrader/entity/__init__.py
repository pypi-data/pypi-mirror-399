
from math import nan
from dqtrader.enums import OrderPositionEffect, OrderRejectReason, OrderSide, OrderStatus, OrderStopExecType, OrderStopGapType, OrderStopTrailingType, OrderStopType, OrderType, TargetType


class FrozenInfo:
    # order 单期货: 手续费
    # order 单股票: 手续费
    fee: float
    # order 单期货: 保证金
    # order 单股票: price * volume
    value: float
    # trader 单期货: 手续费
    # trader 单股票: 手续费
    trader_fee: float
    # trader 单期货:保证金
    # trader 单股票: price * volume
    trader_value: float

    def __init__(self) -> None:
        self.fee = 0.0
        self.value = 0.0
        self.trader_fee = 0.0
        self.trader_value = 0.0

    def set_fee(self, fee: float):
        self.fee = fee

    def set_value(self, value: float):
        self.value = value

    def set_trader_fee(self, trader_fee: float):
        self.trader_fee = trader_fee

    def set_trader_value(self, trader_value: float):
        self.trader_value = trader_value


# 基类单: 普通单基类, 止损单基类, 交易单记录
class DQTOrderBase:
    # 标的类型: 股票, 期货, 期权
    target_type: TargetType = None
    target_index: int
    order_id: int
    # SSE.600000
    code: str
    # 委托来源:
    # 0 手动下单
    # 1 策略下单
    source: int
    # 委托状态
    status: OrderStatus
    # 委托拒绝原因
    rej_reason: OrderRejectReason
    # 委托价格: 只有限价单有意义
    price: float
    # 委托量
    volume: int
    # 委托金额
    value: float
    # 已成交的数量
    filled_volume: int
    # 本次订单已成交数量均价
    filled_average: float
    # 已成交金额
    filled_amount: float
    # 委托创建时间
    created_time: int
    # 最近一次更新时间
    updated_time: int
    # 开平标志: 开/平/平今
    position_effect: OrderPositionEffect
    # 价格类型: 市价/限价
    # 委托类型:
    # 0 不明
    # 1 限价
    # 2 市价
    # 3 即时成交剩余
    # ...
    ctg: OrderType
    # 买卖方向: 买/卖
    side: OrderSide
    # 定单标记, 说明性文字
    tag: str
    frozen_info: FrozenInfo

    def __init__(self):
        self.order_broker = None
        # 标的类型: 股票, 期货, 期权
        self.target_type = None
        self.target_index = None
        self.order_id = None
        # 标的代码, 如: SSE.600000
        self.code = None

        # 委托来源:
        # 0 手动下单
        # 1 策略下单
        self.source = 1

        # 委托状态
        self.status = None
        # 委托拒绝原因
        self.rej_reason = None

        # 委托价格: 只有限价单有意义
        self.price = 0.0
        # 委托量
        self.volume = 0
        # 委托金额
        self.value = 0.0

        # 已成交的数量
        self.filled_volume = 0
        # 本次订单已成交数量均价
        self.filled_average = 0
        # 已成交金额
        self.filled_amount = 0.0

        # 委托创建时间
        self.created_time = None
        # 最近一次更新时间
        self.updated_time = None
        # 开平标志: 开/平/平今
        self.position_effect = None
        # 价格类型: 市价/限价
        # 委托类型:
        # 0 不明
        # 1 限价
        # 2 市价
        # 3 即时成交剩余
        # ...
        self.ctg = None
        # 买卖方向: 买/卖
        self.side = None
        # 定单标记, 说明性文字
        self.tag = ''
        self.frozen_info = FrozenInfo()

    @property
    def unfilled_volume(self):
        return self.volume - self.filled_volume

    def update_status(self, order_status: OrderStatus, rej_reason: OrderRejectReason, update_time: int):
        self.status = order_status
        if rej_reason is not None:
            self.rej_reason = rej_reason
        self.update_time = update_time


# 撤单
class DQTStopOrderBase:
    # 止盈止损委托单ID
    stop_order_id: int
    # 执行状态:
    execute_status: OrderStopExecType
    # 标的索引
    target_index: int
    # 标的名称: 'SSE.600000'
    code: str
    # 止盈止损单触发时形成新的 order_id,
    # 注意: target_order_id 不是同一个值
    order_id: int
    # 针对已存在的目标订单ID
    target_order_id: int
    # 目标单成交价格（成本价）
    target_price: float
    # 触发时实际成交价, 注意区分(stop_price 和 stop_trailing_price)
    trigger_real_price: float
    # 创建 stop_order_id 时 bar 的时间
    created_time: int

    # 更新时间
    updated_time: int

    # 触发时间
    trigger_time: int
    # 止损单类型: StopOrderType_Loss, StopOrderType_Profit, StopOrderType_Trailing
    stop_order_type: OrderStopType
    # 出场
    # 止损阈值(也叫回落点, 计算触发价, 触发价 = 最高价 +/- 回落点)
    stop_gap: float
    # 止损阈值类型: Point, Percent
    stop_gap_type: OrderStopGapType
    # 入场
    # 追踪阈值(也叫追踪点差, 计算启动价, 启动价 = 成本价 +/- 追踪点差)
    # 满足最小变动单位
    trailing_gap: int
    # 追踪类型: Point, Percent
    trailing_gap_type: OrderStopTrailingType
    # 追踪启动价(启动价 = 成本价 +/- trailing_gap)
    trailing_price: float
    # 追踪最高价
    trailing_high: float
    # 追踪最低价
    trailing_low: float
    # 追踪止盈出场价(触发价, 计算得出的)
    stop_trailing_price: float
    # 止损/止盈出场价(触发价, 计算得出的)
    stop_price: float
    # 追踪标记位: 是否开始追踪
    is_begin_trailing: bool
    # 是否在启动价(入场价)的 bar 位置
    in_begin_trailing_bar: bool
    # 是否在成本价的 bar 位置
    in_bar_begin: bool
    # 交易数量, 与 target_order_id 数量相同
    volume: int
    # 买卖操作标识: OrderAct_Sell, OrderAct_Buy
    # 注意: 与 target_order_id 相同方向
    act: OrderSide
    # 买卖价格类型: OrderCtg_Limit, OrderCtg_Market
    ctg: OrderType
    # 买卖订单标识, 字符串, 通常是说明性字符串
    tag: str

    def __init__(self):
        # 止盈止损委托单ID
        self.stop_order_id = None

        # 执行状态:
        self.execute_status = None
        # 标的索引
        self.target_index = None
        # 标的名称: 'SSE.600000'
        self.code = ''
        # 止盈止损单触发时形成新的 order_id,
        # 注意: target_order_id 不是同一个值
        self.order_id = None
        # 针对已存在的目标订单ID
        self.target_order_id = None
        # 目标单成交价格（成本价）
        self.target_price = None
        # 触发时实际成交价, 注意区分(stop_price 和 stop_trailing_price)
        self.trigger_real_price = None

        self.created_time = nan
        self.updated_time = nan

        self.trigger_time = nan

        # 止损单类型: StopOrderType_Loss, StopOrderType_Profit, StopOrderType_Trailing
        self.stop_order_type = None

        # 出场
        # 止损阈值(也叫回落点, 计算触发价, 触发价 = 最高价 +/- 回落点)
        self.stop_gap = None
        # 止损阈值类型: Point, Percent
        self.stop_gap_type = None

        # 入场
        # 追踪阈值(也叫追踪点差, 计算启动价, 启动价 = 成本价 +/- 追踪点差)
        # 满足最小变动单位
        self.trailing_gap = None
        # 追踪类型: Point, Percent
        self.trailing_gap_type = None

        # 追踪启动价(启动价 = 成本价 +/- trailing_gap)
        self.trailing_price = None
        # 追踪最高价
        self.trailing_high = None
        # 追踪最低价
        self.trailing_low = None
        # 追踪止盈出场价(触发价, 计算得出的)
        self.stop_trailing_price = None
        # 止损/止盈出场价(触发价, 计算得出的)
        self.stop_price = None

        # 追踪标记位: 是否开始追踪
        self.is_begin_trailing = False
        # 是否在启动价(入场价)的 bar 位置
        self.in_begin_trailing_bar = False
        # 是否在成本价的 bar 位置
        self.in_bar_begin = False

        # 交易数量, 与 target_order_id 数量相同
        self.volume = None
        # 买卖操作标识: OrderAct_Sell, OrderAct_Buy
        # 注意: 与 target_order_id 相同方向
        self.act = None
        # 买卖价格类型: OrderCtg_Limit, OrderCtg_Market
        self.ctg = None
        # 买卖订单标识, 字符串, 通常是说明性字符串
        self.tag = None

    def update_status(self, status: int):
        self.execute_status = status


# 撤单
class DQTStopOrderInfo:
    # 止盈止损委托单ID
    stop_order_id: int
    # 标的名称: 'SSE.600000'
    code: str
    # 止盈止损单触发时形成新的 order_id,
    # 注意: target_order_id 不是同一个值
    order_id: int
    # 标的索引
    target_index: int
    # 针对已存在的目标订单ID
    target_order_id: int

    stop_point: float
    # 止损单类型: StopOrderType_Loss, StopOrderType_Profit, StopOrderType_Trailing
    stop_type: OrderStopType
    # 执行状态:
    execute_status: OrderStopExecType
    # 目标单成交价格（成本价）
    trigger_price: float
    # 目标单成交价格（成本价）
    open: float
    # 追踪启动价(启动价 = 成本价 +/- trailing_gap)
    trailing_price: float
    # 入场
    # 追踪阈值(也叫追踪点差, 计算启动价, 启动价 = 成本价 +/- 追踪点差)
    # 满足最小变动单位
    trailing_point: int
    # 入场
    # 追踪阈值(也叫追踪点差, 计算启动价, 启动价 = 成本价 +/- 追踪点差)
    # 满足最小变动单位
    trailing_high: float
    # 追踪最低价
    trailing_low: float
    # 创建 stop_order_id 时 bar 的时间
    created_time: int
    # 触发时间
    trigger_time: int

    def __init__(self) -> None:
        pass


class DQTradeBase:
    created: int
    # 标的索引
    target_index: int
    #
    order_id: int
    # 成交单 id
    trade_id: int
    # 开平标志
    position_effect: OrderPositionEffect
    # 成交量
    volume: int
    # 成交价
    price: float
    # 成交金额
    amount: float
    # 订单的委托价
    target_price: float
    # 标的类型 测试用
    target_type: TargetType
    # 买卖方向: 买/卖
    side: OrderSide
    # 买卖价格类型: OrderCtg_Limit, OrderCtg_Market
    ctg: OrderType
    # 买卖订单标识, 字符串, 通常是说明性字符串
    tag: str

    frozen_info: FrozenInfo

    def __init__(self):
        self.created = nan
        self.target_index = None
        self.order_id = None
        # 成交单 id
        self.trade_id = None
        # 开平标志
        self.position_effect = None
        # 成交量
        self.volume = None
        # 成交价
        self.price = None
        # 成交金额
        self.amount = None
        # 订单的委托价
        self.target_price = None
        # 标的类型 测试用
        self.target_type = None
        # 市价限价
        self.ctg = None
        # 订单标记
        self.tag = None
        # 买卖方向
        self.side = None
        #
        self.frozen_info = FrozenInfo()


# 普通单
class DQTBackOrder(DQTOrderBase):
    def __init__(self):
        super(DQTBackOrder, self).__init__()

    @classmethod
    def create(cls,
               target_index: int,
               code: str,
               order_id: int,
               order_price: float,
               target_type: TargetType,
               position_effect: OrderPositionEffect,
               order_status: OrderStatus,
               created_time: int,
               volume: int,
               order_ctg: OrderType,
               order_side: OrderSide):
        new_order = cls()
        new_order.target_index = target_index
        new_order.code = code
        new_order.order_id = order_id
        new_order.price = order_price
        new_order.target_type = target_type
        new_order.position_effect = position_effect
        new_order.status = order_status
        new_order.created_time = created_time
        new_order.updated_time = new_order.created_time
        new_order.volume = volume
        new_order.filled_volume = 0
        new_order.ctg = order_ctg
        new_order.side = order_side
        new_order.status = order_status
        return new_order


# 止损单
class DQTBackStopOrder(DQTStopOrderBase):
    def __init__(self):
        super(DQTBackStopOrder, self).__init__()

    @classmethod
    def create(cls,
               target_index: int,
               code: str,
               target_order_id: int,
               target_price: float,
               stop_order_id: int,
               created_time: int,
               stop_gap: float,
               stop_order_status: OrderStopExecType,
               stop_order_type: OrderStopType,
               stop_gap_type: OrderStopGapType,
               trailing_gap: int,
               trailing_gap_type: OrderStopTrailingType,
               order_act: OrderSide,
               order_type: OrderType,
               order_tag: str,
               order_volume: int):
        new_stop_order = cls()
        new_stop_order.target_index = target_index
        new_stop_order.target_order_id = target_order_id
        new_stop_order.stop_order_id = stop_order_id
        new_stop_order.target_price = target_price
        new_stop_order.stop_gap = stop_gap
        new_stop_order.stop_order_type = stop_order_type
        new_stop_order.stop_gap_type = stop_gap_type
        new_stop_order.trailing_gap = trailing_gap
        new_stop_order.trailing_gap_type = trailing_gap_type
        new_stop_order.execute_status = stop_order_status
        new_stop_order.act = order_act
        new_stop_order.ctg = order_type
        new_stop_order.tag = order_tag
        new_stop_order.volume = order_volume
        new_stop_order.code = code
        new_stop_order.created_time = created_time
        return new_stop_order


# 交易单
class DQTBackTrade(DQTradeBase):
    def __init__(self):
        super(DQTBackTrade, self).__init__()

    @classmethod
    def create(cls,
               target_index: int,
               target_type: TargetType,
               order_id: int,
               order_price: float,
               trade_id: int,
               trader_volume: int,
               trade_price: float,
               trade_amount: float,
               filled_time: int,
               order_ctg: OrderType,
               order_side: OrderSide,
               position_effect: OrderPositionEffect,
               tag: str,
               order_fee: float,
               order_margin: float):
        new_trade = cls()
        new_trade.created = filled_time
        new_trade.order_id = order_id
        new_trade.trade_id = trade_id
        new_trade.target_index = target_index
        new_trade.target_type = target_type
        new_trade.volume = trader_volume
        new_trade.target_price = order_price
        new_trade.price = trade_price
        new_trade.amount = trade_amount
        new_trade.ctg = order_ctg
        new_trade.side = order_side
        new_trade.position_effect = position_effect
        new_trade.tag = tag
        new_trade.frozen_info.set_fee(order_fee)
        new_trade.frozen_info.set_value(order_margin)
        return new_trade


# 基类单: 普通单基类, 止损单基类, 交易单记录
class SnapOrder:
    order_id: int
    # SSE.600000
    code: str
    target_index: int
    # 买卖方向: 买/卖
    side: OrderSide
    # 开平标志: 开/平/平今
    position_effect: OrderPositionEffect

    # 委托来源:
    # 0 手动下单
    # 1 策略下单
    source: int

    # 委托状态
    status: OrderStatus
    # 委托拒绝原因
    rej_reason: OrderRejectReason

    # 委托价格: 只有限价单有意义
    price: float
    # 委托量
    volume: int
    # 委托金额
    value: float
    # 已成交金额
    filled_amount: float
    # 本次订单已成交数量均价
    filled_average: float
    # 已成交的数量
    filled_volume: int
    # 委托创建时间
    created_time: int

    # 最近一次更新时间
    updated_time: int
    # 价格类型: 市价/限价
    # 委托类型:
    # 0 不明
    # 1 限价
    # 2 市价
    # 3 即时成交剩余
    # ...
    ctg: OrderType

    def __init__(self):

        self.target_index = None
        self.order_id = None
        # 标的代码, 如: SSE.600000
        self.code = None

        # 委托来源:
        # 0 手动下单
        # 1 策略下单
        self.source = 1

        # 委托状态
        self.status = None
        # 委托拒绝原因
        self.rej_reason = None

        # 委托价格: 只有限价单有意义
        self.price = 0.0
        # 委托量
        self.volume = 0
        # 委托金额
        self.value = 0.0

        # 已成交的数量
        self.filled_volume = 0
        # 本次订单已成交数量均价
        self.filled_average = 0
        # 已成交金额
        self.filled_amount = 0.0

        # 委托创建时间
        self.created_time = nan
        # 最近一次更新时间
        self.updated_time = nan
        # 开平标志: 开/平/平今
        self.position_effect = None

        # 买卖方向: 买/卖
        self.side = None
        self.ctg = None

    @classmethod
    def from_back_order(cls, order: DQTBackOrder):
        snap_order = cls()

        snap_order.order_id = order.order_id

        snap_order.code = order.code
        snap_order.target_index = order.target_index
        snap_order.side = order.side
        snap_order.position_effect = order.position_effect
        snap_order.ctg = order.ctg
        snap_order.source = order.source
        snap_order.status = order.status
        snap_order.rej_reason = order.rej_reason
        snap_order.price = 0.0 if order.ctg == OrderType.MARKET else order.price
        snap_order.volume = order.volume
        # 委托量及冻结量，在订单没有holding之前均为0
        snap_order.value = 0.0 if order.ctg == OrderType.MARKET else order.frozen_info.value
        snap_order.filled_volume = order.filled_volume
        snap_order.filled_average = order.filled_average
        snap_order.filled_amount = order.filled_amount
        snap_order.created_time = order.created_time
        snap_order.updated_time = order.updated_time

        return snap_order
