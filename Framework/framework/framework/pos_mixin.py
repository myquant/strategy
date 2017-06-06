# encoding: utf-8

import arrow
import numpy as np
from talib import SMA
from collections import deque

from gmsdk import *

from .context import Context
from . import helper

from .time_util import *

from configparser import NoOptionError

ONE_MINUTE = 60


class Trends(object):
    """
    value: values: trend array, (long: OrderSide_Bid, short: OrderSide_Ask, other: None
           dir: trend moving, (...)
    """
    def __init__(self):
        self.values = deque(maxlen=50)
        self.values.append(0)
        self.changed = False
        self.dir = 0
        self.dir_stop_timestamp = arrow.utcnow()

    def __repr__(self):
        return "current trend: {} [ changed: {}, moving dir: {} ]".format(self.values[-1], self.changed, self.dir)

    def append(self, trend, moving):
        if len(self.values):
            prev = self.values[-1]
            if prev != trend:
                self.values.append(trend)
                self.changed = True
            else:
                self.changed = False
        else:
            self.values.append(trend)

        if moving == 0:
            self.dir_stop_timestamp = arrow.utcnow()

        self.dir = moving

    def clear(self):
        self.values.clear()

    def current_trend(self):
        return self.values[-1] if len(self.values) else 0

    def moving_dir(self):
        return self.dir

    def trend_changed(self):
        return self.changed

    def elapsed_seconds_since_stopped(self, side, now):
        if self.dir != self.current_trend() and self.current_trend() == side:
            elapsed = now - self.dir_stop_timestamp
            return elapsed.total_seconds()
        return 0

    def long_trend(self):
        return self.current_trend() == OrderSide_Bid

    def short_trend(self):
        return self.current_trend() == OrderSide_Ask

    def moving_long(self):
        return self.dir == OrderSide_Bid

    def moving_short(self):
        return self.dir == OrderSide_Ask


