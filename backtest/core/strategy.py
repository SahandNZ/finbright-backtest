import itertools
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple

from backtest.core.data import Data
from backtest.core.trade import Trade
from backtest.model.constant import TimeFrame
from backtest.util.event import Event


class Strategy(ABC):
    def __init__(self, ohlcv_dataframe_length):
        self.__ohlcv_dataframe_length: int = ohlcv_dataframe_length

        # configs
        self.__id: int = None
        self.__name: str = None
        self.__symbols: List[str] = None
        self.__time_frames: List[TimeFrame] = None

        # fields
        self.__data: Data = None

        # state
        self.__symbol: str = None
        self.__time_frame: TimeFrame = None
        self.__trades_dict: Dict[Tuple[str, TimeFrame], Trade] = {}

    def load_configuration(self, conf_dict: Dict, data: Data, events_dict: Dict[int, Event]):
        self.__id: int = conf_dict['id']
        self.__name: str = conf_dict['name']
        self.__symbols: List[str] = conf_dict['symbols']
        self.__time_frames: List[TimeFrame] = conf_dict['time-frames']

        self.__data = data

        self.__trades_dict: Dict[Tuple[str, TimeFrame], Trade] = {}
        for symbol, time_frame in itertools.product(self.__symbols, self.__time_frames):
            self.__trades_dict[symbol, time_frame] = Trade(self.__data, self.__id, symbol, time_frame, events_dict)

    def pre_next(self):
        for symbol, time_frame in itertools.product(self.__symbols, self.__time_frames):
            self.__symbol = symbol
            self.__time_frame = time_frame

            self.__trades_dict[(symbol, time_frame)].next()
            if 0 == self.__data.timestamp % time_frame:
                self.data.set_strategy_properties(self.__symbol, self.__time_frame, self.__ohlcv_dataframe_length)
                self.next()

    @abstractmethod
    def next(self):
        raise NotImplemented()

    @property
    def id(self) -> int:
        return self.__id

    @property
    def name(self) -> str:
        return self.__name

    @property
    def time_frames(self) -> List[TimeFrame]:
        return self.__time_frames

    @property
    def symbol(self) -> str:
        return self.__symbol

    @property
    def time_frame(self) -> TimeFrame:
        return self.__time_frame

    @property
    def data(self) -> Data:
        return self.__data

    @property
    def trade(self) -> Trade:
        return self.__trades_dict[(self.__symbol, self.__time_frame)]
