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
from shapely.geometry import (Point as point,
                              Polygon as polygon)


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
    
    @property
    def shapely_point(self):
        """转为geometry对象"""
        return point(eval(str(self)))
    
    def __str__(self):
        return f'({self.x}, {self.y}, {self.z})'

class Polygon(object):

    def __init__(self, *points: List[Point], **kwargs):

        """
        points: List[Point]: ex: (Point, Point, Point, ...)
        kwargs:
            points (tuple): ex: ((x, y, z), (x, y, z), ...)
        """        
        
        if 'points' in kwargs:
            points_list = kwargs.get('points')
            points = [Point(*p) for p in points_list]
        
        assert points

        self.__points = points
    
    @property
    def points(self):
        return self.__points
    
    def indexpoint(self, i):
        return self.points[i]

    @property
    def shapely_polygon(self):
        """转为geometry对象"""
        return polygon(eval(str(self)))
    
    @property
    def bounds(self):
        return self.shapely_polygon.bounds
    
    def intersection(self, other):
        """计算交集 并返回交集对象"""
        inter = self.shapely_polygon.intersection(other.shapely_polygon)
        return self.__class__(points=inter.exterior.coords[:-1])
    
    def __str__(self):
        s = ','.join([str(p) for p in self.__points])
        return f'({s})'
    

def box(minx, miny, maxx, maxy):
    """Returns a rectangular polygon with configurable normal vector"""
    coords = [(minx, maxy), (maxx, maxy), (maxx, miny), (minx, miny)]
    points = (Point(*c) for c in coords)
    return Polygon(*points)