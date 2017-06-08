# encoding: utf-8

import numpy as np
import talib as ta
from .context import Context


class TAMixin(Context, object):

    def __init__(self, *args, **kwargs):
        # print("init ta indicator mixin ...")
        super(TAMixin, self).__init__(*args, **kwargs)
        # print("init ta indicator mixin end")

    # def on_bar(self, bar):
    #     self.append_bar(bar)
    #
    # def on_tick(self, tick):
    #     self.update_ticks(tick)

    ## simple interfaces


    # cross: judge if two lines cross
    # return: cross or not(True/False), up or down (True if ser1 cross up ser2 else False)
    def cross(self, ser1, ser2):
        if isinstance(ser1, (int, float)):
            ser1 = [ser1 for i in range(3)]
        if isinstance(ser2, (int, float)):
            ser2 = [ser2 for i in range(3)]

        if len(ser1) < 3 or len(ser2) < 3:
            return False, False

        return (ser1[-3] - ser2[-3]) * (ser1[-1] - ser2[-1]) < 0, ser1[-1] > ser2[-1]

    def cross_up(self, ser1, ser2):
        crossed, up = self.cross(ser1, ser2)
        return crossed and up

    def cross_down(self, ser1, ser2):
        crossed, up = self.cross(ser1, ser2)
        return crossed and not up

    ## TA functions

    def ad(self, sym, frequency):
        if not self.kbars_ready(sym, frequency):
            return []

        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)
        volumes = self.volume(sym, frequency)

        v = ta.AD(highs, lows, closes, volumes)

        return v

    def adosc(self, sym, frequency, *args, **kwargs):
        if not self.kbars_ready(sym, frequency):
            return []

        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)
        volumes = self.volume(sym, frequency)

        v = ta.ADOSC(highs, lows, closes, volumes, *args, **kwargs)

        return v

    def adx(self, sym, frequency, period=14):
        if not self.kbars_ready(sym, frequency):
            return []

        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)

        return ta.ADX(highs, lows, closes, timeperiod=period)

    def adxr(self, sym, frequency, period=14):
        if not self.kbars_ready(sym, frequency):
            return []

        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)

        return ta.ADXR(highs, lows, closes, timeperiod=period)

    def aroon(self, sym, frequency, *args, **kwargs):
        if not self.kbars_ready(sym, frequency):
            return []

        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)

        v = ta.AROON(highs, lows, *args, **kwargs)

        return v

    def aroonosc(self, sym, frequency, *args, **kwargs):
        if not self.kbars_ready(sym, frequency):
            return []

        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)

        v = ta.AROONOSC(highs, lows, *args, **kwargs)

        return v

    def avg_price(self, sym, frequency):
        if not self.kbars_ready(sym, frequency):
            return []

        opens = self.open(sym, frequency)
        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)

        v = ta.AVGPRICE(opens, highs, lows, closes)

        return v

    def dx(self, sym, frequency, *args, **kwargs):
        if not self.kbars_ready(sym, frequency):
            return []

        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)

        v = ta.DX(highs, lows, closes, *args, **kwargs)

        return v

    def med_price(self, sym, frequency):
        if not self.kbars_ready(sym, frequency):
            return []

        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)

        v = ta.MEDPRICE(highs, lows)

        return v

    def mid_price(self, sym, frequency, *args, **kwargs):
        if not self.kbars_ready(sym, frequency):
            return []

        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)

        v = ta.MIDPRICE(highs, lows, *args, **kwargs)

        return v

    def mfi(self, sym, frequency, *args, **kwargs):
        if not self.kbars_ready(sym, frequency):
            return []

        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)
        volumes = self.volume(sym, frequency)

        v = ta.MFI(highs, lows, closes, volumes, *args, **kwargs)

        return v

    def ma_close(self, sym, frequency, period=30, ma_type=0):
        if not self.kbars_ready(sym, frequency):
            return []

        closes = self.close(sym, frequency)
        ma = ta.MA(closes, timeperiod=period, matype=ma_type)

        return ma

    def sma_close(self, sym, frequency, period=30):
        if not self.kbars_ready(sym, frequency):
            return []

        closes = self.close(sym, frequency)
        ma = ta.SMA(closes, timeperiod=period)

        return ma

    def ema_close(self, sym, frequency, period=30):
        if not self.kbars_ready(sym, frequency):
            return []

        closes = self.close(sym, frequency)
        ma = ta.EMA(closes, timeperiod=period)

        return ma

    def wma_close(self, sym, frequency, period=30):
        if not self.kbars_ready(sym, frequency):
            return []

        closes = self.close(sym, frequency)
        ma = ta.WMA(closes, timeperiod=period)

        return ma

    def macd(self, sym, frequency, fast_period=12, slow_period=26, signal_period=9):
        if not self.kbars_ready(sym, frequency):
            return [], [], []

        closes = self.close(sym, frequency)

        dif, dea, macd = ta.MACD(closes,
                                 fastperiod=fast_period,
                                 slowperiod=slow_period,
                                 signalperiod=signal_period)

        return dif, dea, macd

    def kdj(self, sym, frequency, fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0):
        if not self.kbars_ready(sym, frequency):
            return [], []

        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)

        slowk, slowd = ta.STOCH(high=highs,
                                low=lows,
                                fastk_period=fastk_period,
                                close=closes,
                                slowk_period=slowk_period,
                                slowk_matype=slowk_matype,
                                slowd_period=slowd_period,
                                slowd_matype=slowd_matype)
        return slowk, slowd

    def atr(self, sym, frequency, period=14):
        if not self.kbars_ready(sym, frequency):
            return []

        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)

        atr_index = ta.ATR(highs, lows, closes, timeperiod=period)
        return atr_index

    def natr(self, sym, frequency, period=14):
        if not self.kbars_ready(sym, frequency):
            return []

        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)

        natr = ta.NATR(highs, lows, closes, timeperiod=period)
        return natr

    def boll(self, sym, frequency, period=5, nbdev_up=2, nbdev_down=2, ma_type=0):
        if not self.kbars_ready(sym, frequency):
            return [],[],[]

        closes = self.close(sym, frequency)

        upperband, middleband, lowerband = ta.BBANDS(closes, timeperiod=period,
                                                     nbdevup=nbdev_up, nbdevdn=nbdev_down, matype=ma_type)

        return upperband, middleband, lowerband

    def cci(self, sym, frequency, period=14):
        if not self.kbars_ready(sym, frequency):
            return []

        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)

        cci = ta.CCI(highs, lows, closes, timeperiod=period)

        return cci

    def bop(self, sym, frequency):
        if not self.kbars_ready(sym, frequency):
            return []

        opens = self.open(sym, frequency)
        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)

        bop = ta.BOP(opens, highs, lows, closes)

        return bop

    def cmo(self, sym, frequency, period=14):
        if not self.kbars_ready(sym, frequency):
            return []

        closes = self.close(sym, frequency)

        cmo = ta.CMO(closes, timeperiod=period)

        return cmo

    ## calculate two symbol's return correlation
    def cor(self, sym1, sym2, frequency, period=10):
        if not self.kbars_ready(sym1, frequency) or not self.kbars_ready(sym2, frequency):
            return []

        close1 = self.close(sym1, frequency)
        close2 = self.close(sym2, frequency)

        roc1 = ta.ROC(close1, timeperiod=period)
        roc2 = ta.ROC(close2, timeperiod=period)

        return ta.CORREL(roc1, roc2, timeperiod=period)

    def mom(self, sym, frequency, period=5):
        if not self.kbars_ready(sym, frequency):
            return []

        closes = self.close(sym, frequency)

        mom = ta.MOM(closes, timeperiod=period)
        return mom

    def minus_di(self, sym, frequency, *args, **kwargs):
        if not self.kbars_ready(sym, frequency):
            return []

        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)

        return ta.MINUS_DI(highs, lows, closes, *args, **kwargs)

    def minus_dm(self, sym, frequency, *args, **kwargs):
        if not self.kbars_ready(sym, frequency):
            return []

        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)

        return ta.MINUS_DM(highs, lows, *args, **kwargs)

    def plus_di(self, sym, frequency, *args, **kwargs):
        if not self.kbars_ready(sym, frequency):
            return []

        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)

        return ta.PLUS_DI(highs, lows, closes, *args, **kwargs)

    def plus_dm(self, sym, frequency, *args, **kwargs):
        if not self.kbars_ready(sym, frequency):
            return []

        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)

        return ta.PLUS_DM(highs, lows, *args, **kwargs)

    def rsi(self, sym, frequency, *args, **kwargs):
        if not self.kbars_ready(sym, frequency):
            return []

        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)

        avg_prices = (highs + lows + closes) / 3.0

        return ta.RSI(avg_prices, *args, **kwargs)

    def sar(self, sym, frequency, *args, **kwargs):
        if not self.kbars_ready(sym, frequency):
            return []

        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)

        return ta.SAR(highs, lows, *args, **kwargs)

    def sarext(self, sym, frequency, *args, **kwargs):
        if not self.kbars_ready(sym, frequency):
            return []

        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)

        return ta.SAREXT(highs, lows, *args, **kwargs)

    def ultosc(self, sym, frequency, *args, **kwargs):
        if not self.kbars_ready(sym, frequency):
            return []

        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)

        return ta.ULTOSC(highs, lows, closes, *args, **kwargs)

