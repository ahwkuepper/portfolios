# To do:
# Use API or write script to access SEC's EDGAR database
# https://www.sec.gov/oiea/Article/edgarguide.html
# https://www.sec.gov/developer
# https://github.com/datasets/edgar
# 


import pandas as pd
import numpy as np
from etfs.io import yqd


def read_yahoo_csv(path=None, startdate='2000-01-01', enddate='2100-01-01'):
   '''
   Read locally stored csv with data from Yahoo! Finance for a security.

   '''

   df = pd.read_csv(path, index_col='Date', parse_dates=True)

   return df.loc[(df.index >= startdate) & (df.index <= enddate)]


def retrieve_yahoo_quote(ticker=None, startdate='20000101', enddate='21000101'):
   '''
   Download data from Yahoo! Finance for a security.

   '''

   # Use load_yahoo_quote from yqd to request Yahoo data
   output = yqd.load_yahoo_quote(ticker, startdate, enddate)

   # Break data into column headers, column data, and index 
   header = [sub.split(",") for sub in output[:1]]
   columns=[column for column in header[0][1:]]
   entries = [sub.split(",") for sub in output[1:-1]]
   data = [data[1:] for data in entries]
   indeces = [data[:1] for data in entries]
   index = [index[0] for index in indeces]

   # Turn into pandas dataframe
   df = pd.DataFrame(data, columns=columns, index=index, dtype=np.float32)

   # Drop nulls
   col_list = ['Close', 'Volume']
   df = df.dropna(subset=[col_list], how='any')

   # Convert index to datetime
   df.index = pd.to_datetime(df.index)

   # Convert volume column to integer
   df.Volume = df.Volume.astype(np.int32)

   return df




