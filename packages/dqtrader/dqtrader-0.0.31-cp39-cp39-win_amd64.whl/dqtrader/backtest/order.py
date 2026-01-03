import numpy as np
from math import isnan
from typing import List, Set
from dqtrader.account import get_account
from dqtrader.backtest.domain import calc_order_value_rb
from dqtrader.entity import DQTBackOrder, DQTBackStopOrder, DQTStopOrderInfo
from dqtrader.backtest.order_var import OrderVar
from dqtrader.strategy import get_strategy
from dqtrader.enums import OrderPositionEffect, OrderRejectReason, OrderSide, OrderStatus, OrderStopExecType, \
    OrderStopTrailingType, OrderStopType, OrderType, PositionSide, TargetType
from dqtrader.backtest_environment import get_env
from dqtrader.exception import InvalidParamWarning, NotSupportError
from dqtrader.tframe.language.chinese import text
from dqtrader.tframe.utils.exceptions import InvalidParamError


# 止盈止损单的底层下单接口, 所有对用户开放的止盈止损下单函数最终都有要调用这个函数。
# 正常返回 stop_order_id, 如果出错返回 None


def stop_order_operation(stop_order_type: OrderStopType,
                         target_index: int,
                         target_order_id: int,
                         target_price: float,
                         stop_gap: float,
                         stop_gap_type: OrderStopType,
                         # 跟踪止盈相关参数
                         trailing_gap: int,
                         trailing_gap_type: OrderStopTrailingType,
                         order_volume: int,
                         order_act: OrderSide,
                         order_type: OrderType,
                         order_tag: str) -> int | None:
    if OrderVar.exist_order(target_order_id) and target_price > 0:
        raise InvalidParamError(text.ERROR_STOP_ORDER_ID_AND_PRICE)

    strategy = get_strategy()
    env = get_env()

    stop_order_id = OrderVar.gen_order_id()
    target = strategy.target(target_index)
    stop_order_target_idx = target_index
    stop_order_act = order_act
    stop_order_volume = order_volume
    order: DQTBackOrder = OrderVar.get_order(target_order_id)

    # 针对价格止盈
    if target_price > 0:
        stop_order_status = OrderStopExecType.ACTIVE
    # 针对 order单 进行止盈
    elif order is not None:
        stop_order_status = OrderStopExecType.HOLDING
        stop_order_target_idx = order.target_index
        stop_order_act = order.side
        stop_order_volume = order.volume
    else:
        raise InvalidParamError('Internal Error')

    new_stop_order = DQTBackStopOrder.create(
        target_index=stop_order_target_idx,
        code=target,
        target_order_id=target_order_id,
        target_price=target_price,
        stop_order_id=stop_order_id,
        created_time=env.cur_bar_time(),
        stop_gap=stop_gap,
        stop_order_status=stop_order_status,
        stop_order_type=stop_order_type,
        stop_gap_type=stop_gap_type,
        trailing_gap=trailing_gap,
        trailing_gap_type=trailing_gap_type,
        order_act=stop_order_act,
        order_type=order_type,
        order_tag=order_tag,
        order_volume=stop_order_volume)

    OrderVar.append_stop_order(new_stop_order)
    OrderVar.append_unfired_stop_order(new_stop_order)

    # 跟踪止盈
    if OrderStopType.TRAILING == new_stop_order.stop_gap_type and target_price > 0:
        if order_act == OrderSide.BUY:
            if trailing_gap_type == OrderStopTrailingType.POINT:
                new_stop_order.trailing_price = target_price + trailing_gap
            elif trailing_gap_type == OrderStopTrailingType.PERCENT:
                new_stop_order.trailing_price = target_price * \
                                                (1 + trailing_gap / 100)
        elif order_act == OrderSide.SELL:
            if trailing_gap_type == OrderStopTrailingType.POINT:
                new_stop_order.trailing_price = target_price - trailing_gap
            elif trailing_gap_type == OrderStopTrailingType.PERCENT:
                new_stop_order.trailing_price = target_price * \
                                                (1 - trailing_gap / 100)

    if target_order_id is None:
        new_stop_order.in_bar_begin = True
    else:
        # 存在未撮合的订单
        # if cnt.vr.g_ATOrders.snap_attr_value_eq_count('unfilled', 'order_id', target_order_id) > 0:
        if OrderVar.is_unfilled_order(target_order_id):
            new_stop_order.in_bar_begin = False
        # elif cnt.vr.g_ATTrades.attr_value_eq('order_id', target_order_id) is not None:
        elif OrderVar.exist_order(target_order_id):
            new_stop_order.in_bar_begin = False
        else:
            # todo 输入日志
            # write_userlog(text.WARN_NOTEXIST_ORDERID, level='warn')
            new_stop_order.execute_status = OrderStopExecType.CANCELED
            OrderVar.remove_unfired_stop_order(new_stop_order.stop_order_id)
    return stop_order_id


