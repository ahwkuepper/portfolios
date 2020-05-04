# -*- coding: utf-8 -*-

from datetime import datetime as dt
from os import path

import pandas as pd

from etfs import Asset
from etfs.security.io import get_company_name, read_yahoo_csv, retrieve_yahoo_quote
from etfs.stats.basics import returns_column
from etfs.utils.helpers import last_trading_day, standard_date_format, todays_date


class Security(Asset):
    """
       Class that holds a single security and some useful functions
    """

    def __init__(self, name, start="2000-01-01", end=None):
        super().__init__(name)
        if end is None:
            end = standard_date_format(todays_date())
        self.ticker = name
        self.set_name(name)
        self.load(start=start, end=end)
        self.get_last_price()
        self.get_max_price()
        self.get_min_price()
        self.get_median_price()
        self.get_mean_price()
        self.get_std_price()
        self.dividends = 0.0
        self.benchmark_ticker = "sp500"
        self.benchmark = None

    def set_name(self, name):
        try:
            self.name = get_company_name(ticker=name)
        except:
            self.name = name

    def load(self, datadir="../data/", start="2000-01-01", end=None):
        """
        Tries to load from csv first, then pulls from Yahoo!
        """
        filepath = "{0}{1}.csv".format(datadir, self.ticker)
        print("Checking {}".format(filepath))

        if end is None:
            end = standard_date_format(todays_date())

        start = standard_date_format(pd.to_datetime(start))
        end = standard_date_format(last_trading_day(date=end))

        if path.isfile(filepath):
            self.data = read_yahoo_csv(path=filepath, startdate=start, enddate=end)
            csv_start = standard_date_format(self.data.index.min())
            csv_end = standard_date_format(self.data.index.max())
            if (pd.to_datetime(csv_end) < pd.to_datetime(end)) | (
                pd.to_datetime(csv_start) > pd.to_datetime(start)
            ):
                _refresh_success = self.refresh(
                    datadir=datadir, start=min(start, csv_start), end=max(end, csv_end)
                )
            else:
                _refresh_success = 1
            if _refresh_success:
                self.data = read_yahoo_csv(path=filepath, startdate=start, enddate=end)
        else:
            self.data = retrieve_yahoo_quote(
                ticker=self.ticker, startdate=start, enddate=end
            )
            self.save(filename="{}.csv".format(self.ticker), datadir=datadir)

    def refresh(self, datadir="../data/", start="1900-01-01", end=None):
        """
        Tries to load from csv first, then pulls from Yahoo!
        """

        if end is None:
            end = todays_date()

        start = standard_date_format(start)
        end = standard_date_format(end)

        try:
            self.data = retrieve_yahoo_quote(
                ticker=self.ticker, startdate=start, enddate=end
            )
            self.save(filename="{}.csv".format(self.ticker), datadir=datadir)
            return 1
        except:
            print("Refresh failed")
            return 0

    def get_last_price(self, column="Close"):
        self.last_price = self.data[column][-1]
        return self.last_price

    def get_max_price(self, column="Close"):
        self.max_price = self.data[column].max()
        return self.max_price

    def get_min_price(self, column="Close"):
        self.min_price = self.data[column].min()
        return self.min_price

    def get_median_price(self, column="Close"):
        self.median_price = self.data[column].median()
        return self.median_price

    def get_mean_price(self, column="Close"):
        self.mean_price = self.data[column].mean()
        return self.mean_price

    def get_std_price(self, column="Close"):
        self.std_price = self.data[column].std()
        return self.std_price

    def get_price_at(self, date, column="Close"):
        return self.data.loc[self.data.index == date, column].values[0]

    def dividend(self, currency, price, quantity):
        self.dividends = self.dividends + price * quantity

    def get_returns(self, column="Close"):
        self.data, _ = returns_column(df=self.data, column=column)

    def get_benchmark(self, benchmark_ticker="^GSPC"):

        self.min_date = self.data.index.min()
        self.max_date = min(self.data.index.max(), dt.now())

        if benchmark_ticker == "sp500" or benchmark_ticker == "^GSPC":
            _ticker = "^GSPC"
        elif benchmark_ticker:
            _ticker = benchmark_ticker
        else:
            _ticker = "^GSPC"  # S&P 500 as default

        # create security class object for benchmark ticker
        _benchmark = Security(_ticker, start=self.min_date, end=self.max_date)

        # calculate returns for the benchmark
        _benchmark.data, _ = returns_column(
            df=_benchmark.data, column="Close", uselogs=True
        )

        self.benchmark = _benchmark
