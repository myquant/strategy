# encoding: utf-8

import arrow
import numpy as np
from gmsdk import *

ONE_MINUTE = 60  # min in seconds

LIMIT1 = '2016-11-15 00:00:00'


def noop(*args, **kwargs):
    pass


def last_price(tick):
    return tick.last_price


def last_volume(tick):
    return tick.last_volume


def bid_price(tick, i):
    prc = 0.0
    if tick.exchange in ('SHSE', 'SZSE'):
        if i > 5:
            i = 5
        prc = tick.bids[i-1][0] if len(tick.bids) else 0.0
    else:
        prc = tick.bids[0][0] if len(tick.bids) else 0.0

    return prc


def ask_price(tick, i):
    prc = 0.0
    if tick.exchange in ('SHSE', 'SZSE'):
        if i > 5:
            i = 5
        prc = tick.asks[i-1][0] if len(tick.asks) else float('inf')
    else:
        prc = tick.asks[0][0] if len(tick.bids) else float('inf')

    return prc


def bid_price_1(tick):
    return tick.bids[0][0] if len(tick.bids) else 0.0


def ask_price_1(tick):
    return tick.asks[0][0] if len(tick.asks) else float('inf')


def bid_vol_1(tick):
    return tick.bids[0][1] if len(tick.bids) else 0.0


def ask_vol_1(tick):
    return tick.asks[0][1] if len(tick.asks) else 0.0


def spread(tick):
    return ask_price_1(tick) - bid_price_1(tick)


def symbol(tick):
    return symbol_combine(tick.exchange, tick.sec_id)


def symbol_combine(exchange, sec_id):
    return "{}.{}".format(exchange, sec_id)


# 挂单价格 - 对手价买一（side = OrderSide_Ask）或卖一（side = OrderSide_Bid ）
def get_oppsite_price(tick, side):
    if tick:
        if side == OrderSide_Bid:  ## 1  buy
            return ask_price_1(tick)
        if side == OrderSide_Ask:  ## 2  sell
            return bid_price_1(tick)
    else:
        return 0.0


def aggressive_oppsite_price(tick, side, hops, tick_size):
    if not tick:
        return 0.0

    prc = 0.0
    if side == OrderSide_Bid:
        prc = ask_price_1(tick) + hops * tick_size
        if prc > tick.upper_limit:
            prc = tick.upper_limit
    if side == OrderSide_Ask:
        prc = bid_price_1(tick) - hops * tick_size
        if prc < tick.lower_limit:
            prc = tick.lower_limit

    return prc


def close_long_position(inst, b_p, price=0.0,sync=False):
    if b_p.exchange in (u'SHSE', u'SZSE'):  ## stocks
        if b_p.available_yesterday:
            inst.logger.info("close long yesterday {}.{} {} @ {:.3f}".format(b_p.exchange, b_p.sec_id, b_p.available_yesterday, price))
            if not sync:
                inst.close_long(b_p.exchange, b_p.sec_id, price, b_p.available_yesterday)
            else:
                inst.close_long_sync(b_p.exchange, b_p.sec_id, price, b_p.available_yesterday)
    else:
        if b_p.exchange == u'SHFE':    ## special in SHFE
            if b_p.available_today > 0:
                inst.logger.info("close long today {}.{} {} @ {:.3f}".format(b_p.exchange, b_p.sec_id, b_p.available_today, price))
                if not sync:
                    inst.close_long(b_p.exchange, b_p.sec_id, price, b_p.available_today)
                else:
                    inst.close_long_sync(b_p.exchange, b_p.sec_id, price, b_p.available_today)
            if b_p.available_yesterday > 0:
                inst.logger.info("close long yesterday {}.{} {} @ {:.3f}".format(b_p.exchange, b_p.sec_id, b_p.available_yesterday, price))
                if not sync:
                    inst.close_long_yesterday(b_p.exchange, b_p.sec_id, price, b_p.available_yesterday)
                else:
                    inst.close_long_yesterday_sync(b_p.exchange, b_p.sec_id, price, b_p.available_yesterday)
        else:
            if b_p.available > 0:
                inst.logger.info("close long {}.{} {} @ {:.3f}".format(b_p.exchange, b_p.sec_id, b_p.available, price))
                if not sync:
                    inst.close_long(b_p.exchange, b_p.sec_id, price, b_p.available)
                else:
                    inst.close_long_sync(b_p.exchange, b_p.sec_id, price, b_p.available)                    
            else:
                inst.logger.error("Error: {}.{} available {} not a positive number".format(b_p.exchange, b_p.sec_id, b_p.available))


