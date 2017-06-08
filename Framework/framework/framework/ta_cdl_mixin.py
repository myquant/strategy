# encoding: utf-8

import logging
import logging.config

import numpy as np
import talib as ta
from .context import Context


class CDLMixin(Context):

    def __init__(self, *args, **kwargs):
        super(CDLMixin, self).__init__(*args, **kwargs)


    ## TA CDL functions

    def abandoned_baby(self, sym, frequency, *args, **kwargs):
        if not self.kbars_ready(sym, frequency):
            return []

        opens = self.open(sym, frequency)
        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)

        cdl = ta.CDLABANDONEDBABY(opens, highs, lows, closes, *args, **kwargs)

        return cdl

    def advanced_block(self, sym, frequency):
        if not self.kbars_ready(sym, frequency):
            return []

        opens = self.open(sym, frequency)
        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)

        cdl = ta.CDLADVANCEBLOCK(opens, highs, lows, closes)

        return cdl

    def breakaway(self, sym, frequency):
        if not self.kbars_ready(sym, frequency):
            return []

        opens = self.open(sym, frequency)
        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)

        cdl = ta.CDLBREAKAWAY(opens, highs, lows, closes)

        return cdl

    def two_crows(self, sym, frequency):
        if not self.kbars_ready(sym, frequency):
            return []

        opens = self.open(sym, frequency)
        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)

        cdl = ta.CDL2CROWS(opens, highs, lows, closes)

        return cdl

    def three_black_crows(self, sym, frequency):
        if not self.kbars_ready(sym, frequency):
            return []

        opens = self.open(sym, frequency)
        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)

        cdl = ta.CDL3BLACKCROWS(opens, highs, lows, closes)

        return cdl

    def three_inside(self, sym, frequency):
        if not self.kbars_ready(sym, frequency):
            return []

        opens = self.open(sym, frequency)
        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)

        cdl = ta.CDL3INSIDE(opens, highs, lows, closes)

        return cdl

    def three_line_strike(self, sym, frequency):
        if not self.kbars_ready(sym, frequency):
            return []

        opens = self.open(sym, frequency)
        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)

        cdl = ta.CDL3LINESTRIKE(opens, highs, lows, closes)

        return cdl

    def three_outside(self, sym, frequency):
        if not self.kbars_ready(sym, frequency):
            return []

        opens = self.open(sym, frequency)
        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)

        cdl = ta.CDL3OUTSIDE(opens, highs, lows, closes)

        return cdl

    def three_stars_in_south(self, sym, frequency):
        if not self.kbars_ready(sym, frequency):
            return []

        opens = self.open(sym, frequency)
        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)

        cdl = ta.CDL3STARSINSOUTH(opens, highs, lows, closes)

        return cdl

    def three_white_soldiers(self, sym, frequency):
        if not self.kbars_ready(sym, frequency):
            return []

        opens = self.open(sym, frequency)
        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)

        cdl = ta.CDL3WHITESOLDIERS(opens, highs, lows, closes)

        return cdl

    def belt_hold(self, sym, frequency):
        if not self.kbars_ready(sym, frequency):
            return []

        opens = self.open(sym, frequency)
        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)

        cdl = ta.CDLBELTHOLD(opens, highs, lows, closes)

        return cdl

    def closing_marubozu(self, sym, frequency):
        if not self.kbars_ready(sym, frequency):
            return []

        opens = self.open(sym, frequency)
        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)

        cdl = ta.CDLCLOSINGMARUBOZU(opens, highs, lows, closes)

        return cdl

    def conceal_baby_swall(self, sym, frequency):
        if not self.kbars_ready(sym, frequency):
            return []

        opens = self.open(sym, frequency)
        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)

        cdl = ta.CDLCONCEALBABYSWALL(opens, highs, lows, closes)

        return cdl

    def counter_attack(self, sym, frequency):
        if not self.kbars_ready(sym, frequency):
            return []

        opens = self.open(sym, frequency)
        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)

        cdl = ta.CDLCOUNTERATTACK(opens, highs, lows, closes)

        return cdl

    def doji(self, sym, frequency):
        if not self.kbars_ready(sym, frequency):
            return []

        opens = self.open(sym, frequency)
        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)

        cdl = ta.CDLDOJI(opens, highs, lows, closes)

        return cdl

    def doji_star(self, sym, frequency):
        if not self.kbars_ready(sym, frequency):
            return []

        opens = self.open(sym, frequency)
        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)

        cdl = ta.CDLDOJISTAR(opens, highs, lows, closes)

        return cdl

    def dragonfly_doji(self, sym, frequency):
        if not self.kbars_ready(sym, frequency):
            return []

        opens = self.open(sym, frequency)
        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)

        cdl = ta.CDLDRAGONFLYDOJI(opens, highs, lows, closes)

        return cdl

    def dark_cloud_cover(self, sym, frequency, *args, **kwargs):
        if not self.kbars_ready(sym, frequency):
            return []

        opens = self.open(sym, frequency)
        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)

        cdl = ta.CDLDARKCLOUDCOVER(opens, highs, lows, closes, *args, **kwargs)

        return cdl

    def engulfing(self, sym, frequency):
        if not self.kbars_ready(sym, frequency):
            return []

        opens = self.open(sym, frequency)
        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)

        cdl = ta.CDLENGULFING(opens, highs, lows, closes)

        return cdl

    def evening_doji_star(self, sym, frequency, *args, **kwargs):
        if not self.kbars_ready(sym, frequency):
            return []

        opens = self.open(sym, frequency)
        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)

        cdl = ta.CDLEVENINGDOJISTAR(opens, highs, lows, closes, *args, **kwargs)

        return cdl

    def evening_star(self, sym, frequency, *args, **kwargs):
        if not self.kbars_ready(sym, frequency):
            return []

        opens = self.open(sym, frequency)
        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)

        cdl = ta.CDLEVENINGSTAR(opens, highs, lows, closes, *args, **kwargs)

        return cdl

    def gap_side_side_white(self, sym, frequency):
        if not self.kbars_ready(sym, frequency):
            return []

        opens = self.open(sym, frequency)
        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)

        cdl = ta.CDLGAPSIDESIDEWHITE(opens, highs, lows, closes)

        return cdl

    def gravestone_doji(self, sym, frequency):
        if not self.kbars_ready(sym, frequency):
            return []

        opens = self.open(sym, frequency)
        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)

        cdl = ta.CDLGRAVESTONEDOJI(opens, highs, lows, closes)

        return cdl

    def hammer(self, sym, frequency):
        if not self.kbars_ready(sym, frequency):
            return []

        opens = self.open(sym, frequency)
        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)

        cdl = ta.CDLHAMMER(opens, highs, lows, closes)

        return cdl

    def hanging_man(self, sym, frequency):
        if not self.kbars_ready(sym, frequency):
            return []

        opens = self.open(sym, frequency)
        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)

        cdl = ta.CDLHANGINGMAN(opens, highs, lows, closes)

        return cdl

    def harami(self, sym, frequency):
        if not self.kbars_ready(sym, frequency):
            return []

        opens = self.open(sym, frequency)
        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)

        cdl = ta.CDLHARAMI(opens, highs, lows, closes)

        return cdl

    def harami_cross(self, sym, frequency):
        if not self.kbars_ready(sym, frequency):
            return []

        opens = self.open(sym, frequency)
        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)

        cdl = ta.CDLHARAMICROSS(opens, highs, lows, closes)

        return cdl

    def high_wave(self, sym, frequency):
        if not self.kbars_ready(sym, frequency):
            return []

        opens = self.open(sym, frequency)
        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)

        cdl = ta.CDLHIGHWAVE(opens, highs, lows, closes)

        return cdl

    def hikkake(self, sym, frequency):
        if not self.kbars_ready(sym, frequency):
            return []

        opens = self.open(sym, frequency)
        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)

        cdl = ta.CDLHIKKAKE(opens, highs, lows, closes)

        return cdl

    def hikkake_mod(self, sym, frequency):
        if not self.kbars_ready(sym, frequency):
            return []

        opens = self.open(sym, frequency)
        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)

        cdl = ta.CDLHIKKAKEMOD(opens, highs, lows, closes)

        return cdl

    def homing_pigeon(self, sym, frequency):
        if not self.kbars_ready(sym, frequency):
            return []

        opens = self.open(sym, frequency)
        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)

        cdl = ta.CDLHOMINGPIGEON(opens, highs, lows, closes)

        return cdl

    def identical_3crows(self, sym, frequency):
        if not self.kbars_ready(sym, frequency):
            return []

        opens = self.open(sym, frequency)
        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)

        cdl = ta.CDLIDENTICAL3CROWS(opens, highs, lows, closes)

        return cdl

    def in_neck(self, sym, frequency):
        if not self.kbars_ready(sym, frequency):
            return []

        opens = self.open(sym, frequency)
        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)

        cdl = ta.CDLINNECK(opens, highs, lows, closes)

        return cdl

    def inverted_hammer(self, sym, frequency):
        if not self.kbars_ready(sym, frequency):
            return []

        opens = self.open(sym, frequency)
        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)

        cdl = ta.CDLINVERTEDHAMMER(opens, highs, lows, closes)

        return cdl

    def kicking(self, sym, frequency):
        if not self.kbars_ready(sym, frequency):
            return []

        opens = self.open(sym, frequency)
        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)

        cdl = ta.CDLKICKING(opens, highs, lows, closes)

        return cdl

    def kicking_by_length(self, sym, frequency):
        if not self.kbars_ready(sym, frequency):
            return []

        opens = self.open(sym, frequency)
        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)

        cdl = ta.CDLKICKINGBYLENGTH(opens, highs, lows, closes)

        return cdl

    def ladder_bottom(self, sym, frequency):
        if not self.kbars_ready(sym, frequency):
            return []

        opens = self.open(sym, frequency)
        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)

        cdl = ta.CDLLADDERBOTTOM(opens, highs, lows, closes)

        return cdl

    def long_legged_doji(self, sym, frequency):
        if not self.kbars_ready(sym, frequency):
            return []

        opens = self.open(sym, frequency)
        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)

        cdl = ta.CDLLONGLEGGEDDOJI(opens, highs, lows, closes)

        return cdl

    def long_line(self, sym, frequency):
        if not self.kbars_ready(sym, frequency):
            return []

        opens = self.open(sym, frequency)
        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)

        cdl = ta.CDLLONGLINE(opens, highs, lows, closes)

        return cdl

    def marubozu(self, sym, frequency):
        if not self.kbars_ready(sym, frequency):
            return []

        opens = self.open(sym, frequency)
        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)

        cdl = ta.CDLMARUBOZU(opens, highs, lows, closes)

        return cdl

    def matching_low(self, sym, frequency):
        if not self.kbars_ready(sym, frequency):
            return []

        opens = self.open(sym, frequency)
        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)

        cdl = ta.CDLMATCHINGLOW(opens, highs, lows, closes)

        return cdl

    def mathold(self, sym, frequency):
        if not self.kbars_ready(sym, frequency):
            return []

        opens = self.open(sym, frequency)
        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)

        cdl = ta.CDLMATHOLD(opens, highs, lows, closes)

        return cdl

    def morning_doji_star(self, sym, frequency):
        if not self.kbars_ready(sym, frequency):
            return []

        opens = self.open(sym, frequency)
        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)

        cdl = ta.CDLMORNINGDOJISTAR(opens, highs, lows, closes)

        return cdl

    def morning_star(self, sym, frequency):
        if not self.kbars_ready(sym, frequency):
            return []

        opens = self.open(sym, frequency)
        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)

        cdl = ta.CDLMORNINGSTAR(opens, highs, lows, closes)

        return cdl

    def on_neck(self, sym, frequency):
        if not self.kbars_ready(sym, frequency):
            return []

        opens = self.open(sym, frequency)
        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)

        cdl = ta.CDLONNECK(opens, highs, lows, closes)

        return cdl

    def piercing(self, sym, frequency):
        if not self.kbars_ready(sym, frequency):
            return []

        opens = self.open(sym, frequency)
        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)

        cdl = ta.CDLPIERCING(opens, highs, lows, closes)

        return cdl

    def rick_shawman(self, sym, frequency):
        if not self.kbars_ready(sym, frequency):
            return []

        opens = self.open(sym, frequency)
        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)

        cdl = ta.CDLRICKSHAWMAN(opens, highs, lows, closes)

        return cdl

    def rise_fall_3methods(self, sym, frequency):
        if not self.kbars_ready(sym, frequency):
            return []

        opens = self.open(sym, frequency)
        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)

        cdl = ta.CDLRISEFALL3METHODS(opens, highs, lows, closes)

        return cdl

    def separating_lines(self, sym, frequency):
        if not self.kbars_ready(sym, frequency):
            return []

        opens = self.open(sym, frequency)
        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)

        cdl = ta.CDLSEPARATINGLINES(opens, highs, lows, closes)

        return cdl

    def shooting_star(self, sym, frequency):
        if not self.kbars_ready(sym, frequency):
            return []

        opens = self.open(sym, frequency)
        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)

        cdl = ta.CDLSHOOTINGSTAR(opens, highs, lows, closes)

        return cdl

    def short_line(self, sym, frequency):
        if not self.kbars_ready(sym, frequency):
            return []

        opens = self.open(sym, frequency)
        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)

        cdl = ta.CDLSHORTLINE(opens, highs, lows, closes)

        return cdl

    def spinning_top(self, sym, frequency):
        if not self.kbars_ready(sym, frequency):
            return []

        opens = self.open(sym, frequency)
        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)

        cdl = ta.CDLSPINNINGTOP(opens, highs, lows, closes)

        return cdl

    def stalled_pattern(self, sym, frequency):
        if not self.kbars_ready(sym, frequency):
            return []

        opens = self.open(sym, frequency)
        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)

        cdl = ta.CDLSTALLEDPATTERN(opens, highs, lows, closes)

        return cdl

    def sticks_and_wich(self, sym, frequency):
        if not self.kbars_ready(sym, frequency):
            return []

        opens = self.open(sym, frequency)
        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)

        cdl = ta.CDLSTICKSANDWICH(opens, highs, lows, closes)

        return cdl

    def takuri(self, sym, frequency):
        if not self.kbars_ready(sym, frequency):
            return []

        opens = self.open(sym, frequency)
        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)

        cdl = ta.CDLTAKURI(opens, highs, lows, closes)

        return cdl

    def tasuki_gap(self, sym, frequency):
        if not self.kbars_ready(sym, frequency):
            return []

        opens = self.open(sym, frequency)
        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)

        cdl = ta.CDLTASUKIGAP(opens, highs, lows, closes)

        return cdl

    def thrusting(self, sym, frequency):
        if not self.kbars_ready(sym, frequency):
            return []

        opens = self.open(sym, frequency)
        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)

        cdl = ta.CDLTHRUSTING(opens, highs, lows, closes)

        return cdl

    def tristar(self, sym, frequency):
        if not self.kbars_ready(sym, frequency):
            return []

        opens = self.open(sym, frequency)
        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)

        cdl = ta.CDLTRISTAR(opens, highs, lows, closes)

        return cdl

    def unique_3river(self, sym, frequency):
        if not self.kbars_ready(sym, frequency):
            return []

        opens = self.open(sym, frequency)
        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)

        cdl = ta.CDLUNIQUE3RIVER(opens, highs, lows, closes)

        return cdl

    def upside_gap_2crows(self, sym, frequency):
        if not self.kbars_ready(sym, frequency):
            return []

        opens = self.open(sym, frequency)
        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)

        cdl = ta.CDLUPSIDEGAP2CROWS(opens, highs, lows, closes)

        return cdl

    def xside_gap_3methods(self, sym, frequency):
        if not self.kbars_ready(sym, frequency):
            return []

        opens = self.open(sym, frequency)
        highs = self.high(sym, frequency)
        lows = self.low(sym, frequency)
        closes = self.close(sym, frequency)

        cdl = ta.CDLXSIDEGAP3METHODS(opens, highs, lows, closes)

        return cdl
