import importlib
import inspect
import json
import pathlib
import sys
from typing import Dict, List

from backtest.core.data import Data
from backtest.core.strategy import Strategy
from backtest.model.candle import Candle
from backtest.model.constant import TimeFrame, EventType
from backtest.util.event import Event


class Market:
    def __init__(self, conf_path: str):
        self.__conf_path: str = conf_path
        self.__events_dict: [int, Event] = {
            EventType.NEW_OPEN_ORDER: Event(),
            EventType.NEW_FILLED_ORDER: Event(),
            EventType.NEW_CANCELED_ORDER: Event(),
            EventType.NEW_OPEN_POSITION: Event(),
            EventType.NEW_CLOSED_POSITION: Event(),
        }

        self.__data: Data = None
        self.__strategies_dict: Dict[int, Strategy] = None
        self.__load_configurations()

    def __load_configurations(self):
        with open(self.__conf_path, 'r') as conf_file:
            conf_dict = json.load(conf_file)

        self.__data = Data()
        self.__data.load_configuration(conf_dict['market']['data'])

        self.__strategies_dict: Dict[int, Strategy] = {}
        module_dir = conf_dict['strategy']['module-dir']
        sys.path.append(module_dir)
        for strategy_dict in conf_dict['strategy']['files']:
            file_path = strategy_dict['file-path']
            file_name = pathlib.Path(file_path).stem
            module = importlib.import_module(file_name)
            for name, cls in inspect.getmembers(module, inspect.isclass):
                if file_name == cls.__module__:
                    strategy = cls(**strategy_dict['inputs'])
                    strategy.load_configuration(strategy_dict, self.__data, self.__events_dict)
                    self.__strategies_dict[strategy.id] = strategy

    def next(self, candles_dict: Dict[str, Candle]):
        self.__data.next(candles_dict)
        for strategy in self.strategies:
            strategy.pre_next()

    @property
    def data(self) -> Data:
        return self.__data

    @property
    def strategies(self) -> List[Strategy]:
        return list(self.__strategies_dict.values())

    @property
    def time_frame(self) -> TimeFrame:
        return self.__data.time_frame

    @property
    def symbols(self) -> List[str]:
        return self.__data.symbols

    @property
    def on_new_open_order(self) -> Event:
        return self.__events_dict[EventType.NEW_OPEN_ORDER]

    @property
    def on_new_filled_order(self) -> Event:
        return self.__events_dict[EventType.NEW_FILLED_ORDER]

    @property
    def on_new_canceled_order(self) -> Event:
        return self.__events_dict[EventType.NEW_CANCELED_ORDER]

    @property
    def on_new_open_position(self) -> Event:
        return self.__events_dict[EventType.NEW_OPEN_POSITION]

    @property
    def on_new_closed_position(self) -> Event:
        return self.__events_dict[EventType.NEW_CLOSED_POSITION]
