# -*- coding: utf-8 -*-

import html
import json
import urllib.error
import urllib.parse
import urllib.request

import numpy as np
import pandas as pd

from portfolios.security import yqd
from portfolios.utils.helpers import (standard_date_format, todays_date,
                                      yahoo_date_format)


def read_yahoo_csv(path=None, startdate="2000-01-01", enddate=None):
    """
    Read locally stored csv with data from Yahoo! Finance for a security.
 
    """

    if enddate == None:
        enddate = todays_date()

    # convert dates to pandas format
    startdate = standard_date_format(startdate)
    enddate = standard_date_format(enddate)

    df = pd.read_csv(path, index_col="Date", parse_dates=True)

    return df.loc[(df.index >= startdate) & (df.index <= enddate)]


def call_yqd(ticker, startdate, enddate, info):
    """
    Wrapper for yqd library for calls to Yahoo! Finance API
    """

    # Use load_yahoo_quote from yqd to request Yahoo! data
    output = yqd.load_yahoo_quote(ticker, startdate, enddate, info)

    # Break data into column headers, column data, and index
    header = [sub.split(",") for sub in output[:1]]
    columns = [column for column in header[0][1:]]
    entries = [sub.split(",") for sub in output[1:]]
    data = [data[1:] for data in entries]
    indeces = [data[:1] for data in entries]
    index = [index[0] for index in indeces]

    # Turn into pandas dataframe
    df = pd.DataFrame(data, columns=columns, index=index, dtype=np.float32)
    df.replace("null", np.NaN, inplace=True)

    # Convert index to datetime
    df.index = pd.to_datetime(df.index)

    return df


def retrieve_yahoo_quote(ticker, startdate, enddate):
    """
    Downloads price and volume data from Yahoo! Finance for a security.
    """

    df = call_yqd(ticker=ticker, startdate=startdate, enddate=enddate, info="quote")

    # Drop nulls
    col_list = ["Close", "Volume"]
    df = df.dropna(subset=col_list, how="any")

    # Convert volume column to integer
    df.Volume = df.Volume.astype(np.int32)

    return df


def retrieve_yahoo_dividends(ticker, startdate, enddate):
    """
    Downloads dividends data from Yahoo! Finance for a security.
    """

    df = call_yqd(ticker=ticker, startdate=startdate, enddate=enddate, info="dividend")

    return df


def retrieve_yahoo_splits(ticker, startdate, enddate):
    """
    Downloads split data from Yahoo! Finance for a security.
    """

    def get_split_ratio(split):
        split = split.split(":")
        if float(split[1]) != 0:
            return float(split[0]) / float(split[1])
        else:
            print("Split ratio invalid, division by zero")
            return 1.0

    df = call_yqd(ticker=ticker, startdate=startdate, enddate=enddate, info="split")

    df["split_ratio"] = df.apply(lambda x: get_split_ratio(x["Stock Splits"]), axis=1)
    df.sort_index(ascending=False, inplace=True)
    df["Modifier"] = df["split_ratio"].cumprod(axis=0)

    return df.drop(["Stock Splits", "split_ratio"], axis=1)


def retrieve_yahoo_data(ticker=None, startdate="20000101", enddate=None):
    """
    Downloads quote, dividend, and split data from Yahoo! Finance for a security.
    """

    if enddate == None:
        enddate = todays_date()

    # convert input to yahoo standard
    startdate = yahoo_date_format(startdate)
    enddate = yahoo_date_format(enddate)

    df = retrieve_yahoo_quote(ticker=ticker, startdate=startdate, enddate=enddate)
    df_dividend = retrieve_yahoo_dividends(
        ticker=ticker, startdate=startdate, enddate=enddate
    )
    df_splits = retrieve_yahoo_splits(
        ticker=ticker, startdate=startdate, enddate=enddate
    )

    df = df.join(df_dividend, how="left").fillna(0.0)
    df = df.join(df_splits["Modifier"], how="left").fillna(method="bfill").fillna(1.0)

    return df


def get_company_name(ticker=""):
    """
       Takes a ticker symbol and queries Yahoo! Finance for metadata
    """
    if ticker:

        # Headers to fake a user agent
        _headers = {
            "User-Agent": "Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11"
        }

        # use request to retrieve data
        req = urllib.request.Request(
            "https://query2.finance.yahoo.com/v7/finance/options/{}".format(ticker),
            headers=_headers,
        )
        f = urllib.request.urlopen(req)
        alines = f.read().decode("utf-8")

        # read json
        j = json.loads(alines)
        try:
            # return shortName variable
            return html.unescape(j["optionChain"]["result"][0]["quote"]["longName"])

        except:
            # default to ticker symbol
            return ticker
    else:
        print("Ticker symbol not specified")
        return ""
