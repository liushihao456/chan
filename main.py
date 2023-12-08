from chan.analyzer import ChanAnalyzer, Stock, StockSubscribeCsv
from chan.plot import Plot
from chan.structs import Freq

stocksub = StockSubscribeCsv('./data/300340.csv', '20230201')
stock = Stock(stocksub, [Freq.F1, Freq.F5, Freq.F30, Freq.D])
# stock = Stock(stocksub, [Freq.F1, Freq.F5])
analyzer = ChanAnalyzer(stock)

n = 0
while stocksub.has_next():
    stocksub.next()
    stock.step()
    analyzer.update()
    n += 1
    # if n == 600:
    #     p = Plot(analyzer)
    #     p.generate_plot()
    #     exit()

p = Plot(analyzer)
p.generate_plot()
