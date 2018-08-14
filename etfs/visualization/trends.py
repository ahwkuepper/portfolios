# -*- coding: utf-8 -*-

import pandas as pd
import matplotlib.pyplot as plt
from etfs.stats.basics import runrate_column, ewm_column
from bokeh.plotting import figure, show, output_file
from bokeh.io import output_notebook


def plot_trend(security=None, column='Close', ndays=100, windows=[50,200]):
    """
       Plots data and run rate with given window sizes
    """
    
    plt.plot(security.data.index[-ndays:], security.data[column][-ndays:], label=column)
    
    windows = [window for window in windows if window < len(security.data)]
    cols = []
    for window in windows:
        col = column+"_rr{0}".format(window)
        cols.append(col)
        security.data = runrate_column(security.data, column=column, window=window)
        plt.plot(security.data.index[-ndays:], security.data[col][-ndays:], label='{0} days'.format(window))   
    
    plt.legend()


def plot_ewm(security=None, column='Close', ndays=100, alphas=[.7,.3]):
    """
       Plots data and exponentially weighted moving average with given alphas
    """
    
    plt.plot(security.data.index[-ndays:], security.data[column][-ndays:], label=column)
    
    cols = []
    for alpha in alphas:
        col = column+"_ewm{0}".format(alpha)
        cols.append(col)
        security.data = ewm_column(security.data, column=column, alpha=alpha)
        plt.plot(security.data.index[-ndays:], security.data[col][-ndays:], label='alpha = {0}'.format(alpha))   
    
    plt.legend()


def plot_candlestick(security=None, 
                     open_col=None, 
                     close_col=None, 
                     high_col=None, 
                     low_col=None, 
                     ndays=100,
                     heikin=False):
    """
       Draws a candlestick figure for a security
       Set heikin=True for Heikin-Ashi type of candlestick chart
    """

    if heikin == True:
        def heikin_mean(a,b,c,d):
            return (a+b+c+d)/4.

        def heikin_midpoint(a,b):
            return (a+b)/2.

        def heikin_max(a,b,c):
            return max(a,b,c)

        def heikin_min(a,b,c):
            return min(a,b,c)

        df = security.data.join(security.data.shift(periods=1), rsuffix='_lag')[-ndays:]
        
        df['Close_heikin'] = df[close_col].values
        df['Open_heikin']  = df[open_col].values
        df['High_heikin']  = df[high_col].values
        df['Low_heikin']   = df[low_col].values

        df[close_col] = df.apply(lambda row: heikin_mean(row['Open_heikin'], row['High_heikin'], row['Low_heikin'], row['Close_heikin']), axis=1)
        df[open_col]  = df.apply(lambda row: heikin_midpoint(row["{}_lag".format(open_col)], row["{}_lag".format(close_col)]), axis=1)
        df[high_col]  = df.apply(lambda row: heikin_max(row['High_heikin'], row['Open_heikin'], row['Close_heikin']), axis=1)
        df[low_col]   = df.apply(lambda row: heikin_min(row['Low_heikin'], row['Open_heikin'], row['Close_heikin']), axis=1)

    else:
        df = security.data[-ndays:]

    inc = df[close_col] > df[open_col]
    dec = df[open_col] > df[close_col]
    
    w = 12*60*60*1000 # half day in ms
    TOOLS = "pan,wheel_zoom,box_zoom,reset,save"

    p = figure(x_axis_type="datetime", tools=TOOLS, plot_width=900, title = "")
    p.xaxis.major_label_orientation = 3.1416/4
    p.grid.grid_line_alpha=0.3

    p.segment(df.index, df[high_col], df.index, df[low_col], color="black")
    p.vbar(df.index[inc], w, df[open_col][inc], df[close_col][inc], fill_color="#D5E1DD", line_color="black")
    p.vbar(df.index[dec], w, df[open_col][dec], df[close_col][dec], fill_color="#F2583E", line_color="black")

    #output_file("candlestick.html", title="candlestick.py example")
    output_notebook()

    show(p)
