from datetime import datetime


class Candle:
    def __init__(self, timestamp: int, open: float, high: float, low: float, close: float, volume: float):
        self.timestamp: int = timestamp
        self.datetime: datetime = datetime.fromtimestamp(timestamp)
        self.open: float = open
        self.high: float = high
        self.low: float = low
        self.close: float = close
        self.volume: float = volume

    def to_list(self):
        return [self.timestamp, self.datetime, self.open, self.high, self.low, self.close, self.volume]

    @staticmethod
    def from_kafka(ticker):
        return Candle(int(ticker.timestamp), ticker.open, ticker.high, ticker.low, ticker.close, ticker.volume)
