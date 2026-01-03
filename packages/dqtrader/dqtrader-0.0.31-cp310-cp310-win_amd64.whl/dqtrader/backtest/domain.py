from decimal import Decimal
import itertools
from math import isnan
import dqtrader_rs
import numpy as np
from typing import List
from dqtrader.account import get_account
from dqtrader.entity import DQTBackOrder, DQTBackStopOrder, DQTBackTrade, SnapOrder

from dqtrader.backtest.order_var import OrderVar
from dqtrader.decorator import measure_time
from dqtrader.strategy import get_strategy
from dqtrader.enums import Frequency, OrderPositionEffect, OrderRejectReason, OrderSide, OrderStatus, OrderStopExecType, OrderStopGapType, OrderStopTrailingType, OrderStopType, OrderType, TargetType
from dqtrader.backtest_environment import Environment, get_env
from dqtrader.exception import raise_bultin_error


# 更新股票总金额和手续费
def _update_order_stock_frozen(orders: List[DQTBackOrder]) -> tuple[List[float], List[float]]:
    env = get_env()
    stock_fee_rate = env.cost_fee_rate(TargetType.STOCK)
    account = get_account()
    stock_commission_rate = account.stock_commission_rate

    for order in orders:
        fee = 0

        # 计算印花税
        if order.position_effect == OrderPositionEffect.OPEN:
            fee = (order.price * order.volume) * stock_commission_rate.open_tax
        elif order.position_effect == OrderPositionEffect.CLOSE:
            fee = (order.price * order.volume) * \
                stock_commission_rate.close_tax
        else:
            # 暂时只支持开平标志
            raise_bultin_error('offsetflag')
        # 计算过户费
        fee += (order.price * order.volume) * stock_commission_rate.trans_fee
        # 股票手续费
        trade_fee = (order.price * order.volume) * stock_fee_rate

        # 佣金最低不低于5
        fee += max(trade_fee, stock_commission_rate.min_trade_fee)
        #
        value = order.price * order.volume

        order.frozen_info.set_value(value)
        order.frozen_info.set_fee(fee)

    return [order.frozen_info.value for order in orders], [order.frozen_info.fee for order in orders]


# 订单处理部分
def calc_order_value_rb(order: DQTBackOrder):
    if order.ctg == OrderType.MARKET:
        delegate_value = 0
    else:
        env = get_env()
        strategy = get_strategy()
        account = get_account()
        delegate_value = order.price * order.volume * \
            env.get_multiple(order.target_index) * \
            account.get_margin_rate(order.target_index, order.side)

        # 委托金额 = 委托量*委托价格*合约乘数
        # 股票买入 = 委托金额+手续费
        # 股票卖出 = 委托金额-手续费
        if strategy.is_stock(order.target_index):
            _update_order_stock_frozen([order])
            if order.position_effect == OrderSide.SELL:
                delegate_value -= order.frozen_info.fee
            elif order.position_effect == OrderSide.BUY:
                delegate_value += order.frozen_info.fee

    return delegate_value

# 删除没有成交的订单


def clear_unfilled_order(bar_date: int):
    # 删除指定日期的时间
    order_list = OrderVar.get_all_unfilled_order()
    env = get_env()
    cur_bar_time = env.cur_bar_time()
    # todo 这里要考虑夜盘，交易日
    for order in order_list:
        created_date = order.created_time / 1_00_00_00_000
        # 将前一天的订单，全部取消
        if created_date == bar_date:
            continue
        order.update_status(OrderStatus.CANCELED,
                            OrderRejectReason.DAILYBEGINCANCEL, cur_bar_time)


def _update_stop_order_status(stop_orders: List[DQTBackStopOrder], execute_status: OrderStopExecType):
    for stop_order in stop_orders:
        stop_order.execute_status = execute_status


# 设置止损单的成本价
# :param target_order_id: int, 目标单的 id
# :param trade_price: 目标单成交的价格
def _set_stop_order_target_price(target_order_id: int, trade_price: float):
    # 不存在
    if OrderVar.exist_unfilled_order():
        return
    unfired_stop_orders = OrderVar.get_all_unfired_stop_order()
    #
    order_ids = [
        stop_order.target_order_id for stop_order in unfired_stop_orders]
    stop_order_pos_s = np.where(
        np.array([target_order_id]) == np.array(order_ids))[0]
    if stop_order_pos_s.size < 1:
        return

    unfired_stop_orders: List[DQTBackStopOrder] = OrderVar.batch_get_unfired_stop_order(
        stop_order_pos_s)

    for stop_order in unfired_stop_orders:
        if stop_order.execute_status != OrderStopExecType.HOLDING:
            continue
        stop_order.in_bar_begin = False
        stop_order.target_price = trade_price
        stop_order.trailing_high = trade_price
        stop_order.trailing_low = trade_price
        # 目标单成交后的状态止损单改为激活状态 bug2318
        _update_stop_order_status([stop_order], OrderStopExecType.ACTIVE)

        stop_order_act = stop_order.act
        stop_gap_type = stop_order.stop_gap_type
        stop_order_type = stop_order.stop_order_type
        trailing_gap_type = stop_order.trailing_gap_type
        gap_direction = -1
        temp_price = 0

        if stop_order_type == OrderStopType.LOSS:
            if stop_order_act == OrderSide.BUY:
                gap_direction = -1
            elif stop_order_act == OrderSide.SELL:
                gap_direction = 1
            else:
                raise_bultin_error('orderact')
            if stop_gap_type == OrderStopGapType.POINT:
                temp_price = trade_price + gap_direction * stop_order.stop_gap
            elif stop_gap_type == OrderStopGapType.PERCENT:
                temp_price = trade_price * \
                    (1 + gap_direction * stop_order.stop_gap / 100)
            else:
                raise_bultin_error('stopgap')
            stop_order.trigger_real_price = stop_order.stop_price = temp_price
        elif stop_order_type == OrderStopType.PROFIT:
            if stop_order_act == OrderSide.BUY:
                gap_direction = 1
            elif stop_order_act == OrderSide.SELL:
                gap_direction = -1
            else:
                raise_bultin_error('orderact')

            if stop_gap_type == OrderStopGapType.POINT:
                temp_price = trade_price + gap_direction * stop_order.stop_gap
            elif stop_gap_type == OrderStopGapType.PERCENT:
                temp_price = trade_price * \
                    (1 + gap_direction * stop_order.stop_gap / 100)
            else:
                raise_bultin_error('stopgap')
            stop_order.trigger_real_price = stop_order.stop_price = temp_price
        elif stop_order_type == OrderStopType.TRAILING:
            if stop_order_act == OrderSide.BUY:
                gap_direction = 1
            elif stop_order_act == OrderSide.SELL:
                gap_direction = -1
            else:
                raise_bultin_error('orderact')

            if trailing_gap_type == OrderStopTrailingType.POINT:
                temp_price = trade_price + gap_direction * stop_order.trailing_gap
            elif trailing_gap_type == OrderStopTrailingType.PERCENT:
                temp_price = trade_price * \
                    (1 + gap_direction * stop_order.trailing_gap / 100)
            else:
                raise_bultin_error('stopgap')
            stop_order.trailing_price = temp_price
        else:
            raise_bultin_error('stopordertype')


