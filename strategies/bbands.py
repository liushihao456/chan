import backtrader as bt
from ta import BBANDS, SUPERTREND


class BBands(bt.Strategy):
    params = (
        ('maperiod', 15),
        ('printlog', True),
    )

    def log(self, txt, doprint=False):
        ''' Logging function fot this strategy'''
        if self.params.printlog or doprint:
            dt = self.datas[0].datetime.date(0)
            time = self.datas[0].datetime.time(0)
            print('%s %s, %s' % (dt, time, txt))

    def __init__(self):
        self.dataclose = self.datas[0].close

        self.order = None
        self.stopprice = 0

        self.ema1 = bt.indicators.ExponentialMovingAverage(self.datas[0], period=30)
        self.ema2 = bt.indicators.ExponentialMovingAverage(self.datas[0], period=35)
        self.ema3 = bt.indicators.ExponentialMovingAverage(self.datas[0], period=40)

        # self.dema1 = bt.indicators.ExponentialMovingAverage(self.datas[1], period=30)
        # self.dema2 = bt.indicators.ExponentialMovingAverage(self.datas[1], period=35)
        # self.dema3 = bt.indicators.ExponentialMovingAverage(self.datas[1], period=40)

        # self.up_trend = bt.And(self.ema1 > self.ema2, self.ema2 > self.ema3)
        # self.down_trend = bt.And(self.ema1 < self.ema2, self.ema2 < self.ema3)
        # # self.bigger_up_trend = bt.And(self.dema1 > self.dema2, self.dema2 > self.dema3)
        # bt.LinePlotterIndicator(self.up_trend, name='Up trend')
        # # bt.LinePlotterIndicator(self.bigger_up_trend, name='Day up trend')
        # # bt.LinePlotterIndicator(self.down_trend, name='Down trend')

        self.bbands = bt.indicators.BollingerBands(self.datas[0])
        self.atr = bt.indicators.ATR(self.datas[0])

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('Buy executed, Price: %.2f, Position %d' %
                         (order.executed.price, self.position.size))

                if order.exectype != bt.Order.Stop and self.position:
                    self.log('Sell stop created, Price: %.2f' % self.stopprice)
                    self.order = self.sell(exectype=bt.Order.Stop, price=self.stopprice)
                    return
            else:
                self.log('Sell executed, Price: %.2f, Position %d' %
                         (order.executed.price, self.position.size))

                if order.exectype != bt.Order.Stop and self.position:
                    self.log('Buy stop created, Price: %.2f' % self.stopprice)
                    self.order = self.buy(exectype=bt.Order.Stop, price=self.stopprice)
                    return

            self.bar_executed = len(self)

        # Broker could reject order if not enough cash
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('------ Operation profit, gross %.2f, net %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def next(self):
        if not self.position and not self.order:
            # if self.dema1[0] > self.dema2[0] > self.dema3[0]:
            if self.ema1[0] > self.ema2[0] > self.ema3[0]:
                if self.data.low[0] <= self.bbands.bot[0] and self.data.close[0] >= self.data.open[0]:
                    self.log('Buy create, %.2f' % self.dataclose[0])
                    self.order = self.buy()
                    self.stopprice = min(self.data.low[0], self.data.low[-1]) - 1
            # if self.dema1[0] < self.dema2[0] < self.dema3[0]:
            if self.ema1[0] < self.ema2[0] < self.ema3[0]:
                if self.data.high[0] >= self.bbands.top[0] and self.data.close[0] <= self.data.open[0]:
                    self.log('Short sell create, %.2f position %d' % (self.dataclose[0], self.position.size))
                    self.order = self.sell()
                    self.stopprice = max(self.data.high[0], self.data.high[-1]) + 1
        else:
            if self.position.size > 0:
                if self.data.high[0] >= self.bbands.top[0] and self.data.close[0] <= self.data.open[0]:
                # if self.dataclose[-1] >= self.ema1[-1] and self.dataclose[0] < self.ema1[0]:
                    self.log('Sell create, %.2f' % self.dataclose[0])
                    if self.order:
                        self.broker.cancel(self.order)
                    self.order = self.sell()
            if self.position.size < 0:
                if self.data.low[0] <= self.bbands.bot[0] and self.data.close[0] >= self.data.open[0]:
                # if self.dataclose[-1] <= self.ema1[-1] and self.dataclose[0] > self.ema1[0]:
                    self.log('Buy cover create, %.2f' % self.dataclose[0])
                    if self.order:
                        self.broker.cancel(self.order)
                    self.order = self.buy()

    def stop(self):
        self.log('Ending Value %.2f' % (self.broker.getvalue()), doprint=True)

