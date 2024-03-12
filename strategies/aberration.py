import backtrader as bt


class Aberration(bt.Strategy):
    params = (
        ('bollperiod', 20),
        ('printlog', True),
    )

    def log(self, txt, dt=None, doprint=False):
        ''' Logging function fot this strategy'''
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.order = None
        self.buyprice = None
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
                    'Buy, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                self.buyprice = order.executed.price
            else:
                self.log('Sell, Price: %.2f, Cost: %.2f, Comm %.2f' %
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

        self.log('Trade profit, Gross %.2f, Net %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def next(self):
        # Check if we are in the market
        if not self.position:
            if self.data.close[0] > self.bbands.top[0] and self.data.close[-1] < self.bbands.top[-1]:
                self.order = self.buy()
            if self.data.close[0] < self.bbands.bot[0] and self.data.close[-1] > self.bbands.bot[-1]:
                self.order = self.sell()
        else:
            if self.position.size > 0:
                if self.data.close[0] < self.bbands.mid[0] and self.data.close[-1] > self.bbands.mid[-1]:
                    if self.order:
                        self.broker.cancel(self.order)
                    self.order = self.sell()
            if self.position.size < 0:
                if self.data.close[0] > self.bbands.mid[0] and self.data.close[-1] < self.bbands.mid[-1]:
                    if self.order:
                        self.broker.cancel(self.order)
                    self.order = self.buy()

