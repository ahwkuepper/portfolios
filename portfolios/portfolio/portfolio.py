# -*- coding: utf-8 -*-

import datetime
from collections import deque

import numpy as np
import pandas as pd

from portfolios import Asset
from portfolios.security.security import Security
from portfolios.stats.basics import returns_column
from portfolios.utils.helpers import standard_date_format, todays_date


class Portfolio(Asset):
    """
       Class that holds several securities
    """

    def __init__(self, name):
        super().__init__(name)
        self.securities = {}
        self.securities_archive = {}
        self.tickers = []
        self.tickers_archive = []
        self.dividends = pd.DataFrame(columns=["Date", "Ticker", "Amount"])
        self.payments = pd.DataFrame(columns=["Date", "In", "Out"])
        self.wallet = pd.DataFrame(columns=["Date", "Change"])
        self.total_portfolio_value = 0.0
        self.total_security_value = 0.0
        self.cash = 0.0
        self.return_value = 0.0
        self.return_rate = 0.0
        self.prices = {}
        self.prices_fifo = {}
        self.prices_lifo = {}
        self.index = 0
        self.benchmark_ticker = "sp500"
        self.benchmark = None
        self.transactions = pd.DataFrame(
            columns=["Date", "Transaction", "Ticker", "Currency", "Price", "Quantity"]
        )
        self.date = standard_date_format(todays_date())

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
            return self.tickers[self.index - 1]

    def get_cash(self, date="2100-01-01"):
        date = standard_date_format(date)

        return self.wallet.loc[(self.wallet.Date <= date), "Change"].sum()

    def deposit_cash(self, date, currency="USD", price=1.0, quantity=0):
        """
           Adds an amount of quantity*price to the wallet
           Price acts as exchange rate if currency is not USD
        """
        self.wallet = self.wallet.append(
            {"Date": date, "Change": 1.0 * price * quantity}, ignore_index=True
        ).sort_values("Date")

        # store transaction in df
        self.transactions = self.transactions.append(
            {
                "Date": date,
                "Transaction": "deposit",
                "Ticker": np.nan,
                "Currency": currency,
                "Price": 1.0 * price,
                "Quantity": 1.0 * quantity,
                "TradeValue": 1.0 * price * quantity,
            },
            ignore_index=True,
            sort=False,
        ).sort_values("Date")

        # store payment in df
        self.payments = self.payments.append(
            {"Date": date, "In": 1.0 * price * quantity, "Out": 0.0}, ignore_index=True
        ).sort_values("Date")

        self.cash = self.get_cash(date=todays_date())

        print(
            "depositing {0:.2f} {2} (new balance: {1:.2f} {2})".format(
                quantity * price, self.cash, currency
            )
        )

    def withdraw_cash(self, date, currency="USD", price=1.0, quantity=0):
        """
           Takes amount of quantity*price out of wallet
        """
        self.wallet = self.wallet.append(
            {"Date": date, "Change": -1.0 * price * quantity}, ignore_index=True
        ).sort_values("Date")

        # store transaction in df
        self.transactions = self.transactions.append(
            {
                "Date": date,
                "Transaction": "withdraw",
                "Ticker": np.nan,
                "Currency": currency,
                "Price": 1.0 * price,
                "Quantity": 1.0 * quantity,
                "TradeValue": 1.0 * price * quantity,
            },
            ignore_index=True,
            sort=False,
        ).sort_values("Date")

        # store payments in df
        self.payments = self.payments.append(
            {"Date": date, "In": 0.0, "Out": 1.0 * price * quantity}, ignore_index=True
        ).sort_values("Date")

        self.cash = self.get_cash(date=todays_date())

        if self.cash < 0.0:
            print(
                "Warning, cash balance negative: {0:.2f} {1}".format(
                    self.cash, currency
                )
            )
        else:
            print(
                "withdrawing {0:.2f} {2} (new balance: {1:.2f} {2})".format(
                    quantity * price, self.cash, currency
                )
            )  #

    def dividend(self, date, ticker="", currency="USD", price=1.0, quantity=0):
        """

        """
        self.wallet = self.wallet.append(
            {"Date": date, "Change": 1.0 * price * quantity}, ignore_index=True
        ).sort_values("Date")

        # store transaction in df
        self.transactions = self.transactions.append(
            {
                "Date": date,
                "Transaction": "dividend",
                "Ticker": ticker,
                "Currency": currency,
                "Price": 1.0 * price,
                "Quantity": 1.0 * quantity,
                "TradeValue": 1.0 * price * quantity,
            },
            ignore_index=True,
            sort=False,
        ).sort_values("Date")

        # store dividends in df
        self.dividends = self.dividends.append(
            {"Date": date, "Ticker": ticker, "Amount": 1.0 * price * quantity},
            ignore_index=True,
        ).sort_values("Date")

        self.cash = self.get_cash(date=todays_date())

        if ticker == "" or ticker != ticker:
            print(
                "interest {0:.2f} {2} (new balance: {1:.2f} {2})".format(
                    quantity * price, self.cash, currency
                )
            )
        else:
            print(
                "dividend {0} {1:.2f} {3} (new balance: {2:.2f} {3})".format(
                    ticker, quantity * price, self.cash, currency
                )
            )

    def add_security(self, ticker, min_date="2000-01-01"):
        if ticker in self.securities_archive:
            self.securities[ticker] = self.securities_archive[ticker]
            self.tickers.append(ticker)
        else:
            _security = Security(ticker, start=min_date, end=self.date)
            self.securities[_security.ticker] = _security
            self.tickers.append(ticker)
            self.prices[ticker] = deque()
            self.prices_lifo[ticker] = deque()
            self.prices_fifo[ticker] = deque()

    def add_security_archive(self, ticker, min_date="2000-01-01"):
        if ticker in self.securities:
            self.securities_archive[ticker] = self.securities[ticker]
            self.tickers_archive.append(ticker)
        else:
            _security = Security(ticker, start=min_date, end=self.date)
            self.securities_archive[_security.ticker] = _security
            self.tickers_archive.append(ticker)
            self.prices[ticker] = deque()
            self.prices_lifo[ticker] = deque()
            self.prices_fifo[ticker] = deque()

    def remove_security(self, ticker):
        # copy state of security to archive
        self.securities_archive[ticker] = self.securities[ticker]
        # delete from current list of securities
        del self.securities[ticker]
        self.tickers.remove(ticker)

    def buy_security(self, date, ticker, currency="USD", price=None, quantity=0):

        # potentially add ticker to list
        if ticker not in self.tickers:
            self.add_security(ticker)
            # print('adding', ticker)

        # and to archive
        if ticker not in self.tickers_archive:
            self.add_security_archive(ticker)

        # modify quantity for subsequent stock splits
        quantity, modifier = self.securities[ticker].modify_quantity(date, quantity)

        # get closing price of security for transaction date if price not provided
        # modify price according to stock splits
        try:
            if np.isnan(price):
                price = self.securities[ticker].get_price_at(date)
            else:
                price = price / modifier
        except:
            if price is None:
                price = self.securities[ticker].get_price_at(date)
            else:
                price = price / modifier

        for i in range(np.int(quantity)):
            self.prices[ticker].append(price)
            self.prices_lifo[ticker].append(price)
            self.prices_fifo[ticker].append(price)

        # store point in time value in wallet
        self.wallet = self.wallet.append(
            {"Date": date, "Change": -1.0 * price * quantity}, ignore_index=True
        ).sort_values("Date")

        # store transaction in df
        self.transactions = self.transactions.append(
            {
                "Date": date,
                "Transaction": "buy",
                "Ticker": ticker,
                "Currency": currency,
                "Price": 1.0 * price,
                "Quantity": 1.0 * quantity,
                "TradeValue": 1.0 * price * quantity,
            },
            ignore_index=True,
            sort=False,
        ).sort_values("Date")

        self.cash = self.get_cash(date=todays_date())

        print(
            "buying {0:.2f} {1} (new balance: {2:.2f} {3})".format(
                quantity, ticker, self.cash, currency
            )
        )

    def sell_security(self, date, ticker, currency="USD", price=None, quantity=0):

        # modify quantity for subsequent stock splits
        quantity, modifier = self.securities[ticker].modify_quantity(date, quantity)

        # get closing price of security for transaction date if price not provided
        # modify price according to stock splits
        try:
            if np.isnan(price):
                price = self.securities[ticker].get_price_at(date)
            else:
                price = price / modifier
        except:
            if price is None:
                price = self.securities[ticker].get_price_at(date)
            else:
                price = price / modifier

        # remove number of securities from prices deque
        for i in range(np.int(quantity)):
            _ = self.prices_fifo[ticker].popleft()
            _ = self.prices_lifo[ticker].pop()

        # make sure security is fully removed, correct for rounding errors
        _df = self.transactions.loc[
            self.transactions.Transaction.isin(("buy", "sell")), :
        ].copy()
        _df.loc[_df.Transaction == "sell", "Quantity"] = _df.loc[
            _df.Transaction == "sell", "Quantity"
        ].apply(lambda x: -x)

        # set quantity to exactly match remaining quantity in portfolio
        if _df.groupby(by=["Ticker"])["Quantity"].sum()[ticker] <= quantity * 1.0001:
            quantity = _df.groupby(by=["Ticker"])["Quantity"].sum()[ticker]

        # store point in time value in wallet
        self.wallet = self.wallet.append(
            {"Date": date, "Change": 1.0 * price * quantity}, ignore_index=True
        ).sort_values("Date")

        # store transaction in df
        self.transactions = self.transactions.append(
            {
                "Date": date,
                "Transaction": "sell",
                "Ticker": ticker,
                "Currency": currency,
                "Price": 1.0 * price,
                "Quantity": 1.0 * quantity,
                "TradeValue": 1.0 * price * quantity,
            },
            ignore_index=True,
            sort=False,
        ).sort_values("Date")

        self.cash = self.get_cash(date=todays_date())

        print(
            "selling {0:.2f} {1} (new balance: {2:.2f} {3})".format(
                quantity, ticker, self.cash, currency
            )
        )

        # potentially remove ticker from list
        _df = self.transactions.loc[
            self.transactions.Transaction.isin(("buy", "sell")), :
        ].copy()
        _df.loc[_df.Transaction == "sell", "Quantity"] = _df.loc[
            _df.Transaction == "sell", "Quantity"
        ].apply(lambda x: -x)
        if _df.groupby(by=["Ticker"])["Quantity"].sum()[ticker] <= 0.0001:
            self.remove_security(ticker)
            # print('removing', ticker)

    def overview(self):

        # you have to have one security in the portfolio for meaningful output
        if len(self.securities) > 0:

            # sum up by ticker
            _df = self.transactions.loc[
                self.transactions.Transaction.isin(("buy", "sell", "dividend")), :
            ].copy()
            _df.loc[_df.Transaction == "sell", "Quantity"] = _df.loc[
                _df.Transaction == "sell", "Quantity"
            ].apply(lambda x: -x)
            _df.loc[_df.Transaction == "sell", "TradeValue"] = _df.loc[
                _df.Transaction == "sell", "TradeValue"
            ].apply(lambda x: -x)
            _df.loc[_df.Transaction == "dividend", "TradeValue"] = _df.loc[
                _df.Transaction == "dividend", "TradeValue"
            ].apply(lambda x: -x)
            _df.loc[_df.Transaction == "dividend", "Quantity"] = 0
            self.overview_df = _df.groupby(by=["Ticker"])[
                "Quantity", "TradeValue"
            ].sum()

            # check if sum over volume of a security is < 0
            for index, row in self.overview_df.iterrows():
                if row["Quantity"] < -0.0001:
                    print(
                        "Negative volume encountered: {0:5}\t{1}".format(
                            index, row["Quantity"]
                        )
                    )

            # restrict to securities with volume > 0
            self.overview_df = self.overview_df.loc[self.overview_df.Quantity > 0.0001]

            for ticker in self.tickers:
                self.overview_df.loc[
                    self.overview_df.index == ticker, "LastPrice"
                ] = self.securities[ticker].get_last_price()
                # calculate average security prices from deque of prices
                self.overview_df.loc[
                    self.overview_df.index == ticker, "AvgPriceAll"
                ] = np.mean(self.prices[ticker])
                # calculate average security prices from deque of prices
                self.overview_df.loc[
                    self.overview_df.index == ticker, "AvgPriceFiFo"
                ] = np.mean(self.prices_fifo[ticker])
                # calculate average security prices from deque of prices (last in first out)
                self.overview_df.loc[
                    self.overview_df.index == ticker, "AvgPriceLiFo"
                ] = np.mean(self.prices_lifo[ticker])

            self.overview_df["CurrentValue"] = (
                self.overview_df["LastPrice"] * self.overview_df["Quantity"]
            )

            # sum up dividends by ticker
            self.overview_df["Dividends"] = self.dividends.groupby(by="Ticker")[
                "Amount"
            ].sum()

            self.overview_df["AvgPrice"] = self.overview_df["TradeValue"] / (
                1.0 * self.overview_df["Quantity"]
            )
            self.overview_df.fillna(0.0, inplace=True)
            self.overview_df["Return"] = (
                self.overview_df["CurrentValue"]
                - self.overview_df["TradeValue"]
                + self.overview_df["Dividends"]
            )

            # average price to value ratio
            self.overview_df["AvgPriceToValue"] = (
                self.overview_df["TradeValue"] / self.overview_df["CurrentValue"]
            )

            # join in names of securities
            for ticker in self.tickers:
                self.overview_df.loc[
                    self.overview_df.index == ticker, "Description"
                ] = self.securities[ticker].name

        # make dummy df when no (more) securities in portfolio
        else:
            _d = {
                "Quantity": [0],
                "AvgPriceAll": [0],
                "AvgPriceFiFo": [0],
                "AvgPriceLiFo": [0],
                "AvgPrice": [0],
                "TradeValue": [0],
                "LastPrice": [0],
                "CurrentValue": [0],
                "Dividends": [0],
                "Return": [0],
                "AvgPriceToValue": [0],
                "Description": [np.nan],
            }
            self.overview_df = pd.DataFrame(data=_d, index=[""])

        # update portfolio stats
        self.total_security_value = self.overview_df[["CurrentValue"]].sum().values[0]
        self.total_portfolio_value = self.total_security_value + self.cash
        self.return_value = (
            self.total_security_value
            + self.cash
            - self.payments["In"].sum()
            + self.payments["Out"].sum()
        )
        if self.total_portfolio_value:
            try:
                self.return_rate = self.return_value / (self.payments["In"].sum() - self.payments["Out"].sum())
            except:
                self.return_rate = 0.0
        else:
            self.return_rate = 0.0

        print(
            self.overview_df[
                [
                    "Quantity",
                    "AvgPriceAll",
                    "AvgPriceFiFo",
                    "AvgPriceLiFo",
                    "AvgPrice",
                    "LastPrice",
                    "TradeValue",
                    "CurrentValue",
                    "Dividends",
                    "Return",
                    "AvgPriceToValue",
                    "Description",
                ]
            ]
        )
        print()
        print(
            "Total portfolio value:\t{0:8.2f} USD\nTotal security value:\t{1:8.2f} USD\nCash in wallet:\t\t{2:8.2f} USD\nTotal return:\t\t{3:8.2f} USD\t({4:.2f}%)".format(
                self.total_portfolio_value,
                self.total_security_value,
                self.cash,
                self.return_value,
                self.return_rate * 100.0,
            )
        )

    def overview_archive(self):

        # you have to have one security historically in the portfolio for meaningful output
        if len(self.securities_archive) > 0:

            # sum up by ticker
            _df = self.transactions.loc[
                self.transactions.Transaction.isin(("buy", "sell")), :
            ].copy()
            _df.loc[_df.Transaction == "sell", "Quantity"] = _df.loc[
                _df.Transaction == "sell", "Quantity"
            ].apply(lambda x: -x)
            _df.loc[_df.Transaction == "sell", "TradeValue"] = _df.loc[
                _df.Transaction == "sell", "TradeValue"
            ].apply(lambda x: -x)
            self.overview_archive_df = _df.groupby(by=["Ticker"])[
                "Quantity", "TradeValue"
            ].sum()

            # check if sum over volume of a security is < 0
            for index, row in self.overview_archive_df.iterrows():
                if row["Quantity"] < 0.0:
                    print(
                        "Negative volume encountered: {0:5}\t{1}".format(
                            index, row["Quantity"]
                        )
                    )

            # restrict to securities with volume == 0 (if in portfolio)
            if len(
                self.overview_archive_df.loc[self.overview_archive_df.Quantity == 0]
            ):
                self.overview_archive_df = self.overview_archive_df.loc[
                    self.overview_archive_df.Quantity == 0
                ]

                for ticker in self.tickers_archive:
                    self.overview_archive_df.loc[
                        self.overview_archive_df.index == ticker, "LastPrice"
                    ] = self.securities_archive[ticker].get_last_price()
                    # calculate average security prices from deque of prices
                    self.overview_archive_df.loc[
                        self.overview_archive_df.index == ticker, "AvgPriceAll"
                    ] = np.mean(self.prices[ticker])

                # sum up dividends by ticker
                self.overview_archive_df["Dividends"] = self.dividends.groupby(
                    by="Ticker"
                )["Amount"].sum()
                self.overview_archive_df.fillna(0.0, inplace=True)
                self.overview_archive_df["Return"] = (
                    -self.overview_archive_df["TradeValue"]
                    + self.overview_archive_df["Dividends"]
                )

                # join in names of securities
                for ticker in self.tickers_archive:
                    self.overview_archive_df.loc[
                        self.overview_archive_df.index == ticker, "Description"
                    ] = self.securities_archive[ticker].name

            # make dummy df when no (more) securities are in portfolio archive that are not in portfolio
            else:
                _d = {
                    "Quantity": [0],
                    "AvgPriceAll": [0],
                    "TradeValue": [0],
                    "LastPrice": [0],
                    "Dividends": [0],
                    "Return": [0],
                    "Description": [np.nan],
                }
                self.overview_archive_df = pd.DataFrame(data=_d, index=[""])

        # make dummy df when no (more) securities are in portfolio archive that are not in portfolio
        else:
            _d = {
                "Quantity": [0],
                "AvgPriceAll": [0],
                "TradeValue": [0],
                "LastPrice": [0],
                "Dividends": [0],
                "Return": [0],
                "Description": [np.nan],
            }
            self.overview_archive_df = pd.DataFrame(data=_d, index=[""])

        print(
            self.overview_archive_df[
                [
                    "Quantity",
                    "AvgPriceAll",
                    "LastPrice",
                    "TradeValue",
                    "Dividends",
                    "Return",
                    "Description",
                ]
            ]
        )

    def positions(self):
        # you have to have one security in the portfolio for meaningful output
        if len(self.securities) > 0:
            # sum up by ticker

            _df = self.transactions.loc[
                self.transactions.Transaction.isin(("buy", "sell")), :
            ].copy()
            _df.loc[_df.Transaction == "sell", "Quantity"] = _df.loc[
                _df.Transaction == "sell", "Quantity"
            ].apply(lambda x: -x)
            _df.loc[_df.Transaction == "sell", "TradeValue"] = _df.loc[
                _df.Transaction == "sell", "TradeValue"
            ].apply(lambda x: -x)
            self.positions_df = _df.groupby(by=["Ticker"])[
                "Quantity", "TradeValue"
            ].sum()

            # sum up purchases
            self.positions_df["Bought"] = (
                _df.loc[_df.Transaction == "buy", :]
                .groupby(by=["Ticker"])["Quantity"]
                .sum()
            )
            self.positions_df["Invested"] = (
                _df.loc[_df.Transaction == "buy", :]
                .groupby(by=["Ticker"])["TradeValue"]
                .sum()
            )

            # sum up sales
            self.positions_df["Sold"] = (
                _df.loc[_df.Transaction == "sell", :]
                .groupby(by=["Ticker"])["Quantity"]
                .sum()
            )
            self.positions_df["Devested"] = (
                _df.loc[_df.Transaction == "sell", :]
                .groupby(by=["Ticker"])["TradeValue"]
                .sum()
            )

            # check if sum over volume of a security is < 0
            for index, row in self.positions_df.iterrows():
                if row["Quantity"] < 0.0:
                    print(
                        "Negative volume encountered: {0:5}\t{1}".format(
                            index, row["Quantity"]
                        )
                    )

            # join in last price and names of securities
            for ticker in set(self.positions_df.index):
                if ticker in self.tickers:
                    self.positions_df.loc[
                        self.positions_df.index == ticker, "LastPrice"
                    ] = self.securities[ticker].get_last_price()
                    self.positions_df.loc[
                        self.positions_df.index == ticker, "Description"
                    ] = self.securities[ticker].name
                elif ticker in self.tickers_archive:
                    self.positions_df.loc[
                        self.positions_df.index == ticker, "LastPrice"
                    ] = self.securities_archive[ticker].get_last_price()
                    self.positions_df.loc[
                        self.positions_df.index == ticker, "Description"
                    ] = self.securities_archive[ticker].name
                else:
                    _security = Security(ticker)
                    self.positions_df.loc[
                        self.positions_df.index == ticker, "LastPrice"
                    ] = _security.get_last_price()
                    self.positions_df.loc[
                        self.positions_df.index == ticker, "Description"
                    ] = _security.name

            self.positions_df["CurrentValue"] = (
                self.positions_df["LastPrice"] * self.positions_df["Quantity"]
            )

            # sum up dividends by ticker
            self.positions_df["Dividends"] = self.dividends.groupby(by="Ticker")[
                "Amount"
            ].sum()

            # self.positions_df['AvgPrice'] = self.positions_df['TradeValue'] / (1.0*self.positions_df['Quantity'])
            self.positions_df.fillna(0.0, inplace=True)
            self.positions_df["Return"] = (
                self.positions_df["CurrentValue"]
                - self.positions_df["TradeValue"]
                + self.positions_df["Dividends"]
            )
            self.positions_df["PercentGrowth"] = (
                100.0 * self.positions_df["Return"] / self.positions_df["Invested"]
            )
            self.positions_df.PercentGrowth.replace(
                [np.inf, -np.inf], np.nan, inplace=True
            )

            print(
                self.positions_df[
                    [
                        "Quantity",
                        "Bought",
                        "Sold",
                        "CurrentValue",
                        "Invested",
                        "Devested",
                        "Dividends",
                        "Return",
                        "PercentGrowth",
                        "Description",
                    ]
                ].sort_values(by=["CurrentValue", "Invested"], ascending=False)
            )

        else:
            print("No positions in portfolio.")

    def get_timeseries(self):

        # get date range from the transaction list
        self.min_date = min(self.transactions.Date.min(), self.payments.Date.min())
        self.max_date = datetime.datetime.now()

        # make a list of days between min and max date as index for timeseries df
        date_index = pd.date_range(self.min_date, self.max_date, freq="D")
        _ts = pd.Series(range(len(date_index)), index=date_index)

        # create timeseries df from date index and wallet entries
        _df_ts = (
            _ts.to_frame("Day")
            .join(self.wallet[["Date", "Change"]].groupby(by="Date").sum(), how="left")
            .fillna(method="ffill")
        )

        # join in daily price data for each security
        for security in self.tickers_archive:
            _series = self.securities_archive[security].data["Close"]
            _series = _series.rename(str(_series.name) + "_" + security)
            _df_ts = _df_ts.join(_series, how="left", rsuffix="").fillna(method="ffill")

        for security in self.tickers_archive:
            _df = self.transactions.loc[
                (self.transactions.Ticker == self.securities_archive[security].ticker)
                & (self.transactions.Transaction.isin(("buy", "sell"))),
                :,
            ].copy()
            _df.loc[_df.Transaction == "sell", "Quantity"] = _df.loc[
                _df.Transaction == "sell", "Quantity"
            ].apply(lambda x: -x)
            _df = _df[["Date", "Quantity"]].groupby(by=["Date"]).sum().cumsum()
            _df.columns = _df.columns.map(lambda x: str(x) + "_" + security)
            _df_ts = _df_ts.join(_df, how="left", rsuffix="").fillna(method="ffill")

        # fill all values forward then calculate value in portfolio
        _df_ts = _df_ts.fillna(method="ffill")
        for security in self.tickers_archive:
            _df_ts[security] = (
                _df_ts["Close_" + security] * _df_ts["Quantity_" + security]
            )

        # calculate portfolio value
        _df_ts = _df_ts.join(
            self.wallet[["Date", "Change"]].groupby(by="Date").sum().cumsum(),
            how="left",
            rsuffix="_tot",
        ).fillna(method="ffill")
        _df_ts["Cash"] = _df_ts["Change_tot"]
        _df_ts["Total"] = _df_ts["Change_tot"]
        for security in self.tickers_archive:
            _df_ts["Total"] = _df_ts["Total"] + _df_ts[security].fillna(0)

        # calculate portfolio value
        _df = self.payments.groupby(by=["Date"]).sum().cumsum()
        _df["Total_deposited"] = _df["In"] - _df["Out"]
        _df_ts = _df_ts.join(_df, how="left", rsuffix="").fillna(method="ffill")
        _df_ts["Growth"] = _df_ts["Total"] / _df_ts["Total_deposited"]

        self.data = _df_ts[self.tickers_archive + ["Cash", "Total"]]
        self.data_growth = _df_ts[["Total", "Total_deposited", "Growth"]]

    def get_returns(self, column="Total"):
        try:
            self.data
        except AttributeError:
            self.get_timeseries()
        else:
            pass

        self.data_growth, _ = returns_column(df=self.data_growth, column=column)

        # get date range from the transaction list
        self.min_date = min(self.transactions.Date.min(), self.payments.Date.min())
        self.max_date = datetime.datetime.now()

        # make a list of days between min and max date as index for timeseries df
        date_index = pd.date_range(self.min_date, self.max_date, freq="D")
        _ts = pd.Series(range(len(date_index)), index=date_index)

        # create timeseries df from date index and wallet entries
        _df_ts = _ts.to_frame("Day")
        #

        # join in daily price change data for each security
        cols = []
        for security in self.tickers:
            _series = self.securities[security].data["Close"]
            _col_name = str(_series.name) + "_" + security
            _series = _series.rename(_col_name)
            _df_ts = _df_ts.join(_series, how="left", rsuffix="").fillna(method="ffill")
            _df_ts, _ = returns_column(df=_df_ts, column=_col_name, outname=security)
            cols.append(_col_name)

        self.returns = _df_ts.drop(cols, axis=1)

    def get_benchmark(self, benchmark_ticker="^GSPC"):

        if benchmark_ticker == "sp500" or benchmark_ticker == "^GSPC":
            _ticker = "^GSPC"
        else:
            _ticker = "^GSPC"  # S&P 500 as default

        # create security class object for benchmark ticker
        _benchmark = Security(_ticker, start=self.min_date, end=self.max_date)

        # calculate returns for the benchmark
        _benchmark.data, _ = returns_column(df=_benchmark.data, column="Close")

        self.benchmark = _benchmark

    def get_performance(self):
        try:
            self.data
        except AttributeError:
            self.get_timeseries()
        else:
            pass

        years = []
        growths = []
        dollar_returns = []
        for year in self.data_growth.index.year.unique():
            # get first and last day of year
            min_date = self.data_growth.loc[
                self.data_growth.index.year == year, :
            ].index.min()
            max_date = self.data_growth.loc[
                self.data_growth.index.year == year, :
            ].index.max()

            # compare growth (percentage and dollars) between end of year and beginning of year
            growth = 100 * (
                self.data_growth.loc[
                    self.data_growth.index == max_date, "Growth"
                ].values[0]
                - self.data_growth.loc[
                    self.data_growth.index == min_date, "Growth"
                ].values[0]
            )
            dollar_return = (
                self.data_growth.loc[
                    self.data_growth.index == max_date, "Total"
                ].values[0]
                - self.data_growth.loc[
                    self.data_growth.index == max_date, "Total_deposited"
                ].values[0]
            ) - (
                self.data_growth.loc[
                    self.data_growth.index == min_date, "Total"
                ].values[0]
                - self.data_growth.loc[
                    self.data_growth.index == min_date, "Total_deposited"
                ].values[0]
            )
            years.append(year)
            growths.append(growth)
            dollar_returns.append(dollar_return)

        _df = pd.DataFrame({"Year": years, "Growth": growths, "Return": dollar_returns})

        return _df


class TotalPortfolioValue(object):
    """
       Class that turns the portfolio total into a security-like object
    """

    def __init__(self, name, data):
        self.ticker = name
        self.data = data

    def set_name(self, name):
        self.name = name

    def update_data(self, data):
        self.data = data

    def get_returns(self, column="Total"):
        self.data, _ = returns_column(df=self.data, column=column)

    def get_benchmark(self, benchmark_ticker="^GSPC"):

        self.min_date = self.data.index.min()
        self.max_date = min(self.data.index.max(), datetime.datetime.now())

        if benchmark_ticker == "sp500" or benchmark_ticker == "^GSPC":
            _ticker = "^GSPC"
        else:
            _ticker = "^GSPC"  # S&P 500 as default

        # create security class object for benchmark ticker
        _benchmark = Security(_ticker, start=self.min_date, end=self.max_date)

        # calculate returns for the benchmark
        _benchmark.data, _ = returns_column(df=_benchmark.data, column="Close")

        self.benchmark = _benchmark
