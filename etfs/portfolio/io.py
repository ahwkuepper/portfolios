# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import csv
from math import ceil
from etfs.portfolio.portfolio import Portfolio


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

      # sort chronologically
      df = df.sort_values(by='Date')

      for index, row in df.iterrows():
          if row.notnull()['Date']:
              # add to portfolio raw data frame
              new_row = pd.DataFrame(data={'Date': [row['Date']], 
                                           'Transaction': [row['Transaction']], 
                                           'Ticker': [row['Ticker']], 
                                           'Currency': [row['Currency']], 
                                           'Price': [row['Price']], 
                                           'Quantity': [row['Quantity']]})
              p.raw_data = p.raw_data.append(new_row)

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
                  _SECfee = max(ceil(0.0013*row['Quantity']*row['Price']), 1.0)/100.0
                  
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
 
    # clean up
    p.raw_data.sort_values(by='Date', inplace=True)
    p.raw_data.reset_index(inplace=True, drop=True)

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
      # sort chronologically
      df = df.sort_values(by='Date')

      for index, row in df.iterrows():
          if row.notnull()['Date']:
              #print(row['Date'], row['Transaction'], row['Ticker'], row['Currency'], row['Price'], row['Quantity'], row['Dollars'])
              
              if row['Transaction'] == 'Buy':
                  p.buy_security(date=row['Date'], 
                                 ticker=row['Ticker'], 
                                 currency=row['Currency'], 
                                 price=row['Price'], 
                                 quantity=row['Quantity'])

                  new_row = pd.DataFrame(data={'Date': [row['Date']], 
                                               'Transaction': ['buy'], 
                                               'Ticker': [row['Ticker']], 
                                               'Currency': [row['Currency']], 
                                               'Price': [row['Price']], 
                                               'Quantity': [row['Quantity']]})
                  p.raw_data = p.raw_data.append(new_row)
    
              elif row['Transaction'] == 'Sell':
                  p.sell_security(date=row['Date'], 
                                  ticker=row['Ticker'], 
                                  currency=row['Currency'], 
                                  price=row['Price'], 
                                  quantity=row['Quantity'])

                  new_row = pd.DataFrame(data={'Date': [row['Date']], 
                                               'Transaction': ['sell'], 
                                               'Ticker': [row['Ticker']], 
                                               'Currency': [row['Currency']], 
                                               'Price': [row['Price']], 
                                               'Quantity': [row['Quantity']]})
                  p.raw_data = p.raw_data.append(new_row)
    
              elif row['Transaction'] == 'Contribution' or row['Transaction'] == 'Funds Received':
                  p.deposit_cash(date=row['Date'], 
                                 currency=row['Currency'], 
                                 price=1.0, 
                                 quantity=row['Dollars'])

                  new_row = pd.DataFrame(data={'Date': [row['Date']], 
                                               'Transaction': ['deposit'], 
                                               'Ticker': [''], 
                                               'Currency': [row['Currency']], 
                                               'Price': [1.0], 
                                               'Quantity': [row['Dollars']]})
                  p.raw_data = p.raw_data.append(new_row)
    
              elif row['Transaction'] == 'Distribution':
                  p.withdraw_cash(date=row['Date'], 
                                  currency=row['Currency'], 
                                  price=1.0, 
                                  quantity=row['Dollars'])

                  new_row = pd.DataFrame(data={'Date': [row['Date']], 
                                               'Transaction': ['withdraw'], 
                                               'Ticker': [''], 
                                               'Currency': [row['Currency']], 
                                               'Price': [1.0], 
                                               'Quantity': [row['Dollars']]})
                  p.raw_data = p.raw_data.append(new_row)
    
              elif row['Transaction'] == 'Dividend':
                  p.dividend(date=row['Date'], 
                             ticker=row['Ticker'], 
                             currency=row['Currency'], 
                             price=1.0, 
                             quantity=row['Dollars'])

                  new_row = pd.DataFrame(data={'Date': [row['Date']], 
                                               'Transaction': ['dividend'], 
                                               'Ticker': [row['Ticker']], 
                                               'Currency': [row['Currency']], 
                                               'Price': [1.0], 
                                               'Quantity': [row['Dollars']]})
                  p.raw_data = p.raw_data.append(new_row)
    
              elif row['Transaction'] == 'Reinvestment' and row['Quantity'] != 0:
                  p.buy_security(date=row['Date'], 
                                 ticker=row['Ticker'], 
                                 currency=row['Currency'], 
                                 price=row['Price'], 
                                 quantity=row['Quantity'])

                  new_row = pd.DataFrame(data={'Date': [row['Date']], 
                                               'Transaction': ['buy'], 
                                               'Ticker': [row['Ticker']], 
                                               'Currency': [row['Currency']], 
                                               'Price': [row['Price']], 
                                               'Quantity': [row['Quantity']]})
                  p.raw_data = p.raw_data.append(new_row)
    
              else:
                  pass

          else:
              pass      

    # clean up
    p.raw_data.sort_values(by='Date', inplace=True)
    p.raw_data.reset_index(inplace=True, drop=True)

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

    # read in transaction list
    df = pd.read_csv(path, parse_dates=[0])

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

    # read in csv to find beginning of transaction list
    input_file = csv.reader(open(path, "r"), delimiter=",")

    for i,row in enumerate(input_file):
        if len(row) > 0 and 'Trade' in row[1]:
            break

    # read in transaction list
    df = pd.read_csv(path,
                     skiprows=i,
                     usecols=['Trade Date', 'Transaction Type', 'Symbol', 'Share Price', 'Shares', 'Principal Amount'],
                     parse_dates=['Trade Date'],
                     skip_blank_lines=False
                     )

    # rename columns to match standard format
    df.columns = ['Date', 'Transaction', 'Ticker', 'Quantity', 'Price', 'Dollars']

    # add a currency column to match standard format
    df["Currency"] = 'USD'

    # create a new portfolio object
    p = Portfolio(name=name)

    # parse
    p = parse_portfolio_vanguard(df, p)

    return p

