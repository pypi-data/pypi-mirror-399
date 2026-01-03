# Copyright (c) ZhangYundi.
# Licensed under the MIT License. 
# Created on 2025/12/30 11:20
# Description:
import xcals

import lidb
from lidb import Dataset
import polars as pl

def read_kline_minute(date):
    df= lidb.scan(f"mc/stock_kline_minute/date={date}")
    return df

ds_kline_minute = Dataset(fn=read_kline_minute)

def test_depend(depend: pl.DataFrame):
    # print(depend)
    return depend.select("date", "time", "asset", "close")

ds_test_depend = Dataset(ds_kline_minute, fn=test_depend)

def test_depend2(depend):
    return lidb.from_polars(depend, ).sql("d_mean(close, 20) as close_m20")

ds_test_depend2 = Dataset(ds_test_depend, fn=test_depend2, window="20d")

if __name__ == '__main__':
    test_date = "2022-07-01"
    # print(ds_test_depend.update_time)
    # df = ds_kline_minute.get_value(test_date)
    # print(ds_test_depend._days)
    # df = ds_test_depend.get_value(test_date)
    # df = ds_test_depend2.get_value(test_date).filter(asset="000001")
    # df = ds_test_depend2.get_history(xcals.get_tradingdays("2022-05-01", "2022-07-01")).filter(date="2022-05-05", time="09:31:00")
    # print(df)
    # print(ds_test_depend.constraints)
    # df = ds_kline_minute.get_value(test_date)
    # print(df)
    print(ds_test_depend2)