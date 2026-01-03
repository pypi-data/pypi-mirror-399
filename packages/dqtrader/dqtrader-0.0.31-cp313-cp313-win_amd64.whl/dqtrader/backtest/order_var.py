
from typing import Dict, List

from dqtrader.entity import DQTBackOrder, DQTBackStopOrder, DQTBackTrade






class OrderVar:
    order_index: int = 0
    # 所有订单数量
    order_list: List[DQTBackOrder] = []
    order_dict: Dict[int, DQTBackOrder] = {}
    # 未成交的单
    unfilled_order_list: List[DQTBackOrder] = []
    unfilled_order_dict: Dict[int, DQTBackOrder] = {}
    # 止损单
    stop_order_list: List[DQTBackStopOrder] = []
    stop_order_dict: Dict[int, DQTBackStopOrder] = {}
    # 未触发的撤单
    unfired_stop_order_list: List[DQTBackStopOrder] = []
    unfired_stop_order_dict: Dict[int, DQTBackStopOrder] = {}

    trade_list: List[DQTBackTrade] = []


    # def reset():
    #     OrderVar.order_index = 0
    #     OrderVar.order_list = []
    #     OrderVar.order_dict = {}
    #     OrderVar.unfilled_order_list = []
    #     OrderVar.unfilled_order_dict = {}
    # #
    #     OrderVar.stop_order_list = []
    #     OrderVar.stop_order_dict = {}
    #
    #     OrderVar.unfired_stop_order_list = []
    #     OrderVar.unfired_stop_order_dict = {}
    #
    #     OrderVar.trade_list = {}
    def gen_order_id() -> int:
        OrderVar.order_index += 1
        return OrderVar.order_index

    def append_order(order: DQTBackOrder):
        OrderVar.order_dict[order.order_id] = order
        OrderVar.order_list.append(order)

    def get_order(order_id: int) -> DQTBackOrder:
        return OrderVar.order_dict.get(order_id)

    # 判断订单是否存在
    def exist_order(order_id: int) -> bool:
        return order_id in OrderVar.order_dict

    def get_all_order() -> List[DQTBackOrder]:
        return OrderVar.order_list

    def append_trade(trade: DQTBackTrade):
        OrderVar.trade_list.append(trade)

    def get_all_trade() -> List[DQTBackTrade]:
        return OrderVar.trade_list

    def batch_get_order(order_ids: List[int]) -> List[DQTBackOrder]:
        order_list: List[DQTBackOrder] = []
        for order_id in order_ids:
            order = OrderVar.order_dict.get(order_id)
            if order is None:
                continue
            order_list.append(order)
        return order_list

    def append_unfilled_order(order: DQTBackOrder):
        OrderVar.unfilled_order_dict[order.order_id] = order
        OrderVar.unfilled_order_list.append(order)

    # 判断是否存在未成交订单
    def exist_unfilled_order() -> bool:
        return len(OrderVar.unfilled_order_dict) != 0

    def is_unfilled_order(order_id: int) -> bool:
        return order_id in OrderVar.unfilled_order_dict

    def get_all_unfilled_order() -> List[DQTBackOrder]:
        return OrderVar.unfilled_order_list

    def batch_remove_unfilled_order(order_ids: List[int]):
        for order_id in order_ids:
            OrderVar.remove_unfilled_order(order_id)


    # 删除未触发的撤单
    def remove_unfilled_order(order_ids: List[int]):
        # print(f"order_ids = {len(order_ids)}")
        for order_id in order_ids:
          OrderVar.unfilled_order_dict.pop(order_id, None)
          i = 0
          for order in OrderVar.unfilled_order_list:
            if order.order_id == order_id:
              del OrderVar.unfilled_order_list[i]
              break
            i += 1

    def append_stop_order(order: DQTBackStopOrder):
        OrderVar.stop_order_dict[order.stop_order_id] = order
        OrderVar.stop_order_list.append(order)

    def batch_get_stop_order(stop_order_ids: List[int]) -> List[DQTBackStopOrder]:
        order_list: List[DQTBackStopOrder] = []
        for stop_order_id in stop_order_ids:
            order = OrderVar.stop_order_dict.get(stop_order_id, None)
            if order is None:
                continue
            order_list.append(order)
        return order_list

    def append_unfired_stop_order(order: DQTBackStopOrder):
        OrderVar.unfired_stop_order_dict[order.stop_order_id] = order
        OrderVar.unfired_stop_order_list.append(order)

    # 删除未触发的撤单
    def remove_unfired_stop_order(stop_order_id: int):
        OrderVar.unfired_stop_order_dict.pop(stop_order_id, None)
        i = 0
        for order in OrderVar.unfired_stop_order_list:
            if order.stop_order_id == stop_order_id:
                del OrderVar.unfired_stop_order_list[i]
                break
            i += 1

    def exist_unfired_order() -> bool:
        return len(OrderVar.unfired_stop_order_list) != 0

    def get_unfired_stop_order(stop_order_id: int) -> DQTBackStopOrder:
        return OrderVar.unfired_stop_order_dict.get(stop_order_id, None)

    def get_unfired_stop_order_by_target_id(target_order_id: int) -> List[DQTBackStopOrder]:
        orders: List[DQTBackStopOrder] = []
        for order in OrderVar.unfired_stop_order_list:
            if order.target_order_id == target_order_id:
                orders.append(order)
        return orders

    def get_all_unfired_stop_order() -> List[DQTBackStopOrder]:
        return OrderVar.unfired_stop_order_list

    def clear_all_unfired_stop_order():
        OrderVar.unfired_stop_order_list = []
        OrderVar.unfired_stop_order_dict = {}

    def batch_get_unfired_stop_order(stop_order_ids: List[int]) -> List[DQTBackStopOrder]:
        order_list: List[DQTBackStopOrder] = []
        for stop_order_id in stop_order_ids:
            order = OrderVar.unfired_stop_order_dict.get(stop_order_id, None)
            if order is None:
                continue
            order_list.append(order)
        return order_list

    def clear_data():
        OrderVar.order_index = 0
        OrderVar.order_list = []
        OrderVar.order_dict = {}
        OrderVar.unfilled_order_list = []
        OrderVar.unfilled_order_dict = {}
    #
        OrderVar.stop_order_list = []
        OrderVar.stop_order_dict = {}
        OrderVar.unfired_stop_order_list = []
        OrderVar.unfired_stop_order_dict = {}

        OrderVar.trade_list = []
