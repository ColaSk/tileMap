# -*- encoding: utf-8 -*-
'''
@File    :   point.py
@Time    :   2021/12/03 15:18:37
@Author  :   sk 
@Version :   1.0
@Contact :   kaixuan.sun@boonray.com
@License :   (C)Copyright 2017-2018, Liugroup-NLPR-CASIA
@Desc    :   None
'''

# here put the import lib

from typing import List


class Point(object):

    def __init__(self, x, y, z=0):
        self.__x = x
        self.__y = y
        self.__z = z
    
    @property
    def x(self):
        return self.__x
    
    @property
    def y(self):
        return self.__y
    
    @property
    def z(self):
        return self.__z
    
    def __str__(self):
        return f'({self.x}, {self.y}, {self.z})'

class Polygon(object):

    def __init__(self, *points: List[Point]):
        self.__points = points
    
    @property
    def points(self):
        return self.__points
    
    def __str__(self):
        s = ','.join([str(p) for p in self.__points])
        return f'({s})'
    