# 检查订单是否存在
def _check_and_get_order_by_order_id(order_id: int) -> DQTBackOrder | None:
    order = OrderVar.get_order(order_id)
    if not order:
        # 输出日志
        # write_userlog(text.ERROR_ORDERID, level='warn')
        # user_warning(text.ERROR_ORDERID)
        return None
    return order


# 根据订单下止损单, 固定止损, 返回为 None 表示跟踪单无效
def stop_loss_by_order(
        target_order_id: int,
        stop_gap_type: OrderStopType,
        stop_gap: float,
        order_type: OrderType) -> int | None:
    stop_order_id = None
    # 订单不存在，忽略
    order = _check_and_get_order_by_order_id(target_order_id)
    if order is None:
        return stop_order_id

    stop_order_id = stop_order_operation(
        stop_order_type=OrderStopType.LOSS,
        target_index=order.target_index,
        target_order_id=target_order_id,
        target_price=0,
        stop_gap=stop_gap,
        stop_gap_type=stop_gap_type,
        trailing_gap=1,
        trailing_gap_type=OrderStopTrailingType.UNKNOWN,
        order_volume=0,
        order_act=OrderSide.UNKNOWN,
        order_type=order_type,
        order_tag=order.tag)
    return stop_order_id


# 根据订单下止盈单, 固定止盈, 返回为 None 表示跟踪单无效
def stop_profit_by_order(
        target_order_id: int,
        stop_gap_type: OrderStopType,
        stop_gap: float,
        order_type: OrderType):
    stop_order_id = None
    order = _check_and_get_order_by_order_id(
        target_order_id)

    if order is None:
        return stop_order_id

    stop_order_id = stop_order_operation(
        stop_order_type=OrderStopType.PROFIT,
        target_index=order.target_index,
        target_order_id=order.order_id,
        target_price=0,
        stop_gap=stop_gap,
        stop_gap_type=stop_gap_type,
        trailing_gap=1,
        trailing_gap_type=OrderStopTrailingType.UNKNOWN,
        order_volume=0,
        order_act=OrderSide.UNKNOWN,
        order_type=order_type,
        order_tag=order.tag)
    return stop_order_id


# 根据订单下跟踪止盈单, 返回为 None 表示跟踪单无效
def stop_trailing_by_order(target_order_id: int,
                           stop_gap_type: OrderStopType,
                           stop_gap: float,
                           trailing_gap: int,
                           trailing_gap_type: OrderStopTrailingType,
                           order_type: OrderType):
    stop_order_id = None
    order = _check_and_get_order_by_order_id(target_order_id)
    if order is None:
        return stop_order_id

    stop_order_id = stop_order_operation(
        stop_order_type=OrderStopType.TRAILING,
        target_index=order.target_index,
        target_order_id=order.order_id,
        target_price=0,
        stop_gap=stop_gap,
        stop_gap_type=stop_gap_type,
        trailing_gap=trailing_gap,
        trailing_gap_type=trailing_gap_type,
        order_volume=0,
        order_act=order.side,
        order_ctg=order_type,
        order_tag=order.tag)
    return stop_order_id


