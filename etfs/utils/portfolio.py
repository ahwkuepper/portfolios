# Write a class that holds a several securities
# Content:
# - ...
# Create a benchmark portfolio, e.g., from Investopedia:
#     - 55% of the Russell 3000, which is a market capitalization-weighted index that includes large, mid and small-cap U.S. stocks.
#     - 40% of the Barclays Aggregate Bond Index which includes U.S. investment-grade government and corporate bonds.
#     - 15% of MSCI EAFE, which is an index that tracks the performance of 21 international equity markets including Europe, Australia and Southeast Asia.      
# 

import numpy as np
import pandas as pd
from etfs.utils import security


class portfolio(object):

    def __init__(self, name):
        self.name = name
        self.securities = {}
        self.tickers = []
        self.transactions = pd.DataFrame(columns=['Date', 'Ticker', 'Volume', 'Price', 'TradeValue'])
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if len(self.tickers) == 0:
            self.index = 0
            raise StopIteration
        elif self.index >= len(self.tickers):
            self.index = 0
            raise StopIteration
        else:
            self.index = self.index + 1
            return self.tickers[self.index-1]

    def set_name(self, name):
        self.name = name

    def add_security(self, ticker):
        _security = security.security(ticker)
        self.securities[_security.ticker] = _security
        self.tickers.append(ticker)

    def buy_security(self, date, ticker, volume=0, price=None):

        if ticker not in self.tickers:
            self.add_security(ticker)
            print('adding', ticker)

        if not price:
        	price = self.securities[ticker].get_price_at(date)


        self.transactions = self.transactions.append({'Date': date,
                                                      'Ticker': ticker,
                                                      'Volume': 1.0*volume,
                                                      'Price': 1.0*price,
                                                      'TradeValue': 1.0*price*volume
                                                      }, ignore_index=True)

    def sell_security(self, date, ticker, volume, price):

        self.transactions = self.transactions.append({'Date': date,
                                                      'Ticker': ticker,
                                                      'Volume': -1.0*volume,
                                                      'Price': 1.0*price,
                                                      'TradeValue': -1.0*price*volume
                                                      }, ignore_index=True)

    def overview(self):

        self.overview_df = self.transactions.groupby(by='Ticker')['Volume', 'TradeValue'].sum()

        self.tickers = list(self.overview_df.index.values)

        for ticker in self.tickers:
            self.overview_df.loc[self.overview_df.index == ticker, 
                                 'LastPrice'] = self.securities[ticker].get_last_price()
        
        self.overview_df['CurrentValue'] = self.overview_df['LastPrice'] * self.overview_df['Volume']
        self.overview_df['AvgPrice'] = self.overview_df['TradeValue'] / (1.0*self.overview_df['Volume'])
        self.overview_df['Return'] = self.overview_df['CurrentValue'] - self.overview_df['TradeValue']

        print(self.overview_df[['AvgPrice', 'TradeValue', 'LastPrice', 'CurrentValue', 'Return']])

        print(self.overview_df[['TradeValue', 'CurrentValue', 'Return']].sum())

