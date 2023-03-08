import pandas as pd
import datetime


def adjust_price(df: pd.DataFrame, adj_fname: str):
    adj_df = pd.read_csv(adj_fname, index_col=0, parse_dates=True)
    last_adj = adj_df.iloc[-1, 0]
    for index, row in df.iterrows():
        adj1 = adj_df.loc[index.strftime("%Y-%m-%d"), adj_df.columns[0]]
        a = adj1 / last_adj
        row.Open *= a
        row.High *= a
        row.Low *= a
        row.Close *= a


def read_min_csv(
    fname: str, adj_fname: str, freq: str = "1min", start_date=None, end_date=None
) -> pd.DataFrame:
    df = pd.read_csv(fname)
    if start_date is None:
        start_date = 0
    if end_date is None:
        end_date = 30000000
    df = df.loc[(df.TradingDay >= int(start_date)) & (df.TradingDay <= int(end_date))]
    df["date_time"] = df.apply(
        lambda r: datetime.datetime(
            int(r.TradingDay / 10000),
            int(r.TradingDay % 10000 / 100),
            int(r.TradingDay % 10000 % 100),
            int(r.TradingTime / 1000 / 10000),
            int(r.TradingTime / 1000 % 10000 / 100),
        ),
        axis=1,
    )
    df = df.drop(["TradingDay", "TradingTime"], axis=1)
    df = df.set_index("date_time")
    if freq != "1min":
        agg = {
            "Open": "first",
            "High": "max",
            "Low": "min",
            "Close": "last",
            "Volume": "sum",
            "Turnover": "sum",
            "NumTrades": "sum",
        }
        df = df.resample(freq).agg(agg)
        df = df.dropna()
    adjust_price(df, adj_fname)
    return df
