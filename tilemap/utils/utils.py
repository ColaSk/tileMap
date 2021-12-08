# -*- encoding: utf-8 -*-
'''
@File    :   utils.py
@Time    :   2021/12/07 19:18:05
@Author  :   sk 
@Version :   1.0
@Contact :   kaixuan.sun@boonray.com
@License :   (C)Copyright 2017-2018, Liugroup-NLPR-CASIA
@Desc    :   None
'''

# here put the import lib
def resolution(min, max, length):
    return (max - min)/length

def pixel_num(min, max, r):
    return abs(max-min)/r
