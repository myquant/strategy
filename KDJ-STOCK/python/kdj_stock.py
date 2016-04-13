#!/usr/bin/env python
# encoding: utf-8

import sys
import logging
import logging.config
import ConfigParser
import csv
import numpy as np
import datetime
import talib
from gmsdk import *

eps = 1e-6

class KDJ_STOCK(StrategyBase): 
    cls_config = None
    cls_user_name = None
    cls_password = None
    cls_mode = None
    cls_td_addr = None
    cls_strategy_id = None
    cls_subscribe_symbols = None
    cls_stock_pool = []
    
    
    cls_backtest_start = None
    cls_backtest_end = None
    cls_initial_cash = 1000000
    cls_transaction_ratio = 1
    cls_commission_ratio = 0.0
    cls_slippage_ratio = 0.0
    cls_price_type = 1
    cls_bench_symbol = None
    
    
    def __init__( self, *args, **kwargs ):
        super(KDJ_STOCK, self).__init__(*args, **kwargs)
        self.cur_date = None
        self.dict_adj = {}
        self.dict_high = {}
        self.dict_low = {}
        self.dict_close = {}
        self.dict_price = {}
        self.dict_openlong_signal = {}
    
    
    @classmethod
    def read_ini(cls, ini_name ):
        """
        功能：读取策略配置文件
        """
        cls.cls_config = ConfigParser.ConfigParser()
        cls.cls_config.read( ini_name )


    @classmethod
    def get_strategy_conf( cls ):
        """
        功能：读取策略配置文件strategy段落的值
        """
        if cls.cls_config is None:
            return
        
        cls.cls_user_name = cls.cls_config.get('strategy', 'username')
        cls.cls_password = cls.cls_config.get('strategy', 'password')
        cls.cls_strategy_id = cls.cls_config.get('strategy', 'strategy_id')
        cls.cls_subscribe_symbols = cls.cls_config.get('strategy', 'subscribe_symbols')  
        cls.cls_mode = cls.cls_config.getint('strategy', 'mode')
        cls.cls_td_addr = cls.cls_config.get('strategy', 'td_addr')        
        if len(cls.cls_subscribe_symbols) <=0 :
            cls.get_subscribe_stock()
        else :
            subscribe_ls = cls.cls_subscribe_symbols.split(',')
            for data in subscribe_ls:
                index1 = data.find('.')
                index2 = data.find('.', index1+1, -1)
                cls.cls_stock_pool.append(data[:index2])
        return 
    
    
    @classmethod
    def get_backtest_conf( cls ):
        """
        功能：读取策略配置文件backtest段落的值
        """
        if cls.cls_config is None:
            return
        
        cls.cls_backtest_start = cls.cls_config.get('backtest', 'start_time')
        cls.cls_backtest_end = cls.cls_config.get('backtest', 'end_time')
        cls.cls_initial_cash = cls.cls_config.getfloat('backtest', 'initial_cash')
        cls.cls_transaction_ratio = cls.cls_config.getfloat('backtest', 'transaction_ratio')
        cls.cls_commission_ratio = cls.cls_config.getfloat('backtest', 'commission_ratio')
        cls.cls_slippage_ratio = cls.cls_config.getfloat('backtest', 'slippage_ratio')
        cls.cls_price_type = cls.cls_config.getint('backtest', 'price_type')
        cls.cls_bench_symbol = cls.cls_config.get('backtest', 'bench_symbol')
        
        return
        
        
    @classmethod
    def get_stock_pool(cls, csv_file ):
        """
        功能：获取股票池中的代码
        """   
        csvfile = file( csv_file, 'rb')
        reader = csv.reader(csvfile)
        for line in reader:
            cls.cls_stock_pool.append(line[0])  
            
        return
    
    
    @classmethod
    def get_subscribe_stock( cls ):
        """
        功能：获取订阅代码
        """
        cls.get_stock_pool( 'stock_pool.csv' )
        bar_type_str = '.bar.' + '%d'%cls.cls_config.getint('para', 'bar_type')
        cls.cls_subscribe_symbols = ','.join(data + bar_type_str for data in cls.cls_stock_pool)
        return
        
        
    def get_para_conf( self ):
        """
        功能：读取策略配置文件para(自定义参数)段落的值
        """
        if self.cls_config is None:
            return
        
        self.fastk_period = self.cls_config.getint('para', 'fastk_period')
        self.slowk_period = self.cls_config.getint('para', 'slowk_period')
        self.slowk_matype = self.cls_config.getint('para', 'slowk_matype')
        self.slowd_period = self.cls_config.getint('para', 'slowd_period')
        self.slowd_matype = self.cls_config.getint('para', 'slowd_matype')
        self.slowk_bid = self.cls_config.getint('para', 'slowk_bid')
        self.slowk_sell = self.cls_config.getint('para', 'slowk_sell')
        self.slowd_bid = self.cls_config.getint('para', 'slowd_bid')
        self.slowd_sell = self.cls_config.getint('para', 'slowd_sell')      
        self.hist_size = self.cls_config.getint('para', 'hist_size')
        self.openlong_signal = self.cls_config.getint('para', 'openlong_signal')
        self.open_vol = self.cls_config.getint('para', 'open_vol')
        
        return
            
            
    def init_strategy(self):
        """
        功能：策略启动初始化操作
        """
        if self.cls_mode == gm.MD_MODE_PLAYBACK:
            self.cur_date = self.cls_backtest_start
            self.end_date = self.cls_backtest_end
        else:
            self.cur_date = datetime.date.today().strftime('%Y-%m-%d') + ' 08:00:00'
            self.end_date = datetime.date.today().strftime('%Y-%m-%d') + ' 16:00:00'
          
        self.dict_openlong_signal = {}   
        
        self.init_data()
        return
    
    
    
    def init_data(self):
        """
        功能：获取订阅代码的初始化数据
        """        
        for ticker in self.cls_stock_pool:
            daily_bars = self.get_last_n_dailybars(ticker, self.hist_size, self.cur_date)
            if len(daily_bars) <= 0:
                continue
            
            end_daily_bars = self.get_last_n_dailybars(ticker, 1, self.end_date)
            if len(end_daily_bars) <= 0:
                continue
            
            end_adj_factor = end_daily_bars[0].adj_factor                
            high_ls = [data.high * data.adj_factor/end_adj_factor for data in daily_bars]
            high_ls.reverse()
            low_ls = [data.low * data.adj_factor/end_adj_factor for data in daily_bars]
            low_ls.reverse()            
            cp_ls = [data.close * data.adj_factor/end_adj_factor for data in daily_bars]
            cp_ls.reverse()
            
            
            slowk, slowd = talib.STOCH(high = np.asarray(high_ls),
                                       low = np.asarray(low_ls),
                                       close = np.asarray(cp_ls),
                                       fastk_period= self.fastk_period, 
                                       slowk_period = self.slowk_period,
                                       slowk_matype = self.slowk_matype,
                                       slowd_period = self.slowd_period,
                                       slowd_matype = self.slowd_matype)
            
            
            #留出一个空位存储当天的一笔数据
            high_ls.append(-1)
            high = np.asarray(high_ls)
            low_ls.append(-1)
            low = np.asarray(low_ls)
            cp_ls.append(-1)
            close = np.asarray(cp_ls)
            
            #存储历史的high low close
            self.dict_price.setdefault( ticker, [high, low, close])
            
            #初始化买多信号字典
            self.dict_openlong_signal.setdefault(ticker, 0)
            
     
    def on_bar(self, bar):
        if self.cls_mode == gm.MD_MODE_PLAYBACK:           
            if bar.strtime[0:10] != self.cur_date[0:10]:
                self.cur_date = bar.strtime[0:10] + ' 08:00:00'
                #新的交易日
                self.init_data( )  
                
        symbol = bar.exchange + '.'+ bar.sec_id
        if self.dict_price.has_key( symbol ):
            nlen = len(self.dict_price[symbol][0])
            self.dict_price[symbol][0][nlen-1] = bar.high
            self.dict_price[symbol][1][nlen-1] = bar.low
            self.dict_price[symbol][2][nlen-1] = bar.close
        
            slowk, slowd = talib.STOCH(high = self.dict_price[symbol][0],
                                       low = self.dict_price[symbol][1],
                                       close = self.dict_price[symbol][2],
                                       fastk_period= self.fastk_period, 
                                       slowk_period = self.slowk_period,
                                       slowk_matype = self.slowk_matype,
                                       slowd_period = self.slowd_period,
                                       slowd_matype = self.slowd_matype)
            
            if slowk[-1] < self.slowk_bid or slowd[-1] < self.slowd_bid:
                #self.dict_openlong_signal[symbol] += 1
                #if self.dict_openlong_signal[symbol] == self.openlong_signal :
                self.open_long(bar.exchange, bar.sec_id, 0, self.open_vol)
                logging.info('open long, symbol:%s, time:%s '%(symbol, bar.strtime) )
                print 'open long, symbol:%s, time:%s '%(symbol, bar.strtime)
            elif slowk[-1] > self.slowk_sell or slowd[-1] > self.slowd_sell:
                pos = self.get_position( bar.exchange, bar.sec_id, OrderSide_Bid)
                if pos is not None:
                    vol = pos.volume - pos.volume_today
                    if vol > 0 :
                        self.open_short(bar.exchange, bar.sec_id, 0, vol)
                        logging.info( 'open short, symbol:%s, time:%s '%(symbol, bar.strtime) )
                        print 'open short, symbol:%s, time:%s '%(symbol, bar.strtime)
        
            
