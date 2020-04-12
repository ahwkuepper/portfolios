# -*- coding: utf-8 -*-

from getpass import getpass

import numpy as np

import robin_stocks as r
from etfs.stats.basics import ewm_column


def get_stop_loss_price(security=None, column="Close", alpha=0.5, sigmas=2):
    """
    Return a price that can be used as stop loss signal
    """

    if security:
        # add a column with exponential moving average of price column
        _df, _column_ewm = ewm_column(security.data, column=column, alpha=alpha)
        _columns = _df.columns

        # get the latest exponentially weighted averaged price
        security.last_price_ewm = _df[_column_ewm].values[-1]
        _df["Deviation_ewm"] = _df[column] - security.last_price_ewm

        # calculate standard deviation
        _df["Squared_Deviation_ewm"] = np.square(_df["Deviation_ewm"])
        _df, _column_ewm2 = ewm_column(_df, column="Squared_Deviation_ewm", alpha=alpha)
        _df["Standard_deviation_ewm"] = np.sqrt(_df[_column_ewm2])

        # get the latest exponentially weighted average standard deviation
        security.last_standard_deviation_ewm = _df["Standard_deviation_ewm"].values[-1]

        price = security.last_price_ewm - sigmas * security.last_standard_deviation_ewm
    else:
        price = 0.0

    return price


def put_in_stop_loss_orders_all(
    access_token=None,
    username=None,
    password=None,
    portfolio=None,
    column="Close",
    alpha=0.5,
    sigmas=2,
):
    """
    Accesses Robinhood account and put in stop loss sell orders for all securities in a portfolio.
    Stop loss price is calculated as exponentially weighted average price and standard deviation.


    Parameters
    ==========
    username : Robinhood username
    password : Robinhood account password
    portfolio : portfolio name 
    free_stock : include a free stock not captured by transaction history (see below)

    Returns
    =======

    """

    import time

    if not access_token:
        if username is None:
            username = getpass("Username: ")
        if password is None:
            password = getpass("Password: ")

        # use Robinhood api to access account
        r.login(username, password)

    # check if positions_df exists and if not get current positions
    try:
        portfolio.positions_df
    except AttributeError:
        portfolio.positions_df = None
    if portfolio.positions_df is None:
        portfolio.positions()
    positions_data = r.get_current_positions()

    # cancel all standing orders
    r.cancel_all_open_orders()

    # calculate stop loss prices
    for ticker in portfolio.tickers:

        # get stock data from Robinhood API
        stock_data = [
            item
            for item in positions_data
            if r.get_name_by_url(item["instrument"]) == r.get_name_by_symbol(ticker)
        ][0]

        # assert that portfolio positions are the same as returned from API
        if (portfolio.positions_df.Quantity[ticker] > 0) & (
            portfolio.positions_df.Quantity[ticker] == float(stock_data["quantity"])
        ):
            portfolio.securities[ticker].latest_price = float(
                r.get_latest_price([ticker])[0]
            )
            portfolio.securities[ticker].stop_loss_price = round(
                get_stop_loss_price(
                    security=portfolio.securities[ticker],
                    column=column,
                    alpha=alpha,
                    sigmas=sigmas,
                ),
                2,
            )
            quantity = float(stock_data["quantity"])

            # print out summary
            print(
                ticker,
                quantity,
                portfolio.securities[ticker].latest_price,
                portfolio.securities[ticker].last_price_ewm,
                portfolio.securities[ticker].stop_loss_price,
                portfolio.securities[ticker].stop_loss_price
                - portfolio.securities[ticker].last_price_ewm,
                100
                * (
                    portfolio.securities[ticker].stop_loss_price
                    - portfolio.securities[ticker].latest_price
                )
                / portfolio.securities[ticker].latest_price,
            )

            # put in the order
            r.order_sell_stop_loss(
                ticker, quantity, portfolio.securities[ticker].stop_loss_price
            )

            # Wait for a few seconds to not get thrown off Robinhood
            time.sleep(1)

        else:
            print(
                "Disagreement: ",
                ticker,
                portfolio.positions_df.Quantity[ticker],
                float(stock_data["quantity"]),
            )