def _cancelled_stop_order_by_target_order_id(order_denied_canceled_ids: List[int]):
    if len(order_denied_canceled_ids) > 0 and OrderVar.exist_unfired_order():

        for target_order_id in order_denied_canceled_ids:
            same_target_stop_orders: List[DQTBackStopOrder] = OrderVar.get_unfired_stop_order_by_target_id(
                target_order_id)
            if len(same_target_stop_order) == 0:
                continue

            for same_target_stop_order in same_target_stop_orders:
                same_target_stop_order.execute_status = OrderStopExecType.CANCELED
            # 删除所有的未触发的停止订单
            # 这里存疑，为什么要删除
            OrderVar.clear_all_unfired_stop_order()


# 更新在 on_data 逻辑中下 stop 单时 stop_order 的状态
# 下止损单时, 目标单可能处于3种终结状态: 成交状态/拒绝状态/撤销状态
def _update_unfired_stop_order_status_if_holding_status():
    unfired_stop_orders = OrderVar.get_all_unfired_stop_order()
    target_order_ids = [
        stop_order.target_order_id for stop_order in unfired_stop_orders]
    orders: List[DQTBackOrder] = OrderVar.batch_get_order(target_order_ids)
    order_denied_canceled_ids: List[int] = []
    for stop_order, order in zip(unfired_stop_orders, orders):
        if stop_order.execute_status != OrderStatus.REPORTED:
            continue
        if order.status == OrderStatus.DEALED:
            _set_stop_order_target_price(order.order_id, order.filled_average)
        elif order.status in (OrderStatus.CANCELED, OrderStatus.REJECTED):
            order_denied_canceled_ids.append(order.order_id)
    _cancelled_stop_order_by_target_order_id(order_denied_canceled_ids)


# def _back_test_call_on_order_status(order:DQTBackOrder):
#     call_order_status_wrapper = smm.enter_phase(gv.RUMMODE_PHASE_DEAL_TRADE)(cnt.vr.g_ATraderInputInfo.on_order_status_func)

#     snap_order = convert_back_order_to_snap_order(order,
#                                                   cnt.vr.g_ATraderInputInfo.AccountNameList,
#                                                   cnt.vr.g_ATraderInputInfo.TargetList)
#     call_order_status_wrapper(cnt.vr.g_ATraderUserContext, snap_order)


# """
# 根据订单状态转换线路选择调用on_order
# 不需要调用on_order:
#     preholding -> deny
#     preholding -> cancel
#     holding -> filled
# 需要调用on_order:
#     preholding -> holding
#     holding -> deny
#     holding -> cancel
# :param order:
# :param status_s:
# :param status_idx:
# :param order_status:
# :param rej_reason:
# :param update_time:
# :return:
# """
def _update_order_status(order: DQTBackOrder,
                         order_status: OrderStatus,
                         rej_reason: OrderRejectReason,
                         update_time: int):

    env = get_env()
    account = get_account()
    if order.status == OrderStatus.CREATED and order_status == OrderStatus.REPORTED:
        order.update_status(order_status, rej_reason, update_time)
        account.on_order([order])
    elif order.status == OrderStatus.REPORTED and order_status in (OrderStatus.CANCELED, OrderStatus.REJECTED):
        order.update_status(order_status, rej_reason, update_time)
        account.on_order([order])
    else:
        order.update_status(order_status, rej_reason, update_time)
    # status_s[status_idx] = order_status
    # 订单状态变化回调 策略中回调
    if env.on_order_status is not None:
        env.on_order_status(SnapOrder.from_back_order(order))
    # _back_test_call_on_order_status(order)


# 计算需要冻结的保证金以及手续费
# :param orders: list of ATOrder object
# :return: margin_frozen, fee_frozen
def _update_order_future_frozen(orders: List[DQTBackOrder]) -> tuple[List[float], List[float]]:

    # 保证金率
    env = get_env()

    account = get_account()

    margin_frozen_list: List[float] = []
    fee_frozen_list: List[float] = []
    for order in orders:
        multiple = env.get_multiple(order.target_index)
        margin_rate = 1.0
        if order.side == OrderSide.SELL:
            margin_rate = account.get_short_margin(order.target_index)
        elif order.side == OrderSide.BUY:
            margin_rate = account.get_long_margin(order.target_index)

        # 价格 * 剩余成交量 * 合约乘数 * 保证金率
        margin_frozen = order.price * order.unfilled_volume * multiple * margin_rate
        margin_frozen_list.append(margin_frozen)
        target_info = env.get_target_info(order.target_index)
        trade_fee = 0.0
        if order.position_effect == OrderPositionEffect.OPEN:
            trade_fee = target_info.trading_fee_open
        elif order.position_effect == OrderPositionEffect.CLOSE:
            trade_fee = target_info.trading_fee_close
        else:
            trade_fee = target_info.trading_fee_close_today

        fee_frozen = trade_fee * order.price * order.unfilled_volume * multiple
        fee_frozen_list.append(fee_frozen)
        order.frozen_info.set_value(margin_frozen)
        order.frozen_info.set_fee(fee_frozen)

    return margin_frozen_list, fee_frozen_list


