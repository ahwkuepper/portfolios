# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import csv
from math import ceil
from etfs.portfolio.portfolio import Portfolio
import os
import glob


def parse_portfolio(df=None, p=None):
    """
    Takes a dataframe with transactions and performs those
    on a given portfolio

    Parameters
    ==========
    df : input dataframe
    p : portfolio (Portfolio class object) 

    Returns
    =======
    p : modified portfolio (Portfolio class object)

    """

    # put input dataframe(s) in list
    dfs = []
    if type(df) == pd.core.frame.DataFrame:
        dfs.append(df)
    else:
        dfs.extend(df)

    # loop through list of dataframes
    for df in dfs:

      # define a priority for transaction types so ordering makes sense
      df.loc[df.Transaction == 'deposit', 'Priority'] = 1
      df.loc[df.Transaction == 'Contribution', 'Priority'] = 1
      df.loc[df.Transaction == 'Funds Received', 'Priority'] = 1
      df.loc[df.Transaction == 'Conversion (incoming)', 'Priority'] = 1
      df.loc[df.Transaction == 'buy', 'Priority'] = 2
      df.loc[df.Transaction == 'Buy', 'Priority'] = 2
      df.loc[df.Transaction == 'Reinvestment', 'Priority'] = 2
      df.loc[df.Transaction == 'dividend', 'Priority'] = 3
      df.loc[df.Transaction == 'Dividend', 'Priority'] = 3
      df.loc[df.Transaction == 'sell', 'Priority'] = 4
      df.loc[df.Transaction == 'Sell', 'Priority'] = 4
      df.loc[df.Transaction == 'withdraw', 'Priority'] = 5
      df.loc[df.Transaction == 'Distribution', 'Priority'] = 5

      df.sort_values(by=['Date', 'Priority'], inplace=True)

      for index, row in df.iterrows():
          if row.notnull()['Date']:
              #print(row['Date'], row['Transaction'], row['Ticker'], row['Currency'], row['Price'], row['Quantity'])
              if str.lower(row['Transaction']) == 'buy':
                  p.buy_security(date=row['Date'], 
                                 ticker=row['Ticker'], 
                                 currency=row['Currency'],
                                 price=row['Price'], 
                                 quantity=row['Quantity'])
    
    
              elif str.lower(row['Transaction']) == 'sell':
                  p.sell_security(date=row['Date'], 
                                  ticker=row['Ticker'], 
                                  currency=row['Currency'], 
                                  price=row['Price'],  
                                  quantity=row['Quantity']) 
    
                  # FINRA fee of $.000119 per share up to $5.95
                  _FINRAfee = min(max(ceil(0.0119*row['Quantity']), 1.0)/100.0, 5.95)
                  # SEC fee of $.000013 per trade of up to $1M
                  _SECfee = max(ceil(row['Quantity']*row['Price']/800.0), 1.0)/100.0
                  
                  p.wallet = p.wallet.append({'Date': row['Date'],
                                              'Change': -_FINRAfee -_SECfee
                                             }, ignore_index=True)
    
              elif str.lower(row['Transaction']) == 'deposit':
                  p.deposit_cash(date=row['Date'], 
                                 currency=row['Currency'], 
                                 price=row['Price'], 
                                 quantity=row['Quantity'])
    
              elif str.lower(row['Transaction']) == 'withdraw':
                  p.withdraw_cash(date=row['Date'], 
                                  currency=row['Currency'], 
                                  price=row['Price'], 
                                  quantity=row['Quantity'])

              elif row['Transaction'] == 'Dividend':
                  p.dividend(date=row['Date'], 
                             ticker=row['Ticker'], 
                             currency=row['Currency'], 
                             price=1.0, 
                             quantity=row['Dollars'])
    
              elif row['Transaction'] == 'dividend':
                  p.dividend(date=row['Date'], 
                             ticker=row['Ticker'], 
                             currency=row['Currency'], 
                             price=row['Price'], 
                             quantity=row['Quantity'])

              else:
                  pass
          else:
              pass
 
    return p


