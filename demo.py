from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from numpy import ceil, floor
from czsc.analyze import CZSC
from czsc.enum import Freq
from czsc.stock import StockData, format_stock_kline
from ta import ATRMD, SUPERTREND
import talib

from data_reader import read_min_csv


class SupertrendCross(Strategy):
    suptertrend_atr_n = 10
    suptertrend_atr_m = 2
    atr_n = 14
    atr_md_n = 14

    def init(self):
        self.sd = StockData(df, '300340', Freq.F1, [Freq.F1, Freq.F5, Freq.F30, Freq.D])
        self.czsc = CZSC(self.sd.bars[Freq.D])
        bis = self.czsc.bi_list
        for bi in bis:
            print(bi)

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


min_data_fname = "./data/300340.csv"
adj_data_fname = "./data/300340_adj.csv"
print(f"Reading data from {min_data_fname} ...", end="", flush=True)
df = read_min_csv(
    min_data_fname,
    adj_data_fname,
    freq="1min",
    # start_date="20180101",
    start_date="20220901",
    end_date="20221010",
)
print("done")

# Chan
bt = Backtest(
    df, SupertrendCross, cash=1000000, commission=0.0015, exclusive_orders=True
)
stats = bt.run()
# print(stats)
# bt.plot(superimpose=False, resample=False)
# stats["_trades"].to_csv("result/trades.csv", index=False)