# 计算 order 单 保证金/手续费
def _update_order_frozen(orders: List[DQTBackOrder]) -> tuple[List[float], List[float]]:
    futures_orders = [
        order for order in orders if order.target_type == TargetType.FUTURE]
    stocks_orders = [
        order for order in orders if order.target_type == TargetType.STOCK]
    if futures_orders:
        _update_order_future_frozen(futures_orders)
    if stocks_orders:
        _update_order_stock_frozen(stocks_orders)

    return [order.frozen_info.value for order in orders], [order.frozen_info.fee for order in orders]


# 创建一个成交单
def _create_a_trader(order: DQTBackOrder, order_price: float, trader_volume: int, trade_price: float, filled_time: int) -> DQTBackTrade:
    account = get_account()
    env = get_env()
    min_move = env.get_minmove(order.target_index)
    
    trade_price = float(Decimal(str(trade_price)) -
                        Decimal(str(trade_price)) % Decimal(str(min_move)))
    
    order_price = float(Decimal(str(order_price)) -
                        Decimal(str(order_price)) % Decimal(str(min_move)))
    new_volume = order.filled_volume + trader_volume
    assert new_volume <= order.volume
    order.price = order_price
    order.updated_time = filled_time
    # 计算成交金额
    order.filled_amount += trade_price * trader_volume * env.get_multiple(
        order.target_index) * account.get_margin_rate(order.target_index, order.side)
    # 计算成交均价
    order.filled_average = trade_price
    order.filled_volume = new_volume

    if order.unfilled_volume == 0:
        order.status = OrderStatus.DEALED

    new_trade = DQTBackTrade.create(
        target_index=order.target_index,
        target_type=order.target_type,
        order_id=order.order_id,
        order_price=order_price,
        trade_id=OrderVar.gen_order_id(),
        trader_volume=trader_volume,
        trade_price=trade_price,
        trade_amount=order.filled_amount,
        filled_time=filled_time,
        order_ctg=order.ctg,
        order_side=order.side,
        position_effect=order.position_effect,
        tag=order.tag,
        order_fee=order.frozen_info.fee,
        order_margin=order.frozen_info.value
    )
    OrderVar.append_trade(new_trade)
    # 重置手续费和保证金
    order.frozen_info.set_value(0)
    order.frozen_info.set_fee(0)
    return new_trade


# 计算成交单
# 计算需要冻结的保证金以及手续费
# :param traders: list of ATBackOrder object
# :return: margin_frozen, fee_frozen
def _update_trader_future_frozen(trades: List[DQTBackTrade]) -> tuple[List[float], List[float]]:
    env = get_env()
    account = get_account()
    margin_frozen_list: List[float] = []
    fee_frozen_list: List[float] = []
    for trade in trades:
        multiple = env.get_multiple(trade.target_index)
        margin_rate = 1.0
        if trade.side == OrderSide.SELL:
            margin_rate = account.get_short_margin(trade.target_index)
        elif trade.side == OrderSide.BUY:
            margin_rate = account.get_long_margin(trade.target_index)

        # 价格 * 剩余成交量 * 合约乘数 * 保证金率
        margin_frozen = 0.0
        if trade.position_effect == OrderPositionEffect.OPEN:
            margin_frozen = trade.price * trade.volume * multiple * margin_rate
        elif trade.position_effect == OrderPositionEffect.CLOSE:
            margin_frozen = 0.0

        margin_frozen_list.append(margin_frozen)
        target_info = env.get_target_info(trade.target_index)
        # trade_fee = 0.0
        if trade.position_effect == OrderPositionEffect.OPEN:
            trade_fee = target_info.trading_fee_open
        elif trade.position_effect == OrderPositionEffect.CLOSE:
            trade_fee = target_info.trading_fee_close
        else:
            trade_fee = target_info.trading_fee_close_today

        fee_frozen = trade_fee * trade.price * trade.volume * multiple
        fee_frozen_list.append(fee_frozen)

        trade.frozen_info.set_trader_value(margin_frozen)
        trade.frozen_info.set_trader_fee(fee_frozen)
    return margin_frozen_list, fee_frozen_list


# 更新股票总金额和手续费
def _update_trader_stock_frozen(trades: List[DQTBackTrade]):
    env = get_env()
    fee_rate = env.cost_fee_rate(TargetType.STOCK)
    account = get_account()
    stock_commission_rate = account.stock_commission_rate
    for trade in trades:
        if trade.position_effect not in (OrderPositionEffect.CLOSE, OrderPositionEffect.OPEN):
            raise_bultin_error('offsetflag')

        if trade.position_effect == OrderPositionEffect.OPEN:
            fee = (trade.price * trade.volume) * stock_commission_rate.open_tax
        else:
            fee = (trade.price * trade.volume) * \
                stock_commission_rate.close_tax

        # 计算过户费
        fee += (trade.price * trade.volume) * stock_commission_rate.trans_fee
        trade_fee = (trade.price * trade.volume) * fee_rate

        # 佣金最低不低于5
        fee += max(trade_fee, stock_commission_rate.min_trade_fee)
        value = trade.price * trade.volume

        trade.frozen_info.set_trader_value(value)
        trade.frozen_info.set_trader_fee(fee)
    return [trader.frozen_info.trader_value for trader in trades], [trader.frozen_info.trader_fee for trader in
                                                                    trades]

# 计算 trader 单 保证金/手续费


def _update_trader_frozen(trades: List[DQTBackTrade]) -> tuple[List[float], List[float]]:
    future_trades = []
    stock_trades = []
    for trade in trades:
        if trade.target_type == TargetType.FUTURE:
            future_trades.append(trade)
        elif trade.target_type == TargetType.STOCK:
            stock_trades.append(trade)

    if len(future_trades) > 0:
        _update_trader_future_frozen(future_trades)

    if len(stock_trades) > 0:
        _update_trader_stock_frozen(stock_trades)

    return [trader.frozen_info.trader_value for trader in trades], [trader.frozen_info.trader_fee for trader in
                                                                    trades]


