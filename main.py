import datetime
import backtrader as bt

from plot import BacktraderPlotter
from strategies.bbands import BBands
from strategies.wave import StrategyWave


if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.broker.setcash(1000000)
    data = bt.feeds.GenericCSVData(
        dataname='./data/300340.csv',
        # dataname='./data/tmp.csv',
        timeframe=bt.TimeFrame.Minutes,
        fromdate=datetime.datetime(2022, 1, 1),
        todate=datetime.datetime(2022, 9, 4),
        datetime=0,
        time=1,
        open=2,
        high=3,
        low=4,
        close=5,
        volume=6,
        openinterest=-1,
        dtformat='%Y%m%d',
        tmformat='%H%M%S000',
        # dtformat='%Y-%m-%d',
        # tmformat='%H:%M:%S.000',
    )
    # cerebro.adddata(data)
    cerebro.resampledata(data, timeframe=bt.TimeFrame.Minutes, compression=30)
    cerebro.resampledata(data, timeframe=bt.TimeFrame.Days)
    cerebro.addstrategy(BBands)
    # cerebro.addstrategy(StrategyWave)
    # strats = cerebro.optstrategy(TestStrategy, maperiod=range(10, 31))
    cerebro.broker.setcommission(commission=0.001)
    cerebro.addsizer(bt.sizers.FixedSize, stake=10)

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.run()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    cerebro.plot(BacktraderPlotter())
    # cerebro.plot(style='bar')
