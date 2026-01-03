from math import isnan
from typing import List

import dqtrader_rs
from dqtrader import log
from dqtrader.enums import OrderSide, OrderType, OrderPositionEffect, PositionSide
from dqtrader.real_environment import get_env
from dqtrader.realtrade.real_account import get_account, get_all_account
from dqtrader.strategy import get_strategy
from dqtrader.tframe.language.chinese import text

logger = log.get_logger()

def order_operation(
        account_index: int,  # 账号索引
        target_index: int,  # 标的索引
        volume: int,  # 目标里量
        order_side: OrderSide,  # 买卖
        position_effect: OrderPositionEffect,  # 持仓方向
        order_type: OrderType,  # 订单类型
        price: float):
    strategy = get_strategy()
    account = get_account(account_index)
    target = strategy.target(target_index)

    try:
        order_id = dqtrader_rs.insert_order(
            account.id,
            target,
            price,
            abs(volume),
            order_side,
            order_type,
            position_effect
        )
        return order_id
    except:
        return  0


def order_volume(
        account_index: int,  # 账号索引
        target_index: int,  # 标的索引
        volume: int,  # 目标里量
        order_side: OrderSide,  # 买卖
        position_effect: OrderPositionEffect,  # 持仓方向
        order_type: OrderType,  # 订单类型
        price: float) -> int | None:
    # if order_type <= OrderType.UNKNOWN:
    #     logger.warning(text.WARN_ORDER_TYPE_ERROR.format(order_type))

    # rule: 委托类型为不为限价单时, price 应该为 0.0
    if order_type != OrderType.LIMIT and price != 0.0:
        # logger.warning(text.WARN_NOTLIMIT_ORDER_PRICE)
        price = 0.0

    env = get_env()
    # 下单价格检查
    market_price = env.market_price(target_index, 0) if order_type == OrderType.MARKET else price
    if order_type == OrderType.LIMIT and (isnan(market_price) or abs(market_price) < 1E-15):
        # logger.warning(text.ERROR_INVALID_PRICE)
        return None  # 价格异常，为避免除零错误在此拦截
    #
    order_id = order_operation(
        account_index=account_index,
        target_index=target_index,
        volume=volume,
        order_side=order_side,
        position_effect=position_effect,
        order_type=order_type,
        price=price
    )
    return order_id


