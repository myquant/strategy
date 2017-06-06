# encoding: utf-8

import pandas as pd
import arrow
import numpy as np

from . import helper


ONE_MINUTE = 60
ONE_DAY = 86400

BAR_COLUMNS = ['datetime',
               'symbol',
               'frequency',
               'open',
               'high',
               'low',
               'close',
               'pre_close',
               'adj_factor',
               'volume',
               'position',
               'utc_time',
               'strtime',
               'strendtime']

TICK_COLUMNS = ['datetime',
                'symbol',
                'last_price',
                'last_volume',
                'high',
                'low',
                'ask_p1',
                'ask_v1',
                'bid_p1',
                'bid_v1',
                'cum_position',
                'cum_volume',
                'utc_time',
                'upper_limit',
                'lower_limit']


def frequency_readable(bar_type):
    frequency = ''

    if bar_type == ONE_DAY:
        frequency = '1d'
    elif bar_type >= ONE_MINUTE:
        frequency = "{}m".format(divmod(bar_type, ONE_MINUTE)[0])
    else:
        frequency = "{}s".format(bar_type)

    return frequency


def frequency_to_int(freq):
    if "s" in freq:
        k, _ = freq.split("s")
        return int(k)
    elif "m" in freq:
        k, _ = freq.split("m")
        return int(k) * ONE_MINUTE
    elif "d" in freq:
        k, _ = freq.split("d")
        return int(k) * ONE_DAY


def local_datetime(utc_time):
    return arrow.get(utc_time).to('local').datetime


def bars_to_dataframe(bars):
    def expand_bar(bar):
        return [
            local_datetime(bar.utc_time),
            helper.symbol(bar),
            frequency_readable(bar.bar_type),
            bar.open,
            bar.high,
            bar.low,
            bar.close,
            bar.pre_close,
            bar.adj_factor,
            bar.volume,
            bar.position,
            bar.utc_time,
            bar.strtime,
            bar.strendtime if hasattr(bar, 'strendtime') else bar.strtime
        ]

    return pd.DataFrame([expand_bar(b) for b in bars], columns=BAR_COLUMNS)


def ticks_to_dataframe(ticks):
    def expand_tick(tick):
        return [
            local_datetime(tick.utc_time),
            helper.symbol(tick),
            tick.last_price,
            tick.last_volume,
            tick.high,
            tick.low,
            helper.ask_price_1(tick),
            helper.ask_vol_1(tick),
            helper.bid_price_1(tick),
            helper.bid_vol_1(tick),
            tick.cum_position,
            tick.cum_volume,
            tick.utc_time,
            tick.upper_limit,
            tick.lower_limit
        ]
    return pd.DataFrame([expand_tick(t) for t in ticks], columns=TICK_COLUMNS)


def bar_dict_to_dataframe(k_bars, k=None):
    data = []
    if k:
        one_key_data = make_matrix(k_bars, k)
        return pd.DataFrame(one_key_data, columns=BAR_COLUMNS)

    for k in list(k_bars.keys()):
        one_key_data = make_matrix(k_bars, k)
        data.extend(one_key_data)

    return pd.DataFrame(data, columns=BAR_COLUMNS)


def make_matrix(k_bars, k):
    if not k in k_bars:
        return None

    datetimes = list(k_bars.get(k).get('datetime'))
    symbols = list(k_bars.get(k).get('symbol'))
    frequencies = list(k_bars.get(k).get('frequency'))
    opens = list(k_bars.get(k).get('open'))
    highs = list(k_bars.get(k).get('high'))
    lows = list(k_bars.get(k).get('low'))
    closes = list(k_bars.get(k).get('close'))
    pre_closes = list(k_bars.get(k).get('pre_close'))
    adj_factors = list(k_bars.get(k).get('adj_factor'))
    volumes = list(k_bars.get(k).get('volume'))
    positions = list(k_bars.get(k).get('position'))
    utc_times = list(k_bars.get(k).get('utc_time'))
    strtimes = list(k_bars.get(k).get('strtime'))
    strendtimes = list(k_bars.get(k).get('strendtime'))
    values = [datetimes, symbols, frequencies, opens, highs, lows, closes, pre_closes, adj_factors,
                                 volumes, positions, utc_times, strtimes, strendtimes]

    # transpose
    values_t = list(map(list, zip(*values)))
    return values_t
