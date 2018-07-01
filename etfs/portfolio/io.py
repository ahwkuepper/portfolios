import numpy as np
import pandas as pd
from etfs.portfolio import portfolio


def import_portfolio(path="", name="RobinHood"):

   df = pd.read_csv(path, parse_dates=[0])

   p = portfolio.portfolio(name=name)

   for index, row in df.iterrows():
       print(row['Date'], row['Transaction'], row['Ticker'], row['Currency'], row['Price'], row['Quantity'])
       if row['Transaction'] == 'buy':
           p.buy_security(row['Date'], row['Ticker'], row['Currency'], row['Price'], row['Quantity'])
       elif row['Transaction'] == 'sell':
           p.sell_security(row['Date'], row['Ticker'], row['Currency'], row['Price'], row['Quantity'])    
       elif row['Transaction'] == 'deposit':
           p.deposit_cash(row['Date'], row['Currency'], row['Price'], row['Quantity'])
       elif row['Transaction'] == 'withdraw':
           p.withdraw_cash(row['Date'], row['Currency'], row['Price'], row['Quantity'])
       elif row['Transaction'] == 'dividend':
           p.dividend(row['Date'], row['Ticker'], row['Currency'], row['Price'], row['Quantity'])

   return p

