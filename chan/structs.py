from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class ChanStructException(Exception):
    pass


class Direction(Enum):
    Up = "upward"
    Down = "downward"


class Freq(Enum):
    F1 = 1
    F5 = 5
    F15 = 15
    F30 = 30
    F60 = 60
    D = 240


@dataclass
class Bar:
    open: float
    high: float
    low: float
    close: float
    volume: float
    turnover: float
    num_trades: float
    dt: datetime
    freq: Freq
    index: int
    bar_upper_level: "Bar" = None

    def extend_with_sub_bar(self, bar: "Bar"):
        self.high = max(self.high, bar.high)
        self.low = min(self.low, bar.low)
        self.close = bar.close
        self.volume = self.volume + bar.volume
        self.turnover = self.turnover + bar.turnover
        self.num_trades = self.num_trades + bar.num_trades


class ExclusiveBar(Bar):
    open: float
    high: float
    low: float
    close: float
    volume: float
    turnover: float
    num_trades: float
    bars: list[Bar]
    direction: Direction

    def __init__(self, bars: list[Bar], direction: Direction = None):
        if direction == Direction.Up:
            self.high = max([b.high for b in bars])
            self.low = max([b.low for b in bars])
        else:
            self.high = min([b.high for b in bars])
            self.low = min([b.low for b in bars])
        self.open = bars[0].open
        self.close = bars[0].close
        self.volume = sum([b.volume for b in bars])
        self.turnover = sum([b.turnover for b in bars])
        self.num_trades = sum([b.num_trades for b in bars])
        self.bars = bars
        self.direction = direction
        self.dt = bars[0].dt
        self.freq = bars[0].freq
        self.index = bars[0].index


class FenXing:
    bars: list[Bar]
    exbars: list[ExclusiveBar]
    direction: Direction
    low: float
    high: float
    vertex_bar: Bar
    start_dt: datetime
    end_dt: datetime
    dt: datetime
    index: int

    def __init__(self, exbars: list[ExclusiveBar], direction: Direction):
        if len(exbars) != 3:
            raise Exception(f"Requires 3 exclusive bars to form a FenXing. Given {len(exbars)}.")
        self.bars = [b for exbar in exbars for b in exbar.bars]
        self.exbars = exbars
        self.direction = direction
        if direction == Direction.Up:
            self.low = min(exbars[0].low, exbars[2].low)
            self.high = exbars[1].high
            for b in exbars[1].bars:
                if b.high == self.high:
                    self.vertex_bar = b
                    self.index = b.index
                    self.dt = b.dt
                    break
        else:
            self.high = min(exbars[0].high, exbars[2].high)
            self.low = exbars[1].low
            for b in exbars[1].bars:
                if b.low == self.low:
                    self.vertex_bar = b
                    self.index = b.index
                    self.dt = b.dt
                    break
        self.start_dt = exbars[0].dt
        self.end_dt = exbars[2].dt

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        if self.direction == Direction.Up:
            return f'Ding FenXing({self.high}) at {self.dt}'
        else:
            return f'Di FenXing({self.low}) at {self.dt}'


class Bi:
    start_fx: FenXing
    end_fx: FenXing

    def __init__(self, start_fx: FenXing, end_fx: FenXing):
        self.start_fx = start_fx
        self.end_fx = end_fx

    def extend(self, fx: FenXing):
        self.end_fx = fx

    @property
    def direction(self) -> Direction:
        return self.end_fx.direction

    @property
    def start_bar(self) -> Bar:
        return self.start_fx.vertex_bar

    @property
    def end_bar(self) -> Bar:
        return self.end_fx.vertex_bar

    @property
    def start_index(self) -> int:
        return self.start_fx.index

    @property
    def end_index(self) -> int:
        return self.end_fx.index

    @property
    def start_dt(self) -> datetime:
        return self.start_fx.dt

    @property
    def end_dt(self) -> datetime:
        return self.end_fx.dt

    @property
    def start_price(self) -> float:
        if self.direction == Direction.Up:
            return self.start_fx.low
        else:
            return self.start_fx.high

    @property
    def end_price(self) -> float:
        if self.direction == Direction.Up:
            return self.end_fx.high
        else:
            return self.end_fx.low

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        if self.direction == Direction.Up:
            return f'Bi Up from {self.start_dt} ({self.start_price}) to {self.end_dt} ({self.end_price})'
        else:
            return f'Bi Down from {self.start_dt} ({self.start_price}) to {self.end_dt} ({self.end_price})'


class XianDuan:
    sub_xd: list
    freq: Freq

    def __init__(self, sub_xd: list, freq: Freq):
        self.sub_xd = sub_xd
        self.freq = freq

    def extend(self, sub_xd: list):
        self.sub_xd.extend(sub_xd)

    def start_bar_of_freq(self, freq: Freq) -> Bar:
        b0 = self.start_sub_xd.start_bar
        if b0.freq == freq:
            return b0
        else:
            b1 = b0.bar_upper_level
            while b1 is not None:
                if b1.freq == freq:
                    return b1
                if b1.bar_upper_level is None:
                    return b1
                b1 = b1.bar_upper_level
            return b1

    def end_bar_of_freq(self, freq: Freq) -> Bar:
        b0 = self.end_sub_xd.end_bar
        if b0.freq == freq:
            return b0
        else:
            b1 = b0.bar_upper_level
            while b1 is not None:
                if b1.freq == freq:
                    return b1
                if b1.bar_upper_level is None:
                    return b1
                b1 = b1.bar_upper_level
            return b1

    @property
    def start_bar(self) -> Bar:
        return self.start_bar_of_freq(self.freq)

    @property
    def end_bar(self) -> Bar:
        return self.end_bar_of_freq(self.freq)

    @property
    def start_sub_xd(self):
        return self.sub_xd[0]

    @property
    def end_sub_xd(self):
        return self.sub_xd[-1]

    @property
    def start_index(self) -> int:
        return self.start_bar.index

    @property
    def end_index(self) -> int:
        return self.end_bar.index

    def start_index_of_freq(self, freq: Freq) -> int:
        return self.start_bar_of_freq(freq).index

    def end_index_of_freq(self, freq: Freq) -> int:
        return self.end_bar_of_freq(freq).index

    @property
    def start_dt(self) -> datetime:
        return self.sub_xd[0].start_dt

    @property
    def end_dt(self) -> datetime:
        return self.sub_xd[-1].end_dt

    @property
    def start_price(self) -> float:
        return self.start_sub_xd.start_price

    @property
    def end_price(self) -> float:
        return self.end_sub_xd.end_price

    @property
    def direction(self) -> Direction:
        return self.start_sub_xd.direction

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        if self.direction == Direction.Up:
            return f'XianDuan Up from {self.start_index} ({self.start_price}) to {self.end_index} ({self.end_price})'
        else:
            return f'XianDuan Down from {self.start_index} ({self.start_price}) to {self.end_index} ({self.end_price})'


class ZhongShu:
    zss: list[XianDuan]
    start_zs: XianDuan
    end_zs: XianDuan
    start_dt: datetime
    end_dt: datetime

    def __init__(self, zss: list[XianDuan]) -> None:
        self.zss = zss
        self.start_zs = zss[0]
        self.end_zs = zss[-1]
        self.start_dt = zss[0].start_dt
        self.end_dt = zss[-1].end_dt

