from dataclasses import asdict
from math import pi
from bokeh.plotting import figure, show
from bokeh.layouts import column
from chan.analyzer import ChanAnalyzer
import pandas as pd


class Plot:

    def __init__(self, analyzer: ChanAnalyzer) -> None:
        self.analyzer = analyzer
        self.freqs = analyzer.freqs
        self.ohlcv_dfs = {}
        self.bi_dfs = {}
        self.xd_dfs = {}
        for freq in self.freqs:
            bars = analyzer.stock.freq_bars[freq]
            self.ohlcv_dfs[freq] = pd.DataFrame.from_records([asdict(b) for b in bars])
            self.bi_dfs[freq] = pd.DataFrame.from_records([{'start_index': b.start_index,
                                                            'start_price': b.start_price,
                                                            'end_index': b.end_index,
                                                            'end_price': b.end_price} for b in analyzer.bis])
            self.xd_dfs[freq] = pd.DataFrame.from_records([{'start_index': xd.start_index,
                                                            'start_price': xd.start_price,
                                                            'end_index': xd.end_index,
                                                            'end_price': xd.end_price} for xd in analyzer.xds])
        pass

    def generate_plot(self) -> figure:
        kline_fig = figure(y_axis_label='Candlestick')
        kline_fig.sizing_mode = 'stretch_both'
        kline_fig.xaxis.major_label_orientation = pi / 4
        kline_fig.grid.grid_line_alpha = 0.3

        df = self.ohlcv_dfs[self.freqs[0]]
        inc = df.close > df.open
        dec = df.close < df.open
        w = 0.6
        kline_fig.segment(df.index, df.high, df.index, df.low, color='black')
        kline_fig.vbar(df.index[inc], w, df.open[inc], df.close[inc], fill_color='#D5E1DD', line_color='black')
        kline_fig.vbar(df.index[dec], w, df.open[dec], df.close[dec], fill_color='#F2583E', line_color='black')

        bi_df = self.bi_dfs[self.freqs[0]]
        kline_fig.segment(bi_df.start_index, bi_df.start_price, bi_df.end_index, bi_df.end_price, color='red')

        xd_df = self.xd_dfs[self.freqs[0]]
        kline_fig.segment(xd_df.start_index, xd_df.start_price, xd_df.end_index, xd_df.end_price, color='blue')

        vol_fig = figure(y_axis_label='Volume', height=200)
        vol_fig.sizing_mode = 'stretch_width'
        vol_fig.vbar(df.index, 0.4, 0, df.volume, color='black')

        show(column([kline_fig, vol_fig], sizing_mode='stretch_both'))
