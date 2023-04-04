class TimeFrame:
    MIN1 = 60
    MIN5 = 5 * MIN1
    MIN15 = 15 * MIN1
    MIN30 = 30 * MIN1
    HOUR1 = 60 * MIN1
    HOUR2 = 2 * HOUR1
    HOUR4 = 4 * HOUR1
    HOUR6 = 6 * HOUR1
    HOUR8 = 8 * HOUR1
    HOUR12 = 12 * HOUR1
    DAY1 = 24 * HOUR1
    DAY3 = 3 * DAY1
    WEEK1 = 7 * DAY1
    MONTH1 = 30 * DAY1


class OrderSide:
    BUY = 1
    SELL = -1


class OrderStatus:
    OPEN = 'OPEN'  # same as binance NEW status
    FILLED = 'FILLED'
    CANCELED = 'CANCELED'


class OrderType:
    MARKET = 0
    LIMIT = 1
    STOP_MARKET = 2
    STOP_LIMIT = 3


class PositionSide:
    LONG = 1
    SHORT = -1


class EventType:
    NEW_OPEN_ORDER = 0
    NEW_FILLED_ORDER = 1
    NEW_CANCELED_ORDER = 2
    NEW_OPEN_POSITION = 3
    NEW_CLOSED_POSITION = 4
