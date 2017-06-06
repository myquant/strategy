# encoding: utf-8


from collections import deque
import numpy as np

from gmsdk import *
from . import helper
from . import context_util as ctx_util

class Context(object):
    def __init__(self, *args, **kwargs):
        # print("init context ...")
        self.__init_vars()
        # print("init context end")

    def __init_vars(self):
        self.k_bars = {}  # key: symbol, value: dict {open: deque, high: deque, ...}
        self.last_ticks = {}  # format is sym: Tick
        self.symbols_lookup = {}  # key: sec_id, value: exchange, sec_id, margin_ratio, multiplier

    def __init_data__(self):
        pass

    def __read_para__(self):
        pass

    def init_context(self):
        if not hasattr(self, 'k_bars'):
            self.__init_vars()

    def init_symbols_lookup(self):
        if len(self.symbols_lookup) == 0:
            self.symbols_lookup = self.all_symbols()  # key: sec_id, value: exchange, sec_id, margin_ratio, multiplier

    def quote_key(self, sym, frequency):
        return "{}__{}".format(sym, ctx_util.frequency_readable(frequency) if str(frequency).isdigit() else frequency)

    def decode_k_bars_key(self, key):
        return key.split("__")

    def kbars_ready(self, sym, frequency):
        return self.quote_key(sym, frequency) in self.k_bars

    def prepare_hist_bars(self, symbols, bar_type, window_size):
        for s in symbols:
            self.hist_bars(s, bar_type, window_size)

    def hist_bars(self, s, bar_type, window_size):
        if bar_type == '1d':
            bars = self.get_last_n_dailybars(s, window_size, end_time=self.start_time if self.mode == 4 else '')
        else:
            bar_type = int(bar_type)
            bars = self.get_last_n_bars(s, bar_type, window_size, end_time=self.start_time if self.mode == 4 else '')
        # print "{}: len = {}".format(s, len(bars))
        bars.reverse()
        k = self.quote_key(s, bar_type)
        if not self.kbars_ready(s, bar_type):
            self.k_bars[k] = {
                'datetime': deque(maxlen=window_size),
                'symbol': deque(maxlen=window_size),
                'frequency': deque(maxlen=window_size),
                'open': deque(maxlen=window_size),
                'high': deque(maxlen=window_size),
                'low': deque(maxlen=window_size),
                'close': deque(maxlen=window_size),
                'pre_close': deque(maxlen=window_size),
                'adj_factor': deque(maxlen=window_size),
                'volume': deque(maxlen=window_size),
                'position': deque(maxlen=window_size),
                'utc_time': deque(maxlen=window_size),
                'strtime': deque(maxlen=window_size),
                'strendtime': deque(maxlen=window_size),
            }
        for b in bars:
            self.k_bars[k]['datetime'].append(ctx_util.local_datetime(b.utc_time))
            self.k_bars[k]['symbol'].append(helper.symbol(b))
            self.k_bars[k]['frequency'].append(ctx_util.frequency_readable(b.bar_type))
            self.k_bars[k]['open'].append(b.open)
            self.k_bars[k]['high'].append(b.open)
            self.k_bars[k]['low'].append(b.low)
            self.k_bars[k]['close'].append(b.close)
            self.k_bars[k]['pre_close'].append(b.pre_close)
            self.k_bars[k]['adj_factor'].append(b.adj_factor)
            self.k_bars[k]['volume'].append(b.volume)
            self.k_bars[k]['position'].append(b.position)
            self.k_bars[k]['utc_time'].append(b.utc_time)
            self.k_bars[k]['strtime'].append(b.strtime)
            if hasattr(b, 'strendtime'):
                self.k_bars[k]['strendtime'].append(b.strendtime)
            else:
                self.k_bars[k]['strendtime'].append(b.strtime)

    def prepare_latest_ticks(self, symbols):
        for s in symbols:
            ticks = self.get_last_n_ticks(s, 1, end_time=self.start_time if self.mode == 4 else '')
            for t in ticks:
                self.last_ticks[self.get_symbol(t)] = t

    def history_data(self, symbols, bar_type, window_size):
        self.prepare_hist_bars(symbols, bar_type, window_size)
        self.prepare_latest_ticks(symbols)

    def history_data_single(self, symbol, bar_type, window_size):
        self.hist_bars(symbol, bar_type, window_size)
        self.prepare_latest_ticks([symbol])

    # get symbol from gm structure, such as bar, tick, order, position etc.
    def get_symbol(self, bar):
        return helper.symbol(bar)

    def open(self, sym, frequency):
        if self.kbars_ready(sym, frequency):
            _key = self.quote_key(sym, frequency)
            return np.asarray(self.k_bars[_key].get('open'))

        return []

    def high(self, sym, frequency):
        if self.kbars_ready(sym, frequency):
            _key = self.quote_key(sym, frequency)
            return np.asarray(self.k_bars[_key].get('high'))

        return []

    def low(self, sym, frequency):
        if self.kbars_ready(sym, frequency):
            _key = self.quote_key(sym, frequency)
            return np.asarray(self.k_bars[_key].get('low'))

        return []

    def close(self, sym, frequency):
        if self.kbars_ready(sym, frequency):
            _key = self.quote_key(sym, frequency)
            return np.asarray(self.k_bars[_key].get('close'))

        return []

    def volume(self, sym, frequency):
        if self.kbars_ready(sym, frequency):
            _key = self.quote_key(sym, frequency)
            return np.asarray(self.k_bars[_key].get('volume'))

        return []

    def position(self, sym, frequency):
        if self.kbars_ready(sym, frequency):
            _key = self.quote_key(sym, frequency)
            return np.asarray(self.k_bars[_key].get('position'))

        return []

    def pre_close(self, sym, frequency):
        if self.kbars_ready(sym, frequency):
            _key = self.quote_key(sym, frequency)
            return np.asarray(self.k_bars[_key].get('pre_close'))

        return []

    def adj_factor(self, sym, frequency):
        if self.kbars_ready(sym, frequency):
            _key = self.quote_key(sym, frequency)
            return np.asarray(self.k_bars[_key].get('adj_factor'))

        return []

    def frequency(self, sym, frequency):
        if self.kbars_ready(sym, frequency):
            _key = self.quote_key(sym, frequency)
            return np.asarray(self.k_bars[_key].get('frequency'))

        return []

    def datetime(self, sym, frequency):
        if self.kbars_ready(sym, frequency):
            _key = self.quote_key(sym, frequency)
            return np.asarray(self.k_bars[_key].get('datetime'))

        return []

    def utc_time(self, sym, frequency):
        if self.kbars_ready(sym, frequency):
            _key = self.quote_key(sym, frequency)
            return np.asarray(self.k_bars[_key].get('utc_time'))

        return []

    def strtime(self, sym, frequency):
        if self.kbars_ready(sym, frequency):
            _key = self.quote_key(sym, frequency)
            return np.asarray(self.k_bars[_key].get('strtime'))

        return []

    def strendtime(self, sym, frequency):
        if self.kbars_ready(sym, frequency):
            _key = self.quote_key(sym, frequency)
            return np.asarray(self.k_bars[_key].get('strendtime'))

        return []

    def append_bar(self, bar):
        symbol = self.get_symbol(bar)
        key = self.quote_key(symbol, bar.bar_type)

        if self.kbars_ready(symbol, bar.bar_type):
            self.k_bars[key]['datetime'].append(ctx_util.local_datetime(bar.utc_time))
            self.k_bars[key]['symbol'].append(helper.symbol(bar))
            self.k_bars[key]['frequency'].append(ctx_util.frequency_readable(bar.bar_type))
            self.k_bars[key]['open'].append(bar.open)
            self.k_bars[key]['high'].append(bar.high)
            self.k_bars[key]['low'].append(bar.low)
            self.k_bars[key]['close'].append(bar.close)
            self.k_bars[key]['pre_close'].append(bar.pre_close)
            self.k_bars[key]['adj_factor'].append(bar.adj_factor)
            self.k_bars[key]['volume'].append(bar.volume)
            self.k_bars[key]['position'].append(bar.position)
            self.k_bars[key]['strtime'].append(bar.strtime)
            self.k_bars[key]['strendtime'].append(bar.strendtime)
            self.k_bars[key]['utc_time'].append(bar.utc_time)
        else:
            # init error
            pass

    def pop_bar(self, sym, frequency):
        key = self.quote_key(sym, frequency)

        if self.kbars_ready(sym, frequency):
            self.k_bars[key]['datetime'].pop()
            self.k_bars[key]['symbol'].pop()
            self.k_bars[key]['frequency'].pop()
            self.k_bars[key]['open'].pop()
            self.k_bars[key]['high'].pop()
            self.k_bars[key]['low'].pop()
            self.k_bars[key]['close'].pop()
            self.k_bars[key]['pre_close'].pop()
            self.k_bars[key]['adj_factor'].pop()
            self.k_bars[key]['volume'].pop()
            self.k_bars[key]['position'].pop()
            self.k_bars[key]['utc_time'].pop()
            self.k_bars[key]['strtime'].pop()
            self.k_bars[key]['strendtime'].pop()
        else:
            # init error
            pass

    def update_ticks(self, tick):
        symbol = self.get_symbol(tick)
        if not hasattr(self, 'last_ticks'):
            self.last_ticks = {}

        self.last_ticks[symbol] = tick

    def tick(self, sym):
        return self.last_ticks.get(sym)

    def last_price(self, sym):
        tick = self.last_ticks.get(sym)
        if tick:
            return tick.last_price
        return 0

    ##  挂单价格 - 对手价买一（side = OrderSide_Ask）或卖一（side = OrderSide_Bid ）
    def get_oppsite_price(self, bar, side):
        symbol = self.get_symbol(bar)
        tick = self.last_ticks.get(symbol) if self.mode == 2 else None
        if tick:
            # self.logger.debug("last tick: {0}: Ask/Bid: {1}/{2}".format(symbol, self.ask_1(tick) if self.ask_1(tick) > 0 else '--', self.bid_1(tick) if self.bid_1(tick) > 0 else '--'))
            if side == OrderSide_Bid:  ## 1  buy
                return helper.ask_price_1(tick) if len(tick.asks) else 0.0
            if side == OrderSide_Ask:  ## 2  sell
                return helper.bid_price_1(tick) if len(tick.bids) else 0.0
        else:
            # self.logger.debug("cannot get opsite price, no tick stored for {0}: ticks {1}".format(symbol, self.last_ticks))
            # 实盘时用市价下单，回测时用k线收盘价
            price = 0.0 if self.mode == 2 else bar.close
            return price

    def all_symbols(self, is_active=False):
        symbols = {}
        sh_stocks = self.get_instruments('SHSE', 1, is_active)
        for x in sh_stocks:
            exch, sec_id = x.symbol.split('.')
            symbols[sec_id] = [exch, sec_id, x.margin_ratio, x.multiplier, x.price_tick]
        sz_stocks = self.get_instruments('SZSE', 1, is_active)
        for x in sz_stocks:
            exch, sec_id = x.symbol.split('.')
            symbols[sec_id] = [exch, sec_id, x.margin_ratio, x.multiplier, x.price_tick]
        shfe_fts = self.get_instruments('SHFE', 4, is_active)
        for x in shfe_fts:
            exch, sec_id = x.symbol.split('.')
            symbols[sec_id] = [exch, sec_id, x.margin_ratio, x.multiplier, x.price_tick]
        cffex_fts = self.get_instruments('CFFEX', 4, is_active)
        for x in cffex_fts:
            exch, sec_id = x.symbol.split('.')
            symbols[sec_id] = [exch, sec_id, x.margin_ratio, x.multiplier, x.price_tick]
        dce_fts = self.get_instruments('DCE', 4, is_active)
        for x in dce_fts:
            exch, sec_id = x.symbol.split('.')
            symbols[sec_id] = [exch, sec_id, x.margin_ratio, x.multiplier, x.price_tick]
        czce_fts = self.get_instruments('CZCE', 4, is_active)
        for x in czce_fts:
            exch, sec_id = x.symbol.split('.')
            symbols[sec_id] = [exch, sec_id, x.margin_ratio, x.multiplier, x.price_tick]

        return symbols

    def expand_symbol(self, sym):
        exchange = ''
        sec_id = ''
        if sym in self.symbols_lookup:
            xx = self.symbols_lookup[sym]
            exchange, sec_id = xx[0], xx[1]
        if sym.isdigit():
            exchange = helper.check_exchange(sym)
            sec_id = sym

        return exchange, sec_id

    def margin_ratio(self, sec_id):
        if sec_id.find('.') >= 0:
            sec_id = sec_id.split(".")[-1]

        mr = 1.0
        if sec_id in self.symbols_lookup:
            mr = self.symbols_lookup[sec_id][2]

        return mr

    def multiplier(self, sec_id):
        if sec_id.find('.') >= 0:
            sec_id = sec_id.split(".")[-1]

        ml = 1.0
        if sec_id in self.symbols_lookup:
            ml = self.symbols_lookup[sec_id][3]

        return ml

    def tick_size(self, sec_id):
        if sec_id.find('.') >= 0:
            sec_id = sec_id.split(".")[-1]

        if sec_id in self.symbols_lookup:
            ts = self.symbols_lookup[sec_id][4]
        else:
            ts = 0.01

        return ts

    def to_dataframe(self, sym=None, frequency=None):
        if sym and frequency:
            k = self.quote_key(sym, frequency)
        else:
            k = None
        return ctx_util.bar_dict_to_dataframe(self.k_bars, k)

    def ticks_to_dataframe(self, sym=None):
        if sym:
            ticks = [self.last_ticks.get(sym)]
        else:
            ticks = self.last_ticks.values()

        return ctx_util.ticks_to_dataframe(ticks)
