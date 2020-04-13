# -*- coding: utf-8 -*-

from datetime import datetime as dt
from datetime import timedelta

import numpy as np
import pandas as pd
import pandas_market_calendars as mcal


def todays_date():
    return "{0}{1:02}{2:02}".format(dt.now().year, dt.now().month, dt.now().day)


def last_trading_day(date=None, exchange="NYSE"):
    trading_cal = mcal.get_calendar(exchange)

    if date:
        today = pd.to_datetime(date)
    else:
        today = dt.now()
    last_week = today - timedelta(weeks=1)

    return pd.to_datetime(
        max(trading_cal.valid_days(start_date=last_week, end_date=today).values)
    )


def restrict_to_trading_days(df=None, exchange="NYSE"):
    """
    Gets a trading calendar and inner joins it on input df
    """

    min_date = np.datetime64(df.index.min())
    max_date = np.datetime64(df.index.max())
    trading_cal = mcal.get_calendar(exchange)
    schedule = trading_cal.schedule(start_date=min_date, end_date=max_date)

    return df.join(schedule, how="inner")


def standard_date_format(input_date):
    """
    Try to convert input date into standard format
    """

    # in case input date is in datetime or pandas timestamp format
    if type(input_date) != str:
        input_date = "{0}-{1:02}-{2:02}".format(
            input_date.year, input_date.month, input_date.day
        )

    # in case input date is in format YYYY/MM/DD or YYYY MM DD
    input_date = input_date.replace("/", "-")
    input_date = input_date.replace(" ", "-")

    # in case input date is in format YYYYMMDD or DDMMYYYY
    if len(input_date) == 8 and "-" not in input_date:
        if input_date.startswith(("20", "19")):
            input_date = input_date[:4] + "-" + input_date[4:6] + "-" + input_date[6:]
        else:
            input_date = input_date[4:] + "-" + input_date[2:4] + "-" + input_date[:2]

    return input_date


def yahoo_date_format(input_date):
    """
    Convert input date into yahoo finance format
    """

    # in case input date is in datetime or pandas timestamp format
    if type(input_date) != str:
        input_date = "{0}{1:02}{2:02}".format(
            input_date.year, input_date.month, input_date.day
        )

    # in case input date is in format YYYY/MM/DD or YYYY MM DD
    input_date = input_date.replace("/", "")
    input_date = input_date.replace("-", "")

    # in case input date is in format YYYYMMDD or DDMMYYYY
    if len(input_date) == 8:
        if input_date.startswith(("20", "19")):
            pass
        else:
            input_date = input_date[4:] + input_date[2:4] + input_date[:2]

    return input_date
