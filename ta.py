import numpy as np
import talib


def BBANDS(close, n_lookback, n_std):
    upper, _, lower = talib.BBANDS(close, n_lookback, n_std, n_std, 0)
    return upper, lower


def SUPERTREND(high, low, close, n, m):
    atr = talib.ATR(high, low, close, n)
    is_up = close[n] > close[n - 1]
    res = [np.nan] * (n - 1)
    for i in range(n - 1, len(high)):
        if is_up:
            st = (high[i] + low[i]) / 2 - m * atr[i]
            if not np.isnan(res[i - 1]):
                st = max(st, res[i - 1])
            if close[i] < st:
                is_up = False
                st = (high[i] + low[i]) / 2 + m * atr[i]
            res.append(st)
        else:
            st = (high[i] + low[i]) / 2 + m * atr[i]
            if not np.isnan(res[i - 1]):
                st = min(st, res[i - 1])
            if close[i] > st:
                is_up = True
                st = (high[i] + low[i]) / 2 - m * atr[i]
            res.append(st)
    return np.array(res)


def ATRMD(high, low, close, n, m):
    atr = talib.NATR(high, low, close, n)
    sum = talib.SMA(atr, m) * m
    return atr / sum * 100
