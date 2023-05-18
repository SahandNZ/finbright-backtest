from typing import Dict, List

import pandas as pd

from backtest.model.candle import Candle
from backtest.model.constant import TimeFrame


class Pair:
    def __init__(self):
        self.__symbol: str = None
        self.__price_precision: int = None
        self.__quantity_precision: int = None

        self.__time_frames: List[TimeFrame] = None
        self.__time_frame: int = None

        # states
        self.__index: int = None
        self.__timestamp: int = None
        self.__last_candle: Candle = None
        self.__source_ohlcv_dataframe: pd.DataFrame = None
        self.__data_ohlcv_dataframes_dict: Dict[int, pd.DataFrame] = None

    def load_configuration(self, conf_dict: Dict, time_frame: int, time_frames: List[TimeFrame]):
        self.__symbol: str = conf_dict['symbol']
        self.__price_precision: int = conf_dict['price-precision']
        self.__quantity_precision: int = conf_dict['quantity-precision']

        self.__time_frame: int = time_frame
        self.__time_frames: List[TimeFrame] = time_frames

        # states
        df = pd.DataFrame(columns=['timestamp', 'datetime', 'open', 'high', 'low', 'close', 'volume'])
        self.__source_ohlcv_dataframe = df
        self.__data_ohlcv_dataframes_dict = {}
        for time_frame in self.__time_frames:
            df = pd.DataFrame(columns=['timestamp', 'datetime', 'open', 'high', 'low', 'close', 'volume'])
            self.__data_ohlcv_dataframes_dict[time_frame] = df

    def next(self, candle: Candle):
        if self.__timestamp is None:
            self.__index = 0
            self.__timestamp = candle.timestamp - self.__time_frame

        self.__index += 1
        self.__timestamp += self.__time_frame
        self.__last_candle = candle
        if 0 == candle.timestamp % self.__time_frame:
            self.__source_ohlcv_dataframe.loc[len(self.__source_ohlcv_dataframe)] = candle.to_list
            for time_frame, dataframe in self.__data_ohlcv_dataframes_dict.items():
                step = time_frame // self.__time_frame
                if 0 == (candle.timestamp + self.__time_frame) % time_frame:
                    window = self.__source_ohlcv_dataframe.iloc[-step:]
                    if step == len(window):
                        timestamp = window.timestamp.iloc[0]
                        datetime = window.datetime.iloc[0]
                        open = window.open.iloc[0]
                        high = window.high.max()
                        low = window.low.min()
                        close = window.close.iloc[-1]
                        volume = window.volume.sum()
                        dataframe.loc[len(dataframe)] = [timestamp, datetime, open, high, low, close, volume]
        else:
            print(self.__timestamp, candle.timestamp, self.__time_frame)
            raise Exception("Timestamp of candle is not valid. (market timestamp: {:}, candle timestamp: {})"
                            .format(self.__timestamp, candle.timestamp))

    def get_ohlcv_dataframe(self, time_frame: TimeFrame, limit: int) -> pd.DataFrame:
        return self.__data_ohlcv_dataframes_dict[time_frame].iloc[self.__index - limit: self.__index]

    @property
    def last_candle(self) -> Candle:
        return self.__last_candle

    @property
    def symbol(self) -> str:
        return self.__symbol

    @property
    def price_precision(self) -> int:
        return self.__price_precision

    @property
    def quantity_precision(self) -> int:
        return self.__quantity_precision

    @property
    def time_frame(self) -> int:
        return self.__time_frame
