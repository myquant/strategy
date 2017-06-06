# encoding: utf-8

import csv

from gmsdk import *
from gmsdk import OrderSide_Bid, OrderSide_Ask
from abc import abstractmethod

from .context import Context
from .ta_indicator_mixin import TAMixin
from .order_mixin import OrderMixin
from .pos_mixin import PositionMixin
from .volume_mixin import VolumeMixin
from . import helper


class FakeTick(object):
    """
     to speed up backtest, construct tick data from bar

    """
    def __init__(self):
        self.exchange = ''
        self.sec_id = ''
        self.last_volume = 0
        self.last_price = 0.0
        self.utc_time = 0.0
        self.bids = []
        self.asks = []
        self.lower_limit = 0.0
        self.upper_limit = 0.0

    def __init__(self, bar):
        self.exchange = bar.exchange
        self.sec_id = bar.sec_id
        self.last_price = bar.close
        self.last_volume = bar.volume
        self.utc_time = bar.utc_time
        self.bids = [(bar.close, 0)]
        self.asks = [(bar.close, 0)]
        self.lower_limit = bar.low
        self.upper_limit = bar.high


class TAStrategy(StrategyBase, TAMixin, PositionMixin, OrderMixin, VolumeMixin):
    def __init__(self, *args, **kwargs):
        # print("init TA Strategy Base ...")
        super(TAStrategy, self).__init__(*args, **kwargs)
        # super().__init__(*args, **kwargs)
        # print("init TA strategy Base end")

    def init(self, config=None):
        if config is not None:
            self.config = config

        self.__algo__func = None
        self.__read_para__()

        super(TAStrategy, self).init_context()
        super(TAStrategy, self).init_order_mixin()
        super(TAStrategy, self).init_position_mixin()
        super(TAStrategy, self).init_volume_mixin()

        self.__init_data__()

        super(TAStrategy, self).calc_history_data()

    def __read_para__(self):
        super(TAStrategy, self).__read_para__()

        self.mode = self.config.getint('strategy', 'mode')
        self.backtest_use_tick = self.config.getboolean('backtest', 'use_tick')

        self.csv_file = self.config.get('para', 'csv_file')
        self.bar_type = self.config.get('para', 'bar_type')
        self.lot = self.config.getint('para', 'lot')

        try:
            self.window_size = self.config.getint('para', 'window_size')
        except:
            self.window_size = 50

        try:
            self.analyse_only = self.config.getboolean('para', 'analyse_only')
        except:
            self.analyse_only = False

    def __init_data__(self):
        '''
        read stocks from csv file
        :return:
        '''

        csv_file = self.csv_file

        subscribe_symbols, symbols = self.prepare_subscribe_symbols(csv_file)

        sub_suffix = "daily" if self.bar_type == '1d' else str(self.bar_type)

        ps = self.get_positions()
        for p in ps:
            sym = ".".join([p.exchange, p.sec_id])
            symbols.append(sym)

            if self.mode in (2,3) or self.backtest_use_tick:
                subscribe_symbols.append(sym + ".tick")
            subscribe_symbols.append("{}.bar.{}".format(sym, sub_suffix))   ## bar according to configured bar_type

        for p in ps:
            highest_price, lowest_price = self.get_highest_lowest_price_since_open(sym, p.init_time)
            b_p = p if p.side == OrderSide_Bid else None
            a_p = p if p.side == OrderSide_Ask else None
            self.care_positions_for_symbol(sym, a_p, b_p, highest_price, lowest_price, act=False)

        self.history_data(symbols, self.bar_type, self.window_size)

        subscribe_symbols.append("SHSE.000001.tick")   ## 上证指数

        subscribe_symbols.append("SHSE.000001.bar.{}".format(sub_suffix))   ## bar according to configured bar_type

        self.logger.info("subscribe symbols: {}".format(subscribe_symbols))

        ## subscribe
        self.subscribe(",".join(subscribe_symbols))

    def prepare_subscribe_symbols(self, csv_file):
        symbols = []
        subscribe_symbols = []
        sub_suffix = "daily" if self.bar_type == '1d' else str(self.bar_type)

        with open(csv_file, 'r') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                t = row[0]
                symbols.append(t)
                # exchange, sec_id = t.split(".")

                if self.mode in (2, 3) or self.backtest_use_tick:
                    subscribe_symbols.append(t + ".tick")
                subscribe_symbols.append("{}.bar.{}".format(t, sub_suffix))  ## bar according to configured bar_type
        return subscribe_symbols, symbols

    def set_algo(self, algo_func):
        self.__algo__func = algo_func

    # 所有成交回报, 包括订单状态变化，撤单拒绝等，可以忽略，只处理如下面关心的订单状态变更信息
    def on_execrpt(self, execution):
        self.logger.debug("received execution: exec_type = {}, detail: {}".format(execution.exec_type, to_dict(execution)))
        self.handle_exerpt(execution)

    # def on_order_status(self, order):
    #     self.logger.debug("received order status: exec_type = {}, detail = {} {} status {}".format(order.order_type,  order.sec_id, order.side, order.status))
    #     self.handler_order_status(order)

    # 订单被接受
    def on_order_new(self, order):
        self.logger.info('''
        received order new: sec_id: {}, side: {}, position effect: {}, volume: {:.0f}, price: {:.2f}, cl_ord_id: {}
        '''.format(order.sec_id, order.side, order.position_effect, order.volume, order.price, order.cl_ord_id))
        self.handle_order_new(order)
        self.update_positions(order)

    # 订单部分成交
    def on_order_partially_filled(self, order):
        self.logger.info('''
          received order partially filled: sec_id: {}, side: {}, position effect: {}, volume: {}, filled price: {:.3f}, filled: {}
          '''.format(order.sec_id, order.side, order.position_effect, order.volume, order.filled_vwap, order.filled_volume))
        self.handle_order_partially_filled(order)
        self.update_positions(order)

    # 订单完全成交
    def on_order_filled(self, order):
        self.logger.info('''
        received order filled: sec_id: {}, side: {}, position effect: {}, volume: {}, filled price: {:.3f}, filled: {}
        '''.format(order.sec_id, order.side, order.position_effect, order.volume, order.filled_vwap, order.filled_volume))
        self.handle_order_filled(order)
        self.update_positions(order)

    def on_order_cancelled(self, order):
        self.logger.info('''
        received order cancelled {}: sec_id: {}, side: {}, position effect: {}, volume: {}, price: {:.3f}, filled: {}
        '''.format(order.cl_ord_id, order.sec_id, order.side, order.position_effect, order.volume, order.price, order.filled_volume))
        self.handle_order_cancelled(order)
        self.update_positions(order)

    def on_order_cancel_rejected(self, execrpt):
        self.logger.info('''
        received execrpt cancel rejected {}: sec_id: {}, side: {}, position effect: {}, price: {:.3f}, volume: {}
        '''.format(execrpt.cl_ord_id, execrpt.sec_id, execrpt.side, execrpt.position_effect, execrpt.price, execrpt.volume))
        self.handle_order_cancel_rejected(execrpt)
        self.update_positions(execrpt)

    # 订单被拒绝
    def on_order_rejected(self, execrpt):
        self.logger.info('''
        received order rejected {}, sec_id: {}, side: {}, position effect: {}, volume: {}, price: {:.3f}, reason: {}
        '''.format(execrpt.cl_ord_id, execrpt.sec_id, execrpt.side, execrpt.position_effect, execrpt.volume, execrpt.price, execrpt.ord_rej_reason_detail))
        self.handle_order_rejected(execrpt)
        self.update_positions(execrpt)

    def is_closing(self, ps):
        side = OrderSide_Ask + OrderSide_Bid - ps.side
        return self.has_open_order(ps.exchange, ps.sec_id, side)

    def on_tick(self, tick):
        self.logger.debug("received tick {} {}.{}: last price {:.2f} last vol {}, bid 1 {:.2f}, ask 1 {:.2f}".format(
            tick.strtime,
            tick.exchange,
            tick.sec_id,
            tick.last_price,
            tick.last_volume,
            helper.bid_price_1(tick),
            helper.ask_price_1(tick)))
        self.update_ticks(tick)
        sym = self.get_symbol(tick)

        if sym != 'SHSE.000001':  # ignore index
            self.process_positions(tick)
            self.care_orders(tick, self.hold_minutes)

        if sym == 'SHSE.000001' and 'stock' in self.csv_file:
            if tick.last_price < tick.pre_close:
                self.high_position_ratio = 0.25
            elif tick.last_price > tick.pre_close:
                self.high_position_ratio = 0.85

    def on_bar(self, bar):
        self.logger.debug("received bar: {} -- {}.{}  close: {}, volume: {}".format(
            bar.strtime, bar.exchange, bar.sec_id, bar.close, bar.volume))

        # use bar data to construct a fake tick
        if self.mode == 4 and not self.backtest_use_tick:
            fake_tick = FakeTick(bar)

            self.update_ticks(fake_tick)

            if self.get_symbol(fake_tick) != 'SHSE.000001':  # ignore index
                self.process_positions(fake_tick)

        self.append_bar(bar)
        symbol = self.get_symbol(bar)
        self.calc_trends(bar)

        if symbol == 'SHSE.000001':
            return

        if helper.reach_time_limit(bar):
            print("Forbidden to use, please contact us to continue!")
            return

        if self.__algo__func:
            self.__algo__func(self, bar)

    ## algo inside class
    #
    # def algo(self, bar):
    #     symbol = self.get_symbol(bar)
    #     cci = self.cci(symbol, bar.bar_type)
    #     if len(cci) < 1:
    #         return
    #
    #     if self.cross_up(cci, 100) or self.cross_up(cci, -100):
    #         bid_price = self.get_oppsite_price(bar, OrderSide_Bid)
    #         vol = self.calc_vol(bar, OrderSide_Bid)
    #         if vol == 0:
    #             return
    #         self.open_long(bar.exchange, bar.sec_id, bid_price, vol)
    #     elif self.cross_down(cci, 100) or self.cross_down(cci, -100):
    #         ps = self.get_position(bar.exchange, bar.sec_id, OrderSide_Bid)
    #         if ps and ps.available_yesterday > 0:
    #             ask_price = self.get_oppsite_price(bar, OrderSide_Ask)
    #             self.close_long(bar.exchange, bar.sec_id, ask_price, ps.available_yesterday)
    #     else:
    #         pass

    @abstractmethod
    def algo(self, bar):
        pass

    def open_long(self, exchange, sec_id, price, volume):
        symbol = helper.symbol_combine(exchange, sec_id)
        if not self.long_trend_filtering(symbol):
            self.logger.info("trend filtered, now {} trend is short, ignore open long order {}@{:.2f}".format(symbol, volume, price))
            return

        if not self.position_filtering(symbol, self.bar_type):
            self.logger.info("position filtered, ignore open long order {} {}@{:.2f}".format(symbol, volume, price))
            return

        super(TAStrategy, self).open_long(exchange, sec_id, price, volume)

    def open_short(self, exchange, sec_id, price, volume):
        symbol = helper.symbol_combine(exchange, sec_id)
        if not self.short_trend_filtering(symbol):
            self.logger.info("trend filtered, now {} trend is long, ignore open short order {}@{:.2f}".format(symbol, volume, price))
            return

        if not self.position_filtering(symbol, self.bar_type):
            self.logger.info("position filtered, ignore open short order {} {}@{:.2f}".format(symbol, volume, price))
            return

        super(TAStrategy, self).open_short(exchange, sec_id, price, volume)

#
# if __name__ == '__main__':
#     ini_file = sys.argv[1] if len(sys.argv) > 1 else 'cci.ini'
#     logging.config.fileConfig(ini_file)
#
#     st = TAStrategy(config_file=ini_file)
#     st.init()
#     st.logger.info("Strategy ready, waiting for data ...")
#     ret = st.run()
#     # bt = st.get_indicator()
#     st.logger.info("Strategy message %s" % st.get_strerror(ret))
#

