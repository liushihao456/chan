from abc import ABC, abstractmethod
from datetime import datetime

import pandas as pd

from chan.structs import (
    Bar,
    Bi,
    Direction,
    ExclusiveBar,
    FenXing,
    Freq,
    ZouShi,
    ZhongShu,
)


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
                            dt=dt, freq=Freq.F1, index=len(bars)))
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
                    freq=f,
                    index=len(self.freq_bars)
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
    xds: list[ZouShi]
    zoushis: dict[Freq, list[ZouShi]]
    unresolved_zoushis: dict[Freq, list[ZouShi]]

    def __init__(self, stock: Stock):
        self.stock = stock
        self.freqs = stock.freqs
        self.unresolved_bars = []
        self.fxs = []
        self.unresolved_fxs = []
        self.bis = []
        self.unresolved_bis = []
        self.xds = []
        self.unresolved_xds = []
        self.zoushis = {}
        self.unresolved_zoushis = {}
        for f in self.freqs:
            self.zoushis[f] = []
            self.unresolved_zoushis[f] = []

    def update(self):
        self.check_exclusive_bar()
        self.check_fx()
        self.check_bi()
        self.construct_zoushi(self.unresolved_bis, self.xds, self.unresolved_xds)
        for i in range(len(self.freqs)):
            f = self.freqs[i]
            a = self.unresolved_xds if i == 0 else self.unresolved_zoushis[self.freqs[i-1]]
            self.construct_zoushi(a, self.zoushis[f], self.unresolved_zoushis[f])

    def exclude(self, bar1: ExclusiveBar, bar2: ExclusiveBar | Bar, bar3: Bar = None):
        if bar3 is None:
            if (bar1.high >= bar2.high and bar1.low <= bar2.low) or \
               (bar2.high >= bar1.high and bar2.low <= bar1.low):
                return ExclusiveBar(bar1.bars + [bar2], Direction.Up)
            else:
                return ExclusiveBar([bar2])
        else:
            if (bar2.high >= bar3.high and bar2.low <= bar3.low) or \
               (bar3.high >= bar2.high and bar3.low <= bar2.low):
                if bar2.high >= bar1.high:
                    return ExclusiveBar(bar2.bars + [bar3], Direction.Up)
                else:
                    return ExclusiveBar(bar2.bars + [bar3], Direction.Down)
            else:
                return ExclusiveBar([bar3])

    def check_exclusive_bar(self):
        b = self.stock[self.freqs[0]][0]
        if len(self.unresolved_bars) >= 2:
            eb = self.exclude(self.unresolved_bars[-2], self.unresolved_bars[-1], b)
            if eb.index == self.unresolved_bars[-1].index:
                # The new bar combined with the last bar
                self.unresolved_bars = self.unresolved_bars[:-1] + [eb]
            else:
                self.unresolved_bars = [self.unresolved_bars[-2], self.unresolved_bars[-1], eb]
        elif len(self.unresolved_bars) == 1:
            eb = self.exclude(self.unresolved_bars[0], b)
            if eb.index == self.unresolved_bars[0].index:
                # The new bar combined with the last bar
                self.unresolved_bars = [eb]
            else:
                self.unresolved_bars = [self.unresolved_bars[0], eb]
        else:
            eb = ExclusiveBar([b])
            self.unresolved_bars = [eb]

    def check_fx(self):
        if len(self.unresolved_bars) < 3:
            return
        b1, b2, b3 = self.unresolved_bars
        if b1.low > b2.low < b3.low and b1.high > b2.high < b3.high:
            fx = FenXing(self.unresolved_bars, Direction.Down)
            if not self.fxs or fx.index != self.fxs[-1].index:
                self.unresolved_fxs.append(fx)
                self.fxs.append(fx)
        if b1.low < b2.low > b3.low and b1.high < b2.high > b3.high:
            fx = FenXing(self.unresolved_bars, Direction.Up)
            if not self.fxs or fx.index != self.fxs[-1].index:
                self.unresolved_fxs.append(fx)
                self.fxs.append(fx)

    def num_bars_between(self, bar1: Bar, bar2: Bar) -> int:
        return bar2.index - bar1.index - 1

    def check_bi(self):
        if self.bis and self.unresolved_fxs:
            fx1 = self.bis[-1].end_fx
            fx = self.unresolved_fxs[-1]
            if fx1.direction != fx.direction:
                if self.num_bars_between(fx1.exbars[-1].bars[-1], fx.exbars[0].bars[0]) >= 0:
                    # Make sure the endpoint FXs are the highest and lowest of a Bi
                    if fx.direction == Direction.Up:
                        for f in self.unresolved_fxs[:-1]:
                            if f.direction == fx.direction and f.high > fx.high:
                                return
                    if fx.direction == Direction.Down:
                        for f in self.unresolved_fxs[:-1]:
                            if f.direction == fx.direction and f.low < fx.low:
                                return
                    bi = Bi(fx1, fx)
                    self.bis.append(bi)
                    self.unresolved_bis.append(bi)
                    self.unresolved_fxs.clear()
                    return
                else:
                    if fx.direction == Direction.Down and fx.low < self.bis[-1].start_price:
                        self.bis = self.bis[:-1]
                        self.unresolved_bis = self.unresolved_bis[:-1]
                        self.bis[-1].extend(fx)
                    if fx.direction == Direction.Up and fx.high > self.bis[-1].start_price:
                        self.bis = self.bis[:-1]
                        self.unresolved_bis = self.unresolved_bis[:-1]
                        self.bis[-1].extend(fx)
            if fx1.direction == fx.direction:
                if (fx1.direction == Direction.Up and fx.high > fx1.high) or \
                    (fx1.direction == Direction.Down and fx.low < fx1.low):
                    self.bis[-1].extend(fx)
                    self.unresolved_fxs.clear()
        else:
            # The first Bi
            for i in range(len(self.unresolved_fxs)):
                fx_i = self.unresolved_fxs[i]
                highest_dingfx = 0
                lowest_difx = 1e+10
                for j in range(i + 1, len(self.unresolved_fxs)):
                    fx_j = self.unresolved_fxs[j]

                    # Make sure the endpoint FXs are the highest and lowest of a Bi
                    if fx_i.direction == Direction.Down and fx_j.direction == Direction.Up:
                        if fx_j.high < highest_dingfx:
                            continue
                        else:
                            highest_dingfx = fx_j.high
                    if fx_i.direction == Direction.Up and fx_j.direction == Direction.Down:
                        if fx_j.low > lowest_difx:
                            continue
                        else:
                            lowest_difx = fx_j.low

                    # Early quit
                    if fx_i.direction == fx_j.direction == Direction.Up:
                        if fx_j.high > fx_i.high:
                            break
                    if fx_i.direction == fx_j.direction == Direction.Down:
                        if fx_j.low < fx_i.low:
                            break

                    if self.num_bars_between(fx_i.exbars[-1].bars[-1], fx_j.exbars[0].bars[0]) >= 0:
                        if (fx_i.direction == Direction.Up and fx_j.direction == Direction.Down and fx_i.high > fx_j.low) or \
                            (fx_i.direction == Direction.Down and fx_j.direction == Direction.Up and fx_i.low < fx_j.high):
                            bi = Bi(fx_i, fx_j)
                            self.bis.append(bi)
                            self.unresolved_bis.append(bi)
                            self.unresolved_fxs = self.unresolved_fxs[j+1:]
                            return

    def construct_zoushi(self, zs_lower_unresolved: list, zs_higher: list, zs_higher_unresolved: list):
        if zs_higher and zs_lower_unresolved:
            xd1 = zs_higher[-1]
            bi1 = zs_lower_unresolved[-1]
            if bi1.direction == xd1.direction:
                if xd1.direction == Direction.Up and bi1.start_price >= xd1.start_price and bi1.end_price >= xd1.end_price:
                    xd1.extend(zs_lower_unresolved)
                    zs_lower_unresolved.clear()
                elif xd1.direction == Direction.Down and bi1.start_price <= xd1.start_price and bi1.end_price <= xd1.end_price:
                    xd1.extend(zs_lower_unresolved)
                    zs_lower_unresolved.clear()
            elif len(zs_lower_unresolved) > 1 and len(zs_lower_unresolved) % 2 == 1:
                bi0 = zs_lower_unresolved[0]
                if xd1.direction == Direction.Up and bi1.start_price < bi0.start_price \
                   and bi1.end_price < bi0.end_price:
                    xd = ZouShi(zs_lower_unresolved[:])
                    zs_higher.append(xd)
                    zs_higher_unresolved.append(xd)
                    zs_lower_unresolved.clear()
                elif xd1.direction == Direction.Down and bi1.start_price > bi0.start_price \
                   and bi1.end_price > bi0.end_price:
                    xd = ZouShi(zs_lower_unresolved[:])
                    zs_higher.append(xd)
                    zs_higher_unresolved.append(xd)
                    zs_lower_unresolved.clear()
        elif not zs_higher:
            for i in range(len(zs_lower_unresolved)):
                bi_i = zs_lower_unresolved[i]
                for j in range(i + 1, len(zs_lower_unresolved)):
                    bi_j = zs_lower_unresolved[j]
                    if bi_i.direction == bi_j.direction:
                        if bi_i.direction == Direction.Up and bi_i.end_price < bi_j.end_price:
                            xd = ZouShi(zs_lower_unresolved[i:j+1])
                            zs_higher.append(xd)
                            zs_higher_unresolved.append(xd)
                            zs_lower_unresolved = zs_lower_unresolved[j+1:]
                            return
                        elif bi_i.direction == Direction.Down and bi_i.start_price > bi_j.start_price:
                            xd = ZouShi(zs_lower_unresolved[i:j+1])
                            zs_higher.append(xd)
                            zs_higher_unresolved.append(xd)
                            zs_lower_unresolved = zs_lower_unresolved[j+1:]
                            return

