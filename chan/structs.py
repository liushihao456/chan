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
    start_dt: datetime
    end_dt: datetime
    start_index: int
    end_index: int
    start_price: float
    end_price: float
    direction: Direction
    
    def __init__(self, start_fx: FenXing, end_fx: FenXing):
        self.start_fx = start_fx
        self.end_fx = end_fx
        self.start_dt = start_fx.dt
        self.end_dt = end_fx.dt
        self.start_index = start_fx.index
        self.end_index = end_fx.index
        if start_fx.direction == Direction.Up:
            self.direction = Direction.Down
            self.start_price = start_fx.high
            self.end_price = end_fx.low
        else:
            self.direction = Direction.Up
            self.start_price = start_fx.low
            self.end_price = end_fx.high

    def extend(self, fx: FenXing):
        self.end_fx = fx
        self.end_dt = fx.dt
        self.end_index = fx.index
        if self.direction == Direction.Up:
            self.end_price = fx.high
        else:
            self.end_price = fx.low

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        if self.direction == Direction.Up:
            return f'Bi Up from {self.start_dt} ({self.start_price}) to {self.end_dt} ({self.end_price})'
        else:
            return f'Bi Down from {self.start_dt} ({self.start_price}) to {self.end_dt} ({self.end_price})'


class XianDuan:
    bis: list[Bi]

    def __init__(self, bis: list[Bi]):
        self.bis = bis

    def extend(self, bis: list[Bi]):
        self.bis.extend(bis)

    @property
    def start_bi(self) -> Bi:
        return self.bis[0]

    @property
    def end_bi(self) -> Bi:
        return self.bis[-1]

    @property
    def start_dt(self) -> datetime:
        return self.bis[0].start_dt

    @property
    def end_dt(self) -> datetime:
        return self.bis[-1].end_dt

    @property
    def start_price(self) -> float:
        return self.start_bi.start_price

    @property
    def end_price(self) -> float:
        return self.end_bi.end_price

    @property
    def direction(self) -> Direction:
        return self.start_bi.direction

class ZouShi:
    xds: list[XianDuan]
    start_xd: XianDuan
    end_xd: XianDuan
    start_dt: datetime
    end_dt: datetime

    def __init__(self, xds: list[XianDuan]):
        self.xds = xds
        self.start_xd = xds[0]
        self.end_xd = xds[-1]
        self.start_dt = xds[0].start_dt
        self.end_dt = xds[-1].end_dt


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