def parse_portfolio_vanguard(df=None, p=None):
    """
    Takes a dataframe with transactions in Vanguard format
    and performs those on a given portfolio

    Parameters
    ==========
    df : input dataframe
    p : portfolio (Portfolio class object) 

    Returns
    =======
    p : modified portfolio (Portfolio class object)

    """

    # put input dataframe(s) in list
    dfs = []
    if type(df) == pd.core.frame.DataFrame:
        dfs.append(df)
    else:
        dfs.extend(df)

    # loop through list of dataframes
    for df in dfs:
      # define a priority for transaction types so ordering makes sense
      df.loc[df.Transaction == 'deposit', 'Priority'] = 1
      df.loc[df.Transaction == 'Contribution', 'Priority'] = 1
      df.loc[df.Transaction == 'Funds Received', 'Priority'] = 1
      df.loc[df.Transaction == 'Conversion (incoming)', 'Priority'] = 1
      df.loc[df.Transaction == 'buy', 'Priority'] = 2
      df.loc[df.Transaction == 'Buy', 'Priority'] = 2
      df.loc[df.Transaction == 'Reinvestment', 'Priority'] = 2
      df.loc[df.Transaction == 'dividend', 'Priority'] = 3
      df.loc[df.Transaction == 'Dividend', 'Priority'] = 3
      df.loc[df.Transaction == 'sell', 'Priority'] = 4
      df.loc[df.Transaction == 'Sell', 'Priority'] = 4
      df.loc[df.Transaction == 'withdraw', 'Priority'] = 5
      df.loc[df.Transaction == 'Distribution', 'Priority'] = 5

      df.sort_values(by=['Date', 'Priority'], inplace=True)

      for index, row in df.iterrows():
          if row.notnull()['Date']:
              #print(row['Date'], row['Transaction'], row['Ticker'], row['Currency'], row['Price'], row['Quantity'], row['Dollars'])
              
              if row['Transaction'] == 'Buy':
                  p.buy_security(date=row['Date'], 
                                 ticker=row['Ticker'], 
                                 currency=row['Currency'], 
                                 price=row['Price'], 
                                 quantity=row['Quantity'])
    
              elif row['Transaction'] == 'Sell':
                  p.sell_security(date=row['Date'], 
                                  ticker=row['Ticker'], 
                                  currency=row['Currency'], 
                                  price=row['Price'], 
                                  quantity=row['Quantity'])
    
              elif row['Transaction'] == 'Contribution' or row['Transaction'] == 'Funds Received' \
                or row['Transaction'] == 'Conversion (incoming)':
                  p.deposit_cash(date=row['Date'], 
                                 currency=row['Currency'], 
                                 price=1.0, 
                                 quantity=row['Dollars'])
    
              elif row['Transaction'] == 'Distribution':
                  p.withdraw_cash(date=row['Date'], 
                                  currency=row['Currency'], 
                                  price=1.0, 
                                  quantity=row['Dollars'])

              elif row['Transaction'] == 'Dividend':
                  p.dividend(date=row['Date'], 
                             ticker=row['Ticker'], 
                             currency=row['Currency'], 
                             price=1.0, 
                             quantity=row['Dollars'])
    
              elif row['Transaction'] == 'Reinvestment' and row['Quantity'] != 0:
                  p.buy_security(date=row['Date'], 
                                 ticker=row['Ticker'], 
                                 currency=row['Currency'], 
                                 price=row['Price'], 
                                 quantity=row['Quantity'])
    
              else:
                  pass

          else:
              pass      

    return p


def import_portfolio(path="", name="RobinHood"):
    """
    Reads in CSV file with portfolio transactions

    Parameters
    ==========
    path : path and name of CSV file
    name : desired portfolio name 

    Returns
    =======
    df : dataframe with transactions from CSV file
    p : portfolio (Portfolio class object)

    """

    # get all files that match path
    all_files = glob.glob(path)
    all_dfs = []

    for file in all_files:

        print("Reading in {}".format(file))

        # read in transaction list
        df = pd.read_csv(file, parse_dates=[0])

        # collect all dfs before concatenating them
        all_dfs.append(df)

    # final portfolio df to parse
    df = pd.concat(all_dfs, axis=0, ignore_index=True)

    # create a new portfolio object
    p = Portfolio(name=name)

    # parse
    parse_portfolio(df, p)

    return p


