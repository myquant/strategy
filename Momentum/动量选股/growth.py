from __future__ import division
from gmsdk import *
import sys
import arrow

md.init("41089496@qq.com", "41089496")

def TGP(start_time, end_time, r):


    import arrow
    import pandas as pd
    import numpy as np
    e = ['SHSE', 'SZSE']
    for f in e:
        if f == 'SHSE':
            all_stocks = md.get_instruments(f, 1, 1)
            all_stocks_symbol1 = [b.symbol for b in all_stocks]
        if f == 'SZSE':
            all_stocks = md.get_instruments(f, 1, 1)
            all_stocks_symbol2 = [b.symbol for b in all_stocks]
    all_stocks_symbol = all_stocks_symbol1 + all_stocks_symbol2
    code = []
    time1 = []

    for stock in all_stocks_symbol:

        a = md.get_dailybars(str(stock), start_time + ' 00:00:00', end_time + ' 00:00:00')
        close_daily = [bar.close for bar in a]
        time = [bar.utc_time for bar in a]
        # close_daily.reverse()
        # time.reverse()

        AU1 = pd.Series(close_daily)
        AU2 = pd.Series(close_daily).shift(3)

        AU = np.array(AU1) / np.array(AU2)
        rr = ((r / 100.0) + 1)
        AU[0:3] = 0

        if len(AU[AU >= rr]) > 0:
            index2 = time[np.where(AU >= rr)[0][0]]
            time_happen = arrow.get(index2).to('local')
            time_happen = time_happen.format('YYYY-MM-DD')
            code.append(stock)
            time1.append(time_happen)

    time1 = pd.DataFrame(time1,columns=['time'])
    code = pd.DataFrame(code, columns=['code'])
    result = pd.concat([code, time1], axis=1)
    result.to_csv('growth.csv')

if __name__ == '__main__':
    if len(sys.argv) == 1:
        print ("query last 30 days active stocks, over 25% ...")
        fmt = 'YYYY-MM-DD'
        now = arrow.now()
        current = now.replace(days=1)
        old = now.replace(days=-30) # month ago
        st = old.format(fmt)
        et = current.format(fmt)
        r = 25.0
    elif len(sys.argv) < 4:
        print "please give start / end date (not included), threshold in percentage, for example: " + sys.argv[0] + ' 2015-12-30' + ' 2016-04-30' + '20.'
        sys.exit()
    else:
        st = sys.argv[1]
        et = sys.argv[2]
        r = int(sys.argv[3])

    TGP(st, et, r)
