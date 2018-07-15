import numpy as np
from scipy.stats import linregress


def runrate_column(df=None, column=None, window=5, win_type=None):
    '''
    Calculate the run rate, that is, the moving average,
    of a column, and add it as a new column 
    '''
    
    column_rr = column + '_rr' + str(window)
    df[column_rr] = df[column].rolling(window=window, win_type=win_type).mean()

    return df


def resample_df(df=None, column=None, resolution='B'):
    '''
    Resample data with new resolution, return as new dataframe
    '''

    return df.resample(resolution).agg({column: ['mean', 'std', 'median']})
 

def shift_column(df=None, column=None, shift=1):
    '''
    Shift column by shift rows
    '''
    
    column_shift = column + '_sh' + str(shift)
    df[column_shift] = df[column].shift(shift)

    return df


def return_column(df=None, column=None, window=1, shift=1):
    '''
    Calculate the standard deviation of data - run rate
    '''
    from pandas.tseries import offsets

    if window > 1:
        column_rr = column + '_rr' + str(window)
        print("Calculating '{0}' run rate for window size {1}".format(column, window))
        df = runrate_column(df=df, column=column, window=window)
    else:
        column_rr = column

    column_shift = column_rr + '_sh' + str(shift)
    df = shift_column(df=df, column=column_rr, shift=shift)

    column_return = column_shift + '_ret'
    df[column_return] = (df[column_rr]-df[column_shift])/df[column_rr]

    column_squared_error = column_shift + '_sqerr'
    df[column_squared_error] = np.square(df[column_return])

    print("Average volatility of '{0}' is {1}".format(column, np.sqrt(df[column_squared_error].mean())))

    return df


def difference(df=None, column=None, start='1900-01-01', end='2100-01-01'):
    '''
    Returns start and end value, absolute and relative difference
    '''
    startdate = df[df.index >= start].index[0]
    enddate = df[df.index <= end].index[-1]
    startvalue = df.loc[df.index == startdate, column][0]
    endvalue   = df.loc[df.index == enddate,   column][0]

    return startdate, startvalue, enddate, endvalue, endvalue-startvalue, (endvalue-startvalue)/startvalue


def rsq(sec1=None, sec2=None, col1='Close', col2='Close'):
    '''
    Function that returns R^2 correlation measure between two securities
    :param sec1: First security (object of class security)
    :param sec2: Second security
    :return: R^2
    '''

    if col1==col2:
        col1 = str(col1)+"_2"

    _df = sec1.data.join(sec2.data, how='inner', rsuffix='_2')[[col1, col2]]

    slope, intercept, r_value, p_value, std_err = linregress(_df[col1].values,_df[col2].values)

    return r_value**2