def import_portfolio_vanguard(path="", name="Vanguard"):
    """
    Reads in CSV file with portfolio transactions in Vanguard format

    Parameters
    ==========
    path : path and name of CSV file
    name : desired portfolio name 

    Returns
    =======
    df : dataframe with transactions from CSV file
    p : portfolio (Portfolio class object)

    """

    # get all files that match path
    all_files = glob.glob(path)
    all_dfs = []

    for file in all_files:

        print("Reading in {}".format(file))

        # read in csv to find beginning of transaction list
        input_file = csv.reader(open(file, "r"), delimiter=",")

        for i,row in enumerate(input_file):
            if len(row) > 0 and 'Trade' in row[1]:
                break

        # read in transaction list
        df = pd.read_csv(file,
                         skiprows=i,
                         usecols=['Trade Date', 'Transaction Type', 'Symbol', 'Share Price', 'Shares', 'Principal Amount'],
                         parse_dates=['Trade Date'],
                         skip_blank_lines=False
                         )

        # rename columns to match standard format
        df.columns = ['Date', 'Transaction', 'Ticker', 'Quantity', 'Price', 'Dollars']

        # add a currency column to match standard format
        df["Currency"] = 'USD'
        
        # collect all dfs before concatenating them
        all_dfs.append(df)

    # final portfolio df to parse
    df = pd.concat(all_dfs, axis=0, ignore_index=True)

    # create a new portfolio object
    p = Portfolio(name=name)

    # parse
    p = parse_portfolio_vanguard(df, p)

    return p





def import_portfolio_robinhood(username=None, password=None, name="Robinhood", free_stock=False):
    """
    Accesses Robinhood account and downloads transactions 

    Parameters
    ==========
    username : Robinhood username
    password : Robinhood account password
    name : desired portfolio name 
    free_stock : include a free stock not captured by transaction history (see below)

    Returns
    =======
    df : dataframe with transactions
    p : portfolio (Portfolio class object)

    """
    import robin_stocks as r
    from getpass import getpass

    if username is None: username = getpass("Username: ")
    if password is None: password = getpass("Password: ")

    # use Robinhood api to download transaction history
    r.login(username, password)
    
    # build dataframe
    Date = []
    Transaction = []
    Ticker = []
    Currency = []
    Price = []
    Quantity = []

    # parse order history
    orders = r.get_all_orders()
    print("Parsing orders ...")
    for order in orders:
        if len(order['executions']):
            Date.append(pd.to_datetime(order['last_transaction_at']))
            Transaction.append(order['side'])
            Ticker.append(r.get_instrument_by_url(order['instrument'])['symbol'])
            Currency.append('USD')
            Price.append(order['average_price'])
            Quantity.append(order['quantity'])

    # add deposits
    transfers = r.get_bank_transfers()
    print("Parsing bank transfers ...")
    for transfer in transfers:
        if transfer['cancel'] is None:
            Date.append(pd.to_datetime(transfer['created_at']))
            Transaction.append('deposit')
            Ticker.append(None)
            Currency.append('USD')
            Price.append(1.0)
            Quantity.append(transfer['amount'])

    # add dividends
    dividends = r.get_dividends()
    print("Parsing dividends ...")
    for dividend in dividends:
        if dividend['state'] == 'paid':
            Date.append(pd.to_datetime(dividend['paid_at']))
            Transaction.append('dividend')
            Ticker.append(r.get_instrument_by_url(dividend['instrument'])['symbol'])
            Currency.append('USD')
            Price.append(float(dividend['amount'])/float(dividend['position']))
            Quantity.append(dividend['position'])

    if free_stock == True:
        # include free stock (Robinhood promotion, not included in transaction history)
        print("Adding promotional stock ...")
        Date.append(pd.to_datetime('2/1/18'))
        Transaction.append('buy')
        Ticker.append('CHK')
        Currency.append('USD')
        Price.append(0.0)
        Quantity.append(1.0)

    # build dataframe
    d = {'Date': Date, 
     'Transaction': Transaction,
     'Ticker': Ticker,
     'Currency': Currency,
     'Price': pd.to_numeric(Price),
     'Quantity': pd.to_numeric(Quantity)
    }
    df = pd.DataFrame(data=d)

    # strip time of day information
    df.Date = df.Date.map(lambda x: x.strftime('%m-%d-%Y'))
    df.Date = pd.to_datetime(df.Date)

    # create a new portfolio object
    p = Portfolio(name=name)

    # parse
    p = parse_portfolio(df, p)

    return p


