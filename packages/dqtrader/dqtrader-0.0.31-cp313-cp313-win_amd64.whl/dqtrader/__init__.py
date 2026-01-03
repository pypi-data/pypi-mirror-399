from typing import Dict, List
from .api.history import *
from .api import history as history_api, utils
from . import backtest
from .backtest import order as backtest_order
from .realtrade import order as realtrade_order
from . import realtrade
from . import calcfactor
from .enums import *
from . import enums as enum_api
from pandas import DataFrame
from . import fmt

from .backtest.api import get_performance, get_tab_strategy_id, get_tab_factor_id

from .calcfactor.api import *
from .calcfactor import api as calcfactor_api

__all__ = [
    *history_api.__all__,
    *enum_api.__all__,
    *calcfactor_api.__all__,
    "get_account",
    "get_current_bar",
    "run_backtest",
    "run_realtrade",
    "run_factor",
    "get_reg_kdata",
    "reg_kdata",
    "fmt",
    "get_tab_strategy_id",
    "get_tab_factor_id",
    "get_performance",
    'order_volume',
    'order_value',
    'order_percent',
    'order_target_volume',
    'order_target_value',
    'order_close_all',
    'order_cancel_all',
    'order_cancel',
    'order_target_percent',
    'stop_trailing_by_order',
    'stop_profit_by_order',
    'stop_loss_by_order',
    "get_reg_factor",
    "get_reg_custom_factor"
]
is_real_trade = False
_get_reg_kdata_func = None
_reg_kdata = None
_get_account = None
_get_current_bar = None
#  下单的函数
_order_volume = None
_order_value = None
_order_percent = None
_order_target_volume = None
_order_target_value = None
_order_close_all = None
_order_cancel_all = None
_order_cancel = None
_order_target_percent = None
_stop_trailing_by_order = None
_stop_cancel = None
_stop_profit_by_order = None
_stop_loss_by_order = None


def _set_run_backtest_env():
    global _get_reg_kdata_func
    global _reg_kdata
    global _get_account
    global _get_current_bar
    #
    global _order_volume
    global _order_value
    global _order_percent
    global _order_target_volume
    global _order_target_value
    global _order_close_all
    global _order_cancel_all
    global _order_cancel
    global _order_target_percent
    global _stop_trailing_by_order
    global _stop_cancel
    global _stop_profit_by_order
    global _stop_loss_by_order
    global is_real_trade

    is_real_trade = False

    _get_reg_kdata_func = backtest.api.get_reg_kdata
    _reg_kdata = backtest.api.reg_kdata
    _get_account = backtest.get_account
    _get_current_bar = backtest.api.get_current_bar
    #
    _order_volume = backtest_order.order_volume
    _order_value = backtest_order.order_value
    _order_percent = backtest_order.order_percent
    _order_target_volume = backtest_order.order_target_volume
    _order_target_value = backtest_order.order_target_value
    _order_close_all = backtest_order.order_close_all
    _order_cancel_all = backtest_order.order_cancel_all
    _order_cancel = backtest_order.order_cancel
    _order_target_percent = backtest_order.order_target_percent
    _stop_trailing_by_order = backtest_order.stop_trailing_by_order
    _stop_cancel = backtest_order.stop_cancel
    _stop_profit_by_order = backtest_order.stop_profit_by_order
    _stop_loss_by_order = backtest_order.stop_loss_by_order


def _set_run_realtrade_env():
    global _get_reg_kdata_func
    global _reg_kdata
    global _get_account
    global _get_current_bar
    #
    global _order_volume
    global _order_value
    global _order_percent
    global _order_target_volume
    global _order_target_value
    global _order_close_all
    global _order_cancel_all
    global _order_cancel
    global _order_target_percent
    global _stop_trailing_by_order
    global _stop_cancel
    global _stop_profit_by_order
    global _stop_loss_by_order
    global is_real_trade

    is_real_trade = True

    _get_reg_kdata_func = realtrade.api.get_reg_kdata
    _reg_kdata = realtrade.api.reg_kdata
    _get_account = realtrade.real_account.get_account
    _get_current_bar = realtrade.api.get_current_bar

    #
    _order_volume = realtrade_order.order_volume
    _order_value = realtrade_order.order_value
    _order_percent = realtrade_order.order_percent
    _order_target_volume = realtrade_order.order_target_volume
    _order_target_value = realtrade_order.order_target_value
    _order_close_all = realtrade_order.order_close_all
    _order_cancel_all = realtrade_order.order_cancel_all
    _order_cancel = realtrade_order.order_cancel
    _order_target_percent = realtrade_order.order_target_percent

    # _stop_trailing_by_order = realtrade_order.stop_trailing_by_order
    # _stop_cancel = realtrade_order.stop_cancel
    # _stop_profit_by_order = realtrade_order.stop_profit_by_order
    # _stop_loss_by_order = realtrade_order.stop_loss_by_order


def get_reg_kdata(reg_idx: int, target_list: List[str] = [], length: int = 1, fill_up: bool = False, df=False):
    global _get_reg_kdata_func
    return _get_reg_kdata_func(reg_idx, target_list, length, fill_up, df)


def get_reg_factor(reg_idx: int, target_list: List[str] = [], length: int = 1) -> DataFrame:
    global is_real_trade
    if is_real_trade:

        return calcfactor_api.get_realtrade_reg_factor(reg_idx=reg_idx,
                                                       target_list=target_list, length=length)
    else:
        return calcfactor_api.get_backtest_reg_factor(reg_idx=reg_idx,
                                                      target_list=target_list, length=length)