class PositionMixin(Context, object):

    def __init__(self, *args, **kwargs):
        # print("init pos mixin ...")
        super(PositionMixin, self).__init__(*args, **kwargs)
        self.__init_vars()
        # self.positions = kwargs.pop('positions')
        # print("init pos mixin end")

    def __init_vars(self):
        self.init_context()

        self.positions = {}
        self.highest_pnl = {}
        self.trade_counter = {}
        self.trends = {}  # key: symbol,  Trends object

        # self.moving = False
        # self.moving_short = False
        # self.moving_long = False
        # self.long_trends = False
        # self.short_trends = False
        self.momentum = 0.0
        self.momentum_side = 0

    def init_position_mixin(self):
        if not hasattr(self, 'highest_pnl'):
            self.__init_vars()

        self.__read_position_mixin_para__()

        self.init_symbols_lookup()

        # read positions from accounts
        self.__read_positions()

    def calc_history_data(self):
        self.__calc_historic_trends()

    def __calc_historic_trends(self):
        for k in list(self.k_bars.keys()):
            sym, frequency = self.decode_k_bars_key(k)
            closes = self.close(sym, frequency)
            self.__calc_trends_by_close(closes, sym)

    def __pos_key(self, symbol, side):
        k = "{}__{}".format(symbol, side)
        return k

    def __position_key(self, exchange, sec_id, side):
        k = "{}.{}__{}".format(exchange, sec_id, side)
        return k

    def __read_position_mixin_para__(self):
        self.momentum_factor = self.config.getfloat('para', 'momentum_factor')
        try:
            self.hops = self.config.getint('para', 'hops')
        except:
            self.hops = 0

        try:
            self.position_retire_age = self.config.getfloat('para', 'position_retire_age')
        except:
            self.position_retire_age = self.bar_type / helper.ONE_MINUTE if hasattr(self, 'bar_type') else 1.0

        try:
            self.position_aging = self.config.getboolean('para', 'position_aging')
        except:
            self.position_aging = True

        try:
            self.positive_stop = self.config.getboolean('para', 'positive_stop')
        except:
            self.positive_stop = False

        try:
            self.stop_lose = self.config.getboolean('para', 'stop_lose')
        except:
            self.stop_lose = True

        try:
            self.analyse_only = self.config.getboolean('para', 'analyse_only')
        except:
            self.analyse_only = False

        try:
            self.remove_leverage = self.config.getboolean('para', 'remove_leverage')
        except:
            self.remove_leverage = True

        try:
            self.follow_trends = self.config.getboolean('para', 'follow_trends')
        except:
            self.follow_trends = True

        try:
            self.use_position_filter = self.config.getboolean('para', 'use_position_filter')
        except:
            self.use_position_filter = False

        self.short_timeperiod = self.config.getint('para', 'short_timeperiod')
        self.long_timeperiod = self.config.getint('para', 'long_timeperiod')
        self.life_timeperiod = self.config.getint('para', 'life_timeperiod')

        self.drawdown = self.config.getfloat('para', 'stop_profit_drawdown')
        self.stop_lose_threshold_factor = self.config.getfloat('para', 'stop_lose_threshold_factor')
        self.stop_lose_threshold = self.stop_lose_threshold_factor
        self.threshold_factor = self.config.getfloat('para', 'threshold_factor')
        self.threshold = self.threshold_factor
        self.stop_profit_threshold_factor = self.config.getfloat('para', 'stop_profit_threshold_factor')
        self.stop_profit_threshold = self.stop_profit_threshold_factor

        try:
            self.stock_weight = self.config.getfloat('para', 'stock_weight')
        except:
            self.stock_weight = 0.02
        try:
            self.lowest_cash_limit = self.config.getfloat('para', 'lowest_cash_limit')
        except:
            self.lowest_cash_limit = 3000

        try:
            self.high_position_ratio = self.config.getfloat('para', 'high_position_ratio')
        except:
            self.high_position_ratio = 0.85

    def __read_positions(self):
        ps = self.get_positions()
        self.positions.clear()
        for p in ps:
            _pos_key = self.__position_key(p.exchange, p.sec_id, p.side)
            self.positions[_pos_key] = p

    def increase_trade_counter(self, symbol, side):
        key = self.__pos_key(symbol, side)
        if not self.trade_counter.get(key):
            self.trade_counter[key] = 0

        self.trade_counter[key] += 1

    def clear_trade_counter(self, symbol, side):
        key = self.__pos_key(symbol, side)
        self.trade_counter[key] = 0

    def close_long_position(self, b_p, ord_price=None, msg=None, sync=False):
        self.print_positions(b_p)
        symbol = helper.symbol(b_p)
        last_tick = self.tick(symbol)
        tick_size = self.tick_size(symbol)
        # last_price = self.last_price(symbol)
        # side = OrderSide_Ask
        # price = ord_price if ord_price else last_price - self.hops * tick_size
        price = ord_price if ord_price is not None else helper.aggressive_oppsite_price(last_tick, OrderSide_Ask, self.hops, tick_size)

        if self.is_closing(b_p):
            self.logger.info(
                "Wait! is closing long {} ... vol {} @ prc {:.3f}, msg = {}".format(symbol, b_p.volume, price, msg))
            return

        self.logger.info(
            "try to close long {} ... vol {} @ prc {:.3f}, if future today's position first, msg = {}".format(symbol, b_p.volume, price, msg))

        helper.close_long_position(self, b_p, price, sync)

    def close_short_position(self, a_p, ord_price=None, msg=None, sync=False):
        self.print_positions(a_p)

        symbol = helper.symbol(a_p)
        last_tick = self.tick(symbol)
        tick_size = self.tick_size(symbol)
        # last_price = self.last_price(symbol)
        # side = OrderSide_Bid
        # price = ord_price if ord_price else last_price + self.hops * tick_size
        price = ord_price if ord_price is not None else helper.aggressive_oppsite_price(last_tick, OrderSide_Bid, self.hops, tick_size)

        if self.is_closing(a_p):
            self.logger.info(
                "Wait! is closing short {} ... vol {} @ prc {:.3f}, msg = {}".format(symbol, a_p.volume, price, msg))
            return

        self.logger.info(
            "try to close short {} ... vol {} @ {:.3f}, if future today's position first, msg = {}".format(symbol, a_p.volume, price, msg))

        helper.close_short_position(self, a_p, price, sync)

    def open_long_position(self, tick_or_bar, ord_price=None, vol=None, msg=None, sync=False):
        symbol = helper.symbol(tick_or_bar)
        last_tick = self.tick(symbol)
        tick_size = self.tick_size(symbol)
        price = ord_price if ord_price is not None else helper.aggressive_oppsite_price(last_tick, OrderSide_Bid, self.hops, tick_size)
        volume = vol if vol is not None else self.calc_vol(tick_or_bar, OrderSide_Bid)
        self.logger.info("try to open long {} ... vol {} @ {:.3f}, msg = {}".format(symbol, volume, price, msg))

        if not sync:
            self.open_long(tick_or_bar.exchange, tick_or_bar.sec_id, price, volume)
        else:
            self.open_long_sync(tick_or_bar.exchange, tick_or_bar.sec_id, price, volume)

    def open_short_position(self, tick_or_bar, ord_price=None, vol=None, msg=None, sync=False):
        symbol = helper.symbol(tick_or_bar)
        last_tick = self.tick(symbol)
        tick_size = self.tick_size(symbol)
        price = ord_price if ord_price is not None else helper.aggressive_oppsite_price(last_tick, OrderSide_Ask, self.hops, tick_size)
        volume = vol if vol is not None else self.calc_vol(tick_or_bar, OrderSide_Ask)
        self.logger.info("try to open short {} ... vol {} @ {:.3f}, msg = {}".format(symbol, volume, price, msg))

        if not sync:
            self.open_short(tick_or_bar.exchange, tick_or_bar.sec_id, price, volume)
        else:
            self.open_short_sync(tick_or_bar.exchange, tick_or_bar.sec_id, price, volume)

    def print_positions(self, ps):
        if not ps:
            return

        symbol = helper.symbol(ps)
        hold_side = "long" if ps.side == OrderSide_Bid else "short" if ps.side == OrderSide_Ask else '--'
        last_tick = self.tick(symbol)
        timestamp = last_tick.utc_time if last_tick else arrow.utcnow()

        transact_time = arrow.get(ps.transact_time).to('local')
        current_time = arrow.get(timestamp).to('local')
        ps_fields = "{} {} volume/today={:.1f}/{:.1f}, available/today = {:.1f}/{:.1f}, frozen/today = {:.1f}/{:.1f}".format(
            symbol,
            hold_side,
            ps.volume,
            ps.volume_today,
            ps.available,
            ps.available_today,
            ps.order_frozen,
            ps.order_frozen_today
        )
        ps_info_ts = "{}, last transact time: {}, current time: {}".format(ps_fields, transact_time, current_time)
        self.logger.info(ps_info_ts)

    def get_highest_lowest_price(self, symbol, start_time, end_time):
        # print(symbol)
        ## get dailybars
        hd = self.get_dailybars(symbol, start_time, end_time)

        high_prices = [b.high for b in hd]
        low_prices = [b.low for b in hd]

        return np.max(high_prices) if len(high_prices) else 0, np.min(low_prices) if len(low_prices) else float('inf')

    def get_highest_lowest_price_since_open(self, sym, init_time):
        highest_price = []
        lowest_price = []
        # 当天买入后的最高价
        local_init_time = arrow.get(init_time).to('local')
        buy_day_str_time = local_init_time.format('YYYY-MM-DD hh:mm:ss')
        buy_days_end = buy_day_str_time[:10] + ' 15:01:00'
        min_bars = self.get_bars(sym, 60, buy_day_str_time, buy_days_end)
        high_prices = [b.high for b in min_bars]
        low_prices = [b.low for b in min_bars]
        that_day_highest = np.max(high_prices) if len(high_prices) else 0
        that_day_lowest = np.min(low_prices) if len(low_prices) else float('inf')

        highest_price.append(that_day_highest)
        lowest_price.append(that_day_lowest)

        # 第二天以后至今天开盘前的最高、最低价
        now = arrow.now()
        today_begin = now.format('YYYY-MM-DD') + ' 20:59:00'
        highest, lowest = self.get_highest_lowest_price(sym, buy_days_end, today_begin)
        highest_price.append(highest)
        lowest_price.append(lowest)

        # 如果策略启动在开盘后，检查当天漏掉的行情段的最高、最低价
        exchange, sec_id = sym.split('.')
        if (exchange in ('SHSE', 'SZSE', 'CFFEX') and (15 > now.datetime.hour > 9 or (now.datetime.hour == 9 and now.datetime.minute > 30))) or \
           (exchange in ('DCE', 'CZCE', 'SHFE') and (now.datetime.hour in (21, 22, 23, 0, 1, 2) or 15 > now.datetime.hour >= 9)):
            now_str_time = now.format('YYYY-MM-DD hh:mm:ss')
            min_bars = self.get_bars(sym, 60, today_begin, now_str_time)
            high_prices = [b.high for b in min_bars]
            low_prices = [b.low for b in min_bars]

            today_highest = np.max(high_prices) if len(high_prices) > 0 else 0
            highest_price.append(today_highest)
            today_lowest = np.min(low_prices) if len(low_prices) else float('inf')
            lowest_price.append(today_lowest)

        return np.max(highest_price) if len(highest_price) else 0, np.min(lowest_price) if len(lowest_price) else 0

    def close_old_positions(self, tick, min_pnl, minutes=1):
        symbol = helper.symbol(tick)
        self.logger.debug("try to close old positions for {} ...".format(symbol))
        a_p, b_p = self.query_positions(tick.exchange, tick.sec_id)

        now = arrow.get(tick.utc_time)
        price = self.last_price(helper.symbol(tick))
        mr = self.margin_ratio(tick.sec_id)
        if mr == 0:
            mr = 1.0

        if a_p and a_p.available > 0:
            create_time = arrow.get(a_p.init_time)
            time_span = now - create_time
            self.logger.debug("now = {}, create time = {}, time span {} seconds".format(now, create_time, time_span.total_seconds()))
            a_pnl = (a_p.vwap - price)/a_p.vwap/mr
            if time_span.total_seconds() > minutes * ONE_MINUTE and a_pnl < min_pnl:
                msg='Non-profit old position, short {} (pnl = {:.2f}%) aged over {:.4f} > {} minutes'.format(symbol, a_pnl*100.0, time_span.total_seconds()/60.0, minutes)
                self.close_short_position(a_p, msg=msg)
                self.clear_trade_counter(symbol, OrderSide_Ask)

            if self.follow_trends and symbol in self.trends:
                trend = self.trends.get(symbol)
                if trend.elapsed_seconds_since_stopped(a_p.side, now) > minutes * ONE_MINUTE:
                    msg='{} short (pnl = {:.2f}%), trend {} stopped over {} minutes'.format(symbol, a_pnl*100.0, trend, minutes)
                    self.close_short_position(a_p, msg=msg)
                    self.clear_trade_counter(symbol, OrderSide_Ask)

        if b_p and b_p.available > 0:
            create_time = arrow.get(b_p.init_time)
            time_span = now - create_time
            self.logger.debug("now = {}, create time = {}, time span {} seconds".format(now, create_time, time_span.total_seconds()))
            b_pnl = (price - b_p.vwap)/b_p.vwap/mr
            if time_span.total_seconds() > minutes * ONE_MINUTE and b_pnl < min_pnl:
                msg='Non-profit old position, long {} (pnl = {:.2f}%) aged over {:.4f} > {} minutes'.format(symbol, b_pnl*100.0, time_span.total_seconds()/60.0, minutes)
                self.close_long_position(b_p, msg=msg)
                self.clear_trade_counter(symbol, OrderSide_Bid)

            if self.follow_trends and symbol in self.trends:
                trend = self.trends.get(symbol)
                if trend.elapsed_seconds_since_stopped(b_p.side, now) > minutes * ONE_MINUTE:
                    msg='{} long (pnl = {:.2f}%), trend {} stopped over {} minutes'.format(symbol, b_pnl*100.0, trend, minutes)
                    self.close_long_position(b_p, msg=msg)
                    self.clear_trade_counter(symbol, OrderSide_Bid)

    # 仓位管理，关注持仓的最高收益，用价差变动比例表示
    def care_positions_for_symbol(self, symbol, a_p, b_p, highest_price=None, lowest_price=None, act=True):
        if self.analyse_only:
            return

        if symbol == 'SHSE.000001':
            return

        self.logger.debug("{} pos long: {} vwap: {:.2f}, pos short: {}, vwap: {:.2f}".format(symbol, b_p.volume if b_p else 0.0,
                                                                                     b_p.vwap if b_p else 0.0,
                                                                                     a_p.volume if a_p else 0.0,
                                                                                     a_p.vwap if a_p else 0.0))
        mr = self.margin_ratio(symbol)
        a_key = self.__pos_key(symbol, OrderSide_Ask)
        if a_p:
            price = self.last_price(symbol) if not lowest_price else lowest_price
            if not a_key in self.highest_pnl:
                self.highest_pnl[a_key] = 0
            if price > 0:
                self.highest_pnl[a_key] = max((a_p.vwap - price)/a_p.vwap/mr, self.highest_pnl[a_key])
        else:
            self.highest_pnl[a_key] = 0

        b_key = self.__pos_key(symbol, OrderSide_Bid)
        if b_p:
            price = self.last_price(symbol) if not highest_price else highest_price
            if not b_key in self.highest_pnl:
                self.highest_pnl[b_key] = 0
            if price > 0:
                self.highest_pnl[b_key] = max((price - b_p.vwap)/b_p.vwap/mr, self.highest_pnl[b_key])
        else:
            self.highest_pnl[b_key] = 0

        if act:
            self.try_stop_action(symbol, a_p, b_p)
        else:
            self.logger.debug("No action to try stopping position ... ")

    # 出场信号逻辑，停止持仓
    def try_stop_action(self, symbol, a_p, b_p):
        trends = self.trends.get(symbol) or Trends()

        if symbol == 'SHSE.000001':
            return

        self.logger.debug("{} trends {}, short volume {}, long volume {}".format(symbol, trends, a_p.volume if a_p else 0, b_p.volume if b_p else 0))

        long_trend = trends.long_trend()
        short_trend = trends.short_trend()
        moving_long = trends.moving_long()
        moving_short = trends.moving_short()

        stop_profit_threshold = self.stop_profit_threshold
        stop_lose_threshold = self.stop_lose_threshold
        threshold = self.threshold

        last_tick = self.tick(symbol)
        last_price = self.last_price(symbol)

        mr = self.margin_ratio(symbol)
        tick_size = self.tick_size(symbol)

        # 多仓
        if b_p and b_p.volume > 0 and b_p.available > 0:
            # price_base = helper.get_oppsite_price(last_tick, OrderSide_Ask)
            b_key = self.__pos_key(symbol, OrderSide_Bid)
            if b_key not in self.highest_pnl:
                self.highest_pnl[b_key] = 0
            highest_pnl = self.highest_pnl[b_key]
            b_pnl = (last_price - b_p.vwap)/b_p.vwap/mr

            self.logger.debug("long {} current pnl = {:.2f}%, highest pnl = {:.2f}%".format(symbol, b_pnl*100.0, highest_pnl*100.0))

            # 触发止损阈值，或趋势不再继续
            if self.stop_lose and b_pnl < -stop_lose_threshold:
                msg = "lose threshold reached ({:.2f}% <= -{:.2f}%), stop lose, close long...".format(b_pnl*100.0, stop_lose_threshold*100.0)
                # ord_price = price_base - self.hops * tick_size
                ord_price = helper.aggressive_oppsite_price(last_tick, OrderSide_Ask, self.hops, tick_size)
                self.close_long_position(b_p, ord_price=ord_price, msg=msg)
                self.clear_trade_counter(symbol, OrderSide_Bid)
            if self.positive_stop and self.follow_trends and not long_trend and moving_short:  # or (moving_short and momentum_side == OrderSide_Ask):
                msg = "long trends stopped, close long..."
                # ord_price = price_base - self.hops * tick_size
                ord_price = helper.aggressive_oppsite_price(last_tick, OrderSide_Ask, self.hops, tick_size)
                self.close_long_position(b_p, ord_price=ord_price, msg=msg)
                self.clear_trade_counter(symbol, OrderSide_Bid)
            # 触发最大回撤阈值
            if self.positive_stop and threshold < b_pnl <= (1 - self.drawdown) * highest_pnl:
                msg = "pnl draw down (pnl = {:.2f}%, highest pnl = {:.2f}%), stop profit, close long...".format(b_pnl*100.0, highest_pnl*100.0)
                # ord_price = price_base - self.hops * tick_size
                ord_price = helper.aggressive_oppsite_price(last_tick, OrderSide_Ask, self.hops, tick_size)
                self.close_long_position(b_p, ord_price=ord_price, msg=msg)
                self.clear_trade_counter(symbol, OrderSide_Bid)
            # 触发固定止赢
            if self.positive_stop and b_pnl >= stop_profit_threshold:
                # ord_price = price_base + self.hops * tick_size
                ord_price = helper.aggressive_oppsite_price(last_tick, OrderSide_Ask, -self.hops, tick_size)
                msg = "take fixed earning ({:.2f}% >= {:.2f}%), stop profit, close long...".format(b_pnl*100.0, stop_profit_threshold*100.0)
                self.close_long_position(b_p, ord_price=ord_price, msg=msg)
                self.clear_trade_counter(symbol, OrderSide_Bid)

        # 空仓
        if a_p and a_p.volume > 0 and a_p.available > 0:
            # price_base = helper.get_oppsite_price(last_tick, OrderSide_Bid)
            a_key = self.__pos_key(symbol, OrderSide_Ask)
            if a_key not in self.highest_pnl:
                self.highest_pnl[a_key] = 0
            highest_pnl = self.highest_pnl[a_key]
            a_pnl = -1.0 * (last_price - a_p.vwap)/a_p.vwap/mr
            self.logger.debug("short {} current pnl = {:.2f}%, highest pnl = {:.2f}%".format(symbol, a_pnl*100.0, highest_pnl*100.0))
            # 触发止损阈值
            if self.stop_lose and a_pnl < - stop_lose_threshold:
                msg = "lose threshold reached ({:.2f}% <= -{:.2f}%), stop lose, close short...".format(a_pnl*100.0, stop_lose_threshold*100.0)
                # ord_price = price_base + self.hops * tick_size
                # if ord_price > last_tick.upper_limit:
                #     ord_price = last_tick.upper_limit
                ord_price = helper.aggressive_oppsite_price(last_tick, OrderSide_Bid, self.hops, tick_size)
                self.close_short_position(a_p, ord_price=ord_price, msg=msg)
                self.clear_trade_counter(symbol, OrderSide_Ask)
            # 趋势不再继续
            if self.positive_stop and self.follow_trends and not short_trend and moving_long:  # or (moving_long and momentum_side == OrderSide_Bid):
                msg = "short trends stopped, close short..."
                # ord_price = price_base + self.hops * tick_size
                ord_price = helper.aggressive_oppsite_price(last_tick, OrderSide_Bid, self.hops, tick_size)
                self.close_short_position(a_p, ord_price=ord_price, msg=msg)
                self.clear_trade_counter(symbol, OrderSide_Ask)
            # 触发最大回撤阈值
            if self.positive_stop and threshold < a_pnl <= (1 - self.drawdown) * highest_pnl:
                msg = "pnl draw down (pnl = {:.2f}%, highest pnl = {:.2f}%), stop profit, close short...".format(a_pnl*100.0, highest_pnl*100.0)
                # ord_price = price_base + self.hops * tick_size
                ord_price = helper.aggressive_oppsite_price(last_tick, OrderSide_Bid, self.hops, tick_size)
                self.close_short_position(a_p, ord_price=ord_price, msg=msg)
                self.clear_trade_counter(symbol, OrderSide_Ask)
            # 触发固定止赢
            if self.positive_stop and a_pnl >= stop_profit_threshold:
                msg = "take fixed earning ({:.2f}% >= {:.2f}%), stop profit, close short...".format(a_pnl*100.0, stop_profit_threshold*100.0)
                # ord_price = price_base - self.hops * tick_size
                ord_price = helper.aggressive_oppsite_price(last_tick, OrderSide_Bid, -self.hops, tick_size)
                self.close_short_position(a_p, ord_price=ord_price, msg=msg)
                self.clear_trade_counter(symbol, OrderSide_Ask)

    def query_positions(self, exchange, sec_id):
        a_p = self.short_position(exchange, sec_id)
        b_p = self.long_position(exchange, sec_id)
        return a_p, b_p

    def long_position(self, exchange, sec_id):
        k = self.__position_key(exchange, sec_id, OrderSide_Bid)
        if self.positions and k in self.positions:
            self.logger.debug("return cached long position {}.{}".format(exchange, sec_id))
            return self.positions[k]

        ps = self.get_position(exchange, sec_id, OrderSide_Bid)
        if ps:
            self.logger.debug("return by get_position long position {}.{}".format(exchange, sec_id))
        return ps

    def short_position(self, exchange, sec_id):
        k = self.__position_key(exchange, sec_id, OrderSide_Ask)
        if self.positions and k in self.positions:
            self.logger.debug("return cached short position {}.{}".format(exchange, sec_id))
            return self.positions[k]

        ps = self.get_position(exchange, sec_id, OrderSide_Ask)
        if ps:
            self.logger.debug("return by get_position short position {}.{}".format(exchange, sec_id))
        return ps

    def update_positions(self, order):
        k = self.__position_key(order.exchange, order.sec_id, order.side)
        if order.position_effect == PositionEffect_Open:
            side = order.side
        else:
            side = OrderSide_Bid + OrderSide_Ask - order.side

        # depend on SDK
        ## FIXME
        # if order.exchange in ('SZSE', 'SHSE'):
        side = order.side
        p = self.get_position(order.exchange, order.sec_id, side)
        if not p:
            self.logger.debug("get position returned None for {}.{}__{}".format(order.exchange, order.sec_id, side))
        self.positions[k] = p

    def detect_moving(self, momentum_side, momentum, moving_down_sma, moving_up_sma, s_l_ma_delta, sma_diff):
        moving_short = moving_long = False
        if (momentum_side == OrderSide_Bid or moving_up_sma
            or (sma_diff * momentum > 0 and momentum > self.momentum_factor * s_l_ma_delta)):
            moving_long = True
        elif (momentum_side == OrderSide_Ask or moving_down_sma
              or (sma_diff * momentum > 0 and momentum < self.momentum_factor * s_l_ma_delta)):
            moving_short = True

        return moving_long, moving_short

    def ma_trends(self, close, last_price, momentum_side=0):
        if len(close) < self.life_timeperiod:
            return 0, 0

        sma = SMA(close, timeperiod=self.short_timeperiod)
        lma = SMA(close, timeperiod=self.long_timeperiod)  ## make sure last lma is a number
        life = SMA(close, timeperiod=self.life_timeperiod)

        s_l_ma_delta = sma[-1] - lma[-1]  ## 最新的短长MA差值
        last_ma = sma[-1]  ## 最新的短MA
        momentum = last_price - sma[-1]  ## 当前价格相对MA冲量
        sma_diff = sma[-1] - sma[-2]
        sma_diff_1 = sma[-2] - sma[-3]
        moving_up_sma = last_price > sma[-1]
        moving_down_sma = last_price < sma[-1]
        moving_up_lma = last_price > lma[-1]
        moving_down_lma = last_price < lma[-1]
        moving = sma_diff * sma_diff_1 > 0

        if not moving:
            ## 短MA变动趋势，true表示进入趋势，false表示震荡
            moving_long = moving_short = False
        else:
            moving_long, moving_short = self.detect_moving(momentum_side, momentum, moving_down_sma,
                                                           moving_up_sma, s_l_ma_delta, sma_diff)
        ## 均线是多头还是空头排列
        speed_up = (close[-1] - sma[-1]) >= (sma[-1] - lma[-1]) > (lma[-1] - life[-1])
        long_trends = (sma[-1] > lma[-1] > life[-1]) and speed_up
        decrease_up = (sma[-1] - close[-1]) >= (lma[-1] - sma[-1]) > (life[-1] - lma[-1])
        short_trends = (sma[-1] < lma[-1] < life[-1]) and decrease_up

        self.logger.debug(
            'short ma: {:.4f}, long ma: {:.4f}, life line: {:.4f}, len of close = {}'.format(sma[-1], lma[-1], life[-1], len(close)))
        self.logger.debug(
            'short long ma delta: {:.4f}, last_ma: {:.4f}, momentum: {:.4f}'.format(s_l_ma_delta, last_ma, momentum))
        self.logger.debug(
            '### short ma moving: {}, Trends is : {}.'.format('up' if moving_long else 'down' if moving_short else '--',
                                                             'long' if long_trends else 'short' if short_trends else '--'))

        if long_trends:
            trend = OrderSide_Bid
        elif short_trends:
            trend = OrderSide_Ask
        else:
            trend = 0

        if moving_long:
            moving_dir = OrderSide_Bid
        elif moving_short:
            moving_dir = OrderSide_Ask
        else:
            moving_dir = 0

        return trend, moving_dir

    def order_pct(self, exchange, sec_id, side, percentage=100):
        pass

    def process_positions(self, tick):
        symbol = helper.symbol(tick)
        a_p, b_p = self.query_positions(tick.exchange, tick.sec_id)

        # FIXME ignore ticks before 9:25, or no trade happened
        if tick.last_volume > 0:  # and not stock_bidding_time(tick.utc_time):
            self.care_positions_for_symbol(symbol, a_p, b_p, tick.last_price, tick.last_price)

        if self.position_aging and self.positive_stop:
            self.close_old_positions(tick, self.stop_lose_threshold, minutes=self.position_retire_age)

    def calc_trends(self, bar):
        symbol = helper.symbol(bar)

        if symbol == 'SHSE.000001':
            return

        close = self.close(symbol, bar.bar_type)
        self.logger.debug("check trends for {}, frequency: {}".format(symbol, bar.bar_type))
        if len(close) < self.life_timeperiod:
            self.logger.info('Cannot calculate life ma for {}, data not enough! len = {}'.format(symbol, len(close)))
            return

        self.__calc_trends_by_close(close, symbol)

    def __calc_trends_by_close(self, close, symbol):
        trend, moving_dir = self.ma_trends(close, self.last_price(symbol))
        if symbol in self.trends:
            trd = self.trends[symbol]
            trd.append(trend, moving_dir)
        else:
            self.trends[symbol] = Trends()

    def long_trends(self, symbol):
        if symbol in self.trends:
            trd = self.trends.get(symbol)
            return trd.current_trend() == OrderSide_Bid

        return False

    def short_trends(self, symbol):
        if symbol in self.trends:
            trends = self.trends.get(symbol)
            return trends.current_trend() == OrderSide_Ask

        return False

    def trend_changed(self, symbol):
        if symbol in self.trends:
            return self.trends.get(symbol).trend_changed()

        return False

    # return True, filtered long order
    def long_trend_filtering(self, symbol):
        return not self.follow_trends or (self.follow_trends and not self.short_trends(symbol))

    # return True, filtered short order
    def short_trend_filtering(self, symbol):
        return not self.follow_trends or (self.follow_trends and not self.long_trends(symbol))

    def position_increase(self, sym, frequency):
        p = self.position(sym, frequency)
        pos = [float(i) for i in p]
        if len(pos) < self.life_timeperiod:
            self.logger.error("no enough position data for {}, len = {}".format(sym, len(pos)))
            return False

        positions = np.asarray(pos)
        ma_pos = SMA(positions, timeperiod=self.life_timeperiod)
        return p[-1] > p[-2]

    def position_decrease(self, sym, frequency):
        p = self.position(sym, frequency)
        pos = [float(i) for i in p]
        if len(pos) < self.life_timeperiod:
            self.logger.error("no enough position data for {}, len = {}".format(sym, len(pos)))
            return False

        positions = np.asarray(pos)
        ma_pos = SMA(positions, timeperiod=self.life_timeperiod)
        return p[-1] < p[-2]

    def position_filtering(self, sym, frequency):
        exchange, sec_id = sym.split(".")
        # ignore if stock
        if exchange in ('SZSE', 'SHSE') or not self.use_position_filter:
            return True

        reverse = self.trend_changed(sym) and self.position_decrease(sym, frequency)
        follow = (not self.trend_changed(sym)) and self.position_increase(sym, frequency)

        return follow or reverse

    def calc_vol(self, bar, side):
        act = 'Buy/Long' if side == OrderSide_Bid else 'Sell/Short'
        cash = self.get_cash() or Cash()

        # decide shares
        amount = cash.nav * self.high_position_ratio * self.stock_weight
        if amount < self.lowest_cash_limit:
            self.logger.info("{} {}.{} aborted, allow {:.2f} less than cash lowest limit {:.2f}"
                             .format(act, bar.exchange, bar.sec_id, amount, self.lowest_cash_limit))
            return 0

        # 最高仓位：现设为85%. 判断可用资金比例是否会低于15％ (1 - 0.85), 则仓位超限
        if cash.available - amount < cash.nav * (1.0 - self.high_position_ratio):
            self.logger.info("{} {}.{} aborted, cash left will be {:.2f}, may exceed position limit {:.2f}%"
                             .format(act, bar.exchange, bar.sec_id, cash.available - amount, self.high_position_ratio * 100.0))
            return 0

        price = self.get_oppsite_price(bar, side)
        if not price > 0:
            price = bar.close

        ml = self.multiplier(bar.sec_id)
        # no leverage for future trading if remove_leverage
        mr = self.margin_ratio(bar.sec_id) if not self.remove_leverage else 1.0
        if side == OrderSide_Bid:   # buy
            if bar.exchange in ('SHSE', 'SZSE'):
                volume = int(amount/price/self.lot)*self.lot  ## get lot, then shares
            else:
                volume = int(amount/(price*ml*mr))
        else:
            if bar.exchange in ('SHSE', 'SZSE'):
                volume = 0          # don't short stock A shares
            else:
                volume = int(amount/(price*ml*mr))

        return volume

