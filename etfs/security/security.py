# -*- coding: utf-8 -*-

from etfs.security.io import read_yahoo_csv, retrieve_yahoo_quote, get_company_name
from os import path


class Security(object):
    '''
       Class that holds a single security and some useful functions
    '''

    def __init__(self, name, start='2000-01-01', end='2100-01-01'):
        self.ticker = name
        self.name = name
        self.set_name(name)
        self.load(start=start, end=end)
        self.get_last_price()
        self.get_max_price()
        self.get_min_price()
        self.get_median_price()
        self.get_mean_price()
        self.get_std_price()
        self.dividends = 0.0

    def set_name(self, name):
        self.name = get_company_name(ticker=name)

    def load(self, start='2000-01-01', end='2100-01-01'):
        '''
        Tries to load from csv first, then pulls from Yahoo!
        '''
        filepath = '../data/{0}.csv'.format(self.ticker)
        if path.isfile(filepath):
            self.data = read_yahoo_csv(path=filepath, startdate=start, enddate=end)
        else:
            self.data = retrieve_yahoo_quote(ticker=self.ticker, startdate=start, enddate=end)

    def refresh(self, start='1900-01-01', end='2100-01-01'):
        '''
        Tries to load from csv first, then pulls from Yahoo!
        '''
        try:
            self.data = retrieve_yahoo_quote(ticker=self.ticker, startdate=start, enddate=end)
            filepath = '../data/{0}.csv'.format(self.ticker)
            print(filepath)
            self.data.index.name = 'Date'
            self.data.to_csv(filepath, header=True, index=True)
        except:
            print('Refresh failed')

    def get_last_price(self, column='Close'):
        self.last_price = self.data[column][-1]
        return self.last_price

    def get_max_price(self, column='Close'):
        self.max_price = self.data[column].max()
        return self.max_price

    def get_min_price(self, column='Close'):
        self.min_price = self.data[column].min()
        return self.min_price

    def get_median_price(self, column='Close'):
        self.median_price = self.data[column].median()
        return self.median_price

    def get_mean_price(self, column='Close'):
        self.mean_price = self.data[column].mean()
        return self.mean_price

    def get_std_price(self, column='Close'):
        self.std_price = self.data[column].std()
        return self.std_price

    def get_price_at(self, date, column='Close'):
        return self.data.loc[self.data.index == date, column].values[0]

    def dividend(self, currency, price, quantity):
        self.dividends = self.dividends + price*quantity