def get_reg_custom_factor(reg_idx: int, target_list: List[str] = [], length: int = 1) -> DataFrame:
    global is_real_trade
    if is_real_trade:
        return calcfactor_api.get_realtrade_reg_custom_factor(reg_idx=reg_idx, target_list=target_list, length=length)
    else:
        return calcfactor_api.get_backtest_reg_custom_factor(reg_idx=reg_idx, target_list=target_list, length=length)


# "get_reg_factor",
# "get_reg_custom_factor"

def get_current_bar(target_list=None):
    global _get_current_bar
    return _get_current_bar(target_list)


def get_account():
    global _get_account
    return _get_account()


def reg_kdata(frequency: str, frequency_num: int, adjust=False):
    global _reg_kdata
    _reg_kdata(frequency, frequency_num, adjust)


def order_volume(target_index: int, volume: int, side: OrderSide, position_effect: OrderPositionEffect,
                 order_type: OrderType, price: float) -> int | None:
    # global _order_volume
    global is_real_trade
    if is_real_trade:
        realtrade_order.order_volume(0, target_index, volume, side, position_effect, order_type, price)
    else:
        backtest_order.order_volume(target_index, volume, side, position_effect, order_type, price)


def order_value(target_index: int,
                value: float,
                side: OrderSide,
                position_effect: OrderPositionEffect,
                order_type: OrderType,
                price: float = 0.0) -> List[int]:
    # global _order_value
    global is_real_trade

    if is_real_trade:
        realtrade_order.order_value(0, target_index, value, side, position_effect, order_type, price)
    else:
        return backtest_order.order_value(target_index, value, side, position_effect, order_type, price)


def order_percent(target_index: int,
                  percent: float,
                  side: OrderSide,
                  position_effect: OrderPositionEffect,
                  order_type: OrderType,
                  price: float = 0.0) -> List[int] | int | None:
    # global _order_percent
    global is_real_trade
    if is_real_trade:
        return realtrade_order.order_percent(0, target_index, percent, side, position_effect, order_type, price)
    else:
        return backtest_order.order_percent(target_index, percent, side, position_effect, order_type, price)


def order_target_volume(target_index: int,
                        target_volume: int,
                        side: PositionSide,
                        order_type: OrderType,
                        price: float = 0.0) -> List[int]:
    # global _order_target_volume
    global is_real_trade
    if is_real_trade:
        return realtrade_order.order_target_volume(0, target_index, target_volume, side, order_type, price)
    else:
        return backtest_order.order_target_volume(target_index, target_volume, side, order_type, price)


def order_target_value(
        target_index: int,
        target_value: float,
        side: OrderSide,
        order_type: OrderType,
        price: float = 0.0) -> List[int]:
    # global _order_target_value
    global is_real_trade
    if is_real_trade:
        return realtrade_order.order_target_value(0, target_index, target_value, side, order_type, price)
    else:
        return backtest_order.order_target_value(target_index, target_value, side, order_type, price)


def order_target_percent(target_index: int,
                         target_percent: float,
                         side: OrderSide | PositionSide,
                         order_type: OrderType,
                         price: float = 0.0) -> List[int]:
    global is_real_trade
    if is_real_trade:
        return realtrade_order.order_target_percent(0, target_index, target_percent, side, order_type, price)
    else:
        return backtest_order.order_target_percent(target_index, target_percent, side, order_type, price)


def order_close_all():
    global _order_close_all
    _order_close_all()


def order_cancel_all():
    global is_real_trade
    if is_real_trade:
        account_ids = realtrade.real_account.get_all_account_id()
        realtrade_order.order_cancel_all(account_ids)
    else:
        backtest_order.order_cancel_all()


def order_cancel(order_ids: List[int]):
    global _order_cancel
    _order_cancel(order_ids)


def stop_trailing_by_order(target_order_id: int,
                           stop_gap_type: OrderStopType,
                           stop_gap: float,
                           trailing_gap: int,
                           trailing_gap_type: OrderStopTrailingType,
                           order_type: OrderType):
    # global _stop_trailing_by_order
    global is_real_trade
    if is_real_trade:
        return
    backtest_order.stop_trailing_by_order(target_order_id, stop_gap_type, stop_gap, trailing_gap, trailing_gap_type,
                                          order_type)


def stop_profit_by_order(
        target_order_id: int,
        stop_gap_type: OrderStopType,
        stop_gap: float,
        order_type: OrderType):
    # global _stop_profit_by_order
    global is_real_trade
    if is_real_trade:
        return
    backtest_order.stop_profit_by_order(target_order_id, stop_gap_type, stop_gap, order_type)


def stop_loss_by_order(
        target_order_id: int,
        stop_gap_type: OrderStopType,
        stop_gap: float,
        order_type: OrderType) -> int:
    # global _stop_loss_by_order
    global is_real_trade
    if is_real_trade:
        return 0
    backtest_order.stop_loss_by_order(target_order_id, stop_gap_type, stop_gap, order_type)


def run_backtest(config: Dict, init, on_bar, on_order_status=None, on_order_execution=None):
    _set_run_backtest_env()
    return backtest.run_backtest(config, init, on_bar, on_order_status, on_order_execution)


def run_realtrade(config: Dict, init, on_bar, on_order_status=None):
    _set_run_realtrade_env()
    realtrade.run_realtrade(config, init, on_bar, on_order_status)


def run_factor(config: Dict, init, calc_factor):
    _set_run_backtest_env()
    return calcfactor.run_factor(config, init, calc_factor)