# 模拟券商的功能，冻结保证金，手续费，多空仓位等等，
# 模拟交易所的功能，根据下单的价格是否在当前bar的最高价和最低价之间进行判断是否进行交易
# :param order_ids: 订单号
# :param bar_highs: 高
# :param bar_lows:  低
# :param bar_opens: 开
# :param bar_vols:成交量
# :param target_price_assign:
# :param filled_time_assign:
# :return: numpy.ndarry
def _transaction_order(order_ids: List[int],
                       bar_highs: List[float],
                       bar_lows:  List[float],
                       bar_opens:  List[float],
                       bar_vols: List[int],
                       target_price_assign: List[float],
                       filled_time_assign: List[int],
                       ) -> np.ndarray[np.int32]:
    # print(f"_transaction_order====+++: {len(order_ids)}")
    orders: List[DQTBackOrder] = OrderVar.batch_get_order(order_ids)
    # 市价单时, pirce 为 0, 并且状态为 CREATED , 要将订单的价格设置为当前 bar 的价格
    # print(f"order_ids = {len(order_ids)}, orders = {len(orders)}, bar_highs = {len(bar_highs)}, bar_lows = {len(bar_lows)},bar_opens = {len(bar_opens)}, bar_vols = {len(bar_vols)}")
    for i, order in enumerate(orders):
        if order.status != OrderStatus.CREATED:
            continue
        if order.price == 0.0:
            order.price = bar_opens[i]

    env = get_env()
    account = get_account()
    margin_frozen, fee_frozen = _update_order_frozen(orders)

    cur_bar_time = env.cur_bar_time()

    for i, order in enumerate(orders):
        bar_high = bar_highs[i]
        bar_low = bar_lows[i]
        bar_open = bar_opens[i]
        bar_volume = bar_vols[i]
        trade_price = 0
        order_price = order.price
        positions = account.get_position(order.target_index)
        # True, 下一根bar没有开盘价时 order 单 不取消
        is_not_market_order_holding = not env.market_order_holding and order.ctg == OrderType.MARKET

        if order.status in (OrderStatus.CANCELED, OrderStatus.REJECTED):
            continue

        if len(target_price_assign) > 0:
            target_price = target_price_assign[i]
            filled_time = filled_time_assign[i]
        else:
            target_price = np.nan
            filled_time = env.get_filled_time(order.target_index, cur_bar_time)

        if isnan(bar_open) or bar_open < 1E-10 or bar_volume < 1:
            #
            if is_not_market_order_holding:
                _update_order_status(order, OrderStatus.CANCELED,
                                     OrderRejectReason.MARKETORDERHOLDING, filled_time)
            continue

        #################################
        # order 单状态转换

        if order.status == OrderStatus.CREATED:
            if isnan(bar_open) or bar_open < 1E-10:
                _update_order_status(
                    order, OrderStatus.REJECTED, OrderRejectReason.NOTINTRADINGSESSION, filled_time)
                continue

            # 涨跌停价形成的委托单以挂单的形式存放
            # 涨停不能买入
            if order.side == OrderSide.BUY and order.position_effect in (OrderPositionEffect.OPEN, OrderPositionEffect.CLOSE) and env.at_limit_up_price(order.target_index):
                _update_order_status(
                    order, OrderStatus.CREATED, np.nan, filled_time)
                continue

            # 跌停不能卖出
            if order.side == OrderSide.SELL and order.position_effect in (OrderPositionEffect.OPEN, OrderPositionEffect.CLOSE) and env.at_limit_down_price(order.target_index):
                _update_order_status(
                    order, OrderStatus.CREATED, np.nan, filled_time)
                continue

            if 2e9 < order.unfilled_volume:
                _update_order_status(
                    order, OrderStatus.REJECTED, OrderRejectReason.ILLEGALVOLUME, filled_time)
               
                continue

            if order.target_type == TargetType.STOCK and order.position_effect == OrderPositionEffect.OPEN and order.unfilled_volume % 100 != 0:
                _update_order_status(
                    order, OrderStatus.REJECTED, OrderRejectReason.ILLEGALVOLUME, filled_time)
                continue

            if order.position_effect == OrderPositionEffect.OPEN:
                # 保证金不足
                _valid_cash = account.valid_cash(filled_time)

                if _valid_cash <= (margin_frozen[i] + fee_frozen[i]):
                    # print("拒单=====")
                    _update_order_status(
                        order, OrderStatus.REJECTED, OrderRejectReason.NOENOUGHCASH, filled_time)
                    # todo 输入日志 记录这种情况
                    # write_userlog('保证金不足: order_id=%d, order_volume=%d, order_price=%.2f, valid_cash=%.2f, margin_frozen=%.2f, fee_frozen=%.2f' % (
                    #     order.order_id, order.volume, order.price, _valid_cash, margin_frozen[i], fee_frozen[i]))
 
                    continue
            elif order.position_effect == OrderPositionEffect.CLOSE:
                if order.side == OrderSide.BUY and positions.position_available_short < order.unfilled_volume:
                    _update_order_status(
                        order, OrderStatus.REJECTED, OrderRejectReason.NOENOUGHPOSITION, filled_time)
                    continue

                if order.side == OrderSide.SELL:
                    if positions is None or positions.position_available_long < order.unfilled_volume:
                        _update_order_status(
                            order, OrderStatus.REJECTED, OrderRejectReason.NOENOUGHPOSITION, filled_time)
                        continue
            else:
                raise_bultin_error('offsetflag')

            _update_order_status(
                order, OrderStatus.REPORTED, float('nan'), filled_time)

        #################################
        # 计算 order 单的价格和成交价格

        if order.ctg == OrderType.LIMIT:
            # 价格在 bar 的最低价与最高价之内
            if bar_low <= order_price <= bar_high:
                trade_price = order_price
            # 价格在 bar 的最低价与最高价之外
            elif (order.side == OrderSide.SELL and order_price < bar_low) or (
                    order.side == OrderSide.BUY and order_price > bar_high):
                trade_price = bar_open
            # 价格都不在范围类
            elif env.limit_type:
                _update_order_status(
                    order, OrderStatus.CANCELED, OrderRejectReason.LIMITTYPE, filled_time)
                continue
        elif order.ctg == OrderType.MARKET:
            if isnan(target_price):
                if account.price_loc == 1:
                    # 在上一根 bar 创建订单之后，会在处理下一根 bar 处理. 取下单时的下一个 bar 开盘价
                    order_price = bar_open
                elif account.price_loc == 0:
                    # 下单时 bar 收盘价
                    order_price = env.market_price(order.target_index, -1)
                else:
                    order_price = bar_open
                if order.side == OrderSide.SELL:
                    trade_price = order_price - account.slide_price * \
                        env.get_minmove(order.target_index)
                elif order.side == OrderSide.BUY:
                    trade_price = order_price + account.slide_price * \
                        env.get_minmove(order.target_index)
                else:
                    raise_bultin_error('orderact')
            else:
                trade_price = order_price = target_price
        else:
            raise_bultin_error('orderctg')

        #################################

        if trade_price <= 0:
            continue
        #################################
        # 调整仓位和均价
        new_trade = _create_a_trader(order, order_price, order.unfilled_volume, trade_price, filled_time)
        
        _update_order_status(order,  order.status, OrderRejectReason.UNKNOWN, filled_time)

        # 回报回调
        if env.on_order_execution is not None:
            env.on_order_execution(new_trade)
        # 重新计算费用
        _update_trader_frozen([new_trade])
        account.on_trade([new_trade])

        #################################
        # 更新止损单信息
        _set_stop_order_target_price(order.order_id, trade_price)
    return np.array([order.status for order in orders])


