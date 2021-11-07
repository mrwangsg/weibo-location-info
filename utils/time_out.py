#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/9/28 18:36
# @Author  : sgwang
# @File    : time_out.py
# @Software: PyCharm


class inner_time_out(object):

    def __init__(self):
        pass

    @property
    def s3(self) -> int:
        return int(3)

    @property
    def s5(self) -> int:
        return int(5)

    @property
    def s10(self) -> int:
        return int(10)

    @property
    def s30(self) -> int:
        return int(30)

    @property
    def s60(self) -> int:
        return int(60)

    @property
    def m1(self) -> int:
        return int(1 * 60)

    @property
    def m3(self) -> int:
        return int(3 * 60)


time_out = inner_time_out()

if __name__ == "__main__":
    print(time_out.s10)
    print(time_out.m3)
