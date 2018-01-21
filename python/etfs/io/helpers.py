import pandas as pd


def read_yahoo_csv(path=None):
   '''

   '''
   df = pd.read_csv(path, index_col='Date', parse_dates=True)

   return df

