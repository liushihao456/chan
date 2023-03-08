from backtesting import Backtest, Strategy
from backtesting.lib import crossover

from backtesting.test import SMA

from data_reader import read_min_csv


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
    freq="30min",
    start_date="20180101",
    end_date="20221010",
)
bt = Backtest(df, SmaCross, commission=0.0015, exclusive_orders=True)
stats = bt.run()
bt.plot(superimpose=False)