def stop_info(stop_order_ids: List[int]) -> List[DQTStopOrderInfo]:
    ls: List[DQTStopOrderInfo] = []

    stop_orders: list[DQTBackStopOrder] = OrderVar.batch_get_stop_order(
        stop_order_ids)
    for stop_order in stop_orders:
        stop_info = DQTStopOrderInfo()
        stop_info.stop_order_id = stop_order.stop_order_id
        stop_info.code = stop_order.code
        stop_info.order_id = stop_order.order_id
        stop_info.target_index = stop_order.target_index
        stop_info.target_order_id = stop_order.target_order_id
        stop_info.stop_point = np.abs(
            stop_order.stop_price - stop_order.target_price)
        stop_info.stop_type = stop_order.stop_order_type
        stop_info.execute_status = stop_order.execute_status
        if stop_order.stop_order_type == OrderStopType.TRAILING:
            stop_info.trigger_price = stop_order.stop_trailing_price
            stop_info.open = stop_order.target_price
            stop_info.trailing_price = stop_order.trailing_price
            stop_info.trailing_point = stop_order.trailing_gap
            stop_info.trailing_high = stop_order.trailing_high
            stop_info.trailing_low = stop_order.trailing_low
        else:
            stop_info.trigger_price = stop_order.stop_price
            stop_info.open = stop_order.target_price
            stop_info.trailing_price = np.nan
            stop_info.trailing_point = np.nan
            stop_info.trailing_high = np.nan
            stop_info.trailing_low = np.nan
        stop_info.created_time = stop_order.created_time
        stop_info.trigger_time = stop_order.trigger_time
        ls.append(stop_info)
    return ls


def stop_cancel(stop_order_ids: List[int] | Set[int]):
    env = get_env()
    update_time = env.cur_bar_time()
    stop_order_ids = set(stop_order_ids)

    for stop_order_id in stop_order_ids:
        stop_order: DQTBackStopOrder = OrderVar.get_unfired_stop_order(
            stop_order_id)
        if stop_order is None:
            continue
        stop_order.execute_status = OrderStatus.CANCELED
        stop_order.updated_time = update_time


def order_operation(
        target_index: int,
        volume: int,
        order_side: OrderSide,
        position_effect: OrderPositionEffect,
        order_type: OrderType,
        price: float) -> int:
    #

    strategy = get_strategy()
    env = get_env()
    order_id = OrderVar.gen_order_id()
    target_type = strategy.get_type(target_index)
    target = strategy.target(target_index)
    new_order = DQTBackOrder.create(
        target_index=target_index,
        code=target,
        order_id=order_id,
        order_price=price,
        target_type=target_type,
        position_effect=position_effect,
        order_status=OrderStatus.CREATED,  # 创建
        created_time=env.cur_bar_time(),
        volume=volume,
        order_ctg=order_type,
        order_side=order_side
    )
    # 添加
    OrderVar.append_order(new_order)
    new_order.value = calc_order_value_rb(new_order)
    # 添加未撮合的订单
    OrderVar.append_unfilled_order(new_order)
    return order_id


def order_volume(target_index: int, volume: int, order_side: OrderSide, position_effect: OrderPositionEffect,
                 order_type: OrderType, price: float) -> int | None:
    if order_type < OrderType.UNKNOWN:
        # todo 输出日志
        pass

    # rule: 委托类型为不为限价单时, price 应该为 0.0
    if order_type != OrderType.LIMIT and price != 0.0:
        # todo 输出日志
        price = 0.0

    # 暂时不支持平今操作
    if position_effect > OrderPositionEffect.CLOSE:
        raise InvalidParamWarning(text.ERROR_ORDER_POSITION_EFFECT)

    # 成交量判断
    if volume < 1:
        # todo 输出日志
        return None
    env = get_env()
    is_stock = env.is_stock(target_index)
    is_sell = order_side == OrderSide.SELL

    if is_stock and not is_sell and volume % 100 != 0:
        # todo 输出日志
        return None

    return order_operation(target_index, volume, order_side, position_effect, order_type, price)