def _update_stop_trailing_order_trigger_price(stop_order: DQTBackStopOrder, target_price: float):
    if stop_order.act == OrderSide.BUY:
        if stop_order.stop_gap_type == OrderStopGapType.POINT:
            stop_order.stop_trailing_price = stop_order.trailing_high - stop_order.stop_gap
        elif stop_order.stop_gap_type == OrderStopGapType.PERCENT:
            price = stop_order.trailing_high - \
                (stop_order.trailing_high - target_price) * \
                stop_order.stop_gap / 100
            stop_order.stop_trailing_price = price
        else:
            raise_bultin_error('stopgap')
    elif stop_order.act == OrderSide.SELL:
        if stop_order.stop_gap_type == OrderStopGapType.POINT:
            stop_order.stop_trailing_price = stop_order.trailing_low + stop_order.stop_gap
        elif stop_order.stop_gap_type == OrderStopGapType.PERCENT:
            price = stop_order.trailing_low + \
                (target_price - stop_order.trailing_low) * \
                stop_order.stop_gap / 100
            stop_order.stop_trailing_price = price
        else:
            raise_bultin_error('stopgap')
    else:
        raise_bultin_error('orderact')


# 判断是否要撤单
# :param bar_high: float
# :param bar_low: float
# :param volume: float,持仓量, volume==0, Cancel 掉
# :param same_target_stop_orders: list, ATStopOrder object
# :return: may_fire, must_tick_check. may_fire: list of stop_order, must_tick_check: list of stop_order
def _judge_stop_orders_by_bar(bar_high: float, bar_low: float, volume: int, stop_orders: List[DQTBackStopOrder]) -> tuple[List[DQTBackStopOrder], List[DQTBackStopOrder]]:
    # temp_stop_trailing_price 跟踪止盈单的临时触发价格
    temp_stop_trailing_price = 0
    may_fire = []
    must_tick_check = []
    cancelled_stop_orders: List[DQTBackStopOrder] = []
    for stop_order in stop_orders:
        if stop_order.execute_status == OrderStopExecType.HOLDING:
            continue
        # 持仓量为 0 了就不需要撤单了
        if volume == 0:
            stop_order.execute_status = OrderStopExecType.CANCELED
            cancelled_stop_orders.append(stop_order)
            continue

        # 普通止损单
        if stop_order.stop_order_type == OrderStopType.LOSS:
            if stop_order.act == OrderSide.BUY:
                # 如果是买入持仓
                # 目前 tick 数据已经低于撤单价格，那么撤单
                if bar_low <= stop_order.stop_price:
                    may_fire.append(stop_order)
                # 卖出持仓
                # 如果当前价格已经大于指定的价格，则撤单
            elif stop_order.act == OrderSide.SELL:
                if bar_high >= stop_order.stop_price:
                    may_fire.append(stop_order)
            else:
                raise_bultin_error('orderact')
        # 普通止盈单
        elif stop_order.stop_order_type == OrderStopType.PROFIT:
            if stop_order.act == OrderSide.BUY:
                if bar_high >= stop_order.stop_price:
                    may_fire.append(stop_order)
            elif stop_order.act == OrderSide.SELL:
                if bar_low <= stop_order.stop_price:
                    may_fire.append(stop_order)
            else:
                raise_bultin_error('orderact')
        # 跟踪止盈单
        elif stop_order.stop_order_type == OrderStopType.TRAILING:
            # 没开始跟踪，设置开始跟踪
            if not stop_order.is_begin_trailing:
                # 多头的话，当前最高价高于跟踪价格，则开始跟踪
                cond0 = (stop_order.act ==
                         OrderSide.BUY and bar_high >= stop_order.trailing_price)
                cond1 = (stop_order.act ==
                         OrderSide.SELL and bar_low <= stop_order.trailing_price)
                if not (cond0 or cond1):
                    continue
                # 是否在成本价的 bar 位置，是否在成本价的位置，那么从 tick 检查
                if not stop_order.in_bar_begin:
                    must_tick_check.append(stop_order)
                    continue
                stop_order.is_begin_trailing = True
                stop_order.execute_status = OrderStopExecType.TRAILING
                stop_order.in_begin_trailing_bar = True
                stop_order.trailing_high = stop_order.trailing_price
                stop_order.trailing_low = stop_order.trailing_price
                _update_stop_trailing_order_trigger_price(
                    stop_order, stop_order.target_price)
            if stop_order.act == OrderSide.BUY:
                if bar_high > stop_order.trailing_high:
                    # 最高价理论需要更新
                    if stop_order.stop_gap_type == OrderStopGapType.POINT:
                        temp_stop_trailing_price = bar_high - stop_order.stop_gap
                    elif stop_order.stop_gap_type == OrderStopGapType.PERCENT:
                        temp_stop_trailing_price = bar_high - \
                            (bar_high - stop_order.target_price) * \
                            stop_order.stop_gap / 100
                    else:
                        raise_bultin_error('stopgap')

                    if bar_low <= temp_stop_trailing_price:
                        # 说明在此 bar 中需要执行止盈单
                        must_tick_check.append(stop_order)
                        continue
                    else:
                        stop_order.trailing_high = bar_high
                        stop_order.stop_trailing_price = temp_stop_trailing_price
                elif bar_low <= stop_order.stop_trailing_price:
                    # 市价没有在上升，不需要更新最高价和止损价，直接进行判断
                    if stop_order.in_begin_trailing_bar:
                        must_tick_check.append(stop_order)
                    else:
                        stop_order.trailing_low = min(
                            stop_order.trailing_low, stop_order.stop_trailing_price)
                        may_fire.append(stop_order)
                    continue

                if bar_low < stop_order.trailing_low:
                    stop_order.trailing_low = bar_low
            elif stop_order.act == OrderSide.SELL:
                if bar_low < stop_order.trailing_low:
                    if stop_order.stop_gap_type == OrderStopGapType.POINT:
                        temp_stop_trailing_price = bar_low + stop_order.stop_gap
                    elif stop_order.stop_gap_type == OrderStopGapType.PERCENT:
                        temp_stop_trailing_price = bar_low + \
                            (stop_order.target_price - bar_low) * \
                            stop_order.stop_gap / 100
                    else:
                        raise_bultin_error('stopgap')

                    if bar_high >= temp_stop_trailing_price:
                        must_tick_check.append(stop_order)
                        continue
                    else:
                        stop_order.trailing_low = bar_high
                        stop_order.stop_trailing_price = temp_stop_trailing_price
                elif bar_high >= stop_order.stop_trailing_price:
                    if stop_order.in_begin_trailing_bar:
                        must_tick_check.append(stop_order)
                    else:
                        stop_order.trailing_high = max(
                            stop_order.trailing_high, stop_order.stop_trailing_price)
                        may_fire.append(stop_order)
                    continue
                if bar_high > stop_order.trailing_high:
                    stop_order.trailing_high = bar_high
            else:
                raise_bultin_error('orderact')
        else:
            raise_bultin_error('stopordertype')

    # 止损止盈单已经触发，将其从unfired列表中移除
    for cancelled_stop_order in cancelled_stop_orders:
        OrderVar.remove_unfired_stop_order(cancelled_stop_order.stop_order_id)

    return may_fire, must_tick_check


