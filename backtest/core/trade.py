from typing import Dict, List

from backtest.core.data import Data
from backtest.model.constant import OrderSide, TimeFrame, OrderStatus, PositionSide, EventType
from backtest.model.order import Order
from backtest.model.position import Position
from backtest.util.event import Event


class Trade:
    def __init__(self, data: Data, strategy_id: int, symbol: str, time_frame: int, events_dict: Dict[int, Event]):
        self.__data: Data = data
        self.__strategy_id: int = strategy_id
        self.__symbol: str = symbol
        self.__time_frame: int = time_frame
        self.__event_dict: Dict[int, Event] = events_dict

        self.__orders_dict: Dict[int, Order] = {}
        self.__position = Position(self.__strategy_id, self.__symbol, self.__time_frame, price_precision)
        self.__position.price_precision = self.__data.get_price_precision(self.__symbol)

    def __handle_position(self, order: Order):
        if order.reduce_only:
            self.__position.exit_orders.append(order)
            if 100 == self.__position.exit_percentage:
                on_new_closed_position = self.__event_dict[EventType.NEW_CLOSED_POSITION]
                on_new_closed_position(position=self.__position)

                self.__position = Position(self.__strategy_id, self.__symbol, self.__time_frame)
                self.__position.price_precision = self.__data.get_price_precision(self.__symbol)
        else:
            self.__position.entry_orders.append(order)
            if 1 == len(self.__position.entry_orders):
                on_new_open_position = self.__event_dict[EventType.NEW_OPEN_POSITION]
                on_new_open_position(position=self.__position)

    def __handle_order(self, order):
        # stop orders
        if order.stop_price and not order.is_activated and self.__data.is_price_touched(order.symbol, order.stop_price):
            order.is_activated = True

        # limit and market and activated stop orders
        if order.is_activated and (order.price is None or self.__data.is_price_touched(order.symbol, order.price)):
            order.status = OrderStatus.FILLED
            order.close_timestamp = self.__data.timestamp
            order.filled_price = order.price if order.price else self.__data.get_market_price(order.symbol)
            del self.__orders_dict[order.id]

            on_new_filled_order = self.__event_dict[EventType.NEW_FILLED_ORDER]
            on_new_filled_order(order=order)

            self.__handle_position(order)

    def next(self):
        for order in list(self.__orders_dict.values()):
            self.__handle_order(order)

        last_candle = self.__data.get_last_candle(self.__symbol)
        self.__position.maximum_met_price = max(self.__position.maximum_met_price, last_candle.high)
        self.__position.minimum_met_price = min(self.__position.minimum_met_price, last_candle.low)

    @property
    def symbol(self) -> str:
        return self.__symbol

    @property
    def time_frame(self) -> TimeFrame:
        return self.__time_frame

    @property
    def open_orders(self) -> List[Order]:
        return self.__orders_dict

    def set_order(self, side: OrderSide, percentage: float, price: float = None, stop_price: float = None,
                  reduce_only: bool = None, comment: str = '') -> Order:
        order = Order(side, percentage, price, stop_price, reduce_only, comment)
        order.strategy_id = self.__strategy_id
        order.symbol = self.__symbol
        order.time_frame = self.__time_frame
        order.status = OrderStatus.OPEN
        order.open_timestamp = self.__data.timestamp
        self.__orders_dict[order.id] = order

        on_new_open_order = self.__event_dict[EventType.NEW_OPEN_ORDER]
        on_new_open_order(order=order)

        return order

    def entry(self, side: PositionSide, percentage: float, price: float = None, stop_price: float = None,
              comment: str = '') -> Order:
        return self.set_order(side=side, percentage=percentage, price=price, stop_price=stop_price,
                              reduce_only=False, comment=comment)

    def exit(self, percentage: float = 100, price: float = None, stop_price: float = None, comment: str = '') -> Order:
        close_side = self.position.side * -1
        return self.set_order(side=close_side, percentage=percentage, price=price, stop_price=stop_price,
                              reduce_only=True, comment=comment)

    def get_order(self, order_id: int) -> Order:
        if order_id in self.__orders_dict:
            return self.__orders_dict[order_id]
        else:
            raise Exception('There is no open order with id {}'.format(order_id))

    def cancel_order(self, order_id: int):
        if order_id in self.__orders_dict:
            order = self.__orders_dict[order_id]
            order.status = OrderStatus.CANCELED
            order.close_timestamp = self.__data.timestamp
            del self.__orders_dict[order_id]

            on_new_canceled_order = self.__event_dict[EventType.NEW_CANCELED_ORDER]
            on_new_canceled_order(order=order)

        else:
            raise Exception('There is no open order with id {}'.format(order_id))

    def cancel_all_orders(self) -> bool:
        for order_id in self.__orders_dict.keys():
            self.cancel_order(order_id)

    @property
    def position(self) -> Position:
        return self.__position
