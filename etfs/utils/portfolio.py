import numpy as np
import pandas as pd
from etfs.utils import security


class portfolio(object):
    '''
       Class that holds several securities
    '''

    def __init__(self, name):
        self.name = name
        self.securities = {}
        self.tickers = []
        self.transactions = pd.DataFrame(columns=['Date', 'Ticker', 'Volume', 'Price', 'TradeValue'])
        self.index = 0
        self.cash = 0.0

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

    def remove_security(self, ticker):
        del self.securities[ticker]
        self.tickers.remove(ticker)

    def buy_security(self, date, ticker, volume=0, price=None):

        if ticker not in self.tickers:
            self.add_security(ticker)
            print('adding', ticker)

        if np.isnan(price):
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

        if self.transactions.groupby(by='Ticker')['Volume'].sum()[ticker] <= 0.0:
            self.remove_security(ticker)
            print('removing', ticker)

    def overview(self):

        # you have to have one security in the portfolio for meaningful output
        if len(self.securities) > 0:
            # sum up by ticker
            self.overview_df = self.transactions.groupby(by='Ticker')['Volume', 'TradeValue'].sum()
            self.overview_df = self.overview_df.loc[self.overview_df.Volume > 0]
            
            # check if sum over volume of a security is < 0
            for index, row in self.overview_df.iterrows():
                if row['Volume'] < 0.0:
                    print('Negative volume encountered: {0:5}\t{1}'.format(index, row['Volume']))

            #self.tickers = list(self.overview_df.index.values)

            for ticker in self.tickers:
                self.overview_df.loc[self.overview_df.index == ticker, 
                                     'LastPrice'] = self.securities[ticker].get_last_price()
        
            self.overview_df['CurrentValue'] = self.overview_df['LastPrice'] * self.overview_df['Volume']
            self.overview_df['AvgPrice'] = self.overview_df['TradeValue'] / (1.0*self.overview_df['Volume'])
            self.overview_df['Return'] = self.overview_df['CurrentValue'] - self.overview_df['TradeValue']

        # make dummy df when no (more) securities in portfolio
        else:
            d = {'AvgPrice': [0], 
                 'TradeValue': [0], 
                 'LastPrice': [0], 
                 'CurrentValue': [0], 
                 'Return': [0]
                 }
            self.overview_df = pd.DataFrame(data=d, index=[''])

        print(self.overview_df[['AvgPrice', 'TradeValue', 'LastPrice', 'CurrentValue', 'Return']])
        print()
        print(self.overview_df[['TradeValue', 'CurrentValue', 'Return']].sum())

