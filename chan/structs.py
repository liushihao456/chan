from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import pandas as pd


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

    def __init__(self, bars: list[Bar], direction: Direction):
        if direction > 0:
            self.open = bars[0].open
            self.high = max([b.high for b in bars])
            self.low = max([b.low for b in bars])
            self.close = bars[0].close
            self.volume = sum([b.volume for b in bars])
            self.turnover = sum([b.turnover for b in bars])
            self.num_trades = sum([b.num_trades for b in bars])
            self.bars = bars
            self.direction = direction


class FenXing:
    bars: list[Bar]
    exbars: list[ExclusiveBar]
    direction: Direction
    low: float
    high: float
    start_dt: datetime
    end_dt: datetime

    def __init__(self, exbars: list[ExclusiveBar], direction: Direction):
        if len(exbars) != 3:
            raise Exception(f"Requires 3 exclusive bars to form a FenXing. Given {len(exbars)}.")
        self.bars = [b for exbar in exbars for b in exbar.bars]
        self.exbars = exbars
        self.direction = direction
        if direction == Direction.Up:
            self.low = min(exbars[0].low, exbars[2].low)
            self.high = exbars[1].high
        else:
            self.high = min(exbars[0].high, exbars[2].high)
            self.low = exbars[1].low


class Bi:
    start_fx: FenXing
    end_fx: FenXing
    start_dt: datetime
    end_dt: datetime
    direction: Direction
    
    def __init__(self, start_fx: FenXing, end_fx: FenXing):
        self.start_fx = start_fx
        self.end_fx = end_fx
        self.start_dt = start_fx.start_dt
        self.end_dt = end_fx.end_dt
        if start_fx.direction == Direction.Up:
            self.direction = Direction.Down
        else:
            self.direction = Direction.Up


class XianDuan:
    bis: list[Bi]
    start_bi: Bi
    end_bi: Bi
    start_dt: datetime
    end_dt: datetime

    def __init__(self, bis: list[Bi]):
        self.bis = bis
        self.start_bi = bis[0]
        self.end_bi = bis[-1]
        self.start_dt = bis[0].start_dt
        self.end_dt = bis[-1].end_dt


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

