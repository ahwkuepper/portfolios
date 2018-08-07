# -*- coding: utf-8 -*-

import datetime

def todays_date():
    return '{0}{1:02}{2:02}'.format(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day)
