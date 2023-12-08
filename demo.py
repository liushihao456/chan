from backtesting import Backtest

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
print("done")

# Chan
# bt = Backtest(df, SupertrendCross, cash=1000000, commission=0.0015, exclusive_orders=True)
bt = Backtest(df, BBands, cash=1000000, commission=0.0015, exclusive_orders=True, trade_on_close=True)
stats = bt.run()
bt.plot(superimpose=False, resample=False)
print(stats)
stats["_trades"].to_csv("result/trades.csv", index=False)
