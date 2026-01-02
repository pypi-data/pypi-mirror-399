# Copyright (c) ZhangYundi.
# Licensed under the MIT License. 
# Created on 2025/12/28 15:54
# Description:
from pathlib import Path
from typing import Sequence, Literal

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import polars as pl
from plotly.subplots import make_subplots

from .graph import ScatterGraph, BarGraph, HeatmapGraph
from .tears import get_summary_report
from .utils import get_forward_returns_columns
from ..plot import table as Table
import mlflow

_layout = dict(template='gridon',
               hovermode='x unified',
               hoverlabel=dict(bgcolor='rgba(255, 255, 255, 0.5)'),
               legend=dict(
                   orientation="h",  # 垂直排列
                   yanchor="bottom",  # 图例的锚点在上
                   y=1.02,  # 图例的 y 位置
                   # xanchor="center",  #
                   xanchor="right",  # 靠右
                   x=1,
                   bordercolor='lightgrey',  # 边框颜色
                   borderwidth=1,  # 边框宽度
                   bgcolor='rgba(255, 255, 255, 0.8)',  # 背景颜色
               ), )
_axis = dict(xaxis=dict(linecolor="black",
                        linewidth=1,
                        mirror=True,
                        gridcolor='lightgrey',
                        gridwidth=1,
                        griddash='dot',
                        showspikes=True,  # 启用 x 轴的十字光标
                        spikemode='across',  # 十字光标模式
                        spikecolor='black',  # 十字光标颜色
                        spikethickness=1.5,  # 十字光标粗细
                        spikedash='dot',  # 十字光标样式
                        tickformat="%Y-%m-%d"),
             yaxis=dict(linecolor="black",
                        linewidth=1,
                        mirror=True,
                        gridcolor='lightgrey',
                        gridwidth=1.5,
                        griddash='dot',
                        showspikes=True,  # 启用 x 轴的十字光标
                        spikemode='across',  # 十字光标模式
                        spikecolor='black',  # 十字光标颜色
                        spikethickness=1,  # 十字光标粗细
                        spikedash='dot',  # 十字光标样式
                        tickformat="%Y-%m-%d"),
             # height=500,
             )

def title(factor_name: str):
    _title = dict(text=f"""
                    Factor Report<br><sub>{factor_name}</sub>
                    """,
                  x=0.05,
                  y=0.98,
                  yanchor="top",
                  xanchor="left",
                  font=dict(
                      family="Courier New, monospace",
                      size=25,
                      # color="RebeccaPurple",
                      variant="small-caps",
                      weight="bold",
                  ))
    return _title


def _group_return(pred_label: pl.DataFrame = None, N: int = 5, **kwargs) -> dict[str, go.Figure]:
    """
    绘制 分组收益 图: 平均收益(直方图)/累计收益(曲线图)
    Parameters
    ----------
    pred_label
    N
    by_group
    kwargs

    Returns
    -------

    """

    # Group1 ~ Group5 only consider the dropna values
    pred_label_drop = pred_label.drop_nulls(subset=["score"])

    # Group
    grouper = ["date", "time"]

    # demean
    pred_label_demeaned = pred_label.with_columns(
        (pl.col("label") - pl.col("label").mean().over(grouper)).alias("label"))

    long_demeaned = pred_label_demeaned.filter(pl.col("quantile") == str(N))

    t_df = (pred_label_drop
            .select("date", "time", "quantile", "label")
            .group_by("date", "time", "quantile")
            .mean()
            .drop("time")
            .group_by("date", "quantile")
            .sum()
            .sort(by=["date", "quantile"]))
    # 分组平均收益
    group_mean = t_df.group_by("quantile").mean().drop("date")
    group_mean = group_mean.with_columns((pl.col("label") * 1e4).round(2))
    group_mean = group_mean.to_pandas().set_index("quantile", drop=True)
    color = np.where(group_mean["label"] > 0, '#FF3939', '#17BB43')

    group_bar_figure = BarGraph(
        group_mean,
        graph_kwargs=dict(marker_color=color),
    ).figure

    long_demeaned = (long_demeaned
                     .select("date", "time", pl.col("label").alias("long-average"))
                     .group_by("date", "time")
                     .mean()
                     .drop("time")
                     .group_by("date")
                     .sum()
                     .sort(by="date"))
    t_df = t_df.pivot(on="quantile", index="date", values="label").join(long_demeaned, on="date", how="left")
    t_df = t_df.with_columns(
        (pl.col(str(N)) - pl.col("1")).alias("long-short"),
    ).to_pandas().set_index("date", drop=True)
    # t_df = t_df.to_pandas().set_index("date", drop=True)
    t_df.rename(columns={str(i): f"G{i}" for i in range(1, N + 1)}, inplace=True)
    t_df.index = pd.to_datetime(t_df.index)

    t_df = t_df.dropna(how="all")  # for days which does not contain label
    # Cumulative Return By Group
    cum_df = (t_df.fillna(0.0) + 1).cumprod() - 1

    group_scatter_figure = ScatterGraph(
        cum_df.loc[:, :"long-average"],
        graph_kwargs=dict(hovertemplate='%{fullData.name}:%{y:.2%}<extra></extra>',),
    ).figure
    group_scatter_figure.add_trace(
        go.Scatter(
            x=cum_df.index,
            y=cum_df["long-short"],
            mode='lines',
            name="long-short",
            hovertemplate='%{fullData.name}:%{y:.2%}<extra></extra>',
            visible='legendonly'  # 默认在图例中但隐藏
        )
    )
    return group_bar_figure, group_scatter_figure


