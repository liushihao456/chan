from backtesting import Strategy
import talib
from backtesting.lib import crossover, resample_apply
from ta import BBANDS, SUPERTREND
from math import ceil, floor
import numpy as np

class BBands(Strategy):
    suptertrend_atr_n = 14
    suptertrend_atr_m = 2

    def ema_diff(self, ema1, ema2, ema3):
        return (ema3 - ema1) * 0.5

    def trend(self, open, close, upper_band, lower_band):
        res = np.zeros(len(close))
        for i in range(len(close)):
            if i < 2:
                res[i] = 0
            else:
                if close[i] < lower_band[i] and close[i-1] < lower_band[i-1] and close[i-2] < lower_band[i-2] \
                   and close[i] < open[i] and close[i-1] < open[i-1] and close[i-2] < open[i-2]:
                    res[i] = -1
                if close[i] > upper_band[i] and close[i-1] > upper_band[i-1] and close[i-2] > upper_band[i-2] \
                   and close[i] > open[i] and close[i-1] > open[i-1] and close[i-2] > open[i-2]:
                    res[i] = 1
        return res

    def init(self):
        self.initial_capital = 1000000
        self.ma50 = self.I(talib.EMA, self.data.Close, 50)
        self.ma60 = self.I(talib.EMA, self.data.Close, 60)
        self.ma70 = self.I(talib.EMA, self.data.Close, 70)
        # self.emadiff = self.I(self.ema_diff, self.ma50, self.ma60, self.ma70)
        # self.bbands = self.I(talib.BBANDS, self.data.Close, 20, 2, 2, 0)
        self.bbands = self.I(BBANDS, self.data.Close, 20, 2)
        # self.supertrend = self.I(
        #     SUPERTREND,
        #     self.data.High,
        #     self.data.Low,
        #     self.data.Close,
        #     self.suptertrend_atr_n,
        #     self.suptertrend_atr_m,
        # )
        # self.ma10d = resample_apply('D', talib.EMA, self.data.Close, 5)
        # self.ma20d = resample_apply('D', talib.EMA, self.data.Close, 10)
        self.custom = self.I(self.trend, self.data.Open, self.data.Close, self.bbands[0], self.bbands[1])

    def next(self):
        if self.ma50[-1] < self.ma60[-1] < self.ma70[-1]:
            # if self.ma60[-1] / self.ma50[-1] - 1 > 0.005:
            # if self.ma10d[-1] < self.ma20d[-1]:
            # Allow sells only
            if self.data.High[-1] >= self.bbands[0][-1] and self.data.Close[-1] < self.data.Open[-1] and self.data.Close[-1] < self.bbands[0][-1]:
                self.sell()
            # if crossover(self.data.Close, self.supertrend) or crossover(self.supertrend, self.data.Close):
            #     self.position.close()
        if self.ma50[-1] > self.ma60[-1] > self.ma70[-1]:
            # if self.ma50[-1] / self.ma60[-1] - 1 > 0.005:
            # if self.ma10d[-1] > self.ma20d[-1]:
            # Allow sells only
            if self.data.Low[-1] <= self.bbands[1][-1] and self.data.Close[-1] > self.data.Open[-1] and self.data.Close[-1] > self.bbands[1][-1]:
                self.buy()
            # if self.data.High[-1] >= self.bbands2[0][-1] and self.data.Close[-1] < self.data.Open[-1]:
            #     self.position.close()
            # if crossover(self.data.Close, self.supertrend) or crossover(self.supertrend, self.data.Close):
            #     self.position.close()

        for trade in self.trades:
            if trade.is_long and not trade.sl:
                # trade.sl = min(self.data.Low[-2], self.data.Low[-1])
                trade.sl = min(self.data.Low[-3], self.data.Low[-2])
                # p = trade.entry_price / (1 + 0.0015)
                # trade.sl = ceil(p * 0.993 * 100) / 100
            elif trade.is_short and not trade.sl:
                # trade.sl = max(self.data.High[-2], self.data.High[-1])
                trade.sl = max(self.data.High[-3], self.data.High[-2])
                # p = trade.entry_price / (1 - 0.0015)
                # trade.sl = floor(p * 1.007 * 100) / 100

            if trade.is_long:
                if self.data.Close[-1] / trade.entry_price - 1 > 0.05:
                    p = trade.tp if trade.tp else 0
                    p = max(p, trade.entry_price + (self.data.High[-1] - trade.entry_price) * 0.7)
                    trade.tp = p
            elif trade.is_short:
                if self.data.Close[-1] / trade.entry_price - 1 > 0.05:
                    p = trade.tp if trade.tp else 10000
                    p = min(p, trade.entry_price - (trade.entry_price - self.data.Low[-1]) * 0.7)
                    trade.tp = p

