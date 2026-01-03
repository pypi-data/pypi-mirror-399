from typing import List, Dict
import pandas as pd
import dqtrader_rs
from dqtrader.enums import PositionSide
from dqtrader.strategy import get_strategy
from dqtrader.utils import common_utils


class RealAccount:
    #
    id: int
    #
    name: str
    # 可用资金
    _valid_cash: float
    # 下单冻结
    order_frozen: float
    # 总的冻结保证金
    total_margin_frozen: float
    # 期货保证金冻结
    future_margin_frozen: float
    # 静态权益
    static_value: float
    # 动态权益
    dynamic_equity: float
    # 总盈利
    total_profit: float
    # 持仓盈利
    total_holding_value: float
    # 股票持仓盈利
    stock_holding_value: float
    # 期货持仓盈利
    future_holding_value: float
    # 股票浮动盈亏
    stock_float_profit: float
    # 启动浮动盈亏
    future_float_profit: float
    # 期货平仓收益
    future_close_profit: float
    # 今日手续费
    today_commission_fee: float

    # order_book_id => long/short=>value
    _position: Dict[str, Dict[int, dqtrader_rs.PyPosition]]

    _order_dict: Dict[int, dqtrader_rs.PyOrder]

    user_id: int

    def __init__(self):
        self._valid_cash = 0.0
        self.order_frozen = 0.0
        self.total_margin_frozen = 0.0
        self.future_margin_frozen = 0.0
        self.static_value = 0.0
        self.dynamic_equity = 0.0
        self.total_profit = 0.0
        self.total_holding_value = 0.0
        self.stock_holding_value = 0.0
        self.future_holding_value = 0.0
        self.stock_float_profit = 0.0
        self.future_float_profit = 0.0
        self.future_close_profit = 0.0
        self.today_commission_fee = 0.0
        self.user_id = 0
        self._position = {}
        self._order_dict = {}

    def init_from_sim_account(self, sim_info):
        self.id = sim_info.id
        self.name = sim_info.name

    def load_equity(self):
        equity_info = dqtrader_rs.get_account_equity(self.id)
        self.update_equity(equity_info)

    def update_equity(self, equity_info):
        self._valid_cash = equity_info.valid_cash
        self.order_frozen = equity_info.order_frozen
        self.total_margin_frozen = equity_info.total_margin_frozen
        self.future_margin_frozen = equity_info.future_margin_frozen
        self.static_value = equity_info.static_value
        self.dynamic_equity = equity_info.dynamic_equity
        self.total_profit = equity_info.total_profit
        self.total_holding_value = equity_info.total_holding_value
        self.stock_holding_value = equity_info.stock_holding_value
        self.future_holding_value = equity_info.future_holding_value
        self.stock_float_profit = equity_info.stock_float_profit
        self.future_float_profit = equity_info.future_float_profit
        self.future_close_profit = equity_info.future_close_profit
        self.today_commission_fee = equity_info.today_commission_fee

    def valid_cash(self):
        return self._valid_cash

    # 加载所有委托单
    def load_all_entrusting_order(self):
        # 1 全部成交，2 委托中，3 撤单，4 拒单
        orders = dqtrader_rs.get_account_order(self.id, 2)
        for order in orders:
            self._order_dict[order.client_order_id] = order

    def get_all_position(self):
        return self._position

    def get_all_order(self):
        return self._order_dict.values()

    def has_order(self, order_id: int) -> bool:
        return order_id in self._order_dict

    def update_order(self, order_id):
        #
        order = dqtrader_rs.get_order_by_id(self.id, order_id)
        if order is None:
            self._order_dict.pop(order_id, None)
            return None
        # 判断是不是成交
        if order.order_status == 2:
            self._order_dict[order_id] = order
            return None
        else:
            self._order_dict.pop(order_id, None)
            return order

    #
    def update_position(self):
        positions = dqtrader_rs.get_account_position(self.id)
        self._position = {}
        for position in positions:
            # 这里要判断当前的是否有
            order_book_id = f"{position.market}.{position.code}"
            if order_book_id not in self._position:
                self._position[order_book_id] = {}
            position_dir_dict = self._position[order_book_id]
            position_dir_dict[position.position_dir] = position

    def volume_long(self, target_index: int = -1) -> pd.Series | int:
        return self._volume_with_position_side(PositionSide.LONG, target_index)

    def volume_short(self, target_index: int = -1) -> pd.Series | int:
        return self._volume_with_position_side(PositionSide.SHORT, target_index)




    def _volume_with_position_side(self, position_side: PositionSide, target_index: int = -1) -> pd.Series | int:
        strategy = get_strategy()
        if target_index != -1:
            target = strategy.get_real_target(target_index)
            #  获取真实得

            target = target.lower()
            position_dict = self._position.get(target, None)
            if position_dict is None:
                return 0
            position = position_dict.get(position_side, None)
            if position is None:
                return 0
            return position.position
        # 后去全部
        volume_arr = []
        real_targets = strategy.get_all_real_target()
        for index, target in enumerate(real_targets):
            target = target.lower()
            position_dir_dict = self._position.get(target, None)
            if position_dir_dict is None:
                volume_arr.append(0)
                continue
            position = position_dir_dict.get(position_side, None)
            if position_dir_dict is None:
                volume_arr.append(0)
                continue
            volume_arr.append(position.position)
        return pd.Series(volume_arr)

    def available_long(self, target_index: int = -1) -> pd.Series | int:
        return self._available_with_position_side(PositionSide.LONG, target_index)

    def available_short(self, target_index: int = -1) -> pd.Series | int:
        return self._available_with_position_side(PositionSide.SHORT, target_index)

    def _available_with_position_side(self, position_side: PositionSide, target_index: int = -1) -> pd.Series | int:
        strategy = get_strategy()
        if target_index != -1:
            target = strategy.get_real_target(target_index)
            position_dict = self._position.get(target, None)
            if position_dict is None:
                return 0
            position = position_dict.get(position_side, None)
            if position is None:
                return 0
            if common_utils.is_stock(position.market):
                return position.yd_position - position.close_order_frozen
            else:
                return position.position - position.close_order_frozen
        # 获取全部
        volume_arr = []
        real_targets = strategy.get_all_real_target()
        for index, target in enumerate(real_targets):
            target = target.lower()
            position_dir_dict = self._position.get(target, None)
            if position_dir_dict is None:
                volume_arr.append(0)
                continue
            position = position_dir_dict.get(position_side, None)
            if position_dir_dict is None:
                volume_arr.append(0)
                continue
            if common_utils.is_stock(position.market):
                volume_arr.append(position.yd_position - position.close_order_frozen)
            else:
                volume_arr.append(position.position - position.close_order_frozen)
        return pd.Series(volume_arr)

    def is_order_unfilled(self, order_id: int) -> bool:
        return self._order_dict.get(order_id, None) is not None


_accounts: List[RealAccount] = []


def init_accounts(account_names: List[str]):
    account_name_dict = {}
    for account_name in account_names:
        account_name_dict[account_name.lower()] = True
    sim_accounts = dqtrader_rs.get_all_account()

    for sim_account in sim_accounts:
        account_name = sim_account.name.lower()
        if account_name in account_name_dict:
            account_ins = RealAccount()
            account_ins.user_id = sim_account.user_id
            account_ins.init_from_sim_account(sim_account)
            account_ins.load_all_entrusting_order()
            account_ins.load_equity()
            account_ins.update_position()
            _accounts.append(account_ins)
    if len(_accounts) == 0:
        raise Exception("无可用账号！")


def get_account(index: int = 0):
    return _accounts[index]


def get_all_account():
    return _accounts


def get_account_by_id(account_id: int):
    for account in _accounts:
        if account.id == account_id:
            return account
    return None


def get_all_account_id():
    account_ids = []
    for account in _accounts:
        account_ids.append(account.id)
    return account_ids


def get_all_account_subscribe_tag():
    tags = []
    for account in _accounts:
        tags.append(f"{account.user_id}-{account.id}")
        # account_ids.append(account.id)
    return tags
