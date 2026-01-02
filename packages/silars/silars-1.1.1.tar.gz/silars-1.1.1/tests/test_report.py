# Copyright (c) ZhangYundi.
# Licensed under the MIT License. 
# Created on 2025/12/28 16:21
# Description:

from silars.alphalens.report import get_report
import polars as pl
import mlflow


file_name = "factor_data.parquet"

if __name__ == '__main__':
    data = pl.read_parquet(file_name)
    fig = get_report(data, factor_name="d_ewmmean(cs_moderate(sd), {'half_life': 20})", N=10)
    fig.show()
