import numpy as np
import pandas as pd
import csv
from etfs.portfolio import portfolio


def parse_portfolio(df=None, p=None):

    # sort chronologically
    df = df.sort_values(by='Date')

    for index, row in df.iterrows():
        #print(row['Date'], row['Transaction'], row['Ticker'], row['Currency'], row['Price'], row['Quantity'])
        if row['Transaction'] == 'buy':
            p.buy_security(date=row['Date'], 
                           ticker=row['Ticker'], 
                           currency=row['Currency'], 
                           price=row['Price'], 
                           quantity=row['Quantity'])

        elif row['Transaction'] == 'sell':
            p.sell_security(date=row['Date'], 
                            ticker=row['Ticker'], 
                            currency=row['Currency'], 
                            price=row['Price'], 
                            quantity=row['Quantity'])    

        elif row['Transaction'] == 'deposit':
            p.deposit_cash(date=row['Date'], 
                           currency=row['Currency'], 
                           price=row['Price'], 
                           quantity=row['Quantity'])

        elif row['Transaction'] == 'withdraw':
            p.withdraw_cash(date=row['Date'], 
                            currency=row['Currency'], 
                            price=row['Price'], 
                            quantity=row['Quantity'])

        elif row['Transaction'] == 'dividend':
            p.dividend(date=row['Date'], 
                       ticker=row['Ticker'], 
                       currency=row['Currency'], 
                       price=row['Price'], 
                       quantity=row['Quantity'])
        else:
            pass
 
    return p


def parse_portfolio_vanguard(df=None, p=None):

    # sort chronologically
    df = df.sort_values(by='Date')

    for index, row in df.iterrows():
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

        elif row['Transaction'] == 'Contribution' or row['Transaction'] == 'Funds Received':
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
 

    return p


def import_portfolio(path="", name="RobinHood"):

    # read in transaction list
    df = pd.read_csv(path, parse_dates=[0])

    # create a new portfolio object
    p = portfolio.portfolio(name=name)

    # parse
    parse_portfolio(df, p)

    return p


def import_vanguard_portfolio(path="", name="Vanguard"):

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
    p = portfolio.portfolio(name=name)

    # parse
    p = parse_portfolio_vanguard(df, p)

    return p

