# -*- coding: utf-8 -*-

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from etfs.utils.helpers import restrict_to_trading_days


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
    _df = restrict_to_trading_days(df=_df, exchange='NYSE')
    corr = _df.corr()

    # Generate a mask for the upper triangle
    mask = np.zeros_like(corr, dtype=np.bool)
    mask[np.triu_indices_from(mask)] = True
    
    # Set up the matplotlib figure
    f, ax = plt.subplots(figsize=(11, 9))
    
    # Generate a custom diverging colormap
    cmap = sns.diverging_palette(220, 10, as_cmap=True)
    
    # Draw the heatmap with the mask and correct aspect ratio
    sns.heatmap(corr, mask=mask, cmap=cmap, vmin=-1, vmax=1, center=0,
                square=True, linewidths=.5, cbar_kws={"shrink": .5})


