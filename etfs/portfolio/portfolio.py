import numpy as np
import pandas as pd
from etfs.security import security
from etfs.utils.helpers import todays_date


class portfolio(object):
    '''
       Class that holds several securities
    '''

    def __init__(self, name):
        self.name = name
        self.securities = {}
        self.tickers = []
        self.transactions = pd.DataFrame(columns=['Date', 'Ticker', 'Quantity', 'Price', 'TradeValue'], dty)
        self.dividends = pd.DataFrame(columns=['Date', 'Ticker', 'Amount'])
        self.payments = pd.DataFrame(columns=['Date', 'In', 'Out'])
        self.wallet = pd.DataFrame(columns=['Date', 'Cash'])
        self.total_portfolio_value = 0.0
        self.total_security_value = 0.0
        self.cash = 0.0
        self.return_value = 0.0
        self.return_rate = 0.0
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

    def deposit_cash(self, date, currency='USD', price=1.0, quantity=0):
        self.cash = self.cash + quantity*price
        if date in self.wallet.Date:
            self.wallet.at[self.wallet.Date == date, 'Cash'] = self.cash
        else:
            self.wallet = self.wallet.append({'Date': date,
                                              'Cash': self.cash
                                              }, ignore_index=True)

        self.payments = self.payments.append({'Date': date,
                                              'In': 1.0*price*quantity,
                                              'Out': 0.0
                                              }, ignore_index=True)
        print("Cash balance: {0:.2f} {1}".format(self.cash, currency))

    def withdraw_cash(self, date, currency='USD', price=1.0, quantity=0):
        self.cash = self.cash - quantity*price
        if date in self.wallet.Date:
            self.wallet.at[self.wallet.Date == date, 'Cash'] = self.cash
        else:
            self.wallet = self.wallet.append({'Date': date,
                                          'Cash': self.cash
                                          }, ignore_index=True)
    
        self.payments = self.payments.append({'Date': date,
                                              'In': 0.0,
                                              'Out': 1.0*price*quantity
                                              }, ignore_index=True)
        if self.cash < 0.0:
            print("Warning, cash balance negative: {0:.2f} {1}".format(self.cash, currency))
        else:
            print("Cash balance: {0:.2f} {1}".format(self.cash, currency))

    def dividend(self, date, ticker='', currency='USD', price=1.0, quantity=0):
        self.cash = self.cash + quantity*price
        if date in self.wallet.Date:
            self.wallet.at[self.wallet.Date == date, 'Cash'] = self.cash
        else:
            self.wallet = self.wallet.append({'Date': date,
                                              'Cash': self.cash
                                              }, ignore_index=True)

        print("Cash balance: {0:.2f} {1}".format(self.cash,currency))

        # store transaction in df
        self.dividends = self.dividends.append({'Date': date,
                                                'Ticker': ticker,
                                                'Amount': 1.0*price*quantity
                                                }, ignore_index=True)

    def add_security(self, ticker):
        _security = security.security(ticker)
        self.securities[_security.ticker] = _security
        self.tickers.append(ticker)

    def remove_security(self, ticker):
        del self.securities[ticker]
        self.tickers.remove(ticker)

    def buy_security(self, date, ticker, currency='USD', price=None, quantity=0):

        # potentially add ticker to list
        if ticker not in self.tickers:
            self.add_security(ticker)
            print('adding', ticker)

        # get closing price of security for transaction date if price not provided
        if np.isnan(price):
            price = self.securities[ticker].get_price_at(date)

        # subtract price of security from wallet
        self.cash = self.cash - quantity*price

        # store point in time value in wallet
        if date in self.wallet.Date:
            self.wallet.at[self.wallet.Date == date, 'Cash'] = self.cash
        else:
            self.wallet = self.wallet.append({'Date': date,
                                              'Cash': self.cash
                                              }, ignore_index=True)

        # store transaction in df
        self.transactions = self.transactions.append({'Date': date,
                                                      'Ticker': ticker,
                                                      'Quantity': 1.0*quantity,
                                                      'Price': 1.0*price,
                                                      'TradeValue': 1.0*price*quantity
                                                      }, ignore_index=True)

    def sell_security(self, date, ticker, currency='USD', price=None, quantity=0):

        # subtract price of security from wallet
        self.cash = self.cash + quantity*price

        # store point in time value in wallet
        if date in self.wallet.Date:
            self.wallet.at[self.wallet.Date == date, 'Cash'] = self.cash
        else:
            self.wallet = self.wallet.append({'Date': date,
                                              'Cash': self.cash
                                              }, ignore_index=True)

        # get closing price of security for transaction date if price not provided
        if np.isnan(price):
            price = self.securities[ticker].get_price_at(date)

        # store transaction in df
        self.transactions = self.transactions.append({'Date': date,
                                                      'Ticker': ticker,
                                                      'Quantity': -1.0*quantity,
                                                      'Price': 1.0*price,
                                                      'TradeValue': -1.0*price*quantity
                                                      }, ignore_index=True)

        # potentially remove ticker from list
        if self.transactions.groupby(by='Ticker')['Quantity'].sum()[ticker] <= 0.0:
            self.remove_security(ticker)
            print('removing', ticker)

    def overview(self):

        # you have to have one security in the portfolio for meaningful output
        if len(self.securities) > 0:
            # sum up by ticker
            self.overview_df = self.transactions.groupby(by='Ticker')['Quantity', 'TradeValue'].sum()
            self.overview_df = self.overview_df.loc[self.overview_df.Quantity > 0]
            
            # check if sum over volume of a security is < 0
            for index, row in self.overview_df.iterrows():
                if row['Quantity'] < 0.0:
                    print('Negative volume encountered: {0:5}\t{1}'.format(index, row['Quantity']))

            for ticker in self.tickers:
                self.overview_df.loc[self.overview_df.index == ticker, 
                                     'LastPrice'] = self.securities[ticker].get_last_price()
        
            self.overview_df['CurrentValue'] = self.overview_df['LastPrice'] * self.overview_df['Quantity']

            # sum up dividends by ticker
            self.overview_df['Dividends'] = self.dividends.groupby(by='Ticker')['Amount'].sum()

            self.overview_df['AvgPrice'] = self.overview_df['TradeValue'] / (1.0*self.overview_df['Quantity'])
            self.overview_df.fillna(0.0, inplace=True)
            self.overview_df['Return'] = self.overview_df['CurrentValue'] - self.overview_df['TradeValue'] + self.overview_df['Dividends']

            #self.overview_dividende_df = self.overview_dividende_df.loc[self.overview_dividende_df.Quantity > 0]
            
        # make dummy df when no (more) securities in portfolio
        else:
            _d = {'Quantity': [0],
                 'AvgPrice': [0], 
                 'TradeValue': [0], 
                 'LastPrice': [0], 
                 'CurrentValue': [0],
                 'Dividends': [0], 
                 'Return': [0]
                 }
            self.overview_df = pd.DataFrame(data=_d, index=[''])


        # update portfolio stats
        self.total_portfolio_value = self.overview_df[['CurrentValue']].sum().values[0] + self.cash
        self.total_security_value = self.overview_df[['CurrentValue']].sum().values[0]
        self.return_value = self.overview_df[['CurrentValue']].sum().values[0] + self.cash - self.payments['In'].sum()
        if self.total_portfolio_value:
            self.return_rate = self.return_value/self.total_portfolio_value
        else:
            self.return_rate = 0.0


        print(self.overview_df[['Quantity', 'AvgPrice', 'LastPrice', 'TradeValue', 'CurrentValue', 'Dividends', 'Return']])
        print()
        print("Total portfolio value:\t{0:8.2f} USD\nTotal security value:\t{1:8.2f} USD\nCash in wallet:\t\t{2:8.2f} USD\nTotal return:\t\t{3:8.2f} USD\t({4:.2f}%)".format(
            self.total_portfolio_value,
            self.total_security_value, 
            self.cash,
            self.return_value,
            self.return_rate*100.0
            )
        )


    def positions(self):
        # you have to have one security in the portfolio for meaningful output
        if len(self.securities) > 0:
            # sum up by ticker
            self.positions_df = self.transactions.groupby(by=['Ticker'])['Quantity', 'TradeValue'].sum()
            buy = [Quantity > 0 for Quantity in self.transactions.Quantity]
            self.positions_df["Bought"] = self.transactions[buy].groupby(by=['Ticker'])['Quantity'].sum()
            self.positions_df["Invested"] = self.transactions[buy].groupby(by=['Ticker'])['TradeValue'].sum()

            sell = [Quantity < 0 for Quantity in self.transactions.Quantity]
            self.positions_df["Sold"] = -1.0*self.transactions[sell].groupby(by=['Ticker'])['Quantity'].sum()
            self.positions_df["Devested"] = -1.0*self.transactions[sell].groupby(by=['Ticker'])['TradeValue'].sum()

            # check if sum over volume of a security is < 0
            for index, row in self.positions_df.iterrows():
                if row['Quantity'] < 0.0:
                    print('Negative volume encountered: {0:5}\t{1}'.format(index, row['Quantity']))

            for ticker in set(self.positions_df.index):
                if ticker in self.tickers:
                    self.positions_df.loc[self.positions_df.index == ticker, 
                                          'LastPrice'] = self.securities[ticker].get_last_price()
                else:
                    _security = security.security(ticker) 
                    self.positions_df.loc[self.positions_df.index == ticker, 
                                          'LastPrice'] = _security.get_last_price()
        
            self.positions_df['CurrentValue'] = self.positions_df['LastPrice'] * self.positions_df['Quantity']

            # sum up dividends by ticker
            self.positions_df['Dividends'] = self.dividends.groupby(by='Ticker')['Amount'].sum()

            #self.positions_df['AvgPrice'] = self.positions_df['TradeValue'] / (1.0*self.positions_df['Quantity'])
            self.positions_df.fillna(0.0, inplace=True)
            self.positions_df['Return'] = self.positions_df['CurrentValue'] - self.positions_df['TradeValue'] + self.positions_df['Dividends']
            self.positions_df['PercentGrowth'] = 100.0*self.positions_df['Return']/self.positions_df['Invested']
            self.positions_df.PercentGrowth.replace([np.inf,-np.inf], np.nan, inplace=True)

            print(self.positions_df[['Quantity', 'Bought', 'Sold', 'CurrentValue', 'Invested', 'Devested', 'Dividends', 'Return', 'PercentGrowth']].sort_values(by=['CurrentValue', 'Invested'], ascending=False))

        else:
             print("No positions in portfolio.")

    def get_timeseries(self):

        self.min_date = self.transactions.Date.min()
        self.max_date = todays_date()

        print(self.min_date, self.max_date)

        return 
