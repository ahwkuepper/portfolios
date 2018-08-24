# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from etfs.security import yqd
import urllib.request, urllib.parse, urllib.error
import json
import html


def read_yahoo_csv(path=None, startdate='2000-01-01', enddate='2100-01-01'):
    """
    Read locally stored csv with data from Yahoo! Finance for a security.
 
    """
    
    df = pd.read_csv(path, index_col='Date', parse_dates=True)
 
    return df.loc[(df.index >= startdate) & (df.index <= enddate)]


def retrieve_yahoo_quote(ticker=None, startdate='20000101', enddate='21000101', info = 'quote'):
    """
    Download data from Yahoo! Finance for a security.
    info can be quote, dividend, or split
 
    """
    # Try to convert input values into right format for yahoo
    if type(startdate) != str:
       startdate = '{0}{1:02}{2:02}'.format(startdate.year, startdate.month, startdate.day)
 
    startdate = startdate.replace('-', '')
 
    if type(enddate) != str:
       enddate = '{0}{1:02}{2:02}'.format(enddate.year, enddate.month, enddate.day)
    
    enddate = enddate.replace('-', '')
 
    # Use load_yahoo_quote from yqd to request Yahoo data
    output = yqd.load_yahoo_quote(ticker, startdate, enddate, info)
 
    # Break data into column headers, column data, and index 
    header = [sub.split(",") for sub in output[:1]]
    columns=[column for column in header[0][1:]]
    entries = [sub.split(",") for sub in output[1:-1]]
    data = [data[1:] for data in entries]
    indeces = [data[:1] for data in entries]
    index = [index[0] for index in indeces]
 
    # Turn into pandas dataframe
    df = pd.DataFrame(data, columns=columns, index=index, dtype=np.float32)
    df.replace('null', np.NaN, inplace=True)

    # Drop nulls
    col_list = ['Close', 'Volume']
    df = df.dropna(subset=col_list, how='any', )
 
    # Convert index to datetime
    df.index = pd.to_datetime(df.index)
 
    # Convert volume column to integer
    df.Volume = df.Volume.astype(np.int32)
 
    return df


def get_company_name(ticker=''):
    """
       Takes a ticker symbol and queries Yahoo! Finance for metadata
    """
    if ticker:
        
        # Headers to fake a user agent
        _headers = {
            'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11'
        }
    
        # use request to retrieve data
        req = urllib.request.Request('https://query2.finance.yahoo.com/v7/finance/options/{}'.format(ticker), headers=_headers)
        f = urllib.request.urlopen(req)
        alines = f.read().decode('utf-8')
    
        # read json
        j = json.loads(alines)
        try:
            # return shortName variable
            return html.unescape(j['optionChain']['result'][0]['quote']['longName'])

        except:
            # default to ticker symbol
            return ticker
    else:
        print('Ticker symbol not specified')
        return ''