# 根据标的持仓市值下单，将仓位调整到指定市值的仓位
# target_index 账户索引
# target_volume 目标手数
# side 多头 或者 空头
# order_type 价格类型
# price 价格
# 返回订单id列表
def order_target_volume(target_index: int,
                        target_volume: int,
                        side: PositionSide,
                        order_type: OrderType,
                        price: float = 0.0) -> List[int]:
    #
    order_id_list: List[int] = []
    strategy = get_strategy()
    env = get_env()
    account = get_account()
    position = account.get_position(target_index)
    #  计算目标仓位需要调整的订单

    target_type = env.get_target_type(target_index)

    if target_type == TargetType.STOCK:
        # 股票没有空头
        if side == PositionSide.SHORT:
            # logger.warning(text.ERROR_INVALID_SIDE)
            return []
    elif target_type == TargetType.FUTURE:
        # 注意 这里是平空头买平，平多头卖平
        order_side = OrderSide.BUY if side == PositionSide.LONG else OrderSide.SELL
        # 期货空头仓位
        if side == PositionSide.SHORT:
            volume = position.volume(PositionSide.LONG)
            if volume > 0:
                order_id = order_volume(
                    target_index, volume, order_side, OrderPositionEffect.CLOSE, order_type, price)
                order_id_list.append(order_id)
        else:
            # 期货多头仓位
            # 先平空头仓位
            volume = position.volume(PositionSide.SHORT)
            if volume > 0:
                order_id = order_volume(
                    target_index, volume, order_side, OrderPositionEffect.CLOSE, order_type, price)
                order_id_list.append(order_id)

    # 要下单的数量
    volume = target_volume - position.volume(side)
    if volume > 0:
        order_side = OrderSide.BUY if side == PositionSide.LONG else OrderSide.SELL
        order_id = order_volume(target_index, abs(
            volume), order_side, OrderPositionEffect.OPEN, order_type, price)
        order_id_list.append(order_id)
    elif volume < 0:
        order_side = OrderSide.SELL if side == PositionSide.LONG else OrderSide.BUY
        order_id = order_volume(target_index, abs(
            volume), order_side, OrderPositionEffect.CLOSE, order_type, price)
        order_id_list.append(order_id)
    else:
        # volume = 0 不发单
        pass
    return order_id_list


# 根据标的持仓市值下单，将仓位调整到指定市值的仓位
# target_index 账户索引
# target_value 目标价格, 要消费的钱
# side 多头 或者 空头
# order_type 价格类型
# price 价格
# 返回订单id列表
def order_target_value(
        target_index: int,
        target_value: float,
        side: OrderSide,
        order_type: OrderType,
        price: float = 0.0) -> List[int]:
    env = get_env()
    strategy = get_strategy()
    # 判断类型

    # 获取当前市价，如果是市价，则获从 行情中获取，否则为指定价格
    market_price = env.market_price(target_index) if order_type == OrderType.MARKET else price

    if isnan(market_price) or abs(market_price) < 1E-15:
        # todo 输出日志
        return []

    target_type = env.get_target_type(target_index)
    # 计算目标仓位
    if target_type == TargetType.STOCK:
        # 股票需要对100向下取整
        target_volume = target_value // (market_price *
                                         env.get_multiple(target_index)) // 100 * 100
    elif target_type == TargetType.FUTURE:
        target_volume = target_value // (market_price *
                                         env.get_multiple(target_index))
    else:
        if target_type == TargetType.INDEX:
            raise Exception(f"指数 {strategy.target(target_index)} 不能交易")
        else:
            raise Exception(f"暂不支持 {strategy.target(target_index)} 交易")

    return order_target_volume(target_index, int(target_volume), side, order_type, price)


