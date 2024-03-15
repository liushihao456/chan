import backtrader as bt


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
        # bt.LinePlotterIndicator(self.up_trend, name='Up trend')

        self.bbands = bt.indicators.BollingerBands(self.datas[0])
        self.rsi = bt.indicators.RSI(self.datas[0])

    def notify_order(self, order: bt.Order):
        if order.status == order.Submitted:
            return

        if order.status == order.Accepted:
            self.log('%s %s created' % (order.ExecTypes[order.exectype], 'buy' if order.isbuy() else 'sell'))
            self.order = order
            return

        if order.status == order.Completed:
            if order.isbuy():
                self.log('%s Buy executed, Price: %.2f, Position %d' %
                         (order.ExecTypes[order.exectype], order.executed.price, self.position.size))

                if order.exectype != bt.Order.Stop and self.position:
                    # self.log('Stop Sell created, Price: %.2f' % self.stopprice)
                    self.order = self.sell(exectype=bt.Order.Stop, price=self.stopprice)
                    return
            else:
                self.log('%s Sell executed, Price: %.2f, Position %d' %
                         (order.ExecTypes[order.exectype], order.executed.price, self.position.size))

                if order.exectype != bt.Order.Stop and self.position:
                    # self.log('Stop Buy created, Price: %.2f' % self.stopprice)
                    self.order = self.buy(exectype=bt.Order.Stop, price=self.stopprice)
                    return

            self.bar_executed = len(self)

        elif order.status == order.Canceled:
            self.log('%s Order canceled' % order.ExecTypes[order.exectype])

        elif order.status == order.Margin:
            self.log('%s Order margin' % order.ExecTypes[order.exectype])

        # Broker could reject order if not enough cash
        elif order.status == order.Rejected:
            self.log('%s Order rejected' % order.ExecTypes[order.exectype])

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
                    self.buy()
                    self.stopprice = min(self.data.low[0], self.data.low[-1]) - 1
            # if self.dema1[0] < self.dema2[0] < self.dema3[0]:
            if self.ema1[0] < self.ema2[0] < self.ema3[0]:
                if self.data.high[0] >= self.bbands.top[0] and self.data.close[0] <= self.data.open[0]:
                    self.log('Short sell create, %.2f position %d' % (self.dataclose[0], self.position.size))
                    self.sell()
                    self.stopprice = max(self.data.high[0], self.data.high[-1]) + 1
        else:
            if self.position.size > 0:
                # if self.data.high[0] >= self.bbands.top[0] and self.data.close[0] <= self.data.open[0]:
                if self.data.close[-1] >= self.ema1[-1] and self.data.close[0] < self.ema1[0]:
                    self.log('Sell create, %.2f' % self.dataclose[0])
                    if self.order:
                        self.broker.cancel(self.order)
                    self.sell()
            if self.position.size < 0:
                # if self.data.low[0] <= self.bbands.bot[0] and self.data.close[0] >= self.data.open[0]:
                if self.data.close[-1] <= self.ema1[-1] and self.data.close[0] > self.ema1[0]:
                    self.log('Buy cover create, %.2f' % self.dataclose[0])
                    if self.order:
                        self.broker.cancel(self.order)
                    self.buy()

    def stop(self):
        self.log('Ending Value %.2f' % (self.broker.getvalue()), doprint=True)

