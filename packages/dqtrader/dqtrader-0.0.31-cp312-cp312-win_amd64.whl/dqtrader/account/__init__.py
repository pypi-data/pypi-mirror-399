import pandas as pd
# 账号222
from datetime import datetime
from math import isnan
from typing import Dict, List

from dqtrader.backtest_environment import get_env
from dqtrader.entity import DQTBackOrder, DQTBackTrade
from dqtrader.entity.position_entity import BasePosition, FuturePosition, StockCommissionRate, StockPosition
from dqtrader.strategy import get_strategy
from dqtrader.enums import CashChangeReason, OrderPositionEffect, OrderSide, OrderStatus, PositionChangeReason, \
    PositionSide, TargetType
from dqtrader.exception import raise_bultin_error
from dqtrader.tframe.language.chinese import text


class Account:
    # 初始资金
    initial_cash: float
    #  手续费倍数(相对于交易所)
    future_cost_fee: float
    # 股票手续费(单位万分之一)
    stock_cost_fee: float
    #
    stock_commission_rate: StockCommissionRate
    # 滑价
    slide_price: float
    #    LimitType: 限价单成交方式: 默认为 False
    #        False-直接成交
    #        True-下根 bar 内没有该价格时, 撤单处理
    limit_type: bool
    #    PriceLoc: 定价策略, 市价单成交位置, 默认为 1
    #        0, 当前收盘价
    #        1，下一个 bar 开盘价
    #        2，下一个 bar 第 2 个 tick
    #        n, 下一个 bar 第 n 个 tick
    price_loc: float
    # 无风险利率
    risk_free_rate: float
    #    DealType: 市价单成交类型: 默认为0
    #        1-对方最优价
    #        2-己方最优价
    deal_type: int
    # 保证金倍数(相对于交易所)
    margin_rate: float
    # 下一根bar没有开盘价时 order 单 不取消
    market_order_holding: bool
    # datetime.datetime 日内平仓时间, 默认为 None
    daily_close_time: datetime
    ########################################################
    # 持仓
    _position: Dict[int, BasePosition]

    # 最新期货浮动盈亏更新时间 float 类型与数据保存方式一致
    _update_time: int
    # 期货持仓盈亏(时变)
    _future_float_profit: float
    #
    _raw_valid_cash: float
    # 昨结算后的市值权益
    _last_total_value: float

    # 期货保证金冻结
    _future_margin_frozen: float
    # 期货冻结的资金
    _future_order_frozen: float
    # 股票冻结的自己能
    _stock_order_frozen: float

    _future_cost_fee_frozen: float
    _stock_cost_fee_frozen: float
    # 当日平仓盈亏
    _stock_daily_realize_pnl: float
    _future_daily_realize_pnl: float

    _stock_daily_cost_fee: float

    _future_daily_cost_fee: float

    stock_total_cost_fee: float

    future_total_cost_fee: float

    _change_reason: CashChangeReason

    def __init__(self) -> None:
        # 持仓
        self._position = {}
        # 初始资金
        self.initial_cash = 1e7
        # #  手续费倍数(相对于交易所)
        # self.future_cost_fee = 1.1
        # # 股票手续费(单位万分之一)
        # self.stock_cost_fee = 2.5
        # 滑价
        self.slide_price = 0
        #    LimitType: 限价单成交方式: 默认为 False
        #        False-直接成交
        #        True-下根 bar 内没有该价格时, 撤单处理
        self.limit_type = False
        #    PriceLoc: 定价策略, 市价单成交位置, 默认为 1
        #        0, 当前收盘价
        #        1，下一个 bar 开盘价
        #        2，下一个 bar 第 2 个 tick
        #        n, 下一个 bar 第 n 个 tick
        self.price_loc = 1
        # 无风险利率
        self.risk_free_rate = 0.02
        #    DealType: 市价单成交类型: 默认为0
        #        1-对方最优价
        #        2-己方最优价
        self.deal_type = 0
        # 保证金倍数(相对于交易所)
        self.margin_rate = 1.0
        # 下一根bar没有开盘价时 order 单 不取消
        self.market_order_holding = True
        # datetime.datetime 日内平仓时间, 默认为 None
        self.daily_close_time = None

        self.stock_commission_rate = StockCommissionRate()

        self._update_time = 0

        self._future_float_profit = 0.0
        # 前一天结算的可用资金 + 期货平仓盈亏 - 开仓占用保证金 + 卖出股票收入 - 买入股票成本 - 下单冻结 + 撤单解冻 - 交易手续费
        self._raw_valid_cash = self.initial_cash

        self._last_total_value = self.initial_cash
        #
        self._future_order_frozen = 0.0
        self._stock_order_frozen = 0.0

        self._future_cost_fee_frozen = 0.0
        self._stock_cost_fee_frozen = 0.0

        self._future_margin_frozen = 0.0

        self._stock_daily_realize_pnl = 0.0
        self._future_daily_realize_pnl = 0.0

        self._stock_daily_cost_fee = 0.0
        self._future_daily_cost_fee = 0.0

        self._change_reason = CashChangeReason.UNKNOWN

        self.stock_total_cost_fee = 0.0

        self.future_total_cost_fee = 0.0

    def set_initial_cash(self, initial_cash: float):
        self.initial_cash = initial_cash
        self._raw_valid_cash = self.initial_cash
        self._last_total_value = self.initial_cash

    def set_slide_price(self, slide_price: float):
        self.slide_price = slide_price

    def set_limit_type(self, limit_type: bool):
        self.limit_type = limit_type

    def set_price_loc(self, price_loc: float):
        self.price_loc = price_loc

    def set_risk_free_rate(self, risk_free_rate: float):
        self.risk_free_rate = risk_free_rate

    def set_deal_type(self, deal_type: int):
        self.deal_type = deal_type

    def set_margin_rate(self, margin_rate: float):
        self.margin_rate = margin_rate

    def set_market_order_holding(self, market_order_holding: bool):
        self.market_order_holding = market_order_holding

    def set_daily_close_time(self, daily_close_time: datetime):
        self.daily_close_time = daily_close_time

    def init_from_config(self, config):
        env = get_env()
        # 初始化账号信息
        if "account" in config:
            # 要做类型检查
            account = config["account"]
            if "initial_cash" in account:
                initial_cash = account["initial_cash"]
                self.set_initial_cash(initial_cash)
            else:
                raise Exception("缺少 config['account']['initial_cash'] 字段")

            if "future_cost_fee" in account:
                env.set_future_cost_fee(account["future_cost_fee"])
                # self.future_cost_fee = account["future_cost_fee"]

            if "stock_cost_fee" in account:
                env.set_stock_cost_fee(account["stock_cost_fee"])
                # self.stock_cost_fee = account["stock_cost_fee"]

            if "slide_price" in account:
                self.slide_price = account["slide_price"]

            if "limit_type" in account:
                self.limit_type = account["limit_type"]

            if "price_loc" in account:
                self.price_loc = account["price_loc"]

            if "risk_free_rate" in account:
                self.risk_free_rate = account["risk_free_rate"]

            if "deal_type" in account:
                self.deal_type = account["deal_type"]

            if "margin_rate" in account:
                self.margin_rate = account["margin_rate"]

            if "market_order_holding" in account:
                self.market_order_holding = account["market_order_holding"]

    # 重置账号
    def reset(self):
        self._raw_valid_cash = self.initial_cash
        self._last_total_value = self._raw_valid_cash
        self.stock_commission_rate.trade_fee = self.stock_cost_fee / 10000  # 回测佣金设置

    # 获取弛放
    def get_position(self, target_index: int) -> BasePosition:
        position = self._position.get(target_index)
        if position is None:
            strategy = get_strategy()
            type = strategy.get_type(target_index)
            target = strategy.target(target_index)
            if type == TargetType.STOCK:
                position = StockPosition(target_index, target)
            elif type == TargetType.FUTURE:
                position = FuturePosition(target_index, target)
            self._position[target_index] = position
            return position
        return position

    def volume_long(self) -> pd.Series:
        strategy = get_strategy()
        volume_long_array = []
        for target_index in range(len(strategy.target_list)):
            position = self.get_position(target_index)
            volume_long_array.append(position.volume_long())
        return pd.Series(volume_long_array)

    def volume_short(self) -> pd.Series:
        strategy = get_strategy()
        volume_short_array = []
        for target_index in range(len(strategy.target_list)):
            position = self.get_position(target_index)
            if position.type == TargetType.FUTURE:
                future_position: FuturePosition = position
                volume_short_array.append(future_position.volume_short())
            else:
                volume_short_array.append(0)
        return pd.Series(volume_short_array)

    def get_or_build_position_by_order(self, order: DQTBackOrder) -> BasePosition:

        position = self._position.get(order.target_index, None)
        if position is not None:
            return position

        if order.target_type == TargetType.STOCK:
            position = StockPosition()
            position.target_index = order.target_index
            position.target = order.code
            self._position[order.target_index] = position
        elif order.target_type == TargetType.FUTURE:
            position = FuturePosition()
            position.target_index = order.target_index
            position.target = order.code
            self._position[order.target_index] = position
        else:
            raise NotImplementedError

    def get_or_build_position_by_stock_order(self, order: DQTBackOrder) -> StockPosition:
        return self.get_or_build_position_by_order(order)

    def get_or_build_position_by_future_order(self, order: DQTBackOrder) -> FuturePosition:
        return self.get_or_build_position_by_order(order)

    # 返回多头保证金

    def future_margin_long(self, target_index: int) -> float:
        position = self._position.get(target_index, None)
        if position is None:
            return 0.0
        if position.type != TargetType.FUTURE:
            return 0.0
        env = get_env()
        margin_rate = self.get_long_margin(target_index)
        position: FuturePosition = position
        multiple = env.get_multiple(target_index)
        margin = position.volume_long_yd * \
                 position.holding_cost_long * multiple * margin_rate
        margin += sum((p * v * margin_rate * multiple for p,
                                                          v in position.holding_cost_today_long_list))
        return margin

    #  返回空头保证金
    def future_margin_short(self, target_index: int) -> float:
        position = self._position.get(target_index, None)
        if position is None:
            return 0.0
        if position.type != TargetType.FUTURE:
            return 0.0
        env = get_env()
        margin_rate = self.get_short_margin(target_index)
        position: FuturePosition = position
        multiple = env.get_multiple(target_index)
        margin = position.volume_short_yd * \
                 position.holding_cost_short * multiple * margin_rate
        margin += sum((p * v * multiple * margin_rate for p,
                                                          v in position.holding_cost_today_short_list))
        return margin

    # 标的占用保证金
    # 保证金 = 昨仓仓位 * 昨结算价 * 合约乘数 * 保证金倍率 + 今仓开仓价格 * 持仓量 * 合约乘数 * 保证金倍率
    def future_margin(self, targe_index: int) -> float:
        return self.future_margin_long(targe_index) + self.future_margin_short(targe_index)

    # 获取该账户下所有持仓的占用保证金
    def future_margins(self) -> float:
        total_margin = sum((self.future_margin(position.target_index)
                            for position in self._position.values()))
        return total_margin

    #  可用资金
    #     valid_cash = _raw_valid_cash + future_frozen_profit
    #     期货浮盈是期货持仓浮盈部分，这部分资金可以在下单中占用
    # :param cur_time: 刷新时间，当传入的刷新时间等于当前浮盈刷新时间的时候，不用更新数据直接返回，否则一律重新计算
    # :return: int 可用资金

    def future_holding_pnl(self) -> float:
        holding_pnl: float = 0.0
        env = get_env()
        for targe_index, position in self._position.items():
            if position.type != TargetType.FUTURE:
                continue
            market_price = env.market_price(targe_index, 0)
            multiple = env.get_multiple(targe_index)
            # 转换类型
            position: FuturePosition = position

            holding_pnl += market_price * position.volume(PositionSide.LONG) * multiple - position.long_holding_total

            holding_pnl += position.short_holding_total - market_price * position.volume(PositionSide.SHORT) * multiple
        return holding_pnl

    # 当前可用资金
    def valid_cash(self, cur_time: int | None = None) -> float:
        env = get_env()
        if cur_time is None:
            cur_time = env.cur_bar_time()  # 根据市价计算最新的浮盈

        if cur_time != self._update_time:
            self._future_float_profit = self.future_holding_pnl()
            self._update_time = env.cur_bar_time()  # 根据市价计算最新的浮盈
        return self._raw_valid_cash + self._future_float_profit

    # 获取股票账户下的持仓市值
    # 股票持仓市值 = 持仓数量* 市价
    def stock_market_value(self) -> float:
        total_market_value = 0.0
        env = get_env()
        for position in self._position.values():
            if position.type != TargetType.STOCK:
                continue
            market_price = env.market_price(position.target_index, -1) if env.min_freq_turn_pos else env.market_price(
                position.target_index, 0)

            total_market_value += position.volume(
                PositionSide.LONG) * market_price
        return total_market_value

    # 返回动态权益
    # 动态权益 = 原始可用资金 + 期货浮盈 + 占用保证金 + 期货下单冻结 + 股票下单冻结 + 股票持仓市值
    @property
    def total_value(self) -> float:
        return self.valid_cash() + self._future_order_frozen \
               + self.future_margins() \
               + self._stock_order_frozen \
               + self.stock_market_value()

    def get_long_margin(self, target_index: int, default: float = 1.0) -> float:
        env = get_env()
        strategy = get_strategy()
        target = strategy.target(target_index)
        target_info = env.target_info_dict.get(target)
        if target_info is None:
            return default
        return target_info.long_margin * self.margin_rate

    def get_short_margin(self, target_index: int, default: float = 1.0) -> float:
        strategy = get_strategy()
        env = get_env()
        target = strategy.target(target_index)
        target_info = env.target_info_dict.get(target)
        if target_info is None:
            return default
        return target_info.short_margin * self.margin_rate

    # def cost_fee_rate(self, target_type: TargetType) -> float:
    #     if target_type == 2:
    #         # 期货
    #         return self.future_cost_fee
    #     elif target_type == 1:
    #         # 股票
    #         return self.stock_cost_fee / 1e4
    #     else:
    #         return 0
    def get_margin_rate(self, target_index: int, side: OrderSide, default: float = 1.0) -> float:
        if side == OrderSide.BUY:
            return self.get_long_margin(target_index, default)
        elif side == OrderSide.SELL:
            return self.get_short_margin(target_index, default)
        else:
            return default

    #  处理股票订单， 只处理以下类型的订单
    #     cancel order: 取消订单
    #     deny order:  拒绝的订单
    #     holding order: 下单成功
    #     pre-holding订单跳过, filled订单跳过(成交通过on_trade函数处理)
    #     note: 冻结/解冻资金对可用资金的影响请在外部自己完成
    #           本函数不进行可用资金的检查
    # :param order: 订单对象，为了计算每一笔订单的资金变动和平仓盈亏，只能传入一个订单
    # :return: order_frozen 下单冻结资金，正值表示冻结，负值表示解冻

    def on_stock_order(self, order: DQTBackOrder) -> float:
        fee = 0.0
        order_frozen = 0.0
        env = get_env()
        position = self.get_or_build_position_by_stock_order(order)
        if order.status in (OrderStatus.CANCELED, OrderStatus.REJECTED):
            if order.position_effect == OrderPositionEffect.OPEN:
                fee = -order.frozen_info.fee  # 获取冻结手续费，这部分在order中处理
                order_frozen = -(order.frozen_info.value +
                                 order.frozen_info.fee)
            elif order.position_effect == OrderPositionEffect.CLOSE:
                # 平仓单将冻结仓位返还
                position.order_frozen_long = position.order_frozen_long - order.volume  # 更新【总】冻结仓位
                position.available_long = position.available_long + order.volume  # 更新可平仓位
                if not env.is_old_order_rb(order.updated_time):
                    position.order_frozen_today_long = position.order_frozen_today_long - \
                                                       order.volume  # 如果是今单，更新今仓冻结仓位
                    position.available_today_long = position.available_today_long + order.volume
        elif order.status == OrderStatus.REPORTED:
            if order.position_effect == OrderPositionEffect.OPEN:
                fee = order.frozen_info.fee  # 获取冻结手续费，这部分在order中处理
                order_frozen = order.frozen_info.value + order.frozen_info.fee  # 资金冻结
            elif order.position_effect == OrderPositionEffect.CLOSE:
                # 更新冻结仓位信息
                position.order_frozen_long = position.order_frozen_long + order.volume  # 更新【总】冻结仓位
                position.order_frozen_today_long = position.order_frozen_today_long + \
                                                   order.volume  # 更新今仓冻结仓位
                position.available_long = position.available_long - order.volume  # 订单冻结，【总】可平仓位减少
                position.available_today_long = position.available_today_long - order.volume  # 今可平仓位减小
        # 更新子账户的相关记录
        self._stock_order_frozen += order_frozen
        self._stock_cost_fee_frozen += fee
        return order_frozen

    #   处理一下三种状态的订单，并将资金返还到可用资金中
    #     order cancel: 取消订单，冻结保证金和手续费归还
    #     order deny: 拒绝订单，冻结保证金和手续费归还
    #     order holding: 委托状态，保证金及手续费冻结
    #     note: pre-holding订单直接跳过，filled订单已经在on_trade中处理
    # :param order: 待处理的订单
    # :return: order_frozen 订单冻结
    def on_future_order(self, order: DQTBackOrder) -> float:
        margin_frozen = 0.0
        fee_frozen = 0.0
        order_frozen = 0.0
        env = get_env()
        position = self.get_or_build_position_by_future_order(order)
        if order.status == OrderStatus.REPORTED:
            if order.position_effect == OrderPositionEffect.OPEN:
                # 计算冻结保证金和冻结手续费,这里获取到的手续费已经区分了多空/开平的情况，不需要再自行判断
                margin_frozen = order.frozen_info.value
                fee_frozen = order.frozen_info.fee
                order_frozen = margin_frozen + fee_frozen
            elif order.position_effect == OrderPositionEffect.CLOSE:
                if order.side == OrderSide.SELL:
                    position.order_frozen_long = position.order_frozen_long + order.volume
                    position.order_frozen_today_long = position.order_frozen_today_long + order.volume
                    position.available_long = position.available_long - order.volume
                elif order.side == OrderSide.BUY:
                    position.order_frozen_short = position.order_frozen_short + order.volume
                    position.order_frozen_today_short = position.order_frozen_today_short + order.volume
                    position.available_short = position.available_short - order.volume
                else:
                    raise_bultin_error('orderact')
        elif order.status in (OrderStatus.CANCELED, OrderStatus.REJECTED):
            if order.position_effect == OrderPositionEffect.OPEN:
                # 释放冻结的手续费和冻结的保证金，已经在外部计算好
                margin_frozen = -order.frozen_info.value
                fee_frozen = -order.frozen_info.fee
                order_frozen = order_frozen = margin_frozen + fee_frozen
            elif order.position_effect == OrderPositionEffect.CLOSE:
                # 更新仓位冻结信息
                if order.side == OrderSide.SELL:  # 多头卖平
                    position.order_frozen_long = position.order_frozen_long - order.volume
                    position.available_long = position.available_long + order.volume
                    if not env.is_old_order_rb(order.updated_time):
                        position.order_frozen_today_long = position.order_frozen_today_long - order.volume
                elif order.side == OrderSide.BUY:
                    # 空头卖平
                    position.order_frozen_short = position.order_frozen_short - order.volume
                    position.available_short = position.available_short + order.volume
                    if not env.is_old_order_rb(order.updated_time):
                        position.order_frozen_today_short = position.order_frozen_today_short - order.volume

        self._future_order_frozen = self._future_order_frozen + order_frozen
        self._future_margin_frozen = self._future_margin_frozen + margin_frozen
        self._future_cost_fee_frozen = self._future_cost_fee_frozen + fee_frozen
        return order_frozen

    # 处理订单信息
    def on_order(self, order_list: List[DQTBackOrder]):
        for order in order_list:
            if order.target_type == TargetType.STOCK:
                # 返回的order_frozen是下单冻结资金，为正说明是冻结，为负说明是解冻
                order_frozen = self.on_stock_order(order)
                self._raw_valid_cash -= order_frozen
            elif order.target_type == TargetType.FUTURE:
                # 返回的order_frozen是下单冻结资金，注意正负
                order_frozen = self.on_future_order(order)
                self._raw_valid_cash -= order_frozen
            else:
                raise_bultin_error('targettype')

    #  处理成交单，并对子账户以及仓位中的仓位记录/资金进行调整
    # 为了提高执行效率，函数中不再对可用资金进行检查
    # :param valid_cash: float可用资金
    # :param trade: order对象 成交单据
    # :return: valid_cash : 去掉成交额之后的可用资金
    #           realize_pnl: 平仓盈亏，如果是增仓则返回0
    #           last_cost: 实际手续费
    def _on_stock_trade(self, valid_cash: float, trade: DQTBackTrade):
        env = get_env()
        position: StockPosition = self.get_position(
            trade.target_index)  # type: StockPosition
        position.update_time = trade.created
        position.change_reason = PositionChangeReason.TRADE
        # 获取本次交易的成交额和成交手续费
        real_holding = trade.volume * trade.price
        real_fee = trade.frozen_info.trader_fee
        # 调整账户和仓位信息
        if trade.position_effect == OrderPositionEffect.OPEN and trade.side == OrderSide.BUY:
            order_frozen = trade.frozen_info.value + trade.frozen_info.fee
            fee_frozen = trade.frozen_info.fee
            # 调整账户的相关记录
            self._stock_order_frozen = self._stock_order_frozen - order_frozen  # 解冻资金
            self._stock_cost_fee_frozen = self._stock_cost_fee_frozen - fee_frozen  # 解冻手续费
            if position.volume_long_yd == 0 and len(position.holding_cost_today_long_list) == 0 and isnan(
                    position.create_long_time):
                # 建仓时间设定为对某个标的第一次成功下单的时间，当标的的某个仓位被强平之后也会重新计算的开仓时间
                # 约定: create_long_time 只有在回测开始和每天强平的时候才能够设定为pd.NaT
                position.create_long_time = trade.created
            # 重新计算持仓成本
            total_cost = trade.frozen_info.trader_value + trade.frozen_info.trader_fee
            # 注意，这里成交单会按照成交记录插入，不需要合并同价格项
            position.holding_cost_today_long_list.append(
                [total_cost, trade.volume])
            # 可用资金 = 原可用资金 + 解冻资金 - 实际成交额 - 手续费
            valid_cash = valid_cash + order_frozen - real_holding - real_fee
            realize_pnl = 0.0  # 开仓没有平仓盈亏
            position.available_long = position.available_long + trade.volume  # 可平仓位增加
            # 记录开仓均价
        elif trade.position_effect == OrderPositionEffect.CLOSE and trade.side == OrderSide.SELL:
            # 先平昨仓
            if position.volume_long_yd > 0 and trade.volume <= position.volume_long_yd:  # 平仓量小于昨仓
                # 平仓盈亏 = 持仓量*（平仓价- 持仓均价(开仓均价))
                realize_pnl = trade.volume * \
                              (trade.price - (position.holding_cost_long / position.volume_long_yd))
                if position.volume_long_yd == trade.volume:
                    position.volume_long_yd = 0
                    position.holding_cost_long = 0.0
                else:
                    # 调整持仓成本
                    position.holding_cost_long = position.holding_cost_long - \
                                                 trade.volume * trade.price + trade.frozen_info.trader_fee
                    # 调整昨仓持仓量
                    position.volume_long_yd = position.volume_long_yd - trade.volume
            else:  # 平仓量大于昨仓
                temp_volume = trade.volume - position.volume_long_yd
                realize_pnl = position.volume_long_yd * trade.price - \
                              position.holding_cost_long  # 成交额 - 持仓成本
                # 昨仓全部清空
                position.volume_long_yd = 0
                position.holding_cost_long = 0.0
                # 平今仓 按照FIFO的方式平仓
                clear_element = list()
                for i in range(len(position.holding_cost_today_long_list)):
                    if temp_volume <= position.holding_cost_today_long_list[i][1]:
                        # 平仓结束
                        realize_pnl = realize_pnl + temp_volume * trade.price - \
                                      position.holding_cost_today_long_list[i][0]
                        position.holding_cost_today_long_list[i][1] -= temp_volume
                        if position.holding_cost_today_long_list[i][1] == 0:
                            clear_element.append(i)  # 等待删除的订单序号
                            break  # 剩余仓位为0 不需要重进计算持仓均价直接退出
                        # 重新计算持仓均价
                        # 分摊手续费
                        partial_cost_fee = trade.frozen_info.trader_fee * temp_volume / trade.volume
                        # 持仓成本(未包含手续费）= 剩余持仓量 * 原持仓均价
                        holding_cost_temp = (position.holding_cost_today_long_list[i][1] - trade.volume) \
                                            * position.holding_cost_today_long_list[i][0] \
                                            / position.holding_cost_today_long_list[i][1]
                        # 持仓成本 = 持仓成本(未包含手续费) + 分摊手续费
                        position.holding_cost_today_long_list[i][0] = holding_cost_temp + \
                                                                      partial_cost_fee
                        # 平仓后剩余仓位
                        position.holding_cost_today_long_list[i][1] -= temp_volume
                        break  # 平仓结束
                    else:
                        # 平仓尚未结束，当前遍历到的今仓仓位会被全部释放
                        temp_volume = temp_volume - \
                                      position.holding_cost_today_long_list[i][1]
                        realize_pnl = realize_pnl + position.holding_cost_today_long_list[i][1] * trade.price - \
                                      position.holding_cost_today_long_list[i][0]
                        clear_element.append(i)  # 等待删除的订单序号
                [position.holding_cost_today_long_list.pop(
                    i) for i in clear_element[::-1]]
            # 调整仓位对象中的【总】冻结仓位信息
            position.order_frozen_long = position.order_frozen_long - trade.volume
            if not env.is_old_order_rb(trade.created):
                position.order_frozen_today_long = position.order_frozen_today_long - trade.volume
            # 可平仓位不变，因为这部分已经在冻结的时候减去了
            # 平仓下单，可用资金需要加上成交减去手续费
            valid_cash = valid_cash + trade.volume * trade.price - real_fee
        else:
            strategy = get_strategy()
            error = text.ERROR_ORDERED_OPERATOR.format(
                TARGET=strategy.target([trade.target_index]),
                TARGETTYPE=TargetType.to_str(trade.target_type),
                OFFSETFLAG=OrderPositionEffect.to_str(trade.position_effect),
                ORDERACT=OrderSide.to_str(trade.side))

            raise NotImplementedError(error)
        self._stock_daily_cost_fee += real_fee  # 累计手续费(包括开平)
        self.stock_total_cost_fee += real_fee
        self._stock_daily_realize_pnl = self._stock_daily_realize_pnl + realize_pnl
        return valid_cash, realize_pnl, real_fee

    # 处理期货成交记录，进行资金的结算和仓位的调整
    #     本函数不进行可用资金/可平仓位的检查，一定要在外部自行检查
    # :param valid_cash: 可用资金，可用资金包括原始可用资金和浮盈
    # :param trade: 成交记录对象
    # :return: valid_cash: 对于平仓，可用资金 = 原可用资金 + 平仓盈亏 + 释放保证金 - 手续费,对于开仓 = 原可用资金 - 开仓成本(保证金和手续费)
    #           profit: 仓位变动后新的持仓浮盈
    #           realize_pnl: 平仓盈亏
    #           last_cost: 交易手续费

    def _on_future_trade(self, valid_cash: float, trade: DQTBackTrade):
        # 计算平仓手续费，区分平金平昨
        # :param target_index:标的索引
        # :param volume: 待平仓位
        # :param price: 平仓价格
        # :param close_today: 平今仓
        # :return: 平仓手续费
        env = get_env()

        def calc_cost_fee_close(target_index: int, volume: int, price: float, close_today: bool):
            multiple = env.get_multiple(target_index)
            target_info = env.get_target_info(target_index)
            cost_fee_rate = target_info.trading_fee_close_today if close_today else target_info.trading_fee_close
            if cost_fee_rate <= 0.1:
                # 依据成交金额比例计算的手续费应该不会超过10%
                cost_fee = volume * price * multiple * cost_fee_rate
            else:
                cost_fee = volume * cost_fee_rate
            return cost_fee

        position: FuturePosition = self.get_position(trade.target_index)
        position.change_reason = PositionChangeReason.TRADE
        position.update_time = trade.created
        multiple = env.get_multiple(trade.target_index)
        # 调整账户和仓位信息
        real_fee = trade.frozen_info.trader_fee  # 成交手续费
        # 计算真实平仓手续费，分平金平昨
        realize_pnl = 0
        cost_fee_real_close = 0.0
        if trade.position_effect == OrderPositionEffect.OPEN:  # 开仓报单
            margin_frozen = trade.frozen_info.value  # 冻结保证金
            fee_frozen = trade.frozen_info.fee  # 冻结手续费
            order_frozen = margin_frozen + fee_frozen

            self._future_order_frozen -= order_frozen
            self._future_cost_fee_frozen -= fee_frozen
            self._future_margin_frozen -= margin_frozen

            real_margin = trade.frozen_info.trader_value  # 成交保证金
            if trade.side == OrderSide.BUY:  # 多仓买开
                if position.volume_long_yd == 0 and len(
                        position.holding_cost_today_long_list) == 0 and isnan(position.create_long_time):
                    # 建仓时间设定为对某个标的第一次成功下单的时间，当标的的某个仓位被强平之后也会重新计算的开仓时间
                    # 约定: dt_create_long_time只有在回测开始和每天强平的时候才能够设定为pd.NaT
                    position.create_long_time = trade.created
                # 注意，这里成交单会按照成交记录插入，不需要合并同价格项
                position.holding_cost_today_long_list.append([trade.price, trade.volume])
                # 可平仓位增加
                position.available_long = position.available_long + trade.volume
                # 持仓
                position.long_holding_total += trade.price * trade.volume * multiple
            elif trade.side == OrderSide.SELL:
                if position.volume_short_yd == 0 and len(position.holding_cost_today_short_list) == 0 and isnan(
                        position.create_short_time):
                    # 建仓时间设定为对某个标的第一次成功下单的时间，当标的的某个仓位被强平之后也会重新计算的开仓时间
                    # 约定: dt_create_short_time只有在回测开始和每天强平的时候才能够设定为pd.NaT
                    position.create_short_time = trade.created
                # 注意，这里成交单会按照成交记录插入，不需要合并同价格项
                position.holding_cost_today_short_list.append(
                    [trade.price, trade.volume])
                position.available_short = position.available_short + trade.volume  # 可平仓位增加
                # 持仓
                position.short_holding_total += trade.volume * trade.price * multiple
            else:
                raise_bultin_error('orderact')
            # 可用资金调整，可用资金 + 解冻资金 - 占用保证金 - 交易手续费  # 在回测中都是完全成交的，这里的计算valid不变, 如果有部分成交的情况才会改变
            valid_cash = valid_cash + order_frozen - real_margin - real_fee
            realize_pnl = 0.0  # 开仓没有平仓盈亏
        elif trade.position_effect == OrderPositionEffect.CLOSE:
            # 平仓前的保证金占用
            old_margin = self.future_margin(trade.target_index)
            if trade.side == OrderSide.SELL:  # 多头卖平仓位
                # 先平昨仓
                if trade.volume <= position.volume_long_yd:  # 平仓量小于昨仓
                    # 平仓盈亏 = 持仓量 *（平仓价- 持仓均价(开仓均价)) * 合约乘数
                    temp_holding_cost = trade.volume * position.holding_cost_long * multiple
                    realize_pnl = trade.volume * trade.price * multiple - temp_holding_cost
                    position.volume_long_yd = position.volume_long_yd - trade.volume
                    cost_fee_real_close += calc_cost_fee_close(
                        trade.target_index, trade.volume, trade.price, False)
                    # 持仓
                    position.long_holding_total -= temp_holding_cost
                    if position.volume_long_yd == 0:
                        position.holding_cost_long = 0.0
                else:  # 平仓量大于昨仓
                    temp_volume = trade.volume - position.volume_long_yd
                    # 平仓盈亏 = 持仓量 * (平仓价 - 持仓均价)
                    temp_holding_cost = position.volume_long_yd * position.holding_cost_long * multiple
                    realize_pnl = position.volume_long_yd * trade.price * multiple - temp_holding_cost
                    cost_fee_real_close += calc_cost_fee_close(trade.target_index, position.volume_long_yd, trade.price,
                                                               False)
                    position.volume_long_yd = 0  # 昨仓已空
                    # 持仓
                    position.long_holding_total -= temp_holding_cost
                    position.holding_cost_long = 0.0
                    # 昨仓平不完，需要平今仓 按照FIFO的方式平仓
                    clear_element = list()
                    for i in range(len(position.holding_cost_today_long_list)):
                        if temp_volume <= position.holding_cost_today_long_list[i][1]:
                            # 平仓完毕
                            temp_holding_cost = temp_volume * position.holding_cost_today_long_list[i][0] * multiple
                            realize_pnl = realize_pnl + temp_volume * trade.price * multiple - temp_holding_cost
                            cost_fee_real_close += calc_cost_fee_close(trade.target_index, temp_volume, trade.price,
                                                                       True)
                            # 更新仓位信息
                            position.holding_cost_today_long_list[i][1] -= temp_volume
                            # 持仓
                            position.long_holding_total -= temp_holding_cost
                            if position.holding_cost_today_long_list[i][1] == 0:
                                clear_element.append(i)  # 等待删除的订单序号
                            break  # 平仓完成不需要继续遍历
                            # 不像股票持仓均价不需要调整
                        else:
                            temp_volume = temp_volume - position.holding_cost_today_long_list[i][1]
                            temp_holding_cost = position.holding_cost_today_long_list[i][1] * \
                                                position.holding_cost_today_long_list[i][0] * multiple
                            realize_pnl = realize_pnl + position.holding_cost_today_long_list[i][
                                1] * trade.price * multiple - temp_holding_cost

                            cost_fee_real_close += calc_cost_fee_close(trade.target_index,
                                                                       position.holding_cost_today_long_list[i][1],
                                                                       trade.price, True)
                            # 持仓
                            position.long_holding_total -= temp_holding_cost
                            clear_element.append(i)  # 等待删除的订单序号
                    [position.holding_cost_today_long_list.pop(
                        i) for i in clear_element[::-1]]
                # 替换平仓手续费
                real_fee = cost_fee_real_close
                # 可平仓位不变
                # 调整仓位对象中的冻结信息
                position.order_frozen_long = position.order_frozen_long - trade.volume  # 冻结仓位【总】减少
                if not env.is_old_order_rb(trade.created):
                    position.order_frozen_today_long = position.order_frozen_today_long - trade.volume  # 冻结仓今仓减少
            elif trade.side == OrderSide.BUY:  # 空头买平仓位
                # 先平昨仓
                if trade.volume <= position.volume_short_yd:  # 平仓量小于昨仓
                    # 平仓盈亏 = 持仓量 *（平仓价- 持仓均价(开仓均价)) * 合约乘数
                    temp_holding_cost = trade.volume * position.holding_cost_short * multiple
                    realize_pnl = temp_holding_cost - trade.volume * trade.price * multiple
                    position.volume_short_yd = position.volume_short_yd - trade.volume
                    position.short_holding_total -= temp_holding_cost
                    cost_fee_real_close += calc_cost_fee_close(
                        trade.target_index, trade.volume, trade.price, False)
                    if position.volume_short_yd == 0:
                        position.holding_cost_short = 0.0
                else:  # 平仓量大于昨仓
                    temp_volume = trade.volume - position.volume_short_yd
                    # 平仓盈亏 = 持仓量 * (平仓价 - 持仓均价)
                    temp_holding_cost = position.volume_short_yd * position.holding_cost_short * multiple
                    realize_pnl = temp_holding_cost - position.volume_short_yd * trade.price * multiple
                    cost_fee_real_close += calc_cost_fee_close(trade.target_index, position.volume_short_yd,
                                                               trade.price, False)
                    position.volume_short_yd = 0  # 昨仓已空
                    position.short_holding_total -= temp_holding_cost
                    position.holding_cost_short = 0.0
                    # 昨仓平不完，需要平今仓 按照FIFO的方式平仓
                    clear_element = list()
                    for i in range(len(position.holding_cost_today_short_list)):
                        if temp_volume <= position.holding_cost_today_short_list[i][1]:
                            # 平仓完毕
                            temp_holding_cost = temp_volume * position.holding_cost_today_short_list[i][0] * multiple
                            realize_pnl = realize_pnl + temp_holding_cost - temp_volume * trade.price * multiple

                            cost_fee_real_close += calc_cost_fee_close(trade.target_index, temp_volume, trade.price,
                                                                       True)

                            position.holding_cost_today_short_list[i][1] -= temp_volume
                            position.short_holding_total -= temp_holding_cost
                            if position.holding_cost_today_short_list[i][1] == 0:
                                clear_element.append(i)  # 等待删除的订单序号
                            break
                        else:
                            temp_volume = temp_volume - position.holding_cost_today_short_list[i][1]

                            temp_holding_cost = position.holding_cost_today_short_list[i][1] * \
                                                position.holding_cost_today_short_list[i][0] * multiple

                            realize_pnl = realize_pnl + temp_holding_cost - position.holding_cost_today_short_list[i][
                                1] * trade.price * multiple

                            cost_fee_real_close += calc_cost_fee_close(trade.target_index,
                                                                       position.holding_cost_today_short_list[i][1],
                                                                       trade.price, True)

                            position.short_holding_total -= temp_holding_cost
                            clear_element.append(i)  # 等待删除的订单序号
                    [position.holding_cost_today_short_list.pop(
                        i) for i in clear_element[::-1]]
                # 替换平仓手续费
                real_fee = cost_fee_real_close
                # 可平仓位不变
                # 调整仓位对象中的冻结信息
                position.order_frozen_short = position.order_frozen_short - trade.volume  # 冻结仓位【总】减少
                if not env.is_old_order_rb(trade.created):
                    position.order_frozen_today_short = position.order_frozen_today_short - trade.volume  # 冻结仓今仓减少
            else:
                raise_bultin_error('orderact')
            new_margin = self.future_margin(trade.target_index)
            valid_cash = valid_cash + realize_pnl + (old_margin - new_margin) - real_fee
        else:
            raise NotImplementedError
        profit = self.future_holding_pnl()  # 仓位变动后计算新的持仓盈亏
        self._future_daily_realize_pnl = self._future_daily_realize_pnl + realize_pnl  # 计算累计平仓盈亏
        # print(f"target_index = {trade.target_index}  _daily_realize_pnl = {self._future_daily_realize_pnl}")
        self._future_daily_cost_fee = self._future_daily_cost_fee + real_fee
        self.future_total_cost_fee += real_fee
        return valid_cash, profit, realize_pnl, real_fee

    def on_trade(self, trades: List[DQTBackTrade]):
        env = get_env()
        for trade in trades:
            if trade.target_type == TargetType.STOCK:
                # DEBUG
                # print('stock: idx--%d side--%d volume--%d price--%f date--%s' % (
                #     trade.target_index, trade.side, trade.volume, trade.price, mft_to_str_format(trade.created)))
                try:
                    valid_cash, self._last_realized_pnl, self._last_cost = self._on_stock_trade(
                        self.valid_cash(trade.created), trade)
                    # 计算原始可用资金，实际上就是减去之前的持仓浮盈
                    self._raw_valid_cash = valid_cash - self._future_float_profit
                except NotImplementedError as e:
                    # todo 输出日志
                    pass
                    # write_log(str(e), level='error', use_args_for_console=True)
            elif trade.target_type == TargetType.FUTURE:
                # DEBUG
                # print('future: idx--%d side--%d volume--%d price--%f date--%s' % (
                #     trade.target_index, trade.side, trade.volume, trade.price, mft_to_str_format(trade.created)))
                valid_cash, profit, self._last_realized_pnl, self._last_cost = self._on_future_trade(
                    self.valid_cash(trade.created), trade)
                # 计算原始资金
                self._raw_valid_cash = valid_cash - self._future_float_profit
                self._future_float_profit = profit
            else:
                raise_bultin_error('targettype')
            # 计算最后一次资金变动

            self._last_amount = trade.volume * trade.price * env.get_multiple(
                trade.target_index) * self.get_margin_rate(trade.target_index, trade.side)

            self._change_reason = CashChangeReason.TRADE

    #  每一天的起始bar进行未完成订单的清理，仓位的转换和相关信息的更新
    #     对于股票主要进行一下操作：
    #     1、清除未完成订单，归还冻结资金(可选)
    #     2、今仓转昨仓，并进行持仓均价的计算
    #     3、清空冻结仓今仓
    #     4、可平仓位变动
    # :param clean_unfilled: 是否取消昨天未成交的订单, 并将冻结资金返还
    # :return: order_frozen: 返回冻结的资金，如果没有订单需要处理或者不处理都会返回为 0

    def _on_stock_settlement(self, clean_unfilled: bool = True) -> float:
        # # 逐个仓位进行更新
        for position in self._position.values():
            if position.type != TargetType.STOCK:
                continue
            # 每一个仓位都有两个部分持仓：今仓和昨仓，当日的交易可能会产生新的今仓，而昨仓则需要根据今仓转换成昨仓
            # 在这里，将当日持仓成本加入到昨仓成本中，同时将今仓转换成昨仓，并更新仓位可平量和冻结今仓。
            # 更新昨仓持仓成本,今仓转昨仓
            position: StockPosition = position
            for price, volume in position.holding_cost_today_long_list:
                position.holding_cost_long = position.holding_cost_long + price
                position.volume_long_yd = position.volume_long_yd + volume
            position.holding_cost_today_long_list.clear()  # 清空记录
            # 更新今可平仓量
            position.available_today_long = position.available_long
            # 清空冻结今仓(实际上就是冻结今仓转昨仓)
            position.order_frozen_today_long = 0

        # 清空上一个周期的浮盈
        self._stock_daily_realize_pnl = 0.0
        # 清空上一周期的统计手续费
        self._stock_daily_cost_fee = 0.0
        # 被释放的冻结资金
        total_order_frozen = 0.0
        # 取消未成交的订单，归还冻结仓位和冻结资金
        if clean_unfilled:
            # 释放所有冻结仓位
            for position in self._position.values():
                if position.type != TargetType.STOCK:
                    continue
                # 归还冻结仓位
                position.available_long += position.order_frozen_long
                position.available_today_long = position.available_long
                position.order_frozen_long = 0  # 释放冻结仓位
            # 冻结的下单资金
            total_order_frozen = self._stock_order_frozen  # 释放冻结保证金
            self._stock_order_frozen = 0.0
            self._stock_cost_fee_frozen = 0.0

        return total_order_frozen

    # 标的多头持仓量(单位：手)
    # :param target_index: 标的索引
    # :return: int 标的仓位
    def future_volume_long(self, target_index: int) -> int:
        position: FuturePosition = self.get_position(target_index)

        return position.volume_long_yd + sum((v for _, v in position.holding_cost_today_long_list))

    # 标的空头持仓量(单位：手)
    # :param target_index: 标的索引
    # :return: int 标的仓位
    def future_volume_short(self, target_index: int) -> int:
        position: FuturePosition = self.get_position(target_index)
        return position.volume_short_yd + sum((v for _, v in position.holding_cost_today_short_list))

    # 标的空头持仓量(单位：手)
    # :param target_index: 标的索引
    # :return: int 标的仓位
    def future_volume_long_today(self, target_index: int) -> int:
        position: FuturePosition = self.get_position(target_index)
        return sum((v for _, v in position.holding_cost_today_long_list))

    # 标的空头持仓量(单位：手)
    # :param target_index: 标的索引
    # :return: int 标的仓位
    def future_volume_short_today(self, target_index: int) -> int:
        position: FuturePosition = self.get_position(target_index)
        return sum((v for _, v in position.holding_cost_today_short_list))

    #  每一个回测周期调用本函数刷新一次
    #     本函数完成的工作包括：
    #     1、清除未完成订单，归还冻结资金(可选)
    #     2、今仓转昨仓，更新持仓均价
    #     3、清空冻结仓今仓
    #     5、昨结算盈亏计算
    #     对于期货，每一天都需要根据结算价计算当天的结算收益，并计算新的占用保证金
    #     这两个计算结果之和作为结算盈亏影响下一个交易日的可用结算资金
    # :param clean_unfilled : True:清除未完成订单， False:不清除
    # :return: order_frozen：释放的冻结资金，冻结资金包括冻结手续费和冻结保证金
    #           settle_pnl： 结算盈亏
    def _on_future_settlement(self, clean_unfilled: bool = True) -> tuple[float, float]:
        # 逐个仓位进行更新
        settle_pnl = 0.0
        env = get_env()
        for position in self._position.values():
            if position.type != TargetType.FUTURE:
                continue
            position: FuturePosition = position
            # 更新总开仓均价 结算后的开仓均价 = (昨仓开仓均价 * 开仓量 + 今仓开仓均价 * 开仓量 )/总持仓
            if len(position.holding_cost_today_long_list) > 0 and self.future_volume_long(position.target_index) > 0:
                total_cost = position.volume_long_yd * position.cost_long
                total_volume = position.volume_long_yd
                for price, volume in position.holding_cost_today_long_list:
                    total_cost = total_cost + price * volume
                    total_volume = total_volume + volume
                position.cost_long = total_cost / total_volume

            if len(position.holding_cost_today_short_list) > 0 and self.future_volume_short(position.target_index) > 0:
                total_cost = position.volume_short_yd * position.cost_short
                total_volume = position.volume_short_yd
                for price, volume in position.holding_cost_today_short_list:
                    total_cost = total_cost + price * volume
                    total_volume = total_volume + volume
                position.cost_short = total_cost / total_volume

            # 获取昨结价
            settle_price = env.settle_price(position.target_index, -1)

            multiple = env.get_multiple(position.target_index)
            # 计算旧的占用保证金(更新新的结算价之前的占用保证金)
            old_margin = self.future_margin(position.target_index)
            # 计算结算后的昨仓的持仓盈亏
            settle_pnl += (settle_price - position.holding_cost_long) * position.volume_long_yd * multiple

            settle_pnl += (position.holding_cost_short -
                           settle_price) * position.volume_short_yd * multiple
            # 计算结算后的今仓持仓盈亏，同时进行昨今仓位转换
            for p, v in position.holding_cost_today_long_list:
                settle_pnl = settle_pnl + (settle_price - p) * v * multiple
                position.volume_long_yd += v
            for p, v in position.holding_cost_today_short_list:
                settle_pnl = settle_pnl + (p - settle_price) * v * multiple
                position.volume_short_yd += v
            position.holding_cost_long = settle_price  # 新的昨仓多头持仓均价
            position.holding_cost_short = settle_price  # 新的今仓空头持仓均价
            position.holding_cost_today_long_list.clear()  # 清空多头今持仓记录
            position.holding_cost_today_short_list.clear()  # 清空空头今持仓记录
            # 新的多头/空头总持仓金额
            position.long_holding_total = position.holding_cost_long * position.volume(
                PositionSide.LONG) * multiple  # 昨仓转今仓，持仓成本统一更新为持仓价
            position.short_holding_total = position.holding_cost_short * position.volume(PositionSide.SHORT) * multiple
            # 计算新的保证金
            new_margin = self.future_margin(position.target_index)
            # 计算需要追加/返还的保证金
            settle_pnl = settle_pnl - (new_margin - old_margin)
            # 释放冻结今仓(今仓转昨仓)
            position.order_frozen_today_long = 0
            position.order_frozen_today_short = 0
        # 清空上一个周期的浮盈
        self._future_daily_realize_pnl = 0.0
        # print("_daily_realize_pnl ===  清空")
        # 清空上一周期的统计手续费
        self._future_daily_cost_fee = 0.0
        # 释放未完成订单的冻结保证金和手续费
        total_order_frozen = 0.0
        if clean_unfilled is True:
            # 释放所有冻结仓位
            for position in self._position.values():
                if position.type != TargetType.FUTURE:
                    continue
                position: FuturePosition = position
                # 订单取消，释放冻结仓位
                position.available_long += position.order_frozen_long
                position.available_short += position.order_frozen_short
                position.order_frozen_long = 0
                position.order_frozen_short = 0
            # 释放冻结资金
            total_order_frozen = self._future_order_frozen
            self._future_order_frozen = 0.0
            self._cost_fee_frozen = 0.0
            self._margin_frozen = 0.0
        return total_order_frozen, settle_pnl

    #  每一天起始bar调用本函数进行仓位转换，以及相关资金的调整
    # :param clean_unfilled:  是否取消昨日下单

    def on_settlement(self, clean_unfilled: bool = True):
        # 更新daily动态权益
        self._last_total_value = self.total_value
        # 股票账户日终清算, 获取返还的冻结资金并更新可用资金
        #  对应 order_frozen = self._stock_account.on_settlement(clean_unfilled)
        order_frozen = self._on_stock_settlement(clean_unfilled)
        self._raw_valid_cash += order_frozen

        # 对应 order_frozen, settle_pnl = self._future_account.on_settlement(clean_unfilled)
        # 期货账户日终结算资金包括，释放的冻结保证金 + 昨结算盈亏
        order_frozen, settle_pnl = self._on_future_settlement(clean_unfilled)
        self._raw_valid_cash += order_frozen
        self._raw_valid_cash += settle_pnl

    def reset_daily_close_time(self):
        """将当天停止交易时间设置为0"""
        self.daily_close_time = None

    def exist_daily_close_time(self):
        """判断用户是否设置当天停止交易时间"""
        return self.daily_close_time is not None


_account = None


def get_account():
    global _account
    if _account is None:
        _account = Account()
    return _account


def reset_account():
    global _account
    _account = None
