# -*- coding: utf-8 -*-

from os import path
from datetime import datetime as dt
from etfs import Asset
from etfs.treasury.io import retrieve_treasury_yield_curve_rates, read_treasury_csv
from etfs.utils.helpers import standard_date_format


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

        start = standard_date_format(start)
        end = standard_date_format(end)

        filepath = '{0}{1}.csv'.format(datadir, self.name)
        print("Checking {}".format(filepath))

        if path.isfile(filepath):
            self.data = read_treasury_csv(path=filepath, startdate=start, enddate=end)
            csv_start = standard_date_format(self.data.index.min())
            csv_end = standard_date_format(self.data.index.max())
            if (csv_end < end) | (csv_start > start):
                _refresh_success = self.refresh(url=self.url, datadir=datadir, start=min(start, csv_start), end=max(end, csv_end))
                if _refresh_success:
                    self.data = read_treasury_csv(path=filepath, startdate=start, enddate=end)
        else:
            self.data = retrieve_treasury_yield_curve_rates(url=self.url, startdate=start, enddate=end)
            self.save(filename="{}.csv".format(self.name), datadir=datadir)

    def refresh(self, url, datadir='../data/', start='1900-01-01', end='2100-01-01'):
        """
        Tries to load from csv first, then pulls from Yahoo!
        """

        start = standard_date_format(start)
        end = standard_date_format(end)

        try:
            self.data = retrieve_treasury_yield_curve_rates(url=url, startdate=start, enddate=end)
            self.save(filename="{}.csv".format(self.name), datadir=datadir)
            return 1
        except:
            print('Refresh failed')
            return 0