# 处理正常订单
def _deal_normal_order() -> tuple[List[int], List[int]]:
    # 
    filled_order_ids = []
    order_denied_canceled_ids = []
    if not OrderVar.exist_unfilled_order():
        return filled_order_ids, order_denied_canceled_ids

    # 获取所有订单id
    unfilled_orders = OrderVar.get_all_unfilled_order()
    order_ids = [order.order_id for order in unfilled_orders]
    env = get_env()
    bar_open: List[float] = []
    bar_high: List[float] = []
    bar_low: List[float] = []
    bar_volume: List[int] = []
    
    for unfilled_order in unfilled_orders:
        kdata = env.get_driver_kdata(unfilled_order.target_index)
        bar_open.append(kdata.open)
        bar_high.append(kdata.high)
        bar_low.append(kdata.low)
        bar_volume.append(kdata.volume)

    # step1 处理刷新上根 bar 用户下的单, 返回对应被处理单的 `order status`
    order_status_s = _transaction_order(order_ids,
                                        bar_high,
                                        bar_low,
                                        bar_open,
                                        bar_volume,
                                        [], [])
    # np.where 返回的时索引
    order_cancelled_indexs = np.where(order_status_s == OrderStatus.CANCELED)[0]
    order_filled_indexs = np.where(order_status_s == OrderStatus.DEALED)[0]
    order_denied_indexs = np.where(order_status_s == OrderStatus.REJECTED)[0]

    # step2 step2 取出 `filled` 单 和 `denied/cancel` 状态的单
    order_filled_idxs = list(order_filled_indexs)
    filled_order_ids = [order_ids[idx] for idx in order_filled_idxs]
    order_denied_cancel_idxs = list(order_cancelled_indexs) + list(order_denied_indexs)
    order_denied_canceled_ids = [order_ids[idx]
                                 for idx in order_denied_cancel_idxs]

    # step3 清除 `unfilled` 下单记录中的已完成单子，拒绝单据，和取消单据
    OrderVar.remove_unfilled_order(
        filled_order_ids + order_denied_canceled_ids)

    return filled_order_ids, order_denied_canceled_ids


