import backtrader as bt

class StrategyWave(bt.Strategy):
    
    params = (
        ('printlog', False),
        ('smoothing_period', 5),
        ('stack_len', 3),
    )
    
    
    def log(self, txt, dt=None, doprint=False):
        ''' Logging function fot this strategy'''
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s: %s' % (dt.isoformat(), txt))
            #with open('log.txt', 'a') as file:
                #file.write('%s: %s \n' % (dt.isoformat(), txt))
        
    
    def __init__(self):
        
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close
        self.buyprice = None
        self.sellprice = None

        # Add a MovingAverageSimple indicator
        self.sma = bt.indicators.SimpleMovingAverage(
                    self.datas[0], period=self.params.smoothing_period)
        
        # Add a singal stack
        self.stack = [0] * self.params.stack_len
        
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                
                self.log('BUY EXECUTED, Price: %.2f, Lot:%i, Cash: %i, Value: %i' %
                         (order.executed.price,
                          order.executed.size,
                          self.broker.get_cash(),
                          self.broker.get_value()))
                self.buyprice = order.executed.price

            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Lot:%i, Cash: %i, Value: %i' %
                        (order.executed.price,
                          -order.executed.size,
                          self.broker.get_cash(),
                          self.broker.get_value()))
                self.sellprice = order.executed.price

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        #self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))
        
        
    def next(self):
        
        # Check if an order is pending ... if yes, we cannot send a 2nd one
        #if self.order:
        #    return
        
        for i in range(1, self.params.stack_len+1):
            self.stack[-i] = 1 if self.sma[-i+1] - self.sma[-i] > 0 else -1
            
        # Wave Buy Signal
        if self.stack[-1] == 1 and sum(self.stack) in [-1 * (self.params.stack_len - 2), -1 * (self.params.stack_len - 3)]:
            if self.buyprice is None:
                self.log('BUY CREATE, Price: %.2f, Lots: %i, Current Position: %i' % (self.dataclose[0], 
                                                                                      100, self.getposition(self.data).size))
                self.buy(size = 100)            
            elif self.dataclose > self.buyprice:
                self.log('BUY CREATE, Price: %.2f, Lots: %i, Current Position: %i' % (self.dataclose[0], 
                                                                                                 100, self.getposition(self.data).size))
                self.buy(size = 100)

        # Wave Sell Singal
        elif self.stack[-1] == -1 and sum(self.stack) in [1 * (self.params.stack_len - 2), 1 * (self.params.stack_len - 3)]:
                if self.getposition(self.data).size > 0:
                    self.log('SELL CREATE (Close), Price: %.2f, Lots: %i' % (self.dataclose[0], 
                                                                                            self.getposition(self.data).size))
                    self.close()
                    
        # Keep track of the created order to avoid a 2nd order
        #self.order = self.sell(size = self.getposition(data).size - opt_position) 
