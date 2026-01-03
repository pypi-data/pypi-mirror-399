# 复权类型
from enum import IntEnum

__all__ = [
    "FQType",
    "Frequency",
    "OrderType",
    "TargetType",
    "PositionSide",
    "OrderSide",
    "OrderPositionEffect",
    "OrderStatus",
    "OrderStopExecType",
    "OrderStopType",
    "OrderStopTrailingType",
    "OrderRejectReason",
    "OrderStopGapType",
    "CashChangeReason",
    "PositionChangeReason"
]


class FQType(IntEnum):
    NA: int = 0  # 不复权
    FORWARD: int = 1  # 前复权
    BACKWARD: int = 2  # 后复权


class Frequency(IntEnum):
    # 频率
    Tick: int = 6
    Second: int = 1
    Min: int = 2
    Day: int = 3
    Week: int = 4
    Month: int = 5
    Year: int = 7


# 价格类型
# Order.type 委托类型


class OrderType(IntEnum):
    UNKNOWN = 0  # 不明
    MARKET = 1  # 市价
    LIMIT = 2  # 限价


# 标的类型


class TargetType(IntEnum):
    STOCK = 1  # 股票
    FUTURE = 2  # 期货
    OPTION = 3  # 期权
    INDEX = 4  # 期权

    @classmethod
    def to_str(value: int) -> str:
        if value == TargetType.STOCK:
            return "stock"
        if value == TargetType.FUTURE:
            return "future"
        if value == TargetType.OPTION:
            return "option"
        if value == TargetType.INDEX:
            return "index"
        return "unknown"


# Position常量
class PositionSide(IntEnum):
    # Position.side 持仓类型
    UNKNOWN = 0  # 不明
    LONG = 1  # 多头
    SHORT = 2  # 空头


# Order常量
# Order.side 委托方向
class OrderSide(IntEnum):
    UNKNOWN = 0  # 不明
    BUY = 1  # 买入
    SELL = 2  # 卖出

    @classmethod
    def to_str(value: 'OrderSide') -> str:
        if value == OrderSide.UNKNOWN:
            return "unknown"
        if value == OrderSide.BUY:
            return "buy"
        if value == OrderSide.SELL:
            return "sell"


# Order.position_effect　开平标志
class OrderPositionEffect(IntEnum):
    UNKNOWN = 0  # 不明
    OPEN = 1  # 开仓
    CLOSE = 2  # 平仓
    FORCECLOSE = 3  # 今平仓
    CLOSETODAY = 4  # 今平仓
    CLOSEYESTERDAY = 5  # 平昨仓

    @classmethod
    def to_str(value: 'OrderPositionEffect') -> str:
        if value == OrderPositionEffect.UNKNOWN:
            return "unknown"
        if value == OrderPositionEffect.OPEN:
            return "open"
        if value == OrderPositionEffect.CLOSE:
            return "close"
        if value == OrderPositionEffect.FORCECLOSE:
            return "forceclose"
        if value == OrderPositionEffect.CLOSETODAY:
            return "closetoday"
        if value == OrderPositionEffect.CLOSEYESTERDAY:
            return "closeyesterday"


#  Order.status 委托状态


class OrderStatus(IntEnum):
    UNKNOWN = 0  # 不明
    CREATED = 5  # 创建
    REPORTED = 2  # 已报
    CANCELED = 3  # 已撤销订单
    DEALED = 1  # 全部成交
    REJECTED = 4  # 已拒绝
    #
    # PENDINGCANCEL = 6  # 待撤销订单
    # PARTIALDEALED = 7  # 部分成交
    # PENDINGNEW = 8  # 待报
    # EXPIRED = 9  # 已过期
    # SUSPENDED = 10  # 挂起


class OrderStopExecType(IntEnum):
    # OrderStop.execute_type 执行汇报类型
    UNKNOWN = 0  # 未知
    HOLDING = 1  # 保持
    CANCELED = 2  # 已撤销
    PENDINGCANCEL = 3  # 待撤销
    ACTIVE = 4  # 激活
    TRAILING = 5  # 追踪中
    TRIGGER = 6  # 已触发


# OrderStop.stop_order_type 止损/止盈 跟踪止盈类型
class OrderStopType(IntEnum):
    UNKNOWN = 0
    LOSS = 1  # 止损单类型
    PROFIT = 2  # 止盈单类型
    TRAILING = 3  # 跟踪止盈单类型


# OrderStop 常量
# OrderStop.stop_type 止损类型
# OrderStop.trailing_type


class OrderStopTrailingType(IntEnum):
    UNKNOWN = 0
    POINT = 1
    PERCENT = 2


# OrderStop.trailing_type
class OrderRejectReason(IntEnum):
    UNKNOWN = 0  # 未知原因
    RISKRULECHECKFAILED = 1  # 不符合风控规则
    NOENOUGHCASH = 2  # 资金不足
    NOENOUGHPOSITION = 3  # 仓位不足
    ILLEGALACCOUNTID = 4  # 非法账户ID
    ILLEGALSTRATEGYID = 5  # 非法策略ID
    ILLEGALSYMBOL = 6  # 非法交易标的
    ILLEGALVOLUME = 7  # 非法委托量
    ILLEGALPRICE = 8  # 非法委托价
    ACCOUNTDISABLED = 9  # 账户被禁止交易
    ACCOUNTDISCONNECTED = 10  # 账户未连接
    ACCOUNTLOGGEDOUT = 11  # 账户未登录
    NOTINTRADINGSESSION = 12  # 非交易时间段
    ORDERTYPENOTSUPPORTED = 13  # 委托类型不支持
    THROTTLE = 14  # 流控限制
    MARKETDATA = 15  # 行情数据异常
    ILLEGALPOSITIONEFFECT = 16  # 非法买卖方向
    USERCANCEL = 17  # 用户取消
    LIMITTYPE = 18  # 不符合 LimitType
    MARKETORDERHOLDING = 19
    NORMAL = 20  # 正常
    DAILYBEGINCANCEL = 21  # 开盘关闭


class OrderStopGapType(IntEnum):
    UNKNOWN = 0
    POINT = 1
    PERCENT = 2


# Case常量
# 资金变动原因
# Cash.change_reason


class CashChangeReason(IntEnum):
    UNKNOWN = 0  # 不明
    TRADE = 1  # 交易
    INOUT = 2  # 出入金


# 仓位变动原因
# Position.change_reason


class PositionChangeReason(IntEnum):
    UNKNOWN = 0  # 不明
    TRADE = 1  # 交易
    LIQUIDATION = 2  # 强平
    INOUT = 3  # 出入仓