def ic_figure(ic_df: pd.DataFrame, show_nature_day=True, **kwargs) -> go.Figure:
    if show_nature_day:
        date_index = pd.date_range(ic_df.index.min(), ic_df.index.max())
        ic_df = ic_df.reindex(date_index)
    ic_bar_figure = BarGraph(
        ic_df,
        graph_kwargs=dict(hovertemplate='%{fullData.name}:%{y:.2}<extra></extra>',),
    ).figure
    return ic_bar_figure


def _pred_ic(
        pred_label: pl.DataFrame = None, methods: Sequence[Literal["IC", "Rank IC"]] = ("IC", "Rank IC"), **kwargs
) -> tuple:
    """

    :param pred_label: pl.DataFrame
    must contain one column of realized return with name `label` and one column of predicted score names `score`.
    :param methods: Sequence[Literal["IC", "Rank IC"]]
    IC series to plot.
    IC is sectional pearson correlation between label and score
    Rank IC is the spearman correlation between label and score
    For the Monthly IC, IC histogram, IC Q-Q plot.  Only the first type of IC will be plotted.
    :return:
    """
    _methods_mapping = {"IC": "pearson", "Rank IC": "spearman"}
    grouper = ["date", "time"]

    ic_df = (pred_label
             .drop_nulls(subset=grouper)
             .group_by(grouper)
             .agg(pl.corr("score", "label", method=_methods_mapping[m]).alias(m) for m in methods)
             .drop("time")
             .group_by("date")
             .mean().sort(by="date"))
    ic_df = ic_df.to_pandas().set_index("date", drop=True)
    ic_df.index = pd.to_datetime(ic_df.index)

    _ic = ic_df.iloc(axis=1)[0]

    _index = _ic.index.get_level_values(0).astype("str").str.replace("-", "").str.slice(0, 6)
    _monthly_ic = _ic.groupby(_index).mean()
    _monthly_ic.index = pd.MultiIndex.from_arrays(
        [_monthly_ic.index.str.slice(0, 4), _monthly_ic.index.str.slice(4, 6)],
        names=["year", "month"],
    )

    # fill month
    _month_list = pd.date_range(
        start=pd.Timestamp(f"{_index.min()[:4]}0101"),
        end=pd.Timestamp(f"{_index.max()[:4]}1231"),
        freq="1ME",
    )
    _years = []
    _month = []
    for _date in _month_list:
        _date = _date.strftime("%Y%m%d")
        _years.append(_date[:4])
        _month.append(_date[4:6])

    fill_index = pd.MultiIndex.from_arrays([_years, _month], names=["year", "month"])

    _monthly_ic = _monthly_ic.reindex(fill_index)

    ic_bar_figure = ic_figure(ic_df, kwargs.get("show_nature_day", False))

    ic_heatmap_figure = HeatmapGraph(
        _monthly_ic.unstack(),
        graph_kwargs=dict(xtype="array", ytype="array", showscale=False,
                          hovertemplate='%{y}-%{x}:%{z:.4}<extra></extra>'),
    ).figure

    return ic_bar_figure, ic_heatmap_figure  # , ic_hist_figure


def _pred_autocorr(pred_label: pl.DataFrame, lag=1, **kwargs) -> tuple:
    df = pred_label.with_columns(score_lag=pl.col("score").shift(lag).over("asset", order_by=["date", "time"]))
    _df = df.drop_nulls(["score", "score_lag"]).group_by("date").agg(
        autocorr=pl.corr("score", "score_lag", method="spearman")).sort("date")
    _df = _df.to_pandas().set_index("date", drop=True)
    _df.index = pd.to_datetime(_df.index)
    ac_figure = ScatterGraph(
        _df,
        graph_kwargs=dict(hovertemplate='%{fullData.name}:%{y:.2}<extra></extra>',),
    ).figure
    return ac_figure