def close_short_position(inst, a_p, price=0.0, sync=False):
    if a_p.exchange in (u'SHSE', u'SZSE'):  ## stocks, something must be wrong
        if a_p.available_yesterday:  # support short stocks now
            inst.logger.info("close short yesterday {}.{} {} @ {:.3f}".format(a_p.exchange, a_p.sec_id, a_p.available_yesterday, price))
            if not sync:
                inst.close_short(a_p.exchange, a_p.sec_id, price, a_p.available_yesterday)
            else:
                inst.close_short_sync(a_p.exchange, a_p.sec_id, price, a_p.available_yesterday)
    else:
        if a_p.exchange == u'SHFE':   ## special in SHFE
            if a_p.available_today > 0:
                inst.logger.info("close short today {}.{} {} @ {:.3f}".format(a_p.exchange, a_p.sec_id, a_p.available_today, price))
                if not sync:
                    inst.close_short(a_p.exchange, a_p.sec_id, price, a_p.available_today)
                else:
                    inst.close_short_sync(a_p.exchange, a_p.sec_id, price, a_p.available_today)                    
            if a_p.available_yesterday > 0:
                inst.logger.info("close short yesterday {}.{} {} @ {:.3f}".format(a_p.exchange, a_p.sec_id, a_p.available_yesterday, price))
                if not sync:
                    inst.close_short_yesterday(a_p.exchange, a_p.sec_id, price, a_p.available_yesterday)
                else:
                    inst.close_short_yesterday_sync(a_p.exchange, a_p.sec_id, price, a_p.available_yesterday)
        else:
            if a_p.available > 0:
                inst.logger.info("close short {}.{} {} @ {:.3f}".format(a_p.exchange, a_p.sec_id, a_p.available, price))
                if not sync:
                    inst.close_short(a_p.exchange, a_p.sec_id, price, a_p.available)
                else:
                    inst.close_short_sync(a_p.exchange, a_p.sec_id, price, a_p.available)                    
            else:
                inst.logger.error("Error: {}.{} available {} not a positive number".format(a_p.exchange, a_p.sec_id, a_p.available))


from configparser import ConfigParser

LIMIT2 = '2016-11-15 00:00:00'


def init_strategy(cls, ini_file, str_id=None):
    ## read configuration from ini
    config = ConfigParser.ConfigParser()
    config.read(ini_file)

    user_name = config.get('strategy', 'username')
    password = config.get('strategy', 'password')
    strategy_id = config.get('strategy', 'strategy_id')
    subscribe_symbols = config.get('strategy', 'subscribe_symbols')
    mode = config.getint('strategy', 'mode')
    td_addr = config.get('strategy', 'td_addr')

    inst = cls(
        username=user_name,
        password=password,
        mode=mode,
        td_addr=td_addr,
        subscribe_symbols=subscribe_symbols,
        strategy_id=strategy_id if not str_id else str_id,
    )
    inst.config = config
    return inst

def init_strategy_with_given_id(cls, ini_file, str_id):
    return init_strategy(cls, ini_file, str_id)

def check_exchange(sym):
    szse_prefix = ('30', '00', '15')
    shse_prefix = ('60', '51')  #ignore index starts with 000

    if sym[:2] in shse_prefix:
        return 'SHSE'
    elif sym[:2] in szse_prefix:
        return 'SZSE'
    else:
        raise Exception('wrong code')


LIMIT = '2017-05-15 00:00:00'


def reach_time_limit(bar, limit=LIMIT):
    # ignore
    return False
    LIMIT3 = '2016-11-15 00:00:00'

    ts = arrow.get(bar.utc_time) - arrow.get(limit)
    if ts.total_seconds() > 0:
        return True
    return False
