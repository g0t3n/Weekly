#!/usr/bin/env python
# coding=utf-8
# Created Time: Sun Oct 12 16:12:48 2014
# Author: g0t3nst@gmail.com
import time

def get_time_as_string():
    # (YYYY-MM-DD)
    s = time.localtime()
    return "%s-%s-%s" % (s.tm_year,s.tm_mon,s.tm_mday)

