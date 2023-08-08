from dataclasses import asdict
from math import pi
from bokeh.plotting import figure, show
from chan.analyzer import ChanAnalyzer
import pandas as pd


class Plot:

    def __init__(self, analyzer: ChanAnalyzer) -> None:
        self.analyzer = analyzer
        self.freqs = analyzer.freqs
        self.ohlcv_dfs = {}
        self.bi_dfs = {}
        for freq in self.freqs:
            bars = analyzer.stock.freq_bars[freq]
            self.ohlcv_dfs[freq] = pd.DataFrame.from_records([asdict(b) for b in bars])
            bis = analyzer.bis
            self.bi_dfs[freq] = pd.DataFrame.from_records([{'start_index': b.start_index,
                                                            'start_price': b.start_price,
                                                            'end_index': b.end_index,
                                                            'end_price': b.end_price} for b in bis])
        pass

    def generate_plot(self) -> figure:
        p = figure(y_axis_label='Candlestick', width=1000)
        p.sizing_mode = 'stretch_both'
        p.xaxis.major_label_orientation = pi / 4
        p.grid.grid_line_alpha = 0.3

        df = self.ohlcv_dfs[self.freqs[0]]
        print(df)
        inc = df.close > df.open
        dec = df.close < df.open
        w = 0.6
        p.segment(df.index, df.high, df.index, df.low, color='black')
        p.vbar(df.index[inc], w, df.open[inc], df.close[inc], fill_color='#D5E1DD', line_color='black')
        p.vbar(df.index[dec], w, df.open[dec], df.close[dec], fill_color='#F2583E', line_color='black')

        bi_df = self.bi_dfs[self.freqs[0]]
        print(bi_df)
        p.segment(bi_df.start_index, bi_df.start_price, bi_df.end_index, bi_df.end_price, color='red')
        show(p)
