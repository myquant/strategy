import numpy as np
from talib import SMA
from .context import Context


class VolumeMixin(Context, object):

    # def __init__(self, *args, **kwargs):
    #     super(VolumeMixin, self).__init__(*args, **kwargs)

    def init_volume_mixin(self):
        self.__read_volume_mixin_para__()

    def __read_volume_mixin_para__(self):
        if not hasattr(self, 'life_timeperiod'):
            self.short_timeperiod = self.config.getint('para', 'short_timeperiod')
            self.long_timeperiod = self.config.getint('para', 'long_timeperiod')
            self.life_timeperiod = self.config.getint('para', 'life_timeperiod')

    def volume_up(self, volume):
        sma = SMA(volume, timeperiod=self.short_timeperiod)
        lma = SMA(volume, timeperiod=self.long_timeperiod)  ## make sure last lma is a number
        life = SMA(volume, timeperiod=self.life_timeperiod)

        if len(sma) < 3:
            return False

        volume_enforce = sma[-1] > lma[-1] > life[-1]
        speed_up = (volume[-1] - sma[-1]) > (sma[-1] - lma[-1]) > (lma[-1] - life[-1])

        return volume_enforce and speed_up

    def volume_filtering(self, sym, frequency):
        vol = self.volume(sym, frequency)

        return self.volume_up(vol)
