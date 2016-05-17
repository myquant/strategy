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
import arrow
import time
from gmsdk import *

EPS = 1e-6

INIT_LOW_PRICE = 10000000
INIT_HIGH_PRICE = -1 
INIT_CLOSE_PRICE = 0


class ADX_DMI_STOCK(StrategyBase): 
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
        super(ADX_DMI_STOCK, self).__init__(*args, **kwargs)
        self.cur_date = None
        self.dict_adj = {}
        self.dict_high = {}
        self.dict_low = {}
        self.dict_close = {}
        self.dict_price = {}
        self.dict_openlong_signal = {}
        self.dict_entry_high_low={}  
        self.dict_last_factor={}
    
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
        bar_type = cls.cls_config.getint('para', 'bar_type')
        if 86400 == bar_type:
            bar_type_str = '.bar.' + 'daily'
        else:
            bar_type_str = '.bar.' + '%d'%cls.cls_config.getint('para', 'bar_type')
            
        cls.cls_subscribe_symbols = ','.join(data + bar_type_str for data in cls.cls_stock_pool)
        return
        
        
    @classmethod
    def utc_strtime( utc_time ):
        """
        功能：utc转字符串时间
        """
        str_time = '%s'%arrow.get(pos.init_time).to('local')
        str_time.replace('T', ' ')
        str_time = str_time.replace('T', ' ')
        return str_time[:19]
    
    
    def get_para_conf( self ):
        """
        功能：读取策略配置文件para(自定义参数)段落的值
        """
        if self.cls_config is None:
            return
        
        self.adx_period = self.cls_config.getint('para', 'adx_period')
        self.dmi_period = self.cls_config.getint('para', 'dmi_period')
        self.ma_short_period = self.cls_config.getint('para', 'ma_short_period')
        self.ma_long_period = self.cls_config.getint('para', 'ma_long_period') 
        self.hist_size = self.cls_config.getint('para', 'hist_size')
        self.open_vol = self.cls_config.getint('para', 'open_vol')
        
        self.is_fixation_stop = self.cls_config.getint('para', 'is_fixation_stop')
        self.stop_fixation_profit = self.cls_config.getfloat('para', 'stop_fixation_profit')
        self.stop_fixation_loss = self.cls_config.getfloat('para', 'stop_fixation_loss')
        
        self.is_movement_stop = self.cls_config.getint('para', 'is_movement_stop')
        self.profit_ratio = self.cls_config.getfloat('para', 'profit_ratio')
        self.stop_movement_profit = self.cls_config.getfloat('para', 'stop_movement_profit')
        self.loss_ratio = self.cls_config.getfloat('para', 'loss_ratio')
        self.stop_movement_loss = self.cls_config.getfloat('para', 'stop_movement_loss')
        
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
        self.dict_entry_high_low = {}
        self.get_last_factor()
        self.init_data()
        self.init_entry_high_low()
        return
    
    
    def init_data(self):
        """
        功能：获取订阅代码的初始化数据
        """  
        #start = time.clock()
        
        for ticker in self.cls_stock_pool:
            #初始化买多信号字典
            self.dict_openlong_signal.setdefault(ticker, False)            

            daily_bars = self.get_last_n_dailybars(ticker, self.hist_size - 1, self.cur_date)
            if len(daily_bars) <= 0:
                continue
            
            end_daily_bars = self.get_last_n_dailybars(ticker, 1, self.end_date)
            if len(end_daily_bars) <= 0:
                continue
            
            if not self.dict_last_factor.has_key(ticker):
                continue
            
            end_adj_factor = self.dict_last_factor[ticker]              
            high_ls = [data.high * data.adj_factor/end_adj_factor for data in daily_bars]
            high_ls.reverse()
            low_ls = [data.low * data.adj_factor/end_adj_factor for data in daily_bars]
            low_ls.reverse()            
            cp_ls = [data.close * data.adj_factor/end_adj_factor for data in daily_bars]
            cp_ls.reverse()
            
            
            #留出一个空位存储当天的一笔数据
            high_ls.append(INIT_HIGH_PRICE)
            high = np.asarray(high_ls )
            low_ls.append(INIT_LOW_PRICE)
            low = np.asarray(low_ls)
            cp_ls.append(INIT_CLOSE_PRICE)
            close = np.asarray(cp_ls )
            
            #存储历史的high low close
            self.dict_price.setdefault( ticker, [high, low, close])
       
        #end = time.clock()
        #logging.info('init_data cost time: %f s' % (end - start))
        
    
    def init_data_newday( self ): 
        """
        功能：新的一天初始化数据
        """ 
        #新的一天，去掉第一笔数据,并留出一个空位存储当天的一笔数据
        for key in self.dict_price:
            if len(self.dict_price[key][0]) >= self.hist_size and self.dict_price[key][0][-1] > INIT_HIGH_PRICE:
                #logging.info('init_data_newday begin high len: %s, data: %s'%(len(self.dict_price[key][0]), self.dict_price[key][0]))
                self.dict_price[key][0] = np.append(self.dict_price[key][0][1:], INIT_HIGH_PRICE)
                #logging.info('init_data_newday end high len: %s, data: %s'%(len(self.dict_price[key][0]), self.dict_price[key][0]))
                
            if len(self.dict_price[key][1]) >= self.hist_size and self.dict_price[key][1][-1] < INIT_LOW_PRICE:
                #logging.info('init_data_newday begin low len: %s, data: %s'%(len(self.dict_price[key][1]),self.dict_price[key][1]))
                self.dict_price[key][1] = np.append(self.dict_price[key][1][1:], INIT_LOW_PRICE)
                #logging.info('init_data_newday end low len: %s, data: %s'%(len(self.dict_price[key][1]), self.dict_price[key][1]))                 
                
            if len(self.dict_price[key][2]) >= self.hist_size and abs(self.dict_price[key][2][-1] - INIT_CLOSE_PRICE) > EPS:
                #logging.info('init_data_newday begin close len: %s, data: %s'%(len(self.dict_price[key][2]),self.dict_price[key][2]))
                self.dict_price[key][2] = np.append(self.dict_price[key][2][1:], INIT_CLOSE_PRICE)
                #logging.info('init_data_newday end close len: %s, data: %s'%(len(self.dict_price[key][2]), self.dict_price[key][2]))  
         
                
        #初始化买多信号字典
        for key in self.dict_openlong_signal:
            self.dict_openlong_signal.setdefault(key, False) 
            

    def get_last_factor(self):
        """
        功能：获取最新的复权因子
        """
        for ticker in self.cls_stock_pool:
            daily_bars = self.get_last_n_dailybars(ticker, 1, self.end_date )            
            self.dict_last_factor.setdefault(ticker, daily_bars[0].adj_factor)
               


    def init_entry_high_low( self ):
        """
        功能：获取进场后的最高价和最低价,仿真或实盘交易启动时加载
        """
        pos_list = self.get_positions()
        high_list = []
        low_list = []
        for pos in pos_list:
            symbol = pos.exchange + '.' + pos.sec_id 
            init_time = self.utc_strtime( pos.init_time)
           
            cur_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
            daily_bars = self.get_dailybars(symbol, init_time, cur_time)
            
            high_list = [bar.high for bar in daily_bars]            
            low_list = [bar.low for bar in daily_bars]
        
            highest = np.max( high_list )
            lowest = np.min( low_list)
            
            self.dict_entry_high_low.setdefault(symbol, highest, lowest ) 
                        
    
    def on_bar(self, bar):
        if self.cls_mode == gm.MD_MODE_PLAYBACK:           
            if bar.strtime[0:10] != self.cur_date[0:10]:
                self.cur_date = bar.strtime[0:10] + ' 08:00:00'
                #新的交易日
                #self.init_data( )  
                self.init_data_newday()
                
        symbol = bar.exchange + '.'+ bar.sec_id
            
        self.movement_stop_profit_loss(bar)
        self.fixation_stop_profit_loss(bar)
        
        if self.dict_openlong_signal[symbol] == True:
            #当天已开仓，则不再开仓
            return 
        
        if self.dict_price.has_key( symbol ):
            if self.dict_price[symbol][0][-1] < bar.high:
                self.dict_price[symbol][0][-1] = bar.high
                
            if self.dict_price[symbol][1][-1] > bar.low:
                self.dict_price[symbol][1][-1] = bar.low
  
            self.dict_price[symbol][2][-1] = bar.close
            
            high = self.dict_price[symbol][0]
            if len( high ) < self.hist_size:
                #logging.warn('high data is not enough, symbol: %s, data: %s'%(symbol, high))
                return
            
            low = self.dict_price[symbol][1]
            if len( low ) < self.hist_size:
                #logging.warn('low data is not enough, symbol: %s, data: %s'%(symbol, low))
                return
            
            close = self.dict_price[symbol][2]
            if len( close ) < self.hist_size:
                #logging.warn('low data is not enough, symbol: %s, data: %s'%(symbol, close))
                return            
            
            adx = talib.ADX( high, low, close, timeperiod = self.adx_period )
            
            plus_di = talib.PLUS_DI(high, low, close, timeperiod = self.dmi_period)
            
            minus_di = talib.MINUS_DI(high, low, close, timeperiod = self.dmi_period)
            
            short_ma = talib.SMA(close, timeperiod = self.ma_short_period)
            
            long_ma = talib.SMA(close, timeperiod = self.ma_long_period)
            
            if short_ma[-1] > long_ma[-1] and short_ma[-2] < long_ma[-2] and adx[-1] > adx[-2] and plus_di[-1] > minus_di[-1]:
                self.open_long(bar.exchange, bar.sec_id, bar.close, self.open_vol)
                self.dict_openlong_signal[symbol] = True                
                logging.info('open long, symbol:%s, time:%s, price:%.2f'%(symbol, bar.strtime, bar.close) )
                
            if short_ma[-1] < long_ma[-1] and short_ma[-2] > long_ma[-2] and adx[-1] < adx[-2] and plus_di[-1] < minus_di[-1]:
                pos = self.get_position( bar.exchange, bar.sec_id, OrderSide_Bid)
                if pos is not None:
                    vol = pos.volume - pos.volume_today
                    if vol > 0 :
                        self.close_long(bar.exchange, bar.sec_id, bar.close, vol)
                        logging.info( 'close long, symbol:%s, time:%s, price:%.2f'%(symbol, bar.strtime, bar.close) )
        
        
    def on_order_filled(self, order):
        symbol = order.exchange + '.' + order.sec_id
        if order.side == OrderSide_Ask:
            pos = self.get_position(order.exchange, order.sec_id)
            if 0 == pos.volume:
                self.dict_entry_high_low.pop(symbol)
                
                
    def fixation_stop_profit_loss(self, bar):
        """
        功能：固定止盈、止损,盈利或亏损超过了设置的比率则执行止盈、止损
        """
        if self.is_fixation_stop == 0:
            return
        
        symbol = bar.exchange + '.' + bar.sec_id 
        pos = self.get_position(bar.exchange, bar.sec_id, OrderSide_Bid)
        if pos is not None:
            if pos.fpnl > 0 and pos.fpnl/pos.cost >= self.stop_fixation_profit:
                self.close_long(bar.exchange, bar.sec_id, 0, pos.volume - pos.volume_today)
                logging.info('fixnation stop profit: close long, symbol:%s, time:%s, price:%.2f, volume:%s'%(symbol, 
                                bar.strtime, bar.close, pos.volume) )   
            elif pos.fpnl < 0 and pos.fpnl/pos.cost <= -1 * self.stop_fixation_profit:
                self.close_long(bar.exchange, bar.sec_id, 0, pos.volume - pos.volume_today) 
                logging.info('fixnation stop loss: close long, symbol:%s, time:%s, price:%.2f, volume:%s'%(symbol, 
                                bar.strtime, bar.close, pos.volume))
    
        
        
    def movement_stop_profit_loss(self, bar):
        """
        功能：移动止盈、止损, 移动止盈止损按进场后的最高价、最低价乘以设置的比率与当前价格相比，
              并且盈亏比率达到设定的盈亏比率时，执行止盈止损
        """
        if self.is_movement_stop == 0:
            return 
        
        entry_high = None
        entry_low = None
        pos = self.get_position(bar.exchange, bar.sec_id, OrderSide_Bid)
        symbol = bar.exchange + '.' + bar.sec_id
        
        is_stop_profit = True
        is_stop_loss = True
        
        if pos is not None:
            if self.dict_entry_high_low.has_key( symbol):
                if self.dict_entry_high_low[symbol][0] < bar.close:
                    self.dict_entry_high_low[symbol][0] = bar.close
                    is_stop_profit = False
                elif self.dict_entry_high_low[symbol][1] > bar.close:
                    self.dict_entry_high_low[symbol][1] = bar.close
                    is_stop_loss = False
                [entry_high, entry_low] = self.dict_entry_high_low[symbol]
                
            else:
                self.dict_entry_high_low.setdefault(symbol, [bar.close, bar.close])
                [entry_high, entry_low] = self.dict_entry_high_low[symbol]   
                is_stop_loss = False
                is_stop_profit = False
                
            if is_stop_profit and bar.close > pos.vwap:
                #移动止盈
                if bar.close < (1 - self.stop_movement_profit) * entry_high and pos.fpnl/pos.cost >= self.profit_ratio:
                    if pos.volume - pos.volume_today > 0:
                        self.close_long(bar.exchange, bar.sec_id, 0, pos.volume - pos.volume_today)
                        logging.info('movement stop profit: close long, symbol:%s, time:%s, price:%.2f, volume:%s'%(symbol, bar.strtime, bar.close, pos.volume) )
                        #print 'stop profit: close long, symbol:%s, time:%s '%(symbol, bar.strtime)        
                
                if bar.close > entry_high:
                    self.dict_entry_high_low[symbol][0] = bar.close 
                    
            elif is_stop_loss and bar.close < pos.vwap:
                #移动止损
                if bar.close > (1 + self.stop_movement_loss) * entry_low and pos.fpnl/pos.cost <= -1 * self.loss_ratio:
                    if pos.volume - pos.volume_today > 0:
                        self.close_long(bar.exchange, bar.sec_id, 0, pos.volume - pos.volume_today) 
                        logging.info('movement stop loss: close long, symbol:%s, time:%s, price:%.2f, volume:%s'%(symbol, bar.strtime, bar.close, pos.volume) )
                        #print 'stop loss: close long, symbol:%s, time:%s '%(symbol, bar.strtime)  
                        
                if bar.close < entry_low:
                    self.dict_entry_high_low[symbol][1] = bar.close                     
            
            
        