#  确定通过 tick 数据撮合的止损单的 OHLC
# :param stop_orders: list of ATBackStopOrder, 需要通过 tick 数据进行撮合的止损单
# :return: fire_stop_orders, tick_bar_open, tick_bar_high, tick_bar_low, tick_bar_vol
def _judge_stop_orders_by_tick(stop_orders: List[DQTBackStopOrder]):

    tick_bar_open = np.array([])
    tick_bar_high = np.array([])
    tick_bar_low = np.array([])
    tick_bar_vol = np.array([])

    fire_stop_orders = []
    env = get_env()
    strategy = get_strategy()
    cur_bar_time = env.cur_bar_time()

    tick_datas = dqtrader_rs.get_tick(strategy.target(
        stop_orders[0].target_index), "", cur_bar_time, 0)

    tick_times = []
    tick_prices = []
    tick_volumes = []
    for tick_data in tick_datas:
        tick_times.append(tick_data.datetime)
        tick_prices.append(tick_data.price)
        tick_volumes.append(tick_data.volume)

    tick_times = np.array(tick_times)
    tick_prices = np.array(tick_prices)
    tick_volumes = np.array(tick_volumes)
    tick_begin_num = 0
    tick_end_num = len(tick_times)

    # 构建笛卡尔集
    for tick_num, stop_order in itertools.product(range(tick_begin_num, tick_end_num), stop_orders):
        cur_tick_price = tick_prices[tick_num]
        cur_tick_time = tick_times[tick_num]
        d_cur_tick_price = Decimal(str(cur_tick_price))
        d_target_price = Decimal(str(stop_order.target_price))
        d_stop_price = Decimal(str(stop_order.stop_price))

        if not stop_order.in_bar_begin:
            # The target order never meet the price so we can't check in bar begin
            # Find the target order position
            cond0 = (stop_order.act ==
                     OrderSide.BUY and d_cur_tick_price <= d_target_price)
            cond1 = (stop_order.act ==
                     OrderSide.SELL and d_cur_tick_price >= d_target_price)
            if not (cond0 or cond1):
                continue
            stop_order.in_bar_begin = True

        if stop_order.stop_order_type == OrderStopType.LOSS:
            # 止损
            cond0 = (stop_order.act ==
                     OrderSide.BUY and d_cur_tick_price <= d_stop_price)
            cond1 = (stop_order.act ==
                     OrderSide.SELL and d_cur_tick_price >= d_stop_price)
            if cond0 or cond1:
                stop_order.trigger_real_price = cur_tick_price
                stop_order.trigger_time = cur_tick_time
                tick_bar_open = np.array([cur_tick_price]).ravel()
                tick_bar_high = np.array(
                    [max(tick_prices[tick_num: tick_end_num])]).ravel()
                tick_bar_low = np.array(
                    [min(tick_prices[tick_num: tick_end_num])]).ravel()
                tick_bar_vol = np.array(
                    [sum(tick_volumes[tick_num: tick_end_num])]).ravel()
                fire_stop_orders = [stop_order]
        elif stop_order.stop_order_type == OrderStopType.PROFIT:
            # 止盈
            cond0 = (stop_order.act ==
                     OrderSide.BUY and d_cur_tick_price >= d_stop_price)
            cond1 = (stop_order.act ==
                     OrderSide.SELL and d_cur_tick_price <= d_stop_price)
            if cond0 or cond1:
                stop_order.trigger_real_price = cur_tick_price
                stop_order.trigger_time = cur_tick_time
                tick_bar_open = np.array([cur_tick_price]).ravel()
                tick_bar_high = np.array(
                    [max(tick_prices[tick_num: tick_end_num])]).ravel()
                tick_bar_low = np.array(
                    [min(tick_prices[tick_num: tick_end_num])]).ravel()
                tick_bar_vol = np.array(
                    [sum(tick_volumes[tick_num: tick_end_num])]).ravel()
                fire_stop_orders = [stop_order]
        elif stop_order.stop_order_type == OrderStopType.TRAILING:
            # 跟踪止盈
            trailing_price = stop_order.trailing_price
            d_trailing_price = Decimal(str(trailing_price))
            if not stop_order.is_begin_trailing:
                cond0 = (stop_order.act ==
                         OrderSide.BUY and d_cur_tick_price >= d_trailing_price)
                cond1 = (stop_order.act ==
                         OrderSide.SELL and d_cur_tick_price <= d_trailing_price)

                if not (cond0 or cond1):
                    continue

                stop_order.is_begin_trailing = True
                stop_order.execute_status = OrderStopType.TRAILING
                stop_order.in_begin_trailing_bar = False
                stop_order.trailing_high = trailing_price
                stop_order.trailing_low = trailing_price
                _update_stop_trailing_order_trigger_price(
                    stop_order, stop_order.target_price)

            if stop_order.in_begin_trailing_bar:
                cond0 = (stop_order.act ==
                         OrderSide.BUY and d_cur_tick_price >= d_trailing_price)
                cond1 = (stop_order.act ==
                         OrderSide.SELL and d_cur_tick_price <= d_trailing_price)
                if not (cond0 or cond1):
                    continue

                stop_order.is_begin_trailing = True
                stop_order.execute_status = OrderStopType.TRAILING
                stop_order.in_begin_trailing_bar = False
                stop_order.trailing_high = trailing_price
                stop_order.trailing_low = trailing_price

            stop_trailing_price = stop_order.stop_trailing_price
            d_stop_trailing_price = Decimal(str(stop_trailing_price))
            trailing_high = stop_order.trailing_high
            d_trailing_high = Decimal(str(trailing_high))
            trailing_low = stop_order.trailing_low
            d_trailing_low = Decimal(str(trailing_low))

            cond0 = (stop_order.act ==
                     OrderSide.BUY and d_cur_tick_price <= d_stop_trailing_price)
            cond1 = (
                stop_order.act == OrderSide.SELL and d_cur_tick_price >= d_stop_trailing_price)
            if cond0 or cond1:
                # Tick to fire the trailing order
                stop_order.trigger_real_price = cur_tick_price
                stop_order.trigger_time = cur_tick_time
                stop_order.trailing_high = max(trailing_high, cur_tick_price)
                stop_order.trailing_low = min(trailing_low, cur_tick_price)

                tick_bar_open = np.array([cur_tick_price]).ravel()
                tick_bar_high = np.array(
                    [max(tick_prices[tick_num: tick_end_num])]).ravel()
                tick_bar_low = np.array(
                    [min(tick_prices[tick_num: tick_end_num])]).ravel()
                tick_bar_vol = np.array(
                    [sum(tick_volumes[tick_num: tick_end_num])]).ravel()

                fire_stop_orders = [stop_order]
                _update_stop_trailing_order_trigger_price(
                    stop_order, stop_order.target_price)
            else:
                # Not fire the order check for updating price
                if stop_order.act == OrderSide.BUY and d_cur_tick_price > d_trailing_high:
                    stop_order.trailing_high = cur_tick_price
                    _update_stop_trailing_order_trigger_price(
                        stop_order, cur_tick_price)
                elif stop_order.act == OrderSide.SELL and d_cur_tick_price < d_trailing_low:
                    stop_order.trailing_low = cur_tick_price
                    _update_stop_trailing_order_trigger_price(
                        stop_order, cur_tick_price)
        else:
            raise_bultin_error('stopordertype')

        if len(fire_stop_orders) > 0:
            break

    return fire_stop_orders, tick_bar_open.tolist(), tick_bar_high.tolist(), tick_bar_low.tolist(), tick_bar_vol.tolist()


