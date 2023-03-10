from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from numpy import ceil, floor
from ta import ATRMD, SUPERTREND
import talib

from backtesting.test import SMA

from data_reader import read_min_csv


class SupertrendCross(Strategy):
    suptertrend_atr_n = 10
    suptertrend_atr_m = 2
    atr_n = 14
    atr_md_n = 14

    def init(self):
        self.initial_capital = 1000000
        self.supertrend = self.I(
            SUPERTREND,
            self.data.High,
            self.data.Low,
            self.data.Close,
            self.suptertrend_atr_n,
            self.suptertrend_atr_m,
        )
        self.atr = self.I(
            talib.ATR, self.data.High, self.data.Low, self.data.Close, self.atr_n
        )
        self.atr_md = self.I(
            ATRMD,
            self.data.High,
            self.data.Low,
            self.data.Close,
            self.atr_n,
            self.atr_md_n,
        )

    def next(self):
        if crossover(self.data.Close, self.supertrend) and self.atr_md[-1] >= 7:
            self.buy(size=int(self.initial_capital / self.data.Close[-1]))
        elif crossover(self.supertrend, self.data.Close) and self.atr_md[-1] >= 7:
            self.sell(size=int(self.initial_capital / self.data.Close[-1]))

        if (
            crossover(self.data.Close, self.supertrend)
            and self.atr_md[-1] < 7
            and self.position
        ):
            self.position.close()
        elif (
            crossover(self.supertrend, self.data.Close)
            and self.atr_md[-1] < 7
            and self.position
        ):
            self.position.close()

        for trade in self.trades:
            if trade.is_long and not trade.sl:
                p = trade.entry_price / (1 + 0.0015)
                trade.sl = ceil(p * 0.993 * 100) / 100
            elif trade.is_short and not trade.sl:
                p = trade.entry_price / (1 - 0.0015)
                trade.sl = floor(p * 1.007 * 100) / 100


class SmaCross(Strategy):
    def init(self):
        price = self.data.Close
        self.ma1 = self.I(SMA, price, 10)
        self.ma2 = self.I(SMA, price, 20)

    def next(self):
        if crossover(self.ma1, self.ma2):
            self.buy()
        elif crossover(self.ma2, self.ma1):
            self.sell()


df = read_min_csv(
    "./data/300340.csv",
    "./data/300340_adj.csv",
    freq="15min",
    start_date="20180101",
    end_date="20221010",
)
# bt = Backtest(df, SmaCross, commission=0.0015, exclusive_orders=True)
bt = Backtest(
    df, SupertrendCross, cash=1000000, commission=0.0015, exclusive_orders=True
)
stats = bt.run()
print(stats)
bt.plot(superimpose=False, resample=False)
stats["_trades"].to_csv("result/trades.csv", index=False)
