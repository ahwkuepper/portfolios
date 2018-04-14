# Write a class that holds a single security
# Content:
#  + Raw data (date, closing price, volume)
#  - Dividends
#  - Splits
#  + Ticker symbol
#  + Name 
#  - Description
#  - SEC regulatory filings (see I/O)
#
# Create containers for special security types like treasury bonds
# https://www.treasury.gov/resource-center/data-chart-center/interest-rates/Pages/TextView.aspx?data=yieldAll
#
# Methods:
#  + Current price
#  - Price at date
#  - Difference in prices
#  + Min / Max price
#  + Mean / median price
#  + Standard deviation
#  - Variability
#  + Runrate
#  - Rolling weighted average (with different weighting functions)
#  - Volatility (historical / implied / epxonentially weighted)
#  - Predictions (like runrate, RWA, autoregressive model)
#  - Comparisons against other securities or indices:
#        - R^2
#        - Beta
#        - Sharpe ratio
#  - Performance:
#        - YTD
#        - 52 week
#        - 5 year 
#        - 10 year
#        - average annual return
#        - compared to another security
#        - compared to GDP growth / inflation
#        - real return
#        - momentum (time interval x)
# - Analysis
#        - Donchian Channels
#        - Bollinger Bands
#        - STARC Bands
#        - Keltner Channels

from etfs.io.helpers import read_yahoo_csv, retrieve_yahoo_quote


class security(object):

    def __init__(self, name, start='1900-01-01', end='2100-01-01'):
        self.ticker = name
        self.load(start=start, end=end)
        self.get_last_price()
        self.get_max_price()
        self.get_min_price()
        self.get_median_price()
        self.get_mean_price()
        self.get_std_price()

    def set_name(self, name):
        self.name = name

    def load(self, start='1900-01-01', end='2100-01-01'):
        '''
        Tries to load from csv first, then pulls from Yahoo!
        '''
        try:
            filepath = '../data/{0}.csv'.format(self.ticker)
            self.data = read_yahoo_csv(path=filepath, startdate=start, enddate=end)
        except:
            self.data = retrieve_yahoo_quote(ticker=self.ticker, startdate=start.replace('-', ''), enddate=end.replace('-', ''))
        else:
            pass

    def refresh(self, start='1900-01-01', end='2100-01-01'):
        '''
        Tries to load from csv first, then pulls from Yahoo!
        '''
        try:
            self.data = retrieve_yahoo_quote(ticker=self.ticker, startdate=start.replace('-', ''), enddate=end.replace('-', ''))
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
        self.max_price = self.data.Close.max()
        return self.max_price

    def get_min_price(self, column='Close'):
        self.min_price = self.data.Close.min()
        return self.min_price

    def get_median_price(self, column='Close'):
        self.median_price = self.data.Close.median()
        return self.median_price

    def get_mean_price(self, column='Close'):
        self.mean_price = self.data.Close.mean()
        return self.mean_price

    def get_std_price(self, column='Close'):
        self.std_price = self.data.Close.std()
        return self.std_price
