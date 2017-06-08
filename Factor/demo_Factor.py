# !/usr/bin/env python
# -*- coding: utf-8 -*-
from gmsdk.api import StrategyBase
'''
请在Strategy中修改个人账号密码和策略ID
'''
class Strategy(StrategyBase):
    '''
    始终买入PE最小的1000只股票中市值最小的5只
    先订阅000016分钟行情（也可订阅其他symbol，只是用来作行情触发）
    第一个bar行情到来时在md_init中选股
    选出股票池与持仓作对比
    无持仓时直接按照股票池等权买入
    有持仓时，不在股票池中的股票卖出
    在成交回报on_order_filled中判断是否都已卖出，卖出仓位都成交以后再买入
    '''
    def __init__(self, pe_len = 1000, mv_len = 5, *args, **kwargs):
        super(Strategy, self).__init__(*args, **kwargs)
        self.pe_len = pe_len
        self.mv_len = mv_len
        self.buy_dict = {}
        self.sell_dict = {}
        self.is_traded = False

        self.md.subscribe('SHSE.000016.bar.60') # 订阅一个行情，在交易时间触发下单

    def md_init(self):
# region 获取中证全指中当天可交易的股票
        instruments1 = self.get_instruments('SHSE', 1, 1)
        instruments2 = self.get_instruments('SZSE', 1, 1)
        symbol_list1 = set(instrument.symbol for instrument in instruments2 + instruments1 if instrument.symbol[5] not in ['2', '9']) #获取当日可交易的股票，剔除B股
        constituents = self.get_constituents('SHSE.000985')
        symbol_list2 = set(constituent.symbol for constituent in constituents)#获取中证全指成分股（剔除ST、*ST股票，以及上市时间不足3个月等股票后剩余的股票）
        symbol_list = symbol_list1 & symbol_list2
        symbol_list = ','.join(symbol for symbol in symbol_list)
# endregion

# region 选出PE最小的1000只中市值最小的5只
        market_index = self.get_last_market_index(symbol_list)
        data = list(mi for mi in market_index if mi.pe_ratio > 0) # 剔除PE为负的股票
        data = sorted(data, key= lambda mi: mi.pe_ratio)[:self.pe_len] # PE最小的1000只
        data = sorted(data, key= lambda mi: mi.market_value)[:self.mv_len] # 市值最小的5只
# endregion

# region 为了计算仓位，获取昨日dailybar，存入buy_dict
        buy_list = ','.join(d.symbol for d in data)
        dailybars = self.get_last_dailybars(buy_list)
        self.buy_dict = dict((dailybar.sec_id, dailybar) for dailybar in dailybars)
        # endregion

    # 收到第一根Bar后交易
    def on_bar(self, bar):
        print(bar.strendtime[:-6].replace('T', ' '))
        if self.is_traded:
            return
        self.is_traded = True
        self.md_init()

# region 没有持仓时直接open_long
        print(self.buy_dict.keys())
        positions = self.get_positions()
        if len(positions) == 0:
            cash = self.get_cash()
            for b in self.buy_dict.values():
                order = self.open_long(b.exchange, b.sec_id, 0, int(cash.available * 0.95 / len(self.buy_dict) / b.close / 100) * 100)
            return
# endregion

# region 有持仓时结合持仓获取buy_dict，sell_dict
        for p in positions:
            if p.sec_id in self.buy_dict:
                self.buy_dict.pop(p.sec_id)
            else:
                self.sell_dict[p.sec_id] = p
        # endregion

        for p in self.sell_dict.values(): # 先卖出,卖盘成交时再买入，若资金足够也可以直接买入
            self.close_long(p.exchange, p.sec_id, 0, p.volume)

    def on_order_filled(self,order):
        if order.sec_id in self.sell_dict and order.strategy_id == self.strategy_id:
            self.sell_dict.pop(order.sec_id)
            if len(self.sell_dict) == 0:#由于资金每次都开满，等卖盘全部成交资金回流时再买入
                cash = self.get_cash()
                for bar in self.buy_dict.values():
                    self.open_long(bar.exchange, bar.sec_id, 0, int(cash.available * 0.95 / len(self.buy_dict) / bar.close / 100) * 100)

if __name__ == '__main__':
    my_strategy = Strategy(
        username='username', # 请修改账号
        password='password', # 请修改密码
        strategy_id='strategy_id', # 请修改策略ID
        mode=3,
        td_addr='localhost:8001')
    ret = my_strategy.run()
    print('exit code: ', ret)
