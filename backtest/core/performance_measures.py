from typing import List, Tuple

import numpy as np
from backtest.model.constant import PositionSide
from backtest.model.position import Position
from tabulate import tabulate


class PerformanceMeasures:
    def __init__(self, positions: List[Position], initial_capital: int = 1000, fix_quantity: float = None,
                 fix_equity: float = None, risk_free_rate: float = 0.002, fee_rate: float = 0.0004):
        self.positions: List[Position] = positions

        self.initial_capital: int = initial_capital
        self.fix_quantity: float = fix_quantity
        self.fix_equity: float = fix_equity

        self.risk_free_rate: float = risk_free_rate
        self.fee_rate: float = fee_rate

        self.assign_quantity()

    def assign_quantity(self):
        if self.fix_quantity is not None:
            for position in self.positions:
                position.set_quantity(self.fix_quantity)

        elif self.fix_equity is not None:
            for position in self.positions:
                position.set_equity(self.fix_equity)

        else:
            raise ValueError("Either fix_quantity or fix_equity must be not None.")

    def value2tuple(self, value: float) -> Tuple[float, float]:
        return round(value, 2), round((value / self.initial_capital) * 100, 2)

    @property
    def bars(self) -> np.array:
        return np.array([position.bars for position in self.positions])

    @property
    def days(self) -> float:
        return round(self.bars.sum() * self.positions[0].time_frame / (24 * 60 * 60), 2)

    @property
    def sides(self) -> np.array:
        return np.array([position.side for position in self.positions])

    @property
    def profits(self) -> np.array:
        return np.array([position.profit for position in self.positions])

    @property
    def longs(self) -> np.array:
        return self.profits[PositionSide.LONG == self.sides]

    @property
    def shorts(self) -> np.array:
        return self.profits[PositionSide.SHORT == self.sides]

    @property
    def profits_percentage(self):
        return np.array([position.profit_percentage for position in self.positions])

    @property
    def net_profit(self) -> Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float]]:
        all_tuple = self.value2tuple(self.profits.sum())
        long_tuple = self.value2tuple(self.longs.sum())
        short_tuple = self.value2tuple(self.shorts.sum())

        return all_tuple, long_tuple, short_tuple

    @property
    def gross_profit(self) -> Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float]]:
        all_tuple = self.value2tuple(self.profits[0 < self.profits].sum())
        long_tuple = self.value2tuple(self.longs[0 < self.longs].sum())
        short_tuple = self.value2tuple(self.shorts[0 < self.shorts].sum())

        return all_tuple, long_tuple, short_tuple

    @property
    def gross_loss(self) -> Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float]]:
        all_tuple = self.value2tuple(np.abs(self.profits[self.profits < 0].sum()))
        long_tuple = self.value2tuple(np.abs(self.longs[self.longs < 0].sum()))
        short_tuple = self.value2tuple(np.abs(self.shorts[self.shorts < 0].sum()))

        return all_tuple, long_tuple, short_tuple

    @property
    def maximum_run_up(self) -> Tuple[float, float]:
        equity, minimum_equity, maximum_run_up = self.initial_capital, self.initial_capital, 0
        for position in self.positions:
            run_up = round(equity - minimum_equity + position.run_up, 2)
            maximum_run_up = max(maximum_run_up, run_up)

            equity += position.profit
            minimum_equity = min(minimum_equity, equity)

        run_up_tuple = self.value2tuple(maximum_run_up)
        return run_up_tuple

    @property
    def maximum_drawdown(self) -> Tuple[float, float, int]:
        equity, maximum_equity, maximum_equity_timestamp = self.initial_capital, 0, 0
        maximum_drawdown, maximum_drawdown_duration = 0, 0
        for position in self.positions:
            drawdown = round(maximum_equity - equity - position.drawdown, 2)
            maximum_drawdown = max(maximum_drawdown, drawdown)
            drawdown_duration = int((position.exit_timestamp - maximum_equity_timestamp) / position.time_frame)
            maximum_drawdown_duration = max(maximum_drawdown_duration, drawdown_duration)

            equity = round(equity + position.profit, 2)
            maximum_equity = max(maximum_equity, equity)
            if equity == maximum_equity:
                maximum_equity_timestamp = position.entry_timestamp

        drawdown_tuple = self.value2tuple(maximum_drawdown)
        return *drawdown_tuple, maximum_drawdown_duration

    @property
    def buy_and_hold_return(self) -> Tuple[float, float]:
        profit = round((self.positions[-1].exit_price / self.positions[0].entry_price - 1) * self.initial_capital, 2)
        return self.value2tuple(profit)

    @property
    def sharpe_ratio(self) -> float:
        daily_risk_free_rate = self.risk_free_rate / 365 * self.days
        daily_profit = self.profits.sum() / self.days
        numerator = daily_profit - daily_risk_free_rate
        denominator = self.profits.std()
        return round(numerator / denominator * np.sqrt(365), 4)

    @property
    def sortino_ratio(self) -> float:
        daily_risk_free_rate = self.risk_free_rate / 365 * self.days
        daily_profit = self.profits.sum() / self.days
        numerator = daily_profit - daily_risk_free_rate
        denominator = self.profits[self.profits <= 0].std()
        return round(numerator / denominator * np.sqrt(365), 4)

    @property
    def profit_factor(self) -> Tuple[float, float, float]:
        gross_profit = self.gross_profit
        gross_loss = self.gross_loss

        all = round(gross_profit[0][0] / gross_loss[0][0], 3)
        long = round(gross_profit[1][0] / gross_loss[1][0], 3)
        short = round(gross_profit[2][0] / gross_loss[2][0], 3)
        return all, long, short

    def commission_paid(self) -> Tuple[float, float, float]:
        pass

    @property
    def total_closed_trades(self) -> Tuple[int, int, int]:
        all = len(self.profits)
        long = len(self.longs)
        short = len(self.shorts)
        return all, long, short

    @property
    def number_wining_trades(self) -> Tuple[int, int, int]:
        all = (0 < self.profits).sum()
        long = (0 < self.longs).sum()
        short = (0 < self.shorts).sum()
        return all, long, short

    @property
    def number_losing_trades(self) -> Tuple[int, int, int]:
        all = (self.profits < 0).sum()
        long = (self.longs < 0).sum()
        short = (self.shorts < 0).sum()
        return all, long, short

    @property
    def wining_ratio(self) -> Tuple[float, float, float]:
        total_closed_trades = self.total_closed_trades
        number_wining_trades = self.number_wining_trades

        all = round(number_wining_trades[0] / total_closed_trades[0] * 100, 2)
        long = round(number_wining_trades[1] / total_closed_trades[1] * 100, 2)
        short = round(number_wining_trades[2] / total_closed_trades[2] * 100, 2)
        return all, long, short

    @property
    def average_trade(self) -> Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float]]:
        all_tuple = self.value2tuple(self.profits.mean())
        long_tuple = self.value2tuple(self.longs.mean())
        short_tuple = self.value2tuple(self.shorts.mean())
        return all_tuple, long_tuple, short_tuple

    @property
    def average_wining_trade(self):
        all_tuple = self.value2tuple(self.profits[0 < self.profits].mean())
        long_tuple = self.value2tuple(self.longs[0 < self.longs].mean())
        short_tuple = self.value2tuple(self.shorts[0 < self.shorts].mean())
        return all_tuple, long_tuple, short_tuple

    @property
    def average_losing_trade(self):
        all_tuple = self.value2tuple(np.abs(self.profits[self.profits < 0].mean()))
        long_tuple = self.value2tuple(np.abs(self.longs[self.longs < 0].mean()))
        short_tuple = self.value2tuple(np.abs(self.shorts[self.shorts < 0].mean()))
        return all_tuple, long_tuple, short_tuple

    @property
    def ratio_average_win_average_loss(self):
        avg_win = self.average_wining_trade
        avg_loss = self.average_losing_trade

        all = round(avg_win[0][0] / avg_loss[0][0], 3)
        long = round(avg_win[1][0] / avg_loss[1][0], 3)
        short = round(avg_win[2][0] / avg_loss[2][0], 3)

        return all, long, short

    @property
    def largest_wining_trade(self):
        all_tuple = self.value2tuple(self.profits[0 < self.profits].max())
        long_tuple = self.value2tuple(self.longs[0 < self.longs].max())
        short_tuple = self.value2tuple(self.shorts[0 < self.shorts].max())
        return all_tuple, long_tuple, short_tuple

    @property
    def largest_losing_trade(self):
        all_tuple = self.value2tuple(np.abs(self.profits[self.profits < 0].min()))
        long_tuple = self.value2tuple(np.abs(self.longs[self.longs < 0].min()))
        short_tuple = self.value2tuple(np.abs(self.shorts[self.shorts < 0].min()))
        return all_tuple, long_tuple, short_tuple

    @property
    def average_bar_in_trade(self):
        all = round(self.bars.mean())
        long = round(self.bars[PositionSide.LONG == self.sides].mean())
        short = round(self.bars[PositionSide.SHORT == self.sides].mean())

        return all, long, short

    @property
    def average_bar_in_wining_trade(self):
        all = round(self.bars.mean())
        long = round(self.bars[(PositionSide.LONG == self.sides) & (0 < self.profits)].mean())
        short = round(self.bars[(PositionSide.SHORT == self.sides) & (0 < self.profits)].mean())

        return all, long, short

    @property
    def average_bar_in_losing_trade(self):
        all = round(self.bars.mean())
        long = round(self.bars[(PositionSide.LONG == self.sides) & (self.profits < 0)].mean())
        short = round(self.bars[(PositionSide.SHORT == self.sides) & (self.profits < 0)].mean())

        return all, long, short

    def tabulate(self):
        headers = ["Measure", "All", "Long", "Short"]
        values = [
            ["Net Profit", *[i[0] for i in self.net_profit]],
            [None, *[i[1] for i in self.net_profit]],
            [None, None, None, None],

            ["Gross Profit", *[i[0] for i in self.gross_profit]],
            [None, *[i[1] for i in self.gross_profit]],
            [None, None, None, None],

            ["Gross Loss", *[i[0] for i in self.gross_loss]],
            [None, *[i[1] for i in self.gross_loss]],
            [None, None, None, None],

            ["Max Run-up", self.maximum_run_up[0], None, None],
            [None, self.maximum_run_up[1], None, None],
            [None, None, None, None],

            ["Max Drawdown", self.maximum_drawdown[0], None, None],
            [None, self.maximum_drawdown[1], None, None],
            [None, None, None, None],

            ["Buy & Hold Return", self.buy_and_hold_return[0], None, None],
            [None, self.buy_and_hold_return[1], None, None],
            [None, None, None, None],

            ["Sharpe Ratio", self.sharpe_ratio, None, None],
            ["Sortino Ratio", self.sortino_ratio, None, None],
            [None, None, None, None],

            ["Profit Factor", *self.profit_factor],
            [None, None, None, None],

            ["Total Closed Trades", *self.total_closed_trades],
            ["Number Wining Trades", *self.number_wining_trades],
            ["Number Wining Trades", *self.number_losing_trades],
            [None, None, None, None],

            ["Percent Profitable", *self.wining_ratio],
            [None, None, None, None],

            ["Avg Trade", *[i[0] for i in self.average_trade]],
            [None, *[i[1] for i in self.average_trade]],
            [None, None, None, None],

            ["Avg Wining Trade", *[i[0] for i in self.average_wining_trade]],
            ["Avg Wining Trade %", *[i[1] for i in self.average_wining_trade]],
            [None, None, None, None],

            ["Avg Lossing Trade", *[i[0] for i in self.average_losing_trade]],
            ["Avg Lossing Trade %", *[i[1] for i in self.average_losing_trade]],
            [None, None, None, None],

            ["Ratio Avg Win / Avg Loss", *self.ratio_average_win_average_loss],
            [None, None, None, None],

            ["Largest Wining Trade", *[i[0] for i in self.largest_wining_trade]],
            ["Largest Wining Trade %", *[i[1] for i in self.largest_wining_trade]],
            [None, None, None, None],

            ["Largest Lossing Trade", *[i[0] for i in self.largest_losing_trade]],
            ["Largest Lossing Trade %", *[i[1] for i in self.largest_losing_trade]],
            [None, None, None, None],

            ["Average # Bars in Trades", *self.average_bar_in_trade],
            ["Average # Bars in Wining Trades", *self.average_bar_in_wining_trade],
            ["Average # Bars in Lossing Trades", *self.average_bar_in_losing_trade],
        ]
        table = tabulate(values, headers=headers, tablefmt="pretty")
        print(table)
