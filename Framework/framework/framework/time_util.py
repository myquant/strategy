# encoding: utf-8

import arrow


def before_10_am(utc_time):
    # use bar time to check if before 10 AM
    t = arrow.get(utc_time).to('local')
    hour = t.datetime.hour
    return hour < 10 and hour >= 9     # FIXED hour error

def after_10_am(utc_time):
    # use bar time to check if after 10 AM
    t = arrow.get(utc_time).to('local')
    hour = t.datetime.hour
    return hour >= 10

def is_10_am(utc_time):
    t = arrow.get(utc_time).to('local')
    return t.datetime.hour == 10 and t.datetime.minute == 0

def before_14_30(utc_time):
    # use bar time to check if before 14:30
    t = arrow.get(utc_time).to('local')
    hour = t.datetime.hour
    return hour < 14 or (hour == 14 and t.datetime.minute < 30)

def market_open_time(utc_time):
    t = arrow.get(utc_time).to('local')
    return t.datetime.hour == 9 and 25 <= t.datetime.minute < 30

def continue_trading_time(utc_time):
    t = arrow.get(utc_time).to('local')
    return (t.datetime.hour == 9 and t.datetime.minute >=30) or t.datetime.hour > 9

def stock_bidding_time(utc_time):
    t = arrow.get(utc_time).to('local')
    return t.datetime.hour == 9 and (t.datetime.minute >=15 and t.datetime.minute < 25)
