def runrate(df=None, column=None, window=5, win_type=None):
   '''
   Calculate the run rate, that is, the moving average,
   of a column, and add it as a new column 
   '''
   
   column_rr = column + '_rr' + str(window)
   df[column_rr] = df[column].rolling(window=window, win_type=win_type).mean()

   return df


def resample(df=None, column=None, resolution='B'):
   '''
   Resample data with new resolution, return as new dataframe
   '''
   
   return df.resample(resolution).agg({column: ['mean', 'std', 'median']})
 

def volatility(df=None, column=None, window=5, shift=1):
   '''
   Calculate the standard deviation of data - run rate
   '''
   from pandas.tseries import offsets
   
   column_rr = column + '_rr' + str(window)
   print("Calculating {0} run rate for window size {1}".format(column, window))
   df = runrate(df, column=column, window=window)

   column_shift = column_rr + '_sh' + str(shift)
   df[column_shift] = df[column_rr].shift(shift, freq=offsets.BDay())

   #column_volatility = column_shift + '_vol'
   #df

   return df


