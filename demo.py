from backtesting import Backtest
import pandas as pd
import os
import shutil

from plot import show_result

from data_reader import read_min_csv
from strategies.bbands import BBands
from strategies.supertrend import SupertrendCross


min_data_fname = "./data/300340.csv"
adj_data_fname = "./data/300340_adj.csv"
print(f"Reading data from {min_data_fname} ...", end="", flush=True)
df = read_min_csv(
    min_data_fname,
    adj_data_fname,
    freq="30min",
    start_date="20210101",
    # start_date="20220101",
    # start_date="20220901",
    end_date="20221010",
)
# df.to_csv("./ui/data/daily.csv")
# exit()
print("done")

# Chan
# bt = Backtest(df, SupertrendCross, cash=1000000, commission=0.0015, exclusive_orders=True)
bt = Backtest(df, BBands, cash=1000000, commission=0.0015, exclusive_orders=True, trade_on_close=True)
stats = bt.run()
# bt.plot(superimpose=False, resample=False)
# print(stats)

def clear_directory(dir):
    for root, dirs, files in os.walk(dir):
        for f in files:
            os.unlink(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))

if not os.path.exists("ui/dist/data"):
    os.mkdir("ui/dist/data")
else:
    clear_directory("ui/dist/data")
df.to_csv("ui/dist/data/kline.csv")
stats._trades.to_csv("ui/dist/data/trades.csv", index=False)
stats._equity_curve.to_csv("ui/dist/data/equity.csv", index_label='Datetime')
df1 = pd.concat([ind.df for ind in stats._strategy._indicators], axis=1)
df1.to_csv('ui/dist/data/indicators.csv')
show_result()