# 根据钱来下单
def order_value(
        account_index: int,  # 账号索引
        target_index: int,  # 标的索引
        value: float,  # 资金
        order_side: OrderSide,  # 买卖
        position_effect: OrderPositionEffect,  # 持仓方向
        order_type: OrderType,  # 订单类型
        price: float) -> int | None:
    env = get_env()
    strategy = get_strategy()
    market_price = env.market_price(target_index, 0) if order_type == OrderType.MARKET else price
    if isnan(market_price) or abs(market_price) < 1E-15:
        # logger.warning(text.ERROR_INVALID_PRICE)
        return None  # 价格异常，为避免除零错误在此拦截

    if strategy.is_stock(target_index):
        volume = int(value // market_price // 100 * 100)  # 订单量
    elif strategy.is_future(target_index):
        volume = int(value // (market_price * env.get_multiple(target_index)))  # 订单量
    else:
        target = strategy.target(target_index)
        # logger.warning(text.ERROR_NOT_SUPPORT_TAGERTTYPE.format(TARGET=target))
        return None

    order_id = order_operation(
        account_index=account_index,
        target_index=target_index,
        volume=volume,
        order_side=order_side,
        position_effect=position_effect,
        order_type=order_type,
        price=price
    )
    return order_id


def order_percent(
        account_index: int,  # 账号索引
        target_index: int,  # 标的索引
        percent: float,  # 百分比
        order_side: OrderSide,  # 买卖
        position_effect: OrderPositionEffect,  # 持仓方向
        order_type: OrderType,  # 订单类型
        price: float) -> int | None:

    env = get_env()
    market_price = env.market_price(target_index, 0) if order_type == OrderType.MARKET else price
    if isnan(market_price) or abs(market_price) < 1E-15:
        # logger.warning(text.ERROR_INVALID_PRICE)
        return None  # 价格异常，为避免除零错误在此拦截
    account = get_account(account_index)
    value = account.valid_cash * percent
    order_id = order_value(account_index, target_index, value, order_side, position_effect, order_type, price)
    return order_id


def order_target_volume(
        account_index: int,
        target_index: int,
        target_volume: int,
        position_side: PositionSide,
        order_type: OrderType,
        price: float = 0.0) -> List[int]:

    order_ids = []
    account = get_account(account_index)
    strategy = get_strategy()
    available_long = account.available_long(target_index)
    available_short = account.available_short(target_index)
    volume_long = account.volume_long(target_index)
    volume_short = account.volume_short(target_index)
    # rule：计算目标仓位需要调整的订单
    if strategy.is_stock(target_index):
        # 股票没有空头,给出警告，但是还会继续下单
        if position_side == PositionSide.SHORT:
            # logger.warning(text.ERROR_INVALID_SIDE)
            # 先平多头仓位
            if available_long > 0:
                order_id = order_operation(
                    account_index=account_index,
                    target_index=target_index,
                    volume=available_long,
                    order_side=OrderSide.SELL,
                    position_effect=OrderPositionEffect.CLOSE,
                    order_type=order_type,
                    price=price)
                order_ids.append(order_id)
    elif strategy.is_future(target_index):
        # 注：这里就是防止双边，当前工具箱都不支持双边
        # 注意 这里是平空头买平，平多头卖平
        # order_side = OrderSide.BUY if position_side == PositionSide.LONG else OrderSide.SELL
        if position_side == PositionSide.SHORT:  # 期货空头仓位
            # 先平多头仓位
            if available_long > 0:
                order_id = order_operation(
                    account_index=account_index,
                    target_index=target_index,
                    volume=available_long,
                    order_side=OrderSide.SELL,
                    position_effect=OrderPositionEffect.CLOSE,
                    order_type=order_type,
                    price=price
                )
                order_ids.append(order_id)
        else:  # 期货多头仓位
            # 先平空头仓位
            if available_short > 0:
                order_id = order_operation(
                    account_index=account_index,
                    target_index=target_index,
                    volume=available_short,
                    order_side=OrderSide.BUY,
                    position_effect=OrderPositionEffect.CLOSE,
                    order_type=order_type,
                    price=price
                )
                order_ids.append(order_id)

    #
    volume = target_volume - volume_long if position_side == PositionSide.LONG else target_volume - volume_short
    if volume > 0:
        order_side = OrderSide.BUY if position_side == PositionSide.LONG else OrderSide.SELL
        order_id = order_operation(
            account_index=account_index,
            target_index=target_index,
            volume=volume,
            order_side=order_side,
            position_effect=OrderPositionEffect.OPEN,
            order_type=order_type,
            price=price
        )
        order_ids.append(order_id)
    elif volume < 0:
        order_side = OrderSide.SELL if position_side == PositionSide.LONG else OrderSide.BUY
        order_id = order_operation(
            account_index=account_index,
            target_index=target_index,
            volume=volume,
            order_side=order_side,
            position_effect=OrderPositionEffect.CLOSE,
            order_type=order_type,
            price=price
        )
        order_ids.append(order_id)
    return order_ids


def order_target_value(
        account_index: int,
        target_index: int,
        target_value: float,
        side: OrderSide | PositionSide,
        order_type: OrderType,
        price: float = 0.0) -> List[int]:
    strategy = get_strategy()
    env = get_env()
    # 如果是市价，则获取，不是则用指定价格
    market_price = env.market_price(target_index, 0) if order_type == OrderType.MARKET else price
    #
    if isnan(market_price) or abs(market_price) < 1E-15:
        # logger.warning(text.ERROR_INVALID_PRICE)
        return []

    # 计算目标仓位
    if strategy.is_stock(target_index):
        # 股票需要对100向下取整
        target_volume = target_value // (market_price * env.get_multiple(target_index)) // 100 * 100
    elif strategy.is_future(target_index):
        target_volume = target_value // (market_price * env.get_multiple(target_index))
    else:
        raise NotImplementedError
    return order_target_volume(account_index, target_index, int(target_volume), side, order_type, price)


def order_target_percent(
        account_index: int,
        target_index: int,
        target_percent: float,
        side: OrderSide | PositionSide,
        order_type: OrderType,
        price: float = 0.0):
    env = get_env()
    strategy = get_strategy()
    account = get_account(account_index)
    market_price = env.market_price(target_index, 0) if order_type == OrderType.MARKET else price
    if isnan(market_price) or abs(market_price) < 1E-15:
        # logger.warning(text.ERROR_INVALID_PRICE)
        return []
    # 使用动态权益，进行
    order_amount = account.dynamic_equity * target_percent
    if strategy.is_stock(target_index):
        # 股票需要对100向下取整
        volume = order_amount // (market_price * env.get_multiple(target_index)) // 100 * 100
    elif strategy.is_future(target_index):
        volume = order_amount // (market_price * env.get_multiple(target_index))
    else:
        target = strategy.target(target_index)
        # logger.warning(text.ERROR_NOT_SUPPORT_TAGERTTYPE.format(TARGET=target))
        return []

    order_ids = order_target_volume(account_index=account_index, target_index=target_index, target_volume=volume,
                                    position_side=side, order_type=order_type, price=price)
    return order_ids


def order_close_all():
    order_ids = []
    accounts = get_all_account()
    strategy = get_strategy()
    for index, account in enumerate(accounts):
        positions = account.get_all_position()
        for target, dir_dict in positions.items():
            target_index = strategy.target_index(target)
            #
            for position_dir, position in dir_dict.items():
                #  获取可平量
                if position_dir == PositionSide.SHORT:
                    sub_order_ids = order_target_volume(
                        account_index=index,
                        target_index=target_index,
                        target_volume=0,
                        position_side=PositionSide.LONG,
                        order_type=OrderType.MARKET,
                        price=0.0
                    )
                    order_ids.extend(sub_order_ids)
                elif position_dir == PositionSide.LONG:
                    sub_order_ids = order_target_volume(
                        account_index=index,
                        target_index=target_index,
                        target_volume=0,
                        position_side=PositionSide.SHORT,
                        order_type=OrderType.MARKET,
                        price=0.0
                    )
                    order_ids.extend(sub_order_ids)
    return order_ids


def order_cancel(order_ids: List[int]):
    accounts = get_all_account()
    for order_id in order_ids:
        for account in accounts:
            if account.has_order(order_id):
                try:
                    dqtrader_rs.cancel_order(account.id, order_id)
                except:
                    pass


def order_cancel_all(account_indexs):
    for account_index in account_indexs:
        account = get_account(account_index)
        orders = account.get_all_order()
        for order in orders:
            if order.order_status != 2:
                continue
            dqtrader_rs.cancel_order(account.id, order.client_order_id)
