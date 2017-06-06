# -*- coding: utf-8 -*-

import sys
import logging.config
import numpy as np

from gmsdk import *

from framework import TAStrategy
from framework import helper
from framework.physics import *

from talib import SMA as MA


def algo(st, bar):
    print(st.ticks_to_dataframe()[['datetime', 'symbol', 'last_price']])
    symbol = st.get_symbol(bar)
    close = st.close(symbol, bar.bar_type)
    sar = st.sar(symbol, bar.bar_type)
    sma = st.ma_close(symbol, bar.bar_type, period=st.short_timeperiod)

    # mdi = st.minus_di(symbol, bar.bar_type)
    # pdi = st.plus_di(symbol, bar.bar_type)

    tick_size = st.tick_size(bar.sec_id)
    if len(sar) < 3:
        return
    # print("latest sar {} ".format(sar[-3:]))
    # print(" sar cross up close : {}".format(st.cross_up(close, sar)))
    buy_signal = st.cross_up(close, sma) and span_up(close, sma) and close[-1] > sar[-1]
    sell_signal = st.cross_down(close, sma) and span_up(close, sma) and close[-1] < sar[-1]

    volume_filtered = st.volume_filtering(symbol, bar.bar_type)

    if buy_signal and volume_filtered:
        # print "buy ",bar.sec_id, bar.strtime, sar[-1] < close[-1],  sar[-3]  > close[-3]
        # a_p = st.get_position(bar.exchange, bar.sec_id, OrderSide_Ask)
        a_p = st.short_position(bar.exchange, bar.sec_id)
        ask_price = st.get_oppsite_price(bar, OrderSide_Ask) + st.hops * tick_size
        if a_p and a_p.volume > 0:
            helper.close_short_position(st, a_p, ask_price)

        # ps = st.get_position(bar.exchange, bar.sec_id, OrderSide_Bid)
        ps = st.long_position(bar.exchange, bar.sec_id)
        vol = st.calc_vol(bar, OrderSide_Bid)
        if (ps and ps.volume > 0) or vol == 0:
            return

        st.logger.info("try to open long {}.{} {}@{}".format(bar.exchange, bar.sec_id, vol, ask_price))
        st.open_long(bar.exchange, bar.sec_id, ask_price, vol)
    elif sell_signal and volume_filtered:
        # print "sell ",bar.sec_id, bar.strtime, sar[-1] > close[-1], sar[-3] < close[-3]
        # ps = st.get_position(bar.exchange, bar.sec_id, OrderSide_Bid)
        ps = st.long_position(bar.exchange, bar.sec_id)
        bid_price = st.get_oppsite_price(bar, OrderSide_Bid) - st.hops * tick_size
        if ps and ps.volume > 0:
            helper.close_long_position(st, ps, bid_price)

        # ps = st.get_position(bar.exchange, bar.sec_id, OrderSide_Ask)
        ps = st.short_position(bar.exchange, bar.sec_id)
        vol = st.calc_vol(bar, OrderSide_Bid)
        if not ps and vol > 0 and bar.exchange in ('SHFE', 'DCE', 'CFFEX', 'CZCE'):
            st.logger.info("try to open short {}.{} {}@{}".format(bar.exchange, bar.sec_id, vol, bid_price))
            st.open_short(bar.exchange, bar.sec_id, bid_price, vol)
    else:
        st.logger.info('no change ... {}.{} {}min'.format(bar.exchange, bar.sec_id, bar.bar_type/helper.ONE_MINUTE))

if __name__ == '__main__':
    import arrow
    from configparser import ConfigParser

    print(arrow.now())
    ini_file = sys.argv[1] if len(sys.argv) > 1 else 'demo.ini'
    logging.config.fileConfig(ini_file)

    st = TAStrategy(config_file=ini_file, config_file_encoding='GB18030')

    ## read configuration from ini if necessary
    # config = ConfigParser()
    # config.read(ini_file)
    # st.init(config)

    # 调用初始化
    st.init()
    # 设置自己的行情处理逻辑
    st.set_algo(algo)

    # 启动策略
    st.logger.info("Strategy ready, waiting for data ...")
    ret = st.run()
    # bt = st.get_indicator()
    print(arrow.now())
    st.logger.info("Strategy message %s" % st.get_strerror(ret))
