import pandas as pd
import matplotlib.pyplot as plt
from etfs.stats.basics import runrate_column
from bokeh.plotting import figure, show, output_file
from bokeh.io import output_notebook


def plot_trend(security=None, column='Close', ndays=100, windows=[50,200]):
    '''
       Plots data and run rate with given window sizes
    '''
    
    plt.plot(security.data.index[-ndays:], security.data[column][-ndays:], label=column)
    
    windows = [window for window in windows if window < len(security.data)]
    cols = []
    for window in windows:
        col = column+"_rr{0}".format(window)
        cols.append(col)
        security.data = runrate_column(security.data, column=column, window=window)
        plt.plot(security.data.index[-ndays:], security.data[col][-ndays:], label='{0} days'.format(window))   
    
    plt.legend()



def plot_candlestick(security=None, open_col=None, close_col=None, high_col=None, low_col=None, ndays=100):
    '''
       Draws a candlestick figure for a security
    '''

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