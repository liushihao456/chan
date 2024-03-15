import datetime
import backtrader as bt

from plot import BacktraderPlotter
from strategies.aberration import Aberration
from strategies.bbands import BBands
from strategies.wave import StrategyWave


if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.broker.setcash(6000)
    data = bt.feeds.GenericCSVData(
        dataname='./data/000001.csv',
        # dataname='./data/tmp.csv',
        timeframe=bt.TimeFrame.Minutes,
        fromdate=datetime.datetime(2022, 1, 1),
        todate=datetime.datetime(2024, 1, 1),
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
    )
    # cerebro.adddata(data)
    cerebro.resampledata(data, timeframe=bt.TimeFrame.Minutes, compression=30, boundoff=1, rightedge=False)
    cerebro.resampledata(data, timeframe=bt.TimeFrame.Days)
    cerebro.addstrategy(BBands)
    # cerebro.addstrategy(StrategyWave)
    # cerebro.addstrategy(Aberration)
    # strats = cerebro.optstrategy(TestStrategy, maperiod=range(10, 31))
    cerebro.broker.setcommission(commission=0.0005)
    cerebro.addsizer(bt.sizers.FixedSize, stake=1)

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.run()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    cerebro.plot(BacktraderPlotter())
    # cerebro.plot(style='bar')
