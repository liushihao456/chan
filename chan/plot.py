import os
from dataclasses import asdict
from math import pi
from bokeh.models import ColumnDataSource, CrosshairTool, CustomJS, HoverTool, RadioButtonGroup
from bokeh.plotting import figure, show
from bokeh.layouts import column
from bokeh.transform import factor_cmap
from chan.analyzer import ChanAnalyzer
import pandas as pd


class Plot:

    def __init__(self, analyzer: ChanAnalyzer) -> None:
        self.analyzer = analyzer
        self.freqs = analyzer.freqs
        self.kline_dfs = {}
        self.bi_dfs = {}
        self.xd_dfs = {}
        for freq in self.freqs:
            bars = analyzer.stock.freq_bars[freq]
            self.kline_dfs[freq] = pd.DataFrame.from_records([asdict(b) for b in bars])
            self.bi_dfs[freq] = pd.DataFrame.from_records([{'start_index': b.start_index,
                                                            'start_price': b.start_price,
                                                            'end_index': b.end_index,
                                                            'end_price': b.end_price} for b in analyzer.bis])
            self.xd_dfs[freq] = pd.DataFrame.from_records([{'start_index': xd.start_index,
                                                            'start_price': xd.start_price,
                                                            'end_index': xd.end_index,
                                                            'end_price': xd.end_price} for xd in analyzer.xds])

        self.bull_color = '#D5E1DD'
        self.bear_color = '#F2583E'

        with open(
            os.path.join(os.path.dirname(__file__), "autoscale_cb.js"), encoding="utf-8"
        ) as _f:
            self._AUTOSCALE_JS_CALLBACK = _f.read()

        pass

    def generate_plot(self) -> figure:
        tools_kwargs = {
            'tools': 'xpan,xbox_zoom,xwheel_zoom,undo,redo,reset,save',
            'active_drag': 'xpan',
            'active_scroll': 'xwheel_zoom'
        }

        kline_fig = figure(y_axis_label='Candlestick', **tools_kwargs)
        kline_fig.sizing_mode = 'stretch_both'
        kline_fig.xaxis.major_label_orientation = pi / 4
        kline_fig.grid.grid_line_alpha = 0.3

        # Here source must be a standalone object, insteading being assigned or
        # copied from `sources', so that in the radio group callback, changing
        # source's data will not affect the data in `sources'.
        source = None
        sources = {}
        for freq in self.freqs:
            df = self.kline_dfs[freq]
            inc = df.close > df.open
            source0 = ColumnDataSource({
                'index': df.index,
                'dt': df.dt,
                'open': df.open,
                'high': df.high,
                'low': df.low,
                'close': df.close,
                'volume': df.volume,
                'inc': inc.astype(str),
            })
            sources[str(freq.value)] = source0
            if freq == self.freqs[0]:
                source = ColumnDataSource({
                    'index': df.index,
                    'dt': df.dt,
                    'open': df.open,
                    'high': df.high,
                    'low': df.low,
                    'close': df.close,
                    'volume': df.volume,
                    'inc': inc.astype(str),
                })

        bull_bear_cmap = factor_cmap('inc', palette=[self.bull_color, self.bear_color],
                                     factors=['True', 'False'])
        w = 0.6
        kline_seg = kline_fig.segment('index', 'high', 'index', 'low', color='black', source=source)
        kline_fig.vbar('index', w, 'open', 'close', line_color='black', fill_color=bull_bear_cmap, source=source)

        bi_df = self.bi_dfs[self.freqs[0]]
        kline_fig.segment(bi_df.start_index, bi_df.start_price, bi_df.end_index, bi_df.end_price, color='red')

        xd_df = self.xd_dfs[self.freqs[0]]
        kline_fig.segment(xd_df.start_index, xd_df.start_price, xd_df.end_index, xd_df.end_price, color='blue')

        vol_fig = figure(y_axis_label='Volume', height=200, x_range=kline_fig.x_range, **tools_kwargs)
        vol_fig.sizing_mode = 'stretch_width'
        vol_fig.vbar('index', 0.4, 0, 'volume', color=bull_bear_cmap, source=source)

        # Dynamically scales y range after zooming
        custom_js_args = dict(ohlc_range=kline_fig.y_range, source=source)

        custom_js_args.update(volume_range=vol_fig.y_range)

        # indicator_ranges = {}
        # for idx, (indicator, indicator_idx) in enumerate(zip(indicator_figs, non_overlay_indicator_idxs)):
        #     indicator_range_key = f'indicator_{indicator_idx}_range'
        #     indicator_ranges.update({indicator_range_key: indicator.y_range})
        # custom_js_args.update(indicator_ranges=indicator_ranges)

        kline_fig.x_range.js_on_change(
            "end", CustomJS(args=custom_js_args, code=self._AUTOSCALE_JS_CALLBACK)
        )

        # Linked crosshair
        linked_crosshair = CrosshairTool(dimensions='both')
        kline_fig.add_tools(linked_crosshair)
        vol_fig.add_tools(linked_crosshair)

        # Hover tooltips
        kline_fig.add_tools(
            HoverTool(
                tooltips=[
                    ('Datetime', '@dt{%F %T}'),
                    ('Open', '@open{0.00}'),
                    ('High', '@high{0.00}'),
                    ('Low', '@low{0.00}'),
                    ('Close', '@close{0.00}'),
                    ('Volume', '@volume'),
                ],
                formatters= {
                    '@dt': 'datetime',
                },
                mode='vline',
                renderers=[kline_seg]
            )
        )

        # Add radio buttons to select frequencies
        radio_group_labels = [str(f.value) for f in self.freqs]
        radio_group = RadioButtonGroup(labels=radio_group_labels, active=0)
        radio_group.js_on_change('active',
                                 CustomJS(args=dict(labels=radio_group_labels, sources=sources, source=source),
                                          code="""
                                          // Get the current data source
                                          var current_source = sources[labels[cb_obj.active]];
    
                                          // Update the data source of the plot
                                          source.data = current_source.data;
                                          source.change.emit();
                                          """))

        show(column([radio_group, kline_fig, vol_fig], sizing_mode='stretch_both'))
