# !/usr/bin/env python
# -*- coding: utf-8 -*-
from gmsdk.api import StrategyBase


class Alpha(StrategyBase):
    '''
    始终买入沪深300中市值最小的5只
    先订阅000300分钟行情（也可订阅其他symbol，只是用来作行情触发）
    第一个bar行情到来时在md_init中选股
    选出股票池与持仓作对比
    无持仓时直接按照股票池等权买入
    有持仓时，不在股票池中的股票卖出
    在成交回报on_order_filled中判断是否都已卖出，卖出仓位都成交以后再买入
    '''

    def __init__(self, *args, **kwargs):
        super(Alpha, self).__init__(*args, **kwargs)
        self.buy_dict = {}
        self.sell_dict = {}
        self.is_traded = False

    def initialize(self):
        pass

    # 收到第一根Bar后交易
    def on_bar(self, bar):
        print(bar.strtime)
        if self.is_traded:
            return
        self.is_traded = True
        self.initialize()
        self.handle_data()

    def handle_data(self):
        pass

    def on_order_filled(self, order):
        if order.sec_id in self.sell_dict and order.strategy_id == self.strategy_id:
            self.sell_dict.pop(order.sec_id)
            if len(self.sell_dict) == 0:  # 由于资金每次都开满，等卖盘全部成交资金回流时再买入
                cash = self.get_cash()
                for bar in self.buy_dict.values():
                    vol = int(cash.available * 0.95 / len(self.buy_dict) / bar.close / 100) * 100
                    self.open_long(bar.exchange, bar.sec_id, 0, vol)

