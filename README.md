# Portfolios


## Purpose

*portfolios* is a Python package for combining, managing, and analyzing portfolios. It greatly simplifies aggregating data on equities and bonds, computing statistics on individual securities or entire portfolios, and finding trends or opportunities. 


## Main Features


Input features:
  - Easily retrieve free historical data from Yahoo! Finance and the U.S. Department of the Treasury.
  - Link *portfolios* to Robinhood accounts and retrieve transaction data.
  - Load in Vanguard portfolios (from a CSV file downloaded from a Vanguard account).
  - Create custom portfolios from CSV files with lists of transactions.
  - Retrieves historical price and volume data from Yahoo! Finance.

Basic methods on historical price data:
  - run rates (e.g., 50-day / 200-day moving average)
  - exponentially weighted moving averages
  - resampling of data (e.g., day, week, month)
  - standard deviation / variance
  - `R^2`, beta, alpha
  - and many more

Output:
  - detailed portfolio description (positions, current value, returns, investments, devestments)
  - historical growth timeseries plots 
  - candlestick plots
  - Heikin-Ashi plots



## Install


To install *portfolios* clone or download the repository and execute

```sh
pip install .
```

in the repository directory, or execute


```sh
pip install -e .
```

for installing in development mode.



## License


[BSD 3](LICENSE)



## Documentation


See Jupyter notebooks for examples. More to follow.