def _pred_turnover(pred_label: pl.DataFrame, N=5, lag=1, **kwargs) -> tuple:
    pred_label = pred_label.drop_nulls(subset="quantile").filter(
        ((pl.col("quantile") == "1") | (pl.col("quantile") == str(N))))
    grouper = ["quantile", "date", "time"]
    cur_asset_set = pred_label.group_by(grouper).agg(
        pl.col("asset").unique()
    ).sort(by=grouper)
    shift_grouper = ["quantile", "time"]
    prev_asset_set = cur_asset_set.select(
        *grouper,
        pl.col("asset").shift(lag).over(shift_grouper)
    )
    r_df = cur_asset_set.join(
        prev_asset_set, on=grouper, how="left", suffix="_prev"
    ).with_columns(
        pl.col("asset").list.set_difference("asset_prev").alias("asset_diff").list.len().alias("diff_count"),
        pl.col("asset").list.len().alias("cur_count"),
    ).select(
        # "factor_quantile",
        "quantile", "date", "time",
        (pl.col("diff_count") / pl.col("cur_count")).alias("turnover")
    )
    r_df = r_df.group_by("quantile", "date").mean().drop("time").sort(by="date")
    r_df = r_df.pivot(on="quantile", index="date", values="turnover").to_pandas().set_index("date", drop=True)
    r_df.rename(columns={"1": "to:G1", str(N): f"to:G{N}"}, inplace=True)
    r_df.index = pd.to_datetime(r_df.index)

    turnover_figure = ScatterGraph(
        r_df,
        graph_kwargs=dict(hovertemplate='%{fullData.name}:%{y:.2}<extra></extra>',),
    ).figure
    return turnover_figure


def get_report(
        factor_data: pl.DataFrame,
        factor_name: str = "",
        lag: int = 1,
        N: int = 5,
        show_nature_day: bool = False,
        period: str = "",
        **kwargs, ):
    exp = mlflow.set_experiment("alphalens")
    params = {
        "lag": lag,
        "N": N,
        "period": period,
    }
    with mlflow.start_run(experiment_id=exp.experiment_id,
                          run_name=factor_name) as run:
        summary_tb = get_summary_report(factor_data,
                                        long_short=True,  # 减去市场平均
                                        group_neutral=False,
                                        by_time=True)
        metrics = {"ic": f"{summary_tb["ic"].sum():.3f}",
                   "bottom_bps": f"{summary_tb["bottom_bps"].sum():.2f}",
                   "top_bps": f"{summary_tb["top_bps"].sum():.2f}",
                   "spread_bps": f"{summary_tb["spread_bps"].sum():.2f}",
                   }
        mlflow.log_metrics(metrics)
        table = Table(summary_tb.to_pandas(), highlight_cols=["ic", "top_bps", "bottom_bps", "spread_bps"])
        if not period:
            periods = get_forward_returns_columns(factor_data.columns)
            period = periods[0]
        params["period"] = period
        mlflow.log_params(params)
        pred_label = factor_data.select("date", "time", "asset",
                                        pl.col("factor").alias("score"),
                                        pl.col(period).alias("label"),
                                        pl.col("factor_quantile").alias("quantile"))

        group_bar_figure, group_scatter_figure = _group_return(pred_label=pred_label, lag=lag, N=N,
                                                               show_nature_day=show_nature_day, **kwargs)
        ic_bar_figure, ic_heatmap_figure = _pred_ic(pred_label=pred_label, lag=lag, N=N, show_nature_day=show_nature_day,
                                                    **kwargs)
        ac_figure = _pred_autocorr(pred_label=pred_label, lag=lag, **kwargs)
        turnover_figure = _pred_turnover(pred_label=pred_label, lag=lag, N=N, show_nature_day=show_nature_day, **kwargs)

        specs = [
            [{"type": "table", "colspan": 2}, None],
            [{"type": "bar", "colspan": 2}, None],
            [{"type": "scatter", "colspan": 2}, None],
            [{"type": "bar", "colspan": 2}, None],
            [{"type": "xy", "colspan": 2}, None],
            [{"type": "scatter", "colspan": 2}, None],
            [{"type": "scatter", "colspan": 2}, None],
        ]
        row_heights = [2, 2, 2, 2, 2, 2, 2]
        rows = len(specs)
        cols = len(specs[0])
        fig = make_subplots(
            rows=rows,
            cols=cols,
            specs=specs,
            vertical_spacing=0.03,
            row_heights=[item / sum(row_heights) for item in row_heights],
            subplot_titles=["Summary(demeaned)", "Group Mean Return", "Cumulative Return", "Information Coefficient (IC)",
                            "Monthly IC", "Auto Correlation", "Top-Bottom Turnover"]
        )
        grid = [
            [table, None],
            [group_bar_figure, None],
            [group_scatter_figure, None],
            [ic_bar_figure, None],
            [ic_heatmap_figure, None],
            [ac_figure, None],
            [turnover_figure, None],
            # [group_hist_figure_1, group_hist_figure_2],
        ]

        for row_id, row_figs in enumerate(grid):
            for col_id, col_fig in enumerate(row_figs):
                if col_fig is None:
                    continue
                for k in range(len(col_fig.data)):
                    fig.add_trace(col_fig.data[k], row=row_id + 1, col=col_id + 1)
                    fig.update_xaxes(**_axis["xaxis"], row=row_id + 1, col=col_id + 1)
                    fig.update_yaxes(**_axis["yaxis"], row=row_id + 1, col=col_id + 1)
        _title = title(factor_name)
        fig.update_layout(height=rows * 350, title=_title, **_layout)
        report_name = f"factor_report.html" if not factor_name else f"factor_report({factor_name}).html"
        report_name = Path("alphalens_output") / report_name
        report_name.parent.mkdir(parents=True, exist_ok=True)
        fig.write_html(report_name)
        mlflow.log_artifact(report_name)
    return fig
