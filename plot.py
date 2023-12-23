import http.server
import threading
import webbrowser
import time
import sys
import pandas as pd
import backtrader as bt


PORT = 8081
DIRECTORY = "ui/dist"
URL = f'http://localhost:{PORT}'

class Handler(http.server.SimpleHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def send_response_only(self, code, message=None):
        super().send_response_only(code, message)
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header("Pragma", "no-cache")
        self.send_header('Expires', '0')

def start_server():
    httpd = http.server.HTTPServer(("", PORT), Handler)
    httpd.serve_forever()

def show_result():
    threading.Thread(target=start_server).start()
    webbrowser.open_new(URL)

    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            sys.exit(0)

class BacktraderPlotter:
    
    def plot(self, strategy, **kwargs):
        df = pd.DataFrame({
            'Datetime': [bt.num2date(dt) for dt in strategy.datas[0].datetime.plot()],
            'Open': strategy.datas[0].open.plot(),
            'High': strategy.datas[0].high.plot(),
            'Low': strategy.datas[0].low.plot(),
            'Close': strategy.datas[0].close.plot(),
            'Volume': strategy.datas[0].volume.plot(),
        })
        overlay_ind_df = pd.DataFrame({
            'Datetime': [bt.num2date(dt) for dt in strategy.datas[0].datetime.plot()],
        })
        subplot_ind_df = pd.DataFrame({
            'Datetime': [bt.num2date(dt) for dt in strategy.datas[0].datetime.plot()],
        })
        equity_df = pd.DataFrame({
            'Datetime': [bt.num2date(dt) for dt in strategy.datas[0].datetime.plot()],
        })
        trade_df = pd.DataFrame({
            'Datetime': [bt.num2date(dt) for dt in strategy.datas[0].datetime.plot()],
        })

        inds = strategy.getindicators()
        obs = strategy.getobservers()
        for ind in inds:
            label = ind.plotlabel()
            plotinfo = ind.plotinfo
            if not getattr(plotinfo, 'plot'):
                continue
            for lineidx in range(ind.size()):
                line = ind.lines[lineidx]
                if getattr(plotinfo, 'subplot'):
                    subplot_ind_df = pd.concat([subplot_ind_df, pd.DataFrame({label: line.plot()})], axis=1)
                else:
                    overlay_ind_df = pd.concat([overlay_ind_df, pd.DataFrame({label: line.plot()})], axis=1)
        for ind in obs:
            label = ind.plotlabel()
            for lineidx in range(ind.size()):
                name = ind.lines._getlinealias(lineidx)
                line = ind.lines[lineidx]
                if label.startswith('Broker') and name == 'value':
                    equity_df['Equity'] = line.plot()
                if label.startswith('BuySell'):
                    if name == 'buy':
                        trade_df['Buy'] = line.plot()
                    if name == 'sell':
                        trade_df['Sell'] = line.plot()
        df.to_csv('./ui/dist/data/kline.csv', index=False)
        equity_df.to_csv('./ui/dist/data/equity.csv', index=False)
        overlay_ind_df.to_csv('./ui/dist/data/overlay_indicators.csv', index=False)
        subplot_ind_df.to_csv('./ui/dist/data/subplot_indicators.csv', index=False)
        trade_df.to_csv('./ui/dist/data/trades.csv', index=False)
        show_result()
