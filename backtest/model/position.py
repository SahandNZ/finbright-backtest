import math
import uuid
from datetime import datetime
from typing import List

from backtest.model.constant import PositionSide, TimeFrame, OrderSide
from backtest.model.order import Order
from tabulate import tabulate


class Position:
    @staticmethod
    def from_kafka(position):
        instance = Position(position.strategy_id, position.symbol, position.time_frame, id=position.id)
        instance.set_properties(position.side, position.entry_timestamp, position.entry_percentage,
                                position.entry_price, position.exit_timestamp, position.exit_price,
                                position.profit_percenrage, position.run_up, position.drawdown)
        return instance

    def __init__(self, strategy_id: int, symbol: str, time_frame: int, id: int = None):
        # unique identifiers
        self.__id: int = id if id is not None else uuid.uuid4()
        self.__strategy_id: int = strategy_id
        self.__symbol: str = symbol
        self.__time_frame: TimeFrame = time_frame

        # backtest fields
        self.maximum_met_price: float = -math.inf
        self.minimum_met_price: float = math.inf
        self.entry_orders: List[Order] = []
        self.exit_orders: List[Order] = []
        self.price_precision: int = None
        self.quantity_precision: int = None

        # private properties
        self.__side: OrderSide = None
        self.__entry_timestamp: int = None
        self.__entry_datetime: datetime = None
        self.__entry_percentage: int = None
        self.__entry_price: float = None
        self.__exit_timestamp: datetime = None
        self.__exit_datetime: datetime = None
        self.__exit_price: float = None
        self.__profit_percentage: float = None
        self.__run_up_percentage: float = None
        self.__drawdown_percentage: float = None
        self.__bars: int = None

        # quantity related properties
        self.equity: float = None
        self.paid_fee: float = None
        self.quantity: float = None
        self.profit: float = None
        self.run_up: float = None
        self.drawdown: float = None

    def set_properties(self, side: OrderSide, entry_timestamp: int, entry_percentage: int, entry_price: float,
                       exit_timestamp: int, exit_price: float, profit_percentage: float, run_up_percentage: float,
                       drawdown_percentage: float):
        self.__side: OrderSide = side
        self.__entry_timestamp: int = entry_timestamp
        self.__entry_datetime: datetime = datetime.fromtimestamp(entry_timestamp)
        self.__entry_percentage: float = entry_percentage
        self.__entry_price: float = entry_price
        self.__exit_timestamp: int = exit_timestamp
        self.__exit_datetime: datetime = datetime.fromtimestamp(exit_timestamp)
        self.__exit_price: float = exit_price
        self.__profit_percentage: float = profit_percentage
        self.__run_up_percentage: float = run_up_percentage
        self.__drawdown_percentage: float = drawdown_percentage

    def set_quantity(self, quantity: float):
        self.equity = round(self.entry_price * self.quantity, 2)
        self.set_equity(self.equity)

    def set_equity(self, equity: float):
        self.equity = equity
        self.quantity = (self.equity / self.entry_price, self.quantity_precision)
        self.profit = round(self.profit_percentage / 100 * self.equity, 2)
        self.run_up = round(self.run_up_percentage / 100 * self.equity, 2)
        self.drawdown = round(self.drawdown_percentage / 100 * self.equity, 2)

    @property
    def id(self) -> int:
        return self.__id

    @property
    def strategy_id(self) -> int:
        return self.__strategy_id

    @property
    def symbol(self) -> str:
        return self.__symbol

    @property
    def time_frame(self) -> TimeFrame:
        return self.__time_frame

    @property
    def side(self) -> PositionSide:
        if self.__side:
            return self.__side
        return self.entry_orders[0].side if 0 < len(self.entry_orders) else None

    @property
    def entry_timestamp(self) -> int:
        if self.__entry_timestamp:
            return self.__entry_timestamp
        return self.entry_orders[0].close_timestamp if 0 < len(self.entry_orders) else None

    @property
    def entry_datetime(self) -> datetime:
        if self.__entry_datetime:
            return self.__entry_datetime
        return datetime.fromtimestamp(self.entry_timestamp)

    @property
    def entry_percentage(self) -> float:
        if self.__entry_percentage:
            return self.__entry_percentage
        return sum(order.percentage for order in self.entry_orders) if 0 < len(self.entry_orders) else 0

    @property
    def entry_price(self) -> float:
        if self.__entry_price:
            return self.__entry_price
        weighted_sum = sum(order.filled_price * order.percentage for order in self.entry_orders)
        return round(weighted_sum / self.entry_percentage, self.price_precision) if 0 < len(self.entry_orders) else None

    @property
    def exit_timestamp(self) -> float:
        if self.__exit_timestamp:
            return self.__exit_timestamp
        return self.exit_orders[-1].close_timestamp if 100 == self.exit_percentage else None

    @property
    def exit_datetime(self) -> datetime:
        if self.__exit_datetime:
            return self.__exit_datetime
        return datetime.fromtimestamp(self.exit_timestamp)

    @property
    def exit_percentage(self) -> int:
        return sum(order.percentage for order in self.exit_orders) if len(self.exit_orders) else 0

    @property
    def exit_price(self) -> float:
        if self.__exit_price:
            return self.__exit_price
        weighted_sum = sum(order.filled_price * order.percentage for order in self.exit_orders)
        return round(weighted_sum / self.exit_percentage, self.price_precision) if 0 < len(self.exit_orders) else None

    @property
    def profit_percentage(self) -> float:
        if self.__profit_percentage:
            return self.__profit_percentage
        return round((self.exit_price / self.entry_price - 1) * self.side, 4) if self.exit_price else 0

    @property
    def run_up_percentage(self) -> float:
        if self.__run_up_percentage:
            return self.__run_up_percentage
        best_met_price = self.maximum_met_price if PositionSide.LONG == self.side else self.minimum_met_price
        return round((best_met_price / self.entry_price - 1) * self.side, 4)

    @property
    def drawdown_percentage(self) -> float:
        if self.__drawdown_percentage:
            return self.__drawdown_percentage
        worst_met_price = self.minimum_met_price if PositionSide.LONG == self.side else self.maximum_met_price
        return round((worst_met_price / self.entry_price - 1) * self.side, 4)

    @property
    def bars(self) -> int:
        if self.__bars:
            self.__bars = int((self.exit_timestamp - self.entry_timestamp) / self.time_frame)
        return self.__bars

    def to_list(self):
        return [self.entry_datetime, self.exit_datetime, self.symbol, self.time_frame, self.side, self.entry_price,
                self.exit_price, self.entry_percentage, self.profit, self.run_up, self.drawdown]

    def to_kafka(self):
        raise NotImplemented()

    @staticmethod
    def tabule(positions: List):
        values = [position.to_list() for position in positions]
        headers = ["Entry Datetime", "Exit Datetime", "Symbol", "Time Frame", "Side", "Entry Price", "Exit Price",
                   "Entry Percetage", "Profit", "Run-up", "Drawdown"]
        table = tabulate(values, headers=headers, tablefmt="pretty")
        print(table)

    def __str__(self) -> str:
        return "Position:" \
               "\n\t- {:<20}{}" \
               "\n\t- {:<20}{}" \
               "\n\t- {:<20}{}" \
               "\n\t- {:<20}{}" \
               "\n\t- {:<20}{}" \
               "\n\t- {:<20}{}" \
               "\n\t- {:<20}{}" \
               "\n\t- {:<20}{}\n" \
            .format("ID", self.id,
                    "Side", self.side,
                    "Percentage", self.entry_percentage,
                    "Entry price", self.entry_price,
                    "Exit price", self.exit_price,
                    "PNL", self.profit,
                    "Draw down", self.drawdown,
                    "Run up", self.run_up)
