# etfs: security analysis toolkit



## Purpose

*etfs* is a Python package that makes it easy to gather data on securities, compute statistics, and find trends. It offers a wide range of tools to analyze securities, such as stocks and bonds, or compositions of securities, such as portfolios or ETFs.



## Main Features


Input features:
  - Load in Vanguard portfolios (from a CSV file downloaded from a Vanguard account) or other custom portfolios from a CSV file with a list of transactions (e.g. from RobinHood).
  - Retrieves historical price and volume data from Yahoo! Finance.

Basic methods on historical price data:
  - run rate (e.g., 50-day / 200-day moving average)
  - exponentially weighted moving average
  - resampling (e.g., day, week, month)
  - variance
  - :math:`R^2`
  - beta
  - alpha

Output:
  - detailed portfolio description (positions, current value, returns, investments, devestments)
  - growth timeseries plots 
  - candlestick plots
  - Heikin-Ashi plots



## Install


To install *etfs* clone or download the repository and execute

```sh
pip install .
```

in the `etfs` directory, or execute


```sh
pip install -e .
```

for installing in development mode.



## License


[BSD 3](LICENSE)



## Documentation


See Jupyter notebooks for examples. More to follow.
