from abc import ABC, abstractmethod
from chan.structs import *


class ReverseAccessor:
    data: list

    def __init__(self, data: list):
        self.data = data

    def __getitem__(self, i):
        return self.data[len(self.data) - 1 - i]

    
class StockSubscribe(ABC):
    @abstractmethod
    def next(self):
        pass

    @abstractmethod
    def has_next(self) -> bool:
        pass

    @abstractmethod
    def get(self) -> Bar:
        pass


class StockSubscribeCsv(StockSubscribe):
    bars: list[Bar]
    index: int

    def __init__(self, fname: str, start_date: str = None, end_date: str = None):
        super().__init__()
        self.bars = self.read_csv(fname, start_date, end_date)
        self.index = 0

    def next(self):
        self.index += 1

    def has_next(self) -> bool:
        return self.index <= len(self.bars) - 1

    def get(self) -> Bar:
        return self.bars[self.index - 1]

    def read_csv(self, fname: str, start_date: str = None, end_date: str = None) -> list[Bar]:
        df = pd.read_csv(fname)
        if start_date is None:
            start_date = 0
        if end_date is None:
            end_date = 30000000
        df = df.loc[(df.TradingDay >= int(start_date)) & (df.TradingDay <= int(end_date))]
        bars = []
        for r in df.itertuples():
            if r.TradingDay < int(start_date) or r.TradingDay > int(end_date):
                continue
            dt = datetime(
                int(r.TradingDay / 10000),
                int(r.TradingDay % 10000 / 100),
                int(r.TradingDay % 10000 % 100),
                int(r.TradingTime / 1000 / 10000),
                int(r.TradingTime / 1000 % 10000 / 100),
            )
            bars.append(Bar(open=r.Open, high=r.High, low=r.Low, close=r.Close,
                            volume=r.Volume, turnover=r.Turnover, num_trades=r.NumTrades,
                            dt=dt, freq=Freq.F1))
        return bars
    

class Stock:
    stock_sub: StockSubscribe
    freqs: list[Freq]
    freq_bars: dict[Freq, list[Bar]]
    freq_counters: dict[Freq, int]

    def __init__(self, stock_sub: StockSubscribe, freqs: list[Freq]):
        if freqs[0] != Freq.F1:
            raise Exception(f"The first frequency must be 1min. Given {freqs[0].value}mins.")
        self.stock_sub = stock_sub
        self.freqs = freqs
        self.freq_bars = {f: [] for f in freqs}
        self.freq_counters = {f: 0 for f in freqs}

    def step(self):
        bar = self.stock_sub.get()
        self.freq_bars[self.freqs[0]].append(bar)
        f1 = self.freqs[0]
        for i in range(1, len(self.freqs)):
            f = self.freqs[i]
            self.freq_counters[f] += 1
            if self.freq_counters[f] == 1:
                # Create an f-bar
                self.freq_bars[f].append(Bar(
                    open=self.freq_bars[f1][-1].open,
                    high=self.freq_bars[f1][-1].high,
                    low=self.freq_bars[f1][-1].low,
                    close=self.freq_bars[f1][-1].close,
                    volume=self.freq_bars[f1][-1].volume,
                    turnover=self.freq_bars[f1][-1].turnover,
                    num_trades=self.freq_bars[f1][-1].num_trades,
                    dt=self.freq_bars[f1][-1].dt,
                    freq=f
                ))
            else:
                fbar = self.freq_bars[f][-1]
                f1bar = self.freq_bars[f1][-1]
                fbar.high = max(fbar.high, f1bar.high)
                fbar.low = min(fbar.low, f1bar.low)
                fbar.close = f1bar.close
                fbar.volume = fbar.volume + f1bar.volume
                fbar.turnover = fbar.turnover + f1bar.turnover
                fbar.num_trades = fbar.num_trades + f1bar.num_trades
            if self.freq_counters[f] == f.value / f1.value:
                self.freq_counters[f] = 0

    def __getitem__(self, freq: Freq) -> list[Bar]:
        return ReverseAccessor(self.freq_bars[freq])


class ChanAnalyzer:
    stock: Stock
    freqs: list[Freq]
    fxs: list[FenXing]
    bis: list[Bi]
    xds: list[XianDuan]
    zss: list[ZhongShu]

    def __init__(self, stock: Stock):
        self.stock = stock
        self.freqs = stock.freqs
        self.fxs = []
        self.bis = []
        self.xds = []
        self.zss = []

    def update(self):
        b = self.stock[self.freqs[0]][0]
        print(f'{b.dt}  {b.open}')
        b = self.stock[self.freqs[1]][0]
        print(f'{b.dt}  {b.open}')
