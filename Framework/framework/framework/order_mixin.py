#encoding: utf-8

import arrow
from gmsdk import *


class OrderMixin(object):

    def __init__(self, *args, **kwargs):
        # print("init order mixin ...")
        self.__init_vars()
        # print("init order mixin end")

    def __init_vars(self):
        self.open_orders = {}  # key: exchange.sec_id + side, value: order
        self.trade_count = {}  # key: exchange.sec_id + side, value: int
        self.cancelling_orders = {}    # key: exchange.sec_id + side, value: order

    def init_order_mixin(self):
        if not hasattr(self, 'open_orders'):
            self.__init_vars()

        self.__read_order_man_paras__()
        # self.portfolio = self.get_cash()
        self.__read_open_orders__()

    def __read_order_man_paras__(self):
        try:
            self.hold_minutes = self.config.getfloat('para', 'hold_minutes')
        except:
            self.hold_minutes = 5

    def __read_open_orders__(self):
        orders = self.get_unfinished_orders()
        for o in orders:
            self.append_order(o)

    def __order_key(self, order):
        order_key = self.__order_key__(order.exchange, order.sec_id, order.side)
        return order_key

    def __order_key__(self, exchange, sec_id, side):
        order_key = "{}.{}__{}".format(exchange, sec_id, side)
        return order_key

    def in_open_orders(self, order):
        return self.__order_key(order) in self.open_orders

    def has_open_order(self, exchange, sec_id, side):
        return self.__order_key__(exchange, sec_id, side) in self.open_orders

    def append_order(self, order):
        self.open_orders[self.__order_key(order)] = order
        self.logger.debug("after append, open orders {}".format(list(self.open_orders.keys())))

    ## 移除本地管理的已进入完成状态的订单
    def __clean_final_orders(self, order):
        self.logger.info("try to remove final order {}, {}.{} side: {} position effect: {}, {} @ {:.3f} "
                         .format(order.cl_ord_id, order.exchange, order.sec_id, order.side, order.position_effect,
                                 order.volume, order.price))
        order_key = self.__order_key(order)

        self.logger.debug("before clean, open orders {}".format(list(self.open_orders.keys())))
        if order_key in self.open_orders:
            self.logger.info("remove final order {}".format(order_key))
            self.open_orders.pop(order_key)

        self.logger.debug("after clean, open orders {}".format(list(self.open_orders.keys())))

    # 撤销未完成状态的订单
    def cancel_unfinished_orders(self, tick):
        for o in list(self.open_orders.values()):
            if o.exchange != tick.exchange or o.sec_id != tick.sec_id:
                return

            o_key = self.__order_key(o)
            if o_key in self.cancelling_orders:
                return

            self.logger.info("try to cancel order {}, {}.{} side: {} position effect: {}, {} @ {:.3f}"
                             .format(o.cl_ord_id, o.exchange, o.sec_id, o.side, o.position_effect, o.volume, o.price))
            self.mark_cancel_order(o_key, arrow.get(tick.utc_time))
            self.cancel_order(o.cl_ord_id)

    def cancel_old_orders(self, tick, minutes=5):
        if not len(self.open_orders) > 0:
            return

        self.logger.debug("try to cancel old orders ... ")

        now = arrow.get(tick.utc_time)
        for o in list(self.open_orders.values()):
            if o.exchange != tick.exchange or o.sec_id != tick.sec_id:
                continue

            o_key = self.__order_key(o)
            if self.is_just_cancelled(o_key, now):
                continue
            else:
                self.unmark_cancel_order(o_key)

            sending_time = arrow.get(o.sending_time)
            time_span = now - sending_time
            if time_span.total_seconds() > minutes * 60:
                self.logger.info("try to cancel order {}, {}.{} side: {}, position effect: {}, {} @ {:.3f},"
                                 " aged {} seconds "
                                 .format(o.cl_ord_id, o.exchange, o.sec_id, o.side, o.position_effect, o.volume, o.price,
                                         time_span.total_seconds()))
                self.mark_cancel_order(o_key, now)
                self.cancel_order(o.cl_ord_id)

    def is_just_cancelled(self, o_key, now, seconds=60):
        just_cancelled = False

        if o_key in self.cancelling_orders:
            cancel_span = now - self.cancel_order_timestamp(o_key)
            if cancel_span.total_seconds() < seconds:
                just_cancelled = True

        return just_cancelled

    def cancel_order_timestamp(self, o_key):
        if o_key in self.cancelling_orders:
            return self.cancelling_orders[o_key]

        return arrow.get(0)

    def mark_cancel_order(self, o_key, now):
        self.cancelling_orders[o_key] = now

    def unmark_cancel_order(self, o_key):
        if o_key in self.cancelling_orders:
            self.cancelling_orders.pop(o_key)

    def care_orders(self, tick, hold_minutes):
        # self.open_orders.clear()
        # self.__read_open_orders__()
        self.cancel_old_orders(tick, minutes=hold_minutes)

    def order_target(self, exchange, sec_id, target, limit_price=None, stop_price=None, style=None):
        return self.open_long(exchange, sec_id, target, limit_price)

    def order_percent(self, exchange, sec_id, percent, limit_price=None, stop_price=None, style=None):
        pass

    def order_to(self, symbol, p):
        pass

    # 所有成交回报, 包括订单状态变化，撤单拒绝等，可以忽略，只处理如下面关心的订单状态变更信息
    def handle_exerpt(self, execution):
        if execution.exec_type == ExecType_Trade: #15
            self.logger.info('''
            received execution filled: sec_id: {}, side: {}, position effect: {}, filled volume: {:.0f}, filled price: {:.3f}
            '''.format(execution.sec_id, execution.side, execution.position_effect, execution.volume, execution.price))
        elif execution.exec_type == ExecType_CancelRejected: #19
            o = Order()
            o.cl_ord_id = execution.cl_ord_id
            self.__clean_final_orders(o)

    def handler_order_status(self, order):
        pass

    # 订单被接受
    def handle_order_new(self, order):
        self.append_order(order)

    # 订单部分成交
    def handle_order_partially_filled(self, order):
        pass

    # 订单完全成交
    def handle_order_filled(self, order):
        self.__clean_final_orders(order)

    def __clean_cancelling_order(self, order):
        ord_key = self.__order_key(order)
        if ord_key in self.cancelling_orders:
            self.cancelling_orders.pop(ord_key)

    def handle_order_cancelled(self, order):
        self.logger.info("order cancelled, {}".format(to_dict(order)))
        self.__clean_final_orders(order)
        self.__clean_cancelling_order(order)

    def handle_order_cancel_rejected(self, execrpt):
        o = Order()
        o.cl_ord_id = execrpt.cl_ord_id
        o.exchange = execrpt.exchange
        o.sec_id = execrpt.sec_id
        o.side = execrpt.side
        self.__clean_final_orders(o)
        self.__clean_cancelling_order(o)

    # 订单被拒绝
    def handle_order_rejected(self, exerpt):
        pass