# rule: 只要有一个止损单触发, 相应的止损单(目标单对应的止损单)将撤销
def _cancel_other_stop_order(stop_order: DQTBackStopOrder):
    stop_order_target_order_id = stop_order.target_order_id

    if Environment.is_valid_order_id(stop_order_target_order_id):
        same_stop_orders: List[DQTBackStopOrder] = OrderVar.get_unfired_stop_order_by_target_id(
            stop_order_target_order_id)
        active_stop_orders = [
            stop_order for stop_order in same_stop_orders if stop_order.execute_status == OrderStopExecType.ACTIVE]

        _update_stop_order_status(
            active_stop_orders, OrderStopExecType.CANCELED)

        for same_stop_order in same_stop_orders:
            OrderVar.remove_unfired_stop_order(same_stop_order.stop_order_id)
    else:
        OrderVar.remove_unfired_stop_order(stop_order.stop_order_id)


# 将被触发的止盈单转换为 order，并将此订单对应的止盈单全部清空
# :param stop_order: ATBackStopOrder 对象
# :return: order_id, target_price, trigger_time
# ::
#     order_id: numpy.ndarry(1*1), 生成的订单号
#     target_price: numpy.ndarry(1*1), 生成订单号的成交价
#     trigger_time: numpy.ndarry(1*1), 生成订单时间
def _fire_stop_order(stop_order: DQTBackStopOrder):

    order_id = OrderVar.gen_order_id()
    stop_order.order_id = order_id
    stop_order.execute_status = OrderStopExecType.TRIGGER
    target_price = stop_order.trigger_real_price

    strategy = get_strategy()

    target_type = strategy.get_type(stop_order.target_index)

    new_order = DQTBackOrder.create(
        target_index=stop_order.target_index,
        code=stop_order.code,
        order_id=order_id,
        order_price=0.0,
        target_type=target_type,
        position_effect=OrderPositionEffect.CLOSE,
        created_time=stop_order.trigger_time,
        order_status=OrderStatus.CREATED,
        volume=stop_order.volume,
        order_ctg=stop_order.ctg,
        order_side=stop_order.act)

    OrderVar.append_order(new_order)
    # cnt.vr.g_ATOrders.append(new_order.order_id, new_order)
    _cancel_other_stop_order(stop_order)

    return [order_id], [target_price], [stop_order.trigger_time]


def _get_order_related_unfired_stop_order(order_ids: List[int]):
    unfired_stop_orders = OrderVar.get_all_unfired_stop_order()

    order_relate_unfired_stop_orders = [
        o for o in unfired_stop_orders for order_id in order_ids if o.target_order_id == order_id]

    return order_relate_unfired_stop_orders


def _deal_stop_order(filled_order_ids: List[int], order_denied_canceled_ids: List[int]) -> tuple[List[int], List[int]]:
    fired_stop_order_ids = []

    # step1 撤销普通单为 `Denied/Canceled` 状态所对应的止损单
    _cancelled_stop_order_by_target_order_id(order_denied_canceled_ids)

    if not OrderVar.exist_unfired_order():
        return filled_order_ids, fired_stop_order_ids

    # step2 取出全部止盈止损单对应的普通单单号
    # step3 去掉单号为 np.nan 的值, 暂时不做通过价格进行止盈止损的操作
    env = get_env()
    account = get_account()
    strategy = get_strategy()

    target_order_ids = [
        order.target_order_id for order in OrderVar.get_all_unfired_stop_order()]

    target_order_ids.sort()
    for order_id in target_order_ids:
        order: DQTBackOrder = OrderVar.get_order(order_id)
        positions = account.get_position(order.target_index)
        kdata = env.get_driver_kdata(order.target_index)
        if kdata.volume < 1:
            continue
        if order.side == OrderSide.BUY:
            position_volume = positions.position_available_long
        elif order.side == OrderSide.SELL:
            position_volume = positions.position_available_short
        else:
            position_volume = 0
            raise_bultin_error('orderact')

        fire_stop_orders: List[DQTBackStopOrder] = []
        cur_bar_time = env.cur_bar_time()
        stop_order_list = OrderVar.get_unfired_stop_order_by_target_id(
            order_id)
        # 是否需要使用 tick 检查是否关闭订单
        may_fire, must_tick_check = _judge_stop_orders_by_bar(
            kdata.high, kdata.low, position_volume, stop_order_list)

        in_bar_begin = len(may_fire) > 0 and not getattr(
            may_fire[0], 'in_bar_begin')

        if len(must_tick_check) >= 1 or len(may_fire) >= 2 or in_bar_begin:
            if strategy.frequency_int == Frequency.Tick and strategy.frequency_num == 1:
                fire_stop_orders = must_tick_check.copy()

                for fire_stop_order in fire_stop_orders:
                    fire_stop_order.trigger_time = cur_bar_time
            else:
                tick_check_orders = list(must_tick_check) + list(may_fire)
                fire_stop_orders, bar_open, bar_high, bar_low, bar_volume = _judge_stop_orders_by_tick(
                    tick_check_orders)
        else:
            if len(may_fire) > 0:
                fire_stop_orders = may_fire.copy()
                for fire_stop_order in fire_stop_orders:
                    fire_stop_order.trigger_time = cur_bar_time

        for stop_order in fire_stop_orders:
            fired_stop_order_ids.append(stop_order.stop_order_id)

            order_id, target_price, trigger_time = _fire_stop_order(stop_order)
            order_status_s = _transaction_order(
                order_id, bar_high, bar_low, bar_open, bar_volume, target_price, trigger_time)

            if order_status_s in (OrderStatus.CANCELED, OrderStatus.DEALED, OrderStatus.REJECTED):
                filled_order_ids.extend(order_id)

    filled_order_relate_stop_orders = _get_order_related_unfired_stop_order(
        filled_order_ids)
    for o in filled_order_relate_stop_orders:
        o.in_bar_begin = True
    for o in [o for o in OrderVar.get_all_unfired_stop_order() if o.is_begin_trailing]:
        o.in_begin_trailing_bar = False
    return filled_order_ids, fired_stop_order_ids


# 交易处理主函数
def deal_trade():
    _update_unfired_stop_order_status_if_holding_status()
    filled_order_ids, order_denied_canceled_ids = _deal_normal_order()
    filled_order_ids, fired_stop_order_ids = _deal_stop_order(
        filled_order_ids, order_denied_canceled_ids)

    return filled_order_ids, order_denied_canceled_ids, fired_stop_order_ids
