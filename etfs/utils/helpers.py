# -*- coding: utf-8 -*-

import datetime
import numpy as np
import pandas_market_calendars as mcal


def todays_date():
    return '{0}{1:02}{2:02}'.format(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day)


def restrict_to_trading_days(df=None, exchange='NYSE'):
    """
    Gets a trading calendar and inner joins it on input df
    """

    min_date = np.datetime64(df.index.min())
    max_date = np.datetime64(df.index.max())
    trading_cal = mcal.get_calendar(exchange)
    schedule = trading_cal.schedule(start_date=min_date, end_date=max_date)

    return df.join(schedule, how='inner')

