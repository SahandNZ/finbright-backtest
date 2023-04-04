from typing import Dict, List

from backtest.core.pair import Pair
from backtest.model.candle import Candle
from backtest.model.constant import TimeFrame


class Data:
    def __init__(self, ):
        self.__time_frame: TimeFrame = None
        self.__time_frames: List[TimeFrame] = None
        self.__pairs_dict: Dict[str, Pair] = None

        # states
        self.__timestamp: int = None

        # strategy properties
        self.__strategy_symbol: str = None
        self.__strategy_time_frame: TimeFrame = None
        self.__strategy_candles_limit: int = None

    def load_configuration(self, conf_dict: Dict):
        self.__time_frame: TimeFrame = conf_dict['time-frame']
        self.__time_frames: List[TimeFrame] = conf_dict['time-frames']
        self.__pairs_dict: Dict[str, Pair] = {}
        for pair_conf_dict in conf_dict['pairs']:
            pair = Pair()
            pair.load_configuration(pair_conf_dict, self.__time_frame, self.__time_frames)
            self.__pairs_dict[pair.symbol] = pair

    def next(self, candles_dict: Dict[str, Candle]):
        if self.timestamp is None:
            self.__timestamp = list(candles_dict.values())[0].timestamp - self.time_frame

        self.__timestamp += self.__time_frame
        for symbol, candle in candles_dict.items():
            self.__pairs_dict[symbol].next(candle)

    @property
    def time_frame(self) -> TimeFrame:
        return self.__time_frame

    @property
    def timestamp(self) -> int:
        return self.__timestamp

    @property
    def pairs(self) -> List[Pair]:
        return list(self.__pairs_dict.values())

    @property
    def symbols(self) -> List[str]:
        return list(self.__pairs_dict.keys())

    def get_price_precision(self, symbol: str) -> int:
        return self.__pairs_dict[symbol].price_precision

    def get_quantity_precision(self, symbol: str) -> int:
        return self.__pairs_dict[symbol].price_precision

    def get_last_candle(self, symbol: str) -> Candle:
        return self.__pairs_dict[symbol].last_candle

    def is_price_touched(self, symbol: str, price: float) -> bool:
        last_candle = self.__pairs_dict[symbol].last_candle
        return last_candle.low <= price <= last_candle.high

    def get_market_price(self, symbol: str) -> float:
        return self.__pairs_dict[symbol].last_candle.open

    def get_ohlcv_dataframe(self, symbol: str, time_frame: TimeFrame, limit: int):
        return self.__pairs_dict[symbol].get_ohlcv_dataframe(time_frame, limit)

    # strategy related methods and properties
    def set_strategy_properties(self, symbol: str, time_frame: TimeFrame, candles_limit: int):
        self.__strategy_symbol = symbol
        self.__strategy_time_frame = time_frame
        self.__strategy_candles_limit = candles_limit

    @property
    def ohlcv_dataframe(self):
        df = self.get_ohlcv_dataframe(self.__strategy_symbol, self.__strategy_time_frame, self.__strategy_candles_limit)
        return df
