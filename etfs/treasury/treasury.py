# -*- coding: utf-8 -*-

from os import path
from datetime import datetime as dt
from etfs import Asset
from etfs.treasury.io import retrieve_treasury_yield_curve_rates, read_treasury_csv


class Treasury(Asset):
    """
       Class that holds a single treasury and some useful functions
    """

    def __init__(self, name, start='2000-01-01', end='2100-01-01'):
        super().__init__(name)
        self.url = 'https://www.treasury.gov/resource-center/data-chart-center/interest-rates/Pages/TextView.aspx?data=yieldAll'
        self.load(start=start, end=end)

    def load(self, datadir='../data/', start='2000-01-01', end='2100-01-01'):
        """
        Tries to load from csv first, then pulls from Yahoo!
        """
        filepath = '{0}{1}.csv'.format(datadir, self.name)
        print("Checking {}".format(filepath))

        if path.isfile(filepath):
            self.data = read_treasury_csv(path=filepath, startdate=start, enddate=end)
            if (self.data.index.max() < dt.strptime(end, '%Y-%m-%d')) | (self.data.index.min() > dt.strptime(start, '%Y-%m-%d')):
                _refresh_success = self.refresh(url=self.url, datadir=datadir, start=start, end=end)
                if _refresh_success:
                    self.data = read_treasury_csv(path=filepath, startdate=start, enddate=end)
        else:
            self.data = retrieve_treasury_yield_curve_rates(url=self.url, startdate=start, enddate=end)
            self.save(filename="{}.csv".format(self.name), datadir=datadir)

    def refresh(self, url, datadir='../data/', start='1900-01-01', end='2100-01-01'):
        """
        Tries to load from csv first, then pulls from Yahoo!
        """
        try:
            self.data = retrieve_treasury_yield_curve_rates(url=url, startdate=start, enddate=end)
            self.save(filename="{}.csv".format(self.name), datadir=datadir)
            return 1
        except:
            print('Refresh failed')
            return 0