if __name__=='__main__':
    print get_version()
    cur_date = datetime.date.today().strftime('%Y%m%d')
    log_file = 'kdj_stock' + cur_date + '.log'
    logging.config.fileConfig('kdj_stock.ini')
    KDJ_STOCK.read_ini('kdj_stock.ini')
    KDJ_STOCK.get_strategy_conf()
    
    kdj_stock = KDJ_STOCK( username = KDJ_STOCK.cls_user_name, 
                             password = KDJ_STOCK.cls_password,
                             strategy_id = KDJ_STOCK.cls_strategy_id,
                             subscribe_symbols = KDJ_STOCK.cls_subscribe_symbols,
                             mode = KDJ_STOCK.cls_mode,
                             td_addr = KDJ_STOCK.cls_td_addr)
    
    if KDJ_STOCK.cls_mode == gm.MD_MODE_PLAYBACK:
        KDJ_STOCK.get_backtest_conf()
        ret = kdj_stock.backtest_config(start_time = KDJ_STOCK.cls_backtest_start , 
                               end_time = KDJ_STOCK.cls_backtest_end, 
                               initial_cash = KDJ_STOCK.cls_initial_cash, 
                              transaction_ratio = KDJ_STOCK.cls_transaction_ratio, 
                              commission_ratio = KDJ_STOCK.cls_commission_ratio, 
                              slippage_ratio= KDJ_STOCK.cls_slippage_ratio, 
                              price_type= KDJ_STOCK.cls_price_type, 
                              bench_symbol= KDJ_STOCK.cls_bench_symbol )

    kdj_stock.get_para_conf()
    kdj_stock.init_strategy()
    ret = kdj_stock.run()

    print 'run result %s'%ret
    