if __name__=='__main__':
    print get_version()
    logging.config.fileConfig('adx_dmi_stock.ini')
    ADX_DMI_STOCK.read_ini('adx_dmi_stock.ini')
    ADX_DMI_STOCK.get_strategy_conf()
    
    adx_dmi_stock = ADX_DMI_STOCK( username = ADX_DMI_STOCK.cls_user_name, 
                             password = ADX_DMI_STOCK.cls_password,
                             strategy_id = ADX_DMI_STOCK.cls_strategy_id,
                             subscribe_symbols = ADX_DMI_STOCK.cls_subscribe_symbols,
                             mode = ADX_DMI_STOCK.cls_mode,
                             td_addr = ADX_DMI_STOCK.cls_td_addr)
    
    if ADX_DMI_STOCK.cls_mode == gm.MD_MODE_PLAYBACK:
        ADX_DMI_STOCK.get_backtest_conf()
        ret = adx_dmi_stock.backtest_config(start_time = ADX_DMI_STOCK.cls_backtest_start , 
                               end_time = ADX_DMI_STOCK.cls_backtest_end, 
                               initial_cash = ADX_DMI_STOCK.cls_initial_cash, 
                              transaction_ratio = ADX_DMI_STOCK.cls_transaction_ratio, 
                              commission_ratio = ADX_DMI_STOCK.cls_commission_ratio, 
                              slippage_ratio= ADX_DMI_STOCK.cls_slippage_ratio, 
                              price_type= ADX_DMI_STOCK.cls_price_type, 
                              bench_symbol= ADX_DMI_STOCK.cls_bench_symbol )

    adx_dmi_stock.get_para_conf()
    adx_dmi_stock.init_strategy()
    ret = adx_dmi_stock.run()

    print 'run result %s'%ret
    