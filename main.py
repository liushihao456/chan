from chan.analyzer import *

stocksub = StockSubscribeCsv('./data/300340.csv')
stock = Stock(stocksub, [Freq.F1, Freq.F5])
analyzer = ChanAnalyzer(stock)

n = 0
while stocksub.has_next():
    stocksub.next()
    stock.step()
    analyzer.update()
    n += 1
    if n == 10:
        exit()
