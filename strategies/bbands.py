import backtrader as bt


# Create a Stratey
class BBands(bt.Strategy):
    params = (
        ('maperiod', 15),
        ('printlog', True),
    )

    def log(self, txt, dt=None, doprint=False):
        ''' Logging function fot this strategy'''
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None

        self.ema1 = bt.indicators.ExponentialMovingAverage(self.datas[0], period=30)
        self.ema2 = bt.indicators.ExponentialMovingAverage(self.datas[0], period=35)
        self.ema3 = bt.indicators.ExponentialMovingAverage(self.datas[0], period=40)

        self.dema1 = bt.indicators.ExponentialMovingAverage(self.datas[1], period=30)
        self.dema2 = bt.indicators.ExponentialMovingAverage(self.datas[1], period=35)
        self.dema3 = bt.indicators.ExponentialMovingAverage(self.datas[1], period=40)

        self.up_trend = bt.And(self.ema1 > self.ema2, self.ema2 > self.ema3)
        self.down_trend = bt.And(self.ema1 < self.ema2, self.ema2 < self.ema3)
        self.bigger_up_trend = bt.And(self.dema1 > self.dema2, self.dema2 > self.dema3)
        bt.LinePlotterIndicator(self.up_trend, name='Up trend')
        bt.LinePlotterIndicator(self.bigger_up_trend, name='Day up trend')
        # bt.LinePlotterIndicator(self.down_trend, name='Down trend')

        self.bbands = bt.indicators.BollingerBands(self.datas[0])

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def next(self):
        # # Check if an order is pending ... if yes, we cannot send a 2nd one
        # if self.order:
        #     return

        # Check if we are in the market
        if not self.position:
            if self.dema1[0] > self.dema2[0] > self.dema3[0]:
                if self.ema1[0] > self.ema2[0] > self.ema3[0]:
                    if self.data.low[0] <= self.bbands.bot[0] and self.data.close[0] >= self.data.open[0]:
                        self.log('BUY CREATE, %.2f' % self.dataclose[0])
                        self.order = self.buy()
            if self.dema1[0] < self.dema2[0] < self.dema3[0]:
                if self.ema1[0] < self.ema2[0] < self.ema3[0]:
                    if self.data.high[0] >= self.bbands.top[0] and self.data.close[0] <= self.data.open[0]:
                        self.log('SHORT SELL CREATE, %.2f' % self.dataclose[0])
                        self.order = self.sell()
        else:
            if self.position.size > 0:
                if not self.order:
                    self.order = self.sell(exectype=bt.Order.Stop, price=min(self.data.low[-1], self.data.low[-2]))
                if self.data.high[0] >= self.bbands.top[0] and self.data.close[0] <= self.data.open[0]:
                # if self.dataclose[-1] >= self.ema1[-1] and self.dataclose[0] < self.ema1[0]:
                    self.log('SELL CREATE, %.2f' % self.dataclose[0])
                    if self.order:
                        self.broker.cancel(self.order)
                    self.order = self.sell()
            if self.position.size < 0:
                if not self.order:
                    self.order = self.buy(exectype=bt.Order.Stop, price=max(self.data.high[-1], self.data.high[-2]))
                if self.data.low[0] <= self.bbands.bot[0] and self.data.close[0] >= self.data.open[0]:
                # if self.dataclose[-1] <= self.ema1[-1] and self.dataclose[0] > self.ema1[0]:
                    self.log('BUY COVER CREATE, %.2f' % self.dataclose[0])
                    if self.order:
                        self.broker.cancel(self.order)
                    self.order = self.buy()

    # def stop(self):
    #     self.log('(MA Period %2d) Ending Value %.2f' %
    #              (self.params.maperiod, self.broker.getvalue()), doprint=True)

