from enum import Enum


class Operate(Enum):
    # 持有状态
    HL = "持多"  # Hold Long
    HS = "持空"  # Hold Short
    HO = "持币"  # Hold Other

    # 多头操作
    LO = "开多"  # Long Open
    LE = "平多"  # Long Exit

    # 空头操作
    SO = "开空"  # Short Open
    SE = "平空"  # Short Exit

    def __str__(self):
        return self.value


class Mark(Enum):
    D = "底分型"
    G = "顶分型"

    def __str__(self):
        return self.value


class Direction(Enum):
    Up = "向上"
    Down = "向下"

    def __str__(self):
        return self.value


class Freq(Enum):
    Tick = "Tick"
    F1 = "1min"
    F5 = "5min"
    F15 = "15min"
    F30 = "30min"
    F60 = "60min"
    D = "d"
    W = "w"
    M = "month"
    S = "quarter"
    Y = "year"

    def __str__(self):
        return self.value
