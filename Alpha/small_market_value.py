# !/usr/bin/env python
# -*- coding: utf-8 -*-
from Alpha import Alpha

'''
请在Strategy中修改个人账号密码和策略ID
'''

class Strategy(Alpha):
    def __init__(self, *args, **kwargs):
        super(Strategy, self).__init__(*args, **kwargs)
        self.md.subscribe('SHSE.000300.bar.60')  # 订阅一个symbol，在交易时间触发下单

    def initialize(self):
        # region 获取沪深300中当天可交易的股票
        instruments1 = self.get_instruments('SHSE', 1, 1)
        instruments2 = self.get_instruments('SZSE', 1, 1)
        symbol_list1 = set(instrument.symbol for instrument in instruments2 + instruments1)  # 获取当日可交易的股票，剔除B股
        constituents = self.get_constituents('SHSE.000300')
        symbol_list2 = set(constituent.symbol for constituent in constituents)  # 获取沪深300成分股（剔除ST、*ST股票，以及上市时间不足3个月等股票后剩余的股票）
        symbol_list = symbol_list1 & symbol_list2
        symbol_list = ','.join(symbol for symbol in symbol_list)
        # endregion

        # region 选出市值最小的5只
        market_index = self.get_last_market_index(symbol_list)
        data = [mi for mi in market_index]
        data = sorted(data, key=lambda mi: mi.market_value)[:5]  # 市值最小的5只
        # endregion

        # region 为了计算仓位，获取昨日dailybar，存入buy_dict
        buy_list = ','.join(d.symbol for d in data)
        dailybars = self.get_last_dailybars(buy_list)
        self.buy_dict = {dailybar.sec_id: dailybar for dailybar in dailybars}
        # endregion


    def handle_data(self):
        # region 没有持仓时直接open_long
        print(self.buy_dict.keys())
        positions = self.get_positions()
        if len(positions) == 0:
            cash = self.get_cash()
            for b in self.buy_dict.values():
                vol = int(cash.available * 0.95 / len(self.buy_dict) / b.close / 100) * 100
                self.open_long(b.exchange, b.sec_id, 0, vol)
            return
        # endregion

        # region 有持仓时结合持仓获取buy_dict，sell_dict
        for p in positions:
            if p.sec_id in self.buy_dict:
                self.buy_dict.pop(p.sec_id)
            else:
                self.sell_dict[p.sec_id] = p
        # endregion

        for p in self.sell_dict.values():  # 先卖出,卖盘成交时再买入，若资金足够也可以直接买入
            self.close_long(p.exchange, p.sec_id, 0, p.volume)

    def on_order_status(self, order):
        pass

if __name__ == '__main__':
    my_strategy = Strategy(
        username='username',  # 请修改账号
        password='password',  # 请修改密码
        strategy_id='strategy_id',  # 请修改策略ID
        mode=2,
        td_addr='localhost:8001')
    ret = my_strategy.run()
    print('exit code: ', ret)
