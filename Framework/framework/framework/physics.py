# encoding: utf-8


def going_up(ser):
    return ser[-1] > ser[-2] > ser[-3]


def going_down(ser):
    return ser[-1] < ser[-2] < ser[-3]


def span_up(ser1, ser2):
    return abs(ser1[-1] - ser2[-1]) >= abs(ser1[-2] - ser2[-2]) >= abs(ser1[-3] - ser2[-3])
