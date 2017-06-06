from __future__ import division
from gmsdk import *
import sys
import arrow

md.init("", "")      # 输入用户名、密码

def TGP(start_time, end_time, r):
    import arrow
    import pandas as pd
    import numpy as np
    #获取全市场股票代码
    e = ['SHSE', 'SZSE']
    for f in e:
        if f == 'SHSE':
            all_stocks = md.get_instruments(f, 1, 1)
            all_stocks_symbol1 = [b.symbol for b in all_stocks]  # 获取沪市全部股票代码
        if f == 'SZSE':
            all_stocks = md.get_instruments(f, 1, 1)
            all_stocks_symbol2 = [b.symbol for b in all_stocks]  # 获取深市全部股票代码
    all_stocks_symbol = all_stocks_symbol1 + all_stocks_symbol2


    code = []
    time1 = []
    for stock in all_stocks_symbol:
        a = md.get_dailybars(str(stock), start_time + ' 00:00:00', end_time + ' 00:00:00') #获取指定时间日线数据
        close_daily = [bar.close for bar in a] #获取日线收盘价
        time = [bar.utc_time for bar in a]     #获取日线时间戳

        AU1 = pd.Series(close_daily)            #将日线收盘价存为Series
        AU2 = pd.Series(close_daily).shift(3)   #向前移动三格，得到对应时间点三天前的收盘价

        AU = np.array(AU1) / np.array(AU2)      #相除得到三天的涨幅序列，使用numpy加速运算
        rr = ((r / 100) + 1)          #参数处理，例如输入筛选涨幅为20%， rr = 20/100 + 1 = 1.2

        AU[0:3] = 0                   #数据处理，将NaN赋值为0
        if len(AU[AU >= rr]) > 0:     # 如果三天的涨幅序列中有大于等于要求涨幅的情况
            index2 = time[np.where(AU >= rr)[0][0]]             #得到第一次出现满足条件的时间戳
            time_happen = arrow.get(index2).to('local')        #时间戳格式转换
            time_happen = time_happen.format('YYYY-MM-DD')    #保留 YYYY-MM-DD 部分
            code.append(stock)                                 #记录股票代码
            time1.append(time_happen)                          #记录第一次满足条件时间

    time1 = pd.DataFrame(time1,columns=['time'])      #转换为DataFrame
    code = pd.DataFrame(code, columns=['code'])       #转换为DataFrame
    result = pd.concat([code, time1], axis=1)         #合并两列
    result.to_csv('growth.csv')                      #存为 csv 文件

if __name__ == '__main__':          #程序启动入口
    if len(sys.argv) == 1:           #如果输入参数为 1，则执行默认参数配置
        print ("query last 30 days active stocks, over 20% ...")
        fmt = 'YYYY-MM-DD'
        current = arrow.now()             #当前时间
        old = current.replace(days=-30)   #30天前时间
        st = old.format(fmt)
        et = current.format(fmt)
        r = 20.0
    elif len(sys.argv) < 4:        #如果输入参数小于4，输出参数格式提示
        print "please give start / end date (not included), threshold in percentage, for example: " + sys.argv[0] + ' 2015-12-30' + ' 2016-04-30' + '20.'
        sys.exit()
    else:                          # 如果输入参数不为 1
        st = sys.argv[1]            #输入起始时间
        et = sys.argv[2]            #输入结束时间
        r = int(sys.argv[3])        #输入涨幅要求

    TGP(st, et, r)
