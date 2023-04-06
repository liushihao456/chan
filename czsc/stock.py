from typing import List
import pandas as pd

from typing import List
import pandas as pd

from czsc.enum import Freq
from czsc.objects import RawBar

def format_stock_kline(kline: pd.DataFrame, symbol: str, freq: Freq) -> List[RawBar]:
    """
    :param kline: 
                                  Open       High        Low      Close   Volume  Turnover  NumTrades
        date_time                                                                                    
        2018-01-02 09:30:00  31.271191  31.604911  31.271191  31.446257  4457.00  2.562380        0.0
        2018-01-02 09:45:00  31.446257  31.511907  31.298545  31.446257  1869.00  1.071280        0.0
        2018-01-02 10:00:00  31.457199  31.457199  31.271191  31.397020  1603.00  0.918330        0.0
        2018-01-02 10:15:00  31.397020  31.484553  31.353253  31.375136   967.00  0.555230        0.0
        2018-01-02 10:30:00  31.380607  31.511907  31.375136  31.457199   756.00  0.434520        0.0
    :param freq: K线周期
    :return: 转换好的K线数据
    """
    bars = []
    # dt_key = 'time'
    # kline = kline.sort_values(dt_key, ascending=True, ignore_index=True)
    # records = kline.to_dict('records')

    # for i, record in enumerate(records):
    i = 0
    for index, record in kline.iterrows():
        # 将每一根K线转换成 RawBar 对象
        bar = RawBar(symbol=symbol, dt=pd.to_datetime(index), id=i, freq=freq,
                     open=record['Open'], close=record['Close'], high=record['High'], low=record['Low'],
                     vol=record['Volume'] * 100 if record['Volume'] else 0,  # 成交量，单位：股
                     amount=record['Turnover'] if record['Turnover'] > 0 else 0,  # 成交额，单位：元
                     )
        bars.append(bar)
        i += 1
    return bars


class StockData:

    def __init__(self, df: pd.DataFrame, symbol: str, base_freq: Freq,
                 freqs: List[Freq]):
        base_bars = format_stock_kline(df, symbol, base_freq);
        self.bars = { base_freq: base_bars }
        self.dfs = { base_freq: df }
        for f in freqs:
            if f == base_freq:
                continue
            agg = {
                "Open": "first",
                "High": "max",
                "Low": "min",
                "Close": "last",
                "Volume": "sum",
                "Turnover": "sum",
                "NumTrades": "sum",
            }
            df1 = df.resample(f.value).agg(agg).dropna()
            self.dfs[f] = df1
            self.bars[f] = format_stock_kline(df1, symbol, f)

