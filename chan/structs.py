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
                    self.index = b.index
                    self.dt = b.dt
                    break
        else:
            self.high = min(exbars[0].high, exbars[2].high)
            self.low = exbars[1].low
            for b in exbars[1].bars:
                if b.low == self.low:
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


class ZouShi:
    sub_zs: list

    def __init__(self, sub_zs: list):
        self.sub_zs = sub_zs

    def extend(self, sub_zs: list):
        self.sub_zs.extend(sub_zs)

    @property
    def start_sub_zs(self):
        return self.sub_zs[0]

    @property
    def end_sub_zs(self):
        return self.sub_zs[-1]

    @property
    def start_index(self) -> int:
        return self.sub_zs[0].start_index

    @property
    def end_index(self) -> int:
        return self.sub_zs[-1].end_index

    @property
    def start_dt(self) -> datetime:
        return self.sub_zs[0].start_dt

    @property
    def end_dt(self) -> datetime:
        return self.sub_zs[-1].end_dt

    @property
    def start_price(self) -> float:
        return self.start_sub_zs.start_price

    @property
    def end_price(self) -> float:
        return self.end_sub_zs.end_price

    @property
    def direction(self) -> Direction:
        return self.start_sub_zs.direction

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        if self.direction == Direction.Up:
            return f'Zoushi Up from {self.start_index} ({self.start_price}) to {self.end_index} ({self.end_price})'
        else:
            return f'Zoushi Down from {self.start_index} ({self.start_price}) to {self.end_index} ({self.end_price})'


class ZhongShu:
    zss: list[ZouShi]
    start_zs: ZouShi
    end_zs: ZouShi
    start_dt: datetime
    end_dt: datetime

    def __init__(self, zss: list[ZouShi]) -> None:
        self.zss = zss
        self.start_zs = zss[0]
        self.end_zs = zss[-1]
        self.start_dt = zss[0].start_dt
        self.end_dt = zss[-1].end_dt