def order_value(target_index: int,
                value: float,
                act_side: OrderSide,
                position_effect: OrderPositionEffect,
                order_type: OrderType,
                price: float = 0.0) -> List[int]:
    env = get_env()
    accont = get_account()
    strategy = get_strategy()
    market_price = env.market_price(
        target_index, accont.price_loc) if order_type == OrderType.MARKET else price

    # rule: 委托量检查
    # 下单价格检查
    if isnan(market_price):
        # user_warning(AtraderWarning(text.ERROR_DELEGATE_VOLUME))
        return None  # 市价不存在

    if abs(market_price) < 1E-8:
        # user_warning(AtraderWarning(text.ERROR_DELEGATE_VOLUME))
        return None  # 市价/限价异常，无法计算实际仓位

    target_type = env.get_target_type(target_index)

    if target_type == TargetType.STOCK:
        volume = int(value // market_price // 100 * 100)  # 订单量
    elif target_type == TargetType.FUTURE:
        multiple = env.get_multiple(target_index)
        volume = int(value // (market_price * multiple))
    else:
        if target_type == TargetType.INDEX:
            raise Exception(f"指数 {strategy.target(target_index)} 不能交易")
        else:
            raise Exception(f"暂不支持 {strategy.target(target_index)} 交易")

    return order_volume(target_index, volume, act_side, position_effect, order_type, price)


def order_percent(target_index: int,
                  percent: float,
                  act_side: OrderSide,
                  position_effect: OrderPositionEffect,
                  order_type: OrderType,
                  price: float = 0.0) -> List[int]:
    env = get_env()
    account = get_account()
    market_price = env.market_price(
        target_index, account.price_loc) if order_type == OrderType.MARKET else price

    # rule: 委托量检查
    # 下单价格检查
    if isnan(market_price):
        # user_warning(AtraderWarning(text.ERROR_DELEGATE_VOLUME))
        return None  # 市价不存在

    if abs(market_price) < 1E-15:
        # user_warning(AtraderWarning(text.ERROR_DELEGATE_VOLUME))
        return None  # 市价/限价异常，无法计算实际仓位

    value = account.valid_cash() * percent
    return order_value(target_index, value, act_side, position_effect, order_type, price)


#  根据动态市值权益下单
# :param account_idx: int 账户索引
# :param target_index: int 标的索引
# :param target_percent: float 目标动态市值权益的百分比
# :param side: int 多头 or  空头
# :param order_type: int  价格类型
# :param price: float 价格
# :return: list order_idx_list
def order_target_percent(target_index: int,
                         target_percent: float,
                         side: OrderSide | PositionSide,
                         order_type: OrderType,
                         price: float = 0.0) -> List[int]:
    env = get_env()
    account = get_account()
    strategy = get_strategy()
    market_price = env.market_price(target_index, account.price_loc) if order_type == OrderType.MARKET else price
    if isnan(market_price) or abs(market_price) < 1E-15:  # 价格异常
        # logger.warning(text.ERROR_INVALID_PRICE)
        return []

    # 计算目标动态市值权益
    # total_value = account.total_value
    order_amount = account.total_value * target_percent
    target_type = env.get_target_type(target_index)

    if target_type == TargetType.STOCK:  # 股票需要对100向下取整
        volume = order_amount // (market_price *
                                  env.get_multiple(target_index)) // 100 * 100
    elif target_type == TargetType.FUTURE:
        volume = order_amount // (market_price * env.get_multiple(target_index))
    else:
        if target_type == TargetType.INDEX:
            raise Exception(f"指数 {strategy.target(target_index)} 不能交易")
        else:
            raise Exception(f"暂不支持 {strategy.target(target_index)} 交易")
    # 计算目标仓位
    return order_target_volume(target_index, volume, side, order_type, price)


#  取消订单
def order_cancel(order_ids: List[int]):
    freeze_orders = []  # 需要释放冻结资金的订单
    order_list: List[DQTBackOrder] = OrderVar.batch_get_order(order_ids)
    env = get_env()
    account = get_account()
    cur_bar_time = env.cur_bar_time()
    for order in order_list:
        if OrderVar.is_unfilled_order(order.order_id):  # 检查订单是否处在未完全成交状态
            if order.status == OrderStatus.REPORTED:  # 报单
                freeze_orders.append(order)  # 进入holding状态的订单需要解冻冻结资金

            order.update_status(OrderStatus.CANCELED,
                                OrderRejectReason.USERCANCEL, cur_bar_time)

    account.on_order(freeze_orders)  # 释放订单冻结资金


# 清除所有未完成订单
def order_cancel_all():
    freeze_orders = []
    env = get_env()
    account = get_account()
    cur_bar_time = env.cur_bar_time()
    order_list: List[DQTBackOrder] = OrderVar.get_all_unfilled_order()
    for order in order_list:
        if order.status == OrderStatus.REPORTED:  # 报单
            freeze_orders.append(order)
        order.update_status(OrderStatus.CANCELED,
                            OrderRejectReason.USERCANCEL, cur_bar_time)

    account.on_order(freeze_orders)  # 释放订单冻结资金


# 平掉所有可平仓位
def order_close_all():
    account = get_account()
    for position in account._position.values():
        if position.type == TargetType.STOCK:
            # 平股票
            target_volume = position.volume(
                PositionSide.LONG) - position.position_available_long
            order_target_volume(position.target_index,
                                target_volume, PositionSide.LONG, OrderType.MARKET, 0.0)
        elif position.type == TargetType.FUTURE:
            # 平期货账户
            order_target_volume(position.target_index,
                                0, PositionSide.LONG, OrderType.MARKET, 0.0)


def order_info(order_ids: List[int]) -> List[DQTBackOrder]:
    return OrderVar.batch_get_order(order_ids)


# 获取当天未撮合的订单
def unfinished_orders() -> List[DQTBackOrder]:
    env = get_env()
    cur_date = env.cur_bar_time() / 1_00_00_00_000
    order_list: List[DQTBackOrder] = OrderVar.get_all_unfilled_order()
    unfinished_list = [
        order for order in order_list if order.updated_time / 1_00_00_00_000 == cur_date]
    return unfinished_list


# 获取当日所有的订单
def get_orders_by_date() -> List[DQTBackOrder]:
    env = get_env()
    cur_date = env.cur_bar_time() / 1_00_00_00_000
    order_list: List[DQTBackOrder] = OrderVar.get_all_order()
    result = [
        order for order in order_list if order.created_time / 1_00_00_00_000 == cur_date]
    return result


def last_order(target_index: int, side: OrderSide, position_effect: OrderPositionEffect):
    result = []
    order_list: List[DQTBackOrder] = OrderVar.get_all_order()

    all_zero = (side == OrderSide.UNKNOWN and position_effect ==
                OrderPositionEffect.UNKNOWN)

    for order in order_list[::-1]:
        if order.target_index != target_index:
            continue
        same_sp = (all_zero or ((side == order.side or side == OrderSide.UNKNOWN) and (
                position_effect == order.position_effect or position_effect == OrderPositionEffect.UNKNOWN)))
        if same_sp:
            result.append(order)
            break
    return result


def get_executions():
    env = get_env()
    cur_date = env.cur_bar_time() / 1_00_00_00_000
    traders = OrderVar.get_all_trade()
    result = [
        trade for trade in traders if trade.created / 1_00_00_00_000 == cur_date]
    return result


#
def last_execution(target_index: int, side: OrderSide, position_effect: OrderPositionEffect):
    result = []
    traders = OrderVar.get_all_trade()
    all_zero = (side == OrderSide.UNKNOWN and position_effect ==
                OrderPositionEffect.UNKNOWN)
    for trade in traders[::-1]:
        if trade.target_index != target_index:
            continue
        same_sp = (all_zero or ((side == trade.side or side == OrderSide.UNKNOWN) and (
                position_effect == trade.position_effect or position_effect == OrderPositionEffect.UNKNOWN)))
        if same_sp:
            result.append(trade)
            break
    return result
