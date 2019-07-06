# -*- coding: utf-8 -*-

import numpy as np
from scipy.stats import linregress
from etfs.utils.helpers import restrict_to_trading_days


def runrate_column(df=None, column=None, window=5, win_type=None):
    """
    Calculate the run rate, that is, the moving average, 
    of a column, and add it as a new column.

    Parameters
    ==========
    df : input dataframe
    column : column for which the run rate should be computed
    window : how many observations are used for run rate
    win_type : window type, see https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.rolling.html
        'None' means equal weighting

    Returns
    =======
    df : dataframe with run rate appended as column + "_rr"

    """
    
    column_rr = column + '_rr' + str(window)
    df[column_rr] = df[column].rolling(window=window, win_type=win_type).mean()

    return df


def ewm_column(df=None, column=None, alpha=.8, ignore_na=True):
    """
    Calculate the exponentially weighted moving average 
    of a column, and add it as a new column.

    Parameters
    ==========
    df : input dataframe
    column : column for which the run rate should be computed
    alpha : smoothing factor [0 < alpha <= 1]
    ignore_na : ignore missing values

    Returns
    =======
    df : dataframe with exponentially weighted moving average appended as column + "_ewm"

    """
    
    column_ewm = column + '_ewm' + str(alpha)
    df[column_ewm] = df[column].ewm(alpha=alpha, ignore_na=ignore_na).mean()

    return df


def resample_df(df=None, column=None, resolution='B'):
    """
    Resample data with new resolution, return as new dataframe
    """

    return df.resample(resolution).agg({column: ['mean', 'std', 'median']})
 

def shift_column(df=None, column=None, shift=1):
    """
    Shift column by shift rows
    """
    
    column_shift = column + '_sh' + str(shift)
    df[column_shift] = df[column].shift(shift)

    return df, column_shift


def standard_deviation_column(df=None, column=None, window=1, shift=1):
    """
    Calculate the standard deviation of data - run rate
    """
    if window > 1:
        column_rr = column + '_rr' + str(window)
        print("Calculating '{0}' run rate for window size {1}".format(column, window))
        df = runrate_column(df=df, column=column, window=window)
    else:
        column_rr = column

    df, column_shift = shift_column(df=df, column=column_rr, shift=shift)

    column_return = column_shift + '_ret'
    df[column_return] = (df[column_rr]-df[column_shift])/df[column_rr]

    column_squared_error = column_shift + '_sqerr'
    df[column_squared_error] = np.square(df[column_return])

    print("Standard deviation of '{0}' is {1}".format(column, df[column_squared_error].mean()))
    print("Average volatility of '{0}' is {1}".format(column, np.sqrt(df[column_squared_error].mean())))

    return df


def difference(df=None, column=None, start='1900-01-01', end='2100-01-01'):
    """
    Returns start and end value, absolute and relative difference
    """
    startdate = df[df.index >= start].index[0]
    enddate = df[df.index <= end].index[-1]
    startvalue = df.loc[df.index == startdate, column][0]
    endvalue   = df.loc[df.index == enddate,   column][0]

    return startdate, startvalue, enddate, endvalue, endvalue-startvalue, (endvalue-startvalue)/startvalue


def returns_column(df=None, column=None, uselogs=True, outname='Return'):
    """
    Calculate return from timeseries of prices
    """

    def get_reldiff(a,b):
        return (a-b)/b

    def get_logratio(a,b):
        return np.log(a/b)

    try:
        out_col = outname
    except NameError:
        out_col = 'Return'

    _df, column_shift = shift_column(df, column=column, shift=1)
    
    if uselogs==False:
        _df[out_col] = _df.apply(lambda row: get_reldiff(row[column], row[column_shift]), axis=1)
    else:
        _df[out_col] = _df.apply(lambda row: get_logratio(row[column], row[column_shift]), axis=1)

    return _df.drop(column_shift, axis=1)


def rsq(sec1=None, sec2=None, col1='Close', col2='Close'):
    """
    Function that returns R^2 correlation measure between two securities
    :param sec1: First security (object of class security)
    :param sec2: Second security
    :return: R^2
    """

    if col1==col2:
        col1 = str(col1)+"_2"

    _df = sec1.data.join(sec2.data, how='inner', rsuffix='_2')[[col1, col2]].dropna(how='any')

    #_df = restrict_to_trading_days(df=_df, exchange='NYSE')

    slope, intercept, r_value, p_value, std_err = linregress(_df[col1].values,_df[col2].values)

    return r_value**2


def beta(sec1=None, sec2=None, col1='Return', col2='Return'):
    """
    Function that returns the beta of a security (sec1) with respect to
    its benchmark (sec2)
    """

    if col1==col2:
        col2 = str(col2)+"_2"

    _df = sec1.data.join(sec2.data, how='inner', rsuffix='_2')[[col1, col2]].dropna(how='any')

    #_df = restrict_to_trading_days(df=_df, exchange='NYSE')

    _cov = np.cov(_df[col1], _df[col2])[0,1]
    _var = np.var(_df[col2])

    return _cov/_var


def alpha(sec1=None, sec2=None, col1='Return', col2='Return', risk_free_rate=.004484):
    """
    Calculates alpha of a security
    Risk-free daily rate (from 3-mo. U.S. Treasury bills) = .004484 as of 8/13/18
    """

    _beta = beta(sec1=sec1, sec2=sec2, col1=col1, col2=col2)
    _avg_return1 = sec1.data[col1].mean()
    _avg_return2 = sec2.data[col2].mean()

    return _avg_return1-risk_free_rate-_beta*(_avg_return2-risk_free_rate)


