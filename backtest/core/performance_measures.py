import math
from typing import List

import numpy as np
from backtest.model.position import Position


class PerformanceMeasures:
    def __init__(self, positions: List[Position], initial_capital: int, risk_free_rate: float = 0.04):
        self.positions: List[Position] = positions
        self.intial_capital = initial_capital
        self.risk_free_rate = risk_free_rate

        self.__recalculated_positions: List[Position] = []
        for position in positions:
            position.

    def positions(self) -> List[Position]:
        pass

    @property
    def profits(self) -> np.array:
        return np.array([position.pnl for position in self.positions])

    @property
    def profits_percentage(self) -> np.array:
        return np.array([position.pnl for position in self.positions])

    @property
    def net_profit(self) -> float:
        return round(self.profits.sum(), 2)

    @property
    def net_profit_percentage(self) -> float:
        return round(self.profits.sum(), 2)

    @property
    def total_trades(self) -> float:
        return len(self.__strategy.positions_history)

    @property
    def wining_trades(self) -> float:
        return (0 <= self.profits).sum()

    @property
    def losing_trades(self) -> float:
        return (self.profits < 0).sum()

    @property
    def wining_ratio(self) -> float:
        return round(self.wining_trades / self.total_trades, 4)

    @property
    def gross_profits(self) -> float:
        return round(self.profits[0 < self.profits].sum(), 2)

    @property
    def gross_losses(self) -> float:
        return round(self.profits[self.profits < 0].sum(), 2)

    @property
    def profit_factor(self) -> float:
        return round(self.gross_profits / abs(self.gross_losses), 2)

    @property
    def average_profit(self) -> float:
        return round(self.net_profit / self.total_trades, 2)

    @property
    def average_profit_ratio(self) -> float:
        return round(self.net_profit_ratio / self.total_trades, 4)

    @property
    def average_bars_in_trade(self) -> float:
        interval = self.__strategy.interval
        bars = np.array([(p.close_timestamp - p.open_timestamp) / interval for p in self.__strategy.positions_history])
        return round(bars.mean(), 2)

    @property
    def total_traded_quantity(self) -> float:
        quantity_precision = self.__strategy.data.get_quantity_precision(self.__strategy.symbol)
        total_traded_qty = sum([abs(position.traded_quantity) for position in self.__strategy.positions_history])
        return round(total_traded_qty, quantity_precision)

    @property
    def total_paid_fee(self) -> float:
        return round(sum([position.total_paid_fee for position in self.__strategy.positions_history]), 2)

    @property
    def sharp_ratio(self) -> float:
        first_timestamp = self.__strategy.positions_history[0].open_timestamp
        last_timestamp = self.__strategy.positions_history[-1].close_timestamp
        timestamp_dif = last_timestamp - first_timestamp
        years = round(timestamp_dif / Interval.DAY1 / 365, 4)
        risk_free_rate = self.__risk_free_rate * years / len(self.__strategy.positions_history)
        sharpe_ratio = (self.profit_ratios - risk_free_rate).mean() / self.profit_ratios.std() * math.sqrt(years * 365)
        return round(sharpe_ratio, 2)

    @property
    def maximum_draw_down(self) -> float:
        draw_downs_array = np.array([position.draw_down for position in self.__strategy.positions_history])
        return round(np.max(draw_downs_array), 2)

    @property
    def maximum_draw_down_ratio(self) -> float:
        draw_down_ratios_array = np.array([position.draw_down_ratio for position in self.__strategy.positions_history])
        return round(np.max(draw_down_ratios_array), 4)

    @property
    def maximum_run_up(self) -> float:
        run_up_array = np.array([position.run_up for position in self.__strategy.positions_history])
        return round(np.max(run_up_array), 2)

    @property
    def maximum_run_up_ratio(self) -> float:
        run_up_ratio_array = np.array([position.run_up_ratio for position in self.__strategy.positions_history])
        return round(np.max(run_up_ratio_array), 4)

    def print(self):
        log = "Performance Measures" \
              "\n\t- {:^30}: {:^10} ({:^7}%)" \
              "\n\t- {:^30}: {:^10}                (win: {} / loss: {})" \
              "\n\t- {:^30}: {:^10}                (win: {} / total: {})" \
              "\n\t- {:^30}: {:^10}                (gross profit: {} / gross loss: {})" \
              "\n\t- {:^30}: {:^10} ({:^7}%)     (net profit: {} / total: {})" \
              "\n\t- {:^30}: {:^10} (Interval: {})" \
              "\n\t- {:^30}: {:^10}" \
              "\n\t- {:^30}: {:^10}" \
              "\n\t- {:^30}: {:^10}" \
              "\n\t- {:^30}: {:^10} {:^10}%" \
              "\n\t- {:^30}: {:^10} {:^10}%" \
            .format("Net profit", self.net_profit, self.net_profit_ratio,
                    "Total trades", self.total_trades, self.wining_trades, self.losing_trades,
                    "Wining ratio", self.wining_ratio, self.wining_trades, self.total_trades,
                    "Profit factor", self.profit_factor, self.gross_profits, self.gross_losses,
                    "Avg profit", self.average_profit, self.average_profit_ratio, self.net_profit, self.total_trades,
                    "Avg # bars", self.average_bars_in_trade, Interval.get_str(self.__strategy.interval),
                    "Total traded Quantity", self.total_traded_quantity,
                    "Total paid fee", self.total_paid_fee,
                    "Sharpe Ratio", self.sharp_ratio,
                    "Maximum Draw Down", self.maximum_draw_down, self.maximum_draw_down_ratio,
                    "Maximum Run Up", self.maximum_run_up, self.maximum_run_up_ratio)

        print(log)
