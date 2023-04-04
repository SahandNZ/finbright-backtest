import itertools
from datetime import datetime

from backtest.model.constant import OrderSide, TimeFrame, OrderStatus, OrderType


class Order:
    __counter = itertools.count()

    def __init__(self, side: OrderSide, percentage: float, price: float, stop_price: float,
                 reduce_only: bool, comment: str):
        self.id: int = next(self.__counter)
        self.side: OrderSide = side
        self.percentage: float = percentage
        self.price: float = price
        self.stop_price: float = stop_price
        self.reduce_only: bool = reduce_only
        self.comment: str = comment
        self.type: OrderType = (0 if price else 1) + (0 if stop_price else 2)
        self.is_activated: bool = stop_price is None

        self.status: OrderStatus = None
        self.open_timestamp: int = None
        self.close_timestamp: int = None
        self.filled_price: float = None

        self.strategy_id: int = None
        self.symbol: str = None
        self.time_frame: TimeFrame = None

    def __str__(self) -> str:
        return "Order:" \
               "\n\t- {:<20}{}" \
               "\n\t- {:<20}{}" \
               "\n\t- {:<20}{}" \
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
                    "Percentage", self.percentage,
                    "Price", self.price,
                    "Stop price", self.stop_price,
                    "Reduce only", self.reduce_only,
                    "Comment", self.comment,
                    "Status", self.status,
                    "Open  date time", datetime.fromtimestamp(self.open_timestamp),
                    "Close date time", datetime.fromtimestamp(self.close_timestamp) if self.close_timestamp else None,
                    "Filled price", self.filled_price)
