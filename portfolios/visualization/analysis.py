# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from portfolios.utils.helpers import restrict_to_trading_days


def plot_cross_correlation_matrix(portfolio=None):
    """
       Plots data and run rate with given window sizes
    """
    sns.set(style="white")

    portfolio.tickers.sort()
    try:
        portfolio.returns
    except AttributeError:
        portfolio.get_returns()
    else:
        pass

    # Compute the correlation matrix
    _df = portfolio.returns[portfolio.tickers].copy()
    # _df = restrict_to_trading_days(df=_df, exchange='NYSE')
    corr = _df.corr()

    # Generate a mask for the upper triangle
    mask = np.zeros_like(corr, dtype=np.bool)
    mask[np.triu_indices_from(mask)] = True

    # Set up the matplotlib figure
    f, ax = plt.subplots(figsize=(11, 9))

    # Generate a custom diverging colormap
    cmap = sns.diverging_palette(220, 10, as_cmap=True)

    # Draw the heatmap with the mask and correct aspect ratio
    sns.heatmap(
        corr,
        mask=mask,
        cmap=cmap,
        vmin=-1,
        vmax=1,
        center=0,
        square=True,
        linewidths=0.5,
        cbar_kws={"shrink": 0.5},
    )


def plot_security_performance(portfolio=None, ticker=None):
    """
       Plots price analysis and return of individual security in portfolio
    """
    _df = portfolio.transactions.loc[
        (portfolio.transactions.Ticker == portfolio.securities_archive[ticker].ticker)
        & (portfolio.transactions.Transaction.isin(("buy", "sell"))),
        ["Date", "Transaction", "Quantity", "TradeValue"],
    ].copy()
    _df.loc[_df.Transaction == "sell", "Quantity"] = _df.loc[
        _df.Transaction == "sell", "Quantity"
    ].apply(lambda x: -x)
    _df.loc[_df.Transaction == "sell", "TradeValue"] = _df.loc[
        _df.Transaction == "sell", "TradeValue"
    ].apply(lambda x: -x)

    # Calculate average price by date and prepare for join on timeseries
    _df = _df.groupby(by=["Date"]).sum().cumsum()
    _df["AvgPrice"] = _df["TradeValue"] / _df["Quantity"]
    _df = (
        portfolio.data[["Total", ticker]]
        .join(_df[["Quantity", "TradeValue", "AvgPrice"]], how="left", rsuffix="")
        .fillna(method="ffill")
    )
    _df["AvgValue"] = _df[ticker] / _df.Quantity

    # Set up figure
    f, axes = plt.subplots(ncols=1, nrows=3, sharex=True, figsize=(11, 9))

    # average value vs price
    axes[2].plot(_df.index, _df.AvgValue.values, label="Average value")
    axes[2].plot(_df.index, _df.AvgPrice.values, label="Average price")
    if (
        min(_df.AvgValue.min(), _df.AvgPrice.min()) < 0
        or abs(min(_df.AvgValue.min(), _df.AvgPrice.min()))
        / max(_df.AvgValue.max(), _df.AvgPrice.max())
        < 0.1
    ):
        axes[2].axhline(y=0, linestyle=":")
    axes[2].legend()

    # value vs cost
    axes[1].plot(_df.index, _df[ticker].values, label="Value")
    axes[1].plot(_df.index, _df.TradeValue.values, label="Cost")
    if (
        min(_df[ticker].min(), _df.TradeValue.min()) < 0
        or abs(min(_df[ticker].min(), _df.TradeValue.min()))
        / max(_df[ticker].max(), _df.TradeValue.max())
        < 0.1
    ):
        axes[1].axhline(y=0, linestyle=":")
    axes[1].legend()

    # return
    axes[0].plot(
        _df.index,
        _df[ticker].values - _df.TradeValue.values,
        label="{} return".format(ticker),
    )
    axes[0].axhline(y=0, linestyle=":")
    axes[0].legend()
    plt.show()
