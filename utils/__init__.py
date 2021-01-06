#!/sur/bin/env python
#-*- coding: utf-8 -*-

import datetime
from monthdelta import monthdelta


def dateshift(date,delta,format="%Y-%m-%d",freq="D"): # date="YYYY--MM-DD"
    date=datetime.datetime.strptime(date,format)
    target  = None
    if freq == 'D':
        target = (date + datetime.timedelta(days = delta)).strftime(format)
    elif freq == 'M':
        target = (date +monthdelta(delta)).strftime(format)
    elif freq == 'H':
        target = (date + datetime.timedelta(hours = delta)).strftime(format)
    return  target
